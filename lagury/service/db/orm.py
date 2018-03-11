from sqlalchemy import Column, Integer, Boolean, DateTime, Text, create_engine, MetaData, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.sql import func

from ..config import DB_CREDENTIALS


engine = create_engine('postgresql://{user}:{password}@{host}:{port}/{db}'.format(**DB_CREDENTIALS))
metadata = MetaData(bind=engine)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()


class Project(Base):
    """"""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    root_dir = Text()

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


class Task(Base):
    """"""
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    status = Text()
    root_dir = Text()
    task_instance_path = Text()
    task_source_path = Text()

    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    input_node_id = Column(Integer, ForeignKey('data_nodes.id'), nullable=False)
    output_node_id = Column(Integer, ForeignKey('data_nodes.id'), nullable=False)

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    def to_dict(self):
        self_dict = self.__dict__
        self_dict = {key: value for key, value in self_dict.items() if key != '_sa_instance_state'}
        return self_dict


class DataNode(Base):
    """"""
    __tablename__ = 'data_nodes'

    id = Column(Integer, primary_key=True, autoincrement=False, nullable=False)
    is_ready = Boolean()
    root_dir = Text()

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


# create tables
Base.metadata.create_all(engine)
