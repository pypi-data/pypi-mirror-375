# -*- coding: utf-8 -*-

"""Data models for AWS Redshift schema entities."""

import dataclasses


@dataclasses.dataclass(frozen=True, slots=True)
class Database:
    """Represents a Redshift database with name and type information."""
    database_name: str
    database_type: str


@dataclasses.dataclass(frozen=True, slots=True)
class Schema:
    """Represents a Redshift schema with database context and schema details."""
    database_name: str
    database_type: str
    schema_name: str
    schema_type: str


@dataclasses.dataclass(frozen=True, slots=True)
class Table:
    """Represents a Redshift table with location and distribution information."""
    database_name: str
    schema_name: str
    table_name: str
    diststyle: str


@dataclasses.dataclass(frozen=True, slots=True)
class View:
    """Represents a Redshift view with location information."""
    database_name: str
    schema_name: str
    view_name: str


@dataclasses.dataclass(slots=True)
class Column:
    """Represents a Redshift column with table context and data type information."""
    database_name: str
    schema_name: str
    table_name: str
    column_name: str
    data_type: str
    is_nullable: str
