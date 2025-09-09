from datetime import datetime
from .models import User, Status


def test_to_dict():
    user = User(id=1, name="foris", status=Status.ENABLE, created_at=datetime.now())
    user_dict = user.to_dict(exclude=["status"])
    dtf = "%Y-%m-%d %H:%M:%S"

    assert user_dict == {
        "id": 1,
        "name": "foris",
        "created_at": user.created_at.strftime(dtf)
    }
