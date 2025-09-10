import duckdb
import pandas as pd
from pathlib import Path
from quool import Parquetry


input_path = Path("d:/documents/databasebackup/industry_mapping")
output_path = Path("d:/documents/datalake/industry_mapping_test")


duckdb.connect("")
data = pd.read_parquet(input_path)
data = data[["code", "time"] + data.columns[1:-1].to_list()]
data["code"] = data["code"].map(lambda x: x[:7] + ("SH" if x[-2:] == "HG" or x[-2:] == "SH" else "SZ"))
print(data)
# data["index_code"] = data["index_code"].map(lambda x: x[:7] + ("SH" if x[-2:] == "HG" or x[-2:] == "SH" else "SZ"))
data = data.sort_values(["code", "time"])
print(data)
data["month"] = data["time"].dt.strftime("%Y%m")
pm = Parquetry(output_path, grouper=["month"], unikey=["time", "code"])
pm.update(data, n_jobs=4)
