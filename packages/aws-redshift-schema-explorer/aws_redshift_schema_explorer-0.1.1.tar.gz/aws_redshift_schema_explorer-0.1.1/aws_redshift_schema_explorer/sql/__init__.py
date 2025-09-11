# -*- coding: utf-8 -*-

from pathlib import Path
from functools import cached_property

dir_here = Path(__file__).absolute().parent


def load_sql(name: str) -> str:
    path = dir_here / f"{name}.sql"
    return path.read_text(encoding="utf-8").strip()


class SqlEnum:
    """ """

    @cached_property
    def s01_01_list_database(self):
        return load_sql("s01_01_list_database")

    @cached_property
    def s02_01_list_schema(self):
        return load_sql("s02_01_list_schema")

    @cached_property
    def s03_01_list_table_on_native_database_from_native_schema(self):
        return load_sql("s03_01_list_table_on_native_database_from_native_schema")

    @cached_property
    def s03_02_list_table_or_view_on_native_database_from_shared_schema(self):
        return load_sql("s03_02_list_table_or_view_on_native_database_from_shared_schema")

    @cached_property
    def s04_01_list_columns(self):
        return load_sql("s04_01_list_columns")


sql_enum = SqlEnum()
