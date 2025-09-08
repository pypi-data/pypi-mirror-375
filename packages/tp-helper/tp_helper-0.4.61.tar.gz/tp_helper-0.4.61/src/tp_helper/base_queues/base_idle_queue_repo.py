from redis.asyncio import Redis
from tp_helper.base_queues.base_queue_repo import BaseQueueRepo
from tp_helper.decorators.decorator_retry_forever import retry_forever


class BaseIdleQueueRepo(BaseQueueRepo):
    def __init__(self, redis_client: Redis):
        super().__init__(redis_client)

    async def signal(self):
        await self.redis_client.rpush(self.QUEUE_NAME, "")

    async def wait(self, timeout: int = 0, clear: bool = True) -> str | None:
        result = await self.redis_client.blpop([self.QUEUE_NAME], timeout=timeout)
        if result is None:
            return None
        _, data = result
        if clear:
            await self.redis_client.delete(self.QUEUE_NAME)
        return str(data)

    @retry_forever(
        start_message="Ожидаем сигнал по очереди {QUEUE_NAME}",
        error_message="Ошибка при ожидании сигнала по очереди {QUEUE_NAME}",
    )
    async def wait_with_retry(self, timeout: int = 60) -> None:
        await self.wait(timeout=timeout)

    @retry_forever(
        start_message="Сигнализируем по очереди {QUEUE_NAME}",
        error_message="Ошибка сигнализирования по очереди {QUEUE_NAME}",
    )
    async def signal_with_retry(self):
        await self.signal()
