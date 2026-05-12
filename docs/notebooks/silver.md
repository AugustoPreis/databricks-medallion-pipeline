# 004 - Silver: Data Quality

## Objetivo

Ler as tabelas da camada Bronze, aplicar regras de **Data Quality** e gravar os dados refinados no schema `workspace.silver`.

A camada Silver é a "versão de verdade" dos dados — limpa, validada e padronizada.

## Regras de Data Quality aplicadas

### 1. Deduplicação

Remove linhas completamente idênticas:

```python
df = df.dropDuplicates()
```

### 2. Remoção de nulos em colunas-chave

Remove linhas onde colunas obrigatórias (PKs e FKs) estão nulas:

```python
DQ_KEY_COLS = {
    "bronze.pedido":      ["cd_pedido", "cd_cliente"],
    "bronze.item_pedido": ["cd_item", "cd_pedido", "cd_produto"],
    "bronze.produto":     ["cd_produto", "cd_categoria", "cd_fornecedor"],
    ...
}

df = df.dropna(subset=key_cols)
```

### 3. Remoção das colunas de auditoria Bronze

As colunas `data_hora_bronze` e `nome_arquivo` são removidas antes de gravar na Silver.

### 4. Padronização de nomes de colunas

Todos os nomes de colunas são convertidos para **UPPER_SNAKE_CASE** com prefixos expandidos:

| Prefixo original | Expandido    | Exemplo                               |
| ---------------- | ------------ | ------------------------------------- |
| `cd_`            | `CODIGO_`    | `cd_produto` → `CODIGO_PRODUTO`       |
| `nm_`            | `NOME_`      | `nm_produto` → `NOME_PRODUTO`         |
| `dt_`            | `DATA_`      | `dt_pedido` → `DATA_PEDIDO`           |
| `vl_`            | `VALOR_`     | `vl_preco` → `VALOR_PRECO`            |
| `nr_`            | `NUMERO_`    | `nr_telefone` → `NUMERO_TELEFONE`     |
| `ds_`            | `DESCRICAO_` | `ds_status` → `DESCRICAO_STATUS`      |
| `qt_`            | `QUANTIDADE_`| `qt_quantidade` → `QUANTIDADE_QUANTIDADE` |

### 5. Casting de tipos

```python
DQ_DATE_COLS = {
    "silver.cliente": ["DATA_NASCIMENTO"],
    "silver.pedido":  ["DATA_PEDIDO"],
}

DQ_DOUBLE_COLS = {
    "silver.produto":     ["VALOR_PRECO"],
    "silver.item_pedido": ["VALOR_UNITARIO", "VALOR_DESCONTO"],
}
```

O casting é crítico para que o join com `dim_tempo` no notebook Gold funcione corretamente (join entre `DateType`).

## Colunas de auditoria adicionadas

| Coluna | Tipo | Valor |
|---|---|---|
| `ORIGEM_BRONZE` | String | Nome da tabela de origem (`bronze.pedido`) |
| `DATA_PROCESSAMENTO_SILVER` | Timestamp | Horário do processamento |
| `QTD_REMOVIDOS_DQ` | Integer | Quantidade de registros removidos pelas regras de DQ |

## Relatório de DQ

A função `processar_silver` imprime um relatório para cada tabela:

```
[DQ] bronze.categoria       inicial=   8  após_dedup=   8  final=   8  removidos=0
[DQ] bronze.cliente         inicial=   8  após_dedup=   8  final=   8  removidos=0
[DQ] bronze.item_pedido     inicial=  28  após_dedup=  28  final=  28  removidos=0
[DQ] bronze.pedido          inicial=  15  após_dedup=  15  final=  15  removidos=0
[DQ] bronze.produto         inicial=  15  após_dedup=  15  final=  15  removidos=0
...
```

## Tabelas criadas no Silver

| Tabela Silver | Origem Bronze |
|---|---|
| `silver.categoria` | `bronze.categoria` |
| `silver.cliente` | `bronze.cliente` |
| `silver.endereco` | `bronze.endereco` |
| `silver.estado` | `bronze.estado` |
| `silver.fornecedor` | `bronze.fornecedor` |
| `silver.item_pedido` | `bronze.item_pedido` |
| `silver.municipio` | `bronze.municipio` |
| `silver.pedido` | `bronze.pedido` |
| `silver.produto` | `bronze.produto` |
| `silver.regiao` | `bronze.regiao` |
| `silver.telefone` | `bronze.telefone` |
