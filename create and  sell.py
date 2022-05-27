from pybit import HTTP
import ccxt
from pprint import pprint
import api_confing_my_bybit as ac
import time
from datetime import datetime
import pandas as pd


exchange = ccxt.bybit({
    'options': {
        'adjustForTimeDifference': True,
    },
    'apiKey': ac.API_KEY,
    'secret': ac.SECRET_KEY,
    'password': ac.PASSWORD,
})


symbol = 'BTC/USDT:USDT'  # my symbol
order_book = exchange.fetch_order_book(
    symbol=symbol)   # load order book (asks and bids)
current_price = order_book['asks'][0][0]   # last ask
cost = 5    # cost $
leverage = 11  # Check first if leverage=leverage in exchange  change leverage in exchange . if you do not this you see eror ok!
leverage_params = {
    'buy_leverage': leverage,
    'sell_leverage': leverage,
}
leverageResponse = exchange.set_leverage(leverage, symbol,
                                         params=leverage_params)   # set leverage


# we calculation  amount(size) With cost
amount = (cost / current_price) * leverage
price = 25000  # enty price
shortprice = 32000  # enty price

long_sl = 24000  # stop price
long_tp = 33000  # profit price
type = 'limit'
long_sl_tk = {
    'stop_loss': long_sl,  # stop price
    'take_profit': long_tp,  # profit price
}
short_sl = 33000  # stop price
short_tp = 29000  # profit price

type = 'limit'
short_sl_tk = {
    'stop_loss': short_sl,  # stop price
    'take_profit': short_tp,  # profit price
}


run = True  # while Condition
sleep_time = 20  # sleep time for while
counter = 0  # Counter


in_long_position = False  # position Check
in_short_position = False  # position Check

while run == True:
    pprint('------------------')
    pprint('---------bot is working---------')
    pprint('------------------')
    print(f"Fetching new bars for {datetime.now().isoformat()}")
    bars = exchange.fetch_ohlcv(symbol, timeframe='1m', limit=5)  # fetch ohlcv
    df = pd.DataFrame(bars[:-1], columns=['timestamp',
                      'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    print(df)
    pprint('------------------')
    time.sleep(2)

    # create order Condition
    df.loc[df['close'] > df['open'], 'signal'] = 'long'
    # cancel order Condition
    df.loc[df['close'] < df['open'], 'signal'] = 'short'

    signal = df.iloc[-1]['signal']

    if not in_short_position and not in_long_position:  # Check for create open positions
        if signal == 'long':  # Check for create order
            pprint('long Condition is true')
            pprint('------------------')
            long_order = exchange.create_limit_buy_order(
                symbol, amount, price, params=long_sl_tk)
            in_long_position = True
            time.sleep(2)
            pprint('bot open long position')
            counter = counter + 1
            print(f'Number of positions : ‌‌{(counter)}')

    if not in_long_position and not in_short_position:  # Check for create open positions
        if signal == 'short':  # Check for create order
            pprint('short condition is true ')
            pprint('------------------')
            short_order = exchange.create_limit_sell_order(
                symbol, amount, shortprice, params=short_sl_tk)
            in_short_position = True
            time.sleep(2)
            pprint('bot open short position ')
            counter = counter + 1
            print(f'Number of positions : ‌‌{(counter)}')

    if in_long_position:
        if signal == 'short':
            pprint('close condition for long side is true')
            pprint('------------------')
            close_long_position = exchange.cancel_all_orders(symbol)
            time.sleep(2)
            pprint('bot close long position')
            in_long_position = False

    if in_short_position:
        if signal == 'long':

            pprint('close condition for short side is true')
            pprint('------------------')
            close_short_position = exchange.cancel_all_orders(symbol)
            time.sleep(2)
            pprint('bot close short position')
            in_short_position = False

    time.sleep(sleep_time)
