
import streamlit as st
import plotly.graph_objs as go

from kubernetes import client, config

# TODO: @record_replay
def get_pods(namespace):
    try:
        config.load_kube_config()  # or load_incluster_config() if running inside a cluster
        v1 = client.CoreV1Api()
    
        pod_list = v1.list_namespaced_pod(namespace)
        return pod_list
    except:
        st.error("Oh no, Streamlit can't reach any Kubernetes cluster. Maybe your running online demo ?")

def count_status(pod_list):
    pods_status = []
    if pod_list is None:
        return

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

    if pod_data == None: 
        return

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
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
            legend=dict(
            orientation="h"
        )
    )

    return fig

def display_namespace_info(namespace):
    pods_status = count_status(get_pods(namespace))

    container1 = st.container(border=True)
    style = "<style>h2 {text-align: center;}</style>"

    with container1:
        st.markdown(style, unsafe_allow_html=True)
        st.markdown(f"## {namespace}")

        if pods_status is not None: 
            st.plotly_chart(kube_pie(pods_status), use_container_width=True)

            with st.expander("Pods with errors", expanded=True ):
                for pod in pods_status:
                        pod_name = pod['name']
                        non_ready_statuses = {k: v for k, v in pod['statuses'].items() if k != 'Ready' or v < 1}

                        if non_ready_statuses:  # Only show expander if there are non-ready statuses
                            
                                status_text = ", ".join([f"{key} = {value}" for key, value in non_ready_statuses.items()])
                                st.write(f":red[{pod_name}: {status_text}]")
