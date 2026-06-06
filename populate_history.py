import sqlite3
import random
import math
from datetime import datetime, timedelta

# ==========================================
# CONFIGURAÇÕES
# ==========================================
DB_NAME = "crowd_sensing.db"
DIAS_DE_HISTORICO = 30
ROUTERS = ["router1", "router2", "router3", "router4"]

def gerar_historico():
    print(f"Injetando {DIAS_DE_HISTORICO} dias de histórico no banco de dados...")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Data final é agora. Data inicial é 30 dias atrás.
    agora = datetime.now()
    inicio = agora - timedelta(days=DIAS_DE_HISTORICO)
    
    tempo_atual = inicio
    eventos_gerados = 0
    
    while tempo_atual < agora:
        hora = tempo_atual.hour
        
        # Cria uma curva de sino simulando fluxo humano (Pico às 13h)
        # De madrugada (0h-6h) o valor fica perto de 0 ou negativo (que tratamos como 0)
        volume_base = 50 + 50 * math.sin((hora - 7) * math.pi / 12)
        
        # Adiciona um ruído aleatório para não ficar perfeito demais
        ruido = random.randint(-10, 10)
        pessoas_na_hora = max(0, int(volume_base + ruido))
        
        # Distribui essas pessoas pelos roteadores durante essa hora
        for _ in range(pessoas_na_hora):
            # Sorteia um minuto e segundo aleatório dentro desta hora
            minuto = random.randint(0, 59)
            segundo = random.randint(0, 59)
            tempo_evento = tempo_atual.replace(minute=minuto, second=segundo)
            
            # Escolhe um roteador
            router = random.choice(ROUTERS)
            
            # Gera um Device ID fictício curto apenas para histórico
            device_id = f"hist_{random.randint(1000, 9999)}"
            
            # Grava apenas a associação para a nossa previsão de lotação
            cursor.execute("""
            INSERT INTO events (timestamp, router, device_id, event)
            VALUES (?, ?, ?, ?)
            """, (tempo_evento.isoformat(), router, device_id, "associated"))
            
            eventos_gerados += 1
            
        # Avança o relógio em 1 hora
        tempo_atual += timedelta(hours=1)
        
    conn.commit()
    conn.close()
    print(f"✅ Sucesso! {eventos_gerados} eventos históricos foram criados com padrão diário.")

if __name__ == "__main__":
    gerar_historico()