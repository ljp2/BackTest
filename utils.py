import pandas as pd
import matplotlib.pyplot as plt

class ExponentialSmoothing:
    def __init__(self, alpha=NotImplemented, length=NotImplemented):
        if alpha is NotImplemented:
            self.alpha = 2.0 / (length + 1)
        else:
            self.alpha = alpha
        print(self.alpha)
        self.smoothed_data = []
        self.new_smoothed_value = None

    def update(self, new_raw_value):
        if not self.smoothed_data:
            # If no data is present, use the first raw value as the initial smoothed value
            self.new_smoothed_value = new_raw_value
        else:
            last_smoothed_value = self.smoothed_data[-1]
            self.new_smoothed_value = self.alpha * new_raw_value + (1 - self.alpha) * last_smoothed_value

        self.smoothed_data.append(self.new_smoothed_value)
        return self.new_smoothed_value

    def get_smoothed_data(self):
        return self.smoothed_data
    