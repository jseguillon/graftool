import streamlit as st

import utils.core as gt_core
import utils.prom as gt_prom
import utils.kubernetes as gt_k8s

def init_app():
    page_names_to_funcs = {
        "📈 prometheus": prom_dashboard,
        "kubernetes": kubernetes_dashboard
    }

    st.set_page_config(page_title="Graftool", page_icon="🧊", layout="wide", initial_sidebar_state="expanded")

    demo_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())

    time_range=gt_core.set_time_range()
    page_names_to_funcs[demo_name](time_range[0],time_range[1])

def prom_dashboard(start_datetime, end_datetime):
    st.write("# Prometheus metrics")

    col1, col2 = st.columns(2)
    with col1:
        gt_prom.line_chart(
            gt_prom.promql("process_cpu_seconds_total", start_datetime.timestamp(), end_datetime.timestamp()),
            title="process_cpu_seconds_total in range",
            extract_label="instance"
        )

    with col2:
        gt_prom.gauge_chart(
            gt_prom.promql("sum(go_memstats_frees_total)", end_datetime.timestamp()).iloc[0]/10e9,
            gt_prom.promql("sum(go_memstats_alloc_bytes_total)", end_datetime.timestamp()).iloc[0]/10e10,
            title='go mem free / total (instant at end time)',
            alarm_factor=0.9
        )

    col1, col2 = st.columns(2)
    with col1:
        gt_prom.bar_chart(
            gt_prom.promql("go_memstats_frees_total", start_datetime.timestamp()),
            title="go_memstats_frees_total (instant at start time)", 
            extract_label="instance"
        )

    with col2:
        gt_prom.bar_chart(
            gt_prom.promql("go_memstats_frees_total", end_datetime.timestamp()),
            title="go_memstats_frees_total (instant at end time)",
            extract_label="instance"        
        )

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
            gt_k8s.display_namespace_info(namespace)

init_app()
