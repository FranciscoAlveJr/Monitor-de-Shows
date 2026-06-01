# 🎵 Monitor de Shows SP - Inteligência Artificial & RPA

Este projeto é um **MVP (Minimum Viable Product)** focado na engenharia de dados e automação para monitorar, centralizar e classificar eventos culturais e musicais na cidade de São Paulo. 

O ecossistema realiza web scraping em mais de 10 plataformas de ingressos, utiliza **Agentes de IA (LangChain)** para classificação inteligente de gêneros musicais e distribui relatórios analíticos formatados. A aplicação é dividida entre um portal analítico interativo e um pipeline assíncrono de disparos semanais automatizados.

---

## 📐 Arquitetura do Ecossistema

```text
[Web Scraping: 11 Portais] ➔ [Pipeline de Ingestão / Requests & BS4]
                                            │
                                 [Filtro Semântico / LangChain LLM]
                                            │
               ┌────────────────────────────┴────────────────────────────┐
               ▼                                                         ▼
    [Interface Interativa]                                    [Pipeline Assíncrono]
    - Frontend Streamlit                                      - Execução Cron (Ter/Sex)
    - Filtros em Tempo Real (Pandas)                          - Orquestração: GitHub Actions
    - Download de Relatório .xlsx                             - Disparo de E-mails com Anexos
```

---

## 🛠️ Tecnologias e Infraestrutura

* **Python** - Linguagem core de desenvolvimento.
* **Streamlit** - Frontend interativo para o portal de dados e visualização em tempo real.
* **LangChain** - Orquestração do Agente de IA para processamento de linguagem natural (NLP) e classificação de gêneros.
* **Pandas** - Manipulação, tratamento, filtragem e estruturação dos dados coletados.
* **Requests / BeautifulSoup4** - Motores de extração e web scraping para coleta de dados textuais e metadados.
* **Docker** - Containerização da aplicação para garantia de paridade de ambientes.
* **GCP / Firebase** - Hospedagem da aplicação, nuvem computacional e gerenciamento de credenciais.
* **GitHub Actions** - Engine de CI/CD responsável pelo deploy automatizado e pelo agendamento (*Cron Job*) da rotina de disparos semanais.

---

## 💻 Módulos do Sistema

### 1️⃣ Interface do Usuário (Portal Web Streamlit)
Oferece um painel dinâmico onde o usuário consulta o inventário de eventos unificado, permitindo a aplicação de filtros em tempo real e geração de relatórios `.xlsx` sob demanda.

* **Filtro por Gênero (IA):** Como os portais de origem não possuem padronização de tags, um Agente de IA analisa semanticamente o título e a descrição do evento para determinar o gênero musical exato.
* **Filtro por Local:** Permite seleção múltipla de casas de show, arenas e bares mapeados.
* **Filtro por Data:** Implementação de intervalo temporal dinâmico (*Date Range*) que assume o dia atual como ponto de partida padrão.

> 💡 *Nota: As consultas realizadas via interface geram outputs em tempo real baseados em DataFrames do Pandas e não interferem na esteira de processamento agendada.*

### 2️⃣ Pipeline de Pesquisa Automática (Orquestração Batch)
Uma esteira assíncrona executada de forma automatizada duas vezes por semana (terças e sextas-feiras) via rotina programada.

* O sistema realiza uma varredura massiva de baixa granularidade para capturar o maior volume de dados possível.
* O Agente de IA atua de forma preditiva, filtrando e validando se os eventos mapeados pertencem ao escopo estratégico dos 5 gêneros principais da plataforma.
* Após a conclusão e higienização dos dados com Pandas, a aplicação se conecta a um servidor SMTP para disparar relatórios analíticos em formato Excel diretamente para o e-mail dos usuários cadastrados.

---

## 🌐 Escopo de Coleta (Fontes de Dados Mapeadas)

A esteira de robôs foi construída respeitando as boas práticas de requisições HTTP, realizando a extração de dados nos seguintes portais:

* [Sympla](https://www.sympla.com.br)
* [Clube do Ingresso](https://www.clubedoingresso.com)
* [Uhuu](https://uhuu.com)
* [Eventim](https://www.eventim.com.br/)
* [Ticket360](https://www.ticket360.com.br)
* [Ingresse](https://www.ingresse.com/)
* [Tickets For Fun](https://www.ticketsforfun.com.br)
* [Tickets Master](https://www.ticketmaster.com.br)
* [Tokio Marine Hall](https://www.tokiomarinehall.com.br)
* [Cafe Piu Piu](http://cafepiupiu.com.br)
* [Bourbon Street](https://www.bourbonstreet.com.br)

---

## 🔒 Segurança e Gestão de Credenciais

Em conformidade com as boas práticas de segurança e governança de dados, nenhuma chave de API, credencial de servidor SMTP ou token de acesso está exposto no código-fonte. 

* As variáveis de ambiente de produção são injetadas em tempo de execução através do **Streamlit Secrets Manager** e criptografadas no cofre de dados do **GitHub Actions Secrets** para a esteira de CI/CD.

---

## ⚙️ Como Executar o Projeto Localmente

```bash
# 1. Clone o repositório
git clone [https://github.com/FranciscoAlveJr/monitor-shows.git](https://github.com/FranciscoAlveJr/monitor-shows.git)

# 2. Acesse o diretório
cd monitor-shows

# 3. Certifique-se de configurar suas variáveis de ambiente (.env) e execute via Docker
docker build -t monitor-shows .
docker run -p 8501:8501 monitor-shows
```
