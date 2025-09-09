"""Performance monitoring and optimization for ShellRosetta.

This module provides performance monitoring, caching, and optimization.
"""
import time
from functools import wraps
from typing import Dict, List, Optional, Any
from collections import defaultdict

try:
    import psutil
except ImportError:
    psutil = None

# Import core functions for benchmarking
from .core import lnx2ps


class PerformanceMonitor:
    """Performance monitoring for ShellRosetta."""

    def __init__(self):
        self.metrics: Dict[str, List[float]] = defaultdict(list)
        self.call_counts: Dict[str, int] = defaultdict(int)
        self.memory_cache: Dict[str, Any] = {}
        self.cache_hits = 0
        self.cache_misses = 0

    def time_function(self, func_name: str):
        """Decorator to time function execution."""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    end_time = time.time()
                    execution_time = end_time - start_time
                    self.metrics[func_name].append(execution_time)
                    self.call_counts[func_name] += 1
            return wrapper
        return decorator

    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics."""
        stats = {}
        for func_name, times in self.metrics.items():
            if times:
                stats[func_name] = {
                    'avg_time': sum(times) / len(times),
                    'min_time': min(times),
                    'max_time': max(times),
                    'total_calls': self.call_counts[func_name],
                    'total_time': sum(times)
                }

        # Add cache statistics
        total_cache_requests = self.cache_hits + self.cache_misses
        cache_hit_rate = (
            self.cache_hits / total_cache_requests * 100
            if total_cache_requests > 0 else 0
        )

        stats['cache'] = {
            'hits': self.cache_hits,
            'misses': self.cache_misses,
            'hit_rate': cache_hit_rate,
            'total_cached_items': len(self.memory_cache)
        }

        return stats

    def clear_cache(self):
        """Clear the memory cache."""
        self.memory_cache.clear()
        self.cache_hits = 0
        self.cache_misses = 0

    def cache_get(self, key: str) -> Optional[Any]:
        """Get item from cache."""
        if key in self.memory_cache:
            self.cache_hits += 1
            return self.memory_cache[key]
        else:
            self.cache_misses += 1
            return None

    def cache_set(self, key: str, value: Any):
        """Set item in cache."""
        self.memory_cache[key] = value


def get_system_metrics() -> Dict[str, Any]:
    """Get current system performance metrics."""
    if psutil is None:
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'memory_available_mb': 0,
            'disk_percent': 0,
            'disk_free_gb': 0
        }

    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')

        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_available_mb': memory.available // (1024 * 1024),
            'disk_percent': disk.percent,
            'disk_free_gb': disk.free // (1024 * 1024 * 1024)
        }
    except Exception:
        return {
            'cpu_percent': 0,
            'memory_percent': 0,
            'memory_available_mb': 0,
            'disk_percent': 0,
            'disk_free_gb': 0
        }


def get_memory_cache() -> Dict[str, Any]:
    """Get memory cache for testing."""
    return performance_monitor.memory_cache


def benchmark_translation(command: str, iterations: int = 100) -> Dict[str, float]:
    """Benchmark translation performance."""
    times = []
    for _ in range(iterations):
        start_time = time.time()
        lnx2ps(command)
        end_time = time.time()
        times.append(end_time - start_time)

    return {
        'avg_time': sum(times) / len(times),
        'min_time': min(times),
        'max_time': max(times),
        'total_time': sum(times),
        'iterations': iterations
    }


# Global performance monitor instance
performance_monitor = PerformanceMonitor()