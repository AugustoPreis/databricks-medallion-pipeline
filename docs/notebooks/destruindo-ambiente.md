# 006 - Destruindo o Ambiente

## Objetivo

Este notebook remove toda a estrutura criada pelo notebook `001 - Preparando o Ambiente`:
schemas, tabelas Delta e volumes (incluindo todos os arquivos CSV).

Use-o quando quiser **resetar o ambiente** e reexecutar o pipeline do zero.

!!! warning "Atenção"
    Esta operação é **irreversível**. Todos os dados de todas as camadas serão permanentemente apagados.

## Quando executar

- Após concluir os estudos e querer liberar recursos
- Antes de reexecutar o pipeline completo a partir do zero
- Para limpar um ambiente com dados inconsistentes

## Comandos SQL executados

```sql
DROP SCHEMA IF EXISTS workspace.bronze  CASCADE;
DROP SCHEMA IF EXISTS workspace.silver  CASCADE;
DROP SCHEMA IF EXISTS workspace.gold    CASCADE;
DROP SCHEMA IF EXISTS workspace.landing CASCADE;
```

A cláusula `CASCADE` garante que todos os objetos contidos no schema (tabelas, views, volumes) sejam removidos junto com ele.

A ordem importa: `bronze`, `silver` e `gold` são removidos antes de `landing` para evitar dependências pendentes.

## Verificação

Após a execução, o comando `SHOW SCHEMAS IN workspace` confirma que nenhum dos schemas do pipeline permanece ativo.

## Notebook de configuração

O notebook **001 - Preparando o Ambiente** faz o processo inverso: cria todos os schemas e o volume necessários para o pipeline. Execute-o após destruir o ambiente para recomeçar.
