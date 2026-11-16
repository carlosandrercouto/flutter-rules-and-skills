---
name: assimilar-conhecimento-documentacao
description: >-
  Le um projeto, modulo ou feature especificada (ou assimila descobertas tecnicas
  no contexto do chat) e sincroniza documentacao em dois formatos: HTML em
  linguagem humana para consultas rapidas (navegavel) e Markdown tecnico (.md)
  para a IA consultar. Pode rodar em modo pontual (uma descoberta, modulo ou
  feature especifica), incremental por historico do git (baseline), ou varredura
  completa do projeto. Use quando pedirem: "documenta o modulo X", "documenta
  essa feature", "assimile o conhecimento", "atualize a documentacao", "registre
  essa descoberta tecnica", "sincronize docs", "consolide a doc", "gera a
  documentacao completa". Mantem baseline para evitar retrabalho e preserva a
  hierarquia de navegacao por dominio, modulo e submodulo.
argument-hint: "Descreva o projeto, modulo/feature ou descoberta tecnica e o escopo (pontual, incremental ou completo)"
user-invocable: true
---

# Assimilar conhecimento e documentação

## Objetivo

Ler um projeto, módulo ou feature especificada (ou capturar descobertas técnicas da conversa) e transformar esse entendimento em documentação persistente e consultável em **dois canais complementares**:

- **HTML em linguagem humana** para leitura e consulta rápida de devs e stakeholders.
- **Markdown técnico (`.md`) para IA** com dados técnicos densos e estrutura canônica para busca, RAG e consultas futuras de agentes.

> Vale o `trabalho-seguro`. Esta skill atua apenas sobre arquivos de documentação: não altera código de produção (`lib/`) e nunca faz commit sem permissão explícita.

## Quando usar

Use esta skill quando houver qualquer um destes pedidos:

- "documenta o módulo X" / "documenta essa feature"
- "assimile o conhecimento"
- "registre essa descoberta técnica"
- "atualize a documentação"
- "sincronize docs com o código"
- "consolide a documentação"
- "gera a documentação completa"

## Modos de execução

### 1) Modo pontual / Escopo direcionado (padrão)

Quando o usuário aponta um módulo/feature específico para documentar ou quando uma descoberta técnica nasce durante a conversa:

- leitura e mapeamento de um módulo ou feature específica do projeto;
- novo contrato de API confirmado;
- regra de negócio descoberta;
- comportamento de erro/retry identificado;
- decisão de arquitetura/restrição técnica validada;
- padrão de teste/observabilidade comprovado.

**Resultado:** cria ou atualiza apenas os artefatos (HTML + `.md`) dos módulos/features afetados, sem varrer o repositório inteiro.

### 2) Modo incremental por baseline

Quando houver mudanças recentes no projeto e o pedido for "atualizar docs" ou "sincronizar docs com o código":

- usa a baseline registrada em `<docsRoot>/.docstate.json` (ver `references/baseline-git.md`);
- processa somente o intervalo `BASE..HEAD`;
- atualiza somente módulo/feature com commit novo desde a última passada.

### 3) Modo varredura completa

Quando o pedido for consolidação geral do projeto:

- descobre a estrutura de módulos/features do projeto (`lib/features/`, `lib/app/modules/`, `lib/modules/`, `lib/src/`, packages, etc.);
- revisa todos os módulos/áreas relevantes;
- reconcilia índice central, gaps antigos e `.docstate.json`;
- uso mais pesado, indicado no onboarding de um projeto existente ou antes de marcos/releases.

## Formatos obrigatórios de saída

Defina `<docsRoot>` conforme a convenção do projeto ou preferência do usuário:
- Se o projeto já possuir pasta de documentação (ex.: `docs/`) ou o usuário informar um caminho externo (ex.: `~/Development/docs/<projeto>`), use esse diretório como `<docsRoot>`.
- Caso ainda não exista uma pasta `docs/` no repositório e nenhum destino tenha sido informado, pergunte ao usuário onde deseja salvar antes de criar diretórios novos no repositório.

### A) HTML em linguagem humana (consulta rápida)

Destino padrão:

- `<docsRoot>/index.html` para o hub principal da documentação;
- `<docsRoot>/doc-modulos/index.html` para a visão geral de domínios/módulos;
- `<docsRoot>/doc-modulos/<dominio>/index.html` para o overview do domínio (ou direto `<docsRoot>/doc-modulos/<modulo>.html` em projetos sem divisão por domínio);
- `<docsRoot>/doc-modulos/<dominio>/<modulo>.html` para cada módulo principal;
- âncoras (`#`) dentro da página do módulo para submódulos, endpoints e fluxos;
- página separada de submódulo somente quando houver audiência, ciclo de vida ou contrato independente que justifique a separação.

Requisitos:

- leitura fluida, contextual e objetiva em linguagem humana;
- foco em **"o que existe, como funciona, por que importa"**;
- hierarquia explícita: `domínio > módulo > submódulo` (ou `módulo > feature` em projetos menores);
- navegação direta entre overview do domínio, páginas de módulo e âncoras de submódulo;
- uma entrada no hub por domínio/módulo principal, nunca uma landing page vazia por submódulo;
- tabelas de contrato para endpoints, entrada esperada, resposta/mapper e rota de acesso quando a evidência existir no código;
- navegação por links relativos, layout responsivo e contraste legível;
- sem segredo, token, senha, chave ou endpoint sensível.

### B) Markdown técnico para IA (consulta de agentes)

