# Contexto interno do projeto GoodWe HEMS-EV

Este arquivo reúne o contexto de planejamento do projeto: enunciado, critérios de avaliação, decisões, divisão de tarefas, plano e pontos em aberto. Ele NÃO faz parte da documentação técnica. A documentação técnica está em `README.md`.

Legenda de status:

- DECIDIDO: confirmado pelo grupo.
- PROPOSTA: sugerido no planejamento, ainda não validado pelo grupo.
- VERIFICADO: fato conferido em fonte pública (links no README).
- PENDENTE: depende de informação ou da implementação.

---

## 1. Enunciado da Sprint 4

Título: SPRINT 4 - Solução Final Integrada e Inovadora Goodwe.

Objetivos principais:

- Entregar uma solução integrada, funcional e inovadora, alinhada ao desafio proposto pela GoodWe e às competências do curso.
- Justificar em detalhe a aderência da solução aos requisitos técnicos e à sustentabilidade.

Objetivos específicos:

- Evidenciar, com resultados reais ou simulados, o funcionamento integrado e otimizado do sistema (exemplo do enunciado: geração, armazenamento e uso de energia renovável com monitoramento inteligente).
- Demonstrar o uso de tecnologias compatíveis com a GoodWe e conectar esses pontos aos conteúdos da disciplina.
- Apresentar análise de impactos objetivos: viabilidade técnica, ganhos de eficiência, redução de pegada de carbono, relevância social ou ambiental.
- Mostrar diferenciais inovadores: algoritmos inteligentes, automações avançadas, interface amigável, visualização de dados, integração com assistentes virtuais.

Tarefas exigidas:

- Gravar um vídeo técnico de até 5 minutos com a solução funcionando, justificando a escolha de cada tecnologia GoodWe e cada conceito sustentável.
- Elaborar um documento PDF final ou README.md no repositório com: título do projeto; equipe; descrição detalhada da arquitetura final e da integração dos sistemas; justificativa de alinhamento ao desafio GoodWe e à disciplina; resultados quantitativos e qualitativos; avaliação crítica dos benefícios de sustentabilidade e inovação; referências e conexões com frameworks, ferramentas, linguagens e sensores.
- Consolidar código, diagramas, documentação e README no repositório GitHub.

Observações do enunciado: explicar como cada item da solução resolve pontos-chave do desafio; usar imagens e diagramas funcionais reais do sistema implementado; demonstrar ganhos em sustentabilidade, automação e eficiência.

## 2. Critérios de avaliação

| Critério | Pontuação máxima |
|---|---|
| Solução inovadora, funcional e integrada | 60 |
| Justificativa alinhada à disciplina e à GoodWe | 25 |
| Organização, documentação técnica e repositório | 15 |

Consequência prática: 60 de 100 pontos dependem de o sistema funcionar e estar integrado. Uma demonstração simples e funcionando vale mais que uma arquitetura grande e incompleta.

## 3. Entregável

Apenas um arquivo .txt contendo: nome e RM de cada integrante, link do vídeo no YouTube (não listado) e link do repositório GitHub. Arquivos vazios ou corrompidos não são considerados. Não são aceitos arquivos enviados pelo Teams nem fora do prazo. A integridade do arquivo é responsabilidade do grupo.

## 4. Equipe e divisão de tarefas

Equipe: Davi Ramos (RM 571744), Lucas Galle Melchior (RM 574027), Victor Hugo Ferreira Freire (RM 571099), Gabriel Cavaloti (RM 571643).

Divisão em duas duplas (DECIDIDO em 2026-10-11): código com Victor e Gabriel Cavaloti; gravação e edição do vídeo com Lucas Galle Melchior e Davi Ramos. Dentro da dupla do código não há divisão fixa de obrigações: o Victor atribui tarefas ao Gabriel Cavaloti quando necessário (DECIDIDO em 2026-10-13). Falta definir quem fica com README final, diagramas, organização do repositório e .txt de entrega. A distribuição dos papéis C e D abaixo é PROPOSTA.

| Papel | Dupla | Responsabilidade |
|---|---|---|
| Código | Código | Victor Hugo Ferreira Freire coordena e atribui tarefas ao Gabriel Cavaloti quando necessário. Escopo: simulador, adaptador GoodWe, backend Node/TypeScript, Redis, MySQL, Docker Compose, motor de decisão, previsão, comparativo antes/depois, marketplace, dashboard e integração com a ARIA |
| Código | Código | Gabriel Cavaloti: tarefas atribuídas pelo Victor, sem divisão fixa de obrigações |
| C | Vídeo | Roteiro de 5 minutos, gravação da demonstração, edição, upload no YouTube como não listado |
| D | Documentação | README final, diagramas, organização do repositório GitHub, arquivo .txt de entrega |

