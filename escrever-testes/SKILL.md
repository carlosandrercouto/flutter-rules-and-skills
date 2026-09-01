---
name: escrever-testes
description: >-
  Escreve e mantem os testes de um projeto Flutter no padrao de pirâmide
  (unitarios > widget > integracao, mocktail). Use SEMPRE que a tarefa envolver
  teste, por exemplo: "escreve/cria os testes do modulo X", "testa o use case
  /repository/controller Y", "cobre com testes", "monta a suite", "aumenta a
  cobertura", "faz um teste de widget/integracao". Regras centrais: mock e
  mocktail e SO de contrato/interface; use case/repository cobre Success E
  Failure; data source cobre happy path / erro HTTP / erro de transporte sem
  throw; API real so em *_api_live_test.dart deliberado (nunca no run padrao);
  integracao e suite curada em integration_test/ (nao trava PR). Tem scaffold
  proprio (scripts/scaffold_tests.py) que gera os esqueletos de teste do modulo.
---

# Escrever testes (Flutter genérico)

Cobre o código novo com testes no padrão do projeto e mantém a suite verde.

> Vale o `trabalho-seguro` (branch, escopo, sem commit sem permissão). "Testes
> do código novo escritos" é item do checklist de toda PR.

## Antes de começar

1. **Entenda a arquitetura do projeto.** Identifique:
   - Qual gerenciamento de estado (BLoC, Riverpod, Provider, GetX, MobX, etc.)
   - Qual estrutura de pastas (`lib/features/`, `lib/app/modules/`, `lib/src/`, etc.)
   - Se usa camadas separadas (domain, data, presentation) ou outra organização
   - Qual padrão de resultado (`Result`, `Either`, `dartz`, exceções, etc.)
   - Qual HTTP client (`dio`, `http`, custom adapter, etc.)
2. **mocktail é o padrão de mock** (sem code generation). Se não estiver no
   `pubspec.yaml`, adicione em `dev_dependencies` (`mocktail: ^1.0.4`) e rode
   `flutter pub get` (avise no resumo). Prefira mocktail a mockito/build_runner,
   salvo se o projeto já usa mockito.
3. **Identifique o que tem teste e o que não tem:** `ls test/` e compare com `lib/`.

## Procedimento

1. **Mapear os alvos** do módulo/feature:
   ```bash
   python skills/escrever-testes/scripts/scaffold_tests.py --module <mod> --dry-run
   ```
   (ajuste o path do script e o `--modules-path` conforme a organização do projeto)

2. **Carimbar os esqueletos** (não sobrescreve o que existe):
   ```bash
   python skills/escrever-testes/scripts/scaffold_tests.py --module <mod>
   ```
   Sai `test/<mod>/{use_cases,repositories,controllers,models,widgets}/` com os
   imports `package:` reais e TODOs apontando o molde certo.

3. **Preencher pelos moldes** (`references/moldes.md`):
   - M1 use case/interactor · M2 repository/data source · M3 fromJson · M4 controller
   · M5 widget smoke · M6 integração · M7 clock injetável.
   Mocktail: `references/mocktail.md`.

4. **Regras duras ao preencher:**
   - Em `test/`, imports são `package:<nome_do_pacote>/...` (o lint de import
     relativo vale só para `lib/`).
   - Mock **só de contrato/interface** (ex.: `IRepository`, `IHttpClient`,
     `IAuthService`); model puro se instancia de verdade.
   - Use case / interactor: **sempre os dois caminhos** (Success e Failure).
   - Repository / data source: pelo menos **3 caminhos** (happy path; erro HTTP
     vira failure sem lançar exceção; exceção de transporte vira erro genérico).
   - Widget: wrap `MaterialApp > Theme/ThemeData > Scaffold`; widget burro + dado
     de exemplo; sem rede, sem controller.
   - **Nunca** bater na API real no run padrão. Teste de contrato = sufixo
     `_api_live_test.dart`, rodado deliberado.

5. **Rodar e fechar verde:**
   ```bash
   flutter test test/<mod>                # o módulo
   flutter test                           # a suite completa
   flutter analyze                        # limpo
   ```
   Se o projeto usar tags para excluir testes especiais (ex.: `live`, `e2e`),
   exclua-as: `flutter test -x "live"`.
   Se falhar, conserte antes de reportar. Nunca marque "pronto" com teste vermelho.

6. **Cobertura (quando pedirem, ou ao fechar um módulo):**
   ```bash
   flutter test --coverage
   python skills/escrever-testes/scripts/coverage_report.py --html
   ```
   Tabela por módulo no terminal + `coverage/report.html` interativo. Leia com
   honestidade (`references/cobertura.md`): o lcov só lista arquivo importado pela
   suite, e o bar é por costura, não por percentual.

7. **Conferir o DoD** (`references/checklist-dod.md`) e reportar: o que foi
   coberto, o que ficou de fora e por quê.

## Integração (só quando pedirem o smoke E2E)

Suite **curada** em `integration_test/` (dep do SDK: `integration_test: sdk: flutter`),
poucos fluxos críticos, **não trava PR**. **Local é o padrão** (device/emulador do dev).

Gotchas comuns de apps Flutter:
- Splash animado: `pumpAndSettle` não assenta; use poll (molde M6).
- Auto-login pode pular direto pra home: teste tolerante.

Rodar:
```bash
flutter test integration_test/<fluxo>_test.dart -d <device>
```

Cobertura separada da integração (report próprio, sem misturar com o run padrão):
```bash
flutter test integration_test/ --coverage --coverage-path=coverage/lcov_integration.info
python skills/escrever-testes/scripts/coverage_report.py \
  --lcov coverage/lcov_integration.info --out coverage/report_integration.html --html
```

Semeie `Key` nos elementos-chave dos fluxos cobertos.

## Gotchas

- Se o projeto tem uma classe base de use case que exige dependência extra (ex.:
  `crashlyticsService`, `analyticsService`), mocke junto (void methods de Mock são
  no-op por padrão no mocktail, não precisa stubar).
- `registerFallbackValue(<request>)` no `setUpAll` antes de `any()` com tipo próprio.
- Parâmetro nomeado: `any(named: 'data')`.
- `thenAnswer` para retorno `Future`/`Stream`; `thenReturn` num `Future` dá bug sutil
  (mesma instância reaproveitada). Na dúvida, `thenAnswer`.
- **Relógio: nunca `DateTime.now()` implícito em regra testável.** Injete o clock e
  fixe no teste (molde M7). Caso clássico: teste quebra anos depois sem ninguém tocar
  no código, porque usava datas fixas e `DateTime.now()` avançou.
- **Live tests com tag executável:** cada `*_api_live_test.dart` leva `@Tags(['live'])`
  no topo (com o `dart_test.yaml` do repo declarando a tag). Run padrão exclui a tag;
  contrato deliberado: `-t live`.

## Referências

- `references/moldes.md`: os moldes M1 a M7 completos, com o código real.
- `references/mocktail.md`: instalação, API essencial, regras e armadilhas.
- `references/checklist-dod.md`: o bar por PR + comandos de auditoria.
- `references/cobertura.md`: gerar/exibir lcov e ler o número com honestidade.
- `scripts/scaffold_tests.py`: gera os esqueletos de teste do módulo (dry-run e real).
- `scripts/coverage_report.py`: cobertura por módulo (terminal + report.html).
