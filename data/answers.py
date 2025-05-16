import sqlalchemy
from .db_session import SqlAlchemyBase


class Answers(SqlAlchemyBase):
    __tablename__ = 'Answers'
    id = sqlalchemy.Column(sqlalchemy.Integer, 
                        primary_key=True, autoincrement=True)
    author = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    answer = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    datetime = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    catalog_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    question_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)