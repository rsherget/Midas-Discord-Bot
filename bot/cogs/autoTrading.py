import discord
from discord.ext import commands
from discord import app_commands
from discord.ext import tasks
import bot.taskLoop as tLoop
import alpaca_trade_api as tradeapi
import time
import talib
import numpy as np
import bot.config as config
import alpaca.data.timeframe as timeframe
import pytz
import datetime
import holidays

api = tradeapi.REST(config.API_KEY, config.SECRET_KEY, 'https://paper-api.alpaca.markets', 'v2')

TradeTasks = []

class autoTrading(commands.Cog):
    def __init__(self, client):
        self.client = client

    def get_historical_data(self, symbol):
        today = datetime.datetime.now(pytz.timezone('US/Eastern'))
        start = datetime.datetime(today.year, today.month, today.day, tzinfo=pytz.timezone('America/New_York'))
        barset = api.get_bars(symbol, timeframe.TimeFrame.Minute, start=start.isoformat(), end=None, limit=3000)
        return barset.df

    def calculate_rsi(self, close_prices, n=14):
        return talib.RSI(close_prices, timeperiod=n)[-1]

    def calculate_sma(self, close_prices, n):
        return np.mean(close_prices[-n:])

    def check_price(self, symbol):
        bars = self.get_historical_data(symbol)
        minute_bars = bars.tz_convert('America/New_York')

        # Resample the bars to get hourly bars for only market hours
        agg_functions = {'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last', 'volume': 'sum', 'trade_count': 'sum', }
        minute_bars = minute_bars.resample('1T').agg(agg_functions).between_time('9:30', '16:00')

        close_prices = bars['close'].values
        rsi = self.calculate_rsi(close_prices)
        sma = self.calculate_sma(close_prices, 30)

        return (rsi, sma, close_prices[-1])

    def trade(self, symbol, qty, side):
        api.submit_order(symbol.upper(), qty, side, 'market', 'gtc')

    def positions(self, ticker):
        positions = api.list_positions()
        for p in positions:
            if p.symbol.lower() == ticker.lower():
                return int(p.qty)
                
        return 0

    @app_commands.command(name = 'all_auto_trades', description='Gets All Active AutoTrading Tasks')
    async def all_auto_trades(self, interaction: discord.Interaction):
        s = ''
        for t in TradeTasks:
            if t.isRunning():
                s += f'{str(t)} \n'
            else:
                t.closeTask()
                TradeTasks.remove(t)

        await interaction.response.send_message(s)

    
    @app_commands.command(name = 'close_task', description='Close AutoTrading Task')
    async def close_task(self, interaction: discord.Interaction, ticker: str):
        found = False
        s = ''
        for t in TradeTasks:
            if t.getTicker() == ticker:
                t.closeTask()
                TradeTasks.remove(t)
                found = True

        if found:
            await interaction.response.send_message(f"Closed all AutoTrading tasks for {ticker}")
        else:
            await interaction.response.send_message(f"There were no open AutoTrading tasks for {ticker}")


    @app_commands.command(name = 'start_auto_trading', description='Starts AutoTrading')
    async def start_auto_trading(self, interaction: discord.Interaction, ticker: str):
        @tasks.loop(minutes=1.0)
        async def trader():
            # indicators 0 = rsi, 1 = sma, 2 = last price
            indicators = self.check_price(ticker)
            shares = self.positions(ticker)
            qty = 1

            channel = discord.utils.get(self.client.get_all_channels(), name='stockauto')
            channel_id = channel.id

            channel = self.client.get_channel(channel_id)
            # buy at rsi < 40, sma > price
            if indicators[0] < 35 and indicators[1] > indicators[2]:
                self.trade(ticker, qty, 'buy')
                shares += qty
                await channel.send(f"Bought a share of {ticker}: RSI: {indicators[0]}, SMA: {indicators[1]}, Last Price: {indicators[2]}")
            # sell at rsi > 60, sma < price
            elif indicators[0] > 65 and indicators[1] < indicators[2] and shares > qty:
                self.trade(ticker, qty, 'sell')
                shares -= qty
                await channel.send(f"Sold a share of {ticker}: RSI: {indicators[0]}, SMA: {indicators[1]}, Last Price: {indicators[2]}")

        try:
            t = trader.start()
            TradeTasks.append(tLoop.TradeTask(ticker, t))
            await interaction.response.send_message(f"Now starting AutoTrading with ticker {ticker}. I will notify you when any trades are made")
        except:
            await interaction.response.send_message(f"Something went wrong getting data for {ticker}")

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
    await client.add_cog(autoTrading(client))