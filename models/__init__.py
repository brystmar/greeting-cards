from sqlalchemy import create_engine

engine = create_engine("sqlite+pysqlite:///greeting-cards.sqlite3", echo=True, future=True)
