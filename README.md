# GoodWe HEMS-EV

Gerenciador inteligente de energia residencial com carregamento de veículo elétrico e marketplace de energia entre vizinhos, desenvolvido para o GoodWe EV Challenge 2026 (FIAP).

## Estado do projeto

Em desenvolvimento. Este documento descreve a arquitetura e o comportamento previstos do sistema. A seção "Resultados" será preenchida com dados do sistema implementado.

## Equipe

| Nome | RM |
|---|---|
| Davi Ramos | 571744 |
| Lucas Galle Melchior | 574027 |
| Victor Hugo Ferreira Freire | 571099 |
| Gabriel Cavaloti | 571643 |

## 1. Visão geral

O HEMS-EV (Home Energy Management System com carregamento de veículo elétrico) decide, em intervalos regulares, para onde vai cada quilowatt de energia em uma casa com painel solar fotovoltaico, bateria, carregador de veículo elétrico e ligação com a rede elétrica.

O sistema tem três partes:

1. **Simulador.** Gera os dados que um inversor híbrido GoodWe, uma bateria GoodWe Lynx e um carregador GoodWe HCA G2 enviariam. O projeto não usa hardware real.
2. **Motor de decisão.** Prevê a geração solar e o consumo da casa e escolhe, a cada passo de simulação, entre quatro destinos para a energia: casa, bateria, carro ou rede.
3. **Marketplace.** Casas simuladas com excedente solar vendem energia para carros elétricos de outras casas simuladas, a um preço entre o valor pago pela energia exportada à rede e o preço da energia comprada da rede.

O resultado apresentado é a comparação entre o mesmo dia simulado sem o sistema inteligente e com ele, em custo (R$), energia importada da rede (kWh), autoconsumo solar (%) e emissões de CO2 (kg).

### 1.1 Como o sistema decide

Uma casa com painel solar, bateria e carro elétrico tem quatro pontos de troca de energia:

- **Painel solar:** produz durante o dia.
- **Bateria:** guarda energia para uso posterior.
- **Carro elétrico:** precisa estar carregado até um horário definido pelo usuário.
- **Rede elétrica:** fornece energia quando falta e recebe o excedente.

A cada passo, o sistema responde: com a energia disponível agora, para onde enviá-la? Exemplo de um dia:

- 10h, muito sol e consumo baixo: o excedente carrega o carro, em vez de ser vendido à rede.
- 15h, carro e bateria cheios: o excedente é oferecido no marketplace; sem comprador, vai para a rede.
- 19h, sem sol e consumo alto: a bateria alimenta a casa, evitando comprar energia no horário de tarifa mais alta.
- O usuário precisa do carro com 80% de carga às 7h: o sistema planeja a noite para cumprir esse objetivo usando a bateria e a energia mais barata da rede.

## 2. Alinhamento aos requisitos do desafio

| Requisito do desafio | Como o projeto atende |
|---|---|
| Geração, armazenamento e uso de energia renovável com monitoramento inteligente | Simulação de geração solar, bateria e carga com monitoramento em tempo real no dashboard |
| Tecnologias compatíveis com a GoodWe | Simulador modelado sobre inversor híbrido ET G2, baterias Lynx F G2 e carregador HCA G2; adaptador com a mesma interface de dados da biblioteca de comunicação local `goodwe` (seção 7) |
| Algoritmos inteligentes | Previsão de geração e consumo; planejamento de carga pelo horário de saída do carro; despacho de energia por prioridade |
| Análise de impactos: eficiência, pegada de carbono, relevância social ou ambiental | Comparação entre cenário sem e com otimização em kWh importados, autoconsumo, custo e CO2 |
| Interface amigável e visualização de dados | Dashboard com fluxo de energia, gráficos de geração, consumo e estado de carga |
| Integração com assistente virtual | Integração com a ARIA (Assistente de Recarga Inteligente e Autônoma) |
| Conexão com os conteúdos da disciplina | Ver seção 9 |

## 3. Arquitetura

### 3.1 Fluxo de dados

```
Simulador (casa, inversor ET G2, bateria Lynx F G2, carregador HCA G2)
        |
        v
Adaptador (interface única: modo "simulado" ou modo "goodwe-local")
        |
        v
Backend Node.js/TypeScript  <---->  Redis (estado em tempo real)
        |                           MySQL (histórico e livro-razão do marketplace)
        v
Motor de decisão (Python): previsão + despacho
        |
        +--> Dashboard (fluxo de energia, comparativo antes/depois)
        +--> ARIA (consultas e comandos em linguagem natural)
        +--> Marketplace (ofertas e ordens entre casas simuladas)
```

