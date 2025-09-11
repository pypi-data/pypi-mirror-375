# -*- coding: utf-8 -*-

"""
Enumerations for AWS Redshift system view column values and types.
"""

from enum_mate.api import BetterStrEnum


class SVV_REDSHIFT_DATABASES_DATABASE_TYPE_ENUM(BetterStrEnum):
    """
    Database types from SVV_REDSHIFT_DATABASES system view.
    """
    LOCAL = "local"
    SHARED = "shared"


class SVV_ALL_SCHEMAS_SCHEMA_TYPE_ENUM(BetterStrEnum):
    """
    Schema types from SVV_ALL_SCHEMAS system view.
    """
    LOCAL = "local"
    EXTERNAL = "external"


class SVV_ALL_TABLES_TABLE_TYPE_ENUM(BetterStrEnum):
    """
    See: https://docs.aws.amazon.com/redshift/latest/dg/r_SVV_ALL_TABLES.html
    """

    TABLE = "TABLE"
    EXTERNAL_TABLE = "EXTERNAL TABLE"
    VIEW = "VIEW"


class SVV_TABLES_TABLE_TYPE_ENUM(BetterStrEnum):
    """
    See: https://docs.aws.amazon.com/redshift/latest/dg/r_SVV_TABLES.html
    """

    BASE_TABLE = "BASE TABLE"
    EXTERNAL_TABLE = "EXTERNAL TABLE"
    VIEW = "VIEW"


class SVV_EXTERNAL_TABLES_TABLE_TYPE_ENUM(BetterStrEnum):
    """
    See: https://docs.aws.amazon.com/redshift/latest/dg/r_SVV_EXTERNAL_TABLES.html
    """

    TABLE = "TABLE"
    VIEW = "VIEW"
    MATERIALIZED_VIEW = "MATERIALIZED_VIEW"
    EMPTY = ""


class SVV_TABLE_INFO_DISTSTYLE_ENUM(BetterStrEnum):
    """Distribution styles for Redshift tables."""
    EVEN = "EVEN"
    KEY = "KEY"
    ALL = "ALL"
    AUTO_EVEN = "AUTO(EVEN)"
    AUTO_KEY = "AUTO(KEY)"  # sometimes redshift returns AUTO(KEY(col_name)))
    AUTO_ALL = "AUTO(ALL)"
    UNKNOWN = "UNKNOWN"


class SVV_ALL_COLUMNS_DATA_TYPE_ENUM(BetterStrEnum):
    """
    See: https://docs.aws.amazon.com/redshift/latest/dg/r_SVV_ALL_COLUMNS.html

    Available values:

    ""char""
    ""char"[]"
    "abstime"
    "aclitem[]"
    "anyarray"
    "array<bigint>"
    "array<string>"
    "bigint"
    "boolean"
    "bytea"
    "cardinal_number"
    "character"
    "character varying"
    "character_data"
    "date"
    "double precision"
    "int2vector"
    "integer"
    "integer[]"
    "interval"
    "name"
    "numeric"
    "oid"
    "oid[]"
    "oidvector"
    "real"
    "real[]"
    "regproc"
    "smallint"
    "smallint[]"
    "sql_identifier"
    "string"
    "super"
    "text"
    "text[]"
    "tid"
    "timestamp"
    "timestamp with time zone"
    "timestamp without time zone"
    "xid"
    """

    char = "char"
    # "char[]"
    abstime = "abstime"
    # "aclitem[]"
    anyarray = "anyarray"
    array = "array"
    # "array<bigint>"
    # "array<string>"
    bigint = "bigint"
    boolean = "boolean"
    bytea = "bytea"
    cardinal_number = "cardinal_number"
    character = "character"
    character_varying = "character varying"
    character_data = "character_data"
    date = "date"
    double_precision = "double precision"
    int2vector = "int2vector"
    integer = "integer"
    # "integer[]"
    interval = "interval"
    name = "name"
    numeric = "numeric"
    oid = "oid"
    # "oid[]"
    oidvector = "oidvector"
    real = "real"
    # "real[]"
    regproc = "regproc"
    smallint = "smallint"
    # "smallint[]"
    sql_identifier = "sql_identifier"
    string = "string"
    super = "super"
    text = "text"
    # "text[]"
    tid = "tid"
    timestamp = "timestamp"
    timestamp_with_time_zone = "timestamp with time zone"
    timestamp_without_time_zone = "timestamp without time zone"
    xid = "xid"


class PG_CLASS_REL_KIND_ENUM(BetterStrEnum):
    """
    See: https://www.postgresql.org/docs/current/catalog-pg-class.html
    """

    ORDINARY_TABLE = "r"
    INDEX = "i"
    SEQUENCE = "S"
    TOAST_TABLE = "t"
    VIEW = "v"
    MATERIALIZED_VIEW = "m"
    COMPOSITE_TYPE = "c"
    FOREIGN_TABLE = "f"
    PARTITIONED_TABLE = "p"
    PARTITIONED_INDEX = "I"
