import os
import io
import discord
from discord.ext import commands
from dotenv import load_dotenv
from repo import pdf_image
from services.awsconn import s3

import responses
from services.commons import split_response
from services.database import get_rds_instance
from services.logging import logger

load_dotenv

bucketname = os.getenv('BUCKET_NAME')

def send_as_file(ctx, message):
        with io.StringIO(message) as file:
            file = discord.File(file, filename=f"{ctx.message.author}_review.txt")
            return file

async def lock_thread(thread):
    # Lock the thread
    await thread.edit(locked=True)

async def send_review(ctx, user_message, user_files):
    try:
        # check if user provided attachment
        if user_files:
            print(user_files)
            # check attachments are .png
            png_files = [f for f in user_files if f.filename.lower().endswith('.png')]
            pdf_files = [f for f in user_files if f.filename.lower().endswith('.pdf')]
            if png_files:
                thread = await ctx.message.create_thread(name=f"{ctx.author} Review")

                await thread.send("Running review on Resume, please wait...")
                print(f"\npng files: {user_files}")
                response = await responses.handle_review(user_message, user_files)
                response_pieces = split_response(response)

                for part in response_pieces:
                    await thread.send(part)
            elif pdf_files:
                images = pdf_image.pdf_to_images(pdf_files[0])[0]
                print(f"\nimages: {images}")
                thread = await ctx.message.create_thread(name=f"{ctx.author} Review")

                await thread.send("Running review on Resume, please wait...")

                response = await responses.handle_review_pdf(user_message, images)
                response_pieces = split_response(response)

                try:
                    for part in response_pieces:
                        await thread.send(part)
                except Exception as e:
                    print(f"An error occurred: {e}")
                finally:
                    for image in range(len(images)):
                        s3.delete_object(Bucket=bucketname, Key=images[image])

            else:
                await ctx.send("Sorry, I only accept PNG and PDF files. Please try again.")
            
        else:
            await ctx.send("You didn't provide a file. Please attach a PNG or PDF file(s) of your resume to get a review.")

    except Exception as e:
        logger.info(f"\nERROR sending message: {e}")

def channel_set(ctx):
     _, db = get_rds_instance()

     server_id = ctx.guild.id;
     # Check if the channel is set for this server
     db.execute("SELECT channel_id FROM bot_channels WHERE server_id = %s;", (server_id,))
     
     channel_set = db.fetchone()
     channel_id = channel_set[0] if channel_set else None
     #logger.info("c id: ", channel_id)

     return channel_id


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

        embed = discord.Embed(title="REMO Bot Commands", description="All available commands: ", color=0xeee657)
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
        conn, db = get_rds_instance()

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

        conn.commit()
        db.close()
        conn.close()

    @client.command()
    async def review(ctx):
        channel_id = channel_set(ctx)

        if channel_id == ctx.channel.id:
            # channel set, reviews can proceed
            user_message = ctx.message.content
            user_files = None

            # Check for attachments in the message
            if ctx.message.attachments:
                user_files = ctx.message.attachments

            # Debug print statements
            # print(f"\n{ctx.author} said: '{user_message}' in {ctx.channel}")
            # print(f" and attached '{user_files}'")

            # Process the reviews
            await send_review(ctx, user_message, user_files)
        else:
            return

        
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        # Process commands first
        await client.process_commands(message)

 

    client.run(TOKEN)