### 3.2 Tecnologias

| Camada | Tecnologia | Função |
|---|---|---|
| Simulador | Python | Gerar dados de casa, inversor, bateria e carregador |
| Motor de decisão e previsão | Python | Previsão e despacho de energia |
| Backend | Node.js com TypeScript | API e orquestração |
| Estado em tempo real | Redis | Leitura rápida do estado atual de cada casa |
| Histórico e livro-razão | MySQL | Consultas por período e registro das negociações |
| Contêineres | Docker e Docker Compose | Subir todos os serviços com um comando |
| Interface | Página web | Dashboard |

### 3.3 Estrutura do repositório

```
goodwe-hems-ev/
  README.md
  CONTEXT.md       contexto do projeto: enunciado, decisões, plano e pontos em aberto
  docs/            diagramas de arquitetura e capturas de tela do sistema
  simulator/       simulador de casa, inversor, bateria e carregador
  adapter/         interface única simulado/goodwe-local
  backend/         API Node.js/TypeScript
  engine/          previsão e motor de decisão
  marketplace/     ofertas, ordens e casamento
  dashboard/       interface web
  scripts/         extração e preparo de dados externos (tarifa da ANEEL, radiação do INMET, consumo da ECD-UY)
  dados/
    brutos/        arquivos baixados das fontes públicas; não versionados (.gitignore)
    processados/   perfis e classificação de dias gerados pelos scripts; versionados
  docker-compose.yml
```

### 3.4 Ciclo de execução

O backend não gera dados de simulação. Os dados são gerados pelo simulador. O backend recebe as leituras, armazena, aciona o motor de decisão e o marketplace e serve os dados ao dashboard e à ARIA.

O sistema avança em passos de 15 minutos simulados (96 passos por dia simulado). Em cada passo:

1. O simulador calcula as leituras de todas as casas para o mesmo instante (geração solar, carga, SOC da bateria e SOC do carro) e as envia à API com `POST /readings`.
2. O backend grava o estado atual de cada casa no Redis e a leitura no MySQL.
3. O backend chama o motor de decisão, que prevê geração e consumo e aplica as regras da seção 5.1 a cada casa.
4. O backend executa o marketplace (seção 6) com as ofertas e ordens geradas pelas casas no passo.
5. A resposta de `POST /readings` devolve ao simulador um comando por casa (seção 4.2).
6. O simulador aplica os comandos, atualiza o SOC da bateria e do carro e inicia o passo seguinte.

```
Simulador --(leituras)--> API --> Motor de decisão --> Marketplace
    ^                                                       |
    |_____________(comandos na resposta do POST)____________|
```

O simulador só avança para o passo seguinte depois de receber os comandos do passo atual. Dessa forma, a decisão do motor altera o estado simulado.

### 3.5 Modos de execução

| Modo | Intervalo entre passos | Uso |
|---|---|---|
| Lote | Nenhum; limitado pelo tempo de processamento | Gerar os números do comparativo sem e com otimização (seção 10) |
| Tempo acelerado | Configurável no simulador; valor inicial de 1 segundo por passo, o que equivale a 96 segundos por dia simulado | Dashboard ao vivo e gravação do vídeo de demonstração |

### 3.6 API do backend

A API usa HTTP com corpo em JSON.

| Método | Rota | Quem chama | Descrição |
|---|---|---|---|
| POST | `/readings` | Simulador | Recebe a lista de leituras de todas as casas de um passo (objetos no formato da seção 4.1, com o mesmo `timestamp`) e responde com a lista de comandos (seção 4.2) |
| GET | `/houses/:id/state` | Dashboard, ARIA | Último estado da casa, lido do Redis |
| GET | `/houses/:id/history` | Dashboard | Leituras da casa em um período, lidas do MySQL (parâmetros `from` e `to`) |
| GET | `/houses/:id/decision` | Dashboard, ARIA | Última decisão do motor para a casa e o motivo |
| PUT | `/houses/:id/ev` | Dashboard, ARIA | Define o SOC alvo e a hora de saída do carro |
| GET | `/comparison` | Dashboard | Métricas dos cenários sem e com otimização (seção 5.4) |
| GET | `/market/offers` | Dashboard | Ofertas abertas no marketplace |
| GET | `/market/orders` | Dashboard | Ordens de compra abertas no marketplace |
| GET | `/market/trades` | Dashboard | Negociações realizadas |
| GET | `/summary/today` | ARIA, dashboard | Resumo do dia simulado em curso: economia em R$, energia importada da rede em kWh e CO2 evitado em kg |

