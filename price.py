import numpy as np
import math

class PriceCalculator():
  def __init__(self, drift, volatility, dt, initial_asset_price):
    self.drift = drift
    self.volatility = volatility
    self.dt = dt
    self.current_asset_price = initial_asset_price
    self.asset_prices = [initial_asset_price]

  def time_step(self):
    if len(self.asset_prices) % 100 == 0:
      self.drift = np.random.normal(0, 0.2, 1)[0]
    dw = np.random.normal(0, math.sqrt(self.dt))
    ds = self.drift * self.dt * self.current_asset_price + self.volatility * self.current_asset_price * dw
    self.asset_prices.append(self.current_asset_price + ds)
    self.current_asset_price += ds