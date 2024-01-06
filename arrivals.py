import pandas as pd
import time

class Arrivals:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.df):
            result = self.df.iloc[[self.index]]
            self.index += 1
            return result
        else:
            return None
            # raise StopIteration

    def waitforarrival(self):
        time.sleep(0.25)
        # input()
        self.arrival = next(self)
        return self.arrival

