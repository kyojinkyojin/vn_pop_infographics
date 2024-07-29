from manim import *
import pandas as pd
import geopandas as gpd
import numpy as np

df = pd.read_csv("./cleaned/vietnam_adm_lvl2.csv", index_col=0)
#df = gpd.GeoDataFrame(df, geometry="geometry")
print(df.head())