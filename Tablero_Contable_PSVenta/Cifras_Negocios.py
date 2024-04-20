import dash
import pandas as pd
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import dash_table  
import plotly.graph_objs as go

# Leer el archivo
df = pd.read_excel('CN_Contable.xlsx')

app = dash.Dash(__name__)

# Añadir un layout a la app
app.layout = html.Div([
    
    # Dropdown para seleccionar el mes
    dcc.Dropdown(
        id='mes-dropdown',
        options=[{'label': mes, 'value': mes} for mes in df['Mes'].unique()],
        value=df['Mes'].unique()[0]
    ),
    
    # Tabla
    html.Div(id='tabla-contable'),
    
    # Gráfico de torta
    dcc.Graph(id='grafico-torta'),

    # Nuevo dropdown para seleccionar la columna de interés
    html.Hr(),
    html.Label('Selecciona una columna:'),
    dcc.Dropdown(
        id='columna-dropdown',
        options=[
            {'label': 'MAYORISTA', 'value': 'MAYORISTA'},
            {'label': 'MOSTRADO', 'value': 'MOSTRADO'},
            {'label': 'GARANTIA', 'value': 'GARANTIA'},
            {'label': 'TALLER CHAPA P', 'value': 'TALLER CHAPA P'},
            {'label': 'TALLER MECANICA', 'value': 'TALLER MECANICA'},
            {'label': 'RAPIDE', 'value': 'RAPIDE'},
            {'label': 'INTERNO', 'value': 'INTERNO'},

        ],
        value='MAYORISTA'
            ),

    # Espacio para los gráficos
    html.Div([
        dcc.Graph(id='grafico-margen-bruto', style={'width': '50%', 'display': 'inline-block'}),
        dcc.Graph(id='grafico-descuentos', style={'width': '50%', 'display': 'inline-block'}),
            ]),
           # Espacio para las tablas
    html.Div(id='tabla-margen-bruto',style={'width': '50%', 'display': 'inline-block'}),
    html.Div(id='tabla-descuentos',style={'width': '50%', 'display': 'inline-block'}),
])

@app.callback(
    [Output('tabla-contable', 'children'),
     Output('grafico-torta', 'figure')],
    [Input('mes-dropdown', 'value')]
)
def update_output(selected_month):
     # Filtrar dataframe según el mes seleccionado
    df_filtered = df[df['Mes'] == selected_month].copy()  # Crea una copia del dataframe filtrado

    # Redondear los valores numéricos a dos decimales
    numeric_columns = [col for col in df_filtered.columns if col not in ['Mes', 'C_NEGOCIOS']]
    df_filtered[numeric_columns] = df_filtered[numeric_columns].round(2)

    # Lista de columnas a modificar
    columns_to_convert = ['MAYORISTA', 'MOSTRADO', 'GARANTIA', 'TALLER CHAPA P', 'TALLER MECANICA', 
                          'RAPIDE', 'INVENTARIO ROTATIVO', 'CARGO INTERNO', 'INTERNO', 'TOTAL']

    # Convertir valores de filas específicas a formato de porcentaje para mostrar
    for row_name in ["% SOBRE VENTAS DESPUES DE IMPUESTOS", "% SOBRE VENTAS ANTES DE IMPUESTOS"]:
        for col in columns_to_convert:
            value = df_filtered.loc[df['C_NEGOCIOS'] == row_name, col].values[0] * 100
            rounded_value = round(value, 2)  # Redondear a 2 decimales
            df_filtered.loc[df['C_NEGOCIOS'] == row_name, col] = str(rounded_value) + '%'


    
    # Crear tabla usando dash_table.DataTable
    table = dash_table.DataTable(
        columns=[
            {"name": i, "id": i} for i in df_filtered.columns if i != 'Mes'  # Excluir la columna 'Mes'
        ],
        data=df_filtered.to_dict('records'),
        style_data={
            'whiteSpace': 'normal',
            'height': 'auto',
            'border': '1px solid black'
        },
        style_header={
            'backgroundColor': '#81D4FA',
            'fontWeight': 'bold',
            'border': '1px solid black'
        },
        style_table={
            'overflowX': 'scroll',
            'border': '1px solid black'   
        },
        style_cell_conditional=[  # Estilo condicional para la columna 'C_NEGOCIOS'
            {
                'if': {'column_id': 'C_NEGOCIOS'},
                'textAlign': 'left',
            }
        ]
    )
    
    # Crear gráfico de torta
    pie_data = df_filtered[df_filtered['C_NEGOCIOS'] == "VENTAS"][['MAYORISTA', 'MOSTRADO', 'GARANTIA', 'TALLER CHAPA P', 'TALLER MECANICA', 'RAPIDE', 'INVENTARIO ROTATIVO', 'CARGO INTERNO', 'INTERNO']].iloc[0].to_dict()

    pie_colors = ['#C70039', '#FF5733', '#FFC300', '#DAF7A6', '#81d4fa', '#fce4ec', '#E57373', '#FF5722']
    pie_figure = {
        'data': [{
            'type': 'pie',
            'labels': list(pie_data.keys()),
            'values': list(pie_data.values()),
            'marker': {'colors': pie_colors},
            'hole': 0.3
        }],
        'layout': {'title': 'Gráfico de Negocios: Ventas',  # Aquí agregas el título
                   'paper_bgcolor': '#FCE4EC',
                     'margin': {'t': 50, 'b': 50, 'r': 50, 'l': 50}}
    }
    
    return table, pie_figure

