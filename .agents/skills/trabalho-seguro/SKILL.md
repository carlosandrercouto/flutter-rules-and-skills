---
name: trabalho-seguro
description: >-
  Protocolo de trabalho seguro para atuar em projetos Flutter sem quebrar nada,
  especialmente com o modelo em modo auto (Sonnet). Consulte e siga SEMPRE no
  INICIO de qualquer tarefa de implementacao, mudanca, correcao, refatoracao ou
  setup, ANTES de escrever/editar codigo ou rodar comandos que alterem algo, por
  exemplo quando o usuario disser "vamos fazer X", "implementa Y", "corrige Z",
  "cria/altera ...", "pode comecar", "manda ver". Estabelece os gates de partida
  (confirmar a branch, levantar requisitos, montar plano/checklist), as regras
  durante a execucao (nao sair do escopo, nao agir sobre duvida, demonstrar
  progresso, verificar antes de concluir) e o fecho (nunca commitar/pushar sem
  permissao explicita). Vale com ou sem modo auto: e camada de seguranca. Nao se
  aplica a perguntas puramente informativas/conversa que nao mexem em nada.
---

# Protocolo de trabalho seguro — Flutter (genérico)

Harness comportamental para trabalhar em qualquer projeto Flutter com segurança,
sobretudo com o modelo em modo auto. Objetivo: entregar o que foi pedido sem
estragar o resto, sem surpresa, e sem avançar sobre dúvida. Vale para qualquer
tarefa que crie, altere ou remova algo (código, doc, config, git, assets).

## Regra zero

**Na dúvida, PARE e PERGUNTE.** Nunca atue sobre suposição não confirmada. Refazer
ou reverter custa mais caro do que uma pergunta. Se você se pegou "achando" algo
importante (qual branch, qual arquivo, qual comportamento esperado), isso é sinal
de que precisa perguntar, não agir.

## 1. Antes de começar (gates de partida, obrigatório)

Não escreva nem rode nada que altere o projeto antes de passar por aqui.

1. **Branch certa.** Rode `git branch --show-current` e `git status -sb`. Confirme
   com o usuário que é a branch correta para este trabalho. Se estiver em
   `master`/`main`/`develop`, ou numa branch que não parece a certa, **não comece**:
   pergunte ou proponha criar/trocar de branch.
2. **Estado limpo.** Se há mudanças não commitadas e não relacionadas ao pedido,
   sinalize antes de misturar seu trabalho com elas.
3. **Levantar requisitos.** Elimine ambiguidade com perguntas objetivas antes de
   executar. Para decisões com opções, use `AskUserQuestion`. Não preencha lacuna
   com achismo. (Ver `references/kickoff-checklist.md`.)
4. **Plano de ação (checklist).** Apresente um checklist do que será feito e use a
   lista de tarefas (TodoList) para rastrear. Em trabalho não-trivial, **obtenha o
   OK do usuário** antes de sair executando. Um item = uma unidade verificável.
5. **Contexto do projeto.** Leia o `CLAUDE.md` / `AGENTS.md` / `GEMINI.md` do
   projeto, se existir. Verifique se já há skills ou receitas no repositório para a
   tarefa em questão (ex.: criação de módulo, commit, deploy). Reutilize em vez de
   reinventar.

## 2. Durante a execução

- **Fique no escopo.** Só mexa no plano aprovado. Encontrou algo fora do contexto que
  valeria arrumar? **Anote e pergunte antes** — não "aproveite pra consertar" sem
  pedir. Escopo que cresce em silêncio é o principal jeito de estragar.
- **Seja proativo com escopo controlado.** Conduza a tarefa até a implementação e a
  validação necessárias, tomando as decisões locais que forem sustentadas pelo código e
  pelo requisito. Atualize os testes unitários afetados quando a implementação alterar
  o contrato ou o comportamento coberto, sem pedir confirmação para esse ajuste
  necessário. Faça a menor mudança suficiente para preservar o contrato existente.
  Evite refatorações cosméticas, abstrações, compatibilidades e múltiplos fallbacks sem
  requisito explícito, evidência no código ou necessidade comprovada de preservar
  comportamento. Não amplie a solução por preciosismo; se uma alternativa simples
  resolve o problema, prefira-a.
- **Passos pequenos e reversíveis.** Prefira mudanças incrementais e saiba como
  reverter cada uma antes de fazê-la.
- **Demonstre o que fica pronto.** Ao concluir cada item do checklist, marque-o e
  mostre o resultado: resumo curto + evidência (`arquivo:linha`, saída de comando,
  screenshot). Nada de "terminei tudo" sem mostrar o quê.
- **Cobertura completa.** Ao alterar uma feature, verifique as camadas de domain,
  data, presentation e resources. Adicione testes unitários para cada camada
  afetada e testes integrados para widgets/pages quando o fluxo depender de router,
  composição visual ou mock server.
- **Contrato de referência.** Antes de estruturar ou alterar uma feature, identifique
  um módulo/feature maduro do próprio repositório como exemplo de separação entre
  model e entity, resources centralizados, DI, states por fluxo e fixtures alinhados
  ao contrato real.
- **DI gerado.** Quando o projeto usar geração de código para injeção de dependência
  (ex.: `@Injectable` + `get_it`) e você alterar uma assinatura anotada, descubra o
  executável de geração adotado pelo repositório. Em monorepos ou pacotes isolados,
  prefira `dart run build_runner build --delete-conflicting-outputs` dentro do pacote
  que possui o `pubspec.yaml`; não tente executar `flutter pub run build_runner` se o
  pacote estiver disponível apenas via wrapper ou dependência transitiva. Não
  substitua a configuração gerada por `registerFactory` manual para classes anotadas;
  regenere e versione o arquivo `.config.dart`, validando a composição real no container
  de DI (ex.: GetIt).
