# agent_redis_framework

一个基于 Redis 的多任务调度与消息流工具库，提供：
- 基于 Sorted Set 的轻量任务队列（入队、按分值遍历、原子弹出处理）
- 基于 Redis Streams 的消费组封装（推送、组内消费、回调与自动 ACK）

适合用作中小型任务编排、定时/优先级任务、以及流式事件处理的基础组件。

## 安装

项目已支持可编辑安装与开发依赖：

- 基础安装（库自身及必需依赖）
  - 使用 uv
    - `uv pip install -e .`
  - 或使用 pip
    - `python -m pip install -e .`

- 安装测试依赖（pytest），在 zsh 下注意加引号避免通配符展开：
  - 使用 uv
    - `uv pip install -e '.[dev]'`
  - 或使用 pip
    - `python -m pip install -e '.[dev]'`

要求：Python >= 3.12，Redis Python 客户端 Redis >= 5.0。

## 快速开始

### 连接 Redis

你可以通过环境变量或显式传入配置来创建连接：

```python
from agent_redis_framework import RedisConfig, get_redis

r = get_redis(RedisConfig(host="localhost", port=6379, db=0))
print(r.ping())
```

### Sorted Set 任务队列

核心对象：Task、SortedSetQueue。

```python
from agent_redis_framework.sortedset import SortedSetQueue, Task
from agent_redis_framework import RedisConfig, get_redis

r = get_redis(RedisConfig(host="localhost", port=6379, db=0))
q = SortedSetQueue(redis_client=r)
queue_key = "demo:ss:q"

# 清理队列（示例方便）
q.clear(queue_key)

# 入队（score 可用作时间戳/优先级）
q.push(queue_key, Task(id="t1", payload={"x": 1}), score=1)
q.push(queue_key, Task(id="t2", payload={"x": 2}), score=2)

# 原子弹出并处理
popped: list[str] = []
def handle_task(task: Task) -> bool:
    popped.append(task.id)
    return True  # 返回True表示处理成功

q.pop_and_handle(queue_key, handle_task, count=2)
print(popped)  # ["t1", "t2"]
print(q.size(queue_key))  # 0
```

### Redis Streams 消费组

核心对象：StreamMessage、RedisStreamsClient。

```python
from agent_redis_framework.streams import RedisStreamsClient, StreamMessage
from agent_redis_framework import RedisConfig, get_redis

r = get_redis(RedisConfig(host="localhost", port=6379, db=0))
client = RedisStreamsClient(redis_client=r)
stream = "demo:stream"
group = "g1"
consumer = "c1"

# 创建消费组（幂等）
client.ensure_group(stream, group)

# 推送消息
a_mid = client.push(stream, {"kind": "demo", "value": "42"})
print("xadd id:", a_mid)

# 消费（长循环示例，可在独立进程/线程中运行）
def handle(msg: StreamMessage) -> None:
    print("got:", msg.stream, msg.message_id, dict(msg.fields))

# 注意：consume 是一个持续循环的阻塞方法
# client.consume([stream], group, consumer, handle, block_ms=5000)
```

提示：生产环境中请做好进程生命周期管理（如优雅退出、超时与重试策略等）。