# FORCEIA PRODUCT LANGUAGE

**Constituição visual e verbal da plataforma**  
Versão 1.0 · Agosto 2026  
Status: **Fonte de verdade** — nenhuma tela nova pode ser criada fora deste documento.

---

## 0. Propósito deste documento

Este arquivo define a **personalidade do produto**.

Não é um guia de Tailwind.  
Não é uma lista de componentes.  
É a linguagem com que a ForceIA se apresenta ao mundo.

Toda decisão de interface, copy, motion e hierarquia deve responder a:

> Isto reforça que existe uma equipe de IA comercial trabalhando agora — ou parece um CRM genérico?

Se a resposta for a segunda, a decisão está errada.

---

## 1. Posicionamento de produto

### O que a ForceIA é

A ForceIA **implanta equipes comerciais com IA**.

O cliente não configura funis, sequências ou cadências.  
A ForceIA opera isso. O cliente **acompanha e intervém quando necessário**.

### O que a ForceIA não é

| Não é | Por quê |
|-------|---------|
| CRM | Não organiza contatos como objeto central |
| Inbox de suporte | Não é fila de tickets humanos |
| Analytics dashboard | Métricas servem à narrativa, não a substituem |
| Chatbot UI | Agentes não são “bots de conversa” genéricos |
| Admin panel | Não é painel de configuração administrativa |

### Sensação-alvo

> “Minha equipe de IA está trabalhando neste momento.”

Enterprise · AI-native · Premium · Técnica · Minimalista · Operacional.

---

## 2. Tom de voz

### Personalidade

A ForceIA fala como um **chefe de operações precisas**:

- Calma sob pressão  
- Direta, sem floreio  
- Confiante, sem arrogância  
- Técnica, sem jargão vazio  
- Humana na interrupção, mecânica na operação  

### Princípios de copy

1. **Frases curtas.** Uma ideia por linha.  
2. **Verbos de operação.** “Qualificou”, “agendou”, “recuperou” — não “atualizou o registro”.  
3. **Tempo presente ou passado imediato.** A operação é agora.  
4. **Sem marketing na UI autenticada.** Zero “revolucione suas vendas”.  
5. **Sem culpa no usuário.** Falhas são do fluxo ou do sistema, não do cliente.  

### Exemplos

| Evitar | Preferir |
|--------|----------|
| “Nenhum dado encontrado” | “Nenhuma atividade ainda hoje” |
| “Erro ao carregar” | “Não foi possível atualizar a operação. Tente de novo.” |
| “Seu pipeline está aquecido!” | “+R$ 48.000 em pipeline nas últimas 4h” |
| “Bem-vindo de volta, João! 🚀” | “Operação ao vivo · Clínica Sol” |
| “Clique aqui para continuar” | “Abrir conversa” / “Assumir” |

### Como a IA “fala” na interface

A IA **não conversa com o usuário** no painel como um assistente chatty.

A IA **reporta**:

- O que fez  
- O que está fazendo  
- O que precisa de humano  

Tom de relatório operacional, não de chatbot amigável.

### Como o usuário fala com a IA

No Painel Cliente, o usuário **não treina** a IA.

Ele:

- Observa  
- Aprova ou assume handoffs  
- Navega conversas e agenda  

Linguagem de ação: **Assumir · Abrir · Confirmar · Descartar** — nunca “Enviar prompt”.

---

## 3. Naming e terminologia

### Nome do produto

- **ForceIA** (sempre junto, F e IA maiúsculos)  
- Em UI autenticada: preferir o nome da **operação** (empresa do cliente) no header; ForceIA no logo/mark  

### Agentes (sempre estes três nomes)

| Nome oficial | Função em uma linha |
|--------------|---------------------|
| **SDR IA** | Prospecção e qualificação |
| **Closer IA** | Negociação e avanço de oportunidade |
| **Follow-up IA** | Recuperação e nutrição |

Nunca: “Bot 1”, “Assistant”, “Agent Alpha”.  
Nunca pluralizar de forma vaga (“os bots”). Usar **equipe de IA** ou os nomes.

### Vocabulário operacional (canônico)

