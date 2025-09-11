# -*- coding: utf-8 -*-

"""
Command classes for extracting AWS Redshift schema metadata.
"""

import dataclasses

import simple_aws_redshift.api as aws_rs

from .constants import (
    SVV_ALL_TABLES_TABLE_TYPE_ENUM,
    SVV_TABLE_INFO_DISTSTYLE_ENUM,
)
from .model import (
    Database,
    Schema,
    Table,
    View,
    Column,
)
from .sql import sql_enum

SqlCommand = aws_rs.redshift_data_api.SqlCommand


@dataclasses.dataclass(frozen=True)
class BaseCommand(SqlCommand):
    """
    Base command class for executing SQL queries against Redshift.
    """
    def _run_with_sql(self, sql: str):
        """Execute a SQL query and store results in the command object."""
        object.__setattr__(self, "sql", sql)
        return self.run()

    def __post_init__(self):
        """Initialize the command with empty SQL."""
        object.__setattr__(self, "sql", "")
        super().__post_init__()


@dataclasses.dataclass(frozen=True)
class ListDatabaseCommand(BaseCommand):
    """
    Command to list all databases in the Redshift cluster.
    """
    def exec(self) -> list["Database"]:
        """Execute the command and return a list of Database objects."""
        self._run_with_sql(sql_enum.s01_01_list_database)
        databases = list()
        for row in self.result.vdf.iter_rows():
            database = Database(
                database_name=row[0],
                database_type=row[1],
            )
            databases.append(database)
        return databases


@dataclasses.dataclass(frozen=True)
class ListSchemaCommand(BaseCommand):
    """
    Command to list all schemas across all databases.
    """
    def exec(self) -> list["Schema"]:
        """Execute the command and return a list of Schema objects."""
        self._run_with_sql(sql_enum.s02_01_list_schema)
        schemas = list()
        for row in self.result.vdf.iter_rows():
            schema = Schema(
                database_name=row[0],
                database_type=row[1],
                schema_name=row[2],
                schema_type=row[3],
            )
            schemas.append(schema)
        return schemas


@dataclasses.dataclass(frozen=True)
class ListTableCommand(BaseCommand):
    """
    Command to list all tables and views across all schemas.
    """
    def exec(self) -> tuple[list["Table"], list["View"]]:
        """Execute the command and return tuple of (tables, views) lists."""
        tables = list()
        views = list()

        # native schema table only (no view)
        self._run_with_sql(
            sql_enum.s03_01_list_table_on_native_database_from_native_schema
        )
        # self.result.vdf.show()  # for debug only
        table_keys = self.result.vdf.col_data["table_key"]
        for row in self.result.vdf.iter_rows():
            table = Table(
                database_name=row[1],
                schema_name=row[2],
                table_name=row[4],
                diststyle=row[5],
            )
            tables.append(table)

        # native schema view, and external schema table and view
        keys = ", ".join([f"'{key}'" for key in table_keys])
        sql = sql_enum.s03_02_list_table_or_view_on_native_database_from_shared_schema.format(
            keys=keys,
        )
        self._run_with_sql(sql)
        # self.result.vdf.show()  # for debug only

        for row in self.result.vdf.iter_rows():
            table_type = row[3]
            if table_type == SVV_ALL_TABLES_TABLE_TYPE_ENUM.VIEW.value:
                view = View(
                    database_name=row[1],
                    schema_name=row[2],
                    view_name=row[4],
                )
                views.append(view)
            elif table_type in [
                SVV_ALL_TABLES_TABLE_TYPE_ENUM.TABLE.value,
                SVV_ALL_TABLES_TABLE_TYPE_ENUM.EXTERNAL_TABLE.value,
            ]:
                table = Table(
                    database_name=row[1],
                    schema_name=row[2],
                    table_name=row[4],
                    diststyle=SVV_TABLE_INFO_DISTSTYLE_ENUM.UNKNOWN.value,
                )
                tables.append(table)
            else:
                pass

        return tables, views


@dataclasses.dataclass(frozen=True)
class ListColumnsCommand(BaseCommand):
    """
    Command to list all columns across all tables and views.
    """
    def exec(self) -> list["Column"]:
        """Execute the command and return a list of Column objects."""
        self._run_with_sql(sql_enum.s04_01_list_columns)
        columns = list()
        for row in self.result.vdf.iter_rows():
            column = Column(
                database_name=row[0],
                schema_name=row[1],
                table_name=row[2],
                column_name=row[3],
                data_type=row[4],
                is_nullable=row[5],
            )
            columns.append(column)
        return columns
