import pandas as pd

def translateData(data, game, type):
    if game == "maismilionaria":
        if type == "ganhadores":
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'match': 'acertos',
                'winners': 'ganhadores',
                'prize': 'premio'
            })
            data['acertos'] = data['acertos'].replace({
                "6 + 2 clovers": "sena + 2 trevos",
                "6 + 1 or 0 clovers": "sena + 1 ou 0 trevos",
                "5 + 2 clovers": "quina + 2 trevos",
                "5 + 1 or 0 clovers": "quina + 1 ou 0 trevos",
                "4 + 2 clovers": "quadra + 2 trevos",
                "4 + 1 or 0 clovers": "quadra + 1 ou 0 trevos",
                "3 + 2 clovers": "terno + 2 trevos",
                "3 + 1 clovers": "terno + 1 trevo",
                "2 + 2 clovers": "duque + 2 trevos",
                "2 + 1 clover": "duque + 1 trevo"
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })
        elif type == "dezenas":
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'numbers_clovers': 'dezenas_trevos'
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })

    elif game == "megasena":
        if type == "ganhadores":
            print("oi")
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'match': 'acertos',
                'winners': 'ganhadores',
                'prize': 'premio'
            })
            data['acertos'] = data['acertos'].replace({
                "6": "sena",
                "5": "quina",
                "4": "quadra"
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })
        elif type == "dezenas":
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'numbers': 'dezenas'
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })

    elif game == "lotofacil":
        if type == "ganhadores":
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'match': 'acertos',
                'winners': 'ganhadores',
                'prize': 'premio'
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })
        elif type == "dezenas":
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'numbers': 'dezenas'
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })

    elif game == "quina":
        if type == "ganhadores":
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'match': 'acertos',
                'winners': 'ganhadores',
                'prize': 'premio'
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })
        elif type == "dezenas":
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'numbers': 'dezenas'
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })

    elif game == "lotomania":
        if type == "ganhadores":
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'match': 'acertos',
                'winners': 'ganhadores',
                'prize': 'premio'
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })
        elif type == "dezenas":
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'numbers': 'dezenas'
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })

    elif game == "duplasena":
        if type == "ganhadores":
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'match': 'acertos',
                'winners': 'ganhadores',
                'prize': 'premio'
            })
            data['acertos'] = data['acertos'].replace({
                "6": "sena",
                "5": "quina",
                "4": "quadra",
                "3": "terno"
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })
        elif type == "dezenas":
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'numbers1': 'dezenas1',
                'numbers2': 'dezenas2'
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })

    elif game == "diadesorte":
        if type == "ganhadores":
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'match': 'acertos',
                'winners': 'ganhadores',
                'prize': 'premio'
            })
            data['acertos'] = data['acertos'].replace({
                "Lucky Month": "Mes da Sorte"
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })
        elif type == "dezenas":
            data = data.rename(columns={
                'date': 'data',
                'course': 'concurso',
                'accumulated': 'acumula',
                'numbers': 'dezenas',
                'month': 'mes'
            })
            data['acumula'] = data['acumula'].replace({
                "yes": "sim",
                "no": "nao"
            })
            data['mes'] = data['mes'].replace({
                "January": "Janeiro",
                "February": "Fevereiro",
                "March": "Marco",
                "April": "Abril",
                "May": "Maio",
                "June": "Junho",
                "July": "Julho",
                "August": "Agosto",
                "September": "Setembro",
                "October": "Outubro",
                "November": "Novembro",
                "December": "Dezembro"
            })

    return data
