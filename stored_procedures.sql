-- Хранимая процедура для добавления пользователя
CREATE OR REPLACE PROCEDURE add_user(
    p_username VARCHAR,
    p_password VARCHAR,
    p_role VARCHAR,
    p_email VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO Users (username, password, role, email)
    VALUES (p_username, p_password, p_role, p_email);
END;
$$;

-- Хранимая процедура для добавления курса
CREATE OR REPLACE PROCEDURE add_course(
    p_title VARCHAR,
    p_description TEXT,
    p_instructor_id INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO Courses (title, description, instructor_id)
    VALUES (p_title, p_description, p_instructor_id);
END;
$$;

-- Хранимая процедура для добавления записи (Enrollments)
CREATE OR REPLACE PROCEDURE add_enrollment(
    p_user_id INTEGER,
    p_course_id INTEGER
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO Enrollments (user_id, course_id)
    VALUES (p_user_id, p_course_id);
END;
$$;

-- Хранимая процедура для добавления платежа
CREATE OR REPLACE PROCEDURE add_payment(
    p_enrollment_id INTEGER,
    p_amount NUMERIC
)
LANGUAGE plpgsql
AS $$
BEGIN
    INSERT INTO Payments (enrollment_id, amount)
    VALUES (p_enrollment_id, p_amount);
END;
$$;

-- Хранимая процедура для удаления базы данных
CREATE OR REPLACE PROCEDURE drop_database()
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE 'DROP DATABASE online_school';
END;
$$;

-- Хранимая процедура для очистки таблицы
CREATE OR REPLACE PROCEDURE clear_table(p_table_name VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format('TRUNCATE TABLE %I CASCADE', p_table_name);
END;
$$;

-- Хранимая процедура для поиска по username
CREATE OR REPLACE FUNCTION search_users(p_username VARCHAR)
RETURNS TABLE(user_id INTEGER, username VARCHAR, email VARCHAR, role VARCHAR, created_at TIMESTAMP)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT user_id, username, email, role, created_at
    FROM Users
    WHERE username ILIKE '%'  p_username  '%';
END;
$$;

-- Хранимая процедура для обновления пользователя
CREATE OR REPLACE PROCEDURE update_user(
    p_user_id INTEGER,
    p_username VARCHAR,
    p_email VARCHAR,
    p_role VARCHAR
)
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE Users
    SET username = p_username,
        email = p_email,
        role = p_role
    WHERE user_id = p_user_id;
END;
$$;

-- Хранимая процедура для удаления пользователя по username
CREATE OR REPLACE PROCEDURE delete_user_by_username(p_username VARCHAR)
LANGUAGE plpgsql
AS $$
BEGIN
    DELETE FROM Users WHERE username = p_username;
END;
$$;