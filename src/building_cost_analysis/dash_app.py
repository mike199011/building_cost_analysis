
import dash
from dash.dependencies import Input, Output, State
from dash import dash_table, MATCH, ALL
import dash_html_components as html
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from building_cost_analysis.settings import (
    dir_angebote,
    path_gewerke
)
from building_cost_analysis.parser import (
    get_df_gewerke,
    get_offer_file_paths,
    get_offer_file_paths_and_sheets,
    get_df_offer
)

from building_cost_analysis.calc import (
    append_rolled_up_sum_to_df
)

class ExpandableTable(dbc.Table):

    @staticmethod
    def from_dataframe(df_passed: pd.DataFrame, display_cols=None):
        df = df_passed.copy()
        df['unique_id'] = range(0, 0+len(df))

        # create header
        list_th = []
        list_th.append(html.Th(df.index.name))
        if display_cols is None:
            display_cols = df.columns
        for col in display_cols:
            list_th.append(html.Th(col))


        table_header = [html.Thead(html.Tr(list_th))]

        # create table body (only show top level)
        print("MIN LEVEL")
        print(df['level'].min())
        min_level = df['level'].min()
        list_rows = []
        for id, row in df.iterrows():
            list_td = []
            if row['prices_existing'] and np.isnan(row['price_brutto']):
                expand_id={
                    'type': 'expandable-button',
                    'index': row['unique_id']
                }

                #content_id = [dbc.Button("+", id='my_button', color="primary", className="me-1"), id]
                content_id =dbc.Checklist(
                    options=[
                        {"label": id, "value": 1},
                    ],
                    value=False,
                    id=expand_id,
                    switch=True,
                ),
                
                list_td.append(html.Td(content_id))
            else:
                list_td.append(html.Td(id))
            for col in display_cols:
                list_td.append(html.Td(row[col]))
            
            row_hidden = False
            if row['level'] > min_level:
                prev_level = int(row['level'] - 1)
                id_prev_level = row[f'id_{prev_level}']
                row_parent = df.loc[(df[f'id_{prev_level}'] == id_prev_level) & (df['level'] == prev_level)].iloc[0]
                unique_id = row['unique_id']
                row_id={
                    'type': f'expandable-list_{unique_id}',
                    'index': int(row_parent['unique_id'])
                }
                #print(row_id)
                tr = html.Tr(
                    children=list_td,
                    hidden=True,
                    id=row_id
                )
            else:
                tr = html.Tr(
                    children=list_td,
                    hidden=False
                )
            list_rows.append(tr)
        table_body = [html.Tbody(list_rows, id='my_table_body')]
        return ExpandableTable(table_header + table_body, 
                bordered=True, striped=True, hover=True,
                id='dtDynamicVerticalScrollExample',
                class_name="table table-striped table-bordered table-sm", 
                            color="primary",

                )


list_paths_sheets = get_offer_file_paths_and_sheets(dir_angebote)
df_offer = get_df_offer(list_paths_sheets[-1]['path_offer'], list_paths_sheets[-2]['sheet_name'])
df_gewerke = get_df_gewerke(path_gewerke)
df_offer = df_offer.drop(columns=['file_source', 'sheet_name'])
df_offer = append_rolled_up_sum_to_df(df_offer, df_gewerke)
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

table_header = [
    html.Thead(html.Tr([html.Th("First Name"), html.Th("Last Name")]))
]

#row1 = html.Tr([html.Td("Arthur"), html.Td("Dent")])
#row2 = html.Tr([html.Td("Ford"), html.Td("Prefect")])
#row3 = html.Tr([html.Td("Zaphod"), html.Td("Beeblebrox")])
#row4 = html.Tr([html.Td(dbc.Button("Primary", color="primary", className="me-1")), html.Td("Astra")])

#table_body = [html.Tbody([row1, row2, row3, row4])]

#table = dbc.Table(table_header + table_body, bordered=True)
#table = dbc.Table.from_dataframe(df_offer, striped=True, bordered=True, hover=True)
table = ExpandableTable.from_dataframe(df_offer, display_cols=['Beschreibung', 'Brutto', 'E-Preis', 'Einheit', 'Gesamtpreis', 'Menge', 'summed_up'])

def button_click(n_clicks):
    print("NUMBER OF CLICKS")
    print(n_clicks)
    return None

#app.callback(Input('+', 'n_clicks'))(button_click)
app.layout = html.Div([
    html.Div(children=table, id='my_table'),
    html.Div(id='container-button-basic',
             children='Enter a value and press submit')
])


@app.callback(
    Output('container-button-basic', 'children'),
    Output('my_table_body', 'children'),
    Input({'type': 'expandable-button', 'index': ALL}, 'value'),
    State('my_table_body', 'children')
)
def update_output(n_clicks, state):
    print(dash.callback_context.triggered)
    #print(dash.callback_context.inputs_list)
    prop_id = dash.callback_context.triggered[0]['prop_id']
    to_expand = None
    if prop_id == '.':
        to_expand = None
    else:
        prop_id = prop_id.replace('.value', '')
        prop_dict = eval(prop_id)
        to_expand = prop_dict['index']


    for tr in state:
        #print(tr)
        if 'id' not in tr['props']:
            continue
        #print(tr['props']['id'])
        if tr['props']['id']['index'] == to_expand:
            tr['props']['hidden'] = False
            print(tr)
    #if prop
    #print(state)
    #print('hello')
    return 'The input value was  and the button has been clicked {} times'.format(
        n_clicks
    ), state



if __name__ == '__main__':
    app.run_server(debug=True)