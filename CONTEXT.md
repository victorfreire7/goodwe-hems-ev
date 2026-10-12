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

Divisão em duas duplas (DECIDIDO em 2026-10-11): código com Victor e Gabriel Cavaloti; gravação e edição do vídeo com Lucas Galle Melchior e Davi Ramos. Falta definir quem faz cada papel dentro da dupla e quem fica com README, diagramas, organização do repositório e .txt de entrega. A distribuição de papéis abaixo é PROPOSTA.

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
| 2026-10-11 | Data de entrega: 2026-10-23 (sexta-feira) | DECIDIDO |
| 2026-10-11 | Dupla do código: Victor e Gabriel Cavaloti. Dupla do vídeo (gravação e edição): Lucas Galle Melchior e Davi Ramos | DECIDIDO |
| 2026-10-11 | Simulador em Python; Node.js apenas no backend | DECIDIDO |
| 2026-10-11 | Demonstração começa com 3 casas e é ampliada até 10 | DECIDIDO |
| 2026-10-11 | Carregador simulado: linha HCA G2 (GW7K-HCA-20) | DECIDIDO |
| 2026-10-11 | Disciplinas: Pensamento Computacional e Automação com Python; Soluções em Energias Renováveis e Sustentáveis | DECIDIDO |
| 2026-10-11 | Sem credencial da SEMS Open API: adaptador implementa apenas o modo simulado nesta entrega | PROPOSTA |
| 2026-10-11 | Valores numéricos do simulador definidos pelo Claude a pedido do Victor (README, seção 4.3) | PROPOSTA (falta validação do grupo) |

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

## 9. Pontos em aberto

