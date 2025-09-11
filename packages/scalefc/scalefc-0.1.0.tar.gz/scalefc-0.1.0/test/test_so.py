import numpy as np
import time

# 生成测试数据
np.random.seed(42)
n_clusters = 1000
max_cluster_size = 500
total_size = 10000

# 创建测试数据
result_subclusters_indices = []
used_indices = set()
for i in range(n_clusters):
    cluster_size = np.random.randint(1, max_cluster_size)
    # 生成不重复的随机索引
    available_indices = list(set(range(total_size)) - used_indices)
    if len(available_indices) < cluster_size:
        cluster_size = len(available_indices)
    if cluster_size == 0:
        break
    cluster_indices = np.array(np.random.choice(available_indices, cluster_size, replace=False))
    result_subclusters_indices.append(cluster_indices)
    used_indices.update(cluster_indices)

print(f"测试数据: {len(result_subclusters_indices)}个簇, 总共{sum(len(x) for x in result_subclusters_indices)}个索引")

# 方法1: 原始for循环
def method1(result_subclusters_indices, total_size):
    labels = np.full(total_size, -1)
    for i, x in enumerate(result_subclusters_indices):
        labels[x] = i
    return labels

# 方法2: 向量化操作
def method2(result_subclusters_indices, total_size):
    labels = np.full(total_size, -1)
    if result_subclusters_indices:  # 防止空列表
        all_indices = np.concatenate(result_subclusters_indices)
        all_labels = np.repeat(np.arange(len(result_subclusters_indices)), 
                              [len(x) for x in result_subclusters_indices])
        labels[all_indices] = all_labels
    return labels

# 测试正确性
labels1 = method1(result_subclusters_indices, total_size)
labels2 = method2(result_subclusters_indices, total_size)

print(f"结果是否一致: {np.array_equal(labels1, labels2)}")

# 性能测试
n_runs = 100

# 测试方法1
start_time = time.time()
for _ in range(n_runs):
    labels1 = method1(result_subclusters_indices, total_size)
time1 = time.time() - start_time

# 测试方法2
start_time = time.time()
for _ in range(n_runs):
    labels2 = method2(result_subclusters_indices, total_size)
time2 = time.time() - start_time

print(f"\n性能对比 (运行{n_runs}次):")
print(f"方法1 (for循环): {time1:.4f}秒")
print(f"方法2 (向量化): {time2:.4f}秒")
print(f"速度提升: {time1/time2:.2f}倍" if time2 < time1 else f"速度下降: {time2/time1:.2f}倍")