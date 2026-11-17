---
name: revisar-pr
description: >-
  Faz o code review de uma PR/MR de projeto Flutter com foco em BUGS, e
  devolve duas coisas: o levantamento tecnico dos problemas pra mim e a
  mensagem pronta pra colar no MR, em portugues humano, com sugestao de
  correcao em cada ponto. Use SEMPRE que eu pedir pra revisar uma PR/MR, por
  exemplo: "revisa a PR #123", "faz o code review da branch X", "CR dessa MR",
  "da uma olhada na PR do fulano", "revisa esse diff pra mim". Tambem tem o
  MODO LOCAL, pra revisar a MINHA propria task antes de abrir a PR ("revisa
  minha task", "self review do que eu fiz", "revisa minha branch local"):
  nesse caso o diff vem do git local e eu colo SO a descricao da task. No
  modo PR eu sempre colo a descricao que o dev deixou na PR E a task: use como
  criterio de aceite (o diff entrega o que a task pede?); se faltar entrada,
  peca antes de comecar. Acessa a PR via gh/glab CLI (diff direto ou checkout
  quando precisar de contexto). As PRs costumam ser enormes (codigo gerado com
  IA): priorize, nao comente tudo. NUNCA publica review/comentario na PR nem
  aprova/reprova por conta propria, a entrega e o texto pra eu colar. Nao
  confunda com abrir-pr (que escreve a descricao de abertura da PR).
---

# Code review de PR com foco em bugs (Flutter)

Eu sou dev e reviso PRs grandes, muitas vezes escritas com ajuda de IA. O
objetivo desta skill é me ajudar a achar **bugs de verdade** e entregar um
retorno enxuto e humano pro autor, não uma lista exaustiva de estilo. Sugestões
de melhoria entram, mas em segundo plano e em pequena quantidade.
Reconhecimento genuíno de decisão bem tomada também entra, com o MESMO rigor de
um achado de bug (ver "Reconhecimento genuíno" no Passo 3): não é elogio de
abertura nem tática de suavizar crítica, é um ponto técnico à parte, específico
e verificado.

## Perfil de quem lê (calibrar as explicações)

Sou dev experiente em Flutter/Dart. No levantamento:

- **NÃO explique Flutter/Dart básico** (o que é `ValueNotifier`, `PageView`,
  `async`/`await`, `mounted`). Isso eu domino, é ruído.
- **EXPLIQUE o que é específico DO PROJETO** conforme aparece no achado, em
  uma linha: o vocabulário do domínio, as convenções de arquitetura do repo,
  a mecânica interna da tela em questão. Assuma que eu posso não conhecer cada
  detalhe do projeto a fundo.
- Para cada bug, antes do "por que quebra", situe rápido **o papel daquele
  arquivo/símbolo no fluxo** (quem chama, quando roda, quem depende).
- Continua valendo o resto: enxuto, foco em bug, `arquivo:linha`, cenário
  concreto de falha, separar certeza de dúvida.

## Dois modos de uso

- **Modo PR (review de outro dev):** a PR já existe no GitHub/GitLab, eu passo
  o número/branch e colo a descrição da PR + a descrição da task. O diff vem do
  `gh`/`glab`. Entrega: levantamento + mensagem pro MR.
- **Modo local (self review da minha task):** ainda não abri a PR, o código é
  meu e está na branch local. Eu colo **só a task** (não existe descrição de PR
  ainda, não peça por ela). O diff vem do git local. Entrega: **só o
  levantamento técnico**, pra eu corrigir antes de abrir a PR; a mensagem de MR
  não faz sentido aqui (se eu quiser a descrição de abertura, isso é a skill
  `abrir-pr`).

Identifique o modo pelo pedido: se eu falar da minha task/branch/"o que eu
fiz", é local; se eu apontar uma PR ou o trabalho de outro dev, é PR. Na
dúvida, pergunte.

## Entregas (no modo PR, as duas nesta ordem; no modo local, só a primeira)

1. **Levantamento técnico pra mim:** cada achado com `arquivo:linha`, gravidade
   e explicação de por que é bug (qual entrada/estado quebra). Abra com o
   check de aceite: item a item da task, entregue ou não, e onde no código.
2. **Mensagem pronta pra colar no MR:** português, tom humano de colega de
   time, com sugestão de correção em cada ponto. Requisito da task que ficou
   de fora entra junto com os bugs no bloco que segura o merge. Regras de voz
   mais abaixo.

## Entradas que eu colo junto com o pedido

No **modo PR**, junto com o número/branch, eu sempre colo **duas descrições**:

1. **A descrição que o dev deixou na PR** (o que ele diz que fez e como validou).
2. **A descrição da task** (o que foi pedido de fato — Jira, Monday, ClickUp, etc.).

No **modo local**, só existe a segunda: eu colo a **task** e mais nada (não
peça descrição de PR, ela ainda não existe).

Elas são parte do review, não contexto decorativo:

- A task é o **critério de aceite**: monte a partir dela a lista do que a PR
  precisa entregar e confira item a item contra o diff. Requisito da task que
  não aparece no código é achado de P1 (segura o merge tanto quanto bug).
- A descrição do dev é a **hipótese a verificar**: se ele diz que tratou um
  caso ou validou um fluxo, procure isso no código. Divergência entre o que a
  descrição promete e o que o diff faz é achado.
- Código no diff que a task não pede (scope creep) merece menção: às vezes é
  ajuste legítimo de passagem, às vezes é risco escondido numa PR já enorme.

**Gate de partida:** se faltou entrada obrigatória do modo (modo PR: as duas
descrições; modo local: a task), **pare e me pergunte antes de rodar qualquer
comando do review**. Não comece pelo diff "enquanto espera" nem deduza a task
pelo título da PR ou da branch. Só siga sem ela se eu responder explicitamente
que não tem (ex: task sem descrição), e nesse caso registre no levantamento
que o aceite não foi conferido.

## Passo 1: pegar o diff

### Modo PR (gh/glab CLI)

```bash
# GitHub
gh pr view <num> --json title,body,headRefName,baseRefName,additions,deletions,files
gh pr diff <num>

# GitLab
glab mr view <num>
glab mr diff <num>
```

- Comece SEMPRE pelo view + diff: na maioria dos reviews isso basta e não mexe
  no meu working tree.
- Faça **checkout só quando precisar de contexto** que o diff não dá (ler o
  código ao redor, seguir uma chamada, rodar analyze/teste). Antes do checkout,
  rode `git status`: se eu tiver mudança local não commitada, me avise e
  pergunte antes de trocar de branch. Guarde o nome da branch atual pra voltar
  no final.

```bash
git status --porcelain            # se sujo, pergunta antes
git rev-parse --abbrev-ref HEAD   # guardar pra voltar depois
gh pr checkout <num>              # ou glab mr checkout <num>
# ... review ...
git checkout <branch-anterior>    # ao terminar, voltar
```

- Com checkout feito, vale rodar `flutter analyze` (deve ficar limpo) e, se a
  PR tiver testes, `flutter test` no escopo tocado.

### Modo local (git na minha branch)

O código já está aqui, sem checkout nem gh. O diff é o da minha branch contra
a base, **mais o que ainda não foi commitado** (é self review pré-PR, o
trabalho pode estar meio no working tree):

```bash
git rev-parse --abbrev-ref HEAD    # confirmar em que branch estou
git status --porcelain             # o que ainda não foi commitado
git diff <base>...HEAD             # o que já foi commitado desde a base
git diff HEAD                      # staged + unstaged por cima do HEAD
```

- **Base:** infira pelo fluxo do projeto (em geral `develop`, `main` ou
  `master`; confirme com `git merge-base`). Se não der pra ter certeza de onde
  a branch saiu, me pergunte em vez de chutar.
- Tudo que aparecer no diff entra no review, commitado ou não. Se houver
  arquivo untracked (`??`) que parece fazer parte da task, leia também.
- Aqui o contexto completo já está disponível: leia o código ao redor à
  vontade e rode `flutter analyze` e os testes do escopo direto.
- **Não commite, não faça stash, não toque no working tree.** O review é
  só leitura; corrigir os achados é passo meu, depois.

## Passo 2: triagem (as PRs são enormes, não leia linear)

1. Liste os arquivos e agrupe por módulo/feature (identifique a estrutura de
   pastas do projeto: `lib/features/`, `lib/app/modules/`, `lib/src/`, etc.).
2. Classifique cada grupo pelo papel: lógica de negócio, data layer,
   apresentação, config/DI, testes.
3. Ordem de leitura por risco:
   - controller/cubit/bloc e use cases (estado, fluxo de erro, lógica de negócio);
   - repositories/data sources e models/parsing (contrato com a API);
   - DI e rotas (fiação: erro aqui é crash em runtime);
   - widgets/pages por último, focando em estado e ciclo de vida, não em layout.
4. Pule sem culpa: arquivo gerado, mudança só de formatação, docs, assets,
   `pubspec.lock`. Diga que pulou e por quê no levantamento.
5. Se a PR for grande demais pra um contexto (dezenas de arquivos de lógica),
   revise por módulo em subagentes e consolide, mas a verificação final de
   cada bug apontado é sua.

## Passo 3: o que procurar (prioridade)

### P1, bugs (é o foco do review)

Checklist para projetos Flutter, além dos suspeitos universais (null safety,
índice fora do range, condição invertida, estado não resetado):

- **Result/Either mal usado:** acesso ao valor sem checar sucesso/falha,
  `fold`/`when` com branch de falha vazio ou que não desliga o loading.
- **HTTP não lança (quando o projeto usa validateStatus):** `try/catch`
  esperando exceção de status HTTP é código morto se o HTTP client aceita
  todos os status; a checagem tem que ser no status/Result.
- **Async + UI:** uso de `BuildContext` depois de `await` sem checar `mounted`;
  `setState`/notifier depois de dispose; `Future` relevante não aguardado;
  duas cargas concorrentes escrevendo no mesmo estado sem proteção.
- **Ciclo de vida:** notifiers/streams/controllers de scroll/animation
  criados no widget precisam de dispose. Se o projeto usa uma classe base
  que gerencia o dispose do controller principal, confirme o que ela cobre
  e o que não.
- **DI e rotas:** classe nova usada via DI mas não registrada; rota nova sem
  entrada no roteador; navegação pelo roteador errado.
- **Parsing:** `fromJson`/`fromMap` sem tolerância a campo nulo/ausente que a
  API pode mandar; cast direto de `dynamic` pra tipo errado.
- **Base URL duplicada:** se o base URL já inclui um prefixo (ex.: `/api`),
  rota montada com `'$baseUrl/api/...'` duplica e quebra em runtime.

### P1 também: código fora do padrão

Bug e desvio de padrão têm o mesmo peso. Bug quebra hoje; código fora do
padrão quebra na próxima mão que passar ali. Rode esta passada **arquivo por
arquivo do diff**, e cite o padrão do repo que deveria ter sido seguido (o
"certo" tem que ter endereço, senão soa gosto pessoal).

- **Copiou o vizinho errado.** Arquivo novo dentro de módulo que replica
  vícios de código antigo quando o padrão do repo já existe ao lado.
- **Campo/parâmetro novo com default silencioso.** `bool loaded = false`,
  `String? x` opcional num model que já tem irmão `required`: quem construir
  o model depois esquece e ninguém percebe.
- **Regra de negócio escrita à mão em N lugares.** Mesma condição repetida
  em vários pontos da view é divergência futura garantida. Peça o getter no
  model/controller, não no widget.
- **Fix pontual que deixa a armadilha armada.** A correção resolve o caso
  observado mas deixa o resto do código dependendo dela.
- **Assimetria com o irmão.** Widget/handler novo que não segue a convenção do
  par que já existe.
- **Onde dá teste barato e não tem.** Se a mudança caiu em função pura (parse,
  agregação, formatação), "o módulo não tem fiação de teste" não vale como
  desculpa.

### Reconhecimento genuíno (mesmo rigor que o achado de bug)

Nem todo review é só sobre o que está errado. Quando achar uma decisão
genuinamente bem tomada, sobretudo numa área onde esse tipo de feature costuma
quebrar, registre com o MESMO cuidado de um achado de bug: qual foi a decisão,
por que ela está certa (o mecanismo, não "está bom"), que categoria de falha
ela evita, e o que fica frágil nela pra frente.

Sinais de que vale esse tipo de registro:

- **Nomeie a categoria da feature** (fila paginada, parsing de payload
  agregado, onboarding guiado, cache, fluxo de pagamento) **e lembre os modos
  de falha típicos dela.** Depois de revisar, confira quais o código evitou.
- **Confira o vizinho do que está sendo elogiado.** Se o achado é o guard de
  `initState`, olhe o `dispose` também.
- **Teste que trava a tabela verdade da decisão merece registro à parte.**
- **Em lógica de decisão binária/threshold**, nomeie qual dos dois erros é
  mais caro pro produto e confirme que o código erra pro lado barato por
  construção.
- **Cite o nome exato do padrão existente que a decisão nova respeita.**

### Achados de contexto (não são bug de runtime, mas custam caro)

- **Conflito com frente paralela.** A PR acrescenta entrada em arquivo
  compartilhado e quente (tema, DI, rotas, pubspec) que outra frente está
  reescrevendo agora?
  ```bash
  git log --since="2 months ago" --oneline -- <arquivo compartilhado>
  git branch -r --sort=-committerdate | head -15
  ```
- **Valor cru que já existe como token.** Achou `Color(0xFF...)`, duração,
  string cravada? Procure o mesmo valor no tema/constantes antes de sugerir:
  `grep -rn "0xFF495057" lib/`.
- **Parse: guarda de tipo vs cast.** `x as List?` com `?? []` **não** é
  defensivo: o `??` cobre só `null`, o cast estoura em tipo errado.
- **Blast radius do parse.** Mapeamento eager num payload agregado faz **um**
  item ruim derrubar a tela inteira.
- **O que a PR removeu deixou pendurado?** Constante/lexicon/asset órfão,
  método privado sem chamador, teste que virou tautologia.
- **Simetria entre caminhos análogos.** Se a PR duplica um fluxo, leia os dois
  lado a lado.
- **Desfecho engolido em silêncio.** Enum/Result com ramo sem tratamento
  visível é bug de UX.
- **Compliance de loja.** A PR cria caminho novo até compra fora do app?
  Confira se precisa de guard para conta de revisão da Apple/Google.

### P2, sugestões (poucas e que valham a pena)

No máximo umas 3 a 5 na mensagem final, só as que mudam manutenção ou
comportamento de verdade: duplicação evidente de algo que o core já dá,
lógica de negócio dentro de widget, nome muito enganoso, oportunidade clara
de reutilizar contrato existente. Estilo que o lint já cobre não entra.

### O que NÃO apontar (bom senso com o débito técnico)

- **Código novo:** cobrar o padrão do projeto. Anti-padrões valem como achado.
  Se o projeto tem documento de anti-padrões, use-o como referência.
- **Código legado** que a PR só ajusta pontualmente: NÃO pedir migração pro
  padrão novo nem apontar o débito pré-existente ao redor. Só apontar o que a
  mudança em si introduz ou piora.
- **Fronteira:** se a PR cria costura nova entre padrão novo e legado, isso é
  achado sim.
- Nunca apontar débito em linha que a PR não tocou, a menos que a mudança da
  PR dependa dele pra funcionar.

## Passo 4: verificar antes de apontar

Falso positivo queima o review inteiro. Antes de qualquer bug entrar no
levantamento:

- Leia o código ao redor no arquivo real (não só o hunk do diff); o guard
  pode estar duas linhas acima do contexto do diff.
- Descreva o cenário concreto de falha (que entrada/estado leva ao
  comportamento errado). Se não conseguir descrever, rebaixe pra dúvida ou
  corte.
- Na mensagem do MR, separe o que é certeza do que é dúvida ("confere se...",
  "não sei se aqui...").
- **A mesma verificação vale pra CONFIRMAR que algo está certo, não só pra
  apontar bug.** Rode o comando que prova: `git blame`/`git show`, `grep`,
  testes. **Antes de comparar contra uma branch remota**, **dê `git fetch`
  nela primeiro**: uma branch remota local desatualizada dá a resposta errada
  sobre conflito real sem nenhum aviso.

## Passo 5: a mensagem pro MR (só no modo PR)

No modo local, pule este passo: a entrega termina no levantamento técnico.

Português, primeira pessoa do singular, tom de colega senior que leu o código
com atenção. Pode (e deve) ser técnica.

**Objetividade acima de tudo.** A mensagem não é o levantamento colado, é o
resumo executável dele. Alvo: **cabe numa tela**. Regra prática por achado: uma
frase do que está errado, uma do que acontece por causa disso, o bloco do código
original, o bloco da correção.

- **Nunca travessão (— ou –), nunca emoji.** Vírgula, ponto, ou reescreve.
- Frase curta. Voz ativa. Sem rodeio antes do ponto.
- Sem cara de IA: nada de "Além disso, vale ressaltar", "É importante notar",
  "Espero ter ajudado", "Ótimo trabalho!" de abertura.
- Abra com uma linha situando o review (o que olhei, impressão geral honesta,
  sem elogio protocolar).
- Um bloco pros **bugs e desvios de padrão** (o que segura o merge) e, se
  houver, um bloco curto de **sugestões** deixando claro que não seguram.
- **No máximo 3 pontos no bloco que segura o merge** e 3 ou 4 linhas soltas
  nas sugestões. O resto fica no levantamento técnico pra eu decidir.
- Cada ponto: caminho do arquivo com linha, o problema, e a correção **sempre
  em dois blocos, o original e a sugestão** (bloco de código normal).
- Não reexplique o que o autor obviamente sabe. Vá direto no ponto de código.
- Se a PR for gigante, uma linha no fim com o que você **não** cobriu.

#### Como fazer o achado ser aceito sem atrito

- **Gradue em voz alta.** Diga onde cada ponto se encaixa: "aqui é a parte
  mais importante pra alinhar", "um menor que vale citar", "vale conferir".
- **Marque a incerteza como incerteza.** "Vale conferir" em vez de afirmar.
- **Reconheça a parte certa antes de cobrar.**
- **Explique o custo, não a regra.** Em vez de "não use cor hardcoded", diga
  o que dói.
- **Use a evidência que está na própria PR.**
- **Diga a orientação concreta, com o precedente do repo.**
- **Separe o que a PR introduz do que ela herdou.**

### Exemplo de tom (calibrar por aqui)

```markdown
Li o diff todo e rodei o analyze. Ficou bom no geral, dois pontos seguram o merge:

**1. Spinner infinito quando a API falha** `load_metrics_usecase.dart:42`

O `fold` só trata sucesso. Com 500 o `isLoading` nunca volta pra false e a tela fica girando pra sempre.

Original:

    result.fold(
      (failure) {},
      (data) => metrics.value = data,
    );

Sugestão:

    result.fold(
      (failure) {
        isLoading.value = false;
        lastError.value = failure;
      },
      (data) {
        isLoading.value = false;
        metrics.value = data;
      },
    );

**2. Catch que nunca roda** `metrics_datasource.dart:88`

O `try/catch` espera exceção em 404, mas o HTTP client aceita todos os status como resposta normal. A checagem tem que ser no status.

Original:

    try {
      final res = await httpClient.get(routes.metrics);
      return Success(MetricsModel.fromJson(res.data));
    } on DioException catch (_) {
      return Failure(NotFoundFailure());
    }

Sugestão:

    final res = await httpClient.get(routes.metrics);
    if (res.statusCode != 200) return Failure(NotFoundFailure());
    return Success(MetricsModel.fromJson(res.data));

Sem segurar o merge: o `MetricsCard` refaz o cálculo de porcentagem que o `ProgressBarWidget` já tem. E o `ScrollController` da page não tem dispose, não achei.

Não cobri asset nem pubspec.lock.
```

## Regras duras

- **Nunca começar o review sem as entradas do modo em mãos** (modo PR:
  descrição da PR + task; modo local: task): se faltou, perguntar primeiro
  (gate de partida acima).
- No modo local, o review é só leitura: nunca commitar, stashar, editar
  arquivo ou "já corrigir" um achado por conta própria.
- **Nunca** rodar `gh pr review`, `gh pr comment`, aprovar, reprovar ou pedir
  mudança na PR por conta própria. A entrega é texto pra eu colar. Só publica
  se eu mandar explicitamente, e aí me mostra o texto final antes.
- Nunca commitar, pushar ou alterar arquivos da branch da PR durante o review.
- Se fez checkout, voltar pra branch original ao terminar.
