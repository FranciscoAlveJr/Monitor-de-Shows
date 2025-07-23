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
def convert_to_datetime(date_str: str) -> str:
    formats = [
        '%d %m - %Y',
        '%d %b - %Y',
        '%d %B - %Y',
        '%d/%m/%Y',
        '%d de %B de %Y',
    ]

    mes_list = list(meses.keys())
    date_split = date_str.lower().split()

    for d in date_split:
        if d in mes_list:
            date_str = date_str.lower().replace(d, meses[d])        

    for f in formats:
        try:
            date = datetime.strptime(date_str, f)
            date = date.strftime('%d/%m/%Y')
            return date
        except ValueError:
            continue
    
    raise ValueError(f'Não foi possível converter a data "{date_str}"')
    # return date_str

if __name__=="__main__":
    date = convert_to_datetime('2025-07-25')
    print(date)