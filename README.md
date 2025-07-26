# OCO Order simulation script for Robinhood
cause they dont have it 😭 (use at your own risk)
## Running the script
```
python oco_bot_cli.py \
  --username YOUR_USER --password YOUR_PASS \
  --mfa 123456 \
  --symbol AAPL \
  --quantity 1 \
  --entry_price 150.00 \
  --take_profit 160.00 \
  --stop_loss 145.00 \
  --interval 20 \
  --jitter 5 \
  --av_key YOUR_ALPHAVANTAGE_API_KEY
```
