# Mobile Crowd Sensing via Logs Wi-Fi

## 1. Objetivo

Este projeto implementa uma plataforma de Mobile Crowd Sensing baseada em eventos de associação e desassociação Wi-Fi capturados via Syslog.

O sistema permite:

* Estimar ocupação de ambientes.
* Medir tempo de permanência.
* Detectar fluxo entre pontos de acesso.
* Construir matrizes origem-destino.
* Gerar recomendações logísticas baseadas nos fluxos observados.
* Visualizar métricas em tempo real através de dashboard Streamlit.

---

# 2. Arquitetura

O sistema é composto por três módulos.

## 2.1 Syslog Generator

Responsável por simular dispositivos móveis circulando entre roteadores.

Funções:

* Geração de MACs aleatórios.
* Simulação de associação Wi-Fi.
* Simulação de dispositivos fantasmas.
* Envio dos logs para o servidor Syslog.

Saída:

```text
<14>Jun 05 12:00:00 router1 hostapd: wlan0: STA aa:bb:cc:dd:ee:ff IEEE 802.11: associated
```

---

## 2.2 Syslog Server

Responsável por:

* Receber logs UDP.
* Anonimizar dispositivos.
* Armazenar eventos.
* Calcular permanência.
* Calcular transições.
* Atualizar ocupação atual.

Tecnologias:

* Python
* Socket UDP
* SQLite

Porta utilizada:

```text
514/UDP
```

---

## 2.3 Dashboard

Painel desenvolvido em Streamlit.

Responsável por:

* Exibir KPIs.
* Exibir gráficos.
* Mostrar fluxos.
* Exibir recomendações logísticas.

Tecnologias:

* Streamlit
* Pandas
* Plotly
* SQLite


# 3. Fluxo de Dados

## Etapa 1

O simulador gera um log Syslog.

```text
Dispositivo
    ↓
Syslog Generator
```

## Etapa 2

O log é enviado via UDP.

```text
Generator
    ↓
UDP 514
    ↓
Server
```

## Etapa 3

O servidor processa:

* Timestamp
* Roteador
* MAC
* Evento

Exemplo:

```text
router2
MAC = aa:bb:cc:dd:ee:ff
associated
```

## Etapa 4

O MAC é anonimizado.

```python
sha256(MAC + salt_diário)
```

Resultado:

```text
device_id = 92d4ab...
```

Nenhum MAC real é armazenado.

## Etapa 5

O evento é persistido.

Tabela:

```sql
events
```

## Etapa 6

As sessões são monitoradas.

```text
associated
↓
disassociated
```

Calcula-se:

```text
tempo de permanência
```

Tabela:

```sql
stay_times
```

## Etapa 7

Mudanças de AP geram transições.

```text
router1 → router2
router2 → router3
```

Tabela:

```sql
transitions
```

## Etapa 8

Dispositivos ativos são mantidos.

Tabela:

```sql
active_devices
```

## Etapa 9

Dispositivos inativos são removidos após:

```text
15 minutos
```

através de:

```python
cleanup_stale_devices()
```


# 4. Estrutura do Banco de Dados

## events

Armazena todos os eventos recebidos.

| Campo     | Tipo    |
| --------- | ------- |
| id        | INTEGER |
| timestamp | TEXT    |
| router    | TEXT    |
| device_id | TEXT    |
| event     | TEXT    |

---

## stay_times

Armazena permanências concluídas.

| Campo            | Tipo    |
| ---------------- | ------- |
| id               | INTEGER |
| device_id        | TEXT    |
| router           | TEXT    |
| entry_time       | TEXT    |
| exit_time        | TEXT    |
| duration_minutes | REAL    |

---

## transitions

Armazena deslocamentos entre APs.

| Campo       | Tipo    |
| ----------- | ------- |
| id          | INTEGER |
| timestamp   | TEXT    |
| device_id   | TEXT    |
| from_router | TEXT    |
| to_router   | TEXT    |

---

## active_devices

Representa ocupação atual.

| Campo     | Tipo |
| --------- | ---- |
| device_id | TEXT |
| router    | TEXT |
| last_seen | TEXT |

---

# 5. Métricas Implementadas

## Visitantes Ativos

Consulta:

```sql
SELECT COUNT(*)
FROM active_devices
```

Representa pessoas presentes no ambiente.

---

## Permanência Média

Calculada a partir da tabela:

```sql
stay_times
```

Resultado:

```text
Tempo médio de permanência por visitante.
```

---

## Distribuição por AP

Quantidade de eventos registrados por roteador.

Permite identificar:

* Hotspots
* Regiões de maior uso

---

## Fluxos Entre APs

Obtidos da tabela:

```sql
transitions
```

Exemplo:

```text
router1 → router2 = 250
router2 → router3 = 180
router1 → router4 = 70
```

---

## Sankey Diagram

Representa visualmente:

```text
Origem → Destino
```

com espessura proporcional ao fluxo.

---

# 6. Recomendações Logísticas

O sistema identifica automaticamente os fluxos predominantes.

Exemplo:

```text
router1 → router2
```

utilizado:

```text
1250 vezes
```

Interpretação:

* Principal corredor de circulação.
* Melhor local para sinalização.
* Melhor local para publicidade.
* Melhor local para posicionamento de equipes.

Futuras versões poderão incluir:

* Menor congestionamento.
* Melhor rota por horário.
* Predição de fluxo.
* Alertas de lotação.
* Gêmeo digital do ambiente.

---

# 7. Execução

Terminal 1:

```bash
python3 syslog_generator.py
```

Terminal 2:

```bash
python3 syslog_server.py
```

Terminal 3:

```bash
streamlit run dashboard.py
```

---

# 8. Aplicações

* Campus universitários
* Shopping centers
* Aeroportos
* Estações ferroviárias
* Usinas
* Indústrias
* Centros de convenções
* Hospitais
* Eventos

---

# 9. Próximos Passos

1. Simulação realista de mobilidade.
2. Matriz origem-destino por horário.
3. Heatmap de ocupação.
4. Predição de fluxo utilizando Machine Learning.
5. Integração com InfluxDB.
6. Integração com Grafana.
7. Processamento distribuído.
8. Edge Computing.
9. Digital Twin do ambiente.
10. Recomendações logísticas baseadas em IA.
