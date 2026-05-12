# 002 - Landing: Extração do Banco de Dados

## Objetivo

Extrair todos os dados de um banco de dados relacional e gravar cada tabela como arquivo **CSV** no Volume `workspace.landing.dados`.

## Banco de dados utilizado

**SQLite em memória** — banco de dados relacional leve e embutido na biblioteca padrão do Python. O banco é criado em memória (`:memory:`) a cada execução, simulando a extração de um sistema de origem real.

!!! info "Por que SQLite?"
    O SQLite está disponível em todos os ambientes Python sem necessidade de instalação de drivers adicionais. Para ambientes de produção, a extração seria feita via JDBC (PostgreSQL, MySQL, SQL Server, etc.) ou conectores nativos de cloud (Salesforce, SAP, etc.).

## Modelo de dados (SQLite)

```
regiao ◄──── estado ◄──── municipio ◄──── endereco
                                               │
                                           cliente ──── telefone
                                               │
                                           pedido ──────────────► item_pedido ──► produto ──► categoria
                                                                                            └──► fornecedor
```

## Tabelas extraídas

| Tabela        | Registros | Descrição                                  |
| ------------- | --------- | ------------------------------------------ |
| `regiao`      | 5         | Regiões do Brasil                          |
| `estado`      | 10        | Estados                                    |
| `municipio`   | 15        | Municípios                                 |
| `categoria`   | 8         | Categorias de produtos                     |
| `fornecedor`  | 5         | Fornecedores / distribuidores              |
| `produto`     | 15        | Produtos da loja                           |
| `cliente`     | 8         | Compradores                                |
| `endereco`    | 8         | Endereços de entrega (um por cliente)      |
| `telefone`    | 10        | Telefones de contato                       |
| `pedido`      | 15        | Pedidos realizados                         |
| `item_pedido` | 28        | Itens de cada pedido (produto + quantidade)|

## Fluxo de extração

```python
# 1. Cria banco SQLite em memória
conn = sqlite3.connect(":memory:")

# 2. Cria schema e insere dados
cursor.executescript("CREATE TABLE IF NOT EXISTS ...")
cursor.executemany("INSERT INTO ...")

# 3. Para cada tabela:
for nome_tabela in tabelas:
    # Extrai via pandas
    df_pandas = pd.read_sql_query(f"SELECT * FROM {nome_tabela}", conn)

    # Converte para Spark DataFrame
    df_spark = spark.createDataFrame(df_pandas)

    # Grava como CSV no Volume
    df_spark.coalesce(1).write.mode("overwrite").option("header", "true").csv(...)
```

## Arquivos gerados

Após a execução, o Volume `workspace.landing.dados` conterá:

```
/Volumes/workspace/landing/dados/
├── categoria.csv
├── cliente.csv
├── endereco.csv
├── estado.csv
├── fornecedor.csv
├── item_pedido.csv
├── municipio.csv
├── pedido.csv
├── produto.csv
├── regiao.csv
└── telefone.csv
```

## Por que `coalesce(1)`?

O Spark distribui a escrita em múltiplos arquivos por padrão (um por partição). O `coalesce(1)` força a geração de **um único arquivo CSV** por tabela, facilitando a leitura no notebook Bronze.

!!! tip "Em produção"
    Para volumes maiores de dados, remova o `coalesce(1)` para manter a paralelização do Spark. O notebook Bronze consegue ler múltiplos arquivos de um diretório normalmente.
