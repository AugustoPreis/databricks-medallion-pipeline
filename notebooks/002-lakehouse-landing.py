# Databricks notebook source
# MAGIC %md
# MAGIC # 002 - Landing Zone: Extração do Banco de Dados
# MAGIC
# MAGIC Este notebook realiza a **extração completa** de todas as tabelas de um banco de dados
# MAGIC relacional (**SQLite em memória**) e grava os arquivos no formato **CSV** no Volume
# MAGIC `workspace.landing.dados`.
# MAGIC
# MAGIC ## Banco de Dados
# MAGIC
# MAGIC | Característica | Valor |
# MAGIC |---|---|
# MAGIC | Tipo | Relacional (SQL) |
# MAGIC | Engine | SQLite (em memória) |
# MAGIC | Domínio | E-commerce / Vendas Online |
# MAGIC | Tabelas | 11 |
# MAGIC
# MAGIC ## Fluxo
# MAGIC
# MAGIC ```
# MAGIC SQLite (em memória) ──► Pandas DataFrame ──► Spark DataFrame ──► CSV (/Volumes/workspace/landing/dados/)
# MAGIC ```
# MAGIC
# MAGIC ## Modelo Relacional
# MAGIC
# MAGIC ```
# MAGIC regiao ◄── estado ◄── municipio ◄── endereco ──► cliente ──► telefone
# MAGIC                                                      │
# MAGIC                                                      ▼
# MAGIC categoria ◄── produto ◄── item_pedido ◄── pedido ◄──┘
# MAGIC      ▲
# MAGIC fornecedor
# MAGIC ```

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Verificar Volume de destino

# COMMAND ----------

display(dbutils.fs.ls('/Volumes/workspace/landing/dados/'))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Criar e popular o banco de dados SQLite em memória
# MAGIC
# MAGIC O `sqlite3` faz parte da biblioteca padrão do Python e está disponível no Databricks Runtime.
# MAGIC Criamos o banco **em memória** (`:memory:`) para simular a extração de um banco de dados relacional.

# COMMAND ----------

import sqlite3

conn = sqlite3.connect(":memory:")
cursor = conn.cursor()

# Criar schema relacional
cursor.executescript("""
    CREATE TABLE IF NOT EXISTS regiao (
        cd_regiao   INTEGER PRIMARY KEY,
        nm_regiao   TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS estado (
        cd_estado   INTEGER PRIMARY KEY,
        uf          TEXT NOT NULL,
        nm_estado   TEXT NOT NULL,
        cd_regiao   INTEGER REFERENCES regiao(cd_regiao)
    );

    CREATE TABLE IF NOT EXISTS municipio (
        cd_municipio    INTEGER PRIMARY KEY,
        nm_municipio    TEXT NOT NULL,
        cd_estado       INTEGER REFERENCES estado(cd_estado)
    );

    CREATE TABLE IF NOT EXISTS categoria (
        cd_categoria    INTEGER PRIMARY KEY,
        nm_categoria    TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS fornecedor (
        cd_fornecedor   INTEGER PRIMARY KEY,
        nm_fornecedor   TEXT NOT NULL,
        ds_contato      TEXT
    );

    CREATE TABLE IF NOT EXISTS produto (
        cd_produto      INTEGER PRIMARY KEY,
        nm_produto      TEXT NOT NULL,
        cd_categoria    INTEGER REFERENCES categoria(cd_categoria),
        cd_fornecedor   INTEGER REFERENCES fornecedor(cd_fornecedor),
        vl_preco        REAL NOT NULL
    );

    CREATE TABLE IF NOT EXISTS cliente (
        cd_cliente      INTEGER PRIMARY KEY,
        nome            TEXT NOT NULL,
        cpf             TEXT NOT NULL UNIQUE,
        sexo            CHAR(1) NOT NULL,
        dt_nascimento   TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS endereco (
        cd_endereco     INTEGER PRIMARY KEY,
        cd_cliente      INTEGER REFERENCES cliente(cd_cliente),
        cd_municipio    INTEGER REFERENCES municipio(cd_municipio),
        logradouro      TEXT NOT NULL,
        numero          TEXT NOT NULL,
        bairro          TEXT NOT NULL,
        cep             TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS telefone (
        cd_telefone     INTEGER PRIMARY KEY,
        cd_cliente      INTEGER REFERENCES cliente(cd_cliente),
        nr_telefone     TEXT NOT NULL,
        tp_telefone     TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS pedido (
        cd_pedido       INTEGER PRIMARY KEY,
        cd_cliente      INTEGER REFERENCES cliente(cd_cliente),
        dt_pedido       TEXT NOT NULL,
        ds_status       TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS item_pedido (
        cd_item         INTEGER PRIMARY KEY,
        cd_pedido       INTEGER REFERENCES pedido(cd_pedido),
        cd_produto      INTEGER REFERENCES produto(cd_produto),
        qt_quantidade   INTEGER NOT NULL,
        vl_unitario     REAL NOT NULL,
        vl_desconto     REAL NOT NULL DEFAULT 0
    );
""")

