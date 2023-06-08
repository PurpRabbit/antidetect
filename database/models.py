from sqlalchemy import Column, Integer, String, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()


class ProfileModel(Base):
    __tablename__ = "profile"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(64))
    user_agent = Column("user_agent", String(256))
    proxy_id = Column("proxy_id", Integer, default=0)
    description = Column("description", Text, default=None)


class ProxyModel(Base):
    __tablename__ = "proxy"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    server = Column("server", String(64), unique=True)
    is_valid = Column("is_valid", Boolean, default=None)
    country = Column("country", String(64), default=None)

    def split_server(self) -> tuple[str]:
        user_data, ip_address = self.server.split('@')
        return tuple(user_data.split(':') + ip_address.split(':'))