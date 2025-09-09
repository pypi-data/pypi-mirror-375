import pytest
from sqlalchemy import create_engine, select
from ff_sqlalchemy.orm import Base
from ff_sqlalchemy import ContextManager
from ff_sqlalchemy.session import Session
from .models import User, UserRole


@pytest.fixture(scope="function", autouse=True)
def init_session():
    ContextManager._instance = None
    
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    ContextManager.init(engine=engine)

    yield
    engine.dispose()
    ContextManager._instance = None


def add_user(user_id:int, name: str, role: str):
    with Session() as session:
        with session.begin():
            session.add(User(id=user_id, name=name))
            add_user_role(user_id=user_id, role=role)

def add_user_role(user_id: int, role: str):
    with Session() as session:
        with session.begin():
            if role != "admin":
                raise Exception("invalidate role")
            session.add(UserRole(user_id=user_id, role=role))

def test_transaction_commit():
    user_id = 1
    name = "foris"
    role = "admin"
    add_user(user_id=user_id, name=name, role=role)

    with Session() as session:
        db_user = session.scalar(select(User).where(User.id == 1))
        db_role = session.scalar(select(UserRole).where(UserRole.user_id == 1))

    assert db_user.id == user_id
    assert db_user.name == name
    assert db_role.user_id == user_id
    assert db_role.role == role

def test_transaction_rollback():
    try:
        user_id = 1
        name = "foris"
        role = "tester"
        add_user(user_id=user_id, name=name, role=role)
    except:
        pass

    with Session() as session:
        db_user = session.scalar(select(User).where(User.id == 1))
        db_role = session.scalar(select(UserRole).where(UserRole.user_id == 1))

    assert db_user is None
    assert db_role is None