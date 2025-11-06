from flask import Blueprint, render_template, request, session, current_app, redirect, url_for
from functools import wraps

student_advisor_bp = Blueprint('student_advisor', __name__, template_folder='templates')

# --- Utility Decorator ---
def student_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'student':
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- Routes ---

@student_advisor_bp.route('/student/portal')
@student_required
def portal():
    data_service = current_app.data_service
    student_id = session['user_id']
    student_data = data_service.get_student_by_id(student_id)

    # Check if psychometric score is available
    if student_data and 'psychometric_score' in student_data and pd.notna(student_data['psychometric_score']):
        analysis_complete = True
    else:
        analysis_complete = False

    # Get student's current marks for the dashboard
    marks = {
        'Math': student_data.get('math_marks', 'N/A'),
        'Science': student_data.get('science_marks', 'N/A'),
        'English': student_data.get('english_marks', 'N/A'),
        'Psychometric Score': student_data.get('psychometric_score', 'N/A')
    }

    return render_template('student_portal.html',
                           student_name=student_data['name'],
                           marks=marks,
                           analysis_complete=analysis_complete)

@student_advisor_bp.route('/student/ai-advisor', methods=['GET', 'POST'])
@student_required
def ai_advisor():
    data_service = current_app.data_service
    llm_advisor = current_app.llm_advisor
    student_id = session['user_id']
    student_data = data_service.get_student_by_id(student_id)

    query_response = None

    if request.method == 'POST':
        user_query = request.form.get('query')
        if user_query and llm_advisor.client:
            # Generate a grounded response using student's profile data

            # 1. Format profile for LLM context
            profile_context = f"Student Profile:\nName: {student_data.get('name')}\nID: {student_id}\nMath: {student_data.get('math_marks', 'N/A')}\nScience: {student_data.get('science_marks', 'N/A')}\nEnglish: {student_data.get('english_marks', 'N/A')}\nPsychometric Score: {student_data.get('psychometric_score', 'N/A')}"

            # 2. Build the full prompt
            full_prompt = f"Given the following student context: {profile_context}\n\nStudent Query: {user_query}\n\nProvide a concise, helpful, and encouraging advisory response. You should act as a supportive AI college advisor."

            try:
                # Assuming llm_advisor.generate_content is available and handles the API call
                response_data = llm_advisor.generate_content(
                    prompt=full_prompt,
                    use_search_grounding=True,
                    system_instruction="You are a supportive and professional AI College and Career Advisor. Your response must be short, friendly, and directly address the student's query based on their profile and general knowledge."
                )
                query_response = response_data['text']
            except Exception as e:
                query_response = f"Sorry, the AI Advisor is currently unavailable. Error: {e}"

    return render_template('student_ai_advisor.html',
                           query_response=query_response)

@student_advisor_bp.route('/student/career-path')
@student_required
def career_path():
    data_service = current_app.data_service
    student_id = session['user_id']
    student_data = data_service.get_student_by_id(student_id)

    # --- NEW CHECK: Verification Status ---
    is_verified = student_data.get('is_verified', False)

    if not is_verified:
        # Show the "Awaiting Verification" screen (which matches the user's screenshot)
        return render_template('career_path_awaiting_verification.html',
                               student_name=student_data.get('name', 'Student'))

    # If verified, proceed to generate the actual report

    llm_advisor = current_app.llm_advisor
    career_report = "Career Path Report will be generated here."

    # Mock generation logic (replace with actual LLM call later if necessary)
    if llm_advisor.client:
        # Placeholder for LLM generated report based on student_data

        profile_context = f"Student Profile:\nName: {student_data.get('name')}\nID: {student_id}\nMath: {student_data.get('math_marks', 'N/A')}\nScience: {student_data.get('science_marks', 'N/A')}\nEnglish: {student_data.get('english_marks', 'N/A')}\nPsychometric Score: {student_data.get('psychometric_score', 'N/A')}"

        report_prompt = (
            f"Given the following student data, generate a comprehensive Career Path Report. "
            f"Focus on 3-4 potential career tracks, linking them to their strongest marks (Math, Science, English) "
            f"and psychometric score. The tone should be formal, encouraging, and detailed. "
            f"Use clear headings. Data: {profile_context}"
        )
        try:
            # Generate the detailed report (no search grounding needed for personal analysis)
            response_data = llm_advisor.generate_content(
                prompt=report_prompt,
                use_search_grounding=False,
                system_instruction="You are a professional career counselor. Generate a detailed, multi-paragraph career report in Markdown format. Do not include a conversational intro or closing."
            )
            career_report = response_data['text']
        except Exception as e:
            career_report = f"Could not generate career report due to an AI error. Please try again later. Error: {e}"


    return render_template('student_career_path.html', career_report=career_report)
