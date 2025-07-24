import requests as rq
from requests import Session
from bs4 import BeautifulSoup as bs
# from pprint import pprint
from datetime import datetime
import logging
from filtros import definir_genero
from time import sleep
from date_convert import convert_to_datetime
from requests.exceptions import ConnectionError

# Club do Ingresso
# Ingresso rapido
# Uhuu

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('log.log'), logging.StreamHandler()], encoding='utf-8')


class Sympla:
    def __init__(self, genero: str, todos: bool) -> None:
        self.session = Session()
        self.logger = logging.getLogger(__name__)
        self.todos = todos
        self.genero = genero

        url = 'https://www.sympla.com.br/api/discovery-bff'

        if not genero:
            gen = '/search-closed/event?&cl=17-festas-e-shows'
            self.ver_generos = False
        else:
            gen = f'/search/event?s={genero}&cl=17-festas-e-shows'
            self.ver_generos = True

        self.url2 = url + gen

        self.eventos = []

        # self.url1 = f'https://www.sympla.com.br/eventos/sao-paulo-sp{genero}'
        # self.url_all = f'https://www.sympla.com.br/api/discovery-bff/search-closed/event?&cl=17-festas-e-shows'
        # self.url_gen = f'https://www.sympla.com.br/api/discovery-bff/search/event?{genero}cl=17-festas-e-shows'

        self.headers = {
            'authority': 'www.sympla.com.br',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }

        self.payload = {
            'cl': '17-festas-e-shows'
            }

        self.cookies = {
            's_user_location': '{"city":"S%C3%A3o%20Paulo","coordinates":{"lat":-23.5629,"lon":-46.6544},"sk":3832,"slug":"sao-paulo-sp"}'
        }

    def filtro(self, genero: str):
        self.genero = genero.split()[0].lower()
        # genero = '+'.join(genero[:1])
        # if self.genero != '':
        #     self.genero = f'+{self.genero}'
        # self.url1 = self.url1.format(genero=self.genero)
        self.url2 = self.url2.format(genero=self.genero)

    def pesquisar_eventos(self, locais: list[str], date_list: list):
        self.logger.info(f'Iniciando pesquisa de eventos de em São Paulo no site Sympla...')

        ver_local = False

        if len(locais) > 0:
            ver_local = True

        i = 1
        total_paginas = 1

        while True:
            sleep(1)
            if i == 1:
                page = ''
            else:
                page = f'&page={i}'

            res = self.session.get(self.url2+page, headers=self.headers, cookies=self.cookies)
            try:
                data = res.json()['data']
            except KeyError:
                i += 1
                continue

            if i == 1:
                total = res.json()['total']
                limite = res.json()['limit']

                if total == 0:
                    self.logger.info(f'Nenhum evento foi encontrado.')
                    break

                f = total % limite
                if f != 0:
                    total_paginas = total // limite + 1
                else:
                    total_paginas = total // limite

                self.logger.info(f'Foram encontrados {total} eventos.')


            for event in data:
                sleep(1)

                evento = {
                    'nome': '',
                    'local': '',
                    'dataHora': '',
                    'genero': '',
                    'link': '',
                    'site': 'Sympla'
                }

                url = event['url']
                res2 = self.session.get(url, headers=self.headers)
                soup = bs(res2.content, 'html.parser')

                tent = 0
                try:
                    descricao = soup.select(
                        '#__next > section.sc-b281498b-0.ilWENo > div > div > div.sc-537fdfcb-0.bdUbUp')[0].text
                except IndexError:
                    while tent < 5:
                        try:
                            headers = {
                                'authority': 'bff-sales-api-cdn.bileto.sympla.com.br',
                                'accept': 'application/json',
                                'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
                                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                                'X-Api-Key': 'cQkazy2Wc'
                            }
                            event_id = url.split('/')[-1]
                            bileto_url = f'https://bff-sales-api-cdn.bileto.sympla.com.br/api/v1/events/{event_id}'
                            res3 = self.session.get(bileto_url, headers=headers)
                            try:
                                json_res = res3.json()['data']
                            except KeyError:
                                tent = 5
                                continue
                            try:
                                descricao = json_res['operator_info']
                                break
                            except KeyError:
                                raw = json_res['description']['raw']
                                soup2 = bs(raw, 'html.parser')
                                descricao = soup2.text
                                break
                        except ConnectionError:
                            tent += 1
                            sleep(60)
                            continue

                if tent == 5:
                    continue

                evento['nome'] = event['name']

                local_casa = event['location']['name']
                # endereco = event['location']['address']
                # cidade = event['location']['city']
                # estado = event['location']['state']
                evento['local'] = local_casa

                data = event['start_date_formats']['pt']
                converted_date = convert_to_datetime(data[data.find(',')+1:data.find(' ·')].strip())
                evento['dataHora'] = converted_date
                date_event = datetime.strptime(evento['dataHora'], '%d/%m/%Y').date()

                evento['link'] = event['url']

                evento_genero = definir_genero(evento['nome'], descricao)
                evento['genero'] = evento_genero

                if evento_genero == 'Outro':
                    continue
                else:
                    if not self.todos:
                        if evento_genero.lower() != self.genero.lower():
                            continue                        
                        if ver_local:
                            if not any(local for local in locais if local.lower() in evento['local'].lower()):
                                continue
                        if len(date_list) == 2:
                            if date_event < date_list[0] or date_event > date_list[1]:
                                continue

                    self.eventos.append(evento)
                    self.logger.info(f'{evento["nome"]}')

            if i == total_paginas:
                break

            i += 1
        
        return self.eventos
    
