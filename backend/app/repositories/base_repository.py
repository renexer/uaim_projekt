from app.extensions import db


class BaseRepository:
    model = None

    def __init__(self, session=None):
        self.session = session or db.session

    def add(self, entity):
        self.session.add(entity)
        return entity

    def get(self, entity_id):
        return self.model.query.get(entity_id)

    def delete(self, entity):
        self.session.delete(entity)

    def commit(self):
        self.session.commit()

    def flush(self):
        self.session.flush()
