from sqlalchemy.ext.asyncio import AsyncSession


class AsyncSessionProxy:
    
    def __init__(self, session: AsyncSession):
        """
        构造函数

        :param session: 实际的异步会话对象
        """
        self._session = session

    def __getattr__(self, item):
        """
        获取属性或方法

        :param item: 属性或方法名
        :return: 属性或方法的值
        :raises AttributeError: 如果属性或方法不存在
        """
        return getattr(self._session, item)

    def begin(self):
        """
        开启事务

        :return: 异步上下文管理器
        """
        if self._session.in_transaction():
            class DummyContext:
                async def __aenter__(self_):
                    return self._session
                async def __aexit__(self_, exc_type, exc, tb):
                    return False
            return DummyContext()
        else:
            return self._session.begin()