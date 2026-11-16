---
name: escrever-testes
description: >-
  Escreve e mantem os testes unitarios, de widget/page e integrados de um
  projeto Flutter no padrao de piramide (unitarios > widget/page > integracao,
  mocktail, blocTest, AAA / Given-When-Then), garantindo no minimo 90% de
  cobertura LCOV no escopo alvo. Use SEMPRE que a tarefa envolver criar ou
  atualizar testes: "escreve/cria os testes do modulo X", "testa o use case
  /repository/cubit/page Y", "cobre com testes", "monta a suite", "aumenta a
  cobertura para 90%", "faz um teste de widget/integracao". Segue os requisitos
  da skill valide-testes-unitarios.
---

# Escrever testes (Flutter genérico)

Cobre o código novo ou alterado com testes completos por camada, mantém as suítes unitária e integrada verdes e garante **no mínimo 90% de cobertura agregada de linha (LCOV)** no escopo alvo.

> Vale o `trabalho-seguro` (branch, escopo, sem commit sem permissão). Ao concluir a criação ou manutenção dos testes, valide o resultado seguindo a skill `valide-testes-unitarios`.

## Antes de começar

1. **Entenda a arquitetura e o escopo do projeto.** Identifique:
   - Workspace, package (`pubspec.yaml`) e submódulo/feature alvo
   - Gerenciamento de estado (Cubit/BLoC, ValueNotifier/ChangeNotifier, Riverpod, Provider, etc.)
   - Estrutura de pastas (`lib/<submodulo>/`, `lib/features/`, `lib/app/modules/`, `packages/<mod>/lib/`, etc.)
   - Camadas existentes (`data`, `domain`, `presentation`, `resources`, `di`)
   - Padrão de retorno (`Result`, `Either`, `dartz`, exceções tipadas)
   - Convenção de testes integrados do pacote (`test/integration_tests/` via `flutter test` e/ou `integration_test/` em device/emulador)
2. **mocktail é o padrão de mock** (sem code generation). Para Cubit/BLoC, use `bloc_test` (`blocTest`).
3. **Espelhe a estrutura de `lib/` em `test/`:** os testes unitários e de widget/page devem ficar em `test/<escopo>/**/*_test.dart`, separados de `test/integration_tests/`.

## Requisitos por camada (alinhados com `valide-testes-unitarios`)

Organize cada teste seguindo **AAA (Arrange / Act / Assert)** ou **Given / When / Then**:

1. **Data (`datasource`, `repository`, `model`, `mapper`):**
   - **Repository / Data source:** cubra pelo menos 3 cenários: sucesso (happy path), erro HTTP/status inválido e exceção de transporte/rede convertida na falha/exceção esperada pelo domínio.
   - **Model / Mapper (`fromJson` / `toEntity`):** valide o mapeamento completo de campos obrigatórios e opcionais. Não preserve fallback silencioso quando o contrato exigir erro para payload inválido.
2. **Domain (`entity`, `usecase` / `interactor`):**
   - Cubra sempre os caminhos de **Sucesso** e **Falha**, verificando o repasse exato de parâmetros e o retorno sem engolir erros.
3. **Presentation — Estado (`Cubit`, `BLoC`, `Controller`, `ViewModel`, `State`):**
   - Valide a **sequência exata de estados emitidos** (ex.: `[Loading, Loaded]` / `[Loading, Error]`).
   - Valide obrigatoriamente os **side effects** associados a cada fluxo: chamadas de analytics e registros de log/erro com `identifier`, `message`, `pageName`, `tags` e parâmetros corretos.
   - Garanta que Cubits/controllers criados manualmente ou repassados via `BlocProvider.value` tenham ciclo de vida (`close`/`dispose`) respeitado.
4. **Presentation — UI (`Page`, `Widget`):**
   - Além da renderização de cada estado (loading, sucesso, erro, vazio) e visibilidade condicional de componentes/botões, valide:
     - **interação real** do usuário (`tap`, preenchimento, refresh/retry);
     - **navegação e rotas** disparadas pela ação (argumentos, rota válida e tratamento de rota inválida);
     - **disparos de analytics** vinculados à visualização ou clique.
5. **Transversais (`DI / GetIt`, `Analytics`, `Resources`):**
   - **DI / GetIt:** registre e valide no teste todas as dependências exigidas pelos construtores reais (nunca deixe factory quebrada após mudança em construtor anotado com `@Injectable`).
   - **Resources:** valide strings, endpoints e tags consumidos nos fluxos reais. **Não crie testes artificiais** apenas para exercitar getters triviais, classes só de constantes ou construtores privados.
6. **Integração (`test/integration_tests/` ou `integration_test/`):**
   - Cubra fluxos compostos integrando `Page` + `Router` + `DI/GetIt` + `Cubit/Controller` + mock das bordas (mock server / http client), mantendo sua execução separada da suíte unitária.

