import plotly.express as px
import plotly.io as pio
pio.renderers.default = 'browser'
iris = px.data.iris()
scatter_plot = px.scatter(iris, x="sepal_width", y="sepal_length")
pio.show(scatter_plot)
