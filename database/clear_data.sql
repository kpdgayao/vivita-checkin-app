-- Delete all data from tables in the correct order to respect foreign key constraints
DELETE FROM feedback;
DELETE FROM facility_usage;
DELETE FROM visits;
DELETE FROM users;
DELETE FROM facilities;

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
    ('Heat Shrink Materials', 'Tech-Art', 'lease', 'Heat shrink crafting materials', 'available');
