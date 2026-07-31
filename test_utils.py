import pandas as pd
from utils import convert_df_to_excel

df = pd.DataFrame({
    "Nama": ["Arfan", "Budi"],
    "Status": ["PASS", "FAIL"]
})

excel = convert_df_to_excel(df)

print("Berhasil")
print(type(excel))