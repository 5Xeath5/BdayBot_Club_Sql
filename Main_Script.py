from cmath import inf
import os
from tabnanny import check
import sqlalchemy as sa
import hikari
import lightbulb

bot = lightbulb.BotApp(token=os.environ["BOT_TOKEN"], intents=hikari.Intents.ALL)

#creates a guild table which contains guild_id, channel_id, mod_id
@bot.command
@lightbulb.option('channel', "Enter channel ID to send birthday messages to", type=str)
@lightbulb.option('mod', "Enter mod role ID to restric certain commands to mods", type=str)
@lightbulb.command('setup', "set channel and mod")
@lightbulb.implements(lightbulb.SlashCommand)
async def setup(ctx):
    input_guild = ctx.guild_id
    input_channel = ctx.options.channel
    input_mod = ctx.options.mod
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
        
        if await setupCheck(ctx, input_channel, input_mod):     
            statement2 = """INSERT INTO Guilds (guildId, channelId, modId)
                            VALUES (:guild_id, :channel_id, :mod_id);"""
            para2 = ({"guild_id":input_guild, "channel_id":int(input_channel), "mod_id":int(input_mod)})
            conn.execute(sa.text(statement2), para2)
            print('pass setup')
        conn.commit()
        conn.close()

#Create a check function that checks if channel is valid, if mod is valid, and if guild isn't already setup
async def setupCheck(ctx, channel, mod):
    guildID = ctx.guild_id

    try:
        int(channel)
    except ValueError as e:
        print("channel must be a number")
        return False
    
    try:
        int(mod)
    except ValueError as e:
        print("mod id must be a number")
        return False
        
    #makes sure the channel is in the guild
    channels_in_guild = bot.cache.get_guild_channels_view_for_guild(guildID).keys()
    if not int(channel) in channels_in_guild:
        #error message
        print('error channel')
        return False

    #makes sure the mod id is in the guild
    roles_in_guild = bot.cache.get_roles_view_for_guild(guildID).keys()
    if not mod == None and not int(mod) in roles_in_guild:
        #error message
        print('error mod')
        return False

    engine = sa.create_engine(os.environ["DATABASE_URL"])


    #using sql query for guild to see if guild is already set up
    with engine.connect() as conn:
        statement1 = f"""SELECT guildId
                         FROM Guilds
                         WHERE guildId = {guildID};
                         """
        result = conn.execute(sa.text(statement1))
        conn.commit()
        conn.close()
        
        if result.first() != None:
            #error message
            print('error duplicate')
            return False

    #setup finishing touches (embed, message, respond, etc.....)
    return True



#turns given inputs into string '2000-dd-mm'""
#2000 is used as default year, needed cause sql DATE formate requires year
async def dateFormat(day, month):

    if day < 10:
        dayString = "0" + str(day)
    else:
        dayString = f"{day}"
    
    if month < 10:
        monthString = "0" + str(month)
    else:
        monthString = f"{month}"
    
    return f'2000-{monthString}-{dayString}'

