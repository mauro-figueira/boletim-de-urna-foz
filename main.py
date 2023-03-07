import pandas as pd
import dash
from dash import Dash, dcc, html, Input, Output ,State
from dash import dash_table
import smtplib
import ssl

app = dash.Dash()

votos = pd.read_excel('Votação por Partido Por Bairro.xlsx')
válidos_bairros = pd.read_excel('Votos Válidos Bairro.xlsx')
quociente_eleitoral = 127574//15
quociente_partidário = votos.groupby('Partido').sum()['SomaDeVotos'].values//quociente_eleitoral

def total_partido():
  '''Esta é a função que lista o desempenho de todos os partidos nos votos totais da cidade.
  Mostra o total de votos nominais e o percentual em relação aos 131.102 votos válidos de Foz do Iguaçu
  para vereador nas eleições de 2020.'''
  return pd.DataFrame({
    'Partido' : votos['Partido'].unique(),
    'Total Votos': votos.groupby('Partido').sum()['SomaDeVotos'].values,
    'Porcentagem %': ((votos.groupby('Partido').sum()['SomaDeVotos'].values/válidos_bairros['Válidos Vereador'].sum())*100).round(2),
    'Quociente': quociente_partidário
    }).sort_values('Porcentagem %', ascending=False).reset_index(drop=True)

def partidos(partido, ordem = 'Bairro'):
  '''Esta é a função que lista o desempenho, em cada bairro, do partido selecionado
  Lista de argumentos:
  partido: digite em caixa alta o nome do partido desejado.
  ordem: escolha a ordem entre "Porcentagem" e "Votos".
  '''
  partido = partido.upper()
  from numpy import setdiff1d
  df = votos.loc[votos['Partido']==partido, ['Bairro', 'SomaDeVotos']].copy()
  válidos = válidos_bairros[['Bairro', 'Válidos Vereador']].copy()
  faltantes = setdiff1d(válidos_bairros['Bairro'], votos.loc[votos['Partido']== partido, 'Bairro'].reset_index(drop=True))
  válidos = válidos_bairros.loc[~válidos_bairros['Bairro'].isin(faltantes[:])].copy()
  df['Válidos'] = válidos['Válidos Vereador'].values
  df['Porcentagem %'] = ((df['SomaDeVotos']/df['Válidos'])*100).round(2)
  ordem = ordem
  if partido in votos['Partido'].unique():
    if ordem == 'Porcentagem':
      return df.sort_values('Porcentagem %', ascending=False).reset_index(drop=True)
    elif ordem == 'Votos':
      return df.sort_values('SomaDeVotos', ascending=False).reset_index(drop=True)
    elif ordem == 'Bairro':
      return df.sort_values('Bairro').reset_index(drop=True)
  else:
    print(f"Partido não encontrado. Digite o nome do partido em caixa alta. Lista de partidos: {votos['Partido'].unique()}")

def bairros(bairro):
  '''Esta função lista o desempenho de cada partido no bairro escolhido.
  Digite o nome do bairro no argumento único da função para retornar a lista com o resultado ordenado a partir do mais bem votado.'''
  bairro = bairro
  df = pd.DataFrame(votos.groupby(['Bairro', 'Partido']).sum())
  if bairro in df.index:
    válidos = válidos_bairros.loc[válidos_bairros['Bairro'] == bairro, 'Válidos Vereador'].values.copy()
    df['Porcentagem %'] = ((df['SomaDeVotos']/válidos)*100).round(2)
    return df.loc[bairro].sort_values('SomaDeVotos', ascending=False).reset_index()
  else:
    print(f"Bairro não encontrado. Digite um bairro da lista: {list(válidos_bairros['Bairro'].unique())}")

fontes_letras = 'Georgia'

resultado_geral = dash_table.DataTable(
    id='resultado-geral',
    data=total_partido().to_dict('records'),
    page_size=13,
    style_cell = {'fontFamily': fontes_letras,
                  'textAlign': 'center'}

)

resultado_partidos = dash_table.DataTable(
    id='resultado-partidos',
    page_size=13,
    data=partidos('PDT').to_dict('records'),
    style_cell={'fontFamily': fontes_letras,
                  'textAlign': 'center'}
)

resultado_bairros = dash_table.DataTable(
    id='resultado-bairros',
    page_size=11,
    data=bairros('Centro').to_dict('records'),
    style_cell={'fontFamily': fontes_letras,
                  'textAlign': 'center'}
)

lista_bairros = ['Campos do Iguaçu', 'Centro', 'Cidade Nova', 'Conj. Libra', 'Jd. América', 'Jd. Califórnia', 'Jd. Central',
                 'Jd. Copacabana', 'Jd. das Flores', 'Jd. Ipê', 'Jd. Itália', 'Jd. Jupira', 'Jd. Lancaster', 'Jd. Manaus',
                 'Jd. Naipi', 'Jd. Panorama', 'Jd. Petrópolis', 'Jd. Polo Centro', 'Jd. São Paulo', 'Jd. Tarobá', 'Morumbi I',
                 'Morumbi II', 'Morumbi III', 'Polo Universitário', 'Portal da Foz', 'Porto Belo', 'Pq. Monjolo', 'Pq. Ouro Verde',
                 'Profilurb I', 'Sem Bairro', 'Sol de Maio', 'STI Centro', 'Tamanduá Grande', 'Três Bandeiras', 'Três Lagoas', 'Vila A',
                 'Vila C', 'Vl. Adriana', 'Vl. Boa Esperança', 'Vl. Carimã', 'Vl. Maracanã', 'Vl. Shalon', 'Vl. Yolanda']

