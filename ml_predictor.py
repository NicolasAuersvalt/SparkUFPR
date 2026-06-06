import sqlite3
import pandas as pd
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestRegressor

DB_NAME = "crowd_sensing.db"

def treinar_e_prever():
    print("Iniciando o módulo de Machine Learning...")
    
    # 1. CONECTAR E LER O PASSADO (Preparação de Dados)
    conn = sqlite3.connect(DB_NAME)
    
    # Agrupamos os eventos por hora para o modelo entender o volume
    query = """
    SELECT 
        strftime('%Y-%m-%d %H:00:00', timestamp) as data_hora,
        COUNT(*) as volume
    FROM events
    WHERE event = 'associated'
    GROUP BY data_hora
    ORDER BY data_hora
    """
    df = pd.read_sql_query(query, conn)
    
    if len(df) < 24:
        print("Dados insuficientes para treinar o modelo. Rode o populate_history.py primeiro.")
        return

    # Converte a coluna de texto para formato de data do Pandas
    df['data_hora'] = pd.to_datetime(df['data_hora'])
    
    # 2. ENGENHARIA DE RECURSOS (Feature Engineering)
    # A IA não entende datas, ela entende números. Vamos extrair a hora e o dia da semana.
    df['hora'] = df['data_hora'].dt.hour
    df['dia_semana'] = df['data_hora'].dt.dayofweek
    
    # X são as "pistas" (hora e dia). y é a "resposta" (quantas pessoas estavam lá).
    X_treino = df[['hora', 'dia_semana']]
    y_treino = df['volume']
    
    # 3. TREINAR O MODELO (Random Forest)
    print("Treinando a Floresta Aleatória com dados históricos...")
    modelo = RandomForestRegressor(n_estimators=100, random_state=42)
    modelo.fit(X_treino, y_treino)
    
    # 4. PREVER O FUTURO (Próximas 24 horas)
    print("Prevendo as próximas 24 horas...")
    ultima_data = df['data_hora'].max()
    
    futuro_datas = [ultima_data + timedelta(hours=i) for i in range(1, 25)]
    df_futuro = pd.DataFrame({'data_hora': futuro_datas})
    
    # Extrai as mesmas pistas para o futuro
    df_futuro['hora'] = df_futuro['data_hora'].dt.hour
    df_futuro['dia_semana'] = df_futuro['data_hora'].dt.dayofweek
    
    # Pede para a IA adivinhar o volume
    X_futuro = df_futuro[['hora', 'dia_semana']]
    df_futuro['volume_previsto'] = modelo.predict(X_futuro)
    
    # Arredonda para não termos "pessoas cortadas ao meio"
    df_futuro['volume_previsto'] = df_futuro['volume_previsto'].astype(int)
    
    # 5. SALVAR NO BANCO DE DADOS
    # Cria a tabela de previsões caso não exista
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        predicted_volume INTEGER
    )
    """)
    
    # Limpa as previsões antigas para manter o banco limpo
    cursor.execute("DELETE FROM predictions")
    
    # Salva as novas previsões
    for _, linha in df_futuro.iterrows():
        cursor.execute("""
        INSERT INTO predictions (timestamp, predicted_volume)
        VALUES (?, ?)
        """, (linha['data_hora'].isoformat(), linha['volume_previsto']))
        
    conn.commit()
    conn.close()
    
    print("Sucesso! Previsões geradas e salvas na tabela 'predictions'.")

if __name__ == "__main__":
    treinar_e_prever()