## 4. Simulador

O simulador representa uma ou mais casas. Cada casa tem:

- **Painel solar:** potência gerada ao longo do dia, com curva de sol (nascer, pico, pôr do sol) e variação por nuvens.
- **Carga da casa:** consumo base com picos de manhã e à noite.
- **Bateria:** capacidade em kWh, potência máxima de carga e descarga em kW, estado de carga (SOC) em porcentagem.
- **Carregador EV:** potência máxima em kW, carro conectado ou não, SOC do carro, SOC alvo e hora de saída.
- **Rede:** potência importada ou exportada em kW.

Os parâmetros numéricos de cada casa estão na seção 4.3.

### 4.1 Formato dos dados

Cada leitura é um objeto JSON:

```json
{
  "house_id": "casa-01",
  "timestamp": "2026-10-11T10:00:00-03:00",
  "pv_power_kw": 4.2,
  "load_power_kw": 0.9,
  "battery": { "soc_percent": 62.0, "power_kw": -1.5 },
  "ev": {
    "connected": true,
    "soc_percent": 35.0,
    "capacity_kwh": 60.0,
    "target_soc_percent": 80.0,
    "departure_time": "07:00",
    "charge_power_kw": 1.8
  },
  "grid_power_kw": 0.0
}
```

Convenções: potências em kW; `battery.power_kw` positivo indica descarga e negativo indica carga; `grid_power_kw` positivo indica importação e negativo indica exportação. Os nomes dos campos seguem, sempre que possível, os sensores expostos pela biblioteca `goodwe`, para que a troca do simulador por um inversor real não exija reescrever o restante do sistema.

### 4.2 Comando enviado ao simulador

Para cada casa, a resposta de `POST /readings` traz um comando:

```json
{
  "house_id": "casa-01",
  "timestamp": "2026-10-11T10:00:00-03:00",
  "ev_charge_power_kw": 1.8,
  "battery_power_kw": -1.5,
  "market": { "sold_kwh": 0.0, "bought_kwh": 0.0 },
  "reason": "excedente solar direcionado ao carro e à bateria"
}
```

- `ev_charge_power_kw`: potência ordenada ao carregador, em kW.
- `battery_power_kw`: potência ordenada à bateria, com a mesma convenção da seção 4.1 (positivo descarrega, negativo carrega).
- `market.sold_kwh` e `market.bought_kwh`: energia vendida e comprada no marketplace no passo, em kWh (potência em kW multiplicada por 0,25 h).
- `reason`: texto curto com a regra aplicada. É exibido no dashboard e usado pela ARIA para explicar a decisão.

A potência trocada com a rede não é comandada: ela resulta do balanço de energia da casa. No exemplo, 4,2 kW de geração menos 0,9 kW de carga da casa deixam 3,3 kW, que são consumidos pelo carro (1,8 kW) e pela bateria (1,5 kW), e a troca com a rede é 0 kW. O comando de um passo vale para o passo seguinte.

### 4.3 Parâmetros de simulação

Os valores abaixo definem a primeira versão do simulador. A coluna Origem indica se o valor vem de especificação GoodWe confirmada em fonte pública (seção 12) ou se é uma premissa de simulação, ajustável. Os perfis de geração solar e de consumo são construídos a partir de dados públicos, descritos na seção 4.4. Enquanto os dados não forem processados, o simulador usa as curvas sintéticas das premissas abaixo.

