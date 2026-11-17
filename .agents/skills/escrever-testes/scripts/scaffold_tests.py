#!/usr/bin/env python3
"""
scaffold_tests.py - gera os ESQUELETOS de teste de um modulo/feature Flutter.

Escaneia o modulo por convencao (use cases, repositories/data sources,
controllers, models com fromJson, widgets) e carimba os arquivos de teste em
test/<modulo>/{use_cases,repositories,controllers,models,widgets}/ com os
imports package: reais e TODOs apontando os moldes da skill.

Nao sobrescreve arquivo existente. Auto-detecta a estrutura de pastas do
projeto (lib/app/modules/, lib/features/, lib/src/, etc.).

Uso (na raiz do repo):
  python skills/escrever-testes/scripts/scaffold_tests.py --module login --dry-run
  python skills/escrever-testes/scripts/scaffold_tests.py --module login
Opcoes:
  --root <path>          raiz do repo (default: cwd)
  --package <nome>       nome do package p/ imports (default: lido do pubspec.yaml)
  --modules-path <path>  caminho dos modulos relativo a lib/ (auto-detectado se omitido)
  --dry-run              so lista o que seria gerado
"""
import argparse
import os
import re
import sys
import yaml

sys.stdout.reconfigure(encoding="utf-8")


def read_package_name(root):
    """Le o nome do package do pubspec.yaml."""
    pubspec = os.path.join(root, "pubspec.yaml")
    try:
        with open(pubspec, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return data.get("name", "app")
    except (OSError, ValueError):
        return "app"


def detect_modules_path(root):
    """Auto-detecta o caminho dos modulos/features no projeto."""
    candidates = [
        "app/modules",
        "features",
        "modules",
        "src",
    ]
    for c in candidates:
        p = os.path.join(root, "lib", c)
        if os.path.isdir(p):
            return c
    return None


def rel_import(package, root, dart_file):
    rel = os.path.relpath(dart_file, os.path.join(root, "lib")).replace(os.sep, "/")
    return f"package:{package}/{rel}"


def find_class(path, pattern):
    try:
        src = open(path, encoding="utf-8").read()
    except OSError:
        return None
    m = re.search(pattern, src)
    return m.group(1) if m else None


def has_from_json(path):
    try:
        src = open(path, encoding="utf-8").read()
    except OSError:
        return False
    return "fromJson" in src or "fromMap" in src


def scan(root, module, modules_path):
    base = os.path.join(root, "lib", modules_path, module)
    if not os.path.isdir(base):
        sys.exit(f"modulo nao encontrado: {base}")

    targets = {"use_case": [], "repository": [], "controller": [], "model": [], "widget": []}

    # Procura use cases em varias estruturas possiveis
    uc_dirs = [
        os.path.join(base, "app", "application", "use_cases"),
        os.path.join(base, "domain", "use_cases"),
        os.path.join(base, "domain", "usecases"),
        os.path.join(base, "application", "use_cases"),
        os.path.join(base, "use_cases"),
    ]
    for uc_dir in uc_dirs:
        if os.path.isdir(uc_dir):
            for f in sorted(os.listdir(uc_dir)):
                if f.endswith(".dart"):
                    p = os.path.join(uc_dir, f)
                    cls = find_class(p, r"class\s+(\w+)\s+(?:extends|implements)\s+\w*(?:UseCase|IUseCase|Interactor)")
                    if not cls:
                        cls = find_class(p, r"class\s+(\w+UseCase)")
                    if cls:
                        targets["use_case"].append((p, cls))
            break

    # Procura repositories/data sources
    ds_dirs = [
        os.path.join(base, "app", "infra", "data_source"),
        os.path.join(base, "data", "repositories"),
        os.path.join(base, "data", "datasources"),
        os.path.join(base, "infra", "repositories"),
        os.path.join(base, "infra", "data_sources"),
        os.path.join(base, "repositories"),
    ]
    for ds_dir in ds_dirs:
        if os.path.isdir(ds_dir):
            for f in sorted(os.listdir(ds_dir)):
                if f.endswith(".dart"):
                    p = os.path.join(ds_dir, f)
                    cls = find_class(p, r"class\s+(\w+)[^{]*\b(?:implements|extends)\s+I\w*(?:DataSource|Repository)")
                    if not cls:
                        cls = find_class(p, r"class\s+(\w+(?:Repository|DataSource))\b")
                    if cls:
                        targets["repository"].append((p, cls))
            break

    # Procura controllers/cubits/viewmodels em qualquer lugar do modulo
    controller_patterns = [
        r"class\s+(\w+)\s+extends\s+(?:ControllerBase|ChangeNotifier|ValueNotifier|Cubit|Bloc)\b",
        r"class\s+(\w+(?:Controller|Cubit|Bloc|ViewModel))\b",
    ]
    for dirpath, _, files in os.walk(base):
        for f in sorted(files):
            if f.endswith("_controller.dart") or f.endswith("_cubit.dart") or \
               f.endswith("_bloc.dart") or f.endswith("_viewmodel.dart"):
                p = os.path.join(dirpath, f)
                cls = None
                for pat in controller_patterns:
                    cls = find_class(p, pat)
                    if cls:
                        break
                if cls:
                    targets["controller"].append((p, cls))

    # Procura models com fromJson
    mdl_dirs = [
        os.path.join(base, "app", "domain", "models"),
        os.path.join(base, "domain", "entities"),
        os.path.join(base, "domain", "models"),
        os.path.join(base, "data", "models"),
        os.path.join(base, "models"),
    ]
    for mdl_dir in mdl_dirs:
        if os.path.isdir(mdl_dir):
            for f in sorted(os.listdir(mdl_dir)):
                if f.endswith(".dart"):
                    p = os.path.join(mdl_dir, f)
                    if has_from_json(p):
                        cls = find_class(p, r"class\s+(\w+)")
                        if cls:
                            targets["model"].append((p, cls))
            break

    # Procura widgets do presenter/presentation
    wd_dirs = [
        os.path.join(base, "app", "presenter", "widgets"),
        os.path.join(base, "presentation", "widgets"),
        os.path.join(base, "presenter", "widgets"),
        os.path.join(base, "ui", "widgets"),
        os.path.join(base, "widgets"),
    ]
    for wd_dir in wd_dirs:
        if os.path.isdir(wd_dir):
            for f in sorted(os.listdir(wd_dir)):
                if f.endswith(".dart"):
                    p = os.path.join(wd_dir, f)
                    cls = find_class(p, r"class\s+(\w+)\s+extends\s+(StatelessWidget|StatefulWidget)")
                    if cls:
                        targets["widget"].append((p, cls))
            break

    return targets


# ---------------- templates ----------------

HEADER = "// Esqueleto gerado pela skill escrever-testes (scaffold_tests.py).\n" \
         "// Preencha os TODOs com os moldes: skills/escrever-testes/references/moldes.md\n"


def t_use_case(imp, cls):
    return f"""{HEADER}// Molde M1: use case cobre SEMPRE Success e Failure.
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import '{imp}';

// TODO(M1): mocks de CONTRATO (nunca classe concreta):
// class _MockRepository extends Mock implements I<Mod>Repository {{}}

void main() {{
  // TODO(M1): setUpAll -> registerFallbackValue(<request>) p/ any() com tipo proprio.
  // TODO(M1): setUp -> instancie {cls}(repository: _MockRepository()).

  test('sucesso: devolve o resultado mapeado', () async {{
    fail('TODO(M1): when(...).thenAnswer((_) async => Success(...)); expect isSuccess + verify called(1)');
  }});

  test('falha: propaga o Failure sem lancar', () async {{
    fail('TODO(M1): when(...).thenAnswer((_) async => Failure(...)); expect isError');
  }});
}}
"""


def t_repository(imp, cls):
    return f"""{HEADER}// Molde M2: repository/data source cobre os 3 caminhos (happy path, erro HTTP, transporte).
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import '{imp}';

// TODO(M2): importe o HTTP client/adapter do projeto e crie o mock:
// class _MockHttp extends Mock implements IHttpClient {{}}

void main() {{
  // TODO(M2): late _MockHttp http;
  // TODO(M2): late {cls} repository;

  setUp(() {{
    // TODO(M2): http = _MockHttp();
    // TODO(M2): repository = {cls}(httpClient: http);
  }});

  test('200: mapeia o data pro model', () async {{
    fail('TODO(M2): stub de resposta 200, chame o metodo e expect isSuccess');
  }});

  test('erro HTTP: vira Failure, nao lanca', () async {{
    fail('TODO(M2): stub de resposta 500, chame o metodo e expect isError');
  }});

  test('transporte: excecao cai no catch e vira erro generico', () async {{
    fail('TODO(M2): stub com thenThrow, chame o metodo e confira o Failure');
  }});
}}
"""


def t_controller(imp, cls):
    return f"""{HEADER}// Molde M4: controller dirige o estado sem pumpar widget.
import 'package:flutter_test/flutter_test.dart';
import 'package:mocktail/mocktail.dart';

import '{imp}';

void main() {{
  // TODO(M4): mocke os use cases do {cls} e instancie o controller.

  test('load: liga o loading, popula e desliga', () async {{
    fail('TODO(M4): addListener no loading, await load(), expect([true, false]) e estado populado');
  }});

  test('falha: nao lanca e expoe o estado de erro', () async {{
    fail('TODO(M4): stub de Failure e expect do estado de erro');
  }});
}}
"""


def t_model(imp, cls):
    return f"""{HEADER}// Molde M3: fromJson defensivo, table-driven.
import 'package:flutter_test/flutter_test.dart';

import '{imp}';

void main() {{
  test('fromJson aguenta mapa vazio (defensivo)', () {{
    expect(() => {cls}.fromJson(const <String, dynamic>{{}}), returnsNormally);
  }});

  // TODO(M3): estenda a tabela com null por campo e o happy path com valores reais.
}}
"""


def t_widgets(module, widgets, package):
    lst = "\n".join(f"//   - {cls}  ({os.path.basename(p)})" for p, cls in widgets)
    return f"""{HEADER}// Molde M5: smoke de render dos widgets burros (sem rede, sem controller).
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

// Widgets encontrados no modulo {module}:
{lst}

Future<void> pump(WidgetTester tester, Widget child) {{
  return tester.pumpWidget(
    MaterialApp(
      // TODO(M5): se o projeto tem ThemeData customizado, use-o aqui
      home: Scaffold(body: SingleChildScrollView(child: child)),
    ),
  );
}}

void main() {{
  test('TODO(M5): escolha os widgets burros e pumpe com dado de exemplo', () {{
    fail('TODO(M5): um testWidgets por widget relevante; expect(find.text(...), findsOneWidget)');
  }});
}}
"""


def main():
    ap = argparse.ArgumentParser(description="Gera esqueletos de teste de um modulo/feature Flutter.")
    ap.add_argument("--module", required=True, help="nome do modulo/feature")
    ap.add_argument("--root", default=".", help="raiz do repo (default: cwd)")
    ap.add_argument("--package", default=None, help="nome do package (default: lido do pubspec.yaml)")
    ap.add_argument("--modules-path", default=None,
                    help="caminho relativo a lib/ dos modulos (auto-detectado se omitido)")
    ap.add_argument("--dry-run", action="store_true", help="so lista o que seria gerado")
    args = ap.parse_args()

    root = os.path.abspath(args.root)

    # Package name
    package = args.package
    if not package:
        try:
            package = read_package_name(root)
        except Exception:
            package = "app"
    print(f"package: {package}")

    # Modules path
    modules_path = args.modules_path
    if not modules_path:
        modules_path = detect_modules_path(root)
        if not modules_path:
            sys.exit("nao consegui detectar a pasta de modulos/features. "
                     "Use --modules-path <path relativo a lib/>")
    print(f"modules path: lib/{modules_path}/")

    targets = scan(root, args.module, modules_path)

    plans = []  # (out_path, content)
    out_base = os.path.join(root, "test", args.module)

    for p, cls in targets["use_case"]:
        out = os.path.join(out_base, "use_cases", os.path.basename(p).replace(".dart", "_test.dart"))
        plans.append((out, t_use_case(rel_import(package, root, p), cls)))
    for p, cls in targets["repository"]:
        out = os.path.join(out_base, "repositories", os.path.basename(p).replace(".dart", "_test.dart"))
        plans.append((out, t_repository(rel_import(package, root, p), cls)))
    for p, cls in targets["controller"]:
        out = os.path.join(out_base, "controllers", os.path.basename(p).replace(".dart", "_test.dart"))
        plans.append((out, t_controller(rel_import(package, root, p), cls)))
    for p, cls in targets["model"]:
        out = os.path.join(out_base, "models", os.path.basename(p).replace(".dart", "_test.dart"))
        plans.append((out, t_model(rel_import(package, root, p), cls)))
    if targets["widget"]:
        out = os.path.join(out_base, "widgets", "smoke_test.dart")
        plans.append((out, t_widgets(args.module, targets["widget"], package)))

    if not plans:
        sys.exit("nada testavel encontrado. Confira a estrutura do modulo e o --modules-path.")

    created, skipped = 0, 0
    for out, content in plans:
        exists = os.path.isfile(out)
        mark = "SKIP (ja existe)" if exists else ("DRY " if args.dry_run else "CRIA")
        print(f"  {mark:18s} {os.path.relpath(out, root)}")
        if exists:
            skipped += 1
            continue
        if not args.dry_run:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            with open(out, "w", encoding="utf-8", newline="\n") as fh:
                fh.write(content)
            created += 1

    resumo = f"alvos: {sum(len(v) for v in targets.values())} | arquivos: {len(plans)} | criados: {created} | pulados: {skipped}"
    print(("[dry-run] " if args.dry_run else "") + resumo)
    if created and not args.dry_run:
        print("proximo passo: preencher os TODOs (references/moldes.md) e rodar: flutter test test/" + args.module)


if __name__ == "__main__":
    main()
