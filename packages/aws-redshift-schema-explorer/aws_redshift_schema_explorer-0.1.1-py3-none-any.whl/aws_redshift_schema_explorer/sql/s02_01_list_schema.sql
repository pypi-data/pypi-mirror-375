SELECT
    t.database_name,
    t1.database_type,
    t.schema_name,
    t.schema_type
FROM SVV_ALL_SCHEMAS t
    JOIN SVV_REDSHIFT_DATABASES t1
    ON t.database_name = t1.database_name
ORDER BY
    t1.database_type,
    t.database_name,
    t.schema_type,
    t.schema_name