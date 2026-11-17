# Moldes de teste (M1 a M8)

Código genérico para qualquer projeto Flutter, estruturado em **AAA (Arrange / Act / Assert)** ou **Given / When / Then**. Adapte os nomes de classes, imports e contratos ao seu projeto. Em `test/`, os imports são sempre `package:<nome_do_pacote>/...`.

## M1 · Use case / Interactor (Success E Failure, sempre os dois)

```dart
// test/<escopo>/domain/use_cases/<nome>_use_case_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

class MockRepository extends Mock implements IExampleRepository {}

void main() {
  late MockRepository repository;
  late ExampleUseCase useCase;
  final request = ExampleRequest(id: 1);

  setUpAll(() => registerFallbackValue(request));

  setUp(() {
    repository = MockRepository();
    useCase = ExampleUseCase(repository: repository);
  });

  test('sucesso: repassa o resultado do repository', () async {
    // Arrange
    when(() => repository.execute(any()))
        .thenAnswer((_) async => Success(ExampleResult(value: 42)));

    // Act
    final result = await useCase(request);

    // Assert
    expect(result.isSuccess, isTrue);
    verify(() => repository.execute(request)).called(1);
  });

  test('falha: propaga o Failure sem lançar exceção', () async {
    // Arrange
    when(() => repository.execute(any()))
        .thenAnswer((_) async => Failure(AppFailure.unknown()));

    // Act
    final result = await useCase(request);

    // Assert
    expect(result.isError, isTrue);
    verify(() => repository.execute(request)).called(1);
  });
}
```

## M2 · Repository / Data source (3 caminhos: happy path, erro HTTP, transporte)

```dart
// test/<escopo>/data/repositories/<nome>_repository_impl_test.dart
class MockHttpClient extends Mock implements IHttpClient {}

void main() {
  late MockHttpClient http;
  late ExampleRepository repository;

  setUp(() {
    http = MockHttpClient();
    repository = ExampleRepository(httpClient: http);
  });

  test('200: mapeia o payload para a entidade/model', () async {
    when(() => http.post(any(), data: any(named: 'data'))).thenAnswer(
        (_) async => HttpResponse(data: {'value': 42}, statusCode: 200));

    final result = await repository.execute(request);

    expect(result.isSuccess, isTrue);
  });

  test('500: converte erro HTTP em Failure sem vazar exceção não tratada', () async {
    when(() => http.post(any(), data: any(named: 'data'))).thenAnswer(
        (_) async => HttpResponse(data: null, statusCode: 500));

    final result = await repository.execute(request);

    expect(result.isError, isTrue);
  });

  test('transporte: exceção de rede cai no catch e retorna falha', () async {
    when(() => http.post(any(), data: any(named: 'data')))
        .thenThrow(Exception('timeout'));

    final result = await repository.execute(request);

    expect(result.isError, isTrue);
  });
}
```

## M3 · Model / Mapper (`fromJson` e validação de contrato)

```dart
// test/<escopo>/data/models/<nome>_model_test.dart
group('ExampleModel.fromJson', () {
  test('mapeia corretamente payload válido completo e com campos opcionais nulos', () {
    final model = ExampleModel.fromJson({
      'id': '123',
      'title': 'Resumo',
      'subtitle': null,
    });

    expect(model.id, '123');
    expect(model.title, 'Resumo');
    expect(model.subtitle, isNull);
  });

  test('lança FormatException/TypeError quando campo obrigatório do contrato está inválido', () {
    expect(
      () => ExampleModel.fromJson({'id': null}),
      throwsA(isA<Object>()),
    );
  });
});
```

## M4 · Controller / Cubit / BLoC (sequência de estados E side effects)

### Variante BLoC / Cubit (validando estado + analytics/logs)

```dart
// test/<escopo>/presentation/cubit/<nome>_cubit_test.dart
class MockUseCase extends Mock implements IExampleUseCase {}
class MockAnalytics extends Mock implements IAnalyticsService {}

void main() {
  late MockUseCase useCase;
  late MockAnalytics analytics;

  setUp(() {
    useCase = MockUseCase();
    analytics = MockAnalytics();
  });

  blocTest<ExampleCubit, ExampleState>(
    'load emite [ExampleLoading, ExampleLoaded] quando useCase retorna sucesso',
    build: () {
      when(() => useCase()).thenAnswer((_) async => Success(dataDemo));
      return ExampleCubit(useCase: useCase, analytics: analytics);
    },
    act: (cubit) => cubit.load(),
    expect: () => [
      isA<ExampleLoading>(),
      isA<ExampleLoaded>(),
    ],
    verify: (_) {
      verify(() => useCase()).called(1);
    },
  );

  blocTest<ExampleCubit, ExampleState>(
    'load emite [ExampleLoading, ExampleError] e registra log de erro quando falha',
    build: () {
      when(() => useCase()).thenAnswer((_) async => Failure(AppFailure.server()));
      return ExampleCubit(useCase: useCase, analytics: analytics);
    },
    act: (cubit) => cubit.load(),
    expect: () => [
      isA<ExampleLoading>(),
      isA<ExampleError>(),
    ],
    verify: (_) {
      verify(
        () => analytics.trackErrorLog(
          identifier: 'example_load_error',
          message: any(named: 'message'),
          pageName: 'example_page',
        ),
      ).called(1);
    },
  );
}
```

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
```

## M5 · Page / Widget (renderização, interação, navegação e analytics)

```dart
// test/<escopo>/presentation/pages/<nome>_page_test.dart
class MockExampleCubit extends MockCubit<ExampleState> implements ExampleCubit {}
class MockNavigatorObserver extends Mock implements NavigatorObserver {}

