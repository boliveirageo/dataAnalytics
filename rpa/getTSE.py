# -*- coding: utf-8 -*-
"""
Created on Thu Dec 29 15:52:03 2022

@author: bernard.oliveira
"""
#Configurando a importação arquivos dos link's da fonte de dados
import sys
sys.path.insert(1,'../')

#Importando modulos
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import pandas as pd
from urlsFontes import fonteDatas


def getSource():
    
    drivers = {
        'mozilla':os.path.join(os.getcwd(),'geckodriver.exe')
    }

    #Ocultar a janela do navegador
    #options = Options()
    #options.add_argument("-headless")
    
    driver = webdriver.Firefox(executable_path=drivers['mozilla'])#,options=options)
    driver.get(fonteDatas['TSE'])

    #Ano
    selAno = Select(driver.find_element('id','P0_SLS_ANO_DIS_SF'))
    selAno.select_by_index(0)

    #Mês
    selMes = Select(driver.find_element('id','P0_SLS_MES_DIS_SF'))
    selMes.select_by_index(0)

    #Abrangencia
    selAbr = Select(driver.find_element('id','P0_SLS_ABRAN_DIS_SF'))
    selAbr.select_by_value('M')

    #UF
    selUF = Select(driver.find_element('id','P0_SLS_UF_DIS_SF'))
    selUF.select_by_value('GO')

    #Criando a lista de municipio
    ListSelectMun = Select(driver.find_element('id','P0_SLS_MUNICIPIO_DIS_SF'))
    listMun = [ListSelectMun.options[i].get_attribute('innerHTML') for i in range(0,len(ListSelectMun.options))]  
    
    #Criando a tabela final
    df = pd.DataFrame()

    #Percorrer cada Municipios, consultar e salvar as informações
    for i in range(1,len(listMun)):
        print('Processando município:',listMun[i])
        
        selMun = Select(driver.find_element('id','P0_SLS_MUNICIPIO_DIS_SF'))
        selMun.select_by_index(i)
    
        table = driver.find_element(By.CLASS_NAME,'t16StandardAlternatingRowColors')
        data = pd.read_html(str(table.get_attribute('outerHTML')))[0]
    
        data['Municipio'] = listMun[i]
        df = pd.concat([df,data])  

    
    df = df[['Faixa Etária','Masculino(M)','Feminino(F)','Não Informado(N)','Total(T)','Municipio']]
        
    #Retornando a tabela
    return df

df = getSource()