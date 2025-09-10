#!/usr/bin/env python3
import multiprocessing as mp
import time
from storage_layout_extractor import extract_storage

def load_contracts():
    """Load contract bytecodes from files"""
    contracts = {}
    contract_files = ["vault.bin", "erc20.bin", "univ2pair.bin", "weth.bin"]
    
    for filename in contract_files:
        try:
            with open(f"contracts/{filename}", "r") as f:
                bytecode = f.readline().strip()
                contracts[filename.replace(".bin", "")] = bytecode
        except Exception as e:
            print(f"Error loading {filename}: {e}")
    
    return contracts

def process_contract(name, bytecode):
    """Process a single contract in a worker process"""
    pid = mp.current_process().pid
    print(f"[Worker {pid}] Processing {name}")
    
    try:
        start = time.time()
        layout = extract_storage(bytecode)
        elapsed = time.time() - start
        
        if layout:
            slots = [(f"slot_{x.index}", x.typ) for x in layout]
            print(f"[Worker {pid}] {name}: Found {len(slots)} storage slots in {elapsed:.3f}s")
            return name, slots
        else:
            print(f"[Worker {pid}] {name}: No storage slots found in {elapsed:.3f}s")
            return name, []
    except Exception as e:
        print(f"[Worker {pid}] {name}: Error - {e}")
        return name, f"Error: {e}"

def test_multiprocessing(num_workers=4):
    """Test storage extraction with multiple processes"""
    contracts = load_contracts()
    print(f"\n=== Testing {len(contracts)} contracts with {num_workers} workers ===\n")
    
    # Create a pool of worker processes
    with mp.Pool(processes=num_workers) as pool:
        # Process all contracts in parallel
        results = pool.starmap(process_contract, contracts.items())
    
    print("\n=== Results ===")
    for name, result in sorted(results):
        if isinstance(result, str) and result.startswith("Error"):
            print(f"{name}: {result}")
        else:
            print(f"{name}: {len(result) if result else 0} slots")
    
    return results

def stress_worker(args):
    """Worker function for stress test - must be at module level for pickling"""
    worker_id, test_code, iterations_per_worker = args
    successes = 0
    failures = 0
    
    for i in range(iterations_per_worker):
        try:
            layout = extract_storage(test_code)
            successes += 1
            if (i + 1) % 10 == 0:
                print(f"[Worker {worker_id}] Progress: {i+1}/{iterations_per_worker}")
        except Exception as e:
            failures += 1
            print(f"[Worker {worker_id}] Failed at iteration {i}: {e}")
    
    return worker_id, successes, failures

def stress_test(num_workers=20, num_iterations=100):
    """Stress test with many concurrent calls"""
    contracts = load_contracts()
    
    # Use vault contract for stress testing
    test_code = contracts.get("vault", "")
    if not test_code:
        print("Could not load vault contract for stress test")
        return False
    
    print(f"\n=== Stress test: {num_workers} workers, {num_iterations} total calls ===\n")
    
    iterations_per_worker = num_iterations // num_workers
    worker_args = [(i, test_code, iterations_per_worker) for i in range(num_workers)]
    
    start_time = time.time()
    with mp.Pool(processes=num_workers) as pool:
        results = pool.map(stress_worker, worker_args)
    elapsed = time.time() - start_time
    
    total_successes = sum(r[1] for r in results)
    total_failures = sum(r[2] for r in results)
    
    print(f"\n=== Stress test results ===")
    print(f"Total successes: {total_successes}")
    print(f"Total failures: {total_failures}")
    print(f"Success rate: {total_successes / (total_successes + total_failures) * 100:.1f}%")
    print(f"Total time: {elapsed:.2f}s")
    print(f"Throughput: {total_successes / elapsed:.1f} extractions/second")
    
    return total_failures == 0

def heavy_parallel_test(num_workers=20):
    """Test all contracts repeatedly in parallel - simulates heavy multiprocess env"""
    contracts = load_contracts()
    
    print(f"\n=== Heavy parallel test: {num_workers} workers processing all contracts 10 times ===\n")
    
    # Create work items: each contract 10 times
    work_items = []
    for i in range(10):
        for name, bytecode in contracts.items():
            work_items.append((f"{name}_{i}", bytecode))
    
    print(f"Processing {len(work_items)} total items with {num_workers} workers...")
    
    start_time = time.time()
    with mp.Pool(processes=num_workers) as pool:
        results = pool.starmap(process_contract, work_items)
    elapsed = time.time() - start_time
    
    # Count successes and failures
    successes = sum(1 for _, result in results if not (isinstance(result, str) and result.startswith("Error")))
    failures = len(results) - successes
    
    print(f"\n=== Heavy parallel test results ===")
    print(f"Total items processed: {len(results)}")
    print(f"Successes: {successes}")
    print(f"Failures: {failures}")
    print(f"Total time: {elapsed:.2f}s")
    print(f"Throughput: {successes / elapsed:.1f} extractions/second")
    
    return failures == 0

if __name__ == "__main__":
    # Test basic multiprocessing
    print("Testing basic multiprocessing functionality...")
    test_multiprocessing(num_workers=4)
    
    # Run stress test
    print("\nRunning stress test...")
    stress_success = stress_test(num_workers=20, num_iterations=200)
    
    # Run heavy parallel test
    print("\nRunning heavy parallel test...")
    heavy_success = heavy_parallel_test(num_workers=20)
    
    if stress_success and heavy_success:
        print("\n✅ All tests passed! The multiprocessing fix is working correctly in heavy multiprocess environments.")
    else:
        print("\n❌ Some tests failed. There may still be multiprocessing issues.")