# TODO: add some debug flag
# TODO: add minimalisics unit test
# TODO: create or find State timeline plus  Time series
# streamlit-heatmap-chart
# streamlit-chart-card

# (https://medium.com/quiq-blog/using-plotly-timelines-to-visualize-thread-activity-c135bb17880)

import datetime
import requests
import streamlit as st
import json
import numpy as np
import plotly.figure_factory as ff
import plotly.graph_objs as go
import plotly.express as px
import urllib.parse

import pandas as pd
from datetime import timedelta  
from kubernetes import client, config

def get_pods(namespace):
    config.load_kube_config()  # or load_incluster_config() if running inside a cluster
    v1 = client.CoreV1Api()
    pod_list = v1.list_namespaced_pod(namespace)
    return pod_list

def count_status(pod_list):
    pods_status = []

    for pod in pod_list.items:
        pod_status = {'name': pod.metadata.name, 'statuses': {}}
        # Check each container status in the pod
        for cs in pod.status.container_statuses:
            # If the container is waiting and has a reason, count that reason
            if cs.state.waiting and cs.state.waiting.reason:
                reason = cs.state.waiting.reason
                pod_status['statuses'].setdefault(reason, 0)
                pod_status['statuses'][reason] += 1
            # If the container is running, count it as 'Ready'
            elif cs.state.running:
                pod_status['statuses'].setdefault('Ready', 0)
                pod_status['statuses']['Ready'] += 1

        pods_status.append(pod_status)

    return pods_status

def all_containers_ready(container_statuses):
    return all(status.ready for status in container_statuses)

import plotly.graph_objects as go
import streamlit as st

def get_color_gradient(start_color, end_color, n):
    """Generate a color gradient between two colors."""
    if n <= 1:
        return [start_color] if n == 1 else []

    colors = []
    for i in range(n):
        intermediate_color = [start_color[j] + (float(i) / (n - 1)) * (end_color[j] - start_color[j]) for j in range(3)]
        colors.append('rgb({},{},{})'.format(int(intermediate_color[0]), int(intermediate_color[1]), int(intermediate_color[2])))
    return colors

def kube_pie(pod_data):
    status_counts = {'Ready': 0, 'Completed': 0}
    other_statuses = {}

    # Extracting and counting statuses
    for pod in pod_data:
        for status, count in pod['statuses'].items():
            if status in ['Ready', 'Completed']:
                status_counts[status] += count
            else:
                other_statuses[status] = other_statuses.get(status, 0) + count

    # Preparing data for the pie chart
    labels = list(status_counts.keys())
    values = list(status_counts.values())

    # Color settings
    colors = ['green', 'grey', 'red']

    # Handling other statuses
    if other_statuses:
        labels += list(other_statuses.keys())
        values += list(other_statuses.values())
        other_colors = get_color_gradient([255, 165, 0], [255, 0, 0], len(other_statuses))
        colors += other_colors

    # Creating the pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.3, marker_colors=colors)])
    # fig.update_layout(title_text='Pods Container Statuses')

    return fig

def display_namespace_info(namespace):
    pods_status = count_status(get_pods(namespace))

    container1 = st.container(border=True)
    style = "<style>h2 {text-align: center;}</style>"
    with container1:
        st.markdown(style, unsafe_allow_html=True)
        st.markdown(f"## {namespace}")

        total_pods = len(pods_status)
        total_ready = sum(pod['statuses'].get('Ready', 0) for pod in pods_status)
        total_crashloop = sum(pod['statuses'].get('CrashloopBackoff', 0) for pod in pods_status)
        total_create_error = sum(pod['statuses'].get('CreateContainerError', 0) for pod in pods_status)
        has_error = total_crashloop != 0 or total_create_error != 0

        pods_text = f" Pods: {total_pods}"
        col1, col2 = st.columns(2)
        with col1:
            pods_text = f":red[{pods_text}]" if has_error else f":green[{pods_text}]"
            st.markdown(f"### {pods_text}")

            st.markdown(f"#### Containers")
            st.markdown(f"Ready: {total_ready}")
            st.markdown(f"CrashloopBackoff: {total_crashloop}")
            create_error_text = f"CreateContainerError: {total_create_error}"
            create_error_text = f":red[{create_error_text}]" if has_error else f"{create_error_text}"
            st.markdown(create_error_text)
        with col2:
            st.plotly_chart(kube_pie(pods_status), use_container_width=True)

    for pod in pods_status:
            pod_name = pod['name']
            non_ready_statuses = {k: v for k, v in pod['statuses'].items() if k != 'Ready' or v < 1}

            if non_ready_statuses:  # Only show expander if there are non-ready statuses
                with st.expander("Pods with errors", expanded=True ):
                    status_text = ", ".join([f"{key} = {value}" for key, value in non_ready_statuses.items()])
                    st.write(f":red[{pod_name}: {status_text}]")

# TODO: take promql as jinja templates plus vars
# TODO: also return pandaframe to users ?
# TODO: test and make use of @st.cache_data and other 
def promql(prometheus_query, start_time=None, end_time=None):
    # Replace with your Prometheus server URL
    prometheus_server = 'http://localhost:9090'

    # Construct the full URL for the query
    query_url = f"{prometheus_server}/api/v1"
    
    prometheus_query = urllib.parse.quote(prometheus_query)
    if end_time != None:
        # TODO: is 60s best value? should it be configurable
        query_url = f"{query_url}/query_range?query={prometheus_query}&start={start_time}&end={end_time}&step=60s"
    else: 
        query_url = f"{query_url}/query?query={prometheus_query}&time={start_time}"

    # Perform the query
    response = requests.get(query_url)
    data = response.json()
    if data['status'] != 'success':
        raise Exception("Query failed")

    return data

