# 005 - Gold: Modelo Dimensional (Kimball)

## Objetivo

Ler as tabelas da camada Silver e construir o **modelo dimensional** no schema `workspace.gold`, seguindo a metodologia de **Ralph Kimball**.

O modelo Gold é otimizado para consumo por ferramentas de BI (Power BI, Tableau, Looker) e consultas analíticas.

## Schema Estrela criado

```
               dim_tempo
              (FK_TEMPO)
                   │
                   │
dim_produto ── fato_vendas ── dim_localidade
(FK_PRODUTO)        │           (FK_LOCALIDADE)
                    │
               dim_cliente
              (FK_CLIENTE)
```

## Dimensões

### `dim_produto`

Criada via **MERGE INTO** (SCD Tipo 1) a partir de um join entre `silver.produto`, `silver.categoria` e `silver.fornecedor`.
Desnormaliza a hierarquia de produto em uma única dimensão, eliminando joins em tempo de consulta.

```sql
WITH produto_relacional AS (
    SELECT p.codigo_produto, p.nome_produto,
           c.nome_categoria, f.nome_fornecedor, p.valor_preco
    FROM produto p
    INNER JOIN categoria c ON p.codigo_categoria = c.codigo_categoria
    INNER JOIN fornecedor f ON p.codigo_fornecedor = f.codigo_fornecedor
)
MERGE INTO gold.dim_produto AS d
USING produto_relacional AS r ON d.codigo_produto = r.codigo_produto
WHEN MATCHED AND (...) THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT (codigo_produto, nome_produto, ...)
```

### `dim_cliente`

Criada via **MERGE INTO** (SCD Tipo 1) a partir de `silver.cliente`.

### `dim_localidade`

Criada via **MERGE INTO** a partir de um join entre `silver.municipio`, `silver.estado` e `silver.regiao`.

### `dim_tempo`

Criada **programaticamente** em Python/Spark. Gera um calendário completo de 2023 a 2026.

## Tabela Fato: `fato_vendas`

### Grain (granularidade)

Um registro por combinação de **(data do pedido, produto, cliente, localidade)**.

### Colunas

| Coluna | Tipo | Descrição |
|---|---|---|
| `FK_TEMPO` | Date | Chave estrangeira → `dim_tempo.Data` |
| `FK_PRODUTO` | Int | Chave estrangeira → `dim_produto.SK_PRODUTO` |
| `FK_CLIENTE` | Int | Chave estrangeira → `dim_cliente.SK_CLIENTE` |
| `FK_LOCALIDADE` | Int | Chave estrangeira → `dim_localidade.SK_LOCALIDADE` |
| `QT_ITENS` | Int | Quantidade total de itens vendidos |
| `VL_TOTAL` | Double | Receita bruta (`valor_unitario × quantidade`) |
| `VL_DESCONTO` | Double | Total de descontos concedidos |

### Processo de carga

```sql
WITH pedido_endereco AS (
    SELECT p.codigo_pedido, p.codigo_cliente,
           p.data_pedido, e.codigo_municipio
    FROM pedido p INNER JOIN endereco e ON p.codigo_cliente = e.codigo_cliente
)
INSERT INTO gold.fato_vendas
SELECT dtem.data, dp.sk_produto, dc.sk_cliente, dl.sk_localidade,
       SUM(ip.quantidade_quantidade)                         AS QT_ITENS,
       SUM(ip.valor_unitario * ip.quantidade_quantidade)     AS VL_TOTAL,
       SUM(ip.valor_desconto)                                AS VL_DESCONTO
FROM item_pedido ip
     INNER JOIN pedido_endereco  pe   ON ip.codigo_pedido   = pe.codigo_pedido
     INNER JOIN gold.dim_produto dp   ON ip.codigo_produto  = dp.codigo_produto
     INNER JOIN gold.dim_cliente dc   ON pe.codigo_cliente  = dc.codigo_cliente
     INNER JOIN gold.dim_localidade dl ON pe.codigo_municipio = dl.codigo_municipio
     INNER JOIN gold.dim_tempo    dtem ON pe.data_pedido    = dtem.data
GROUP BY dtem.data, dp.sk_produto, dc.sk_cliente, dl.sk_localidade
```

## Consulta analítica de exemplo

```sql
-- Receita por mês e categoria de produto
SELECT t.NomeMes, t.Ano, p.NOME_CATEGORIA,
       SUM(f.QT_ITENS)    AS total_itens,
       SUM(f.VL_TOTAL)    AS receita_bruta,
       SUM(f.VL_DESCONTO) AS total_descontos,
       SUM(f.VL_TOTAL - f.VL_DESCONTO) AS receita_liquida
FROM gold.fato_vendas f
INNER JOIN gold.dim_tempo      t ON f.FK_TEMPO    = t.Data
INNER JOIN gold.dim_produto    p ON f.FK_PRODUTO  = p.SK_PRODUTO
GROUP BY t.NomeMes, t.Ano, t.Mes, p.NOME_CATEGORIA
ORDER BY t.Ano, t.Mes, p.NOME_CATEGORIA;
```
