import pandas as pd


def get_df_duplicated_positions(df) -> pd.DataFrame:
    # TODO use index instead of 'ID' column
    duplicated_id = df[df[['ID']].duplicated()]['ID'].values
    return df.loc[df['ID'].isin(duplicated_id)]

def append_rolled_up_sum_to_df(df_offers: pd.DataFrame, df_gewerke: pd.DataFrame) -> pd.DataFrame:
    df_offers_int = df_offers.copy()
    df_offers_int['desc_offer'] = df_offers['Beschreibung']
    df_offers_int = df_offers_int.drop(columns=['Beschreibung'])
    df_combined = df_offers_int.combine_first(df_gewerke)
    max_level = df_combined['level'].max()
    list_level_sums = []
    list_ids_sort = []
    for cur_level in range(max_level+1):
        list_ids_sort.append(f'id_{cur_level}')
        list_ids = []
        for lev in range(cur_level + 1):
            list_ids.append(f'id_{lev}')
        df_level = df_combined.loc[df_combined['level'] >= cur_level]
        df_level_count = df_level.groupby(list_ids).count()
        df_level_sum = df_level.groupby(list_ids).sum()
        df_level_sum['summed_up'] = df_level_sum['price_brutto']
        df_level_count['prices_existing'] = False
        df_level_count.loc[df_level_count['price_brutto'] != 0, 'prices_existing'] = True
        df_level_sum = df_level_sum[['summed_up']].combine_first(df_level_count[['prices_existing']])
        df_level_sum['level'] = cur_level
        df_level_sum = df_level_sum.reset_index()
        df_level_sum['ID'] = df_level_sum['id_0'].astype(int).astype(str)
        for lev in range(1, cur_level + 1):
            df_level_sum['ID'] += "." + df_level_sum[f'id_{lev}'].astype(int).astype(str)
        list_level_sums.append(df_level_sum)
    df_rolled_up_sum = pd.DataFrame()

    for df_sum in list_level_sums:
        df_rolled_up_sum = df_rolled_up_sum.combine_first(df_sum.set_index('ID'))
    df_ret = df_combined.combine_first(df_rolled_up_sum[['prices_existing', 'summed_up']])
    df_ret = df_ret.sort_values(list_ids_sort)
    return df_ret

def combine_offers(list_df_offers: list) -> pd.DataFrame:
    # use for example to determine total cost with a list of offers combined
    df_offers = pd.concat(list_df_offers)
    return df_offers

def compare_offers(list_df_offers: list, df_gewerke: pd.DataFrame) -> pd.DataFrame:
    # use to compare different offers
    return None


def get_missing_positions(df_sorted):
    max_level = df_sorted['level'].max()
    list_ids = []
    df_missing = df_sorted.copy()
    df_missing['display_missing'] = False
    df_missing['upper_level_missing'] = False
    df_missing['upper_level_inserted'] = False
    for lev in range(max_level + 1):
        mask_cur_level = (df_missing['level'] == lev) & (df_missing['prices_existing'] == False) & (df_missing['upper_level_missing'] == False)
        df_missing.loc[mask_cur_level, 'display_missing'] = True
        # set upper level missing
        for row_id, missing_row in df_missing[mask_cur_level].iterrows():
            mask = (df_missing['level'] > lev)
            for sublev in range(lev+1):
                mask = mask & (df_missing[f'id_{sublev}'] == missing_row[f'id_{sublev}'])
            df_missing.loc[mask, 'upper_level_missing'] = True
        # set upper level inserted
        mask_inserted = (df_missing['level'] == lev) & (~df_missing['price_brutto'].isnull())
        for row_id, missing_row in df_missing[mask_inserted].iterrows():
            mask = (df_missing['level'] > lev)
            for sublev in range(lev+1):
                mask = mask & (df_missing[f'id_{sublev}'] == missing_row[f'id_{sublev}'])
            df_missing.loc[mask, 'upper_level_inserted'] = True
    return df_missing.loc[(df_missing['display_missing'] == True) & ((df_missing['upper_level_inserted'] == False))]