#creates users table, dates table and inputs necessary info
@bot.command
@lightbulb.option("day", "Birth Day", type=int, min_value=1, max_value=31)
@lightbulb.option("month", "Birth Month", type=int, min_value=1, max_value=12)
@lightbulb.command("newdate", "Add Birthdate")
@lightbulb.implements(lightbulb.SlashCommand)
async def newdate(ctx):
    guildID = ctx.guild_id
    userID = ctx.author.id
    date = await dateFormat(ctx.options.day, ctx.options.month)
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    if await generalCheck(guildID) and not await checkUser(userID):
        with engine.connect() as conn:
            statement1 = (
                """
                CREATE TABLE IF NOT EXISTS Users(
                    userID INT PRIMARY KEY NOT NULL,
                    dates DATE NOT NULL,
                    guildID INT[] NOT NULL DEFAULT array[]::INT[], 
                    INDEX (userID)
                );   
                """
            )
            conn.execute(sa.text(statement1))
            conn.commit()

            statement2 = (
                f"""
                INSERT INTO Users(userID, dates)
                VALUES ({userID}, '{date}')
                ON CONFLICT (userID)
                DO NOTHING
                """
                )
            conn.execute(sa.text(statement2))
            conn.commit()

            statement2_1 = (
                f"""
                SELECT guildID
                FROM Users
                WHERE userID = {userID}
                """
            )

            results0 = conn.execute(sa.text(statement2_1))
            conn.commit()

            arr0 = results0.first()[0]
            if (guildID not in arr0):
                arr0.append(str(guildID))

                statement2_2 = (
                    f"""
                    UPDATE Users
                    SET guildID = ARRAY {arr0}
                    WHERE userID = {userID}
                    """
                )

                conn.execute(sa.text(statement2_2))
                conn.commit()

            statement3 = (
                f"""
                SELECT userID
                FROM Guilds
                WHERE guildID = {guildID}
                """
            )
            results = conn.execute(sa.text(statement3))
            conn.commit()
            
            arr = results.first()[0]
            if (userID not in arr):
                arr.append(str(userID))

                statement4 = (
                    f"""
                    UPDATE Guilds
                    SET userID = ARRAY {arr}
                    WHERE guildID = {guildID}
                    """
                )
                conn.execute(sa.text(statement4))
                conn.commit()

            statement5 = (
                """
                CREATE TABLE IF NOT EXISTS Dates(
                    dates DATE PRIMARY KEY NOT NULL,
                    users INT[] NOT NULL DEFAULT array[]::INT[],
                    INDEX (dates)
                );
                """
            )
            conn.execute(sa.text(statement5))
            conn.commit()

            statement6 = (
            f"""
                INSERT INTO Dates(dates)
                VALUES('{date}')
                ON CONFLICT (dates)
                DO NOTHING;
                """
            )
            conn.execute(sa.text(statement6))
            conn.commit()

            statement7 = (
                f"""
                SELECT users
                FROM Dates
                WHERE dates = '{date}'
                """
            )

            results = conn.execute(sa.text(statement7))
            arr2 = results.first()[0]
            if (userID not in arr2):
                arr2.append(str(userID))

                statement8 = (
                    f"""
                    UPDATE Dates
                    SET users = ARRAY {arr2}
                    WHERE dates = '{date}'
                    """
                )
                conn.execute(sa.text(statement8))
                conn.commit()
            print('pass newdate')
            conn.close()

#checks if guild is regesterd
async def generalCheck(guildID):
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    with engine.connect() as conn:
        statement1 = (
            f"""
            SELECT guildID
            FROM Guilds
            WHERE guildID = {guildID}
            """
        )
        results = conn.execute(sa.text(statement1))
        conn.commit()
        conn.close()

        if results.first() == None:
            print('fail generalCheck')
            return False
        else:
            return True

#removes the user from all table
@bot.command
@lightbulb.command('allremove', 'remove your birthdate from all servers')
@lightbulb.implements(lightbulb.SlashCommand)
async def allremove(ctx):
    guildID = ctx.guild_id
    userID = ctx.author.id
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    if await generalCheck(guildID):
        with engine.connect() as conn:
            statement1 = (
                f"""
                SELECT guildID, dates
                FROM Users
                WHERE userID = {userID}
                """
            )
            results = conn.execute(sa.text(statement1))
            conn.commit()
            first = results.first()
            guildarr = first[0]
            date = first[1]

            for guild in guildarr:
                statement2 = (
                    f"""
                    SELECT userId
                    FROM Guilds
                    WHERE guildId = {guild}
                    """
                )
                userArr = conn.execute(sa.text(statement2))
                conn.commit()
                userArr = userArr.first()[0]
                userArr.remove(userID)

                statement2_1 = (
                    f"""
                    UPDATE Guilds
                    SET userId = ARRAY {userArr}
                    WHERE guildId = {guild}
                    """
                )
                conn.execute(sa.text(statement2_1))
                conn.commit()
            
            statement3 = (
                f"""
                SELECT users
                FROM Dates
                WHERE dates = '{date}'
                """
            )
            userArr = conn.execute(sa.text(statement3))
            conn.commit()

            userArr = userArr.first()[0]
            userArr.remove(userID)

            statement3_1 = (
                f"""
                UPDATE Dates
                SET users = ARRAY {userArr}
                WHERE dates = '{date}'
                """
            )

            conn.execute(sa.text(statement3_1))
            conn.commit()

            statement4 = (
                f"""
                DELETE FROM Users
                WHERE userId = {userID}
                """
            )
            conn.execute(sa.text(statement4))
            conn.commit()
            conn.close()
            print('pass allremove')

