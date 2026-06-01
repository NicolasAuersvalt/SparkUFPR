# SparkUFPR

Fase 1: O Simulador (Mock de Dados)

Antes de lidar com roteadores reais, você precisa de um gerador de caos controlado.

    [ ] Passo 1: Criar um script Python que gere logs Syslog falsos. Ele deve cuspir strings no formato exato que um roteador comercial usa quando alguém conecta/desconecta (ex: <14>Jan 1 00:00:00 router1 hostapd: wlan0: STA aa:bb:cc:dd:ee:ff IEEE 802.11: associated).

    [ ] Passo 2: Fazer esse script enviar esses logs via protocolo UDP para a porta 514 do localhost.

    Teste: Usar o comando nc -u -l 514 (Netcat) no seu terminal Linux para ver se as mensagens falsas estão chegando corretamente.

Fase 2: O Receptor (Ingestão)

Agora seu sistema precisa "ouvir" esses dados.

    [ ] Passo 1: Escrever um servidor UDP simples em Python (usando a biblioteca nativa socket) que fique escutando a porta 514.

    [ ] Passo 2: Aplicar expressões regulares (Regex) para extrair exatamente 3 coisas da string recebida: Timestamp, Endereço MAC e ID do Roteador/Ponto.

    [ ] Passo 3: Aplicar imediatamente uma função de hash (como hashlib.sha256) no Endereço MAC + um "salt" diário, descartando o MAC real para garantir privacidade.

    Teste: Rodar o Simulador (Fase 1) e o Receptor juntos. O console do Receptor deve imprimir apenas dicionários ou JSONs limpos e anonimizados.

Fase 3: Estrutura de Dados e Lógica (O "Cérebro")

Aqui é onde a mágica acontece. Você precisa transformar os logs soltos em um fluxo lógico.

    [ ] Passo 1: Modelar a estrutura. Uma matriz de adjacência ou uma lista de transições funciona bem para representar os caminhos entre os roteadores.

    [ ] Passo 2: Criar a lógica de tempo de permanência. Se o Hash X conectou no Roteador A às 10:00 e desconectou às 10:45, salvar o delta (45 minutos).

    [ ] Passo 3: Armazenar esses dados processados. Para não complicar no início, use um banco de dados em memória ou um SQLite. Para produção, um banco de séries temporais como o InfluxDB é o ideal.

    Teste: Injetar no sistema um MAC simulado que "pula" do Roteador 1 para o 2 e depois para o 3. Fazer uma query (consulta) no banco e confirmar se o caminho e o tempo batem com o que você simulou.

Fase 4: O Dashboard (Visualização)

Agora sim, dar vida aos dados.

    [ ] Passo 1: Escolher a ferramenta. Você tem dois caminhos rápidos:

        Opção A: Usar Grafana conectado ao seu banco de dados (zero código de interface, tudo via configuração).

        Opção B: Subir um painel rápido usando Streamlit em Python (ótimo se você quiser programar os gráficos na mão e customizar as regras de logística).

    [ ] Passo 2: Criar as 3 métricas principais:

        Um número grande com o "Total de Visitantes Ativos Agora".

        Um gráfico de barras ou velocímetro com o "Tempo Médio de Permanência".

        Um grafo direcionado (ou diagrama de Sankey) mostrando a espessura do fluxo entre os pontos A, B e C.

    Teste: Aumentar a velocidade do seu Simulador (Fase 1) para gerar 100 conexões por segundo. O Dashboard deve atualizar em tempo real sem travar.

Fase 5: O Teste de Fogo (Sua Rede Local)

Tudo funciona no mundo perfeito das simulações. Hora de ir para a realidade.

    [ ] Passo 1: Acessar o painel de administração do roteador Wi-Fi da sua casa.

    [ ] Passo 2: Procurar pela aba de "System Log", "Syslog Server" ou "Log Settings" e configurar para enviar os logs para o IP local da sua máquina de desenvolvimento (ex: 192.168.1.100), na porta UDP 514.

    [ ] Passo 3: Desligar o script Simulador da Fase 1, mas manter o Receptor da Fase 2 rodando.

    Teste Final: Pegar o seu celular, desligar o Wi-Fi e ligar novamente. Conectar e desconectar da rede. Caminhar pela casa até o sinal cair (se tiver mais de um ponto de acesso). Você deverá ver os dados reais pipocando no seu painel e os ponteiros se mexendo.