| Termo ForceIA | Significado | Evitar |
|---------------|-------------|--------|
| **Operação** | Workspace / conta em execução | “Conta”, “Tenant” na UI |
| **Equipe de IA** | Os três agentes juntos | “Robôs”, “Automações” |
| **Em operação** | Agente ativo processando | “Online”, “Available” |
| **Handoff** | Caso que exige humano | “Ticket”, “Escalation” genérico |
| **Precisa de você** | Fila de handoffs | “Pendências”, “Inbox” |
| **Qualificado** | Lead que passou critério BANT/ICP | “Won lead” |
| **Pipeline** | Valor gerado em oportunidades | “Revenue” solto |
| **Ops log** | Linha do tempo do que a IA fez | “Activity feed” de CRM |
| **Assumir** | Humano toma a conversa | “Claim”, “Take over” em PT-BR solto |

### Códigos mono (assinatura verbal visual)

Usar em logs e timestamps, sempre IBM Plex Mono:

| Código | Evento |
|--------|--------|
| `QUAL` | Qualificação |
| `MTG` | Reunião |
| `FUP` | Follow-up |
| `HO` | Handoff |
| `MSG` | Mensagem |
| `PIPE` | Movimentação de pipeline |

---

## 4. Hierarquia de informação

### Ordem mental em qualquer tela principal

1. **Estado da operação** (está viva? saudável?)  
2. **Quem está trabalhando** (equipe de IA)  
3. **O que exige humano** (interrupções)  
4. **O que mudou** (prova / tendência)  
5. **Detalhe** (listas, tabelas, histórico)  

### Regras

- A IA nunca fica “no rodapé”.  
- Métricas nunca competem com a narrativa principal.  
- Handoffs, quando existem, têm prioridade visual sobre gráficos.  
- Empty states explicam o **estado da operação**, não a ausência de rows.

---

## 5. Princípios de UX

1. **Operação > configuração** — o cliente observa e intervém; não monta o sistema.  
2. **Interrupção clara** — quando o humano é necessário, a UI muda de tom (warning), não só de número.  
3. **Densidade com ar** — informação alta, ornamentação baixa.  
4. **Uma ação primária por contexto** — Assumir, Abrir, Confirmar.  
5. **Feedback local** — loading e erro no objeto, não modal global.  
6. **Sem surpresa destrutiva** — ações irreversíveis pedem confirmação explícita.  
7. **Teclado e foco** — toda ação crítica alcançável sem depender só de hover.  
8. **Mobile** — narrativa e handoffs primeiro; gráficos depois.

---

## 6. Identidade visual — assinaturas

Mesmo **sem o logo**, a ForceIA deve ser reconhecível por:

1. **Rail cyan** (2px) em superfícies de operação ao vivo  
2. **Agent Stage** — três agentes como processos, não avatares de usuário  
3. **Códigos mono** QUAL / MTG / FUP / HO  
4. **Pulse verde** + label “Em operação”  
5. **Process bar** fina sob cada agente  
6. **“Precisa de você”** como nome da fila de handoff  
7. **Brief operacional** — uma frase do que a equipe fez hoje  

Se uma tela nova não carregar ao menos parte dessas assinaturas onde fizer sentido, ela não está na linguagem ForceIA.

---

## 7. Cores

### Base (monocromática)

| Token | Hex | Uso |
|-------|-----|-----|
| Background | `#090909` | Shell |
| Canvas | `#0E0E0E` | Superfícies de conteúdo |
| Surface | `#141414` | Hover, elevação leve |
| Elevated | `#1A1A1A` | Chips, inputs |
| Border | `#232323` | Divisores |
| Ink | `#F5F5F5` | Texto primário |
| Ink muted | `#A7A7A7` | Secundário |
| Ink soft | `#707070` | Meta, labels |

### Semântica (só significado)

| Token | Hex | Uso exclusivo |
|-------|-----|----------------|
| **Brand** | `#05B5DB` | IA ativa, links, foco, rail de operação |
| **Success** | `#0DA387` | Live, confirmado, delta positivo |
| **Warning** | `#DD6539` | Handoff, atenção humana |
| **AI** | `#9B95FE` | Eventos de agente / follow-up (sparingly) |
| **Danger** | `#E5484D` | Erro destrutivo, prioridade alta crítica |

