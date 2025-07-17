import streamlit as st
import pandas as pd
from datetime import datetime, date
import io
from main import Shows
import firebase_admin
from firebase_admin import credentials, firestore

locais_list = ['Bar - Blue note', 'Bar - Bourbon street', 'Bar - Cafe Piu Piu', 'Bar - Manifesto bar', 'Casa de Show - Allianz', 'Casa de Show - Audio Club', 'Casa de Show - Bona', 'Casa de Show - Carioca Club', 'Casa de Show - Casa Natura', 'Casa de Show - Casa de Francisca', 'Casa de Show - Espaço Unimed', 'Casa de Show - Tokio Marine Hall', 'Casa de Show - Vibra São Paulo', 'Teatro - J. Safra', 'Teatro Paulo Altran', 'Teatro Sérgio Cardoso', 'Teatro Alpha', 'Teatro B32', 'Teatro Bibi Ferreira', 'Teatro Bradesco', 'Teatro Bravos', 'Teatro Cacilda Becker', 'Teatro Claro', 'Teatro Eva Herz', 'Teatro Faap', 'Teatro Frei Caneca', 'Teatro Gazeta', 'Teatro Liberdade', 'Teatro Municipal', 'Teatro Porto', 'Teatro Procópio Ferreira', 'Teatro Renault', 'Teatro Santander', 'Teatro UOL', 'Theatro São Pedro']

def excel_to_bytes(df: pd.DataFrame):
    df['Data'] = pd.to_datetime(df['Data'])
    buffer = io.BytesIO()
    df = df.fillna('')
    df = df.replace('\x00', '', regex=True)
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Eventos')
    buffer.seek(0)
    return buffer.getvalue()


st.set_page_config(
    layout="wide",
    page_icon="🎵",
    page_title="Monitor de Shows em São Paulo",
    )

