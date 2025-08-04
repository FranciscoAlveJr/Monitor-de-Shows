from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
from time import sleep
import streamlit as st


class Groq:
    def __init__(self):
        key = os.getenv('GROQ_API_KEY')

        if not key:
            key = st.secrets['GROQ_API_KEY']

        model = 'meta-llama/llama-4-scout-17b-16e-instruct' # Principal
        # model = 'llama3-70b-8192' # Teste
        chat = ChatGroq(model=model, max_tokens=5, temperature=0.1, api_key=key)

        prompt = ChatPromptTemplate.from_messages([
            ('system', 'O nome e a descrição de um espetáculo musical serão fornecidos. Responda apenas um gênero musical específico entre: (Rock Nacional, Rock Internacional, Pop Nacional, Pop Internacional e MPB). Caso não seja nenhum destes, retorne "outro".'),
            ('human', '{input}')
        ])
        parser = StrOutputParser()

        self.chain = prompt | chat

    def definir_genero(self, titulo, descricao):
        input = f'{titulo} - {descricao}'
        response = self.chain.invoke({'input': input})
        genero = response.content
        total_tokens = response.usage_metadata['total_tokens']
        return [genero, total_tokens]

if __name__ == '__main__':
    nome = ' 21h30 • ROCK • DIRE STRAITS EXPERIENCE by GUI CICARELLI '
    descricao = """
Uma noite com os clássicos do Dire Straits!
Prepare-se para uma noite inesquecível no palco do Bourbon Street Music Club! Os grandes clássicos do Dire Straits ganham vida em um show eletrizante com Gui Cicarelli e sua banda, recriando toda a atmosfera e sonoridade que marcaram gerações. 
Com interpretações fiéis e emocionantes, o espetáculo Dire Straits Experience traz sucessos como Sultans of Swing, Money for Nothing, Brothers in Arms, Romeo and Juliet e muito mais — em uma homenagem impecável à genialidade de Mark Knopfler e sua icônica banda britânica.
"""

    groq = Groq()
    print(groq.definir_genero(nome, descricao))
