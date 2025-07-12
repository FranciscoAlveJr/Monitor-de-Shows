from scraping import ClubdoIngresso, Eventim, Uhuu, Sympla
import pandas as pd
import logging
from send_gmail import main_api
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('log.log'), logging.StreamHandler()])


class Shows:
    def __init__(self, genero: str) -> None:
        self.logger = logging.getLogger(__name__)
        self.genero = genero
        self.clube = ClubdoIngresso()
        self.eventim = Eventim(genero)
        self.uhuu = Uhuu()
        self.sympla = Sympla()

    def nome_planilha(self):
        data = datetime.now().strftime('%H%M%S%d%m%Y')
        return f'{self.genero}_{data}'

    def pesquisar_eventos(self) -> None:
        sympla = self.sympla.pesquisar_eventos(self.genero)
        # eventim = self.eventim.pesquisar_eventos()
        clube = self.clube.pesquisar_eventos(self.genero)
        # uhuu = self.uhuu.pesquisar_eventos(self.genero)

        self.eventos = sympla + clube

        return self.eventos
    
    def criar_excel_local(self):
        nome = self.nome_planilha()
        colunas = ['Nome', 'Endereço', 'Data e Hora', 'Gênero', 'Link', 'Site']
        df = pd.DataFrame(self.eventos)
        df.columns = colunas
        with pd.ExcelWriter(f'data/{nome}.xlsx', engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Eventos')

        self.logger.info(f'Planilha de eventos criada.')

        main_api(f'data/{nome}.xlsx')

        self.logger.info(f'Email enviado.')

    def criar_df(self):
        colunas = ['Nome', 'Endereço', 'Data', 'Gênero', 'Link', 'Site']
        df = pd.DataFrame(self.eventos)
        df.columns = colunas
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')

        return df
    
    def enviar_email(self):
        nome = self.nome_planilha()
        main_api(f'data/{nome}.xlsx')
        self.logger.info(f'Email enviado.')


if __name__ == '__main__':
    shows = Shows('Rock Nacional')
    shows.pesquisar_eventos()
    shows.criar_excel_local()