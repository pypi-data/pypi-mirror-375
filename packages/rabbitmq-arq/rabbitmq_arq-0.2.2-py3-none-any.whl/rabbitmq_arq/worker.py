# -*- coding: utf-8 -*-
# @version        : 1.0
# @Create Time    : 2025/5/9 15:02
# @File           : worker
# @IDE            : PyCharm
# @desc           : Worker 核心实现 - 使用 Python 3.12 现代语法

from __future__ import annotations

import asyncio
import json
import logging
import signal
import traceback
import uuid
from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from functools import partial
import inspect
from typing import get_type_hints
from signal import Signals
from typing import Any

from aio_pika import connect_robust, IncomingMessage, Message
from aio_pika.abc import AbstractConnection, AbstractChannel
from pydantic import TypeAdapter

from .connections import WorkerSettings
from .exceptions import Retry, JobTimeout, MaxRetriesExceeded, RabbitMQConnectionError
from .models import JobModel, JobContext, JobStatus, WorkerInfo
from .protocols import WorkerCoroutine
from .result_storage import ResultStore
from .result_storage.factory import create_result_store_from_settings
from .result_storage.models import JobResult
from .result_storage.url_parser import parse_store_type_from_url

logger = logging.getLogger('rabbitmq-arq.worker')

# TypeAdapter 简易缓存，减少重复构建开销
_TYPE_ADAPTER_CACHE: dict[str, TypeAdapter] = {}


# 错误分类定义
class ErrorClassification:
    """错误分类配置，用于智能重试策略"""

    # 可重试的错误类型（仅限系统级错误和显式重试）
    RETRIABLE_ERRORS = (
        RabbitMQConnectionError,  # RabbitMQ 连接错误
        TimeoutError,  # 超时错误
        OSError,  # 操作系统错误
        IOError,  # IO错误
        Retry,  # 显式重试请求（ARQ 风格）
    )

    # 不可重试的错误类型（包括所有其他异常）
    NON_RETRIABLE_ERRORS = (
        TypeError,  # 函数签名错误、参数类型错误
        ValueError,  # 参数值错误
        AttributeError,  # 属性错误
        ImportError,  # 导入错误
        ModuleNotFoundError,  # 模块未找到
        SyntaxError,  # 语法错误
        NameError,  # 名称错误
        KeyError,  # 字典键错误（配置相关）
        MaxRetriesExceeded,  # 已达到最大重试次数
        Exception,  # 所有其他异常都不自动重试（ARQ 风格）
    )

    @classmethod
    def is_retriable_error(cls, error: Exception) -> bool:
        """
        判断错误是否可重试（ARQ 风格）
        
        Args:
            error: 异常对象
            
        Returns:
            True 如果错误可重试，False 如果应立即失败
        """
        # 显式可重试的错误（主要是系统级错误和 Retry 异常）
        if isinstance(error, cls.RETRIABLE_ERRORS):
            return True

        # 所有其他异常都不可重试（ARQ 风格）
        return False

    @classmethod
    def get_error_category(cls, error: Exception) -> str:
        """
        获取错误分类（ARQ 风格）
        
        Args:
            error: 异常对象
            
        Returns:
            错误分类字符串
        """
        if isinstance(error, cls.RETRIABLE_ERRORS):
            return "retriable"
        else:
            return "non_retriable"


