import pandas as pd
import numpy as np
import os
import glob

from building_cost_analysis.calc import (
    combine_offers
)
# TODO plausibility checks ID == np.nan
# TODO plausibility check ascending ids!
# TODO check if all ids < level remain constant inside the group ( for example 10.10, 10.20 10.30 ok, 10.10, 20.10, 10.20 wrong!)
# maybe this makes no sense!..

def get_df_with_extended_id_cols(df, level=None):
    df['ID'] = df['ID'].astype(str)
    df['level'] = df['ID'].str.count('\\.')
    df['id_list'] = df['ID'].str.split('\\.')
    max_level = df['level'].max()
    print(max_level)
    for cur_level in range(max_level+1):
        df[f'id_{cur_level}'] = np.nan
        mask_level = df['level'] >= cur_level
        df.loc[mask_level, f'id_{cur_level}'] = df.loc[mask_level]['id_list'].apply(lambda x: x[cur_level])
        df[f'id_{cur_level}'] = df[f'id_{cur_level}'].astype(float).fillna(0)
    return df


def get_df_gewerke(path_gewerke: str) -> pd.DataFrame:
    df_gewerke = pd.read_excel(path_gewerke, skiprows=1, converters={'ID':str})
    # bring all position descriptions to column 'Beschreibung'
    df_gewerke.loc[~df_gewerke['Unnamed: 3'].isnull(), 'Beschreibung'] = df_gewerke.loc[~df_gewerke['Unnamed: 3'].isnull()]['Unnamed: 3']
    df_gewerke.loc[~df_gewerke['Unnamed: 4'].isnull(), 'Beschreibung'] = df_gewerke.loc[~df_gewerke['Unnamed: 4'].isnull()]['Unnamed: 4']
    # remove all columns except ID and Beschreibung
    df_gewerke = df_gewerke[['ID', 'Beschreibung']]
    df_gewerke = df_gewerke.loc[~df_gewerke['ID'].isnull()]
    df_gewerke = get_df_with_extended_id_cols(df_gewerke)
    return df_gewerke.set_index('ID')

def get_df_offer(path_offer: str, sheet_name: str) -> pd.DataFrame:
    df_angebot = pd.read_excel(path_offer, skiprows=3, converters={'ID':str}, sheet_name=sheet_name)
    df_angebot = df_angebot[df_angebot.columns.drop(list(df_angebot.filter(regex='Unnamed')))]
    df_angebot = df_angebot.loc[~df_angebot['ID'].isnull()]
    df_angebot.loc[:, 'ID'] = df_angebot['ID'].astype(str)
    # add brutto column
    if "Brutto" not in df_angebot.columns:
        df_angebot["Brutto"] = "Nein"
    # add UST everywhere Brutto == Nein
    df_angebot["price_brutto"] = df_angebot["Gesamtpreis"]
    df_angebot["factor"] = 1.0
    df_angebot.loc[df_angebot["Brutto"] != "Ja", "factor"] = 1.2
    df_angebot.loc[:, "price_brutto"] =  df_angebot["price_brutto"] * df_angebot["factor"]
    df_angebot.loc[:, 'file_source'] = path_offer
    df_angebot.loc[:, 'sheet_name'] = sheet_name
    df_angebot = get_df_with_extended_id_cols(df_angebot)
    return df_angebot.set_index('ID')

def get_list_df_offers(path_offers: list) -> list:
    list_df_offer = []
    for offer_entry in path_offers:
        df = get_df_offer(offer_entry['path_offer'], offer_entry['sheet_name'])
        list_df_offer.append(df)
    return list_df_offer

def get_df_offers_combined(path_offers: list) -> pd.DataFrame:
    """
    pass list of dict containing following fields: path_offer, sheet_name
    """
    return combine_offers(get_list_df_offers(path_offers))

def get_offer_file_paths(dir_offers: str) -> list:
    list_ret = []
    files = os.listdir(dir_offers)
    for file_path in files:
        if not file_path.endswith('.xlsx') or file_path.startswith('~'):
            continue
        list_ret.append(os.path.join(dir_offers, file_path))
    return list_ret

def get_offer_file_sheets(path_offer: str) -> list:
    xl = pd.ExcelFile(path_offer)
    list_names = xl.sheet_names
    if 'Einheiten' in list_names:
        list_names.remove('Einheiten')
    return list_names

def get_offer_file_paths_and_sheets(dir_offers: str) -> list:
    """ returns list of dict with path_offer, sheet_name"""
    paths = get_offer_file_paths(dir_offers)
    list_ret = []
    for file_path in paths:
        sheets = get_offer_file_sheets(file_path)
        for sheet in sheets:
            list_ret.append({
                'path_offer': file_path,
                'sheet_name': sheet 
            })
    return list_ret