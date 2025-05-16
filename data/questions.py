import sqlalchemy
from .db_session import SqlAlchemyBase


class Questions(SqlAlchemyBase):
    __tablename__ = 'Questions'
    id = sqlalchemy.Column(sqlalchemy.Integer, 
                        primary_key=True, autoincrement=True)
    title = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    content = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    datetime = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    catalog_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    question_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)