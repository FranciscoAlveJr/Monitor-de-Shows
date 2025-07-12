import streamlit as st
import pandas as pd
from datetime import datetime, date
import io
from main import Shows


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

# Header
st.title("Monitor de Shows em São Paulo")
st.markdown('---')

if 'dados_pesquisa' not in st.session_state:
    st.session_state.dados_pesquisa = None


with st.sidebar:
    st.header('🔎 Pesquisar')

    # Gênero
    genero = st.selectbox(
        'Gêneros',
        ['Rock Nacional', 'Rock Internacional', 'Pop Nacional', 'Pop Internacional', 'MPB'],
        placeholder='Escolha um gênero',
    )

    if 'pesquisar' not in st.session_state:
        st.session_state.pesquisar = True
    
    if st.button('Pesquisar', type='primary', disabled=st.session_state.pesquisar):
        with st.spinner(f'Pesquisando por {genero}...'):
            shows = Shows(genero)
            shows.pesquisar_eventos()
            df_result = shows.criar_df()


            st.session_state.dados_pesquisa = df_result
            st.session_state.genero = genero

        st.success(f'Foram encontrados {len(df_result)} eventos do gênero {genero}')
        st.session_state.pesquisar = False


    st.markdown('---')


    # # Email
    # st.header('🔔 Configurar E-mail')

    # with open('data/email.json', 'r') as f:
    #     email_dict = json.load(f)
    #     saved_email = email_dict['email']

    # if saved_email != '':
    #     st.write(f'Email salvo: {saved_email}')

    # email = st.text_input('E-mail:', placeholder='usuario@email.com')
    # email_dict = {'email': email}
    
    # if st.button('Salvar'):
    #     with open('data/email.json', 'w') as f:
    #         json.dump(email_dict, f)
    #     st.success('E-mail salvo com sucesso!')

    #     st.session_state.email = ""

    # st.markdown('---')

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

    


