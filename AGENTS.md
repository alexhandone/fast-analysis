# AGENTS.md — fast-analysis

## Propósito deste arquivo

Este documento orienta qualquer agente que trabalhe neste repositório. Ele deve ser atualizado gradualmente conforme o projeto e as decisões técnicas evoluírem.

As instruções deste arquivo valem para todo o repositório, salvo quando um diretório possuir um `AGENTS.md` mais específico.

## Contexto do projeto

O **fast-analysis** é um ambiente local para análises operacionais rápidas, exploratórias e automatizadas. O primeiro caso de uso será uma operação de distribuição de brindes de Natal.

O projeto tem dois objetivos inseparáveis:

1. construir uma solução simples, confiável e organizada;
2. ensinar ao desenvolvedor as tecnologias e decisões envolvidas.

Este não é um sistema corporativo de BI, uma aplicação web ou uma plataforma distribuída de dados.

## Regra central de colaboração

O desenvolvedor deve executar as etapas, configurações e comandos para aprender durante o processo.

O agente deve:

- orientar uma pequena etapa por vez;
- explicar conceitos e decisões antes de apresentar comandos ou código;
- aguardar o desenvolvedor executar e compartilhar o resultado;
- analisar o resultado antes de avançar;
- editar arquivos ou executar comandos de alteração somente quando o desenvolvedor pedir explicitamente ou autorizar claramente;
- poder realizar inspeções somente de leitura quando forem necessárias para entender o estado do projeto, informando antes o que será verificado;
- não concluir várias fases automaticamente.

Quando o desenvolvedor pedir explicitamente que o agente execute uma ação, o agente deve limitar a execução ao escopo solicitado e validar o resultado.

## Formato das etapas de desenvolvimento

Sempre que aplicável, conduzir cada etapa nesta ordem:

1. **Conceito** — explicar o que será aprendido.
2. **Por que estamos usando** — relacionar o conceito ao fast-analysis.
3. **O que faremos agora** — definir uma tarefa pequena e objetiva.
4. **Comando ou código** — fornecer somente o necessário.
5. **Explicação** — explicar comandos, parâmetros e trechos relevantes.
6. **Resultado esperado** — mostrar como reconhecer o sucesso.
7. **Riscos e impacto** — classificar aproximadamente como baixo, moderado ou alto.
8. **Validação** — indicar como confirmar o funcionamento.
9. Aguardar o resultado do desenvolvedor antes de avançar quando houver execução manual.

Evitar entregar longas sequências de comandos de uma só vez.

## Regras para comandos de terminal

Antes de sugerir qualquer comando, explicar:

- o que ele faz;
- seus principais parâmetros;
- o resultado esperado;
- o impacto e os riscos.

Comandos destrutivos ou que removam, substituam ou sobrescrevam dados exigem explicação clara e autorização explícita. Isso também se aplica a comandos que:

- instalam software globalmente;
- alteram o `PATH`;
- modificam Git ou o histórico do repositório;
- alteram bancos de dados;
- apagam tabelas ou arquivos;
- manipulam credenciais.

## Princípios arquiteturais

Prioridades, nesta ordem geral:

1. rapidez para obter respostas;
2. simplicidade operacional;
3. confiabilidade;
4. organização e manutenção;
5. baixo acoplamento;
6. aprendizado;
7. suporte progressivo a múltiplas fontes;
8. evolução futura quando houver necessidade comprovada.

Usar a tecnologia mais simples capaz de resolver corretamente o problema atual. Evitar abstrações prematuras, estruturas vazias e engenharia especulativa.

Não introduzir sem necessidade concreta:

- Spark ou PySpark;
- Airflow;
- Kafka;
- Kubernetes;
- microserviços;
- aplicação web;
- data lake ou lakehouse;
- dashboard corporativo;
- dbt;
- camada semântica;
- agente de IA.

Docker e outras ferramentas adicionais também devem entrar apenas se resolverem um problema real.

