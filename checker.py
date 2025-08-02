import requests
import csv
import json
from datetime import datetime

def fetch_canvas_action_log(canvas_url, access_token, course_id, quiz_id, quiz_submission_id):
    """
    Fetches action log events for a specific quiz submission from Canvas LMS API.

    Args:
        canvas_url (str): The base URL of your Canvas instance.
        access_token (str): Your Canvas API Personal Access Token.
        course_id (int/str): The ID of the course.
        quiz_id (int/str): The ID of the quiz.
        quiz_submission_id (int/str): The ID of the specific quiz submission attempt.

    Returns:
        list: A list of dictionaries, where each dictionary represents an event,
              or None if an error occurs.
    """
    # Corrected API endpoint for quiz submission events
    api_url = f"{canvas_url}/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{quiz_submission_id}/events"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    try:
        print(f"Attempting to fetch action log data for submission {quiz_submission_id} from: {api_url}")
        response = requests.get(api_url, headers=headers)
        response.raise_for_status() # Raise an exception for HTTP errors (4xx or 5xx)

        data = response.json()
        events = data.get('quiz_submission_events')
        if events is None:
            print(f"Warning: 'quiz_submission_events' key not found for submission {quiz_submission_id}.")
            print("This could mean the API call was successful but no events were returned,")
            print("or the response structure is different than expected.")
            print("Full API Response (for debugging):")
            print(json.dumps(data, indent=2))
        return events

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred for submission {quiz_submission_id}: {http_err}")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")
        print("Please check your Canvas URL, Access Token, Course ID, Quiz ID, and Submission ID.")
        print("Ensure the Access Token has sufficient permissions (e.g., to read quiz submissions).")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred for submission {quiz_submission_id}: {conn_err}")
        print("Please check your internet connection and Canvas URL.")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred for submission {quiz_submission_id}: {timeout_err}")
        print("The request took too long. Try again or check network conditions.")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred during the request for submission {quiz_submission_id}: {req_err}")
    except json.JSONDecodeError as json_err:
        print(f"Error decoding JSON response for submission {quiz_submission_id}: {json_err}")
        print(f"Response text: {response.text}")
        print("The API response was not valid JSON. This might indicate an error from the Canvas server.")
    except Exception as e:
        print(f"An unexpected error occurred for submission {quiz_submission_id}: {e}")
    return None

