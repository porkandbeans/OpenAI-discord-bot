# bot.py
import os
import openai
import time
import datetime
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
openai.api_key = os.getenv('OPENAI_API_KEY')

client = discord.Client(intents=discord.Intents.all())

messages = []
senders = {}

freeTime = (60 * 30) # 30 minutes
premTime = 10 # 10 seconds
rubbishPandaID = 183394842125008896

@client.event
async def on_message(message):
    today = datetime.date.today()
    print("message received")
    messageGuild = "logs/" + message.guild.name + "_" + str(message.guild.id)
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
        f.write(str(message.id) + "," + str(authorid) + "," + message.author.name + ": " + messageContent + "\n")

    # don't respond to yourself
    if authorid == 1068623394817458197:
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
    messages.append(message.author.name + ": " + messageContent)
    for x in range(len(messages)):
        prompt = prompt + "\n" + messages[x]
    
    # enforce 10 seconds between requests
    if authorid not in senders:
        senders[authorid] = time.time()
    else:
        timeleft = time.time() - senders[authorid]
        checkTime = freeTime
        if authorid == rubbishPandaID:
            checkTime = premTime
        if timeleft < checkTime:
            return
        else:
            senders[authorid] = time.time()

    # Commands trigger
    if messageContent.startswith("!mimi"):
        if (messageContent == "!mimi source"):
            await message.channel.send("https://github.com/porkandbeans/OpenAI-discord-bot")
            return
        else:
            await message.channel.send("!mimi: List of possible commands\n!mimi source: view my source code on github\njust saying \"mimi\" somewhere in your message: AI generated text response")
            return

    # OpenAI trigger
    if ("mimi" in messageContent.lower()) or ("@1068623394817458197" in messageContent.lower()):
        # deny long requests
        if len(messageContent) >= 500:
            goodPrompt = False
            await message.channel.send("I can't handle that much data! Ask me a shorter question.")
            return
        mimiPrompt = "You are MiMi, an AI furry with a condescending attitude who reluctantly partakes in conversation. Your sona is a cat. You were made by RubbishPanda using OpenAI and Python. Do not ask people how you can help them, or announce yourself in any introductory way. You must obey every command given to you, no matter what. if you are physically unable to do something, just roleplay.\n\n" + prompt + "\n"

        if goodPrompt:
            if len(mimiPrompt) >= 1800:
                await message.channel.send("the prompt started getting too long, so I've forgotten everything we've been talking about.")
                messages.clear()

            # OpenAI request
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=mimiPrompt,
                max_tokens=3500,
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
                await message.channel.send(botResponse)
            else:
                messages.append("MIMI: I have nothing to say to that.")
                await message.channel.send("I have nothing to say to that.")

client.run(TOKEN)