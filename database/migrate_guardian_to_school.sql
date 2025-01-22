-- Backup users table
CREATE TABLE users_backup AS SELECT * FROM users;

-- Add new columns
ALTER TABLE users
ADD COLUMN first_name TEXT,
ADD COLUMN last_name TEXT,
ADD COLUMN school_organization TEXT;

-- Split name into first_name and last_name
UPDATE users
SET 
    first_name = SPLIT_PART(name, ' ', 1),
    last_name = SUBSTRING(name FROM POSITION(' ' IN name) + 1);

-- Set school_organization to a default value
UPDATE users
SET school_organization = 'Not Specified';

-- Make new columns NOT NULL
ALTER TABLE users
ALTER COLUMN first_name SET NOT NULL,
ALTER COLUMN last_name SET NOT NULL,
ALTER COLUMN school_organization SET NOT NULL;

-- Drop old columns
ALTER TABLE users
DROP COLUMN name,
DROP COLUMN guardian_name,
DROP COLUMN guardian_contact;

-- Create index on first_name and last_name for faster searches
CREATE INDEX idx_users_first_name ON users(first_name);
CREATE INDEX idx_users_last_name ON users(last_name);
