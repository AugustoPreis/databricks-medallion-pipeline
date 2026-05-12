# Databricks Medallion Pipeline

Bem-vindo à documentação do **Databricks Medallion Pipeline** — um projeto de engenharia de dados que demonstra a implementação completa da Arquitetura Medalhão no Databricks Free Edition.

---

## O que este projeto faz

O pipeline extrai dados de um banco de dados relacional (SQLite), os processa através de quatro camadas progressivas de qualidade e os disponibiliza em um modelo dimensional pronto para consumo por ferramentas de BI.

```
Banco de Dados        Landing Zone          Bronze              Silver              Gold
(SQLite)          ────────────────►  ─────────────►  ──────────────►  ─────────────►
Relacional             CSV                Delta             Delta +              Delta
11 tabelas          (Volume)            (raw)            Data Quality          Dimensional
```

---

## Estrutura da Documentação

| Seção                | Conteúdo                                                                      |
| -------------------- | ----------------------------------------------------------------------------- |
| **Introdução**       | Conceitos fundamentais: Databricks, Arquitetura Medalhão, Delta Lake, Kimball |
| **Notebooks**        | Explicação detalhada de cada notebook do pipeline                             |
| **Jobs & Pipelines** | Como encadear os notebooks em uma Job no Databricks                           |

---

## Início Rápido

1. Configure o ambiente: execute o notebook **001 - Preparando Ambiente**
2. Extraia os dados: execute **002 - Landing**
3. Ingira na Bronze: execute **003 - Bronze**
4. Aplique DQ na Silver: execute **004 - Silver**
5. Construa o modelo dimensional: execute **005 - Gold**

Ou configure uma **Job** no Databricks para executar tudo encadeado automaticamente. Veja [Jobs & Pipelines](jobs.md).

---

## Domínio de Negócio

O projeto utiliza dados fictícios do domínio de **e-commerce / vendas online**, com as seguintes entidades:

| Tabela        | Descrição                                              |
| ------------- | ------------------------------------------------------ |
| `regiao`      | Regiões do Brasil                                      |
| `estado`      | Estados brasileiros                                    |
| `municipio`   | Municípios                                             |
| `categoria`   | Categorias de produtos (Eletrônicos, Roupas, etc.)     |
| `fornecedor`  | Fornecedores / distribuidores dos produtos             |
| `produto`     | Produtos disponíveis na loja (nome, preço, categoria)  |
| `cliente`     | Compradores (nome, CPF, data de nascimento)            |
| `endereco`    | Endereços de entrega dos clientes                      |
| `telefone`    | Telefones de contato dos clientes                      |
| `pedido`      | Pedidos realizados (data, status)                      |
| `item_pedido` | Itens de cada pedido (produto, quantidade, preço)      |
