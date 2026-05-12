# Databricks Free Edition

## O que é o Databricks?

O **Databricks** é uma plataforma unificada de dados e IA construída sobre o Apache Spark. Ele combina engenharia de dados, ciência de dados e análise em um único ambiente colaborativo baseado em notebooks.

### Principais componentes

| Componente           | Descrição                                                              |
| -------------------- | ---------------------------------------------------------------------- |
| **Workspace**        | Ambiente de desenvolvimento com notebooks, repositórios e clusters     |
| **Unity Catalog**    | Governança centralizada de dados (catálogo, schemas, tabelas, volumes) |
| **Delta Lake**       | Formato de armazenamento transacional (ACID) sobre object storage      |
| **Workflows / Jobs** | Orquestração de pipelines de dados                                     |
| **SQL Warehouse**    | Endpoints SQL para consultas analíticas                                |

---

## Databricks Free Edition

O **Databricks Free Edition** oferece acesso gratuito à plataforma para aprendizado e experimentação.

### Recursos disponíveis no Free Edition

- Clusters de computação (com limitações de recursos)
- Unity Catalog com catálogo `workspace`
- Delta Lake e Delta Sharing
- Jobs & Workflows
- Notebooks Python, SQL, Scala e R
- Repositórios Git integrados

### Como criar uma conta

1. Acesse [databricks.com/br/learn/free-edition](https://www.databricks.com/br/learn/free-edition/)
2. Clique em **"Começar de graça"**
3. Preencha o formulário com nome, e-mail e senha
4. Confirme o e-mail
5. Selecione o provedor de cloud (AWS, Azure ou GCP) — o Free Edition usa infraestrutura gerenciada pela Databricks

---

## Unity Catalog: nomenclatura de três níveis

O Unity Catalog usa uma hierarquia de **catálogo → schema → tabela/volume**:

```
workspace                   ← catálogo (padrão no Free Edition)
├── landing                 ← schema
│   └── dados               ← volume (armazena arquivos)
├── bronze                  ← schema
│   ├── pedido              ← tabela Delta
│   └── ...
├── silver                  ← schema
│   └── ...
└── gold                    ← schema
    └── ...
```

### Acessar arquivos em um Volume

```python
# Listar arquivos no Volume
dbutils.fs.ls('/Volumes/workspace/landing/dados/')

# Ler CSV do Volume
df = spark.read.csv('/Volumes/workspace/landing/dados/pedido.csv', header=True)
```

---

## Clusters

Um **cluster** é um conjunto de máquinas virtuais que executam o código Spark. No Free Edition, o cluster é criado automaticamente (serverless) ou pode ser configurado manualmente.

### Tipos de cluster no Free Edition

| Tipo            | Uso                                                       |
| --------------- | --------------------------------------------------------- |
| **Serverless**  | Iniciado automaticamente, sem necessidade de configuração |
| **All-Purpose** | Criado manualmente, persiste entre sessões                |
| **Job Cluster** | Criado e destruído automaticamente ao executar um Job     |
