#!/usr/bin/env python3
"""
Complete performance testing
"""

import sys
import os
import time
import statistics
# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from shellrosetta.core import lnx2ps, clear_translation_cache, get_translation_stats
from shellrosetta.performance import get_memory_cache

def test_caching_performance():
    """Test caching provides performance benefit"""
    
    # Clear cache to start fresh
    clear_translation_cache()
    
    test_command = "ls -la | grep error"
    
    print("Testing caching performance...")
    
    # Measure uncached performance (first 3 calls)
    uncached_times = []
    for i in range(3):
        start = time.perf_counter()
        result1 = lnx2ps(test_command)
        end = time.perf_counter()
        uncached_times.append((end - start) * 1000)
    
    # Measure cached performance (next 3 calls)
    cached_times = []
    for i in range(3):
        start = time.perf_counter()
        result2 = lnx2ps(test_command)
        end = time.perf_counter()
        cached_times.append((end - start) * 1000)
    
    # Verify results are the same
    assert result1 == result2, "Cached and uncached results differ!"
    
    avg_uncached = statistics.mean(uncached_times)
    avg_cached = statistics.mean(cached_times)
    improvement = ((avg_uncached - avg_cached) / avg_uncached) * 100
    
    print(f"   Average uncached time: {avg_uncached:.2f}ms")
    print(f"   Average cached time: {avg_cached:.2f}ms")
    print(f"   Performance improvement: {improvement:.1f}%")
    
    return improvement > 0  # Any improvement is good

def test_memory_cache_functionality():
    """Test memory cache operations"""
    
    cache = get_memory_cache()
    cache.clear()
    
    # Test basic cache operations
    cache.set("test_key", "test_value", ttl=60)
    value = cache.get("test_key")
    
    assert value == "test_value", "Cache get/set not working"
    print("✅ Memory cache basic operations working")
    
    # Test cache stats
    stats = cache.get_stats()
    assert 'hits' in stats and 'misses' in stats
    print("✅ Memory cache statistics working")
    
    return True

def test_large_volume_performance():
    """Test performance with larger volumes"""
    
    print("Testing large volume performance...")
    
    commands = [f"ls file{i}.txt" for i in range(50)]
    
    start_time = time.perf_counter()
    results = [lnx2ps(cmd) for cmd in commands]
    end_time = time.perf_counter()
    
    total_time = end_time - start_time
    avg_time_per_command = (total_time / len(commands)) * 1000
    
    print(f"   Processed {len(commands)} commands in {total_time:.3f}s")
    print(f"   Average time per command: {avg_time_per_command:.2f}ms")
    
    # Should complete reasonably quickly
    return avg_time_per_command < 100  # Less than 100ms per command

def test_translation_stats():
    """Test translation statistics collection"""
    
    # Generate some activity
    for i in range(10):
        lnx2ps(f"ls test{i}.txt")
    
    stats = get_translation_stats()
    
    assert isinstance(stats, dict), "Stats should be a dictionary"
    assert 'cache_stats' in stats, "Should include cache stats"
    
    print("✅ Translation statistics collection working")
    print(f"   Cache hit rate: {stats.get('cache_stats', {}).get('hit_rate', 0):.1%}")
    
    return True

if __name__ == "__main__":
    print("⚡ Complete Performance Testing")
    print("=" * 40)
    
    tests = [
        test_caching_performance,
        test_memory_cache_functionality,
        test_large_volume_performance,
        test_translation_stats
    ]
    
    results = [test() for test in tests]
    
    if all(results):
        print("\n🎉 All performance tests passed!")
    else:
        print("\n❌ Some performance tests need attention!")