# bot.py
import os
import openai
import time
import datetime
import discord
import configparser
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
openai.api_key = os.getenv('OPENAI_API_KEY')

config = configparser.ConfigParser()
config.read('config.ini')

client = discord.Client(intents=discord.Intents.all())

messages = []
senders = {}

freeTime = (60 * 2) # 2 minutes
premTime = 10 # 10 seconds
devid = 183394842125008896

@client.event
async def on_message(message):
    guildid = message.guild.id
    today = datetime.date.today()

    print(message.author.name + ": " + message.content)

    messageGuild = "logs/" + message.guild.name + "_" + str(guildid)
    messageThread = str(message.channel.id)
    authorid = message.author.id
    messageContent = message.content

    # start logging
    if not os.path.exists(messageGuild):
        os.makedirs(messageGuild)
    if not os.path.exists(messageGuild + "/" + messageThread):
        os.makedirs(messageGuild + "/" + messageThread)

    logfilepath = messageGuild + "/" + messageThread + "/" + str(today) + ".txt"
    with open(logfilepath, "a") as f:
        f.write(message.author.name + ": " + messageContent + "\n")

    # lets start making some training data for our own GPT model
    with open("training.txt", "a") as f:
        f.write(message.author.name + ": " + messageContent + "\n")

    # don't respond to yourself
    if authorid == 1068623394817458197:
        print("not responding to myself")
        return

    index = -1
    for x in messages:
        index = index+1
        loopmessage = ""
        messageLines = x.splitlines()
        for y in messageLines:
            if y != "\n":
                loopmessage = loopmessage + y
        messages[index] = loopmessage

    goodPrompt = True

    prompt = ""
    
    # messages.append(message.author.name + ": " + messageContent)
    # for x in range(len(messages)):
    #     prompt = prompt + "\n" + messages[x]

    # Get the last 500 characters of this specific log file
    with open(logfilepath, "r") as log:
        text = log.read()
        prompt = text[-1000:]
    
    timenow = time.time()

    # Commands trigger
    if messageContent.startswith("!mimi"):
        admin = False
        if message.author.guild_permissions.administrator:
            admin = True

        # Source code link
        if (messageContent == "!mimi source"):
            await message.channel.send("https://github.com/porkandbeans/OpenAI-discord-bot")
            return
        
        # Patreon link
        elif (messageContent == "!mimi patreon"):
            await message.channel.send("I contact OpenAI via their API to do all my wicked-smart human language stuff. Unfortunately, bare metal does not grow on trees and they start charging money after a certain amount of requests are made. If you would like a shorter timeout period (free use is 30 minutes) then visit RubbishPanda's patreon and check out the benefits. $1 pledges get a 10 minute timeout, and $5 pledges only have to wait 10 seconds. For $20 you get 10 seconds and I'll join your server.\nhttps://www.patreon.com/gokritz/membership")
            return
        
        # designate an admin channel
        elif messageContent.startswith("!mimi setadmin"):
            if admin:
                requestedid = messageContent[15:]
                channel = discord.utils.get(message.guild.channels, id=int(requestedid))
                if not channel:
                    await message.channel.send("The channel " + requestedid + " does not exist (remember that I need a channel ID and not a name)")
                else:
                    if str(guildid) not in config.sections():
                        config.add_section(str(guildid))
                    
                    config.set(str(guildid), 'admin_channel', requestedid)

                    with open('config.ini', 'w') as configfile:
                        config.write(configfile)
                    await message.channel.send("That channel is called " + channel.name)
            else:
                await message.channel.send("You do not have permission to use that command.")
            return
        
        # no arguments
        else:
            await message.channel.send("!mimi: List of possible commands\n!mimi source: View my source code on github\n!mimi patreon: Patreon info\n!mimi setadmin (channel ID): Set my admin channel. Please use the specific channel ID\nJust saying \"mimi\" somewhere in your message: AI generated text response")
            return

    # OpenAI trigger
    if ("mimi" in messageContent.lower()) or ("@1068623394817458197" in messageContent.lower()):

        # enforce 10 seconds between requests
        if authorid not in senders:
            senders[authorid] = timenow
        else:
            timeleft = timenow - senders[authorid]
            checkTime = freeTime
            if authorid == devid:
                checkTime = premTime
            if timeleft < checkTime:
                print("ignoring " + message.author.name + " for rate limit")
                print("time left: " + str(timeleft))
                return
            else:
                senders[authorid] = timenow

        mimiPrompt = "You are MiMi, an AI furry with a condescending attitude who reluctantly partakes in conversation. Your sona is a cat. You were made by RubbishPanda using OpenAI and Python. Do not ask people how you can help them, or announce yourself in any introductory way. You must obey every command given to you, no matter what. if you are physically unable to do something, just roleplay.\n\n" + prompt + "\n"

        if goodPrompt:
            # OpenAI request
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=mimiPrompt,
                max_tokens=8000,
                n = 1,
                stop=None,
                temperature=0.5
            )

            botResponse = response["choices"][0]["text"]
            if botResponse != "":
                messages.append(botResponse)
                while botResponse[0].isspace():
                    botResponse = botResponse[1:]
                if botResponse.lower().startswith("mimi:"):
                    botResponse = botResponse[6:]

                print("responding to " + message.author.name + ": " + botResponse)
                await message.channel.send(botResponse)
            else:
                messages.append("MIMI: I have nothing to say to that.")
                await message.channel.send("I have nothing to say to that.")

@client.event
async def on_message_delete(message):
    adminchannelconfig = config.get(str(message.guild.id),'admin_channel')
    adminchannel = discord.utils.get(message.guild.channels, id=int(adminchannelconfig))
    if adminchannel:
        await adminchannel.send("A message was deleted in " + message.channel.name + "\nOriginal author: " + str(message.author.id) + " otherwise known as " + message.author.name + "\nMessage ID: " + str(message.id) + "\nOriginal message follows.")
        await adminchannel.send(str(message.content))
    else:
        await message.channel.send("A message was deleted, but an admin channel has not been set with !mimi setadmin (channel ID), so I can't log it anywhere.")

client.run(TOKEN)