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
if 'feedback_success' not in st.session_state:
    st.session_state.feedback_success = False
if 'feedback_user_name' not in st.session_state:
    st.session_state.feedback_user_name = ""
if 'show_new_user_form' not in st.session_state:
    st.session_state.show_new_user_form = False

def load_active_visits():
    """Load currently active visits"""
    try:
        response = supabase.table('visits').select(
            'id, check_in_time, users!inner(first_name, last_name)'
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
    
    # Show success message if feedback was just submitted
    if st.session_state.feedback_success:
        st.success(f"Thank you {st.session_state.feedback_user_name} for your feedback! 🎉 Have a great day!")
        st.balloons()
        # Reset the success state
        st.session_state.feedback_success = False
        st.session_state.feedback_user_name = ""
    
    # Show feedback form if needed
    if st.session_state.show_feedback and st.session_state.checkout_visit_id:
        with st.form("feedback_form"):
            st.subheader("How was your experience today?")
            
            # Emoticon-based rating using radio buttons
            rating = st.radio(
                "Select your rating:",
                options=[1, 2, 3, 4, 5],
                format_func=lambda x: {
                    1: "😢 Very Bad",
                    2: "🙁 Not Nice",
                    3: "😐 Meh",
                    4: "🙂 Good",
                    5: "😊 Super Fun!"
                }[x],
                horizontal=True,
                index=4  # Default to highest rating
            )
            
            facilities_used = st.multiselect(
                "Facilities used",
                ["3D Printer", "Laser Cutter", "Robotics", "Tablet", "Desktop Computer", "Cricut", "Polymer Clay", "Heat Press", "Heat Shrink", "Button Pin", "Art Supplies", "Jewelry Making"]
            )
            
            comments = st.text_area("Additional comments (optional)")
            
            if st.form_submit_button("Submit Feedback", type="primary"):
                try:
                    # Record feedback
                    supabase.table("feedback").insert({
                        "visit_id": st.session_state.checkout_visit_id,
                        "rating": rating,
                        "comments": comments,
                        "created_at": datetime.now(pytz.UTC).isoformat()
                    }).execute()
                    
                    # Get facility types from facilities table
                    facilities_data = supabase.table("facilities").select("name, type").execute()
                    facility_types = {f['name']: f['type'] for f in facilities_data.data}
                    
                    # Record facility usage with correct facility type
                    for facility in facilities_used:
                        facility_type = facility_types.get(facility)
                        if facility_type:  # Only record if we have the facility type
                            supabase.table("facility_usage").insert({
                                "visit_id": st.session_state.checkout_visit_id,
                                "facility_name": facility,
                                "facility_type": facility_type,
                                "created_at": datetime.now(pytz.UTC).isoformat()
                            }).execute()
                    
                    # Set success state
                    st.session_state.feedback_success = True
                    # Reset feedback form state
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
                with st.expander(f"🧑‍💻 {visit['users']['first_name']} {visit['users']['last_name']}", expanded=True):
                    # Convert check-in time to PH timezone
                    check_in_time = datetime.fromisoformat(visit['check_in_time'])
                    ph_check_in_time = check_in_time.astimezone(PH_TIMEZONE)
                    st.write(f"Check-in time: {ph_check_in_time.strftime('%I:%M %p')}")
                    if st.button("Check Out", key=f"checkout_{visit['id']}", type="primary"):
                        if record_check_out(visit['id']):
                            user_name = f"{visit['users']['first_name']} {visit['users']['last_name']}"
                            st.success(f"✅ {user_name} checked out successfully!")
                            st.balloons()
                            st.session_state.show_feedback = True
                            st.session_state.checkout_visit_id = visit['id']
                            st.session_state.feedback_user_name = user_name
                            st.rerun()
        else:
            st.info("No active visitors at the moment")
    
    with col2:
        st.subheader("Check In")
        
        # Search form
        with st.form("search_form", clear_on_submit=False):
            search_query = st.text_input("🔍 Search by name", key="search_input")
            search_col1, search_col2 = st.columns([3, 1])
            with search_col1:
                search_submitted = st.form_submit_button("Search", use_container_width=True)
            with search_col2:
                new_user_button = st.form_submit_button("New User", use_container_width=True)
        
        # Clear search results if search query is empty
        if not search_query:
            if 'search_results' in st.session_state:
                del st.session_state.search_results
        
        # Handle form submission
        if new_user_button:
            st.session_state.show_new_user_form = True
            st.session_state.search_results = []
        elif search_submitted and search_query:
            try:
                # Case-insensitive search using ilike
                search_terms = search_query.strip().split()
                query_conditions = []
                
                for term in search_terms:
                    query_conditions.append(
                        f"first_name.ilike.%{term}%,"
                        f"last_name.ilike.%{term}%"
                    )
                
                response = supabase.table("users").select("*").or_(
                    ','.join(query_conditions)
                ).execute()
                
                st.session_state.search_results = response.data
            except Exception as e:
                st.error(f"Error searching users: {str(e)}")
                st.session_state.search_results = []
        
        # New user form
        if st.session_state.get('show_new_user_form', False):
            with st.form("new_user_form"):
                st.subheader("Create New User")
                
                first_name = st.text_input("First Name*")
                last_name = st.text_input("Last Name*")
                birthdate = st.date_input("Birthdate*", min_value=date(1900, 1, 1), max_value=date.today())
                school_organization = st.text_input("School/Organization*")
                emergency_contact = st.text_input("Emergency Contact*")
                
                submit_button = st.form_submit_button("Create User")
                
                if submit_button:
                    if not all([first_name, last_name, birthdate, school_organization, emergency_contact]):
                        st.error("Please fill in all required fields")
                    else:
                        try:
                            response = supabase.table("users").insert({
                                "first_name": first_name,
                                "last_name": last_name,
                                "birthdate": birthdate.isoformat(),
                                "school_organization": school_organization,
                                "emergency_contact": emergency_contact
                            }).execute()
                            
                            if response.data:
                                st.success("User created successfully!")
                                # Clear the form
                                st.session_state.show_new_user_form = False
                                # Show the new user in search results
                                st.session_state.search_results = response.data
                                st.experimental_rerun()
                        except Exception as e:
                            st.error(f"Error creating user: {str(e)}")
        
        # Display search results from session state
        if hasattr(st.session_state, 'search_results') and st.session_state.search_results:
            st.write("### Search Results")
            for user in st.session_state.search_results:
                # Convert birthdate string to date object
                birthdate = datetime.strptime(user['birthdate'], '%Y-%m-%d').date()
                age = calculate_age(birthdate)
                
                with st.expander(f"{user['first_name']} {user['last_name']} - Age: {age}", expanded=True):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"School/Organization: {user['school_organization']}")
                    with col2:
                        st.write(f"Emergency Contact: {user['emergency_contact']}")
                    
                    # Check if user is already checked in
                    active_visit = supabase.table('visits').select('*').eq('user_id', user['id']).is_('check_out_time', None).execute()
                    
                    if not active_visit.data:
                        check_in_button_key = f"checkin_{user['id']}"
                        if st.button("Check In", key=check_in_button_key, type="primary"):
                            if record_check_in(user['id']):
                                st.success(f"✅ {user['first_name']} {user['last_name']} checked in successfully!")
                                st.balloons()
                                # Clear search results and rerun
                                st.session_state.search_results = []
                                st.rerun()
                    else:
                        st.warning("⚠️ User is already checked in")
        elif search_submitted and search_query:
            st.info("No users found")

