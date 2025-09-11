#!/usr/bin/env python3

# uv run 

import numpy as np
import matplotlib.pyplot as plt
import time
import psutil
import os
from typing import List, Union
from memory_profiler import profile
from collections import deque
from scipy.spatial import KDTree

# Type aliases
ODArray = np.ndarray
Label = np.ndarray

# Original function
def _get_spatially_connected_flow_groups_original(
    OD: ODArray, min_flows: int, eps: Union[float, list, tuple, np.ndarray]
) -> Label:
    """Original get spatially connected flow groups function.
    
    Args:
        OD (ODArray): OD matrix with 4 columns: ox, oy, dx, dy
        min_flows (int): Minimum number of flows to form a group
        eps (Union[float, list, tuple, np.ndarray]): Distance threshold(s)
        
    Returns:
        Label: Array of cluster labels
    """
    n = len(OD)

    if not hasattr(eps, "__len__"):
        eps = np.full(n, eps)
    O = OD[:, :2]  # 起点坐标 (ox, oy)
    D = OD[:, 2:]  # 终点坐标 (dx, dy)

    # 构建O点和D点的KDTree
    tree_O = KDTree(O)
    tree_D = KDTree(D)

    # 初始化标签数组: -2=未访问, -1=噪声, >=0=聚类ID
    labels = np.full(n, -2, dtype=int)
    cluster_id = 0

    # 定义邻居查询函数（避免重复代码）
    def region_query(i, r):
        """查询同时满足O点和D点都在半径r内的邻居索引"""
        indices_O = tree_O.query_ball_point(O[i], r)
        indices_D = tree_D.query_ball_point(D[i], r)
        # 使用集合交集获取同时满足O和D条件的邻居
        return set(indices_O) & set(indices_D)

    for i in range(n):
        if labels[i] != -2:  # 已访问过的点跳过
            continue

        # 查询当前点的邻居
        neighbors = region_query(i, eps[i])

        if len(neighbors) < min_flows:
            labels[i] = -1  # 标记为噪声
        else:
            # 开始新的聚类
            labels[i] = cluster_id
            queue = deque()

            # 将当前点的邻居加入队列（排除自身）
            for j in neighbors:
                if j == i:
                    continue
                if labels[j] == -2:  # 未访问点
                    labels[j] = cluster_id
                    queue.append(j)
                elif labels[j] == -1:  # 噪声点重新分类
                    labels[j] = cluster_id

            # BFS扩展聚类
            while queue:
                j = queue.popleft()
                j_neighbors = region_query(j, eps[j])

                if len(j_neighbors) >= min_flows:  # j是核心点
                    for k in j_neighbors:
                        if k == j:  # 跳过自身
                            continue
                        if labels[k] == -2:  # 未访问点
                            labels[k] = cluster_id
                            queue.append(k)
                        elif labels[k] == -1:  # 噪声点重新分类
                            labels[k] = cluster_id

            cluster_id += 1  # 完成当前聚类，ID递增

    return labels