## Arquitetura pretendida

Fluxo principal:

```text
SQL Server / MySQL / PostgreSQL
              ↓
     driver específico
              ↓
         SQLAlchemy
              ↓
      extração em Python
              ↓
           DuckDB
        RAW → ANALYTICAL
              ↓
      Jupyter + SQL/Polars
              ↓
         CSV / Excel
```

Stack inicial:

- Python;
- SQLAlchemy Core;
- `pyodbc` para SQL Server;
- DuckDB;
- SQL;
- Jupyter Notebook;
- Polars.

PostgreSQL e MySQL serão adicionados somente quando entrarem efetivamente em uso, com seus respectivos drivers.

## Responsabilidade de cada tecnologia

- **Driver do banco:** realiza a comunicação específica com o SGBD.
- **SQLAlchemy:** fornece engines, conexões e uma interface comum de acesso; não substitui o driver.
- **DuckDB:** é o ponto local de convergência, persistência analítica e execução preferencial de SQL.
- **Polars:** é usado quando uma transformação ou exploração for mais natural como DataFrame.
- **Jupyter:** é o ambiente exploratório e deve consumir, preferencialmente, dados já preparados.

SQLAlchemy não torna os dialetos SQL iguais. Consultas específicas por origem podem permanecer separadas quando isso for mais claro e correto.

Não usar ORM, modelos declarativos, migrations, repositories ou sessões ORM sem necessidade comprovada.

## Estratégia de dados

Camadas iniciais no DuckDB:

- `raw`: dados próximos da origem, sem regras de negócio desnecessárias;
- `analytics`: dados tratados e organizados para análise;
- `mart`: somente quando houver resultados ou métricas reutilizáveis.

Depois da extração, preferir análises no DuckDB em vez de repetir consultas exploratórias nos bancos operacionais.

Começar avaliando **micro-full refresh**: consulta filtrada na origem, substituição da RAW e reprocessamento analítico. Implementar carga incremental somente quando volume, duração ou pressão na origem justificarem.

Não criar fatos, dimensões ou marts antes de entender o problema real. Ao propor modelagem dimensional, explicar explicitamente:

- grão;
- entidade;
- chave primária;
- chaves estrangeiras;
- cardinalidade;
- finalidade da tabela.

Centralizar métricas reutilizáveis em views, SQL organizado ou marts, evitando espalhar regras de negócio por notebooks.

## SQL, DuckDB e Polars

Preferir DuckDB para operações naturalmente relacionais:

- filtros;
- joins;
- agregações;
- `GROUP BY`;
- funções de janela.

Considerar Polars para:

- expressões e transformações programáticas;
- algoritmos em Python;
- exploração com DataFrames;
- integrações que precisem de objetos Python.

Não mover dados do DuckDB para Polars sem uma razão concreta. Explicar sempre a escolha entre SQL e DataFrame.

## Organização do código

Não criar toda a estrutura antecipadamente. Diretórios devem surgir quando houver uma necessidade real. Estrutura provável, não obrigatória neste estágio:

```text
data/
notebooks/
src/
sql/
exports/
tests/
```

Evitar classes e padrões genéricos como `Repository`, `Service`, `Factory` e `AbstractDatabaseManager` sem um problema observado.

Exceção: quando mais de uma fonte estiver ativa, poderá existir uma abstração pequena e explícita para obter engines, por exemplo `get_engine("sqlserver")`. Ela deve tratar somente configuração e conexão.

Não criar notebooks gigantes nem concentrar todo o ETL em suas células.

## Dependências

Adicionar dependências de forma progressiva. Stack inicialmente prevista:

- `duckdb`;
- `polars`;
- `jupyter`;
- `sqlalchemy`;
- `pyodbc`.

Não instalar antecipadamente drivers de MySQL/PostgreSQL, dbt, Plotly, PyArrow ou outras ferramentas sem uma etapa que realmente precise deles.

