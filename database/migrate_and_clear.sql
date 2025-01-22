-- First, delete all data from tables in the correct order
DELETE FROM feedback;
DELETE FROM facility_usage;
DELETE FROM visits;
DELETE FROM users;
DELETE FROM facilities;

-- Drop the old tables completely since we're starting fresh
DROP TABLE IF EXISTS feedback CASCADE;
DROP TABLE IF EXISTS facility_usage CASCADE;
DROP TABLE IF EXISTS visits CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS facilities CASCADE;

-- Recreate tables with new schema
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    birthdate DATE NOT NULL CHECK (birthdate <= CURRENT_DATE AND birthdate >= '1920-01-01'),
    school_organization TEXT NOT NULL,
    emergency_contact TEXT,
    photo_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS visits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    check_in_time TIMESTAMP WITH TIME ZONE NOT NULL,
    check_out_time TIMESTAMP WITH TIME ZONE,
    duration FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS facilities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('Arts & Crafts', 'Tech-Art')),
    type TEXT NOT NULL CHECK (type IN ('consumable', 'lease')),
    description TEXT,
    status TEXT DEFAULT 'available' CHECK (status IN ('available', 'in_use', 'maintenance', 'unavailable')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS facility_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    visit_id UUID REFERENCES visits(id) ON DELETE CASCADE,
    facility_name TEXT NOT NULL,
    facility_type TEXT NOT NULL CHECK (facility_type IN ('consumable', 'lease')),
    usage_duration FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    visit_id UUID REFERENCES visits(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for faster searches
CREATE INDEX idx_users_first_name ON users(first_name);
CREATE INDEX idx_users_last_name ON users(last_name);
CREATE INDEX idx_visits_user_id ON visits(user_id);
CREATE INDEX idx_visits_check_in_time ON visits(check_in_time);
CREATE INDEX idx_facility_usage_visit_id ON facility_usage(visit_id);
CREATE INDEX idx_feedback_visit_id ON feedback(visit_id);

-- Create updated_at triggers
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Add triggers to all tables
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_visits_updated_at
    BEFORE UPDATE ON visits
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_facilities_updated_at
    BEFORE UPDATE ON facilities
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_facility_usage_updated_at
    BEFORE UPDATE ON facility_usage
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_feedback_updated_at
    BEFORE UPDATE ON feedback
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Re-insert default facilities
INSERT INTO facilities (name, category, type, description, status) VALUES
    ('Button Pin Maker', 'Arts & Crafts', 'consumable', 'Create custom button pins', 'available'),
    ('Art Supplies', 'Arts & Crafts', 'consumable', 'General art supplies', 'available'),
    ('Jewelry Making Tools', 'Arts & Crafts', 'consumable', 'Tools for jewelry making', 'available'),
    ('Jewelry Making Materials', 'Arts & Crafts', 'consumable', 'Materials for jewelry making', 'available'),
    ('Tablets', 'Tech-Art', 'lease', 'Digital tablets for art creation', 'available'),
    ('3D Printer', 'Tech-Art', 'lease', '3D printing equipment', 'available'),
    ('Cricut', 'Tech-Art', 'lease', 'Cricut cutting machine', 'available'),
    ('Polymer Clay', 'Tech-Art', 'lease', 'Clay for modeling', 'available'),
    ('Heat Press', 'Tech-Art', 'lease', 'Heat press for transfers', 'available'),
    ('Heat Shrink Materials', 'Tech-Art', 'lease', 'Heat shrink crafting materials', 'available'),
    ('Desktop Computer', 'Tech-Art', 'lease', 'Computer for digital work', 'available'),
    ('Robotics Kit', 'Tech-Art', 'lease', 'Kit for robotics projects', 'available');
