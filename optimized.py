import requests
import csv
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

#---Reusable session for performance ---
session = requests.Session()


def fetch_canvas_action_log(session, canvas_url, course_id, quiz_id, quiz_submission_id):
    api_url = f"{canvas_url}/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions/{quiz_submission_id}/events"
    try:
        response = session.get(api_url)
        response.raise_for_status()
        return response.json().get('quiz_submission_events', [])
    except Exception as e:
        print(f"Error fetching events for submission {quiz_submission_id}: {e}")
        return []


def fetch_quiz_submissions_for_user(session, canvas_url, course_id, quiz_id, user_id):
    api_url = f"{canvas_url}/api/v1/courses/{course_id}/quizzes/{quiz_id}/submissions"
    params = {'user_id': user_id, 'per_page': 100}
    try:
        response = session.get(api_url, params=params)
        response.raise_for_status()
        return response.json().get('quiz_submissions', [])
    except Exception as e:
        print(f"Error fetching submissions for user {user_id}: {e}")
        return []


def fetch_course_enrollments(session, canvas_url, course_id):
    api_url = f"{canvas_url}/api/v1/courses/{course_id}/enrollments"
    params = {'type[]': 'StudentEnrollment', 'per_page': 100, 'include[]': 'user'}
    students_info = []
    try:
        response = session.get(api_url, params=params)
        response.raise_for_status()
        for enrollment in response.json():
            if enrollment.get('role') == 'StudentEnrollment':
                user = enrollment.get('user', {})
                students_info.append({'id': enrollment['user_id'], 'name': user.get('name', 'N/A')})
    except Exception as e:
        print(f"Error fetching enrollments: {e}")
    return students_info


def format_event_description(event):
    event_type = event.get('event_type')
    desc = event.get('description', '')
    data = event.get('data', {})
    if event_type == 'session_started':
        return "Session started"
    elif event_type == 'question_answered':
        return f"Answered question:#{data.get('question_id', 'N/A')}"
    elif event_type == 'window_blurred':
        return "Stopped viewing the Canvas quiz-taking page..."
    elif event_type == 'window_focused':
        return "Resumed."
    elif event_type == 'page_view':
        return f"Viewed page: {desc or event.get('url', 'N/A')}"
    return event_type.replace('_', ' ').capitalize() + (f": {desc}" if desc else '')


def process_student_submissions(student_info):
    student_id, student_name = student_info['id'], student_info['name']
    results = []
    submissions = fetch_quiz_submissions_for_user(session, CANVAS_BASE_URL, COURSE_ID, QUIZ_ID, student_id)
    for sub in submissions:
        submission_id = sub.get('id')
        if not submission_id:
            continue
        events = fetch_canvas_action_log(session, CANVAS_BASE_URL, COURSE_ID, QUIZ_ID, submission_id)
        events.sort(key=lambda e: e.get('created_at', ''))
        for event in events:
            ts = event.get('created_at', '')
            try:
                time = datetime.fromisoformat(ts.replace('Z', '+00:00')).strftime("%H:%M")
            except:
                time = 'N/A'
            results.append({
                'student_id': student_id,
                'student_name': student_name,
                'submission_id': submission_id,
                'timestamp_hh_mm': time,
                'action_description': format_event_description(event),
                'raw_event_type': event.get('event_type', 'N/A'),
                'raw_description': event.get('description', ''),
                'user_agent': event.get('user_agent', ''),
                'url': event.get('url', ''),
                'full_event_json': json.dumps(event, separators=(',', ':'))
            })
    return results


def save_all_events_to_single_csv(filename, events):
    header = ["Student ID", "Student Name", "Submission ID", "Timestamp", "Action", "Raw Event Type", "Raw Description", "User Agent", "URL"] #"Full Event Data"]
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=header)
            writer.writeheader()
            for e in events:
                writer.writerow({
                    "Student ID": e['student_id'],
                    "Student Name": e['student_name'],
                    "Submission ID": e['submission_id'],
                    "Timestamp": e['timestamp_hh_mm'],
                    "Action": e['action_description'],
                    "Raw Event Type": e['raw_event_type'],
                    "Raw Description": e['raw_description'],
                    "User Agent": e['user_agent'],
                    "URL": e['url']
                    
                })
        print(f"Saved all events to '{filename}'")
    except Exception as e:
        print(f"Error saving CSV: {e}")


if __name__ == "__main__":
    CANVAS_BASE_URL = "https://uc-bcf.instructure.com"
    CANVAS_ACCESS_TOKEN = "16936~DvJ2JLZx4rkCWXXrmJTcYAMLncwAFBt97wAM9HMHMckfAfaa9t4R3BQcJZMurDkE"

    #Attach token to session
    session.headers.update({"Authorization": f"Bearer {CANVAS_ACCESS_TOKEN}", "Content-Type": "application/json"})

    try:
        COURSE_ID = input("Enter Course ID: ")
        QUIZ_ID = input("Enter Quiz ID: ")
        CSV_FILENAME = input("Enter CSV filename (e.g., logs.csv): ")
        if not CSV_FILENAME.lower().endswith('.csv'):
            CSV_FILENAME += '.csv'
    except Exception as e:
        print(f"Input error: {e}")
        exit()

    students = fetch_course_enrollments(session, CANVAS_BASE_URL, COURSE_ID)
    print(f"Found {len(students)} students.")

    all_events = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_student_submissions, s) for s in students]
        for f in as_completed(futures):
            all_events.extend(f.result())

    if all_events:
        save_all_events_to_single_csv(CSV_FILENAME, all_events)
    else:
        print("No events collected.")