#FIXME: allow full customisation of update layout
#FIXME: ensure data missing creates empty zones in the graph
def line_chart(data, title):
    # Parse the response
    results = data['data']['result']

    # Convert the results into a DataFrame
    timestamps = []
    values = []

    # Parse the response
    results = data['data']['result']

    # Create a Plotly figure
    fig = go.Figure()

    # st.expander(st.dataframe(pd.DataFrame({"first column": results}), use_container_width=True))
    metrics = []
    # Loop through each metric and add a separate trace
    for result in results:
        if  result['metric'].get('pod', None) != None:
            pod_name = result['metric'].get('pod', 'unknown_pod')  # Get the pod name, default to 'unknown_pod' if not present
            timestamps = [datetime.datetime.fromtimestamp(float(value[0])) for value in result['values']]
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


# FIXME: use real datas
def gauge_chart(a, b, title=""):
    value = int(a['data']['result'][0]['value'][1])
    total = int(b['data']['result'][0]['value'][1])
    fig = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = int(a['data']['result'][0]['value'][1]),
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': title, 'font': {'size': 24} },
    gauge = {
        'axis': {'range': [None, total], 'tickwidth': 1, 'tickcolor': "darkblue"},
        'bgcolor': "red",
        'borderwidth': 2,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, total*0.7], 'color': 'green'},
            {'range': [250, total*0.9], 'color': 'orange'}],
        'threshold': {
            'line': {'color': "black", 'width': 4},
            'thickness': 0.75,
            'value': value
            }}))

    fig.update_layout( font = {'color': "green", 'family': "Arial"})

    st.plotly_chart(fig, use_container_width=True)

def bar_chart(data, title):
    result_list = []
    for entry in data['data']['result']:
        pod_name = entry['metric'].get('pod', None)
        if pod_name != None:
            value_1 = int(entry['value'][1])
            # FIXME: check real calculation !!!!!!!
            result_list.append({'pod_name': pod_name, 'value_1': value_1/(1024*1024)/2})

    # FIXME: those sums operations should be either in promql or panda
    result_dict = {}
    for entry in result_list:
        pod_name = entry['pod_name']
        value_1 = int(entry['value_1'])
        
        if pod_name in result_dict:
            result_dict[pod_name] += value_1
        else:
            result_dict[pod_name] = value_1

    # Creating a Pandas DataFrame from the list of dictionaries
    df = pd.DataFrame({'pod_name': list(result_dict.keys()), 'Mi': list(result_dict.values())})

    # Generate some random data using NumPy
    fig = px.bar(df, x='pod_name', y='Mi', title='Container Memory Usage')

    st.plotly_chart(fig, use_container_width=True)

def init_app():
    page_names_to_funcs = {
        "—": kubernetes_dashboard,
        "metrics": prom_dashboard
    }

    st.set_page_config(
        page_title="Graftool",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
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
    te = st.sidebar.time_input('End time', datetime.datetime.now()+timedelta(minutes=15), key='end_time')
    # TODO: set all paramters as "app_config" (global? classes?) var
    # TODO: make "T-5mns" "T-10mns" "T-15mns"


    d_start = d[0] # numpy.datetime64
    d_end = d[1] # numpy.datetime64

    d_start = pd.to_datetime(d[0])
    d_start = pd.to_datetime(d_start, unit='ms')
    d_end = pd.to_datetime(d[1])
    
    # Combine date and time into datetime.datetime
    start_datetime = datetime.datetime.combine(d_start, ts)
    end_datetime = datetime.datetime.combine(d_end, te)

    page_names_to_funcs[demo_name](start_datetime, end_datetime)

def kubernetes_dashboard(start_datetime, end_datetime):
    st.write("# Kubernetes Dashboard")
    options = st.multiselect(
        'Namespaces',
        ['kube-system', 'monitoring', 'default'],
        ['kube-system']
    )

    if len(options) == 0:
        st.write("Selected all")

    cols = st.columns(len(options))
    for i, namespace in enumerate(options):
        with cols[i]:
            display_namespace_info(namespace)

# FIXME: make some union operator for prom metrics
# FIXME: default to template
def prom_dashboard(start_datetime, end_datetime):
    st.write("# Prometheus metrics")

    col1, col2 = st.columns(2)
    with col1:
        line_chart(
            promql("container_cpu_usage_seconds_total", start_datetime.timestamp(), end_datetime.timestamp()), 
            title="CPU Usage Over Time"
        )

    with col2:
        bar_chart(
            promql("container_memory_usage_bytes", start_datetime.timestamp()),
            title="container_memory_usage_bytes"
        )

    col1, col2 = st.columns(2)
    with col1:
        gauge_chart(
            promql("kubelet_running_pods", start_datetime.timestamp()), 
            promql("kube_node_status_capacity{resource=\"pods\"}", start_datetime.timestamp()),
            'Pods Capacity'
        )

    with col2:
        line_chart(
            promql("container_cpu_system_seconds_total", start_datetime.timestamp(), end_datetime.timestamp()), 
            title="Cpu system"
        )

init_app()
