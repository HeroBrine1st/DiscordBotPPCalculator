import asyncio
import discord
import re
import subprocess
import concurrent.futures
import traceback
import logging

from discord.ext import commands
from discord.ext import tasks
from io import StringIO


#===============================#

CLIENT_ID = ""
CLIENT_SECRET = ""
DISCORD_BOT_TOKEN = ""
NUMBER_OF_TASKS_AT_THE_SAME_TIME = 5
NICKNAME_REGEX = re.compile(r"^[A-Za-z0-9 _]+$")
GET_COMMAND = lambda nickname: ["dotnet", "PerformanceCalculator.dll", "profile", nickname, CLIENT_ID, CLIENT_SECRET]

#===============================#


logger = logging.getLogger("Bot")
bot = commands.Bot(command_prefix='%')
sem = asyncio.Semaphore(NUMBER_OF_TASKS_AT_THE_SAME_TIME)


error_embed = discord.Embed(
    title="Error", description="Command not found. Type `%help`.", color=0xff0000)
error_embed.set_thumbnail(
    url="https://cdn.discordapp.com/emojis/877579403599687741.png")

rework_embed = discord.Embed(title="Links", color=0x000000)
rework_embed.add_field(
    name="Pull", value="https://github.com/ppy/osu/pull/14395", inline=False)
rework_embed.add_field(
    name="Branch", value="https://github.com/emu1337/osu/tree/skillsrework", inline=False)
rework_embed.set_footer(
    text="If branch is outdated in bot, please tell @Bullet#2268 about this issue.")

invite_embed=discord.Embed(description="The bot is private because non-verified bots have 100 servers limit. So if you want to add this bot to your server — just ping <@270892441509298177>.", color=0x000000)
invite_embed.add_field(
    name="Or host it yourself", value="https://github.com/HeroBrine1st/DiscordBotPPCalculator", inline=False)

pardon_embed = discord.Embed(color=0xff8700)
pardon_embed.set_image(
    url="https://media.discordapp.net/attachments/502936093260513280/878989028404375562/pardon.png")

@tasks.loop(seconds=90.0)
async def my_background_task():
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f"%help in {len(bot.guilds)} servers"))


@bot.event
async def on_ready():
    await bot.wait_until_ready()
    my_background_task.start()


@bot.command(name="pp")
async def pp(ctx, *, nickname: str):
    if not NICKNAME_REGEX.match(nickname):
        await ctx.reply(embed=discord.Embed(title="Error", description="The requested username contains invalid characters. If nickname contains space, use `_` instead (`%pp Nick_Name`). If nickname contains `-`, use `%pp UserID`.", color=0xff0000))
        return
    logger.info("Calculating %s (requested by %s)" %
                (nickname, ctx.message.author.id))
    message = await ctx.reply(embed=discord.Embed(title="In queue...", color=0x000000))
    async with sem:
        await message.edit(embed=discord.Embed(description="Script is started, waiting...", color=0x000000))
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await asyncio.get_running_loop().run_in_executor(pool, lambda: subprocess.run(GET_COMMAND(nickname), capture_output=True, timeout=180, encoding="cp866"))
    user_pos = result.stdout.find("User:")
    if not ~user_pos:
        logging.error("Dotnet exception occurred.")
        print(result.stdout)
        await message.delete()
        await ctx.reply(embed=discord.Embed(title="Error", description="Dotnet exception occurred.", color=0xff0000))
        return
    output = result.stdout[user_pos:]
    await message.delete()
    await ctx.reply(":white_check_mark:", file=discord.File(StringIO(output), filename="calculation.txt"))


@pp.error
async def handle_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.reply(embed=discord.Embed(title="Error", description="Arguments missing. Type `%pp Nick`‎. If nickname contains space, use `_` instead (`%pp Nick_Name`). If nickname contains `-`, use `%pp UserID`.", color=0xff0000))
    else:
        logger.error("Unhandled exception occurred.")
        traceback.print_exception(None, error, None)
        await ctx.reply(embed=discord.Embed(title="Error", description="Unhandled exception occurred.", color=0xff0000))


@bot.command(name="rework")
async def rework(ctx):
    await ctx.reply(embed=rework_embed)


@bot.command(name="invite")
async def invite(ctx):
    await ctx.reply(embed=invite_embed)


@bot.command(name="pardon")
async def pardon(ctx):
    await ctx.reply(embed=pardon_embed)

bot.remove_command("help")


@bot.group(invoke_without_command=True)
async def help(ctx):
    await ctx.reply(embed=discord.Embed(title="Commands", description="`pp`, `rework`, `invite`, `pardon`", color=0x000000))


@help.command()
async def pp(ctx):
    await ctx.reply(embed=discord.Embed(title="%pp", description="Type `%pp Nick` for seeing pp after «rework». If nickname contains space, use `_` instead (`%pp Nick_Name`). If nickname contains `-`, use `%pp UserID`.", color=0x000000))


@help.command()
async def rework(ctx):
    await ctx.reply(embed=discord.Embed(title="%rework", description="Type `%rework` to get links to «rework».", color=0x000000))


@help.command()
async def invite(ctx):
    await ctx.reply(embed=discord.Embed(title="%invite", description="d0 y0u r34lly n33d 70 kn0w wh47 7h15 c0mm4nd d035?", color=0x000000))


@help.command()
async def pardon(ctx):
    await ctx.reply(embed=discord.Embed(title="%pardon", description="**AH↓HA↑HA↑HA↑HA↑**", color=0x000000))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.reply(embed=error_embed)


bot.run(DISCORD_BOT_TOKEN)
