from contextvars import ContextVar
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession as SqlalchemyAsyncSession
from sqlalchemy.orm import sessionmaker as async_sessionmaker

from ...context import ContextManager
from .session_proxy import AsyncSessionProxy


_session_context: ContextVar[Optional[SqlalchemyAsyncSession]] = ContextVar("_session_context", default=None)
_session_counter: ContextVar[int] = ContextVar("_session_counter", default=0)


class AsyncSession:

    def __init__(self):
        """
        构造函数
        """
        self._is_outermost = False
        self._token_session = None
        self._token_counter = None
        self._real_session = None

    async def __aenter__(self) -> SqlalchemyAsyncSession:
        """
        进入异步上下文管理器

        :return: 异步会话代理对象
        """
        current_session = _session_context.get()
        current_counter = _session_counter.get()

        if current_session is None:
            engine = ContextManager.get_instance().get_engine()
            session_maker = async_sessionmaker(
                bind=engine, expire_on_commit=False, class_=SqlalchemyAsyncSession
            )

            session = session_maker()
            self._token_session = _session_context.set(session)
            self._token_counter = _session_counter.set(1)
            self._is_outermost = True
            self._real_session = await session.__aenter__()
            return AsyncSessionProxy(self._real_session)
        else:
            # 内层，复用session，计数+1
            _session_counter.set(current_counter + 1)
            return AsyncSessionProxy(current_session)

    async def __aexit__(self, exc_type, exc, tb):
        """
        退出异步上下文管理器
        
        :param exc_type: 异常类型
        :param exc: 异常实例
        :param tb: 异常追踪信息
        :return: None
        """
        current_counter = _session_counter.get()
        if self._is_outermost:
            # 最外层退出，关闭session
            await self._real_session.__aexit__(exc_type, exc, tb)
            _session_context.reset(self._token_session)
            _session_counter.reset(self._token_counter)
        else:
            _session_counter.set(current_counter - 1)