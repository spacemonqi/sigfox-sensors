import plotly
plotly.tools.set_credentials_file(username='lathkar', api_key='********************')
import plotly.plotly as py
import plotly.graph_objs as go
import numpy as np
import math #needed for definition of pi

xpoints = np.arange(0, math.pi*2, 0.05)
ypoints = np.sin(xpoints)
trace0 = go.Scatter(
   x = xpoints, y = ypoints
)
data = [trace0]
py.plot(data, filename = 'Sine wave', auto_open=True)
