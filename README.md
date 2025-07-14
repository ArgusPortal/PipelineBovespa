# PipelineBovespa

## Sobre o Projeto
Pipeline de dados para processamento batch de informações do pregão da B3 (Bolsa de Valores Brasileira). Este projeto implementa um fluxo completo de ETL utilizando serviços da AWS, incluindo S3, Lambda, Glue e Athena.

## Objetivos
- Extrair dados do pregão da B3 via web scraping
- Processar e transformar os dados utilizando AWS Glue
- Disponibilizar os dados para análise via AWS Athena
- Criar um pipeline automatizado e escalável

## Documentação
- [Requisitos do Projeto](./requirements.md)
- [Plano de Ação](./action-plan.md)

## Arquitetura
```
Web Scraping → S3 (raw) → Lambda → Glue Job → S3 (refined) → Glue Catalog → Athena
```

## Tecnologias Utilizadas
- Python (Web Scraping)
- AWS S3 (Armazenamento)
- AWS Lambda (Gatilho)
- AWS Glue (ETL)
- AWS Athena (Consulta)
- Formato Parquet (Armazenamento otimizado)
