#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import time
import psutil
import os
from typing import List
from memory_profiler import profile

from scalefc.util import flow_attribute_angle, flow_attribute_centroid_OD


# Original function
def _rearrange_flow_group_indices_original(OD: np.ndarray) -> List[int]:
    """Original rearrange the flow in OD matrix, and return a new OD matrix's indices.

    Args:
        OD (np.ndarray): OD matrix has 4 columns:  ox, oy, dx, dy.

    Returns:
        List[int]: rearrange indices
    """
    if np.ndim(OD) == 1:
        return [0]
    OD = OD.copy()  # copy it
    # 获取每一列的最小值
    max_values = np.max(OD, axis=0) - np.min(OD, axis=0)
    assert max_values.size == 4
    o_max = max(max_values[0], max_values[1])
    d_max = max(max_values[2], max_values[3])
    if o_max > d_max:
        # 交换OD矩阵的O点和D点坐标
        ox = OD[:, 0]
        oy = OD[:, 1]
        dx = OD[:, 2]
        dy = OD[:, 3]
        OD = np.column_stack((dx, dy, ox, oy))

    # 1. get centroid flow
    cf = flow_attribute_centroid_OD(OD)
    cf_ang = flow_attribute_angle(cf)
    # 2. assign new O point
    OD[:, [0, 1]] = cf[:2]
    # 3. calculate all angles
    ang = flow_attribute_angle(OD)
    # 4. get reverse flow angle
    cf_rev_ang = np.mod(cf_ang + np.pi, 2 * np.pi)
    # 5. calculate the sequence
    all_ang = np.append(ang, cf_rev_ang)
    res = np.argsort(all_ang).tolist()  # it's a list
    cf_index = res.index(len(all_ang) - 1)

    return res[cf_index + 1 :] + res[:cf_index]

# Optimized function
def _rearrange_flow_group_indices(OD: np.ndarray) -> List[int]:
    """Optimized rearrange the flow in OD matrix, and return a new OD matrix's indices.
    
    Optimizations:
    - Use ptp for efficient range calculation
    - Minimize array copies and intermediate variables
    - Optimize column swapping with advanced indexing
    - Use vectorized operations for angle calculations
    - Reduce memory allocations in sorting and indexing

    Args:
        OD (np.ndarray): OD matrix has 4 columns:  ox, oy, dx, dy.

    Returns:
        List[int]: rearrange indices
    """
    if np.ndim(OD) == 1:
        return [0]
    
    # Use ptp for efficient range calculation
    ranges = np.ptp(OD, axis=0)
    
    # Vectorized max operations
    o_max = np.max(ranges[:2])
    d_max = np.max(ranges[2:])
    
    # Conditional copy and swap - only when needed
    if o_max > d_max:
        # Use advanced indexing for efficient column swapping
        OD_work = OD[:, [2, 3, 0, 1]]
    else:
        OD_work = OD

    # 1. get centroid flow - inline calculation to avoid function call overhead
    cf = np.mean(OD_work, axis=0)
    
    # 2. calculate centroid flow angle - inline to avoid function overhead
    cf_vec = cf[2:] - cf[:2]
    cf_ang = np.arctan2(cf_vec[1], cf_vec[0])
    cf_ang = np.mod(cf_ang, 2 * np.pi)
    
    # 3. assign new O point and calculate angles in one operation
    # Create modified OD matrix with new origin points
    modified_OD = OD_work.copy()
    modified_OD[:, :2] = cf[:2]
    
    # Calculate vectors and angles vectorized
    vecs = modified_OD[:, 2:] - modified_OD[:, :2]
    ang = np.arctan2(vecs[:, 1], vecs[:, 0])
    ang = np.mod(ang, 2 * np.pi)
    
    # 4. get reverse flow angle
    cf_rev_ang = np.mod(cf_ang + np.pi, 2 * np.pi)
    
    # 5. calculate the sequence - use concatenate for better performance
    all_ang = np.concatenate([ang, [cf_rev_ang]])
    res = np.argsort(all_ang)
    
    # Find cf_index using numpy operations - more efficient than list.index()
    cf_index = np.where(res == len(all_ang) - 1)[0][0]
    
    # Use numpy slicing and concatenation, then convert to list
    result = np.concatenate([res[cf_index + 1:], res[:cf_index]])
    
    return result.tolist()

def measure_memory():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def run_performance_test():
    """Run comprehensive performance and memory tests."""
    # Test data sizes
    sizes = [10, 50, 100, 500, 1000, 2000, 4000, 6000, 10000]
    
    # Results storage
    original_times = []
    optimized_times = []
    original_memory = []
    optimized_memory = []
    
    print("Performance and Memory Test Results:")
    print("=" * 60)
    print(f"{'Size':<8} {'Original (ms)':<15} {'Optimized (ms)':<16} {'Speedup':<10} {'Mem Orig (MB)':<14} {'Mem Opt (MB)':<13} {'Mem Saved':<10}")
    print("-" * 60)
    
    for size in sizes:
        # Generate test data
        np.random.seed(42)
        test_data = np.random.rand(size, 4) * 100
        
        # Test original function
        start_mem = measure_memory()
        start_time = time.perf_counter()
        
        for _ in range(10):  # Run multiple times for better accuracy
            result_orig = _rearrange_flow_group_indices_original(test_data)
        
        orig_time = (time.perf_counter() - start_time) * 100  # Convert to ms
        orig_mem = measure_memory() - start_mem
        
        # Test optimized function
        start_mem = measure_memory()
        start_time = time.perf_counter()
        
        for _ in range(10):  # Run multiple times for better accuracy
            result_opt = _rearrange_flow_group_indices(test_data)
        
        opt_time = (time.perf_counter() - start_time) * 100  # Convert to ms
        opt_mem = measure_memory() - start_mem
        
        # Verify results are identical
        assert result_orig == result_opt, f"Results differ for size {size}!"
        
        # Store results
        original_times.append(orig_time)
        optimized_times.append(opt_time)
        original_memory.append(abs(orig_mem))
        optimized_memory.append(abs(opt_mem))
        
        # Calculate improvements
        speedup = orig_time / opt_time if opt_time > 0 else float('inf')
        mem_saved = ((orig_mem - opt_mem) / orig_mem * 100) if orig_mem != 0 else 0
        
        print(f"{size:<8} {orig_time:<15.2f} {opt_time:<16.2f} {speedup:<10.2f}x {abs(orig_mem):<14.2f} {abs(opt_mem):<13.2f} {mem_saved:<10.1f}%")
    
    return sizes, original_times, optimized_times, original_memory, optimized_memory

