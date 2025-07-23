from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import base64
import json
from datetime import datetime
import logging
# from main import Shows

from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.utils import formataddr

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.FileHandler('log.log'), logging.StreamHandler()])

class GmailSenderAPI:
    def __init__(self, excel_bytes, filename, token_ref, emails_ref):
        self.logger = logging.getLogger(__name__)

        self.SCOPES = [
            'https://www.googleapis.com/auth/gmail.compose',
            'https://www.googleapis.com/auth/gmail.send'
        ]
        self.credentials_file = 'data/client_secret.json'
        # self.token_file = 'data/token.json'
        self.token_ref = token_ref
        self.emails_ref = emails_ref
        self.service = None
        self.excel_bytes = excel_bytes
        self.filename = filename

    def load_credentials(self):
        token_info = self.token_ref.get().to_dict()
        if not token_info:
            self.logger.error("Token não encontrado no banco de dados. Execute a autenticação local primeiro.")
            return None
        
        creds = Credentials.from_authorized_user_info(token_info)
        return creds
    
    def save_credentials(self, creds):
        creds_json = creds.to_json()
        token_info = json.loads(creds_json)
        self.token_ref.set(token_info)

    def authenticate(self):
        """Autentica usando OAuth 2.0"""
        creds = self.load_credentials()
        
        # # Carrega token existente
        # if os.path.exists(self.token_file):
        #     creds = Credentials.from_authorized_user_file(self.token_file, self.SCOPES)
        
        def logar():
            flow = InstalledAppFlow.from_client_secrets_file(
                self.credentials_file, self.SCOPES)
            creds = flow.run_local_server(port=0)
            return creds

        # Se não há credenciais válidas, faz login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Token expirado. Atualizando...")
                try:
                    creds.refresh(Request())
                except RefreshError:
                    creds = logar()
            else:
                creds = logar()
            
            self.save_credentials(creds)
            self.logger.info("Token atualizado e salvo.")
        
        try:
            self.service = build('gmail', 'v1', credentials=creds)
            return True
        except Exception as e:
            self.logger.exception(f"Erro ao conectar ao Gmail: {e}")
            return False
    
    def create_message(self):
        titulo = f'🔔 Shows em São Paulo'

        corpo_email = f"""
        {titulo}
        
        Pesquisa do dia {datetime.now().strftime('%d/%m/%Y')} foi concluída.
        Sua Planilha de eventos está pronta!
        

        ---
        Esta é uma mensagem automática. Não responda este email.

        """

        # with open('data/email.json', 'r') as f:
        #     to_emails = json.load(f)['emails']

        to_emails = self.emails_ref.get().to_dict()['emails']

        # Cria uma mensagem de email
        try:
            msg = MIMEMultipart()
            msg['To'] = ', '.join(to_emails)
            msg['From'] = formataddr(('Monitor de Shows em São Paulo', 'franciscoalves.dev@gmail.com'))
            msg['Subject'] = titulo
            
            msg.attach(MIMEText(corpo_email, "plain", "utf-8"))

            # with open(self.file_path, 'rb') as attachment:
            #     part = MIMEBase('application', 'octet-stream')
            #     part.set_payload(attachment.read())
            
            # encoders.encode_base64(part)
            
            # filename = os.path.basename(self.file_path)
            # part.add_header(
            #     'Content-Disposition',
            #     f'attachment; filename= {filename}',
            # )

            part = MIMEBase('application', 'octet-stream')
            part.set_payload(self.excel_bytes)
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={self.filename}.xlsx')
            
            msg.attach(part)

            
            raw_message = base64.urlsafe_b64encode(msg.as_bytes()).decode('utf-8')
            return {'raw': raw_message}
        except Exception as e:
            self.logger.exception(f"Erro ao criar mensagem de email: {e}")
            return None

    def send_email(self, message):
        if not self.service:
            self.logger.error("Autenticação falhou. Por favor, autentique-se novamente.")
            return None
        
        try:
            response = self.service.users().messages().send(
                userId="me", body=message).execute()
            
            msg_id = response['id']
            return response
        
        except HttpError as error:
            self.logger.error(f"Erro ao enviar email: {error}")
            return None
        except Exception as e:
            self.logger.error(f"Erro ao enviar email: {e}")
            return None
        
    def enviar_email(self):
        message = self.create_message()
        if message:
            return self.send_email(message)
        return None
    
# Exemplo de uso da API
def main_api(excel_bytes, nome_planilha, token_ref, emails_ref):
    gmail_api = GmailSenderAPI(excel_bytes, nome_planilha, token_ref, emails_ref)
    
    if gmail_api.authenticate():
        gmail_api.enviar_email()
        

# if __name__ == "__main__":
#     shows = Shows(genero='')

#     db = shows.get_db()
#     token_ref = db.collection('streamlit_secrets').document('cnXygf2mVmWqJwvmgQH2')
#     emails_ref = db.collection('streamlit_secrets').document('emails_json')

#     main_api(r'Rock Internacional_12072025.xlsx', 'Rock Internacional', token_ref, emails_ref)