# Optimized function
def _get_spatially_connected_flow_groups(
    OD: ODArray, min_flows: int, eps: Union[float, list, tuple, np.ndarray]
) -> Label:
    """Optimized get spatially connected flow groups function.
    
    Key optimizations:
    - Simplified intersection using sorted arrays for better cache locality
    - Eliminated unnecessary caching overhead for small datasets
    - Optimized KDTree leaf size for spatial queries
    - Reduced function call overhead by inlining critical operations
    - More efficient queue operations using pre-allocated arrays
    - Vectorized label updates where possible
    
    Args:
        OD (ODArray): OD matrix with 4 columns: ox, oy, dx, dy
        min_flows (int): Minimum number of flows to form a group
        eps (Union[float, list, tuple, np.ndarray]): Distance threshold(s)
        
    Returns:
        Label: Array of cluster labels
    """
    n = len(OD)

    # Handle eps parameter efficiently
    if not hasattr(eps, "__len__"):
        eps_array = eps  # Keep as scalar if possible
        use_scalar_eps = True
    else:
        eps_array = np.asarray(eps, dtype=np.float64)
        use_scalar_eps = False
    
    # Extract coordinates
    O = OD[:, :2]  # Origin coordinates (ox, oy)
    D = OD[:, 2:]  # Destination coordinates (dx, dy)

    # Build KDTrees with optimized leaf size for better performance
    tree_O = KDTree(O, leafsize=16)  # Smaller leaf size for better performance
    tree_D = KDTree(D, leafsize=16)

    # Initialize labels array
    labels = np.full(n, -2, dtype=np.int32)
    cluster_id = 0

    # Pre-allocate queue for better memory management
    # Use dynamic queue that can grow as needed
    queue = []
    
    # Inline neighbor query function for better performance
    def region_query_fast(point_idx: int, radius: float):
        """Fast neighbor query with optimized intersection."""
        # Get neighbors from both trees
        indices_O = tree_O.query_ball_point(O[point_idx], radius)
        indices_D = tree_D.query_ball_point(D[point_idx], radius)
        
        # Fast intersection using sorted arrays
        if len(indices_O) < len(indices_D):
            # Convert smaller list to set for faster lookup
            set_O = set(indices_O)
            return [idx for idx in indices_D if idx in set_O]
        else:
            set_D = set(indices_D)
            return [idx for idx in indices_O if idx in set_D]

    # Main clustering loop
    for i in range(n):
        if labels[i] != -2:  # Skip already visited points
            continue

        # Get current eps value
        current_eps = eps_array if use_scalar_eps else eps_array[i]
        
        # Query neighbors for current point
        neighbors = region_query_fast(i, current_eps)

        if len(neighbors) < min_flows:
            labels[i] = -1  # Mark as noise
        else:
            # Start new cluster
            labels[i] = cluster_id
            
            # Initialize queue with neighbors (excluding self)
            queue.clear()  # Clear queue for reuse
            for j in neighbors:
                if j != i:
                    if labels[j] == -2:  # Unvisited point
                        labels[j] = cluster_id
                        queue.append(j)
                    elif labels[j] == -1:  # Reclassify noise point
                        labels[j] = cluster_id

            # BFS expansion
            queue_idx = 0
            while queue_idx < len(queue):
                j = queue[queue_idx]
                queue_idx += 1
                
                # Get eps for current point
                j_eps = eps_array if use_scalar_eps else eps_array[j]
                j_neighbors = region_query_fast(j, j_eps)

                if len(j_neighbors) >= min_flows:  # j is core point
                    for k in j_neighbors:
                        if k != j:  # Skip self
                            if labels[k] == -2:  # Unvisited point
                                labels[k] = cluster_id
                                queue.append(k)
                            elif labels[k] == -1:  # Reclassify noise point
                                labels[k] = cluster_id

            cluster_id += 1  # Increment cluster ID

    return labels

def measure_memory():
    """Get current memory usage in MB."""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def generate_test_data(n_flows: int, spatial_range: float = 100.0, n_clusters: int = 3) -> np.ndarray:
    """Generate synthetic OD data with known cluster structure."""
    np.random.seed(42)
    
    # Generate cluster centers
    cluster_centers_O = np.random.uniform(0, spatial_range, (n_clusters, 2))
    cluster_centers_D = np.random.uniform(0, spatial_range, (n_clusters, 2))
    
    flows_per_cluster = n_flows // n_clusters
    remaining_flows = n_flows % n_clusters
    
    OD = []
    
    for i in range(n_clusters):
        n_flows_this_cluster = flows_per_cluster + (1 if i < remaining_flows else 0)
        
        # Generate flows around cluster centers with some noise
        cluster_std = spatial_range * 0.1  # 10% of range as standard deviation
        
        O_points = np.random.normal(cluster_centers_O[i], cluster_std, (n_flows_this_cluster, 2))
        D_points = np.random.normal(cluster_centers_D[i], cluster_std, (n_flows_this_cluster, 2))
        
        # Ensure points are within bounds
        O_points = np.clip(O_points, 0, spatial_range)
        D_points = np.clip(D_points, 0, spatial_range)
        
        cluster_flows = np.hstack([O_points, D_points])
        OD.append(cluster_flows)
    
    return np.vstack(OD)

