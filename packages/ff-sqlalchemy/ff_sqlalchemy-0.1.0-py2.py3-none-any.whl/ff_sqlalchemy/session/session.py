from contextvars import ContextVar
from typing import Optional
from sqlalchemy.orm import (
    Session as SqlalchemySession, 
    sessionmaker
)

from ..context import ContextManager
from .session_proxy import SessionProxy


_session_context: ContextVar[Optional[SqlalchemySession]] = ContextVar("_session_context", default=None)
_session_counter: ContextVar[int] = ContextVar("_session_counter", default=0)


class Session:

    def __init__(self):
        """
        构造函数
        """
        self._is_outermost = False
        self._token_session = None
        self._token_counter = None
        self._session = None

    def __enter__(self) -> SqlalchemySession:
        """
        进入上下文管理器

        :return: 异步会话代理对象
        """
        current_session = _session_context.get()
        current_counter = _session_counter.get()

        if current_session is None:
            # 最外层，创建新session
            engine = ContextManager.get_instance().get_engine()
            session_maker = sessionmaker(bind=engine, expire_on_commit=False, class_=SqlalchemySession)
            session = session_maker()
            self._token_session = _session_context.set(session)
            self._token_counter = _session_counter.set(1)
            self._is_outermost = True
            self._session = session.__enter__()
            return SessionProxy(self._session)
        else:
            # 内层，复用session，计数+1
            _session_counter.set(current_counter + 1)
            return SessionProxy(current_session)

    def __exit__(self, exc_type, exc, tb):
        """
        退出上下文管理器
        
        :param exc_type: 异常类型
        :param exc: 异常实例
        :param tb: 异常追踪信息
        :return: None
        """
        current_counter = _session_counter.get()
        if self._is_outermost:
            # 最外层退出，关闭session
            self._session.__exit__(exc_type, exc, tb)
            _session_context.reset(self._token_session)
            _session_counter.reset(self._token_counter)
        else:
            _session_counter.set(current_counter - 1)