### Regras

- Brand **não** pinta botões primários de formulário por padrão (CTA neutro).  
- Brand marca **presença de IA**, não “sucesso de marketing”.  
- Nunca gradiente roxo/rosa “AI hype”.  
- Nunca cor só por estética.

---

## 8. Tipografia

### Famílias

- **UI:** Inter (400 / 500 / 600)  
- **Dados:** IBM Plex Mono (400 / 500) — métricas, códigos, horários, deltas  

### Escala (somente estes papéis)

| Papel | Tamanho | Peso | Uso |
|-------|---------|------|-----|
| title | 14px | 500 | Nome da operação / página |
| section | 13px | 500 | Header de painel |
| body | 13px | 400–500 | Título de linha |
| body-muted | 12px | 400 | Descrição |
| meta | 11px | 400 | Meta secundária |
| label | 10px | 500 | Uppercase tracking largo |
| metric | 20px | 500 mono | KPI principal |
| metric-sm | 16px | 500 mono | KPI aninhado |
| mono | 11px | 400 mono | Códigos, horas |
| badge | 10px | 500 | Badges |

Proibido inventar tamanhos fora desta escala.

---

## 9. Espaçamento e grid

- Base **4px**  
- Header de painel: altura 36px, padding horizontal 12px  
- Linha de lista: padding 8–12px  
- Gaps de seção: 8–12px  
- Densidade alta; não “respirar” como landing page  

---

## 10. Radius, borda, sombra

- Radius padrão de controle: **4px (sm)**  
- Painéis: **0–2px**  
- Bordas 1px  
- **Sem sombra de card**  
- Foco: ring brand 2px  

---

## 11. Ícones

- Biblioteca única: **Lucide**  
- Stroke **1.75**  
- Tamanhos: 12 / 14 / 16 / 20  
- Nunca emoji como ícone de UI  
- Nunca misturar outra família de ícones  

---

## 12. Componentes exclusivos da linguagem

| Componente | Função |
|------------|--------|
| **OpsBrief** | Narrativa do dia + rail + pulse |
| **AgentStage** | Equipe de IA em operação |
| **InterruptLane** (“Precisa de você”) | Handoffs humanos |
| **OpsLog** | Linha do tempo com códigos mono |
| **ProcessBar** | Carga visual do agente |
| **StatusPulse** | Indicador live |

---

## 13. Estados da IA

| Estado | Visual | Copy |
|--------|--------|------|
| **Em operação** | Pulse verde + process bar brand + rail cyan | “Em operação” / “processando” / “live” |
| **Pausado** | Dot warning, bar curta | “Pausado” |
| **Offline** | Dot soft, bar mínima | “Offline” |
| **Handoff pendente** | Interrupt lane com borda warning | “Precisa de você” + motivo |
| **Cobertura total** | Interrupt vazia, tom neutro | “A equipe de IA está cobrindo o fluxo” |

Nunca mostrar agente como “usuário” com foto genérica. Agente é **serviço**.

---

## 14. Como operações aparecem

- Nome da empresa do cliente no header  
- “Operação ao vivo” no brief  
- Período como chip técnico, não marketing  

---

## 15. Como interrupções aparecem

- Label humana: **“Precisa de você”**  
- Contagem em mono  
- Motivo em meta  
- CTA “abrir →” ou “Assumir”  
- Prioridade via badge semântico  

---

## 16. Como sucessos aparecem

- Deltas em mono verde  
- Eventos QUAL / PIPE no ops log  
- Sem confetti, sem toast verde em cascata  
- Sucesso de login = navegação  

---

## 17. Como falhas aparecem

- Erro **junto ao objeto**  
- Tom calmo, acionável  
- Retry explícito quando fizer sentido  
- Nunca stack trace na UI  
- Nunca culpar o usuário  

---

## 18. Motion