class WorkerUtils:
    """
    消费者工具类 - 基础属性和信号处理
    """

    def __init__(self, worker_settings: WorkerSettings | None = None):
        self.allow_pick_jobs = True
        self.tasks: dict[str, asyncio.Task] = {}
        self.main_task: asyncio.Task | None = None
        self.on_stop: Callable | None = None

        # 基础配置 - 如果有worker_settings就使用，否则创建临时属性
        self.worker_settings = worker_settings
        self.shutdown_event = asyncio.Event()

        # 任务统计
        self.jobs_complete = 0
        self.jobs_failed = 0
        self.jobs_retried = 0

        # Worker 基础信息 - 可能会被子类覆盖
        self.worker_id = uuid.uuid4().hex
        self.worker_info = WorkerInfo(
            worker_id=self.worker_id,
            start_time=datetime.now(timezone.utc)
        )

        # 信号处理相关属性
        self._job_completion_wait = 30  # 默认等待时间30秒

        # 子类可能需要的burst模式相关属性的默认值
        self._burst_mode = False
        self._burst_should_exit = False

        # 连接相关属性 - 子类会覆盖这些默认值
        self.connection: AbstractConnection | None = None
        self.channel: AbstractChannel | None = None
        self.dlq_channel: AbstractChannel | None = None

        # 设置信号处理器的标志，子类可以控制是否启用
        self._signal_handlers_enabled = False

    def handle_sig_wait_for_completion(self, signum: Signals) -> None:
        """
        允许任务在给定时间内完成后再关闭 worker 的信号处理器。
        可通过 `wait_for_job_completion_on_signal_second` 配置时间。
        收到信号后 worker 将停止获取新任务。
        """
        sig = Signals(signum)

        # 记录当前状态
        running_tasks = len(self.tasks)
        logger.info(
            f'🛑 收到 {sig.name} 信号 - 统计信息: ✅完成:{self.jobs_complete} ❌失败:{self.jobs_failed} '
            f'🔄重试:{self.jobs_retried} ⏳运行中:{running_tasks}'
        )

        if self._burst_mode:
            logger.info(f'🛑 Burst 模式收到信号 {sig.name}，开始优雅关闭')
            self.allow_pick_jobs = False
            self._burst_should_exit = True

            # 立即取消消费者，停止接收新消息
            asyncio.create_task(self._cancel_consumer())

            # 在 burst 模式下，可以选择立即退出或等待任务完成
            if self.worker_settings.burst_wait_for_tasks and running_tasks > 0:
                logger.info(f'⏳ Burst 模式：等待 {running_tasks} 个正在执行的任务完成...')
                asyncio.create_task(self._wait_for_tasks_to_complete(signum=sig))
            else:
                if running_tasks > 0:
                    logger.info(f'🚫 Burst 模式：不等待任务完成，取消 {running_tasks} 个正在执行的任务')
                    # 取消所有任务
                    for t in self.tasks.values():
                        if not t.done():
                            t.cancel()
                else:
                    logger.info('✅ Burst 模式：没有正在执行的任务，立即退出')
                self.main_task and self.main_task.cancel()
        else:
            logger.info(f'🔄 常规模式：开始优雅关闭，停止接收新任务')
            self.allow_pick_jobs = False

            # 立即取消消费者，停止接收新消息
            asyncio.create_task(self._cancel_consumer())

            if running_tasks > 0:
                # 获取等待超时时间，如果没有配置则使用默认值
                timeout = (getattr(self.worker_settings, 'wait_for_job_completion_on_signal_second', None)
                           if self.worker_settings else None) or 30
                logger.info(
                    f'⏳ 等待 {running_tasks} 个正在执行的任务完成（超时时间：{timeout}秒）')
                asyncio.create_task(self._wait_for_tasks_to_complete(signum=sig))
            else:
                logger.info('✅ 没有正在执行的任务，可以立即关闭')
                self.shutdown_event.set()
                # 取消主任务以立即退出
                if self.main_task and not self.main_task.done():
                    self.main_task.cancel()

    async def _wait_for_tasks_to_complete(self, signum: Signals) -> None:
        """
        等待任务完成，直到达到 `wait_for_job_completion_on_signal_second`。
        """
        start_time = datetime.now(timezone.utc)
        initial_tasks = len(self.tasks)
        # 使用worker_settings中的配置，如果没有则使用默认值
        timeout = (getattr(self.worker_settings, 'wait_for_job_completion_on_signal_second', None)
                   if self.worker_settings else None) or self._job_completion_wait

        logger.info(f'⏳ 开始等待任务完成：初始任务数 {initial_tasks}，超时时间 {timeout} 秒')

        try:
            await asyncio.wait_for(
                self._sleep_until_tasks_complete(),
                timeout,
            )
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            logger.info(f'✅ 所有任务已完成，用时 {elapsed:.2f} 秒')
        except asyncio.TimeoutError:
            elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
            remaining_tasks = len(self.tasks)
            completed_tasks = initial_tasks - remaining_tasks

            logger.warning(
                f'⏰ 等待超时（{elapsed:.2f}秒）：{completed_tasks} 个任务已完成，'
                f'{remaining_tasks} 个任务将被强制取消'
            )

        # 显示最终状态统计
        cancelled_count = sum(not t.done() for t in self.tasks.values())
        logger.info(
            f'🔚 关闭信号 {signum.name} 处理完成 - 统计信息: ✅完成:{self.jobs_complete} '
            f'❌失败:{self.jobs_failed} 🔄重试:{self.jobs_retried} 🚫取消:{cancelled_count}'
        )

        # 取消剩余的任务
        for t in self.tasks.values():
            if not t.done():
                t.cancel()

        # 设置关闭事件
        self.shutdown_event.set()

        # 取消主任务
        self.main_task and self.main_task.cancel()

        # 执行关闭回调
        self.on_stop and self.on_stop(signum)

    async def _sleep_until_tasks_complete(self) -> None:
        """
        等待所有任务完成。与 asyncio.wait_for() 一起使用。
        """
        while len(self.tasks):
            await asyncio.sleep(0.1)

    def _add_signal_handler(self, signum: Signals, handler: Callable[[Signals], None]) -> None:
        try:
            # 使用当前运行的事件循环，而不是保存的循环引用
            loop = asyncio.get_running_loop()
            loop.add_signal_handler(signum, partial(handler, signum))
            logger.debug(f"✅ 已设置 {signum.name} 信号处理器")
        except NotImplementedError:  # pragma: no cover
            logger.debug('Windows 不支持向事件循环添加信号处理器')
        except RuntimeError as e:
            logger.warning(f"⚠️ 无法设置 {signum.name} 信号处理器: {e}")

    async def _cancel_consumer(self) -> None:
        """
        取消消费者，停止接收新消息
        """
        if hasattr(self, '_consumer_tag') and self._consumer_tag and hasattr(self, '_queue') and self._queue:
            if not self.channel or self.channel.is_closed:
                logger.warning("⚠️ 消息通道已关闭，无法取消消费者")
                return

            try:
                logger.info("🛑 立即停止消息消费者，阻止接收新消息")
                await self._safe_operation_with_timeout(
                    self._queue.cancel(self._consumer_tag),
                    "取消消息消费者",
                    timeout=5.0
                )
                logger.info("✅ 消息消费者已停止")
                self._consumer_tag = None
            except Exception as e:
                logger.warning(f"⚠️ 取消消费者时出现错误: {e}")
        else:
            logger.debug("🔍 消费者未启动或已取消")

    async def _safe_operation_with_timeout(self, operation, operation_name: str, timeout: float = 30.0):
        """
        安全执行操作，带超时保护和异常处理
        
        Args:
            operation: 要执行的协程操作
            operation_name: 操作名称，用于日志
            timeout: 超时时间（秒）
        """
        try:
            logger.debug(f"🔧 开始执行 {operation_name}...")
            await asyncio.wait_for(operation, timeout=timeout)
            logger.debug(f"✅ {operation_name} 执行成功")
        except asyncio.TimeoutError:
            logger.warning(f"⏰ {operation_name} 执行超时 ({timeout}秒)")
        except Exception as e:
            logger.error(f"❌ {operation_name} 执行失败: {e}")
            logger.debug(f"详细错误信息: {traceback.format_exc()}")

    async def graceful_shutdown(self, reason: str = "用户请求") -> None:
        """
        基础优雅关闭方法 - 不包含特定的结果存储逻辑
        
        Args:
            reason: 关闭原因，用于日志记录
        """
        running_tasks = len(self.tasks)
        logger.info(
            f'🔄 开始优雅关闭 Worker - 原因: {reason}'
            f' - 统计信息: ✅完成:{self.jobs_complete} ❌失败:{self.jobs_failed} '
            f'🔄重试:{self.jobs_retried} ⏳运行中:{running_tasks}'
        )

        # 停止接收新任务
        self.allow_pick_jobs = False

        # 立即取消消费者，停止接收新消息
        await self._cancel_consumer()

        # 如果有正在运行的任务，等待它们完成
        if running_tasks > 0:
            # 统一的超时时间获取逻辑
            timeout = (getattr(self.worker_settings, 'wait_for_job_completion_on_signal_second', None)
                       if self.worker_settings else None) or 30
            logger.info(f'⏳ 等待 {running_tasks} 个正在执行的任务完成（超时时间：{timeout}秒）')

            try:
                await asyncio.wait_for(
                    self._sleep_until_tasks_complete(),
                    timeout=timeout
                )
                logger.info('✅ 所有任务已完成，开始关闭连接')
            except asyncio.TimeoutError:
                remaining = len(self.tasks)
                logger.warning(f'⏰ 等待超时，强制取消 {remaining} 个未完成的任务')
                for t in self.tasks.values():
                    if not t.done():
                        t.cancel()

        # 关闭连接 - 使用超时保护
        if self.connection and not self.connection.is_closed:
            await self._safe_operation_with_timeout(
                self.connection.close(),
                "RabbitMQ 连接关闭 (graceful_shutdown)",
                timeout=10.0
            )

        # 设置关闭事件
        self.shutdown_event.set()
        logger.info('✅ Worker 基础关闭完成')


