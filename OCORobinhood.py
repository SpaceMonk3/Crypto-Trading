import time, random, argparse
import robin_stocks.robinhood as rh
import requests

# External data provider for live stock prices(Alpha Vantage)
from alpha_vantage.timeseries import TimeSeries

def login(username, password, mfa=None):
    if mfa:
        rh.login(username, password, mfa_code=mfa)
    else:
        rh.login(username, password)

def get_live_price(av_key, symbol):
    ts = TimeSeries(key=av_key, output_format='json')
    data, _ = ts.get_quote_endpoint(symbol)
    return float(data['05. price'])

def buy_entry(symbol, qty, limit):
    if limit:
        return rh.orders.order_buy_limit(symbol, qty, limitPrice=limit)
    return rh.orders.order_buy_market(symbol, qty)

def place_exit_orders(symbol, qty, tp, sl):
    tp_order = rh.orders.order_sell_limit(symbol, qty, limitPrice=tp)
    sl_order = rh.orders.order_sell_stop_loss(symbol, qty, stopPrice=sl)
    return {'tp': tp_order, 'sl': sl_order}

def cancel(order):
    rh.orders.cancel_order(order['id'])

def main():
    parser = argparse.ArgumentParser(description="Simulate OCO using Robinhood API")
    parser.add_argument('--username', required=True)
    parser.add_argument('--password', required=True)
    parser.add_argument('--mfa', default=None, help='MFA code if enabled')
    parser.add_argument('--symbol', required=True)
    parser.add_argument('--quantity', type=float, required=True)
    parser.add_argument('--entry_price', type=float, default=None,
                        help="Limit price; omit for market entry")
    parser.add_argument('--take_profit', type=float, required=True)
    parser.add_argument('--stop_loss', type=float, required=True)
    parser.add_argument('--interval', type=float, default=20,
                        help="Polling interval in seconds (default 20)")
    parser.add_argument('--jitter', type=float, default=5,
                        help="Random jitter ± seconds (default 5)")
    parser.add_argument('--av_key', required=True,
                        help="Alpha Vantage API key for live pricing")

    args = parser.parse_args()

    login(args.username, args.password, args.mfa)
    print("Logged in successfully.")

    entry_order = buy_entry(args.symbol, args.quantity, args.entry_price)
    print("Entry order placed:", entry_order)
    time.sleep(1)

    exits = place_exit_orders(args.symbol, args.quantity,
                              args.take_profit, args.stop_loss)
    print("Exit orders placed:", exits)

    while True:
        price = get_live_price(args.av_key, args.symbol)
        print(f"[{time.strftime('%H:%M:%S')}] {args.symbol} price: ${price:.2f}")

        if price >= args.take_profit:
            print("Take-profit reached ✅")
            rh.orders.order_sell_market(args.symbol, args.quantity)
            cancel(exits['sl'])
            break
        elif price <= args.stop_loss:
            print("Stop-loss reached 🔻")
            rh.orders.order_sell_market(args.symbol, args.quantity)
            cancel(exits['tp'])
            break

        wait = max(1, args.interval + random.uniform(-args.jitter, args.jitter))
        time.sleep(wait)

    print("OCO sequence completed.")

if __name__ == '__main__':
    main()
