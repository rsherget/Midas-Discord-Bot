import asyncio
import discord
import time
import datetime
from discord import app_commands
from discord.ext import commands

def insufficent_permissions():
    '''
    Creates an embed to be sent when a user does not have permission to use a command
    '''
    embed = discord.Embed(
        title = 'Insufficient Permissions',
        description = 'You do not have permission to use this command.',
        color = discord.Color.red()
    )
    return embed

def serverInfo(interaction: discord.Interaction):
    '''
    Generates an embed with information about the server
    '''
    embed = discord.Embed(
        title = f'{interaction.guild.name}\'s Information',
        color = discord.Color.blue()
    )
    created_time = interaction.guild.created_at
    created_unix_time = int(time.mktime(created_time.timetuple()))

    try:
        embed.set_thumbnail(url=interaction.guild.icon_url)
    except:
        pass

    embed.add_field(name='Server ID', value=f'`{interaction.guild.id}`', inline=True)
    embed.add_field(name='Server Owner', value=f'`{interaction.guild.owner}`', inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=True) # Add blank field for spacing
    embed.add_field(name='Server Created', value=f'<t:{created_unix_time}>', inline=True)
    embed.add_field(name='Server Member Count', value=f'`{interaction.guild.member_count}`', inline=True)
    embed.add_field(name='\u200b', value='\u200b', inline=True) # Add blank field for spacing

    return embed