def test_correctness():
    """Test function correctness with various inputs."""
    print("\nCorrectness Tests:")
    print("=" * 30)
    
    # Test case 1: Single row
    test1 = np.array([1, 2, 3, 4])
    result1_orig = _rearrange_flow_group_indices_original(test1)
    result1_opt = _rearrange_flow_group_indices(test1)
    assert result1_orig == result1_opt == [0], "Single row test failed"
    print("✓ Single row test passed")
    
    # Test case 2: Small matrix
    test2 = np.array([[0, 0, 1, 1], [1, 0, 0, 1], [0, 1, 1, 0]])
    result2_orig = _rearrange_flow_group_indices_original(test2)
    result2_opt = _rearrange_flow_group_indices(test2)
    assert result2_orig == result2_opt, "Small matrix test failed"
    print("✓ Small matrix test passed")
    
    # Test case 3: Random matrices
    np.random.seed(123)
    for i in range(5):
        test_random = np.random.rand(2000, 4) * 50
        result_orig = _rearrange_flow_group_indices_original(test_random)
        result_opt = _rearrange_flow_group_indices(test_random)
        assert result_orig == result_opt, f"Random test {i+1} failed. {result_orig} != {result_opt}"
    print("✓ Random matrix tests passed")
    
    # Test case 4: Edge cases
    # All same values
    test_same = np.ones((10, 4))
    result_same_orig = _rearrange_flow_group_indices_original(test_same)
    result_same_opt = _rearrange_flow_group_indices(test_same)
    assert result_same_orig == result_same_opt, "Same values test failed"
    print("✓ Edge case tests passed")
    
    print("All correctness tests passed! ✓")

def create_visualization(sizes, original_times, optimized_times, original_memory, optimized_memory):
    """Create performance visualization plots."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
    
    # Time comparison
    ax1.plot(sizes, original_times, 'ro-', label='Original', linewidth=2, markersize=8)
    ax1.plot(sizes, optimized_times, 'bo-', label='Optimized', linewidth=2, markersize=8)
    ax1.set_xlabel('Input Size')
    ax1.set_ylabel('Execution Time (ms)')
    ax1.set_title('Execution Time Comparison')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    
    # Speedup
    speedups = [o/n if n > 0 else 0 for o, n in zip(original_times, optimized_times)]
    ax2.bar(range(len(sizes)), speedups, color='green', alpha=0.7)
    ax2.set_xlabel('Input Size')
    ax2.set_ylabel('Speedup Factor')
    ax2.set_title('Performance Speedup')
    ax2.set_xticks(range(len(sizes)))
    ax2.set_xticklabels(sizes)
    ax2.grid(True, alpha=0.3)
    
    # Memory comparison
    ax3.plot(sizes, original_memory, 'ro-', label='Original', linewidth=2, markersize=8)
    ax3.plot(sizes, optimized_memory, 'bo-', label='Optimized', linewidth=2, markersize=8)
    ax3.set_xlabel('Input Size')
    ax3.set_ylabel('Memory Usage (MB)')
    ax3.set_title('Memory Usage Comparison')
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Memory savings percentage
    mem_savings = [((o-n)/o*100) if o != 0 else 0 for o, n in zip(original_memory, optimized_memory)]
    colors = ['green' if x > 0 else 'red' for x in mem_savings]
    ax4.bar(range(len(sizes)), mem_savings, color=colors, alpha=0.7)
    ax4.set_xlabel('Input Size')
    ax4.set_ylabel('Memory Savings (%)')
    ax4.set_title('Memory Usage Reduction')
    ax4.set_xticks(range(len(sizes)))
    ax4.set_xticklabels(sizes)
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('optimization_results.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print("Flow Group Indices Optimization Test")
    print("=" * 50)
    
    # Run correctness tests
    test_correctness()
    
    # Run performance tests
    sizes, orig_times, opt_times, orig_mem, opt_mem = run_performance_test()
    
    # Create visualization
    create_visualization(sizes, orig_times, opt_times, orig_mem, opt_mem)
    
    # Summary
    avg_speedup = np.mean([o/n if n > 0 else 1 for o, n in zip(orig_times, opt_times)])
    avg_mem_savings = np.mean([((o-n)/o*100) if o != 0 else 0 for o, n in zip(orig_mem, opt_mem)])
    
    print(f"\nSummary:")
    print(f"Average speedup: {avg_speedup:.2f}x")
    print(f"Average memory savings: {avg_mem_savings:.1f}%")
    print(f"Visualization saved as 'optimization_results.png'")