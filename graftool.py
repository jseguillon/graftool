import datetime
import streamlit as st

import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objs as go

import pandas as pd
from datetime import timedelta  



def kubernetes(d, ts, te):
    st.write("# Fake kubeview")
    options = st.multiselect(
        'Namespaces',
        ['kube-system', 'kubevirt', 'mongodb', 'longhorn' ],
        [ 'kube-system', 'kubevirt' ]
    )

    if len(options) == 0:
        st.write("selected all")

    # FIXME: columns number should be options len
    style = "<style>h2 {text-align: center;}</style>"
    st.markdown(style, unsafe_allow_html=True)
    col1, col2, = st.columns(2)
    
    with col1:
        container = st.container(border=True)
        container.markdown("## kube-virt")
        container.markdown("### :red[Pods: 15]")
        container.markdown(":green[Ready: 11]")
        container.markdown(":red[CrashloopBackoff: 4]")
    with col2:
        container = st.container(border=True)
        container.markdown("## kube-system")
        container.markdown("### :green[Pods: 24]")
        container.markdown(":green[Ready: 24]")
        container.markdown(":grey[CrashloopBackoff: 0]")

def to_datetime(dt64):
    return (dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')

def do_fake_metrics(title="eth0", y_axis_title="Bandwith"):
        d_start = d[0] # numpy.datetime64
        d_end = d[1] # numpy.datetime64

        # Assuming d_start and d_end are datetime.date objects and ts, te are datetime.time objects
        d_start = datetime.date(2023, 12, 18)  # Replace with your actual start date
        d_end = datetime.date(2023, 12, 18)    # Replace with your actual end date

        d_start = pd.to_datetime(d[0])
        d_end = pd.to_datetime(d[1])
        
        # Combine date and time into datetime.datetime
        start_datetime = datetime.datetime.combine(d_start, ts)
        end_datetime = datetime.datetime.combine(d_end, te)

        # Ensure end_datetime is after start_datetime
        if end_datetime <= start_datetime:
            end_datetime += datetime.timedelta(days=1)

        # Generate timestamps at a specified interval (e.g., every minute)
        interval = datetime.timedelta(minutes=1)  # You can change the interval
        timestamps = [start_datetime + i * interval for i in range(int((end_datetime - start_datetime) / interval))]

        # Convert datetime objects to minutes since the start
        timestamps_in_minutes = [(t - start_datetime).total_seconds() / 60.0 for t in timestamps]
        timestamps_in_minutes = np.array(timestamps_in_minutes)

        # # Define a base sine wave function for simulating bandwidth
        # def sine_wave(t, amplitude=1, frequency=1, phase=0):
        #     return amplitude * np.sin(2 * np.pi * frequency * t + phase)

        bandwidth_series_1 = np.random.randint(800, 1200, size=len(timestamps))
        bandwidth_series_2 = np.random.randint(500, 1100, size=len(timestamps))
        bandwidth_series_3 = np.random.randint(900, 1300, size=len(timestamps))

        # Create a Plotly figure
        fig = go.Figure()

        # Add traces for each bandwidth series
        fig.add_trace(go.Scatter(x=timestamps, y=bandwidth_series_1, mode='lines', name='kubevirt-xyzv'))
        fig.add_trace(go.Scatter(x=timestamps, y=bandwidth_series_2, mode='lines', name='kubevirt-plpes'))
        fig.add_trace(go.Scatter(x=timestamps, y=bandwidth_series_3, mode='lines', name='kubevirt-sasas'))

        # Update layout
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title=y_axis_title,
            xaxis=dict(
                # If you have many timestamps, you might want to format the ticks accordingly
                tickformat='%Y-%m-%d %H:%M:%S',
                tickmode='auto',
                nticks=10,
                tickangle=-45
            ),
            yaxis=dict(
                range=[min(np.min(bandwidth_series_1), np.min(bandwidth_series_2), np.min(bandwidth_series_3))  , max(np.max(bandwidth_series_1), np.max(bandwidth_series_2), np.max(bandwidth_series_3)) * 1.1]  # Adjust y-axis to fit the data
            ),
            legend_title="Pod"
        )

        st.plotly_chart(fig, use_container_width=True)

def columns(d, ts, te):

    st.write("# Fake metrics")

    do_fake_metrics("Disk usage", "Gi")    
    col1, col2 = st.columns(2)
    
    with col1:
        do_fake_metrics()

    with col2:
        do_fake_metrics("Disk io", "kbps")




page_names_to_funcs = {
    "—": kubernetes,
    "metrics": columns
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
    (today, today),
    format="MM.DD.YYYY",
)

# TODO: set as curr date
ts = st.sidebar.time_input('Start time', datetime.datetime.now())
te = st.sidebar.time_input('End time', datetime.datetime.now()+timedelta(minutes=45))

page_names_to_funcs[demo_name](d, ts, te)

