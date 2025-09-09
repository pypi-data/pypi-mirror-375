from datetime import datetime
from sqlalchemy.orm import declarative_base


Base = declarative_base()

class BaseModel(Base):

    __abstract__ = True

    def to_dict(self, exclude=[]) -> dict:
        """
        转成dict

        :param exclude 排除的字段
        :return dict对象
        """
        _fmt_data = {}
        exclude = exclude if exclude else []
        dtf = "%Y-%m-%d %H:%M:%S"
        
        for col in self.__table__.columns:
            if col.name in exclude:
                continue

            value = getattr(self, col.name)
            _fmt_data[col.name] = value if not isinstance(value, datetime) else value.strftime(dtf)

        return _fmt_data