Observação de carga: o motor de decisão e o marketplace concentram o diferencial técnico, e o dashboard é a parte visual que aparece no vídeo. A dupla do vídeo pode apoiar o layout do dashboard, sem alterar a lógica.

## 5. Decisões tomadas

| Data | Decisão | Status |
|---|---|---|
| 2026-10-11 | Tema: gerenciador de energia residencial com carregador EV (HEMS-EV), com simulador de dados GoodWe como fonte | DECIDIDO |
| 2026-10-11 | Marketplace de energia entre vizinhos simulados está dentro do escopo | DECIDIDO |
| 2026-10-11 | Não há hardware real: inversor, bateria e carregador são simulados | DECIDIDO |
| 2026-10-11 | Divisão da equipe: 2 pessoas no código, 2 no vídeo e documentação | DECIDIDO |
| 2026-10-11 | Reaproveitar a ARIA como assistente virtual | PROPOSTA (professor aceitaria, segundo o Victor) |
| 2026-10-11 | README sem emojis, texto específico, sem conteúdo de planejamento interno | DECIDIDO |
| 2026-10-11 | Contexto de planejamento separado da documentação técnica | DECIDIDO |
| 2026-10-11 | Data de entrega: 2026-10-23 (sexta-feira) | DECIDIDO |
| 2026-10-11 | Dupla do código: Victor e Gabriel Cavaloti. Dupla do vídeo (gravação e edição): Lucas Galle Melchior e Davi Ramos | DECIDIDO |
| 2026-10-11 | Simulador em Python; Node.js apenas no backend | DECIDIDO |
| 2026-10-11 | Demonstração começa com 3 casas e é ampliada até 10 | DECIDIDO |
| 2026-10-11 | Carregador simulado: linha HCA G2 (GW7K-HCA-20) | DECIDIDO |
| 2026-10-11 | Disciplinas: Pensamento Computacional e Automação com Python; Soluções em Energias Renováveis e Sustentáveis | DECIDIDO |
| 2026-10-11 | Sem credencial da SEMS Open API: adaptador implementa apenas o modo simulado nesta entrega | PROPOSTA |
| 2026-10-11 | Valores numéricos do simulador definidos pelo Claude a pedido do Victor (README, seção 4.3) | PROPOSTA (falta validação do grupo) |
| 2026-10-13 | Sem divisão fixa de obrigações na dupla do código: o Victor atribui tarefas ao Gabriel Cavaloti quando necessário | DECIDIDO |
| 2026-10-13 | Perfis de geração solar e de consumo derivados de dados públicos, explicitado na documentação | DECIDIDO |
| 2026-10-17 | Fontes dos dados públicos: INMET (estação A701) para geração solar e ECD-UY (Uruguai) para consumo; origem uruguaia declarada como limitação | DECIDIDO (aprovado pelo Victor) |
| 2026-10-17 | README sob responsabilidade do Victor (escrito com o Claude) | DECIDIDO |
| 2026-10-17 | Repositório na conta do Victor, público; comentários em português; nomes de arquivos e pastas mantidos em inglês como no README (campos JSON da API também em inglês); mensagens de commit em inglês; o Gabriel Cavaloti commita com a própria conta; `CONTEXT.md` público com as notas internas | DECIDIDO |
| 2026-10-19 | Modelo físico do marketplace: `financial_only` (a energia negociada passa pela rede; só o dinheiro muda entre as casas). Escolhido pelo Claude por delegação do Victor ("faça o que facilita o desenvolvimento"): cada casa fecha o próprio balanço com a rede, sem acoplar casas no simulador | DECIDIDO |
| 2026-10-20 | Regra 4 do motor (guardar a bateria para a tarifa alta) removida da primeira versão: nos 7 dias de teste, com exportação a R$ 0,00/kWh, aumentou o custo das casas 02 e 03. Decisão do Claude por delegação do Victor; reavaliar quando o piso do marketplace (ponto 17) existir | DECIDIDO (validado pelo Victor em 2026-10-20) |
| 2026-10-17 | Corte de escopo, se faltar tempo: 1) simulador, motor e comparativo; 2) dashboard; 3) marketplace; 4) ARIA integrada. Entrega parcial aceita (por exemplo, marketplace só como regra no motor, sem tela própria) | DECIDIDO |

Itens do README que ainda são PROPOSTA e precisam de validação do grupo: formato JSON do simulador, passo de simulação de 15 minutos, regras de despacho do motor, regras de preço e casamento do marketplace, stack e estrutura de pastas do repositório, parâmetros numéricos da seção 4.3 do README, ciclo de execução em passos com comando de retorno ao simulador (resposta do POST /readings), formato do comando, lista de endpoints da API e modos de execução (lote e tempo acelerado).

