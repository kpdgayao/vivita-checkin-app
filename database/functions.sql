-- Drop the existing function
DROP FUNCTION IF EXISTS get_visit_records(timestamp with time zone, timestamp with time zone);

-- Create a function to get visit records with all related data
CREATE OR REPLACE FUNCTION get_visit_records(start_date timestamp with time zone, end_date timestamp with time zone)
RETURNS TABLE (
    id uuid,
    user_id uuid,
    check_in_time timestamp with time zone,
    check_out_time timestamp with time zone,
    duration float,
    created_at timestamp with time zone,
    updated_at timestamp with time zone,
    first_name text,
    last_name text,
    birthdate date,
    school_organization text,
    emergency_contact text
) 
SECURITY DEFINER 
SET search_path = public
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        v.id,
        v.user_id,
        v.check_in_time,
        v.check_out_time,
        v.duration,
        v.created_at,
        v.updated_at,
        u.first_name,
        u.last_name,
        u.birthdate,
        u.school_organization,
        u.emergency_contact
    FROM visits v
    LEFT JOIN users u ON v.user_id = u.id
    WHERE v.check_in_time >= start_date
    AND v.check_in_time <= end_date
    ORDER BY v.check_in_time DESC;
END;
$$;
