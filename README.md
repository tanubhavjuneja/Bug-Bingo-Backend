CREATE DATABASE IF NOT EXISTS bingo;
USE bingo;
CREATE TABLE IF NOT EXISTS `scores` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `rollno` VARCHAR(255) NOT NULL,
    `score` INT NOT NULL,
    UNIQUE KEY `unique_rollno` (`rollno`)
);
CREATE TABLE IF NOT EXISTS `submissions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `rollno` VARCHAR(255) NOT NULL,
    `code` TEXT NOT NULL,
    `execution_time` FLOAT NOT NULL,
    `result` INT NOT NULL,  -- Use 1 for correct, 0 for incorrect
    `language` ENUM('python', 'cpp') NOT NULL,
    `submitted_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
