from sqlalchemy.engine import Engine


class ContextManager:

    _instance = None

    def __init__(
        self,
        engine: Engine
    ):
        """
        构造函数

        :param engine db engine
        """
        self.engine = engine

    @classmethod
    def init(cls, engine: Engine):
        """
        初始化上下文实例
        
        :param engine db engine
        """
        if not cls._instance:
            cls._instance = ContextManager(engine=engine)
        
        return cls._instance
    
    @classmethod
    def get_instance(cls):
        """
        获取ContextManager实例

        :return ContextManager实例
        """
        return cls._instance

    def get_engine(self):
        """
        获取db engine instance

        :return Engine实例
        """
        return self.engine