1. RESOLVIDO: entrega em 2026-10-23 (sexta-feira). Confirmar se as duas sprints de tema livre têm a mesma data.
2. PARCIAL: código com Victor e Gabriel Cavaloti; gravação e edição do vídeo com Lucas Galle Melchior e Davi Ramos. Falta definir quem faz A e B, quem faz C e D, e quem fica com README, diagramas, repositório e .txt (sugestão: Lucas e Davi, já que o código sobrecarrega Victor e Gabriel).
3. RESOLVIDO: valores definidos pelo Claude a pedido do Victor (README, seção 4.3), com carregador da linha HCA G2, bateria Lynx F G2 e inversor ET G2. Falta validação do grupo.
4. Valores de tarifa por horário e fator de emissão de CO2, com fonte oficial. O Victor informará depois.
5. Método de previsão: persistência, média móvel por hora e regressão linear foram explicados ao Victor. Decisão pendente; sugestão: média móvel por hora como método principal e persistência como comparação.
6. RESOLVIDO: começar com 3 casas e ampliar até 10 se houver tempo.
7. RESOLVIDO: Python; Node.js apenas no backend.
8. Como a ARIA está implementada hoje e como será integrada (contrato da API HTTP). O Victor informará depois.
9. RESOLVIDO: Pensamento Computacional e Automação com Python; Soluções em Energias Renováveis e Sustentáveis (README, seção 9). Conferir se os conceitos citados na seção 9 batem com a ementa de cada disciplina. Candidatos considerados antes: Candidatos: estruturas de dados e algoritmos (fila de prioridade no casamento de ordens), modelagem e previsão (regressão), banco de dados (histórico e livro-razão), arquitetura de computadores (sensores e comunicação, se aplicável).
10. RESOLVIDO: o grupo não possui credencial; a SEMS Open API não será usada.
11. Pesquisa em fonte oficial sobre a regulação de venda de energia entre particulares no Brasil, para refinar a seção 11 do README.
12. Nome completo do Victor para o arquivo .txt e para o README.
13. Validação entre os papéis A e B do formato do comando de retorno ao simulador e da lista de endpoints da API (README, seções 3.4 a 3.6 e 4.2).
14. RESOLVIDO na seção 4.3 do README (valores definidos pelo Claude, falta validação do grupo); itens cobertos: capacidade da bateria do carro em kWh (usada na regra 2 do motor, mas ausente do contrato JSON da seção 4.1; acrescentar `ev.capacity_kwh`), eficiência de carga e descarga da bateria, SOC mínimo e máximo da bateria, perdas do carregador, e quais casas têm carro, bateria e qual tamanho de painel (casas homogêneas ou não).
15. Fonte dos perfis de geração solar e de consumo: a seção 4.3 do README adota curvas sintéticas na primeira versão; decidir se mantém ou usa dados públicos (irradiação solar de São Paulo, perfil residencial). Risco: se o simulador gera os dados e o modelo de previsão aprende com eles, o erro de previsão fica artificialmente baixo e a banca pode questionar. Mitigação possível: ruído, dias de clima diferentes ou dados externos.
16. Cenários de teste: quantos dias simulados e quais perfis (ensolarado, parcialmente nublado, chuvoso; dia útil e fim de semana). A seção 10 do README prevê "porcentagem de dias em que o carro atingiu o SOC alvo", o que exige vários dias.
17. Formação de preço no marketplace: o README define piso e teto, mas não como vendedor e comprador escolhem o preço dentro da faixa (ponto médio fixo ou dinâmico por oferta e demanda). Também definir como modelar o piso: no Brasil, a energia injetada na rede por geração distribuída costuma virar crédito de energia (sistema de compensação) e não pagamento em dinheiro. Verificar em fonte oficial.
18. Perfil do comprador no marketplace: definir por que um carro compra de um vizinho em vez de usar o carregador próprio ou a rede (por exemplo, compra quando o preço é menor que a tarifa da rede) e se o custo de uso da rede para transportar a energia é ignorado (e declarado como limitação) ou modelado.
19. Corte de escopo: ordem de prioridade se faltar tempo. Sugestão a validar: 1) simulador, motor e comparativo; 2) dashboard; 3) marketplace; 4) ARIA integrada.
20. Dashboard: framework ou biblioteca do front-end e do diagrama de fluxo de energia (o README diz apenas "página web"). O papel B precisa dominar a escolha.
21. ARIA na demonstração: verificar se depende de API de modelo de linguagem (chave, custo, internet durante a gravação) e definir um plano alternativo para a gravação do vídeo.
22. Repositório: conta dona do repositório, visibilidade (se for privado, o professor precisa de acesso, senão o link do .txt não abre), convenção de branches e commits (commits em inglês), idioma do código e dos comentários, e se cada integrante commita com a própria conta para o histórico mostrar a contribuição de todos.
23. Execução e testes: o README ainda não tem seção de como executar (comando do Docker Compose, versões de Node e Python, portas) nem critérios de aceitação. Sugestão a validar: carro atinge o SOC alvo em 100% dos dias simulados; bateria nunca viola o SOC mínimo e máximo; o balanço de energia fecha a cada passo dentro de uma tolerância; o comparativo é reproduzível com a mesma semente.

## Histórico de alterações

| Data | Alteração |
|---|---|
| 2026-10-11 | Criação a partir do README original, separando contexto e documentação técnica |
| 2026-10-11 | README: adicionados ciclo de execução, modos de execução, API do backend e comando de retorno ao simulador |
| 2026-10-11 | Pontos em aberto 14 a 23 adicionados após revisão; corrigida no README (seção 6) uma referência circular na definição de vendedor |
| 2026-10-11 | Respostas do Victor registradas (pontos 1 a 3, 6, 7, 9 e 10); plano reescrito em calendário até 2026-10-23; README: parâmetros de simulação (4.3), disciplinas (9), HCA G2 e Lynx F G2 (7.1) |
| 2026-10-12 | README: potência da bateria passou a seguir a ficha técnica da Lynx F G2 (2,24 kW por módulo, limitada ao inversor); referências a HCA G2 e Lynx F G2 uniformizadas no texto e no diagrama |
