# dashboard.py

import sqlite3
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Mobile Crowd Sensing",
    layout="wide"
)

st.title("Mobile Crowd Sensing Dashboard")

conn = sqlite3.connect("crowd_sensing.db")

events = pd.read_sql_query(
    "SELECT * FROM events",
    conn
)

stay_times = pd.read_sql_query(
    "SELECT * FROM stay_times",
    conn
)

st.metric(
    "Eventos",
    len(events)
)

st.metric(
    "Permanências",
    len(stay_times)
)

st.dataframe(events.tail(20))