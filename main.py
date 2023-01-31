# bot.py
import os
import openai
import time
import discord
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
openai.api_key = os.getenv('OPENAI_API_KEY')

client = discord.Client(intents=discord.Intents.all())

messages = []
senders = {}

@client.event
async def on_message(message):
    authorid = message.author.id

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

    messageContent = message.content
    goodPrompt = True

    prompt = ""
    messages.append(message.author.name + ": " + messageContent)
    for x in range(len(messages)):
        prompt = prompt + "\n" + messages[x]
    
    # Commands trigger
    if messageContent.startswith("!mimi"):
        if (messageContent == "!mimi source"):
            await message.channel.send("")

        # prompt = ""
        # for x in range(len(messages)):
        #     prompt = prompt + "\n" + messages[x]
        # await message.channel.send(prompt)
        # return

    # OpenAI trigger
    if ("mimi" in messageContent.lower()) or ("@1068623394817458197" in messageContent.lower()):
        
        # enforce 10 seconds between requests
        if authorid not in senders:
            senders[authorid] = time.time()
        else:
            timeleft = time.time() - senders[authorid]
            if timeleft < 10:
                #await message.channel.send("Please allow 10 seconds between requests.")
                return
            else:
                senders[authorid] = time.time()

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