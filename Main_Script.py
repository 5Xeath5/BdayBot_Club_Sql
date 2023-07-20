import os
from sqlalchemy import create_engine, text

engine = create_engine(os.environ["DATABASE_URL"])
conn = engine.connect()

res = conn.execute(text("SELECT now()")).fetchall()
print(res)

