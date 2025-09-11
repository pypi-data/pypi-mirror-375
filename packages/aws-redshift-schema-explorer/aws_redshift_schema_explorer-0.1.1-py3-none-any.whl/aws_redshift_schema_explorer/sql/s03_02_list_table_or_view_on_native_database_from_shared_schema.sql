SELECT
    t.database_name || '.' || t.schema_name || '.' || t.table_name AS table_key,
    t.database_name,
    t.schema_name,
    t.table_type,
    t.table_name
FROM SVV_ALL_TABLES t
WHERE
    table_key NOT IN ({keys})
ORDER BY
    t.database_name,
    t.schema_name,
    t.table_type,
    table_name