| Parâmetro | Valor | Origem |
|---|---|---|
| Passo de simulação | 15 minutos | Premissa |
| Carregador EV | GW7K-HCA-20 (linha HCA G2), potência máxima de 7 kW | Especificação GoodWe |
| Eficiência do carregador | 100% (perdas ignoradas) | Premissa |
| Capacidade da bateria do carro | 60 kWh | Premissa |
| Bateria residencial | Lynx F G2, módulos de 3,2 kWh | Especificação GoodWe |
| Potência máxima de carga e de descarga da bateria | Potência nominal da torre Lynx F G2 da ficha técnica, de 2,24 kW por módulo (4,48 kW com 2 módulos; 8,96 kW com 4 módulos), limitada à potência nominal do inversor | Especificação GoodWe; o limite pelo inversor é premissa |
| Eficiência de carga e de descarga da bateria | 95% cada (rendimento de ida e volta de 90,25%) | Premissa |
| SOC mínimo e máximo da bateria | 10% e 100% | Premissa |
| Inversor | ET G2, de 6 a 15 kW nominais (6, 8, 10, 12 e 15 kW) | Especificação GoodWe |
| Painel solar | Potência em kWp por casa; fator de desempenho do sistema de 0,80 | Premissa (a GoodWe não fabrica painéis) |
| Curva de geração | Seno entre 06:00 e 18:00, com pico às 12:00, multiplicado pelo fator de clima do dia | Premissa |
| Fator de clima | Ensolarado 1,0; parcialmente nublado 0,6, com variação de 20% por passo; chuvoso 0,25 | Premissa |
| Carga da casa | Perfil por faixa horária (tabela abaixo), com variação de 10% por passo | Premissa |

Perfil de carga da casa (15,0 kWh por dia):

| Faixa horária | Potência |
|---|---|
| 00:00 a 06:00 | 0,3 kW |
| 06:00 a 09:00 | 0,8 kW |
| 09:00 a 17:00 | 0,5 kW |
| 17:00 a 22:00 | 1,2 kW |
| 22:00 a 23:59 | 0,4 kW |

Casas da demonstração inicial:

| Casa | Painel | Inversor | Bateria | Carro |
|---|---|---|---|---|
| casa-01 | 6,0 kWp | ET G2 de 6 kW | 12,8 kWh (4 módulos) | Em casa das 18:00 às 07:00; chega com SOC de 30%; meta de 80% às 07:00 |
| casa-02 | 4,0 kWp | ET G2 de 6 kW | 6,4 kWh (2 módulos) | Em casa das 09:00 às 17:00; chega com SOC de 40%; meta de 80% às 17:00 |
| casa-03 | 8,0 kWp | ET G2 de 8 kW | 12,8 kWh (4 módulos) | Sem carro; atua como vendedora de excedente |

Os perfis exercitam os três comportamentos do sistema: a casa-01 planeja a carga noturna com bateria e tarifa por horário; a casa-02, em dias nublados, precisa de mais energia do que o próprio painel produz e compra no marketplace; a casa-03 produz mais do que consome e vende. As casas 04 a 10 serão definidas na ampliação do escopo, repetindo estes perfis com variações de painel e bateria.

### 4.4 Dados públicos de geração e consumo

Os perfis de geração solar e de consumo vêm de bases públicas, para que a previsão do motor (seção 5.2) seja avaliada sobre dados que o simulador não gerou. Se a previsão fosse treinada sobre curvas sintéticas do próprio simulador, o erro ficaria artificialmente baixo.

| Dado | Fonte | Detalhes |
|---|---|---|
| Geração solar | INMET, estação automática A701 (São Paulo - Mirante de Santana), dados históricos horários | Radiação global em kJ/m2 por hora, em UTC, arquivos anuais em https://portal.inmet.gov.br/dadoshistoricos |
| Consumo residencial | ECD-UY (detailed household electricity consumption dataset of Uruguay), subconjunto THC (consumo total do domicílio) | 110.953 domicílios, de 2019-01-01 a 2020-11-03; intervalo de amostragem do subconjunto a confirmar nos arquivos |

Tratamento da radiação solar (`scripts/preparar_geracao_inmet.py`):

1. Lê os arquivos da estação A701 (.CSV ou .zip) em `dados/brutos/inmet/`; separador ";", codificação latin-1, vírgula decimal; valores iguais ou abaixo de -9990 são tratados como ausentes.
2. Converte o horário de UTC para o horário local (UTC-3).
3. Converte radiação acumulada na hora (kJ/m2) em irradiância média da hora (kW/m2), dividindo por 3600.
4. Grava `dados/processados/perfil_solar_sp.csv` (colunas `timestamp_local` e `irradiancia_kw_m2`). A geração de cada casa em um passo é a irradiância multiplicada pelo kWp da casa e pelo fator de desempenho de 0,80 (seção 4.3).
5. Classifica cada dia com pelo menos 22 horas válidas, pela razão entre sua irradiação diária (kWh/m2) e o percentil 90 dos dias válidos: ensolarado (razão de 0,75 ou mais), parcialmente nublado (de 0,35 a menos de 0,75) e chuvoso (abaixo de 0,35). Resultado em `dados/processados/dias_sp_classificados.csv`, que alimenta os cenários de teste.
6. Lista, por classe, os dias mais recentes que têm 7 dias válidos anteriores, que servem de histórico para a previsão.

