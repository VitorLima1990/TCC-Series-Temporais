# UNIVERSIDADE DE SÃO PAULO
# MBA DATA SCIENCE & ANALYTICS USP/ESALQ
# Códigos utilizados no Trabalho de Conclusão de Curso
# Vitor Lima
# Estudo de séries temporais aplicado a dados meteorológicos da estação A433 - Brumado

# %% BLOCO 00 - Instalação de pacotes necessários --------------------------------

# Dependências do projeto:
# pandas
# numpy
# matplotlib
# seaborn
# statsmodels

from Functions import ReadFile
from Functions import Save
from Functions import calcular_metricas
from Functions import salvar_grafico
from EstacaoMetereologica import EstacaoMetereologica
from datetime import timedelta

import sys
import matplotlib.pyplot as mplot
from statsmodels.graphics.tsaplots import plot_acf
from statsmodels.graphics.tsaplots import plot_pacf
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX
import seaborn as sns

import pandas as pd # manipulação de dados em formato de dataframe
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.expand_frame_repr', False)


# %% BLOCO 01 - Análise Exploratória do Banco de Dados do INMET --------------------------------

def main(argv=None):  
    output = []
    def Print(*args, sep=' ', end='\n'):
        texto = sep.join(str(arg) for arg in args)

        output.append(texto)

        #print(*args, sep=sep, end=end)
   
    # Initializes the input data
    FileName = "dados/dados_A433_H_2008-04-27_2026-09-12.csv"
    caminho = "dados/dados_A433_H_2008-04-27_2026-09-12.csv"
    inicioInverno = 4
    finalInverno = 9
    inicioDia = 6
    finalDia = 17
    FixarRadSolar = False
    RadSolarFixa = 1000  # utilizado somente se FixarRadSolar = True
    desconsiderarRadSolarMenor = 0
    desconsiderarRadSolarMaior = 1500
    limiteDiasEstacao = 90
    desvPadrao = 4   
    progressBar1=None
    progress_Label=None    
    
    # Condutor de referência da LT 230 kV Ibicoara - Brumado II C2,
    # circuito simples, pertencente ao Lote 01 do Leilão 004/2026.
    
    nCondFeixe= 1 #unidades
    d_Total= 27.03/ 1000 #m
    d_Fios= 3.38/ 1000 #m
    area_Total= 431.60/ 1000000 #m²
    camadas=4 #unidades
    R20DC=0.0717/ 1000 #ohms/m
    DC_AC= "DC"
    C_Var= 0.00403 #ohm/°C
    Vel_Vento= 1 #m/s
    AngIncid= 90 #°
    AltMedia= 750 #m
    TempAmb= 28 #°C
    CoefAbsorcao= 0.9
    CoefEmiss= 0.7
    radincGlobal= 1000 #W/m²
    CLongaDur= 765 #A
    CCurtaDur= 1010 #A
    TempInicial = 20 #°C
    TempFinal = 150 #°C
    Temp_Loc = 65 #°C 
        
    file = ReadFile(FileName)
    linhas = file.lines
    
    if(file.Error):
        return
    else:        
        EM = EstacaoMetereologica(linhas, FileName, caminho, inicioInverno, finalInverno,
                    inicioDia, finalDia, FixarRadSolar, RadSolarFixa,
                    desconsiderarRadSolarMenor, desconsiderarRadSolarMaior,
                    limiteDiasEstacao, desvPadrao, progressBar1,
                    progress_Label)       
        
        EM.ProcessarSerieDiaria()
        
        #Visualização inicial dos dados
        
        df = pd.DataFrame()
        dates_hours = []
        t = []        
        sr = []
        TL = []
        Cap_I = []
        nFig=1      
        
        #Visualização usando dados do dia anterior para dados faltantes
        #Este será o banco de dados usado no restante do código.
        
        df = pd.DataFrame()
        dates_hours = []
        t = []        
        sr = []
        TL = []
        Cap_I = []
        
        dataInicialBD = EM.SerieDiaria[0].dataHora.date()
        dataFinalBD = EM.SerieDiaria[len(EM.SerieDiaria)-1].dataHora.date()
        
        data = dataInicialBD
        i = 0
        while (data <= dataFinalBD):
            datatemp = EM.SerieDiaria[i].dataHora
            datatemp = datatemp.date()
            dates_hours.append(data)
            if(data == datatemp):
                t.append(EM.SerieDiaria[i].tempMaxima)
                sr.append(EM.SerieDiaria[i].radiacaoSolar)  
                Temps,Amp,[Qs,PcL_,PrL_,PcC_,PrC_],TL_,TC_,resultado = EM.CalculoTemperaturaLocacao(nCondFeixe,d_Total,d_Fios,area_Total,camadas,R20DC,DC_AC,C_Var,Vel_Vento,AngIncid,AltMedia,EM.SerieDiaria[i].tempMaxima,CoefAbsorcao,CoefEmiss,EM.SerieDiaria[i].radiacaoSolar,CLongaDur,CCurtaDur,TempInicial,TempFinal)
                TL.append(TL_)
                I = EM.CalculoCorrente(nCondFeixe,d_Total,d_Fios,area_Total,camadas,R20DC,DC_AC,C_Var,Vel_Vento,AngIncid,AltMedia,EM.SerieDiaria[i].tempMaxima,CoefAbsorcao,CoefEmiss,EM.SerieDiaria[i].radiacaoSolar,Temp_Loc)
                Cap_I.append(I)
                i+=1
            else:
                t.append(t[-1])
                sr.append(sr[-1])                  
                TL.append(TL[-1])
                Cap_I.append(Cap_I[-1])            

            data=data+timedelta(days=1) 

        df['Date']=dates_hours
        df['Date'] = pd.to_datetime(df['Date'])
        df['Temperature']=t        
        df['Solar_Radiation']=sr
        df['Conductor_Temperature']=TL
        df['Conductor_Capacity'] = Cap_I 
        
        df.info()        
        Print(df.describe().to_string())
        
        mplot.figure(figsize=(12, 5))        
        mplot.subplot(212) 
        mplot.plot(df['Date'], df['Temperature'], color='blue')
        mplot.xlabel('Data')
        mplot.ylabel('Temperatura [°C]')
        
        titulo = 'Estação - ' + EM.codigo + ' - ' + EM.nome 
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}_Temperaturas.png')                 
        mplot.show()
        mplot.close()
        nFig+=1
        
              
        mplot.figure(figsize=(12, 5))        
        mplot.subplot(212) 
        mplot.plot(df['Date'], df['Solar_Radiation'], color='red')        
        mplot.xlabel('Data')
        mplot.ylabel('Radiação solar [W/m²]')   
        titulo = 'Estação - ' + EM.codigo + ' - ' + EM.nome
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}_Radiacao_solar.png')                 
        mplot.show()
        mplot.close()
        nFig+=1
        
        mplot.figure(figsize=(12, 5))        
        mplot.subplot(212) 
        mplot.plot(df['Date'], df['Conductor_Temperature'])        
        mplot.xlabel('Data')
        mplot.ylabel('Temperatura do Condutor [°C]')   
        titulo = 'Estação - ' + EM.codigo + ' - ' + EM.nome
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}_Temp_Condutor.png')                 
        mplot.show()
        mplot.close()
        nFig+=1      
        
        mplot.figure(figsize=(12, 5))        
        mplot.subplot(212) 
        mplot.plot(df['Date'], df['Conductor_Capacity'], color='darkgreen')        
        mplot.xlabel('Data')
        mplot.ylabel('Capacidade de Corrente [A]')   
        titulo = 'Estação - ' + EM.codigo + ' - ' + EM.nome
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}_Capacidade.png')                 
        mplot.show()
        mplot.close()
        nFig+=1
        
        #Criando filtros de anos.
        Ano_Inicial = 2010
        Ano_Final= 2024
        
        df['day_year']=df['Date'].dt.dayofyear
        
        mplot.figure(figsize=(12, 10))        
        mplot.subplot(212)         
        for year in range(Ano_Inicial, Ano_Final + 1, 1):
            dfTemp = pd.DataFrame()
            dfTemp = df[df['Date'].dt.year == year]
            Print("Ano = " + str(year))
            Print(dfTemp.describe().to_string())
            Print("")
            mplot.plot(dfTemp['day_year'], dfTemp['Temperature'],label=year)                             
                
        mplot.legend(loc="upper right")
        mplot.xlabel('Dia do ano')
        mplot.ylabel('Temperatura [°C]')
        titulo = 'Estação: ' + EM.codigo + ' - ' + EM.nome
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}_Temperatura_Valores Diários.png')                 
        mplot.show()
        mplot.close()
        nFig+=1       
        
        
        mplot.figure(figsize=(12, 10))        
        mplot.subplot(212) 
        for year in range(Ano_Inicial, Ano_Final + 1, 1):
            dfTemp = pd.DataFrame()
            dfTemp = df[df['Date'].dt.year == year]
            Print("")
            mplot.plot(dfTemp['day_year'], dfTemp['Solar_Radiation'],label=year)
            
        mplot.legend(loc="upper right")
        mplot.xlabel('Dia do ano')
        mplot.ylabel('Radiação solar [W/m²]')   
        titulo = 'Estação: ' + EM.codigo + ' - ' + EM.nome
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}_Radiacao_solar_Valores Diários.png')                 
        mplot.show()
        mplot.close()
        nFig+=1 
           
        
        mplot.figure(figsize=(12, 10))        
        mplot.subplot(212) 
        for year in range(Ano_Inicial, Ano_Final + 1, 1):
            dfTemp = pd.DataFrame()
            dfTemp = df[df['Date'].dt.year == year]
            Print("")
            mplot.plot(dfTemp['day_year'], dfTemp['Conductor_Temperature'],label=year)
            
        mplot.legend(loc="upper right")
        mplot.xlabel('Dia do ano')
        mplot.ylabel('Temperatura do condutor [°C]')   
        titulo = 'Estação: ' + EM.codigo + ' - ' + EM.nome + 'Valores Diários'
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}_Temp_condutor_Valores Diários.png')                 
        mplot.show()
        mplot.close()
        nFig+=1         
        
        mplot.figure(figsize=(12, 10))        
        mplot.subplot(212) 
        for year in range(Ano_Inicial, Ano_Final + 1, 1):
            dfTemp = pd.DataFrame()
            dfTemp = df[df['Date'].dt.year == year]
            Print("")
            mplot.plot(dfTemp['day_year'], dfTemp['Conductor_Capacity'],label=year)
            
        mplot.legend(loc="upper right")
        mplot.xlabel('Dia do ano')
        mplot.ylabel('Capacidade de Corrente [A]')
        titulo = 'Estação: ' + EM.codigo + ' - ' + EM.nome + 'Valores Diários'
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}_Capacidade_Valores Diários.png')                 
        mplot.show()
        mplot.close()
        nFig+=1

        #Gráficos com Valores médios diários
        df = df[df['Date'].dt.year.between(Ano_Inicial, Ano_Final)].reset_index(drop=True)
              
        MediaDia_Temperatures = (df.groupby('day_year')['Temperature'].mean().reset_index())        
        mplot.figure(figsize=(12, 10))        
        mplot.subplot(212) 
        mplot.plot(MediaDia_Temperatures['day_year'], MediaDia_Temperatures['Temperature'], color='blue')
        mplot.xlabel('Dia do ano')
        mplot.ylabel('Temperatura [°C]')        
        titulo = 'Estação: ' + EM.codigo + ' - ' + EM.nome + ' - Média das Temperaturas Máximas Diárias entre os anos '+ str(Ano_Inicial) + ' a ' + str(Ano_Final)
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
        mplot.show()
        mplot.close()
        nFig+=1        
        
        MediaDia_Solar_Radiation = (df.groupby('day_year')['Solar_Radiation'].mean().reset_index())
        mplot.figure(figsize=(12, 10))        
        mplot.subplot(212) 
        mplot.plot(MediaDia_Solar_Radiation['day_year'], MediaDia_Solar_Radiation['Solar_Radiation'], color='red')
        mplot.xlabel('Dia do ano')
        mplot.ylabel('Radiação solar [W/m²]')
        titulo = 'Estação: ' + EM.codigo + ' - ' + EM.nome + ' - Médias das Radiações Solares Diárias entre os anos '+ str(Ano_Inicial) + ' a ' + str(Ano_Final)
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
        mplot.show()
        mplot.close()
        nFig+=1        
        
        MediaDia_Cond_Capacity = (df.groupby('day_year')['Conductor_Capacity'].mean().reset_index())
        mplot.figure(figsize=(12, 10))        
        mplot.subplot(212) 
        mplot.plot(MediaDia_Cond_Capacity['day_year'], MediaDia_Cond_Capacity['Conductor_Capacity'], color='darkgreen')
        mplot.xlabel('Dia do ano')
        mplot.ylabel('Capacidade de Corrente [A]')
        
        #Gráficos com Valores médios mensais
        
        df['Mes']=df['Date'].dt.month
        
        MediaMensal_Temperatures = (df.groupby('Mes')['Temperature'].mean().reset_index())
        mplot.figure(figsize=(12, 10))        
        mplot.subplot(212) 
        mplot.plot(MediaMensal_Temperatures['Mes'], MediaMensal_Temperatures['Temperature'], color='blue')
        mplot.xlabel('Mês')
        mplot.ylabel('Temperatura [°C]')
        titulo = 'Estação: ' + EM.codigo + ' - ' + EM.nome + ' - Média das Temperaturas Mensais entre os anos '+ str(Ano_Inicial) + ' a ' + str(Ano_Final)
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
        mplot.show()
        mplot.close()
        nFig+=1 
        
        MediaMensal_Solar_Radiation = (df.groupby('Mes')['Solar_Radiation'].mean().reset_index())
        mplot.figure(figsize=(12, 10))        
        mplot.subplot(212) 
        mplot.plot(MediaMensal_Solar_Radiation['Mes'], MediaMensal_Solar_Radiation['Solar_Radiation'], color='red')
        mplot.xlabel('Mês')
        mplot.ylabel('Radiação solar [W/m²]')
        titulo = 'Estação: ' + EM.codigo + ' - ' + EM.nome + ' - Médias das Radiações Solares Mensais entre os anos '+ str(Ano_Inicial) + ' a ' + str(Ano_Final)
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
        mplot.show()
        mplot.close()
        nFig+=1 
        
        MediaMensal_Cond_Capacity = (df.groupby('Mes')['Conductor_Capacity'].mean().reset_index())
        mplot.figure(figsize=(12, 10))        
        mplot.subplot(212) 
        mplot.plot(MediaMensal_Cond_Capacity['Mes'], MediaMensal_Cond_Capacity['Conductor_Capacity'], color='darkgreen')
        mplot.xlabel('Mês')
        mplot.ylabel('Conductor Capacity [A]')
        titulo = 'Estação: ' + EM.codigo + ' - ' + EM.nome + ' - Média das Capacidades de Corrente Mensais entre os anos '+ str(Ano_Inicial) + ' a ' + str(Ano_Final)
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
        mplot.show()
        mplot.close()
        nFig+=1         
        
        #Processamento para calcular as médias mensais das temperaturas máximas
        df_mensal = (
        df
        .set_index('Date')
        .resample('MS')
        .agg({
            'Temperature': 'mean',
            'Solar_Radiation': 'mean',
            'Conductor_Capacity': 'mean'
        })
        .reset_index())
        
        df_mensal['Mes'] = df_mensal['Date'].dt.month
                
        mplot.figure(figsize=(12, 10))        
        mplot.subplot(212)         
        for year in range(Ano_Inicial, Ano_Final + 1, 1):
            dfTemp = pd.DataFrame()
            dfTemp = df_mensal[df_mensal['Date'].dt.year == year]
            Print("Ano = " + str(year))
            Print(dfTemp.describe().to_string())
            Print("")
            mplot.plot(dfTemp['Mes'], dfTemp['Temperature'],label=year)                             
                
        mplot.legend(loc="upper right")
        mplot.xlabel('Mês')
        mplot.ylabel('Temperatura [°C]')   
        titulo = 'Estação: ' + EM.codigo + ' - ' + EM.nome + 'Média das Temperaturas Máximas Mensais'
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
        mplot.show()
        mplot.close()
        nFig+=1         
        
        mplot.figure(figsize=(12, 10))        
        mplot.subplot(212)         
        for year in range(Ano_Inicial, Ano_Final + 1, 1):
            dfTemp = pd.DataFrame()
            dfTemp = df_mensal[df_mensal['Date'].dt.year == year]
            Print("Ano = " + str(year))
            Print(dfTemp.describe().to_string())
            Print("")
            mplot.plot(dfTemp['Mes'], dfTemp['Solar_Radiation'],label=year)                             
                
        mplot.legend(loc="upper right")
        mplot.xlabel('Mês')
        mplot.ylabel('Radiação Solar [W/m²]') 
        titulo = 'Estação: ' + EM.codigo + ' - ' + EM.nome + 'Média das Radiações Solares Máximas Mensais'
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
        mplot.show()
        mplot.close()
        nFig+=1         
        
        mplot.figure(figsize=(12, 10))        
        mplot.subplot(212)         
        for year in range(Ano_Inicial, Ano_Final + 1, 1):
            dfTemp = pd.DataFrame()
            dfTemp = df_mensal[df_mensal['Date'].dt.year == year]
            Print("Ano = " + str(year))
            Print(dfTemp.describe().to_string())
            Print("")
            mplot.plot(dfTemp['Mes'], dfTemp['Conductor_Capacity'],label=year)                             
                
        mplot.legend(loc="upper right")
        mplot.xlabel('Mês')
        mplot.ylabel('Capacidade de Corrente [A]')   
        titulo = 'Estação: ' + EM.codigo + ' - ' + EM.nome + 'Média das Capacidades de Corrente Mensais'
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
        mplot.show()
        mplot.close()
        nFig+=1         
                        
           
