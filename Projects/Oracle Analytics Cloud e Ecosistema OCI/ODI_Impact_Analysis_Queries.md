# ODI – Análise de Impacto de Migração de Banco de Dados
## Queries para o Repositório ODI (Master + Work Repository)

> **Versão validada:** ODI 12c  
> **Objetivo:** Identificar todos os Scenarios/Jobs que acessam um determinado Data Server, para suportar análise de impacto antes de uma migração de servidor de banco de dados.

---

## PASSO 0 — Verificar tabelas disponíveis no schema

```sql
-- Confirma quais tabelas SNP_ existem no schema conectado
SELECT TABLE_NAME
FROM ALL_TABLES
WHERE TABLE_NAME LIKE 'SNP%'
  AND OWNER = USER
ORDER BY TABLE_NAME;
```

---

## PASSO 1 — Listar todos os Data Servers cadastrados no ODI

Use esta query para identificar o nome exato (`CON_NAME`) do servidor que será migrado.

```sql
-- Rodar no Master Repository
SELECT
    c.I_CONNECT,
    c.CON_NAME      AS data_server,
    c.DSERV_NAME    AS service_name,
    c.JAVA_URL      AS jdbc_url,
    c.USER_NAME     AS db_user
FROM SNP_CONNECT c
ORDER BY c.CON_NAME;
```

---

## PASSO 2 — Data Server + Schemas Físicos

```sql
-- Rodar no Master Repository
SELECT
    c.I_CONNECT,
    c.CON_NAME          AS data_server,
    c.DSERV_NAME        AS service_name,
    c.JAVA_URL          AS jdbc_url,
    c.USER_NAME         AS db_user,
    ps.I_PSCHEMA,
    ps.SCHEMA_NAME      AS physical_schema,
    ps.CATALOG_NAME     AS catalog_name
FROM SNP_CONNECT c
JOIN SNP_PSCHEMA ps ON c.I_CONNECT = ps.I_CONNECT
ORDER BY c.CON_NAME, ps.SCHEMA_NAME;
```

---

## PASSO 3 — Data Server → Physical Schema → Logical Schema → Context

```sql
-- Rodar no Master Repository
SELECT
    c.CON_NAME          AS data_server,
    c.DSERV_NAME        AS service_name,
    c.JAVA_URL          AS jdbc_url,
    ps.SCHEMA_NAME      AS physical_schema,
    ps.CATALOG_NAME     AS catalog_name,
    ctx.CONTEXT_NAME    AS context,
    ctx.CONTEXT_CODE    AS context_code,
    ls.LSCHEMA_NAME     AS logical_schema
FROM SNP_CONNECT        c
JOIN SNP_PSCHEMA        ps  ON c.I_CONNECT     = ps.I_CONNECT
JOIN SNP_PSCHEMA_CONT   pc  ON ps.I_PSCHEMA    = pc.I_PSCHEMA
JOIN SNP_LSCHEMA        ls  ON pc.I_LSCHEMA     = ls.I_LSCHEMA
JOIN SNP_CONTEXT        ctx ON pc.I_CONTEXT     = ctx.I_CONTEXT
WHERE c.CON_NAME = '<NOME_DO_DATA_SERVER>'   -- substitua pelo CON_NAME do PASSO 1
ORDER BY ctx.CONTEXT_NAME, ls.LSCHEMA_NAME;
```

---

## PASSO 4 — Impacto: Scenarios que acessam o Data Server (caminho direto)

Usa `LSCHEMA_NAME` presente diretamente em `SNP_SCEN_STEP` — caminho mais direto e confiável.