@st.cache_resource
def get_db():
    if not firebase_admin._apps:
        creds_value = st.secrets['firebase_credentials']
        creds_dict = {
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
        cred = credentials.Certificate(creds_dict)
        firebase_admin.initialize_app(cred)
    db = firestore.client()
    return db

db = get_db()
token_ref = db.collection('streamlit_secrets').document('cnXygf2mVmWqJwvmgQH2')
emails_ref = db.collection('streamlit_secrets').document('emails_json')

# Header
st.title("Monitor de Shows em São Paulo")
st.markdown('---')

if 'dados_pesquisa' not in st.session_state:
    st.session_state.dados_pesquisa = None

with st.sidebar:
    st.header('🔎 _Pesquisar_', divider='gray', help='Faça pesquisas filtrando por gênero, local ou data, ou faça uma pesquisa sem filtros. Os resultados aparecerão ao lado com visualização e opção de download.')

    # st.markdown('---')

    todos = st.checkbox('Marque se preferir a pesquisa sem filtros')

    st.subheader('Filtrar por:')
    # Gênero
    genero = st.multiselect(
        'Gênero',
        ['Rock Nacional', 'Rock Internacional', 'Pop Nacional', 'Pop Internacional', 'MPB'],
        placeholder = 'Todos os gêneros',
        disabled = todos,
        help = 'Se preferir por todos os gêneros, deixe vazio.'
    )

    # Local
    locais = st.multiselect(
        'Local',
        locais_list,
        placeholder = 'Todos os locais',
        disabled = todos,
        help = 'Se preferir por todos os locais, deixe vazio.'
    )

    # Data
    data_min = date.today()
    data = st.date_input(
        'Data',
        value=('today',),
        min_value='today',
        format='DD/MM/YYYY',
        disabled=todos,
        help='Primeiro marque a data de início e, depois, uma data final. Se não quiser uma data final, marque apenas a data inicial, ou deixe como está, e clique fora da caixa.'
    )

    # Pesquisar
    if 'pesquisar_disabled' not in st.session_state:
        st.session_state.pesquisar_disabled = False
    
    for i, local in enumerate(locais):
        if len(local.split(' - ')) == 2:
            locais[i] = local.split(' - ')[1]
    
    def pesquisar():
        st.session_state.pesquisar_disabled = True
        with st.spinner(f'Pesquisando...'):
            shows = Shows(genero, locais, data, todos)
            shows.pesquisar_eventos()
            df_result = shows.criar_df()
            st.session_state.dados_pesquisa = df_result
            st.session_state.genero = genero
        st.success(f'Foram encontrados {len(df_result)} eventos.')
        st.session_state.pesquisar_disabled = False

    if st.button('Pesquisar', type='primary', on_click=pesquisar, disabled=st.session_state.pesquisar_disabled):
        pass

    st.markdown('---')

    # Email
    st.header('📧 _Configurar E-mail_', divider='gray', help='Salve os emails que receberão notificação da pesquisa diária. Abaixo, poderá ver os emails salvos. Também há a opção de apagar os e-mails, basta clicar no ícone de lixeira do lado e o e-mail correspondente será apagado.')

    # st.subheader('Configurar E-mail:')

    # try:
    #     with open('data/email.json', 'r') as f:
    #         email_dict = json.load(f)
    #         saved_emails = email_dict['emails']
    # except json.decoder.JSONDecodeError:
    #     saved_emails = []

    saved_emails = emails_ref.get().to_dict()['emails']

    if len(saved_emails) > 0:
        if len(saved_emails) == 1:
            salvo = 'E-mail salvo'
        else:
            salvo = 'E-mails salvos'

        with st.expander(salvo, expanded=True):
            for i, email in enumerate(saved_emails):
                col1, col2 = st.columns([6, 1])

                with col1:
                    st.write(email)
                with col2:
                    if st.button('', key=f'delete_{i}', help='Deleta o e-mail.', type='tertiary', icon='🗑️'):
                        saved_emails.pop(i)
                        email_dict = {'emails': saved_emails}
                        emails_ref.set(email_dict)

                        # with open('data/email.json', 'w') as f:
                        #     json.dump(email_dict, f)
                        st.rerun()
    
    if "email_input" not in st.session_state:
        st.session_state.email_input = ""
    if 'clear_input' not in st.session_state:
        st.session_state.clear_input = False
    
    if st.session_state.clear_input:
        email_value = ''
        st.session_state.clear_input = False
    else: 
        email_value = st.session_state.get('email_field', '')

    email = st.text_input('E-mail:', placeholder='Insira aqui um email válido', key='email_field', value=email_value)
    
    if st.button('Salvar'):
        if email:
            saved_emails.append(email)
            email_dict = {'emails': saved_emails}
            emails_ref.set(email_dict)

            # with open('data/email.json', 'w') as f:
            #     json.dump(email_dict, f)
            # st.success('E-mail salvo com sucesso!')

            st.session_state.clear_input = True
            st.rerun()
        else:
            st.error('Por favor, insira um e-mail válido.')
    
    # if st.session_state.clear_input:
        # st.session_state.clear_input = False

    st.markdown('---')

if st.session_state.dados_pesquisa is not None:
    df = st.session_state.dados_pesquisa

    st.subheader('🎤 Resultados da Pesquisa')

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric('Total de registros', len(df), border=True)

    st.subheader('Eventos')
    
    # Filtro por período
    df_filtro = df.copy()

    data_min = date.today()
    data = st.date_input(
        'Filtrar por Período:',
        value=(data_min,),
        min_value=data_min,
        format='DD/MM/YYYY',
    )

    if len(data) == 2:
        df_filtro = df_filtro[
            (df_filtro['Data'].dt.date >= data[0]) &
            (df_filtro['Data'].dt.date <= data[1])
        ]

    df_filtro['Data'] = df_filtro['Data'].dt.strftime('%d/%m/%Y')
    st.dataframe(df_filtro, height=400, use_container_width=True, hide_index=True)

    # Exportar
    st.subheader('Exportar Eventos')
    dados = excel_to_bytes(df)
    st.download_button(
        label='📥 Exportar para Excel',
        data=dados,
        file_name=f'{genero}_{datetime.now().strftime("%d%m%Y")}.xlsx',
        mime='application/vnd.octet-stream',
    )

else:
    st.info('👈 Use o painel lateral para fazer uma pesquisa e visualizar os dados!')

    


