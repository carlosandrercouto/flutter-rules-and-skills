# Cobertura (LCOV): gerar, filtrar por escopo e garantir >= 90%

## Meta de cobertura

O critério padrão exigido pela skill `valide-testes-unitarios` é **cobertura agregada de linha >= 90%** para o código de produção do escopo solicitado:

```text
cobertura agregada = (linhas executadas / linhas instrumentadas) * 100 >= 90%
```

Além do percentual agregado, acompanhe e reporte quaisquer arquivos executáveis individuais (`data`, `domain`, `presentation`, `di`) que fiquem abaixo de 90%.

## 1. Gerar o LCOV

Para um escopo específico (módulo ou submódulo/feature):

```bash
cd <package>
flutter test test/<escopo> --coverage
```

Quando o pacote possuir harness integrado em `test/integration_tests/` compatível com `flutter test`, você pode combinar ambos para medir a cobertura consolidada do alvo:

```bash
flutter test --coverage test/<escopo> test/integration_tests/<arquivos-do-alvo>
```

Se o projeto usa tags para excluir testes especiais:
```bash
flutter test --coverage -x "live"
```

## 2. Filtrar e calcular apenas o escopo alvo

O arquivo `coverage/lcov.info` pode conter arquivos de outros módulos carregados por import transitivo. Ao validar um módulo/submódulo (ex.: `lib/<submodulo>/`), filtre **somente os arquivos de produção daquele escopo**, ignorando:
- arquivos de outros módulos/packages;
- arquivos gerados (`*.g.dart`, `*.freezed.dart`, `*.config.dart`);
- classes formadas apenas por constantes estáticas e construtores privados não executáveis.

Cálculo rápido no terminal para um escopo `< prefixo >` (ex.: `lib/payment_summary/`):

```bash
python3 - "lib/<submodulo>/" <<'PY'
import sys

prefix = sys.argv[1]
sf = None
total_lf = 0
total_lh = 0
below_90 = []

with open('coverage/lcov.info', encoding='utf-8') as f:
    lf = lh = 0
    for line in f:
        line = line.strip()
        if line.startswith('SF:'):
            sf = line[3:]
            lf = lh = 0
        elif line.startswith('LF:'):
            lf = int(line[3:])
        elif line.startswith('LH:'):
            lh = int(line[3:])
        elif line == 'end_of_record' and sf:
            if prefix in sf and not sf.endswith(('.g.dart', '.freezed.dart', '.config.dart')):
                total_lf += lf
                total_lh += lh
                pct = (lh / lf * 100) if lf else 100.0
                if pct < 90.0:
                    below_90.append((sf, lh, lf, pct))
            sf = None

agg = (total_lh / total_lf * 100) if total_lf else 0.0
print(f"Cobertura agregada ({prefix}): {agg:.2f}% ({total_lh}/{total_lf} linhas)")
if below_90:
    print("\nArquivos abaixo de 90%:")
    for path, h, f_cnt, p in sorted(below_90, key=lambda x: x[3]):
        print(f"  - {path}: {p:.1f}% ({h}/{f_cnt})")
PY
```

## 3. Exibir com `coverage_report.py`

```bash
python skills/escrever-testes/scripts/coverage_report.py --module <mod>           # tabela do módulo no terminal
python skills/escrever-testes/scripts/coverage_report.py --module <mod> --html    # + coverage/report.html interativo
python skills/escrever-testes/scripts/coverage_report.py --module <mod> --min 90  # exit 1 se ficar abaixo de 90%
python skills/escrever-testes/scripts/coverage_report.py --module <mod> --card --png
```

## Leitura honesta (gotchas importantes)

1. **O LCOV só lista arquivo que a suíte importou.** Se um arquivo executável de `lib/<escopo>/` nunca foi importado por nenhum teste, ele não aparece no `lcov.info` nem como 0%. Sempre compare os arquivos de `lib/<escopo>/` com `test/<escopo>/`.
2. **Linha tocada por import transitivo não substitui teste unitário.** Cada camada (`data`, `domain`, `presentation`, `di`) deve ter sua própria suíte espelhada.
3. **Zero testes artificiais ou mudanças cosméticas em `lib/`.** Não altere código de produção apenas para subir percentual e não escreva testes inúteis de constantes isoladas: cubra os ramos reais de negócio, tratamento de erro, estados, side effects, navegação e interações de UI.

## Higiene

- `coverage/` é artefato local: mantenha `coverage/` no `.gitignore` (não commitar `lcov.info` nem relatórios HTML/PNG).
