SELECT
    database_name,
    database_type
FROM SVV_REDSHIFT_DATABASES
ORDER BY database_type, database_name