Tratamento do consumo (ECD-UY): o script ainda não existe. O plano é calcular o perfil médio por passo de 15 minutos (reamostrando, se o intervalo original for outro) para dia útil e para fim de semana e normalizá-lo para o consumo diário de cada casa (15,0 kWh na casa de referência da seção 4.3).

Limitações dos dados: a radiação é medida em um único ponto da cidade; o consumo vem de domicílios uruguaios, com hábitos e clima diferentes dos brasileiros, e por isso só o formato da curva diária é aproveitado, não os valores absolutos. A origem uruguaia está declarada na seção 11.

## 5. Motor de decisão

### 5.1 Regras de despacho

A cada passo de simulação (15 minutos), o motor aplica estas prioridades:

1. Cobrir a carga da casa com a geração solar.
2. Garantir o objetivo do carro. A energia necessária é (SOC alvo menos SOC atual) multiplicado pela capacidade da bateria do carro. A partir da potência do carregador, o motor calcula o horário limite para iniciar a carga. Ao atingir esse horário, o carro carrega mesmo sem excedente solar, com energia da bateria ou da rede.
3. Direcionar o excedente solar, nesta ordem: carro (até a potência do carregador), bateria (até a potência máxima de carga), marketplace, rede.
4. Descarregar a bateria para a casa nos horários de tarifa mais alta, mantendo reserva para o objetivo do carro.

### 5.2 Previsão

Modelo simples de geração e consumo por hora do dia. O erro é medido com o erro médio absoluto (MAE, em kW) e informado na seção de resultados.

### 5.3 Tarifas e emissões

- **Tarifa:** a referência é a tarifa branca, que cobra preços diferentes por horário para consumidores de baixa tensão. A distribuidora de referência é a Enel SP. Em dias úteis, os postos horários são: ponta das 17:30 às 20:30; intermediário das 16:30 às 17:30 e das 20:30 às 21:30; fora de ponta nas demais horas. Aos fins de semana e feriados nacionais, vale fora de ponta o dia todo. Os valores em R$/kWh são a soma da TE e da TUSD de cada posto na modalidade Branca, extraídas do conjunto de dados "Tarifas de aplicação das distribuidoras de energia elétrica" da ANEEL. Os valores vigentes, consultados em 12/10/2026, estão na tabela abaixo.
- **Fator de emissão de CO2 da rede elétrica brasileira:** fator médio mensal do Sistema Interligado Nacional publicado pelo MCTI na plataforma SIRENE, em kg CO2/MWh, dividido por 1000 para obter kg CO2/kWh. O valor adotado, o período de referência e a data da consulta são registrados nesta seção.

Tarifa branca residencial (subgrupo B1) da Enel SP, sem tributos, em vigor de 04/07/2026 a 03/07/2027. No arquivo da ANEEL, a distribuidora aparece com a sigla ELETROPAULO.

| Posto | TUSD (R$/MWh) | TE (R$/MWh) | Total (R$/MWh) | Total (R$/kWh) |
|---|---|---|---|---|
| Fora ponta | 367,33 | 301,91 | 669,24 | 0,6692 |
| Intermediário | 682,59 | 301,91 | 984,50 | 0,9845 |
| Ponta | 997,85 | 482,45 | 1480,30 | 1,4803 |

O simulador usa esses valores sem tributos (ICMS e PIS/COFINS não são incluídos). Em reais, os resultados ficam abaixo dos de uma conta real. Fonte: conjunto de dados "Tarifas de aplicação das distribuidoras de energia elétrica", ANEEL, extraído com `scripts/extrair_tarifa_enel_sp.py`.

### 5.4 Cenários comparados

| Cenário | Comportamento |
|---|---|
| Sem otimização | O carro carrega na potência máxima assim que conectado; a bateria opera apenas em autoconsumo simples; sem previsão e sem marketplace |
| Com otimização | Regras da seção 5.1, previsão e marketplace ativos |

Os dois cenários rodam sobre o mesmo dia simulado, com a mesma semente aleatória.

## 6. Marketplace de energia entre vizinhos

Casas com excedente solar que o próprio carro e a própria bateria não absorvem vendem essa energia a carros elétricos de outras casas simuladas que precisam carregar.

