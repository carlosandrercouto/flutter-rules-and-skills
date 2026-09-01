# Cobertura (lcov): gerar, exibir e ler com honestidade

## Gerar

```bash
flutter test --coverage    # gera coverage/lcov.info
```

Se o projeto usa tags para excluir testes especiais:
```bash
flutter test --coverage -x "live"    # exclui live tests da API real
```

Cobertura separada da integração (report próprio):

```bash
flutter test integration_test/<fluxo>_test.dart -d <device> \
  --coverage --coverage-path=coverage/lcov_integration.info
```

## Exibir

```bash
python skills/escrever-testes/scripts/coverage_report.py           # tabela por módulo no terminal
python skills/escrever-testes/scripts/coverage_report.py --html    # + coverage/report.html interativo
python skills/escrever-testes/scripts/coverage_report.py --min 40  # exit 1 abaixo de 40% (p/ gate)
python skills/escrever-testes/scripts/coverage_report.py \
  --lcov coverage/lcov_integration.info \
  --out coverage/report_integration.html --html                     # report separado (ex. integração)
```

O `report.html` abre no navegador e é interativo: stat tiles (donut do total),
faixa global do projeto e barra POR MÓDULO **empilhadas por contagem de arquivos**
(verde >=80% de linhas / amarelo 50 a 79 / vermelho <50 tocado / cinza = zero
linhas cobertas), busca, ordenação e drill-down por arquivo.

Não depende de `genhtml`/perl. Se quiser o relatório clássico linha a linha:
```bash
genhtml coverage/lcov.info -o coverage/html   # precisa do pacote lcov instalado
```

## Cobertura de UM módulo, como IMAGEM

Ao fechar a suite de um módulo, entregue um cartão PNG do número dele:

```bash
flutter test test/<mod> --coverage
python skills/escrever-testes/scripts/coverage_report.py --module <mod> --card --png
```

- `--module <mod>` filtra o lcov para o módulo (número limpo, sem o transitivo).
- `--card` escreve `coverage/card_<mod>.html` (cartão compacto).
- `--png` rasteriza em `coverage/card_<mod>.png` via headless Chrome (acha
  Chrome/Edge sozinho; sem browser, deixa o HTML e avisa).

`--module` também vale com `--html` (report interativo só daquele módulo).

## Leitura honesta (os 3 gotchas do número)

1. **O lcov só lista arquivo que a suite IMPORTOU.** Arquivo nunca importado não
   aparece nem como 0%. Por isso o report mostra "arquivos no lcov / no disco" por
   módulo: se a segunda coluna for bem maior, a cobertura real é menor que o número.
2. **Linha tocada por import transitivo não é teste.** Módulo com 0.5% no report não
   está "meio testado": só teve arquivo carregado por dependência. Cobertura de verdade
   é a dos módulos com suite própria.
3. **O bar do projeto é por costura, não por percentual mágico.** O DoD exige use case,
   repository, model e controller cobertos no código novo; o percentual é um mapa de
   calor pra achar buraco, não a meta.

## Higiene

- `coverage/` é artefato local: adicione `coverage/` ao `.gitignore` (não commitar lcov
  nem report).
