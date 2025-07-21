import requests as rq
from requests import Session
from bs4 import BeautifulSoup as bs
from pprint import pprint
from datetime import datetime, date
import logging
from filtros import definir_genero
from time import sleep
from date_convert import convert_to_datetime

# import playwright
# from playwright.sync_api import sync_playwright
# from playwright.async_api import async_playwright
import asyncio
from lxml import etree

# Club do Ingresso
# Ingresso rapido
# Uhuu

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('log.log'), logging.StreamHandler()])

class Sympla:
    def __init__(self, generos: list[str], todos: bool) -> None:
        self.session = Session()
        self.logger = logging.getLogger(__name__)
        self.todos = todos
        self.generos = generos

        url = 'https://www.sympla.com.br/api/discovery-bff'

        if len(generos) == 0 or len(generos) > 1:
            gen = '/search-closed/event?&cl=17-festas-e-shows'
            self.ver_generos = False
        else:
            gen = f'/search/event?s={generos[0]}&cl=17-festas-e-shows'
            self.ver_generos =True

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

    def pesquisar_eventos(self, locais: list[str], date_list):
        self.logger.info(f'Iniciando pesquisa de eventos de em São Paulo no site Sympla...')

        ver_local = False

        if len(locais) > 0:
            ver_local = True

        i = 1
        total_paginas = 1

        while True:
            if i == 1:
                page = ''
            else:
                page = f'&page={i}'

            res = self.session.get(self.url2+page, headers=self.headers, cookies=self.cookies)
            data = res.json()['data']

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

            print(f'Pagina {i}')

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

                try:
                    descricao = soup.select(
                        '#__next > section.sc-b281498b-0.ilWENo > div > div > div.sc-537fdfcb-0.bdUbUp')[0].text
                except IndexError:
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
                        continue
                    try:
                        descricao = json_res['operator_info']
                    except KeyError:
                        raw = json_res['description']['raw']
                        soup2 = bs(raw, 'html.parser')
                        descricao = soup2.text

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
                        if self.ver_generos:
                            if not any(genero for genero in self.generos if genero.lower() == evento_genero.lower()):
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

    def pesquisar_eventos(self, generos: list[str], locais: list[str], data_list: datetime):
        if len(generos) == 0:
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
                        if not any(genero for genero in generos if genero.lower() == evento_genero.lower()):
                            continue
                    if ver_locais:
                        if not any(local for local in locais if local.lower() in evento['local'].lower()):
                            continue
                    if len(data_list) == 2:
                        if date_event < data_list[0] or date_event > data_list[1]:
                            continue

                self.eventos.append(evento)
                self.logger.info(f'{evento["nome"]}')

        print('Pesquisa finalizada.')
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

    def pesquisar_eventos(self, generos: list[str], locais: list[str], data_list: datetime):
        if len(generos) == 0:
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
                        if not any(genero for genero in generos if genero.lower() == evento_genero.lower()):
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


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('log.log'), logging.StreamHandler()])

    # sympla = Sympla(['Rock Nacional'], True)
    # print(sympla.pesquisar_eventos('São Paulo', datetime.now()))


    # clube = ClubdoIngresso()
    # pprint(clube.pesquisar_eventos())

    # eventim = Eventim('Rock Nacional')
    # print(eventim.pesquisar_eventos())

    uhuu = Uhuu(True)
    pprint(uhuu.pesquisar_eventos([], [], datetime.now()))

# Gêneros:
# Shows Internacionais
# Shows Nacionais|MPB
# Shows Nacionais|Pop Nacional
# Shows Nacionais|Rock Nacional

# class Eventim:
#     def __init__(self, genero: str) -> None:
#         self.session = Session()
#         self.eventos = []
#         self.logger = logging.getLogger(__name__)
#         self.genero = genero

#         if 'Internacional' in genero:
#             f_genero = f'Shows Internacionais|{genero}'
#         else:
#             f_genero = f'Shows Nacionais|{genero}'

#         self.url = 'https://public-api.eventim.com/websearch/search/api/exploration/v2/productGroups'

