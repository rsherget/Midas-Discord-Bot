from discord.ext import tasks
import asyncio.tasks



class TradeTask:
    """A background task helper that abstracts the loop and reconnection logic for you.
    The main interface to create this is through :func:`loop`.
    """

    def __init__(self, ticker: str, task: asyncio.Task):
        self.ticker = ticker
        self.task = task

    def __str__(self):
        return f"{self.ticker} task"
    
    def __repr__(self):
        return str(self)

    def getTicker(self):
        return self.ticker
    
    def getTask(self):
        return self.task
    
    def closeTask(self):
        self.task.cancel()
    
    def isRunning(self):
        return not bool(self.task.done()) if self.task else False
