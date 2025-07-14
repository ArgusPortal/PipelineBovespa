# Plano de Ação - Pipeline Batch Bovespa

## 1. Preparação do Ambiente (Semana 1)
- [  ] Configurar credenciais da AWS
- [  ] Criar bucket S3 com estrutura de diretórios apropriada (raw, refined)
- [  ] Configurar permissões IAM necessárias para Lambda e Glue

## 2. Desenvolvimento do Web Scraper (Semana 1-2)
- [  ] Analisar a estrutura do site da B3
- [  ] Implementar script de web scraping em Python utilizando bibliotecas como BeautifulSoup ou Selenium
- [  ] Garantir que o scraper capture todos os dados necessários do pregão
- [  ] Implementar transformação dos dados para formato Parquet
- [  ] Adicionar lógica de particionamento diário

## 3. Configuração da Ingestão de Dados (Semana 2)
- [  ] Automatizar o processo de scraping para execução diária
- [  ] Implementar lógica para upload dos dados para o bucket S3 (pasta raw)
- [  ] Testar o fluxo de extração e ingestão

## 4. Desenvolvimento da Função Lambda (Semana 3)
- [  ] Criar função Lambda que será acionada por eventos do S3
- [  ] Implementar código para iniciar o job do Glue
- [  ] Configurar trigger no bucket S3 para acionar a Lambda
- [  ] Testar o acionamento automático

## 5. Desenvolvimento do Job Glue (Semana 3-4)
- [  ] Criar job Glue no modo visual
- [  ] Implementar transformação A: agrupamento numérico/sumarização
- [  ] Implementar transformação B: renomear duas colunas
- [  ] Implementar transformação C: cálculos com campos de data
- [  ] Configurar particionamento de saída por data e código da ação
- [  ] Salvar dados refinados em formato Parquet na pasta "refined"

## 6. Configuração do Glue Catalog e Athena (Semana 4)
- [  ] Configurar o job Glue para catalogar automaticamente os dados
- [  ] Verificar a criação da tabela no banco de dados default do Glue Catalog
- [  ] Configurar o Athena para consulta dos dados
- [  ] Testar consultas SQL básicas no Athena

## 7. Análise e Visualização (Opcional) (Semana 5)
- [  ] Criar notebook no Athena para análise exploratória
- [  ] Desenvolver visualizações gráficas dos dados processados
- [  ] Documentar insights obtidos

## 8. Documentação e Finalização (Semana 5)
- [  ] Documentar arquitetura completa do pipeline
- [  ] Criar instruções de execução e manutenção
- [  ] Preparar apresentação do projeto
- [  ] Revisar todos os requisitos para garantir cumprimento

## Tecnologias Utilizadas
- **Extração de Dados**: Python (BeautifulSoup/Selenium)
- **Armazenamento**: AWS S3 (formato Parquet)
- **Processamento**: AWS Lambda, AWS Glue
- **Análise**: AWS Athena
- **Controle de Versão**: Git

## Monitoramento e Logs
- Implementar logs detalhados em cada etapa do pipeline
- Configurar alertas para falhas no processo
- Monitorar tempos de execução e performance
