from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(128), default="")
    role = db.Column(db.String(50), default="user")
    opened_requests = db.relationship("Request", primaryjoin="User.id == Request.creator_id")
    assigned_requests = db.relationship("Request", primaryjoin="User.id == Request.solver_id")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, name, email, password, role="user"):
        self.name = name
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        return self.password == password


    def __repr__(self):
        return "<User %r>" % self.name


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    creator = db.relationship("User", back_populates="opened_requests", foreign_keys=[creator_id])
    solver_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    solver = db.relationship("User", back_populates="assigned_requests", foreign_keys=[solver_id])
    title = db.Column(db.String(50))
    description = db.Column(db.String(250))
    status = db.Column(db.String(50), default="Opened")
    comments = db.relationship("Comment")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, title: str, description: str, solver_id: int, creator_id: int):
        self.title = title
        self.description = description
        self.solver_id = solver_id
        self.creator_id = creator_id

    def __repr__(self):
        return "<Request %r>" % self.title


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("request.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    content = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return "<Comment %r>" % self.id


class RequestStatus(db.Model):
    status_id = db.Column(db.Integer, primary_key=True)
    status_name = db.Column(db.String(50))

    def __repr__(self):
        return "<RequestStatus %r>" % self.status_name


class RequestHistory(db.Model):
    history_id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, db.ForeignKey("request.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    status_id = db.Column(db.Integer, db.ForeignKey("request_status.status_id"))
    description = db.Column(db.String(250))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, request_id: int, user_id: int, status_id: int, description: str):
        self.request_id = request_id
        self.user_id = user_id
        self.status_id = status_id
        self.description = description

    def __repr__(self):
        return "<RequestHistory %r>" % self.history_id
