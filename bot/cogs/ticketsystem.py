import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View, TextInput, Modal
import asyncio
import sqlite3

panelName = 'Support Tickets'
supportRoles = []
category = None
log = None
ticketChannel = None
current_ticket = 1

def populateDatabase(interaction: discord.Interaction):
    '''
    Populate the database after setup
    '''
    conn = sqlite3.connect("ticket.db")
    c = conn.cursor()

    if len(supportRoles) == 0:
        role_id = None
    else:
        role_id = ','.join(supportRoles)

    # Set all values into the database
    c.execute("""INSERT INTO ticketInfo 
             (server_id, role_id, category_id, channel_id, ticket_number) 
             VALUES (?, ?, ?, ?, ?)""", 
             (interaction.guild_id, role_id, category, log, current_ticket))
            
    conn.commit()
    conn.close()

def checkServer(interaction: discord.Interaction):
    '''
    Check if the database has been populated for the server
    '''
    conn = sqlite3.connect("ticket.db")
    c = conn.cursor()

    c.execute("""SELECT * FROM ticketInfo WHERE server_id = ?""",
          (interaction.guild_id,))
    result = c.fetchone()

    conn.commit()
    conn.close()

    return result

def updateTicketNumber(interaction: discord.Interaction):
    '''
    Update the ticket number in the database
    '''
    conn = sqlite3.connect("ticket.db")
    c = conn.cursor()

    ticket = getTicketNumber(interaction)

    # Update the ticket number
    c.execute("UPDATE ticketInfo SET ticket_number = ? WHERE server_id = ?", (ticket + 1, interaction.guild_id))
    conn.commit()
    conn.close()

def getTicketNumber(interaction: discord.Interaction):
    '''
    Get the ticket number from the database
    '''
    conn = sqlite3.connect("ticket.db")
    c = conn.cursor()

    c.execute("""SELECT ticket_number FROM ticketInfo WHERE server_id = ?""",
          (interaction.guild_id,))
    result = c.fetchone()

    ticket = result[0] if result is not None else 0

    conn.commit()
    conn.close()

    return ticket

def getSupportRoles(interaction: discord.Interaction):
    '''
    Get the support roles from the database
    '''
    conn = sqlite3.connect("ticket.db")
    c = conn.cursor()

    c.execute("""SELECT role_id FROM ticketInfo WHERE server_id = ?""",
          (interaction.guild_id,))
    result = c.fetchone()

    roles = result[0].split(',') if result is not None else []

    conn.commit()
    conn.close()

    return roles

def getCategory(interaction: discord.Interaction):
    '''
    Get the category from the database
    '''
    conn = sqlite3.connect("ticket.db")
    c = conn.cursor()

    c.execute("""SELECT category_id FROM ticketInfo WHERE server_id = ?""",
          (interaction.guild_id,))
    result = c.fetchone()

    category = result[0] if result is not None else None

    conn.commit()
    conn.close()

    return category

def getLog(interaction: discord.Interaction):
    '''
    Get the log from the database
    '''
    conn = sqlite3.connect("ticket.db")
    c = conn.cursor()

    c.execute("""SELECT channel_id FROM ticketInfo WHERE server_id = ?""",
          (interaction.guild_id,))
    result = c.fetchone()

    log = result[0] if result is not None else None

    conn.commit()
    conn.close()

    return log

def createEmbed(title, description, color):
    '''
    Create a discord embed
    '''
    embed = discord.Embed(title=title, description=description, color=color)
    return embed

async def createTicketLogEmbed(action: str, interaction: discord.Interaction, ticket_name: str):
    '''
    Generates a log message for a ticket event
    '''
    color = {
        'created': 0x00FF00, # green
        'closed': 0xFFFF00, # yellow
        'deleted': 0xFF0000, # red
    }.get(action.lower(), 0x000000) # default to black

    user = interaction.user
    user_avatar = user.display_avatar.url

    log_channel = interaction.guild.get_channel(int(getLog(interaction)))

    title = f'**LoggedInfo**'
    description = f'Ticket: {ticket_name}\nAction: {action.title()}'

    embed = createEmbed(title, description, color)
    embed.set_author(name=user, icon_url=user_avatar)

    await log_channel.send(embed=embed)

