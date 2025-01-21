import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import pytz
from supabase import create_client, Client
import plotly.express as px
import plotly.graph_objects as go

# Initialize connection to Supabase
supabase: Client = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

# Set Philippine timezone
PH_TIMEZONE = pytz.timezone('Asia/Manila')

def get_ph_time():
    """Get current time in Philippine timezone"""
    return datetime.now(PH_TIMEZONE)

def format_ph_time(dt):
    """Format datetime in Philippine format"""
    return dt.strftime("%B %d, %Y %I:%M %p")

# Page configuration
st.set_page_config(
    page_title="Vivita Makerspace Check-in",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #FF4B4B;
        color: white;
    }
    .success-button>button {
        background-color: #00CC66;
    }
    .stAlert {
        padding: 1rem;
        border-radius: 5px;
    }
    div[data-testid="stExpander"] {
        border: none;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
        padding: 1rem;
        border-radius: 5px;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize session state
if 'show_feedback' not in st.session_state:
    st.session_state.show_feedback = None
if 'checkout_visit_id' not in st.session_state:
    st.session_state.checkout_visit_id = None

def load_active_visits():
    """Load currently active visits"""
    try:
        response = supabase.table('visits').select(
            'id, check_in_time, users!inner(*)'
        ).is_('check_out_time', None).execute()
        return response.data
    except Exception as e:
        st.error(f"Error loading active visits: {str(e)}")
        return []

def check_in_out_page():
    st.header("📍 Check-in/out")
    
    # Display current date and time
    current_time = get_ph_time()
    st.markdown(f"### 📅 {format_ph_time(current_time)}")
    st.markdown("---")
    
    # Show feedback form if needed
    if st.session_state.show_feedback and st.session_state.checkout_visit_id:
        with st.form("feedback_form"):
            st.subheader("Quick Feedback")
            rating = st.slider("Rate your experience", 1, 5, 5)
            comments = st.text_area("Comments (optional)")
            facilities_used = st.multiselect(
                "Facilities used",
                ["3D Printer", "Laser Cutter", "Robotics", "Tablet", "Dekstop Computer", "Cricut", "Polymer Clay", "Heat Press", "Heat Shrink", "Button Pin", "Art Supplies", "Jewelry Making"]
            )
            
            if st.form_submit_button("Submit Feedback"):
                try:
                    # Record feedback
                    supabase.table("feedback").insert({
                        "visit_id": st.session_state.checkout_visit_id,
                        "rating": rating,
                        "comments": comments,
                        "created_at": datetime.now(pytz.UTC).isoformat()
                    }).execute()
                    
                    # Record facility usage
                    for facility in facilities_used:
                        supabase.table("facility_usage").insert({
                            "visit_id": st.session_state.checkout_visit_id,
                            "facility_name": facility,
                            "created_at": datetime.now(pytz.UTC).isoformat()
                        }).execute()
                    
                    st.success("Thank you for your feedback!")
                    # Reset the session state
                    st.session_state.show_feedback = False
                    st.session_state.checkout_visit_id = None
                    st.rerun()
                except Exception as e:
                    st.error(f"Error saving feedback: {str(e)}")
    
    # Create two columns for active visits and check-in
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.subheader("Active Visitors")
        active_visits = load_active_visits()
        
        if active_visits:
            for visit in active_visits:
                with st.expander(f"🧑‍💻 {visit['users']['name']}", expanded=True):
                    # Convert check-in time to PH timezone
                    check_in_time = datetime.fromisoformat(visit['check_in_time'])
                    ph_check_in_time = check_in_time.astimezone(PH_TIMEZONE)
                    st.write(f"Check-in time: {ph_check_in_time.strftime('%I:%M %p')}")
                    if st.button("Check Out", key=f"checkout_{visit['id']}", type="primary"):
                        if record_check_out(visit['id']):
                            st.success(f"✅ {visit['users']['name']} checked out successfully!")
                            st.balloons()
                            st.session_state.show_feedback = True
                            st.session_state.checkout_visit_id = visit['id']
                            st.rerun()
        else:
            st.info("No active visitors at the moment")
    
    with col2:
        st.subheader("Check In")
        search_query = st.text_input("🔍 Search by name")
        
        if search_query:
            try:
                response = supabase.table("users").select("*").ilike("name", f"%{search_query}%").execute()
                if response.data:
                    for user in response.data:
                        # Convert birthdate string to date object
                        birthdate = datetime.strptime(user['birthdate'], '%Y-%m-%d').date()
                        age = calculate_age(birthdate)
                        
                        with st.expander(f"{user['name']} - Age: {age}", expanded=True):
                            col1, col2 = st.columns(2)
                            with col1:
                                st.write(f"Guardian: {user['guardian_name']}")
                                st.write(f"Contact: {user['guardian_contact']}")
                            with col2:
                                st.write(f"Emergency Contact: {user['emergency_contact']}")
                                
                                # Check if user is already checked in
                                active_visit = supabase.table('visits').select('*').eq('user_id', user['id']).is_('check_out_time', None).execute()
                                if not active_visit.data:
                                    if st.button("Check In", key=f"checkin_{user['id']}", type="primary"):
                                        if record_check_in(user['id']):
                                            st.success(f"✅ {user['name']} checked in successfully!")
                                            st.balloons()
                                            st.rerun()
                                else:
                                    st.warning("⚠️ User is already checked in")
                else:
                    st.info("No users found")
            except Exception as e:
                st.error(f"Error searching users: {str(e)}")

def user_management_page():
    st.header("👥 User Management")
    
    tab1, tab2 = st.tabs(["Register New User", "View/Edit Users"])
    
    with tab1:
        with st.form("new_user_form"):
            st.subheader("Register New User")
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name*")
                birthdate = st.date_input(
                    "Birthdate*",
                    min_value=date(1920, 1, 1),
                    max_value=date.today(),
                    value=date.today()
                )
                photo_url = st.text_input("Photo URL (optional)")
            
            with col2:
                guardian_name = st.text_input("Guardian Name*")
                guardian_contact = st.text_input("Guardian Contact*")
                emergency_contact = st.text_input("Emergency Contact")
            
            # Calculate and display age
            age = calculate_age(birthdate)
            st.info(f"Age: {age} years old")
            
            if st.form_submit_button("Register User", type="primary"):
                if name and birthdate and guardian_name and guardian_contact:
                    # Validate minimum age
                    if age < 5:
                        st.error("User must be at least 5 years old")
                    else:
                        try:
                            response = supabase.table("users").insert({
                                "name": name,
                                "birthdate": birthdate.isoformat(),
                                "guardian_name": guardian_name,
                                "guardian_contact": guardian_contact,
                                "emergency_contact": emergency_contact,
                                "photo_url": photo_url,
                                "created_at": datetime.now(pytz.UTC).isoformat()
                            }).execute()
                            st.success("User registered successfully!")
                            st.balloons()
                            st.session_state.redirect_to = "Check-in/out"
                            st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error registering user: {str(e)}")
                else:
                    st.error("Please fill in all required fields")
    
    with tab2:
        st.subheader("Registered Users")
        try:
            response = supabase.table("users").select("*").execute()
            if response.data:
                df = pd.DataFrame(response.data)
                df['birthdate'] = pd.to_datetime(df['birthdate']).dt.date
                df['age'] = df['birthdate'].apply(calculate_age)
                df['created_at'] = pd.to_datetime(df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                
                # Reorder and rename columns for display
                display_df = df[[
                    'name', 'birthdate', 'age', 'guardian_name', 
                    'guardian_contact', 'emergency_contact', 'created_at'
                ]].rename(columns={
                    'name': 'Name',
                    'birthdate': 'Birthdate',
                    'age': 'Age',
                    'guardian_name': 'Guardian Name',
                    'guardian_contact': 'Guardian Contact',
                    'emergency_contact': 'Emergency Contact',
                    'created_at': 'Registration Date'
                })
                
                st.dataframe(
                    display_df,
                    column_config={
                        "Age": st.column_config.NumberColumn(
                            "Age",
                            help="User's current age",
                            format="%d years"
                        ),
                        "Birthdate": st.column_config.DateColumn(
                            "Birthdate",
                            help="User's date of birth"
                        )
                    }
                )
            else:
                st.info("No users registered yet")
        except Exception as e:
            st.error(f"Error loading users: {str(e)}")

def admin_dashboard_page():
    st.header("📊 Admin Dashboard")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Start Date", value=date.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("End Date", value=date.today())
    
    if start_date and end_date:
        try:
            # Fetch visit data with user details and feedback
            response = supabase.table("visits")\
                .select(
                    """
                    *,
                    users!visits_user_id_fkey (
                        name,
                        birthdate,
                        guardian_name,
                        guardian_contact
                    ),
                    feedback!visits_id_fkey (
                        rating,
                        comments
                    ),
                    facility_usage!visits_id_fkey (
                        facility_name,
                        created_at
                    )
                    """
                )\
                .gte("check_in_time", start_date.isoformat())\
                .lte("check_in_time", (end_date + timedelta(days=1)).isoformat())\
                .execute()

            if response.data:
                # Process the data
                visits_data = []
                for visit in response.data:
                    try:
                        # Get user info
                        user_data = visit.get('users', [{}])[0] if visit.get('users') else None
                        
                        # Handle missing user data
                        if not user_data:
                            visits_data.append({
                                'Date': datetime.fromisoformat(visit['check_in_time']).astimezone(PH_TIMEZONE).strftime('%Y-%m-%d'),
                                'Name': f'[Deleted User {visit["user_id"]}]',
                                'Age': None,
                                'Guardian': 'N/A',
                                'Guardian Contact': 'N/A',
                                'Check-in Time': datetime.fromisoformat(visit['check_in_time']).astimezone(PH_TIMEZONE).strftime('%I:%M %p'),
                                'Check-out Time': datetime.fromisoformat(visit['check_out_time']).astimezone(PH_TIMEZONE).strftime('%I:%M %p') if visit.get('check_out_time') else 'Not checked out',
                                'Duration (hours)': round(visit['duration'], 2) if visit.get('duration') else None,
                                'Facilities Used': ', '.join([f['facility_name'] for f in visit.get('facility_usage', [])]) if visit.get('facility_usage') else '',
                                'Feedback Rating': None if not visit.get('feedback') or not visit.get('feedback')[0].get('rating') else visit['feedback'][0]['rating'],
                                'Feedback Comments': visit.get('feedback', [{}])[0].get('comments', '')
                            })
                            continue
                            
                        birthdate = datetime.strptime(user_data['birthdate'], '%Y-%m-%d').date()
                        age = calculate_age(birthdate)
                        
                        # Get feedback info (might not exist)
                        feedback_data = visit.get('feedback', [])
                        feedback = feedback_data[0] if feedback_data else {}
                        
                        # Get facilities used (might not exist)
                        facilities = visit.get('facility_usage', [])
                        facilities_list = ', '.join([f['facility_name'] for f in facilities]) if facilities else ''
                        
                        # Convert times to PH timezone
                        check_in_time = datetime.fromisoformat(visit['check_in_time']).astimezone(PH_TIMEZONE)
                        check_out_time = datetime.fromisoformat(visit['check_out_time']).astimezone(PH_TIMEZONE) if visit.get('check_out_time') else None
                        
                        visits_data.append({
                            'Date': check_in_time.strftime('%Y-%m-%d'),
                            'Name': user_data['name'],
                            'Age': age,
                            'Guardian': user_data.get('guardian_name', ''),
                            'Guardian Contact': user_data.get('guardian_contact', ''),
                            'Check-in Time': check_in_time.strftime('%I:%M %p'),
                            'Check-out Time': check_out_time.strftime('%I:%M %p') if check_out_time else 'Not checked out',
                            'Duration (hours)': round(visit['duration'], 2) if visit.get('duration') else None,
                            'Facilities Used': facilities_list,
                            'Feedback Rating': feedback.get('rating'),
                            'Feedback Comments': feedback.get('comments', '')
                        })
                    except Exception as e:
                        st.warning(f"Error processing visit {visit.get('id')}: {str(e)}")
                        continue
                
                if visits_data:
                    # Create DataFrame
                    df = pd.DataFrame(visits_data)
                    
                    # Display summary metrics
                    st.subheader("📈 Summary Metrics")
                    metrics_col1, metrics_col2, metrics_col3, metrics_col4 = st.columns(4)
                    
                    with metrics_col1:
                        st.metric("Total Visits", len(df))
                    with metrics_col2:
                        avg_duration = df['Duration (hours)'].mean()
                        st.metric("Avg Duration", f"{avg_duration:.1f} hrs" if pd.notnull(avg_duration) else "N/A")
                    with metrics_col3:
                        # Convert rating to numeric, ignoring non-numeric values
                        df['Feedback Rating'] = pd.to_numeric(df['Feedback Rating'], errors='coerce')
                        avg_rating = df['Feedback Rating'].mean()
                        st.metric("Avg Rating", f"{avg_rating:.1f}/5" if pd.notnull(avg_rating) else "N/A")
                    with metrics_col4:
                        active_visits = df['Check-out Time'].eq('Not checked out').sum()
                        st.metric("Active Visits", active_visits)
                    
                    # Display visit data
                    st.subheader("📋 Visit Records")
                    st.dataframe(
                        df,
                        column_config={
                            "Duration (hours)": st.column_config.NumberColumn(
                                "Duration (hours)",
                                help="Visit duration in hours",
                                format="%.2f"
                            ),
                            "Feedback Rating": st.column_config.NumberColumn(
                                "Rating",
                                help="Feedback rating out of 5",
                                format="%.1f"
                            )
                        }
                    )
                    
                    # Download button
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download Visit Data",
                        data=csv,
                        file_name=f'visits_{start_date}_{end_date}.csv',
                        mime='text/csv',
                    )
                    
                    # Visualizations
                    st.subheader("📊 Visualizations")
                    
                    # Visits over time
                    daily_visits = df['Date'].value_counts().sort_index()
                    fig_visits = px.line(
                        x=daily_visits.index, 
                        y=daily_visits.values,
                        title='Daily Visits',
                        labels={'x': 'Date', 'y': 'Number of Visits'}
                    )
                    st.plotly_chart(fig_visits)
                    
                    # Facility usage
                    if not df['Facilities Used'].empty and df['Facilities Used'].str.len().sum() > 0:
                        all_facilities = [facility.strip() for facilities in df['Facilities Used'].dropna() for facility in facilities.split(',') if facility.strip()]
                        if all_facilities:
                            facility_counts = pd.Series(all_facilities).value_counts()
                            fig_facilities = px.bar(
                                x=facility_counts.index,
                                y=facility_counts.values,
                                title='Facility Usage',
                                labels={'x': 'Facility', 'y': 'Times Used'}
                            )
                            st.plotly_chart(fig_facilities)
                else:
                    st.info("No valid visit data to display")
            else:
                st.info("No visit data found for the selected date range")
                
        except Exception as e:
            st.error(f"Error loading dashboard data: {str(e)}")

def record_check_in(user_id):
    try:
        # Record check-in with Philippine time
        check_in_time = get_ph_time()
        
        # Insert visit record
        supabase.table("visits").insert({
            "user_id": user_id,
            "check_in_time": check_in_time.isoformat(),
            "created_at": check_in_time.isoformat()
        }).execute()
        
        return True
    except Exception as e:
        st.error(f"Error recording check-in: {str(e)}")
        return False

def record_check_out(visit_id):
    try:
        # Find the visit
        visit = supabase.table("visits").select("*").eq("id", visit_id).single().execute()
        
        if visit.data:
            check_in_time = datetime.fromisoformat(visit.data['check_in_time'])
            check_out_time = get_ph_time()
            
            # Update visit record
            supabase.table("visits").update({
                "check_out_time": check_out_time.isoformat(),
                "duration": (check_out_time.astimezone(pytz.UTC) - check_in_time.astimezone(pytz.UTC)).total_seconds() / 3600  # Duration in hours
            }).eq("id", visit_id).execute()
            
            return True
            
    except Exception as e:
        st.error(f"Error recording check-out: {str(e)}")
        return False

def calculate_age(birthdate):
    today = date.today()
    age = today.year - birthdate.year - ((today.month, today.day) < (birthdate.month, birthdate.day))
    return age

def main():
    # Sidebar navigation
    with st.sidebar:
        st.title("🏢 Vivita Makerspace")
        st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRMnphwMpP9pFqKNENko8lahwFk5Uif84vELA&s", 
                use_column_width=True,
                caption="Vivita Makerspace")
        
        selected = st.radio(
            "Navigation",
            ["Check-in/out", "User Management", "Admin Dashboard"],
            key="navigation"
        )
        
        st.markdown("---")
        st.markdown("### Quick Stats")
        try:
            active_count = len(load_active_visits())
            st.metric("Active Users", active_count)
        except:
            st.error("Could not load stats")
    
    # Store the selected page in session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = selected
    
    # Check if we need to redirect
    if 'redirect_to' in st.session_state:
        selected = st.session_state.redirect_to
        del st.session_state.redirect_to
    
    # Update current page
    st.session_state.current_page = selected

    # Main content
    if selected == "Check-in/out":
        check_in_out_page()
    elif selected == "User Management":
        user_management_page()
    elif selected == "Admin Dashboard":
        admin_dashboard_page()

if __name__ == "__main__":
    main()
