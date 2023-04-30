import discord
import time
from redbot.core import commands
from redbot.core import Config
import asyncio


class tv2(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config = Config.get_conf(self, identifier=1234567890)

        default_guild = {
            "keywords": {}
        }

        self.config.register_guild(**default_guild)

    @commands.group(name="tv2", aliases=["trigger2"])
    @commands.guild_only()
    async def _tv2(self, ctx):
        """Custom message replies to users who trigger a keyword"""
        pass

    @_tv2.command(name="add")
    async def add_keyword(self, ctx, keyword: str, delay: int, *, message: str):
        """Add a keyword, delay (in seconds), and the message to be sent"""
        if delay < 1:
            await ctx.send("Delay must be at least 1 second.")
            return
        keywords = await self.config.guild(ctx.guild).keywords()
        keywords[keyword.lower()] = {"message": message, "last_triggered": 0, "delay": delay}
        await self.config.guild(ctx.guild).keywords.set(keywords)
        await ctx.send(f"{keyword.lower()} has been added to the keyword list with a delay of {delay} seconds.")

    @_tv2.command(name="edit")
    async def edit_keyword(self, ctx, keyword: str, *, message: str):
        """Edit a keyword and its message"""
        keywords = await self.config.guild(ctx.guild).keywords()
        if keyword.lower() in keywords:
            keywords[keyword.lower()]["message"] = message
            await self.config.guild(ctx.guild).keywords.set(keywords)
            await ctx.send(f"{keyword.lower()} has been edited.")
        else:
            await ctx.send(f"{keyword.lower()} is not in the keyword list.")

    @_tv2.command(name="remove")
    async def remove_keyword(self, ctx, keyword: str):
        """Remove a keyword"""
        keywords = await self.config.guild(ctx.guild).keywords()
        if keyword.lower() in keywords:
            keywords.pop(keyword.lower())
            await self.config.guild(ctx.guild).keywords.set(keywords)
            await ctx.send(f"{keyword.lower()} has been removed from the keyword list.")
        else:
            await ctx.send(f"{keyword.lower()} is not in the keyword list.")

    @_tv2.command(name="list")
    async def list_keywords(self, ctx):
        """List all keywords"""
        keywords = await self.config.guild(ctx.guild).keywords()
        if not keywords:
            await ctx.send("No keywords have been added.")
            return
        msg = "List of keywords:\n"
        for k, v in keywords.items():
            msg += f"\n{k} - {v['message']} (delay: {v['delay']} seconds)"
        await ctx.send(msg)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        keywords = await self.config.guild(message.guild).keywords()
        if not keywords:
            return

        for keyword in keywords:
            if keyword.lower() in message.content.lower():
                last_triggered = keywords[keyword]["last_triggered"]
                current_time = time.time()
                delay = keywords[keyword]["delay"]
                if current_time - last_triggered > delay:
                    reply = keywords[keyword]["message"].format(user=message.author.mention)
                    await message.channel.send(f"{message.author.mention} {reply}")
                    keywords[keyword]["last_triggered"] = current_time
                    await self.config.guild(message.guild).keywords.set(keywords)
                    break

    async def red_delete_data_for_user(self, **kwargs):
        """Nothing to delete."""
        return

    async def red_get_data_for_user(self, **kwargs):
        """Nothing to get."""
        return {}
