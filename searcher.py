from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os
from dotenv import load_dotenv
from time import sleep


class Groq:
    def __init__(self):
        key = os.getenv('GROQ_API_KEY')

        if not key:
            load_dotenv('data/.env')
            key = os.getenv('GROQ_API_KEY')    

        chat = ChatGroq(model='meta-llama/llama-4-scout-17b-16e-instruct', max_tokens=5, temperature=0.1)

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
    nome = 'LAUANA PRADO RAIZ - SÃO PAULO/SP'
    descricao = """
CENTENÁRIO SMCC – UMA NOITE PARA FICAR NA HISTÓRIA!
Chegou em São Paulo a festa mais RAIZ do Brasil! Agora o petêco vai cair a foia! Prepare-se para uma experiência única, comandada por Lauana Prado com muita moda boa.  
Só pra quem é raiz de verdade!  
"""

    groq = Groq()
    print(groq.definir_genero(nome, descricao))
