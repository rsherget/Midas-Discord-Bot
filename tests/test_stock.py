import pytest
import bot.cogs.autoTrading as autoTrading
import numpy as np
import time

@pytest.fixture()
def Auto():
    auto = autoTrading.autoTrading('None')
    yield auto


def test_rsi(Auto: autoTrading.autoTrading):
    nums = np.array([1.0,3.0,7.0,4.0,8.0,5.0,0.0,8.0,6.0,3.0,6.0,8.0,6.0,8.0,5.0,3.0,6.0,8.0,5.0,2.0])

    assert round(Auto.calculate_rsi(nums, 10), 2) == 46.52
    assert round(Auto.calculate_rsi(nums, 15), 2) == 49.89

def test_sma(Auto: autoTrading.autoTrading):
    nums = np.array([1.0,3.0,7.0,4.0,8.0,5.0,0.0,8.0,6.0,3.0,6.0,8.0,6.0,8.0,5.0,3.0,6.0,8.0,5.0,2.0])

    assert round(Auto.calculate_sma(nums, 10), 1) == 5.7
    assert round(Auto.calculate_sma(nums, 15), 1) == 5.3

def test_check_price(Auto: autoTrading.autoTrading):
    stockData = Auto.check_price('AAPL')

    assert stockData[0]
    assert stockData[1]
    assert stockData[2]


def test_buy_sell(Auto: autoTrading.autoTrading):
    if not autoTrading.stockHours():
        pytest.skip('Not During Stock Hours')
    
    pos = Auto.positions('DLTR')
    if pos > 0:
        Auto.trade('DLTR', pos, 'sell')
        time.sleep(1)
        pos = Auto.positions('DLTR')

    assert pos == 0

    Auto.trade('DLTR', 1, 'buy')
    time.sleep(1)
    pos = Auto.positions('DLTR')

    assert pos == 1

    Auto.trade('DLTR', 1, 'sell')
    time.sleep(1)
    pos = Auto.positions('DLTR')

    assert pos == 0