Destino padrão:

- `<docsRoot>/ia-conhecimento/<slug>.md` para módulos, features ou descobertas específicas;
- para varredura completa de um domínio ou projeto, preferir `<docsRoot>/ia-conhecimento/<dominio>-domain-catalog.md` (ou `<projeto>-catalog.md`);
- manter documentos focados por feature/módulo quando houver escopo independente, relacionando-os ao catálogo.

Estrutura mínima do arquivo:

```md
# <titulo tecnico>

## Metadados
- dominio:
- modulo:
- package:
- feature:
- fonte:
- commit_range:
- atualizado_em:

## Resumo executivo

## Arquitetura e Estrutura
- gerenciamento de estado e padroes aplicados
- mapa de arquivos, classes e simbolos principais
- dependencias internas e externas

## Evidencias
- arquivos e simbolos relevantes
- comandos e saidas resumidas
- decisoes validadas

## Contratos tecnicos
- APIs / endpoints / payloads / mappers
- rotas / deeplinks / argumentos
- eventos / analytics / logs
- erros, fallbacks e tratamentos

## Fluxos e Regras de Negocio

## Impacto, limites e dividas tecnicas

## Relacoes
- docs humanas relacionadas (caminho relativo para o .html)
- conhecimentos dependentes (outros .md em ia-conhecimento/)
```

Regra: o Markdown deve ser técnico, denso, objetivo e orientado a consulta automática por IA.

## Fluxo obrigatório

### 1. Mapear escopo ou capturar descoberta

Consolidar os fatos técnicos com escopo claro:

- qual projeto, domínio, módulo, package ou feature está sendo documentado;
- o que existe ou foi descoberto no código;
- onde foi validado (arquivos, classes, símbolos, diff, testes, comandos).

### 2. Classificar o conteúdo técnico

Identificar as dimensões presentes no módulo/descoberta:

- arquitetura e estado
- contrato de API / integração de dados
- navegação / rotas / deeplinks
- regra de negócio
- observabilidade / analytics
- testes / cobertura
- operação / processo

### 3. Atualizar HTML humano

Criar ou atualizar o documento HTML do módulo/tema em `<docsRoot>/doc-modulos/`, refletindo o funcionamento de forma clara e visual sem reescrever seções estáveis desnecessariamente.

### 4. Atualizar Markdown técnico de IA

Criar ou atualizar o arquivo correspondente em `<docsRoot>/ia-conhecimento/` com metadados, arquitetura, evidências, contratos e limites.

### 5. Sincronizar índices (`references/indice-hub.md`)

- manter `<docsRoot>/index.html` com navegação canônica;
- manter `<docsRoot>/doc-modulos/index.html` com uma entrada por domínio/módulo;
- manter `<docsRoot>/doc-modulos/<dominio>/index.html` (quando houver domínios) com uma entrada por módulo principal;
- manter âncoras de submódulos, endpoints, rotas e status coerentes nas páginas de módulo;
- opcional recomendado: índice técnico em `<docsRoot>/ia-conhecimento/README.md` listando os conhecimentos por domínio/módulo.

### 6. Atualizar estado (`references/baseline-git.md`)

Registrar baseline e trilha de assimilação em `<docsRoot>/.docstate.json`:

- `baseline` geral (SHA do `HEAD` quando aplicável);
- último SHA por módulo processado;
- último update por conhecimento técnico (`slug -> sha/data`).

## Regras duras

- **Dois formatos sempre**: HTML humano (`doc-modulos/`) + Markdown técnico para IA (`ia-conhecimento/`).
- **Sem retrabalho desnecessário**: no modo incremental, respeitar estritamente `BASE..HEAD`.
- **Sem inventar**: toda afirmação técnica precisa de evidência verificável no código, testes ou histórico do git.
- **Sem landing pages vazias**: prefira uma seção ancorada na página do módulo e promova um submódulo a página própria somente quando o escopo justificar.
- **Sem tocar código de produção**: esta skill nunca altera `lib/` ou arquivos de build.
- **Sem segredos**: nunca registrar credenciais, tokens, chaves ou dados sensíveis.
- **Sem commit sem permissão**: seguir `trabalho-seguro`.

## Qualidade mínima

Antes de concluir, validar:

- links relativos funcionando entre o hub, páginas HTML e referências cruzadas;
- HTML legível em desktop e mobile;
- cada domínio abre seu overview e cada módulo abre sua página direta;
- cada módulo documentado possui links ou âncoras para seus submódulos/fluxos;
- Markdown técnico com metadados completos e caminhos reais do código;
- consistência entre a narrativa humana (HTML) e os contratos técnicos (`.md`);
- resumo final entregue ao usuário com:
  - módulo/feature ou conhecimento assimilado;
  - arquivos HTML e Markdown criados/atualizados;
  - baseline usada/gravada (se aplicável);
  - pendências explícitas.

## Compatibilidade e aliases

- Esta skill substitui e evolui a antiga `gerar-documentacao`.
- Se o pedido vier como "gerar documentação", "documentar módulo" ou "atualizar doc", execute no modo pontual, incremental ou completo conforme o contexto solicitado.

## Referências

- `references/baseline-git.md`: como funciona o `.docstate.json`, descoberta da estrutura de módulos, cálculo do diff `BASE..HEAD` e gravação da baseline.
- `references/indice-hub.md`: estrutura e sincronização dos hubs HTML (`index.html`, `doc-modulos/`) e índice de `ia-conhecimento/`.
