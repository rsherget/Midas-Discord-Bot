from bot.midas import Midas
import pytest
from discord.ext import commands

@pytest.fixture()
def coroutine():
    async def some_coro(*args, **kwargs):
        return args, kwargs

    return some_coro

@pytest.fixture()
def Bot():
    midas = Midas()

    yield midas

@pytest.fixture(scope="session")
def group():
    @commands.group()
    async def fixturegroup(*args, **kwargs):
        return args, kwargs

    return fixturegroup

def is_Command(obj):
    return isinstance(obj, commands.Command)


def is_Group(obj):
    return isinstance(obj, commands.Group)



def test_command_decorators(coroutine):
    assert is_Command(commands.command(name="cmd")(coroutine))
    assert is_Group(commands.group(name="grp")(coroutine))


def test_group_decorator_methods(group, coroutine):
    assert is_Command(group.command(name="cmd")(coroutine))
    assert is_Group(group.group(name="grp")(coroutine))


def test_bot_decorator_methods(Bot, coroutine):
    assert is_Command(Bot.command(name="cmd")(coroutine))
    assert is_Group(Bot.group(name="grp")(coroutine))
