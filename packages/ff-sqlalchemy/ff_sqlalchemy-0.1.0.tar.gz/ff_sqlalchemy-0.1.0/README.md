
# ff-sqlalchemy

一个简洁易用的 SQLAlchemy 封装库，简化数据库操作流程。

## 功能简介

- 基于 SQLAlchemy 封装，支持常用 ORM 操作
- 提供简洁的上下文管理和会话管理
- 支持枚举类型映射
- 便于扩展和集成到现有项目

## 安装

```bash
pip install ff-sqlalchemy
```

## 快速开始

```python
from enum import Enum
from datetime import datetime
from sqlalchemy import create_engine, select, Column, Integer, String, DateTime

from ff_sqlalchemy import ContextManager
from ff_sqlalchemy.orm import Base, BaseModel
from ff_sqlalchemy.session import Session
from ff_sqlalchemy.types import DbStrPyEnum


class Status(Enum):

    ENABLE = 'enable'
    DISABLE = 'disable'

class User(BaseModel):
    
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String(20))
    status = Column(DbStrPyEnum(enum_class=Status), default=Status.ENABLE)
    created_at = Column(DateTime, default=datetime.now())

def add_user(user_id:int, name: str):
    with Session() as session:
        with session.begin():
            session.add(User(id=user_id, name=name))

def get_user(user_id:int):
    with Session() as session:
        return session.scalar(select(User).where(User.id == 1))

if __name__ == "__main__":

    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    ContextManager.init(engine=engine)

    add_user(user_id=1, name="foris")
    user = get_user(user_id=1)

    print(user.to_dict())
    # {id: 1, name: "foris", status: "enable", created_at: "xxxx-xx-xx xx:xx:xx"}
```

## 更多示例

请参考 `tests` 目录下的用例，涵盖模型定义、增删查改、事务管理等场景。

## 贡献指南

欢迎提交 Issue 或 PR，完善功能或修复问题。请确保代码风格与项目保持一致，并补充必要的测试。

## License

MIT