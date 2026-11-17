---
name: consultar-documentacao-modulo
description: >-
  Busca contexto documentado de um dominio, microfrontend, modulo, package ou
  feature Flutter antes de analisar o codigo. Use quando o usuario pedir "busque
  informacoes sobre o modulo", "consulte a documentacao do modulo", "entenda o
  modulo X", "qual API ou rota esse modulo usa", "como funciona esse package" ou
  precisar de contexto arquitetural documentado para implementar, revisar ou
  explicar algo.
argument-hint: "Informe o nome do dominio, modulo, package ou feature e a duvida"
user-invocable: true
---

# Consultar Documentação de Módulo

## Objetivo

Recuperar contexto confiável sobre um domínio, microfrontend, módulo, package ou feature a partir da documentação gerada em `<docsRoot>` (pela skill `assimilar-conhecimento-documentacao`), evitando exploração desnecessária do código e preparando uma resposta ou tarefa já alinhada com o vocabulário, arquitetura, APIs, rotas e convenções registradas.

Esta skill é exclusivamente de **consulta**: não altera código, documentação, skills, instruções ou arquivos do repositório.

## Quando usar

Use quando o usuário:

- pedir informações sobre um módulo, package ou feature;
- perguntar quais APIs, rotas ou telas uma área possui;
- pedir para implementar algo dentro de um módulo/microfrontend sem fornecer contexto;
- pedir uma explicação arquitetural de uma feature;
- solicitar uma revisão ou diagnóstico que dependa das convenções do módulo;
- mencionar o nome de um módulo, package ou feature do projeto para entender seu funcionamento.

## Fonte de verdade e prioridade

Defina `<docsRoot>` procurando a pasta de documentação do projeto (por padrão `docs/` na raiz do repositório, ou o caminho de documentação indicado pelo usuário/ambiente). Consulte as fontes nesta ordem:

1. **Catálogo e fichas técnicas de IA (`<docsRoot>/ia-conhecimento/`):**
   - `<docsRoot>/ia-conhecimento/<dominio>-domain-catalog.md` (ou `<projeto>-catalog.md`)
   - `<docsRoot>/ia-conhecimento/<slug>.md` referente ao módulo, package ou feature
2. **Outros arquivos `.md` de contexto do módulo:**
   - `<docsRoot>/doc-modulos/<modulo>/context.md` ou `<docsRoot>/<modulo>/README.md`, quando existirem
   - `README.md` local do package/módulo e ADRs em `<docsRoot>/adr/`
3. **Documentação HTML humana (`<docsRoot>/doc-modulos/`):**
   - `<docsRoot>/doc-modulos/<dominio>/<modulo>.html` e `index.html`, apenas para complementar visão humana, tabelas de contrato, navegação e links. Não trate CSS ou estrutura visual como fonte arquitetural primária.
4. **Código, testes e configurações do repositório:**
   - consulte somente para confirmar um fato específico, preencher uma lacuna ou responder algo que a documentação ainda não cobre.

A documentação registrada tem prioridade sobre suposições. Quando o código e a documentação divergirem, informe a divergência e indique qual fonte foi atualizada mais recentemente com base no `baseline` ou `commit_range` registrado.

## Localização do módulo

Resolva o nome informado contra os caminhos documentados (domínios, microfrontends, módulos ou packages internos como `auth`, `checkout`, `payments`, `core`, etc.).

Comece lendo `<docsRoot>/.docstate.json` (e `<docsRoot>/ia-conhecimento/README.md`, se existir) para descobrir o formato, os módulos mapeados e os slugs de conhecimento registrados. Depois:

1. localize o catálogo ou arquivo `.md` correspondente em `<docsRoot>/ia-conhecimento/`;
2. localize `context.md` ou `README.md` do módulo, se existir;
3. identifique o package ou feature solicitado dentro do contexto;
4. leia os arquivos Markdown relacionados ao package ou feature;
5. use o HTML em `<docsRoot>/doc-modulos/` somente para navegação por âncoras ou complemento.

Não vasculhe o repositório inteiro antes de consultar os caminhos documentados.

## Fluxo de consulta

### 1. Entender a pergunta

Extraia o alvo e o tipo de informação solicitado:

- arquitetura e camadas;
- responsabilidade de package, módulo ou feature;
- APIs, endpoints e payloads;
- telas, rotas e deeplinks;
- injeção de dependência (DI) e ciclo de vida;
- gerenciamento de estado (BLoC, Cubit, Riverpod, Provider, etc.);
- testes, fixtures e mocks;
- convenções para implementar uma mudança.

Se o nome informado for ambíguo (puder representar mais de um package ou feature), faça uma pergunta curta ou liste a ambiguidade antes de prosseguir.

### 2. Ler a documentação Markdown

Leia primeiro os arquivos Markdown relacionados ao alvo:

- fichas em `<docsRoot>/ia-conhecimento/<slug>.md` e catálogos de domínio;
- `context.md` ou `README.md` do módulo;
- notas de arquitetura ou ADRs relacionadas, quando existirem.

Priorize as seções:

- metadados (`dominio`, `modulo`, `package`, `feature`, `commit_range`);
- resumo executivo e responsabilidade;
- arquitetura, estrutura e dependências;
- contratos técnicos (APIs consumidas, rotas/deeplinks, eventos/analytics, erros);
- fluxos e regras de negócio;
- evidências, testes e validações;
- impacto, limitações e dívidas técnicas conhecidas.

### 3. Confirmar somente o necessário no código

Se a documentação responder à pergunta com segurança, não faça uma varredura ampla no código. Se faltar informação:

- deixe claro o que está documentado e o que não está;
- consulte somente os arquivos de código diretamente relacionados;
- confirme endpoints em arquivos de rotas de API, data sources, repositories e constantes de rede;
- confirme telas em arquivos de rotas (`routes.dart`), composers, `PageRoute`, deeplinks e configurações de navegação;
- confirme comportamentos específicos nos testes unitários/widget próximos;
- nunca transforme uma inferência em fato.

### 4. Responder com rastreabilidade

Responda em português, de forma objetiva, separando:

- **Documentado:** fatos encontrados nos arquivos Markdown de documentação.
- **Confirmado no código:** fatos verificados diretamente nos arquivos do repositório porque a doc era insuficiente ou estava desatualizada.
- **Não documentado:** lacunas que ainda precisam ser analisadas.
- **Impacto para a tarefa:** como esse contexto deve orientar a implementação, correção ou revisão solicitada.

Quando citar arquivos locais, use links relativos para os arquivos existentes no workspace. Não invente links para documentos que ainda não existem.

## Regras para uso durante implementação

Antes de editar código com base nesta consulta:

- use a arquitetura documentada como primeiro guia;
- confira o módulo/package interno correto;
- respeite APIs, contratos e rotas registradas;
- preserve o padrão de DI, gerenciamento de estado, repositories e testes documentado;
- se o contexto estiver ausente ou contraditório, pare para confirmar ou faça uma leitura local pontual antes de alterar;
- após concluir uma mudança relevante, atualize a documentação do módulo usando a skill `assimilar-conhecimento-documentacao` ou avise sobre a necessidade de atualização.

## Exemplo de consulta

Pergunta:

> Busque informações sobre o módulo `checkout` antes de alterar o `PaymentRepositoryImpl`.

Procedimento esperado:

1. Ler `<docsRoot>/.docstate.json` e localizar os registros de `checkout` / `payments`.
2. Ler `<docsRoot>/ia-conhecimento/checkout-payments.md` (ou o catálogo do domínio).
3. Consultar a seção do módulo `checkout` e a feature de pagamento.
4. Identificar API, rota, mapper, DI, analytics e testes documentados.
5. Confirmar no código apenas o que faltar (ex.: a assinatura exata de um método no `PaymentRepositoryImpl`).
6. Apresentar o contexto estruturado antes de propor ou realizar a edição.

## Resultado esperado

A resposta final deve permitir que o desenvolvedor ou outra IA entenda rapidamente:

- onde a feature vive;
- qual módulo/package é responsável;
- quais APIs são consumidas;
- quais telas e rotas existem;
- como o estado e a injeção de dependência funcionam;
- quais testes precisam ser mantidos ou atualizados;
- quais pontos ainda não estão cobertos pela documentação.

Nunca altere arquivos como parte desta skill e nunca afirme que uma informação veio da documentação sem ter lido o arquivo correspondente.