class moderationsystem(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name='kick', description='Kicks a user from the server')
    async def kick(self, interaction: discord.Interaction, user: discord.Member):
        '''
        Command: /kick
        Description: Removes a user from the server
        Usage: /kick <user>
        '''

        # Check if the user executing the command has the necessary permissions to kick users
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message(embed=insufficent_permissions())
            return

        # Check if the user specified is kickable
        if user.guild_permissions.administrator:
            await interaction.response.send_message("I cannot remove this user!")
            return

        # Kick the user
        await user.kick()

        # Send a confirmation message
        await interaction.response.send_message(f"{user.mention} has been removed from the server.")

    @app_commands.command(name='mute', description='Mutes a user')
    async def mute(self, interaction: discord.Interaction, user: discord.Member):
        '''
        Command: /mute
        Description: Mutes a user
        Usage: /mute <user>
        '''
        # Check if user has permission to use the command
        if not interaction.user.guild_permissions.mute_members:
            await interaction.response.send_message(embed=insufficent_permissions())
            return

        for channel in interaction.guild.channels:
            await channel.set_permissions(user, send_messages=False)

        await interaction.response.send_message(f'{user.mention} has been muted.')
    
    @app_commands.command(name='unmute', description='Unmutes a user in the server')
    async def unmute(self, interaction: discord.Interaction, user: discord.Member):
        '''
        Command: /unmute
        Description: Unmutes a user in the server
        Usage: /unmute <user>
        '''
        # Check if the user has the necessary permissions to unmute other users
        if not interaction.user.guild_permissions.manage_roles:
            await interaction.response.send_message(embed=insufficent_permissions())
            return

        for channel in interaction.guild.channels:
            await channel.set_permissions(user, send_messages=True)

        await interaction.response.send_message(f"Unmuted {user.mention}.")
    
    @app_commands.command(name='tempmute', description='Temporarily mute a user on the server')
    async def tempmute(self, interaction: discord.Interaction, user: discord.Member, minutes: int):
        '''
        Command: /tempmute
        Description: Temporarily mute a user on the server
        Usage: /tempmute <user> <minutes>
        '''
        
        # Calculate the duration (in seconds)
        duration_seconds = minutes * 60

        # Check if user has permission to use the command
        if not interaction.user.guild_permissions.mute_members:
            await interaction.response.send_message(embed=insufficent_permissions())
            return
        # Mute the member for the chosen duration
        for channel in interaction.guild.channels:
            await channel.set_permissions(user, send_messages=False)

        await interaction.response.send_message(f'Muted {user.name} for {minutes} minutes.')
        # Schedule to unmute user after the chosen duration ends
        await asyncio.sleep(duration_seconds)
        
        for channel in interaction.guild.channels:
            await channel.set_permissions(user, send_messages=True)
        
        # Send a message to the user indicating they have been unmuted if possible
        try: 
            await user.send(f'You have been unmuted on {interaction.guild.name} after a temporary mute of {minutes} minutes.')
        except:
            pass

    @app_commands.command(name='ban', description='Permanently ban a member for inappropriate use')
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        '''
        Command: /ban
        Description: Permanently ban a member for inappropriate use
        Usage: /ban <user> <reason>
        '''
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message(embed=insufficent_permissions())
            return
        try:
            await user.ban(reason=reason)
            await interaction.response.send_message(f'Successfully banned {user.name}.')
        except:
            await interaction.response.send_message(f'Unable to ban {user.name}.')
    
    @app_commands.command(name='tempban', description='Temporarily ban a member')
    async def tempban(self, interaction: discord.Interaction, user: discord.Member, hours: int, reason: str):
        '''
        Command: /tempban
        Description: Allow user to return to server shortly after being soft-Banned
        Usage: /tempban <user> <hours> <reason> 
        '''
        # Check if command is being called for by an administrator
        if not interaction.user.guild_permissions.ban_members:
            await interaction.response.send_message(embed=insufficent_permissions())
            return
        # Calculate the duration (in seconds)
        duration_seconds = hours * 60 * 60
        # Ban the member for the chosen duration
        try:
            await user.ban(reason=reason)
            await interaction.response.send_message(f'Successfully banned {user.name} for {hours} hours.')
        except:
            await interaction.response.send_message(f'Unable to ban {user.name}.')
        # Schedule to unban user after the chosen duration ends
        await asyncio.sleep(duration_seconds)
        await interaction.guild.unban(user)
        # Send a message to the user indicating they have been unbanned if possible
        try:
            await user.send(f'You have been unbanned on {interaction.guild.name} after a temporary ban of {hours} hours.')
        except:
            pass
    
    @app_commands.command(name='timeout', description='Puts a user in time-out')
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, minutes: int):
        '''
        Command: /timeout
        Description: selected member is put in time-out
        Usage: /timeout <user>
        '''
        # Check if the user using command has permissions to manage roles
        if not interaction.user.guild_permissions.kick_members:
            await interaction.response.send_message(embed=insufficent_permissions())
            return
        
        # Calculate the duration (in seconds)
        duration_seconds = minutes * 60

        # Convert duration to a timedelta object
        duration_timedelta = datetime.timedelta(seconds=duration_seconds)

        # put selected user in time-out
        await user.timeout(duration_timedelta)

        await interaction.response.send_message(f"{user.mention} has been put in time-out.")
        

    
    @app_commands.command(name='lock', description='Lock the current channel')
    async def lock(self, interaction: discord.Interaction):
        '''
        Command: /lock
        Description: Lock a channel in the server
        Usage: /lock
        '''
        # Check if the user has the necessary permissions to lock a channel
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(embed=insufficent_permissions())
            return
        # Get the channel to lock
        channel = interaction.channel
        await channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message(f'locked {channel.name}.')

    @app_commands.command(name='unlock', description='Unlock the current channel')
    async def unlock(self, interaction: discord.Interaction):
        '''
        Command: /unlock
        Description: Unlock a channel in the server
        Usage: /unlock
        '''
        # Check if the user has the necessary permissions to unlock a channel
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(embed=insufficent_permissions())
            return
        # Get the channel to unlock
        channel = interaction.channel
        await channel.set_permissions(interaction.guild.default_role, send_messages=True)
        await interaction.response.send_message(f'unlocked {channel.name}.')

    @app_commands.command(name='purge', description='Purge messages in a channel')
    async def purge(self, interaction: discord.Interaction, amount: int):
        '''
        Command: /purge
        Description: Purge messages in a channel
        Usage: /purge <amount>
        '''
        # Check if the user has the necessary permissions to purge messages
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(embed=insufficent_permissions())
            return

        # Fetch the channel where messages need to be purged
        channel = interaction.channel

        # Fetch the messages to be purged
        messages = []
        async for message in channel.history(limit=amount + 1):
            messages.append(message)

        # Delete the messages
        await channel.delete_messages(messages)

        # Send a message to the channel indicating the messages have been purged
        await channel.send(f'Purged {amount} messages.', delete_after=5)
        
    @app_commands.command(name='nick', description='change your nickname')
    async def nick(self, interaction: discord.Interaction, nickname: str):
        '''
        Command: /nick
        Description: Change your nickname
        Usage: /nick <nickname>
        ''' 
        try:
            # Change member's nickname
            await interaction.user.edit(nick=nickname)

            # Send response to confirm user's nickname was changed
            await interaction.response.send_message(f'Your nickname has been changed to: {nickname}', ephemeral=True)
        except:
            # Send response to confirm user's nickname was not changed
            await interaction.response.send_message('Unable to change your nickname.', ephemeral=True)

    @app_commands.command( name='serverinfo', description = 'Get server information')
    async def serverinfo(self, interaction: discord.Interaction):
        '''
        Command: /serverInfo
        Description: Get server information
        Usage: /serverInfo
        '''
            
        await interaction.response.send_message(embed=serverInfo(interaction))

async def setup(client: commands.Bot) -> None:
    await client.add_cog(moderationsystem(client)) 