print("Schema criado com sucesso.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Inserir dados de exemplo

# COMMAND ----------

# Regiões do Brasil
cursor.executemany("INSERT INTO regiao VALUES (?, ?)", [
    (1, 'Norte'),
    (2, 'Nordeste'),
    (3, 'Centro-Oeste'),
    (4, 'Sudeste'),
    (5, 'Sul'),
])

# Estados
cursor.executemany("INSERT INTO estado VALUES (?, ?, ?, ?)", [
    (1,  'SP', 'São Paulo',           4),
    (2,  'RJ', 'Rio de Janeiro',      4),
    (3,  'MG', 'Minas Gerais',        4),
    (4,  'RS', 'Rio Grande do Sul',   5),
    (5,  'PR', 'Paraná',              5),
    (6,  'SC', 'Santa Catarina',      5),
    (7,  'BA', 'Bahia',               2),
    (8,  'PE', 'Pernambuco',          2),
    (9,  'GO', 'Goiás',               3),
    (10, 'AM', 'Amazonas',            1),
])

# Municípios
cursor.executemany("INSERT INTO municipio VALUES (?, ?, ?)", [
    (1,  'São Paulo',       1),
    (2,  'Campinas',        1),
    (3,  'Santos',          1),
    (4,  'Rio de Janeiro',  2),
    (5,  'Niterói',         2),
    (6,  'Belo Horizonte',  3),
    (7,  'Uberlândia',      3),
    (8,  'Porto Alegre',    4),
    (9,  'Caxias do Sul',   4),
    (10, 'Curitiba',        5),
    (11, 'Londrina',        5),
    (12, 'Florianópolis',   6),
    (13, 'Salvador',        7),
    (14, 'Recife',          8),
    (15, 'Goiânia',         9),
])

# Categorias de produtos
cursor.executemany("INSERT INTO categoria VALUES (?, ?)", [
    (1, 'Eletrônicos'),
    (2, 'Roupas e Calçados'),
    (3, 'Alimentos e Bebidas'),
    (4, 'Livros e Papelaria'),
    (5, 'Casa e Decoração'),
    (6, 'Esportes e Lazer'),
    (7, 'Beleza e Cuidados Pessoais'),
    (8, 'Informática e Acessórios'),
])

# Fornecedores
cursor.executemany("INSERT INTO fornecedor VALUES (?, ?, ?)", [
    (1, 'TechBrasil Distribuidora Ltda',    'contato@techbrasil.com.br'),
    (2, 'Moda Sul Importações',             'vendas@modasul.com.br'),
    (3, 'AlimentosBR Ind. e Comércio',      'pedidos@alimentosbr.com.br'),
    (4, 'InfoShop Tecnologia',              'info@infoshop.com.br'),
    (5, 'Casa & Lar Distribuidora',         'atendimento@casaelar.com.br'),
])

# Produtos
cursor.executemany("INSERT INTO produto VALUES (?, ?, ?, ?, ?)", [
    (1,  'Smartphone 128GB',                  1, 1, 1299.90),
    (2,  'Notebook 15.6" Intel i5',           8, 4, 2899.90),
    (3,  'Fone de Ouvido Bluetooth',          1, 1,  199.90),
    (4,  'Camiseta Polo Masculina',           2, 2,   89.90),
    (5,  'Tênis Running Feminino',            2, 2,  349.90),
    (6,  'Jaqueta Corta-vento',               2, 2,  179.90),
    (7,  'Arroz Integral 5kg',                3, 3,   22.90),
    (8,  'Café Moído Premium 500g',           3, 3,   34.90),
    (9,  'Azeite de Oliva Extra Virgem 500ml',3, 3,   45.00),
    (10, 'Python para Iniciantes',            4, 3,   79.90),
    (11, 'Caderno Universitário 200fls',      4, 3,   24.90),
    (12, 'Mesa de Escritório Ergonômica',     5, 5,  599.00),
    (13, 'Luminária LED de Mesa',             5, 5,   89.90),
    (14, 'Bicicleta 21 Marchas Alumínio',     6, 4, 1299.00),
    (15, 'Protetor Solar FPS50 200ml',        7, 5,   49.90),
])

# Clientes
cursor.executemany("INSERT INTO cliente VALUES (?, ?, ?, ?, ?)", [
    (1, 'João Carlos Silva',        '12345678901', 'M', '1985-03-15'),
    (2, 'Maria Aparecida Souza',    '23456789012', 'F', '1990-07-22'),
    (3, 'Carlos Eduardo Oliveira',  '34567890123', 'M', '1978-11-08'),
    (4, 'Ana Paula Santos',         '45678901234', 'F', '1995-01-30'),
    (5, 'Pedro Henrique Lima',      '56789012345', 'M', '1988-06-12'),
    (6, 'Fernanda Costa Melo',      '67890123456', 'F', '1992-09-25'),
    (7, 'Roberto Alves Pereira',    '78901234567', 'M', '1982-04-18'),
    (8, 'Juliana Ferreira Ramos',   '89012345678', 'F', '1997-12-05'),
])

# Endereços (um por cliente)
cursor.executemany("INSERT INTO endereco VALUES (?, ?, ?, ?, ?, ?, ?)", [
    (1, 1, 1,  'Avenida Paulista',        '1000', 'Bela Vista',      '01310-100'),
    (2, 2, 4,  'Rua Copacabana',          '200',  'Copacabana',      '22020-001'),
    (3, 3, 6,  'Rua Amazonas',            '350',  'Savassi',         '30180-000'),
    (4, 4, 10, 'Rua XV de Novembro',      '500',  'Centro',          '80020-310'),
    (5, 5, 8,  'Avenida Ipiranga',        '750',  'Jardim Botânico', '90160-090'),
    (6, 6, 2,  'Rua Barão de Campinas',   '120',  'Centro',          '13010-040'),
    (7, 7, 12, 'Avenida Hercílio Luz',    '300',  'Centro',          '88020-000'),
    (8, 8, 13, 'Rua Chile',               '100',  'Comércio',        '40020-000'),
])

# Telefones
cursor.executemany("INSERT INTO telefone VALUES (?, ?, ?, ?)", [
    (1,  1, '11987654321', 'Celular'),
    (2,  1, '1133334444',  'Residencial'),
    (3,  2, '21998765432', 'Celular'),
    (4,  3, '31987654321', 'Celular'),
    (5,  4, '41996543210', 'Celular'),
    (6,  5, '51987654321', 'Celular'),
    (7,  5, '5133332222',  'Residencial'),
    (8,  6, '19987654321', 'Celular'),
    (9,  7, '48987654321', 'Celular'),
    (10, 8, '71987654321', 'Celular'),
])

# Pedidos
cursor.executemany("INSERT INTO pedido VALUES (?, ?, ?, ?)", [
    (1,  1, '2023-03-10', 'Entregue'),
    (2,  2, '2023-04-15', 'Entregue'),
    (3,  3, '2023-05-20', 'Entregue'),
    (4,  4, '2023-06-08', 'Entregue'),
    (5,  5, '2023-07-22', 'Entregue'),
    (6,  6, '2023-08-14', 'Entregue'),
    (7,  7, '2023-09-05', 'Entregue'),
    (8,  8, '2023-10-18', 'Entregue'),
    (9,  1, '2023-11-25', 'Entregue'),
    (10, 3, '2024-01-12', 'Entregue'),
    (11, 2, '2024-02-28', 'Entregue'),
    (12, 5, '2024-03-15', 'Entregue'),
    (13, 4, '2024-04-20', 'Entregue'),
    (14, 7, '2024-05-08', 'Entregue'),
    (15, 6, '2024-06-30', 'Em Processamento'),
])

# Itens dos pedidos
cursor.executemany("INSERT INTO item_pedido VALUES (?, ?, ?, ?, ?, ?)", [
    (1,  1,  1,  1, 1299.90,   0.00),  # pedido 1: smartphone
    (2,  1,  3,  2,  199.90,  20.00),  # pedido 1: 2 fones c/ desconto
    (3,  2,  5,  1,  349.90,   0.00),  # pedido 2: tênis
    (4,  2,  10, 1,   79.90,   0.00),  # pedido 2: livro python
    (5,  3,  2,  1, 2899.90, 200.00),  # pedido 3: notebook c/ desconto
    (6,  3,  13, 2,   89.90,   0.00),  # pedido 3: 2 luminárias
    (7,  4,  7,  3,   22.90,   0.00),  # pedido 4: 3 arrozes
    (8,  4,  8,  2,   34.90,   5.00),  # pedido 4: 2 cafés c/ desconto
    (9,  5,  14, 1, 1299.00, 100.00),  # pedido 5: bicicleta c/ desconto
    (10, 6,  12, 1,  599.00,   0.00),  # pedido 6: mesa
    (11, 6,  13, 2,   89.90,   0.00),  # pedido 6: 2 luminárias
    (12, 7,  4,  3,   89.90,  15.00),  # pedido 7: 3 camisetas c/ desconto
    (13, 7,  6,  1,  179.90,   0.00),  # pedido 7: jaqueta
    (14, 8,  15, 2,   49.90,   0.00),  # pedido 8: 2 protetores solares
    (15, 8,  11, 3,   24.90,   0.00),  # pedido 8: 3 cadernos
    (16, 9,  1,  1, 1299.90,   0.00),  # pedido 9: smartphone
    (17, 9,  3,  1,  199.90,   0.00),  # pedido 9: fone
    (18, 10, 2,  1, 2899.90, 300.00),  # pedido 10: notebook c/ desconto
    (19, 10, 8,  3,   34.90,   0.00),  # pedido 10: 3 cafés
    (20, 11, 5,  2,  349.90,  50.00),  # pedido 11: 2 tênis c/ desconto
    (21, 12, 14, 1, 1299.00,   0.00),  # pedido 12: bicicleta
    (22, 12, 9,  2,   45.00,   0.00),  # pedido 12: 2 azeites
    (23, 13, 7,  5,   22.90,  10.00),  # pedido 13: 5 arrozes c/ desconto
    (24, 13, 10, 1,   79.90,   0.00),  # pedido 13: livro
    (25, 14, 2,  1, 2899.90,   0.00),  # pedido 14: notebook
    (26, 14, 3,  2,  199.90,  30.00),  # pedido 14: 2 fones c/ desconto
    (27, 15, 6,  1,  179.90,   0.00),  # pedido 15: jaqueta
    (28, 15, 15, 3,   49.90,   0.00),  # pedido 15: 3 protetores solares
])

conn.commit()
print("Dados inseridos com sucesso em todas as tabelas.")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Listar tabelas do banco de dados

# COMMAND ----------

tabelas = cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name").fetchall()
tabelas = [t[0] for t in tabelas]
print(f"Tabelas encontradas ({len(tabelas)}): {tabelas}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Extrair cada tabela e gravar como CSV no Volume `landing/dados`
# MAGIC
# MAGIC O processo para cada tabela:
# MAGIC 1. Executar `SELECT * FROM tabela` no SQLite
# MAGIC 2. Converter resultado em Spark DataFrame
# MAGIC 3. Gravar no Volume como CSV com cabeçalho

# COMMAND ----------

import pandas as pd

caminho_landing = '/Volumes/workspace/landing/dados'

for nome_tabela in tabelas:
    # Extrai a tabela do SQLite via pandas
    df_pandas = pd.read_sql_query(f"SELECT * FROM {nome_tabela}", conn)

    # Converte para Spark DataFrame
    df_spark = spark.createDataFrame(df_pandas)

    # Grava como CSV no Volume (sobrescreve se existir)
    (df_spark
        .coalesce(1)
        .write
        .mode("overwrite")
        .option("header", "true")
        .option("encoding", "UTF-8")
        .csv(f"{caminho_landing}/{nome_tabela}_temp")
    )

    # Renomeia o arquivo gerado para o nome da tabela
    arquivos = [f.path for f in dbutils.fs.ls(f"{caminho_landing}/{nome_tabela}_temp") if f.name.endswith('.csv')]
    dbutils.fs.mv(arquivos[0], f"{caminho_landing}/{nome_tabela}.csv")
    dbutils.fs.rm(f"{caminho_landing}/{nome_tabela}_temp", recurse=True)

    linhas = df_pandas.shape[0]
    colunas = df_pandas.shape[1]
    print(f"[OK] {nome_tabela}.csv  →  {linhas} linhas, {colunas} colunas")

conn.close()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. Confirmar arquivos gerados no Volume

# COMMAND ----------

display(dbutils.fs.ls(caminho_landing))

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Validação: pré-visualizar cada arquivo CSV

# COMMAND ----------

for nome_tabela in tabelas:
    print(f"\n{'='*50}")
    print(f"Tabela: {nome_tabela}")
    print('='*50)
    df = spark.read.option("header", "true").csv(f"{caminho_landing}/{nome_tabela}.csv")
    df.show(3, truncate=True)
