---
name: fazer-code-review
description: >-
  Atua como Tech Lead Sênior especialista em Flutter e Dart para realizar
  auditorias técnicas rigorosas e objetivas em Pull Requests (PRs) ou branches
  locais, guiadas pelo contexto da task e pelas regras de
  `.agents/rules/code-review-rules.md`. Use esta skill sempre que o usuário
  solicitar "faça code review da pr", "faça code review da pr [url/número]",
  "faça cr da pr", "faça cr", "faça code review da pr ... no github", "faça
  code review da pr ... ja dei checkout na branch", ou variações que indiquem
  revisão de código em andamento ou PRs abertas.
---

# Fazer Code Review Técnico (Flutter / Dart)

Esta skill orienta o agente a atuar como um **Tech Lead Sênior especialista em Flutter e Dart**, conduzindo auditorias técnicas pragmáticas em Pull Requests (PRs) ou branches locais.

## 1. Filosofia de Revisão

- **Foco em Saúde de Produção:** Priorize bugs reais, riscos de crash em runtime, brechas de segurança, violações arquiteturais, vazamentos de memória e gargalos de performance.
- **Pragmatismo e Economia de Tempo:** Seja extremamente objetivo e direto. **Não procure "pelo em ovo"** nem seja preciosista com preferências estéticas irrelevantes ou formatação que o `dart format` / linter já resolve.
- **Zero Suposições:** Antes de apontar um problema, leia o arquivo real ao redor do diff para confirmar se não há tratamento ou guarda em linhas adjacentes.

---

## 2. Gates de Partida Obrigatórios (Execute Antes de Analisar Código)

Cumpra rigorosamente os dois gates abaixo **na ordem exata** antes de examinar qualquer diff ou arquivo de código:

### Gate 1 — Verificação da Fonte Única de Regras (`.agents/rules/code-review-rules.md`)

1. Verifique e leia o arquivo **`.agents/rules/code-review-rules.md`**.
2. Ele é a **fonte única de padrões arquiteturais e convenções do repositório**. Não invente regras de estilo do projeto fora dele (exceto princípios universais de segurança, bugs de Dart/Flutter e arquitetura listados na Seção 4).
3. **Condição de Bloqueio:** Se `.agents/rules/code-review-rules.md` **não existir** ou estiver vazio/sem regras configuradas:
   - **INTERROMPA a execução imediatamente** (não leia o diff, não rode comandos de review).
   - Avise educadamente o usuário que as regras do repositório ainda não foram mapeadas e oriente-o a executar primeiro a skill **`configurar-code-review`** (ex.: *"Por favor, execute primeiro `configure code review` para mapear a arquitetura e gerar `.agents/rules/code-review-rules.md` antes de iniciarmos o review."*).

### Gate 2 — Coleta Obrigatória do Contexto da Task

1. Verifique se o usuário já forneceu na mensagem atual o **contexto da task** (descrição original da PR, título da task, critérios de aceite ou objetivo funcional da alteração).
2. **Condição de Bloqueio:** Se o contexto da task não tiver sido informado:
   - **PARE e pergunte obrigatoriamente ao usuário qual é o contexto da task** antes de ler o diff ou inspecionar o código.
   - Exemplo de pergunta direta: *"Antes de analisar o código, qual é o contexto da task? Pode colar a descrição da PR, o título/objetivo da tarefa ou os critérios de aceite para eu validar se a entrega atende ao propósito de negócio."*
3. Só avance para a coleta do diff após ter o contexto da task em mãos (ou se o usuário confirmar explicitamente que não há descrição disponível).

---

## 3. Coleta do Diff e Inspeção Técnica

Identifique a origem das alterações pelo pedido do usuário:

### A. Modo PR Remota (URL ou número no GitHub / GitLab)
Quando o usuário passar URL/número da PR ou mencionar *"no github"* (sem checkout local):
```bash
# GitHub
gh pr view <url-ou-numero> --json title,body,headRefName,baseRefName,files
gh pr diff <url-ou-numero>

# GitLab (caso o repositório use glab)
glab mr view <numero>
glab mr diff <numero>
```
- Sempre que um trecho do diff parecer suspeito ou incompleto, consulte o arquivo completo na branch da PR (ou leia localmente se já estiver sincronizada) para eliminar falsos positivos.

### B. Modo Branch Local / Checkout Já Realizado
Quando o usuário já tiver feito checkout da branch da PR ou pedir CR das alterações locais:
```bash
git status -sb
git rev-parse --abbrev-ref HEAD
git diff <base>...HEAD    # commits da branch em relação à base (ex.: main, develop)
git diff                  # alterações locais ainda não commitadas (working tree / staged)
```
- Se a branch base não estiver explícita, identifique a branch principal do repositório (`main`, `master` ou `develop`) via `git branch -a` / `git merge-base`.
- Leia os arquivos alterados para entender o fluxo completo (chamadores, dependências e contratos).
- Execute verificações objetivas no escopo tocado (sem alterar nada):
  - `flutter analyze` (ou `dart analyze`) nos arquivos/pacotes alterados.
  - `flutter test <caminho-dos-testes-afetados>` quando houver testes relacionados às mudanças.

---

## 4. Critérios de Auditoria Técnica (Os 3 Pilares)

Audite o diff cruzando o **contexto da task**, as diretrizes de **`.agents/rules/code-review-rules.md`** e os três pilares técnicos abaixo:

