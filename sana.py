def process_student_submissions(student_info, canvas_url, course_id, quiz_id):
    """
    Fetches all submissions for a student, then aggregates all events for each submission.
    Returns a list of dictionaries, where each dictionary represents a single submission
    and contains an aggregated event log string.
    """
    student_id, student_name = student_info['id'], student_info['name']
    all_submission_summaries = []
    submissions = fetch_quiz_submissions_for_user(session, canvas_url, course_id, quiz_id, student_id)
    
    for sub in submissions:
        submission_id = sub.get('id')
        if not submission_id:
            continue
        
        events = fetch_canvas_action_log(session, canvas_url, course_id, quiz_id, submission_id)
        events.sort(key=lambda e: e.get('created_at', ''))
        
        event_log_lines = []
        seen = set()

        for event in events:
            ts = event.get('created_at', '')
            try:
                time = datetime.fromisoformat(ts.replace('Z', '+00:00')).strftime("%H:%M")
            except:
                time = 'N/A'
            
            action_desc = format_event_description(event)
            raw_event_type = event.get('event_type', 'N/A')
            user_agent = event.get('user_agent', '')
            url = event.get('url', '')

            # Use a tuple key to detect duplicates
            event_key = (time, action_desc, raw_event_type)
            if event_key in seen:
                continue
            seen.add(event_key)

            event_log_lines.append(
                f"[{time}] - Action: {action_desc} | Type: {raw_event_type} | User Agent: {user_agent} | URL: {url}"
            )

        full_event_log = "\n".join(event_log_lines)
        
        all_submission_summaries.append({
            'student_id': student_id,
            'student_name': student_name,
            'submission_id': submission_id,
            'events_log': full_event_log
        })
    
    return all_submission_summaries
