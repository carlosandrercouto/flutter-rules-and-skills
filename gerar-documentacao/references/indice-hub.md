# Manter o índice (hub de documentação)

O hub é a porta de entrada das docs. A `gerar-documentacao` é quem mantém as
entradas de módulo lá. Objetivo: **uma entrada por módulo documentado**, sempre
coerente com o que existe em `docs/<modulo>/`.

## Formato do hub

O hub pode ser um `docs/index.html` (visual, com cards) ou um `docs/README.md`
(markdown simples). Escolha o formato na primeira execução e mantenha.

### Opção A: HTML com cards (`docs/index.html`)

Se o projeto já tem um `index.html` com cards, siga o padrão existente. Se for
criar do zero, use esta estrutura:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Documentação — <Nome do Projeto></title>
  <style>
    body { font-family: system-ui, sans-serif; max-width: 900px; margin: 2rem auto; padding: 0 1rem; }
    .grp { font-size: 1.2rem; font-weight: 600; margin: 2rem 0 1rem; color: #333; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 1rem; }
    .card { display: block; padding: 1rem; border: 1px solid #e0e0e0; border-radius: 8px;
            text-decoration: none; color: inherit; transition: box-shadow 0.2s; }
    .card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.12); }
    .ct { font-weight: 600; margin-bottom: 0.4rem; }
    .ic { font-size: 1.2rem; }
    .cd { font-size: 0.9rem; color: #666; margin-bottom: 0.5rem; }
    .cp { font-size: 0.8rem; color: #999; font-family: monospace; }
  </style>
</head>
<body>
  <h1>📚 <Nome do Projeto> — Documentação</h1>

  <div class="grp">Documentação por módulo</div>
  <div class="grid">
    <!-- cards de módulo aqui -->
  </div>
</body>
</html>
```

Formato do card:

```html
<a class="card" href="<modulo>/README.md">
  <div class="ct"><span class="ic"><emoji></span> <Título do módulo></div>
  <div class="cd"><uma ou duas frases do que o módulo faz></div>
  <span class="cp"><modulo>/</span>
</a>
```

- `href` e `cp` apontam pra `<modulo>/README.md` e `<modulo>/` (relativo ao hub).
- `ic` é um emoji que combine com o módulo.
- `cd` é a mesma frase-resumo da Visão geral do `README.md`, curta.

### Opção B: Markdown (`docs/README.md`)

```markdown
# 📚 <Nome do Projeto> — Documentação

## Módulos documentados

| Módulo | Descrição |
|--------|-----------|
| [login](login/README.md) | Autenticação e onboarding do usuário |
| [home](home/README.md) | Tela principal com dashboard |
| [settings](settings/README.md) | Configurações do app e perfil |
```

## Procedimento de sincronização

1. Liste os módulos que têm doc:
   ```bash
   ls -d docs/*/ | sed 's#docs/##;s#/##' | sort
   ```
   Filtre as pastas que NÃO são módulo (ex.: `adr/`, `processo/`, `web/`) — ajuste
   a lista de exclusão conforme o projeto.

2. Para cada módulo com `docs/<modulo>/README.md`:
   - **Entrada ausente no hub** → adicione, com título e resumo tirados do próprio
     README.
   - **Entrada presente** → confira se o resumo ainda bate com a Visão geral;
     atualize se o módulo mudou de escopo.

3. **Entrada apontando pra doc que não existe mais** (módulo removido/renomeado) →
   remova a entrada (e trate a doc obsoleta conforme a SKILL.md).

4. Ordene as entradas de forma estável (alfabética por módulo é um jeito simples de
   não embaralhar o diff a cada passada).

## Validar

Se for HTML, sirva local e confira que abre sem link quebrado:

```bash
python3 -m http.server -d docs 8756   # abre http://localhost:8756/index.html
```

Se for Markdown, confira que os links relativos resolvem.

Cheque: cada entrada de módulo abre o `README.md` certo, sem 404; nenhuma entrada
duplicada; entradas que não são de módulo intactas.

## Regras

- Não invente entrada pra módulo sem `README.md`. Entrada = doc que existe.
- Não mexa em seções do hub que não são de módulo (guias, processos, ADRs) além
  do necessário; o escopo aqui é a doc por módulo.
- Uma entrada por módulo. Módulo com vários `.md` mostra só o `README.md` (que já
  indexa os demais internamente).
