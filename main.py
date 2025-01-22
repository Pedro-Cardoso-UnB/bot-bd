import discord
from discord.ext import commands
from typing import Literal, Optional
from discord.ext.commands import Greedy, Context
import sqlite3
import random


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('$'), intents=intents)

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

bot = Bot()

# Tree syncer
@bot.command()
@commands.guild_only()
@commands.is_owner()
async def sync(
  ctx: Context, guilds: Greedy[discord.Object], spec: Optional[Literal["~", "*", "^"]] = None) -> None:
    if not guilds:
        if spec == "~":
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "*":
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == "^":
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}"
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except discord.HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

# End Boilerplate

# Begin SQL Queries

update_query = "UPDATE Usuario SET saldo = ? WHERE id_usuario = ?"

fetch_saldo_query = "SELECT saldo FROM Usuario WHERE id_usuario = ?"

insert_user_query = "INSERT INTO Usuario(id_usuario,nome,pontos,saldo) VALUES (?,?,?,?)"

# End SQL Queries

# TODO:
# Achievements
# Shop
# Item multipliers

@bot.event
async def on_message(ctx):
    if ctx.author.bot: # Makes sure the bot doesn't give itself money
        return
    author = ctx.author.id
    name = await bot.fetch_user(author)
    name = name.name
    channel = ctx.channel
    msgSize = len(ctx.content)
    sqliteConnection = sqlite3.connect('bot.db')    # DB connection
    cursor = sqliteConnection.cursor()
    cashAmount = int(msgSize/10)
    cursor.execute(fetch_saldo_query, (author,))
    data = cursor.fetchone()
    if data == None: # User does not exist, yet. Create one.
        print("User not registered!")
        cursor.execute(insert_user_query, (author, name, 0, 0))
        cursor.execute(fetch_saldo_query, (author,))
    saldoOriginal = data[0]
    new_values = (saldoOriginal + cashAmount, author)
    cursor.execute(update_query, new_values)
    sqliteConnection.commit()
    sqliteConnection.close()
    # await channel.send(str(saldoOriginal + cashAmount) + " +" + str(cashAmount))

@bot.tree.command()
async def minigame(interaction: discord.Interaction):
    ops = ['+', '-', '*']
    chosen1 = random.choice(ops)
    n1 = random.randint(1, 10)
    n2 = random.randint(1, 10)
    ans = eval(str(n1) + chosen1 + str(n2))
    await interaction.response.send_message("Responda: " + str(n1) + chosen1 + str(n2))
    msg = await bot.wait_for('message', timeout=10)
    if int(msg.content) == ans:
        author = msg.author.id
        name = await bot.fetch_user(author)
        name = name.name
        sqliteConnection = sqlite3.connect('bot.db')    # DB connection
        cursor = sqliteConnection.cursor()
        cashAmount = 10
        cursor.execute(fetch_saldo_query, (author,))
        data = cursor.fetchone()
        if data == None: # User does not exist, yet. Create one.
            print("User not registered!")
            cursor.execute(insert_user_query, (author, name, 0, 0))
            cursor.execute(fetch_saldo_query, (author,))
        saldoOriginal = data[0]
        new_values = (saldoOriginal + cashAmount, author)
        cursor.execute(update_query, new_values)
        sqliteConnection.commit()
        sqliteConnection.close()
        await interaction.followup.send("Creditados 10 CR")
    else:
        await interaction.followup.send("Buxa?")

@bot.tree.command()
async def money(interaction: discord.Interaction):
    author = interaction.user.id
    name = await bot.fetch_user(author)
    name = name.name
    sqliteConnection = sqlite3.connect('bot.db')    # DB connection
    cursor = sqliteConnection.cursor()
    cashAmount = 10
    cursor.execute(fetch_saldo_query, (author,))
    data = cursor.fetchone()
    if data == None: # User does not exist, yet. Create one.
        print("User not registered!")
        cursor.execute(insert_user_query, (author, name, 0, 0))
        cursor.execute(fetch_saldo_query, (author,))
    saldoOriginal = data[0]
    sqliteConnection.commit()
    sqliteConnection.close()
    await interaction.response.send_message("Vc tem " + str(saldoOriginal) + " créditos.")

    

f = open("secret.txt", "r")
token = f.read()
bot.run(token)
