import json
import os
import requests
import random
import asyncio
from datetime import datetime, timedelta
from typing import Union
from dotenv import load_dotenv

import discord
import discord.ext
from discord import Interaction

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

BOT_TOKEN = os.getenv("BOT_TOKEN")

INVOKE_NAME = "piirka"


def cleanup_prompt(prompt: str) -> str:
    variations = [INVOKE_NAME.upper(), INVOKE_NAME.capitalize(), INVOKE_NAME]
    for v in variations:
        prompt = prompt.replace(v, "")
    prompt = prompt.lstrip(",").lstrip(".").lstrip()
    return prompt


def random_chance(message: discord.Message) -> bool:
    if len(message.content) < 10:
        return False
    return random.random() < (1.0 / 100.0)


REPLACE = {
    "*grumbles*": ":unamused:",
    "*grumble*": ":unamused:",
    "*grumble grumble*": ":unamused:",
    "*sigh*": ":face_exhaling:",
    "*frustrated face*": ":triumph:",
    "*curses*": ":face_with_symbols_over_mouth:",
    "*Curses*": ":face_with_symbols_over_mouth:",
    "*curse*": ":face_with_symbols_over_mouth:",
    "*swear*": ":face_with_symbols_over_mouth:",
    "*rolls eyes*": ":rolling_eyes:",
    "*giggles*": ":sweat_smile:"
}


def discord_format(text: str) -> str:
    for i, o in REPLACE.items():
        text = text.replace(i, o)
    return text


async def prompt_ai(prompt: str) -> str:
    body = {
        "model": "jysses2",
        "prompt": prompt,
        "stream": False
    }
    headers = {"Content-type": "application/json"}
    result = requests.post("http://127.0.0.1:11434/api/generate", data=json.dumps(body), headers=headers)
    data = json.loads(result.content)
    if "response" in data:
        return discord_format(data["response"])
    return "Ingen svar..."


client = discord.Bot(intents=intents)

async def get_nickname(ctx, user_id) -> str:
    user = ctx.guild.get_member(user_id)
    if not user:
        user = await ctx.guild.fetch_member(user_id)
    return user.display_name if user else "UKJENT"


@client.slash_command(name="prompt", description="Få ett svar") #, guild_ids=SERVER_IDS)
async def post_log(ctx: discord.ApplicationContext, prompt: discord.Option(str, required=True, description="Prompt")):
    await ctx.channel.trigger_typing()
    await ctx.defer()
    svar = await prompt_ai(prompt)
    await ctx.followup.send(f"**{prompt}**:\n\n" + svar)
    # await ctx.respond(svar)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    if message.content.lower().startswith(INVOKE_NAME) or random_chance(message):
        prompt = cleanup_prompt(message.content)
        async with message.channel.typing():
            # await message.channel.trigger_typing()
            svar = await prompt_ai(prompt)
        await message.channel.send(svar.lstrip("\"").rstrip("\""), reference=message)

#
# async def main():
#     await ap.auth_user()


if __name__ == "__main__":
    # asyncio.run(main())
    client.run(BOT_TOKEN)

