# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import numpy as np
from joblib import load
from dash.dependencies import Input, Output

BUISSNES_MAPPING = [
	{'label': 'studio fizjoterapełtyczne', 'value': 'Q_86'},
	{'label': 'biuro księgowe', 'value': 'M_69'},
	{'label': 'muzeum', 'value': 'R_91'},
	{'label': 'kasyno', 'value': 'R_92'},
	{'label': 'statek', 'value': 'H_50'},
	{'label': 'firmę opikuńczą', 'value': 'Q_88'},
    {'label': 'sdf asdf', 'value': 'F_43'},
]
LICENCED_BUISSNES = ['Q_86', 'M_69', 'R_92', 'H_50', 'Q_88', 'F_43']

SEX_MAPPING = [
	{'label': 'kobietą', 'value': 'F'},
	{'label': 'mężczyzną', 'value': 'M'}
]

VOIVODESHIPS_MAPPING = [
	{'label': 'Mazowieckiego', 'value': 'mazowieckie'},
	{'label': 'Wielkopolskie', 'value': 'wielkopolskie'},
	{'label': 'Warminsko-Mazurskie', 'value': 'warminskomazurskie'},
	{'label': 'Zachodniopomorskie', 'value': 'zachodniopomorskie'},
	{'label': '', 'value': 'na'},
]

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
clf = load('model.joblib')

app.layout = html.Div(children=[
    html.H1(children='Ile przetrwa twój biznes?'),

    html.Plaintext("Jestem ", style=dict(display='inline-block')),
    dcc.Dropdown(
        id='sex',
        options=SEX_MAPPING,
        value='M',
	style=dict(
            width=200,
	    display='inline-block',
            verticalAlign="middle"
        )
    ),

    html.Plaintext(", mam ", style=dict(display='inline-block')),
    dcc.Dropdown(
        id='business-type',
        options=BUISSNES_MAPPING,
        value='Q_86',
	style=dict(
            width=200,
	    display='inline-block',
            verticalAlign="middle"
        )
    ),

    html.Plaintext(", jestem z województwa ", style=dict(display='inline-block')),
    dcc.Dropdown(
        id='voivodeship',
        options=VOIVODESHIPS_MAPPING,
        value='mazowieckie',
	style=dict(
            width=170,
	    display='inline-block',
            verticalAlign="middle"
        )
    ),

    html.Plaintext(" ", style=dict(display='inline-block')),

    html.Div([
        html.Plaintext(" i ", style=dict(display='inline-block')),

	dcc.Dropdown(
		id='is_licence',
		options=[
		    {'label': 'licencje', 'value': 1},
		    {'label': 'nie mam licencji', 'value': 0},
		],
		value=0,
		style=dict(
		    width=135,
		    display='inline-block',
		    verticalAlign="middle",
		    padding='0',
		)
    	),
	], id='to_hide', style= {'display': 'inline-block'},
        
    ),
    

    html.Plaintext(".  ", style=dict(display='inline-block')),
    dcc.Dropdown(
        id='is_shareholder',
        options=[
            {'label': 'Posiadam udziały', 'value': 1},
            {'label': 'Nie posiadam udziałów', 'value': 0},
        ],
        value=0,
	style=dict(
            width=185,
	    display='inline-block',
            verticalAlign="middle",
	    padding='0',
        )
    ),
    html.Plaintext(" w innych firmach. ", style=dict(display='inline-block')),

    html.Plaintext("Moj emial to "),
    dcc.Input(id="email", type="text", value="", placeholder="", style=dict(display='block')),

    html.Plaintext("Moj numer telefonu to ", style=dict(display='block')),	
    dcc.Input(id="phone_number", type="text", value="", placeholder="", style=dict(display='block')),
    
    html.Plaintext("Twoja firma przetrwa:", style=dict(display='block')),
    dcc.Input(id="output", type="text", placeholder=""),


    dcc.Graph(id='bankrupcy_proba-graph')

])

@app.callback(
   Output(component_id='to_hide', component_property='style'),
   [Input(component_id='business-type', component_property='value')])
def show_hide_element(visibility_state):
    if visibility_state in LICENCED_BUISSNES:
        return  {'display': 'inline-block'}
    else:
        return {'display': 'none'}


@app.callback(
   Output(component_id='output', component_property='value'),
   [Input(component_id='sex', component_property='value'),   
    Input(component_id='business-type', component_property='value'),
    Input(component_id='voivodeship', component_property='value'),
    Input(component_id='is_licence', component_property='value'),
    Input(component_id='is_shareholder', component_property='value'),
    Input(component_id='email', component_property='value'),
    Input(component_id='phone_number', component_property='value')]
   )
def predict(sex, PKD_Div_Sec, voivodeship, licence, shareholder, email, phone_number):
    X = {'HasLicences':[licence>0], 'PKDMainDivision':[PKD_Div_Sec.split('_')[1]], \
        'PKDMainSection': [PKD_Div_Sec.split('_')[0]], 'MainAddressVoivodeship': [voivodeship], \
        'ShareholderInOtherCompanies': [shareholder>0], 'IsPhoneNo': [phone_number != ""], \
        'IsEmail': [email != ""], 'Sex': [sex]}
    pred = int(clf.predict(pd.DataFrame(X).astype(str))[0])
    print(pred)
    return {
        0: "mniej niż rok",
        1: "niecałe 2 lata",
        2: "niecałe 3 lata",
        3: "niecałe 4 lata",
        4: "4-5 lat",
        5: "ponad 5 lat",
        6: "ponad 6 lat",
        7: "ponad 7 lat",
    }.get(pred, "4-5 lat")

@app.callback(
   Output(component_id='bankrupcy_proba-graph', component_property='figure'),
  [Input(component_id='sex', component_property='value'),
    Input(component_id='business-type', component_property='value'),
    Input(component_id='voivodeship', component_property='value'),
    Input(component_id='is_licence', component_property='value'),
    Input(component_id='is_shareholder', component_property='value'),
    Input(component_id='email', component_property='value'),
    Input(component_id='phone_number', component_property='value')]
   )
def plot_proba(sex, PKD_Div_Sec, voivodeship, licence, shareholder, email, phone_number):
    X = {'HasLicences':[licence>0], 'PKDMainDivision':[PKD_Div_Sec.split('_')[1]], \
        'PKDMainSection': [PKD_Div_Sec.split('_')[0]], 'MainAddressVoivodeship': [voivodeship], \
        'ShareholderInOtherCompanies': [shareholder>0], 'IsPhoneNo': [phone_number != ""], \
        'IsEmail': [email != ""], 'Sex': [sex]}

    proba = clf.predict_proba(pd.DataFrame(X).astype(str))[0]
    print(pd.DataFrame(X).astype(str))
    print(proba)
    return  {
            'data': [
                {'x': ['0-11','12-23', '24-35', '36-47','48-59','60-71','72-83','84-95'], 'y': proba, 'type': 'bar'},
            ],
            'layout': {
                'title': 'Prawdopodobienstwo updaku firmy w przedzialach miesiecznych'
            }
        }

if __name__ == '__main__':
    app.run_server(debug=True)