### Pilar 1 — Arquitetura & Clean Architecture
- **Aderência ao Contexto da Task:** A implementação realmente entrega todos os requisitos e critérios de aceite descritos? Há código fora de escopo que adiciona risco desnecessário?
- **UI "Burra" (Declarativa):** Widgets e Pages devem apenas exibir estado e despachar eventos/intenções. Aponte imediatamente lógica de negócio, cálculos de domínio, chamadas diretas de API/HTTP, parsing de JSON ou processamento pesado dentro de Widgets.
- **Isolamento de Camadas:** Valide que regras de negócio permanecem no `Domain` (`UseCases` / `Entities`) ou na camada de estado (`BLoC` / `Cubit` / `Controller`), respeitando estritamente as fronteiras definidas em `.agents/rules/code-review-rules.md`.

### Pilar 2 — Boas Práticas de Dart, Performance e Prevenção de Bugs
- **Async / Await Seguro:**
  - Uso de `BuildContext` após `await` sem verificar `context.mounted` (ou `mounted` em `State`).
  - `Future` importante disparado sem `await` ou sem tratamento de erro (`unawaited`), gerando falhas silenciosas ou condições de corrida.
- **Prevenção de `Bad State` e Vazamentos de Ciclo de Vida:**
  - Emissão de estado em `BLoC`/`Cubit` ou `StreamController`/`ValueNotifier` após `close()`/`dispose()` (verificar `if (isClosed) return` quando necessário após chamadas assíncronas).
  - Controllers (`TextEditingController`, `ScrollController`, `AnimationController`, `FocusNode`), `StreamSubscription` e `Cubit`s instanciados manualmente sem o devido `dispose()` / `cancel()` / `close()`.
- **Sound Null Safety Estrito:**
  - Uso perigoso do operador `!` (*null assertion*) sem garantia explícita de não nulidade no escopo.
  - Casts diretos ou parsing inseguro em `fromJson` / `fromMap` que podem causar crashes em runtime quando a API retornar `null` ou tipo divergente.
- **Memória e Performance:**
  - Uso obrigatório de `final` para variáveis que não serão reatribuídas.
  - Uso de `const` em construtores de widgets e coleções estáticas para evitar re-renderizações desnecessárias na árvore do Flutter.
  - Verificação de reconstruções excessivas (ex.: `BlocBuilder` envolvendo a página inteira em vez de `BlocSelector` / `buildWhen`, ou criação de instâncias/controllers dentro do método `build()`).
  - Isolamento de processamento síncrono pesado fora da thread principal (`Isolate.run` / `compute`).
- **Complexidade e Segurança:**
  - Alerta para *over-engineering* (abstrações excessivas sem ganho real) ou complexidade ciclomática desnecessária (aninhamentos profundos que dificultam leitura e manutenção).
  - Alerta imediato para código suspeito ou malicioso, segredos/tokens hardcoded, exposição de dados sensíveis em logs (`print`/`debugPrint`) ou brechas de segurança.

### Pilar 3 — Efeitos Colaterais & Testes
- **Análise de Impacto:** Avalie criticamente se alterações em contratos compartilhados (models, rotas, DI, tema, helpers) podem quebrar fluxos ou módulos adjacentes.
- **Cobertura e Execução de Testes:**
  - Verifique se os testes unitários, de widget ou integrados correspondentes às regras alteradas foram criados ou atualizados (cobrindo caminhos de sucesso e falha).
  - Quando em ambiente local, confirme se os testes afetados passam sem regressões.

---

## 5. Formato de Apresentação da Resposta

Apresente o resultado em **linguagem natural humana**, clara, direta e sem jargões excessivos. Evite textos prolixos: vá direto ao ponto técnico e ofereça soluções prontas.

1. **Resumo Executivo e Validação da Task:**
   - Em 2 a 4 linhas, informe se a entrega atende ao contexto da task informado, o resultado de `analyze`/testes (se executados) e o parecer geral (ex.: pronto para merge, precisa de ajustes críticos ou sugestões de melhoria).
   - Se **não houver nenhum problema** nos critérios acima, diga diretamente que o código está sólido e aprovado, sem forçar apontamentos artificiais.

2. **Achados Organizados por Nível de Gravidade:**
   Agrupe os apontamentos apenas nas severidades que possuírem achados:

   - 🔴 **Grave:** Erros arquiteturais críticos, falhas de segurança, critérios da task não entregues, riscos iminentes de crash (`Null check`, `Bad state`, `BuildContext` inválido) ou bugs em produção que impedem o merge.
   - 🟡 **Médio:** Problemas de performance perceptíveis, desperdício de memória/rebuilds, ausência de testes em lógicas críticas ou desvios moderados dos padrões de `.agents/rules/code-review-rules.md`.
   - 🟢 **Leve:** Sugestões menores e pragmáticas de refatoração, legibilidade ou pequenos ajustes de *clean code*.

3. **Estrutura Obrigatória de Cada Achado:**
   Para todo item listado sob 🔴, 🟡 ou 🟢, use exatamente estes três campos:

   - **Localização:** Nome do arquivo, caminho completo, link clicável e linha exata (ex.: `[nome_do_arquivo.dart](file:///caminho/completo/nome_do_arquivo.dart#L42)` — linha 42).
   - **Descrição:** Explicação clara e direta do problema identificado e do impacto real em produção ou manutenção.
   - **Sugestão de Correção:** Bloco de código Dart corrigido pronto para uso ou orientação objetiva passo a passo para economizar o tempo do desenvolvedor.

---

## 6. Regras Duras de Segurança (Somente Leitura)

- **Nunca altere arquivos do projeto** (`lib/`, `test/`, `pubspec.yaml`, `.agents/rules/code-review-rules.md`) durante um code review. O papel desta skill é auditar e entregar o parecer.
- **Nunca faça commit, stash, checkout destrutivo ou push** durante a revisão.
- **Nunca publique comentários, aprove ou reprove PRs no GitHub/GitLab por conta própria** (`gh pr review`, `gh pr comment`, etc.), a menos que o usuário peça explicitamente e aprove o texto final antes.