# 
class ClubdoIngresso:
    def __init__(self, todos: bool) -> None:
        self.session = Session()
        self.eventos = []
        self.logger = logging.getLogger(__name__)
        self.todos = todos

        self.headers = {
            'authority': 'www.clubedoingresso.com',
            'accept': '*/*',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        }

        self.payload = {
            'filtrar_estado': 'SP'
        }

        self.url = 'https://www.clubedoingresso.com/categoria/3'
        self.url_estado = 'https://www.clubedoingresso.com/hotsite/filtrarEstados'

    def pesquisar_eventos(self, genero: str, locais: list[str], data_list: list):
        if not genero:
            ver_generos = False
        else:
            ver_generos = True

        if len(locais) == 0:
            ver_locais = False
        else:
            ver_locais = True        

        self.logger.info('Pesquisando Eventos em São Paulo no site Clube do Ingresso...')

        res_filtro = self.session.post(self.url_estado, headers=self.headers, data=self.payload)

        if res_filtro.status_code != 200:
            self.logger.info('Ocorreu um erro no servidor.')
            return None

        res = self.session.get(self.url, headers=self.headers)
        soup = bs(res.content, 'html.parser')

        shows = soup.find_all('div', {'class': 'ItemCarrousel__content'})

        if len(shows) == 0:
            self.logger.info('Nenhum evento foi encontrado.')
            return self.eventos

        self.logger.info(f'Foram encontrados {len(shows)} eventos.')


        for show in shows:
            sleep(1)

            link = show.find('a').get('href')
            link = 'https://www.clubedoingresso.com' + link

            res2 = self.session.get(link, headers=self.headers)
            soup = bs(res2.content, 'html.parser')

            descricao = soup.find('div', {'class': 'EventDescricao'}).text.strip()

            evento = {
                'nome': '',
                'local': '',
                'dataHora': '',
                'genero': '',
                'link': '',
                'site': 'Clube do Ingresso'
            }

            evento['nome'] = soup.find('div', {'class': 'PageEvent__nameEvent'}).text.strip()

            data = soup.find('div', {'class': 'PageEvent__desc'}).text.strip()
            data = data[data.find(',')+1:data.find('-')].strip()
            evento['dataHora'] = convert_to_datetime(data)
            date_event = datetime.strptime(evento['dataHora'], '%d/%m/%Y').date()

            local = soup.find('div', {'class': 'PageEvent__local'})
            teatro = local.find('div', {'class': 'PageEvent__subTitle'}).text.strip()
            # endereco = local.find('div', {'class': 'PageEvent__desc'}).text.strip()
            evento['local'] = f'{teatro}'
            evento['link'] = link

            evento_genero = definir_genero(evento['nome'], descricao)
            evento['genero'] = evento_genero

            if evento_genero == 'Outro':
                continue
            else:
                if not self.todos:
                    if ver_generos:
                        if genero.lower() != evento_genero.lower():
                            continue
                    if ver_locais:
                        if not any(local for local in locais if local.lower() in evento['local'].lower()):
                            continue
                    if len(data_list) == 2:
                        if date_event < data_list[0] or date_event > data_list[1]:
                            continue

                self.eventos.append(evento)
                self.logger.info(f'{evento["nome"]}')

        self.logger.info('PESQUISA NO CLUBE DO INGRESSO FINALIZADA.')
        return self.eventos

    
