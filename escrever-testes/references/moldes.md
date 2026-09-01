# Moldes de teste (M1 a M7)

Código genérico para qualquer projeto Flutter. Adapte os nomes de classes,
imports e contratos ao seu projeto. Em `test/`, os imports são
`package:<nome_do_pacote>/...` (o lint de import relativo vale só para `lib/`).

## M1 · Use case / Interactor (Success E Failure, sempre os dois)

```dart
// test/<mod>/use_cases/<nome>_use_case_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

// Adapte os imports ao seu projeto:
// import 'package:<pkg>/features/<mod>/domain/use_cases/<nome>_use_case.dart';
// import 'package:<pkg>/features/<mod>/domain/repositories/i_<mod>_repository.dart';

class MockRepository extends Mock implements IExampleRepository {}

void main() {
  late MockRepository repository;
  late ExampleUseCase useCase;
  final request = ExampleRequest(id: 1);

  setUpAll(() => registerFallbackValue(request)); // habilita any() com tipo próprio

  setUp(() {
    repository = MockRepository();
    useCase = ExampleUseCase(repository: repository);
  });

  test('sucesso: repassa o resultado do repository', () async {
    when(() => repository.execute(any()))
        .thenAnswer((_) async => Success(ExampleResult(value: 42)));

    final result = await useCase(request);

    expect(result.isSuccess, isTrue);
    verify(() => repository.execute(request)).called(1);
  });

  test('falha: propaga o Failure sem lançar', () async {
    when(() => repository.execute(any()))
        .thenAnswer((_) async => Failure(AppFailure.unknown()));

    final result = await useCase(request);

    expect(result.isError, isTrue);
  });
}
```

> **Nota:** Adapte `Success`/`Failure` ao padrão do projeto (`Result`, `Either`,
> `dartz`, exceções, etc.). O importante é testar SEMPRE os dois caminhos.

## M2 · Repository / Data source (3 caminhos: happy path, erro HTTP, transporte)

```dart
class MockHttpClient extends Mock implements IHttpClient {}

void main() {
  late MockHttpClient http;
  late ExampleRepository repository;

  setUp(() {
    http = MockHttpClient();
    repository = ExampleRepository(httpClient: http);
  });

  test('200: mapeia o data pro model', () async {
    when(() => http.post(any(), data: any(named: 'data'))).thenAnswer(
        (_) async => HttpResponse(data: {'value': 42}, statusCode: 200));

    final result = await repository.execute(request);

    expect(result.isSuccess, isTrue);
  });

  test('500: vira Failure, não lança', () async {
    when(() => http.post(any(), data: any(named: 'data'))).thenAnswer(
        (_) async => HttpResponse(data: null, statusCode: 500));

    final result = await repository.execute(request);

    expect(result.isError, isTrue);
  });

  test('transporte: exceção cai no catch e vira erro genérico', () async {
    when(() => http.post(any(), data: any(named: 'data')))
        .thenThrow(Exception('timeout'));

    final result = await repository.execute(request);

    expect(result.isError, isTrue);
  });
}
```

> Se o projeto usa Dio diretamente, o mock é do `Dio` ou de um adapter customizado.
> Adapte `HttpResponse` ao tipo real do projeto.

## M3 · Model fromJson defensivo (table-driven)

```dart
test('fromJson aguenta null e chave faltando', () {
  final casos = <Map<String, dynamic>>[
    {},                              // tudo faltando
    {'name': null},                  // campo nulo
    {'name': 'Example', 'value': 42}, // happy path
  ];
  for (final json in casos) {
    expect(() => ExampleModel.fromJson(json), returnsNormally, reason: '$json');
  }
  expect(ExampleModel.fromJson({'name': 'Example', 'value': 42}).value, 42);
});
```

## M4 · Controller / Cubit / ViewModel (fluxo de estado, sem pumpar widget)

### Variante ValueNotifier / ChangeNotifier

