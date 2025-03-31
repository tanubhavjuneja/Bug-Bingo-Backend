SQL Statements to Create Database and Tables:
Create Database:

sql
Copy
CREATE DATABASE IF NOT EXISTS bingo;
USE bingo;
Create Table for Storing Scores (scores):

sql
Copy
CREATE TABLE IF NOT EXISTS `scores` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `rollno` VARCHAR(255) NOT NULL,
    `score` INT NOT NULL,
    UNIQUE KEY `unique_rollno` (`rollno`)
);
Create Table for Storing Submissions (submissions):

sql
Copy
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
Explanation of the Tables:
scores table: This table stores student names, roll numbers, and their scores. The rollno column is set to be unique.

submissions table: This table records the code submissions, along with the name, roll number, execution time, result (correct or incorrect), language (either Python or C++), and the submission timestamp.
