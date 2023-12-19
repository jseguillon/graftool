import datetime
import streamlit as st

import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objs as go

import pandas as pd


def intro(d, ts, te):

    st.write("# Welcome to Graftool ! 👋")

    st.markdown(
        """
        Hello
    """
    )

def columns(d, ts, te):

    st.write("# Fake metrics")
    
    col1, col2, col3 = st.columns(3)
    
    # FIXME: use dynamic time and dates
    # FIXME: not the best way (?) => no groups in column view
    with col1:
        d_start = d[0] # numpy.datetime64
        d_end = d[1] # numpy.datetime64

        # Assuming d_start and d_end are datetime.date objects and ts, te are datetime.time objects
        d_start = datetime.date(2023, 12, 18)  # Replace with your actual start date
        d_end = datetime.date(2023, 12, 19)    # Replace with your actual end date
        ts = datetime.time(8, 45)              # Replace with your actual start time
        te = datetime.time(11, 45)             # Replace with your actual end time

        # Combine date and time into datetime.datetime
        start_datetime = datetime.datetime.combine(d_start, ts)
        end_datetime = datetime.datetime.combine(d_end, te)

        # Ensure end_datetime is after start_datetime
        if end_datetime <= start_datetime:
            end_datetime += datetime.timedelta(days=1)

        # Generate timestamps at a specified interval (e.g., every minute)
        interval = datetime.timedelta(minutes=1)  # You can change the interval
        timestamps = [start_datetime + i * interval for i in range(int((end_datetime - start_datetime) / interval))]

        # Simulate bandwidth data for 3 series
        bandwidth_series_1 = np.random.rand(len(timestamps))
        bandwidth_series_2 = np.random.rand(len(timestamps))
        bandwidth_series_3 = np.random.rand(len(timestamps))

        # Combine data
        data = np.array([timestamps, bandwidth_series_1, bandwidth_series_2, bandwidth_series_3]).T

        # Create a Plotly figure
        fig = go.Figure()

        # Add traces for each bandwidth series
        fig.add_trace(go.Scatter(x=timestamps, y=bandwidth_series_1, mode='lines', name='Series 1'))
        fig.add_trace(go.Scatter(x=timestamps, y=bandwidth_series_2, mode='lines', name='Series 2'))
        fig.add_trace(go.Scatter(x=timestamps, y=bandwidth_series_3, mode='lines', name='Series 3'))

        # Update layout
        fig.update_layout(
            title="Prometheus Bandwidth on eth0 Over Time",
            xaxis_title="Time",
            yaxis_title="Bandwidth",
            xaxis=dict(
                # If you have many timestamps, you might want to format the ticks accordingly
                tickformat='%Y-%m-%d %H:%M:%S',
                tickmode='auto',
                nticks=20
            ),
            yaxis=dict(
                range=[0, max(np.max(bandwidth_series_1), np.max(bandwidth_series_2), np.max(bandwidth_series_3)) * 1.1]  # Adjust y-axis to fit the data
            ),
            legend_title="Series"
        )

        st.plotly_chart(fig)


    with col2:
        # Add histogram data
        x1 = np.random.randn(200) - 2
        x2 = np.random.randn(200)
        x3 = np.random.randn(200) + 2

        # Group data together
        hist_data = [x1, x2, x3]

        group_labels = ['Group 1', 'Group 2', 'Group 3']

        # Create distplot with custom bin_size
        fig = ff.create_distplot(
                hist_data, group_labels, bin_size=[.1, .25, .5])

        # Plot!
        st.plotly_chart(fig, use_container_width=True)


    with col3:
        # Add histogram data
        x1 = np.random.randn(200) - 2
        x2 = np.random.randn(200)
        x3 = np.random.randn(200) + 2

        # Group data together
        hist_data = [x1, x2, x3]

        group_labels = ['Group 1', 'Group 2', 'Group 3']

        # Create distplot with custom bin_size
        fig = ff.create_distplot(
                hist_data, group_labels, bin_size=[.1, .25, .5])

        # Plot!
        st.plotly_chart(fig, use_container_width=True)


page_names_to_funcs = {
    "—": columns,
    "intro": intro
}
st.set_page_config(
    page_title="Graftool",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    }
)

demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())

today = datetime.datetime.now()
next_year = today.year + 1
jan_1 = datetime.date(next_year, 1, 1)
dec_31 = datetime.date(next_year, 12, 31)

d = st.sidebar.date_input(
    "Date range",
    (jan_1, datetime.date(next_year, 1, 7)),
    jan_1,
    dec_31,
    format="MM.DD.YYYY",
)

# TODO: set as curr date
ts = st.sidebar.time_input('Start time', datetime.time(8, 45))
te = st.sidebar.time_input('End time', datetime.time(11, 45))

page_names_to_funcs[demo_name](d, ts, te)

