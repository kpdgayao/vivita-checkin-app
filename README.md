# Vivita Check-in App

A Streamlit-based web application for managing makerspace attendance and facility usage at Vivita Philippines.

## Features

- ✨ User Registration and Management
  - Register new users with guardian information
  - Age verification (minimum 5 years)
  - User search functionality

- 📝 Check-in/out System
  - Quick user search and check-in
  - Facility usage tracking
  - Feedback collection at check-out
  - Duration calculation

- 📊 Admin Dashboard
  - Visit statistics and metrics
  - Daily visit charts
  - Facility usage analytics
  - Data export to CSV

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: Supabase (PostgreSQL)
- **Language**: Python 3.8+

## Installation

1. Clone the repository:
```bash
git clone https://github.com/kpdgayao/vivita-checkin-app.git
cd vivita-checkin-app
```

2. Create a virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set up your Supabase credentials:
   - Create a `.streamlit/secrets.toml` file
   - Add your Supabase credentials:
     ```toml
     [supabase]
     url = "YOUR_SUPABASE_URL"
     key = "YOUR_SUPABASE_KEY"
     ```

4. Initialize the database:
   - Run the SQL scripts in the `database` folder in order:
     1. `init.sql`
     2. `migrate_to_birthdate.sql` (if needed)

5. Run the application:
```bash
streamlit run app.py
```

## Project Structure

```
vivita-checkin-app/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── .streamlit/        # Streamlit configuration
│   └── secrets.toml   # (gitignored) Credentials
├── database/          # Database scripts
│   ├── init.sql      # Initial schema
│   └── migrate_to_birthdate.sql
└── README.md         # This file
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see LICENSE file for details