# %% BLOCO 02 - Análise da Sensibilidade dos Parâmetros do Cálculo da Ampacidade ---------------------------

    ##Análise da sensibilidade da Temperatura ambiente
    
    mplot.figure(figsize=(10, 20)) 
    mplot.subplot(212)     
    T = []
    X_values = []
    T_Amb = 0
    while T_Amb < 41:
        Temps,Amp,[Qs,PcL_,PrL_,PcC_,PrC_],TL_,TC_,resultado = EM.CalculoTemperaturaLocacao(nCondFeixe,d_Total,d_Fios,area_Total,camadas,R20DC,DC_AC,C_Var,Vel_Vento,AngIncid,AltMedia,T_Amb,CoefAbsorcao,CoefEmiss,radincGlobal,CLongaDur,CCurtaDur,TempInicial,TempFinal)
        T.append(TL_)
        X_values.append(T_Amb)
        T_Amb+=1
        
    mplot.plot(X_values, T, color='blue')
    mplot.xlabel('Temperatura [°C]')
    mplot.ylabel('Temperatura do Condutor [°C]')
    titulo = 'Análise da Sensibilidade da Temperatura'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1  
    
    #Análise da sensibilidade da radiação solar
    
    mplot.figure(figsize=(10, 20))        
    mplot.subplot(212)
    T = []
    X_values = []
    sr=0
    while sr<1201:
        Temps,Amp,[Qs,PcL_,PrL_,PcC_,PrC_],TL_,TC_,resultado = EM.CalculoTemperaturaLocacao(nCondFeixe,d_Total,d_Fios,area_Total,camadas,R20DC,DC_AC,C_Var,Vel_Vento,AngIncid,AltMedia,TempAmb,CoefAbsorcao,CoefEmiss,sr,CLongaDur,CCurtaDur,TempInicial,TempFinal)
        T.append(TL_)
        X_values.append(sr)
        sr+=1
    
    mplot.plot(X_values, T, color='red')
    mplot.xlabel('Radiação solar [W/m²]')
    mplot.ylabel('Temperatura do Condutor [°C]')     
    titulo = 'Análise da Sensibilidade da Radiação Solar'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1 
    
    ##Análise da sensibilidade da velocidade do vento
    
    mplot.figure(figsize=(10, 20))        
    mplot.subplot(212)
    T = []
    X_values = []    
    v = 0.0
    while v<2.1:    
        Temps,Amp,[Qs,PcL_,PrL_,PcC_,PrC_],TL_,TC_,resultado = EM.CalculoTemperaturaLocacao(nCondFeixe,d_Total,d_Fios,area_Total,camadas,R20DC,DC_AC,C_Var,v,AngIncid,AltMedia,TempAmb,CoefAbsorcao,CoefEmiss,radincGlobal,CLongaDur,CCurtaDur,TempInicial,TempFinal)
        T.append(TL_)
        X_values.append(v)
        v+=0.1
        
    mplot.plot(X_values, T, color='darkorange')
    mplot.xlabel('Velocidade do Vento [m/s]')
    mplot.ylabel('Temperatura do Condutor [°C]')    
    titulo = 'Análise da Sensibilidade da Velocidade do Vento'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1     

