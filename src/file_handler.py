import csv
from datetime import datetime
from collections import namedtuple

import pandas as pd
from ta.volatility import BollingerBands, AverageTrueRange
from ta.momentum import RSIIndicator
from ta.trend import MACD, SMAIndicator, EMAIndicator
from ta.volume import VolumeWeightedAveragePrice

BtcState = namedtuple(
    "BtcState",
    "datetime open high low close volume sma7 sma10 sma15 sma30 ema9 ema50 macd macd_signal "
    "macd_histogram vwap bollinger_hband bollinger_lband bollinger_mavg rsi atr",
)


def load_data_from_file(filename):
    with open(filename, "r") as f:
        data = csv.reader(f)
        for i in range(50):
            # Skip incomplete data
            next(data)

        btc_states = []
        for row in data:
            btc_states.append(
                BtcState(
                    open=float(row[1]),
                    close=float(row[2]),
                    high=float(row[3]),
                    low=float(row[4]),
                    volume=float(row[5]),
                    datetime=datetime.strptime(row[7], "%Y-%m-%dT%H:%M:%S"),
                    bollinger_hband=float(row[8]),
                    bollinger_lband=float(row[9]),
                    bollinger_mavg=float(row[10]),
                    atr=float(row[11]),
                    rsi=float(row[12]),
                    macd=float(row[13]),
                    macd_signal=float(row[14]),
                    macd_histogram=float(row[15]),
                    sma7=float(row[16]),
                    sma15=float(row[17]),
                    sma30=float(row[18]),
                    vwap=float(row[19]),
                    ema9=float(row[20]),
                    ema50=float(row[21]),
                    sma10=float(row[22]),
                )
            )
    return btc_states


def add_technical_indicators_to_data(filename):
    df = pd.read_csv(filename)
    closes = df["close"]
    highs = df["high"]
    lows = df["low"]

    #  Merge date time columns
    df["datetime"] = df["date"] + "T" + df["time"]
    del df["date"]
    del df["time"]

    b = BollingerBands(close=closes)
    df["bollinger_hband"] = b.bollinger_hband()
    df["bollinger_lband"] = b.bollinger_lband()
    df["bollinger_mavg"] = b.bollinger_mavg()

    atr = AverageTrueRange(close=closes, high=highs, low=lows).average_true_range()
    df["atr"] = atr

    rsi = RSIIndicator(close=closes).rsi()
    df["rsi"] = rsi

    macd = MACD(close=closes)
    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    df["macd_histogram"] = macd.macd_diff()

    sma7 = SMAIndicator(close=closes, window=7).sma_indicator()
    sma15 = SMAIndicator(close=closes, window=15).sma_indicator()
    sma30 = SMAIndicator(close=closes, window=30).sma_indicator()
    df["sma7"] = sma7
    df["sma15"] = sma15
    df["sma30"] = sma30

    vwap = VolumeWeightedAveragePrice(
        high=highs, low=lows, close=closes, volume=df["volume"]
    ).volume_weighted_average_price()
    df["vwap"] = vwap

    ema9 = EMAIndicator(close=closes, window=9).ema_indicator()
    ema50 = EMAIndicator(close=closes, window=50).ema_indicator()
    df["ema9"] = ema9
    df["ema50"] = ema50

    sma10 = SMAIndicator(close=closes, window=10).sma_indicator()
    df["sma10"] = sma10

    filename = filename.split(".")[0] + "_TA.csv"
    df.to_csv(filename)  # Save new file
