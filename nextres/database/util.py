from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def first_or_instance(model, **kwargs):
    instance = model.query.filter_by(**kwargs).first()
    if not instance:
        instance = model(**kwargs)
    return instance
