---
name: valide-testes-unitarios
user-invocable: true
description: >-
  Valida testes unitarios, de widget/page e integrados de um dominio, modulo ou
  submodulo/feature Flutter, identifica o workspace e package atual, executa as
  suites corretas, mede cobertura LCOV e garante no minimo 90% de cobertura no
  escopo alvo. Use quando pedirem: "valide os testes", "valide os testes
  unitarios", "rode os testes unitarios", "rode os integrados", "confira a
  cobertura", "garanta 90% de cobertura", ou "valide os testes do modulo X".
argument-hint: "Informe o dominio, modulo ou submodulo/feature e, opcionalmente, se deseja unitarios, integrados ou ambos"
---

# Validar os testes (unitários, widget e integrados)

## Objetivo

Validar de ponta a ponta os testes de um domínio, módulo ou submódulo/feature Flutter:

- resolver o contexto correto a partir do workspace e package atual;
- localizar testes unitários, widget/page e integrados relacionados;
- executar as suítes correspondentes separadamente quando existirem;
- gerar e interpretar cobertura de linha com LCOV;
- garantir **no mínimo 90% de cobertura agregada** do código de produção alvo;
- corrigir testes insuficientes ou ausentes quando necessário, seguindo o padrão da skill `escrever-testes`;
- entregar um relatório objetivo, sem fazer commit ou push.

## Hierarquia e nomenclatura

Em projetos Flutter (monorepos, multi-packages ou projetos modulares), interprete o escopo em três níveis:

- **Domínio / Workspace:** o repositório ou grupo de packages aberto (ex.: `payments_workspace` ou a raiz do projeto).
- **Módulo / Package:** um package ou módulo principal dentro do projeto (ex.: `packages/checkout` ou `lib/app/modules/checkout`).
- **Submódulo / Feature:** uma feature interna dentro do módulo (ex.: `packages/checkout/lib/payment_summary` ou `lib/features/checkout/payment_summary`).

Use essa hierarquia para interpretar pedidos como:

- "valide os testes do domínio `<dominio>`"
- "valide os testes unitários do módulo `<modulo>`"
- "valide os testes do submódulo/feature `<feature>`"

## Regras de segurança

1. Antes de criar ou alterar testes, siga as diretrizes da skill `escrever-testes` (e eventuais instruções locais de testes do repositório).
2. Confirme o workspace, package e escopo resolvidos antes de executar comandos abrangentes.
3. Preserve alterações existentes do usuário. Nunca use `git reset`, `git checkout` destrutivo ou limpeza de arquivos.
4. **Não altere código de produção** apenas para aumentar cobertura.
5. **Não crie testes artificiais** para getters triviais, classes apenas de constantes ou construtores privados não executáveis.
6. Se uma lacuna real exigir mudança ou adição de teste, altere somente testes do escopo solicitado.
7. Nunca faça commit, push ou criação de branch sem pedido explícito (`trabalho-seguro`).
8. Warnings preexistentes de `dart_test.yaml`, dependências externas ou geração de código não devem ser tratados como falha sem verificar o exit code e o efeito real no teste.

## Procedimento

### 1. Resolver o contexto

Determine o alvo nesta ordem:

1. Workspace aberto no editor e arquivo atual.
2. Diretório de trabalho do terminal.
3. Nome informado pelo usuário.
4. Estrutura de diretórios (`packages/*`, `libraries/*`, `lib/features/*`, `lib/app/modules/*`) e o `pubspec.yaml` correspondente.

Para um workspace multi-package, localize o package que possui o `pubspec.yaml` dono do código alvo. Não execute a suíte inteira do monorepo se o pedido apontar para um módulo ou submódulo específico.

Se houver múltiplos pacotes plausíveis ou o nome for ambíguo, liste as opções e peça confirmação antes de alterar arquivos.

Resolva os caminhos (adaptando à estrutura do projeto):

```text
Domínio / Raiz: <workspace>/
Módulo / Package: <workspace>/packages/<modulo>/ (ou <workspace>/lib/features/<modulo>/)
Submódulo / Feature: <package>/lib/<submodulo>/
```

### 2. Inventariar os testes

Dentro do package resolvido, procure:

- `test/<escopo>/**/*_test.dart` para testes unitários, widget e page;
- `test/integration_tests/**/*_test.dart` para testes do harness integrado (rodados via `flutter test`);
- `integration_test/**/*_test.dart` para testes Flutter de integração tradicionais (E2E em device/emulador);
- `test/**` e `integration_test/**` que referenciem o submódulo quando a árvore de `test/` não espelhar exatamente `lib/`.

Classifique os arquivos encontrados por camada:

- **data:** datasource, repository, model, mapper;
- **domain:** entity, usecase / interactor;
- **presentation:** cubit / bloc / controller, state, viewmodel, widget, page;
- **transversais:** analytics, logs, resources e injeção de dependência (DI / GetIt);
- **integração:** router, DI completo, mock server e fluxos compostos.

Registre também comandos ou scripts convencionais do package em `README.md`, `Makefile` ou documentação local, se existirem.

### 3. Validar a suíte unitária

Execute a suíte focal do alvo:

```bash
cd <package>
flutter test test/<escopo>
```

Se o escopo for o módulo inteiro e não houver uma subpasta única:

```bash
flutter test test
```

