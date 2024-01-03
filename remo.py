import os
import io
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

import responses
from app import db
from services.logging import logger

def send_as_file(ctx, message):
        with io.StringIO(message) as file:
            file = discord.File(file, filename=f"{ctx.message.author}_review.txt")
            return file


async def lock_thread(thread):
    # Lock the thread
    await thread.edit(locked=True)


async def send_review(ctx, client, user_message, user_files):
    thread = await ctx.message.create_thread(name=f"{ctx.author} Review")
    try:
        if user_files:
            await thread.send("Running review on Resume, please wait...")
            response = await responses.handle_review(user_message, user_files)
            if isinstance(response, str) and response.startswith("Sorry"): 
                await thread.send(response)   
            else:
                response_file = send_as_file(ctx, response)  
                await thread.send(file=response_file)
            
        else:
            response = "You didn't provide a file. Please attach a PNG file(s) of your resume to get a review."
            # send response to channel
            await thread.send(response)

        # set duration for thread to 15 minutes
        thread_timeout = 900

        # keep thread alive and responsive
        while True:
            try:
                response = await client.wait_for("message", check=lambda m: m.author == ctx.author and m.channel == thread, timeout=thread_timeout)
                # process user's responses within' thread
                if response.content == "!review":
                    send_review(ctx, client, response.content, response.attachments)
                else:
                    return
            except asyncio.TimeoutError:
                await thread.send("I'm closing this thread due to inactivity. If you want another review, please start a new thread.")
                lock_thread(thread)
                break

    except Exception as e:
        print(f"\nERROR sending message: {e}")

def run_remo_bot():
    load_dotenv()
    TOKEN = os.getenv('DISCORD_REMO_BOT_TOKEN')

    # define intent
    intents = discord.Intents.default()
    intents.message_content = True

    client = commands.Bot(command_prefix='!', intents=intents)
    

    # override default help command
    client.remove_command('help')
    @client.command()
    async def help(ctx):
        embed = discord.Embed(title="Bot Commans", description="All available commands: ", color=0xeee657)
        embed.add_field(name="!set_channel #channel-name", value="Sets the bot to operate in a specified channel.\nAdmin must set a channel before bot can be used", inline=False)
        embed.add_field(name="!review <png_file_attachment(s)>", value="Executes resume review", inline=False)

        await ctx.send(embed=embed)

    # When the bot has started
    @client.event
    async def on_ready():
        logger.info(f'{client.user} is now running!')

    @client.command()
    async def set_channel(ctx, channel: discord.TextChannel):
        if not ctx.author.guild_permissions.manage_channels:
            return await ctx.send("You don't have permission to set me to a specific channel.")
        
        server_id = ctx.guild.id
        channel_id = channel.id

        # check if server already given channel set already
        db.execute("SELECT * FROM bot_channels WHERE server_id = %s", (server_id,))
        existing_record = db.fetchone()

        # update or save chosen channel to database
        if existing_record:
            # update the existing record with new channel id
            db.execute("UPDATE bot_channels SET channel_id = %s WHERE server_id = %s", (channel_id, server_id))
            await ctx.send(f"Bot channel updated to {channel.name}")
        else:
            # save new record and add server and channel
            db.execute("INSERT INTO bot_channels (server_id, channel_id) VALUES (%s, %s);", (server_id, channel_id))
            await ctx.send(f"Bot channel set to {channel.name}")



    @client.command()
    async def review(ctx):
        server_id = ctx.guild.id;
        # Check if the channel is set for this server
        db.execute("SELECT channel_id FROM bot_channels WHERE server_id = %s;", (server_id))
        channel_set = db.fetchone()

        if channel_set:
            # channel set, reviews can proceed
            user_message = ctx.message.content
            user_files = None

            # Check for attachments in the message
            if ctx.message.attachments:
                user_files = ctx.message.attachments
                # Optionally save the file or process it as needed
                # await user_file.save(user_file.filename)

            # Debug print statements
            # print(f"\n{ctx.author} said: '{user_message}' in {ctx.channel}")
            # print(f" and attached '{user_files}'")

            # Process the reviews
            await send_review(ctx, client, user_message, user_files)
        else:
            return

        
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        # Process commands first
        await client.process_commands(message)

 

    client.run(TOKEN)

