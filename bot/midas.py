import os
import bot.config as config
import discord
from discord.ext import commands
from discord import app_commands
from os.path import splitext
from colorama import Back, Fore, Style
import time
import platform

intents = discord.Intents.all()
intents.message_content = True
intents.members = True

embeded_footer = '© Midas | All Rights Reserved'

cogPath = './bot/cogs'
cogModule = 'bot.cogs.'

class Midas(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or('/'), intents=intents)
    
    async def setup_hook(self):
        '''
        Sets up the bot and loads cogs
        '''
        print('>> Beginning setup...')
        print('>> Attemping to load cogs...')

        for filename in os.listdir(cogPath):
            if filename.endswith('.py') and not filename.startswith('__'):
                try: 
                    await self.load_extension(f'{cogModule}{filename[:-3]}')
                    print(f'>> Loaded {splitext(filename)[0]}')
                except Exception as e:
                    print(f'>> Failed {filename}: {e}')

        print('>> Setup complete.')      

    @commands.Cog.listener()
    async def on_app_command_completion(self, interaction: discord.Interaction, command: app_commands.Command) -> bool:
        '''
        Logs when a slash command is used
        '''
        prfx = (Back.BLACK + Fore.GREEN + time.strftime('%H:%M:%S UTC', time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
        slash_command = f"{command.name}"
        user = f"{interaction.user}"
        location = f"[{interaction.guild}]"
        print('>> ' + prfx + ' ' + user + ' executed the ' + Fore.YELLOW + slash_command + Fore.RESET + ' command in ' + location)

def createModuleEmbed(user, action, extension, color):
    '''
    Helper method to create an embed for module actions
    '''
    embed = discord.Embed(title = 'Midas Modules', color = color)
    embed.add_field(name = 'Action', value = '`' + action + '`', inline = True)
    embed.add_field(name = 'Authorized', value = '`' + user + '`', inline = True)
    embed.add_field(name = 'Module', value = '`' + ''.join(extension) + '`', inline = True)
    embed.set_footer(text = embeded_footer)

    return embed

def getUserName(name):
    '''
    Helper method to get the username from a discord user object
    '''
    requested_info = str(name)
    split_name = requested_info.split('#', 1)
    user = split_name[0]

    return user

client = Midas()

@commands.has_permissions(administrator=True)
@client.tree.command(name='load', description='Load a module')
async def load(interaction: discord.Interaction, module: str):
    '''
    Command: /load
    Description: Load a module
    Usage: /load <module>
    '''
    await client.load_extension(f'{cogModule}{module}')

    user = getUserName(interaction.user)
    embed = createModuleEmbed(user, 'LOAD', module, 0x00ff00)
            
    await interaction.response.send_message(embed = embed)
    print('>> ' + user + ' had loaded the ' + ''.join(module) + ' module.')

@commands.has_permissions(administrator=True)
@client.tree.command(name='unload', description='Unload a module')
async def unload(interaction: discord.Interaction, module: str):
    '''
    Command: /unload
    Description: Unload a module
    Usage: /unload <module>
    '''
    await client.unload_extension(f'{cogModule}{module}')

    user = getUserName(interaction.user)
    embed = createModuleEmbed(user, 'UNLOAD', module, 0xFF0000)

    await interaction.response.send_message(embed = embed)
    print('>> ' + user + ' had unloaded the ' + ''.join(module) + ' module.')

@commands.has_permissions(administrator=True)
@client.tree.command(name='reload', description='Reload a module')
async def reload(interaction: discord.Interaction, module: str):
    '''
    Command: /reload
    Description: Reload a module
    Usage: /reload <module>
    '''
    await client.unload_extension(f'{cogModule}{module}')
    await client.load_extension(f'{cogModule}{module}')
    
    user = getUserName(interaction.user)
    embed = createModuleEmbed(user, 'RELOAD', module, 0xFF7000)

    await interaction.response.send_message(embed = embed)
    print('>> ' + user + ' had reloaded the ' + ''.join(module) + ' module.')

@commands.has_permissions(administrator=True)
@client.tree.command(name='modules', description='List all modules')
async def modules(interaction: discord.Interaction):
    '''
    Command: /modules
    Description: List all modules
    Usage: /modules
    '''
    user = getUserName(interaction.user)

    filename_list = ""
    filename_count = 0

    for filename in os.listdir(cogPath):
        if filename.endswith('.py') and not filename.startswith('__'):
            filename_list += "\n`" + splitext(filename)[0] + "`"
            filename_count += 1

    embed=discord.Embed(title = "Midas Modules", description = filename_list, color=0x00ff00)
    embed.add_field(name = "Count", value = "`" + str(filename_count) + "`", inline = False)
    embed.set_footer(text = embeded_footer)

    print(">> " + user + " has executed the module list command")
    await interaction.response.send_message(embed=embed)

@commands.has_permissions(administrator=True)
@client.tree.command(name='say', description='Make the bot say something')
async def say(interaction: discord.Interaction, message: str):
    '''
    Command: /say
    Description: Make the bot say something
    Usage: /say <message>
    '''
    await interaction.response.send_message(message)

@client.event
async def on_ready():
    '''Display bot information when it is ready.'''
    prfx = (Back.BLACK + Fore.GREEN + time.strftime('%H:%M:%S UTC', time.gmtime()) + Back.RESET + Fore.WHITE + Style.BRIGHT)
    print(prfx + ' Logged in as ' + Fore.YELLOW + client.user.name)
    print(prfx + ' Bot ID ' + Fore.YELLOW + str(client.user.id))
    print(prfx + ' Discord Version ' + Fore.YELLOW + str(discord.__version__))
    print(prfx + ' Python Version ' + Fore.YELLOW + str(platform.python_version()))
    synced = await client.tree.sync()
    print(prfx + ' Slash CMDs Synced ' + Fore.YELLOW + str(len(synced)) + ' commands') 


def run():
    client.run(config.BOT_KEY)