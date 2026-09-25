# Estudo de séries temporais aplicado a dados meteorológicos da estação A433 – Brumado

Código-fonte desenvolvido para o Trabalho de Conclusão de Curso (TCC) do MBA Data Science & Analytics USP/ESALQ.

O projeto utiliza dados meteorológicos da estação automática **A433 – Brumado**, do Instituto Nacional de Meteorologia (INMET), para caracterizar séries temporais de temperatura e radiação solar e avaliar modelos de previsão. A partir das condições meteorológicas diárias também é calculada a capacidade de condução de corrente de um condutor de referência.

## Conteúdo do projeto

```text
TCC-Series-Temporais/
├── Main.py
├── Functions.py
├── EstacaoMetereologica.py
├── requirements.txt
├── README.md
└── dados/
    ├── dados_A433_H_2008-04-27_2026-09-12.csv
    └── README.md
```

### Arquivos Python

- **Main.py** – rotina principal do estudo, incluindo preparação dos dados, análise exploratória, cálculo da capacidade de condução de corrente, modelos de previsão, avaliação e geração dos gráficos.
- **Functions.py** – funções auxiliares para leitura de arquivos, salvamento de resultados e gráficos e cálculo das métricas de avaliação.
- **EstacaoMetereologica.py** – classes e funções relacionadas ao tratamento das informações meteorológicas e ao cálculo térmico do condutor.

### Dados

O arquivo de entrada utilizado pelo programa é:

`dados/dados_A433_H_2008-04-27_2026-09-12.csv`

Embora a base contenha um período maior, o estudo considera os dados de **2010 a 2024**.

Os dados meteorológicos são provenientes da estação automática A433 – Brumado, do INMET. Consulte `dados/README.md` para informações sobre o arquivo de entrada.

## Principais etapas do processamento

O programa realiza, de forma integrada:

1. leitura e processamento dos dados meteorológicos;
2. tratamento de registros diários ausentes;
3. cálculo diário da temperatura do condutor e da capacidade de condução de corrente;
4. agregação das séries para frequência mensal;
5. análise exploratória, incluindo correlação, autocorrelação, teste ADF e decomposição sazonal;
6. previsão por Naive sazonal;
7. previsão por Holt-Winters;
8. busca sistemática de modelos SARIMA com sazonalidade anual (`s = 12`);
9. avaliação das previsões no período de validação de 2023–2024;
10. diagnóstico dos resíduos por meio do teste de Ljung-Box e da ACF;
11. geração dos gráficos e do arquivo de resultados.

## Período de estimação e validação

Para os modelos de previsão, os dados mensais foram divididos em:

- **2010–2022:** período de estimação;
- **2023–2024:** período de validação fora da amostra.

## Cálculo da capacidade de condução de corrente

A capacidade de condução é calculada diariamente a partir das condições meteorológicas e dos parâmetros do condutor de referência. No processamento utilizado no estudo, a temperatura do condutor é fixada em **65 °C** para o cálculo da capacidade.

A série mensal de capacidade é obtida pela média dos valores calculados diariamente, e não pelo cálculo da capacidade diretamente a partir das médias mensais das variáveis meteorológicas.

## Modelos de séries temporais

São considerados os seguintes métodos:

- Naive sazonal;
- Holt-Winters;
- SARIMA.

Para os modelos SARIMA, foi realizada uma busca sistemática entre combinações das ordens não sazonais e sazonais definidas no código, utilizando período sazonal de 12 meses.

## Requisitos

O projeto foi desenvolvido em Python e pode ser executado utilizando as bibliotecas listadas em `requirements.txt`.

Para instalar as dependências:

```bash
pip install -r requirements.txt
```

## Execução

Com o arquivo CSV disponível na pasta `dados/`, execute:

```bash
python Main.py
```

O código também pode ser executado pelo ambiente Spyder.

O programa gera os resultados e os gráficos conforme definido nas rotinas de processamento.

## Observação sobre os dados

O arquivo CSV é mantido no repositório para permitir a reprodução do processamento apresentado no TCC. O período efetivamente utilizado na análise estatística é 2010–2024.

## Autor

**Vitor Lima**  
MBA Data Science & Analytics – USP/ESALQ
