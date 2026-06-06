import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Mobile Crowd Sensing", layout="wide", page_icon="📡")
st.title(" Mobile Crowd Sensing Dashboard")

# ==========================================
# FUNÇÕES DE ACESSO A DADOS (OTIMIZADAS)
# ==========================================
@st.cache_data(ttl=5)
def load_kpis():
    with sqlite3.connect("crowd_sensing.db") as conn:
        ativos = pd.read_sql("SELECT COUNT(*) as count FROM active_devices", conn).iloc[0]['count']
        unicos = pd.read_sql("SELECT COUNT(DISTINCT device_id) as count FROM events", conn).iloc[0]['count']
        transicoes = pd.read_sql("SELECT COUNT(*) as count FROM transitions", conn).iloc[0]['count']
        
        tempo_medio_df = pd.read_sql("SELECT AVG(duration_minutes) as media FROM stay_times", conn)
        tempo_medio = round(tempo_medio_df.iloc[0]['media'], 2) if pd.notna(tempo_medio_df.iloc[0]['media']) else 0.0
        
        return ativos, unicos, transicoes, tempo_medio

@st.cache_data(ttl=5)
def load_transitions():
    with sqlite3.connect("crowd_sensing.db") as conn:
        return pd.read_sql("""
            SELECT from_router, to_router, COUNT(*) as count 
            FROM transitions 
            GROUP BY from_router, to_router 
            ORDER BY count DESC
        """, conn)

@st.cache_data(ttl=5)
def load_router_stats():
    with sqlite3.connect("crowd_sensing.db") as conn:
        dist = pd.read_sql("SELECT router, COUNT(*) as eventos FROM events GROUP BY router", conn)
        perm = pd.read_sql("SELECT router, AVG(duration_minutes) as tempo_medio FROM stay_times GROUP BY router", conn)
        return dist, perm

@st.cache_data(ttl=5)
def load_recent_events():
    with sqlite3.connect("crowd_sensing.db") as conn:
        return pd.read_sql("SELECT * FROM events ORDER BY timestamp DESC LIMIT 50", conn)

@st.cache_data(ttl=15)
def load_ml_predictions():
    try:
        with sqlite3.connect("crowd_sensing.db") as conn:
            # Puxa o histórico real (Últimas 24h)
            historico = pd.read_sql("""
                SELECT strftime('%Y-%m-%d %H:00:00', timestamp) as data_hora, COUNT(*) as volume
                FROM events
                WHERE event = 'associated'
                GROUP BY data_hora
                ORDER BY data_hora DESC LIMIT 24
            """, conn).sort_values('data_hora')
            
            # Puxa as previsões da IA (Próximas 24h)
            previsao = pd.read_sql("""
                SELECT timestamp as data_hora, predicted_volume as volume
                FROM predictions
                ORDER BY data_hora ASC
            """, conn)
            
            return historico, previsao
    except sqlite3.OperationalError:
        # Retorna vazio se a tabela predictions ainda não existir
        return pd.DataFrame(), pd.DataFrame()

# ==========================================
# CARREGAMENTO DOS DADOS
# ==========================================
ativos, unicos, transicoes, tempo_medio = load_kpis()
df_transitions = load_transitions()
df_dist, df_perm = load_router_stats()
df_events = load_recent_events()
df_hist, df_pred = load_ml_predictions()

# ==========================================
# INTERFACE DE USUÁRIO (UI)
# ==========================================

col_title, col_btn = st.columns([8, 1])
with col_btn:
    if st.button(" Atualizar"):
        st.cache_data.clear()

# --- KPIs ---
st.markdown("### Indicadores Principais")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Visitas Ativas (Agora)", ativos)
kpi2.metric("Dispositivos Únicos", unicos)
kpi3.metric("Tempo Médio (min)", tempo_medio)
kpi4.metric("Total de Transições", transicoes)

st.divider()

# --- Organização em Abas ---
tab1, tab2, tab3, tab4 = st.tabs([
    " Visão Geral", 
    " Fluxo e Mobilidade", 
    " Inteligência Artificial", 
    " Logs Recentes"
])

with tab1:
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Eventos por Roteador")
        if not df_dist.empty:
            st.bar_chart(df_dist.set_index("router"))
        else:
            st.info("Aguardando dados...")

    with colB:
        st.subheader("Permanência Média (min)")
        if not df_perm.empty:
            st.bar_chart(df_perm.set_index("router"))
        else:
            st.info("Aguardando fechamento de sessões...")

with tab2:
    if not df_transitions.empty:
        best_route = df_transitions.iloc[0]
        st.success(
            f" **Recomendação Logística:** O fluxo predominante é **{best_route['from_router']} → {best_route['to_router']}** "
            f"(Utilizado {best_route['count']} vezes). Considere este o principal corredor para sinalização ou publicidade."
        )
        
        col_sankey, col_table = st.columns([2, 1])
        with col_table:
            st.subheader("Top Transições")
            st.dataframe(df_transitions, use_container_width=True, hide_index=True)
            
        with col_sankey:
            st.subheader("Diagrama de Mobilidade")
            routers = sorted(list(set(df_transitions["from_router"]).union(set(df_transitions["to_router"]))))
            router_map = {router: idx for idx, router in enumerate(routers)}
            
            fig = go.Figure(go.Sankey(
                node=dict(label=routers, pad=15, thickness=20, color="blue"),
                link=dict(
                    source=[router_map[r] for r in df_transitions["from_router"]],
                    target=[router_map[r] for r in df_transitions["to_router"]],
                    value=df_transitions["count"].tolist()
                )
            ))
            fig.update_layout(margin=dict(l=0, r=0, t=10, b=10), height=400)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Nenhuma transição registrada ainda.")

with tab3:
    st.subheader("Predição de Lotação (Próximas 24h)")
    
    if not df_pred.empty and not df_hist.empty:
        # Gráfico combinando Passado (Real) e Futuro (Previsto)
        fig_ml = go.Figure()
        
        # Linha do Histórico
        fig_ml.add_trace(go.Scatter(
            x=df_hist['data_hora'], y=df_hist['volume'],
            mode='lines+markers', name='Fluxo Observado',
            line=dict(color='#1f77b4', width=3)
        ))
        
        # Linha da Previsão
        fig_ml.add_trace(go.Scatter(
            x=df_pred['data_hora'], y=df_pred['volume'],
            mode='lines+markers', name='Previsão (Machine Learning)',
            line=dict(color='#ff7f0e', width=3, dash='dot')
        ))
        
        fig_ml.update_layout(
            xaxis_title="Data e Hora",
            yaxis_title="Volume de Dispositivos",
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig_ml, use_container_width=True)
        
        # Informação extra sobre o pico
        pico = df_pred.loc[df_pred['volume'].idxmax()]
        st.info(f" **Alerta de Pico:** A maior movimentação esperada será em **{pico['data_hora']}** com cerca de **{pico['volume']} dispositivos**.")
        
    else:
        st.warning(" Os dados de previsão ainda não estão disponíveis. Certifique-se de ter rodado o script `ml_predictor.py`.")

with tab4:
    st.subheader("Últimos 50 Eventos")
    st.dataframe(df_events, use_container_width=True, hide_index=True)