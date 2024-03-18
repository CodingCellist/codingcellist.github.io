import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

DATA_PATH = "static/uploads/thesis-plot/wcount.csv"

# read the data and work out the daily word diff

df = pd.read_csv(DATA_PATH)
df["word_diff"] = df.words.diff()

# construct the subplot figure for containing the two graphs
fig = make_subplots(rows=2, cols=1, vertical_spacing=0.1)

# plot the data
fig.add_trace(
    # top plot: word diff
    go.Scatter(x=df["date"], y=df["word_diff"], name="difference"),
    row=1,
    col=1
)

fig.add_trace(
    # bottom plot: word count
    go.Scatter(x=df["date"], y=df["words"], name="total"),
    row=2,
    col=1
)

# set the labels of the bottom x-axis and both y-axes
fig.update_xaxes(title_text="date", row=2, col=1)
fig.update_yaxes(title_text="words", row=1, col=1)
fig.update_yaxes(title_text="words", row=2, col=1)


# set the title
fig.update_layout(title_text="How it's going:")

# output the Plotly json for rendering
print(fig.to_json())

