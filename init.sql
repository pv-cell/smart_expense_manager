CREATE DATABASE IF NOT EXISTS expense_manager;
CREATE USER IF NOT EXISTS 'appuser'@'%' IDENTIFIED BY 'apppassword';

-- Grant full access on this DB
GRANT ALL PRIVILEGES ON expense_manager.* TO 'appuser'@'%';

-- Apply changes
FLUSH PRIVILEGES;
USE expense_manager;


CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    UNIQUE (name)

);


CREATE TABLE `groups` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE group_members (
    group_id INT,
    user_id INT,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES `groups`(id),
    FOREIGN KEY (user_id) REFERENCES users(id) 
);


CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    paid_by INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description VARCHAR(255),
    expense_date DATE,
    FOREIGN KEY (group_id) REFERENCES `groups`(id),
    FOREIGN KEY (paid_by) REFERENCES users(id)


);


CREATE TABLE expense_splits (
    expense_id INT,
    user_id INT,
    amount DECIMAL(10,2) NOT NULL,
    PRIMARY KEY (expense_id, user_id),
    FOREIGN KEY (expense_id) REFERENCES expenses(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);