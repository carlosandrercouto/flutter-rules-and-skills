# Manter os índices (hubs de navegação HTML e catálogo de IA)

O hub é a porta de entrada das docs humanas, enquanto o diretório `ia-conhecimento/` concentra os arquivos técnicos para consulta rápida de IA. A `assimilar-conhecimento-documentacao` mantém ambos sincronizados.

## Estrutura de diretórios em `<docsRoot>`

```text
<docsRoot>/
├── index.html                                # Hub principal da documentação
├── .docstate.json                            # Estado e baseline (SHA por módulo/slug)
├── doc-modulos/
│   ├── index.html                            # Visão geral com um card por domínio/módulo
│   └── <dominio>/
│       ├── index.html                        # Overview do domínio (lista módulos principais)
│       └── <modulo>.html                     # Página humana do módulo (com âncoras # para submódulos/fluxos)
└── ia-conhecimento/
    ├── README.md                             # Índice técnico opcional para consulta rápida da IA
    ├── <dominio>-domain-catalog.md           # Catálogo consolidado do domínio (em varreduras completas)
    └── <slug>.md                             # Documento técnico denso por módulo/feature/descoberta
```

> Em projetos menores sem divisão por domínio, `<docsRoot>/doc-modulos/<modulo>.html` pode ficar direto abaixo de `doc-modulos/`.

## Formato do hub HTML (`<docsRoot>/doc-modulos/index.html`)

Se o projeto já tiver um estilo visual próprio nos arquivos `.html`, preserve-o. Se for criar do zero, use um layout limpo, responsivo e de alto contraste:

```html
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Documentação — <Nome do Projeto></title>
  <style>
    :root { color-scheme: light dark; }
    body { font-family: system-ui, -apple-system, sans-serif; max-width: 980px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }
    .breadcrumb { font-size: 0.9rem; margin-bottom: 1rem; opacity: 0.8; }
    .grp { font-size: 1.2rem; font-weight: 600; margin: 2rem 0 1rem; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
    .card { display: block; padding: 1rem; border: 1px solid rgba(128,128,128,0.3); border-radius: 8px;
            text-decoration: none; color: inherit; transition: transform 0.15s, box-shadow 0.15s; }
    .card:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
    .ct { font-weight: 600; margin-bottom: 0.4rem; }
    .cd { font-size: 0.92rem; opacity: 0.85; margin-bottom: 0.6rem; }
    .cp { font-size: 0.8rem; opacity: 0.65; font-family: monospace; }
  </style>
</head>
<body>
  <div class="breadcrumb"><a href="../index.html">Início</a> / Domínios e Módulos</div>
  <h1><Nome do Projeto> — Documentação por Domínio/Módulo</h1>

  <div class="grp">Domínios / Módulos</div>
  <div class="grid">
    <!-- cards de domínio ou módulo aqui -->
  </div>
</body>
</html>
```

Formato do card:

```html
<a class="card" href="<dominio>/index.html">
  <div class="ct"><Título do Domínio ou Módulo></div>
  <div class="cd"><Uma ou duas frases explicando o que existe, como funciona e por que importa></div>
  <span class="cp"><dominio>/</span>
</a>
```

## Hierarquia e âncoras nas páginas de módulo (`<modulo>.html`)

Cada página `<modulo>.html` deve permitir leitura rápida e navegação direta:

- **Resumo humano** do módulo ("o que existe, como funciona, por que importa");
- **Índice interno** com links para âncoras (`#arquitetura`, `#fluxos`, `#contratos`, `#submodulos`);
- **Submódulos e fluxos** documentados como seções ancoradas dentro da página do módulo (evite criar páginas HTML quase vazias para submódulos pequenos);
- **Tabelas de contrato** (endpoints, parâmetros de entrada, response/mapper, rotas/deeplinks) quando existirem no módulo;
- **Referência cruzada** para o arquivo técnico correspondente em `ia-conhecimento/<slug>.md`.

## Índice técnico de IA (`<docsRoot>/ia-conhecimento/README.md`)

Mantenha um índice simples em Markdown para facilitar a descoberta por agentes de IA:

```markdown
# Índice de Conhecimento Técnico (IA)

| Domínio / Módulo | Arquivo `.md` | Doc Humana (HTML) | Resumo Técnico |
|------------------|---------------|-------------------|----------------|
| `<dominio>/<modulo>` | [`<slug>.md`](<slug>.md) | [`../doc-modulos/<dominio>/<modulo>.html`](../doc-modulos/<dominio>/<modulo>.html) | Contratos, arquitetura, fluxos e evidências |
```

## Procedimento de sincronização

1. **Verifique os documentos existentes** em `<docsRoot>/doc-modulos/` e `<docsRoot>/ia-conhecimento/`.
2. **Para cada módulo/domínio documentado**:
   - **Entrada ausente no hub** -> adicione o card apontando para a página correta.
   - **Entrada presente** -> atualize o resumo se o escopo mudou.
   - **Submódulos novos** -> adicione a âncora correspondente na página do módulo principal e no índice do topo da página.
3. **Módulo removido/renomeado** -> remova links quebrados do hub e marque ou migre o registro em `ia-conhecimento/`.
4. **Ordene as entradas** de forma estável (alfabética por domínio/módulo) para manter diffs limpos.

## Validar

Sirva localmente ou verifique a resolução dos caminhos relativos:

```bash
python3 -m http.server -d <docsRoot> 8756   # abre http://localhost:8756/index.html
```

Cheque:
- todos os links entre `index.html`, `doc-modulos/<dominio>/index.html`, `<modulo>.html` e âncoras `#` funcionam sem 404;
- todo módulo documentado possui tanto a visão humana (`.html`) quanto a ficha técnica de IA (`.md`).
