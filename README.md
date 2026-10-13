# fast-analysis

Ambiente local para extrair dados operacionais de SQL Server, persistir uma cópia analítica no DuckDB e analisá-la com SQL, Polars e Jupyter.

## Fluxo

```text
SQL Server --pyodbc--> SQLAlchemy --Python--> DuckDB (raw --> analytics) --> Notebook / CSV / Excel
```

O banco operacional é acessado somente pelo `refresh`. Depois disso, consultas exploratórias devem usar o DuckDB local.

## Configuração inicial

1. Copie `.env.example` para `.env` e preencha `SQLSERVER_URL`.
2. Edite `sql/sqlserver/operacao.sql` com uma consulta `SELECT` de leitura.
3. Defina `FA_SOURCE_NAME`; ele será usado como `raw.<nome>` e `analytics.vw_<nome>`.
4. Opcionalmente informe `FA_PRIMARY_KEY` para validar nulos e duplicidades.
5. Confirme que o Microsoft ODBC Driver 18 for SQL Server está instalado. Se usar outro driver, altere apenas `driver` na URL.

Credenciais ficam exclusivamente em `.env`, que é ignorado pelo Git.

## Operação diária

```powershell
uv run fast-analysis refresh
uv run fast-analysis inspect
uv run jupyter lab
```

`refresh` executa a consulta na origem, substitui `raw.<nome>` (micro-full refresh), recria `analytics.vw_<nome>`, registra o resultado em `audit.refresh_log` e exibe validações. Uma falha de conexão ou consulta não substitui a RAW existente.

## Análise e exportação

Crie SQL analítico em `sql/analytics/`, consultando a view `analytics.vw_<nome>`. Para gerar um arquivo:

```powershell
uv run fast-analysis export --query sql/analytics/exemplo_resumo.sql --name resumo --format csv
uv run fast-analysis export --query sql/analytics/exemplo_resumo.sql --name resumo --format xlsx
```

Os arquivos vão para `exports/` e não são versionados. O notebook inicial está em `notebooks/01_operacao.ipynb`.

## Camadas

| Camada | Finalidade |
| --- | --- |
| `raw` | Cópia próxima do resultado extraído da origem. |
| `analytics` | Views e tabelas tratadas para consumo. Inicialmente, uma view espelha a RAW sem regra de negócio. |
| `audit` | Histórico de refreshes locais. |
| `mart` | Não criado ainda; só entra quando houver métricas reutilizáveis e entendimento do negócio. |

Depois do primeiro refresh real, defina o grão, as chaves e as métricas da operação. Então crie as views ou tabelas analíticas apropriadas, sem adivinhar regras de negócio agora.