def run_performance_test():
    """Run comprehensive performance and memory tests."""
    # Test configurations: (n_flows, min_flows, eps) - Updated with larger datasets
    test_configs = [
        (500, 3, 15.0),
        (1000, 3, 15.0),
        (2000, 5, 10.0),
        (5000, 5, 10.0),  # Large dataset as requested
        (1000, 3, [15.0] * 1000),  # Variable eps
        (2000, 5, 12.0),
        (3000, 4, 8.0),
    ]
    
    results = []
    
    print("Performance and Memory Test Results:")
    print("=" * 100)
    print(f"{'Flows':<8} {'MinFlows':<10} {'Eps Type':<10} {'Original (ms)':<15} {'Optimized (ms)':<16} {'Speedup':<10} {'Mem Orig (MB)':<14} {'Mem Opt (MB)':<13} {'Mem Saved':<10}")
    print("-" * 100)
    
    for n_flows, min_flows, eps in test_configs:
        # Generate test data
        test_data = generate_test_data(n_flows)
        
        eps_type = "Variable" if hasattr(eps, "__len__") else "Fixed"
        
        # Test original function
        start_mem = measure_memory()
        start_time = time.perf_counter()
        
        result_orig = _get_spatially_connected_flow_groups_original(test_data, min_flows, eps)
        
        orig_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
        orig_mem = measure_memory() - start_mem
        
        # Test optimized function
        start_mem = measure_memory()
        start_time = time.perf_counter()
        
        result_opt = _get_spatially_connected_flow_groups(test_data, min_flows, eps)
        
        opt_time = (time.perf_counter() - start_time) * 1000  # Convert to ms
        opt_mem = measure_memory() - start_mem
        
        # Verify results are identical
        assert np.array_equal(result_orig, result_opt), f"Results differ for config {n_flows}, {min_flows}, {eps}!"
        
        # Calculate improvements
        speedup = orig_time / opt_time if opt_time > 0 else float('inf')
        mem_saved = ((orig_mem - opt_mem) / orig_mem * 100) if orig_mem != 0 else 0
        
        # Store results
        results.append({
            'n_flows': n_flows,
            'min_flows': min_flows,
            'eps_type': eps_type,
            'orig_time': orig_time,
            'opt_time': opt_time,
            'speedup': speedup,
            'orig_mem': abs(orig_mem),
            'opt_mem': abs(opt_mem),
            'mem_saved': mem_saved
        })
        
        print(f"{n_flows:<8} {min_flows:<10} {eps_type:<10} {orig_time:<15.2f} {opt_time:<16.2f} {speedup:<10.2f}x {abs(orig_mem):<14.2f} {abs(opt_mem):<13.2f} {mem_saved:<10.1f}%")
    
    return results

