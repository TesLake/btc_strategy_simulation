from pathlib import Path

from file_handler import load_data_from_file
from reports import print_results

BASE_DIR = Path().absolute()


class BTCPriceAnalyzer:
    def __init__(self, bank=1000):
        self.bank = self.initial_bank = bank
        self.current_btc = 0

        self.btc_price_data = []

        self.bought_btc_state = None  # Contains last bought BTC data
        self.sold_btc_state = None  # Contains last sold BTC data
        self.trade_opened = False

        # Data used for results stats
        self.biggest_trade = None
        self.biggest_trade_percent = 0
        self.biggest_lost_trade_percent = 0
        self.negative_trades = 0
        self.positive_trades = 0
        self.profits_history = []
        self.trades_to_analyze = []

    def run(self, data_filename):
        self.btc_price_data = load_data_from_file(data_filename)
        self.run_strategy_simulation()
        self.create_stats_reports()

    def run_strategy_simulation(self):
        """
            ITERATES THROUGH EACH BITCOIN PRICE DATA AND DECIDES
            TO BUY WHEN:
                EMA9 is above SMA7, PRICE below EMA50 and MACD HISTOGRAM is more than 3
            TO SELL WHEN:
                MACD HISTOGRAM is less than -5.1 AND SMA10 BELOW EMA50
        """
        for state in self.btc_price_data:
            if not self.trade_opened:  # BUY
                if (state.ema9 > state.sma7) & (state.close > state.ema50):
                    if state.macd_histogram > 3:
                        self.perform_buy(state)
            else:  # SELL
                if self.should_stop_loss(state):  # STOP LOSS
                    self.perform_sell(state)
                if state.macd_histogram < -5.1:
                    if state.sma10 < state.ema50:
                        self.perform_sell(state)

    def perform_buy(self, btc_state):
        self.bought_btc_state = btc_state
        self.current_btc = self.bank / btc_state.close
        self.trade_opened = True

    def perform_sell(self, btc_state):
        self.sold_btc_state = btc_state
        self.bank = self.current_btc * btc_state.close
        self.trade_opened = False
        self.handle_trade_stats(btc_state)

    def should_stop_loss(self, btc_state):
        """ Stop loss at -3% """
        if btc_state.close < self.bought_btc_state.close:
            percent_change = (
                (self.bought_btc_state.close - btc_state.close)
                / self.bought_btc_state.close
            ) * -100
            if percent_change < -3:
                self.trades_to_analyze.append((self.bought_btc_state, btc_state))
                return True
        return False

    def handle_trade_stats(self, btc_state):
        if btc_state.close > self.bought_btc_state.close:
            percent_change = (
                (btc_state.close - self.bought_btc_state.close)
                / self.bought_btc_state.close
            ) * 100
            self.positive_trades += 1
        else:
            percent_change = (
                (self.bought_btc_state.close - btc_state.close)
                / self.bought_btc_state.close
            ) * -100
            if not percent_change == -0.0:
                self.negative_trades += 1

        if percent_change > self.biggest_trade_percent:
            self.biggest_trade_percent = percent_change
            self.biggest_trade = (self.bought_btc_state, btc_state)
        self.profits_history.append(percent_change)

    def create_stats_reports(self):
        print_results(
            self.bank,
            self.initial_bank,
            self.profits_history,
            self.biggest_trade_percent,
            self.positive_trades,
            self.negative_trades,
        )
        with open("reports/losing_trades.txt", "w") as f:
            for i in self.trades_to_analyze[-20:]:
                f.write(str(i[0]) + "\n")
                f.write(str(i[1]) + "\n-----------------------\n\n")
        with open(BASE_DIR / "reports/profits_percentages.txt", "w") as f:
            self.profits_history.sort()
            for i in self.profits_history:
                f.write(str(i) + "\n")


if __name__ == "__main__":
    btc_analyzer = BTCPriceAnalyzer()
    data_file_path = BASE_DIR / "datasets/BTCUSD-1h_2018-01_2021-01_TA.csv"
    btc_analyzer.run(data_filename=data_file_path)
