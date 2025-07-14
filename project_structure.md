# Estrutura do Projeto PipelineBovespa

Este documento descreve a estrutura de diretórios e arquivos do projeto.

```
PipelineBovespa/
│
├── config/                      # Configurações do projeto
│   ├── __init__.py
│   └── settings.py              # Configurações centralizadas (URLs, nomes de buckets, etc.)
│
├── data/                        # Diretório para dados (local, não versionado)
│   ├── raw/                     # Dados brutos
│   └── refined/                 # Dados processados
│
├── src/                         # Código-fonte do projeto
│   ├── __init__.py
│   │
│   ├── extraction/              # Código para extração de dados
│   │   ├── __init__.py
│   │   └── b3_scraper.py        # Web scraper para dados da B3
│   │
│   ├── lambda/                  # Código para funções Lambda
│   │   ├── __init__.py
│   │   └── trigger_glue_job.py  # Função para acionar job Glue
│   │
│   └── glue/                    # Scripts relacionados ao Glue (visual jobs exportados)
│       └── bovespa_etl_job.py   # Job Glue exportado do modo visual
│
├── notebooks/                   # Notebooks para análise exploratória
│   └── bovespa_analysis.ipynb   # Notebook para análise dos dados da B3
│
├── infra/                       # Código de infraestrutura (CloudFormation, etc.)
│
├── tests/                       # Testes do projeto
│
├── .gitignore                   # Arquivos a serem ignorados pelo Git
├── requirements.txt             # Dependências do projeto
├── README.md                    # Documentação principal do projeto
├── requirements.md              # Requisitos do projeto
└── action-plan.md              # Plano de ação do projeto
```
