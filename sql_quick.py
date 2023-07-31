from importlib.metadata import metadata
import sqlalchemy as sa
import os


def GuildsDrop():
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    with engine.connect() as conn:
        statement1 = "DROP TABLE IF EXISTS Guilds"
        conn.execute(sa.text(statement1))
        conn.commit()
        conn.close()

def Guildsheck():
    engine = sa.create_engine(os.environ["DATABASE_URL"])
    insp = sa.inspect(engine)
    print(insp.get_table_names())

def GuildsCreate():
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    with engine.connect() as conn:
        statement1 = """CREATE TABLE IF NOT EXISTS Guilds(
	                        guildId INT PRIMARY KEY NOT NULL,
                            channelId INT NOT NULL,
                            modId INT NULL,
	                        INDEX (guildId)
                        );"""
        conn.execute(sa.text(statement1))
        conn.commit()
        conn.close()

def GuildsShow():
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    with engine.connect() as conn:
        statement1 = "SELECT * FROM Guilds;"
        result = conn.execute(sa.text(statement1))
        conn.commit()
        conn.close()

        for row in result:
            print(row)

def GuildsDelete():
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    with engine.connect() as conn:
        statement1 = (
        """DELETE FROM Guilds
        WHERE guildID = 229617924241883136;""")
        conn.execute(sa.text(statement1))
        conn.commit()
        conn.close()

if __name__ == "__main__":
    GuildsShow()