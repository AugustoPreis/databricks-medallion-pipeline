# Delta Lake

## O que é Delta Lake?

O **Delta Lake** é um formato de armazenamento de dados open-source que adiciona transações ACID, controle de versão e outras funcionalidades ao objeto de armazenamento tradicional (S3, ADLS, GCS, DBFS).

Criado pela Databricks, o Delta Lake é o formato padrão de tabelas no Databricks e no Unity Catalog.

---

## Características principais

### Transações ACID

O Delta Lake garante as quatro propriedades ACID:

| Propriedade     | Descrição                                                                |
| --------------- | ------------------------------------------------------------------------ |
| **Atomicity**   | Uma operação é executada completamente ou não é executada                |
| **Consistency** | O banco permanece em estado consistente antes e depois de cada transação |
| **Isolation**   | Leituras e escritas concorrentes não interferem entre si                 |
| **Durability**  | Dados confirmados nunca são perdidos                                     |

### Delta Log (Transaction Log)

Toda operação em uma tabela Delta é registrada no **Delta Log** — um diretório `_delta_log/` com arquivos JSON que descrevem cada transação. Isso permite:

- **Time Travel:** consultar versões anteriores dos dados
- **Auditoria:** ver quem fez o quê e quando
- **Rollback:** reverter para uma versão anterior

```sql
-- Consultar versão anterior da tabela
SELECT * FROM bronze.pedido VERSION AS OF 1;

-- Consultar pelo timestamp
SELECT * FROM bronze.pedido TIMESTAMP AS OF '2024-01-01';

-- Ver histórico de versões
DESCRIBE HISTORY bronze.pedido;
```

### Schema Evolution

O Delta Lake suporta evolução automática do schema:

```python
df.write.format("delta").option("mergeSchema", "true").mode("append").saveAsTable("bronze.pedido")
```

---

## Tipos de tabelas Delta no Databricks

### Managed Tables (Tabelas Gerenciadas)

- O Databricks gerencia tanto os **metadados** (Unity Catalog) quanto os **dados físicos** (armazenamento interno)
- Ao apagar a tabela (`DROP TABLE`), os dados físicos também são apagados
- Usadas neste projeto em todas as camadas (Bronze, Silver, Gold)

```python
# Criar tabela Managed
df.write.format("delta").saveAsTable("bronze.pedido")
```

### External Tables (Tabelas Externas)

- O Databricks gerencia apenas os **metadados**; os dados ficam em um local externo (S3, ADLS, etc.)
- Ao apagar a tabela, os dados físicos **não** são apagados
- Útil para dados que precisam existir independentemente do catálogo

```python
# Criar tabela External
df.write.format("delta").option("path", "s3://bucket/path").saveAsTable("bronze.pedido")
```

---

## Comandos SQL úteis

```sql
-- Ver formato e localização da tabela
DESCRIBE DETAIL bronze.pedido;

-- Ver se é MANAGED ou EXTERNAL
DESCRIBE EXTENDED bronze.pedido;

-- Otimizar a tabela (compactar arquivos pequenos)
OPTIMIZE bronze.pedido;

-- Limpar versões antigas (economy de storage)
VACUUM bronze.pedido RETAIN 168 HOURS;

-- Operação MERGE (upsert)
MERGE INTO gold.dim_cliente AS target
USING novos_clientes AS source
ON target.codigo_cliente = source.codigo_cliente
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;
```

---

## Por que Delta Lake neste projeto?

| Necessidade                            | Como o Delta Lake resolve         |
| -------------------------------------- | --------------------------------- |
| Reprocessar dados sem duplicar         | `mode("overwrite")` é idempotente |
| Rastrear quando cada dado foi inserido | Colunas de auditoria + Delta Log  |
| Suportar MERGE para dimensões SCD1     | Suporte nativo a `MERGE INTO`     |
| Performance em leituras analíticas     | Estatísticas e Z-ordering         |
| Evolução de schema ao longo do tempo   | `mergeSchema` option              |
