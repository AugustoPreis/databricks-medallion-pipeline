# Databricks Medallion Pipeline

Pipeline de dados completo implementado no **Databricks Free Edition**, seguindo a **Arquitetura Medalhão** (Landing → Bronze → Silver → Gold) com modelagem dimensional segundo **Ralph Kimball**.

---

## Descrição do Projeto

Este projeto extrai dados de um banco de dados relacional (**SQLite**), processa-os através de quatro camadas e os disponibiliza em um modelo dimensional pronto para consumo analítico (BI).

**Domínio:** E-commerce / Vendas Online  
**Tabelas de origem:** 11 (categoria, cliente, endereco, estado, fornecedor, item_pedido, municipio, pedido, produto, regiao, telefone)

### Arquitetura

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Databricks Free Edition                      │
│                                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────────┐   │
│  │ LANDING  │    │  BRONZE  │    │  SILVER  │    │     GOLD     │   │
│  │          │    │          │    │          │    │              │   │
│  │ SQLite   │───►│ Delta    │───►│ Delta    │───►│ Delta        │   │
│  │ ──► CSV  │    │ Lake     │    │ Lake +   │    │ Dimensional  │   │
│  │  (Volume)│    │ (raw)    │    │ DQ       │    │ (Kimball)    │   │
│  └──────────┘    └──────────┘    └──────────┘    └──────────────┘   │
│                                                                      │
│  workspace.landing.dados   workspace.bronze   workspace.silver       │
│                                               workspace.gold         │
└──────────────────────────────────────────────────────────────────────┘
```

### Modelo Dimensional (Gold)

```
               dim_tempo
                   │
dim_produto ── fato_vendas ── dim_localidade
                   │
              dim_cliente
```

---

## Pré-Requisitos

- Conta no [Databricks Free Edition](https://www.databricks.com/br/learn/free-edition/)
- Python 3.8+ (para documentação MkDocs local)
- Git

---

## Estrutura de Pastas

```
databricks-medallion-pipeline/
├── notebooks/
│   ├── 001-preparando-ambiente.py
│   ├── 002-lakehouse-landing.py
│   ├── 003-lakehouse-bronze.py
│   ├── 004-lakehouse-silver.py
│   ├── 005-lakehouse-gold.py
│   └── 006-destruindo-ambiente.py
├── docs/
│   ├── index.md
│   ├── introducao/
│   │   ├── databricks.md
│   │   ├── arquitetura-medalhao.md
│   │   ├── delta-lake.md
│   │   └── kimball.md
│   ├── notebooks/
│   │   ├── landing.md
│   │   ├── bronze.md
│   │   ├── silver.md
│   │   └── gold.md
│   └── jobs.md
├── mkdocs.yml
├── requirements-docs.txt
├── README.md
└── LICENSE
```

---

## Como Rodar

### 1. Clonar o repositório

```bash
git clone https://github.com/AugustoPreis/databricks-medallion-pipeline.git
```

### 2. Configurar o Databricks

1. Acesse [Databricks Free Edition](https://www.databricks.com/br/learn/free-edition/) e faça login
2. No menu lateral, vá em **Workspace** → **Create** → **Git folder**
3. Cole a URL do seu repositório e confirme

### 3. Executar os notebooks (manualmente)

Execute na ordem numérica dentro de **Workspace → seu-repositório → notebooks**:

| #   | Notebook            | O que faz                                               |
| --- | ------------------- | ------------------------------------------------------- |
| 001 | Preparando Ambiente | Cria schemas (landing, bronze, silver, gold) e o Volume |
| 002 | Landing             | Extrai dados do SQLite e grava CSVs no Volume           |
| 003 | Bronze              | Lê CSVs e grava em Delta Lake no schema bronze          |
| 004 | Silver              | Aplica Data Quality e grava no schema silver            |
| 005 | Gold                | Cria modelo dimensional no schema gold                  |
| 006 | Destruindo Ambiente | Remove todos os schemas (limpeza)                       |

### 4. Executar via Job (encadeado)

1. No Databricks, acesse **Workflows** → **Jobs** → **Create Job**
2. Crie uma tarefa para cada notebook na ordem acima
3. Configure cada tarefa como dependente da anterior (**"Depends on"**)
4. Configure o cluster (pode ser o cluster default do Free Edition)
5. Clique em **Run now**

> Para instruções detalhadas sobre configuração do Job, consulte a [documentação MkDocs](docs/jobs.md).

### 5. Visualizar a documentação MkDocs localmente

```bash
pip install -r requirements-docs.txt
mkdocs serve
```

Acesse `http://127.0.0.1:8000` no navegador.

---

## Camadas da Arquitetura Medalhão

### Landing

- **Origem:** Banco de dados SQLite em memória (domínio de e-commerce / vendas online)
- **Destino:** `/Volumes/workspace/landing/dados/*.csv`
- **Formato:** CSV com cabeçalho, encoding UTF-8

### Bronze

- **Origem:** CSVs da Landing Zone
- **Destino:** `workspace.bronze.*` (Delta Lake, Managed)
- **Transformações:** Adição de colunas de auditoria (`data_hora_bronze`, `nome_arquivo`)

### Silver

- **Origem:** `workspace.bronze.*`
- **Destino:** `workspace.silver.*` (Delta Lake, Managed)
- **Data Quality:**
  - Deduplicação de linhas
  - Remoção de nulos em colunas-chave (PK/FK)
  - Casting de tipos (datas como `DateType`, numéricos como `IntegerType`/`DoubleType`)
  - Padronização de nomes de colunas (UPPER_SNAKE_CASE, prefixos expandidos)

### Gold

- **Origem:** `workspace.silver.*`
- **Destino:** `workspace.gold.*` (Delta Lake, Managed)
- **Modelo:** Dimensional (Ralph Kimball) com tabelas de dimensão e fato

| Tabela           | Tipo              | Descrição                                         |
| ---------------- | ----------------- | ------------------------------------------------- |
| `dim_produto`    | Dimensão (SCD1)   | Produtos com categoria e fornecedor               |
| `dim_cliente`    | Dimensão (SCD1)   | Compradores                                       |
| `dim_localidade` | Dimensão (SCD1)   | Municípios, estados e regiões                     |
| `dim_tempo`      | Dimensão estática | Calendário 2023–2026                              |
| `fato_vendas`    | Fato              | Vendas por dia, produto, cliente e localidade     |

---

## Referências

- [Databricks Free Edition](https://www.databricks.com/br/learn/free-edition/)
- [Arquitetura Medalhão](https://www.databricks.com/glossary/medallion-architecture)
- [Delta Lake](https://docs.delta.io/)
- [Jobs & Workflows no Databricks](https://docs.databricks.com/workflows/jobs/index.html)
- [Unity Catalog](https://docs.databricks.com/data-governance/unity-catalog/index.html)
- [Modelagem Dimensional — Ralph Kimball](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/)
- [MkDocs](https://www.mkdocs.org/) | [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/)
- [Repositório do Professor](https://github.com/jlsilva01/databricks-free-edition)