@app.callback(
    [Output('grafico-margen-bruto', 'figure'),
     Output('grafico-descuentos', 'figure')],
    [Input('columna-dropdown', 'value')]
)
def update_graphs(columna_seleccionada):
    # Filtra el dataframe por C_NEGOCIOS para 'MARGEN BRUTO', 'DESCUENTOS', y 'VENTAS'
    df_bruto = df[df['C_NEGOCIOS'] == 'MARGEN BRUTO']
    df_descuentos = df[df['C_NEGOCIOS'] == 'DESCUENTOS']
    df_ventas = df[df['C_NEGOCIOS'] == 'VENTAS']

   # Crear los gráficos de líneas
    fig_bruto = go.Figure()
    fig_bruto.add_trace(go.Scatter(x=df_bruto['Mes'], y=df_bruto[columna_seleccionada], line=dict(color='#FF5722')))
    fig_bruto.update_layout(paper_bgcolor='#F8BBD0', plot_bgcolor='#F8BBD0', title='Margen Bruto por Mes')

    fig_descuentos = go.Figure()
    fig_descuentos.add_trace(go.Scatter(x=df_descuentos['Mes'], y=df_descuentos[columna_seleccionada], line=dict(color='#FF5722')))
    fig_descuentos.update_layout(paper_bgcolor='#B3E5FC', plot_bgcolor='#B3E5FC', title='Descuentos por Mes')
   
    
    return fig_bruto, fig_descuentos

@app.callback(
    [Output('tabla-margen-bruto', 'children'),
     Output('tabla-descuentos', 'children')],
    [Input('columna-dropdown', 'value')]
)
def update_graphs_and_tables(columna_seleccionada):
    # Filtrar datos según negocio seleccionado
    df_bruto1 = df[(df['C_NEGOCIOS'] == 'MARGEN BRUTO')]
    df_descuentos1 = df[(df['C_NEGOCIOS'] == 'DESCUENTOS')]
    df_ventas1 = df[(df['C_NEGOCIOS'] == 'VENTAS')]
    
    # Crear tablas de porcentajes
    tabla_margen_bruto = dash_table.DataTable(
        columns=[{'name': 'Mes', 'id': 'Mes'}, {'name': 'Porcentaje', 'id': 'Porcentaje'}],
        style_data={'whiteSpace': 'normal', 'height': 'auto'},
        style_header={'backgroundColor': '#FF5722', 'fontWeight': 'bold'}
    )
    
    tabla_descuentos = dash_table.DataTable(
        columns=[{'name': 'Mes', 'id': 'Mes'}, {'name': 'Porcentaje', 'id': 'Porcentaje'}],
        style_data={'whiteSpace': 'normal', 'height': 'auto'},
        style_header={'backgroundColor': '#FF5722', 'fontWeight': 'bold'}
    )
    
    # Inicializar listas para almacenar datos de porcentaje por mes
    porcentaje_bruto_data = []
    porcentaje_descuentos_data = []

    # Calcular el porcentaje para cada mes y agregar a las listas de datos
    for mes in df_bruto1['Mes']:
        porcentaje_bruto = (df_bruto1.loc[df_bruto1['Mes'] == mes, columna_seleccionada].values[0] / df_ventas1.loc[df_ventas1['Mes'] == mes, columna_seleccionada].values[0]) * 100
        porcentaje_descuentos = (df_descuentos1.loc[df_descuentos1['Mes'] == mes, columna_seleccionada].values[0] / df_ventas1.loc[df_ventas1['Mes'] == mes, columna_seleccionada].values[0]) * 100
        porcentaje_bruto_data.append({'Mes': mes, 'Porcentaje': round(porcentaje_bruto, 2)})
        porcentaje_descuentos_data.append({'Mes': mes, 'Porcentaje': round(porcentaje_descuentos, 2)})

    tabla_margen_bruto.data = porcentaje_bruto_data
    tabla_descuentos.data = porcentaje_descuentos_data
    
    return tabla_margen_bruto, tabla_descuentos



if __name__ == '__main__':
    app.run_server(debug=True)