-- Create a new table 'Service' with a primary key and columns
CREATE TABLE Service (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    url VARCHAR(1024) NOT NULL
);

-- Create a new table 'Environment' with a primary key and columns
CREATE TABLE Environment (
    id SERIAL PRIMARY KEY,
    name VARCHAR(500) NOT NULL,
    region VARCHAR(120) NOT NULL,
    cluster VARCHAR(120) NOT NULL
);