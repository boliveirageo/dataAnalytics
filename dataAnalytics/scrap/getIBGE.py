# -*- coding: utf-8 -*-
"""
Created on Tue Dec 27 14:46:33 2022

@author: bernard.oliveira
"""

#Configurando a importação arquivos dos link's da fonte de dados
import sys
sys.path.insert(1,'../')

#Importando modulos
import requests as req
from requests.models import PreparedRequest
import pandas as pd
import json
from urlsFontes import fonteDatas


def getSource(fonteDatas):
     
    #Dados utilizado no BDE-GO
    fontes = {
              '74':{'colunas':['D1C','D2C','D3N','V'],'parametros':{'v':'106','c80':'all'}},
              '94':{'colunas':['D1C','D2N','V'],'parametros':{'v':'107'}},
              '289':{'colunas':['D1C','D2C','D3N','V'],'parametros':{'v':'144,145','c193':'all'}},
              '291':{'colunas':['D1C','D2C','D3N','V'],'parametros':{'v':'142,143','c194':'all'}},
              '839':{'colunas':['D1C','D2C','D3N','V'],'parametros':{'v':'214,216','c81':'allxt'}},
              '1002':{'colunas':['D1C','D2C','D3N','V'],'parametros':{'v':'214,216','c81':'allxt'}},
              '1378':{'colunas':['D2C','D4C','D3N','V'],'parametros':{'v':'93','c1':'all','c2':'all','c287':'all','c455':'all'}},
              '2759':{'colunas':['D1C','D7N','V'],'parametros':{'v':'221','c236':'0','c247':'0','c248':'0','c245':'0','c246':'0'}},
              '3939':{'colunas':['D1C','D2C','D3N','V'],'parametros':{'v':'105','c79':'all'}},
              '5457':{'colunas':['D1C','D2C','D3N','V'],'parametros':{'v':'214,216','c782':'allxt'}},
              '5938':{'colunas':['D1C','D2N','V'],'parametros':{'v':'37,498,513,517,6575,525'}},
              '6579':{'colunas':['D1C','D2N','V'],'parametros':{'v':'9324'}}
    }
    
    tbComplete = pd.DataFrame()
    for cod in fontes.keys():
                
        dados = fontes[cod]['parametros']
        colunas = fontes[cod]['colunas']
        
        #Configurando os parametros para acessar a API do IBGE
        param = {'t':cod}
        for value in dados.keys():
            param[value] = dados[value]
        param['n3'] = '52'
        param['n6'] = 'in n3 52'    
                
        #Preparando a url para extrair os dados    
        url = PreparedRequest()
        url.prepare_url(fonteDatas['IBGE'],param) 
        url = str(url.url).replace('&','/').replace('=','/').replace('?','/').replace('+',' ')
            
        try:
            #Extraindo os dados
            data = req.get(url)
            dados = json.loads(str(data.text))
            dfdata = pd.DataFrame(data=dados)
              
            #Transformação dos dados
            dfdata = dfdata[colunas]
            dfdata.rename(columns = {colunas[-2]:'loc_nome'},inplace = True)
            dfdata['var_cod'] = dfdata[colunas[:-2]].apply(lambda x: '-'.join(x.values),axis=1)
            dfdata = dfdata.drop(dfdata.index[0])
            dfdata = dfdata[['loc_nome','var_cod','V']]
        
            #Atualizando a tabela principal
            tbComplete = pd.concat([tbComplete, dfdata])
        except:
            continue
    
    #Retornar a tabela estruturda com os dados
    return tbComplete