def user_management_page():
    st.header("👥 User Management")
    
    tab1, tab2 = st.tabs(["Register New User", "View/Edit Users"])
    
    with tab1:
        with st.form("new_user_form"):
            st.subheader("Register New User")
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name*")
                last_name = st.text_input("Last Name*")
                birthdate = st.date_input(
                    "Birthdate*",
                    min_value=date(1920, 1, 1),
                    max_value=date.today(),
                    value=date.today()
                )
            
            with col2:
                school_organization = st.text_input("School/Educational Institution/Organization*")
                emergency_contact = st.text_input("Emergency Contact Number")
                photo_url = st.text_input("Photo URL (optional)")
            
            # Calculate and display age
            age = calculate_age(birthdate)
            st.info(f"Age: {age} years old")
            
            if st.form_submit_button("Register User", type="primary"):
                if first_name and last_name and birthdate and school_organization:
                    # Validate minimum age
                    if age < 5:
                        st.error("User must be at least 5 years old")
                    else:
                        try:
                            response = supabase.table("users").insert({
                                "first_name": first_name,
                                "last_name": last_name,
                                "birthdate": birthdate.isoformat(),
                                "school_organization": school_organization,
                                "emergency_contact": emergency_contact,
                                "photo_url": photo_url,
                                "created_at": datetime.now(pytz.UTC).isoformat()
                            }).execute()
                            st.success("User registered successfully!")
                            st.balloons()
                            st.session_state.redirect_to = "Check-in/out"
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error registering user: {str(e)}")
                else:
                    st.error("Please fill in all required fields")
    
    with tab2:
        st.subheader("View/Edit Users")
        
        # Add search functionality
        search_col1, search_col2 = st.columns([3, 1])
        with search_col1:
            search_query = st.text_input("🔍 Search users by name")
        with search_col2:
            sort_by = st.selectbox("Sort by", ["Name (A-Z)", "Name (Z-A)", "Latest First", "Oldest First"])
        
        try:
            # Build the query
            query = supabase.table("users").select("*")
            if search_query:
                query = query.or_(f"first_name.ilike.%{search_query}%,last_name.ilike.%{search_query}%")
            
            # Apply sorting
            if sort_by == "Name (A-Z)":
                query = query.order('first_name', desc=False).order('last_name', desc=False)
            elif sort_by == "Name (Z-A)":
                query = query.order('first_name', desc=True).order('last_name', desc=True)
            elif sort_by == "Latest First":
                query = query.order('created_at', desc=True)
            else:  # Oldest First
                query = query.order('created_at', desc=False)
            
            response = query.execute()
            users = response.data
            
            if users:
                for user in users:
                    # Convert birthdate string to date object
                    birthdate = datetime.strptime(user['birthdate'], '%Y-%m-%d').date()
                    age = calculate_age(birthdate)
                    
                    with st.expander(f"{user['first_name']} {user['last_name']} - Age: {age}", expanded=False):
                        edit_col1, edit_col2 = st.columns(2)
                        
                        # Edit form
                        with edit_col1:
                            with st.form(f"edit_user_{user['id']}", clear_on_submit=False):
                                st.subheader("Edit User")
                                new_first_name = st.text_input("First Name", value=user['first_name'])
                                new_last_name = st.text_input("Last Name", value=user['last_name'])
                                new_birthdate = st.date_input(
                                    "Birthdate",
                                    value=birthdate,
                                    min_value=date(1920, 1, 1),
                                    max_value=date.today()
                                )
                                new_school = st.text_input("School/Organization", value=user['school_organization'])
                                new_emergency = st.text_input("Emergency Contact", value=user['emergency_contact'] or "")
                                new_photo = st.text_input("Photo URL", value=user['photo_url'] or "")
                                
                                if st.form_submit_button("Save Changes", type="primary"):
                                    new_age = calculate_age(new_birthdate)
                                    if new_age < 5:
                                        st.error("User must be at least 5 years old")
                                    else:
                                        try:
                                            supabase.table("users").update({
                                                "first_name": new_first_name,
                                                "last_name": new_last_name,
                                                "birthdate": new_birthdate.isoformat(),
                                                "school_organization": new_school,
                                                "emergency_contact": new_emergency,
                                                "photo_url": new_photo,
                                                "updated_at": datetime.now(pytz.UTC).isoformat()
                                            }).eq("id", user['id']).execute()
                                            st.success("User updated successfully!")
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error updating user: {str(e)}")
                        
                        # User info and delete button
                        with edit_col2:
                            st.markdown("### Current Information")
                            st.write(f"**School/Organization:** {user['school_organization']}")
                            st.write(f"**Emergency Contact:** {user['emergency_contact'] or 'Not provided'}")
                            st.write(f"**Registration Date:** {datetime.fromisoformat(user['created_at']).strftime('%Y-%m-%d')}")
                            
                            # Check if user has any visits
                            visits = supabase.table("visits").select("id").eq("user_id", user['id']).execute()
                            has_visits = len(visits.data) > 0
                            
                            # Delete section with warning
                            st.markdown("---")
                            st.markdown("### ⚠️ Danger Zone")
                            if has_visits:
                                st.warning("This user has visit records. Deleting will also remove all associated visits, feedback, and facility usage data.")
                            
                            # Two-step delete process using session state
                            if f"confirm_delete_{user['id']}" not in st.session_state:
                                st.session_state[f"confirm_delete_{user['id']}"] = False
                            
                            if not st.session_state[f"confirm_delete_{user['id']}"]:
                                if st.button("Delete User", key=f"delete_{user['id']}", type="primary"):
                                    st.session_state[f"confirm_delete_{user['id']}"] = True
                                    st.rerun()
                            else:
                                st.error("Are you sure? This action cannot be undone!")
                                col1, col2 = st.columns(2)
                                with col1:
                                    if st.button("Yes, Delete", key=f"confirm_{user['id']}", type="primary"):
                                        try:
                                            # The cascade delete will handle related records
                                            supabase.table("users").delete().eq("id", user['id']).execute()
                                            st.success("User and all related records deleted successfully!")
                                            st.session_state[f"confirm_delete_{user['id']}"] = False
                                            st.rerun()
                                        except Exception as e:
                                            st.error(f"Error deleting user: {str(e)}")
                                with col2:
                                    if st.button("Cancel", key=f"cancel_{user['id']}"):
                                        st.session_state[f"confirm_delete_{user['id']}"] = False
                                        st.rerun()
            else:
                st.info("No users found")
                
        except Exception as e:
            st.error(f"Error loading users: {str(e)}")

