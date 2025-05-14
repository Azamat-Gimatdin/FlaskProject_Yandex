import sqlalchemy
from .db_session import SqlAlchemyBase
from werkzeug.security import check_password_hash
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'Users'
    id = sqlalchemy.Column(sqlalchemy.Integer, 
                        primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    email = sqlalchemy.Column(sqlalchemy.String, 
                                index=True, unique=True, nullable=True)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)