import os
import io
import discord
from discord.ext import commands
from dotenv import load_dotenv

import responses

def send_as_file(ctx, message):
        with io.StringIO(message) as file:
            file = discord.File(file, filename=f"{ctx.message.author}_review.txt")
            return file
            
async def send_review(ctx, user_message, user_files):
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


    def channel_is_set(guild_id, channel_id) -> bool:
        return True

    # When the bot has started
    @client.event
    async def on_ready():
        print(f'{client.user} is now running!')

    @client.command()
    async def set_channel(ctx, channel: discord.TextChannel):
        if not ctx.author.guild_permissions.manage_channels:
            return await ctx.send("You don't have permission to set me to a specific channel.")
        
        # save chosen channel to database
        #TODO: set a save to db function
        await ctx.send(f"Bot channel set to {channel.name}")

    @client.command()
    async def review(ctx):
        # Check if the channel is set for this server
        if not channel_is_set(ctx.guild.id, ctx.channel.id):
            return

        user_message = ctx.message.content
        user_files = None

        # Check for attachments in the message
        if ctx.message.attachments:
            user_files = ctx.message.attachments
            # Optionally save the file or process it as needed
            # await user_file.save(user_file.filename)

        # Debug print statements
        print(f"\n{ctx.author} said: '{user_message}' in {ctx.channel}")
        print(f" and attached '{user_files}'")

        # Process the review here
        await send_review(ctx, user_message, user_files)

        
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        # Process commands first
        await client.process_commands(message)

 

    client.run(TOKEN)