# %% BLOCO 03 - Correlação e Autocorreção das Variáveis  ---------------------------
    
    #Correlação
    Print("Correlação entre os dados")            
    df_filtrado = df_mensal[df_mensal['Date'].dt.year.between(Ano_Inicial, Ano_Final)].reset_index(drop=True)
    corr = df_filtrado[['Temperature', 'Solar_Radiation','Conductor_Capacity']].corr().round(3)
    #corr = df_filtrado.corr().round(3)
    Print(corr)

    mplot.figure(figsize=(8, 6))            
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f')        
    titulo = 'Matriz de correlação'    
    mplot.title(titulo)    
    salvar_grafico(f'{nFig:02d}_{titulo}.png')    
    mplot.show()
    mplot.close()    
    nFig += 1
    
    #Autocorrelação
    
    lags = [1, 2, 3, 12, 24]
    
    Print("")
    Print("Autocorrelação das temperaturas")
    Print("Lag  Autocorrelação")
    for lag in lags:
        Print(f'Lag {lag}: {df_filtrado["Temperature"].autocorr(lag=lag):.3f}')
            
    Print("")
    Print("Autocorrelação da radiação solar")
    Print("Lag  Autocorrelação")
    for lag in lags:
        Print(f'Lag {lag}: {df_filtrado["Solar_Radiation"].autocorr(lag=lag):.3f}')
        
    
    df_filtrado['Date_ano_anterior'] = df_filtrado['Date']- pd.DateOffset(years=1)
    
    df_anterior = df_mensal[['Date', 'Temperature', 'Solar_Radiation']].copy()
    
    df_anterior = df_anterior.rename(
        columns={
            'Date': 'Date_ano_anterior',
            'Temperature': 'Temperature_ano_anterior',
            'Solar_Radiation': 'Solar_Radiation_ano_anterior'
        })
    
    df_comparacao = df_filtrado.merge(df_anterior,on='Date_ano_anterior',how='left')
    
    Print("")
    Print("Autocorrelação da Temperatura com o ano anterior")
    correlacao1 = df_comparacao[['Temperature', 'Temperature_ano_anterior']].corr()
    Print(correlacao1)
    
    Print("")
    Print("Autocorrelação da Radiação solar com o ano anterior")
    correlacao2 = df_comparacao[['Solar_Radiation', 'Solar_Radiation_ano_anterior']].corr()
    Print(correlacao2)
    
    #Gráficos ACF (Autocorrelation Function ou Função de Autocorrelação)    
    mplot.figure(figsize=(10, 6))    
    plot_acf(df_filtrado['Temperature'].dropna(), lags=24,
              vlines_kwargs={'colors': 'blue'},
              markerfacecolor='blue',
              markeredgecolor='blue')
        
    titulo = 'ACF - Temperatura'    
    mplot.title(titulo)    
    salvar_grafico(f'{nFig:02d}_{titulo}.png')    
    mplot.show()
    mplot.close()    
    nFig += 1
    
    mplot.figure(figsize=(10, 6))
    plot_acf(df_filtrado['Solar_Radiation'].dropna(), lags=24,
              vlines_kwargs={'colors': 'red'},
              markerfacecolor='red',
              markeredgecolor='red')
    titulo = 'ACF - Radiação solar'    
    mplot.title(titulo)    
    salvar_grafico(f'{nFig:02d}_{titulo}.png')    
    mplot.show()
    mplot.close()    
    nFig += 1
    
    #Gráficos PACF (Partial Autocorrelation Function ou Função de Autocorrelação Parcial)   
    mplot.figure(figsize=(10, 6))
    plot_pacf(df_filtrado['Temperature'].dropna(), lags=24,
              vlines_kwargs={'colors': 'blue'},
              markerfacecolor='blue',
              markeredgecolor='blue')
    titulo = 'PACF - Temperatura'    
    mplot.title(titulo)    
    salvar_grafico(f'{nFig:02d}_{titulo}.png')    
    mplot.show()
    mplot.close()    
    nFig += 1
    
    mplot.figure(figsize=(10, 6))
    plot_pacf(df_filtrado['Solar_Radiation'].dropna(), lags=24,
              vlines_kwargs={'colors': 'red'},
              markerfacecolor='red',
              markeredgecolor='red')
    
    titulo = 'PACF - Radiação solar'    
    mplot.title(titulo)    
    salvar_grafico(f'{nFig:02d}_{titulo}.png')    
    mplot.show()
    mplot.close()    
    nFig += 1
    
    Print("")
    Print("Gráficos de Decomposição")
    resultado = seasonal_decompose(
        df_filtrado['Temperature'].dropna(),
        model='additive',
        period=12
    )
    fig = resultado.plot()
    for ax in fig.axes:
        for linha in ax.lines:
            linha.set_color('blue')
    titulo = 'Decomposição - Temperatura'
    fig.suptitle(titulo)    
    salvar_grafico(f'{nFig:02d}_{titulo}.png')    
    mplot.show()
    mplot.close(fig)    
    nFig += 1    
    
    resultado_rad = seasonal_decompose(
        df_filtrado['Solar_Radiation'].dropna(),
        model='additive',
        period=12
    )
    fig = resultado_rad.plot()
    for ax in fig.axes:
        for linha in ax.lines:
            linha.set_color('red')    
    titulo = 'Decomposição - Radiação Solar'
    fig.suptitle(titulo)    
    salvar_grafico(f'{nFig:02d}_{titulo}.png')    
    mplot.show()
    mplot.close(fig)    
    nFig += 1    

    Print("Teste de Dickey-Fuller Aumentado - ADF")
    
    #---------------------------------------------------------------------------------------------------------------------------             
    # ADF significa:    
    # Augmented Dickey-Fuller — Teste de Dickey-Fuller Aumentado    
    # Ele é um dos testes utilizados para avaliar a presença de raiz unitária, que está associada à não estacionariedade.    
    # O ponto mais importante é entender as hipóteses do teste.    
    
    # Hipótese nula — H₀    
    # A série possui raiz unitária.    
    # Em termos práticos:    
    # A série não é estacionária.
    
    # Hipótese alternativa — H₁    
    # A série não possui raiz unitária.    
    # Em termos práticos:    
    # A série é estacionária.
    
    # Portanto, a interpretação do p-valor é fundamental.
    
    #Considerando um nível de significância de 5%:            
    # p < 0,05
    
    # Caso p-valor = 0.0008
    # Então rejeitamos H₀.
    
    # Conclusão:    
    # Há evidências estatísticas para considerar a série estacionária.
    
    # Agora para:
    
    # Estatística ADF: -1.52
    # p-valor: 0.52
    
    # Como:    
    # p > 0.05
    
    # não rejeitamos H₀.
    
    # Conclusão:    
    # Não há evidências suficientes para rejeitar a hipótese de raiz unitária; a série não deve ser considerada estacionária com base nesse teste.    
    # Atenção: "não rejeitar H₀" é mais correto do que dizer simplesmente "provar que a série não é estacionária".
    #---------------------------------------------------------------------------------------------------------------------------     
          
    resultado = adfuller(df_filtrado['Temperature'].dropna())
    Print("")
    Print("Temperaturas")
    Print('Estatística ADF:', resultado[0])
    Print('p-valor:', resultado[1])
    if(resultado[1]<0.05):
        Print("Rejeita-se H₀.")
        Print("Rejeita-se a hipótese nula de raiz unitária e há evidência de estacionariedade da série de temperatura segundo o Teste ADF.")
    else:
        Print("Não rejeita-se H₀.")
        Print("Não há evidências suficientes para rejeitar a hipótese de raiz unitária; a série não deve ser considerada estacionária com base nesse teste.")
        
    resultado = adfuller(df_filtrado['Solar_Radiation'].dropna())
    
    Print("")
    Print("Radiação Solar")
    Print('Estatística ADF:', resultado[0])
    Print('p-valor:', resultado[1])
    if(resultado[1]<0.05):
        Print("Rejeita-se H₀.")
        Print("Rejeita-se a hipótese nula de raiz unitária e há evidência de estacionariedade da série de radiação solar segundo o Teste ADF.")
    else:
        Print("Não rejeita-se H₀.")
        Print("Não há evidências suficientes para rejeitar a hipótese de raiz unitária; a série não deve ser considerada estacionária com base nesse teste.")


