# GoodWe HEMS-EV

Gerenciador inteligente de energia residencial com carregamento de veículo elétrico e marketplace de energia entre vizinhos, desenvolvido para o GoodWe EV Challenge 2026 (FIAP).

## Estado do projeto

Em desenvolvimento. Este documento descreve a arquitetura e o comportamento previstos do sistema. As seções "Resultados" e "Alinhamento à disciplina" serão preenchidas com dados e conteúdos do sistema implementado.

## Equipe

| Nome | RM |
|---|---|
| Davi Ramos | 571744 |
| Lucas Galle Melchior | 574027 |
| Victor | 571099 |
| Gabriel Cavaloti | 571643 |

## 1. Visão geral

O HEMS-EV (Home Energy Management System com carregamento de veículo elétrico) decide, em intervalos regulares, para onde vai cada quilowatt de energia em uma casa com painel solar fotovoltaico, bateria, carregador de veículo elétrico e ligação com a rede elétrica.

O sistema tem três partes:

1. **Simulador.** Gera os dados que um inversor híbrido GoodWe, uma bateria GoodWe Lynx e um carregador GoodWe HCA enviariam. O projeto não usa hardware real.
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
| Tecnologias compatíveis com a GoodWe | Simulador modelado sobre inversor híbrido ET G2, baterias Lynx Home e carregador HCA; adaptador com a mesma interface de dados da biblioteca de comunicação local `goodwe` (seção 7) |
| Algoritmos inteligentes | Previsão de geração e consumo; planejamento de carga pelo horário de saída do carro; despacho de energia por prioridade |
| Análise de impactos: eficiência, pegada de carbono, relevância social ou ambiental | Comparação entre cenário sem e com otimização em kWh importados, autoconsumo, custo e CO2 |
| Interface amigável e visualização de dados | Dashboard com fluxo de energia, gráficos de geração, consumo e estado de carga |
| Integração com assistente virtual | Integração com a ARIA (Assistente de Recarga Inteligente e Autônoma) |
| Conexão com os conteúdos da disciplina | A preencher (seção 9) |

## 3. Arquitetura

### 3.1 Fluxo de dados

```
Simulador (casa, inversor ET/ES, bateria Lynx, carregador HCA)
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
| Simulador | Python ou Node.js | Gerar dados de casa, inversor, bateria e carregador |
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
  docs/            diagramas de arquitetura e capturas de tela do sistema
  simulator/       simulador de casa, inversor, bateria e carregador
  adapter/         interface única simulado/goodwe-local
  backend/         API Node.js/TypeScript
  engine/          previsão e motor de decisão
  marketplace/     ofertas, ordens e casamento
  dashboard/       interface web
  docker-compose.yml
```

## 4. Simulador

O simulador representa uma ou mais casas. Cada casa tem:

- **Painel solar:** potência gerada ao longo do dia, com curva de sol (nascer, pico, pôr do sol) e variação por nuvens.
- **Carga da casa:** consumo base com picos de manhã e à noite.
- **Bateria:** capacidade em kWh, potência máxima de carga e descarga em kW, estado de carga (SOC) em porcentagem.
- **Carregador EV:** potência máxima em kW, carro conectado ou não, SOC do carro, SOC alvo e hora de saída.
- **Rede:** potência importada ou exportada em kW.

