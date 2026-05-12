# Databricks notebook source
# MAGIC %md
# MAGIC # 004 - Silver: Bronze + Data Quality → Silver
# MAGIC
# MAGIC Este notebook lê as tabelas Delta da camada **Bronze**, aplica regras de **Data Quality**
# MAGIC e grava o resultado no schema `workspace.silver`.
# MAGIC
# MAGIC ## Regras de Data Quality aplicadas
# MAGIC
# MAGIC | Regra | Descrição |
# MAGIC |---|---|
# MAGIC | Deduplicação | Remove linhas completamente duplicadas |
# MAGIC | Nulos em colunas-chave | Remove linhas com nulos nas PKs/FKs obrigatórias |
# MAGIC | Casting de tipos | Converte datas e numéricos para os tipos corretos |
# MAGIC | Padronização de nomes | Colunas renomeadas para UPPER_SNAKE_CASE com prefixos expandidos |
# MAGIC
# MAGIC ## Convenção de nomes (prefixos)
# MAGIC
# MAGIC | Prefixo original | Expandido |
# MAGIC |---|---|
# MAGIC | `cd_` | `CODIGO_` |
# MAGIC | `nm_` | `NOME_` |
# MAGIC | `dt_` | `DATA_` |
# MAGIC | `vl_` | `VALOR_` |
# MAGIC | `nr_` | `NUMERO_` |
# MAGIC | `ds_` | `DESCRICAO_` |
# MAGIC | `qt_` | `QUANTIDADE_` |
# MAGIC
# MAGIC ## Colunas de auditoria adicionadas
# MAGIC
# MAGIC | Coluna | Descrição |
# MAGIC |---|---|
# MAGIC | `ORIGEM_BRONZE` | Identificador da tabela de origem no Bronze |
# MAGIC | `DATA_PROCESSAMENTO_SILVER` | Timestamp de processamento na camada Silver |
# MAGIC | `QTD_REMOVIDOS_DQ` | Quantidade de registros removidos pelas regras de DQ |

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Definir regras de Data Quality por tabela

# COMMAND ----------

from pyspark.sql import functions as F
from pyspark.sql.types import DateType, IntegerType, DoubleType

# Colunas-chave que não podem ser nulas (nomes originais do Bronze, antes do rename)
DQ_KEY_COLS = {
    "bronze.categoria":   ["cd_categoria"],
    "bronze.cliente":     ["cd_cliente", "cpf"],
    "bronze.endereco":    ["cd_endereco", "cd_cliente", "cd_municipio"],
    "bronze.estado":      ["cd_estado", "cd_regiao"],
    "bronze.fornecedor":  ["cd_fornecedor"],
    "bronze.item_pedido": ["cd_item", "cd_pedido", "cd_produto"],
    "bronze.municipio":   ["cd_municipio", "cd_estado"],
    "bronze.pedido":      ["cd_pedido", "cd_cliente"],
    "bronze.produto":     ["cd_produto", "cd_categoria", "cd_fornecedor"],
    "bronze.regiao":      ["cd_regiao"],
    "bronze.telefone":    ["cd_telefone", "cd_cliente"],
}

# Colunas de data a serem convertidas para DateType (nomes APÓS o rename)
DQ_DATE_COLS = {
    "silver.cliente": ["DATA_NASCIMENTO"],
    "silver.pedido":  ["DATA_PEDIDO"],
}

# Colunas numéricas inteiras a serem convertidas (nomes APÓS o rename)
DQ_INT_COLS = {
    "silver.item_pedido": ["QUANTIDADE_QUANTIDADE"],
}

# Colunas numéricas decimais a serem convertidas (nomes APÓS o rename)
DQ_DOUBLE_COLS = {
    "silver.produto":     ["VALOR_PRECO"],
    "silver.item_pedido": ["VALOR_UNITARIO", "VALOR_DESCONTO"],
}

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Funções auxiliares

# COMMAND ----------

def _apply_name_rules(colname: str) -> str:
    n = colname.upper()
    n = n.replace("CD_",  "CODIGO_")
    n = n.replace("VL_",  "VALOR_")
    n = n.replace("DT_",  "DATA_")
    n = n.replace("NM_",  "NOME_")
    n = n.replace("DS_",  "DESCRICAO_")
    n = n.replace("NR_",  "NUMERO_")
    n = n.replace("QT_",  "QUANTIDADE_")
    return n