def createTicketEmbed(title, description, color):
    '''
    Create the ticket panel embed
    '''
    title = panelName
    description = 'Click the button below to create a ticket'
    embed = createEmbed(title, description, 0x00FF00)
    return embed

def createWelcomeEmbed():
    '''
    Create the welcome embed for the setup process
    '''
    title = 'Welcome to the Ticket System'
    description = '''
    It looks like this is your first time using the bot, to get started we first need to create a panel.\n
    Q: What is a panel?
    A: The panel is what we will use to create tickets, You can create multiple panels to handle issues of different types like `Bans Appeals`, `Contact an admin`, `General Help` and anything else you may need.
    '''
    embed = createEmbed(title, description, 0x00FF00)
    return embed

def createPanelCreateEmbed():
    '''
    Create the panel create embed for the setup process
    '''
    title = 'Step 1/5: Set the panel name'
    description = '''
    Use the button to set the panel name and continue.\n
    Use this to give a brief overview of what this panel is for like `Bans Appeals`, `Contact an admin`, `General Help`.\n
    This is displayed on the panel when created.
    '''
    embed1 = createEmbed(title, description, 0xAFE1AF)
    embed2 = createEmbed('Current Name', f'`{panelName}`', 0x424549)
    return embed1, embed2

def createSupportRoleEmbed(selected_roles):
    '''
    Create the support role embed for the setup process
    '''
    title = 'Step 2/5: Select the support team role(s)'
    description = '''
    The support roles will be automatically added to this panels tickets so they can assist people as needed.\n
    Use the dropdown to select roles.\n
    Not seeing your role? Try searching for it inside the dropdown\n
    '''
    embed1 = createEmbed(title, description, 0xAFE1AF)
    if len(supportRoles) == 0:
        embed2 = createEmbed('Selected Role(s)', 'None Selected..', 0x424549)
    else:
        embed2 = createEmbed('Current Roles', '\n'.join([f'<@&{role}>' for role in selected_roles]) , 0x424549)
    return embed1, embed2

def createCategoryEmbed(selected_categories):
    '''
    Create the category embed for the setup process
    '''
    title = 'Step 3/5: Select the category to create tickets in'
    description = '''
    The selected category is where tickets will be created into.\n
    Use the dropdown to select the categories.\n
    Not seeing your channel? try searching for it inside the dropdown\n
    '''
    embed1 = createEmbed(title, description, 0xAFE1AF)
    if category == None:
        embed2 = createEmbed('Selected Category', 'None Selected..', 0x424549)
    else:
        embed2 = createEmbed('Selected Category', f'<#{selected_categories}>', 0x424549)
    return embed1, embed2

def createLogEmbed(selected_channel):
    '''
    Create the log embed for the setup process
    '''
    title = 'Step 4/5: Set the ticket log channel'
    description = '''
    The selected channel is where logs will be saved into.\n
    Use the dropdown to select the channel.\n
    Not seeing your channel? Try searching for it inside the dropdown.\n
    '''
    embed1 = createEmbed(title, description, 0xAFE1AF)
    if log == None:
        embed2 = createEmbed('Selected Channel', 'None Selected..', 0x424549)
    else:
        embed2 = createEmbed('Selected Channel', f'<#{selected_channel}>', 0x424549)
    return embed1, embed2

def createPanelEmbed(selected_panel):
    '''
    Create the panel embed for the setup process
    '''
    title = 'Step 5/5: Set the panel channel'
    description = '''
    The ticket creation panel is what the community will use to create tickets.\n
    Use the dropdown to select the channel to send the panel into.\n
    Not seeing your channel? try searching for it inside the dropdown\n
    '''
    embed1 = createEmbed(title, description, 0xAFE1AF)
    if ticketChannel == None:
        embed2 = createEmbed('Selected Channel', 'None Selected..', 0x424549)
    else:
        embed2 = createEmbed('Selected Channel', f'<#{selected_panel}>', 0x424549)
    return embed1, embed2