# %% BLOCO 04 - Previsões e Análise de Erros ---------------------------

#Opções de Modelos de Previsão:
    
    # | Modelo            | Tendência                   | Sazonalidade | Diferenciação                | Característica                                      |
    # | ----------------- | --------------------------- | ------------ | ---------------------------- | --------------------------------------------------- |
    # | **Naive sazonal** | Não                         | Sim          | Não                          | Usa o valor do último período sazonal               |
    # | **Holt-Winters**  | Sim                         | Sim          | Não tradicionalmente         | Suavização exponencial com tendência + sazonalidade |
    # | **SARIMA**        | Sim                         | Sim          | Sim                          | Extensão sazonal do ARIMA                           |
    # | **ETS sazonal**   | Dependente da especificação | Sim          | Não da mesma forma que ARIMA | Modelos de erro, tendência e sazonalidade           |
    
    # Principais candidatos:
    
    # Naive sazonal — baseline;
    # Holt-Winters — se a sazonalidade anual for confirmada;
    # SARIMA — se a estrutura de autocorrelação justificar.

#Medidas para Análise dos Erros
   
    # | Medida   | Nome                           | Descrição                                                                                                                                  |
    # | -------- | ------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
    # | **ME**   | Mean Error                     | **Erro médio**. Calcula a média dos erros \(e_t = y_t-\hat y_t\). Indica se o modelo tende a **subestimar ou superestimar**.               |
    # | **MAE**  | Mean Absolute Error            | **Erro absoluto médio**. Média do valor absoluto dos erros. Mede o erro médio sem que erros positivos e negativos se anulem.               |
    # | **MSE**  | Mean Squared Error             | **Erro quadrático médio**. Média dos erros elevados ao quadrado. Penaliza mais fortemente os **erros grandes**.                            |
    # | **RMSE** | Root Mean Squared Error        | **Raiz do erro quadrático médio**. É a raiz quadrada do MSE. Fica na **mesma unidade da variável prevista**, facilitando a interpretação.  |
    # | **MPE**  | Mean Percentage Error          | **Erro percentual médio**. Expressa o erro médio em termos percentuais e permite identificar tendência de **superestimação/subestimação**. |
    # | **MAPE** | Mean Absolute Percentage Error | **Erro percentual absoluto médio**. Mede o erro percentual médio em valor absoluto, facilitando a interpretação como percentual.           |
    
    # Para interpretar rapidamente
    # ME ≈ 0 → pouca tendência sistemática de erro.
    # MAE menor → melhor precisão média.
    # MSE menor → melhor, dando maior peso aos erros grandes.
    # RMSE menor → melhor, com interpretação na unidade original.
    # MPE ≈ 0% → pouca tendência de super/subestimação.
    # MAPE menor → menor erro percentual médio.
    
    # MAE, RMSE e MAPE serão as medidas mais úteis para comparar os modelos de previsão de temperatura e radiação solar. 
    # Um cuidado importante para MAPE/MPE: eles não são adequados quando os valores observados podem ser zero ou muito próximos de zero. 

