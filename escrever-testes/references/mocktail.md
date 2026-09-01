# Mocktail: regras de uso e armadilhas

Instalação (uma vez, no `pubspec.yaml`):

```yaml
dev_dependencies:
  mocktail: ^1.0.4
```

Depois `flutter pub get`.

## O essencial

```dart
class MockX extends Mock implements X {}                 // mock de CONTRATO, nunca de classe concreta
when(() => mock.metodo(any())).thenAnswer((_) async => valor);  // stub async (Future)
when(() => mock.metodo(any())).thenReturn(valor);               // stub síncrono
when(() => mock.metodo(any())).thenThrow(Exception());          // stub de erro
verify(() => mock.metodo(request)).called(1);                   // verificação exata
verifyNever(() => mock.metodo(any()));                          // nunca chamado
registerFallbackValue(MeuRequest(...));   // no setUpAll, p/ any() com tipo próprio
```

## Regras

- **Mocka-se contrato/interface**: `IRepository`, `IHttpClient`, `IAuthService`,
  `IUseCase`. Nunca a classe concreta de infra (se precisou mockar concreta, o
  design está furado; conserte o contrato).
- **Model puro não se mocka**: instancie de verdade (é barato e testa o construtor).
- `registerFallbackValue` é por TIPO, uma vez no `setUpAll` do arquivo. Sem ele,
  `any()` com tipo próprio lança em runtime.
- Parâmetro nomeado usa `any(named: 'data')` (o nome é o do parâmetro, em string).
- `thenAnswer` para retorno `Future`/`Stream`; `thenReturn` num `Future` dá bug sutil
  (mesma instância reaproveitada). Na dúvida, `thenAnswer`.
- `captureAny()` + `verify(...).captured` quando precisar inspecionar o argumento.
- Um mock por teste lógico; se o setup de mocks passar de ~10 linhas, o alvo está
  fazendo coisa demais (sinal de design, não de teste).

## Armadilhas conhecidas

- Esquecer `await` no método testado: o teste passa em falso. Sempre `await`.
- Stub genérico demais (`any()` em tudo) esconde regressão de request: prefira
  `verify(() => repo.metodo(request))` com o objeto exato quando ele importa.
- Mock de serviço de analytics/crashlytics sem stub: os métodos void de Mock viram
  no-op por padrão no mocktail, não precisa stubar (só não esqueça o mock no
  construtor se a classe base exige).
- Não reutilize mock entre testes sem `setUp` recriando (estado de verify vaza).