class panelNameModal(Modal, title='Set Panel Name'):
    '''
    Set the panel name
    '''
    panel_name = TextInput(label='Panel Name', placeholder='Support Tickets', default='Support Tickets', style=discord.TextStyle.short)

    async def on_submit(self, interaction: discord.Interaction):

        global panelName
        panelName = self.panel_name.value

        embed1, embed2 = createPanelCreateEmbed()
        
        await interaction.response.edit_message(embeds=[embed1, embed2], view=setPanelNameView(timeout=None))

class RoleSelect(discord.ui.Select):
    '''
    Select the support roles for the panel
    '''
    def __init__(self, roles):
        options = []
        for role in roles:
            if role.name == '@everyone':
                continue

            option_label = f'{role.name} ({len(role.members)})'
            option_description = f'{role.name} role'

            option = discord.SelectOption(
                label=option_label,
                value=str(role.id),
                description=option_description
            )
            options.append(option)
        super().__init__(placeholder='Select a role...', options=options, max_values=len(options))
        self.selected_options = []

    async def callback(self, interaction: discord.Interaction):
        # Get the selected values
        selected_values = self.values
        
        # Get the selected role objects
        selected_roles = [value for value in selected_values if value is not None]
        
        global supportRoles
        supportRoles = selected_roles

        embed1, embed2 = createSupportRoleEmbed(selected_roles)

        await interaction.response.edit_message(embeds=[embed1, embed2], view=setSupportRoleView(interaction))

class categorySelect(discord.ui.Select):
    '''
    Select the category to create tickets in
    '''
    def __init__(self, categories):
        options = []
        for category in categories:
            # Add an option for each category, displaying the category's name and channel count
            option_label = f'{category.name}'
            option_description = f'{category.name} category'

            option = discord.SelectOption(
                label=option_label,
                value=str(category.id),
                description=option_description
            )
            options.append(option)
        super().__init__(placeholder='Select a category...', options=options)

    async def callback(self, interaction: discord.Interaction):
        # Get the selected values
        selected_values = self.values
        
        # Get the selected category objects
        selected_categories = [value for value in selected_values if value is not None]

        global category
        category = selected_categories[0]

        embed1, embed2 = createCategoryEmbed(category)

        await interaction.response.edit_message(embeds=[embed1, embed2], view=setTicketCategoryView(interaction))

class channelSelect(discord.ui.Select):
    '''
    Select the channel to send the logs into
    '''
    def __init__(self, channels):
        options = []
        for channel in channels:
            option_label = f'{channel.name}'
            option_description = f'{channel.name} channel'

            option = discord.SelectOption(
                label=option_label,
                value=str(channel.id),
                description=option_description
            )
            options.append(option)
        super().__init__(placeholder='Select a channel...', options=options)

    async def callback(self, interaction: discord.Interaction):
        # Get the selected values
        selected_value = self.values
        
        selected_channel = selected_value[0]

        global log
        log = selected_channel

        embed1, embed2 = createLogEmbed(selected_channel)

        await interaction.response.edit_message(embeds=[embed1, embed2], view=setTicketLogView(interaction))

class panelSelect(discord.ui.Select):
    '''
    Select the channel to send the panel into
    '''
    def __init__(self, channels):
        options = []
        for channel in channels:
            option_label = f'{channel.name}'
            option_description = f'{channel.name} channel'

            option = discord.SelectOption(
                label=option_label,
                value=str(channel.id),
                description=option_description
            )
            options.append(option)
        super().__init__(placeholder='Select a channel...', options=options)

    async def callback(self, interaction: discord.Interaction):
        # Get the selected values
        selected_value = self.values
        
        selected_panel = selected_value[0]

        global ticketChannel
        ticketChannel = selected_panel

        embed1, embed2 = createPanelEmbed(selected_panel)

        await interaction.response.edit_message(embeds=[embed1, embed2], view=setPanelChannelView(interaction))

