# Pare e pergunte - gatilhos

Situações em que NÃO se decide/age sozinho: pare e confirme com o usuário primeiro.
Quando em dúvida se algo está nesta lista, trate como se estivesse.

## Git / versionamento

- **Commit ou push:** só com pedido explícito ("pode commitar"). Siga as convenções
  de commit do projeto (conventional commits, commitizen, etc.), se houver.
- **Nunca sem pedido:** `--no-verify` (pular hooks), `--force`/force-push, `--amend`
  de commit já existente, reescrever histórico (rebase, `reset` que move commits).
- **Trocar/criar/apagar branch, apagar stash, descartar working tree** (`git checkout
  -- <arquivo>`, `git reset --hard`, `git clean`): confirme, pode destruir trabalho.

## Destrutivo / difícil de reverter

- Deletar ou sobrescrever arquivo/pasta que **você não criou nesta sessão**. Antes,
  **olhe o alvo**: se o conteúdo contradiz como foi descrito, avise em vez de prosseguir.
- Rodar migração, seed, script que muda banco/estado externo.
- Mexer em credenciais, segredos, tokens, `.env`, config de release/assinatura, CI/CD,
  keystores, provisioning profiles.
- Qualquer ação com efeito externo (enviar, publicar, deploy, chamar API que escreve).
- Alterar `pubspec.yaml` (adicionar/remover/atualizar dependências) sem discutir.
- Alterar configurações nativas (`android/`, `ios/`, `macos/`, `web/`, `linux/`,
  `windows/`) — podem quebrar builds ou assinaturas.

## Ambiguidade / decisão

- Requisito pouco claro, ou mais de uma interpretação plausível do pedido.
- **Mais de um caminho razoável** com trade-off (arquitetura, lib, abordagem):
  apresente as opções via `AskUserQuestion`, não escolha por conta.
- Precisaria "assumir" algo importante (branch, arquivo-alvo, comportamento esperado,
  contrato de API) que não foi confirmado nem está claro no código.

## Escopo

- Ampliar o trabalho além do plano aprovado.
- "Aproveitar pra arrumar" algo fora do contexto atual (dead code, lint, refactor não
  pedido): anote e ofereça, não faça junto sem pedir.
- Mudança que afeta muitos arquivos/módulos além do previsto.

## Convenções do projeto

- Antes de introduzir um gerenciamento de estado diferente do usado no projeto, pare
  e pergunte. Ex.: projeto usa BLoC e você ia criar com Provider, ou vice-versa.
- Antes de criar estrutura de pastas diferente do padrão existente no projeto, confirme.
- Antes de adicionar um pacote/plugin que o projeto não usa, discuta alternativas.
- Se o projeto tem arquivo de convenções (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`,
  guia de estilo), siga-o. Não contradiga sem perguntar.

## Como perguntar bem

- Seja específico e ofereça opções quando fizer sentido (`AskUserQuestion`).
- Diga o que você faria por padrão (recomendação) e por quê, para o usuário só
  confirmar ou corrigir.
- Uma pergunta boa agora evita retrabalho depois.
