import os
import re
import uuid
import shutil
from typing import List, Optional, Dict, Any, Sequence, Union
from joblib import Parallel, delayed
import duckdb
import pandas as pd


class DuckParquet:
    def __init__(
        self,
        dataset_path: str,
        name: Optional[str] = None,
        db_path: str = ":memory:",
        threads: Optional[int] = None,
    ):
        """Initializes the DuckParquet object.

        Args:
            dataset_path (str): Directory path that stores the parquet dataset.
            name (Optional[str]): The view name. Defaults to directory basename.
            db_path (str): Path to DuckDB database file. Defaults to in-memory.
            threads (Optional[int]): Number of threads used for partition operations.

        Raises:
            ValueError: If the dataset_path is not a directory.
        """
        self.dataset_path = os.path.abspath(dataset_path)
        if not os.path.exists(self.dataset_path):
            os.makedirs(self.dataset_path)
        if not os.path.isdir(self.dataset_path):
            raise ValueError("Only directory is valid in dataset_path param")
        self.view_name = name or self._default_view_name(self.dataset_path)
        config = {}
        self.threads = threads or 1
        config["threads"] = self.threads
        self.con = duckdb.connect(database=db_path, config=config)
        self.scan_pattern = self._infer_scan_pattern(self.dataset_path)
        if self._parquet_files_exist():
            self._create_or_replace_view()

    # --- Private Helper Methods ---

    @staticmethod
    def _is_identifier(name: str) -> bool:
        """Check if a string is a valid DuckDB SQL identifier.

        Args:
            name (str): The identifier to check.

        Returns:
            bool: True if valid identifier, else False.
        """
        return bool(re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name))

    @staticmethod
    def _quote_ident(name: str) -> str:
        """Quote a string if it's not a valid identifier for DuckDB.

        Args:
            name (str): The identifier to quote.

        Returns:
            str: Quoted identifier as DuckDB requires.
        """
        if DuckParquet._is_identifier(name):
            return name
        return '"' + name.replace('"', '""') + '"'

    @staticmethod
    def _default_view_name(path: str) -> str:
        """Generate a default DuckDB view name from file/directory name.

        Args:
            path (str): Directory or parquet file path.

        Returns:
            str: Default view name.
        """
        base = os.path.basename(path.rstrip(os.sep))
        name = os.path.splitext(base)[0] if base.endswith(".parquet") else base
        if not DuckParquet._is_identifier(name):
            name = "ds_" + re.sub(r"[^A-Za-z0-9_]+", "_", name)
        return name or "dataset"

    @staticmethod
    def _infer_scan_pattern(path: str) -> str:
        """Infer DuckDB's parquet_scan path glob based on the directory path.

        Args:
            path (str): Target directory.

        Returns:
            str: Glob scan pattern.
        """
        if os.path.isdir(path):
            return os.path.join(path, "**/*.parquet")
        return path

    @staticmethod
    def _local_tempdir(target_dir, prefix="__parquet_rewrite_"):
        """Generate a temporary directory for atomic operations under target_dir.

        Args:
            target_dir (str): Directory for temp.

        Returns:
            str: Path to temp directory.
        """
        tmpdir = os.path.join(target_dir, f"{prefix}{uuid.uuid4().hex[:8]}")
        os.makedirs(tmpdir)
        return tmpdir

    def _parquet_files_exist(self) -> bool:
        """Check if there are any parquet files under the dataset path.

        Returns:
            bool: True if any parquet exists, else False.
        """
        for root, dirs, files in os.walk(self.dataset_path):
            for fn in files:
                if fn.endswith(".parquet"):
                    return True
        return False

    def _create_or_replace_view(self):
        """Create or replace the DuckDB view for current dataset."""
        view_ident = DuckParquet._quote_ident(self.view_name)
        sql = f"CREATE OR REPLACE VIEW {view_ident} AS SELECT * FROM parquet_scan('{self.scan_pattern}')"
        self.con.execute(sql)

    def _base_columns(self) -> List[str]:
        """Get all base columns from current parquet duckdb view.

        Returns:
            List[str]: List of column names in the schema.
        """
        return self.list_columns()

    def _copy_select_to_dir(
        self,
        select_sql: str,
        target_dir: str,
        partition_by: Optional[List[str]] = None,
        params: Optional[Sequence[Any]] = None,
        compression: str = "zstd",
    ):
        """Dump SELECT query result to parquet files under target_dir.

        Args:
            select_sql (str): SELECT SQL to copy data from.
            target_dir (str): Target directory to store parquet files.
            partition_by (Optional[List[str]]): Partition columns.
            params (Optional[Sequence[Any]]): SQL bind parameters.
            compression (str): Parquet compression, default 'zstd'.
        """
        opts = [f"FORMAT 'parquet'"]
        if compression:
            opts.append(f"COMPRESSION '{compression}'")
        if partition_by:
            cols = ", ".join(DuckParquet._quote_ident(c) for c in partition_by)
            opts.append(f"PARTITION_BY ({cols})")
        options_sql = ", ".join(opts)
        sql = f"COPY ({select_sql}) TO '{target_dir}' ({options_sql})"
        self.con.execute(sql, params)

    def _copy_df_to_dir(
        self,
        df: pd.DataFrame,
        target: str,
        partition_by: Optional[List[str]] = None,
        compression: str = "zstd",
    ):
        """Write pandas DataFrame into partitioned parquet files.

        Args:
            df (pd.DataFrame): Source dataframe.
            target (str): Target directory.
            partition_by (Optional[List[str]]): Partition columns.
            compression (str): Parquet compression.
        """
        reg_name = f"incoming_{uuid.uuid4().hex[:8]}"
        self.con.register(reg_name, df)
        opts = [f"FORMAT 'parquet'"]
        if compression:
            opts.append(f"COMPRESSION '{compression}'")
        if partition_by:
            cols = ", ".join(DuckParquet._quote_ident(c) for c in partition_by)
            opts.append(f"PARTITION_BY ({cols})")
        options_sql = ", ".join(opts)
        if partition_by:
            sql = f"COPY (SELECT * FROM {DuckParquet._quote_ident(reg_name)}) TO '{target}' ({options_sql})"
        else:
            sql = f"COPY (SELECT * FROM {DuckParquet._quote_ident(reg_name)}) TO '{target}/data_0.parquet' ({options_sql})"
        self.con.execute(sql)
        self.con.unregister(reg_name)

    def _atomic_replace_dir(self, new_dir: str, old_dir: str):
        """Atomically replace a directory's contents.

        Args:
            new_dir (str): Temporary directory with new data.
            old_dir (str): Target directory to replace.
        """
        if os.path.exists(old_dir):
            shutil.rmtree(old_dir)
        os.replace(new_dir, old_dir)

    # ---- Upsert Internal Logic ----

    def _upsert_no_exist(self, df: pd.DataFrame, partition_by: Optional[list]) -> None:
        """Upsert logic branch if no existing parquet files.

        Args:
            df (pd.DataFrame): Raw DataFrame
            partition_by (Optional[list]): Partition columns
        """
        tmpdir = self._local_tempdir(".")
        try:
            self._copy_df_to_dir(
                df,
                target=tmpdir,
                partition_by=partition_by,
            )
            self._atomic_replace_dir(tmpdir, self.dataset_path)
        finally:
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir, ignore_errors=True)
        self.refresh()

    def _export_partition(
        self,
        part_row,
        partition_by,
        all_cols,
        key_expr,
        view_ident,
        df,
        tmpdir,
        sql_template,
    ):
        """Export partition sub-data for upsert, called in parallel for each partition.

        Args:
            part_row (pd.Series): Partition key row.
            partition_by (list): Partition columns.
            all_cols (str): Columns to select.
            key_expr (str): Key expression.
            view_ident (str): View identifier.
            df (pd.DataFrame): DataFrame to upsert.
            tmpdir (str): Temporary directory.
            sql_template (str): SQL COPY template.
        """
        temp_name = f"newdata_{uuid.uuid4().hex[:6]}"
        where_clauses = [
            f"{DuckParquet._quote_ident(col)} = '{part_row[col]}'"
            for col in partition_by
        ]
        where_sql = " AND ".join(where_clauses)
        sql = sql_template.format(
            all_cols=all_cols,
            key_expr=key_expr,
            view_ident=view_ident,
            tmpdir=tmpdir,
            temp_name=DuckParquet._quote_ident(temp_name),
            partition_subsql=f"PARTITION_BY ({', '.join(partition_by or [])}),",
        )
        sub_df = df.loc[(df[partition_by] == part_row[partition_by]).all(axis=1)]
        con = duckdb.connect()
        con.register(view_ident, self.select(where=where_sql))
        con.register(temp_name, sub_df)
        con.execute(sql)
        con.unregister(view_ident)
        con.unregister(temp_name)
        con.close()

    def _upsert_existing(
        self, df: pd.DataFrame, keys: list, partition_by: Optional[list]
    ) -> None:
        """Upsert logic branch if existing parquet files already present.

        Args:
            df (pd.DataFrame): Raw DataFrame
            keys (list): Primary key columns
            partition_by (Optional[list]): Partition columns
        """
        tmpdir = self._local_tempdir(".")
        base_cols = self.list_columns()
        view_ident = DuckParquet._quote_ident(self.view_name)
        all_cols = ", ".join(
            [
                DuckParquet._quote_ident(c)
                for c in base_cols
                if c in df.columns or c in base_cols
            ]
        )
        key_expr = ", ".join(keys)
        sql_template = """
            COPY (
                SELECT {all_cols} FROM (
                    SELECT *, ROW_NUMBER() OVER (PARTITION BY {key_expr} ORDER BY is_new DESC) AS rn
                    FROM (
                        SELECT {all_cols}, 0 as is_new FROM {view_ident}
                        UNION ALL
                        SELECT {all_cols}, 1 as is_new FROM {temp_name}
                    )
                ) WHERE rn=1
            ) TO '{tmpdir}' (FORMAT 'parquet', {partition_subsql} OVERWRITE_OR_IGNORE true)
        """
        if not partition_by:
            try:
                temp_name = f"newdata_{uuid.uuid4().hex[:6]}"
                sql = sql_template.format(
                    all_cols=all_cols,
                    key_expr=key_expr,
                    view_ident=view_ident,
                    tmpdir=os.path.join(tmpdir, "data_0.parquet"),
                    temp_name=DuckParquet._quote_ident(temp_name),
                    partition_subsql="",
                )
                self.con.register(view_ident, self.select())
                self.con.register(temp_name, df)
                self.con.execute(sql)
                self.con.unregister(temp_name)
                self.con.unregister(view_ident)
                src_part_dir = os.path.join(tmpdir, "data_0.parquet")
                dst_part_dir = os.path.join(self.dataset_path, "data_0.parquet")
                os.remove(dst_part_dir)
                shutil.move(src_part_dir, dst_part_dir)
            finally:
                shutil.rmtree(tmpdir)
            return

        affected_partitions = df[partition_by].drop_duplicates()
        try:
            Parallel(n_jobs=self.threads, backend="threading")(
                delayed(self._export_partition)(
                    part_row,
                    partition_by,
                    all_cols,
                    key_expr,
                    view_ident,
                    df,
                    tmpdir,
                    sql_template,
                )
                for _, part_row in affected_partitions.iterrows()
            )
            subdirs = next(os.walk(tmpdir))[1]
            for subdir in subdirs:
                src_part_dir = os.path.join(tmpdir, subdir)
                dst_part_dir = os.path.join(self.dataset_path, subdir)
                if os.path.exists(dst_part_dir):
                    if os.path.isdir(dst_part_dir):
                        shutil.rmtree(dst_part_dir)
                    else:
                        os.remove(dst_part_dir)
                os.makedirs(os.path.dirname(dst_part_dir), exist_ok=True)
                shutil.move(src_part_dir, dst_part_dir)
        finally:
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir, ignore_errors=True)
        self.refresh()

    # --- Context/Resource Management ---
    def close(self):
        """Close the DuckDB connection."""
        try:
            self.con.close()
        except Exception:
            pass

    def __enter__(self):
        """Enable usage as a context manager.

        Returns:
            DuckParquet: Current instance.
        """
        return self

    def __exit__(self, exc_type, exc, tb):
        """Context manager exit: close connection."""
        self.close()

    # --- Public Query/Mutation Methods ---

    def refresh(self):
        """Refreshes DuckDB view after manual file changes."""
        self._create_or_replace_view()

    def raw_query(
        self, sql: str, params: Optional[Sequence[Any]] = None
    ) -> pd.DataFrame:
        """Execute a raw SQL query and return results as a DataFrame.

        Args:
            sql (str): SQL statement.
            params (Optional[Sequence[Any]]): Bind parameters.

        Returns:
            pd.DataFrame: Query results.
        """
        res = self.con.execute(sql, params or [])
        try:
            return res.df()
        except Exception:
            return pd.DataFrame()

    def get_schema(self) -> pd.DataFrame:
        """Get the schema (column info) of current parquet dataset.

        Returns:
            pd.DataFrame: DuckDB DESCRIBE result.
        """
        view_ident = DuckParquet._quote_ident(self.view_name)
        return self.con.execute(f"DESCRIBE {view_ident}").df()

    def list_columns(self) -> List[str]:
        """List all columns in the dataset.

        Returns:
            List[str]: Column names in the dataset.
        """
        df = self.get_schema()
        if "column_name" in df.columns:
            return df["column_name"].tolist()
        if "name" in df.columns:
            return df["name"].tolist()
        return df.iloc[:, 0].astype(str).tolist()

    def select(
        self,
        columns: Union[str, List[str]] = "*",
        where: Optional[str] = None,
        params: Optional[Sequence[Any]] = None,
        group_by: Optional[Union[str, List[str]]] = None,
        having: Optional[str] = None,
        order_by: Optional[Union[str, List[str]]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        distinct: bool = False,
    ) -> pd.DataFrame:
        """Query current dataset with flexible SQL generated automatically.

        Args:
            columns (Union[str, List[str]]): Columns to select (* or list of str).
            where (Optional[str]): WHERE clause.
            params (Optional[Sequence[Any]]): Bind parameters for WHERE.
            group_by (Optional[Union[str, List[str]]]): GROUP BY columns.
            having (Optional[str]): HAVING clause.
            order_by (Optional[Union[str, List[str]]]): ORDER BY columns.
            limit (Optional[int]): Max rows to get.
            offset (Optional[int]): Row offset.
            distinct (bool): Whether to add DISTINCT clause.

        Returns:
            pd.DataFrame: Query results.
        """
        view_ident = DuckParquet._quote_ident(self.view_name)
        col_sql = columns if isinstance(columns, str) else ", ".join(columns)
        sql = ["SELECT"]
        if distinct:
            sql.append("DISTINCT")
        sql.append(col_sql)
        sql.append(f"FROM {view_ident}")
        bind_params = list(params or [])
        if where:
            sql.append("WHERE")
            sql.append(where)
        if group_by:
            group_sql = group_by if isinstance(group_by, str) else ", ".join(group_by)
            sql.append("GROUP BY " + group_sql)
        if having:
            sql.append("HAVING " + having)
        if order_by:
            order_sql = order_by if isinstance(order_by, str) else ", ".join(order_by)
            sql.append("ORDER BY " + order_sql)
        if limit is not None:
            sql.append(f"LIMIT {int(limit)}")
        if offset is not None:
            sql.append(f"OFFSET {int(offset)}")
        final = " ".join(sql)
        return self.con.execute(final, bind_params).df()

    def count(
        self, where: Optional[str] = None, params: Optional[Sequence[Any]] = None
    ) -> int:
        """Count rows in the dataset matching the given WHERE clause.

        Args:
            where (Optional[str]): WHERE condition to filter rows.
            params (Optional[Sequence[Any]]): Bind parameters.

        Returns:
            int: The count of rows.
        """
        view_ident = DuckParquet._quote_ident(self.view_name)
        sql = f"SELECT COUNT(*) AS c FROM {view_ident}"
        bind_params = list(params or [])
        if where:
            sql += " WHERE " + where
        return int(self.con.execute(sql, bind_params).fetchone()[0])

    def upsert_from_df(
        self, df: pd.DataFrame, keys: list, partition_by: Optional[list] = None
    ):
        """Upsert rows from DataFrame according to primary keys, overwrite existing rows.

        Args:
            df (pd.DataFrame): New data.
            keys (list): Primary key columns.
            partition_by (Optional[list]): Partition columns.
        """
        if not self._parquet_files_exist():
            self._upsert_no_exist(df, partition_by)
        else:
            self._upsert_existing(df, keys, partition_by)

    def update(
        self,
        set_map: Dict[str, Union[str, Any]],
        where: Optional[str] = None,
        partition_by: Optional[str] = None,
        params: Optional[Sequence[Any]] = None,
    ):
        """Update specified columns for rows matching WHERE.

        Args:
            set_map (Dict[str, Union[str, Any]]): {column: value or SQL expr}.
            where (Optional[str]): WHERE clause.
            partition_by (Optional[str]): Partition column.
            params (Optional[Sequence[Any]]): Bind parameters for WHERE.
        """
        if os.path.isfile(self.dataset_path):
            pass
        view_ident = DuckParquet._quote_ident(self.view_name)
        base_cols = self._base_columns()
        bind_params = list(params or [])
        select_exprs = []
        for col in base_cols:
            col_ident = DuckParquet._quote_ident(col)
            if col in set_map:
                val = set_map[col]
                if where:
                    if isinstance(val, str):
                        expr = f"CASE WHEN ({where}) THEN ({val}) ELSE {col_ident} END AS {col_ident}"
                    else:
                        expr = f"CASE WHEN ({where}) THEN (?) ELSE {col_ident} END AS {col_ident}"
                        bind_params.append(val)
                else:
                    if isinstance(val, str):
                        expr = f"({val}) AS {col_ident}"
                    else:
                        expr = f"(?) AS {col_ident}"
                        bind_params.append(val)
            else:
                expr = f"{col_ident}"
            select_exprs.append(expr)
        select_sql = f"SELECT {', '.join(select_exprs)} FROM {view_ident}"
        tmpdir = self._local_tempdir(".")
        try:
            self._copy_select_to_dir(
                select_sql,
                target_dir=tmpdir,
                partition_by=partition_by,
            )
            self._atomic_replace_dir(tmpdir, self.dataset_path)
        finally:
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir, ignore_errors=True)
        self.refresh()

    def delete(
        self,
        where: str,
        partition_by: Optional[str] = None,
        params: Optional[Sequence[Any]] = None,
    ):
        """Delete rows matching the WHERE clause.

        Args:
            where (str): SQL WHERE condition for deletion.
            partition_by (Optional[str]): Partition column.
            params (Optional[Sequence[Any]]): Bind parameters for WHERE.
        """
        view_ident = DuckParquet._quote_ident(self.view_name)
        bind_params = list(params or [])
        select_sql = f"SELECT * FROM {view_ident} WHERE NOT ({where})"
        tmpdir = self._local_tempdir(".")
        try:
            self._copy_select_to_dir(
                select_sql,
                target_dir=tmpdir,
                partition_by=partition_by,
            )
            self._atomic_replace_dir(tmpdir, self.dataset_path)
        finally:
            if os.path.exists(tmpdir):
                shutil.rmtree(tmpdir, ignore_errors=True)
        self.refresh()


if __name__ == "__main__":
    # Example usage.
    from pathlib import Path
    from tqdm import tqdm

    path = Path("d:/documents/databasebackup/quotes_day")
    data = pd.read_parquet(path)
    data = data[data["time"] > "2025-07-03"]
    dp = DuckParquet("d:/documents/dataset/quotes_day_test", threads=4)
    data["date"] = data["time"].dt.strftime("%Y-%m-%d")
    dp.upsert_from_df(data, keys=["time", "code"], partition_by=["date"])
    print(dp.select())
