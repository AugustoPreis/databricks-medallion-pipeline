# Jobs & Pipelines

## O que é uma Job no Databricks?

Uma **Job** no Databricks é uma forma de executar notebooks (ou scripts) de maneira automatizada e encadeada. Cada etapa do pipeline é configurada como uma **Task** dentro da Job, com dependências definidas entre elas.

## Pipeline deste projeto

```
Task 1              Task 2             Task 3
Preparando   ──►   Landing     ──►    Bronze
Ambiente

    Task 4             Task 5
    Silver   ──►       Gold
```

Cada task só é iniciada após a conclusão bem-sucedida da task anterior.

---

## Como criar a Job no Databricks

### Passo 1: Acessar Workflows

No menu lateral do Databricks, clique em **Workflows** → aba **Jobs** → botão **Create job**.

### Passo 2: Configurar a primeira task (001 - Preparando Ambiente)

1. **Task name:** `01-preparando-ambiente`
2. **Type:** Notebook
3. **Source:** Workspace (ou Git, se configurou o repositório Git)
4. **Path:** Selecione o notebook `001 - Atifidade Pratica - Lakehouse - Preparando ambiente`
5. **Cluster:** Selecione o cluster default ou crie um novo
6. Clique em **Create task**

### Passo 3: Adicionar as demais tasks

Clique em **Add task** e repita para cada notebook:

| Task name                | Notebook                  | Depends on               |
| ------------------------ | ------------------------- | ------------------------ |
| `01-preparando-ambiente` | 001 - Preparando Ambiente | —                        |
| `02-landing`             | 002 - Landing             | `01-preparando-ambiente` |
| `03-bronze`              | 003 - Bronze              | `02-landing`             |
| `04-silver`              | 004 - Silver              | `03-bronze`              |
| `05-gold`                | 005 - Gold                | `04-silver`              |

Para configurar a dependência ("Depends on"):

1. Ao adicionar uma nova task, procure o campo **Depends on**
2. Selecione a task anterior na lista

### Passo 4: Executar o pipeline

1. Clique em **Run now** para executar imediatamente
2. Ou configure um **Schedule** para execução automática (cron)

---

## Monitoramento da execução

Após iniciar o Job, acesse a aba **Runs** para acompanhar:

- **Status de cada task:** Pending, Running, Succeeded, Failed
- **Logs de execução:** clique na task para ver o output do notebook
- **Duração:** tempo de execução de cada etapa
- **Erros:** mensagens de erro caso alguma task falhe

### Exemplo de execução bem-sucedida

```
✓ 01-preparando-ambiente  (12s)
✓ 02-landing              (45s)
✓ 03-bronze               (38s)
✓ 04-silver               (52s)
✓ 05-gold                 (61s)

Total: 3m 28s
```

---

## Reexecução de tasks

Se uma task falhar, você pode:

1. Corrigir o problema (notebook ou dados)
2. Clicar em **Repair run** para reexecutar apenas as tasks que falharam (sem reiniciar as bem-sucedidas)

---

## Agendamento (Schedule)

Para executar o pipeline periodicamente:

1. Na página da Job, clique em **Add trigger** → **Scheduled**
2. Configure a expressão cron, por exemplo:
   - `0 6 * * *` — todo dia às 06:00
   - `0 6 * * 1` — toda segunda-feira às 06:00
3. Selecione o **Time zone**
4. Clique em **Save**

!!! tip "Databricks Free Edition"
O Free Edition tem limites de execução de Jobs. Verifique os limites da sua conta antes de agendar execuções frequentes.

---

## Boas práticas

- Use **`mode("overwrite")`** em todos os notebooks para garantir idempotência (reexecução segura)
- Configure **alertas de e-mail** em caso de falha: Job → **Edit** → **Notifications**
- Mantenha o notebook **006 - Destruindo Ambiente** fora da Job principal — execute-o apenas manualmente quando necessário