```dart
test('load: liga o loading, popula e desliga', () async {
  when(() => useCase(any())).thenAnswer((_) async => Success(dataDemo));
  final passos = <bool>[];
  controller.loading.addListener(() => passos.add(controller.loading.value));

  await controller.load();

  expect(passos, [true, false]);
  expect(controller.items.value, isNotEmpty);
});

test('falha: não lança e expõe o estado de erro', () async {
  when(() => useCase(any()))
      .thenAnswer((_) async => Failure(AppFailure.unknown()));

  await controller.load();

  expect(controller.errorMessage.value, isNotEmpty);
});
```

### Variante BLoC / Cubit

```dart
blocTest<ExampleCubit, ExampleState>(
  'load emite [loading, loaded]',
  build: () {
    when(() => useCase(any())).thenAnswer((_) async => Success(dataDemo));
    return ExampleCubit(useCase: useCase);
  },
  act: (cubit) => cubit.load(),
  expect: () => [
    isA<ExampleLoading>(),
    isA<ExampleLoaded>(),
  ],
);
```

> Adapte ao gerenciamento de estado do projeto. O importante é testar a transição
> de estados: loading → sucesso / loading → erro.

## M5 · Widget smoke (render sem rede, sem controller)

```dart
// widget burro + dado de exemplo; sem rede, sem controller
Future<void> pump(WidgetTester tester, Widget child) {
  return tester.pumpWidget(
    MaterialApp(
      // Se o projeto tem ThemeData customizado, use-o aqui:
      // theme: AppTheme.light(),
      home: Scaffold(body: SingleChildScrollView(child: child)),
    ),
  );
}

testWidgets('ExampleCard mostra título e descrição', (tester) async {
  await pump(tester, ExampleCard(item: sampleItem()));

  expect(find.text('Título exemplo'), findsOneWidget);
  expect(find.text('Descrição'), findsOneWidget);
});
```

> Se o projeto tem um wrapper de tema obrigatório (ex.: `AppTheme`, `ThemeProvider`),
> inclua-o no `pump`.

## M6 · Integração (smoke de fluxo crítico, integration_test oficial)

```dart
// integration_test/example_flow_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:<pkg>/main.dart' as app;

// Se o app tem splash animado: pumpAndSettle não assenta. Use poll:
Future<void> pumpUntilFound(WidgetTester tester, Finder finder,
    {Duration timeout = const Duration(seconds: 30)}) async {
  final fim = DateTime.now().add(timeout);
  while (DateTime.now().isBefore(fim)) {
    await tester.pump(const Duration(milliseconds: 250));
    if (finder.evaluate().isNotEmpty) return;
  }
  fail('não apareceu: $finder');
}

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('fluxo principal funciona', (tester) async {
    app.main();
    await pumpUntilFound(tester, find.text('Home'));
    expect(find.text('Home'), findsOneWidget);
  });
}
// rodar: flutter test integration_test/example_flow_test.dart -d <device>
```

## M7 · Regra com tempo (clock injetável, nunca DateTime.now() implícito)

Caso clássico: teste quebra anos depois sem ninguém tocar no código, porque a
lógica compara com `DateTime.now()` e o teste usava datas fixas do passado.
Bomba-relógio. A regra: lógica que depende de "agora" recebe o relógio por
parâmetro (default produção), e o teste FIXA o relógio.

```dart
// produção: default continua DateTime.now, nada muda pra quem chama
class ExampleBusiness {
  final DateTime Function() now;
  const ExampleBusiness({this.now = DateTime.now});

  bool expirado(DateTime fim) => fim.isBefore(now());
}

// teste: relógio congelado, o teste nunca envelhece
test('expirado quando o fim já passou', () {
  final business = ExampleBusiness(now: () => DateTime(2024, 8, 10, 12));

  expect(business.expirado(DateTime(2024, 8, 10, 11, 59)), isTrue);
  expect(business.expirado(DateTime(2024, 8, 10, 12, 1)), isFalse);
});
```

> Alternativa: use o pacote `clock` do Dart. Mas o padrão de injeção por parâmetro
> funciona sem dependência extra.

Sinal de alerta em review: `DateTime.now()` dentro de regra de negócio testável.
Sintoma clássico: "teste quebrou e ninguém mexeu no código" = suspeite do relógio.
