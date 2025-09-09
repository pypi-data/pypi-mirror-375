import pytest
from enum import Enum
from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.exc import StatementError
from src.ff_sqlalchemy.types.db_str_py_enum import DbStrPyEnum

Base = declarative_base()

class Color(Enum):
    RED = 'red'
    GREEN = 'green'
    BLUE = 'blue'

class Item(Base):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True)
    color = Column(DbStrPyEnum(Color), nullable=True)

def setup_db():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()

def test_bind_param_accepts_enum():
    session = setup_db()
    item = Item(color=Color.RED)
    session.add(item)
    session.commit()
    assert session.query(Item).first().color == Color.RED

def test_bind_param_accepts_none():
    session = setup_db()
    item = Item(color=None)
    session.add(item)
    session.commit()
    assert session.query(Item).first().color is None

def test_bind_param_rejects_invalid_type():
    session = setup_db()
    item = Item(color='red')  # 不是 Color 枚举
    session.add(item)
    with pytest.raises(StatementError) as excinfo:
        session.commit()
    assert 'invalid value' in str(excinfo.value)

def test_result_value_invalid_db_value():
    session = setup_db()
    # 直接插入非法值
    from sqlalchemy import text
    session.execute(text("INSERT INTO items (id, color) VALUES (1, 'yellow')"))
    with pytest.raises(RuntimeError) as excinfo:
        session.query(Item).first()
    assert 'invalid value' in str(excinfo.value)

def test_result_value_none():
    # color 字段非空，这里只测试 process_result_value 的 None 情况
    enum_type = DbStrPyEnum(Color)
    assert enum_type.process_result_value(None, None) is None
