from keys import pop_internacional, pop_nacional, rock_internacional, rock_nacional, nacionalidades, rock, pop, mpb
import re

def maior_genero(generos: dict, texto):
    texto_limpo = re.sub('[-+={};:!@#$%^&*’_<>|~,(.)\n]', '', texto)
    texto_l = texto_limpo.lower().replace('’', "'")
    texto_split = texto_l.split()
    scores = {}

    for genero, tags in generos.items():
        score = 0
        tags_achadas = []
        for tag in tags:
            tag1 = tag.split()[0] if len(tag.split()) > 0 else tag
            tag2 = tag.split()[1] if len(tag.split()) > 1 else tag1
            tag3 = tag.split()[2] if len(tag.split()) > 2 else tag1

            if tag1 in texto_l and tag2 in texto_l and tag3 in texto_l:
                score += 1
                tags_achadas.append(tag)
        
        if score > 0:
            scores[genero] = score
        
    if not scores:
        return {"Gênero": 'Outro', "matches": 0}
    else:
        maior = float('-inf')
        maiores = []

        for genero, score in scores.items():
            if score > maior:
                maior = score
                maiores = [genero]
            elif score == maior:
                maiores.append(genero)

        return maiores

def separar_texto(texto):
    texto_limpo = re.sub('[,(.)\n]', '', texto)
    texto_l = texto_limpo.lower()
    texto_split = texto_l.split()
    return texto_split

# texto_split = separar_texto(texto)

def definir_genero(titulo: str, descricao: str):
    generos = {
        'Rock': rock,
        'Pop': pop,
        'MPB': mpb
    }

    texto = f'{titulo} {descricao}'

    maiores_generos = maior_genero(generos, texto)

    if len(maiores_generos) == 1:
        genero = maiores_generos[0]

        if genero == 'Pop':
            nacional = pop_nacional
            internacional = pop_internacional + nacionalidades
        elif genero == 'Rock':
            nacional = rock_nacional
            internacional = rock_internacional + nacionalidades
        elif genero == 'MPB':
            genero_final = genero
            return genero_final
    elif isinstance(maiores_generos, dict):
        genero_final = maiores_generos['Gênero']
        return genero_final
    else:
        genero_final = '/'.join(maiores_generos)
        return genero_final

    nacoes = {'Nacional': nacional, 'Internacional': internacional}

    maiores_nacoes = maior_genero(nacoes, texto)

    if len(maiores_nacoes) == 1:
        nacao = maiores_nacoes[0]
    else:
        nacao = ''

    genero_final = f'{genero} {nacao}'

    return genero_final

if __name__ == '__main__':
    titulo = 'Rodrigo Teaser - Tributo ao Rei do Pop'
    descricao = """
Rodrigo Teaser Tributo ao Rei do Pop 
O maior tributo ao Michael Jackson do mundo 
Com 12 anos de sucesso de público e crítica o Show já passou por 8 países , 4 continentes mais de 300 cidades e já foi visto por mais de um milhão de pessoas .

Retornando de uma turnê pelos EUA , China e África Rodrigo volta a Fortaleza com novo show, novas músicas e novos figurinos. 

Rodrigo traz ao palco do Teatro Rio Mar um show com uma mega promoção, elevadores de palco, catapulta , banda ao vivo, bailarinos.

Thriller, Billie Jean, Black or White, Human Nature e Beat It, são alguns dos inúmeros hits do Rei do Pop a serem reproduzidos durante o espetáculo Tributo ao Rei do Pop, em homenagem ao eterno cantor Michael Jackson.

Uma celebração ao maior artista de todos os tempos."""


    print(definir_genero(titulo, descricao))