## 6. Como o projeto foi escolhido

Foi usada uma árvore de ideias. Cada ideia fraca foi removida e substituída por um novo ramo. Critérios de remoção: ideia batida, pouco inovadora, simples demais ou que muitas equipes fazem.

| Ideia | Motivo da remoção |
|---|---|
| Chatbot de recarga | O grupo já tem a ARIA; seria repetição |
| Dashboard de consumo de energia | Muito comum |
| Detector genérico de objetos ou placas | Muito comum |
| Contador de dedos ou gestos | Já feito pelo Victor e simples |
| Sensor de temperatura com aplicativo | Simples demais |
| Carrinho ou robô controlado por aplicativo | O Victor já tem o carrinho ESP32 em outra disciplina |
| Aplicativo de gestão financeira | Saturado |
| Marketplace genérico | Saturado |
| Inspeção de carregadores por câmera | Exigiria um conjunto de imagens que o grupo não tem |
| Rede de microcontroladores simulando microrrede (isolada) | Difícil de ligar à tecnologia GoodWe; demonstração frágil |
| Gêmeo digital de rede de carregadores (isolado) | É apenas um simulador, sem solução integrada; virou componente do projeto escolhido |
| Plataforma de créditos de carbono de recarga | Tende a virar buzzword de blockchain sem entrega concreta |

Ideia escolhida: gerenciador de energia residencial com carregador EV, simulador de inversor GoodWe como fonte de dados e marketplace de energia entre vizinhos (marketplace incluído no escopo por decisão do grupo em 2026-10-11).

## 7. Ressalvas sobre as fontes GoodWe

