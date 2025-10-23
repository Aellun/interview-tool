import streamlit as st
from openai import OpenAI
from streamlit_js_eval import streamlit_js_eval
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime

# Setting up the Streamlit page configuration
st.set_page_config(page_title="AI Interview System", page_icon="📋")
st.title("AI Interview System")

# Configuration constants
MAX_MESSAGES_PER_ROUND = 3
ROUNDS = ["Behavioral", "Technical", "Case Study"]

# System prompts for each round
ROUND_SYSTEM_PROMPTS = {
    "Behavioral": """You are an HR executive conducting a behavioral interview.
    
Candidate: {name}
Experience: {experience}
Skills: {skills}
Position: {level} {position} at {company}

Assess the candidate's soft skills, teamwork, conflict resolution, and motivation.
Ask about past experiences using the STAR method (Situation, Task, Action, Result).
Ask one question at a time. Be professional and concise.
Do not provide feedback during the interview - only ask questions and acknowledge responses.""",
    
    "Technical": """You are a technical interviewer conducting a technical assessment.
    
Candidate: {name}
Experience: {experience}
Skills: {skills}
Position: {level} {position} at {company}

Assess the candidate's problem-solving abilities, technical depth, tools knowledge, and domain expertise.
Ask specific technical questions relevant to the position.
Ask one question at a time. Be professional and concise.
Do not provide feedback during the interview - only ask questions and probe deeper when needed.""",
    
    "Case Study": """You are a senior interviewer presenting a case study.
    
Candidate: {name}
Experience: {experience}
Skills: {skills}
Position: {level} {position} at {company}

Present a realistic business scenario relevant to the position.
Assess the candidate's analytical reasoning, creativity, and structured thinking.
Ask one question at a time. Be professional and concise.
Do not provide feedback during the interview - only present scenarios and listen to their approach."""
}

ROUND_FEEDBACK_PROMPT = """You are an HR evaluation assistant. Evaluate the candidate's responses from this specific round.

Round: {round_name}
Role: {level} {position}
Company: {company}

Provide feedback in this exact format:
Round Score (1-10): [Your score]
Feedback Summary: [2-3 sentence summary]
Key Strengths: [Bullet points]
Areas for Improvement: [Bullet points]

Keep it concise and actionable. Do not ask further questions."""

FINAL_FEEDBACK_PROMPT = """Combine the following round feedback reports into one overall interview evaluation.

Candidate: {name}
Position: {level} {position} at {company}

Round Feedbacks:
{all_round_feedback}

Provide final feedback in this exact format:
Overall Score (1-10): [Your score]
Summary: [3-4 sentences on overall performance]
Key Strengths: [Consolidated strengths across all rounds]
Areas for Improvement: [Consolidated improvement areas]
Hiring Recommendation: [Yes/No/Maybe with brief justification]

Be thorough but concise."""

# Initialize session state variables
if "setup_complete" not in st.session_state:
    st.session_state.setup_complete = False
if "rounds" not in st.session_state:
    st.session_state.rounds = ROUNDS
if "current_round" not in st.session_state:
    st.session_state.current_round = 0
if "round_message_count" not in st.session_state:
    st.session_state.round_message_count = 0
if "round_question_count" not in st.session_state:
    st.session_state.round_question_count = 0
if "intro_message_sent" not in st.session_state:
    st.session_state.intro_message_sent = False
if "round_messages" not in st.session_state:
    st.session_state.round_messages = []
if "all_rounds_history" not in st.session_state:
    st.session_state.all_rounds_history = []
if "round_feedback" not in st.session_state:
    st.session_state.round_feedback = []
if "chat_complete" not in st.session_state:
    st.session_state.chat_complete = False
if "feedback_generated" not in st.session_state:
    st.session_state.feedback_generated = False
if "final_feedback" not in st.session_state:
    st.session_state.final_feedback = ""


# Helper functions
def complete_setup():
    st.session_state.setup_complete = True
    initialize_round()

