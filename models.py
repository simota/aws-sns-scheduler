from datetime import datetime
from sqlalchemy import create_engine, MetaData, Column, Integer, String, Text, DATETIME
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///notfication.db', echo=False)
Session = scoped_session(sessionmaker(
    autocommit=False, autoflush=False, bind=engine))
metadata = MetaData(engine)
Base = declarative_base()


class Notfication(Base):
    __tablename__ = 'notfications'
    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(Text, nullable=False)
    delivery_status = Column(Integer, nullable=False)
    scheduled_at = Column(DATETIME, nullable=False)
    created_at = Column(DATETIME, default=datetime.now, nullable=False)
    updated_at = Column(DATETIME, default=datetime.now, nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'delivery_status': self.delivery_status,
            'message': self.message,
            'scheduled_at': self.scheduled_at.strftime('%Y-%m-%d %H:%M:%S')
        }

    def delivered(self):
        return delivery_status == 1


class NotficationStore:

    def __init__(self, session):
        self.session = session

    def add(self, message, schedule):
        notfication = Notfication()
        notfication.message = message
        notfication.delivery_status = 0
        notfication.scheduled_at = schedule
        self.session.add(notfication)
        self.session.commit()
        return notfication

    def remove(self, notfication_id):
        notfication = self.find(notfication_id)
        if notfication is not None:
            self.session.delete(notfication)
            self.session.commit()

    def update(self, notfication_id, params):
        self.session.query(Notfication).filter_by(
            id=notfication_id).update(params)
        self.session.commit()

    def close(self):
        self.session.close()

    def find(self, notfication_id):
        return self.session.query(Notfication) \
            .filter_by(id=notfication_id) \
            .first()

    def filter_by(self, params):
        return self.session.query(Notfication) \
            .filter_by(**params) \
            .order_by("scheduled_at desc") \
            .all()

    def all(self):
        return self.session.query(Notfication) \
            .order_by("scheduled_at desc") \
            .all()


Base.metadata.create_all(engine)


def create_store():
    return NotficationStore(Session())
