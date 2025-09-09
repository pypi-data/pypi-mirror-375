from typing import Type
from enum import Enum
from sqlalchemy import String, TypeDecorator


class DbStrPyEnum(TypeDecorator):
    
    impl = String
    cache_ok = True

    def __init__(
        self, 
        enum_class: Type[Enum],
        length: int = 20, 
        *args, 
        **kwargs
    ):
        """
        构造函数

        :param enum_class 枚举类
        :param length 枚举值在数据库中的字符串长度
        :param args
        :param kwargs
        """
        super().__init__(length=length, *args, **kwargs)
        self.enum_class = enum_class

    def process_bind_param(self, value, dialect):
        """
        执行数据库操作时，参数预处理

        :param value 参数值
        :param dialect
        :return 处理后的参数值
        """
        if value is None:
            return None
        
        if not isinstance(value, self.enum_class):
            raise RuntimeError(
                f"invalid value: {value}, expected instance of {self.enum_class.__name__}"
            )

        return value.value

    def process_result_value(self, value, dialect):
        """
        读取数据库查询结果时，结果值预处理

        :param value 数据库查询结果值
        :param dialect
        :return 处理后的结果值
        """
        if value is None or isinstance(value, self.enum_class):
            return value
        
        values = [item.value for item in self.enum_class]
        if value not in values:
            raise RuntimeError(
                f"invalid value: {value!r}, expected one of: {values} for enum {self.enum_class.__name__}"
            )

        return self.enum_class(value)