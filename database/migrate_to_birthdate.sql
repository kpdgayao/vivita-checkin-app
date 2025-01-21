-- 1. First add the new birthdate column (nullable initially)
ALTER TABLE users ADD COLUMN IF NOT EXISTS birthdate DATE;

-- 2. Calculate and set approximate birthdates based on existing age
-- This will set birthdate to the same day of current year minus their age
UPDATE users 
SET birthdate = (CURRENT_DATE - (age || ' years')::INTERVAL)::DATE
WHERE birthdate IS NULL AND age IS NOT NULL;

-- 3. Make birthdate column required
ALTER TABLE users ALTER COLUMN birthdate SET NOT NULL;

-- 4. Remove the age column
ALTER TABLE users DROP COLUMN IF EXISTS age;
