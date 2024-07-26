import pandas as pd
from useful_func import *

ex = pd.ExcelFile("./raw/indepth_pop.xlsx")
df = pd.read_excel(ex, "Bieu 12")
df.columns = df.iloc[1]
df = df.iloc[3:]
df = df.dropna(how='all').reset_index(drop=True)
df = df.rename(columns={'Sơ bộ 2022': '2022'})
df.columns = df.columns.fillna("Region")
col_names = []
for col in df.columns:
    try: 
        col_names.append(str(int(col)))
    except ValueError:
        col_names.append(str(col))
        
df.columns = col_names
df.head()

non_province = ["CẢ NƯỚC", "Tỉnh, thành phố", "Đồng bằng sông Hồng", "Trung du và miền núi phía Bắc", "Trung du miền núi phía Bắc", "Bắc Trung Bộ và Duyên hải miền Trung", "Đông Nam Bộ", "Đồng bằng sông Cửu Long", "Vùng kinh tế - xã hội"]
province = [r for r in df["Region"] if r not in non_province]
df = df[df["Region"].isin(province)].reset_index(drop=True)
df.columns = ["Region", "total", "male", "female"]