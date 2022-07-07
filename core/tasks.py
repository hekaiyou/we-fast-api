import asyncio
from loguru import logger
from functools import wraps
from asyncio import ensure_future
from starlette.concurrency import run_in_threadpool
from typing import Any, Callable, Coroutine, Optional, Union

NoArgsNoReturnFuncT = Callable[[], None]
NoArgsNoReturnAsyncFuncT = Callable[[], Coroutine[Any, Any, None]]
NoArgsNoReturnDecorator = Callable[
    [Union[NoArgsNoReturnFuncT,
           NoArgsNoReturnAsyncFuncT]], NoArgsNoReturnAsyncFuncT]


def repeat_task(
    *,
    seconds: float,
    wait_first: bool = False,
    raise_exceptions: bool = False,
    max_repetitions: Optional[int] = None,
) -> NoArgsNoReturnDecorator:
    """
    返回一个修饰器, 该修饰器修改函数, 使其在首次调用后定期重复执行.
    其装饰的函数不能接受任何参数并且不返回任何内容.
    参数:
        seconds: float
            等待重复执行的秒数
        wait_first: bool (默认 False)
            如果为 True, 该函数将在第一次调用前先等待一个周期.
        raise_exceptions: bool (默认 False)
            如果为 True, 该函数抛出的错误将被再次抛出到事件循环的异常处理程序.
        max_repetitions: Optional[int] (默认 None)
            该函数重复执行的最大次数, 如果为 None, 则该函数将永远重复.
    """

    def decorator(
        func: Union[NoArgsNoReturnAsyncFuncT, NoArgsNoReturnFuncT]
    ) -> NoArgsNoReturnAsyncFuncT:
        """
        将修饰函数转换为自身重复且定期调用的版本.
        """
        is_coroutine = asyncio.iscoroutinefunction(func)

        @wraps(func)
        async def wrapped() -> None:
            repetitions = 0

            async def loop() -> None:
                nonlocal repetitions
                if wait_first:
                    await asyncio.sleep(seconds)
                while max_repetitions is None or repetitions < max_repetitions:
                    try:
                        if is_coroutine:
                            # 以协程方式执行
                            await func()  # type: ignore
                        else:
                            # 以线程方式执行
                            await run_in_threadpool(func)
                        repetitions += 1
                    except Exception as exc:
                        logger.error(f'执行重复任务异常: {exc}')
                        if raise_exceptions:
                            raise exc
                    await asyncio.sleep(seconds)

            ensure_future(loop())

        return wrapped

    return decorator
