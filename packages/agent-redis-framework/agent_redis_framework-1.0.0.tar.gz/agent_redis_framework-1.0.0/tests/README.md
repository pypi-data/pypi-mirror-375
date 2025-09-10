# Multi-Task Framework Test API

这是一个基于FastAPI的RESTful API，用于测试 `agent_redis_framework` 中的 `SortedSetQueue` 和 `RedisStreamsClient` 功能。

## 启动服务

```bash
# 使用uv运行
UV_INDEX_URL=https://pypi.org/simple/ uv run uvicorn tests.test_api:app --host 0.0.0.0 --port 8001
```

服务启动后，可以访问：
- API文档: http://localhost:8001/docs
- 健康检查: http://localhost:8001/health


## 测试示例

### 基础健康检查

```bash
# 健康检查
curl -s http://localhost:8001/health
```

### Queue 测试

```bash
# 1. 推送任务到队列
curl -X POST "http://localhost:8001/queue/push" \
  -H "Content-Type: application/json" \
  -d '{"id": "task-1", "payload": {"data": "test1"}, "score": 1.0}'

# 2. 推送第二个任务
curl -X POST "http://localhost:8001/queue/push" \
  -H "Content-Type: application/json" \
  -d '{"id": "task-2", "payload": {"data": "test2"}, "score": 2.0}'

# 3. 弹出并处理任务
curl -X POST "http://localhost:8001/queue/pop?count=1"

# 4. 查看所有处理过的任务
curl -s "http://localhost:8001/queue/getall"
```

### Stream 测试

```bash
# 1. 推送消息到流（服务启动时会自动开始消费test-stream）
curl -X POST "http://localhost:8001/stream/push" \
  -H "Content-Type: application/json" \
  -d '{"stream": "test-stream", "fields": {"event": "test", "data": "hello world"}}'