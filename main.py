from scraping import ClubdoIngresso, Uhuu, Sympla
import pandas as pd
import logging
from send_gmail import main_api
from datetime import datetime
import io
import os
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
import json

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('log.log'), logging.StreamHandler()])


class Shows:
    def __init__(self, genero: str, locais: list=[], data=datetime.now(), todos=True) -> None:
        self.logger = logging.getLogger(__name__)
        self.data = data
        self.locais = locais

        self.genero = genero
        self.clube = ClubdoIngresso(todos)
        # self.eventim = Eventim(genero)
        self.uhuu = Uhuu(todos)
        self.sympla = Sympla(genero, todos)

    def nome_planilha(self):
        data = datetime.now().strftime('%H%M%S%d%m%Y')
        return f'eventos_{data}'
    
    def excel_to_bytes(self, df: pd.DataFrame):
        df['Data'] = pd.to_datetime(df['Data'])
        buffer = io.BytesIO()
        df = df.fillna('')
        df = df.replace('\x00', '', regex=True)
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Eventos')
        buffer.seek(0)
        return buffer.getvalue()

    @staticmethod
    def acessar_secrets():
        credenciais = os.getenv('firebase_credentials')
        if credenciais:
            creds = json.loads(credenciais)
        else:
            creds_value = st.secrets['firebase_credentials']
            creds = {
                'type': creds_value['type'],
                'project_id': creds_value['project_id'],
                'private_key_id': creds_value['private_key_id'],
                'private_key': creds_value['private_key'],
                'client_email': creds_value['client_email'],
                'client_id': creds_value['client_id'],
                'auth_uri': creds_value['auth_uri'],
                'token_uri': creds_value['token_uri'],
                'auth_provider_x509_cert_url': creds_value['auth_provider_x509_cert_url'],  
                'client_x509_cert_url': creds_value['client_x509_cert_url'],
                'universe_domain': creds_value['universe_domain']
            }

        return creds

    def get_db(self):
        if not firebase_admin._apps:
            creds_dict = self.acessar_secrets()
            cred = credentials.Certificate(creds_dict)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        return db

    def pesquisar_eventos(self):
        sympla = self.sympla.pesquisar_eventos(self.locais, self.data)
        # eventim = self.eventim.pesquisar_eventos()
        clube = self.clube.pesquisar_eventos(self.genero, self.locais, self.data)
        uhuu = self.uhuu.pesquisar_eventos(self.genero, self.locais, self.data)

        self.eventos = sympla + clube + uhuu

        return self.eventos
    
    def criar_excel_local(self):
        nome = self.nome_planilha()
        colunas = ['Nome', 'Endereço', 'Data e Hora', 'Gênero', 'Link', 'Site']
        df = pd.DataFrame(self.eventos)
        df.columns = colunas
        with pd.ExcelWriter(f'data/{nome}.xlsx', engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Eventos')

        self.logger.info(f'Planilha de eventos criada.')

    def criar_df(self):
        colunas = ['Nome', 'Endereço', 'Data', 'Gênero', 'Link', 'Site']
        df = pd.DataFrame(self.eventos)
        df.columns = colunas
        df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y')

        return df
    
    def enviar_email(self, excel_bytes, token_ref, emails_ref):
        nome = self.nome_planilha()
        main_api(excel_bytes, nome, token_ref, emails_ref)
        self.logger.info(f'Email enviado.')


if __name__ == '__main__':
    shows = Shows(genero='')
    shows.pesquisar_eventos()
    df = shows.criar_df()
    excel_bytes = shows.excel_to_bytes(df)
    db = shows.get_db()
    token_ref = db.collection('streamlit_secrets').document('cnXygf2mVmWqJwvmgQH2')
    emails_ref = db.collection('streamlit_secrets').document('emails_json')
    shows.enviar_email(excel_bytes, token_ref, emails_ref)