class Uhuu():
    def __init__(self, todos: bool) -> None:
        self.session = Session()
        self.eventos = []
        self.logger = logging.getLogger(__name__)
        self.todos = todos

        self.url = 'https://uhuu.com/busca/show'

        self.headers = {
            'authority': 'uhuu.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        }

        self.payload = {
            'termo': 'são paulo',
            'page': 1
        }

    def pesquisar_eventos(self, genero: str, locais: list[str], data_list: list):
        if not genero:
            ver_generos = False
        else:
            ver_generos = True

        if len(locais) == 0:
            ver_locais = False
        else:
            ver_locais = True        

        self.logger.info(f'Pesquisando Eventos em São Paulo no site Uhuu...')

        links = []
        is_saopaulo = True

        res = rq.get(self.url, headers=self.headers, params=self.payload)
        soup = bs(res.content, 'html.parser')

        paginacao = soup.find('ul', {'class': 'pagination'})
        paginas = paginacao.find_all('a')
        paginas = paginas[:-1]
        num_paginas = len(paginas)

        shows = soup.find_all('div', {'class': 'item card-evento'})
        if len(shows) == 0:
            self.logger.info('Nenhum evento foi encontrado.')
            return self.eventos
        
        for show in shows:
            link = show.find('a', {'class': 'link'}).get('href')
            links.append(link)

        for i in range(1, num_paginas):
            sleep(1)
            if not is_saopaulo:
                break
            self.payload['page'] = i+1
            res = rq.get(self.url, headers=self.headers, params=self.payload)
            soup = bs(res.content, 'html.parser')
            shows = soup.find_all('div', {'class': 'item card-evento'})
            
            for show in shows:
                link = show.find('a', {'class': 'link'}).get('href')
                if 'sp/sao-paulo' not in link:
                    is_saopaulo = False
                    break
                links.append(link)

        # Remover links duplicados
        links = list(set(links))

        self.logger.info(f'Foram encontrados {len(links)} eventos.')
        
        for link in links:
            sleep(1)

            res = rq.get(link, headers=self.headers)
            soup = bs(res.content, 'html.parser')

            descricao = soup.find('div', {'class': 'tabs-content-item sobre active'}).text

            evento = {
                'nome': '',
                'local': '',
                'dataHora': '',
                'genero': '',
                'link': '',
                'site': 'Uhuu'
            }

            evento['nome'] = soup.find('h1', {'class': 'event-title'}).text.strip()
            evento['local'] = soup.find('strong', {'id': 'pageEventLocal'}).text.strip()

            data = soup.find_all('div', {'class': 'event-details'})[0].find('p').text.strip()
            data = ' '.join(data.split()[:-2])
            data = data.split(' a ')[0].strip()
            evento['dataHora'] = convert_to_datetime(data)
            date_event = datetime.strptime(evento['dataHora'], '%d/%m/%Y').date()

            evento['link'] = link

            evento_genero = definir_genero(evento['nome'], descricao)
            evento['genero'] = evento_genero

            if evento_genero == 'Outro':
                continue
            else:
                if not self.todos:
                    if ver_generos:
                        if genero.lower() != evento_genero.lower():
                            continue
                    if ver_locais:
                        if not any(local for local in locais if local.lower() in evento['local'].lower()):
                            continue
                    if len(data_list) == 2:
                        if date_event < data_list[0] or date_event > data_list[1]:
                            continue

                self.eventos.append(evento)
                self.logger.info(f'{evento["nome"]}')
        
        return self.eventos

class Eventim:
    def __init__(self, genero: str, todos: bool) -> None:
        self.session = Session()
        self.eventos = []
        self.logger = logging.getLogger(__name__)
        self.genero = genero
        self.todos = todos

        if not todos:
            if 'Internacional' in genero:
                f_genero = f'Shows Internacionais|{genero}'
            else:
                f_genero = f'Shows Nacionais|{genero}'
        else:
            f_genero = ''

        self.url = 'https://public-api.eventim.com/websearch/search/api/exploration/v2/productGroups'

        self.headers = {
            'authority': 'public-api.eventim.com',
            'accept': '*/*',
            'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
        }

        self.payload = {
            'webId': 'web__eventim-com-br',
            'language': 'pt',
            'retail_partner': 'BR1',
            'categories': f_genero,
            'city_ids': '943',
            'sort': 'Recommendation',
            'in_stock': 'true'
        }

    
    def pesquisar_eventos(self, locais: list[str], data_list: list):
        if len(locais) == 0:
            ver_locais = False
        else:
            ver_locais = True        

        if self.todos:
            self.payload.pop('categories')

        self.logger.info(f'Iniciando pesquisa de eventos em São Paulo no site Eventim...')
        i = 0

        while True:
            sleep(1)
            i += 1

            if i > 1:
                self.payload['page'] = i

            res = self.session.get(self.url, headers=self.headers, params=self.payload)
            shows = res.json()['productGroups']

            if i == 1:
                total_paginas = res.json()['totalPages']
                total_results = res.json()['totalResults']
                self.logger.info(f'Foram encontrados {total_results} eventos.')

            for show in shows:
                evento = {
                    'nome': '',
                    'local': '',
                    'dataHora': '',
                    'genero': '',
                    'link': '',
                    'site': 'Eventim'
                }

                num_produtos = show['productCount']
                produtos = show['products']
                try:
                    genero = show['categories'][1]['name']
                except (IndexError, KeyError):
                    genero = "Outro"

                for produto in produtos:
                    evento['nome'] = produto['name']
                    data_hora = produto['typeAttributes']['liveEntertainment']['startDate']
                    data = datetime.strftime(datetime.strptime(data_hora.split('T')[0], '%Y-%m-%d'), "%d/%m/%Y")
                    evento['dataHora'] = convert_to_datetime(data)
                    date_event = datetime.strptime(evento['dataHora'], '%d/%m/%Y').date()

                    evento['link'] = produto['link']
                    evento['genero'] = genero

                    local = produto['typeAttributes']['liveEntertainment']['location']['name']
                    evento['local'] = local

                    if not self.todos:
                        if ver_locais:
                            if not any(local for local in locais if local.lower() in evento['local'].lower()):
                                continue
                        if len(data_list) == 2:
                            if date_event < data_list[0] or date_event > data_list[1]:
                                continue


                    self.logger.info(evento['nome'])
                    self.eventos.append(evento)

            if i == total_paginas:
                # self.eventos = [dict(t) for t in {tuple(evento.items()) for evento in self.eventos}]
                self.logger.info(f'PESQUISA NO EVENTIM FINALIZADA.')
                return self.eventos

class Ticket360:
    def __init__(self, genero: str, todos: bool) -> None:
        self.session = Session()
        self.eventos = []
        self.logger = logging.getLogger(__name__)
        self.genero = genero
        self.todos = todos

        self.url = r'https://www.ticket360.com.br/eventos/pesquisar?s=sao+paulo'

        self.headers = {
            'authority': 'www.ticket360.com.br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Sec-Ch-Ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36'
        }

    def pesquisar_eventos(self, locais: list[str], data_list: list):
        if len(locais) == 0:
            ver_locais = False
        else:
            ver_locais = True

        self.logger.info(f'Iniciando pesquisa de eventos em São Paulo no site Ticket360...')

        # OS EVENTOS EM SÃO PAULO
        self.logger.info('Buscando por eventos em São Paulo...')
        res = rq.get(self.url, headers=self.headers)
        soup = bs(res.content, 'html.parser')

        all_eventos = soup.find_all('a', {'class': 'event-click'})

        sleep(1)
        # EVENTOS DO GÊNERO
        if self.todos:
            generos_dict = {'rock': [], 'pop': [], 'mpb': [], 'pop-rock': []}
            generos = list(generos_dict.keys())

            for genero in generos:
                self.logger.info(f'Buscando por eventos de {genero}...')
                self.url_gen = f'https://www.ticket360.com.br/eventos/pesquisar?s={genero}'
                sleep(1)
                res2 = rq.get(self.url_gen, headers=self.headers)
                soup2 = bs(res2.content, 'html.parser')

                gen_eventos = soup2.find_all('a', {'class': 'event-click'})
                gen_eventos = [evento.get('data-id') for evento in gen_eventos]
                generos_dict[genero] = gen_eventos
        else:
            genero = self.genero.split()[0].lower() if len(self.genero.split()) > 1 else self.genero.lower()

            self.url_gen = f'https://www.ticket360.com.br/eventos/pesquisar?s={genero}'
            res2 = rq.get(self.url_gen, headers=self.headers)
            soup2 = bs(res2.content, 'html.parser')

            gen_eventos = soup2.find_all('a', {'class': 'event-click'})
            gen_eventos = [evento.get('data-id') for evento in gen_eventos]

        for evento in all_eventos:
            endereco = evento.find('span', {'class': 'card-endereco'}).text.strip()
            estado = endereco.split('/')[1].strip().lower()
            if estado != 'sp':
                continue


            evento_dict = {
                'nome': '',
                'local': '',
                'dataHora': '',
                'genero': '',
                'link': '',
                'site': 'Ticket360'
            }

            nome = evento.find('span', {'class': 'card-name-evento'})
            nome = nome.text.strip().replace('\n', '')
            local = evento.find('div', {'class': 'row header-card-event'})
            local = local.text.strip().replace('\n', '')
            data = evento.find('div', {'class': 'row data-calendar'})
            data = data.text.strip().replace('\n', '').split()
            data = f'{data[1]} {data[0]}'
            data = convert_to_datetime(data)
            date_event = datetime.strptime(data, '%d/%m/%Y').date()

            title = evento.get('data-id')
            if not self.todos:
                if title not in gen_eventos:
                    continue
                if ver_locais:
                    if not any(local_e for local_e in locais if local_e.lower() in local.lower()):
                        continue
                if len(data_list) == 2:
                    if date_event < data_list[0] or date_event > data_list[1]:
                        continue
            else:
                for genero, gen_eventos in generos_dict.items():
                    if title in gen_eventos:
                        self.genero = genero
                        break
                    else:
                        self.genero = "outro"
            
            if self.genero == 'outro':
                continue

            evento_dict['nome'] = nome
            evento_dict['local'] = local
            evento_dict['dataHora'] = data
            evento_dict['genero'] = self.genero.title()
            evento_dict['link'] = f"https://www.ticket360.com.br/{evento.get('href')}"

            self.eventos.append(evento_dict)

            self.logger.info(nome)

        self.logger.info('PESQUISA NO TICKET360 CONCLUIDA.')
        return self.eventos


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('log.log'), logging.StreamHandler()])

    # sympla = Sympla(['Rock Nacional'], True)
    # print(sympla.pesquisar_eventos('São Paulo', datetime.now()))

    # clube = ClubdoIngresso()
    # pprint(clube.pesquisar_eventos())

    # eventim = Eventim('Rock Nacional', True)
    # pprint(eventim.pesquisar_eventos([], datetime.now()))

    # uhuu = Uhuu(True)
    # pprint(uhuu.pesquisar_eventos([], [], datetime.now()))

    ticket360 = Ticket360('', True)
    print(ticket360.pesquisar_eventos([], [datetime.now()]))



# Gêneros:
# Shows Internacionais
# Shows Nacionais|MPB
# Shows Nacionais|Pop Nacional
# Shows Nacionais|Rock Nacional

