#!/usr/bin/env python3
import numpy as np
import matplotlib.pyplot as plt
import time
import psutil
import os
from typing import List, Optional
from memory_profiler import profile
from joblib import Parallel, delayed
from scalefc.util import flow_neighbor_knn_indices,flow_attribute_number,flow_indicator_rmse_OD_distance

# Original function
def _calculate_flow_group_local_density_original(
    OD: np.ndarray, k: int, n_jobs: Optional[int] = None
) -> List[float]:
    """Original calculate flow group local density function.
    
    Args:
        OD (np.ndarray): OD matrix with 4 columns: ox, oy, dx, dy
        k (int): Number of nearest neighbors
        n_jobs (Optional[int]): Number of parallel jobs
        
    Returns:
        List[float]: Local densities for each flow
    """
    knn_idx = flow_neighbor_knn_indices(OD, k)

    if not n_jobs:
        local_densities = []
        for i in range(flow_attribute_number(OD)):
            ll = knn_idx[i].tolist()
            ll.append(i)
            # get cluster
            sub_od = OD[ll, :]
            # calculate
            cur_indicator = flow_indicator_rmse_OD_distance(sub_od)
            local_densities.append(cur_indicator)

        return local_densities
    else:

        def process_batch(batch_indices):
            batch_results = []
            for i in batch_indices:
                ll = knn_idx[i].tolist()
                ll.append(i)
                sub_od = OD[ll, :]
                cur_indicator = flow_indicator_rmse_OD_distance(sub_od)
                batch_results.append(cur_indicator)
            return batch_results

        num_flows = flow_attribute_number(OD)
        indices = np.arange(num_flows)
        batch_size = 4
        batches = [indices[i : i + batch_size] for i in range(0, num_flows, batch_size)]

        results = Parallel(n_jobs=n_jobs, backend="threading")(
            delayed(process_batch)(batch) for batch in batches
        )

        # Flatten the list of results
        local_densities = [item for sublist in results for item in sublist]

        return local_densities