def initialize_round():
    """Initialize a new round with appropriate system prompt."""
    current_round_idx = st.session_state.current_round
    current_round_name = st.session_state.rounds[current_round_idx]
    
    system_prompt = ROUND_SYSTEM_PROMPTS[current_round_name].format(
        name=st.session_state["name"],
        experience=st.session_state["experience"],
        skills=st.session_state["skills"],
        level=st.session_state["level"],
        position=st.session_state["position"],
        company=st.session_state["company"]
    )
    
    st.session_state.round_messages = [{"role": "system", "content": system_prompt}]
    st.session_state.round_message_count = 0
    st.session_state.round_question_count = 0
    st.session_state.intro_message_sent = False

def generate_round_feedback():
    """Generate feedback for the current round."""
    current_round_idx = st.session_state.current_round
    current_round_name = st.session_state.rounds[current_round_idx]
    
    feedback_prompt = ROUND_FEEDBACK_PROMPT.format(
        round_name=current_round_name,
        level=st.session_state["level"],
        position=st.session_state["position"],
        company=st.session_state["company"]
    )
    
    # Collect conversation history (exclude system message)
    conversation = "\n".join([
        f"{msg['role']}: {msg['content']}"
        for msg in st.session_state.round_messages
        if msg["role"] != "system"
    ])
    
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": feedback_prompt},
            {"role": "user", "content": f"Interview transcript:\n{conversation}"}
        ]
    )
    
    feedback = response.choices[0].message.content
    st.session_state.round_feedback.append({
        "round": current_round_name,
        "feedback": feedback
    })
    
    # Store round history
    st.session_state.all_rounds_history.append({
        "round": current_round_name,
        "messages": st.session_state.round_messages.copy()
    })

def generate_final_feedback():
    """Generate aggregated final feedback across all rounds."""
    all_feedback = "\n\n".join([
        f"=== {item['round']} Round ===\n{item['feedback']}"
        for item in st.session_state.round_feedback
    ])
    
    final_prompt = FINAL_FEEDBACK_PROMPT.format(
        name=st.session_state["name"],
        level=st.session_state["level"],
        position=st.session_state["position"],
        company=st.session_state["company"],
        all_round_feedback=all_feedback
    )
    
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": final_prompt},
            {"role": "user", "content": "Generate final evaluation."}
        ]
    )
    
    st.session_state.final_feedback = response.choices[0].message.content
    st.session_state.feedback_generated = True

def export_interview_transcript():
    """Export full interview transcript as formatted text."""
    transcript_parts = []
    transcript_parts.append("=" * 60)
    transcript_parts.append("INTERVIEW TRANSCRIPT")
    transcript_parts.append("=" * 60)
    transcript_parts.append(f"\nCandidate: {st.session_state['name']}")
    transcript_parts.append(f"Position: {st.session_state['level']} {st.session_state['position']}")
    transcript_parts.append(f"Company: {st.session_state['company']}")
    transcript_parts.append(f"Experience: {st.session_state['experience']}")
    transcript_parts.append(f"Skills: {st.session_state['skills']}")
    transcript_parts.append("\n" + "=" * 60)
    
    for round_history in st.session_state.all_rounds_history:
        transcript_parts.append(f"\n{round_history['round'].upper()} ROUND")
        transcript_parts.append("-" * 60)
        for msg in round_history['messages']:
            if msg['role'] != 'system':
                transcript_parts.append(f"\n{msg['role'].upper()}: {msg['content']}\n")
    
    transcript_parts.append("\n" + "=" * 60)
    transcript_parts.append("END OF TRANSCRIPT")
    transcript_parts.append("=" * 60)
    
    return "\n".join(transcript_parts)

