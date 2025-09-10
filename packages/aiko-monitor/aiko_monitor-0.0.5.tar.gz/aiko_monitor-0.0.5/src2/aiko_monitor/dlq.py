from __future__ import annotations

import gzip
import hashlib
import json
import logging
import os
import queue
import threading
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from uuid import uuid4

logger = logging.getLogger("aiko.monitor")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


class EventStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    FAILED = "failed"
    COMPLETED = "completed"


@dataclass
class DLQEvent:
    id: str
    data: Dict[str, Any]
    created_at: float
    attempt_count: int = 0
    last_attempt: Optional[float] = None
    next_retry: float = field(default_factory=lambda: time.time())
    status: EventStatus = EventStatus.PENDING
    error: Optional[str] = None

    def should_retry(self, max_age_hours: int = 24) -> bool:
        age = time.time() - self.created_at
        return age < (max_age_hours * 3600) and self.attempt_count < 10

    def calculate_backoff(self) -> float:
        base = min(300, 2**self.attempt_count)
        jitter = base * 0.1 * (0.5 - uuid4().int % 100 / 100)
        return base + jitter


class DLQStorage:
    def __init__(self, base_dir: Path, max_file_size_mb: int = 10):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.max_file_size = max_file_size_mb * 1024 * 1024
        self._lock = threading.RLock()

        self.pending_dir = self.base_dir / "pending"
        self.processing_dir = self.base_dir / "processing"
        self.failed_dir = self.base_dir / "failed"

        for dir in [self.pending_dir, self.processing_dir, self.failed_dir]:
            dir.mkdir(exist_ok=True)

    def write_batch(self, events: List[DLQEvent]) -> Optional[str]:
        if not events:
            return None

        batch_id = f"{int(time.time() * 1000)}_{uuid4().hex[:8]}"
        filepath = self.pending_dir / f"{batch_id}.gz"
        temp_path = filepath.with_suffix(".tmp")

        try:
            data = {
                "version": 1,
                "batch_id": batch_id,
                "created_at": time.time(),
                "events": [
                    {
                        "id": e.id,
                        "data": e.data,
                        "created_at": e.created_at,
                        "attempt_count": e.attempt_count,
                        "last_attempt": e.last_attempt,
                        "next_retry": e.next_retry,
                        "status": e.status.value,
                        "error": e.error,
                    }
                    for e in events
                ],
                "checksum": None,
            }

            json_data = json.dumps(data["events"], sort_keys=True)
            data["checksum"] = hashlib.sha256(json_data.encode()).hexdigest()

            with gzip.open(temp_path, "wb") as f:
                f.write(json.dumps(data).encode("utf-8"))

            with open(temp_path, "rb") as f:
                os.fsync(f.fileno())

            temp_path.rename(filepath)
            logger.debug(f"Wrote batch {batch_id} with {len(events)} events")
            return batch_id

        except Exception as e:
            logger.error(f"Failed to write batch: {e}")
            if temp_path.exists():
                temp_path.unlink()
            return None

    def read_batch(self, batch_id: str, source_dir: Optional[Path] = None) -> List[DLQEvent]:
        source_dir = source_dir or self.pending_dir
        filepath = source_dir / f"{batch_id}.gz"

        if not filepath.exists():
            return []

        try:
            with gzip.open(filepath, "rb") as f:
                data = json.loads(f.read().decode("utf-8"))

            json_data = json.dumps(data["events"], sort_keys=True)
            expected = hashlib.sha256(json_data.encode()).hexdigest()

            if data.get("checksum") != expected:
                logger.error(f"Checksum mismatch for batch {batch_id}")
                self._quarantine_file(filepath)
                return []

            events = []
            for e in data["events"]:
                event = DLQEvent(
                    id=e["id"],
                    data=e["data"],
                    created_at=e["created_at"],
                    attempt_count=e.get("attempt_count", 0),
                    last_attempt=e.get("last_attempt"),
                    next_retry=e.get("next_retry", time.time()),
                    status=EventStatus(e.get("status", "pending")),
                    error=e.get("error"),
                )
                events.append(event)

            return events

        except Exception as e:
            logger.error(f"Failed to read batch {batch_id}: {e}")
            self._quarantine_file(filepath)
            return []

    def move_batch(self, batch_id: str, from_dir: Path, to_dir: Path) -> bool:
        src = from_dir / f"{batch_id}.gz"
        dst = to_dir / f"{batch_id}.gz"

        try:
            if src.exists():
                src.rename(dst)
                return True
        except Exception as e:
            logger.error(f"Failed to move batch {batch_id}: {e}")
        return False

    def list_batches(self, directory: Optional[Path] = None) -> List[str]:
        directory = directory or self.pending_dir
        batches = []

        try:
            for file in directory.glob("*.gz"):
                batch_id = file.stem
                batches.append(batch_id)
        except Exception as e:
            logger.error(f"Failed to list batches: {e}")

        return sorted(batches)

    def _quarantine_file(self, filepath: Path) -> None:
        quarantine_dir = self.base_dir / "quarantine"
        quarantine_dir.mkdir(exist_ok=True)

        try:
            dst = quarantine_dir / f"{filepath.stem}_{int(time.time())}.gz"
            filepath.rename(dst)
            logger.warning(f"Quarantined corrupted file: {dst}")
        except Exception:
            pass