> **Atenção:** Não confunda um diretório `test/integration_tests` com a suíte unitária padrão. Os testes do harness integrado devem ser executados separadamente.

Ao analisar falhas, corrija primeiro o mesmo slice que falhou. Verifique:

- sequência de estados e side effects de Cubits/BLoCs/Controllers;
- chamadas de analytics e logs de erro com parâmetros corretos (`identifier`, `message`, `pageName`, `tags`, etc.);
- contratos de repositories, mappers e tratamento de exceções;
- composição de DI (ex.: GetIt) e rotas;
- interação real, visibilidade e navegação de pages/widgets.

### 4. Validar os testes integrados

Execute todos os arquivos integrados pertencentes ao alvo.

Para o padrão de harness integrado em `test/integration_tests/`:

```bash
cd <package>
flutter test test/integration_tests/<arquivos-do-alvo>
```

Se o package usar `integration_test/` tradicional, use o comando documentado pelo package e o device/emulador exigido:

```bash
flutter test integration_test/<arquivo>_test.dart -d <device>
```

Não substitua um teste integrado por um unitário apenas porque o runner unitário não o reconhece.

Registre separadamente:

- total de testes integrados;
- sucesso/falha;
- warnings de tags ou infraestrutura;
- pré-requisitos ausentes (device, mock server, assets ou variáveis de ambiente).

### 5. Medir cobertura (meta >= 90%)

Gere cobertura para os testes do alvo:

```bash
cd <package>
flutter test test/<escopo> --coverage
```

Quando fizer sentido e o runner suportar a combinação, execute unitários e integrados juntos para consolidar o LCOV:

```bash
flutter test --coverage test/<escopo> test/integration_tests/<arquivos-do-alvo>
```

Leia `coverage/lcov.info` e filtre **somente os arquivos de produção do alvo** (ex.: `lib/<submodulo>/`). Calcule:

```text
cobertura agregada = (linhas executadas / linhas instrumentadas) * 100
```

- O critério obrigatório é **cobertura agregada de linha >= 90%** para o código de produção do escopo solicitado.
- Liste também **arquivos individuais abaixo de 90%**, principalmente quando forem arquivos executáveis de `presentation`, `data`, `domain` ou `di`.
- **Exclusões legítimas do cálculo:** não conte arquivos de outros módulos, arquivos gerados (`*.g.dart`, `*.freezed.dart`, `*.config.dart`) ou dependências externas no percentual do alvo. Para arquivos de `resources` formados apenas por constantes e construtores privados, valide os contratos usados no fluxo e não crie execução artificial apenas para inflar o número.

### 6. Corrigir lacunas reais

Se a cobertura ficar abaixo de 90% ou houver uma lacuna comportamental relevante:

1. Siga as regras e moldes da skill `escrever-testes`.
2. Identifique no `lcov.info` as linhas não cobertas (`DA:<linha>,0`) e o comportamento que elas representam.
3. Adicione o menor teste realista possível na pasta espelho de `lib/` dentro de `test/`.
4. Use estrutura **AAA (Arrange / Act / Assert)** ou **Given / When / Then**, `mocktail` e `blocTest` conforme o tipo do código.
5. Para **Cubits/BLoCs/Controllers**, valide tanto a emissão de estados quanto os side effects (analytics, logs, chamadas de use cases).
6. Para **pages/widgets**, valide renderização por estado, interação do usuário, navegação/rotas e disparos de analytics.
7. Para **DI/GetIt**, registre e valide as dependências exigidas pelo construtor real.
8. Rode novamente o teste focal, depois a suíte unitária completa do escopo e recalcule a cobertura.
9. Repita no máximo **três ciclos** de correção antes de reportar bloqueio ou necessidade de decisão arquitetural.

Não altere a implementação de produção somente para satisfazer cobertura. Se o código de produção estiver acoplado de forma que impeça o teste, descreva a refatoração mínima necessária e peça confirmação ao usuário antes de tocar em `lib/`.

### 7. Fechar a validação

Antes de concluir, confira:

- [ ] Testes unitários do alvo passaram;
- [ ] Testes integrados do alvo passaram (quando existirem);
- [ ] Cobertura agregada de linha >= 90% no escopo alvo;
- [ ] Arquivos de `presentation` alterados possuem testes unitários/widget/page ou justificativa técnica;
- [ ] `flutter analyze` / `dart analyze` não apresenta novos erros ou warnings no escopo;
- [ ] `git diff --check` passa sem erros de formatação/whitespace;
- [ ] Nenhum arquivo fora do domínio/módulo/submódulo solicitado foi alterado.

## Formato do relatório

Responda em português com:

1. **Contexto resolvido:** domínio/workspace, módulo/package e submódulo/feature.
2. **Unitários:** comando executado, total de testes aprovados/falhas.
3. **Integrados:** arquivos executados, total de aprovados/falhas e warnings relevantes.
4. **Cobertura (LCOV):** percentual agregado (`linhas cobertas / total instrumentado`) e lista de arquivos abaixo de 90%.
5. **Alterações feitas nos testes:** arquivos criados ou atualizados (se houver).
6. **Bloqueios ou lacunas remanescentes:** pontos que dependem de decisão ou infraestrutura externa.

Nunca afirme que a cobertura atende 90% sem apresentar o cálculo real extraído do `coverage/lcov.info`.