def generate_transcript_pdf():
    """Generate PDF of interview transcript."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1f4788',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#1f4788',
        spaceAfter=12,
        spaceBefore=12
    )
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    dialogue_style = ParagraphStyle(
        'DialogueStyle',
        parent=styles['Normal'],
        fontSize=10,
        leftIndent=20,
        spaceAfter=10
    )
    
    # Title
    story.append(Paragraph("INTERVIEW TRANSCRIPT", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Candidate Information
    story.append(Paragraph("<b>Candidate Information</b>", heading_style))
    story.append(Paragraph(f"<b>Name:</b> {st.session_state['name']}", info_style))
    story.append(Paragraph(f"<b>Position:</b> {st.session_state['level']} {st.session_state['position']}", info_style))
    story.append(Paragraph(f"<b>Company:</b> {st.session_state['company']}", info_style))
    story.append(Paragraph(f"<b>Experience:</b> {st.session_state['experience']}", info_style))
    story.append(Paragraph(f"<b>Skills:</b> {st.session_state['skills']}", info_style))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", info_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Round transcripts
    for round_history in st.session_state.all_rounds_history:
        story.append(Paragraph(f"<b>{round_history['round'].upper()} ROUND</b>", heading_style))
        story.append(Spacer(1, 0.1*inch))
        
        for msg in round_history['messages']:
            if msg['role'] != 'system':
                role_label = "Interviewer" if msg['role'] == 'assistant' else "Candidate"
                content = msg['content'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(f"<b>{role_label}:</b> {content}", dialogue_style))
        
        story.append(Spacer(1, 0.2*inch))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_feedback_pdf():
    """Generate PDF of feedback report."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.75*inch, bottomMargin=0.75*inch)
    styles = getSampleStyleSheet()
    story = []
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor='#1f4788',
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor='#1f4788',
        spaceAfter=12,
        spaceBefore=12
    )
    
    info_style = ParagraphStyle(
        'InfoStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    feedback_style = ParagraphStyle(
        'FeedbackStyle',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=10
    )
    
    # Title
    story.append(Paragraph("INTERVIEW FEEDBACK REPORT", title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Candidate Information
    story.append(Paragraph("<b>Candidate Information</b>", heading_style))
    story.append(Paragraph(f"<b>Name:</b> {st.session_state['name']}", info_style))
    story.append(Paragraph(f"<b>Position:</b> {st.session_state['level']} {st.session_state['position']}", info_style))
    story.append(Paragraph(f"<b>Company:</b> {st.session_state['company']}", info_style))
    story.append(Paragraph(f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}", info_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Final Evaluation
    story.append(Paragraph("<b>FINAL EVALUATION</b>", heading_style))
    final_feedback = st.session_state.final_feedback.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    for line in final_feedback.split('\n'):
        if line.strip():
            story.append(Paragraph(line, feedback_style))
    story.append(Spacer(1, 0.3*inch))
    
    # Round-by-Round Feedback
    story.append(Paragraph("<b>ROUND-BY-ROUND FEEDBACK</b>", heading_style))
    story.append(Spacer(1, 0.1*inch))
    
    for feedback_item in st.session_state.round_feedback:
        story.append(Paragraph(f"<b>{feedback_item['round'].upper()} ROUND</b>", heading_style))
        feedback_content = feedback_item['feedback'].replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        for line in feedback_content.split('\n'):
            if line.strip():
                story.append(Paragraph(line, feedback_style))
        story.append(Spacer(1, 0.2*inch))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# Setup stage for collecting user details
if not st.session_state.setup_complete:
    # Welcome message with instructions
    st.info(
        """**Welcome to the AI Interview System**
        
        This interview consists of three structured rounds:
        1. **Behavioral Round** - Assess your soft skills and teamwork abilities
        2. **Technical Round** - Evaluate your problem-solving and technical expertise
        3. **Case Study Round** - Test your analytical and strategic thinking
        
        Each round will have a series of questions. Answer thoughtfully and professionally.
        You will receive detailed feedback after each round and a comprehensive evaluation at the end.
        
        Please provide your information below to begin."""
    )
    
    st.subheader('Personal Information')

    # Initialize session state for personal information
    if "name" not in st.session_state:
        st.session_state["name"] = ""
    if "experience" not in st.session_state:
        st.session_state["experience"] = ""
    if "skills" not in st.session_state:
        st.session_state["skills"] = ""
   
    # Get personal information input
    st.session_state["name"] = st.text_input(label="Name", value=st.session_state["name"], placeholder="Enter your name", max_chars=40)
    st.session_state["experience"] = st.text_area(label="Experience", value=st.session_state["experience"], placeholder="Describe your experience", max_chars=200)
    st.session_state["skills"] = st.text_area(label="Skills", value=st.session_state["skills"], placeholder="List your skills", max_chars=200)
    
    # Company and Position Section
    st.subheader('Company and Position')

    # Initialize session state for company and position information and setting default values 
    if "level" not in st.session_state:
        st.session_state["level"] = "Junior"
    if "position" not in st.session_state:
        st.session_state["position"] = "Data Scientist"
    if "company" not in st.session_state:
        st.session_state["company"] = "Amazon"

    col1, col2 = st.columns(2)
    with col1:
        st.session_state["level"] = st.radio(
            "Choose level",
            key="visibility",
            options=["Junior", "Mid-level", "Senior"],
            index=["Junior", "Mid-level", "Senior"].index(st.session_state["level"])
        )

    with col2:
        st.session_state["position"] = st.selectbox(
            "Choose a position",
            ("Data Scientist", "Data Engineer", "ML Engineer", "BI Analyst", "Financial Analyst"),
            index=("Data Scientist", "Data Engineer", "ML Engineer", "BI Analyst", "Financial Analyst").index(st.session_state["position"])
        )

    st.session_state["company"] = st.selectbox(
        "Select a Company",
        ("Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify"),
        index=("Amazon", "Meta", "Udemy", "365 Company", "Nestle", "LinkedIn", "Spotify").index(st.session_state["company"])
    )

    # Validation and start button
    st.markdown("---")
    if not st.session_state["name"] or not st.session_state["experience"] or not st.session_state["skills"]:
        st.warning("Please fill in all personal information fields before starting the interview.")
    
    if st.button("Start Interview", on_click=complete_setup, type="primary", disabled=(not st.session_state["name"] or not st.session_state["experience"] or not st.session_state["skills"])):
        pass

# Interview phase
if st.session_state.setup_complete and not st.session_state.chat_complete:
    # Sidebar with active section display
    with st.sidebar:
        st.markdown("### Interview Progress")
        st.markdown("---")
        
        current_round_idx = st.session_state.current_round
        current_round_name = st.session_state.rounds[current_round_idx]
        total_rounds = len(st.session_state.rounds)
        
        # Display all rounds with active indicator
        for idx, round_name in enumerate(st.session_state.rounds):
            if idx < current_round_idx:
                st.markdown(f"✓ **{round_name}** - Completed")
            elif idx == current_round_idx:
                st.markdown(f"→ **{round_name}** - Active")
            else:
                st.markdown(f"○ **{round_name}** - Pending")
        
        st.markdown("---")
        st.markdown("### Candidate Information")
        st.markdown(f"**Name:** {st.session_state['name']}")
        st.markdown(f"**Position:** {st.session_state['level']} {st.session_state['position']}")
        st.markdown(f"**Company:** {st.session_state['company']}")
    
    # Progress indicator at the top
    current_round_idx = st.session_state.current_round
    current_round_name = st.session_state.rounds[current_round_idx]
    total_rounds = len(st.session_state.rounds)
    
    # Show progress bar
    progress = (current_round_idx + 1) / total_rounds
    st.progress(progress, text=f"Round {current_round_idx + 1} of {total_rounds}: {current_round_name}")
    
    # Question counter ring in top left
    col_counter, col_header = st.columns([1, 5])
    with col_counter:
        st.markdown(f"<div style='text-align: center; padding: 10px; border: 3px solid #1f4788; border-radius: 50%; width: 60px; height: 60px; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 18px; color: #1f4788;'>{st.session_state.round_question_count}/{MAX_MESSAGES_PER_ROUND}</div>", unsafe_allow_html=True)
    with col_header:
        st.subheader(f"{current_round_name} Round")
    
    # Initialize OpenAI client and model
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    if "openai_model" not in st.session_state:
        st.session_state["openai_model"] = "gpt-4o"
    
    # Display round instructions
    if st.session_state.round_message_count == 0:
        round_instructions = {
            "Behavioral": "In this round, you will be asked about your past experiences, teamwork, and interpersonal skills. Use the STAR method (Situation, Task, Action, Result) when answering.",
            "Technical": "This round focuses on your technical knowledge and problem-solving abilities. Be specific about your experience with tools, methodologies, and technical challenges you've faced.",
            "Case Study": "You will be presented with a business scenario. Demonstrate your analytical thinking, structured approach, and creativity in solving complex problems."
        }
        st.info(round_instructions[current_round_name])
    
    # Display chat messages for current round
    for message in st.session_state.round_messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Check if round is complete (based on question count, not total messages)
    if st.session_state.round_question_count >= MAX_MESSAGES_PER_ROUND:
        st.success(f"{current_round_name} round complete")
        st.info("Generating feedback for this round...")
        
        # Generate feedback if not already done
        if len(st.session_state.round_feedback) <= current_round_idx:
            generate_round_feedback()
        
        # Display round feedback
        with st.expander(f"View {current_round_name} Round Feedback", expanded=True):
            st.markdown(st.session_state.round_feedback[current_round_idx]["feedback"])
        
        st.markdown("---")
        
        # Check if more rounds remain
        if current_round_idx < total_rounds - 1:
            if st.button("Continue to Next Round", type="primary"):
                st.session_state.current_round += 1
                initialize_round()
                st.rerun()
        else:
            if st.button("View Final Feedback", type="primary"):
                st.session_state.chat_complete = True
                st.rerun()
    
    else:
        # Active chat input with character limit
        if prompt := st.chat_input("Your response", max_chars=1000):
            st.session_state.round_messages.append({"role": "user", "content": prompt})
            st.session_state.round_message_count += 1
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get assistant response
            with st.chat_message("assistant"):
                stream = client.chat.completions.create(
                    model=st.session_state["openai_model"],
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.round_messages
                    ],
                    stream=True
                )
                response = st.write_stream(stream)
            
            st.session_state.round_messages.append({"role": "assistant", "content": response})
            
            # After bot responds, increment question count (intro message doesn't count)
            if st.session_state.intro_message_sent:
                st.session_state.round_question_count += 1
            else:
                st.session_state.intro_message_sent = True
            
            st.rerun()

# Final feedback section
if st.session_state.chat_complete:
    st.subheader("Interview Complete")
    
    # Generate final feedback if not already done
    if not st.session_state.feedback_generated:
        with st.spinner("Generating comprehensive final feedback..."):
            generate_final_feedback()
        st.rerun()
    
    # Display final feedback
    st.markdown("### Final Evaluation Report")
    st.markdown(st.session_state.final_feedback)
    
    st.markdown("---")
    
    # Show all round feedbacks in expandable sections
    st.markdown("### Round-by-Round Feedback")
    for feedback_item in st.session_state.round_feedback:
        with st.expander(f"{feedback_item['round']} Round"):
            st.markdown(feedback_item['feedback'])
    
    st.markdown("---")
    
    # Download buttons and restart
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download interview transcript as PDF
        transcript_pdf = generate_transcript_pdf()
        st.download_button(
            label="Download Interview Transcript (PDF)",
            data=transcript_pdf,
            file_name=f"interview_transcript_{st.session_state['name'].replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    
    with col2:
        # Download feedback report as PDF
        feedback_pdf = generate_feedback_pdf()
        st.download_button(
            label="Download Feedback Report (PDF)",
            data=feedback_pdf,
            file_name=f"feedback_report_{st.session_state['name'].replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    
    with col3:
        # Restart interview button
        if st.button("Restart Interview", type="primary"):
            streamlit_js_eval(js_expressions="parent.window.location.reload()")
