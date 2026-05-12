# 001 - Preparando o Ambiente

## Objetivo

Este notebook cria toda a infraestrutura necessária no Unity Catalog do Databricks antes de executar o pipeline:

- Schemas (databases): `landing`, `bronze`, `silver`, `gold`
- Volume: `workspace.landing.dados` (onde os arquivos CSV serão armazenados)

## Quando executar

**Apenas uma vez**, antes de qualquer outro notebook do pipeline. Pode ser reexecutado sem problemas — todos os comandos usam `IF NOT EXISTS`.

## O que é criado

### Schemas

| Schema              | Propósito                                  |
| ------------------- | ------------------------------------------ |
| `workspace.landing` | Contém o Volume para arquivos brutos (CSV) |
| `workspace.bronze`  | Tabelas Delta com dados brutos ingeridos   |
| `workspace.silver`  | Tabelas Delta com Data Quality aplicado    |
| `workspace.gold`    | Tabelas dimensionais (modelo Kimball)      |

### Volume

O **Volume** `workspace.landing.dados` é uma abstração do Unity Catalog para armazenamento de arquivos. É acessado como um caminho de sistema de arquivos:

```
/Volumes/workspace/landing/dados/
```

## Comandos SQL executados

```sql
CREATE SCHEMA IF NOT EXISTS workspace.landing
    COMMENT 'Schema/Database para a Landing Zone';

CREATE VOLUME IF NOT EXISTS workspace.landing.dados
    COMMENT 'Volume para arquivos CSV extraídos do banco de dados';

CREATE SCHEMA IF NOT EXISTS workspace.bronze
    COMMENT 'Schema/Database para dados Bronze (Delta Lake)';

CREATE SCHEMA IF NOT EXISTS workspace.silver
    COMMENT 'Schema/Database para dados Silver (Delta Lake)';

CREATE SCHEMA IF NOT EXISTS workspace.gold
    COMMENT 'Schema/Database para dados Gold — modelagem dimensional (Kimball)';
```

## Diferença entre Schema e Volume

| Conceito   | Armazena                                        | Acessado via                             |
| ---------- | ----------------------------------------------- | ---------------------------------------- |
| **Schema** | Tabelas (Delta, Parquet, etc.) e metadados      | `catalog.schema.tabela`                  |
| **Volume** | Arquivos arbitrários (CSV, JSON, imagens, etc.) | `/Volumes/catalog/schema/volume/arquivo` |

## Notebook de limpeza

O notebook **006 - Destruindo Ambiente** faz o processo inverso: remove todos os schemas (e consequentemente todas as tabelas e volumes) com `DROP SCHEMA ... CASCADE`.

!!! warning "Atenção"
Execute o notebook 006 apenas quando quiser remover **todos** os dados e recomeçar do zero. Esta operação é irreversível.