# Naive sazonal — baseline com origem fixa em 2022

    Ano_Inicial_T = 2010 #Ano inicial do período de estimação
    Ano_Final_T = 2022   #Ano final do período de estimação
    Ano_Inicial_V = 2023 #Ano inicial do período de validação
    Ano_Final_V = 2024   #Ano final do período de validação
    
    # Período de estimação
    df_treino = df_filtrado[
        df_filtrado['Date'].dt.year.between(Ano_Inicial_T, Ano_Final_T)
    ].copy()
    
    # Período de validação
    df_validacao = df_filtrado[
        df_filtrado['Date'].dt.year.between(Ano_Inicial_V, Ano_Final_V)
    ].copy()
    
    # Valores de referência do ano de 2022
    df_2022 = df_treino[
        df_treino['Date'].dt.year == Ano_Final_T
    ].copy()
    
    # Identificação do mês
    df_2022['Mes'] = df_2022['Date'].dt.month
    df_validacao['Mes'] = df_validacao['Date'].dt.month
    
    # Dicionários contendo os valores de cada mês de 2022
    temp_2022 = df_2022.set_index('Mes')['Temperature'].to_dict()
    
    solar_2022 = df_2022.set_index('Mes')['Solar_Radiation'].to_dict()
    
    # Previsão pelo Naive Sazonal
    # 2023 e 2024 utilizam os valores correspondentes de 2022
    df_validacao['Temperature_Naive_Sazonal'] = (
        df_validacao['Mes'].map(temp_2022))
    
    df_validacao['Solar_Radiation_Naive_Sazonal'] = (
        df_validacao['Mes'].map(solar_2022))
    
    reais = df_validacao['Temperature'].to_numpy()    
    previstos = df_validacao['Temperature_Naive_Sazonal'].to_numpy()    
    Print("")
    Print('Modelo Naive Sazonal - Medidas de Erro - Temperatura:')
    ME, MAE, MSE, RMSE, MPE, MAPE = calcular_metricas(reais, previstos)    
        
    Print("ME   =", round(ME, 3))
    Print("MAE  =", round(MAE, 3))
    Print("MSE  =", round(MSE, 3))
    Print("RMSE =", round(RMSE, 3))
    Print("MPE  =", round(MPE, 3), "%")
    Print("MAPE =", round(MAPE, 3), "%")
        
    mplot.figure(figsize=(12, 5))    
    mplot.plot(
        df_validacao['Date'],
        df_validacao['Temperature'],
        label='Temperatura real',
        color='blue')
    
    mplot.plot(
        df_validacao['Date'],
        df_validacao['Temperature_Naive_Sazonal'],
        label='Naive Sazonal - Temperatura',
        color='orange')
    titulo = 'Temperatura real e previsão pelo Naive Sazonal'    
    mplot.xlabel('Mês')
    mplot.ylabel('Temperatura [°C]')
    mplot.legend()
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1
    
    reais = df_validacao['Solar_Radiation'].to_numpy()    
    previstos = df_validacao['Solar_Radiation_Naive_Sazonal'].to_numpy()    
    
    Print("")
    Print('Modelo Naive Sazonal - Medidas de Erro - Radiação Solar:')        
    ME, MAE, MSE, RMSE, MPE, MAPE = calcular_metricas(reais, previstos)    
        
    Print("ME   =", round(ME, 3))
    Print("MAE  =", round(MAE, 3))
    Print("MSE  =", round(MSE, 3))
    Print("RMSE =", round(RMSE, 3))
    Print("MPE  =", round(MPE, 3), "%")
    Print("MAPE =", round(MAPE, 3), "%")
    
    mplot.figure(figsize=(12, 5))    
    mplot.plot(
        df_validacao['Date'],
        df_validacao['Solar_Radiation'],
        label='Radiação solar real',
        color='red')
    
    mplot.plot(
        df_validacao['Date'],
        df_validacao['Solar_Radiation_Naive_Sazonal'],
        label='Naive Sazonal - Radiação Solar',
        color='orange')
    
    titulo = 'Radiação solar real e previsão pelo Naive Sazonal'
    mplot.xlabel('Data')
    mplot.ylabel('Radiação solar [W/m²]')
    mplot.legend()
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1
    
    ##Análise dos Resíduos
    
        #Gráfico dos Resíduos ao longo do tempo
        #ACF dos resíduos;
        #Ljung-Box, por exemplo nos lags: 1, 2, 6, 12 
        #Como interpretar os resultados:
        # Utilizamos normalmente:
        
        # alpha=0.05
        
        # Então:
        
        # p-valor > 0.05    
        # Não rejeitamos H₀.    
        # → Não encontramos evidência estatística de autocorrelação conjunta significativa até aquele lag.    
        # Bom sinal.
        
        # p-valor < 0,05
        
        # Rejeitamos H₀.    
        # → Há evidência de autocorrelação nos resíduos até aquele lag.    
        # Indica que ainda existe estrutura temporal não capturada pelo modelo.
        
    
    #Gráfico dos Resíduos ao longo do tempo - Temperatura
    df_validacao['Residuo_T'] = (df_validacao['Temperature']- df_validacao['Temperature_Naive_Sazonal'])    
    mplot.figure(figsize=(12, 5))    
    mplot.plot(df_validacao['Date'], df_validacao['Residuo_T'], color='blue')    
    mplot.axhline(0, linestyle='--', color='blue')        
    mplot.xlabel('Data')
    mplot.ylabel('Resíduo [°C]')    
    titulo =  'Erros de previsão do Naive Sazonal - Temperatura'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1
    
    #ACF        
    plot_acf(df_validacao['Residuo_T'].dropna(),lags=12, vlines_kwargs={'colors': 'blue'},
    markerfacecolor='blue',
    markeredgecolor='blue')    
    mplot.plot(color='blue')
    titulo = 'ACF dos erros de previsão - Naive Sazonal - Temperatura'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1
        
    #Gráfico dos Resíduos ao longo do tempo - Radiação Solar
    df_validacao['Residuo_SR'] = (df_validacao['Solar_Radiation']- df_validacao['Solar_Radiation_Naive_Sazonal'])
    mplot.figure(figsize=(12, 5))    
    mplot.plot(df_validacao['Date'],df_validacao['Residuo_SR'], color='red')    
    mplot.axhline(0, linestyle='--', color='red')        
    mplot.xlabel('Data')
    mplot.ylabel('Resíduo [W/m²]')    
    titulo = 'Erros de previsão do Naive Sazonal - Radiação Solar'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1
    
    #ACF        
    plot_acf(df_validacao['Residuo_SR'].dropna(),lags=12, vlines_kwargs={'colors': 'red'},
    markerfacecolor='red',
    markeredgecolor='red')    
    titulo = 'ACF dos erros de previsão - Naive Sazonal - Radiação Solar'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1
    
