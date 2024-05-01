from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean, Text


Base = declarative_base()


class ProfileModel(Base):
    __tablename__ = "profile"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    name = Column("name", String(32))
    user_agent = Column("user_agent", String(256))
    status = Column("status", String(32), default=None)
    proxy_server = Column("proxy_server", String(256), default=None)
    note = Column("note", Text, default=None)


class ProxyModel(Base):
    __tablename__ = "proxy"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    server = Column("server", String(64), unique=True)
    is_valid = Column("is_valid", Boolean, default=None)
    country = Column("country", String(64), default=None)


class WalletModel(Base):
    __tablename__ = "wallet"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    private_key = Column("private_key", String(64), unique=True)