class createPanelView(View):
    '''
    View to create the panel
    '''
    @discord.ui.button(label='Create a Panel')
    async def panel_button_callback(self, interaction: discord.Interaction, button):

        embed1, embed2 = createPanelCreateEmbed()
        
        await interaction.response.edit_message(embeds=[embed1, embed2], view=setPanelNameView(timeout=None))

class setPanelNameView(View):
    '''
    View to set the panel name
    '''
    @discord.ui.button(label='Set name', row=0)
    async def set_name_button_callback(self, interaction: discord.Interaction, button):
        await interaction.response.send_modal(panelNameModal())

    @discord.ui.button(label='Back', row=1)
    async def back_button_callback(self, interaction: discord.Interaction, button):

        embed = createWelcomeEmbed()

        await interaction.response.edit_message(embed=embed, view=createPanelView(timeout=None))

    @discord.ui.button(label='Save & Continue', row=1)
    async def save_button_callback(self, interaction: discord.Interaction, button):
        
        embed1, embed2 = createSupportRoleEmbed(supportRoles)

        await interaction.response.edit_message(embeds=[embed1, embed2], view=setSupportRoleView(interaction))

class setSupportRoleView(View):
    '''
    View to set the support roles
    '''

    def __init__(self, interaction):
        super().__init__()
        self.guild = interaction.guild
        self.roles = self.guild.roles
        self.role_select = RoleSelect(self.roles)
        self.add_item(self.role_select)

    @discord.ui.button(label='Back', row=1)
    async def back_button_callback(self, interaction: discord.Interaction, button):
        
        embed1, embed2 = createPanelCreateEmbed()

        await interaction.response.edit_message(embeds=[embed1, embed2], view=setPanelNameView(timeout=None))

    @discord.ui.button(label='Save & Continue', row=1)
    async def save_button_callback(self, interaction: discord.Interaction, button):
        
        embed1, embed2 = createCategoryEmbed(category)

        await interaction.response.edit_message(embeds=[embed1, embed2], view=setTicketCategoryView(interaction))

class setTicketCategoryView(View):
    '''
    View to set the category to create tickets in
    '''

    def __init__(self, interaction):
        super().__init__()
        self.guild = interaction.guild
        self.categories = self.guild.categories
        self.category_select = categorySelect(self.categories)
        self.add_item(self.category_select)

    @discord.ui.button(label='Back', row=1)
    async def back_button_callback(self, interaction: discord.Interaction, button):

        embed1, embed2 = createSupportRoleEmbed(supportRoles)

        await interaction.response.edit_message(embeds=[embed1, embed2], view=setSupportRoleView(interaction))

    @discord.ui.button(label='Save & Continue', row=1)
    async def save_button_callback(self, interaction: discord.Interaction, button):
        
        embed1, embed2 = createLogEmbed(log)

        await interaction.response.edit_message(embeds=[embed1, embed2], view=setTicketLogView(interaction))

class setTicketLogView(View):
    '''
    View to set the channel to send logs to
    '''

    def __init__(self, interaction):
        super().__init__()
        self.guild = interaction.guild
        self.channels = self.guild.text_channels
        self.channel_select = channelSelect(self.channels)
        self.add_item(self.channel_select)

    @discord.ui.button(label='Back', row=1)
    async def back_button_callback(self, interaction: discord.Interaction, button):

        embed1, embed2 = createCategoryEmbed(category)

        await interaction.response.edit_message(embeds=[embed1, embed2], view=setTicketCategoryView(interaction))

    @discord.ui.button(label='Save & Continue', row=1)
    async def save_button_callback(self, interaction: discord.Interaction, button):
        
        embed1, embed2 = createPanelEmbed(ticketChannel)

        await interaction.response.edit_message(embeds=[embed1, embed2], view=setPanelChannelView(interaction))

