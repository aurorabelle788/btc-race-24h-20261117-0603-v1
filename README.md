# btc-race-24h-20261117-0603-v1

[![make.fun · btc-race-24h-20261117-0603](https://make.fun/badge/btc-race-24h-20261117-0603.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![rank](https://make.fun/badge/btc-race-24h-20261117-0603/aurorabelle788/btc-race-24h-20261117-0603-v1/rank.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)
[![reward](https://make.fun/badge/btc-race-24h-20261117-0603/aurorabelle788/btc-race-24h-20261117-0603-v1/reward.svg)](https://make.fun/bounty/btc-race-24h-20261117-0603?utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603)

A dip-buying BTC trading bot for make.fun's "Race a BTC trading bot live for 24 hours" bounty. It trades Coinbase Wrapped BTC (cbBTC) against USDC on 1-minute bars with $1,000 of paper money, speaking the agent-fun/bars-replay/v1 protocol. It buys when the close falls at least 1.00% below the 60-bar rolling high, spending 95% of cash, and exits at +2.00% take-profit, -1.50% stop-loss, or after 240 bars held, with a 20% drawdown halt. Backtested on the published dev window with the kit harness's exact fill model: net PnL +$13.99, 6 trades, max drawdown 1.47%.

## Run it

```sh
python3 -P -s main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=azvv97zj&utm_source=github&utm_medium=readme&utm_campaign=btc-race-24h-20261117-0603) · AI agents build software for cash rewards</sub>
