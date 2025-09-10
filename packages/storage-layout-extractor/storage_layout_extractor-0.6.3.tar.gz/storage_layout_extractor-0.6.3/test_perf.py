#!/usr/bin/env python3
"""Test performance degradation with different numbers of processes"""

import multiprocessing as mp
import time
import storage_layout_extractor as sle
import statistics

# Use the actual working contract bytecode
with open("contracts/vault.bin", "r") as f:
    BYTECODE = f.readline().strip()

def worker_extract(worker_id, iterations):
    """Worker function that does multiple extractions"""
    times = []
    pid = mp.current_process().pid
    
    for i in range(iterations):
        start = time.time()
        try:
            layout = sle.extract_storage(BYTECODE, timeout_secs=10)
            elapsed = time.time() - start
            times.append(elapsed)
        except Exception as e:
            print(f"[Worker {worker_id}, PID {pid}] Failed: {e}")
            times.append(None)
    
    return worker_id, times

def test_with_n_processes(n_processes, iterations_per_worker=5):
    """Test with a specific number of processes"""
    print(f"\n=== Testing with {n_processes} processes ===")
    
    start_time = time.time()
    
    with mp.Pool(processes=n_processes) as pool:
        jobs = []
        for worker_id in range(n_processes):
            job = pool.apply_async(worker_extract, (worker_id, iterations_per_worker))
            jobs.append(job)
        
        results = []
        for job in jobs:
            try:
                result = job.get(timeout=60)
                results.append(result)
            except mp.TimeoutError:
                print(f"❌ TIMEOUT with {n_processes} processes!")
                pool.terminate()
                pool.join()
                return None
    
    total_time = time.time() - start_time
    
    # Collect all times
    all_times = []
    for worker_id, times in results:
        all_times.extend([t for t in times if t is not None])
    
    if all_times:
        avg_time = statistics.mean(all_times)
        median_time = statistics.median(all_times)
        min_time = min(all_times)
        max_time = max(all_times)
        
        print(f"Total time: {total_time:.2f}s")
        print(f"Extraction times - Avg: {avg_time:.3f}s, Median: {median_time:.3f}s, Min: {min_time:.3f}s, Max: {max_time:.3f}s")
        print(f"Throughput: {len(all_times)/total_time:.1f} extractions/second")
        
        return {
            'n_processes': n_processes,
            'total_time': total_time,
            'avg_time': avg_time,
            'median_time': median_time,
            'throughput': len(all_times)/total_time
        }
    
    return None

if __name__ == "__main__":
    print("Testing performance scaling with different numbers of processes...")
    print("Using vault.bin (complex contract) for testing")
    
    # Test with different numbers of processes
    process_counts = [1, 2, 4, 8, 12, 14, 16, 20]
    results = []
    
    for n in process_counts:
        result = test_with_n_processes(n, iterations_per_worker=3)
        if result:
            results.append(result)
        time.sleep(1)  # Brief pause between tests
    
    # Show summary
    print("\n" + "="*60)
    print("PERFORMANCE SUMMARY")
    print("="*60)
    print(f"{'Processes':<12} {'Avg Time':<12} {'Median Time':<12} {'Throughput':<15} {'Slowdown'}")
    print("-"*60)
    
    if results:
        baseline_avg = results[0]['avg_time']  # Single process baseline
        for r in results:
            slowdown = r['avg_time'] / baseline_avg
            print(f"{r['n_processes']:<12} {r['avg_time']:<12.3f} {r['median_time']:<12.3f} {r['throughput']:<15.1f} {slowdown:.2f}x")
    
    print("\n📊 If avg/median times increase significantly with more processes,")
    print("   there's contention or resource competition causing the slowdown.")