class setPanelChannelView(View):
    '''
    View to set the channel to send the panel into
    '''

    def __init__(self, interaction):
        super().__init__()
        self.guild = interaction.guild
        self.channels = self.guild.text_channels
        self.channel_select = panelSelect(self.channels)
        self.add_item(self.channel_select)

    @discord.ui.button(label='Back', row=1)
    async def back_button_callback(self, interaction: discord.Interaction, button):
        
        embed1, embed2 = createLogEmbed(log)

        await interaction.response.edit_message(embeds=[embed1, embed2], view=setTicketLogView(interaction))

    @discord.ui.button(label='Finish', row=1)
    async def save_button_callback(self, interaction: discord.Interaction, button):
        if category == None or log == None or ticketChannel == None:
            embed = createEmbed('Error', 'You must select all options before finishing the setup', 0xFF0000)
            await interaction.response.edit_message(embed=embed, view=setPanelChannelView(timeout=None))
        else:
            embed = createEmbed('Setup Complete', 'You can now create tickets by using the `newticket` command', 0x00FF00)
            await interaction.response.edit_message(embed=embed, view=None)
            channel = await self.guild.fetch_channel(ticketChannel)

            populateDatabase(interaction)

            # Create the panel
            description = 'Hello, to create a ticket to speak privately with the staff team, please react to this message with: 📩'
            embed = createEmbed('', description, 0x00FF00)
            embed.set_author(name = panelName)
            embed.set_footer(text = '© Midas | All Rights Reserved')
            await channel.send(embed=embed, view=createTicketView(timeout=None))

class createTicketView(View):
    '''
    View to create a new ticket
    '''

    @discord.ui.button(label='Create Ticket', emoji='📩')
    async def create_ticket_button_callback(self, interaction: discord.Interaction, button):

        ticket_number = 'ticket-{0:04d}'.format(getTicketNumber(interaction))

        category_channel = interaction.guild.get_channel(int(getCategory(interaction)))
        
        # Create a new channel
        channel = await interaction.guild.create_text_channel(ticket_number, category=category_channel)

        # Lock the channel
        await channel.set_permissions(interaction.guild.default_role, read_messages=False, send_messages=False)

        # Add the support roles to the channel
        supportRoles = getSupportRoles(interaction)
        for role_id in supportRoles:
            role = interaction.guild.get_role(int(role_id))
            await channel.set_permissions(role, read_messages=True, send_messages=True)
        
        # Add the user to the channel
        await channel.set_permissions(interaction.user, read_messages=True, send_messages=True)

        # Send a message to the new channel
        title = ''
        description = 'Hello, a staff member will be with you as soon as possible. If you\'d like to close this ticket at any point, please react to this message with: 🔒'
        embed = createEmbed(title, description, 0x00FF00)
        await channel.send(embed=embed, view=createCloseTicketView(timeout=None))

        # Send a message to the user
        await interaction.response.send_message('Your ticket has been created in {0}'.format(channel.mention), ephemeral=True)

        await createTicketLogEmbed('created', interaction, channel.name)

        updateTicketNumber(interaction)

class createCloseTicketView(View):
    '''
    View to close a ticket
    '''

    @discord.ui.button(label='Close Ticket', emoji='🔒')
    async def close_ticket_button_callback(self, interaction: discord.Interaction, button):
        await interaction.response.send_message('Are you sure you would like to close this ticket?', view=createConfirmCloseTicketView(timeout=None))

