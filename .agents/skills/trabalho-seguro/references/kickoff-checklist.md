# Kickoff - levantamento e plano de ação

O que fazer no início de qualquer trabalho em um projeto Flutter, antes de tocar
em algo.

## 1. Reancorar no estado atual

```bash
git branch --show-current    # estou na branch certa?
git status -sb               # tem mudança não commitada / não relacionada?
git log --oneline -3         # de onde estou partindo?
```

Se a branch não for claramente a certa para este trabalho (ex.: `master`/`main`,
`develop`, ou uma branch de outra feature), **pare e pergunte / proponha** criar
ou trocar de branch antes de continuar.

## 2. Perguntas de levantamento (ajuste ao pedido)

Só siga em frente quando estas estiverem respondidas (por você com certeza, ou pelo
usuário). Na dúvida, pergunte, não assuma.

- **Objetivo:** qual é o resultado esperado, em uma frase? Como saberemos que ficou
  pronto?
- **Escopo:** o que está dentro e o que está **fora**? Há algo que eu explicitamente
  NÃO devo tocar?
- **Branch/alvo:** é aqui mesmo? Precisa de branch nova? Vai virar PR/commit ou é
  exploração?
- **Restrições:** algum arquivo/módulo sensível, padrão a seguir, prazo, ordem?
- **Decisões em aberto:** onde há mais de um caminho razoável? (leve como opções
  via `AskUserQuestion`)
- **Verificação:** como validar (`dart analyze`, `flutter test`, `flutter build`,
  rodar o app, inspeção visual)?
- **Contexto do projeto:** já existe skill/receita para isso? Há arquivo de
  convenções (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`, guia de arquitetura)?
  Reusar em vez de reinventar.
- **Arquitetura:** qual gerenciamento de estado o projeto usa (BLoC, Riverpod,
  Provider, GetX, MobX, etc.)? Qual estrutura de pastas? Devo seguir o mesmo
  padrão?
- **Dependências:** a tarefa exige algum pacote novo? Se sim, confirme antes de
  adicionar ao `pubspec.yaml`.

## 3. Plano de ação (o checklist)

Apresente antes de executar. Cada item deve ser pequeno e **verificável**. Modelo:

```
Plano para: <objetivo em uma frase>
Branch: <branch atual, confirmada>
Fora do escopo: <o que não vou tocar>

[ ] 1. <passo> -> verificação: <como sei que ficou ok>
[ ] 2. <passo> -> verificação: ...
[ ] 3. <passo> -> verificação: ...
Verificação final: dart analyze / flutter test / flutter build
```

Registre isso também na lista de tarefas (TodoList): marque `in_progress` ao começar
cada item e `completed` só quando verificado. Em trabalho não-trivial, **espere o OK**
do usuário no plano antes de executar.

## 4. Durante e no fim

- Ao fechar cada item: marque e mostre a evidência (o que mudou + `arquivo:linha` +
  saída de comando).
- No fim: resumo (o que mudou / onde / como validar / o que ficou de fora). Não
  commitar sem permissão.