@bot.command
@lightbulb.command('sremove', 'remove your birthdate from this server')
@lightbulb.implements(lightbulb.SlashCommand)
async def sremove(ctx):
    guildID = ctx.guild_id
    userID = ctx.author.id
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    if await generalCheck(guildID) and await checkUser(userID):
        with engine.connect() as conn:
            statement1 = (
                f"""
                SELECT guildID, dates
                FROM Users
                WHERE userID = {userID}
                """
            )
            results = conn.execute(sa.text(statement1))
            conn.commit()
            first = results.first()
            guildarr = first[0]
            date = first[1]

            
            statement2 = (
                f"""
                SELECT userId
                FROM Guilds
                WHERE guildId = {guildID}
                """
            )
            userArr = conn.execute(sa.text(statement2))
            conn.commit()
            userArr = userArr.first()[0]
            userArr.remove(userID)

            statement2_1 = (
                f"""
                UPDATE Guilds
                SET userId = ARRAY {userArr}
                WHERE guildId = {guildID}
                """
            )
            conn.execute(sa.text(statement2_1))
            conn.commit()
            
            if len(guildarr) == 1:
                statement3 = (
                    f"""
                    SELECT users
                    FROM Dates
                    WHERE dates = '{date}'
                    """
                )
                userArr = conn.execute(sa.text(statement3))
                conn.commit()

                userArr = userArr.first()[0]
                userArr.remove(userID)

                statement3_1 = (
                    f"""
                    UPDATE Dates
                    SET users = ARRAY {userArr}
                    WHERE dates = '{date}'
                    """
                )

                conn.execute(sa.text(statement3_1))
                conn.commit()

                statement4 = (
                    f"""
                    DELETE FROM Users
                    WHERE userId = {userID}
                    """
                )
                conn.execute(sa.text(statement4))
                conn.commit()
            else:
                statement5 = (
                    f"""
                    SELECT guildID
                    FROM Users
                    WHERE userId = {userID}
                    """
                )
                arr1 = conn.execute(sa.text(statement5))
                conn.commit()
                arr1 = arr1.first()[0]
                arr1.remove(guildID)

                statement5_1 = (
                    f"""
                    UPDATE Users
                    SET guildID = ARRAY {arr1}
                    WHERE userID = {userID}
                    """
                )

                conn.execute(sa.text(statement5_1))
                conn.commit()
            conn.close()
            print('pass sremove')