- A SEMS Open API exige conta organizacional e solicitação ao time de serviço da GoodWe. O grupo não tem credencial. PENDENTE perguntar ao professor ou à organização do desafio se existe credencial de demonstração.
- O protocolo local (UDP 8899, Modbus/TCP 502) é mapeado pela comunidade. Relato da comunidade indica DTLS em firmwares recentes. No README, ele é descrito como "protocolo mapeado pela comunidade", não como API oficial.
- Existe uma API não documentada usada pelos aplicativos móveis (cliente de exemplo: https://www.github.com/AaronSaikovski/gogoodwe). NÃO usar: pode deixar de funcionar sem aviso.
- O carregador HCA já faz carga por excedente solar sozinho. O diferencial do projeto não pode ser apenas esse.

## 8. Plano de trabalho (PROPOSTA)

| Etapa | Conteúdo | Marco de conclusão |
|---|---|---|
| 11 a 13/10 (dom a ter) | Contrato JSON e parâmetros do simulador validados entre Victor e Gabriel; simulador de 1 casa; esqueleto do backend (POST /readings, banco de dados, Docker Compose). Dupla do vídeo: roteiro e estrutura dos diagramas | Contrato aprovado e simulador de 1 casa enviando leituras à API |
| 14 a 17/10 (qua a sáb) | Motor de decisão com as regras de despacho; cenários sem e com otimização; 3 casas; dashboard básico | Comparativo sem e com otimização rodando em lote |
| 18 e 19/10 (dom e seg) | Marketplace; integração com a ARIA; ajustes do dashboard | Fluxo completo funcionando |
| 20/10 (ter) | Congelar o código; rodar os cenários em lote e gerar os números finais | Código congelado e resultados gerados |
| 21 e 22/10 (qua e qui) | Gravar e editar o vídeo; subir no YouTube como não listado; preencher resultados e capturas de tela no README; montar o .txt | Vídeo publicado e README completo |
| 23/10 (sex) | Margem de segurança; conferir os links; enviar o .txt | .txt enviado dentro do prazo |

Prazo: 12 dias corridos, de 2026-10-11 a 2026-10-23. O plano anterior, em semanas, foi substituído por este calendário.

Regras de trabalho: nenhum número entra na seção de resultados sem ter sido gerado pelo sistema; nenhum valor de tarifa ou fator de emissão de CO2 é usado sem fonte oficial citada.

### 8.1 Próximos passos do código (2026-10-20)

Situação: simulador, motor, marketplace integrado ao simulador, comparação e radiação real do INMET estão prontos e testados (35 testes). O backend e a API ficam com o Gabriel Cavaloti, que versiona o código na `main` com a própria conta; o Victor testa com as próprias chaves.

Repasse ao Gabriel (DECIDIDO em 2026-10-20):

- Ler README, seções 3.4 a 3.6 (ciclo, modos e endpoints) e 4.1 a 4.2 (formatos de leitura e comando).
- Começar pelo `POST /readings`, com validação do schema e comando neutro na resposta (carro 0, bateria 0), até o motor estar disponível.
- Em seguida: gravação em Redis e MySQL, `GET` de estado e histórico, `PUT /houses/:id/ev` e `docker-compose.yml`.
- Esquema do MySQL e chaves do Redis: proposta do Gabriel (mínimo: leituras, decisões, negociações e comparativo).

O que falta depois da API, em ordem de prioridade (corte de escopo do ponto 19):

| # | Item | Responsável | Situação |
|---|---|---|---|
| 1 | Serviço HTTP do motor (`/decide`: leituras de um passo para comandos e negociações), embrulhando `decide`, `trade_step` e `validate_reading` | Victor e Claude | PROPOSTA (aguarda ok do Victor) |
| 2 | Modo do simulador que envia `POST /readings` e aplica os comandos da resposta | Victor e Claude | PENDENTE |
| 3 | `scripts/comparar_cenarios.py` gravando um JSON para o `/comparison` | Victor e Claude | PENDENTE |
| 4 | Dashboard: fluxo de energia, gráficos de geração, consumo e SOC, painel comparativo e negociações. Sugestão: HTML com JavaScript puro e Chart.js servido pelo backend, sem etapa de build. Responsável e framework ainda não definidos (ponto 20) | A definir | PENDENTE |
| 5 | Previsão (ponto 5): média móvel sobre os dias reais do INMET com MAE, ou ajustar o README para persistência | Victor e Claude | PENDENTE |
| 6 | ARIA (ponto 8), reaproveitando o projeto da outra sprint | A definir | PENDENTE |
| 7 | Seção de resultados do README com números reais, diagramas, `.txt`, capturas de tela, vídeo (previsto para 22/10) e `docker-compose.yml` | Grupo | PENDENTE |

Pontos menores: corrigir a classificação de dias de verão em `preparar_geracao_inmet.py` (a soma usa só os rótulos de 06:00 a 18:00 e subestima a irradiação de verão; os números de 609 dias do README precisam ser refeitos depois), valor de exportação (ponto 17), fator de CO2 (ponto 4) e perfil de consumo (ECD-UY, opcional).

Resultado parcial com radiação real (3 dias: 2026-09-27, 2026-09-24 e 2026-09-23; exportação a R$ 0,00/kWh): custo de R$ 132,76 para R$ 113,56 (-14,5%), dos quais R$ 9,92 vêm do marketplace; a economia sem marketplace é de cerca de 7%. Esses números dependem da premissa do piso e não entram nos resultados finais.

Calendário: PROPOSTA de congelar o código na noite de 21/10 (a data de 20/10 da tabela acima já passou), com vídeo em 22/10 e entrega em 23/10.

## 9. Pontos em aberto

A numeração original dos pontos foi mantida (outros trechos e o histórico a citam). Ordem: gravidade primeiro, depois urgência. Critério de gravidade: o que bloqueia a implementação ou a entrega vem antes do que apenas melhora a qualidade; 60 dos 100 pontos dependem de o sistema funcionar (seção 2). Os pontos concluídos estão no fim. Situação em 2026-10-17: faltam 6 dias para a entrega e o congelamento do código está previsto para 2026-10-20 (seção 8).

### Resumo: ordem de importância e situação (2026-10-17)

Pontos abertos, do mais para o menos importante:

| Ordem | Ponto | Assunto | Situação | O que falta |
|---|---|---|---|---|
| 1 | 15 | Dados públicos de geração e consumo | PARCIAL | Baixar os ZIPs do INMET e rodar o script; decidir se a ECD-UY entra agora ou fica opcional (curva sintética no consumo) |
| 2 | 5 | Método de previsão | PARCIAL (persistência implementada) | Escolher o método (sugestão: média móvel por hora, com persistência como comparação) |
| 3 | 2 | Responsável por diagramas e .txt de entrega | PARCIAL | README já é do Victor; faltam diagramas e .txt |
| 4 | 17 | Preço no marketplace e piso (SCEE) | PARCIAL | Preço médio já implementado pelo Gabriel; falta definir o piso (valor da energia exportada) e entender o SCEE |
| 5 | 18 | Perfil do comprador no marketplace | RESOLVIDO | Comprador negocia se o preço for menor que a tarifa da rede; transporte pela rede não modelado e declarado como limitação (README, seção 11) |
| 6 | 23 | Execução e testes | PARCIAL | Validação e testes unitários existem, com comando no README (seção 13); faltam como executar o sistema completo e testes integrados |
| 7 | 16 | Cenários de teste | PENDENTE | Escolher quantidade de dias e perfis |
| 8 | 4 | Fator de CO2 (tarifa já resolvida) | PARCIAL | Baixar o fator do SIRENE; confirmar Enel SP por uma conta de energia |
| 9 | 8 | Implementação atual e integração da ARIA | PENDENTE | Victor informar como a ARIA funciona hoje |
| 10 | 21 | ARIA na gravação do vídeo | PENDENTE | Verificar dependência de API externa e plano alternativo |
| 11 | 20 | Framework do dashboard | PENDENTE | Escolher a biblioteca do front-end |
| 12 | - | Validação do grupo dos itens do README em PROPOSTA | PENDENTE | Grupo revisar a lista da seção 5 |
| 13 | 11 | Pesquisa sobre regulação | PENDENTE | Consultar fonte oficial |

Pontos concluídos (detalhe em 9.5): 22, 19, 1, 3, 6, 7, 9, 10, 12, 13 e 14. O ponto 18 também está resolvido (texto em 9.2).

### 9.1 Crítico: decidir ou resolver agora

2. PARCIAL, responsável por README, diagramas, organização do repositório e .txt. DECIDIDO em 2026-10-17: o README é do Victor (escrito com o Claude). Continuam sem dono: diagramas e .txt de entrega. Código com Victor e Gabriel Cavaloti (sem divisão fixa de obrigações; o Victor atribui tarefas ao Gabriel quando necessário); gravação e edição do vídeo com Lucas Galle Melchior e Davi Ramos. Falta definir quem fica com README, diagramas, repositório e .txt (sugestão: Lucas e Davi, já que o código sobrecarrega Victor e Gabriel). Por que é crítico: o README, os diagramas e o .txt têm dono indefinido e os diagramas precisam de imagens reais do sistema (enunciado, seção 1).

15. PARCIAL, dados públicos. DECIDIDO em 2026-10-13 e fontes aprovadas pelo Victor em 2026-10-17: dados públicos nos perfis de geração solar (INMET, estação automática A701 Mirante de Santana) e de consumo (conjunto residencial público ECD-UY, do Uruguai; alternativa: curva de carga horária do ONS). Script de geração pronto e testado só com arquivo sintético: `scripts/preparar_geracao_inmet.py`. PENDENTE: baixar os ZIPs do INMET para `dados/brutos/inmet/` e rodar o script; baixar o subconjunto THC da ECD-UY e escrever o script de consumo depois de conferir o formato real do arquivo (nome dos arquivos e primeiras linhas). Enquanto os dados não forem processados, o README usa curvas sintéticas. Risco que motivou a decisão: se o simulador gera os dados e o modelo de previsão aprende com eles, o erro de previsão fica artificialmente baixo e a banca pode questionar. Por que é crítico: o simulador e a previsão dependem desses perfis, e o download é manual. DECISÃO PENDENTE do Victor (2026-10-17): a ECD-UY não é essencial; a sugestão é usar o INMET agora e começar o consumo com a curva sintética da seção 4.3 do README, com ruído e variação entre dia útil e fim de semana, deixando a ECD-UY como melhoria opcional. O intervalo de amostragem e o formato dos arquivos da ECD-UY não estão confirmados.

5. PARCIAL, método de previsão. Em 2026-10-20 a persistência (leitura atual como estimativa do passo seguinte) foi implementada em `engine/dispatch.py`; o método final (média móvel por hora) e o cálculo do MAE continuam em aberto. Persistência, média móvel por hora e regressão linear foram explicados ao Victor. Sugestão: média móvel por hora como método principal e persistência como comparação (precisa de 7 dias de histórico real, que o script do INMET lista). Por que é crítico: o motor de decisão não pode ser escrito sem essa escolha, e a previsão é um dos algoritmos inteligentes exigidos.

### 9.2 Alto: necessário para o sistema integrado e para os resultados

Atualização em 2026-10-19: implementação inicial dos pontos 17/18 em `marketplace/matching.py`, com regra de preço médio sujeita à validação do grupo. Valor de exportação e integração com o motor continuam pendentes.

No ponto 23, marketplace e validador possuem testes unitários; comando no README 13. Simulador, backend e testes integrados continuam pendentes. Os registros abaixo mantêm as demais decisões e pendências.

17. PARCIAL, formação de preço no marketplace. Em 2026-10-19 o Gabriel implementou em `marketplace/matching.py` o preço médio entre piso e teto, com negociação só quando piso < teto (README, seção 6). Modelo físico DECIDIDO: `financial_only`. PENDENTE: o piso (valor da energia exportada) e o SCEE. Texto original do ponto: O README define piso e teto, mas não como vendedor e comprador escolhem o preço dentro da faixa (ponto médio fixo ou dinâmico por oferta e demanda). Também definir como modelar o piso: no Brasil, a energia injetada na rede por geração distribuída costuma virar crédito de energia (sistema de compensação) e não pagamento em dinheiro. Verificar em fonte oficial. Observação: o arquivo da ANEEL traz, para a mesma distribuidora, linhas com detalhe SCEE (Sistema de Compensação de Energia Elétrica) em que a TE é de 37,36 R$/MWh nos três postos, com a mesma TUSD das demais linhas. O significado exato para modelar o valor da energia exportada não foi confirmado e precisa ser entendido antes de definir o piso do marketplace. Bloqueia o código do marketplace (que é o diferencial do projeto).

18. RESOLVIDO em 2026-10-19 (implementado em `marketplace/matching.py`: o comprador só negocia se o preço for menor que a tarifa da rede; transporte pela rede não modelado, declarado na seção 11 do README). Texto original do ponto: Definir por que um carro compra de um vizinho em vez de usar o carregador próprio ou a rede (por exemplo, compra quando o preço é menor que a tarifa da rede) e se o custo de uso da rede para transportar a energia é ignorado (e declarado como limitação) ou modelado. Decidir junto com o ponto 17.

23. PARCIAL, execução e testes. Em 2026-10-19 o Gabriel adicionou `engine/validation.py` (balanço, SOC e limites de potência por passo) e `tests/` (unittest) do marketplace e da validação; o comando de execução dos testes já está no README, seção 13 (`python -m unittest discover -s tests -v`, testado com Python 3.12 segundo o registro do README); faltam a seção de como executar o sistema completo (Docker Compose, portas, versões) e os testes integrados com simulador e backend. Texto original do ponto (a dupla do código, Victor e Gabriel, cuida disso; o Victor envia instruções ao Gabriel quando necessário, sem atribuir cada tarefa pequena de antemão, DECIDIDO em 2026-10-17). O README ainda não tem seção de como executar (comando do Docker Compose, versões de Node e Python, portas) nem critérios de aceitação. Sugestão a validar: carro atinge o SOC alvo em 100% dos dias simulados; bateria nunca viola o SOC mínimo e máximo; o balanço de energia fecha a cada passo dentro de uma tolerância; o comparativo é reproduzível com a mesma semente. Os critérios de aceitação são o que prova o "funcional" dos 60 pontos.

16. PENDENTE, cenários de teste. Quantos dias simulados e quais perfis (ensolarado, parcialmente nublado, chuvoso; dia útil e fim de semana). A seção 10 do README prevê "porcentagem de dias em que o carro atingiu o SOC alvo", o que exige vários dias. A classificação de dias gerada pelo script do INMET (`dias_sp_classificados.csv`) já fornece as classes; falta escolher a quantidade.

4. PARCIAL, tarifa e CO2. Caminho definido: a tarifa vem do CSV "tarifas-homologadas-distribuidoras-energia-eletrica" do portal de dados abertos da ANEEL (atualização semanal), filtrando pelo CNPJ da Enel SP (61695227000193; no arquivo o nome pode aparecer como Eletropaulo, e a busca por "ENEL SP" não retornou resultado), modalidade Branca, subgrupo B1, classe residencial, base tarifária "Tarifa de Aplicação" e vigência mais recente (o reajuste de 2026 vale a partir de 04/07/2026), somando TE e TUSD (R$/MWh dividido por 1000); o CO2 vem do fator médio mensal do SIN no SIRENE (MCTI). TARIFA RESOLVIDA: valores de 04/07/2026 a 03/07/2027 extraídos em 2026-10-12 com `scripts/extrair_tarifa_enel_sp.py` (sigla ELETROPAULO no arquivo) e registrados no README (seção 5.3); os valores provisórios de fonte secundária foram descartados. PENDENTE: baixar o fator de CO2 mais recente do SIRENE (necessário para a métrica de CO2 dos resultados; regra de trabalho da seção 8 proíbe usar valor sem fonte oficial) e confirmar Enel SP como distribuidora de referência (por uma conta de energia). Ordem de grandeza confirmada em reportagens, não no SIRENE: 21,5 a 28,9 kg CO2/MWh por mês nos primeiros meses de 2025 e 38,5 kg CO2/MWh em 2023; o fator é baixo, e a redução de CO2 em kg será pequena frente à economia em reais.

8. PENDENTE, como a ARIA está implementada hoje e como será integrada (contrato da API HTTP). O Victor informará depois. A integração com assistente virtual é critério do enunciado.

21. PENDENTE, ARIA na demonstração. Verificar se depende de API de modelo de linguagem (chave, custo, internet durante a gravação) e definir um plano alternativo para a gravação do vídeo. Resolver junto com o ponto 8.

### 9.3 Médio: qualidade e decisões de apoio

20. PENDENTE, dashboard. Framework ou biblioteca do front-end e do diagrama de fluxo de energia (o README diz apenas "página web"). Quem construir o dashboard precisa dominar a escolha. É a parte visual do vídeo; decidir antes de começar o front-end.

Validação do grupo dos itens do README que estão como PROPOSTA (lista na seção 5, abaixo da tabela de decisões), incluindo os parâmetros numéricos da seção 4.3 definidos pelo Claude. Sem validação, o grupo pode divergir do que foi documentado.

### 9.4 Baixo: refinamento

11. PENDENTE, pesquisa em fonte oficial sobre a regulação de venda de energia entre particulares no Brasil, para refinar a seção 11 do README. O marketplace já está declarado como simulação acadêmica; a pesquisa apenas melhora o texto (e pode ajudar no ponto 17).

### 9.5 Concluídos

19. RESOLVIDO em 2026-10-17: corte de escopo, na ordem em que os blocos caem se faltar tempo: 1) simulador, motor e comparativo; 2) dashboard; 3) marketplace; 4) ARIA integrada. Aceita entrega parcial de um bloco (por exemplo, marketplace só como regra no motor, sem tela própria). Base: 60 dos 100 pontos dependem de o sistema funcionar (seção 2), e o núcleo é o que prova isso.

