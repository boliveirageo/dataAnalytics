# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 13:13:06 2023

@author: bernard.oliveira
"""
#Configurando a importação arquivos dos link's da fonte de dados
import sys
sys.path.insert(1,'../')

#Importando módulos
import requests as req
import pandas as pd
import json
import os
from zipfile import ZipFile
from urlsFontes import fonteDatas
import tempfile
import re
import numpy as np


def getSource(anoinicial,anofinal,ensino,tipoEnsinoBasiso=None):
    '''
        Coleta as informações de educação básica e/ou superior da fonte do INEP
        
        Exemplo do ensino Básico: getSource(2021,2021,'Básica','3.2')
        
        Exemplo do ensino Superior: getSource(2021,2021,'Superior')
    
    '''    
    
    tbCompleto = pd.DataFrame()
    fonte = fonteDatas['INEP'][ensino]
    anos = [str(i) for i in range(anoinicial,anofinal+1)]
    
    for ano in anos:
        
        dado = fonte+ano+'.zip'
        outfileTmp = tempfile.gettempdir()+'\\tmp.zip'
        resposta = req.get(dado,verify = False);
        
        with open(outfileTmp,'wb') as filezip:
            filezip.write(resposta.content)
            filezip.close()
            with ZipFile(outfileTmp) as z:
                if ensino == 'Superior':
                    foldernm = 'Microdados do Censo da Educação Superior '+ano+'/'+'dados/MICRODADOS_CADASTRO_IES_'+ano+'.CSV'
                    listfiles = [f for f in z.namelist() if f[-3:] == 'CSV']
                    filecsv = [j for j in listfiles if j.rfind('IES') > 0][0]
                    with z.open(filecsv) as dt:
                        df = pd.read_csv(dt,sep=';',encoding='cp1252')
                        tbCompleto = pd.concat([tbCompleto, df])
                         
                elif ensino == 'Básica':
                    file = [j for j in z.namelist() if j.rfind('.xlsx') > 0][0]
                    dirName = os.path.dirname(file)
                    z.extractall(tempfile.gettempdir(),None,None)
                    file_excel = os.path.join(tempfile.gettempdir(),file)                       
                    if tipoEnsinoBasiso == None:
                        plan = '1.2'
                    else:
                        plan = tipoEnsinoBasiso
                    df = pd.read_excel(file_excel,sheet_name=plan)
                    tbCompleto = df
            
            
            del filezip,z
    
    os.remove(outfileTmp)
    return tbCompleto

def processingdata(data,ensino,tipoEnsinoBasiso=None):
    '''
        Coleta as informações de educação básica e/ou superior da fonte do INEP
        
        Exemplo do ensino Básico: processingdata(variavel,'Básica','3.2')
        
        Exemplo do ensino Superior: processingdata(variavel,'Superior')
    
    '''
    if ensino == 'Superior':
        # IES Instituiçoes de Ensino Superior em Goiás
        data = data[data['CO_UF_IES'] == 52]

        # Codificacar a variável Organizacao Academica com as informações do dicionario de variáveis
        data['Organizacao Academica'] = data['TP_ORGANIZACAO_ACADEMICA'].map({
                1:"Universidades",
                2:"Centros Universitários",
                3:"Faculdades",
                4:"IFs e Cefets"})

        # Codificacar a variável grau de instrução com as informações do arquivo layout
        data['Categoria Administrativa'] = data['TP_CATEGORIA_ADMINISTRATIVA'].map({
                1:"Pública Federal",
                2:"Pública Estadual",
                3:"Pública Municipal",
                4:"Privada com fins lucrativos",
                5:"Privada sem fins lucrativos",
                6:"Privada - Particular em sentido estrito",
                7:"Especial",
                8:"Privada comunitária",
                9:"Privada confessional"
            })
       
        #data.rename(columns={'CO_MUNICIPIO_IES':'Cod.IBGE', 'NO_MUNICIPIO_IES': 'LOC_NOME', 'NU_ANO_CENSO': 'ANO'}, inplace = True)

    elif ensino == 'Básica':
        
        esferas = ['Municipal','Estadual','Federal','Privada']
        propriedade = ['Rural','Urbana']
        
        variaveis = {
                '1.2':{'Número de Matrículas da Educação Básica':[propriedade,esferas]},
                'Creche 1.6':{'Número de Matrículas da Creche':[propriedade,esferas]},
                'Pré-Escola 1.10':{'Número de Matrículas da Pré-Escola':[propriedade,esferas]},
                '1.16':{'Número de Matrículas nos Anos Iniciais do Ensino Fundamental':[propriedade,esferas]},
                '1.21':{'Número de Matrículas nos Anos Finais do Ensino Fundamental Regular':[propriedade,esferas]},
                '1.26':{'Número de Matrículas do Ensino Médio Regular':[propriedade,esferas]},
                '1.31':{'Número de Matrículas da Educação Profissional Regular':[propriedade,esferas]},
                '1.35':{'Número de Matrículas da Educação de Jovens e Adultos (EJA)':[propriedade,esferas]},
                '1.40':{'Número de Matrículas da Educação Especial em Classes Comuns':[propriedade,esferas]},
                ##'2.22':{
                ##        'Número de Docentes da Educação Básica':[]
                ##},
                '3.2':{'Número de Estabelecimentos da Educação Básica':[propriedade,esferas]},
                '4.2':{'Número de Turmas da Educação Básica':[propriedade,esferas]}
        }
        
        data = data.iloc[4:,0:]
        data.fillna('',inplace=True)
        data.columns = data.iloc[0].values 
        
        data = data.iloc[2:-6,0:]
        delrows = 3
        
        for row in range(0,delrows):
            rows = data.iloc[row,:].values
            for i in range(1,len(rows)):
                if rows[i] =='' and rows[i-1]!= '':
                    rows[i] = rows[i-1]
            data.columns = data.columns+rows
        
        data = data.iloc[delrows:,:]   
        data['Unidade da Federação'] = data['Unidade da Federação'].str.strip()
        data['Código do Município'] = data['Código do Município'].apply(lambda x: '52' if x == ' ' else x)        
        variavel = [i for i in variaveis[tipoEnsinoBasiso].keys()][0]
        
        data = data[data['Unidade da Federação'] == 'Goiás']
        data['variaveis'] = variavel
        
        for k in variaveis[tipoEnsinoBasiso][variavel][1]: 
            listEsfera = []
            for b in variaveis[tipoEnsinoBasiso][variavel][0]:
                listEsfera.append(b+k)
            data[k] = data[listEsfera].apply(lambda x: np.sum(x.values),axis=1)
        
        data = data[['Unidade da Federação','Código do Município','variaveis','Município','Municipal','Estadual','Federal','Privada']]
        
    return data