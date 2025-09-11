import os
import time
import csv
import threading
from datetime import datetime
from typing import List, Dict, Tuple

import numpy as np
import psutil
from scalefc import flow_cluster_scalefc

# 配置参数 - 保持全局设置
SCALE_FACTOR = 0.2
MIN_FLOWS = 5
N_JOBS = -1

# 数据规模配置
DATA_SCALES = (
    list(range(1000, 11000, 1000)) +  # 1000-10000，步长1000
    list(range(12000, 42000, 2000))   # 12000-40000，步长2000
)


def generate_random_flows(num_flows, seed=42):
    """生成随机的OD流数据

    Args:
        num_flows: 流的数量
        seed: 随机种子，确保结果可重现

    Returns:
        numpy.ndarray: 形状为(num_flows, 4)的数组，包含[ox, oy, dx, dy]
    """
    np.random.seed(seed)

    # 生成随机的起点和终点坐标
    # 坐标范围设置为[0, 100]
    ox = np.random.uniform(0, 100, num_flows)
    oy = np.random.uniform(0, 100, num_flows)
    dx = np.random.uniform(0, 100, num_flows)
    dy = np.random.uniform(0, 100, num_flows)

    return np.column_stack([ox, oy, dx, dy]).astype(np.float32)


class MultiProcessMemoryMonitor:
    """多进程内存监控器
    
    使用psutil监控当前进程及其所有子进程的内存使用情况，
    能够准确捕获joblib等多进程库的内存使用。
    """
    
    def __init__(self, interval: float = 0.1):
        self.interval = interval
        self.memory_usage: List[float] = []
        self.monitoring = False
        self.monitor_thread = None
        self.start_time = None
        
    def _get_process_tree_memory(self) -> float:
        """获取当前进程及其所有子进程的内存使用量（MB）"""
        try:
            current_process = psutil.Process()
            total_memory = current_process.memory_info().rss
            
            # 递归获取所有子进程的内存使用
            try:
                children = current_process.children(recursive=True)
                for child in children:
                    try:
                        total_memory += child.memory_info().rss
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        # 子进程可能已经结束或无法访问
                        continue
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
            return total_memory / (1024 * 1024)  # 转换为MB
        except Exception:
            return 0.0
    
    def _monitor_loop(self):
        """内存监控循环"""
        while self.monitoring:
            memory_mb = self._get_process_tree_memory()
            self.memory_usage.append(memory_mb)
            time.sleep(self.interval)
    
    def start_monitoring(self):
        """开始内存监控"""
        self.memory_usage.clear()
        self.monitoring = True
        self.start_time = time.time()
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self) -> List[float]:
        """停止内存监控并返回内存使用记录"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1.0)
        
        # 最后采样一次
        final_memory = self._get_process_tree_memory()
        if final_memory > 0:
            self.memory_usage.append(final_memory)
            
        return self.memory_usage.copy()


def test_clustering_with_memory_monitor(od_data, num_flows) -> Dict:
    """测试聚类算法的执行时间和内存使用情况
    
    Args:
        od_data: OD流数据
        num_flows: 流的数量
        
    Returns:
        dict: 包含测试结果的字典，包括时间和内存数据
    """
    print(f"\n正在测试 {num_flows:,} 条流的聚类性能（时间+内存）...")
    
    # 创建内存监控器
    monitor = MultiProcessMemoryMonitor(interval=0.1)
    
    # 开始监控
    monitor.start_monitoring()
    start_time = time.time()
    
    # 执行聚类算法
    try:
        labels = flow_cluster_scalefc(
            OD=od_data,
            scale_factor=SCALE_FACTOR,
            min_flows=MIN_FLOWS,
            n_jobs=N_JOBS,
            show_time_usage=False,  # 关闭内部时间显示
            debug=False  # 关闭调试信息
        )
        
        # 记录结束时间
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 停止内存监控
        mem_usage = monitor.stop_monitoring()
        
        # 分析聚类结果
        unique_labels = np.unique(labels)
        n_clusters = len(unique_labels[unique_labels >= 0])
        n_noise = np.sum(labels == -1)
        
        # 分析内存使用情况
        if mem_usage:
            min_memory = min(mem_usage)
            max_memory = max(mem_usage)
            avg_memory = np.mean(mem_usage)
            memory_peak_growth = max_memory - min_memory
        else:
            min_memory = max_memory = avg_memory = memory_peak_growth = 0.0
        
        result = {
            'num_flows': num_flows,
            'execution_time': execution_time,
            'n_clusters': n_clusters,
            'n_noise': n_noise,
            'noise_ratio': n_noise / len(labels) * 100,
            'min_memory_mb': min_memory,
            'max_memory_mb': max_memory,
            'avg_memory_mb': avg_memory,
            'memory_peak_growth_mb': memory_peak_growth,
            'memory_samples': len(mem_usage),
            'success': True,
            'error_message': None
        }
        
        print(f"  执行时间: {execution_time:.3f}秒")
        print(f"  聚类数量: {n_clusters}")
        print(f"  噪声点数: {n_noise} ({result['noise_ratio']:.1f}%)")
        print(f"  内存使用: {min_memory:.1f}MB - {max_memory:.1f}MB (峰值增长: {memory_peak_growth:.1f}MB)")
        print(f"  内存采样: {len(mem_usage)} 次")
        
    except Exception as e:
        execution_time = time.time() - start_time
        # 停止内存监控
        mem_usage = monitor.stop_monitoring()
        
        result = {
            'num_flows': num_flows,
            'execution_time': execution_time,
            'n_clusters': -1,
            'n_noise': -1,
            'noise_ratio': -1,
            'min_memory_mb': min(mem_usage) if mem_usage else 0.0,
            'max_memory_mb': max(mem_usage) if mem_usage else 0.0,
            'avg_memory_mb': np.mean(mem_usage) if mem_usage else 0.0,
            'memory_peak_growth_mb': (max(mem_usage) - min(mem_usage)) if mem_usage else 0.0,
            'memory_samples': len(mem_usage),
            'success': False,
            'error_message': str(e)
        }
        print(f"  执行失败: {str(e)}")
        
    return result


def save_results_to_csv(results: List[Dict], output_dir: str = None):
    """将测试结果保存到CSV文件
    
    Args:
        results: 测试结果列表
        output_dir: 输出目录，默认为当前脚本目录
    """
    if output_dir is None:
        output_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scalefc_performance_memory_test_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    # 定义CSV列名，包含内存监控数据
    fieldnames = [
        'num_flows', 'execution_time', 'n_clusters', 'n_noise', 'noise_ratio',
        'min_memory_mb', 'max_memory_mb', 'avg_memory_mb', 'memory_peak_growth_mb',
        'memory_samples', 'success', 'error_message'
    ]
    
    # 写入CSV文件
    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    
    print(f"\n测试结果已保存到: {filepath}")
    return filepath


def run_performance_test():
    """运行完整的性能测试（时间+内存）"""
    print("=== ScaleFC算法时间性能+内存监控测试 ===")
    print(f"测试规模: {len(DATA_SCALES)} 个数据点")
    print(f"数据范围: {min(DATA_SCALES):,} - {max(DATA_SCALES):,} 条流")
    print(f"算法参数:")
    print(f"  规模因子: {SCALE_FACTOR}")
    print(f"  最小流数: {MIN_FLOWS}")
    print(f"  并行任务数: {N_JOBS}")
    print(f"内存监控: 多进程监控（包含子进程），采样间隔0.1秒")
    print("=" * 60)
    
    results = []
    total_tests = len(DATA_SCALES)
    
    for i, num_flows in enumerate(DATA_SCALES, 1):
        print(f"\n[{i}/{total_tests}] 测试进度: {i/total_tests*100:.1f}%")
        
        # 生成测试数据
        print(f"生成 {num_flows:,} 条流的测试数据...")
        data_start_time = time.time()
        od_data = generate_random_flows(num_flows)
        data_generation_time = time.time() - data_start_time
        print(f"数据生成完成，耗时: {data_generation_time:.3f}秒")
        
        # 执行性能测试（包含内存监控）
        result = test_clustering_with_memory_monitor(od_data, num_flows)
        results.append(result)
        
        # 如果测试失败，记录但继续下一个测试
        if not result['success']:
            print(f"警告: {num_flows:,} 条流的测试失败，继续下一个测试")
    
    # 保存结果到CSV
    csv_filepath = save_results_to_csv(results)
    
    # 打印测试总结
    print("\n=== 测试总结 ===")
    successful_tests = [r for r in results if r['success']]
    failed_tests = [r for r in results if not r['success']]
    
    print(f"总测试数: {len(results)}")
    print(f"成功测试: {len(successful_tests)}")
    print(f"失败测试: {len(failed_tests)}")
    
    if successful_tests:
        times = [r['execution_time'] for r in successful_tests]
        flows = [r['num_flows'] for r in successful_tests]
        max_memories = [r['max_memory_mb'] for r in successful_tests]
        memory_growths = [r['memory_peak_growth_mb'] for r in successful_tests]
        
        print(f"\n时间性能统计:")
        print(f"  最快执行时间: {min(times):.3f}秒 ({flows[times.index(min(times))]:,} 条流)")
        print(f"  最慢执行时间: {max(times):.3f}秒 ({flows[times.index(max(times))]:,} 条流)")
        print(f"  平均执行时间: {np.mean(times):.3f}秒")
        
        print(f"\n内存使用统计:")
        print(f"  最小内存峰值: {min(max_memories):.1f}MB ({flows[max_memories.index(min(max_memories))]:,} 条流)")
        print(f"  最大内存峰值: {max(max_memories):.1f}MB ({flows[max_memories.index(max(max_memories))]:,} 条流)")
        print(f"  平均内存峰值: {np.mean(max_memories):.1f}MB")
        print(f"  平均内存增长: {np.mean(memory_growths):.1f}MB")
        
        # 计算时间复杂度趋势
        if len(successful_tests) > 1:
            # 简单的线性拟合来估算时间复杂度
            flows_array = np.array([r['num_flows'] for r in successful_tests])
            times_array = np.array([r['execution_time'] for r in successful_tests])
            memories_array = np.array([r['max_memory_mb'] for r in successful_tests])
            
            # 计算每千条流的平均时间和内存
            time_per_1k_flows = times_array / (flows_array / 1000)
            memory_per_1k_flows = memories_array / (flows_array / 1000)
            print(f"\n规模化分析:")
            print(f"  平均每千条流耗时: {np.mean(time_per_1k_flows):.3f}秒")
            print(f"  平均每千条流内存: {np.mean(memory_per_1k_flows):.1f}MB")
    
    if failed_tests:
        print(f"\n失败的测试:")
        for test in failed_tests:
            print(f"  {test['num_flows']:,} 条流: {test['error_message']}")
    
    print(f"\n详细结果已保存到CSV文件: {csv_filepath}")
    print("CSV文件包含完整的时间和内存监控数据")
    print("=== 测试完成 ===")
    
    return results, csv_filepath


if __name__ == "__main__":
    # 运行性能测试
    results, csv_file = run_performance_test()
    
    print("\n提示:")
    print("- 可以修改全局参数 SCALE_FACTOR, MIN_FLOWS, N_JOBS 来测试不同配置")
    print("- 可以修改 DATA_SCALES 来自定义测试的数据规模")
    print("- CSV文件包含了时间和内存的详细监控数据，可用于进一步分析")
    print("- 内存监控包括主进程和所有子进程，适用于joblib多进程场景")
