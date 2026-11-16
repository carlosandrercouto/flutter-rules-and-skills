# Baseline e o jump do git

Como a `assimilar-conhecimento-documentacao` sabe o que é novo (e o que NÃO precisa reprocessar) no modo incremental. A ideia: guardar o último ponto documentado num marcador e, na próxima passada, olhar só os commits que entraram desde então, agrupados por módulo/feature.

## O marcador: `<docsRoot>/.docstate.json`

Arquivo pequeno, versionado, na raiz de `<docsRoot>/` (ex.: `docs/.docstate.json`):

```json
{
  "baseline": "<sha do HEAD na ultima passada completa>",
  "updatedAt": "2026-11-16",
  "modulesPath": "lib/app/modules/",
  "modules": {
    "login": "<ultimo sha que documentou esse modulo>",
    "home": "<sha>",
    "settings": "<sha>"
  },
  "knowledge": {
    "login-auth-flow": {
      "sha": "<sha>",
      "updatedAt": "2026-11-16",
      "html": "doc-modulos/auth/login.html",
      "md": "ia-conhecimento/login-auth-flow.md"
    }
  },
  "pendentes": {
    "prioritarios": ["<modulos de valor ainda sem doc>"],
    "baixa_prioridade": ["<modulos legados ou vazios; backfill de baixa prioridade>"]
  }
}
```

- `baseline` = de onde o `git log` parte por padrão nas execuções incrementais.
- `modulesPath` = o caminho base dos módulos no projeto (ex.: `lib/app/modules/`, `lib/features/`, `lib/modules/`, `lib/src/`). Descoberto na primeira execução e registrado para uso futuro.
- `modules{}` = o SHA por módulo, pra granularidade (um módulo pode ter sido documentado no modo pontual depois do baseline geral).
- `knowledge{}` = mapa de cada slug de conhecimento técnico (`ia-conhecimento/<slug>.md`) para o último SHA/data de atualização e os artefatos associados.
- `pendentes{}` = os módulos que ainda não possuem par HTML + Markdown documentado.
- `updatedAt` é informativo. A verdade para o modo incremental é o SHA.

Ler o baseline:

```bash
DOCS_ROOT="docs" # ou o <docsRoot> definido no projeto
BASE=$(python3 -c "import json;print(json.load(open('$DOCS_ROOT/.docstate.json'))['baseline'])")
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

Registre o caminho encontrado em `modulesPath` no `.docstate.json`.

## O jump: módulos com novidade desde a baseline

```bash
# lista dos módulos que mudaram (nome da pasta no caminho de módulos)
MODULES_PATH=$(python3 -c "import json;print(json.load(open('$DOCS_ROOT/.docstate.json')).get('modulesPath','lib/app/modules/'))")
git diff --name-only "$BASE"..HEAD -- "$MODULES_PATH" | \
  sed "s#${MODULES_PATH}##" | cut -d/ -f1 | sort -u
```

Cada nome que sai daqui é um módulo a (re)documentar nos dois formatos (`doc-modulos/` em HTML e `ia-conhecimento/` em `.md`). **Módulo que não sai NÃO é tocado no modo incremental** ("evita repassar algo que já foi feito e não foi modificado").

Detalhe por módulo (pra escrever com fidelidade):

```bash
git log --oneline "$BASE"..HEAD -- ${MODULES_PATH}<modulo>/     # os commits
git diff "$BASE"..HEAD -- ${MODULES_PATH}<modulo>/              # o que mudou
```

Docs que também mudaram na mão desde a baseline (pra não sobrescrever trabalho manual):

```bash
git diff --name-only "$BASE"..HEAD -- "$DOCS_ROOT/doc-modulos/**" "$DOCS_ROOT/ia-conhecimento/**"
```

Se a documentação de um módulo já foi alterada no range, leia os arquivos antes e apenas complemente o que falta.

## Primeira execução (sem docstate)

Sem `<docsRoot>/.docstate.json`, `"$BASE"..HEAD` não existe e o range viraria o repo inteiro. No modo incremental, escolha uma âncora explícita e **registre**:

- um release tag: `git tag --list 'v*' | sort -V | tail -1`;
- o ponto de onde as docs atuais partiram (ex.: um merge conhecido);
- `origin/main` de referência, ou um SHA que o dev indicar.

No modo pontual (um módulo/feature específico), você pode criar o `.docstate.json` registrando apenas o SHA do módulo/conhecimento documentado, deixando `baseline` para quando houver uma varredura incremental/completa.

## "Jump entre mains"

Na `main`/`master`, os merges são os pontos de integração. A baseline natural é o último ponto documentado; o jump são os merges que entraram desde então. Se o dev pedir "desde a tag X" ou "desde o merge Y", use esse ref como `BASE` no lugar do docstate.

Ver o jump em termos de merges:

```bash
git log --merges --oneline "$BASE"..HEAD
```

## Fechar a passada: gravar a nova baseline

Depois de atualizar as docs HTML, os arquivos `.md` de IA e os índices, grave o estado atualizado em `<docsRoot>/.docstate.json`:

```bash
HEAD_SHA=$(git rev-parse HEAD)
python3 - "$DOCS_ROOT" "$HEAD_SHA" <<'PY'
import json, sys, os
docs_root, sha = sys.argv[1], sys.argv[2]
p = os.path.join(docs_root, '.docstate.json')
st = json.load(open(p)) if os.path.isfile(p) else {"modules": {}, "knowledge": {}}
st['baseline'] = sha
# marque também cada módulo e conhecimento processado nesta passada:
for m in MODULOS_PROCESSADOS:            # preencha com a lista real desta run
    st.setdefault('modules', {})[m] = sha
open(p, 'w', encoding='utf-8', newline='\n').write(json.dumps(st, indent=2, ensure_ascii=False) + "\n")
PY
```

## Regras

- O SHA manda, não a data. Range incremental sempre `"$BASE"..HEAD`.
- Nunca deixe o range virar "repo inteiro" por acidente quando o pedido for apenas incremental: confirme a âncora.
- Grave o `.docstate.json` SÓ depois de a documentação (HTML + Markdown) e os índices terem sido atualizados com sucesso.