| Tipo | Duração | Uso |
|------|---------|-----|
| fast | 120ms | Hover, press |
| base | 160ms | Troca de estado, enter de alerta |
| slow | 180ms | Máximo para micro UI |

Easing: `cubic-bezier(0.2, 0.8, 0.2, 1)`  

- Respeitar `prefers-reduced-motion`  
- Sem bounce, sem parallax  
- Press em CTA: `scale(0.99)` sutil  

---

## 19. Microinterações

- Hover de linha: surface  
- Focus: ring brand  
- Loading de botão: spinner inline + label  
- Erro de form: borda warning + texto abaixo do campo  
- Agente live: pulse contínuo baixo  

---

## 20. Loading

- Skeleton **local** no painel  
- Skeleton com elevated, radius sm  
- Evitar spinners centrais de página inteira  

---

## 21. Empty states

1. Título  
2. Uma linha de contexto operacional  
3. Opcional: próxima ação  

Exemplos:

- “Nenhum handoff. A equipe de IA está cobrindo o fluxo.”  
- “Nenhuma reunião no radar.”  
- “Nenhuma atividade ainda hoje.”  

Proibido: mascotes, “Comece adicionando seu primeiro lead!”.

---

## 22. Feedback

| Tipo | Forma |
|------|-------|
| Sucesso implícito | Navegação ou atualização da lista |
| Sucesso explícito | Badge/estado no item (raro) |
| Erro | Alert local + copy acionável |
| Progresso | Process bar / label de loading |

Toasts só para eventos fora do viewport, com parcimônia.

---

## 23. Navegação

- Sidebar ícone-only (~56px), tooltip no hover  
- Header baixo: operação + busca + notificações + avatar  
- Itens: Dashboard · Conversas · Leads · Agenda · Resultados · Suporte  
- Deep link para conversa  
- Estado ativo com rail brand  

---

## 24. Estrutura das páginas

### Dashboard
1. OpsBrief  
2. AgentStage  
3. InterruptLane  
4. Tendência + KPIs  
5. OpsLog + Agenda  

### Conversas
- Lista densa + thread  
- Handoff no topo se houver  
- Agente responsável visível  

### Leads
- Tabela densa, mono em scores/datas  
- Filtros técnicos  

### Agenda
- Rail de horário + status  
- Framing “O que acontece depois”  

### Resultados
- Gráficos com legenda além da cor  
- Narrativa curta acima do chart quando houver insight  

### Settings (painel cliente)
- Perfil, notificações, segurança  
- **Sem** configuração de agentes (interno ForceIA)  

---

## 25. Gráficos

- Multi-série com legenda label + estilo  
- Pipeline como série protagonista  
- Grid baixo contraste  
- Labels mono  
- Cor não é o único canal de significado  

---

## 26. Acessibilidade

- Contraste AA no texto principal  
- aria-current na nav  
- aria-live em alertas  
- Focus visível  
- Ícones decorativos aria-hidden  

---

## 27. Anti-padrões (proibidos)

- Hero de marketing no app autenticado  
- Gradientes “AI purple/pink”  
- Cards com sombra de template  
- Emoji em navegação ou métricas  
- “Bem-vindo de volta 👋”  
- Kanban de CRM como primeira tela  
- Configurador de sequência para o cliente final  
- Toast em todo save  

---

## 28. Checklist antes de qualquer tela nova

- [ ] Narrativa: operação / IA / atenção humana?  
- [ ] Só escala tipográfica e tokens de cor?  
- [ ] Ícones Lucide stroke 1.75?  
- [ ] Assinatura ForceIA onde cabe?  
- [ ] Copy operacional, não marketing?  
- [ ] Handoffs visíveis sem caça?  
- [ ] Loading/empty/erro definidos?  
- [ ] Não parece HubSpot / Pipedrive / admin genérico?  

Se algum item falhar, a tela **não entra**.

---

## 29. Governança

- Este documento prevalece sobre preferências individuais de UI.  
- Mudanças na linguagem exigem atualização explícita desta versão.  
- Implementação (código) é consequência — nunca o contrário.

**ForceIA Product Language v1.0**  
Head of Product Design · ForceIA
