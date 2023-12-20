import datetime
import requests
import streamlit as st

import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objs as go

import pandas as pd
from datetime import timedelta  
from kubernetes import client, config


def get_pod_status(namespace):
    config.load_kube_config()  # or load_incluster_config() if running inside a cluster
    v1 = client.CoreV1Api()
    pod_list = v1.list_namespaced_pod(namespace)
    status_count = {'Ready': 0, 'CrashloopBackoff': 0, 'CreateContainerError': 0, 'Total': 0}

    for pod in pod_list.items:
        status_count['Total'] += 1
        if any([cs.state.waiting and cs.state.waiting.reason == 'CrashLoopBackOff' for cs in pod.status.container_statuses]):
            status_count['CrashloopBackoff'] += 1
        if any([cs.state.waiting and cs.state.waiting.reason == 'CreateContainerError' for cs in pod.status.container_statuses]):
            status_count['CreateContainerError'] += 1
        elif pod.status.phase == 'Running':
            status_count['Ready'] += 1

    return status_count

def display_namespace_info(namespace):
    status = get_pod_status(namespace)
    container = st.container(border=True)
    style = "<style>h2 {text-align: center;}</style>"
    st.markdown(style, unsafe_allow_html=True)
    has_error = (status['CrashloopBackoff'] != 0) or (status['CreateContainerError'] != 0)

    container.markdown(f"## {namespace}")
    pods_text = f" Pods: {status['Total']}"
    if has_error: 
        pods_text = f":red[{pods_text}]"
    else: 
        pods_text = f":green[{pods_text}]"
    container.markdown(f"### {pods_text}")
    container.markdown(f"Ready: {status['Ready']}")
    container.markdown(f"CrashloopBackoff: {status['CrashloopBackoff']}")
    create_error_text = f"CreateContainerError: {status['CreateContainerError']}"
    if has_error: 
        create_error_text = f":red[{create_error_text}]"
    container.markdown(f"{create_error_text}")

def kubernetes_dashboard(d, ts, te):
    st.write("# Kubernetes Dashboard")
    options = st.multiselect(
        'Namespaces',
        ['kube-system', 'monitoring', 'default'],
        ['kube-system', 'monitoring']
    )

    if len(options) == 0:
        st.write("Selected all")

    cols = st.columns(len(options))
    for i, namespace in enumerate(options):
        with cols[i]:
            display_namespace_info(namespace)

def to_datetime(dt64):
    return (dt64 - np.datetime64('1970-01-01T00:00:00Z')) / np.timedelta64(1, 's')

def do_fake_metrics(prometheus_query, start_time, end_time, title):
    # Replace with your Prometheus server URL
    prometheus_server = 'http://localhost:9090'

    # Construct the full URL for the query
    # TODO: is 60s best value, should it be configurable
    query_url = f"{prometheus_server}/api/v1/query_range?query={prometheus_query}&start={start_time}&end={end_time}&step=60s"

    # Perform the query
    response = requests.get(query_url)
    data = response.json()
    # st.write(query_url)
    # st.write(response)
    # Check if the response is successful
    if data['status'] != 'success':
        raise Exception("Query failed")

    # Parse the response
    results = data['data']['result']

    # Convert the results into a DataFrame
    timestamps = []
    values = []

    # Parse the response
    results = data['data']['result']

    # Create a Plotly figure
    fig = go.Figure()

    metrics = []
    # Loop through each metric and add a separate trace
    for result in results:
        if  result['metric'].get('pod', None) != None:
            pod_name = result['metric'].get('pod', 'unknown_pod')  # Get the pod name, default to 'unknown_pod' if not present
            timestamps = [datetime.datetime.fromtimestamp(float(value[0])) for value in result['values']]
            values = [float(value[1]) for value in result['values']]
            values = [float(value[1]) for value in result['values']]
            metric = result['metric']
            metrics.append(metric)
            fig.add_trace(go.Scatter(x=timestamps, y=values, mode='lines', name=pod_name))

    # Update layout
    fig.update_layout(
        title=title,
        xaxis_title="Time",
        yaxis_title="CPU Usage",
        xaxis=dict(
            tickformat='%Y-%m-%d %H:%M:%S',
            tickmode='auto',
            nticks=10,
            tickangle=-45
        )
    )

    # Display the figure in Streamlit
    st.plotly_chart(fig, use_container_width=True)

    # st.dataframe(metrics)
def columns(d, ts, te):

    st.write("# Real metrics")

    d_start = d[0] # numpy.datetime64
    d_end = d[1] # numpy.datetime64

    d_start = pd.to_datetime(d[0])
    d_end = pd.to_datetime(d[1])
    
    # Combine date and time into datetime.datetime
    start_datetime = datetime.datetime.combine(d_start, ts)
    end_datetime = datetime.datetime.combine(d_end, te)

    do_fake_metrics("container_cpu_usage_seconds_total", start_datetime.timestamp(), end_datetime.timestamp(), title="CPU Usage Over Time")
    col1, col2 = st.columns(2)

    with col1:
        do_fake_metrics("container_memory_usage_bytes", start_datetime.timestamp(), end_datetime.timestamp(), title="Memory")
    
    with col2:
        do_fake_metrics("container_cpu_system_seconds_total", start_datetime.timestamp(), end_datetime.timestamp(), title="Cpu system") 




page_names_to_funcs = {
    "—": kubernetes_dashboard,
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
ts = st.sidebar.time_input('Start time', key='start_time')
te = st.sidebar.time_input('End time', datetime.datetime.now()+timedelta(minutes=45), key='end_time')

page_names_to_funcs[demo_name](d, ts, te)

