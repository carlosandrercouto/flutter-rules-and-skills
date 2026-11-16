# Checklist: Definition of Done (DoD) de Testes por PR / Escopo

Antes de dar a tarefa por pronta (e para passar na validação da skill `valide-testes-unitarios`):

- [ ] **Estrutura espelhada:** Testes unitários e de widget/page estão em `test/<escopo>/**/*_test.dart`, separados de `test/integration_tests/`.
- [ ] **Padrão de escrita:** Testes seguem **AAA (Arrange / Act / Assert)** ou **Given / When / Then** com `mocktail` e `blocTest`.
- [ ] **Use case / Interactor:** Cobre `Success` E `Failure`, validando os parâmetros repassados.
- [ ] **Repository / Data source:** Cobre pelo menos os 3 caminhos (happy path, erro HTTP/status inválido e erro de transporte/exceção).
- [ ] **Model / Mapper (`fromJson` / `toEntity`):** Cobre campos obrigatórios, opcionais e rejeição/tratamento adequado de payloads inválidos (sem fallback silencioso indevido).
- [ ] **Controller / Cubit / BLoC / ViewModel:** Valida tanto a **sequência de estados** quanto os **side effects** (analytics e logs de erro com `identifier`, `message`, `pageName` e `tags` corretos).
- [ ] **Pages e Widgets de apresentação:** Validam renderização por estado, visibilidade condicional, **interação real** (`tap`, retry, etc.), **navegação/rotas** e disparos de analytics.
- [ ] **DI / GetIt:** Registra e valida todas as dependências concretas exigidas pelos construtores reais.
- [ ] **Suíte unitária verde:** `flutter test test/<escopo>` passa sem falhas e sem bater em API real.
- [ ] **Suíte integrada verde:** `flutter test test/integration_tests/<arquivos-do-alvo>` (ou `integration_test/`) passa quando existir para o escopo.
- [ ] **Cobertura LCOV >= 90%:** Cobertura agregada de linha (`linhas executadas / linhas instrumentadas * 100`) nos arquivos de produção do escopo alvo é **>= 90%**, e arquivos individuais abaixo de 90% foram analisados/cobertos.
- [ ] `flutter analyze` / `dart analyze` limpo e `git diff --check` sem erros.
- [ ] Sem `print()` / `debugPrint()` esquecidos e sem dados reais/sensíveis em mocks ou fixtures.

## Comandos de auditoria e validação

```bash
# 1. Suíte unitária e widget/page do escopo
flutter test test/<escopo>

# 2. Suíte integrada do escopo (harness em test/integration_tests)
flutter test test/integration_tests/<arquivos-do-alvo>

# 3. Cobertura LCOV do escopo
flutter test --coverage test/<escopo>

# 4. Análise estática e diff check
flutter analyze
git diff --check
```

Se o projeto usa tags para excluir testes especiais no run geral:
```bash
flutter test -x "live"
```

## O que NÃO fazer para atingir os 90%

- **Não altere código de produção** apenas para facilitar ou inflar cobertura sem necessidade funcional/arquitetural combinada com o usuário.
- **Não crie testes artificiais** para getters triviais, classes puras de constantes (`resources` estáticos sem lógica) ou construtores privados não executáveis: teste os contratos reais consumidos pelos fluxos.
- **Não misture outros módulos ou arquivos gerados** (`*.g.dart`, `*.freezed.dart`, `*.config.dart`) na conta para mascarar baixa cobertura do módulo alvo.
