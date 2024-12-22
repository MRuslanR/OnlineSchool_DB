-- procedures.sql

-- Процедура для создания базы данных
CREATE OR REPLACE PROCEDURE create_database_proc()
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE 'DROP DATABASE IF EXISTS ' || quote_ident('online_school');
    EXECUTE 'CREATE DATABASE ' || quote_ident('online_school');
END;
$$;

-- Процедура для удаления базы данных
CREATE OR REPLACE PROCEDURE delete_database_proc()
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE 'SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = ''online_school'' AND pid <> pg_backend_pid()';
    EXECUTE 'DROP DATABASE IF EXISTS ' || quote_ident('online_school');
END;
$$;

CREATE OR REPLACE FUNCTION load_tables_proc()
RETURNS TABLE(table_name TEXT) AS
$$
BEGIN
    RETURN QUERY
    SELECT t.table_name::TEXT
    FROM information_schema.tables t
    WHERE t.table_schema = 'public';
END;
$$ LANGUAGE plpgsql;


-- Процедура для очистки таблицы
CREATE OR REPLACE PROCEDURE clear_table_proc(table_name TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE 'TRUNCATE TABLE ' || quote_ident(table_name) || ' RESTART IDENTITY';
END;
$$;
