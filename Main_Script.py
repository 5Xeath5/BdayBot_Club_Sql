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
@lightbulb.option('channel', "Enter channel ID to send birthday messages to")
@lightbulb.option('mod', "Enter mod role ID to restric certain commands to mods", required=False)
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
                        VALUES(g_id, c_id, m_id)"""
        para2 = ({"g_id":ctx.guild_id, "c_id":ctx.options.channel, "m_id":ctx.options.mod})
        conn.execute(sa.text(statement2), para2)

        conn.commit()
#Create a check function that checks if channel is valid, if mod is valid, and if guild isn't already setup