22. RESOLVIDO em 2026-10-17: repositório na conta do Victor, público (o link do .txt abre para o professor); comentários em português; nomes de arquivos e pastas e campos JSON em inglês; mensagens de commit em inglês; commits direto na `main` (se o Victor criar uma branch, ele avisa ao fazer o checkout); Gabriel Cavaloti commita com a própria conta; `CONTEXT.md` público com as notas internas. Ação do Victor: adicionar o Gabriel como colaborador no GitHub (Settings, Collaborators).
1. RESOLVIDO: entrega em 2026-10-23 (sexta-feira). Restou apenas confirmar se as duas sprints de tema livre têm a mesma data.
3. RESOLVIDO: valores definidos pelo Claude a pedido do Victor (README, seção 4.3), com carregador da linha HCA G2, bateria Lynx F G2 e inversor ET G2. Falta validação do grupo (ver 9.3).
6. RESOLVIDO: começar com 3 casas e ampliar até 10 se houver tempo.
7. RESOLVIDO: Python; Node.js apenas no backend.
9. RESOLVIDO: Pensamento Computacional e Automação com Python; Soluções em Energias Renováveis e Sustentáveis (README, seção 9). Conferir se os conceitos citados na seção 9 batem com a ementa de cada disciplina. Candidatos considerados antes: estruturas de dados e algoritmos (fila de prioridade no casamento de ordens), modelagem e previsão (regressão), banco de dados (histórico e livro-razão), arquitetura de computadores (sensores e comunicação, se aplicável).
10. RESOLVIDO: o grupo não possui credencial; a SEMS Open API não será usada.
12. RESOLVIDO: Victor Hugo Ferreira Freire (RM 571099), registrado no README e neste arquivo.
13. RESOLVIDO: não há divisão fixa de obrigações entre Victor e Gabriel Cavaloti; o Victor atribui tarefas ao Gabriel quando necessário. O formato do comando de retorno ao simulador e a lista de endpoints da API (README, seções 3.4 a 3.6 e 4.2) seguem como proposta, sem etapa de validação entre papéis.
14. RESOLVIDO na seção 4.3 do README (valores definidos pelo Claude, falta validação do grupo); itens cobertos: capacidade da bateria do carro em kWh (acrescentada ao contrato JSON como `ev.capacity_kwh`), eficiência de carga e descarga da bateria, SOC mínimo e máximo da bateria, perdas do carregador, e quais casas têm carro, bateria e qual tamanho de painel.