# Holt-Winters aditivo

    Print('Holt-Winters aditivo - Temperatura')

    # Dados de treinamento: 
    df_treino = df_mensal[
        df_mensal['Date'].dt.year.between(
            Ano_Inicial_T,
            Ano_Final_T
        )
    ].copy()
    
    # Dados de validação: 
    df_validacao = df_mensal[
        df_mensal['Date'].dt.year.between(
            Ano_Inicial_V,
            Ano_Final_V
        )
    ].copy()
    
    # Série de temperatura para treinamento
    temperatura_treino = df_treino.set_index('Date')['Temperature'] 
        
    # Modelo Holt-Winters aditivo
    modelo_HW_T = ExponentialSmoothing(
        temperatura_treino,
        trend='add',
        seasonal='add',
        seasonal_periods=12
    ).fit()  

    # Previsões para o período de validação
    previsao_HW_T = modelo_HW_T.forecast(len(df_validacao))
    
    # Armazenar as previsões
    df_validacao['Temperature_HW_Adit'] = previsao_HW_T.values
    
    reais = df_validacao['Temperature'].values
    previstos = df_validacao['Temperature_HW_Adit'].values
    
    ME, MAE, MSE, RMSE, MPE, MAPE = calcular_metricas(reais, previstos)    
        
    Print("ME   =", round(ME, 3))
    Print("MAE  =", round(MAE, 3))
    Print("MSE  =", round(MSE, 3))
    Print("RMSE =", round(RMSE, 3))
    Print("MPE  =", round(MPE, 3), "%")
    Print("MAPE =", round(MAPE, 3), "%")
    
    mplot.figure(figsize=(12, 5))    
    mplot.plot(
        df_validacao['Date'],
        df_validacao['Temperature'],
        label='Temperatura real',
        color='blue')
    
    mplot.plot(
        df_validacao['Date'],
        df_validacao['Temperature_HW_Adit'],
        label='Holt-Winters Aditivo',
        color='orange')
        
    mplot.xlabel('Data')
    mplot.ylabel('Temperatura [°C]')
    mplot.legend()
    titulo = 'Temperatura real e previsão pelo Holt-Winters Aditivo'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1

    #Gráfico dos Resíduos
    residuos_HW_T = modelo_HW_T.resid.dropna()
    mplot.figure(figsize=(12, 5))
    
    mplot.plot(
        temperatura_treino.index[-len(residuos_HW_T):],
        residuos_HW_T,
        color='blue'
    )
    
    mplot.axhline(0, linestyle='--', color='blue')        
    mplot.xlabel('Data')
    mplot.ylabel('Resíduo [°C]')
    titulo = 'Resíduos do Holt-Winters Aditivo - Temperatura'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1
    
    #ACF
    plot_acf(
        residuos_HW_T,
        lags=12,
        vlines_kwargs={'colors': 'blue'}
    )
    
    titulo = 'ACF dos resíduos - Holt-Winters Aditivo - Temperatura'
    mplot.title(titulo)
    
    salvar_grafico(f'{nFig:02d}_{titulo}.png')
    mplot.show()
    mplot.close()
    nFig += 1
    
    #Ljung-Box
    Print('Ljung-Box - resíduos - Holt-Winters Aditivo - Temperatura')
    ljung_box_HW_T = acorr_ljungbox(
        residuos_HW_T,
        lags=[1, 2, 6, 12],
        return_df=True
    )
    
    Print(ljung_box_HW_T)
    Print("")
    
    Print('Holt-Winters aditivo - Radiação Solar')
    
    # Série de radiação solar para treinamento
    RadiacaoSolar_treino = df_treino.set_index('Date')['Solar_Radiation']
    
    # Modelo Holt-Winters aditivo
    modelo_HW_SR = ExponentialSmoothing(
        RadiacaoSolar_treino,
        trend='add',
        seasonal='add',
        seasonal_periods=12
    ).fit()
    
    # Previsões para o período de validação
    previsao_HW_SR = modelo_HW_SR.forecast(len(df_validacao))
    
    # Armazenar as previsões
    df_validacao['Solar_Radiation_HW_Adit'] = previsao_HW_SR.values
    
    reais = df_validacao['Solar_Radiation'].values
    previstos = df_validacao['Solar_Radiation_HW_Adit'].values
    
    ME, MAE, MSE, RMSE, MPE, MAPE = calcular_metricas(reais, previstos)    
        
    Print("ME   =", round(ME, 3))
    Print("MAE  =", round(MAE, 3))
    Print("MSE  =", round(MSE, 3))
    Print("RMSE =", round(RMSE, 3))
    Print("MPE  =", round(MPE, 3), "%")
    Print("MAPE =", round(MAPE, 3), "%")       
    
    mplot.figure(figsize=(12, 5))    
    mplot.plot(
        df_validacao['Date'],
        df_validacao['Solar_Radiation'],
        label='Radiação solar real',
        color='red')
    
    mplot.plot(
        df_validacao['Date'],
        df_validacao['Solar_Radiation_HW_Adit'],
        label='Holt-Winters Aditivo',
        color='orange')    
    
    mplot.xlabel('Data')
    mplot.ylabel('Radiação solar [W/m²]')
    mplot.legend()
    titulo = 'Radiação solar real e previsão pelo Holt-Winters Aditivo'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1
    
    #Gráfico dos Resíduos
    residuos_HW_SR = modelo_HW_SR.resid.dropna()
    mplot.figure(figsize=(12, 5))
    
    mplot.plot(
        RadiacaoSolar_treino.index[-len(residuos_HW_SR):],
        residuos_HW_SR,
        color='red'
    )
    
    mplot.axhline(0, linestyle='--', color='red')
    mplot.xlabel('Data')
    mplot.ylabel('Resíduo [W/m²]')
    
    titulo = 'Resíduos do Holt-Winters Aditivo - Radiação Solar'
    mplot.title(titulo)
    
    salvar_grafico(f'{nFig:02d}_{titulo}.png')
    mplot.show()
    mplot.close()
    nFig += 1
    
    # ACF
    plot_acf(
        residuos_HW_SR,
        lags=12,
        vlines_kwargs={'colors': 'red'}
    )
    
    titulo = 'ACF dos resíduos - Holt-Winters Aditivo - Radiação Solar'
    mplot.title(titulo)
    
    salvar_grafico(f'{nFig:02d}_{titulo}.png')
    mplot.show()
    mplot.close()
    nFig += 1
    
    # Ljung-Box
    Print('Ljung-Box - resíduos - Holt-Winters Aditivo - Radiação Solar')
    
    ljung_box_HW_SR = acorr_ljungbox(
        residuos_HW_SR,
        lags=[1, 2, 6, 12],
        return_df=True
    )
    
    Print(ljung_box_HW_SR)
    Print("") 
    