- **Vendedor:** casa com excedente solar maior que zero depois de atender a carga da casa, o carro e a bateria (seção 5.1). Publica uma oferta com quantidade em kWh e preço em R$/kWh.
- **Comprador:** carro conectado em outra casa, com necessidade de carga não atendida. Publica uma ordem com quantidade e preço máximo.
- **Faixa de preço:** entre o valor pago ao vendedor pela energia exportada à rede (piso) e o preço da energia comprada da rede (teto). Nessa faixa, o vendedor recebe mais que na rede e o comprador paga menos que na rede.
- **Casamento:** ofertas e ordens são ordenadas por preço, e a negociação ocorre quando o preço da oferta é menor ou igual ao preço máximo da ordem.
- **Registro:** cada negociação gera uma linha no MySQL com casa vendedora, casa compradora, kWh, preço e horário.

A demonstração começa com 3 casas (seção 4.3) e é ampliada até 10 casas.

A implementação inicial está em `marketplace/matching.py`: preço médio entre o valor de oportunidade da exportação e a tarifa do comprador, prioridade por preço e desempate por casa. Uma casa não pode comprar e vender no mesmo passo. Essa regra de preço é uma proposta; o valor de exportação e a integração com o motor ainda estão pendentes.

## 7. Tecnologias GoodWe e integração

### 7.1 Equipamentos de referência

| Equipamento | Características confirmadas em fontes públicas | Uso no projeto |
|---|---|---|
| Carregador EV série HCA (GW7K-HCA, GW11K-HCA, GW22K-HCA) | Carregador AC com carga por excedente solar, compatível com inversores solares e híbridos GoodWe; variantes monofásica de 7 kW e trifásicas de 11 kW e 22 kW; conexão Wi-Fi com o sistema GoodWe; acompanhamento no SEMS e no aplicativo | Geração anterior da linha; o simulador usa a HCA G2 (linha seguinte) |
| Carregador EV série HCA G2 (GW7K-HCA-20, GW11K-HCA-20, GW22K-HCA-20) | Carregador AC de 7, 11 e 22 kW com função de troca de fases (phase switching) para maximizar o uso de energia solar; carga totalmente solar ou complemento rápido da rede, com modos configuráveis no aplicativo GoodWe SEMS+; comunicação por Bluetooth, Wi-Fi, LAN e RS485; proteção IP66 | Modelo de carregador simulado: GW7K-HCA-20 (7 kW) |
| Inversor híbrido ET G2 | Trifásico de alta tensão, de 6 a 15 kW, com medidor inteligente embutido, compatível com a bateria Lynx F G2 | Referência para o inversor simulado |
| Baterias Lynx Home (F e D) | A série Lynx Home F é compatível com inversores ET e EH (híbridos) e BH e BT (de bateria) | Referência para a bateria simulada |
| Bateria Lynx F G2 | Módulo LX F3.2-20 de 3,2 kWh; de 2 a 9 módulos por torre, de 6,4 a 28,8 kWh de energia utilizável; potência nominal da torre de 4,48 kW (2 módulos) a 20,16 kW (9 módulos); tecnologia LFP; compatível com inversores BH, EH, BT e ET | Bateria simulada (seção 4.3) |

O carregador HCA G2 já realiza carga por excedente solar por conta própria. O diferencial do HEMS-EV está na camada acima dele: previsão, planejamento pelo horário de saída do carro, uso de tarifa por horário e marketplace.

### 7.2 Interfaces de comunicação

| Interface | Descrição | Situação no projeto |
|---|---|---|
| SEMS Portal Open API (nuvem) | API HTTPS da GoodWe com 31 interfaces em 4 grupos (usina, dispositivo, controle remoto, data logger); entrega dados brutos e dados de negócio processados pela plataforma SEMS | Exige conta organizacional e solicitação à GoodWe. O grupo não possui credencial, e a API não é utilizada na versão simulada |
| Protocolo local do inversor | A biblioteca Python de código aberto `goodwe` lê dados pela rede local por UDP na porta 8899, ou por Modbus/TCP na porta 502 com o dongle LAN+WiFi V2.0 (modelo WLA0000-01-00P), nas famílias ET, EH, BT, BH, ES, EM, BP, DT, MS, D-NS e XS | Protocolo mapeado pela comunidade, não documentado oficialmente pela GoodWe. Relatos da comunidade indicam que firmwares recentes de algumas linhas usam DTLS na porta 8899. É a interface de referência do adaptador |

### 7.3 Estratégia de integração

