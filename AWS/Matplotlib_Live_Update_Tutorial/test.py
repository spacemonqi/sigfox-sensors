import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import pandas as pd


plt.style.use('seaborn')
fig = plt.figure()
ax = fig.add_subplot(1,1,1)


def animation(i):
  AAPL_STOCK = pd.read_csv('https://raw.githubusercontent.com/plotly/datasets/master/2014_apple_stock.csv')
  x = []
  y = []

  x = AAPL_STOCK[0:i]['AAPL_x']
  y = AAPL_STOCK[0:i]['AAPL_y']

  ax.clear()
  ax.plot(x, y)

animation = FuncAnimation(fig, func=animation, interval=1000)
plt.show()
