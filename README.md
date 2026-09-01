# Flutter Rules and Skills

Coleção de skills genéricas para projetos Flutter, prontas para uso com assistentes de IA (Claude, Gemini, etc.). Cada skill é um protocolo completo e autocontido que padroniza um fluxo de trabalho, garantindo consistência e qualidade independente do projeto.

> **100% genéricas.** Nenhuma skill referencia projeto, ferramenta de gestão ou arquitetura específica. Funcionam com qualquer stack Flutter (BLoC, Riverpod, Provider, GetX, MobX, etc.) e qualquer ferramenta (Jira, Monday, ClickUp, GitHub, GitLab, Bitbucket).

## Skills

### 🛡️ [trabalho-seguro](trabalho-seguro/SKILL.md)

Protocolo de segurança para qualquer alteração no código. Garante que o assistente nunca quebre o que funciona.

- Checklist de kickoff (branch, estado do repo, contexto do projeto)
- Gates de segurança: `flutter analyze` limpo + `flutter test` verde antes de reportar "pronto"
- Stop-and-ask: lista de ações que **nunca** devem ser feitas sem permissão explícita (push, merge, delete branch, alterar .env)
- Auto-detecção de arquitetura e dependências do projeto

**Quando ativa:** toda tarefa que envolva alterar código. É a base de todas as outras skills.

| Arquivo | Descrição |
|---------|-----------|
| `SKILL.md` | Protocolo principal |
| `references/kickoff-checklist.md` | Checklist completo de início de tarefa |
| `references/stop-and-ask.md` | Lista de ações bloqueadas sem permissão |

---

### 📝 [abrir-pr](abrir-pr/SKILL.md)

Monta o título + corpo da PR já preenchidos a partir do contexto do trabalho feito, prontos para colar no GitHub/GitLab/Bitbucket.

- Título em inglês (Conventional Commits: `type(scope): description`)
- Corpo em português humano, tom simples
- Auto-detecção de template de PR (`.github/PULL_REQUEST_TEMPLATE.md` ou equivalente)
- Modelo padrão embutido caso o projeto não tenha template
- Suporte a `gh pr create` (GitHub) e `glab mr create` (GitLab)
- Sem travessão, sem emoji

**Quando ativa:** "monta a PR", "prepara a PR", "gera o texto da PR", "descrição da PR".

---

### 🔍 [revisar-pr](revisar-pr/SKILL.md)

Code review de PR com foco em **bugs de verdade**, não lista exaustiva de estilo. A maior e mais detalhada skill da coleção (410 linhas).

- **Dois modos:** PR (review de outro dev via `gh`/`glab`) e Local (self-review antes de abrir PR)
- **Duas entregas:** levantamento técnico detalhado + mensagem pronta para colar no MR
- Triagem inteligente: prioriza controller/use cases → data sources → DI/rotas → widgets
- Checklist P1 completo: Result/Either mal usado, HTTP que não lança, async+UI sem `mounted`, ciclo de vida, DI/rotas, parsing defensivo
- Reconhecimento genuíno de decisões bem tomadas (mesmo rigor que achado de bug)
- Achados de contexto: conflitos com frentes paralelas, tokens duplicados, compliance de loja

**Quando ativa:** "revisa a PR #123", "faz o code review", "revisa minha branch local".

---

### 💬 [comentarios-task-commits](comentarios-task-commits/SKILL.md)

Dois registros que nunca se misturam: comentário de task (humano) e mensagem de commit (técnica).

**Comentário de task** (Jira, Monday, ClickUp, Trello, Linear, Asana):
- Português, leve, sem jargão técnico
- Primeira pessoa do singular ("Ajustei", "Validei", "Corrigi")
- Formato: **título em negrito** + descrição em blockquote
- Adaptação por ferramenta (ex.: Jira usa `{quote}`, Asana usa rich text)

**Mensagem de commit:**
- Inglês, Conventional Commits
- Corpo técnico detalhado com seção Evidence
- Sem travessão, sem emoji

**Quando ativa:** "escreve pro jira/monday", "comentário da tarefa", "pode commitar", "faz o commit".

---

### 🏷️ [criar-commit-cz](criar-commit-cz/SKILL.md)

Gera o texto de commit no formato específico do Commitizen (`cz`): tipo, título e descrição longa **em três saídas separadas**, prontas para colar nos prompts do `cz`.

- Tipo em linha separada (para selecionar com setas no terminal)
- Título com escopo composto (`área > alvo`)
- Descrição longa em português, com verbos no imperativo
- Quebra de linha vira `|` (o campo do `cz` trata Enter como envio)

**Quando ativa:** **somente** quando o usuário menciona commitizen/cz explicitamente. Pedidos genéricos de commit usam a skill `comentarios-task-commits`.

---

### 🧪 [escrever-testes](escrever-testes/SKILL.md)

Sistema completo de testes para Flutter: scaffold automático, moldes prontos, relatório de cobertura interativo.