O adaptador expõe uma interface única, com duas implementações previstas: `simulado` e `goodwe-local`. Nesta entrega, apenas `simulado` é implementada; `goodwe-local` é o caminho previsto para um inversor real e não é validada contra hardware. O simulador produz os mesmos sensores que a biblioteca `goodwe` entrega. Assim, substituir o simulador por um inversor real não exige alterar o motor de decisão, o backend nem o dashboard.

## 8. Dashboard e assistente virtual

### 8.1 Dashboard

- Diagrama do fluxo de energia em tempo real entre painel, bateria, carro, casa e rede.
- Gráfico de geração e consumo do dia.
- Gráficos do SOC da bateria e do carro.
- Painel comparativo sem e com otimização: custo, kWh importados da rede, autoconsumo e CO2.
- Lista das negociações do marketplace.

### 8.2 Assistente ARIA

A ARIA (Assistente de Recarga Inteligente e Autônoma) responde a perguntas como "quanto economizei hoje?" e aceita comandos como "deixe o carro pronto às 7h", consultando o backend por API HTTP. Ela usa os endpoints `GET /summary/today`, `GET /houses/:id/state`, `GET /houses/:id/decision` e `PUT /houses/:id/ev`, descritos na seção 3.6.

## 9. Alinhamento à disciplina

O projeto se conecta às disciplinas Pensamento Computacional e Automação com Python e Soluções em Energias Renováveis e Sustentáveis.

### 9.1 Pensamento Computacional e Automação com Python

| Conceito | Aplicação no projeto |
|---|---|
| Decomposição | O problema é dividido em simulador, adaptador, backend, motor de decisão, marketplace, dashboard e assistente |
| Reconhecimento de padrões | A previsão usa o padrão diário de geração solar e de consumo, hora a hora |
| Abstração | Cada casa é modelada por um balanço de energia a cada passo de 15 minutos, sem os detalhes elétricos internos do inversor |
| Algoritmos | Regras de prioridade do despacho (seção 5.1), cálculo do horário limite de carga do carro e casamento de ordens de compra e ofertas por preço (seção 6) |
| Automação | Execução em lote dos cenários sem e com otimização, geração automática das métricas e do comparativo, ciclo de simulação sem intervenção manual (seção 3.4) |
| Python | Linguagem do simulador e do motor de decisão |

### 9.2 Soluções em Energias Renováveis e Sustentáveis

| Conceito | Aplicação no projeto |
|---|---|
| Geração fotovoltaica | Curva de geração por casa, definida em kWp (seção 4.3) |
| Armazenamento de energia | Bateria Lynx F G2 simulada, com SOC, limites de potência e eficiência (seção 4.3) |
| Mobilidade elétrica | Carga do veículo com excedente solar pelo carregador HCA G2 e planejamento pelo horário de saída |
| Autoconsumo e eficiência | Métricas de autoconsumo solar e de energia importada da rede (seção 10) |
| Tarifa por horário | Tarifa branca como referência para decidir quando carregar e quando descarregar a bateria (seção 5.3) |
| Redução de emissões | Cálculo de CO2 evitado entre os cenários sem e com otimização (seção 5.3) |

## 10. Resultados

A preencher com dados gerados pelo sistema implementado:

- Tabela comparativa dos cenários sem e com otimização: custo (R$), energia importada da rede (kWh), autoconsumo solar (%), emissões de CO2 (kg) e porcentagem de dias em que o carro atingiu o SOC alvo na hora de saída.
- Erro da previsão (métrica e valor).
- Resumo do marketplace: número de negociações, kWh negociados e preço médio.
- Capturas de tela do dashboard e diagramas do sistema implementado.

## 11. Avaliação crítica e limitações

- Os resultados são obtidos por simulação, não por medição em campo.
- Sistemas de gestão de energia residencial já existem. As contribuições do projeto são a combinação de previsão, reserva de bateria pelo horário de saída do carro, comparativo de CO2, marketplace entre vizinhos e assistente em linguagem natural.
- O perfil de consumo vem de domicílios do Uruguai (ECD-UY), não do Brasil. A curva diária é usada como forma do consumo, escalada para o consumo diário de cada casa simulada; hábitos de consumo e clima do Uruguai diferem dos de São Paulo. A radiação solar, ao contrário, é medida em São Paulo (INMET, estação A701).
- A venda direta de energia entre particulares está sujeita à regulação do setor elétrico brasileiro. O marketplace é tratado como simulação acadêmica.
- A integração com a SEMS Open API depende de credencial fornecida pela GoodWe. A versão atual usa o adaptador simulado.
- As tarifas usadas são as publicadas pela ANEEL, sem tributos. Os valores em reais são menores que os de uma conta de energia real.
- O fator de emissão de CO2 da rede elétrica brasileira é baixo: o MCTI publicou valores mensais entre 21,5 e 28,9 kg CO2/MWh nos primeiros meses de 2025. Por isso, a redução de CO2 em kg é pequena em comparação com a economia em reais. Esse resultado reflete a matriz elétrica brasileira, em que fontes limpas responderam por 88,2% da oferta interna de energia elétrica em 2024, segundo a EPE, e não uma falha do sistema.

