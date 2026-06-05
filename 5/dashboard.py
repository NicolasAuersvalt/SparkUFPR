import sqlite3
import pandas as pd
import streamlit as st
import plotly.graph_objects as go

@st.cache_resource
def start_background_services():
    st.toast("Iniciando serviços Syslog em background...", icon="⚙️")
    
    # Inicia o Servidor e o Gerador usando subprocess
    server_process = subprocess.Popen(["python", "syslog_server.py"])
    
    # Dá 2 segundos para o servidor abrir a porta antes do gerador começar
    time.sleep(2) 
    
    generator_process = subprocess.Popen(["python", "syslog_generator.py"])
    
    # Garante que os processos sejam mortos se o Streamlit for desligado
    def cleanup():
        server_process.kill()
        generator_process.kill()
        
    atexit.register(cleanup)
    
    return True

# Chama a função. O Streamlit garante que ela só roda na primeira vez.
_ = start_background_services()

# ==========================================
# CONFIGURAÇÃO DA PÁGINA
# ==========================================
st.set_page_config(page_title="Mobile Crowd Sensing", layout="wide", page_icon="📡")
st.title("📡 Mobile Crowd Sensing Dashboard")

# ==========================================
# FUNÇÕES DE ACESSO A DADOS (OTIMIZADAS)
# ==========================================
# O cache expira a cada 5 segundos (ttl=5), aliviando o banco de dados
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

# ==========================================
# CARREGAMENTO DOS DADOS
# ==========================================
ativos, unicos, transicoes, tempo_medio = load_kpis()
df_transitions = load_transitions()
df_dist, df_perm = load_router_stats()
df_events = load_recent_events()

# ==========================================
# INTERFACE DE USUÁRIO (UI)
# ==========================================

# Botão de atualização manual no topo
col_title, col_btn = st.columns([8, 1])
with col_btn:
    st.button("🔄 Atualizar Agora")

# --- KPIs ---
st.markdown("### 📊 Indicadores Principais")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Visitas Ativas (Agora)", ativos)
kpi2.metric("Dispositivos Únicos", unicos)
kpi3.metric("Tempo Médio (min)", tempo_medio)
kpi4.metric("Total de Transições", transicoes)

st.divider()

# --- Organização em Abas (Tabs) ---
tab1, tab2, tab3 = st.tabs(["📍 Visão Geral", "🚶‍♂️ Fluxo e Mobilidade", "📝 Logs Recentes"])

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
        # Recomendação Logística Dinâmica
        best_route = df_transitions.iloc[0]
        st.success(
            f"💡 **Recomendação Logística:** O fluxo predominante é **{best_route['from_router']} → {best_route['to_router']}** "
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
        st.info("Nenhuma transição registrada ainda. Aguarde a movimentação dos dispositivos.")

with tab3:
    st.subheader("Últimos 50 Eventos")
    st.dataframe(df_events, use_container_width=True, hide_index=True)