```sql
-- Rodar no Work Repository (com acesso ao Master Repository)
SELECT DISTINCT
    c.CON_NAME              AS data_server,
    c.DSERV_NAME            AS service_name,
    ps.SCHEMA_NAME          AS physical_schema,
    ctx.CONTEXT_NAME        AS context,
    ls.LSCHEMA_NAME         AS logical_schema,
    ss.STEP_NAME            AS step_name,
    ss.STEP_TYPE            AS step_type,
    sc.SCEN_NAME            AS scenario,
    sc.SCEN_VERSION         AS version,
    sc.LAST_DATE            AS last_modified
FROM SNP_CONNECT        c
JOIN SNP_PSCHEMA        ps  ON c.I_CONNECT     = ps.I_CONNECT
JOIN SNP_PSCHEMA_CONT   pc  ON ps.I_PSCHEMA    = pc.I_PSCHEMA
JOIN SNP_LSCHEMA        ls  ON pc.I_LSCHEMA     = ls.I_LSCHEMA
JOIN SNP_CONTEXT        ctx ON pc.I_CONTEXT     = ctx.I_CONTEXT
JOIN SNP_SCEN_STEP      ss  ON ls.LSCHEMA_NAME  = ss.LSCHEMA_NAME
JOIN SNP_SCEN           sc  ON ss.SCEN_NO       = sc.SCEN_NO
WHERE c.CON_NAME = '<NOME_DO_DATA_SERVER>'   -- substitua pelo CON_NAME do PASSO 1
ORDER BY sc.SCEN_NAME, sc.SCEN_VERSION, ctx.CONTEXT_NAME;
```

---

## PASSO 5 — Impacto com Model (mais detalhado)

Inclui o nome do Model/Datastore de origem para rastreabilidade completa.

```sql
-- Rodar no Work Repository (com acesso ao Master Repository)
SELECT DISTINCT
    c.CON_NAME              AS data_server,
    c.DSERV_NAME            AS service_name,
    ps.SCHEMA_NAME          AS physical_schema,
    ctx.CONTEXT_NAME        AS context,
    ls.LSCHEMA_NAME         AS logical_schema,
    m.MOD_NAME              AS model,
    m.COD_MOD               AS model_code,
    sc.SCEN_NAME            AS scenario,
    sc.SCEN_VERSION         AS version,
    sc.LAST_DATE            AS last_modified
FROM SNP_CONNECT        c
JOIN SNP_PSCHEMA        ps  ON c.I_CONNECT     = ps.I_CONNECT
JOIN SNP_PSCHEMA_CONT   pc  ON ps.I_PSCHEMA    = pc.I_PSCHEMA
JOIN SNP_LSCHEMA        ls  ON pc.I_LSCHEMA     = ls.I_LSCHEMA
JOIN SNP_CONTEXT        ctx ON pc.I_CONTEXT     = ctx.I_CONTEXT
JOIN SNP_MODEL          m   ON ls.LSCHEMA_NAME  = m.LSCHEMA_NAME
JOIN SNP_SCEN_STEP      ss  ON m.COD_MOD        = ss.MOD_CODE
JOIN SNP_SCEN           sc  ON ss.SCEN_NO       = sc.SCEN_NO
WHERE c.CON_NAME = '<NOME_DO_DATA_SERVER>'   -- substitua pelo CON_NAME do PASSO 1
ORDER BY sc.SCEN_NAME, sc.SCEN_VERSION, m.MOD_NAME;
```

---

## PASSO 6 — Resumo Executivo por Scenario

Para apresentar à equipe o impacto resumido — um Scenario por linha com a lista de Logical Schemas afetados.

```sql
-- Rodar no Work Repository (com acesso ao Master Repository)
SELECT
    sc.SCEN_NAME                                            AS scenario,
    sc.SCEN_VERSION                                         AS version,
    sc.LAST_DATE                                            AS last_modified,
    COUNT(DISTINCT ls.LSCHEMA_NAME)                         AS logical_schemas_impacted,
    COUNT(DISTINCT ps.SCHEMA_NAME)                          AS physical_schemas_impacted,
    LISTAGG(DISTINCT ls.LSCHEMA_NAME, ', ')
        WITHIN GROUP (ORDER BY ls.LSCHEMA_NAME)             AS logical_schemas
FROM SNP_CONNECT        c
JOIN SNP_PSCHEMA        ps  ON c.I_CONNECT     = ps.I_CONNECT
JOIN SNP_PSCHEMA_CONT   pc  ON ps.I_PSCHEMA    = pc.I_PSCHEMA
JOIN SNP_LSCHEMA        ls  ON pc.I_LSCHEMA     = ls.I_LSCHEMA
JOIN SNP_SCEN_STEP      ss  ON ls.LSCHEMA_NAME  = ss.LSCHEMA_NAME
JOIN SNP_SCEN           sc  ON ss.SCEN_NO       = sc.SCEN_NO
WHERE c.CON_NAME = '<NOME_DO_DATA_SERVER>'   -- substitua pelo CON_NAME do PASSO 1
GROUP BY sc.SCEN_NAME, sc.SCEN_VERSION, sc.LAST_DATE
ORDER BY sc.SCEN_NAME, sc.SCEN_VERSION;
```

