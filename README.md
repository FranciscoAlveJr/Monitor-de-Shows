# Monitor de Shows
MVP (Model-View-Presenter) que visa monitorar os eventos que ocorrem na cidade de São Paulo. Usando agente de IA para refinar os filtros por gênero.

O projeto é dividido em duas partes:
- **A interface de usuário**, feito em **Streamlit**, onde o usuário pode realizar pesquisas dos eventos do momento em sites de venda ingresso, casas de show e bares, podendo aplicar filtros de acordo com o gênero, o local e a data. Também é possível cadastrar um e-mail para receber os resultados semanalmente.
- **Pesquisa automática**, em que o usuário, com o e-mail cadastrado, receberá semanalmente os resultados em formato Excel.

## Interface
Aqui o usuário tem a opção de fazer uma pesquisa que, ao final, retornará uma tabela e um arquivo em `.xlsx` para fazer o download.
Para fazer a pesquisa, o usuário pode escolher definir filtros por:
- Gênero
- Local
- Data

### Gênero
Pode escolher um gênero específico, podendo escolher apenas um. Somente eventos do gênero escolhido serão apresentados na tabela e no arquivo `.xlsx`. Como nem todos os sites dividem os eventos por gênero, é usado um agente de IA simples que refina a pesquisa, usando como parâmetros o título e a descrição do evento.
### Local
Já a escolha do local não é obrigatória, sendo da opção do usuário filtrar por eles ou não.<br>
Ao optar por filtrar por local, é possível fazer escolha múltipla, onde o usuário pode escolher mais de uma opção.<br>
### Data
O filtro por data é feito no intervalo entre duas datas. Basta escolher a primeira data e, logo após, a segunda, o sistema retornará apenas os eventos contidos entre essas datas. Por padrão, a primeira data é o dia atual. Se o usuário não escolher a segunda data, o sistema entenderá que ele quer qualquer data à partir da atual.
<br>
<br>
>[!NOTE]
>Os dados da pesquisa por filtros serão retornados apenas na interface, com a tabela, que aparece na tela à direita, e na planilha Excel para download. Isso não interfare na pesquisa automática semanal

## Pesquisa Automática
Toda semana (terças e sextas) o sistema irá fazer uma pesquisa pelos eventos em São Paulo. <br>
Diferente da pesquisa via interface, o sistema faz a pesquisa com menos filtros, o que demanda muito mais tempo para executar.
Aqui também é utilizado o agente de IA para filtrar os gêneros, porém, diferentemente da interface, aqui o filto é feito de maneira mais ampla, abrangendo cinco gêneros, sendo que, se o gênero do evento não estiver entre os cinco, ele não é escolhido.

Após executar a pesquisa em todos sites de venda de ingresso, o sistema envia um alerta, via e-mail, para o usuário, contendo, em anexo, o arquivo em `.xlsx` com todos os eventos encontrados

## Sites pesquisados
Os seguintes sites serviram como base de pesquisa, tudo dentro dos limites de requisição das mesmas:
- [Sympla](https://www.sympla.com.br)
- [Clube do Ingresso](https://www.clubedoingresso.com)
- [Uhuu](https://uhuu.com)
- [Eventim](https://www.eventim.com.br/)
- [Ticket360](https://www.ticket360.com.br)
- [Ingresse](https://www.ingresse.com/)
- [Tickets For Fun](https://www.ticketsforfun.com.br)
- [Tickets Master](https://www.ticketmaster.com.br)
- [Tokio Marine Hall](https://www.tokiomarinehall.com.br)
- [Cafe Piu Piu](http://cafepiupiu.com.br)
- [Bourbon Street](https://www.bourbonstreet.com.br)

## Especificações Técnicas
As seguintes tecnologias foram utilizadas na produção deste sistema:
- Python
- Streamlit - Interface Web
- Pandas - Tratamento de dados
- Requests/BeautifulSoup - Web Scraping
- Langchain - Agente de IA
- GCP/Firebase - Deploy de credenciais
- GitHub Actions - Entrega e implantação remota

<br>

>[!NOTE]
>Todos os dados sensíveis, chaves de API, credenciais e afins foram devidamente salvos em locais seguros, seja na parte de *Secrets* do Streamlit, quanto nos *Secrets* do GitHub Actions.