class ReliableDLQ:
    def __init__(
        self,
        send_func: Callable,
        base_dir: Path = Path("./.aiko-dlq"),
        batch_size: int = 100,
        flush_interval: float = 5.0,
        sweep_interval: float = 10.0,
        max_age_hours: int = 24,
        max_memory_items: int = 10000,
    ):
        self.storage = DLQStorage(base_dir)
        self.send_func = send_func
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.sweep_interval = sweep_interval
        self.max_age_hours = max_age_hours
        self.max_memory_items = max_memory_items

        self._memory_queue = queue.Queue(maxsize=max_memory_items)
        self._shutdown = threading.Event()

        self._flush_thread = threading.Thread(target=self._flush_worker, name="dlq-flush", daemon=False)
        self._sweep_thread = threading.Thread(target=self._sweep_worker, name="dlq-sweep", daemon=False)

        self._flush_thread.start()
        self._sweep_thread.start()

        logger.info("ReliableDLQ initialized")

    def add_event(self, event_data: Dict[str, Any]) -> bool:
        if self._shutdown.is_set():
            return False

        event = DLQEvent(id=str(uuid4()), data=event_data, created_at=time.time())

        try:
            self._memory_queue.put_nowait(event)
            return True
        except queue.Full:
            logger.warning("Memory queue full, writing directly to disk")
            if self.storage.write_batch([event]):
                return True
            return False

    def _flush_worker(self) -> None:
        logger.info("Flush worker started")
        batch = []
        last_flush = time.time()

        while not self._shutdown.is_set():
            timeout = max(0.1, self.flush_interval - (time.time() - last_flush))

            try:
                event = self._memory_queue.get(timeout=timeout)
                batch.append(event)

                should_flush = len(batch) >= self.batch_size or time.time() - last_flush >= self.flush_interval

                if should_flush and batch:
                    self._flush_batch(batch)
                    batch = []
                    last_flush = time.time()

            except queue.Empty:
                if batch:
                    self._flush_batch(batch)
                    batch = []
                    last_flush = time.time()
            except Exception as e:
                logger.error(f"Flush worker error: {e}")

        if batch:
            self._flush_batch(batch)

        logger.info("Flush worker stopped")

    def _flush_batch(self, batch: List[DLQEvent]) -> None:
        if not batch:
            return

        batch_id = self.storage.write_batch(batch)
        if batch_id:
            logger.debug(f"Flushed {len(batch)} events to batch {batch_id}")
        else:
            for event in batch:
                if not self.storage.write_batch([event]):
                    logger.error(f"Failed to persist event {event.id}")

    def _sweep_worker(self) -> None:
        logger.info("Sweep worker started")

        while not self._shutdown.is_set():
            try:
                self._process_pending_batches()
                self._cleanup_old_events()
                self._shutdown.wait(self.sweep_interval)

            except Exception as e:
                logger.error(f"Sweep worker error: {e}")

        logger.info("Sweep worker stopped")

    def _process_pending_batches(self) -> None:
        pending_batches = self.storage.list_batches(self.storage.pending_dir)

        for batch_id in pending_batches:
            if self._shutdown.is_set():
                break

            if not self.storage.move_batch(batch_id, self.storage.pending_dir, self.storage.processing_dir):
                continue

            events = self.storage.read_batch(batch_id, self.storage.processing_dir)
            if not events:
                continue

            now = time.time()
            to_retry = [e for e in events if e.next_retry <= now and e.should_retry(self.max_age_hours)]
            expired = [e for e in events if not e.should_retry(self.max_age_hours)]
            to_defer = [e for e in events if e.next_retry > now and e.should_retry(self.max_age_hours)]

            if expired:
                logger.info(f"Expired {len(expired)} events from batch {batch_id}")

            failed_events = []
            for event in to_retry:
                if self._shutdown.is_set():
                    failed_events.append(event)
                    continue

                success = False
                if self.send_func:
                    try:
                        success = self.send_func(event.data)
                    except Exception as e:
                        logger.error(f"Send function error: {e}")

                event.attempt_count += 1
                event.last_attempt = time.time()

                if success:
                    event.status = EventStatus.COMPLETED
                else:
                    event.status = EventStatus.FAILED
                    event.next_retry = time.time() + event.calculate_backoff()
                    event.error = "Send failed"
                    failed_events.append(event)

            events_to_requeue = failed_events + to_defer

            if events_to_requeue:
                new_batch_id = self.storage.write_batch(events_to_requeue)
                if not new_batch_id:
                    self.storage.move_batch(batch_id, self.storage.processing_dir, self.storage.failed_dir)
                    continue

            processing_file = self.storage.processing_dir / f"{batch_id}.gz"
            if processing_file.exists():
                processing_file.unlink()

    def _cleanup_old_events(self) -> None:
        cutoff = time.time() - (self.max_age_hours * 3600 * 2)

        for batch_id in self.storage.list_batches(self.storage.failed_dir):
            filepath = self.storage.failed_dir / f"{batch_id}.gz"
            try:
                if filepath.stat().st_mtime < cutoff:
                    filepath.unlink()
                    logger.info(f"Cleaned up old failed batch: {batch_id}")
            except Exception as e:
                logger.error(f"Failed to clean up batch {batch_id}: {e}")

    def shutdown(self, timeout: float = 30.0) -> None:
        logger.info("Shutting down ReliableDLQ")

        self._shutdown.set()
        self._flush_thread.join(timeout=timeout / 2)
        self._sweep_thread.join(timeout=timeout / 2)

        remaining = []
        while not self._memory_queue.empty():
            try:
                remaining.append(self._memory_queue.get_nowait())
            except queue.Empty:
                break

        if remaining:
            self._flush_batch(remaining)
            logger.info(f"Flushed {len(remaining)} events on shutdown")

        logger.info("ReliableDLQ shutdown complete")