class Worker(WorkerUtils):
    """
    消费者基类。
    该类用于实现 RabbitMQ 消费者的核心逻辑，支持自定义启动、关闭、任务开始和结束的钩子函数，
    并可通过 ctx 传递上下文信息。
    """

    def __init__(self, worker_settings: WorkerSettings) -> None:
        """
        初始化 Worker
        
        Args:
            worker_settings: Worker 配置对象，包含所有必要的配置参数
        """
        # 调用父类初始化，传递worker_settings
        super().__init__(worker_settings)

        # Worker特有的属性
        self.functions = {fn.__name__: fn for fn in worker_settings.functions}
        self.consuming = False

        # 生命周期钩子
        self.on_startup = worker_settings.on_startup
        self.on_shutdown = worker_settings.on_shutdown
        self.on_job_start = worker_settings.on_job_start
        self.on_job_end = worker_settings.on_job_end

        # 上下文
        self.ctx = {}

        # 兼容性属性
        self.functions_map = self.functions  # 兼容性别名
        self.after_job_end = None  # 兼容性钩子

        # 覆盖父类的worker_id，使用配置中的名称
        self.worker_id = worker_settings.worker_name or f"worker_{uuid.uuid4().hex[:8]}"
        self.worker_info = WorkerInfo(
            worker_id=self.worker_id,
            start_time=datetime.now(timezone.utc)
        )

        # Burst 模式相关（覆盖父类默认值）
        self._burst_mode = worker_settings.burst_mode
        self._burst_start_time: datetime | None = None
        self._burst_check_task: asyncio.Task | None = None
        self._health_check_task: asyncio.Task | None = None

        # 延迟任务机制配置（初始化时暂不设置，在连接后按需设置）
        self._use_delayed_exchange = False
        self._delayed_exchange_name = None
        self._delay_queue_name = None
        self._delay_mechanism_detected = False

        # 消费者标签管理 - 用于取消消费者
        self._consumer_tag: str | None = None
        self._queue = None

        # 结果存储初始化
        self.result_store: ResultStore | None = None
        self._init_result_store()

        # 并发控制（与 prefetch 协同）：最大并发任务数
        self._job_semaphore: asyncio.Semaphore | None = None
        try:
            mcj = getattr(self.worker_settings, 'max_concurrent_jobs', None)
            if isinstance(mcj, int) and mcj > 0:
                self._job_semaphore = asyncio.Semaphore(mcj)
        except Exception:
            # 若配置异常则不启用并发限制
            self._job_semaphore = None

        # 信号处理器将在 main() 方法中设置，因为此时事件循环还没有运行

    @staticmethod
    def _ensure_aware_utc(dt: datetime | None) -> datetime | None:
        """将 datetime 统一为带时区(UTC)。若传入为 naive，则假定为 UTC。"""
        if dt is None:
            return None
        if dt.tzinfo is None:
            return dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)

    def _init_result_store(self) -> None:
        """初始化结果存储"""
        try:
            self.result_store = create_result_store_from_settings(
                store_url=self.worker_settings.job_result_store_url,
                ttl=self.worker_settings.job_result_ttl
            )

            if self.result_store:
                store_type = parse_store_type_from_url(self.worker_settings.job_result_store_url)
                logger.info(f"任务结果存储已初始化: {store_type} ({self.worker_settings.job_result_store_url})")

        except Exception as e:
            logger.error(f"初始化结果存储失败: {e}")
            logger.info("将在不存储结果的情况下继续运行")
    
    async def _validate_result_store(self) -> None:
        """验证结果存储连接"""
        if not self.result_store:
            logger.error("⚠️ 未配置结果存储，任务结果将不会被保存")
            # 根据配置决定是否允许降级
            if getattr(self.worker_settings, 'job_result_store_degrade_on_failure', True):
                logger.warning("⚠️ 结果存储未配置：启用降级模式（不保存结果）")
                return
            raise RuntimeError("结果存储未配置")
        
        try:
            # 调用存储对象的连接验证方法
            is_valid = await self.result_store.validate_connection()
            if is_valid:
                store_type = parse_store_type_from_url(self.worker_settings.job_result_store_url)
                logger.info(f"✅ 结果存储连接验证成功: {store_type}")
            else:
                store_type = parse_store_type_from_url(self.worker_settings.job_result_store_url)
                raise ValueError(f"结果存储连接验证失败: {store_type}")
                
        except Exception as e:
            store_type = parse_store_type_from_url(self.worker_settings.job_result_store_url)
            logger.error(f"❌ 结果存储连接验证失败 ({store_type}): {e}")
            # 根据配置决定是否降级
            if getattr(self.worker_settings, 'job_result_store_degrade_on_failure', True):
                logger.warning("⚠️ 启用降级模式：禁用结果存储并继续运行")
                self.result_store = None
                return
            # 否则抛出异常阻止启动
            raise RuntimeError(f"结果存储 ({store_type}) 连接失败，Worker 无法启动") from e

    async def _store_job_result(self, job: JobModel) -> None:
        """存储任务结果
        
        Args:
            job: 任务模型，包含执行结果和元数据
        """
        # 检查结果存储是否可用
        if not self.result_store:
            return  # 结果存储未启用、初始化失败或连接不可用

        try:

            # 构建结果对象
            job_result = JobResult(
                job_id=job.job_id,
                status=job.status,
                result=job.result,
                error=job.error,
                start_time=job.start_time,
                end_time=job.end_time,
                duration=(job.end_time - job.start_time).total_seconds() if job.end_time else None,
                worker_id=self.worker_id,
                queue_name=job.queue_name,
                retry_count=job.job_try - 1,  # job_try 从1开始
                function_name=job.function,
                args=job.args,
                kwargs=job.kwargs
            )

            # 异步存储结果
            await self.result_store.store_result(job_result)
            logger.debug(f"任务结果已存储: {job.job_id} - {job.status}")

        except Exception as e:
            # 存储失败不应影响任务处理流程，但标记存储为不可用避免重复报错
            logger.warning(f"存储任务结果失败 {job.job_id}: {e}")

    def _setup_signal_handlers(self) -> None:
        """设置信号处理器"""
        if not self._signal_handlers_enabled:
            logger.info("🔧 正在设置信号处理器...")

            # 设置主要的终止信号处理器
            signals_to_handle = [signal.SIGINT, signal.SIGTERM]

            # 在非Windows系统上添加SIGHUP支持
            if hasattr(signal, 'SIGHUP'):
                signals_to_handle.append(signal.SIGHUP)

            for sig in signals_to_handle:
                self._add_signal_handler(sig, self.handle_sig_wait_for_completion)

            self._signal_handlers_enabled = True
            signal_names = [sig.name for sig in signals_to_handle]
            logger.info(f"✅ 信号处理器设置完成 ({', '.join(signal_names)})")
            logger.info("💡 提示: 请使用 Ctrl+C、kill -TERM 或 kill -HUP 优雅停止 Worker")

    async def _init(self) -> None:
        """初始化连接"""
        if not self.worker_settings.rabbitmq_settings:
            raise ValueError("必须提供 RabbitMQ 连接配置")

        logger.info(f"正在连接到 RabbitMQ: {self.worker_settings.rabbitmq_settings.rabbitmq_url}")
        self.connection = await connect_robust(self.worker_settings.rabbitmq_settings.rabbitmq_url)
        self.channel = await self.connection.channel()
        self.dlq_channel = await self.connection.channel()

        # 设置 QoS 限制预取消息数量
        await self.channel.set_qos(prefetch_count=self.worker_settings.rabbitmq_settings.prefetch_count)

        # 队列名称设置
        self.rabbitmq_queue = self.worker_settings.queue_name
        self.rabbitmq_dlq = self.worker_settings.dlq_name

        # 构建延迟机制相关名称（与 Client 保持一致）
        self._delayed_exchange_name = f"delayed.{self.worker_settings.queue_name}"
        self._delay_queue_name = f"delay.{self.worker_settings.queue_name}"

        # 声明主队列
        await self.channel.declare_queue(self.rabbitmq_queue, durable=True)

        # 声明死信队列
        await self.dlq_channel.declare_queue(self.rabbitmq_dlq, durable=True)

        # 检测延迟机制
        await self._setup_delay_mechanism()

        logger.info(f"成功连接到 RabbitMQ，队列: {self.rabbitmq_queue}")
        
        # 输出订阅的队列信息
        logger.info(f"📋 订阅队列: {self.rabbitmq_queue}")
        logger.info(f"💀 死信队列: {self.rabbitmq_dlq}")
        if hasattr(self, '_delay_queue_name'):
            logger.info(f"⏰ 延迟队列: {self._delay_queue_name}")
        
        # 输出注册的函数列表
        if self.worker_settings.functions:
            function_names = [func.__name__ for func in self.worker_settings.functions]
            logger.info(f"🔧 注册函数: {', '.join(function_names)}")
        else:
            logger.info("⚠️ 未注册任何函数")

    async def on_message(self, message: IncomingMessage) -> None:
        """
        处理 RabbitMQ 消息的回调方法，包含重试和失败转死信队列逻辑。
        """
        job_id = None
        
        # 提前检查是否允许接收新任务，避免消息被process后再reject
        if not self.allow_pick_jobs:
            # 直接reject，不进入process上下文
            await message.reject(requeue=True)
            logger.warning(f"Worker 正在关闭，拒绝消息处理")
            return
            
        async with message.process(requeue=False):  # 禁用自动重入队，防止重复消费
            headers = message.headers or {}
            retry_count = headers.get("x-retry-count", 0)

            try:
                # 解析消息
                job_data = json.loads(message.body.decode())
                job = JobModel(**job_data)
                job_id = job.job_id

                # 检查是否是客户端已处理的延迟任务
                client_delayed = headers.get("x-client-delayed") == "true"

                # 只有非客户端延迟任务才需要检查延迟执行时间
                if not client_delayed and job.defer_until:
                    now_utc = datetime.now(timezone.utc)
                    defer_dt = self._ensure_aware_utc(job.defer_until)
                    if defer_dt and defer_dt > now_utc:
                        delay_seconds = (defer_dt - now_utc).total_seconds()
                        logger.info(f"任务 {job_id} 需要延迟 {delay_seconds:.1f} 秒执行，发送到延迟队列")
                        # 发送到延迟队列，不阻塞当前处理
                        await self._send_to_delay_queue(job, delay_seconds)
                        return
                elif client_delayed:
                    logger.debug(f"任务 {job_id} 已由客户端处理延迟，直接执行")

                # 创建任务并执行（受并发限制）
                acquired = False
                try:
                    if self._job_semaphore is not None:
                        await self._job_semaphore.acquire()
                        acquired = True

                    task = asyncio.create_task(self._execute_job(job))
                    self.tasks[job_id] = task

                    # 等待任务完成
                    await task
                finally:
                    if acquired:
                        try:
                            self._job_semaphore.release()
                        except Exception:
                            pass

            except json.JSONDecodeError as e:
                logger.error(f"消息解析失败: {e}\n{message.body}")
                # 无法解析的消息直接发送到死信队列
                await self._send_to_dlq_with_error(message.body, headers, e, job_id="parse_failed")

            except Exception as e:
                logger.error(f"处理消息时发生错误: {e}\n{traceback.format_exc()}")

                # ARQ 风格错误处理
                error_category = ErrorClassification.get_error_category(e)

                # 不可重试的错误：立即发送到死信队列
                if not ErrorClassification.is_retriable_error(e):
                    logger.error(f"任务 {job_id} 遇到不可重试错误 ({error_category}): {type(e).__name__}: {e}")
                    await self._send_to_dlq_with_error(message.body, headers, e, job_id)
                    return

                # 可重试的错误：检查重试次数限制
                if retry_count >= self.worker_settings.max_retries:
                    logger.error(f"任务 {job_id} 已达到最大重试次数 {self.worker_settings.max_retries}")
                    await self._send_to_dlq_with_error(message.body, headers, e, job_id)
                    return

                # 准备重试：递增重试计数
                new_retry_count = retry_count + 1
                if job_id and job:
                    # 更新任务的尝试次数（用于下次执行）
                    job.job_try = new_retry_count + 1  # job_try 从1开始，表示执行次数

                # 计算退避时间（指数退避）
                delay_seconds = self.worker_settings.retry_backoff * (2 ** retry_count)

                # 发送到延迟队列进行重试
                if job_id and job:
                    await self._send_to_delay_queue(job, delay_seconds, new_retry_count)
                    logger.debug(
                        f"任务 {job_id} 第 {new_retry_count} 次重试，延迟 {delay_seconds:.1f} 秒 (错误类型: {type(e).__name__}, 分类: {error_category})")

            finally:
                # 从任务列表中移除
                if job_id and job_id in self.tasks:
                    del self.tasks[job_id]

    async def _execute_job(self, job: JobModel) -> Any:
        """
        执行单个任务
        """
        job.start_time = datetime.now(timezone.utc)
        job.status = JobStatus.IN_PROGRESS
        self.worker_info.jobs_ongoing = len(self.tasks)

        # 构建任务上下文
        job_ctx = JobContext(
            job_id=job.job_id,
            job_try=job.job_try,
            enqueue_time=job.enqueue_time,
            start_time=job.start_time,
            queue_name=job.queue_name,
            worker_id=self.worker_id,
            extra=self.ctx
        )

        try:
            # 调用 on_job_start 钩子
            if self.on_job_start:
                # 传递任务上下文和 Worker 统计信息
                hook_ctx = job_ctx.model_dump()
                hook_ctx['worker_stats'] = {
                    'jobs_complete': self.jobs_complete,
                    'jobs_failed': self.jobs_failed,
                    'jobs_retried': self.jobs_retried,
                    'jobs_ongoing': len(self.tasks)
                }
                await self.on_job_start(hook_ctx)

            # 获取要执行的函数
            func = self.functions.get(job.function)  # type: WorkerCoroutine
            if not func:
                logger.error(f"未找到函数: {job.function}")
                logger.error(f"可用函数列表: {list(self.functions.keys())}")
                raise ValueError(f"未找到函数: {job.function}")

            # 在调用任务函数前，基于函数的类型注解将 JSON 反序列化后的 dict/list
            # 自动重建为 Pydantic 模型或相应容器类型（不修改原始 job.args/kwargs）
            coerced_args, coerced_kwargs = self._coerce_task_args(func, job.args, job.kwargs)

            # 执行函数（带超时控制）
            logger.debug(f"开始执行任务 {job.job_id} - {job.function}")

            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(job_ctx, *coerced_args, **coerced_kwargs),
                    timeout=self.worker_settings.job_timeout
                )
            else:
                # 同步函数在线程池中执行
                loop = asyncio.get_running_loop()
                result = await asyncio.wait_for(
                    loop.run_in_executor(None, partial(func, job_ctx, *coerced_args, **coerced_kwargs)),
                    timeout=self.worker_settings.job_timeout
                )

            # 任务成功完成
            job.status = JobStatus.COMPLETED
            job.result = result
            job.end_time = datetime.now(timezone.utc)
            self.jobs_complete += 1

            logger.info(f"任务 {job.job_id} 执行成功，耗时 {(job.end_time - job.start_time).total_seconds():.2f} 秒")

            # 存储任务结果
            await self._store_job_result(job)

            # 无需更新全局统计，将通过钩子传递

        except asyncio.TimeoutError:
            job.status = JobStatus.FAILED
            job.error = f"任务执行超时 ({self.worker_settings.job_timeout}秒)"
            job.end_time = datetime.now(timezone.utc)
            self.jobs_failed += 1
            logger.error(f"任务 {job.job_id} 执行超时")
            # 存储失败结果
            await self._store_job_result(job)
            raise JobTimeout(job.error)

        except Retry as e:
            job.status = JobStatus.RETRYING
            job.error = str(e)
            self.jobs_retried += 1
            logger.warning(f"任务 {job.job_id} 请求重试: {e}")

            # 无需更新全局统计，将通过钩子传递

            # 在重试前检查次数（避免在 _enqueue_job_retry 中抛出异常）
            current_retry_count = job.job_try - 1  # job_try 从1开始，表示当前是第几次执行
            if current_retry_count >= self.worker_settings.max_retries:
                logger.error(f"任务 {job.job_id} 已达到最大重试次数 {self.worker_settings.max_retries}，发送到死信队列")
                job.status = JobStatus.FAILED
                job.error = f"任务超过最大重试次数 {self.worker_settings.max_retries}"
                job.end_time = datetime.now(timezone.utc)
                # 存储最终失败结果
                await self._store_job_result(job)
                return  # 直接返回，不再重试

            # 计算重试延迟
            if e.defer:
                if isinstance(e.defer, timedelta):
                    defer_seconds = e.defer.total_seconds()
                else:
                    defer_seconds = float(e.defer)
            else:
                # 指数退避（基于当前重试次数）
                defer_seconds = self.worker_settings.retry_backoff * (2 ** current_retry_count)

            # 重新入队前递增重试计数
            job.job_try += 1
            await self._enqueue_job_retry(job, defer_seconds)

        except Exception as e:
            job.status = JobStatus.FAILED
            job.error = f"{type(e).__name__}: {str(e)}"
            job.end_time = datetime.now(timezone.utc)
            self.jobs_failed += 1
            logger.error(f"任务 {job.job_id} 执行失败: {job.error}\n{traceback.format_exc()}")

            # 存储失败结果
            await self._store_job_result(job)

            # 无需更新全局统计，将通过钩子传递

            raise

        finally:
            job.end_time = datetime.now(timezone.utc)

            # 调用 on_job_end 钩子
            if self.on_job_end:
                # 传递任务上下文和更新后的 Worker 统计信息
                hook_ctx = job_ctx.model_dump()
                hook_ctx['worker_stats'] = {
                    'jobs_complete': self.jobs_complete,
                    'jobs_failed': self.jobs_failed,
                    'jobs_retried': self.jobs_retried,
                    'jobs_ongoing': len(self.tasks)
                }
                # 同步统计数据到全局 ctx（用于关闭钩子）
                self.ctx['jobs_complete'] = self.jobs_complete
                self.ctx['jobs_failed'] = self.jobs_failed
                self.ctx['jobs_retried'] = self.jobs_retried
                self.ctx['jobs_ongoing'] = len(self.tasks)

                await self.on_job_end(hook_ctx)

            # 调用 after_job_end 钩子
            if self.after_job_end:
                hook_ctx = job_ctx.model_dump()
                hook_ctx['worker_stats'] = {
                    'jobs_complete': self.jobs_complete,
                    'jobs_failed': self.jobs_failed,
                    'jobs_retried': self.jobs_retried,
                    'jobs_ongoing': len(self.tasks)
                }
                await self.after_job_end(hook_ctx)

            # 更新 Worker 信息
            self.worker_info.jobs_complete = self.jobs_complete
            self.worker_info.jobs_failed = self.jobs_failed
            self.worker_info.jobs_retried = self.jobs_retried
            self.worker_info.jobs_ongoing = len(self.tasks)

    def _coerce_task_args(self, func: WorkerCoroutine, args: list[Any], kwargs: dict[str, Any]) -> tuple[list[Any], dict[str, Any]]:
        """
        基于任务函数的类型注解，将 JSON 反序列化后的参数恢复为 Pydantic 模型或容器类型。
        仅用于调用时的参数转换，不修改原始 job.args/kwargs。

        Args:
            func: 任务函数
            args: 位置参数列表（不包含 ctx）
            kwargs: 关键字参数字典

        Returns:
            (coerced_args, coerced_kwargs): 转换后的参数
        """
        try:
            # 提取类型注解（解析前向引用、跨模块）
            type_hints = get_type_hints(func, globalns=getattr(func, "__globals__", None))
        except Exception:
            type_hints = {}

        try:
            params = list(inspect.signature(func).parameters.values())
        except Exception:
            params = []

        # 跳过第一个 ctx 参数，构造位置参数名序列
        positional_param_names: list[str] = [p.name for p in params[1:]] if params else []

        # 处理位置参数
        coerced_args: list[Any] = []
        for idx, value in enumerate(args):
            if idx < len(positional_param_names):
                name = positional_param_names[idx]
                annotation = type_hints.get(name, params[idx + 1].annotation if params else inspect._empty)
            else:
                annotation = inspect._empty

            coerced_args.append(self._coerce_single_value(value, annotation))

        # 处理关键字参数
        coerced_kwargs: dict[str, Any] = {}
        for k, v in kwargs.items():
            annotation = type_hints.get(k, inspect._empty)
            coerced_kwargs[k] = self._coerce_single_value(v, annotation)

        return coerced_args, coerced_kwargs

    @staticmethod
    def _get_type_adapter(annotation: Any) -> TypeAdapter | None:
        """获取或创建注解对应的 TypeAdapter，带本地缓存。"""
        try:
            key = repr(annotation)
            adapter = _TYPE_ADAPTER_CACHE.get(key)
            if adapter is None:
                adapter = TypeAdapter(annotation)
                _TYPE_ADAPTER_CACHE[key] = adapter
            return adapter
        except Exception:
            return None

    @staticmethod
    def _coerce_single_value(value: Any, annotation: Any) -> Any:
        """
        使用 Pydantic TypeAdapter 按注解将值转换为目标类型；失败则原样返回。
        支持 BaseModel 以及 list[Model]、dict[str, Model]、Optional[Model] 等容器/联合类型。
        """
        if annotation in (None, inspect._empty) or annotation is Any:
            return value
        try:
            adapter = Worker._get_type_adapter(annotation)
            return adapter.validate_python(value) if adapter else value
        except Exception:
            return value

    async def _enqueue_job_retry(self, job: JobModel, defer_seconds: float) -> None:
        """
        重新入队任务进行重试，使用延迟队列
        
        Args:
            job: 任务模型（包含正确的 job_try 计数）
            defer_seconds: 延迟时间（秒）
        """
        # 检查重试次数（job_try 已经在调用前正确设置）
        retry_count = job.job_try - 1
        if retry_count >= self.worker_settings.max_retries:
            logger.error(f"任务 {job.job_id} 重试次数 {retry_count} 已超过最大限制 {self.worker_settings.max_retries}")
            raise MaxRetriesExceeded(max_retries=self.worker_settings.max_retries, job_id=job.job_id)

        # 使用延迟队列进行重试
        await self._send_to_delay_queue(job, defer_seconds)

        logger.debug(f"任务 {job.job_id} 已发送到延迟队列进行重试，将在 {defer_seconds:.1f} 秒后执行 (重试次数: {retry_count})")

    async def _send_to_dlq(self, body: bytes, headers: dict[str, Any]) -> None:
        """
        将消息发送到死信队列
        """
        await self.dlq_channel.default_exchange.publish(
            Message(body=body, headers=headers),
            routing_key=self.rabbitmq_dlq
        )

    async def _send_to_dlq_with_error(self, body: bytes, headers: dict[str, Any], error: Exception, job_id: str | None = None) -> None:
        """
        将消息连同错误信息发送到死信队列
        
        Args:
            body: 消息体
            headers: 消息头
            error: 异常对象
            job_id: 任务ID
        """
        # 增强错误信息
        error_headers = headers.copy()
        error_headers.update({
            'x-error-type': type(error).__name__,
            'x-error-message': str(error),
            'x-error-category': ErrorClassification.get_error_category(error),
            'x-failed-at': datetime.now(timezone.utc).isoformat(),
            'x-job-id': job_id or 'unknown'
        })

        logger.error(f"任务 {job_id} 发送到死信队列: {type(error).__name__}: {error}")

        await self.dlq_channel.default_exchange.publish(
            Message(body=body, headers=error_headers),
            routing_key=self.rabbitmq_dlq
        )

    async def _send_to_delay_queue(self, job: JobModel, delay_seconds: float, retry_count: int | None = None) -> None:
        """
        将任务发送到延迟队列，自动选择最佳延迟机制
        
        Args:
            job: 任务模型
            delay_seconds: 延迟时间（秒）
            retry_count: 重试计数（如果提供，则使用此值；否则从 job.job_try 计算）
        """
        # 清除延迟时间，避免循环延迟
        job.defer_until = None

        # 序列化任务
        message_body = json.dumps(job.model_dump(), ensure_ascii=False, default=str).encode()

        # 确定重试计数
        if retry_count is not None:
            # 使用提供的重试计数
            actual_retry_count = retry_count
        else:
            # 从 job_try 计算重试计数
            actual_retry_count = job.job_try - 1 if job.job_try > 0 else 0
            
        headers = {"x-retry-count": actual_retry_count}

        if self._use_delayed_exchange:
            # 使用延迟插件（更优雅的方案）
            # 延迟时间通过 x-delay 头设置（毫秒）
            delay_ms = int(delay_seconds * 1000)
            headers['x-delay'] = delay_ms

            # 获取延迟交换机
            delayed_exchange = await self.channel.get_exchange(self._delayed_exchange_name)

            # 发送到延迟交换机
            await delayed_exchange.publish(
                Message(
                    body=message_body,
                    headers=headers
                ),
                routing_key=self.rabbitmq_queue
            )

            logger.debug(f"任务 {job.job_id} 已通过延迟交换机发送，将在 {delay_seconds:.1f} 秒后处理 (重试次数: {actual_retry_count})")

        else:
            # 使用 TTL + DLX 方案（降级方案）
            expiration = timedelta(seconds=delay_seconds)

            # 发送到 TTL 延迟队列
            await self.channel.default_exchange.publish(
                Message(
                    body=message_body,
                    headers=headers,
                    expiration=expiration  # TTL 设置
                ),
                routing_key=self._delay_queue_name
            )

            logger.debug(f"任务 {job.job_id} 已通过 TTL 队列发送，将在 {delay_seconds:.1f} 秒后处理 (重试次数: {actual_retry_count})")

    async def _setup_delay_mechanism(self) -> None:
        """
        检测并设置延迟机制：优先使用延迟插件，其次使用 TTL + DLX
        与 Client 的检测逻辑保持一致
        """
        if self._delay_mechanism_detected:
            return  # 已检测过

        logger.info(f"🔍 正在为队列 {self.worker_settings.queue_name} 检测延迟机制...")

        try:
            # 尝试声明延迟交换机（需要 rabbitmq_delayed_message_exchange 插件）
            delayed_exchange = await self.channel.declare_exchange(
                self._delayed_exchange_name,
                type='x-delayed-message',  # 特殊的延迟消息类型
                durable=True,
                arguments={
                    'x-delayed-type': 'direct'  # 实际的路由类型
                }
            )

            # 绑定延迟交换机到主队列
            queue = await self.channel.get_queue(self.rabbitmq_queue)
            await queue.bind(delayed_exchange, routing_key=self.rabbitmq_queue)

            self._use_delayed_exchange = True
            self._delay_mechanism_detected = True
            logger.info(f"✅ 队列 {self.worker_settings.queue_name} 检测到 RabbitMQ 延迟插件，使用延迟交换机模式")

        except Exception as e:
            # 插件未安装或声明失败，降级到 TTL + DLX 方案
            logger.warning(f"⚠️ 队列 {self.worker_settings.queue_name} 未检测到 RabbitMQ 延迟插件: {e}")
            logger.warning("💡 推荐安装 rabbitmq_delayed_message_exchange 插件以获得更好的延迟队列性能")
            logger.warning("   安装命令: rabbitmq-plugins enable rabbitmq_delayed_message_exchange")
            logger.info(f"📌 队列 {self.worker_settings.queue_name} 降级使用 TTL + Dead Letter Exchange 方案")

            try:
                # 重新创建一个新的 Channel（如果当前 Channel 有问题）
                if self.channel.is_closed:
                    logger.warning("🔄 当前 Channel 已关闭，重新创建...")
                    self.channel = await self.connection.channel()
                    await self.channel.set_qos(prefetch_count=self.worker_settings.rabbitmq_settings.prefetch_count)

                # 声明 TTL 延迟队列
                await self.channel.declare_queue(
                    self._delay_queue_name,
                    durable=True,
                    arguments={
                        'x-dead-letter-exchange': '',  # 默认交换机
                        'x-dead-letter-routing-key': self.rabbitmq_queue  # 路由到主队列
                    }
                )

                self._use_delayed_exchange = False
                self._delay_mechanism_detected = True
                logger.info(f"✅ 队列 {self.worker_settings.queue_name} TTL + DLX 延迟机制设置完成")

            except Exception as dlx_error:
                logger.error(f"❌ TTL + DLX 延迟机制设置失败: {dlx_error}")
                # 重新抛出异常，让调用者处理
                raise

    async def _health_check_loop(self) -> None:
        """
        健康检查循环
        """
        while self.allow_pick_jobs:
            try:
                self.worker_info.last_health_check = datetime.now(timezone.utc)
                # 健康检查：可以扩展添加更多检查逻辑（如 Redis 心跳等）
                logger.debug(f"健康检查 - Worker {self.worker_id} 正常运行")
                await asyncio.sleep(self.worker_settings.health_check_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"健康检查失败: {e}")

    async def _get_queue_message_count(self) -> int:
        """
        获取队列中的消息数量
        
        Returns:
            队列中待处理的消息数量
        """
        try:
            queue = await self.channel.declare_queue(self.rabbitmq_queue, durable=True, passive=True)
            return queue.declaration_result.message_count
        except Exception as e:
            logger.warning(f"获取队列消息数量失败: {e}")
            return 0

    async def _should_exit_burst_mode(self) -> bool:
        """
        检查是否应该退出 burst 模式
        
        Returns:
            True 如果应该退出 burst 模式
        """
        if not self._burst_mode:
            return False

        # 检查是否已标记为应该退出
        if self._burst_should_exit:
            return True

        # 检查超时
        if self._burst_start_time:
            elapsed = (datetime.now(timezone.utc) - self._burst_start_time).total_seconds()
            if elapsed >= self.worker_settings.burst_timeout:
                logger.info(f"🕐 Burst 模式超时 ({elapsed:.1f}s >= {self.worker_settings.burst_timeout}s)，准备退出")
                return True

        # 检查队列是否为空且没有正在执行的任务
        queue_count = await self._get_queue_message_count()
        running_tasks = len(self.tasks)

        if queue_count == 0 and running_tasks == 0:
            logger.info("🎯 Burst 模式: 队列为空且没有正在执行的任务，准备退出")
            return True

        # 如果配置了不等待任务完成，只检查队列是否为空
        if not self.worker_settings.burst_wait_for_tasks and queue_count == 0:
            logger.info("🎯 Burst 模式: 队列为空，立即退出（不等待正在执行的任务）")
            return True

        logger.debug(f"Burst 检查: 队列={queue_count}条消息, 运行中={running_tasks}个任务")
        return False

    async def _burst_monitor_loop(self) -> None:
        """
        Burst 模式监控循环
        """
        if not self._burst_mode:
            return

        logger.info(f"🚀 启动 Burst 模式监控 (超时: {self.worker_settings.burst_timeout}s)")
        self._burst_start_time = datetime.now(timezone.utc)

        while self.allow_pick_jobs and not self._burst_should_exit:
            try:
                if await self._should_exit_burst_mode():
                    logger.info("📤 Burst 模式退出条件满足，停止接收新任务")
                    self.allow_pick_jobs = False
                    self._burst_should_exit = True

                    # 如果需要等待任务完成
                    if self.worker_settings.burst_wait_for_tasks and self.tasks:
                        logger.info(f"⏳ 等待 {len(self.tasks)} 个正在执行的任务完成...")
                        await self._sleep_until_tasks_complete()

                    # 取消主任务以触发退出
                    if self.main_task:
                        self.main_task.cancel()
                    break

                await asyncio.sleep(self.worker_settings.burst_check_interval)

            except asyncio.CancelledError:
                logger.debug("Burst 监控循环被取消")
                break
            except Exception as e:
                logger.error(f"Burst 监控出错: {e}")
                await asyncio.sleep(1)

    async def consume(self) -> None:
        """
        开始消费消息
        """
        # 声明队列（Burst 和常规模式都需要）
        queue = await self.channel.declare_queue(self.rabbitmq_queue, durable=True)
        self._queue = queue  # 保存队列引用

        if self._burst_mode:
            # Burst 模式：检查队列是否为空
            initial_queue_count = await self._get_queue_message_count()
            if initial_queue_count == 0:
                logger.info("🎯 Burst 模式: 队列为空，立即退出")
                return

            logger.info(f"🚀 Burst 模式启动: 队列中有 {initial_queue_count} 条消息待处理")
            # 启动 burst 监控
            self._burst_check_task = asyncio.create_task(self._burst_monitor_loop())
        else:
            logger.info(f"[*] 等待队列 {self.rabbitmq_queue} 中的消息。按 CTRL+C 退出")

        # 开始健康检查（非 burst 模式或需要健康检查的 burst 模式）
        if not self._burst_mode or self.worker_settings.health_check_interval > 0:
            self._health_check_task = asyncio.create_task(self._health_check_loop())

        # 开始消费消息（Burst 和常规模式都需要）
        consumer_tag = await queue.consume(lambda message: asyncio.create_task(self.on_message(message)))
        self._consumer_tag = consumer_tag  # 保存消费者标签
        logger.debug(f"🔧 消息消费器已启动，consumer_tag: {consumer_tag}")

        try:
            # 等待关闭信号或被取消
            await self.shutdown_event.wait()
            logger.info("🛑 收到关闭信号，准备退出消费循环")
        except asyncio.CancelledError:
            if self._burst_mode:
                logger.info("🏁 Burst 模式消费者被取消")
            else:
                logger.info("🛑 常规模式消费者被取消")
            raise
        finally:
            # 关键改进：停止消息消费器
            if self._consumer_tag and not self.channel.is_closed:
                try:
                    logger.info("🔧 正在停止消息消费器...")
                    await self._safe_operation_with_timeout(
                        queue.cancel(self._consumer_tag),
                        "消息消费器停止",
                        timeout=5.0
                    )
                    logger.info("✅ 消息消费器已停止")
                    self._consumer_tag = None
                except Exception as e:
                    logger.warning(f"⚠️ 停止消费器时出现错误: {e}")

            # 清理后台任务
            if self._health_check_task:
                logger.debug("🔧 取消健康检查任务...")
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass

            if self._burst_check_task:
                logger.debug("🔧 取消 Burst 检查任务...")
                self._burst_check_task.cancel()
                try:
                    await self._burst_check_task
                except asyncio.CancelledError:
                    pass

            logger.info("✅ 消费循环清理完成")

    async def main(self) -> None:
        """
        Worker 主函数
        """
        start_time = datetime.now(timezone.utc)

        try:

            # 设置信号处理器（事件循环已经在运行）
            self._setup_signal_handlers()

            # Burst 模式启动信息
            if self._burst_mode:
                logger.info(f"🚀 启动 Burst 模式 Worker (超时: {self.worker_settings.burst_timeout}s)")
            else:
                logger.info("🚀 启动常规模式 Worker")
            # 初始化连接
            await self._init()

            # 验证结果存储连接（可配置降级或跳过）
            if getattr(self.worker_settings, 'enable_job_result_storage', True):
                await self._validate_result_store()

            # 启动钩子
            if self.on_startup:
                logger.info("执行启动钩子")
                await self.on_startup(self.ctx)

            # 记录主任务
            self.main_task = asyncio.current_task()

            # 开始消费
            await self.consume()

        except KeyboardInterrupt:
            logger.info("🛑 收到键盘中断信号 (SIGINT)，正在优雅关闭...")
        except asyncio.CancelledError:
            if self._burst_mode:
                # 计算运行时间和统计信息
                elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
                logger.info(f"🏁 Burst 模式正常结束 (运行时间: {elapsed:.1f}s)")
                logger.info(f"📊 任务统计: 完成 {self.jobs_complete} 个, "
                            f"失败 {self.jobs_failed} 个, "
                            f"重试 {self.jobs_retried} 个")
            else:
                logger.info("🛑 Worker 收到取消信号，正在优雅关闭...")
        except SystemExit as e:
            logger.info(f"🛑 系统退出信号: {e}")
        except Exception as e:
            logger.error(f"❌ Worker 运行出错: {e}")
            logger.error(f"详细错误信息:\n{traceback.format_exc()}")
            # 如果是连接错误，给出建议
            if "connection" in str(e).lower() or "rabbitmq" in str(e).lower():
                logger.error("💡 请检查:")
                logger.error("   1. RabbitMQ 服务是否正在运行")
                logger.error("   2. 连接配置是否正确")
                logger.error("   3. 网络连接是否正常")
            raise
        finally:
            # 等待最后的任务完成（如果在 burst 模式且配置了等待）
            if self._burst_mode and self.worker_settings.burst_wait_for_tasks and self.tasks:
                logger.info(f"⏳ 等待最后 {len(self.tasks)} 个任务完成...")
                try:
                    await asyncio.wait_for(
                        self._sleep_until_tasks_complete(),
                        timeout=30  # 最多等待30秒
                    )
                except asyncio.TimeoutError:
                    logger.warning("等待任务完成超时，强制退出")

            # 关闭钩子 - 使用超时保护
            if self.on_shutdown:
                logger.info("🔧 开始执行关闭钩子...")
                # 最终同步统计数据
                self.ctx['jobs_complete'] = self.jobs_complete
                self.ctx['jobs_failed'] = self.jobs_failed
                self.ctx['jobs_retried'] = self.jobs_retried
                self.ctx['jobs_ongoing'] = len(self.tasks)

                # 使用超时保护执行关闭钩子
                await self._safe_operation_with_timeout(
                    self.on_shutdown(self.ctx),
                    "关闭钩子 (on_shutdown)",
                    timeout=30.0
                )
                logger.info("✅ 关闭钩子执行完成")

            # 关闭连接 - 使用超时保护
            if self.connection and not self.connection.is_closed:
                logger.info("🔧 开始关闭 RabbitMQ 连接...")
                await self._safe_operation_with_timeout(
                    self.connection.close(),
                    "RabbitMQ 连接关闭",
                    timeout=10.0
                )
                logger.info("✅ RabbitMQ 连接已关闭")
            elif self.connection and self.connection.is_closed:
                logger.info("ℹ️ RabbitMQ 连接已经关闭")

    async def graceful_shutdown(self, reason: str = "用户请求") -> None:
        """
        Worker的优雅关闭方法 - 包含结果存储处理
        
        重写父类方法，增加结果存储的关闭处理
        
        Args:
            reason: 关闭原因，用于日志记录
        """
        running_tasks = len(self.tasks)
        logger.info(
            f'🔄 开始优雅关闭 Worker - 原因: {reason}'
            f' - 统计信息: ✅完成:{self.jobs_complete} ❌失败:{self.jobs_failed} '
            f'🔄重试:{self.jobs_retried} ⏳运行中:{running_tasks}'
        )

        # 停止接收新任务
        self.allow_pick_jobs = False

        # 立即取消消费者，停止接收新消息
        await self._cancel_consumer()

        # 如果有正在运行的任务，等待它们完成
        if running_tasks > 0:
            # 统一的超时时间获取逻辑
            timeout = (getattr(self.worker_settings, 'wait_for_job_completion_on_signal_second', None)
                       if self.worker_settings else None) or 30
            logger.info(f'⏳ 等待 {running_tasks} 个正在执行的任务完成（超时时间：{timeout}秒）')

            try:
                await asyncio.wait_for(
                    self._sleep_until_tasks_complete(),
                    timeout=timeout
                )
                logger.info('✅ 所有任务已完成，开始关闭连接')
            except asyncio.TimeoutError:
                remaining = len(self.tasks)
                logger.warning(f'⏰ 等待超时，强制取消 {remaining} 个未完成的任务')
                for t in self.tasks.values():
                    if not t.done():
                        t.cancel()

        # 关闭结果存储连接
        if self.result_store:
            try:
                await self.result_store.close()
                logger.info('✅ 结果存储连接已关闭')
            except Exception as e:
                logger.warning(f'⚠️ 关闭结果存储时出错: {e}')

        # 关闭连接 - 使用超时保护
        if self.connection and not self.connection.is_closed:
            await self._safe_operation_with_timeout(
                self.connection.close(),
                "RabbitMQ 连接关闭 (graceful_shutdown)",
                timeout=10.0
            )

        # 设置关闭事件
        self.shutdown_event.set()
        logger.info('✅ Worker 优雅关闭完成')

    @classmethod
    def run(cls, worker_settings: WorkerSettings) -> None:
        """
        同步启动 Worker，仅接受 WorkerSettings 实例。

        Args:
            worker_settings: Worker 配置对象（必须为 WorkerSettings 实例）
        """
        if not isinstance(worker_settings, WorkerSettings):
            raise TypeError("Worker.run 仅接受 WorkerSettings 实例")

        worker = cls(worker_settings)
        asyncio.run(worker.main())
