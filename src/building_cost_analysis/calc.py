import pandas as pd


def get_df_duplicated_positions(df) -> pd.DataFrame:
    # TODO use index instead of 'ID' column
    duplicated_id = df[df[['ID']].duplicated()]['ID'].values
    return df.loc[df['ID'].isin(duplicated_id)]