---

## PASSO 7 — Execuções recentes dos Scenarios impactados (últimos 30 dias)

Valida quais Scenarios estão ativamente em uso no ambiente.

```sql
-- Rodar no Work Repository
-- Substitua os nomes de scenario pelos retornados no PASSO 4 ou 5
SELECT
    sl.SESS_NAME        AS session_name,
    sl.SESS_STATUS      AS status,
    sl.SESS_BEG         AS start_time,
    sl.SESS_END         AS end_time,
    sl.SCEN_NAME        AS scenario,
    sl.SCEN_VERSION     AS version,
    sl.AGENT_NAME       AS agent
FROM SNP_SESSION sl
WHERE sl.SESS_BEG >= SYSDATE - 30
  AND sl.SCEN_NAME IN (
      '<SCENARIO_1>',
      '<SCENARIO_2>'
      -- adicione os cenários identificados nos passos anteriores
  )
ORDER BY sl.SESS_BEG DESC;
```

---

## Referência: Estrutura das Tabelas Validadas

| Tabela | Chave | Coluna de Nome | Observação |
|---|---|---|---|
| SNP_CONNECT | I_CONNECT | CON_NAME | Data Servers. DSERV_NAME = service name, JAVA_URL = JDBC URL |
| SNP_PSCHEMA | I_PSCHEMA | SCHEMA_NAME | Schemas físicos. Liga a SNP_CONNECT via I_CONNECT |
| SNP_PSCHEMA_CONT | — | — | Mapeamento Physical ↔ Logical ↔ Context (I_PSCHEMA, I_LSCHEMA, I_CONTEXT) |
| SNP_LSCHEMA | I_LSCHEMA | LSCHEMA_NAME | Logical Schemas |
| SNP_CONTEXT | I_CONTEXT | CONTEXT_NAME | Contextos ODI (DEV, TEST, PROD, etc.) |
| SNP_MODEL | I_MOD | MOD_NAME | Models/Datastores. Liga a SNP_LSCHEMA via LSCHEMA_NAME |
| SNP_SCEN | SCEN_NO | SCEN_NAME | Scenarios (jobs compilados) |
| SNP_SCEN_STEP | SCEN_NO + NNO | STEP_NAME | Steps do Scenario. Contém LSCHEMA_NAME e MOD_CODE diretamente |

---

## Notas de Execução

- **Master Repository** contém: SNP_CONNECT, SNP_PSCHEMA, SNP_PSCHEMA_CONT, SNP_LSCHEMA, SNP_CONTEXT
- **Work Repository** contém: SNP_MODEL, SNP_SCEN, SNP_SCEN_STEP, SNP_SESSION
- Se Master e Work estiverem em schemas separados, adicione o prefixo de schema nas tabelas (ex: `MASTER_REPO.SNP_CONNECT`)
- Substitua `<NOME_DO_DATA_SERVER>` pelo valor exato da coluna `CON_NAME` retornado no PASSO 1
- A coluna `JAVA_URL` em SNP_CONNECT contém o hostname/IP do servidor — útil para filtrar por IP quando o CON_NAME não for suficiente:  
  `WHERE c.JAVA_URL LIKE '%<HOSTNAME_OU_IP>%'`