class createConfirmCloseTicketView(View):
    '''
    View to confirm closing a ticket
    '''

    @discord.ui.button(label='Close', style=discord.ButtonStyle.red)
    async def close_ticket_button_callback(self, interaction: discord.Interaction, button):
        user_id = interaction.user.id
        
        channel = interaction.channel
        channel_name = channel.name

        ticket_number = channel_name.split('-')[1]

        async for message in channel.history(limit=1):
            await message.delete()

        # Remove all permissions for users to send messages
        for member in channel.members:
            if member.guild_permissions.administrator:
                continue
            else:
                await channel.set_permissions(member, read_messages=True, send_messages=False)

        embed = createEmbed('', f'Ticket Closed by <@{user_id}>', 0xFFFF00)
        await interaction.response.send_message(embed=embed)

        await channel.edit(name=f'closed-{ticket_number}')

        embed = createEmbed('', '`Support Team Ticket Controls`', discord.Color.default())
        await interaction.followup.send(embed=embed, view=createTicketControlsView(timeout=None))
        await createTicketLogEmbed('closed', interaction, interaction.channel.name)
    
    @discord.ui.button(label='Cancel')
    async def cancel_ticket_button_callback(self, interaction: discord.Interaction, button):
        channel = interaction.channel
        async for message in channel.history(limit=1):
            await message.delete()

class createTicketControlsView(View):

    @discord.ui.button(label='open', emoji='🔓')
    async def open_ticket_button_callback(self, interaction: discord.Interaction, button):
        user_id = interaction.user.id

        channel = interaction.channel
        channel_name = channel.name

        ticket_number = channel_name.split('-')[1]

        async for message in channel.history(limit=1):
            await message.delete()

        # Add all permissions for users to send messages
        for member in channel.members:
            if member.guild_permissions.administrator:
                continue
            else:
                await channel.set_permissions(member, read_messages=True, send_messages=True)

        embed = createEmbed('', f'Ticket Opened by <@{user_id}>', 0x00FF00)
        await interaction.response.send_message(embed=embed)

        await channel.edit(name=f'ticket-{ticket_number}')
        await createTicketLogEmbed('created', interaction, interaction.channel.name)
        
        
    @discord.ui.button(label='delete', emoji='⛔')
    async def delete_ticket_button_callback(self, interaction: discord.Interaction, button):

        embed = createEmbed('', f'Ticket will be deleted in a few seconds', 0xFF0000)

        await interaction.response.send_message(embed=embed)

        await asyncio.sleep(5)
        await interaction.channel.delete()
        await createTicketLogEmbed('deleted', interaction, interaction.channel.name)