#         self.headers = {
#             'authority': 'public-api.eventim.com',
#             'accept': '*/*',
#             'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
#             'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
#         }

#         self.payload = {
#             'webId': 'web__eventim-com-br',
#             'language': 'pt',
#             'retail_partner': 'BR1',
#             'categories': f_genero,
#             'city_ids': '943',
#             'sort': 'Recommendation',
#             'in_stock': 'true'
#         }

#     async def get_local_async(self, link: str):
#         async with sync_playwright() as p:
#             browser = await p.chromium.launch(headless=True, args=['--disable-http2'])
#             page = await browser.new_page()
#             await page.set_extra_http_headers({
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
#             })

#             try:
#                 await page.goto(link, timeout=60000)
#                 await page.wait_for_load_state('load')

#                 await page.wait_for_selector('p.paragraph.external-content', timeout=60000)
#                 endereco = await page.query_selector('p.paragraph.external-content').text_content()
#                 endereco = endereco.split('\n')[1]

#                 await browser.close()

#                 return endereco
#             except Exception as e:
#                 self.logger.error(e)
#                 endereco = None
#             finally:
#                 browser.close()
            
#             return endereco
    
#     def get_local(self, link: str):
#         try:
#             loop = asyncio.new_event_loop()
#             asyncio.set_event_loop(loop)
#             return loop.run_until_complete(self.get_local_async(link))
#         except Exception as e:
#             self.logger.error(e)
#             return None
#         finally:
#             loop.close()

#     def pesquisar_eventos(self):
#         self.logger.info(f'Iniciando pesquisa de eventos de {self.genero} em São Paulo no site Eventim...')
#         i = 0
#         while True:
#             i += 1
#             print(f'Pagina {i}')

#             res = self.session.get(self.url, headers=self.headers, params=self.payload)
#             shows = res.json()['productGroups']
#             total_paginas = res.json()['totalPages']

#             self.logger.info(f'Foram encontrados {len(shows)} eventos de {self.genero}.')

#             for show in shows:
#                 evento = {
#                     'nome': '',
#                     'local': '',
#                     'dataHora': '',
#                     'genero': '',
#                     'link': '',
#                     'site': 'Eventim'
#                 }

#                 num_produtos = show['productCount']
#                 produtos = show['products']

#                 for produto in produtos:
#                     evento['nome'] = produto['name']
#                     data_hora = produto['typeAttributes']['liveEntertainment']['startDate']
#                     data = datetime.strftime(datetime.strptime(data_hora.split('T')[0], '%Y-%m-%d'), '%d/%m/%Y')
#                     evento['dataHora'] = convert_to_datetime(data)
#                     evento['link'] = produto['link']
#                     try:
#                         evento['genero'] = self.genero.split('|')[1]
#                     except IndexError:
#                         evento['genero'] = self.genero

#                     headers = {
#                         'authority': 'www.eventim.com.br',
#                         'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
#                         'accept-language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
#                         'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
#                         'sec-ch-ua-mobile': '?0',
#                         'sec-ch-ua-platform': '"Windows"',
#                         'sec-fetch-dest': 'document',
#                         'sec-fetch-mode': 'navigate',
#                         'sec-fetch-site': 'same-origin',
#                         'sec-fetch-user': '?1',
#                         'upgrade-insecure-requests': '1',
#                         'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
#                     }
#                     # res_pro = self.session.get(produto['link'], headers=headers)
#                     # if res.status_code == 403:
#                     #     print('Erro 403: Acesso negado')
#                     # else:
#                     #     soup = bs(res_pro.content, 'html.parser')
#                     #     endereco = soup.find('p', {'class': 'paragraph external-content'}).text
#                     #     endereco = endereco.split('\n')[1]
#                     #     evento['local'] = endereco

#                     endereco = self.get_local(produto['link'])
#                     evento['local'] = endereco

#                     self.logger.info(evento['nome'])

#                     self.eventos.append(evento)

#             if i == total_paginas:
#                 self.eventos = [dict(t) for t in {tuple(evento.items()) for evento in self.eventos}]
#                 return self.eventos
