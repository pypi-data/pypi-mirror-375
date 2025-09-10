import pandas as pd
from tqdm import tqdm
from pathlib import Path
from quool import Parquetry, DuckDBManager


db = DuckDBManager("D:/Documents/database.duckdb")


def rectify_code(x):
    if x[-4] == "X":
        return x[:6] + (".SZ" if x[-4:] == "XSHE" else ".SH")
    return x


# print("migrate instruments_info...")
# df = pd.read_parquet(r"D:/Documents/DataBaseBackUp/instruments_info")
# df = df[~df["code"].duplicated(keep='last')]
# df = df.set_index("code")
# db.upsert(df, "instruments_info")

# print("migrate quotes_day...")
# for i, file in tqdm(list(enumerate(Path("D:/Documents/DataBaseBackUp/quotes_day").glob("*.parquet")))):
#     df = pd.read_parquet(file)
#     df = df.drop_duplicates(["time", "code"])
#     df["code"] = df["code"].map(rectify_code)
#     if i == 0:
#         df = df.set_index(["time", "code"])
#     else:
#         df = df[["time", "code"] + df.columns[2:].to_list()]
#     db.upsert(df, "quotes_day")

# print("migrate index_quotes_day...")
# for i, file in tqdm(list(enumerate(Path("D:/Documents/DataBaseBackUp/index_quotes_day").glob("*.parquet")))):
#     df = pd.read_parquet(file)
#     df = df.drop_duplicates(["time", "code"])
#     df["code"] = df["code"].map(rectify_code)
#     if i == 0:
#         df = df.set_index(["time", "code"])
#     else:
#         df = df[["time", "code"] + df.columns[2:].to_list()]
#     db.upsert(df, "index_quotes_day")

# print("migrate index_weights...")
# for i, file in tqdm(list(enumerate(Path("D:/Documents/DataBaseBackUp/index_weights").glob("*.parquet")))):
#     df = pd.read_parquet(file)
#     df = df.drop_duplicates(["time", "code", "index_code"])
#     df["code"] = df["code"].map(rectify_code)
#     df["index_code"] = df["index_code"].map(rectify_code)
#     if i == 0:
#         df = df.set_index(["time", "code", "index_code"])
#     db.upsert(df, "index_weights")

print("migrate quotes_min...")
for i, file in tqdm(
    list(enumerate(Path("D:/Documents/DataBaseBackUp/quotes_min").glob("*.parquet")))[816:]
):
    df = pd.read_parquet(file)
    df = df.drop_duplicates(["time", "code"])
    df["code"] = df["code"].map(rectify_code)
    seq = [
        "time",
        "code",
        "open",
        "high",
        "low",
        "close",
        "volume",
        "amount",
        "open_post",
        "high_post",
        "low_post",
        "close_post",
        "volume_post",
    ]
    if i == 0:
        df = df.set_index(["time", "code"])
        df = df[seq[2:]]
    else:
        df = df[seq]
    db.upsert(df, "quotes_min")

# print("migrate industry_mapping...")
# for i, file in tqdm(list(enumerate(Path("D:/Documents/DataBaseBackUp/industry_mapping").glob("*.parquet")))):
#     df = pd.read_parquet(file)
#     df = df.drop_duplicates(["time", "code"])
#     df["code"] = df["code"].map(rectify_code)
#     if i == 0:
#         df = df.set_index(["time", "code"])
#     else:
#         df = df[["time", "code"] + df.columns[1:-1].to_list()]
#     db.upsert(df, "industry_mapping")

# print("migrate financial_report...")
# for i, file in tqdm(list(enumerate(Path("D:/Documents/DataBaseBackUp/financial_report").glob("*.parquet")))[-1:]):
# df = pd.read_parquet(file)
#     df = df.drop_duplicates(["time", "code", "account_name"])
#     df["code"] = df["code"].map(rectify_code)
#     if i == 0:
#         df = df.set_index(["time", "code", "account_name"])
#     else:
#         df = df[["time", "code", "account_name", "lyr", "mrq", "ttm"]]
#     db.upsert(df, "financial_report")
