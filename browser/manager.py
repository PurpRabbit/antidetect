from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from browser.models import Base


class ObjectsManager:
    engine = create_engine("sqlite:///database.db")
    Session = sessionmaker(bind=engine)
    session = Session()

    Base.metadata.create_all(engine)

    @classmethod
    def create(cls, obj):
        cls.session.add(obj)
        cls.session.commit()

    @classmethod
    def get(cls, stmt):
        return cls.session.execute(stmt).first()

    @classmethod
    def update(cls, stmt):
        cls.session.execute(stmt)
        cls.session.commit()

    @classmethod
    def delete(cls, stmt):
        cls.session.execute(stmt)
        cls.session.commit()

    @classmethod
    def all(cls, model) -> list:
        return cls.session.query(model).all()
