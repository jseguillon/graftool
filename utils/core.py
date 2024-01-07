import streamlit as st 
import pandas as pd
import datetime
from datetime import timedelta

def set_time_range():
    today = datetime.datetime.now()

    ds = st.sidebar.date_input("Start date", today-timedelta(hours=24), key='start_date')
    ts = st.sidebar.time_input('Start time', today-timedelta(hours=1), key='start_time', step=60)

    de = st.sidebar.date_input("End date", today, key='end_date')
    te = st.sidebar.time_input('End time', today, key='end_time', step=60)

    d_start = ds # numpy.datetime64
    d_end = de # numpy.datetime64

    d_start = pd.to_datetime(ds)
    d_start = pd.to_datetime(d_start, unit='ms')
    d_end = pd.to_datetime(de)
    
    # Combine date and time into datetime.datetime
    start_datetime = datetime.datetime.combine(d_start, ts)
    end_datetime = datetime.datetime.combine(d_end, te)

    return [start_datetime, end_datetime]
        
