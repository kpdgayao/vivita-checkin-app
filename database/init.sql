-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    birthdate DATE NOT NULL CHECK (birthdate <= CURRENT_DATE AND birthdate >= '1920-01-01'),
    guardian_name TEXT NOT NULL,
    guardian_contact TEXT NOT NULL,
    emergency_contact TEXT,
    photo_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Visits table
CREATE TABLE IF NOT EXISTS visits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    check_in_time TIMESTAMP WITH TIME ZONE NOT NULL,
    check_out_time TIMESTAMP WITH TIME ZONE,
    duration FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Facilities table
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

-- Facility usage table
CREATE TABLE IF NOT EXISTS facility_usage (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    visit_id UUID REFERENCES visits(id) ON DELETE CASCADE,
    facility_name TEXT NOT NULL,
    facility_type TEXT NOT NULL CHECK (facility_type IN ('consumable', 'lease')),
    usage_duration FLOAT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    visit_id UUID REFERENCES visits(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    comments TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

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

-- Insert default facilities
INSERT INTO facilities (name, category, type, description) VALUES
    ('Button Pin Maker', 'Arts & Crafts', 'consumable', 'Create custom button pins'),
    ('Art Supplies', 'Arts & Crafts', 'consumable', 'General art supplies'),
    ('Jewelry Making Tools', 'Arts & Crafts', 'consumable', 'Tools for jewelry making'),
    ('Jewelry Making Materials', 'Arts & Crafts', 'consumable', 'Materials for jewelry making'),
    ('Tablets', 'Tech-Art', 'lease', 'Digital tablets for art creation'),
    ('3D Printer', 'Tech-Art', 'lease', '3D printing equipment'),
    ('Cricut', 'Tech-Art', 'lease', 'Cricut cutting machine'),
    ('Polymer Clay', 'Tech-Art', 'lease', 'Clay for modeling'),
    ('Heat Press', 'Tech-Art', 'lease', 'Heat press for transfers'),
    ('Heat Shrink Materials', 'Tech-Art', 'lease', 'Heat shrink crafting materials')
ON CONFLICT DO NOTHING;