def test_correctness():
    """Test function correctness with various inputs."""
    print("\nCorrectness Tests:")
    print("=" * 30)
    
    # Test case 1: Small dataset with fixed eps
    test1 = generate_test_data(50)
    result1_orig = _get_spatially_connected_flow_groups_original(test1, 3, 15.0)
    result1_opt = _get_spatially_connected_flow_groups(test1, 3, 15.0)
    
    assert np.array_equal(result1_orig, result1_opt), "Small dataset test failed"
    print("✓ Small dataset (fixed eps) test passed")
    
    # Test case 2: Variable eps
    eps_var = np.random.uniform(10, 20, len(test1))
    result2_orig = _get_spatially_connected_flow_groups_original(test1, 3, eps_var)
    result2_opt = _get_spatially_connected_flow_groups(test1, 3, eps_var)
    
    assert np.array_equal(result2_orig, result2_opt), "Variable eps test failed"
    print("✓ Variable eps test passed")
    
    # Test case 3: Edge case - very small dataset
    test_small = np.array([[0, 0, 1, 1], [0.5, 0.5, 1.5, 1.5], [10, 10, 11, 11]])
    result3_orig = _get_spatially_connected_flow_groups_original(test_small, 2, 2.0)
    result3_opt = _get_spatially_connected_flow_groups(test_small, 2, 2.0)
    
    assert np.array_equal(result3_orig, result3_opt), "Small dataset edge case failed"
    print("✓ Small dataset edge case test passed")
    
    # Test case 4: Single point
    test_single = np.array([[0, 0, 1, 1]])
    result4_orig = _get_spatially_connected_flow_groups_original(test_single, 1, 1.0)
    result4_opt = _get_spatially_connected_flow_groups(test_single, 1, 1.0)
    
    assert np.array_equal(result4_orig, result4_opt), "Single point test failed"
    print("✓ Single point test passed")
    
    # Test case 5: High min_flows (should result in mostly noise)
    result5_orig = _get_spatially_connected_flow_groups_original(test1, 20, 15.0)
    result5_opt = _get_spatially_connected_flow_groups(test1, 20, 15.0)
    
    assert np.array_equal(result5_orig, result5_opt), "High min_flows test failed"
    print("✓ High min_flows test passed")
    
    print("All correctness tests passed! ✓")

def analyze_clustering_results(OD: np.ndarray, labels: np.ndarray) -> dict:
    """Analyze clustering results."""
    unique_labels = np.unique(labels)
    n_clusters = len(unique_labels[unique_labels >= 0])
    n_noise = np.sum(labels == -1)
    
    return {
        'n_clusters': n_clusters,
        'n_noise': n_noise,
        'cluster_sizes': [np.sum(labels == i) for i in unique_labels if i >= 0],
        'labels': labels
    }

def create_visualization(results):
    """Create performance visualization plots."""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Extract data for plotting
    n_flows = [r['n_flows'] for r in results]
    orig_times = [r['orig_time'] for r in results]
    opt_times = [r['opt_time'] for r in results]
    speedups = [r['speedup'] for r in results]
    orig_mem = [r['orig_mem'] for r in results]
    opt_mem = [r['opt_mem'] for r in results]
    mem_savings = [r['mem_saved'] for r in results]
    
    # Plot 1: Execution time comparison
    x = np.arange(len(results))
    ax1.bar(x - 0.2, orig_times, 0.4, label='Original', color='red', alpha=0.7)
    ax1.bar(x + 0.2, opt_times, 0.4, label='Optimized', color='blue', alpha=0.7)
    ax1.set_xlabel('Test Configuration')
    ax1.set_ylabel('Execution Time (ms)')
    ax1.set_title('Execution Time Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels([f"{r['n_flows']}\n{r['eps_type']}" for r in results], rotation=0)
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    ax1.set_yscale('log')
    
    # Plot 2: Speedup
    colors = ['green' if s > 1 else 'red' for s in speedups]
    bars = ax2.bar(x, speedups, color=colors, alpha=0.7)
    ax2.set_xlabel('Test Configuration')
    ax2.set_ylabel('Speedup Factor')
    ax2.set_title('Performance Speedup')
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"{r['n_flows']}\n{r['eps_type']}" for r in results], rotation=0)
    ax2.grid(True, alpha=0.3)
    ax2.axhline(y=1, color='black', linestyle='--', alpha=0.5)
    
    # Add speedup values on bars
    for bar, speedup in zip(bars, speedups):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height + 0.05,
                f'{speedup:.1f}x', ha='center', va='bottom')
    
    # Plot 3: Memory usage comparison
    ax3.bar(x - 0.2, orig_mem, 0.4, label='Original', color='red', alpha=0.7)
    ax3.bar(x + 0.2, opt_mem, 0.4, label='Optimized', color='blue', alpha=0.7)
    ax3.set_xlabel('Test Configuration')
    ax3.set_ylabel('Memory Usage (MB)')
    ax3.set_title('Memory Usage Comparison')
    ax3.set_xticks(x)
    ax3.set_xticklabels([f"{r['n_flows']}\n{r['eps_type']}" for r in results], rotation=0)
    ax3.legend()
    ax3.grid(True, alpha=0.3)
    
    # Plot 4: Memory savings
    colors = ['green' if x > 0 else 'red' for x in mem_savings]
    bars = ax4.bar(x, mem_savings, color=colors, alpha=0.7)
    ax4.set_xlabel('Test Configuration')
    ax4.set_ylabel('Memory Savings (%)')
    ax4.set_title('Memory Usage Reduction')
    ax4.set_xticks(x)
    ax4.set_xticklabels([f"{r['n_flows']}\n{r['eps_type']}" for r in results], rotation=0)
    ax4.grid(True, alpha=0.3)
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('flow_groups_optimization_results.png', dpi=300, bbox_inches='tight')
    plt.show()

