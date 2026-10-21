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
  engine/          previsão e motor de decisão (serviço HTTP em service.py, imagem em Dockerfile)
  marketplace/     ofertas, ordens e casamento
  dashboard/       interface web (index.html) e servidor que a entrega e repassa /api/* ao backend (server.py, Dockerfile)
  tests/           testes automatizados (unittest) do marketplace e da validação de leituras
  scripts/         extração e preparo de dados externos (tarifa da ANEEL, radiação do INMET, consumo da ECD-UY)
  dados/
    brutos/        arquivos baixados das fontes públicas (aneel/, inmet/); não versionados (.gitignore)
    processados/   perfis e classificação de dias gerados pelos scripts; versionados
  docker-compose.yml
  .env.example     variáveis de ambiente (copiar para .env e trocar as senhas; o .env não é versionado)
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

O backend em `backend/` implementa essas rotas e `GET /health`. Use `X-Simulation-Id` para separar execuções (padrão: `default`). Cada lote deve manter as mesmas casas, com avanço de 15 minutos. Reenviar um lote idêntico devolve a resposta salva; mudar um passo já recebido ou pular intervalos retorna 409. Datas exigem fuso. Histórico e negociações aceitam `from`, `to` e `limit` (padrão 1000, máximo 1000), em ordem crescente; o intervalo máximo é 31 dias, com últimas 24 horas como padrão.

`PUT /houses/:id/ev` recebe `{"target_soc_percent":80,"departure_time":"07:00"}` e salva a meta para o próximo passo. Casa sem carro informa capacidade zero, `connected: false`, carga zero e `departure_time: null`. O estado usa Redis com recuperação pelo MySQL. Leituras, decisões e negociações são gravadas na mesma transação; as decisões ficam no JSON de `steps`. As metas ficam em `ev_targets`, o comparativo em `comparisons` e as chaves do Redis seguem `hems:<simulation>:house:<id>:state`.

Contrato do serviço do motor (detalhado na seção 3.8): com `ENGINE_MODE=http`, o backend envia `POST /decide` ao `ENGINE_URL`, com `{readings, ev_targets, export_value_per_kwh, optimized}`. As leituras já incluem as metas salvas. A resposta deve conter `{commands, trades, offers, orders}`; os tipos estão em `backend/src/types.ts`. Os comandos usam o timestamp recebido e controlam o próximo intervalo; negociações pertencem ao intervalo recebido (`financial_only`). Falha ou resposta inválida do motor retorna 502 sem gravar o passo. Em `ENGINE_MODE=neutral`, os comandos têm potências zeradas e não há negociações.

`GET /comparison` importa o JSON definido em `COMPARISON_FILE` e guarda a última versão válida de cada simulação no MySQL. O formato mínimo para a exportação do comparador é:

```json
{
  "simulation_id": "default",
  "period": {"from": "2026-10-20T00:00:00-03:00", "to": "2026-10-21T00:00:00-03:00"},
  "baseline": {"cost": 20, "import_kwh": 30},
  "optimized": {"cost": 15, "import_kwh": 20}
}
```

Esses números são apenas exemplo do formato. O período tem início inclusivo e fim exclusivo. Sem arquivo válido ou versão salva, a rota retorna 503. O resumo usa o dia da última leitura em São Paulo; economia e CO2 evitado exigem comparativo desse mesmo dia. Sem premissas configuradas, custo líquido e emissões retornam `null`.

### 3.7 Limitações conhecidas da API

- `PUT /houses/:id/ev` grava a meta e o backend a aplica à leitura enviada ao motor, mas o simulador ainda não adota a nova meta: o carro continua saindo no horário do simulador, e `/houses/:id/state` devolve a meta original. A correção prevista é um campo opcional `ev_target` no comando, aplicado pelo simulador.
- O comparativo gerado por `scripts/comparar_cenarios.py --json` cobre todo o período simulado, a partir das 07:00. Por isso `savings` e `co2_avoided_kg` de `GET /summary/today` ficam `null`, já que exigem um comparativo de exatamente o dia local corrente.
- A API não tem CORS. Um dashboard servido em outra porta não consegue chamá-la; o dashboard deve ser servido pelo próprio backend ou o CORS deve ser habilitado.

### 3.8 Contrato entre o backend e o motor

O serviço do motor está em `engine/service.py`. O corpo da requisição de `POST {ENGINE_URL}/decide`:

```json
{
  "readings": [ { "house_id": "casa-01", "...": "leitura no formato da seção 4.1, com a meta do PUT /ev já aplicada" } ],
  "ev_targets": { "casa-01": { "target_soc_percent": 90, "departure_time": "07:30" } },
  "export_value_per_kwh": 0.0,
  "optimized": true
}
```

A resposta traz `commands` (um por casa, formato da seção 4.2, com `market.sold_kwh` e `market.bought_kwh` iguais à soma das negociações da casa), `trades` (`seller_id`, `buyer_id`, `quantity_kwh`, `price_per_kwh`), `offers` (`house_id`, `quantity_kwh`, `export_value_per_kwh`) e `orders` (`house_id`, `quantity_kwh`, `grid_price_per_kwh`). O backend rejeita qualquer resposta fora desse formato (502).

O motor valida cada leitura com `engine/validation.py` (balanço de potência, SOC e limites). A potência máxima da bateria vem de `simulator/config.py` pelo `house_id`, porque a leitura não a informa; uma casa que não está no `simulator/config.py` recebe 422, e leitura malformada recebe 400. Com `optimized: false`, o motor não monta ofertas nem ordens. O mesmo `optimized` e o valor de exportação vêm das variáveis `SIM_OPTIMIZATION` e `EXPORT_VALUE_PER_KWH` do backend; esta última é obrigatória em `ENGINE_MODE=http` e, enquanto o ponto 17 do CONTEXT.md está em aberto, usa-se `0` como premissa.

### 3.9 Como executar o sistema

1. Copie `.env.example` para `.env`, troque `MYSQL_PASSWORD` e `MYSQL_ROOT_PASSWORD` e defina `ENGINE_MODE=http` e `EXPORT_VALUE_PER_KWH=0`.
2. Gere o comparativo que o `/comparison` vai ler (use os mesmos parâmetros da simulação): `python scripts/comparar_cenarios.py --dias 3 --inicio 2026-01-05 --json dados/processados/comparison.json --simulacao demo`.
3. Suba os serviços: `docker compose up --build` (MySQL, Redis, motor e backend).
4. Rode o simulador contra a API: `python scripts/rodar_simulacao.py --simulacao demo --dias 3 --inicio 2026-01-05`. Use `--segundos-por-passo 1` para o modo acelerado e `--simulacao` com outro nome a cada nova execução.
5. Consulte a API, por exemplo: `curl -H "X-Simulation-Id: demo" http://127.0.0.1:3000/summary/today`.

Sem Docker, o motor roda com `python -m engine.service` (variáveis `ENGINE_HOST` e `ENGINE_PORT`) e o backend com `npm run dev` em `backend/`. O dashboard ainda não existe.

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
- `market.sold_kwh` e `market.bought_kwh`: energia vendida e comprada no marketplace no passo, em kWh (potência em kW multiplicada por 0,25 h). Tem efeito financeiro apenas: não altera o balanço físico da casa (seção 6).
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

Os perfis exercitam os três comportamentos do sistema: a casa-01 planeja a carga noturna com bateria e tarifa por horário; a casa-02, em dias nublados, precisa de mais energia do que o próprio painel produz e compra no marketplace; a casa-03 produz mais do que consome e vende.

As casas 04 a 10 (`EXTRA_HOUSES` em `simulator/config.py`) repetem esses perfis com variações de painel, bateria e horário do carro. A opção `--casas N` (de 3 a 10) escolhe quantas participam do comparativo e da simulação.

| Casa | Painel | Inversor | Bateria | Carro |
|---|---|---|---|---|
| casa-04 | 5,0 kWp | ET G2 de 6 kW | 6,4 kWh (2 módulos) | Em casa das 19:00 às 07:00; chega com SOC de 25%; meta de 80% |
| casa-05 | 7,0 kWp | ET G2 de 8 kW | 12,8 kWh (4 módulos) | Em casa das 08:00 às 18:00; chega com SOC de 35%; meta de 80% |
| casa-06 | 5,0 kWp | ET G2 de 6 kW | 6,4 kWh (2 módulos) | Em casa das 20:00 às 07:00; chega com SOC de 30%; meta de 90% |
| casa-07 | 10,0 kWp | ET G2 de 10 kW | 12,8 kWh (4 módulos) | Sem carro; vendedora de excedente |
| casa-08 | 4,5 kWp | ET G2 de 6 kW | 6,4 kWh (2 módulos) | Em casa das 17:00 às 06:00; chega com SOC de 20%; meta de 80% |
| casa-09 | 6,0 kWp | ET G2 de 6 kW | 12,8 kWh (4 módulos) | Em casa das 10:00 às 16:00; chega com SOC de 50%; meta de 80% |
| casa-10 | 9,0 kWp | ET G2 de 10 kW | 12,8 kWh (4 módulos) | Sem carro; vendedora de excedente |

A saída da casa-06 é às 07:00, e não às 08:00, para que a visita caiba no período simulado, que termina às 07:00 depois do último dia.

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
5. Classifica cada dia com pelo menos 11 das 12 horas de sol (06:00 a 18:00) com medição (a irradiação do dia soma todas as horas medidas), pela razão entre sua irradiação diária (kWh/m2) e o percentil 90 dos dias válidos: ensolarado (razão de 0,75 ou mais), parcialmente nublado (de 0,35 a menos de 0,75) e chuvoso (abaixo de 0,35). Resultado em `dados/processados/dias_sp_classificados.csv`, que alimenta os cenários de teste.
6. Lista, por classe, os dias mais recentes que têm 7 dias válidos anteriores, que servem de histórico para a previsão.

Tratamento do consumo (ECD-UY): o script ainda não existe. O plano é calcular o perfil médio por passo de 15 minutos (reamostrando, se o intervalo original for outro) para dia útil e para fim de semana e normalizá-lo para o consumo diário de cada casa (15,0 kWh na casa de referência da seção 4.3).

O INMET não registra radiação à noite, então a hora sem medição fora do período de sol vale zero. Uma regra anterior, que exigia 22 horas válidas por dia, descartava todos os dias.

No simulador (`simulator/solar.py`), o clima de um dia pode ser uma data (`--clima 2026-09-27,2026-09-23`): a geração de cada passo é a irradiância daquele dia, interpolada linearmente entre as horas, multiplicada pelo kWp da casa e por 0,80 e limitada à potência do inversor. A hora H do INMET é a média da hora anterior a H, e por isso o valor é associado ao meio dessa hora. Os nomes `ensolarado`, `parcialmente nublado` e `chuvoso` continuam usando a curva sintética da seção 4.3.

Resultado da execução sobre os dados de 2025-01-01 a 2026-09-30 (8.146 registros horários, pico de 1,110 kW/m2): 609 dias válidos, com referência p90 de 6,59 kWh/m2 por dia; 206 ensolarados, 310 parcialmente nublados e 93 chuvosos. Esses números foram obtidos somando só as horas de sol (06:00 a 18:00). O script agora soma todas as horas medidas do dia (a validade continua pelas horas de sol), para não subestimar dias de verão com sol antes das 06:00 ou depois das 18:00; a contagem e a referência p90 precisam ser atualizadas depois de executar o script de novo.

Limitações dos dados: a radiação é medida em um único ponto da cidade; o consumo vem de domicílios uruguaios, com hábitos e clima diferentes dos brasileiros, e por isso só o formato da curva diária é aproveitado, não os valores absolutos. A origem uruguaia está declarada na seção 11.

## 5. Motor de decisão

### 5.1 Regras de despacho

A cada passo de simulação (15 minutos), o motor aplica estas prioridades:

1. Cobrir a carga da casa com a geração solar.
2. Garantir o objetivo do carro. A energia necessária é (SOC alvo menos SOC atual) multiplicado pela capacidade da bateria do carro. A partir da potência do carregador, o motor calcula o horário limite para iniciar a carga. Ao atingir esse horário, o carro carrega mesmo sem excedente solar, com energia da bateria ou da rede.
3. Direcionar o excedente solar, nesta ordem: carro (até a potência do carregador), bateria (até a potência máxima de carga), marketplace, rede.
4. Descarregar a bateria para a casa nos horários de tarifa mais alta, mantendo reserva para o objetivo do carro.

Implementação atual (`engine/dispatch.py`):

- O comando de um passo usa a leitura do passo atual como estimativa do passo seguinte (persistência).
- Sem otimização: o carro carrega na potência máxima assim que conectado, até o SOC alvo; a bateria recebe o excedente solar e cobre o déficit em qualquer horário.
- Com otimização: o carro carrega na potência máxima quando o tempo até a saída se iguala ao tempo necessário; antes disso, carrega nos passos de menor tarifa até a saída (em empate de preço, nos mais cedo) e, fora deles, com o excedente solar. A bateria recebe o excedente depois do carro e cobre o déficit em qualquer horário.
- A regra 4 (guardar a bateria para a tarifa alta) foi testada e não foi mantida: no cenário padrão de 7 dias, com exportação a R$ 0,00/kWh, ela aumentou o custo das casas 02 e 03, possivelmente porque a bateria mais cheia pela manhã deixava o excedente solar do dia ser exportado sem receita. Deve ser reavaliada quando o valor da exportação (piso do marketplace) estiver definido.

### 5.2 Previsão

Modelo simples de geração e consumo por hora do dia. O erro é medido com o erro médio absoluto (MAE, em kW) e informado na seção de resultados. Na implementação atual, a previsão é por persistência: a leitura do passo atual é a estimativa do passo seguinte (seção 5.1). O método final ainda será definido e comparado com a persistência.

`scripts/avaliar_previsao.py` mede o MAE de duas previsões de geração (`engine/forecast.py`) sobre a radiação real do INMET, hora a hora, de 06:00 a 17:00: a persistência (valor da hora anterior) e a média da mesma hora nos 7 dias anteriores. Só entram as horas em que as duas previsões existem, e o erro sai em kW/m2 e em kW de uma casa de 6 kWp (fator 0,80). O motor continua usando a persistência; trocar o método só depois de o script mostrar ganho. O MAE ainda não foi medido: o valor entra na seção 10 depois que o Victor executar o script. A previsão de consumo não é avaliada, porque o perfil de consumo (ECD-UY) ainda não foi processado.

### 5.3 Tarifas e emissões

- **Tarifa:** a referência é a tarifa branca, que cobra preços diferentes por horário para consumidores de baixa tensão. A distribuidora de referência é a Enel SP. Em dias úteis, os postos horários são: ponta das 17:30 às 20:30; intermediário das 16:30 às 17:30 e das 20:30 às 21:30; fora de ponta nas demais horas. Aos fins de semana e feriados nacionais, vale fora de ponta o dia todo. Os valores em R$/kWh são a soma da TE e da TUSD de cada posto na modalidade Branca, extraídas do conjunto de dados "Tarifas de aplicação das distribuidoras de energia elétrica" da ANEEL. Os valores vigentes, consultados em 12/10/2026, estão na tabela abaixo.
- **Fator de emissão de CO2 da rede elétrica brasileira:** fator médio mensal do Sistema Interligado Nacional publicado pelo MCTI na plataforma SIRENE, em kg CO2/MWh, dividido por 1000 para obter kg CO2/kWh. O valor adotado, o período de referência e a data da consulta são registrados nesta seção.

Tarifa branca residencial (subgrupo B1) da Enel SP, sem tributos, em vigor de 04/07/2026 a 03/07/2027. No arquivo da ANEEL, a distribuidora aparece com a sigla ELETROPAULO.

| Posto | TUSD (R$/MWh) | TE (R$/MWh) | Total (R$/MWh) | Total (R$/kWh) |
|---|---|---|---|---|
| Fora ponta | 367,33 | 301,91 | 669,24 | 0,6692 |
| Intermediário | 682,59 | 301,91 | 984,50 | 0,9845 |
| Ponta | 997,85 | 482,45 | 1480,30 | 1,4803 |

O simulador usa esses valores sem tributos (ICMS e PIS/COFINS não são incluídos). Em reais, os resultados ficam abaixo dos de uma conta real. Fonte: conjunto de dados "Tarifas de aplicação das distribuidoras de energia elétrica", ANEEL, extraído com `scripts/extrair_tarifa_enel_sp.py`, que lê `dados/brutos/aneel/tarifas-homologadas-distribuidoras-energia-eletrica.csv` e grava `dados/processados/tarifa_enel_sp_branca.csv`.

### 5.4 Cenários comparados

| Cenário | Comportamento |
|---|---|
| Sem otimização | O carro carrega na potência máxima assim que conectado; a bateria opera apenas em autoconsumo simples; sem previsão e sem marketplace |
| Com otimização | Regras da seção 5.1, previsão e marketplace ativos |

Os dois cenários rodam sobre o mesmo dia simulado, com a mesma semente aleatória.

No código atual, o marketplace roda a cada passo apenas no cenário com otimização (`marketplace/settlement.py`). O comparativo mostra, por casa, os kWh vendidos e comprados e o ganho do marketplace em R$, que já está descontado do custo. A opção `--sem-marketplace` desliga o marketplace para isolar o efeito dele.

## 6. Marketplace de energia entre vizinhos

Casas com excedente solar que o próprio carro e a própria bateria não absorvem vendem essa energia a carros elétricos de outras casas simuladas que precisam carregar.

- **Vendedor:** casa com excedente solar maior que zero depois de atender a carga da casa, o carro e a bateria (seção 5.1). Publica uma oferta com quantidade em kWh e preço em R$/kWh.
- **Comprador:** carro conectado em outra casa, com necessidade de carga não atendida. Publica uma ordem com quantidade e preço máximo.
- **Faixa de preço:** entre o valor pago ao vendedor pela energia exportada à rede (piso) e o preço da energia comprada da rede (teto). Nessa faixa, o vendedor recebe mais que na rede e o comprador paga menos que na rede.
- **Preço da negociação:** média entre o piso da oferta e o teto da ordem.
- **Casamento:** as ofertas são ordenadas por piso crescente e as ordens por teto decrescente, com desempate por `house_id`. A negociação só ocorre quando o piso da oferta é estritamente menor que o teto da ordem, para que vendedor e comprador ganhem em relação à rede. Cada casa tem no máximo uma oferta e uma ordem por passo, uma casa não compra e vende no mesmo passo, e as sobras expiram ao fim do passo. Implementado em `marketplace/matching.py`.
- **Modelo físico:** a energia negociada passa fisicamente pela rede elétrica (modelo `financial_only`). O marketplace altera apenas o valor em R$ de cada casa; o balanço de energia de cada casa fecha com a potência da rede, como na seção 4.2. A verificação do balanço, do SOC e dos limites de potência a cada passo está em `engine/validation.py`.
- **Registro:** cada negociação gera uma linha no MySQL com casa vendedora, casa compradora, kWh, preço e horário.

A demonstração começa com 3 casas (seção 4.3) e é ampliada até 10 casas.

A implementação inicial está em `marketplace/matching.py`: preço médio entre o valor de oportunidade da exportação e a tarifa do comprador, prioridade por preço e desempate por casa. Uma casa não pode comprar e vender no mesmo passo.

Integração com o simulador (`marketplace/settlement.py`): a cada passo, toda casa que exportou publica uma oferta com a energia exportada e piso igual ao valor da exportação; toda casa que importou da rede enquanto carregava o carro publica uma ordem com quantidade igual ao menor valor entre a importação e a energia do carro, e teto igual à tarifa da rede no passo. O vendedor ganha (preço - valor da exportação) por kWh e o comprador economiza (tarifa - preço) por kWh; esses ganhos entram no custo de cada casa.

O ganho do marketplace depende do valor da exportação, que ainda é premissa (R$ 0,00/kWh por padrão, `--valor-exportacao`). Com esse valor, o piso é zero e o preço médio é metade da tarifa, o que infla o ganho em relação a um valor de exportação real.

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

Implementado em `dashboard/index.html` (um arquivo, JavaScript puro e SVG, sem dependências externas; tema claro ou escuro conforme o sistema) e `dashboard/server.py` (biblioteca padrão do Python). A página consulta o backend a cada 2 segundos e mostra:

- Resumo do dia (`GET /summary/today`): energia importada e exportada, custo líquido, ganho do marketplace, emissões e economia. Campos que o backend devolve nulos aparecem como "n/d".
- Diagrama do fluxo de energia entre painel, bateria, carro, casa e rede, com a potência de cada ligação, para a casa selecionada.
- Decisão do motor para a casa (`GET /houses/:id/decision`), com o texto de `reason`.
- Gráfico de geração, consumo e rede, e gráfico do SOC da bateria e do carro (`GET /houses/:id/history`).
- Tabela com todas as casas no último passo; clicar em uma linha seleciona a casa.
- Comparativo sem e com otimização (`GET /comparison`); se o arquivo ainda não existe, a página avisa em vez de falhar.
- Negociações, ofertas e ordens do marketplace.
- Formulário da meta do carro (`PUT /houses/:id/ev`).

O campo "Simulação" do cabeçalho define o cabeçalho `X-Simulation-Id`. Como o backend não tem rota que liste as casas, a página procura `casa-01`, `casa-02`... até a primeira que responde 404.

O backend não habilita CORS (seção 3.7). Por isso o navegador não fala com ele diretamente: `dashboard/server.py` entrega a página e repassa `/api/*` ao backend, repassando `Content-Type` e `X-Simulation-Id`; se o backend estiver fora do ar, responde 502. Variáveis: `BACKEND_URL` (padrão `http://127.0.0.1:3000`), `DASHBOARD_HOST` (`127.0.0.1`) e `DASHBOARD_PORT` (`8080`).

Execução sem Docker, com o backend já no ar: `python dashboard/server.py` e abrir `http://127.0.0.1:8080`. Com Docker: o serviço `dashboard` do Compose sobe junto (`docker compose up --build`) e fica em `http://localhost:8080`.

Verificação feita: a página foi aberta em navegador automatizado (largura de computador e de celular, tema claro e escuro) contra uma API simulada que usa o simulador e o motor reais, sem erros de script e sem rolagem horizontal. Não foi testada contra o backend real nem dentro do Docker.

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
- No marketplace, a energia negociada passa pela rede e o custo de uso da rede (transporte) entre vendedor e comprador não é modelado; o valor da energia exportada usado como piso é uma premissa de simulação.
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

### API e bancos

Com Docker Compose v2, copie `.env.example` para `.env`, ajuste as senhas e execute na raiz:

```sh
docker compose up --build -d
curl http://localhost:3000/health
```

São iniciados backend (porta 3000), MySQL 8.4 (3306) e Redis 7 (6379), acessíveis apenas no computador local. As tabelas são criadas na inicialização. O padrão `ENGINE_MODE=neutral` permite testar a API enquanto o serviço HTTP do motor está pendente. Para ativá-lo, configure `ENGINE_MODE=http`, um `ENGINE_URL` acessível pelo container e `EXPORT_VALUE_PER_KWH`; o serviço `engine` já faz parte do Compose, e o backend usa `ENGINE_URL: http://engine:8000`. O dashboard sobe junto, em `http://localhost:8080`.

Para desenvolver com Node.js 22 ou superior, suba os bancos com `docker compose up -d mysql redis`, use `MYSQL_HOST=localhost` e `REDIS_HOST=localhost` no `.env` e execute:

```sh
cd backend
npm ci
npm run dev
```

Verificação do backend, dentro de `backend/`:

```sh
npm run build
npm test
node --env-file=../.env --import tsx --test test/integration/*.test.ts
```

O último comando exige os bancos acessíveis nos hosts do `.env`. Cria uma simulação de teste isolada e remove seus registros ao terminar. Foram verificados concorrência, rollback e recuperação após reinício com MySQL 8.4.6 e Redis 5.0.14.1 para Windows. O Compose com Redis 7 ainda precisa ser executado em um ambiente com Docker.

### Simulador, motor e marketplace

Testado com Python 3.12, sem dependências externas para os módulos novos:

```sh
python -m unittest discover -s tests -v
```

Os testes cobrem o marketplace e `engine/validation.py`, que verifica balanço de potência, SOC, limites de potência, EV desconectado e compra/venda simultânea. O validador recebe leituras do mesmo intervalo de 15 minutos e o modelo de troca: `ideal_microgrid` inclui a energia interna no balanço; `financial_only` considera apenas o fluxo físico da rede. O sistema adota `financial_only` (seção 6).

`tests/test_scenario.py` cobre os postos da tarifa, os limites de SOC e de potência da casa simulada e o comparativo: cada leitura de cada passo passa por `validate_reading`, a mesma semente reproduz o mesmo resultado, os dois cenários veem o mesmo clima, o carro atinge o SOC alvo em todas as saídas e o cenário com otimização custa menos que o cenário sem.

`TenHousesTests` roda 10 casas por 3 dias: todas as leituras passam pela validação, todo carro atinge o SOC alvo em todas as visitas e o total vendido no marketplace é igual ao total comprado; também verifica que `houses_for` recusa menos de 3 ou mais de 10 casas.

Também verifica o marketplace no simulador: o total vendido é igual ao total comprado, o cenário sem otimização não tem negociações, e o marketplace reduz o custo sem alterar a energia importada (modelo `financial_only`).

O comparativo roda em linha de comando, sem backend: `python scripts/comparar_cenarios.py` (opções: `--dias`, `--inicio`, `--semente`, `--clima`, `--valor-exportacao`, `--fator-co2`, `--sem-marketplace`, `--casas`, `--json`, `--simulacao`). O CO2 só é calculado quando o fator é informado.

`tests/test_forecast.py` verifica as duas previsões de geração: a média da mesma hora acerta exatamente um perfil que se repete, exige 7 dias de histórico, e a persistência usa a hora anterior. O MAE sobre dados reais sai de `python scripts/avaliar_previsao.py`.

`tests/test_service.py` cobre o serviço do motor: o formato da resposta de `/decide`, a consistência entre `market` dos comandos e as negociações, o cenário sem otimização sem marketplace, as entradas inválidas (400 e 422), o laço fechado do simulador com o motor (mesma energia importada que `simulator.scenario.run`) e as rotas HTTP.

Os testes do backend estão em `backend/test/` (`npm test` em `backend/`; `npm run test:integration` usa MySQL e Redis reais). Além deles, o contrato foi verificado com o código de validação do backend (`validation.ts`) sobre 192 passos reais de 2 dias simulados, todos aceitos, com 68 negociações.

Ainda faltam testes de ponta a ponta com o Docker Compose.
