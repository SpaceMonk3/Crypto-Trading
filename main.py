import krakenex
from pykrakenapi import KrakenAPI
import pandas as pd
import time
import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv()

# Initialize Kraken API
api = krakenex.API(os.getenv("API_KEY"), os.getenv("PRIVATE_KEY"))  
kraken = KrakenAPI(api)

# Trading parameters
PAIR = 'XXETHUSD'  # Ethereum to USD
TRADE_AMOUNT = 0.001  # Amount to trade (0.001 ETH)
TIMEFRAME = 1  # Timeframe in minutes for OHLC data
SHORT_MA_PERIOD = 5  # Short moving average period
LONG_MA_PERIOD = 20  # Long moving average period
SLEEP_INTERVAL = 60  # Wait time in seconds between each iteration


# Fetch OHLC data
def fetch_ohlc(pair, interval):
    """
    Fetch OHLC data for the given pair and interval.
    """
    try:
        ohlc, last = kraken.get_ohlc_data(pair, interval=interval)
        return ohlc
    except Exception as e:
        print(f"Error fetching OHLC data: {e}")
        return None


# Calculate moving averages
def calculate_moving_average(df, period):
    """
    Calculate the moving average for the given period.
    """
    return df['close'].rolling(window=period).mean()


# Define trading strategy
def trading_signal(df):
    """
    Generate trading signal based on moving average crossover strategy.
    """
    # Calculate moving averages
    df['short_ma'] = calculate_moving_average(df, SHORT_MA_PERIOD)
    df['long_ma'] = calculate_moving_average(df, LONG_MA_PERIOD)

    # Determine signal
    if df['short_ma'].iloc[-1] > df['long_ma'].iloc[-1]:  # Buy signal
        return 'buy'
    elif df['short_ma'].iloc[-1] < df['long_ma'].iloc[-1]:  # Sell signal
        return 'sell'
    else:
        return 'hold'


# Place order
def place_order(pair, side, volume):
    """
    Place a market order on Kraken.
    """
    try:
        order = kraken.add_standard_order(pair=pair, type=side, ordertype='market', volume=volume)
        print(f"Order placed: {order}")
    except Exception as e:
        print(f"Error placing order: {e}")


# Main loop
def main():
    print("Starting trading bot...")
    while True:
        try:
            # Fetch data
            ohlc = fetch_ohlc(PAIR, TIMEFRAME)
            if ohlc is None:
                time.sleep(SLEEP_INTERVAL)
                continue

            # Generate signal
            signal = trading_signal(ohlc)

            # Act on signal
            if signal == 'buy':
                print("Signal: BUY")
                place_order(PAIR, 'buy', TRADE_AMOUNT)
            elif signal == 'sell':
                print("Signal: SELL")
                place_order(PAIR, 'sell', TRADE_AMOUNT)
            else:
                print("Signal: HOLD")

            # Wait before next iteration
            time.sleep(SLEEP_INTERVAL)

        except KeyboardInterrupt:
            print("Bot stopped by user.")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(SLEEP_INTERVAL)


# Run the bot
if __name__ == '__main__':
    main()