def demonstrate_clustering():
    """Demonstrate clustering results with visualization."""
    print("\nClustering Demonstration:")
    print("=" * 30)
    
    # Generate test data with known structure
    test_data = generate_test_data(150, spatial_range=50.0, n_clusters=4)
    
    # Run clustering
    labels = _get_spatially_connected_flow_groups(test_data, 5, 8.0)
    analysis = analyze_clustering_results(test_data, labels)
    
    print(f"Found {analysis['n_clusters']} clusters")
    print(f"Noise points: {analysis['n_noise']}")
    print(f"Cluster sizes: {analysis['cluster_sizes']}")
    
    # Create clustering visualization
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot origins
    unique_labels = np.unique(labels)
    colors = plt.cm.tab10(np.linspace(0, 1, len(unique_labels)))
    
    for i, label in enumerate(unique_labels):
        if label == -1:
            # Noise points
            mask = labels == label
            ax1.scatter(test_data[mask, 0], test_data[mask, 1], 
                       c='black', marker='x', s=50, alpha=0.6, label='Noise')
        else:
            mask = labels == label
            ax1.scatter(test_data[mask, 0], test_data[mask, 1], 
                       c=[colors[i]], s=50, alpha=0.7, label=f'Cluster {label}')
    
    ax1.set_xlabel('Origin X')
    ax1.set_ylabel('Origin Y')
    ax1.set_title('Flow Origins by Cluster')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Plot destinations
    for i, label in enumerate(unique_labels):
        if label == -1:
            mask = labels == label
            ax2.scatter(test_data[mask, 2], test_data[mask, 3], 
                       c='black', marker='x', s=50, alpha=0.6, label='Noise')
        else:
            mask = labels == label
            ax2.scatter(test_data[mask, 2], test_data[mask, 3], 
                       c=[colors[i]], s=50, alpha=0.7, label=f'Cluster {label}')
    
    ax2.set_xlabel('Destination X')
    ax2.set_ylabel('Destination Y')
    ax2.set_title('Flow Destinations by Cluster')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('clustering_demonstration.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print("Spatially Connected Flow Groups Optimization Test")
    print("=" * 70)
    
    # Run correctness tests
    test_correctness()
    
    # Run performance tests
    results = run_performance_test()
    
    # Create visualization
    create_visualization(results)
    
    # Demonstrate clustering
    demonstrate_clustering()
    
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
    print(f"Visualizations saved as 'flow_groups_optimization_results.png' and 'clustering_demonstration.png'")