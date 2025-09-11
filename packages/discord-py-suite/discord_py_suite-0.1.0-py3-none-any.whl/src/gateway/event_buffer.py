"""Circular event buffer for Discord gateway events."""

import time
from collections import deque
from typing import Any, Dict, List, Optional, Deque


class CircularEventBuffer:
    """Memory-efficient circular buffer for Discord gateway events."""

    def __init__(self, maxsize: int = 1000) -> None:
        self.maxsize = maxsize
        self.buffer: Deque[Dict[str, Any]] = deque(maxlen=maxsize)
        self.total_events = 0
        self.start_time = time.time()

    def add(self, event: Dict[str, Any]) -> None:
        """Add an event to the buffer."""
        # Add timestamp if not present
        if "timestamp" not in event:
            event["timestamp"] = time.time()

        # Add sequence number for ordering
        event["sequence"] = self.total_events

        self.buffer.append(event)
        self.total_events += 1

    def get_events(
        self, limit: Optional[int] = None, since: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Get events from the buffer with optional filtering."""
        events = list(self.buffer)

        # Filter by timestamp if provided
        if since is not None:
            events = [e for e in events if e.get("timestamp", 0) > since]

        # Apply limit
        if limit is not None:
            events = events[-limit:]

        return events

    def clear(self) -> None:
        """Clear all events from the buffer."""
        self.buffer.clear()

    def get_stats(self) -> Dict[str, Any]:
        """Get buffer statistics."""
        return {
            "current_size": len(self.buffer),
            "max_size": self.maxsize,
            "total_events": self.total_events,
            "uptime_seconds": time.time() - self.start_time,
            "events_per_second": self.total_events / (time.time() - self.start_time)
            if self.total_events > 0
            else 0,
        }
