from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any
import time
import threading
from contextlib import asynccontextmanager

from agent_redis_framework.sortedset.sorted_queue import SortedSetQueue, Task
from agent_redis_framework.streams.stream_client import RedisStreamsClient, StreamMsg


# Pydantic models for request/response
class TaskRequest(BaseModel):
    id: str
    payload: dict[str, Any]
    score: float | None = None


class StreamMessageRequest(BaseModel):
    stream: str
    fields: dict[str, Any]
    maxlen: int | None = None


class TaskResponse(BaseModel):
    success: bool
    message: str
    data: dict[str, Any] | None = None


# Global instances
sorted_queue = SortedSetQueue()
stream_client = RedisStreamsClient()

# Storage for processed data
processed_tasks: list[dict[str, Any]] = []
stream_messages: list[dict[str, Any]] = []

# Stream consumer configuration
STREAM_NAME = "test-stream"
GROUP_NAME = "test-group"
CONSUMER_NAME = "test-consumer"
consumer_thread = None
stop_consumer = threading.Event()


def stream_message_handler(msg: StreamMsg) -> bool:
    """处理流消息的回调函数"""
    message_data = {
        "stream": msg.stream,
        "message_id": msg.message_id,
        "payload": dict(msg.payload),
        "processed_at": time.time()
    }
    stream_messages.append(message_data)
    print(f"收到流消息: {message_data}")
    return True


def start_stream_consumer():
    """启动流消费者"""
    global consumer_thread
    if consumer_thread and consumer_thread.is_alive():
        return
    
    def consumer_worker():
        try:
            # 确保消费者组存在
            stream_client.ensure_group(STREAM_NAME, GROUP_NAME)
            
            # 开始消费
            stream_client.consume(
                streams=[STREAM_NAME],
                group=GROUP_NAME,
                consumer=CONSUMER_NAME,
                callback=stream_message_handler,
                count=10,
                block_ms=1000,
                read_new_only=True,
                discard_on_failure=False
            )
        except Exception as e:
            print(f"流消费者错误: {e}")
    
    consumer_thread = threading.Thread(target=consumer_worker, daemon=True)
    consumer_thread.start()
    print(f"流消费者已启动，监听流: {STREAM_NAME}")


def stop_stream_consumer():
    """停止流消费者"""
    global consumer_thread
    stop_consumer.set()
    if consumer_thread and consumer_thread.is_alive():
        consumer_thread.join(timeout=2)
    print("流消费者已停止")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting FastAPI test server for agent-redis-framework")
    start_stream_consumer()
    yield
    # Shutdown
    print("Shutting down FastAPI test server")
    stop_stream_consumer()


app = FastAPI(
    title="Agent Redis Framework Test API",
    description="简化的API用于测试SortedSetQueue和RedisStreamsClient",
    version="1.0.0",
    lifespan=lifespan
)


# Queue endpoints - 简化版本
@app.post("/queue/push", response_model=TaskResponse)
async def queue_push(task_request: TaskRequest):
    """推送任务到队列"""
    try:
        task = Task(id=task_request.id, payload=task_request.payload)
        score = task_request.score or time.time()
        sorted_queue.push("default-queue", task, score)
        return TaskResponse(
            success=True,
            message=f"Task {task_request.id} pushed to queue",
            data={"task_id": task_request.id, "score": score}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/queue/pop", response_model=TaskResponse)
async def queue_pop(count: int = 1):
    """从队列弹出任务"""
    try:
        def task_handler(task: Task) -> bool:
            processed_tasks.append({
                "id": task.id,
                "payload": task.payload,
                "processed_at": time.time()
            })
            return True
        
        popped_tasks = sorted_queue.pop_and_handle(
            "default-queue", task_handler, count=count
        )
        
        return TaskResponse(
            success=True,
            message=f"Popped {len(popped_tasks)} tasks from queue",
            data={
                "processed_count": len(popped_tasks),
                "tasks": [{"id": task.id, "payload": task.payload} for task in popped_tasks]
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/queue/getall", response_model=TaskResponse)
async def queue_getall():
    """获取所有处理过的任务"""
    return TaskResponse(
        success=True,
        message=f"Retrieved {len(processed_tasks)} processed tasks",
        data={"tasks": processed_tasks}
    )


# Stream endpoints - 简化版本
@app.post("/stream/push", response_model=TaskResponse)
async def stream_push(message_request: StreamMessageRequest):
    """推送消息到流"""
    try:
        # 如果没有指定流名，使用默认的测试流
        stream_name = message_request.stream if message_request.stream != "test-stream" else STREAM_NAME
        
        message_id = stream_client.push(
            stream_name,
            message_request.fields,
            maxlen=message_request.maxlen
        )
        return TaskResponse(
            success=True,
            message=f"Message pushed to stream {stream_name}",
            data={"message_id": message_id, "stream": stream_name}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stream/messages", response_model=TaskResponse)
async def get_stream_messages():
    """获取所有处理过的流消息"""
    return TaskResponse(
        success=True,
        message=f"Retrieved {len(stream_messages)} processed stream messages",
        data={"messages": stream_messages}
    )


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {"status": "healthy", "timestamp": time.time()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)