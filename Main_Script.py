from cmath import inf
import os
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
    input_channel = int(ctx.options.channel)
    input_mod = int(ctx.options.mod)
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
        
        if await setupCheck(ctx, input_channel, input_mod):     
            statement2 = """INSERT INTO Guilds (guildId, channelId, modId)
                            VALUES (:guild_id, :channel_id, :mod_id);"""
            para2 = ({"guild_id":input_guild, "channel_id":input_channel, "mod_id":input_mod})
            conn.execute(sa.text(statement2), para2)
            print('pass')
        conn.commit()
        conn.close()

#Create a check function that checks if channel is valid, if mod is valid, and if guild isn't already setup
async def setupCheck(ctx, channel, mod):
    guildID = ctx.guild_id

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

    return True

#setup finishing touches (embed, message, respond, etc.....)

bot.run()