def _safe_drop(df, cols):
    existing = set(df.columns)
    to_drop = [c for c in cols if c in existing]
    return df.drop(*to_drop) if to_drop else df

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Função principal de processamento Silver (com DQ)

# COMMAND ----------

def processar_silver(src_fqn: str, dest_fqn: str):
    """
    Lê da Bronze, aplica DQ completo e salva na Silver como Managed Table Delta.

    Etapas aplicadas:
      1. Deduplicação de linhas
      2. Remoção de nulos em colunas-chave
      3. Remoção das colunas de auditoria do Bronze
      4. Renomeação de colunas (UPPER_SNAKE_CASE com prefixos expandidos)
      5. Casting de tipos para datas e numéricos
      6. Adição de colunas de auditoria Silver
      7. Gravação como Managed Table Delta
    """

    df = spark.read.format("delta").table(src_fqn)
    contagem_inicial = df.count()

    # 1. Deduplicação
    df = df.dropDuplicates()
    apos_dedup = df.count()

    # 2. Remoção de nulos nas colunas-chave
    key_cols = DQ_KEY_COLS.get(src_fqn, [])
    if key_cols:
        df = df.dropna(subset=key_cols)
    contagem_final = df.count()

    removidos = contagem_inicial - contagem_final
    print(f"[DQ] {src_fqn:32s}  inicial={contagem_inicial:4d}  após_dedup={apos_dedup:4d}  final={contagem_final:4d}  removidos={removidos}")

    # 3. Remover colunas de auditoria do Bronze
    df = _safe_drop(df, ["data_hora_bronze", "nome_arquivo"])

    # 4. Renomear colunas
    new_cols = [_apply_name_rules(c) for c in df.columns]
    df = df.toDF(*new_cols)

    # 5. Casting de tipos
    for col in DQ_DATE_COLS.get(dest_fqn, []):
        if col in df.columns:
            df = df.withColumn(col, F.to_date(F.col(col).cast("string"), "yyyy-MM-dd"))

    for col in DQ_INT_COLS.get(dest_fqn, []):
        if col in df.columns:
            df = df.withColumn(col, F.col(col).cast(IntegerType()))

    for col in DQ_DOUBLE_COLS.get(dest_fqn, []):
        if col in df.columns:
            df = df.withColumn(col, F.col(col).cast(DoubleType()))

    # 6. Colunas de auditoria Silver
    df = (df
          .withColumn("ORIGEM_BRONZE",             F.lit(src_fqn))
          .withColumn("DATA_PROCESSAMENTO_SILVER", F.current_timestamp())
          .withColumn("QTD_REMOVIDOS_DQ",          F.lit(removidos))
         )

    # 7. Gravar como Managed Table Delta
    (df.write
       .format("delta")
       .mode("overwrite")
       .saveAsTable(dest_fqn))

    return dest_fqn

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Processar todas as tabelas Bronze → Silver

# COMMAND ----------

processar_silver("bronze.categoria",   "silver.categoria")
processar_silver("bronze.cliente",     "silver.cliente")
processar_silver("bronze.endereco",    "silver.endereco")
processar_silver("bronze.estado",      "silver.estado")
processar_silver("bronze.fornecedor",  "silver.fornecedor")
processar_silver("bronze.item_pedido", "silver.item_pedido")
processar_silver("bronze.municipio",   "silver.municipio")
processar_silver("bronze.pedido",      "silver.pedido")
processar_silver("bronze.produto",     "silver.produto")
processar_silver("bronze.regiao",      "silver.regiao")
processar_silver("bronze.telefone",    "silver.telefone")

print("\nProcessamento Silver concluído.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Verificar tabelas criadas no schema Silver

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN silver

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Inspecionar relatório de auditoria DQ

# COMMAND ----------

# MAGIC %sql
# MAGIC SELECT ORIGEM_BRONZE, DATA_PROCESSAMENTO_SILVER, QTD_REMOVIDOS_DQ
# MAGIC FROM silver.pedido
# MAGIC LIMIT 5;

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Confirmar formato Delta e tipo Managed

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE DETAIL silver.pedido;

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE EXTENDED silver.pedido;
