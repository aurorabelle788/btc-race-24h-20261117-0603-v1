"""Dip-buying BTC bot for make.fun btc-race-24h-20261117-0603.

Strategy (chosen by backtesting the 1,440-bar dev window with the kit harness's
exact fill model: fee 4 bps, slippage 2 bps, constant-product impact vs open
depth; dev result +$13.99, 6 trades, max drawdown 1.47%):
  - Buy when the close is >= 1.00% below the 60-bar rolling high (a dip), spending
    95% of cash. The proven 7.5%-from-session-high capitulation base makes ZERO
    trades on this dev window (its max drop from the session high is only 2.12%),
    so the entry uses a 60-bar rolling high instead, which fires reliably.
  - Exit at +2.00% take-profit, -1.50% stop-loss, or after 240 bars held.
  - Halt all trading if equity falls 20% from its peak.
  - At most 1 open position, long only, deterministic: every decision is a pure
    function of the bars seen; no clock, no environment, no randomness.

Protocol: agent-fun/bars-replay/v1 via the vendored makefun_bars shim.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "vendor"))
import makefun_bars

SYMBOL = "CBBTC"
DROP_BPS = 100        # buy when close <= rolling high * (1 - 1.00%)
TP_BPS = 200          # take profit at +2.00% vs fill price
SL_BPS = 150          # stop loss at -1.50% vs fill price
MAX_HOLD = 240        # max bars to hold a position
SIZE_BPS = 9500       # spend 95% of cash on each buy
DD_HALT_BPS = 2000    # halt trading at a 20% drawdown from peak equity
MAX_SLIP_BPS = 1000   # max slippage vs decision close (10%)
ROLL_HIGH = 60        # rolling-high window in bars
MIN_NOTIONAL = 1000000  # 1 USDC, in micro-USDC


class Bot:
    def __init__(self):
        self.closes = []
        self.entry_px = None
        self.entry_bar = -1
        self.peak_equity = None
        self.halted = False
        self.trades = 0

    def on_hello(self, state):
        self.peak_equity = state.equity

    def on_batch(self, state, batch):
        close = state.close(SYMBOL)
        if close is None:
            return []
        self.closes.append(close)
        if self.peak_equity is None:
            self.peak_equity = state.equity
        if state.equity > self.peak_equity:
            self.peak_equity = state.equity
        drawdown_bps = (self.peak_equity - state.equity) * 10000 // self.peak_equity
        if drawdown_bps >= DD_HALT_BPS:
            self.halted = True
        if self.halted:
            holding = state.positions.get(SYMBOL)
            if holding is not None and holding.qty > 0:
                self.trades += 1
                return [{"side": "sell", "symbol": SYMBOL, "qty": holding.qty,
                         "max_slippage_bps": MAX_SLIP_BPS}]
            return []
        if state.warming_up:
            return []
        holding = state.positions.get(SYMBOL)
        if holding is None or holding.qty <= 0:
            if self.entry_px is not None:
                self.entry_px = None
                self.entry_bar = -1
            lo = len(self.closes) - ROLL_HIGH
            if lo < 0:
                lo = 0
            high = max(self.closes[lo:])
            if close * 10000 <= high * (10000 - DROP_BPS):
                notional = state.cash * SIZE_BPS // 10000
                if notional >= MIN_NOTIONAL and notional <= state.cash:
                    self.trades += 1
                    return [{"side": "buy", "symbol": SYMBOL,
                             "notional_quote_units": notional,
                             "max_slippage_bps": MAX_SLIP_BPS}]
            return []
        if self.entry_px is None:
            cost = holding.cost
            spend = cost * (10000 - 4) // 10000
            self.entry_px = spend * 10**7 // holding.qty
            self.entry_bar = state.seq
        held = state.seq - self.entry_bar
        if (close * 10000 >= self.entry_px * (10000 + TP_BPS)
                or close * 10000 <= self.entry_px * (10000 - SL_BPS)
                or held >= MAX_HOLD):
            self.trades += 1
            return [{"side": "sell", "symbol": SYMBOL, "qty": holding.qty,
                     "max_slippage_bps": MAX_SLIP_BPS}]
        return []


BOT = Bot()


def on_batch(state, batch):
    return BOT.on_batch(state, batch)


def on_hello(state):
    BOT.on_hello(state)


def on_done(state, done):
    sys.stderr.write(
        "done: final cash %d micro-USDC, equity %d, orders sent %d\n"
        % (state.cash, state.equity, BOT.trades)
    )


makefun_bars.run(on_batch, on_hello=on_hello, on_done=on_done)
