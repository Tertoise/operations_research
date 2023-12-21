import numpy as np

class PoissonProcessGenerator:
    def __init__(self, intensity, time_step, value_range):
        self.intensity = intensity
        self.time_step = time_step
        self.value_range = value_range

    def generate_next_value(self):
        # Generate the number of events in the given time interval
        num_events = np.random.poisson(self.intensity * self.time_step)

        # Clip the number of events to stay within the range of values
        num_events = np.clip(num_events, 0, len(self.value_range) - 1)

        # Choose a random value from the modified range
        value = np.random.choice(self.value_range, size=num_events + 1)[-1]
        value = int(round(1 - value / max(self.value_range), 0))

        # Update the time

        return value