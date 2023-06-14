import discord
from discord.ext import commands
from discord import app_commands
import datetime
import pytz
import alpaca_trade_api as tradeapi
import alpaca.data.timeframe as timeframe
import matplotlib.pyplot as plt
import bot.config as config
import io
import holidays

alpacaAPI = tradeapi.REST(config.API_KEY, config.SECRET_KEY, 'https://paper-api.alpaca.markets', 'v2')

class stocks(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(name = 'account', description='Gets account status')
    async def account(self, interaction: discord.Interaction):
        '''
        Command: /account
        Description: Gets account status
        Usage: /account
        '''
        accountInfo = alpacaAPI.get_account()
        
        embed = discord.Embed(title="Account Status", description="Alpaca Markets Account Status", color=0x47c02c)
        embed.add_field(name="Cash", value=f"${accountInfo.cash}")
        embed.add_field(name="Buying Power", value=f"${accountInfo.buying_power}")
        embed.add_field(name="Portfolio Value", value=f"${accountInfo.portfolio_value}")
        embed.add_field(name="Equity", value=f"${accountInfo.equity}")
        
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name = 'price', description='Gets the last price of a stock')
    async def price(self, interaction: discord.Interaction, ticker: str):
        '''
        Command: /price
        Description: Gets the last price of a stock
        Usage: /price <ticker>
        '''
        try:
            ticker = ticker.upper()
            lastPrice = alpacaAPI.get_latest_trade(ticker)
            await interaction.response.send_message(f"{ticker} -- {lastPrice.price}")
        except Exception as e:
            await interaction.response.send_message(f"Error getting the last price: {e}")

    @app_commands.command(name = 'check', description='Gets the last 100 days of a stock')
    async def check(self, interaction: discord.Interaction, ticker: str):
        '''
        Command: /check
        Description: Gets the last 100 days of a stock
        Usage: /check <ticker>
        '''
        try:
            ticker = ticker.upper()

            timeNow = datetime.datetime.now(pytz.timezone('US/Eastern'))
            start = timeNow - datetime.timedelta(days=100) 

            bars = alpacaAPI.get_bars(ticker, timeframe.TimeFrame.Day, start=start.isoformat(), end=None, limit=100)
            bars = bars.df

            fig = io.BytesIO()

            lastPrice = bars.tail(1)['close'].values[0]

            plt.title(f"{ticker} -- Last Price ${lastPrice:.02f}")
            plt.xlabel("Last 100 days")
            plt.plot(bars["close"])

            plt.savefig(fig, format="png")
            fig.seek(0)

            await interaction.response.send_message(file=discord.File(fig, f"{ticker}.png"))
            plt.close()
        except Exception as e:
            await interaction.response.send_message(f"Error getting the stock's data: {e}")

    @app_commands.command(name = 'check_today', description='Gets today\'s data of a stock')
    async def check_today(self, interaction: discord.Interaction, ticker: str):
        '''
        Command: /check_today
        Description: Gets today's data of a stock
        Usage: /check_today <ticker>
        '''
        try:
            ticker = ticker.upper()

            today = datetime.datetime.now(pytz.timezone('US/Eastern'))
            start = datetime.datetime(today.year, today.month, today.day, tzinfo=pytz.timezone('America/New_York'))

            bars = alpacaAPI.get_bars(ticker, timeframe.TimeFrame.Minute, start=start.isoformat(), end=None, limit=3000)
            bars = bars.df

            minute_bars = bars.tz_convert('America/New_York')

            # Resample the bars to get hourly bars for only market hours
            agg_functions = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum', 'trade_count': 'sum', }
            minute_bars = minute_bars.resample('1T').agg(agg_functions).between_time('9:30', '16:00')

            fig = io.BytesIO()

            lastPrice = bars.tail(1)['close'].values[0]

            plt.title(f"{ticker} -- Last Price ${lastPrice:.02f}")
            plt.xlabel("Today")
            plt.plot(minute_bars["close"])

            plt.savefig(fig, format="png")
            fig.seek(0)

            await interaction.response.send_message(file=discord.File(fig, f"{ticker}.png"))
            plt.close()
        except Exception as e:
            await interaction.response.send_message(f"Error getting the stock's data: {e}")

    @app_commands.command(name = 'buy', description='Buys a stock')
    async def buy(self, interaction: discord.Interaction, ticker: str, quantity: int):
        '''
        Command: /buy
        Description: Buys a stock
        Usage: /buy <ticker> <quantity>
        '''
        if isinstance(ticker, str):
            ticker=ticker.upper()

        try:
            last_trade = alpacaAPI.get_latest_trade(ticker)
            last_price = last_trade.price
        except Exception as e:
            await interaction.response.send_message(f"Error getting the last price: {e}")
            return

        embed = generate_buy_embed(ticker, quantity, last_price)

        await interaction.response.send_message(embed=embed)

        def check(reaction, user):
            return user == interaction.user

        try:
            reaction, user = await self.client.wait_for("reaction_add", timeout=30, check=check)

        except TimeoutError:
            await interaction.followup.send("Cancelling the trade. No activity")

        else:
            if str(reaction.emoji) == '👍':
                placed_order = alpacaAPI.submit_order(ticker, quantity, 'buy', 'market', 'gtc')
                await interaction.followup.send(f"Executing on the trade\nOrder ID: {placed_order.id}")
            else:
                await interaction.followup.send("Cancelling Order")

    @app_commands.command(name = 'positions', description='Gets all current positions')
    async def positions(self, interaction: discord.Interaction):
        '''
        Command: /positions
        Description: Gets all current positions
        Usage: /positions
        '''
        positions = alpacaAPI.list_positions()
        embed = generate_positions_embed(positions)

        await interaction.response.send_message(embed=embed)

    @app_commands.command(name = 'sell', description='Sells a stock')
    async def sell(self, interaction: discord.Interaction, ticker: str, quantity: int):
        '''
        Command: /sell
        Description: Sells a stock
        Usage: /sell <ticker> <quantity>
        '''
        if isinstance(ticker, str):
            ticker=ticker.upper()

        try:
            last_trade = alpacaAPI.get_latest_trade(ticker)
            last_price = last_trade.price
        except Exception as e:
            await interaction.response.send_message(f"Error getting the last price: {e}")
            return

        positions = alpacaAPI.list_positions()
        pos = 0
        for p in positions:
            if p.symbol.upper() == ticker:
                pos = int(p.qty)
                break

        if pos == 0:
            await interaction.response.send_message(f"You own 0 of {ticker}")
            return
        elif pos < quantity:
            await interaction.response.send_message(f"You can't sell {quantity} of {ticker} because you own {pos}")
            return
        
        alpacaAPI.submit_order(ticker, quantity, 'sell', 'market', 'gtc')

        await interaction.response.send_message(f"You sold {quantity} of {ticker} and now own {pos-quantity}")

        


