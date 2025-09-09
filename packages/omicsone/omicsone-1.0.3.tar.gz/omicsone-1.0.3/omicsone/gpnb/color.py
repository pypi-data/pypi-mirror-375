import pandas as pd
import seaborn as sns

palette_gb_function = {
    "+H": "#2ca02c",
    "-H": "#98df8a",
    "+S": "#800080",
    "+N": "#1f77b4",
    "-N": "#a6cee3",
    "+H  or  +N" : "#ff9896",
    "N/A": "#646464",
    "+F": "#d62728"
}

palette_glycan_type = {
    "HM": "green",
    "Other": "grey",
    "only_F": "red",
    "only_S": "purple",
    "F+S": "orange"
}

def build_col_colors(enzyme_data, enzymes_sorted):
    uniq_paths = enzyme_data['PATH'].unique()
    uniq_locations = enzyme_data['Location'].unique()
    palette_gb_pathway = dict(zip(uniq_paths, sns.color_palette("Set2", len(uniq_paths))))
    palette_gb_location = dict(zip(uniq_locations, sns.color_palette("Paired", len(uniq_locations))))

    rows = []
    for index, row in enzyme_data.iterrows():
        function = row['Function']
        path = row['PATH']
        location = row['Location']
        rows.append({
            'PROTEIN': row['PROTEIN'],
            'Function': palette_gb_function.get(function, "#646464"),
            'Path': palette_gb_pathway.get(path, "#646464"),
            'Location': palette_gb_location.get(location, "#646464"),
        })
    col_colors = pd.DataFrame(rows).set_index('PROTEIN')
    
    df_reset = col_colors.reset_index()  # index 变成列
    df_unique = df_reset.drop_duplicates()
    df_unique = df_unique.set_index('PROTEIN')  # 还原原来的 index
    
    col_colors = df_unique.loc[enzymes_sorted,:].copy()
    col_colors = col_colors[~col_colors.index.duplicated(keep='first')]
    
    palettes = {
        'Function': palette_gb_function,
        'Path': palette_gb_pathway,
        'Location': palette_gb_location
    }
    
    return col_colors, palettes
    
    
def build_row_colors(glycans):
    from .glyco import decide_glycan_type
    rows = [{"Glycan": glycan, 
             "GlycanType": decide_glycan_type(glycan)} for glycan in glycans]
        
    row_df = pd.DataFrame(rows).set_index('Glycan')
    row_colors = row_df['GlycanType'].map(palette_glycan_type)
    return row_colors