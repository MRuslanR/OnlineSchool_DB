
CREATE TABLE Users (
    user_id INTEGER PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(10) CHECK (role IN ('student', 'parent', 'tutor')) NOT NULL
);

CREATE TABLE Tutors (
    tutor_id INTEGER PRIMARY KEY,
    user_id INT UNIQUE NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    rating FLOAT DEFAULT 0,
    bio TEXT
);

CREATE TABLE Subjects (
    subject_id SERIAL PRIMARY KEY,
    title VARCHAR(100) UNIQUE NOT NULL,
    level VARCHAR(15) CHECK (level IN ('beginner', 'intermediate', 'advanced')) NOT NULL
);

CREATE TABLE Sessions (
    session_id SERIAL PRIMARY KEY,
    tutor_id INT NOT NULL REFERENCES Tutors(tutor_id) ON DELETE CASCADE,
    subject_id INT NOT NULL REFERENCES Subjects(subject_id) ON DELETE CASCADE,
    session_date DATE NOT NULL,
    duration INTEGER NOT NULL
);

CREATE TABLE Payments (
    payment_id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES Sessions(session_id) ON DELETE CASCADE,
    amount DECIMAL(10, 2) NOT NULL,
    payment_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method VARCHAR(15) CHECK (payment_method IN ('credit_card', 'paypal', 'bank_transfer')) NOT NULL
);

CREATE TABLE Enrollments (
    enrollment_id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES Sessions(session_id) ON DELETE CASCADE,
    student_id INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    enrollment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Reviews (
    review_id SERIAL PRIMARY KEY,
    session_id INT NOT NULL REFERENCES Sessions(session_id) ON DELETE CASCADE,
    student_id INT NOT NULL REFERENCES Users(user_id) ON DELETE CASCADE,
    rating INT CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION update_tutor_rating() RETURNS TRIGGER AS $$
BEGIN
    UPDATE Tutors
    SET rating = (SELECT AVG(rating) FROM Reviews WHERE session_id IN
    (SELECT session_id FROM Sessions  WHERE tutor_id =
    (SELECT tutor_id FROM Sessions  WHERE session_id = NEW.session_id)))
    WHERE tutor_id = (SELECT tutor_id FROM Sessions  WHERE session_id = NEW.session_id);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_review_insert
AFTER INSERT ON Reviews
FOR EACH ROW EXECUTE FUNCTION update_tutor_rating();

CREATE INDEX idx_users_role ON Users(role);

CREATE INDEX idx_sessions_subject_id ON Sessions(subject_id);