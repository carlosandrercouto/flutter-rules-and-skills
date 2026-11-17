---
name: registrar-nova-skill
description: >-
  Registra uma skill PESSOAL (nova, ou já criada no lugar errado) no esquema
  correto: arquivos de verdade em ~/Development/claude/skills/<nome>/ e um
  symlink em ~/.claude/skills/<nome> apontando pra lá (o Claude Code só
  descobre skills olhando ~/.claude/skills/). Use SEMPRE que eu disser
  "registra a nova skill", "registra essa skill nas minhas skills", "registra
  a skill <nome>", "põe essa skill no lugar certo", ou pedir pra registrar
  uma skill pessoal que acabou de ser criada/discutida na conversa, sem dizer
  o nome explicitamente (nesse caso, identifique pelo contexto qual skill foi
  criada/editada por último). NÃO é para skill de PROJETO (.claude/skills/
  dentro de um repo específico): essa é só para as PESSOAIS.
---

# Registrar skill pessoal (symlink pro workspace)

Toda skill pessoal minha mora fisicamente em
`~/Development/claude/skills/<nome>/`, nunca direto em `~/.claude/skills/`.
O Claude Code só descobre skills olhando `~/.claude/skills/`, então cada
skill de lá precisa ser um symlink apontando pro workspace (não existe
suporte documentado pra symlinkar o diretório `~/.claude/skills/` inteiro de
uma vez, só entrada por entrada). Essa skill garante que qualquer skill
pessoal, nova ou já existente, siga esse esquema.

## Como identificar QUAL skill registrar

- Se eu disser o nome ("registra a skill revisar-pr"), use esse nome.
- Se eu disser "registra a nova skill" / "registra essa skill" sem nome,
  identifique pelo contexto da conversa: qual skill foi criada ou editada por
  último nesta sessão (arquivo escrito, ou skill que acabamos de discutir no
  turno anterior). Se não der pra ter certeza de qual é, **pergunte o nome
  antes de mexer em qualquer arquivo.**

## Procedimento

1. **Reancore.** Confira o estado atual dos dois lados antes de decidir o
   que fazer, nunca assuma:
   ```bash
   ls -la ~/.claude/skills/<nome> 2>&1
   ls -la ~/Development/claude/skills/<nome> 2>&1
   ```

2. **Decida pelo estado encontrado** (só um destes se aplica por vez):

   - **Não existe em nenhum lugar ainda** (skill nova, só descrita/redigida
     na conversa, nenhum arquivo salvo): crie o `SKILL.md` (e eventuais
     arquivos auxiliares) direto em `~/Development/claude/skills/<nome>/`,
     depois vá pro passo 3.
   - **Já existe em `~/Development/claude/skills/<nome>/`, mas falta o
     symlink em `~/.claude/skills/`:** só falta o passo 3.
   - **Existe como diretório REAL dentro de `~/.claude/skills/<nome>/`**
     (skill criada no lugar errado, por hábito antigo ou engano): mova pro
     workspace e só então symlink:
     ```bash
     mv ~/.claude/skills/<nome> ~/Development/claude/skills/<nome>
     ```
   - **Já é um symlink em `~/.claude/skills/<nome>` apontando pro lugar
     certo:** nada a fazer, só confirme e avise que já estava registrada.
   - **É um symlink apontando pra outro lugar, ou já existe conteúdo
     DIFERENTE nos dois lados com o mesmo nome:** pare e pergunte antes de
     sobrescrever qualquer coisa. Nunca resolva colisão de nome sozinho.

3. **Crie o symlink** (só quando `~/.claude/skills/<nome>` ainda não existir
   de forma nenhuma, nem real nem link):
   ```bash
   ln -s ~/Development/claude/skills/<nome> ~/.claude/skills/<nome>
   ```

4. **Verifique.** Confirme que o link resolve e o conteúdo é legível através
   dele:
   ```bash
   ls -la ~/.claude/skills/<nome>
   wc -l ~/.claude/skills/<nome>/SKILL.md
   ```

5. **Feche o loop.** Diga em uma linha o que foi feito (criada do zero /
   movida e symlinkada / já estava correta) e o caminho final dos dois
   lados.

## Regras duras

- **Nunca sobrescreva silenciosamente** um `~/.claude/skills/<nome>` ou
  `~/Development/claude/skills/<nome>` que já tenha conteúdo diferente do
  esperado. Pare e pergunte.
- **Nunca dê `rm -rf`** sem antes confirmar que o conteúdo já foi preservado
  no destino (depois de um `mv`, a origem já não existe mais sozinha; não é
  preciso remover nada à parte).
- Isso é só para **skills PESSOAIS** (`~/.claude/skills/`). Skill de
  **PROJETO** (`.claude/skills/` dentro de um repo) não usa esse esquema,
  fica no próprio repo mesmo, sem symlink.
- Depois de registrada, a skill já fica disponível na sessão atual e nas
  próximas (o Claude Code recarrega `~/.claude/skills/` automaticamente,
  inclusive seguindo o symlink).
