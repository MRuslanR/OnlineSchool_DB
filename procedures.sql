CREATE OR REPLACE PROCEDURE create_database_proc()
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE 'DROP DATABASE IF EXISTS ' || quote_ident('online_school');
    EXECUTE 'CREATE DATABASE ' || quote_ident('online_school');
END;
$$;

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

CREATE OR REPLACE PROCEDURE clear_table_proc(table_name TEXT)
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE 'TRUNCATE TABLE ' || quote_ident(table_name) || ' RESTART IDENTITY CASCADE';
END;
$$;

CREATE OR REPLACE PROCEDURE add_record_to_table(
    table_name TEXT,
    column_names TEXT[],
    column_values TEXT[]
)
LANGUAGE plpgsql AS $$
DECLARE
    query TEXT;
    value_placeholders TEXT;
BEGIN
    query := format(
        'INSERT INTO %I (%s) VALUES (%s)',
        table_name,
        array_to_string(column_names, ', '),
        array_to_string(
            array(SELECT quote_literal(v) FROM unnest(column_values) v),
            ', '
        )
    );

    EXECUTE query;
END;
$$;

CREATE OR REPLACE FUNCTION get_columns_excluding_timestamp(table_name TEXT)
RETURNS TABLE(column_name TEXT) LANGUAGE sql AS $$
    SELECT column_name
    FROM information_schema.columns
    WHERE table_name = table_name AND data_type NOT LIKE 'timestamp%';
$$;

CREATE OR REPLACE PROCEDURE delete_records_by_condition(table_name TEXT, column_name TEXT, condition TEXT)
LANGUAGE plpgsql AS $$
DECLARE
    query TEXT;
BEGIN
    query := format('DELETE FROM %I WHERE %I ILIKE %L', table_name, column_name, condition);
    EXECUTE query;
END;
$$;

CREATE OR REPLACE PROCEDURE get_table_content(table_name TEXT, OUT result_set REFCURSOR)
LANGUAGE plpgsql AS $$
BEGIN
    OPEN result_set FOR EXECUTE format('SELECT * FROM %I', table_name);
END;
$$;

CREATE OR REPLACE PROCEDURE clear_all_tables_proc()
LANGUAGE plpgsql
AS $$
DECLARE
    table_record RECORD;
BEGIN
    FOR table_record IN
        SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'
    LOOP
        EXECUTE 'CALL clear_table_proc(' || quote_literal(table_record.table_name) || ')';
    END LOOP;
END;
$$;

CREATE OR REPLACE FUNCTION get_primary_key_column(
    table_name TEXT
) RETURNS TEXT AS $$
DECLARE
    primary_key_column TEXT;
BEGIN
    SELECT a.attname
    INTO primary_key_column
    FROM pg_index i
    JOIN pg_attribute a ON a.attrelid = i.indrelid
                        AND a.attnum = ANY(i.indkey)
    WHERE i.indrelid = table_name::regclass
      AND i.indisprimary;

    RETURN primary_key_column;
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE delete_records_by_condition_proc(
    table_name TEXT,
    search_column TEXT,
    search_value TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    query TEXT;
BEGIN
    query := format(
        'DELETE FROM %I WHERE %I::text ILIKE %L',
        table_name, search_column, '%' || search_value || '%'
    );

    EXECUTE query;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_record_by_pk_proc(
    table_name TEXT,
    pk_column TEXT,
    pk_value TEXT
)
LANGUAGE plpgsql
AS $$
DECLARE
    query TEXT;
BEGIN
    query := format(
        'DELETE FROM %I WHERE %I = %L',
        table_name, pk_column, pk_value
    );

    EXECUTE query;
END;
$$;

CREATE OR REPLACE FUNCTION get_columns(p_table_name text)
RETURNS SETOF text
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT column_name::text
    FROM information_schema.columns
    WHERE table_name = p_table_name AND data_type NOT LIKE 'timestamp%';
END;
$$;