@bot.command
@lightbulb.option('userid', "user's ID to remove")
@lightbulb.command('mremove', "specifically remove a user's birthdate from server")
@lightbulb.implements(lightbulb.SlashCommand)
async def mremove(ctx):
    guildID = ctx.guild_id
    removeID = int(ctx.options.userid)
    roleArr = ctx.member.role_ids
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    if await ModCheck(guildID, roleArr) and await generalCheck(guildID) and await checkUser(removeID):
            with engine.connect() as conn:
                statement1 = (
                    f"""
                    SELECT guildID, dates
                    FROM Users
                    WHERE userID = {removeID}
                    """
                )
                results = conn.execute(sa.text(statement1))
                conn.commit()
                first = results.first()
                guildarr = first[0]
                date = first[1]

                
                statement2 = (
                    f"""
                    SELECT userId
                    FROM Guilds
                    WHERE guildId = {guildID}
                    """
                )
                userArr = conn.execute(sa.text(statement2))
                conn.commit()
                userArr = userArr.first()[0]
                userArr.remove(removeID)

                statement2_1 = (
                    f"""
                    UPDATE Guilds
                    SET userId = ARRAY {userArr}
                    WHERE guildId = {guildID}
                    """
                )
                conn.execute(sa.text(statement2_1))
                conn.commit()
                
                if len(guildarr) == 1:
                    statement3 = (
                        f"""
                        SELECT users
                        FROM Dates
                        WHERE dates = '{date}'
                        """
                    )
                    userArr = conn.execute(sa.text(statement3))
                    conn.commit()

                    userArr = userArr.first()[0]
                    userArr.remove(removeID)

                    statement3_1 = (
                        f"""
                        UPDATE Dates
                        SET users = ARRAY {userArr}
                        WHERE dates = '{date}'
                        """
                    )

                    conn.execute(sa.text(statement3_1))
                    conn.commit()

                    statement4 = (
                        f"""
                        DELETE FROM Users
                        WHERE userId = {removeID}
                        """
                    )
                    conn.execute(sa.text(statement4))
                    conn.commit()
                else:
                    statement5 = (
                        f"""
                        SELECT guildID
                        FROM Users
                        WHERE userId = {removeID}
                        """
                    )
                    arr1 = conn.execute(sa.text(statement5))
                    conn.commit()
                    arr1 = arr1.first()[0]
                    arr1.remove(guildID)

                    statement5_1 = (
                        f"""
                        UPDATE Users
                        SET guildID = ARRAY {arr1}
                        WHERE userID = {removeID}
                        """
                    )

                    conn.execute(sa.text(statement5_1))
                    conn.commit()
            conn.close()
            print('pass mremove')




async def ModCheck(guildID, modID):
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    with engine.connect() as conn:
        statement1 = (
            f"""
            SELECT modId
            FROM Guilds
            WHERE guildId = {guildID}
            """
        )  
        results = conn.execute(sa.text(statement1))
        conn.commit()

        guildmod = results.first()[0]

        if guildmod in modID:
            return True
        
        print('fail modCheck')
        return False
    

@bot.command
@lightbulb.command('listall', 'list all saved birthdates for server')
@lightbulb.implements(lightbulb.SlashCommand)
async def listall(ctx):
    guildID = ctx.guild_id
    engine = sa.create_engine(os.environ["DATABASE_URL"])
    bdays = ""

    with engine.connect as conn:
        statement1 = (
            f"""
            SELECT userId
            FROM Guilds
            WHERE guildId = {guildID}
            """
        )
        results = conn.execute(sa.text(statement1))
        userArr = results.first()[0]

        for user in userArr:
            statement2 = (
                f"""
                SELECT dates
                FROM Users
                WHERE userID = {user}
                """
            )
            result = conn.execute(sa.text(statement2))
            date = results.first()[0]
            bdays += f"{date} \n"

async def checkUser(userID):
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    with engine.connect() as conn:
        statement1 = (
            f"""
            SELECT userId
            FROM Users
            WHERE userId = {userID}
            """
        )
        results = conn.execute(sa.text(statement1))
        if results.first() == None:
            print("fail checkUser")
            return False

        return True

async def checkGuildUser(userID, GuildID):
    engine = sa.create_engine(os.environ["DATABASE_URL"])

    with engine.connect() as conn:
        statement1 = (
            f"""
            SELECT userId 
            FROM Guilds
            WHERE guildId = {GuildID}
            """
        )

        results = conn.execute(sa.text(statement1))
        userArr = results.first()[0]

        if userID in userArr:
            return True

        print("fail checkGuildUser")
        return False

@bot.command
@lightbulb.command('addtoserver', 'saves your birthdate in this server')
@lightbulb.implements(lightbulb.SlashCommand)
async def addtoserver(ctx):
    userID = ctx.author.id
    guildID = ctx.guild_id

    if not checkGuildUser(userID, guildID):
        pass


#test listall
#finish addtoserver
#next task: prevent duplicates
bot.run()