partidos_dict = [{'label': 'AVANTE', 'value': 'AVANTE'},
           {'label': 'CIDADANIA', 'value': 'CIDADANIA'},
           {'label': 'DEM', 'value': 'DEM'},
           {'label': 'MDB', 'value': 'MDB'},
           {'label': 'PATRIOTA', 'value': 'PATRIOTA'},
           {'label': 'PC do B', 'value': 'PC do B'},
           {'label': 'PDT', 'value': 'PDT'},
           {'label': 'PL', 'value': 'PL'},
           {'label': 'PODE', 'value': 'PODE'},
           {'label': 'PP', 'value': 'PP'},
           {'label': 'PROS', 'value':'PROS'},
           {'label': 'PRTB', 'value': 'PRTB'},
           {'label':'PSC', 'value': 'PSC'},
           {'label': 'PSD', 'value': 'PSD'},
           {'label':'PSL', 'value': 'PSL'},
           {'label':'PSOL', 'value': 'PSOL'},
           {'label': 'PT', 'value': 'PT'},
           {'label': 'PTB', 'value': 'PTB'},
           {'label': 'PV', 'value': 'PV'},
           {'label': 'REPUBLICANOS', 'value': 'REPUBLICANOS'},
           {'label': 'SOLIDARIEDADE', 'value': 'SOLIDARIEDADE'}]

app.layout = html.Div(children=[
    html.Div(children=[html.H2('Projeto Boletim de Urna Foz'),
             html.P('Bem-vindo ao projeto Boletim de Urna Foz com os resultados parlamentares de Foz do Iguaçu-PR em 2020.')]),
    html.Div(children=[html.H3('Resultado Geral'),
                       resultado_geral],
             style={'width': '50%'},
             id='resultado-geral'),
    html.Div(children=[html.H3('Resultado por Partido'),
                       dcc.Dropdown(id='selecionar-partido',
                                    options=partidos_dict,
                                    value='PDT',
                                    placeholder='Selecione o Partido'),
                       resultado_partidos],
             style={'width': '50%'}),
    html.Div(children=[html.H3('Resultado por bairro'),
                       dcc.Dropdown(id='selecionar-bairro',
                                    options=lista_bairros,
                                    value='Centro',
                                    placeholder='Selecione o bairro'),
                       resultado_bairros],
             style={'width': '50%'}),
    html.Div(children=[
        html.H3('Envie uma mensagem'),
        html.P('Este é um projeto em início de construção. Suas críticas, sugestões e elogios são bem-vindos.'),
        dcc.Textarea(
            id='message-input',
            placeholder='Escreva sua mensagem.',
            style={'width': '100%', 'height': 200, 'margin': '10px'}
        ),
        html.Button('Enviar', id='send-button', n_clicks=0, style={'margin': '10px'}),
        html.Div(id='email-status')],
            style={'width': '50%'}),
    html.Div([html.P("Obrigado!", style={'font-style': 'italic'}),
             html.P('Mauro Sérgio Figueira', style={'font-style': 'italic'})],
        style={'width': '50%'})
],
    style={'font-family': fontes_letras}
)

@app.callback(
    Output(component_id='resultado-partidos', component_property='data'),
    Input(component_id='selecionar-partido', component_property='value'),
    prevent_initial_call=True
)
def selecionar_partido(partido):
    if partido in votos['Partido'].unique():
        return partidos(partido).to_dict('records')
    else:
        raise dash.exceptions.PreventUpdate

@app.callback(
    Output(component_id='resultado-bairros', component_property='data'),
    Input(component_id='selecionar-bairro', component_property='value'),
    prevent_initial_call=True
)
def selecionar_bairro(bairro):
    if bairro in votos['Bairro'].unique():
        return bairros(bairro).to_dict('records')
    else:
        raise dash.exceptions.PreventUpdate

senha = 'ikldudnqtnjcskjx'

@app.callback(
    Output('email-status', 'children'),
              Input('send-button', 'n_clicks'),
              State('message-input', 'value'))

def send_email(n_clicks, message):
    if n_clicks > 0:
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login('projetoboletimdeurnafoz@gmail.com', senha)
            sender_email = 'projetoboletimdeurnafoz@gmail.com'
            recipient_email = 'projetoboletimdeurnafoz@gmail.com'
            message_body = f'Subject: New message from {sender_email}\n\n{message}'
            server.sendmail(sender_email, recipient_email, message_body)
            server.quit()
            return 'Mensagem enviada!'
        except Exception as e:
            return f'Error: {str(e)}'

# if __name__ == '__main__':
#     app.run_server(debug=True)

if __name__=='__main__':
    app.run_server(debug=True, host="0.0.0.0")