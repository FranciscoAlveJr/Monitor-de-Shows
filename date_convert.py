from datetime import datetime, date

meses = {
    "janeiro": "January",
    "fevereiro": "February",
    "março": "March",
    "abril": "April",
    "maio": "May",
    "junho": "June",
    "julho": "July",
    "agosto": "August",
    "setembro": "September",
    "outubro": "October",
    "novembro": "November",
    "dezembro": "December",
    "jan": "Jan",
    "fev": "Feb",
    "mar": "Mar",
    "abr": "Apr",
    "mai": "May",
    "jun": "Jun",
    "jul": "Jul",
    "ago": "Aug",
    "set": "Sep",
    "out": "Oct",
    "nov": "Nov",
    "dez": "Dec"
}
def convert_to_datetime(data_str: str) -> str:
    formats = [
        '%d %m - %Y',
        '%d %b - %Y',
        '%d %B - %Y',
        '%d/%m/%Y',
        '%d de %B de %Y',
        '%d/%b/%Y'
    ]

    mes_list = list(meses.keys())
    date_split = data_str.lower().split()
    hoje = datetime.strptime(datetime.now().strftime('%d/%m/%Y'), '%d/%m/%Y')

    for d in date_split:
        if d in mes_list:
            data_str = data_str.lower().replace(d, meses[d])        

    if len(data_str.split()) == 2:
        ano = date.today().year
        data_l = data_str.split()
        data_str = f'{data_l[0]}/{data_l[1]}'
        data_str2 = f'{data_str}/{ano}'
    else:
        data_str2 = data_str

    for f in formats:
        try:
            data = datetime.strptime(data_str2, f)
            if data < hoje:
                try:
                    data_str2 = f'{data_str}/{ano+1}'
                except UnboundLocalError:
                    pass
            data = datetime.strptime(data_str2, f)
            data = data.strftime('%d/%m/%Y')
            return data
        except ValueError:
            continue
    
    raise ValueError(f'Não foi possível converter a data "{data_str}"')
    # return data_str

if __name__=="__main__":
    data = convert_to_datetime('27 Mar - 2025')
    print(data)