- **7 moldes** (M1 a M7): use case, repository, fromJson, controller/cubit, widget smoke, integração, clock injetável
- **Script `scaffold_tests.py`**: escaneia o módulo e gera os esqueletos de teste com imports reais e TODOs
- **Script `coverage_report.py`**: relatório interativo em HTML com barras empilhadas por arquivo, busca, filtros e cartão PNG por módulo
- Regras duras: mock só de interface (mocktail), nunca API real no run padrão, sempre Success E Failure
- Auto-detecção de arquitetura (`lib/features/`, `lib/app/modules/`, `lib/src/`, etc.)

**Quando ativa:** "escreve os testes", "testa o use case", "cobre com testes", "aumenta a cobertura".

| Arquivo | Descrição |
|---------|-----------|
| `SKILL.md` | Protocolo principal |
| `references/moldes.md` | Moldes M1 a M7 com código completo |
| `references/mocktail.md` | Guia de mocktail: API, regras e armadilhas |
| `references/checklist-dod.md` | Definition of Done por PR |
| `references/cobertura.md` | Como gerar, exibir e ler cobertura com honestidade |
| `scripts/scaffold_tests.py` | Gerador de esqueletos de teste |
| `scripts/coverage_report.py` | Relatório de cobertura interativo (terminal + HTML) |

---

### 📚 [gerar-documentacao](gerar-documentacao/SKILL.md)

Gera documentação técnica de módulos/features Flutter com sistema de baseline incremental via git.

- Baseline por SHA: só regenera o que mudou desde o último snapshot
- Hub de navegação (HTML ou Markdown) com índice de todos os módulos documentados
- Auto-detecção da estrutura de módulos do projeto
- Estado persistido em `docs/.docstate.json`

**Quando ativa:** "documenta o módulo X", "gera a documentação", "atualiza a doc".

| Arquivo | Descrição |
|---------|-----------|
| `SKILL.md` | Protocolo principal |
| `references/baseline-git.md` | Como funciona o sistema de baseline incremental |
| `references/indice-hub.md` | Template e lógica do hub de navegação |

---

### 📋 [registrar-nova-skill](registrar-nova-skill/SKILL.md)

Meta-skill: guia para criar novas skills seguindo o padrão desta coleção.

- Estrutura de pastas (`SKILL.md` + `references/` + `scripts/`)
- Frontmatter YAML obrigatório (name, description com gatilhos de ativação)
- Convenções de nomenclatura e organização

**Quando ativa:** "cria uma nova skill", "registra essa skill".

---

## Estrutura

```
flutter-rules-and-skills/
├── README.md
├── trabalho-seguro/
│   ├── SKILL.md
│   └── references/
│       ├── kickoff-checklist.md
│       └── stop-and-ask.md
├── abrir-pr/
│   └── SKILL.md
├── revisar-pr/
│   └── SKILL.md
├── comentarios-task-commits/
│   └── SKILL.md
├── criar-commit-cz/
│   └── SKILL.md
├── escrever-testes/
│   ├── SKILL.md
│   ├── references/
│   │   ├── moldes.md
│   │   ├── mocktail.md
│   │   ├── checklist-dod.md
│   │   └── cobertura.md
│   └── scripts/
│       ├── scaffold_tests.py
│       └── coverage_report.py
├── gerar-documentacao/
│   ├── SKILL.md
│   └── references/
│       ├── baseline-git.md
│       └── indice-hub.md
└── registrar-nova-skill/
    └── SKILL.md
```

## Como usar

### Com Claude (Anthropic) / Gemini (Google)

Copie as skills desejadas para a pasta `.claude/skills/` ou `.gemini/skills/` (dependendo do assistente) do seu projeto Flutter:

```bash
cp -r trabalho-seguro /caminho/do/projeto/.claude/skills/
cp -r escrever-testes /caminho/do/projeto/.claude/skills/
# ... etc
```

O assistente detecta automaticamente as skills pelo frontmatter YAML do `SKILL.md` e as ativa quando o pedido do usuário casa com os gatilhos da `description`.

### Com outros assistentes

Cada `SKILL.md` é um documento markdown autocontido. Você pode:

1. **Colar como contexto** no início da conversa
2. **Referenciar como arquivo** se o assistente suporta leitura de arquivos
3. **Adaptar o frontmatter** para o formato de skills do seu assistente

### Skills pessoais vs. projeto

- **No projeto**: todos os devs do time usam (salvo no repositório)
- **Pessoal**: só você usa, em qualquer projeto (ex: na sua pasta pessoal de configurações do assistente)

## Dependências

As skills funcionam com qualquer projeto Flutter. As únicas dependências externas são:

| Dependência | Onde é usada | Obrigatória? |
|-------------|-------------|--------------|
| `mocktail` (Dart) | `escrever-testes` | Sim, para testes |
| `Python 3` | Scripts de scaffold e cobertura | Só se usar os scripts |
| `PyYAML` | `scaffold_tests.py` (lê pubspec.yaml) | Só se usar o scaffold |
| `gh` CLI | `abrir-pr`, `revisar-pr` (modo PR) | Só para GitHub |
| `glab` CLI | `abrir-pr`, `revisar-pr` (modo PR) | Só para GitLab |
| Chrome/Edge | `coverage_report.py --png` | Só se quiser PNG |

## Licença

Uso pessoal e de time. Adapte livremente para seu projeto.
