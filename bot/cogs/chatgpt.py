import discord
from discord.ext import commands
from discord import app_commands
import bot.config as config
import openai

embeded_footer = '© Midas | All Rights Reserved'

def create_embed(type, message, color):
    '''
    Helper method to create embeds for openAI's responses
    '''
    embed = discord.Embed(title = type, description = message, color = color)
    embed.set_footer(text = embeded_footer)

    return embed

class chatgpt(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'chatgpt', description='Ask ChatGPT a question')
    async def chatgpt(self, interaction: discord.Interaction, question: str):
        '''
        Command: /chatgpt
        Description: Ask ChatGPT a question
        Usage: /chatgpt <question>
        '''
        await interaction.response.defer()
        openai.api_key = config.OPENAI_KEY
        response = openai.Completion.create(engine='text-davinci-003', prompt=question, max_tokens=1000)
        aimsg = response['choices'][0]['text']
        embed = create_embed('ChatGPT', aimsg, 0x0097FF)

        await interaction.followup.send(embed = embed)
    
    @app_commands.command(name = 'makeimage', description='Generate an image with GPT')
    async def makeImage(self, interaction: discord.Interaction, description: str):
        
        '''
        Command: /makeimage
        Description: Generate an image with GPT
        Usage: /makeimage <description>
        '''
        await interaction.response.defer()
        openai.api_key = config.OPENAI_KEY
        response = openai.Image.create(prompt=description, n=1, size='256x256')
        image_url = response['data'][0]['url']

        await interaction.followup.send(image_url)

async def setup(client: commands.Bot) -> None:
    await client.add_cog(chatgpt(client))
