This is a discord bot that utilises OpenAI's API to respond to messages with an AI generated response.

It requires the following PIP packages:
- discord
- openai
- python-dotenv

You will need an API key from OpenAI and a bot token from Discord. You must source these yourself.
- discord tokens: https://discord.com/developers/applications
- OpenAI key: https://platform.openai.com/account/api-keys

put these keys in your `.env` file in the root of your project like so:
```
DISCORD_TOKEN=[token goes here]
OPENAI_API_KEY=[key goes here]
DEVELOPER_ID=[your discord user ID goes here]
```
