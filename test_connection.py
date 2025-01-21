import streamlit as st
from supabase import create_client
import sys
import traceback

def test_supabase_connection():
    try:
        print("Supabase URL:", st.secrets["SUPABASE_URL"])
        print("Supabase Key length:", len(st.secrets["SUPABASE_KEY"]))
        
        # Initialize Supabase client
        supabase = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"]
        )
        
        print("✅ Initial connection successful!")
        
        # Test each table
        tables = ['users', 'visits', 'facility_usage', 'feedback', 'facilities']
        missing_tables = []
        
        for table in tables:
            try:
                response = supabase.table(table).select('*').limit(1).execute()
                print(f"✅ Table '{table}' exists and is accessible")
            except Exception as e:
                error_msg = str(e)
                if "relation" in error_msg and "does not exist" in error_msg:
                    missing_tables.append(table)
                    print(f"❌ Table '{table}' does not exist")
                else:
                    print(f"❌ Error accessing table '{table}': {error_msg}")
        
        if missing_tables:
            print("\nMissing tables that need to be created:")
            for table in missing_tables:
                print(f"- {table}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Connection failed!")
        print("Error details:")
        print(traceback.format_exc())
        return False

if __name__ == "__main__":
    print("Testing Supabase connection...")
    success = test_supabase_connection()
    sys.exit(0 if success else 1)
