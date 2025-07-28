# Configuração de Encoding no VSCode para Arquivos CSV

Quando trabalhamos com arquivos CSV que contêm acentos e caracteres especiais do português, podemos encontrar problemas de exibição no VSCode, enquanto o mesmo arquivo aparece corretamente no Excel.

## Por Que Isso Acontece?

O Excel detecta automaticamente que o arquivo está em codificação Windows (CP-1252), que é comum para arquivos gerados em sistemas Windows no Brasil. No entanto, o VSCode por padrão tenta abrir arquivos em UTF-8, o que causa problemas com caracteres acentuados.

## Soluções para VSCode

### 1. Alternar a Codificação Manualmente

Quando um arquivo CSV estiver aberto:

1. Clique no indicador de codificação na barra de status (canto inferior direito)
2. Selecione "Reopen with Encoding..." (Reabrir com Codificação...)
3. Escolha "Windows 1252" ou "Western (Windows 1252)"
4. O arquivo deve agora exibir corretamente os caracteres acentuados

### 2. Configuração Automática (Já Implementada)

Foi criado um arquivo `.vscode/settings.json` que configura automaticamente o VSCode para:

- Abrir arquivos `.csv` com codificação Windows 1252
- Associar arquivos CSV a um tipo específico que usa ponto e vírgula como separador

### 3. Extensão CSV Recomendada

Para melhor visualização de arquivos CSV, instale a extensão "Rainbow CSV":

1. Vá para a aba de Extensões (Ctrl+Shift+X)
2. Pesquise por "Rainbow CSV"
3. Instale a extensão

Esta extensão coloriza as colunas e permite visualizar os dados tabulados corretamente, além de oferecer várias ferramentas para trabalhar com CSV.

## Alternativas de Visualização

Se continuar tendo problemas com a visualização no VSCode, você pode:

1. Usar o Excel para visualizar os arquivos
2. Usar o Pandas no Python para ler e manipular os dados
3. Utilizar ferramentas online como o Google Sheets

## Como Verificar se o Arquivo Está Correto

Para verificar se o arquivo CSV está com a codificação correta:

```python
import pandas as pd

# Leia o arquivo com a codificação correta
df = pd.read_csv('caminho/para/arquivo.csv', sep=';', encoding='latin-1')

# Exiba as primeiras linhas para verificar
print(df.head())
```

Isso deve mostrar os caracteres acentuados corretamente no terminal do Python.
