# Simple Tracker(Redis)

Simple Tracker 是一个基于 Redis 的轻量级计数跟踪系统，支持按分钟、小时、天三种时间粒度对项目进行计数统计。

## 功能特点

- 支持多种时间粒度跟踪：分钟（m）、小时（h）、天（d）
- 自动过期机制，避免数据无限增长
- 同步和异步两种实现方式
- 提供装饰器模式方便集成

## 核心组件

### ItemTracker (同步版本)

```python
from tracker import ItemTracker

# 初始化
tracker = ItemTracker(redis_client, tracker_name="my_tracker")

# 跟踪项目出现次数
tracker.track_item_occurrence("item_name")

# 获取指定时间粒度的计数
count = tracker.get_item_count("item_name", "h")  # 按小时统计

# 获取分布统计
distribution = tracker.get_count_distribution("d")  # 按天获取分布
```

### AsyncItemTracker (异步版本)

```python
from tracker import AsyncItemTracker

# 初始化
async_tracker = AsyncItemTracker(redis_client, tracker_name="my_tracker")

# 异步跟踪项目出现次数
await async_tracker.track_item_occurrence("item_name")

# 异步获取指定时间粒度的计数
count = await async_tracker.get_item_count("item_name", "h")

# 异步获取分布统计
distribution = await async_tracker.get_count_distribution("d")
```

## 使用装饰器模式

### 同步装饰器

```python
from tracker import get_tracker

track_item = get_tracker(redis_client)

@track_item("api_call")
def my_function():
    pass
```

### 异步装饰器

```python
from tracker import get_async_tracker

track_item = get_async_tracker(redis_client)

@track_item("api_call")
async def my_async_function():
    pass
```

## 数据存储结构

Redis 中的数据以以下格式存储：

```
{tracker_name}:{granularity}:{time_period} -> Hash {item_name: count}
```

例如：

```
my_tracker:h:2023120115 -> {"api_call": 25, "user_login": 10}
```

## 过期时间设置

- 分钟级数据保留 60 分钟
- 小时级数据保留 24 小时
- 天级数据保留 14 天

## 返回数据格式

get_count_distribution 方法返回如下格式的数据：

```json
[
  {
    "item_name": "api_call",
    "total_count": 25,
    "freq": "h",
    "period": "2023120115"
  }
]
```
