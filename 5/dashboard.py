import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

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

transitions = pd.read_sql_query(
    "SELECT * FROM transitions",
    conn
)

associated = events[
    events["event"] == "associated"
]["device_id"].nunique()

disassociated = events[
    events["event"] == "disassociated"
]["device_id"].nunique()

ativos = max(
    associated - disassociated,
    0
)

# =====================
# KPIs
# =====================

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Ativos Agora",
        ativos
    )

with col2:
    st.metric(
        "Dispositivos Únicos",
        events["device_id"].nunique()
    )

with col3:

    permanencia_media = 0

    if not stay_times.empty:

        permanencia_media = round(
            stay_times[
                "duration_minutes"
            ].mean(),
            2
        )

    st.metric(
        "Tempo Médio (min)",
        permanencia_media
    )

with col4:

    st.metric(
        "Transições",
        len(transitions)
    )



st.subheader(
    "Fluxo Entre Roteadores"
)

if not transitions.empty:

    flows = (
        transitions
        .groupby(
            [
                "from_router",
                "to_router"
            ]
        )
        .size()
        .reset_index(name="fluxo")
        .sort_values(
            "fluxo",
            ascending=False
        )
    )

    st.dataframe(
        flows,
        width="stretch"
    )

st.subheader(
    "Top Fluxos"
)

if not transitions.empty:

    top_flows = (
        transitions
        .groupby(
            [
                "from_router",
                "to_router"
            ]
        )
        .size()
        .reset_index(name="fluxo")
        .sort_values(
            "fluxo",
            ascending=False
        )
        .head(10)
    )

st.subheader(
    "Fluxo de Mobilidade (Sankey)"
)

if not transitions.empty:

    sankey_data = (
        transitions
        .groupby(
            [
                "from_router",
                "to_router"
            ]
        )
        .size()
        .reset_index(name="count")
    )

    routers = sorted(
        list(
            set(
                sankey_data["from_router"]
            ).union(
                set(
                    sankey_data["to_router"]
                )
            )
        )
    )

    router_map = {
        router: idx
        for idx, router
        in enumerate(routers)
    }

    source = [
        router_map[r]
        for r in sankey_data["from_router"]
    ]

    target = [
        router_map[r]
        for r in sankey_data["to_router"]
    ]

    value = sankey_data[
        "count"
    ].tolist()

    fig = go.Figure(
        go.Sankey(
            node=dict(
                label=routers,
                pad=15,
                thickness=20
            ),
            link=dict(
                source=source,
                target=target,
                value=value
            )
        )
    )

    st.plotly_chart(
        fig,
        width="stretch"
    )


st.subheader(
    "Recomendação Logística"
)

if not transitions.empty:

    best_route = (
        transitions
        .groupby(
            [
                "from_router",
                "to_router"
            ]
        )
        .size()
        .reset_index(name="count")
        .sort_values(
            "count",
            ascending=False
        )
        .iloc[0]
    )

    st.success(
        f"""
        Fluxo predominante:

        {best_route['from_router']}
        →
        {best_route['to_router']}

        Utilizado {best_route['count']} vezes.
        """
    )

# =====================
# Ocupação por AP
# =====================

st.subheader("Distribuição por Roteador")

router_counts = (
    events
    .groupby("router")
    .size()
    .reset_index(name="eventos")
)

st.bar_chart(
    router_counts.set_index("router")
)

# =====================
# Permanência por AP
# =====================

if not stay_times.empty:

    st.subheader(
        "Tempo Médio de Permanência"
    )

    stay_router = (
        stay_times
        .groupby("router")
        ["duration_minutes"]
        .mean()
    )

    st.bar_chart(stay_router)

# =====================
# Últimos Eventos
# =====================

st.subheader("Últimos Eventos")

st.dataframe(
    events.tail(50),
    width="stretch"
)