# Optimized function
def _calculate_flow_group_local_density(
    OD: np.ndarray, k: int, n_jobs: Optional[int] = None
) -> List[float]:
    """Optimized calculate flow group local density function.
    
    Optimizations:
    - Vectorized operations where possible
    - More efficient array indexing and slicing
    - Reduced memory allocations through pre-allocation
    - Optimized parallel processing with better batch sizing
    - Eliminated unnecessary list conversions and appends
    - Used advanced numpy indexing for better performance
    
    Args:
        OD (np.ndarray): OD matrix with 4 columns: ox, oy, dx, dy
        k (int): Number of nearest neighbors
        n_jobs (Optional[int]): Number of parallel jobs
        
    Returns:
        List[float]: Local densities for each flow
    """
    knn_idx = flow_neighbor_knn_indices(OD, k)
    num_flows = flow_attribute_number(OD)
    
    if not n_jobs:
        # Pre-allocate result array for better memory efficiency
        local_densities = np.empty(num_flows, dtype=np.float64)
        
        # Vectorized processing where possible
        for i in range(num_flows):
            # Use numpy concatenate instead of list operations
            indices = np.concatenate([knn_idx[i], [i]])
            # Direct array indexing - more efficient than list slicing
            sub_od = OD[indices]
            # Calculate and store directly
            local_densities[i] = flow_indicator_rmse_OD_distance(sub_od)
        
        return local_densities.tolist()
    else:
        def process_batch_optimized(batch_indices: np.ndarray) -> np.ndarray:
            """Optimized batch processing function."""
            batch_size = len(batch_indices)
            batch_results = np.empty(batch_size, dtype=np.float64)
            
            for idx, i in enumerate(batch_indices):
                # Use numpy operations instead of list operations
                indices = np.concatenate([knn_idx[i], [i]])
                sub_od = OD[indices]
                batch_results[idx] = flow_indicator_rmse_OD_distance(sub_od)
            
            return batch_results

        # Calculate optimal batch size based on data size and available cores
        if n_jobs == -1:
            n_jobs = os.cpu_count()
        elif n_jobs is None:
            n_jobs = 1
            
        # Dynamic batch sizing for better load balancing
        optimal_batch_size = max(1, num_flows // (n_jobs * 4))  # 4x more batches than cores
        optimal_batch_size = min(optimal_batch_size, 64)  # Cap at 64 for memory efficiency
        
        # Create batches using array slicing instead of list comprehension
        indices = np.arange(num_flows)
        num_batches = (num_flows + optimal_batch_size - 1) // optimal_batch_size
        batches = np.array_split(indices, num_batches)
        
        # Use "threads" backend for I/O bound operations, "loky" for CPU bound
        backend = "threading" if optimal_batch_size < 16 else "loky"
        
        results = Parallel(n_jobs=n_jobs, backend=backend)(
            delayed(process_batch_optimized)(batch) for batch in batches
        )

        # Efficiently concatenate results using numpy
        local_densities = np.concatenate(results)
        
        return local_densities.tolist()

def measure_memory():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def run_performance_test():
    """Run comprehensive performance and memory tests."""
    # Test configurations: (data_size, k_value, n_jobs)
    test_configs = [
        (50, 5, None),
        (100, 5, None),
        (200, 5, None),
        (50, 5, 2),
        (100, 5, 2),
        (200, 5, 2),
        (100, 10, None),
        (100, 10, 2),
    ]
    
    results = []
    
    print("Performance and Memory Test Results:")
    print("=" * 90)
    print(f"{'Size':<6} {'k':<3} {'Jobs':<6} {'Original (ms)':<15} {'Optimized (ms)':<16} {'Speedup':<10} {'Mem Orig (MB)':<14} {'Mem Opt (MB)':<13} {'Mem Saved':<10}")
    print("-" * 90)
    
    for size, k, n_jobs in test_configs:
        # Generate test data
        np.random.seed(42)
        test_data = np.random.rand(size, 4) * 100
        
        # Test original function
        start_mem = measure_memory()
        start_time = time.perf_counter()
        
        result_orig = _calculate_flow_group_local_density_original(test_data, k, n_jobs)
        
        orig_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
        orig_mem = measure_memory() - start_mem
        
        # Test optimized function
        start_mem = measure_memory()
        start_time = time.perf_counter()
        
        result_opt = _calculate_flow_group_local_density(test_data, k, n_jobs)
        
        opt_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
        opt_mem = measure_memory() - start_mem
        
        # Verify results are approximately equal (allowing for floating point differences)
        assert len(result_orig) == len(result_opt), f"Result lengths differ for config {size}, {k}, {n_jobs}!"
        for i, (o, n) in enumerate(zip(result_orig, result_opt)):
            assert abs(o - n) < 1e-10, f"Results differ at index {i} for config {size}, {k}, {n_jobs}!"
        
        # Calculate improvements
        speedup = orig_time / opt_time if opt_time > 0 else float('inf')
        mem_saved = ((orig_mem - opt_mem) / orig_mem * 100) if orig_mem != 0 else 0
        
        # Store results
        results.append({
            'size': size,
            'k': k,
            'n_jobs': n_jobs,
            'orig_time': orig_time,
            'opt_time': opt_time,
            'speedup': speedup,
            'orig_mem': abs(orig_mem),
            'opt_mem': abs(opt_mem),
            'mem_saved': mem_saved
        })
        
        jobs_str = str(n_jobs) if n_jobs else "None"
        print(f"{size:<6} {k:<3} {jobs_str:<6} {orig_time:<15.2f} {opt_time:<16.2f} {speedup:<10.2f}x {abs(orig_mem):<14.2f} {abs(opt_mem):<13.2f} {mem_saved:<10.1f}%")
    
    return results

def test_correctness():
    """Test function correctness with various inputs."""
    print("\nCorrectness Tests:")
    print("=" * 30)
    
    # Test case 1: Small matrix, no parallel
    np.random.seed(123)
    test1 = np.random.rand(10, 4) * 50
    result1_orig = _calculate_flow_group_local_density_original(test1, 3, None)
    result1_opt = _calculate_flow_group_local_density(test1, 3, None)
    
    assert len(result1_orig) == len(result1_opt), "Length mismatch in test 1"
    for i, (o, n) in enumerate(zip(result1_orig, result1_opt)):
        assert abs(o - n) < 1e-10, f"Value mismatch at index {i} in test 1"
    print("✓ Small matrix (no parallel) test passed")
    
    # Test case 2: Small matrix, with parallel
    result2_orig = _calculate_flow_group_local_density_original(test1, 3, 2)
    result2_opt = _calculate_flow_group_local_density(test1, 3, 2)
    
    assert len(result2_orig) == len(result2_opt), "Length mismatch in test 2"
    for i, (o, n) in enumerate(zip(result2_orig, result2_opt)):
        assert abs(o - n) < 1e-10, f"Value mismatch at index {i} in test 2"
    print("✓ Small matrix (with parallel) test passed")
    
    # Test case 3: Different k values
    for k in [2, 5, 8]:
        result_orig = _calculate_flow_group_local_density_original(test1, k, None)
        result_opt = _calculate_flow_group_local_density(test1, k, None)
        
        assert len(result_orig) == len(result_opt), f"Length mismatch for k={k}"
        for i, (o, n) in enumerate(zip(result_orig, result_opt)):
            assert abs(o - n) < 1e-10, f"Value mismatch at index {i} for k={k}"
    print("✓ Different k values test passed")
    
    print("All correctness tests passed! ✓")

def create_visualization(results):
    """Create performance visualization plots."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Separate results by parallel vs non-parallel
    serial_results = [r for r in results if r['n_jobs'] is None]
    parallel_results = [r for r in results if r['n_jobs'] is not None]
    
    # Plot 1: Execution time comparison (serial)
    if serial_results:
        sizes = [r['size'] for r in serial_results]
        orig_times = [r['orig_time'] for r in serial_results]
        opt_times = [r['opt_time'] for r in serial_results]
        
        ax1.plot(sizes, orig_times, 'ro-', label='Original', linewidth=2, markersize=8)
        ax1.plot(sizes, opt_times, 'bo-', label='Optimized', linewidth=2, markersize=8)
        ax1.set_xlabel('Input Size')
        ax1.set_ylabel('Execution Time (ms)')
        ax1.set_title('Execution Time Comparison (Serial)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        ax1.set_yscale('log')
    
    # Plot 2: Speedup comparison
    speedups = [r['speedup'] for r in results]
    labels = [f"S{r['size']}_k{r['k']}_j{r['n_jobs']}" for r in results]
    
    colors = ['green' if r['n_jobs'] is None else 'blue' for r in results]
    bars = ax2.bar(range(len(speedups)), speedups, color=colors, alpha=0.7)
    ax2.set_xlabel('Test Configuration')
    ax2.set_ylabel('Speedup Factor')
    ax2.set_title('Performance Speedup by Configuration')
    ax2.set_xticks(range(len(labels)))
    ax2.set_xticklabels(labels, rotation=45, ha='right')
    ax2.grid(True, alpha=0.3)
    
    # Add legend for colors
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor='green', alpha=0.7, label='Serial'),
                      Patch(facecolor='blue', alpha=0.7, label='Parallel')]
    ax2.legend(handles=legend_elements)
    
    # Plot 3: Memory usage comparison
    orig_mem = [r['orig_mem'] for r in results]
    opt_mem = [r['opt_mem'] for r in results]
    
    x = np.arange(len(results))
    width = 0.35
    
    ax3.bar(x - width/2, orig_mem, width, label='Original', color='red', alpha=0.7)
    ax3.bar(x + width/2, opt_mem, width, label='Optimized', color='blue', alpha=0.7)
    ax3.set_xlabel('Test Configuration')
    ax3.set_ylabel('Memory Usage (MB)')
    ax3.set_title('Memory Usage Comparison')
    ax3.set_xticks(x)
    ax3.set_xticklabels(labels, rotation=45, ha='right')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Memory savings
    mem_savings = [r['mem_saved'] for r in results]
    colors = ['green' if x > 0 else 'red' for x in mem_savings]
    
    ax4.bar(range(len(mem_savings)), mem_savings, color=colors, alpha=0.7)
    ax4.set_xlabel('Test Configuration')
    ax4.set_ylabel('Memory Savings (%)')
    ax4.set_title('Memory Usage Reduction')
    ax4.set_xticks(range(len(labels)))
    ax4.set_xticklabels(labels, rotation=45, ha='right')
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('flow_density_optimization_results.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print("Flow Group Local Density Optimization Test")
    print("=" * 60)
    
    # Run correctness tests
    test_correctness()
    
    # Run performance tests
    results = run_performance_test()
    
    # Create visualization
    create_visualization(results)
    
    # Summary
    speedups = [r['speedup'] for r in results]
    mem_savings = [r['mem_saved'] for r in results]
    
    avg_speedup = np.mean(speedups)
    avg_mem_savings = np.mean(mem_savings)
    
    print(f"\nSummary:")
    print(f"Average speedup: {avg_speedup:.2f}x")
    print(f"Average memory savings: {avg_mem_savings:.1f}%")
    print(f"Best speedup: {max(speedups):.2f}x")
    print(f"Best memory savings: {max(mem_savings):.1f}%")
    print(f"Visualization saved as 'flow_density_optimization_results.png'")