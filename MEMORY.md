# Memória do projeto — fast-analysis

Última atualização: 13/10/2026

Este arquivo preserva o contexto técnico e as decisões do projeto entre sessões. Não registrar aqui credenciais, connection strings reais, dados corporativos ou exports.

## Objetivo

Ambiente **local** para análises operacionais rápidas. O primeiro caso de uso será a distribuição de brindes de Natal. A solução deve continuar simples, confiável e orientada a aprendizado — não é um BI corporativo, aplicação web, plataforma distribuída nem data lake.

## Arquitetura em vigor

```text
SQL Server -- ODBC Driver / pyodbc -- SQLAlchemy -- Python
                                                   |
                                                   v
                                       DuckDB local (raw -> analytics)
                                                   |
                                                   v
                                    Jupyter / SQL / Polars / CSV / Excel
```

- **Fonte inicial:** SQL Server.
- **Extração:** consulta `SELECT` definida em arquivo `.sql`.
- **Atualização:** micro-full refresh; cada refresh substitui a tabela RAW da fonte configurada.
- **Análise:** deve ocorrer preferencialmente no DuckDB local após o refresh, não no banco operacional.
- **Modelagem de negócio:** ainda não criada deliberadamente; depende do primeiro conjunto real de dados.

## Ambiente e dependências

- Windows, PowerShell, VS Code e Git.
- Gerenciador de ambiente/pacotes: `uv` (confirmado instalado).
- Python do projeto: 3.11.11, localizado e gerenciado pelo `uv`.
- ODBC Driver 17 e 18 para SQL Server estão disponíveis em 32 e 64 bits; o exemplo usa ODBC Driver 18.
- Dependências registradas em `pyproject.toml` e bloqueadas em `uv.lock`:
  - DuckDB;
  - Polars;
  - PyArrow (necessário para a carga direta Polars → DuckDB);
  - SQLAlchemy;
  - pyodbc;
  - python-dotenv;
  - JupyterLab;
  - XlsxWriter.

## O que foi implementado

| Área | Estado | Local |
| --- | --- | --- |
| Projeto Python instalável e CLI | Pronto | `pyproject.toml`, `src/fast_analysis/cli.py` |
| Configuração por variáveis de ambiente | Pronto | `.env.example`, `src/fast_analysis/config.py` |
| Extração de SQL Server | Pronta, aguarda dados reais | `src/fast_analysis/refresh.py` |
| DuckDB com schemas `raw`, `analytics`, `audit` | Pronto | `src/fast_analysis/warehouse.py` |
| Refresh e log de execução | Pronto | `audit.refresh_log` |
| Validações básicas | Prontas | contagem, nulos e duplicidades da chave opcional |
| Exportação CSV/Excel | Pronta | comando `fast-analysis export` |
| Notebook inicial | Pronto | `notebooks/01_operacao.ipynb` |
| Teste automatizado local | Pronto e aprovado | `tests/test_warehouse.py` |
| Modelo analítico do negócio | Pendente | depende da fonte real |

## Como a solução funciona

1. O usuário configura `.env` com a conexão e os nomes locais.
2. O usuário escreve uma consulta de leitura em `sql/sqlserver/operacao.sql`.
3. `uv run fast-analysis refresh` abre a conexão pela cadeia SQLAlchemy → pyodbc, executa a consulta e traz o resultado a um DataFrame Polars.
4. O DataFrame substitui `raw.<FA_SOURCE_NAME>` no arquivo `data/fast_analysis.duckdb`.
5. A view `analytics.vw_<FA_SOURCE_NAME>` é recriada apontando para a RAW.
6. Validações são exibidas e o resultado do refresh é gravado em `audit.refresh_log`.
7. Notebooks, SQL analítico e exports trabalham sobre o DuckDB local.

## Comandos operacionais

```powershell
# Sincroniza o ambiente após alterações nas dependências.
uv sync

# Executa a extração e atualização local.
uv run fast-analysis refresh

# Lista objetos do DuckDB e os últimos refreshes.
uv run fast-analysis inspect

# Abre o ambiente de notebooks.
uv run jupyter lab

# Exporta o resultado de um arquivo SQL executado no DuckDB.
uv run fast-analysis export --query sql/analytics/exemplo_resumo.sql --name resumo --format xlsx

# Executa a validação automatizada atual.
uv run python -m unittest discover -s tests -v
```

## Configuração pendente do usuário

Antes do primeiro refresh real:

1. Copiar `.env.example` para `.env`.
2. Preencher `SQLSERVER_URL` com a conexão real, mantendo o arquivo fora do Git.
3. Escolher um nome curto e seguro para `FA_SOURCE_NAME`.
4. Editar `sql/sqlserver/operacao.sql` com um `SELECT` estritamente de leitura.
5. Preencher `FA_PRIMARY_KEY` se houver chave natural confiável para validação.
6. Executar o primeiro `refresh` e revisar número de registros e validações.

## Pendências por prioridade

### Próxima sessão — após a primeira fonte real

1. Entender a origem: schema, entidades, volume, período, frequência de atualização e regras da operação.
2. Revisar a consulta de extração para limitar período e colunas ao necessário.
3. Validar contagens entre SQL Server e DuckDB; confirmar chaves nulas, duplicadas e tipos de data.
4. Definir explicitamente o grão da análise e só então criar dimensões, fatos, views ou marts necessários.
5. Criar consultas analíticas e evoluir o notebook com indicadores reais.

### Posteriormente, apenas se houver necessidade comprovada

- Novas fontes: MySQL ou PostgreSQL, cada uma com seu driver instalado somente quando entrar em uso.
- Agendamento local de refresh.
- Exportações padronizadas recorrentes.
- Parquet, dbt, camada de métricas ou agente de IA — somente se resolverem um problema observado.

## Regras e decisões que não devem ser esquecidas

- Nunca versionar `.env`, credenciais, dados corporativos, banco DuckDB local ou exports descartáveis.
- Não executar consultas exploratórias repetidas contra a origem depois que a RAW local estiver atualizada.
- Não criar ORM, repositórios, serviços genéricos, Spark, Airflow, Docker, Kafka, Kubernetes ou dashboards sem necessidade real.
- SQLAlchemy padroniza conexão, mas não unifica dialetos SQL; SQL específico de SQL Server pode permanecer em `sql/sqlserver/`.
- Preferir DuckDB para joins, filtros, agregações e janelas; usar Polars quando transformações programáticas em DataFrame forem mais naturais.
- Evitar criar fatos, dimensões e métricas antes de conhecer o domínio e os dados reais.

## Validações realizadas

Em 11/10/2026, foram aprovados:

- `uv run python -m unittest discover -s tests -v`;
- validação estrutural do notebook;
- `uv lock --check`;
- execução da ajuda da CLI `fast-analysis --help`.

Não houve conexão com banco corporativo nem uso de credenciais reais durante a implementação.
