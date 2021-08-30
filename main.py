
# %% 
import requests
import csv
import pandas
import numpy
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression


def saveFile(filename, source):
    with open(filename,'w') as f:
        f.write(source.__str__())


def convert2Csv(filename, source):
    csvLista = []
    f = open(filename, 'w', newline='', encoding='utf-8')
    w = csv.writer(f, delimiter=',')
    cabecalho = ['Pais', 'Populacao','IDH','Mortes por milhao','Atualizacao']
    w.writerow(cabecalho)
    z = len(source)
    for index in range(0,z):
        temp_data = []
        temp_data.append(source[index]['pais'])
        temp_data.append(source[index]['populacao'])
        temp_data.append(source[index]['idh'])
        temp_data.append(source[index]['mortes_por_milhao'])
        temp_data.append(source[index]['ultima_atualizacao'])
        w.writerow(temp_data)
        del temp_data
    print('ok')


def correlacao(filename, source):
    f = open(filename, 'w', newline='', encoding='utf-8')
    w = csv.writer(f, delimiter=',')
    cabecalho = ['Atualizacao','Pais','IDH (x)','Mortes por milhao (y)']
    w.writerow(cabecalho)
    z = len(source)
    x = []
    y = []
    for index in range(0,z):
        temp_data = []
        temp_data.append(source[index]['ultima_atualizacao'])
        temp_data.append(source[index]['pais'])
        temp_data.append(source[index]['idh'])
        temp_data.append(source[index]['mortes_por_milhao'])
        x.append(source[index]['idh'])
        y.append(source[index]['mortes_por_milhao'])
        w.writerow(temp_data)
        del temp_data
    valorCorrelacao = numpy.corrcoef(x,y)[1,0]
    print('ok')
    return [valorCorrelacao, x, y]


def requestAPI(urlCovid):
    responseCovid = requests.get(urlCovid)
    dataCovid = responseCovid.json()
    countryList = []
    noCountryList = []
    regionList = []
    noDeathList = []
    for index in dataCovid:
        if(dataCovid[index].get('continent')):
            if(dataCovid[index].get('human_development_index')):
                if(dataCovid[index]['data'][-1].get('total_deaths_per_million')):
                    dados = {
                        'pais': dataCovid[index]['location'],
                        'populacao': dataCovid[index]['population'] if (dataCovid[index].get('population')) else None,
                        'ultima_atualizacao': dataCovid[index]['data'][-1]['date'],
                        'idh': dataCovid[index]['human_development_index'],
                        'mortes_por_milhao': dataCovid[index]['data'][-1]['total_deaths_per_million'] if (dataCovid[index]['data'][-1].get('total_deaths_per_million')) else None
                    }
                    countryList.append(dados)
                else:
                    noDeath = {
                        'pais': dataCovid[index]['location'],
                        'populacao': dataCovid[index]['population'] if (dataCovid[index].get('population')) else None,
                        'ultima_atualizacao': dataCovid[index]['data'][-1]['date'],
                        'idh': dataCovid[index]['human_development_index'],
                        'mortes_por_milhao': None
                    }
                    noDeathList.append(noDeath)
            else:
                noDados = {
                    'pais': dataCovid[index]['location'],
                    'populacao': dataCovid[index]['population'] if (dataCovid[index].get('population')) else None,
                    'ultima_atualizacao': dataCovid[index]['data'][-1]['date'],
                    'idh': None
                }
                noCountryList.append(noDados)
        else:
            regioes = {
                'regiao': dataCovid[index]['location'],
                'populacao': dataCovid[index]['population'] if (dataCovid[index].get('population')) else None,
            }
            regionList.append(regioes)
    return [countryList, noCountryList, regionList, noDeathList]


def regressaoLinear(source,x,y,filename):
    dados = pandas.read_csv(filename)
    dados.head()
    x = dados['IDH (x)'].values
    y = dados['Mortes por milhao (y)'].values

    plt.scatter(x,y,label='y(x)')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()

    from sklearn.linear_model import LinearRegression
    modelo = LinearRegression()
    x = x.reshape(-1,1)
    modelo.fit(x,y)
    acuracia = modelo.score(x,y) #quão bem ajustou os pontos
    print (acuracia)

    coef_angular = modelo.coef_[0]
    coef_linear = modelo.intercept_
    print("Coeficiente angular = {:0.2f}".format(coef_angular))
    print("Coeficiente linear = {:0.2f}".format(coef_linear))

    reta = coef_angular*x+coef_linear
    plt.scatter(x,y,label='y(x)')
    plt.plot(x,reta,label='Ajuste linear',color='red')
    plt.xlabel('x')
    plt.ylabel('y')
    plt.legend()

    #Encontrando os erros
    from sklearn.metrics import mean_absolute_error,mean_squared_error
    MAE = mean_absolute_error(y, reta)
    RMSE = numpy.sqrt(mean_squared_error(y,reta))
    print("Erro médio = {:0.2f}".format(MAE))
    print("Desvio = {:0.2f}".format(RMSE))

    print("ok")
     


def main():
    result = requestAPI('https://covid.ourworldindata.org/data/owid-covid-data.json')

    saveFile('paisesComDados.txt', result[0])
    saveFile('paisesSemDados.txt', result[1])
    saveFile('regioes.txt', result[2])
    saveFile('paisesSemMortes.txt', result[3])

    convert2Csv('paisesComDados.csv',result[0])
    valor = correlacao('trabalho.csv',result[0])
    print(valor[0])
    regressaoLinear(result[0],valor[1],valor[2],'trabalho.csv')
    


if __name__ == "__main__":
    main()
# %%
