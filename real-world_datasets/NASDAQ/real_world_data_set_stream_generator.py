import argparse
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np


class StockData:
    def __init__(self, ticker, per, date, open_price, high, low, close, vol, volume_90th_percentile, volume_10th_percentile):
        self.ticker = ticker
        self.per = per
        self.date = date
        self.open_price = float(open_price)
        self.high = float(high)
        self.low = float(low)
        self.close = float(close)
        self.vol = int(vol)
        self.volume_90th_percentile = volume_90th_percentile
        self.volume_10th_percentile = volume_10th_percentile

    def get_event_type(self):
        # Event A - price rise
        if self.close > self.open_price * 1.005:
            return 'A'
        # Event B - price drop
        elif self.close < self.open_price * 0.995:
            return 'B'
        # Event C - high trading volume
        elif self.vol > self.volume_90th_percentile:
            return 'C'
        # Event D - closing price is the highest
        elif self.close == self.high:
            return 'D'
        # Event E - closing price is the lowest
        elif self.close == self.low:
            return 'E'
        # Event F - lack of volatility
        elif abs(self.high - self.low) < 0.005 * self.open_price:
            return 'F'
        # Event G - uncertainty or indecisiveness in the market
        elif abs(self.high - self.low) > 0.01 * self.open_price and abs(self.close - self.open_price) < 0.001 * self.open_price:
            return 'G'
        # Event H - low trading volume
        elif self.vol < self.volume_10th_percentile:
            return 'H'
        else:
            return None
    
    @staticmethod
    def get_probability_distribution(stock_data_objects):
        event_types = [obj.get_event_type() for obj in stock_data_objects]
        event_counts = Counter(event_types)
        total_events = len(event_types)
        distribution = {event: count / total_events for event, count in event_counts.items()}
    
        probability_distribution = ''
        for event, probability in distribution.items():
            probability_distribution += event + " " + str(probability) + " "

        print(probability_distribution)

    @staticmethod
    def create_objects_from_file(file_path):
        volumes = []
        with open(file_path, 'r') as file:
            next(file)
            for line in file:
                values = line.strip().split(',')
                volumes.append(int(values[7]))
        volume_90th_percentile = np.percentile(volumes, 90)
        volume_10th_percentile = np.percentile(volumes, 10)
        
        objects = []
        with open(file_path, 'r') as file:
            next(file)
            for line in file:
                values = line.strip().split(',')
                data_obj = StockData(*values, volume_90th_percentile, volume_10th_percentile)
                if data_obj.get_event_type() is None:
                    continue
                objects.append(data_obj)
        return objects
    
    @staticmethod
    def generate_event_stream(stock_data_objects):
        event_stream_str = ''
        for idx,obj in enumerate(stock_data_objects):
            event_stream_str += obj.get_event_type() + " " + str(idx+1) + " "
        print(event_stream_str)


def main():
    parser = argparse.ArgumentParser(description='Generate an event stream from NASDAQ stock data.')

    parser.add_argument('--file_name', default="NASDAQ_20151102_1.txt", type=str, help='Enther the NASDAQ file name.')
    parser.add_argument('--produce_stream', default=False, action='store_true', help='If set, produce stream.')
    parser.add_argument('--produce_alphabet_probs', default=False, action='store_true', help='If set, produce alphabet probabilities.')
    args = parser.parse_args()

    stock_data = StockData.create_objects_from_file(args.file_name)

    if args.produce_stream:
        StockData.generate_event_stream(stock_data)

    if args.produce_alphabet_probs:
        StockData.get_probability_distribution(stock_data)


if __name__ == "__main__":
    main()