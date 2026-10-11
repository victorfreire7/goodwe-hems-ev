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

Equipe: Davi Ramos (RM 571744), Lucas Galle Melchior (RM 574027), Victor (RM 571099), Gabriel Cavaloti (RM 571643).

Divisão em duas duplas (DECIDIDO): duas pessoas no código e duas no vídeo e na documentação. Quem está em qual dupla: PENDENTE. A distribuição abaixo é PROPOSTA.

| Papel | Dupla | Responsabilidade |
|---|---|---|
| A (proposta: Victor, por perfil backend) | Código | Simulador, adaptador GoodWe, backend Node/TypeScript, Redis, MySQL, Docker Compose |
| B | Código | Motor de decisão, previsão, comparativo antes/depois, marketplace, dashboard, integração com a ARIA |
| C | Vídeo | Roteiro de 5 minutos, gravação da demonstração, edição, upload no YouTube como não listado |
| D | Documentação | README final, diagramas, organização do repositório GitHub, arquivo .txt de entrega |

Observação de carga: o papel B concentra o diferencial técnico (algoritmo e marketplace) e a parte visual que aparece no vídeo. A dupla do vídeo pode apoiar o layout do dashboard, sem alterar a lógica.

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

Itens do README que ainda são PROPOSTA e precisam de validação do grupo: formato JSON do simulador, passo de simulação de 15 minutos, regras de despacho do motor, regras de preço e casamento do marketplace, stack e estrutura de pastas do repositório, modelo GW7K-HCA como carregador simulado.

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
| Semana 1 | Escopo fechado; contrato JSON do simulador validado entre A e B; valores numéricos do simulador definidos; estrutura do README e diagramas iniciados pela dupla do vídeo; roteiro iniciado | Contrato JSON aprovado |
| Semanas 2 e 3 | Simulador, adaptador, backend, motor de decisão, marketplace e dashboard em construção | Primeiro fluxo completo (simulador, motor, dashboard), mesmo simples |
| Última semana | Congelar o código; rodar os cenários com e sem otimização; gravar o vídeo; preencher resultados no README; montar o .txt de entrega | Arquivo .txt enviado dentro do prazo |

Regras de trabalho: nenhum número entra na seção de resultados sem ter sido gerado pelo sistema; nenhum valor de tarifa ou fator de emissão de CO2 é usado sem fonte oficial citada.

## 9. Pontos em aberto

1. Data exata de entrega.
2. Quem fica em qual papel (A, B, C, D).
3. Valores numéricos do simulador e modelos GoodWe de referência escolhidos.
4. Valores de tarifa por horário e fator de emissão de CO2, com fonte oficial.
5. Método de previsão (média móvel por hora, regressão ou outro).
6. Quantidade de casas no marketplace (sugestão: de 3 a 10).
7. Linguagem do simulador (Python ou Node.js).
8. Como a ARIA está implementada hoje e como será integrada (contrato da API HTTP).
9. Disciplina que avalia esta sprint e conteúdos que o projeto usa (seção 9 do README). Candidatos: estruturas de dados e algoritmos (fila de prioridade no casamento de ordens), modelagem e previsão (regressão), banco de dados (histórico e livro-razão), arquitetura de computadores (sensores e comunicação, se aplicável).
10. Existência de credencial para a SEMS Open API.
11. Pesquisa em fonte oficial sobre a regulação de venda de energia entre particulares no Brasil, para refinar a seção 11 do README.
12. Nome completo do Victor para o arquivo .txt e para o README.

## Histórico de alterações

| Data | Alteração |
|---|---|
| 2026-10-11 | Criação a partir do README original, separando contexto e documentação técnica |
