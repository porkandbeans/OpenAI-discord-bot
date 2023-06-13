import os
import discord
from discord.utils import get
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

client = discord.Client(intents=discord.Intents.all())

reactionmessage = 1111937249819500626

# role IDs
artist = 1050370202266775602
tech = 1050370239679963157
furry = 1050370319459823666
gamer = 1050369720165072957

roleid = None
guildid = 374863653595381760

@client.event
async def on_reaction_add(reaction, user):
    print("reaction added")
    
    # ensure these
    if reaction.message.channel.id != 1050368481209630750:
        print("wrong channel")
        return
    if reaction.message.id != reactionmessage:
        print("wrong message")
        return
    if reaction.message.guild.id != guildid:
        print("wrong server")
        return
    
    guild = client.fetch_guild(guildid)
    
    # figure out which role we're going to give the user
    if reaction.emoji == "🎨":
        roleid = artist

    if reaction.emoji == "🦊":
        roleid = furry
    
    if reaction.emoji == "🎮":
        roleid = gamer
    
    if reaction.emoji == "⌨️":
        roleid = tech

    if roleid == None:
        # Remove the reaction if it is not one of the specified ones
        print("removing reaction")
        await reaction.message.remove_reaction(reaction.emoji, user)
        return
    
    #finally, give the user the role
    role = get(guild.roles, id=roleid)
    await user.add_roles(role)
    print("gave role: " + str(roleid))
    print("to user: " + user.name)

client.run(TOKEN)