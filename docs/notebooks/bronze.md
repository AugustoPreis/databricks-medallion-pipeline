# 003 - Bronze: Landing → Delta Lake

## Objetivo

Ler os arquivos CSV da Landing Zone e gravá-los como tabelas **Delta Lake Managed** no schema `workspace.bronze`.

A camada Bronze representa a **ingestão bruta** — os dados são preservados como vieram da fonte, com adição apenas de colunas de auditoria.

## Transformações aplicadas

### Colunas de auditoria

Duas colunas são adicionadas a cada tabela:

| Coluna | Tipo | Valor |
|---|---|---|
| `data_hora_bronze` | Timestamp | Horário da ingestão (`current_timestamp()`) |
| `nome_arquivo` | String | Nome do arquivo CSV de origem |

Essas colunas permitem rastrear quando e de onde cada linha foi ingerida.

## Leitura dos CSVs

```python
caminho_landing = '/Volumes/workspace/landing/dados'

df_pedido = spark.read \
    .option("inferSchema", "true") \
    .option("header", "true") \
    .csv(f"{caminho_landing}/pedido.csv")
```

### `inferSchema=true`

Com `inferSchema=true`, o Spark analisa os dados para detectar tipos automaticamente:
- Números inteiros → `IntegerType` ou `LongType`
- Números decimais → `DoubleType`
- Strings → `StringType`

## Gravação em Delta Lake

```python
df_pedido.write \
    .format('delta') \
    .mode("overwrite") \
    .saveAsTable("bronze.pedido")
```

### `mode("overwrite")`

Garante **idempotência**: reexecutar o notebook sobrescreve os dados sem duplicar.

### `saveAsTable("bronze.pedido")`

Cria uma **Managed Table** no Unity Catalog.

## Tabelas criadas no Bronze

| Tabela | Origem CSV |
|---|---|
| `bronze.categoria` | `categoria.csv` |
| `bronze.cliente` | `cliente.csv` |
| `bronze.endereco` | `endereco.csv` |
| `bronze.estado` | `estado.csv` |
| `bronze.fornecedor` | `fornecedor.csv` |
| `bronze.item_pedido` | `item_pedido.csv` |
| `bronze.municipio` | `municipio.csv` |
| `bronze.pedido` | `pedido.csv` |
| `bronze.produto` | `produto.csv` |
| `bronze.regiao` | `regiao.csv` |
| `bronze.telefone` | `telefone.csv` |

## Verificação

```sql
-- Listar tabelas criadas
SHOW TABLES IN bronze;

-- Ver detalhes do formato Delta
DESCRIBE DETAIL bronze.pedido;

-- Confirmar que é MANAGED
DESCRIBE EXTENDED bronze.pedido;
```