def generate_positions_embed(positions):
    '''
    Helper method to generate the embed for the positions command
    '''
    embed = discord.Embed(title="Current Positions", 
        description="All held positions and their stats")

    for p in positions:
        embed.add_field(name=p.symbol,
        value=f"Shares: {p.qty}\nValue: {p.market_value}\nToday's Change: {round(float(p.change_today)*100, 5)}%\nUnrealized Gains: {p.unrealized_pl}",
        inline=False)

    return embed

def generate_buy_embed(ticker, quantity, market_price):
    '''
    Helper method to generate the embed for the buy command
    '''
    total = int(quantity) * market_price
    embed = discord.Embed(title=f"Buying {ticker}", description="Review your buy order below.\
        React with :thumbsup: to confirm in the next 30 seconds")
        
    embed.add_field(name="Quantity", value=f"{quantity}", inline=False)
    embed.add_field(name="Per Share Cost", value=f"{market_price}", inline=False)
    embed.add_field(name="Estimated Cost", value=f"{total}", inline=False)
    embed.add_field(name="In Force", value="Good Until Cancelled", inline=False)

    return embed


def stockHours(now = None):
    tz = pytz.timezone('US/Eastern')
    us_holidays = holidays.US()
    if not now:
        now = datetime.datetime.now(tz)
    openTime = datetime.time(hour = 9, minute = 30, second = 0)
    closeTime = datetime.time(hour = 16, minute = 0, second = 0)
    # If a holiday
    if now.strftime('%Y-%m-%d') in us_holidays:
        return False
    # If before 0930 or after 1600
    if (now.time() < openTime) or (now.time() > closeTime):
        return False
    # If it's a weekend
    if now.date().weekday() > 4:
        return False

    return True 

async def setup(client: commands.Bot) -> None:
    await client.add_cog(stocks(client))