class ticketsystem(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.has_permissions(administrator=True)
    @app_commands.command(name = 'setup', description='Sets up the ticket system')
    async def setup(self, interaction: discord.Interaction):
        '''
        Command: /setup
        Description: Sets up the ticket system
        Usage: /setup
        '''
        result = checkServer(interaction)

        if result is None:
            embed = createWelcomeEmbed()
            await interaction.response.send_message(embed=embed, ephemeral=True, view=createPanelView(timeout=None))
        else:
            await interaction.response.send_message('The ticket system has already been setup for this discord server.', ephemeral=True)


    @app_commands.command(name = 'newticket', description='Creates a new ticket')
    async def newTicket(self, interaction: discord.Integration):
        '''
        Command: /newticket
        Description: Creates a new ticket
        Usage: /newticket
        '''

        ticket_number = 'ticket-{0:04d}'.format(getTicketNumber(interaction))
        # Create a new channel with the user
        ticket_channel = await interaction.guild.create_text_channel(f'{ticket_number}', category=interaction.guild.get_channel(int(getCategory(interaction))))
        updateTicketNumber(interaction)

        # Set the permissions for the new channel
        await ticket_channel.set_permissions(interaction.user, read_messages=True, send_messages=True)
        await ticket_channel.set_permissions(interaction.guild.default_role, read_messages=False)

        # Add the support roles to the channel
        supportRoles = getSupportRoles(interaction)
        for role_id in supportRoles:
            role = interaction.guild.get_role(int(role_id))
            await ticket_channel.set_permissions(role, read_messages=True, send_messages=True)
        
        # Send a message to the user in the original channel with a link to the new channel
        await interaction.response.send_message(f'Ticket created! You can access it here: {ticket_channel.mention}')

        # Send a message to the new channel
        title = ''
        description = '''
        Hi, a member of the Staff Team will be with you as soon as possible.
        If you\'d like to close this ticket at any point, please react to this message with: 🔒
        '''
        embed = createEmbed(title, description, 0x00FF00)
        await ticket_channel.send(embed=embed, view=createCloseTicketView())
        await createTicketLogEmbed('created', interaction, ticket_channel.name)

    
    @app_commands.command(name = 'deleteticket', description='Deletes a ticket')
    async def deleteTicket(self, interaction: discord.Interaction):
        '''
        Command: /deleteticket
        Description: Deletes a ticket
        Usage: /deleteticket
        '''

        channel = interaction.channel
        
        if channel.name.startswith('ticket-'):
            await interaction.response.send_message('Please close the ticket before deleteing a ticket!', view=createConfirmCloseTicketView())
        elif channel.name.startswith('closed-'):
            embed = createEmbed('', f'Ticket will be deleted in a few seconds', 0xFF0000)

            await interaction.response.send_message(embed=embed)           

            await asyncio.sleep(5)
            await interaction.channel.delete()

            await createTicketLogEmbed('deleted', interaction, channel.name)
        else:
            await interaction.response.send_message(f'You can only delete tickets!')
    
    @app_commands.command(name = 'lockticket', description='Locks a ticket')
    async def lockTicket(self, interaction: discord.Interaction):
        '''
        Command: /lockticket
        Description: Locks a ticket
        Usage: /lockticket
        '''

        channel = interaction.channel
        
        if channel.name.startswith('ticket-'):
            await interaction.response.send_message('Are you sure you would like to close this ticket?', view=createConfirmCloseTicketView())
        else:
            await interaction.response.send_message(f'You can only lock tickets!')

    @app_commands.command(name = 'openticket', description='Opens a ticket')
    async def openTicket(self, interaction: discord.Interaction):
        '''
        Command: /openticket
        Description: Opens a ticket
        Usage: /openticket
        '''
        
        user_id = interaction.user.id
        channel = interaction.channel
        channel_name = channel.name

        ticket_number = channel_name.split('-')[1]
        
        if channel.name.startswith('closed-'):
            await channel.set_permissions(channel.guild.default_role, read_messages=True, send_messages=True)
            for member in channel.members:
                if member.guild_permissions.administrator:
                    continue
                else:
                    await channel.set_permissions(member, read_messages=True, send_messages=True)
            embed = createEmbed('', f'Ticket Opened by <@{user_id}>', 0x00FF00)
            await interaction.response.send_message(embed=embed)
            await channel.edit(name=f'ticket-{ticket_number}')
            await createTicketLogEmbed('opened', interaction, channel_name)
        else:
            await interaction.response.send_message(f'You can only open closed tickets!')

    @app_commands.command(name = 'adduser', description='Adds a user to a ticket')
    async def addUser(self, interaction: discord.Interaction, user: discord.Member):
        '''
        Command: /adduser
        Description: Adds a user to a ticket
        Usage: /adduser <user>
        '''

        channel = interaction.channel
        
        if channel.name.startswith('ticket-'):
            await channel.set_permissions(user, read_messages=True)
            await interaction.response.send_message(f"{user.mention} has been added to the ticket!")
        else:
            await interaction.response.send_message("This command can only be used in a ticket channel.")

    @app_commands.command(name = 'removeuser', description='Removes a user from a ticket')
    async def removeUser(self, interaction: discord.Interaction, user: discord.Member):
        '''
        Command: /removeuser
        Description: Removes a user from a ticket
        Usage: /removeuser <user>
        '''

        channel = interaction.channel
        
        if channel.name.startswith('ticket-'):
            if user._permissions_in(channel).read_messages:
                await channel.set_permissions(user, read_messages=False)
                await interaction.response.send_message(f"{user.mention} has been removed from the ticket!")
        else:
            await interaction.response.send_message("This command can only be used in a ticket channel.")

async def setup(client: commands.Bot) -> None:
    await client.add_cog(ticketsystem(client))