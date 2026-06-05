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