def admin_dashboard_page():
    st.header("🏢 Admin Dashboard")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=date.today() - timedelta(days=30),
            max_value=date.today()
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=date.today(),
            max_value=date.today()
        )
    
    try:
        # Convert dates to datetime with timezone for database query
        start_datetime = datetime.combine(start_date, datetime.min.time()).replace(tzinfo=PH_TIMEZONE)
        end_datetime = datetime.combine(end_date, datetime.max.time()).replace(tzinfo=PH_TIMEZONE)
        
        # Get visits within date range
        visits_response = supabase.rpc(
            'get_visit_records',
            {
                'start_date': start_datetime.isoformat(),
                'end_date': end_datetime.isoformat()
            }
        ).execute()
        
        if visits_response.data:
            # Process visit records
            visits_with_users = []
            for visit in visits_response.data:
                try:
                    # Convert times to PH timezone
                    check_in_time = datetime.fromisoformat(visit['check_in_time']).astimezone(PH_TIMEZONE)
                    check_out_time = datetime.fromisoformat(visit['check_out_time']).astimezone(PH_TIMEZONE) if visit.get('check_out_time') else None
                    
                    # Calculate age
                    birthdate = datetime.strptime(visit['birthdate'], '%Y-%m-%d').date()
                    age = calculate_age(birthdate)
                    
                    # Get feedback
                    feedback_response = supabase.table("feedback").select("*").eq("visit_id", visit["id"]).execute()
                    
                    # Get facility usage
                    facility_usage_response = supabase.table("facility_usage").select("*").eq("visit_id", visit["id"]).execute()
                    
                    record = {
                        'Date': check_in_time.strftime('%Y-%m-%d'),
                        'Name': f"{visit['first_name']} {visit['last_name']}",
                        'Age': age,
                        'School/Organization': visit['school_organization'],
                        'Emergency Contact': visit['emergency_contact'],
                        'Check-in Time': check_in_time.strftime('%I:%M %p'),
                        'Check-out Time': check_out_time.strftime('%I:%M %p') if check_out_time else 'Not checked out',
                        'Duration (hrs)': round(visit['duration'], 2) if visit.get('duration') else None,
                        'Facilities Used': ', '.join([f['facility_name'] for f in facility_usage_response.data]) if facility_usage_response.data else '',
                        'Facility Types': ', '.join(set([f['facility_type'] for f in facility_usage_response.data])) if facility_usage_response.data else '',
                        'Rating': feedback_response.data[0]['rating'] if feedback_response.data else None,
                        'Comments': feedback_response.data[0]['comments'] if feedback_response.data else ''
                    }
                    visits_with_users.append(record)
                except Exception as e:
                    st.error(f"Error processing visit {visit['id']}: {str(e)}")
                    continue
            
            if visits_with_users:
                # Display summary metrics
                total_visits = len(visits_with_users)
                active_visits = sum(1 for v in visits_with_users if v['Check-out Time'] == 'Not checked out')
                completed_visits = [v for v in visits_with_users if v['Duration (hrs)'] is not None]
                avg_duration = sum(v['Duration (hrs)'] for v in completed_visits) / len(completed_visits) if completed_visits else 0
                ratings = [v['Rating'] for v in visits_with_users if v['Rating'] is not None]
                avg_rating = sum(ratings) / len(ratings) if ratings else None
                
                st.markdown("### 📊 Summary Metrics")
                metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
                
                with metric_col1:
                    st.metric("Total Visits", total_visits)
                with metric_col2:
                    st.metric("Avg Duration", f"{avg_duration:.1f} hrs" if avg_duration else "N/A")
                with metric_col3:
                    st.metric("Avg Rating", f"{avg_rating:.1f}" if avg_rating else "N/A")
                with metric_col4:
                    st.metric("Active Visits", active_visits)
                
                # Display visit records
                st.markdown("### 📋 Visit Records")
                df = pd.DataFrame(visits_with_users)
                st.dataframe(
                    df,
                    column_config={
                        "Duration (hrs)": st.column_config.NumberColumn(
                            "Duration (hrs)",
                            help="Visit duration in hours",
                            format="%.2f"
                        ),
                        "Rating": st.column_config.NumberColumn(
                            "Rating",
                            help="Feedback rating (1-5)",
                            format="%d"
                        )
                    },
                    hide_index=True
                )
                
                # Download button for CSV
                if st.download_button(
                    "📥 Download Visit Data",
                    df.to_csv(index=False).encode('utf-8'),
                    "vivita_visits_data.csv",
                    "text/csv",
                    help="Download the visit data as a CSV file"
                ):
                    st.success("Data downloaded successfully!")
            else:
                st.info("No visit records to display")
        else:
            st.info("No visits found for the selected date range")
            
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")

def record_check_in(user_id):
    try:
        # Record check-in with Philippine time
        check_in_time = get_ph_time()
        
        # First check if user is already checked in
        existing_visit = supabase.table("visits").select("*").eq("user_id", user_id).is_("check_out_time", None).execute()
        if existing_visit.data:
            st.error("User is already checked in!")
            return False
        
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
    """Calculate age from birthdate, considering month and day"""
    today = date.today()
    age = today.year - birthdate.year
    # Subtract a year if birthday hasn't occurred this year
    if today.month < birthdate.month or (today.month == birthdate.month and today.day < birthdate.day):
        age -= 1
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