## Procedimento

1. **Mapear os alvos** do módulo/submódulo:
   ```bash
   python skills/escrever-testes/scripts/scaffold_tests.py --module <mod> --dry-run
   ```
   (ou inspecione `lib/<escopo>` vs `test/<escopo>` diretamente para listar lacunas por camada).

2. **Gerar ou criar os arquivos de teste espelhados** (sem sobrescrever testes existentes):
   ```bash
   python skills/escrever-testes/scripts/scaffold_tests.py --module <mod>
   ```

3. **Implementar os testes pelos moldes** (`references/moldes.md`):
   - M1 Use case / Interactor · M2 Repository / Data source · M3 Model / Mapper (`fromJson`) · M4 Controller / Cubit + Side effects · M5 Widget / Page (render + interação + navegação + analytics) · M6 Integração (harness `test/integration_tests/` e `integration_test/`) · M7 Clock injetável · M8 DI / GetIt e Analytics.
   - Guia de Mocktail: `references/mocktail.md`.

4. **Regras duras ao escrever:**
   - Em `test/`, use imports `package:<nome_do_pacote>/...`.
   - Mock **somente de contrato/interface** (repositories, use cases, analytics, router, http client); `Entity`, `Model` e `State` puros são instanciados de verdade (ou via fixtures alinhadas ao payload real).
   - **Não altere código de produção** apenas para aumentar cobertura. Se o código for difícil de testar, aponte a refatoração mínima necessária e peça confirmação antes.
   - **Nunca** bater na API real no run padrão (`*_api_live_test.dart` leva `@Tags(['live'])` e fica fora do run padrão).

5. **Executar suíte unitária e suíte integrada separadamente:**
   ```bash
   # 1) Suíte unitária e widget/page do escopo
   flutter test test/<escopo>

   # 2) Suíte integrada do escopo (quando existir em test/integration_tests)
   flutter test test/integration_tests/<arquivos-do-alvo>

   # 3) Análise estática
   flutter analyze
   ```
   Corrija qualquer falha antes de prosseguir.

6. **Medir e garantir cobertura LCOV >= 90% (`references/cobertura.md`):**
   ```bash
   flutter test test/<escopo> --coverage
   # ou combinando unitários + harness integrado quando suportado:
   flutter test --coverage test/<escopo> test/integration_tests/<arquivos-do-alvo>
   ```
   - Filtre `coverage/lcov.info` apenas para os arquivos de produção do escopo (`lib/<escopo>/`), excluindo arquivos gerados (`*.g.dart`, `*.freezed.dart`, `*.config.dart`) e outros módulos.
   - Garanta **cobertura agregada de linha >= 90%** (`linhas executadas / linhas instrumentadas * 100`) e verifique arquivos individuais abaixo de 90%.
   - Se quiser gerar o relatório visual:
     ```bash
     python skills/escrever-testes/scripts/coverage_report.py --module <mod> --min 90 --html
     ```

7. **Conferir o DoD (`references/checklist-dod.md`) e fechar com `valide-testes-unitarios`:**
   - Apresente o resumo com contexto resolvido, resultado dos unitários, resultado dos integrados, cálculo real da cobertura LCOV (>= 90%), arquivos abaixo de 90% e eventuais bloqueios.

## Gotchas

- `registerFallbackValue(<instancia>)` no `setUpAll` antes de usar `any()` com tipo customizado no `mocktail`.
- Parâmetro nomeado no `mocktail`: `any(named: 'nomeDoParametro')`.
- Sempre use `thenAnswer((_) async => ...)` para retornos `Future`/`Stream`; `thenReturn` em `Future` reaproveita a mesma instância e causa bugs sutis.
- **Relógio:** nunca use `DateTime.now()` implícito em regra de negócio testável. Injete o clock e congele-o no teste (molde M7).
- **Ciclo de vida em Widget tests:** ao fornecer um `MockCubit` ou `Cubit` real via `BlocProvider.value`, garanta quem é dono do `close` para não gerar leaks ou erros de stream fechada.

## Referências

- `references/moldes.md`: moldes M1 a M8 completos (incluindo Cubit + side effects, Page + navegação/analytics, integração e DI/GetIt).
- `references/mocktail.md`: instalação, API essencial, regras e armadilhas.
- `references/checklist-dod.md`: Definition of Done por escopo/PR (incluindo meta >= 90% e integração com `valide-testes-unitarios`).
- `references/cobertura.md`: como gerar, filtrar por escopo e calcular os >= 90% no LCOV sem inflar artificialmente.
- `scripts/scaffold_tests.py`: gerador de esqueletos de teste do módulo (dry-run e real).
- `scripts/coverage_report.py`: relatório de cobertura por módulo (terminal + `report.html`).
