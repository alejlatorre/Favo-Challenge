import numpy as np
import pandas as pd 
import plotly.graph_objs as go
from plotly.offline import (
    iplot, 
    init_notebook_mode
)

class Plotly_Plots:
    def __init__(self, df, dim_col, dim_title):
        self.df = df
        self.dim_col = dim_col
        self.dim_title = dim_title

    def series_to_frame(self, df):
        if isinstance(df, (pd.DatetimeIndex, pd.MultiIndex)):
            df = df.to_frame(index=False)
        return df

    def barplot_plotly(self):
        self.df = self.series_to_frame(self.df)

        self.df = self.df.reset_index().drop('index', axis=1, errors='ignore')
        self.df.columns = [str(c) for c in self.df.columns]  # update columns to strings in case they are numbers

        s = self.df[~pd.isnull(self.df[self.dim_col])][self.dim_col]
        chart = pd.value_counts(s).to_frame(name='data')
        chart.index.name = 'labels'
        chart = chart.reset_index().sort_values(['data', 'labels'], ascending=[False, True])
        chart = chart[:100]
        charts = [go.Bar(x=chart['labels'].values, y=chart['data'].values, name='Frequency')]
        figure = go.Figure(data=charts, layout=go.Layout({
            'barmode': 'group',
            'legend': {'orientation': 'h'},
            'title': {'text': f'{self.dim_title} Value Counts'},
            'xaxis': {'title': {'text': f'{self.dim_col}'}},
            'yaxis': {'title': {'text': 'Frequency'}}
        }))
        init_notebook_mode(connected=True)
        for chart in charts:
            chart.pop('id', None) # for some reason iplot does not like 'id'
        iplot(figure)



# if isinstance(df, (pd.DatetimeIndex, pd.MultiIndex)):
# 	df = df.to_frame(index=False)

# # remove any pre-existing indices for ease of use in the D-Tale code, but this is not required
# df = df.reset_index().drop('index', axis=1, errors='ignore')
# df.columns = [str(c) for c in df.columns]  # update columns to strings in case they are numbers

# chart_data = pd.concat([
# 	df['category'],
# 	df['order_number'],
# 	df['region_id'],
# ], axis=1)
# chart_data = chart_data.query("""(`region_id` == '2')""")
# chart_data = chart_data.sort_values(['region_id', 'category'])
# chart_data = chart_data.rename(columns={'category': 'x'})
# chart_data_nunique = chart_data.groupby(['region_id', 'x'])[['order_number']].nunique()
# chart_data_nunique.columns = ['order_number|nunique']
# chart_data = chart_data_nunique.reset_index()
# chart_data = chart_data.dropna()
# chart_data = chart_data.sort_values('order_number|nunique')

# charts = []
# charts.append(go.Bar(
# 	x=list(range(len(chart_data['x']))),
# 	y=chart_data['order_number|nunique'],
# 	name='(region_id: 2)',
# 	hovertext=chart_data['x'].values,
# 	hoverinfo='y_text'
# ))
# figure = go.Figure(data=charts, layout=go.Layout({
#     'barmode': 'group',
#     'legend': {'orientation': 'h'},
#     'title': {'text': 'Unique Count of order_number by category'},
#     'xaxis': {'nticks': 26, 'tickmode': 'auto', 'title': {'text': 'category'}},
#     'yaxis': {'tickformat': '0:g', 'title': {'text': 'Unique Count of order_number'}, 'type': 'linear'}
# }))

# If you're having trouble viewing your chart in your notebook try passing your 'chart' into this snippet:
#
# from plotly.offline import iplot, init_notebook_mode
#
# init_notebook_mode(connected=True)
# for chart in charts:
#     chart.pop('id', None) # for some reason iplot does not like 'id'
# iplot(figure)