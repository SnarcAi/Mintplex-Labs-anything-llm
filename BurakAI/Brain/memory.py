#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BurakAI - Memory System
═════════════════════════════════════════════════════════
NEXUS'tan esinlendi - basitleştirilmiş:
- Neo4j graph yerine → JSONL append-only log
- Complex semantic memory yerine → Simple episodic + learned patterns
- Real-time embeddings yerine → Periodic batch analysis

But still LEARNS:
- Every interaction logged
- Pattern detection (weekly analysis)
- Context enrichment over time
═════════════════════════════════════════════════════════
"""

import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import defaultdict, Counter


@dataclass
class MemoryEntry:
    """Single memory entry"""
    timestamp: str  # ISO format
    type: str  # episodic, learned, pattern
    event: str  # Event type (query, result, feedback, etc.)
    data: Dict[str, Any]  # Flexible data storage
    tags: List[str]  # Searchable tags

    def to_dict(self) -> Dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict) -> 'MemoryEntry':
        return MemoryEntry(**d)


class MemorySystem:
    """
    Append-only memory system with pattern learning
    """

    def __init__(self, memory_file: Path, max_entries: int = 10000):
        """
        Initialize memory system

        Args:
            memory_file: Path to memory.jsonl file
            max_entries: Max entries before rotation
        """
        self.memory_file = Path(memory_file)
        self.max_entries = max_entries

        # Ensure parent dir exists
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)

        # In-memory cache of recent entries
        self._recent_cache: List[MemoryEntry] = []
        self._cache_size = 100

        # Load recent entries
        self._load_recent()

    # ═════════════════════════════════════════════════════
    # WRITE OPERATIONS
    # ═════════════════════════════════════════════════════

    def log_query(self, query: str, intent: str, profile: str, entities: Dict = None):
        """Log a user query"""
        entry = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            type="episodic",
            event="query",
            data={
                "query": query,
                "intent": intent,
                "profile": profile,
                "entities": entities or {}
            },
            tags=["query", intent, profile]
        )
        self._append(entry)

    def log_result(self, query: str, result: str, latency_sec: float, cache_hit: bool, tools_used: List[str] = None):
        """Log a query result"""
        entry = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            type="episodic",
            event="result",
            data={
                "query": query,
                "result": result[:500],  # Truncate long results
                "latency_sec": latency_sec,
                "cache_hit": cache_hit,
                "tools_used": tools_used or []
            },
            tags=["result", "cache_hit" if cache_hit else "cache_miss"]
        )
        self._append(entry)

    def log_feedback(self, query: str, feedback: str, accepted: bool):
        """Log user feedback"""
        entry = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            type="episodic",
            event="feedback",
            data={
                "query": query,
                "feedback": feedback,
                "accepted": accepted
            },
            tags=["feedback", "positive" if accepted else "negative"]
        )
        self._append(entry)

    def log_pattern(self, pattern_type: str, pattern_data: Dict, confidence: float):
        """Log a learned pattern"""
        entry = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            type="learned",
            event="pattern",
            data={
                "pattern_type": pattern_type,
                "pattern": pattern_data,
                "confidence": confidence
            },
            tags=["pattern", pattern_type]
        )
        self._append(entry)

    def log_value_generated(self, task: str, value_try: float, time_saved_hours: float):
        """Log value/ROI generated"""
        entry = MemoryEntry(
            timestamp=datetime.now().isoformat(),
            type="episodic",
            event="value_generated",
            data={
                "task": task,
                "value_try": value_try,
                "time_saved_hours": time_saved_hours
            },
            tags=["value", "roi"]
        )
        self._append(entry)

    def _append(self, entry: MemoryEntry):
        """Append entry to file and cache"""
        # Write to file
        with open(self.memory_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry.to_dict(), ensure_ascii=False) + "\n")

        # Add to cache
        self._recent_cache.append(entry)
        if len(self._recent_cache) > self._cache_size:
            self._recent_cache.pop(0)

        # Check if rotation needed
        self._check_rotation()

    # ═════════════════════════════════════════════════════
    # READ OPERATIONS
    # ═════════════════════════════════════════════════════

    def get_recent(self, n: int = 10, event_type: Optional[str] = None) -> List[MemoryEntry]:
        """
        Get recent entries

        Args:
            n: Number of entries
            event_type: Filter by event type (optional)

        Returns:
            List of recent entries
        """
        entries = self._recent_cache[::-1]  # Reverse (newest first)

        if event_type:
            entries = [e for e in entries if e.event == event_type]

        return entries[:n]

    def search(self, query: str = None, tags: List[str] = None, since: datetime = None, limit: int = 100) -> List[MemoryEntry]:
        """
        Search memory entries

        Args:
            query: Search in data (case-insensitive)
            tags: Filter by tags
            since: Filter entries since this date
            limit: Max results

        Returns:
            List of matching entries
        """
        results = []

        # Read from file (can be slow for large files, but OK for <10K entries)
        if not self.memory_file.exists():
            return []

        with open(self.memory_file, "r", encoding="utf-8") as f:
            for line in f:
                if len(results) >= limit:
                    break

                try:
                    entry = MemoryEntry.from_dict(json.loads(line))

                    # Filter by date
                    if since and datetime.fromisoformat(entry.timestamp) < since:
                        continue

                    # Filter by tags
                    if tags and not any(tag in entry.tags for tag in tags):
                        continue

                    # Filter by query
                    if query:
                        entry_str = json.dumps(entry.data, ensure_ascii=False).lower()
                        if query.lower() not in entry_str:
                            continue

                    results.append(entry)

                except Exception:
                    continue

        return results

    def get_stats(self, days: int = 7) -> Dict[str, Any]:
        """
        Get memory statistics for last N days

        Args:
            days: Number of days to analyze

        Returns:
            Stats dict
        """
        since = datetime.now() - timedelta(days=days)
        entries = self.search(since=since, limit=10000)

        stats = {
            "total_entries": len(entries),
            "by_event": Counter(e.event for e in entries),
            "by_type": Counter(e.type for e in entries),
            "avg_latency": 0.0,
            "cache_hit_rate": 0.0,
            "total_value_try": 0.0,
        }

        # Calculate latency
        latencies = [e.data["latency_sec"] for e in entries if e.event == "result" and "latency_sec" in e.data]
        if latencies:
            stats["avg_latency"] = sum(latencies) / len(latencies)

        # Calculate cache hit rate
        cache_hits = sum(1 for e in entries if e.event == "result" and e.data.get("cache_hit"))
        cache_total = sum(1 for e in entries if e.event == "result")
        if cache_total > 0:
            stats["cache_hit_rate"] = cache_hits / cache_total

        # Calculate total value
        values = [e.data["value_try"] for e in entries if e.event == "value_generated"]
        stats["total_value_try"] = sum(values)

        return stats

    # ═════════════════════════════════════════════════════
    # PATTERN LEARNING
    # ═════════════════════════════════════════════════════

    def analyze_patterns(self, days: int = 7) -> Dict[str, Any]:
        """
        Analyze patterns from recent history

        Args:
            days: Days to analyze

        Returns:
            Detected patterns
        """
        since = datetime.now() - timedelta(days=days)
        entries = self.search(since=since, limit=10000)

        patterns = {
            "frequent_intents": self._find_frequent_intents(entries),
            "customer_patterns": self._find_customer_patterns(entries),
            "time_patterns": self._find_time_patterns(entries),
            "tool_usage": self._find_tool_patterns(entries),
        }

        return patterns

    def _find_frequent_intents(self, entries: List[MemoryEntry]) -> List[Dict]:
        """Find most frequent intents"""
        intents = [e.data.get("intent") for e in entries if e.event == "query" and "intent" in e.data]
        counter = Counter(intents)
        return [{"intent": k, "count": v} for k, v in counter.most_common(5)]

    def _find_customer_patterns(self, entries: List[MemoryEntry]) -> Dict[str, Dict]:
        """Find customer-related patterns"""
        customer_data = defaultdict(lambda: {"queries": 0, "intents": []})

        for e in entries:
            if e.event == "query":
                entities = e.data.get("entities", {})
                customer = entities.get("customer")
                if customer:
                    customer_data[customer]["queries"] += 1
                    customer_data[customer]["intents"].append(e.data.get("intent"))

        # Summarize
        result = {}
        for customer, data in customer_data.items():
            result[customer] = {
                "total_queries": data["queries"],
                "top_intents": [k for k, v in Counter(data["intents"]).most_common(3)]
            }

        return result

    def _find_time_patterns(self, entries: List[MemoryEntry]) -> Dict[str, int]:
        """Find time-based patterns"""
        hours = defaultdict(int)

        for e in entries:
            if e.event == "query":
                dt = datetime.fromisoformat(e.timestamp)
                hour = dt.hour
                hours[f"{hour:02d}:00"] += 1

        # Get top 5 hours
        top_hours = sorted(hours.items(), key=lambda x: x[1], reverse=True)[:5]
        return dict(top_hours)

    def _find_tool_patterns(self, entries: List[MemoryEntry]) -> Dict[str, int]:
        """Find tool usage patterns"""
        tools = []

        for e in entries:
            if e.event == "result":
                tools.extend(e.data.get("tools_used", []))

        counter = Counter(tools)
        return dict(counter.most_common(10))

    # ═════════════════════════════════════════════════════
    # INTERNAL
    # ═════════════════════════════════════════════════════

    def _load_recent(self):
        """Load recent entries into cache"""
        if not self.memory_file.exists():
            return

        entries = []
        with open(self.memory_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    entries.append(MemoryEntry.from_dict(json.loads(line)))
                except Exception:
                    continue

        # Keep last N entries
        self._recent_cache = entries[-self._cache_size:]

    def _check_rotation(self):
        """Check if file needs rotation"""
        if not self.memory_file.exists():
            return

        # Count lines
        with open(self.memory_file, "r") as f:
            count = sum(1 for _ in f)

        if count > self.max_entries:
            # Rotate: memory.jsonl -> memory.YYYYMMDD.jsonl
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_file = self.memory_file.with_suffix(f".{timestamp}.jsonl")
            self.memory_file.rename(archive_file)
            print(f"[Memory] Rotated to {archive_file.name}")


# ═════════════════════════════════════════════════════════
# EXAMPLE USAGE
# ═════════════════════════════════════════════════════════
if __name__ == "__main__":
    # Test memory system
    mem = MemorySystem(Path("test_memory.jsonl"))

    # Log some events
    mem.log_query("ABC'nin faturasını kontrol et", "invoice_check", "finance", {"customer": "ABC"})
    time.sleep(0.1)
    mem.log_result("ABC'nin faturasını kontrol et", "Fatura kontrol edildi...", 1.2, False, ["ocr_pdf", "margin_calc"])
    time.sleep(0.1)
    mem.log_value_generated("invoice_check", 2000, 0.5)

    # Get stats
    stats = mem.get_stats(days=1)
    print("\n=== STATS ===")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    # Analyze patterns
    patterns = mem.analyze_patterns(days=1)
    print("\n=== PATTERNS ===")
    print(json.dumps(patterns, indent=2, ensure_ascii=False))

    # Clean up
    Path("test_memory.jsonl").unlink(missing_ok=True)
