# Baseline e o jump do git

Como a `gerar-documentacao` sabe o que é novo (e o que NÃO precisa reprocessar). A
ideia: guardar o último ponto documentado num marcador e, na próxima passada, olhar
só os commits que entraram desde então, agrupados por módulo.

## O marcador: `docs/.docstate.json`

Arquivo pequeno, versionado, na raiz de `docs/`:

```json
{
  "baseline": "<sha do HEAD na ultima passada completa>",
  "updatedAt": "2026-07-10",
  "modulesPath": "lib/app/modules/",
  "modules": {
    "login": "<ultimo sha que documentou esse modulo>",
    "home": "<sha>",
    "settings": "<sha>"
  },
  "pendentes": {
    "prioritarios": ["<modulos de valor ainda sem docs/<mod>/README.md>"],
    "baixa_prioridade": ["<modulos legados ou vazios; backfill de baixa prioridade>"]
  }
}
```

- `baseline` = de onde o `git log` parte por padrão.
- `modulesPath` = o caminho base dos módulos no projeto (ex.: `lib/app/modules/`,
  `lib/features/`, `lib/src/`). Descoberto na primeira execução e registrado para
  uso futuro.
- `modules{}` = o SHA por módulo, pra granularidade (um módulo pode ter sido
  documentado depois do baseline geral, ex. documentação pontual na sprint).
- `pendentes{}` = os módulos que ainda NÃO têm `docs/<mod>/README.md`. Existem
  porque a primeira passada preenche por lacuna, não pelo range do git (senão
  ficariam invisíveis após o baseline virar HEAD). Cada passada futura pode drenar
  essa fila (documentar mais alguns) além de pegar o que o `git log` acusar.
  `prioritarios` são os alvos de valor; `baixa_prioridade` documenta-se sob demanda.
- `updatedAt` é informativo. Não use `Date.now()` do próprio processo pra decidir
  nada; a verdade é o SHA. O marcador de "já documentado" é o `README.md` existir.

Ler o baseline:

```bash
BASE=$(python3 -c "import json,sys;print(json.load(open('docs/.docstate.json'))['baseline'])")
```

## Descobrir o caminho dos módulos

Na primeira execução, descubra e registre:

```bash
# Tente os padrões mais comuns em projetos Flutter
if [ -d "lib/app/modules" ]; then
  MODULES_PATH="lib/app/modules/"
elif [ -d "lib/features" ]; then
  MODULES_PATH="lib/features/"
elif [ -d "lib/modules" ]; then
  MODULES_PATH="lib/modules/"
elif [ -d "lib/src" ]; then
  MODULES_PATH="lib/src/"
else
  echo "Estrutura de módulos não identificada. Confirme com o usuário."
fi
```

Registre o caminho encontrado em `modulesPath` no docstate.

## O jump: módulos com novidade desde a baseline

```bash
# lista dos módulos que mudaram (nome da pasta no caminho de módulos)
MODULES_PATH=$(python3 -c "import json;print(json.load(open('docs/.docstate.json')).get('modulesPath','lib/app/modules/'))")
git diff --name-only "$BASE"..HEAD -- "$MODULES_PATH" | \
  sed "s#${MODULES_PATH}##" | cut -d/ -f1 | sort -u
```

Cada nome que sai daqui é um módulo a (re)documentar. **Módulo que não sai NÃO é
tocado** — é o coração do incremental ("evita repassar algo que já foi feito e não
foi modificado").

Detalhe por módulo (pra escrever com fidelidade):

```bash
git log --oneline "$BASE"..HEAD -- ${MODULES_PATH}<modulo>/     # os commits
git diff "$BASE"..HEAD -- ${MODULES_PATH}<modulo>/              # o que mudou
```

Docs que também mudaram na mão desde a baseline (pra não sobrescrever trabalho
manual):

```bash
git diff --name-only "$BASE"..HEAD -- 'docs/**/README.md'
```

Se um `docs/<modulo>/README.md` já foi mexido no range, leia-o antes: pode já ter
sido atualizado manualmente; aí você só complementa o que falta.

## Primeira execução (sem docstate)

Sem `docs/.docstate.json`, `"$BASE"..HEAD` não existe e o range viraria o repo
inteiro. Escolha uma âncora explícita e **registre**:

- um release tag: `git tag --list 'v*' | sort -V | tail -1`;
- o ponto de onde as docs atuais partiram (ex. um merge conhecido);
- `origin/main` de referência, ou um SHA que o dev indicar.

Diga no resumo qual âncora usou e por quê. Depois grave o docstate com HEAD.

## "Jump entre mains"

Na `main`/`master`, os merges são os pontos de integração. A baseline natural é o
último ponto documentado; o jump são os merges que entraram desde então. Se o dev
pedir "desde a tag X" ou "desde o merge Y", use esse ref como `BASE` no lugar do
docstate (sem apagar o docstate; só um alvo pontual).

Ver o jump em termos de merges:

```bash
git log --merges --oneline "$BASE"..HEAD
```

## Fechar a passada: gravar a nova baseline

Depois de atualizar as docs e o índice, escreva HEAD de volta:

```bash
HEAD_SHA=$(git rev-parse HEAD)
python3 - "$HEAD_SHA" <<'PY'
import json, sys, os
sha = sys.argv[1]
p = 'docs/.docstate.json'
st = json.load(open(p)) if os.path.isfile(p) else {"modules": {}}
st['baseline'] = sha
# marque também cada módulo processado nesta passada:
for m in MODULOS_PROCESSADOS:            # preencha com a lista real desta run
    st.setdefault('modules', {})[m] = sha
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(st, indent=2, ensure_ascii=False) + "\n")
PY
```

(A data em `updatedAt`, se quiser preencher, vem de fora do processo, ex. do
ambiente; não invente timestamp.)

## Regras

- O SHA manda, não a data. Range sempre `"$BASE"..HEAD`.
- Nunca deixe o range virar "repo inteiro" por baseline ausente: escolha a âncora.
- Só conta módulo na pasta de módulos do projeto; mudança fora disso (core, lib
  raiz, packages compartilhados) não gera doc de módulo (se for decisão estrutural,
  é ADR).
- Grave o docstate SÓ depois de a passada ter dado certo (senão você perde o range
  na próxima).