## Histórico de alterações

| Data | Alteração |
|---|---|
| 2026-10-11 | Criação a partir do README original, separando contexto e documentação técnica |
| 2026-10-11 | README: adicionados ciclo de execução, modos de execução, API do backend e comando de retorno ao simulador |
| 2026-10-11 | Pontos em aberto 14 a 23 adicionados após revisão; corrigida no README (seção 6) uma referência circular na definição de vendedor |
| 2026-10-11 | Respostas do Victor registradas (pontos 1 a 3, 6, 7, 9 e 10); plano reescrito em calendário até 2026-10-23; README: parâmetros de simulação (4.3), disciplinas (9), HCA G2 e Lynx F G2 (7.1) |
| 2026-10-12 | README: potência da bateria passou a seguir a ficha técnica da Lynx F G2 (2,24 kW por módulo, limitada ao inversor); referências a HCA G2 e Lynx F G2 uniformizadas no texto e no diagrama |
| 2026-10-12 | README (seção 5.3): postos horários da Enel SP e fontes de tarifa (ANEEL) e de CO2 (MCTI); ponto em aberto 4 com o caminho para obter os valores |
| 2026-10-12 | Tarifa branca da Enel SP extraída da base da ANEEL e registrada no README (seção 5.3); limitação de tarifas sem tributos adicionada à seção 11; observação sobre linhas SCEE no ponto 17 |
| 2026-10-12 | README: referências de tarifa e CO2 adicionadas à seção 12 e limitação sobre o fator de emissão baixo na seção 11; CONTEXT: ordem de grandeza do fator de CO2 no ponto 4 |
| 2026-10-13 | Nome completo do Victor registrado; fim da divisão A/B na dupla do código; decisão de usar dados públicos nos perfis (ponto 15) registrada, com as fontes ainda em proposta |
| 2026-10-17 | Fontes aprovadas (INMET A701 e ECD-UY); criados `scripts/preparar_geracao_inmet.py`, `dados/` e regra no .gitignore para `dados/brutos/` |
| 2026-10-17 | Seção 9 reorganizada por prioridade e gravidade (crítico, alto, médio, baixo, concluídos), mantendo a numeração original |
| 2026-10-17 | Pontos 2 e 22 atualizados: README do Victor; repositório público na conta do Victor, comentários em português, commits em inglês |
| 2026-10-17 | Branches: commits na `main`; execução e testes (23) ficam com Victor e Gabriel sem atribuição prévia de tarefas; README: intervalo de amostragem da ECD-UY marcado como a confirmar |
| 2026-10-17 | Seção 9: tabela-resumo com ordem de importância e situação de cada ponto; ponto 22 movido para concluídos; decisão pendente sobre a ECD-UY registrada no ponto 15 |
| 2026-10-19 | Análise do código do Gabriel (marketplace, validação, testes); modelo `financial_only` decidido; pontos 17 (parcial), 18 (resolvido) e 23 (parcial) atualizados; README: seção 6, 4.2, 11 e estrutura com `tests/` |
| 2026-10-19 | Repositório preparado: CSVs movidos para `dados/brutos/aneel/` e `dados/processados/`, script da tarifa ajustado, `.gitignore` completo (Node, .env, .venv), pastas `simulator/`, `adapter/`, `backend/`, `dashboard/`, `docs/` e `dados/*` criadas com `.gitkeep` |
| 2026-10-20 | Criado `.env.example` (backend, Redis, MySQL, motor, simulador, adaptador, marketplace, tarifas e CO2, dashboard, ARIA); nomes das variáveis são proposta; fator de CO2 e piso do marketplace ficam vazios até os pontos 4 e 17 serem resolvidos; README: estrutura com `.env.example` |
| 2026-10-20 | Passos 1 a 5 do código: `simulator/` (config, house, scenario), `engine/` (tariff, dispatch, metrics), `scripts/comparar_cenarios.py` e `tests/test_scenario.py`; README: seções 5.1, 5.2 e 13 |
| 2026-10-20 | Passo 6: marketplace do Gabriel ligado ao simulador por passo (`marketplace/settlement.py`); `HouseMetrics` com kWh vendidos e comprados e ganho do marketplace; comparativo com colunas do marketplace e `--sem-marketplace`; 3 testes novos; README: seções 5.4, 6 e 13. Ganho depende do valor da exportação (premissa R$ 0,00/kWh, ponto 17 em aberto) |
| 2026-10-20 | `preparar_geracao_inmet.py` corrigido (só horas de sol, mínimo de 11 em 12) e executado pelo Victor sobre os dados reais: 609 dias válidos (206 ensolarados, 310 parcialmente nublados, 93 chuvosos); gerados `perfil_solar_sp.csv` e `dias_sp_classificados.csv` em `dados/processados/` |
| 2026-10-20 | Radiação real no simulador: `simulator/solar.py`; `--clima` aceita datas AAAA-MM-DD (INMET) além das classes sintéticas; 3 testes novos (2 dependem do `perfil_solar_sp.csv`) |
| 2026-10-20 | Seção 8.1: próximos passos do código, repasse ao Gabriel (API) e itens restantes por prioridade; resultado parcial com radiação real |
| 2026-10-17 | Ponto 19 resolvido (ordem de corte de escopo); ponto 22: nomes de arquivos mantidos em inglês, Gabriel commita com a própria conta, `CONTEXT.md` público; restou só a convenção de branches |
