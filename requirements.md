# Pipeline Batch Bovespa - Requisitos do Projeto

## Descrição
Este projeto consiste em construir um pipeline de dados completo para extrair, processar e analisar dados do pregão da B3 (Bolsa de Valores Brasileira), utilizando serviços da AWS como S3, Lambda, Glue e Athena.

## Requisitos Técnicos

### 1. Extração de Dados
- **Requisito 1:** Implementar web scraping de dados do site da B3 com informações do pregão diário.

### 2. Ingestão de Dados
- **Requisito 2:** Ingerir dados brutos no AWS S3 em formato Parquet com particionamento diário.

### 3. Processamento e Transformação
- **Requisito 3:** Configurar o bucket S3 para acionar uma função Lambda automaticamente quando novos dados forem inseridos.
- **Requisito 4:** Desenvolver função Lambda em qualquer linguagem com o único propósito de iniciar o job do Glue.
- **Requisito 5:** Criar job no AWS Glue no modo visual com as seguintes transformações obrigatórias:
  - A: Realizar agrupamento numérico, sumarização, contagem ou soma.
  - B: Renomear duas colunas existentes além das colunas de agrupamento.
  - C: Executar cálculos com campos de data (duração, comparação ou diferença entre datas).

### 4. Armazenamento Refinado
- **Requisito 6:** Salvar os dados refinados em formato Parquet em uma pasta chamada "refined" no S3, com particionamento por data e por nome/abreviação da ação do pregão.

### 5. Catalogação de Dados
- **Requisito 7:** Configurar o job do Glue para catalogar automaticamente os dados no Glue Catalog e criar uma tabela no banco de dados default.

### 6. Análise de Dados
- **Requisito 8:** Garantir que os dados estejam disponíveis e legíveis no Amazon Athena para consultas SQL.
- **Requisito 9 (Opcional):** Desenvolver um notebook no Athena para visualização gráfica dos dados ingeridos.

## Critérios de Avaliação
Este projeto é uma atividade obrigatória e vale 90% da nota de todas as disciplinas da fase.