# Holt-Winters Multiplicativo
    Print('Holt-Winters multiplicativo - Temperatura')
    
    modelo_HW_T_mult = ExponentialSmoothing(
        temperatura_treino,
        trend='add',
        seasonal='mul',
        seasonal_periods=12
    ).fit()
    
    previsao_HW_T_mult = modelo_HW_T_mult.forecast(len(df_validacao))    
    df_validacao['Temperature_HW_Mult'] = (previsao_HW_T_mult.values)  
    
    reais = df_validacao['Temperature'].values
    previstos = df_validacao['Temperature_HW_Mult'].values
    
    ME, MAE, MSE, RMSE, MPE, MAPE = calcular_metricas(reais, previstos)    
        
    Print("ME   =", round(ME, 3))
    Print("MAE  =", round(MAE, 3))
    Print("MSE  =", round(MSE, 3))
    Print("RMSE =", round(RMSE, 3))
    Print("MPE  =", round(MPE, 3), "%")
    Print("MAPE =", round(MAPE, 3), "%")   
    
    mplot.figure(figsize=(12, 5))    
    mplot.plot(
        df_validacao['Date'],
        df_validacao['Temperature'],
        label='Temperatura real',
        color='blue')
    
    mplot.plot(
        df_validacao['Date'],
        df_validacao['Temperature_HW_Mult'],
        label='Holt-Winters Multiplicativo',
        color='orange'
    )
    mplot.xlabel('Data')
    mplot.ylabel('Temperatura [°C]')
    mplot.legend()
    titulo = 'Temperatura real e previsão pelo Holt-Winters Multiplicativo'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1
    
    #Gráfico dos Resíduos
    residuos_HW_T_mult = modelo_HW_T_mult.resid.dropna()
    mplot.figure(figsize=(12, 5))  
    
    mplot.plot(
        temperatura_treino.index[-len(residuos_HW_T_mult):],
        residuos_HW_T_mult,
        color='blue'
    )
    
    mplot.axhline(0, linestyle='--', color='blue')        
    mplot.xlabel('Data')
    mplot.ylabel('Resíduo [°C]')
    titulo = 'Resíduos do Holt-Winters Multiplicativo - Temperatura'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1
    
    #ACF
    plot_acf(
        residuos_HW_T_mult,
        lags=12,
        vlines_kwargs={'colors': 'blue'}
    )
    
    titulo = 'ACF dos resíduos - Holt-Winters Multiplicativo - Temperatura'
    mplot.title(titulo)
    
    salvar_grafico(f'{nFig:02d}_{titulo}.png')
    mplot.show()
    mplot.close()
    nFig += 1
    
    # Ljung-Box
    Print('Ljung-Box - resíduos - Holt-Winters Multiplicativo - Temperatura')
    
    ljung_box_HW_T_mult = acorr_ljungbox(
        residuos_HW_T_mult,
        lags=[1, 2, 6, 12],
        return_df=True
    )
    
    Print(ljung_box_HW_T_mult)
    Print("")
    
    Print('Holt-Winters multiplicativo - Radiação Solar')
    
    modelo_HW_SR_mult = ExponentialSmoothing(
        RadiacaoSolar_treino,
        trend='add',
        seasonal='mul',
        seasonal_periods=12
    ).fit()
    
    previsao_HW_SR_mult = modelo_HW_SR_mult.forecast(len(df_validacao))    
    df_validacao['Solar_Radiation_HW_Mult'] = (previsao_HW_SR_mult.values)    
    
    reais = df_validacao['Solar_Radiation'].values
    previstos = df_validacao['Solar_Radiation_HW_Mult'].values
    
    ME, MAE, MSE, RMSE, MPE, MAPE = calcular_metricas(reais, previstos)    
        
    Print("ME   =", round(ME, 3))
    Print("MAE  =", round(MAE, 3))
    Print("MSE  =", round(MSE, 3))
    Print("RMSE =", round(RMSE, 3))
    Print("MPE  =", round(MPE, 3), "%")
    Print("MAPE =", round(MAPE, 3), "%")   
    
    mplot.figure(figsize=(12, 5))    
    mplot.plot(
        df_validacao['Date'],
        df_validacao['Solar_Radiation'],
        label='Radiação solar real',
        color='red'
    )
    
    mplot.plot(
        df_validacao['Date'],
        df_validacao['Solar_Radiation_HW_Mult'],
        label='Holt-Winters Multiplicativo',
        color='orange'
    )
    mplot.xlabel('Data')
    mplot.ylabel('Radiação Solar [W/m²]')
    mplot.legend()
    titulo = 'Radiação Solar real e previsão pelo Holt-Winters Multiplicativo'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1
    
    #Gráfico dos Resíduos
    residuos_HW_SR_mult = modelo_HW_SR_mult.resid.dropna()
    mplot.figure(figsize=(12, 5))
    
    mplot.plot(
        RadiacaoSolar_treino.index[-len(residuos_HW_SR_mult):],
        residuos_HW_SR_mult,
        color='red'
    )
    
    mplot.axhline(0, linestyle='--', color='red')
    mplot.xlabel('Data')
    mplot.ylabel('Resíduo [W/m²]')
    titulo = 'Resíduos do Holt-Winters Multiplicativo - Radiação Solar'
    mplot.title(titulo)
    salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
    mplot.show()
    mplot.close()
    nFig+=1
    
    #ACF
    mplot.figure(figsize=(12, 5))    
    mplot.plot(
        RadiacaoSolar_treino.index[-len(residuos_HW_SR_mult):],
        residuos_HW_SR_mult,
        color='red'
    )
    
    mplot.axhline(0, linestyle='--', color='red')
    mplot.xlabel('Data')
    mplot.ylabel('Resíduo [W/m²]')
    
    titulo = 'Resíduos do Holt-Winters Multiplicativo - Radiação Solar'
    mplot.title(titulo)
    
    salvar_grafico(f'{nFig:02d}_{titulo}.png')
    mplot.show()
    mplot.close()
    nFig += 1
    
    # ACF
    plot_acf(
        residuos_HW_SR_mult,
        lags=12,
        vlines_kwargs={'colors': 'red'}
    )
    
    titulo = 'ACF dos resíduos - Holt-Winters Multiplicativo - Radiação Solar'
    mplot.title(titulo)
    
    salvar_grafico(f'{nFig:02d}_{titulo}.png')
    mplot.show()
    mplot.close()
    nFig += 1
    
    # Ljung-Box
    Print('Ljung-Box - resíduos - Holt-Winters Multiplicativo - Radiação Solar')
    
    ljung_box_HW_SR_mult = acorr_ljungbox(
        residuos_HW_SR_mult,
        lags=[1, 2, 6, 12],
        return_df=True
    )
    
    Print(ljung_box_HW_SR_mult)
    Print("")
    
