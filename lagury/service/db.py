import json
from sqlalchemy import Column, Integer, DateTime, Text, create_engine, MetaData, ForeignKey
from sqlalchemy.schema import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session, relationship
from sqlalchemy.sql import func

from . import config


engine = create_engine(config.DB_CONN_SETTING)
metadata = MetaData(bind=engine)
session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = session.query_property()

task_input_nodes = Table('task_input_nodes',
                         Base.metadata,
                         Column('task_id', Integer, ForeignKey('tasks.id')),
                         Column('input_node_id', Integer, ForeignKey('data_nodes.id')))


class Task(Base):
    """"""
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    status = Column(Text, default='pending')
    parameters_json = Column(Text, default='{}')
    launch_file_name = Column(Text, nullable=False)
    description = Column(Text, default='')
    priority = Column(Integer, nullable=False, default=1)

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

    source_node_id = Column(Integer, ForeignKey('data_nodes.id'))
    source_node = relationship('DataNode', foreign_keys=[source_node_id])

    output_node_id = Column(Integer, ForeignKey('data_nodes.id'))
    output_node = relationship('DataNode', foreign_keys=[output_node_id])

    input_nodes = relationship('DataNode', secondary=task_input_nodes)

    @property
    def parameters(self):
        return json.loads(self.parameters_json)

    @parameters.setter
    def parameters(self, value: dict):
        if not isinstance(value, dict):
            raise ValueError('Parameters should be dictionary.')

        self.parameters_json = json.dumps(value)

    @classmethod
    def get_pending(cls):
        return cls.query.filter(cls.status == 'pending').order_by(cls.priority.desc(), cls.time_created.asc()).first()


class DataNode(Base):
    """"""
    __tablename__ = 'data_nodes'

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    status = Column(Text, default='pending')
    target_dir = Column(Text)
    description = Column(Text, default='')

    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())


# create tables
Base.metadata.create_all(engine)
