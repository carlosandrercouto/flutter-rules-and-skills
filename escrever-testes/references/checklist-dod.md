# Checklist: o bar de teste por PR (DoD)

Antes de dar a tarefa por pronta (e o que a revisão vai cobrar):

- [ ] Todo **use case / interactor** novo tem teste cobrindo `Success` E `Failure`.
- [ ] Todo **repository / data source** novo tem teste dos 3 caminhos: happy path,
      erro HTTP sem throw, e erro de transporte no catch.
- [ ] Todo **model** com `fromJson` não trivial tem teste de parsing com os ramos
      defensivos (mapa vazio, campo null, happy path).
- [ ] Todo **controller / cubit / viewmodel** novo tem teste do fluxo de estado
      (loading liga/desliga, sucesso popula, falha expõe erro sem lançar).
- [ ] Widgets de **apresentação** novos têm ao menos um smoke de render (wrap
      `MaterialApp > Theme > Scaffold`).
- [ ] `flutter test` verde local, sem bater na API real no run padrão.
- [ ] Nenhum teste novo com sufixo errado: API real só em `*_api_live_test.dart`
      (deliberado, fora do CI); integração só em `integration_test/`.
- [ ] `flutter analyze` limpo.
- [ ] Sem `print()` / `debugPrint()` esquecidos nos testes.

## Comandos de auditoria rápida

```bash
flutter test                               # suite completa
flutter test test/<modulo>                  # só o módulo
flutter analyze                            # deve ficar limpo
```

Se o projeto usa tags para excluir testes especiais:
```bash
flutter test -x "live"                     # exclui live tests
```

Listar os live tests existentes (conferir sufixo + tag `@Tags(['live'])`):

```bash
find test -name '*_api_live_test.dart' | sort
```

## O que NÃO exigir

- Cobertura percentual mágica: o bar é por costura (use case/repository/model/
  controller), não por número.
- Golden tests: só se o projeto já os adota.
- Teste de código legado que será migrado: se vai morrer, o esforço é para migrar,
  não para testar.