#SARIMA
    Print('INÍCIO DOS CÁLCULOS DO SARIMA')  
    modelos = [

    # D = 0
    ((0, 0, 0), (0, 0, 0, 12)),
    ((0, 0, 1), (0, 0, 0, 12)),
    ((1, 0, 0), (0, 0, 0, 12)),
    ((1, 0, 1), (0, 0, 0, 12)),

    ((0, 0, 0), (0, 0, 1, 12)),
    ((0, 0, 1), (0, 0, 1, 12)),
    ((1, 0, 0), (0, 0, 1, 12)),
    ((1, 0, 1), (0, 0, 1, 12)),

    ((0, 0, 0), (1, 0, 0, 12)),
    ((0, 0, 1), (1, 0, 0, 12)),
    ((1, 0, 0), (1, 0, 0, 12)),
    ((1, 0, 1), (1, 0, 0, 12)),

    ((0, 0, 0), (1, 0, 1, 12)),
    ((0, 0, 1), (1, 0, 1, 12)),
    ((1, 0, 0), (1, 0, 1, 12)),
    ((1, 0, 1), (1, 0, 1, 12)),

    # D = 1
    ((0, 0, 0), (0, 1, 0, 12)),
    ((0, 0, 1), (0, 1, 0, 12)),
    ((1, 0, 0), (0, 1, 0, 12)),
    ((1, 0, 1), (0, 1, 0, 12)),

    ((0, 0, 0), (0, 1, 1, 12)),
    ((0, 0, 1), (0, 1, 1, 12)),
    ((1, 0, 0), (0, 1, 1, 12)),
    ((1, 0, 1), (0, 1, 1, 12)),

    ((0, 0, 0), (1, 1, 0, 12)),
    ((0, 0, 1), (1, 1, 0, 12)),
    ((1, 0, 0), (1, 1, 0, 12)),
    ((1, 0, 1), (1, 1, 0, 12)),

    ((0, 0, 0), (1, 1, 1, 12)),
    ((0, 0, 1), (1, 1, 1, 12)),
    ((1, 0, 0), (1, 1, 1, 12)),
    ((1, 0, 1), (1, 1, 1, 12))
    ]    
    
    resultadosT = []
    resultadosSR = []
    
    for numero, (order, seasonal_order) in enumerate(modelos, start=1):        
        p,d,q = order
        P,D,Q,s = seasonal_order
        if(D==0):
            trend = 'c'
        else:
            trend = None
       
        Print()
        Print("=" * 70)
        Print("Modelo", numero)
        Print("order =", order)
        Print("seasonal_order =", seasonal_order)      
        Print("")
        
        Print('SARIMA - Temperatura')               
        
        # Série de treinamento    
        temperatura_treino = df_treino['Temperature']
        
        # Primeiro modelo SARIMA
        modelo_SARIMA_T = SARIMAX(
            temperatura_treino,
            order=order,
            seasonal_order=seasonal_order,
            trend=trend,
            enforce_stationarity=True,
            enforce_invertibility=True
        )
        
        resultado_SARIMA_T = modelo_SARIMA_T.fit(
            method='lbfgs',
            maxiter=200,
            disp=False
        )
        
        Print(resultado_SARIMA_T.summary())
        
        previsao_SARIMA_T = resultado_SARIMA_T.forecast(steps=len(df_validacao))    
        df_validacao['Temperature_SARIMA'] = (previsao_SARIMA_T.values)            
        
        ME, MAE, MSE, RMSE, MPE, MAPE = calcular_metricas(
                df_validacao['Temperature'].values,
                df_validacao['Temperature_SARIMA'].values)
        
        mplot.figure(figsize=(12, 5))        
        mplot.plot(
            df_validacao['Date'],
            df_validacao['Temperature'],
            label='Temperatura real',
            color='blue')
        
        mplot.plot(
            df_validacao['Date'],
            df_validacao['Temperature_SARIMA'],
            label='SARIMA',
            color='orange')        
        
        mplot.xlabel('Data')
        mplot.ylabel('Temperatura [°C]')
        mplot.legend()
        titulo = f'Temperatura real e previsão pelo SARIMA - ({p},{d},{q})×({P},{D},{Q},{s})​'
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
        mplot.show()
        mplot.close()
        nFig+=1
        
        #Gráfico dos Resíduos
        # Resíduos do SARIMA ajustado no período de estimação
        residuos_SARIMA_T = resultado_SARIMA_T.resid.dropna()
        mplot.figure(figsize=(12, 5))
                
        mplot.plot(
            temperatura_treino.index[-len(residuos_SARIMA_T):],
            residuos_SARIMA_T,
            color='blue')
        
        mplot.axhline(0, linestyle='--', color='blue')            
        mplot.xlabel('Data')
        mplot.ylabel('Resíduo [°C]')
        titulo = f'Resíduos do SARIMA - ({p},{d},{q})×({P},{D},{Q},{s}) - Temperatura'
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
        mplot.show()
        mplot.close()
        nFig+=1
        
        #ACF
        plot_acf(
            residuos_SARIMA_T,
            lags=12,
            vlines_kwargs={'colors': 'blue'}
        )
        
        titulo = f'ACF dos resíduos - SARIMA - ({p},{d},{q})×({P},{D},{Q},{s}) - Temperatura'
        mplot.title(titulo)
        
        salvar_grafico(f'{nFig:02d}_{titulo}.png')
        mplot.show()
        mplot.close()
        nFig += 1
        
        #Ljung-Box
        Print(
            f'Ljung-Box - resíduos - SARIMA - '
            f'({p},{d},{q})×({P},{D},{Q},{s}) - Temperatura'
        )
        
        lb = acorr_ljungbox(
            residuos_SARIMA_T,
            lags=[1, 2, 6, 12],
            return_df=True
        )
        Print(lb) 
       
        resultadosT.append({
                'Modelo': numero,
                'order': str(order),
                'seasonal_order': str(seasonal_order),
                'AIC': resultado_SARIMA_T.aic,
                'BIC': resultado_SARIMA_T.bic,
                'ME': ME,
                'MAE': MAE,
                'MSE': MSE,
                'RMSE': RMSE,
                'MPE (%)': MPE,
                'MAPE (%)': MAPE,
                'LB p-valor (1)': lb.loc[1, 'lb_pvalue'],
                'LB p-valor (2)': lb.loc[2, 'lb_pvalue'],
                'LB p-valor (6)': lb.loc[6, 'lb_pvalue'],
                'LB p-valor (12)': lb.loc[12, 'lb_pvalue']
            })
               
        Print("")
        Print('SARIMA - Radiação Solar')    
        Print(f'(p,d,q) = ({p},{d},{q})')
        Print(f'(P,D,Q,s) = ({P},{D},{Q},{s})')        
        
        # Série de treinamento
        RadiacaoSolar_treino = df_treino['Solar_Radiation']
        
        # Primeiro modelo SARIMA
        modelo_SARIMA_SR = SARIMAX(
            RadiacaoSolar_treino,
            order=order,
            seasonal_order=seasonal_order,
            trend=trend,
            enforce_stationarity=True,
            enforce_invertibility=True
        )
        
        resultado_SARIMA_SR = modelo_SARIMA_SR.fit(
            method='lbfgs',
            maxiter=200,
            disp=False
        )
        
        Print(resultado_SARIMA_SR.summary())        
        
        previsao_SARIMA_SR = resultado_SARIMA_SR.forecast(steps=len(df_validacao))    
        df_validacao['Solar_Radiation_SARIMA'] = (previsao_SARIMA_SR.values)            
        
        ME, MAE, MSE, RMSE, MPE, MAPE = calcular_metricas(
                df_validacao['Solar_Radiation'].values,
                df_validacao['Solar_Radiation_SARIMA'].values)
        
        mplot.figure(figsize=(12, 4))
        
        mplot.plot(
            df_validacao['Date'],
            df_validacao['Solar_Radiation'],
            label='Radiação solar real',
            color='red')
        
        mplot.plot(
            df_validacao['Date'],
            df_validacao['Solar_Radiation_SARIMA'],
            label='SARIMA',
            color='orange')
                
        mplot.xlabel('Data')
        mplot.ylabel('Radiação Solar [W/m²]')
        mplot.legend()
        titulo = f'Radiação solar real e previsão pelo SARIMA - ({p},{d},{q})×({P},{D},{Q},{s})'
        mplot.title(titulo)
        salvar_grafico(f'{nFig:02d}_{titulo}.png')                 
        mplot.show()
        mplot.close()
        nFig+=1
        
        #Gráfico dos Resíduos
        # Resíduos do SARIMA ajustado no período de estimação
        residuos_SARIMA_SR = resultado_SARIMA_SR.resid.dropna()
        
        mplot.figure(figsize=(12, 5))        
        mplot.plot(
            RadiacaoSolar_treino.index[-len(residuos_SARIMA_SR):],
            residuos_SARIMA_SR,
            color='red')
        
        mplot.axhline(0, linestyle='--', color='red')
        mplot.xlabel('Data')
        mplot.ylabel('Resíduo [W/m²]')
        
        titulo = f'Resíduos do SARIMA - ({p},{d},{q})×({P},{D},{Q},{s}) - Radiação Solar'
        mplot.title(titulo)
        
        salvar_grafico(f'{nFig:02d}_{titulo}.png')
        mplot.show()
        mplot.close()
        nFig += 1
       
        #ACF
        plot_acf(
        residuos_SARIMA_SR,
            lags=12,
            vlines_kwargs={'colors': 'red'})
        
        titulo = f'ACF dos resíduos - SARIMA - ({p},{d},{q})×({P},{D},{Q},{s}) - Radiação Solar'
        mplot.title(titulo)
        
        salvar_grafico(f'{nFig:02d}_{titulo}.png')
        mplot.show()
        mplot.close()
        nFig += 1
                
        #Ljung-Box
        Print(f'Ljung-Box - resíduos - SARIMA - '
            f'({p},{d},{q})×({P},{D},{Q},{s}) - Radiação Solar')
        
        lb_SR = acorr_ljungbox(
            residuos_SARIMA_SR,
            lags=[1, 2, 6, 12],
            return_df=True)
        
        Print(lb_SR)
       
        resultadosSR.append({
                'Modelo': numero,
                'order': str(order),
                'seasonal_order': str(seasonal_order),
                'AIC': resultado_SARIMA_SR.aic,
                'BIC': resultado_SARIMA_SR.bic,
                'ME': ME,
                'MAE': MAE,
                'MSE': MSE,
                'RMSE': RMSE,
                'MPE (%)': MPE,
                'MAPE (%)': MAPE,
                'LB p-valor (1)': lb_SR.loc[1, 'lb_pvalue'],
                'LB p-valor (2)': lb_SR.loc[2, 'lb_pvalue'],
                'LB p-valor (6)': lb_SR.loc[6, 'lb_pvalue'],
                'LB p-valor (12)': lb_SR.loc[12, 'lb_pvalue']
            })
    
    Print("")
    Print("RESULTADOS SARIMA - TEMPERATURA")
    tabela_resultadosT = pd.DataFrame(resultadosT)
    Print(tabela_resultadosT.to_string(index=False))
    Print("")
    
    Print("RESULTADOS SARIMA - RADIAÇÃO SOLAR")
    tabela_resultadosSR = pd.DataFrame(resultadosSR)
    Print(tabela_resultadosSR.to_string(index=False))    
    
    Save("Resultados.txt", output)
    print('PROCESSO ENCERRADO.')
    
if __name__=="__main__":
    sys.exit(main())