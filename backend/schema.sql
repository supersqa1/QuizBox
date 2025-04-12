CREATE TABLE IF NOT EXISTS quizzes (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    user_id INTEGER NOT NULL,
    quiz_type VARCHAR(20) NOT NULL,
    question_text TEXT NOT NULL,
    answer_text TEXT NOT NULL,
    theme_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (theme_id) REFERENCES themes(id)
); 