def fetch_quiz_submissions_for_user(canvas_url, access_token, course_id, quiz_id, user_id):
    """
    Fetches all quiz submissions for a specific quiz and user.

    Args:
        canvas_url (str): The base URL of your Canvas instance.
        access_token (str): Your Canvas API Personal Access Token.
        course_id (int/str): The ID of the course.
        quiz_id (int/str): The ID of the quiz.
        user_id (int/str): The ID of the student user.

    Returns:
        list: A list of quiz submission dictionaries.
    """
    api_url = f"{canvas_url}/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions"

    params = {
        'user_id': user_id,
        'per_page': 100 # Increase per_page to get more results per request
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    all_submissions = []
    page = 1
    while True:
        print(f"Fetching quiz submissions for user {user_id}, quiz {quiz_id}, page {page}...")
        params['page'] = page
        try:
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            submissions = data.get('quiz_submissions')
            if not submissions:
                break # No more submissions

            all_submissions.extend(submissions)

            # Check for pagination link in headers
            if 'Link' in response.headers:
                next_page_link = None
                links = response.headers['Link'].split(',')
                for link in links:
                    if 'rel="next"' in link:
                        # Extract the URL for the next page
                        next_page_link = link[link.find('<')+1:link.find('>')]
                        break
                if next_page_link:
                    page += 1
                else:
                    break # No more pages
            else:
                break # No Link header, assume single page or end of pagination

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error fetching submissions for user {user_id}: {http_err} - Response: {response.text}")
            return None
        except Exception as e:
            print(f"An error occurred fetching submissions for user {user_id}: {e}")
            return None
    return all_submissions

def fetch_course_enrollments(canvas_url, access_token, course_id):
    """
    Fetches all student enrollments for a given course, including user display names.

    Args:
        canvas_url (str): The base URL of your Canvas instance.
        access_token (str): Your Canvas API Personal Access Token.
        course_id (int/str): The ID of the course.

    Returns:
        list: A list of dictionaries, each containing student's 'id' and 'name' (display name).
    """
    api_url = f"{canvas_url}/api/v1/courses/{course_id}/enrollments"
    params = {
        'type[]': 'StudentEnrollment', # Only fetch student enrollments
        'per_page': 100, # Adjust as needed for your course size
        'include[]': 'user' # Include user object to get name details
    }
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    students_info = []
    page = 1
    while True:
        print(f"Fetching enrollments for course {course_id}, page {page}...")
        params['page'] = page
        try:
            response = requests.get(api_url, headers=headers, params=params)
            response.raise_for_status()
            enrollments = response.json()

            if not enrollments:
                break # No more enrollments

            for enrollment in enrollments:
                if enrollment.get('role') == 'StudentEnrollment' and 'user_id' in enrollment:
                    user_data = enrollment.get('user', {})
                    student_info = {
                        'id': enrollment['user_id'],
                        'name': user_data.get('name', 'N/A') # Get the full display name
                    }
                    students_info.append(student_info)

            if 'Link' in response.headers:
                next_page_link = None
                links = response.headers['Link'].split(',')
                for link in links:
                    if 'rel="next"' in link:
                        next_page_link = link[link.find('<')+1:link.find('>')]
                        break
                if next_page_link:
                    page += 1
                else:
                    break
            else:
                break

        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error fetching enrollments: {http_err} - Response: {response.text}")
            return None
        except Exception as e:
            print(f"An error occurred fetching enrollments: {e}")
            return None
    return students_info

def format_event_description(event):
    """
    Formats the event dictionary into a human-readable description similar to the user's example.
    """
    event_type = event.get('event_type')
    description = event.get('description', '')
    data = event.get('data', {})

    if event_type == 'session_started':
        return "Session started"
    elif event_type == 'Youtubeed':
        question_id = data.get('question_id', 'N/A')
        return f"Answered question:#{question_id}"
    elif event_type == 'window_blurred':
        return "Stopped viewing the Canvas quiz-taking page..."
    elif event_type == 'window_focused':
        return "Resumed."
    elif event_type == 'page_view':
        return f"Viewed page: {description or event.get('url', 'N/A')}"
    else:
        return f"{event_type.replace('_', ' ').capitalize()}: {description}" if description else event_type.replace('_', ' ').capitalize()


def skip_duplicates(events_list):
    """
    Removes duplicate events from a list. An event is considered a duplicate if it has
    the same submission_id, timestamp, action_description, and raw_event_type.

    Args:
        events_list (list): A list of consolidated event dictionaries.

    Returns:
        list: A new list with duplicate events removed.
    """
    unique_events = []
    seen = set()

    for event in events_list:
        # Create a tuple of key fields to act as a unique identifier
        event_key = (
            event.get('submission_id'),
            event.get('timestamp_hh_mm'),
            event.get('action_description'),
            event.get('raw_event_type')
        )
        if event_key not in seen:
            seen.add(event_key)
            unique_events.append(event)
    return unique_events


def save_all_events_to_single_csv(filename, all_consolidated_events):
    """
    Saves a list of consolidated event dictionaries to a single CSV file.

    Args:
        filename (str): The name of the CSV file to create.
        all_consolidated_events (list of dict): A list of dictionaries, where each dictionary
                                                represents an event with student and submission details.
    """
    if not all_consolidated_events:
        print(f"No consolidated events data to save to '{filename}'.")
        return

    # Define the header for the CSV, including student and submission info
    header = [
        "Student ID", "Student Name",
        "Submission ID", "Timestamp", "Action", "Raw Event Type",
        "Raw Description", "User Agent", "URL", "Full Event Data"
    ]

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            csv_writer = csv.writer(csvfile)
            csv_writer.writerow(header)

            for event_row in all_consolidated_events:
                csv_writer.writerow([
                    event_row.get('student_id', 'N/A'),
                    event_row.get('student_name', 'N/A'),
                    event_row.get('submission_id', 'N/A'),
                    event_row.get('timestamp_hh_mm', 'N/A'),
                    event_row.get('action_description', 'N/A'),
                    event_row.get('raw_event_type', 'N/A'),
                    event_row.get('raw_description', 'N/A'),
                    event_row.get('user_agent', 'N/A'),
                    event_row.get('url', 'N/A'),
                    event_row.get('full_event_json', 'N/A')
                ])
        print(f"All events successfully saved to '{filename}'")
    except IOError as e:
        print(f"Error saving data to file '{filename}': {e}")
    except Exception as e:
        print(f"An unexpected error occurred during CSV saving for '{filename}': {e}")

def generate_console_report(student_info, submission_id, events_data):
    """
    Prints a formatted action log report to the console for a specific submission.

    Args:
        student_info (dict): Dictionary containing student's 'id' and 'name' (display name).
        submission_id (int/str): The ID of the quiz submission.
        events_data (list of dict): A list of dictionaries, where each dictionary
                                    represents an event.
    """
    if not events_data:
        print(f"No events data to generate console report for {student_info.get('name')} (ID: {student_info.get('id')}), submission {submission_id}.")
        return

    print(f"\n--- Canvas Action Log Report for {student_info.get('name')} (ID: {student_info.get('id')}), Submission ID: {submission_id} ---")
    print("Action Log")
    for event in events_data:
        created_at_iso = event.get('created_at', '')
        timestamp_hh_mm = 'N/A'
        try:
            dt_object = datetime.fromisoformat(created_at_iso.replace('Z', '+00:00'))
            timestamp_hh_mm = dt_object.strftime("%H:%M")
        except ValueError:
            pass

        action_description = format_event_description(event)
        print(f"{timestamp_hh_mm} {action_description}")
    print("----------------------------")


# --- Configuration and Example Usage ---

# !!! IMPORTANT: Replace these placeholders with your actual Canvas details !!!
CANVAS_BASE_URL = "https://uc-bcf.instructure.com"
CANVAS_ACCESS_TOKEN = "16936~DvJ2JLZx4rkCWXXrmJTcYAMLncwAFBt97wAM9HMHMckfAfaa9t4R3BQcJZMurDkE"
# COURSE_ID and QUIZ_ID will now be prompted from the user

if __name__ == "__main__":
    print("Starting Canvas API script to fetch all student action logs for a quiz...")

    # --- User Input Prompts ---
    try:
        COURSE_ID = input("Please enter the Course ID: ")
        QUIZ_ID = input("Please enter the Quiz ID: ")
        CSV_FILENAME = input("Please enter the desired CSV filename (e.g., quiz_logs.csv): ")
        if not CSV_FILENAME.lower().endswith('.csv'):
            CSV_FILENAME += '.csv' # Ensure it has a .csv extension
    except Exception as e:
        print(f"Error getting user input: {e}")
        exit()
    # --- End User Input Prompts ---


    all_consolidated_events = [] # This list will hold all event rows for the single CSV

    # Step 1: Fetch all student IDs and names in the specified course
    all_students_info = fetch_course_enrollments(
        CANVAS_BASE_URL,
        CANVAS_ACCESS_TOKEN,
        COURSE_ID
    )

    if not all_students_info:
        print("Failed to retrieve any student information for the specified course. Exiting.")
    else:
        print(f"\nFound {len(all_students_info)} students in course {COURSE_ID}.")
        for student_info in all_students_info:
            student_id = student_info.get('id')
            student_name = student_info.get('name')

            print(f"\n===== Processing Student: {student_name} (ID: {student_id}) =====")
            
            # Step 2: For each student, fetch all their quiz submissions for the specified quiz
            all_student_submissions = fetch_quiz_submissions_for_user(
                CANVAS_BASE_URL,
                CANVAS_ACCESS_TOKEN,
                COURSE_ID,
                QUIZ_ID,
                student_id
            )

            # Only proceed if the student has actual submissions for this quiz
            if all_student_submissions:
                print(f"Found {len(all_student_submissions)} submissions for {student_name} on quiz {QUIZ_ID}.")
                for submission in all_student_submissions:
                    submission_id = submission.get('id')
                    if submission_id:
                        print(f"\n--- Processing Submission ID: {submission_id} for {student_name} ---")
                        # Step 3: Fetch action log for each submission
                        events = fetch_canvas_action_log(
                            CANVAS_BASE_URL,
                            CANVAS_ACCESS_TOKEN,
                            COURSE_ID,
                            QUIZ_ID,
                            submission_id
                        )

                        if events:
                            # Sort events by 'created_at' timestamp to ensure chronological order
                            events.sort(key=lambda x: x.get('created_at', ''))
                            
                            # Add student and submission info to each event and collect them
                            for event in events:
                                created_at_iso = event.get('created_at', '')
                                timestamp_hh_mm = 'N/A'
                                try:
                                    dt_object = datetime.fromisoformat(created_at_iso.replace('Z', '+00:00'))
                                    timestamp_hh_mm = dt_object.strftime("%H:%M")
                                except ValueError:
                                    pass

                                consolidated_row = {
                                    'student_id': student_id,
                                    'student_name': student_name,
                                    'submission_id': submission_id,
                                    'timestamp_hh_mm': timestamp_hh_mm,
                                    'action_description': format_event_description(event),
                                    'raw_event_type': event.get('event_type', 'N/A'),
                                    'raw_description': event.get('description', ''),
                                    'user_agent': event.get('user_agent', ''),
                                    'url': event.get('url', '')
                                    # 'full_event_json': json.dumps(event)
                                }
                                all_consolidated_events.append(consolidated_row)

                            # Generate console report for individual submission (optional, can be removed if only CSV is needed)
                            generate_console_report(student_info, submission_id, events)
                        else:
                            print(f"No events found or failed to retrieve events for {student_name}, submission {submission_id}.")
                    else:
                        print(f"Warning: Submission dictionary missing 'id' key for student {student_name}: {submission}")
            else:
                # This block is now explicitly for students who did NOT take the quiz (no submissions)
                print(f"Skipping student {student_name} (ID: {student_id}) as they have no submissions for quiz {QUIZ_ID}.")
        
        # Step 4: Remove duplicates and save all collected events to a single CSV file
        if all_consolidated_events:
            unique_events = skip_duplicates(all_consolidated_events)
            print(f"\nProcessing complete. Found {len(all_consolidated_events)} events total, with {len(unique_events)} unique events after de-duplication.")
            save_all_events_to_single_csv(CSV_FILENAME, unique_events)
        else:
            print(f"\nNo events collected for any student with submissions. No consolidated CSV file created (filename: {CSV_FILENAME}).")