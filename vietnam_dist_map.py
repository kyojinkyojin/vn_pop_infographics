import pandas as pd
import geopandas as gpd
from useful_func import *

gmvn10_df = gpd.read_file("./gmvn10/polbnda.shp")
gmvn10_df['laa'] = gmvn10_df['laa'].str.upper()

url = "https://vi.wikipedia.org/wiki/Danh_s%C3%A1ch_%C4%91%C6%A1n_v%E1%BB%8B_h%C3%A0nh_ch%C3%ADnh_c%E1%BA%A5p_huy%E1%BB%87n_c%E1%BB%A7a_Vi%E1%BB%87t_Nam#Danh_s%C3%A1ch_c%C3%A1c_%C4%91%C6%A1n_v%E1%BB%8B_h%C3%A0nh_ch%C3%ADnh_c%E1%BA%A5p_huy%E1%BB%87n"
tables = pd.read_html(url, encoding='utf-8')

df = tables[0]
df = df.drop(columns=["Số thứ tự", "Chú thích"], axis=1)
df.columns = ["dist", 'region', 'population', 'area_km2', 'density', 'adm_id']
df['region'] = df['region'].apply(lambda x: xoa_dau(x.upper()))
df['dist'] = df['dist'].apply(lambda x: xoa_dau(x.upper()))
m_replace = {"THANH PHO HO CHI MINH": "HO CHI MINH", 
             "BA RIA – VUNG TAU": "BA RIA VUNG TAU"} # - = U+2013

for k, v in m_replace.items():
    df['region'] = df['region'].str.replace(k, v, regex=False)
df.head()

f_df = gmvn10_df[gmvn10_df['laa'].isin(df['dist'].values) | gmvn10_df['laa'].isin(df['region'].values) | gmvn10_df['nam'].isin(df['region'].values)].reset_index(drop=True)
