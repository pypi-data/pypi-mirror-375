from __future__ import annotations

import json
import time
from dataclasses import dataclass, asdict
from typing import Any, Callable

from ..redis_client import get_redis


@dataclass(frozen=True)
class Task:
    """任务数据类
    
    用于表示队列中的任务，包含任务ID和负载数据。
    使用frozen=True确保任务对象不可变，保证线程安全。
    
    Attributes:
        id: 任务的唯一标识符
        payload: 任务的负载数据，包含任务执行所需的参数
    """
    id: str
    payload: dict[str, Any]

    def to_json(self) -> str:
        """将任务对象序列化为JSON字符串
        
        Returns:
            str: 紧凑格式的JSON字符串，用于存储到Redis中
        """
        return json.dumps(asdict(self), separators=(",", ":"))

    @staticmethod
    def from_json(data: str) -> "Task":
        """从JSON字符串反序列化为任务对象
        
        Args:
            data: JSON格式的任务数据字符串
            
        Returns:
            Task: 反序列化后的任务对象
        """
        obj = json.loads(data)
        return Task(id=obj["id"], payload=obj.get("payload", {}))


class SortedSetQueue:
    """基于Redis有序集合的任务调度队列
    
    这是一个轻量级的Redis有序集合封装，用于任务调度和优先级队列。
    
    主要功能：
    - zadd: 推送带有分数的任务（如优先级或时间戳）
    - zrange: 按分数顺序读取任务
    - zrem: 处理后移除任务
    
    在多消费者场景中，使用ZPOPMIN进行原子性任务声明，
    它会原子性地弹出分数最低的成员。
    
    适用场景：
    - 优先级任务队列
    - 延时任务调度
    - 多消费者任务分发
    
    重构说明：
    - key参数已从构造函数移到各个方法中
    - 一个SortedSetQueue实例可以操作多个不同的sortedset
    - 避免了为每个sortedset创建单独实例的开销
    """

    def __init__(self, *, redis_client=None) -> None:
        """初始化有序集合队列
        
        Args:
            redis_client: Redis客户端实例，如果未提供则使用默认客户端
        """
        self.redis = redis_client or get_redis()

    def push(self, key: str, task: Task, score: float | None = None) -> None:
        """将任务推送到队列中
        
        Args:
            key: Redis中有序集合的键名
            task: 要推送的任务对象
            score: 任务的分数（用于排序，分数越低优先级越高）。
                  如果不提供，则使用当前时间戳作为分数
        """
        if score is None:
            score = time.time()
        self.redis.zadd(key, {task.to_json(): score})

    def pop_and_handle(
        self,
        key: str,
        callback: Callable[[Task], bool],
        *,
        on_failure: Callable[[Task], None] | None = None,
        ascending: bool = True,
        count: int = 1,
    ) -> list[Task]:
        """原子性地弹出并处理任务
        
        按指定的排序顺序，原子性地弹出指定数量的任务并立即处理。
        根据处理函数的返回值决定任务的后续处理：
        - 返回True：任务处理成功，从队列中移除
        - 返回False：任务处理失败，调用失败回调函数或直接丢弃
        
        Args:
            key: Redis中有序集合的键名
            callback: 任务处理函数，接收Task对象作为参数，返回bool值表示处理结果
            count: 要弹出的任务数量，默认为1
            on_failure: 可选的失败处理回调函数，接收失败的Task对象
                       如果未提供，则使用默认行为（直接丢弃失败的任务）
            ascending: 排序顺序控制，默认为True
                      - True: 按分数从低到高的顺序弹出（使用zpopmin）
                      - False: 按分数从高到低的顺序弹出（使用zpopmax）
            
        Returns:
            list[Task]: 已成功处理并移除的任务列表，用于观察和测试
        """
        popped: list[Task] = []
        for _ in range(max(1, count)):
            # 根据排序参数选择弹出方法
            if ascending:
                item = self.redis.zpopmin(key, 1)  # 分数从低到高
            else:
                item = self.redis.zpopmax(key, 1)  # 分数从高到低
            
            if not item:
                break
            member, score = item[0]
            task = Task.from_json(member)
            
            # 调用处理函数并根据返回值决定后续操作
            success = callback(task)
            if success:
                # 处理成功，加入已处理列表
                popped.append(task)
            else:
                # 处理失败，调用失败回调或使用默认行为
                if on_failure is not None:
                    on_failure(task)
                # 默认行为：直接丢弃失败的任务
        return popped

    def size(self, key: str) -> int:
        """获取队列中任务的数量
        
        Args:
            key: Redis中有序集合的键名
            
        Returns:
            int: 队列中任务的总数
        """
        return int(self.redis.zcard(key))

    def clear(self, key: str) -> None:
        """清空队列中的所有任务
        
        Args:
            key: Redis中有序集合的键名
            
        注意：此操作会删除整个Redis键，不可恢复
        """
        self.redis.delete(key)