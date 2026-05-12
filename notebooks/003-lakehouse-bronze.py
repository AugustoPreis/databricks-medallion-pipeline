# Databricks notebook source
# MAGIC %md
# MAGIC # 003 - Bronze: Landing → Delta Lake
# MAGIC
# MAGIC Este notebook lê os arquivos **CSV** gerados na etapa anterior (Landing) e os grava
# MAGIC no formato **Delta Lake** no schema `workspace.bronze`.
# MAGIC
# MAGIC As tabelas Bronze são do tipo **Managed** — o Databricks gerencia tanto os metadados
# MAGIC (Unity Catalog) quanto os dados físicos (armazenamento interno).
# MAGIC
# MAGIC ## Fluxo
# MAGIC
# MAGIC ```
# MAGIC /Volumes/workspace/landing/dados/*.csv  ──►  workspace.bronze.<tabela>  (Delta Lake, Managed)
# MAGIC ```
# MAGIC
# MAGIC ## Colunas de auditoria adicionadas
# MAGIC
# MAGIC | Coluna | Descrição |
# MAGIC |---|---|
# MAGIC | `data_hora_bronze` | Timestamp de ingestão na camada Bronze |
# MAGIC | `nome_arquivo` | Nome do arquivo CSV de origem |

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Verificar arquivos disponíveis na Landing

# COMMAND ----------

display(dbutils.fs.ls('/Volumes/workspace/landing/dados/'))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Ler os arquivos CSV da Landing Zone
# MAGIC
# MAGIC `inferSchema=true` faz com que o Spark analise o conteúdo para detectar os tipos de dados automaticamente.

# COMMAND ----------

caminho_landing = '/Volumes/workspace/landing/dados'

df_categoria   = spark.read.option("inferSchema", "true").option("header", "true").csv(f"{caminho_landing}/categoria.csv")
df_cliente     = spark.read.option("inferSchema", "true").option("header", "true").csv(f"{caminho_landing}/cliente.csv")
df_endereco    = spark.read.option("inferSchema", "true").option("header", "true").csv(f"{caminho_landing}/endereco.csv")
df_estado      = spark.read.option("inferSchema", "true").option("header", "true").csv(f"{caminho_landing}/estado.csv")
df_fornecedor  = spark.read.option("inferSchema", "true").option("header", "true").csv(f"{caminho_landing}/fornecedor.csv")
df_item_pedido = spark.read.option("inferSchema", "true").option("header", "true").csv(f"{caminho_landing}/item_pedido.csv")
df_municipio   = spark.read.option("inferSchema", "true").option("header", "true").csv(f"{caminho_landing}/municipio.csv")
df_pedido      = spark.read.option("inferSchema", "true").option("header", "true").csv(f"{caminho_landing}/pedido.csv")
df_produto     = spark.read.option("inferSchema", "true").option("header", "true").csv(f"{caminho_landing}/produto.csv")
df_regiao      = spark.read.option("inferSchema", "true").option("header", "true").csv(f"{caminho_landing}/regiao.csv")
df_telefone    = spark.read.option("inferSchema", "true").option("header", "true").csv(f"{caminho_landing}/telefone.csv")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Adicionar colunas de auditoria (metadados)
# MAGIC
# MAGIC Estas colunas permitem rastrear quando e de onde os dados foram ingeridos.

# COMMAND ----------

from pyspark.sql.functions import current_timestamp, lit

df_categoria   = df_categoria.withColumn("data_hora_bronze", current_timestamp()).withColumn("nome_arquivo", lit("categoria.csv"))
df_cliente     = df_cliente.withColumn("data_hora_bronze", current_timestamp()).withColumn("nome_arquivo", lit("cliente.csv"))
df_endereco    = df_endereco.withColumn("data_hora_bronze", current_timestamp()).withColumn("nome_arquivo", lit("endereco.csv"))
df_estado      = df_estado.withColumn("data_hora_bronze", current_timestamp()).withColumn("nome_arquivo", lit("estado.csv"))
df_fornecedor  = df_fornecedor.withColumn("data_hora_bronze", current_timestamp()).withColumn("nome_arquivo", lit("fornecedor.csv"))
df_item_pedido = df_item_pedido.withColumn("data_hora_bronze", current_timestamp()).withColumn("nome_arquivo", lit("item_pedido.csv"))
df_municipio   = df_municipio.withColumn("data_hora_bronze", current_timestamp()).withColumn("nome_arquivo", lit("municipio.csv"))
df_pedido      = df_pedido.withColumn("data_hora_bronze", current_timestamp()).withColumn("nome_arquivo", lit("pedido.csv"))
df_produto     = df_produto.withColumn("data_hora_bronze", current_timestamp()).withColumn("nome_arquivo", lit("produto.csv"))
df_regiao      = df_regiao.withColumn("data_hora_bronze", current_timestamp()).withColumn("nome_arquivo", lit("regiao.csv"))
df_telefone    = df_telefone.withColumn("data_hora_bronze", current_timestamp()).withColumn("nome_arquivo", lit("telefone.csv"))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Gravar no formato Delta Lake — schema `bronze`
# MAGIC
# MAGIC Tabelas **Managed**: o Databricks controla localização física e metadados.
# MAGIC `mode("overwrite")` garante idempotência (reexecutar o notebook não duplica dados).

# COMMAND ----------

df_categoria.write.format('delta').mode("overwrite").saveAsTable("bronze.categoria")
df_cliente.write.format('delta').mode("overwrite").saveAsTable("bronze.cliente")
df_endereco.write.format('delta').mode("overwrite").saveAsTable("bronze.endereco")
df_estado.write.format('delta').mode("overwrite").saveAsTable("bronze.estado")
df_fornecedor.write.format('delta').mode("overwrite").saveAsTable("bronze.fornecedor")
df_item_pedido.write.format('delta').mode("overwrite").saveAsTable("bronze.item_pedido")
df_municipio.write.format('delta').mode("overwrite").saveAsTable("bronze.municipio")
df_pedido.write.format('delta').mode("overwrite").saveAsTable("bronze.pedido")
df_produto.write.format('delta').mode("overwrite").saveAsTable("bronze.produto")
df_regiao.write.format('delta').mode("overwrite").saveAsTable("bronze.regiao")
df_telefone.write.format('delta').mode("overwrite").saveAsTable("bronze.telefone")

print("Todas as tabelas foram gravadas no schema bronze com sucesso.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Verificar tabelas criadas no schema Bronze

# COMMAND ----------

# MAGIC %sql
# MAGIC SHOW TABLES IN bronze

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Confirmar tipo Managed e formato Delta

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE DETAIL bronze.pedido;

# COMMAND ----------

# MAGIC %sql
# MAGIC DESCRIBE EXTENDED bronze.pedido;