- **Verifique antes de dizer "pronto".** Rode o que for aplicável:
  - `dart analyze` / `flutter analyze` — erros estáticos
  - `flutter test` — testes unitários/widget
  - `flutter build` — garantir que compila
  - `dart format --set-exit-if-changed .` — formatação
  - testes com cobertura e inspeção do LCOV quando o pipeline usar Sonar ou cobertura
    de diff
  Se algo falha, diga com a saída. Nunca afirme concluído sem verificação.
- **Não invente.** Comando, arquivo, flag ou API que você não conhece: verifique no
  código ou pergunte. Memórias e contexto podem estar desatualizados — confirme no
  código atual antes de afirmar como fato.
- **Respeite a arquitetura existente.** Antes de criar algo novo, entenda o padrão
  de pastas, nomenclatura e gerenciamento de estado que o projeto já usa. Não
  introduza padrões conflitantes sem discutir.
- **Parsing e UI.** Não preserve fallback silencioso quando o contrato exigir erro
  para dados inválidos. Na presentation, mantenha visibilidade, ação habilitada,
  campos opcionais e navegação tipada cobertos por testes.
- **Migração de contrato.** Quando a API mudar chaves, casing ou estrutura,
  faça uma busca por todas as representações do payload antes de editar. Atualize
  parser, fixtures unitárias, mocks de integração e registries compartilhados de
  mock, depois valide um payload novo e a rejeição do contrato antigo.
- **Navegação e analytics.** Antes de concluir fluxos com navegação ou elementos
  dinâmicos, verifique rota, URL, parâmetros permitidos e comportamento para rota
  inválida. Confirme na interface concreta do projeto se o registro deve usar log de
  erro (ex.: `trackErrorLog`) ou um evento de analytics, sem inventar ou copiar uma
  API de outro módulo.

## 3. Ações que exigem permissão explícita (nunca faça sozinho)

Ver a lista completa de gatilhos em `references/stop-and-ask.md`. Os principais:

- **Commit / push.** Só quando o usuário pedir ("pode commitar"). Nunca
  `--no-verify`, nunca `--force`/force-push, nunca pular hooks, sem pedido explícito.
- **Destrutivo / difícil de reverter.** Deletar ou sobrescrever arquivo que você
  não criou, `git reset --hard`, `git checkout --` que descarta trabalho, apagar
  branch/stash, rodar migração/seed, mexer em credenciais/segredos/config sensível,
  ou qualquer efeito externo/irreversível. Antes: olhe o alvo e confirme.
- **Ampliar o escopo** além do plano combinado.
- **Alterar dependências.** Adicionar, remover ou atualizar pacotes no
  `pubspec.yaml` sem discutir impacto e compatibilidade.

## 4. Ao concluir

- Resumo objetivo: **o que mudou**, **onde** (`arquivo:linha`), **como validar**, e
  **o que ficou de fora / próximos passos**.
- **Não commite por conta própria.** Aguarde a permissão. Deixe claro que está pronto
  para commitar quando o usuário quiser.

## Modo auto (atenção redobrada)

Sem confirmação a cada passo, o risco de derrapar é maior. Então:

- Mantenha o checklist sempre visível e atualizado.
- **Pare em toda bifurcação de decisão** com trade-off real (mais de um caminho
  razoável): pergunte, não escolha sozinho.
- Nunca amplie escopo em silêncio; nunca commite/pushe.
- Se perder a confiança sobre estado (branch, arquivo, o que já foi feito), pare e
  reancore com `git status`/leitura antes de continuar.

## Boas práticas Flutter (checklist rápido)

Antes de finalizar qualquer tarefa, confirme:

- [ ] Nenhum warning no `dart analyze` / `flutter analyze`
- [ ] Testes existentes continuam passando (`flutter test`)
- [ ] Build compila sem erros (`flutter build apk --debug` ou equivalente)
- [ ] Código formatado (`dart format .`)
- [ ] Imports organizados (sem imports não utilizados)
- [ ] Sem `print()` / `debugPrint()` esquecidos em código de produção
- [ ] Nenhuma credencial, token ou dado sensível foi introduzido em código, logs ou
  mocks
- [ ] Mocks não usam dados reais ou sensíveis
- [ ] Imagens adicionadas ou alteradas foram otimizadas quando aplicável
- [ ] Strings hardcoded avaliadas (i18n, se o projeto usa)
- [ ] Strings, endpoints e tags centralizados em resources quando forem contratos da
  feature
- [ ] Testes unitários adicionados para todas as camadas alteradas
- [ ] Testes integrados atualizados para widgets/pages quando o fluxo visual ou de
  navegação mudou
- [ ] Cobertura LCOV conferida nos arquivos alterados quando o pipeline usar Sonar ou
  cobertura de diff
- [ ] Nenhum `TODO` / `FIXME` introduzido sem sinalizar ao usuário
- [ ] Arquivos gerados pelo DI foram regenerados após mudanças em construtores
  anotados
- [ ] Factories do container de DI (ex.: GetIt) e testes usam todas as dependências
  exigidas pelos construtores reais
- [ ] Cubits/controllers criados manualmente ou com `BlocProvider.value` possuem dono
  claro do `close`/`dispose`
- [ ] Erros de cada fluxo registram o side effect correto e preservam o feedback
  visual correspondente

## Referências

- `references/kickoff-checklist.md` — template do plano de ação + perguntas de
  levantamento de requisitos (o que confirmar antes de começar).
- `references/stop-and-ask.md` — lista dos gatilhos que exigem parar e pedir
  confirmação (decisão, ambiguidade, destrutivo, escopo, git).
