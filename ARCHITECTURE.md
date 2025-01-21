# Vivita Check-in App Architecture

## System Overview

The Vivita Check-in App is a Streamlit-based web application that manages makerspace attendance and facility usage. It uses Supabase as its backend database and real-time engine. The app is designed for the Philippine timezone and includes comprehensive tracking of makerspace activities.

## Architecture Components

### 1. Frontend (Streamlit)

```
app.py
├── Main Interface
│   ├── Navigation Component
│   └── Current Date/Time Display (PH timezone)
├── Check-in/out Interface
│   ├── User Search
│   ├── Active Visitors Display
│   ├── Check-in Process
│   └── Check-out Process with Feedback
├── User Management
│   ├── Registration Form
│   │   ├── Basic Information
│   │   ├── Age Validation (5+ years)
│   │   └── Guardian Information
│   └── User List View
└── Admin Dashboard
    ├── Date Range Selection
    ├── Summary Metrics
    ├── Visit Records
    ├── Interactive Visualizations
    │   ├── Daily Visits Chart
    │   └── Facility Usage Chart
    └── Data Export (CSV)
```

### 2. Backend (Supabase)

#### Database Schema
```sql
users
├── id (UUID, primary key)
├── name (text, required)
├── birthdate (date, required)
├── guardian_name (text, required)
├── guardian_contact (text, required)
├── emergency_contact (text)
├── photo_url (text)
├── created_at (timestamp)
└── updated_at (timestamp)

visits
├── id (UUID, primary key)
├── user_id (UUID, foreign key)
├── check_in_time (timestamp with timezone)
├── check_out_time (timestamp with timezone)
├── duration (float)
├── created_at (timestamp)
└── updated_at (timestamp)

facilities
├── id (UUID, primary key)
├── name (text, required)
├── category (text: 'Arts & Crafts'|'Tech-Art')
├── type (text: 'consumable'|'lease')
├── description (text)
├── status (text: 'available'|'in_use'|'maintenance'|'unavailable')
├── created_at (timestamp)
└── updated_at (timestamp)

facility_usage
├── id (UUID, primary key)
├── visit_id (UUID, foreign key)
├── facility_name (text)
├── facility_type (text: 'consumable'|'lease')
├── usage_duration (float)
├── created_at (timestamp)
└── updated_at (timestamp)

feedback
├── id (UUID, primary key)
├── visit_id (UUID, foreign key)
├── rating (integer: 1-5)
├── comments (text)
├── created_at (timestamp)
└── updated_at (timestamp)
```

### 3. Data Flow

1. User Management
   - Registration with age validation (minimum 5 years)
   - Required guardian information
   - Optional photo URL

2. Check-in Process
   - Search user by name
   - Verify user is not already checked in
   - Record check-in time in PH timezone
   - Display in active visitors list

3. Check-out Process
   - Update visit record with check-out time
   - Calculate visit duration
   - Collect feedback and facility usage data
   - Show success message and animations

4. Activity Tracking
   - Categorized facilities (Arts & Crafts, Tech-Art)
   - Type classification (consumable, lease)
   - Usage tracking per visit

5. Reporting & Analytics
   - Date range filtering
   - Summary metrics
   - Interactive visualizations
   - Comprehensive CSV export
   - All times in Philippine timezone

## Security Considerations

1. Data Validation
   - Age restrictions (minimum 5 years)
   - Required guardian information
   - Valid facility categories and types
   - Rating range (1-5)

2. Time Handling
   - All timestamps in Philippine timezone
   - Proper timezone conversion for display
   - Duration calculations accounting for timezone

3. Database Security
   - Foreign key constraints
   - Cascading deletes for related records
   - Check constraints for enums
   - Automatic timestamp updates

## Development Guidelines

1. Code Organization
   - Modular function structure
   - Clear error handling
   - Consistent timezone handling
   - Proper data validation

2. User Interface
   - Clear success/error messages
   - Visual feedback (balloons)
   - Responsive layout
   - Real-time updates

3. Data Management
   - Efficient database queries
   - Proper join handling
   - Null value handling
   - Data type validation

4. Maintenance
   - Regular backups
   - Monitor active users
   - Track facility usage
   - Update facility status

## Future Enhancements
1. Offline mode capability
2. Mobile app integration
3. Advanced analytics dashboard
4. Automated reporting
5. Integration with other makerspace tools

## Maintenance
- Regular database backups
- Log rotation
- Performance monitoring
- Security updates
- User feedback collection

## Dependencies
- Python 3.8+
- Streamlit 1.31.0
- Supabase 2.3.0
- Pandas 2.2.0
- PyTZ 2024.1
- python-dotenv 1.0.0

This architecture document serves as a reference for maintaining consistency in development and future enhancements of the Vivita Check-in App.
