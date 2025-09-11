SELECT
    database_name,
    schema_name,
    table_name,
    column_name,
    data_type,
    is_nullable
FROM SVV_ALL_COLUMNS t
WHERE
    schema_name NOT LIKE 'pg_%'
    AND schema_name NOT IN ('information_schema', 'catalog_history')
ORDER BY
    database_name,
    schema_name,
    table_name,
    ordinal_position