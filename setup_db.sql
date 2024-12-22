-- Создание таблицы Users
CREATE TABLE Users (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL UNIQUE,
    surname VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('student', 'instructor', 'admin')),
    email VARCHAR(100) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы Courses
CREATE TABLE Courses (
    course_id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    instructor_id INTEGER NOT NULL,
    start_time TIMESTAMP NOT NULL,
    duration INTERVAL NOT NULL,
    FOREIGN KEY (instructor_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Создание таблицы Enrollments
CREATE TABLE Enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    course_id INTEGER NOT NULL,
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (course_id) REFERENCES Courses(course_id) ON DELETE CASCADE
);

-- Создание таблицы Payments
CREATE TABLE Payments (
    payment_id SERIAL PRIMARY KEY,
    enrollment_id INTEGER NOT NULL,
    amount NUMERIC(10, 2) NOT NULL CHECK (amount > 0),
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount NUMERIC(10, 2) DEFAULT 0,
    FOREIGN KEY (enrollment_id) REFERENCES Enrollments(enrollment_id) ON DELETE CASCADE
);

-- Создание индекса на поле username в таблице Users
CREATE INDEX idx_users_username ON Users(username);

-- Создание индекса на поле title в таблице Courses
CREATE INDEX idx_courses_title ON Courses(title);

-- Функция для обновления total_amount
CREATE OR REPLACE FUNCTION update_total_amount()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'INSERT' OR TG_OP = 'UPDATE' OR TG_OP = 'DELETE') THEN
        UPDATE Payments
        SET total_amount = (
            SELECT SUM(amount)
            FROM Payments
            WHERE enrollment_id = OLD.enrollment_id
        )
        WHERE enrollment_id = OLD.enrollment_id;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Создание триггера после вставки, обновления или удаления в таблице Payments
CREATE TRIGGER trg_update_total_amount
AFTER INSERT OR UPDATE OR DELETE ON Payments
FOR EACH ROW
EXECUTE FUNCTION update_total_amount();