void main() {
  late MockExampleCubit cubit;
  late MockAnalytics analytics;

  setUp(() {
    cubit = MockExampleCubit();
    analytics = MockAnalytics();
  });

  Widget makeTestableWidget(Widget child) {
    return MaterialApp(
      routes: {
        '/details': (_) => const Scaffold(body: Text('Detalhes Page')),
      },
      home: BlocProvider<ExampleCubit>.value(
        value: cubit,
        child: child,
      ),
    );
  }

  testWidgets('exibe conteúdo no estado carregado, dispara analytics e navega ao tocar no card',
      (tester) async {
    // Arrange
    when(() => cubit.state).thenReturn(ExampleLoaded(items: [sampleItem()]));

    // Act
    await tester.pumpWidget(makeTestableWidget(ExamplePage(analytics: analytics)));
    await tester.pump();

    // Assert renderização
    expect(find.text('Título exemplo'), findsOneWidget);

    // Act interação
    await tester.tap(find.text('Título exemplo'));
    await tester.pumpAndSettle();

    // Assert analytics e navegação
    verify(() => analytics.trackClick(tag: 'example_card_tap')).called(1);
    expect(find.text('Detalhes Page'), findsOneWidget);
  });

  testWidgets('no estado de erro exibe feedback e aciona retry ao clicar no botão',
      (tester) async {
    when(() => cubit.state).thenReturn(const ExampleError());
    when(() => cubit.load()).thenAnswer((_) async {});

    await tester.pumpWidget(makeTestableWidget(ExamplePage(analytics: analytics)));
    await tester.tap(find.text('Tentar novamente'));
    await tester.pump();

    verify(() => cubit.load()).called(1);
  });
}
```

## M6 · Integração (`test/integration_tests/` e `integration_test/`)

### Variante A: Harness integrado de pacote (`test/integration_tests/<fluxo>_test.dart`)

Executado via `flutter test test/integration_tests/<fluxo>_test.dart`, integrando Page + Cubit real + UseCase real + Repository real + DI/GetIt com mock apenas na borda HTTP/servidor:

```dart
// test/integration_tests/example_flow_integration_test.dart
void main() {
  setUp(() async {
    await GetIt.I.reset();
    // Registre o módulo de DI real e substitua apenas o client HTTP/mock server
    configureExampleDependencies(GetIt.I, httpClient: mockHttpClient);
  });

  tearDown(() async {
    await GetIt.I.reset();
  });

  testWidgets('fluxo completo: carrega dados do mock server, renderiza page e navega',
      (tester) async {
    when(() => mockHttpClient.get(any())).thenAnswer(
      (_) async => HttpResponse(data: validPayloadFixture, statusCode: 200),
    );

    await tester.pumpWidget(const MaterialApp(home: ExamplePage()));
    await tester.pumpAndSettle();

    expect(find.text('Título vindo do payload'), findsOneWidget);
  });
}
```

### Variante B: Smoke E2E em device/emulador (`integration_test/<fluxo>_test.dart`)

```dart
// integration_test/example_flow_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';
import 'package:<pkg>/main.dart' as app;

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
```

## M7 · Regra com tempo (clock injetável, nunca `DateTime.now()` implícito)

```dart
class ExampleBusiness {
  final DateTime Function() now;
  const ExampleBusiness({this.now = DateTime.now});

  bool expirado(DateTime fim) => fim.isBefore(now());
}

test('expirado quando o fim já passou', () {
  final business = ExampleBusiness(now: () => DateTime(2024, 8, 10, 12));

  expect(business.expirado(DateTime(2024, 8, 10, 11, 59)), isTrue);
  expect(business.expirado(DateTime(2024, 8, 10, 12, 1)), isFalse);
});
```

## M8 · Injeção de Dependência (DI / GetIt)

Valida que todas as factories e singletons do módulo resolvem no container de DI com todas as dependências exigidas pelos construtores reais:

```dart
// test/<escopo>/di/<nome>_di_test.dart
void main() {
  final getIt = GetIt.instance;

  setUp(() async {
    await getIt.reset();
    // Registra dependências externas exigidas pelo módulo
    getIt.registerLazySingleton<IHttpClient>(() => MockHttpClient());
    getIt.registerLazySingleton<IAnalyticsService>(() => MockAnalytics());
    // Inicializa o registro do módulo (gerado por injectable ou módulo de DI)
    initExampleModuleDependencies(getIt);
  });

  tearDown(() async {
    await getIt.reset();
  });

  test('resolve ExampleCubit e todas as suas dependências no GetIt', () {
    final cubit = getIt<ExampleCubit>();
    expect(cubit, isA<ExampleCubit>());
    cubit.close();
  });
}
```