## 12. Referências

- GoodWe, API introduction: https://community.goodwe.com/solution/API%20introduction
- Biblioteca Python goodwe (PyPI): https://pypi.org/project/goodwe/0.4.6/
- GoodWe, HCA Series: https://en.goodwe.com/hca-series
- pv magazine, GoodWe lança carregador EV solar residencial: https://www.pv-magazine.com/press-releases/goodwe-launches-solar-powered-smart-ev-charger-for-residential-use-2/
- Krannich, EV Charger GW 7K-HCA: https://shop.krannich-solar.com/de-en/e-mobility/charging-stations/42618/ev-charger-gw-7k-hca
- pv magazine Australia, ET G2: https://www.pv-magazine-australia.com/2024/12/13/goodwe-releases-three-phase-high-voltage-hybrid-inverter-in-australia
- Solartraders, Lynx Home F: https://www.solartraders.com/en/products/batteries/bms-modules/goodwe-lynx-home-f-hv-pcu
- Home Assistant Community, GW6000-ES-20 e DTLS: https://community.home-assistant.io/t/goodwe-gw6000-es-20-read-real-time-pv-production-locally-python-no-cloud/1016056
- Sun.store, GoodWe GW7K-HCA-20 (HCA G2): https://sun.store/en/product/goodwe-gw7k-hca-20-50534
- Krannich, EV Charger GW 7K-HCA G2: https://shop.krannich-solar.com/de-en/e-mobility/ac-charging-stations/71716/ev-charger-gw-7k-hca-g2
- GoodWe, Lynx F G2 Series: https://en.goodwe.com/lynxf-g2-series
- GoodWe, Lynx F G2 Series datasheet: https://solarproof.com.au/datasheets/battery_datasheet_GW_Lynx-F-G2_Datasheet-EN.pdf
- GoodWe, ET G2 hybrid inverter: https://en.goodwe.com/goodwe-introduces-et-g2-hybrid-inverter-to-power-modern-homes-winner-of-the-reddot-design-award
- ANEEL, Tarifas de aplicação das distribuidoras de energia elétrica (dados abertos): https://dadosabertos.aneel.gov.br/dataset/tarifas-distribuidoras-energia-eletrica
- INMET, dados históricos (estação A701): https://portal.inmet.gov.br/dadoshistoricos
- ECD-UY, detailed household electricity consumption dataset of Uruguay (artigo): https://www.ncbi.nlm.nih.gov/pmc/articles/PMC8776758/
- ECD-UY, dados (Springer Nature, figshare): https://springernature.figshare.com/collections/ECD-UY_Detailed_household_electricity_consumption_dataset_of_Uruguay/5428608
- Idec, tarifa branca (horários em São Paulo): https://idec.org.br/node/26342
- MCTI, nota técnica sobre os fatores de emissão do SIN (jun/2025): https://cenarioenergia.com.br/wp-content/uploads/2025/06/NT_FE_jun25.pdf
- Canal Solar, emissões de CO2 da geração elétrica (MCTI e EPE): https://canalsolar.com.br/emissoes-de-co%e2%82%82-geracao-eletrica-mcti/

## 13. Testes

Testado com Python 3.12, sem dependências externas para os módulos novos:

```sh
python -m unittest discover -s tests -v
```

Os testes cobrem o marketplace e `engine/validation.py`, que verifica balanço de potência, SOC, limites de potência, EV desconectado e compra/venda simultânea. O validador recebe leituras do mesmo intervalo de 15 minutos e o modelo de troca: `ideal_microgrid` inclui a energia interna no balanço; `financial_only` considera apenas o fluxo físico da rede.

Ainda faltam testes integrados com simulador e backend, evolução temporal do SOC e cumprimento do prazo de carga do carro.
