-- Delete all data from tables in the correct order to respect foreign key constraints
DELETE FROM feedback;
DELETE FROM facility_usage;
DELETE FROM visits;
DELETE FROM users;
DELETE FROM facilities;


