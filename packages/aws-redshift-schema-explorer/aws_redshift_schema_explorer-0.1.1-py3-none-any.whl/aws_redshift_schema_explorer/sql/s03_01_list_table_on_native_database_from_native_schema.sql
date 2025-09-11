SELECT
    t.database || '.' || t.schema || '.' || t.table AS table_key,
    t.database,
    t.schema,
    t1.table_type,
    t.table,
    t.diststyle
FROM SVV_TABLE_INFO t
    LEFT JOIN SVV_TABLES t1
    ON
        t.database = t1.table_catalog
        AND t.schema = t1.table_schema
        AND t.table = t1.table_name
WHERE
    t.schema NOT LIKE 'pg_%'
    AND t.schema NOT IN ('information_schema', 'catalog_history')
ORDER BY
    t.database,
    t.schema