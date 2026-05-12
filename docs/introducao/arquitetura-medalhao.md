# Arquitetura Medalhão

## Conceito

A **Arquitetura Medalhão** (Medallion Architecture) é um padrão de design para organizar dados em um Data Lakehouse. Os dados fluem progressivamente por camadas, onde cada camada aumenta a qualidade, o refinamento e a utilidade dos dados.

O nome vem da analogia com medalhas: Bronze (bruto), Silver (refinado) e Gold (pronto para uso).

```
Fonte de dados
     │
     ▼
┌──────────────────────────────────────────────────────────┐
│  LANDING                                                 │
│  Dados brutos extraídos da fonte (CSV, JSON, Parquet...) │
│  Sem transformações — cópia fiel da origem               │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  BRONZE                                                  │
│  Dados brutos em formato Delta Lake                      │
│  Adição de metadados de ingestão                         │
│  Tipo: Managed Tables                                    │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  SILVER                                                  │
│  Dados limpos e padronizados                             │
│  Data Quality aplicado (dedup, nulos, tipos)             │
│  Nomes de colunas padronizados                           │
└────────────────────────┬─────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────┐
│  GOLD                                                    │
│  Modelo dimensional (Kimball)                            │
│  Dimensões e fatos prontos para BI                       │
│  Alta performance para consultas analíticas              │
└──────────────────────────────────────────────────────────┘
```

---

## Características de cada camada

### Landing Zone

| Aspecto            | Descrição                                                    |
| ------------------ | ------------------------------------------------------------ |
| **Propósito**      | Zona de pouso para dados brutos vindos de sistemas de origem |
| **Formato**        | Arquivos (CSV, JSON, Parquet, Avro...)                       |
| **Transformações** | Nenhuma — preservação fiel da fonte                          |
| **No projeto**     | `/Volumes/workspace/landing/dados/*.csv`                     |

A Landing Zone é equivalente ao "raw zone" em algumas nomenclaturas. Ela garante que os dados originais sempre podem ser reprocessados.

### Camada Bronze

| Aspecto            | Descrição                                                             |
| ------------------ | --------------------------------------------------------------------- |
| **Propósito**      | Ingestão dos arquivos da Landing em Delta Lake                        |
| **Formato**        | Delta Lake (Managed Tables)                                           |
| **Transformações** | Adição de metadados de auditoria (`data_hora_bronze`, `nome_arquivo`) |
| **No projeto**     | `workspace.bronze.*`                                                  |

A Bronze serve como repositório histórico dos dados brutos em formato otimizado para Spark.

### Camada Silver

| Aspecto            | Descrição                                             |
| ------------------ | ----------------------------------------------------- |
| **Propósito**      | Dados limpos, validados e padronizados                |
| **Formato**        | Delta Lake (Managed Tables)                           |
| **Transformações** | Data Quality, renomeação de colunas, casting de tipos |
| **No projeto**     | `workspace.silver.*`                                  |

A Silver é a "versão de verdade" dos dados — confiável o suficiente para consumo por cientistas e engenheiros de dados.

### Camada Gold

| Aspecto            | Descrição                                           |
| ------------------ | --------------------------------------------------- |
| **Propósito**      | Modelo dimensional otimizado para consumo analítico |
| **Formato**        | Delta Lake (Managed Tables)                         |
| **Transformações** | Joins, agregações, criação de dimensões e fatos     |
| **No projeto**     | `workspace.gold.*`                                  |

A Gold é consumida diretamente por ferramentas de BI (Power BI, Tableau, Looker) e pela área de negócio.

---

## Vantagens da Arquitetura Medalhão

- **Rastreabilidade:** dados originais preservados na Landing/Bronze
- **Qualidade progressiva:** cada camada garante um nível de qualidade maior
- **Reprocessamento:** qualquer camada pode ser recriada a partir da anterior
- **Separação de responsabilidades:** cada equipe trabalha na camada adequada
- **Performance:** Gold otimizada para leituras analíticas
