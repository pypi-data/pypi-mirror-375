from sqlalchemy import create_engine

from castoranalytics.core.singleton import singleton
from castoranalytics.core.db.models.basemodel import BaseModel


@singleton
class Engine:
    def __init__(self):
        self._engine = create_engine(f'sqlite:///db.sqlite3', echo=False)
        BaseModel.metadata.create_all(self._engine)

    def get(self):
        return self._engine