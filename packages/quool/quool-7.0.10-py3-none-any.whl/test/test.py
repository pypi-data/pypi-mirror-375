from quool import DuckParquet

dp = DuckParquet("d:/documents/dataset/quotes_day")

print(
    dp.dpivot(
        index="time",
        values="close",
        columns="code",
        where="time > '2025-07-01'",
    )
)

print(
    dp.select(
        columns=["close", "code", "time"], where="time > ?", params=["2025-09-01"]
    )
)
