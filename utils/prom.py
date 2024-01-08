import streamlit as st
import os
import plotly.graph_objs as go
import plotly.express as px

from prometheus_pandas import query
import pandas as pd

#FIXME: signature should be df Or serie
def get_plotly_title_defaults():
    return dict(y=0.92, x=0.5, xanchor="center", yanchor='top')

def prom_label(df, label):
    if type(df) is pd.core.series.Series :
        return df.rename(index=lambda x:prom_split_label(x, label))
    else:
        return df.rename(columns={col: prom_split_label(col, label) for col in df.columns})

#FIXME: signature: should be column or row
#FIXME: exception if not found label
def prom_split_label(column_name, label):
    return column_name.split(f'{label}=')[1].split(',')[0].strip('"')

def promql(prometheus_query, start_time=None, end_time=None):
    # Replace with your Prometheus server URL
    prom_url = None
    if "prom_url" in os.environ:
        prom_url = os.environ["prom_url"]
    else:
        prom_url = st.secrets.prom_credentials.url

    p = query.Prometheus(prom_url)

    if end_time != None:
        # TODO: is 60s best value? should it be configurable
        return p.query_range(
            prometheus_query,
            start_time, end_time, (end_time-start_time)/20)
    else: 
        return p.query(
            prometheus_query,
            start_time)


def line_chart(df, title, extract_label=None):
    if extract_label: 
        df = prom_label(df, extract_label)

    fig = px.line(df, markers=True)

    plottly_title=get_plotly_title_defaults()
    plottly_title.update({'text': title})
    fig.update_layout(
        title=plottly_title,
        xaxis=dict(
            tickformat='%Y-%m-%d %H:%M:%S',
        ),
        legend=dict(
            orientation="h"
        )
    )

    # Display the figure in Streamlit
    st.plotly_chart(fig, use_container_width=True)

def gauge_chart(value, total, title="", warn_factor=0.7, alarm_factor=0.9):
    fig = go.Figure(
        go.Indicator(
            mode = "gauge+number",
            value = value,
            domain = {'x': [0, 1], 'y': [0, 1]},
            gauge = {
                'axis': {'range': [None, total], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bgcolor': "red",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, total*warn_factor], 'color': 'green'},
                    {'range': [total*warn_factor, total*alarm_factor], 'color': 'orange'}],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                    }}
        )
    )

    plottly_title=get_plotly_title_defaults()
    plottly_title.update({'text': title})
    fig.update_layout(
        title=plottly_title
    )

    st.plotly_chart(fig, use_container_width=True)

def bar_chart(df, title, extract_label=None):
    if extract_label: 
        df = prom_label(df, extract_label)

    # Generate some random data using NumPy
    fig = px.bar(df, x=0, color=0, title=title)

    plottly_title=get_plotly_title_defaults()
    plottly_title.update({'text': title})
    fig.update_layout(
        title=plottly_title
    )

    st.plotly_chart(fig, use_container_width=True)