Os parâmetros numéricos (capacidade da bateria, potência do painel, consumo médio) são derivados de especificações de modelos GoodWe reais e registrados nesta seção com o modelo de referência.

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
    "target_soc_percent": 80.0,
    "departure_time": "07:00",
    "charge_power_kw": 1.8
  },
  "grid_power_kw": 0.0
}
```

Convenções: potências em kW; `battery.power_kw` positivo indica descarga e negativo indica carga; `grid_power_kw` positivo indica importação e negativo indica exportação. Os nomes dos campos seguem, sempre que possível, os sensores expostos pela biblioteca `goodwe`, para que a troca do simulador por um inversor real não exija reescrever o restante do sistema.

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

- **Tarifa:** a referência é a tarifa branca, que cobra preços diferentes por horário para consumidores de baixa tensão. Os valores em R$/kWh e a fonte (distribuidora e ano) são registrados nesta seção.
- **Fator de emissão de CO2 da rede elétrica brasileira:** valor em kg CO2/kWh, com fonte oficial e ano, registrado nesta seção.

### 5.4 Cenários comparados

| Cenário | Comportamento |
|---|---|
| Sem otimização | O carro carrega na potência máxima assim que conectado; a bateria opera apenas em autoconsumo simples; sem previsão e sem marketplace |
| Com otimização | Regras da seção 5.1, previsão e marketplace ativos |

Os dois cenários rodam sobre o mesmo dia simulado, com a mesma semente aleatória.

## 6. Marketplace de energia entre vizinhos

Casas com excedente solar que o próprio carro e a própria bateria não absorvem vendem essa energia a carros elétricos de outras casas simuladas que precisam carregar.

- **Vendedor:** casa com excedente restante maior que zero após as prioridades 1 a 3 da seção 5.1. Publica uma oferta com quantidade em kWh e preço em R$/kWh.
- **Comprador:** carro conectado em outra casa, com necessidade de carga não atendida. Publica uma ordem com quantidade e preço máximo.
- **Faixa de preço:** entre o valor pago ao vendedor pela energia exportada à rede (piso) e o preço da energia comprada da rede (teto). Nessa faixa, o vendedor recebe mais que na rede e o comprador paga menos que na rede.
- **Casamento:** ofertas e ordens são ordenadas por preço, e a negociação ocorre quando o preço da oferta é menor ou igual ao preço máximo da ordem.
- **Registro:** cada negociação gera uma linha no MySQL com casa vendedora, casa compradora, kWh, preço e horário.

O número de casas simuladas na demonstração é registrado nesta seção.

## 7. Tecnologias GoodWe e integração

### 7.1 Equipamentos de referência

| Equipamento | Características confirmadas em fontes públicas | Uso no projeto |
|---|---|---|
| Carregador EV série HCA (GW7K-HCA, GW11K-HCA, GW22K-HCA) | Carregador AC com carga por excedente solar, compatível com inversores solares e híbridos GoodWe; variantes monofásica de 7 kW e trifásicas de 11 kW e 22 kW; conexão Wi-Fi com o sistema GoodWe; acompanhamento no SEMS e no aplicativo | Modelo de carregador simulado (GW7K-HCA, monofásico) |
| Inversor híbrido ET G2 | Trifásico de alta tensão, de 6 a 15 kW, com medidor inteligente embutido, compatível com a bateria Lynx F G2 | Referência para o inversor simulado |
| Baterias Lynx Home (F e D) | A série Lynx Home F é compatível com inversores ET e EH (híbridos) e BH e BT (de bateria) | Referência para a bateria simulada |

O carregador HCA já realiza carga por excedente solar por conta própria. O diferencial do HEMS-EV está na camada acima dele: previsão, planejamento pelo horário de saída do carro, uso de tarifa por horário e marketplace.

### 7.2 Interfaces de comunicação

| Interface | Descrição | Situação no projeto |
|---|---|---|
| SEMS Portal Open API (nuvem) | API HTTPS da GoodWe com 31 interfaces em 4 grupos (usina, dispositivo, controle remoto, data logger); entrega dados brutos e dados de negócio processados pela plataforma SEMS | Exige conta organizacional e solicitação à GoodWe. Não utilizada na versão simulada |
| Protocolo local do inversor | A biblioteca Python de código aberto `goodwe` lê dados pela rede local por UDP na porta 8899, ou por Modbus/TCP na porta 502 com o dongle LAN+WiFi V2.0 (modelo WLA0000-01-00P), nas famílias ET, EH, BT, BH, ES, EM, BP, DT, MS, D-NS e XS | Protocolo mapeado pela comunidade, não documentado oficialmente pela GoodWe. Relatos da comunidade indicam que firmwares recentes de algumas linhas usam DTLS na porta 8899. É a interface de referência do adaptador |

### 7.3 Estratégia de integração

O adaptador expõe uma interface única com duas implementações: `simulado` e `goodwe-local`. O simulador produz os mesmos sensores que a biblioteca `goodwe` entrega. Assim, substituir o simulador por um inversor real não exige alterar o motor de decisão, o backend nem o dashboard.

## 8. Dashboard e assistente virtual

### 8.1 Dashboard

- Diagrama do fluxo de energia em tempo real entre painel, bateria, carro, casa e rede.
- Gráfico de geração e consumo do dia.
- Gráficos do SOC da bateria e do carro.
- Painel comparativo sem e com otimização: custo, kWh importados da rede, autoconsumo e CO2.
- Lista das negociações do marketplace.

### 8.2 Assistente ARIA

A ARIA (Assistente de Recarga Inteligente e Autônoma) responde a perguntas como "quanto economizei hoje?" e aceita comandos como "deixe o carro pronto às 7h", consultando o backend por API HTTP. O contrato dessa API é registrado nesta seção.

## 9. Alinhamento à disciplina

A preencher com os conteúdos da disciplina aplicados no projeto.

## 10. Resultados

A preencher com dados gerados pelo sistema implementado:

- Tabela comparativa dos cenários sem e com otimização: custo (R$), energia importada da rede (kWh), autoconsumo solar (%), emissões de CO2 (kg) e porcentagem de dias em que o carro atingiu o SOC alvo na hora de saída.
- Erro da previsão (métrica e valor).
- Resumo do marketplace: número de negociações, kWh negociados e preço médio.
- Capturas de tela do dashboard e diagramas do sistema implementado.

## 11. Avaliação crítica e limitações

- Os resultados são obtidos por simulação, não por medição em campo.
- Sistemas de gestão de energia residencial já existem. As contribuições do projeto são a combinação de previsão, reserva de bateria pelo horário de saída do carro, comparativo de CO2, marketplace entre vizinhos e assistente em linguagem natural.
- A venda direta de energia entre particulares está sujeita à regulação do setor elétrico brasileiro. O marketplace é tratado como simulação acadêmica.
- A integração com a SEMS Open API depende de credencial fornecida pela GoodWe. A versão atual usa o adaptador simulado.

## 12. Referências

- GoodWe, API introduction: https://community.goodwe.com/solution/API%20introduction
- Biblioteca Python goodwe (PyPI): https://pypi.org/project/goodwe/0.4.6/
- GoodWe, HCA Series: https://en.goodwe.com/hca-series
- pv magazine, GoodWe lança carregador EV solar residencial: https://www.pv-magazine.com/press-releases/goodwe-launches-solar-powered-smart-ev-charger-for-residential-use-2/
- Krannich, EV Charger GW 7K-HCA: https://shop.krannich-solar.com/de-en/e-mobility/charging-stations/42618/ev-charger-gw-7k-hca
- pv magazine Australia, ET G2: https://www.pv-magazine-australia.com/2024/12/13/goodwe-releases-three-phase-high-voltage-hybrid-inverter-in-australia
- Solartraders, Lynx Home F: https://www.solartraders.com/en/products/batteries/bms-modules/goodwe-lynx-home-f-hv-pcu
- Home Assistant Community, GW6000-ES-20 e DTLS: https://community.home-assistant.io/t/goodwe-gw6000-es-20-read-real-time-pv-production-locally-python-no-cloud/1016056
