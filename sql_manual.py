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
                            modId INT NOT NULL,
                            userId INT[] NOT NULL DEFAULT array[]::INT[],
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
        
        print("Guilds")
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

def UsersCreate():
    engine = sa.create_engine(os.environ["DATABASE_URL"])
    with engine.connect() as conn:
        statement1 = (
        """
        CREATE TABLE IF NOT EXISTS Users(
            userID INT PRIMARY KEY NOT NULL,
            date DATE NOT NULL,
            INDEX (userID)
        );   
        """
        )
        conn.execute(sa.text(statement1))
        conn.commit()
        conn.close()

def UsersShow():
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    with engine.connect() as conn:
        statement1 = "SELECT * FROM Users;"
        result = conn.execute(sa.text(statement1))
        conn.commit()
        conn.close()

        print("Users")
        for row in result:
            print(row)

def UsersDrop():
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    with engine.connect() as conn:
        statement1 = "DROP TABLE IF EXISTS Users"
        conn.execute(sa.text(statement1))
        conn.commit()
        conn.close()


def DatesShow():
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    with engine.connect() as conn:
        statement1 = "SELECT * FROM Dates;"
        result = conn.execute(sa.text(statement1))
        conn.commit()
        conn.close()

        print("Dates")
        for row in result:
            print(row)

def DatesDrop():
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    with engine.connect() as conn:
        statement1 = "DROP TABLE IF EXISTS Dates"
        conn.execute(sa.text(statement1))
        conn.commit()
        conn.close()

def test():
    engine = sa.create_engine(os.environ["DATABASE_URL"])
    guildID = 229617924241883136

    with engine.connect() as conn:
        statement3 = (
        f"""
        SELECT userID
        FROM Guilds
        WHERE guildID = {guildID}
        """
        )
        results = conn.execute(sa.text(statement3))
        conn.commit()
        conn.close()
        
        arr = results.first()[0]
        print(type(arr))

def AllDrop():
    GuildsDrop()
    UsersDrop()
    DatesDrop()

def AllShow():
    GuildsShow()
    UsersShow()
    DatesShow()

if __name__ == "__main__":
    AllShow()