import numpy as np
import os
import re
import unicodedata
import matplotlib.pyplot as mplot


class ReadFile:
    
    def __init__(self, filename):
        """Constructor"""
        self.lines = []
        self.Error = False
        try:
            dados = open(filename,'r', encoding = 'utf-8')
            self.lines = dados.readlines()
            dados.close()
            self.Error = False
        except IOError:
            self.Error = True
            print("Error while trying to open the file. Check if the file exists and if it is located at the correct path.")

def Save(filename, lines):
    try:
        with open(filename, "w", encoding="utf-8") as file:
            for line in lines:
                file.write(str(line) + "\n")
    except IOError:
        print("Error while trying to save the file.")
 
    
def salvar_grafico(nome_arquivo):
    nome_arquivo = limpar_nome_arquivo(nome_arquivo)
    
    pasta_graficos = 'Graficos'
    os.makedirs(pasta_graficos, exist_ok=True)

    caminho = os.path.join(
        pasta_graficos,
        nome_arquivo
    )

    mplot.savefig(
        caminho,
        dpi=300,
        bbox_inches='tight'
    )
    
def limpar_nome_arquivo(nome):
    # Remove acentos
    nome = unicodedata.normalize('NFKD', nome)
    nome = ''.join(
        c for c in nome
        if not unicodedata.combining(c)
    )

    # Substitui caracteres inválidos no Windows por "_"
    nome = re.sub(r'[<>:"/\\|?*]', '_', nome)

    # Substitui espaços por "_"
    nome = re.sub(r'\s+', '_', nome)

    # Remove "_" repetidos
    nome = re.sub(r'_+', '_', nome)

    return nome.strip('_')

def calcular_metricas(reais, previstos):

    reais = np.asarray(reais)
    previstos = np.asarray(previstos)

    erros = reais - previstos

    ME = np.mean(erros)
    MAE = np.mean(np.abs(erros))
    MSE = np.mean(erros ** 2)
    RMSE = np.sqrt(MSE)

    # Evita divisão por zero
    mascara = reais != 0

    MPE = np.mean(
        erros[mascara] / reais[mascara]
    ) * 100

    MAPE = np.mean(
        np.abs(erros[mascara] / reais[mascara])
    ) * 100

    return ME, MAE, MSE, RMSE, MPE, MAPE
        