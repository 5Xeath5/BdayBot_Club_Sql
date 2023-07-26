import os
import sqlalchemy as sa
import hikari
import lightbulb




bot = lightbulb.BotApp(token="BOT_TOKEN", intents=hikari.Intents.ALL)

# engine = create_engine(os.environ["DATABASE_URL"])
# conn = engine.connect()

# res = conn.execute(text("SELECT now()")).fetchall()
# print(res)



@bot.command
@lightbulb.option('channel', "Enter channel ID to send birthday messages to", type=int)
@lightbulb.option('mod', "Enter mod role ID to restric certain commands to mods", required=False, type=int)
@lightbulb.implements(lightbulb.SlashCommand)
async def setup(ctx):
    engine = sa.create_engine(os.environ["DATABASE_URL"])
    with engine.connect() as conn:
        statement1 = """CREATE TABLE IF NOT EXISTS Guilds (
	                        guild_id INT PRIMARY KEY NOT NULL,
                            channel_id INT NOT NULL,
                            mod_id INT NULL,
	                        INDEX (guild_id)
                        );"""
        conn.execute(sa.text(statement1))

        statement2 = """INSERT INTO Guilds(guild_id, channel_id, mod_id)
                        VALUES(g_id, c_id, m_id);"""
        para2 = ({"g_id":ctx.guild_id, "c_id":ctx.options.channel, "m_id":ctx.options.mod})
        conn.execute(sa.text(statement2), para2)

        conn.commit()
        conn.close()

#Create a check function that checks if channel is valid, if mod is valid, and if guild isn't already setup
async def setupCheck(ctx, channel, mod):
    guildID = ctx.guild_id

    channels_in_guild = bot.cache.get_guild_channels_view_for_guild(guildID).keys()
    if not int(channel) in channels_in_guild:
        #error message
        pass

    roles_in_guild = bot.cache.get_roles_view_for_guild(guildID).keys()
    if not mod == None or not int(mod) in roles_in_guild:
        #error message
        pass

    #using sql query for guild to see if guild is already set up