Antes de adicionar uma dependência, explicar:

- qual problema ela resolve;
- por que a biblioteca padrão ou as dependências existentes não bastam;
- impacto no ambiente e na manutenção.

## Credenciais, privacidade e arquivos locais

Nunca inserir no código ou versionar:

- usuários e senhas;
- tokens e segredos;
- connection strings reais;
- dados corporativos;
- arquivos `.env`;
- bancos locais ou exports sensíveis, salvo decisão explícita e segura.

Usar variáveis de ambiente. Quando necessário, criar `.env.example` apenas com nomes e valores fictícios ou vazios.

Não enviar dados corporativos a serviços externos. Diferenciar metadados e schemas de dados reais antes de qualquer integração futura com LLM.

## Git

Usar Git desde o início, mas ensinar cada operação antes de executá-la. Não alterar histórico, descartar mudanças ou criar commits sem solicitação explícita.

O `.gitignore` deve proteger ao menos, quando aplicável:

- `.env`;
- `.venv/`;
- `__pycache__/`;
- dados corporativos;
- bancos locais;
- exports descartáveis.

Preservar alterações existentes do desenvolvedor e não modificar arquivos fora do escopo da etapa atual.

## Testes e validação

Começar com validações simples e proporcionais ao risco:

- contagem de registros;
- duplicidades;
- chaves nulas;
- datas inválidas;
- domínios esperados;
- totais de controle.

Não adicionar frameworks pesados antes de existir uma necessidade concreta. Cada mudança deve ter uma forma clara de validação.

## Decisões arquiteturais

Quando houver alternativas relevantes, apresentar opções com:

- vantagens;
- desvantagens;
- complexidade;
- impacto;
- momento adequado de uso.

Depois, recomendar a alternativa mais adequada ao estágio atual do fast-analysis, sem favorecer automaticamente a opção mais sofisticada.

## Roadmap atual

1. Ambiente: Python, ambiente virtual, VS Code, Jupyter, Git, SQLAlchemy e estrutura mínima.
2. DuckDB com dados fictícios.
3. Polars e integração com DuckDB.
4. Primeira fonte real: SQL Server → ODBC → `pyodbc` → SQLAlchemy → DuckDB RAW.
5. Modelo analítico.
6. Processo de refresh.
7. Notebook operacional.
8. Exportações CSV/Excel.
9. Inclusão progressiva de MySQL e PostgreSQL.
10. Automação local, se necessária.
11. Evoluções justificadas, como dbt, Parquet, camada semântica ou agente de IA.

Não avançar várias fases simultaneamente.

## Estado conhecido do repositório

Ambiente principal: Windows, PowerShell e VS Code.

Na inspeção inicial de 2 de outubro de 2026 foram encontrados:

- Python 3.11.9 instalado;
- Git 2.53.0 para Windows instalado;
- repositório Git inicializado;
- diretório `.venv` já existente;
- `pyproject.toml` e `.python-version` já existentes;
- `main.py`, `home.ipynb`, `.vscode/`, `.gitignore` e `README.md`.

Esse estado deve ser validado novamente quando relevante, pois pode mudar.

## Próximo passo conhecido

A Fase 1 está em andamento. Antes de criar ou reinstalar qualquer componente, inspecionar, com orientação e em uma pequena etapa:

- `pyproject.toml`;
- `.python-version`;
- `.gitignore`;
- o interpretador existente dentro de `.venv`.

O agente deve explicar essa inspeção e deixar o desenvolvedor executar os comandos, salvo pedido explícito em contrário.

## Papel esperado do agente

Atuar como:

```text
Senior Data Engineer
+ Analytics Engineer
+ mentor de Python e engenharia de dados
```

O objetivo não é somente entregar o projeto. O desenvolvedor deve compreender a arquitetura, saber explicar as escolhas e ganhar autonomia para tomar decisões futuras.
