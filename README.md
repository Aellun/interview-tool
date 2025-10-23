# AI Interview System

A structured, multi-round interview application built with Streamlit and OpenAI's GPT-4. The system conducts professional technical interviews across three distinct rounds: Behavioral, Technical, and Case Study, with comprehensive feedback generation and PDF reporting.

## Features

### Multi-Round Interview Structure
- **Behavioral Round**: Evaluates soft skills, teamwork, and conflict resolution using the STAR method
- **Technical Round**: Assesses problem-solving abilities, technical depth, and domain expertise
- **Case Study Round**: Tests analytical reasoning through realistic business scenarios

### Real-Time Progress Tracking
- Visual progress bar showing current round and completion status
- Question counter displaying current question out of total questions per round
- Sidebar navigation showing completed, active, and pending rounds
- Candidate information displayed throughout the interview

### Intelligent Question Management
- Introduction message not counted toward question limit
- Question tracking begins after initial greeting exchange
- Configurable questions per round (default: 3 questions)
- Character limits enforced on all inputs for quality responses

### Comprehensive Feedback System
- Automated per-round feedback generation after each round completion
- Structured evaluation including:
  - Round Score (1-10)
  - Feedback Summary
  - Key Strengths
  - Areas for Improvement
- Final aggregated evaluation with:
  - Overall Score (1-10)
  - Performance Summary
  - Consolidated Strengths
  - Consolidated Improvement Areas
  - Hiring Recommendation (Yes/No/Maybe)

### Professional PDF Reports
- Interview Transcript: Complete dialogue from all rounds with professional formatting
- Feedback Report: Final evaluation and round-by-round feedback in organized PDF
- Reports include candidate information, timestamps, and proper sectioning

### User Experience
- Clean, professional interface without visual clutter
- Form validation ensuring complete information before starting
- Expandable feedback sections for easy review
- Streaming responses for natural conversation flow
- Page reload functionality for starting new interviews

## Installation

### Prerequisites
- Python 3.8 or higher
- OpenAI API key

### Setup Instructions

1. Clone or download this repository
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

3. Create `.streamlit/secrets.toml` file in the project directory:

```toml
OPENAI_API_KEY = "your-api-key-here"
```

Replace `your-api-key-here` with your actual OpenAI API key.

## Usage

### Starting the Application

Run the following command in the project directory:

```bash
streamlit run app.py
```

The application will open in your default web browser.

### Interview Process

#### Step 1: Setup
1. Read the welcome message explaining the interview structure
2. Fill in required information:
   - Name (maximum 40 characters)
   - Experience (maximum 200 characters)
   - Skills (maximum 200 characters)
   - Level: Junior, Mid-level, or Senior
   - Position: Data Scientist, Data Engineer, ML Engineer, BI Analyst, or Financial Analyst
   - Company: Select from available options
3. Click "Start Interview" (button is disabled until all fields are complete)

#### Step 2: Behavioral Round
- Introduce yourself in the first message
- Answer 3 behavioral questions about past experiences
- Use the STAR method (Situation, Task, Action, Result) for structured responses
- Each response limited to 1000 characters
- Feedback generated automatically after completion

#### Step 3: Technical Round
- Answer 3 technical questions specific to your selected position
- Demonstrate problem-solving abilities and technical knowledge
- Be specific about tools, frameworks, and methodologies
- Feedback generated automatically after completion

#### Step 4: Case Study Round
- Respond to a realistic business scenario
- Show analytical thinking and structured problem-solving approach
- Answer 3 follow-up questions about your approach
- Feedback generated automatically after completion

#### Step 5: Final Evaluation
- Review comprehensive final evaluation report
- Access all round-by-round feedback in expandable sections
- Download PDF reports:
  - Interview Transcript (complete conversation history)
  - Feedback Report (all evaluations and recommendations)
- Restart interview for a new session if desired

### Character Limits
- **Name**: 40 characters
- **Experience**: 200 characters
- **Skills**: 200 characters
- **Chat Responses**: 1000 characters per message

These limits ensure focused, quality responses and optimal AI evaluation.

## Configuration

### Adjusting Questions Per Round

Edit line 18 in `app.py`:

```python
MAX_MESSAGES_PER_ROUND = 3  # Change to desired number
```

### Modifying Interview Rounds

Edit line 19 in `app.py`:

```python
ROUNDS = ["Behavioral", "Technical", "Case Study"]
```

To add or remove rounds, you must also update the system prompts in the `ROUND_SYSTEM_PROMPTS` dictionary (lines 22-58).

### Changing AI Model

Edit line 502 in `app.py`:

```python
st.session_state["openai_model"] = "gpt-4o"  # Change to another model
```

Available models: `gpt-4o`, `gpt-4o-mini`, `gpt-4-turbo`, etc.

## Technical Architecture

### Session State Management
The application uses Streamlit's session state to maintain interview progress across interactions:

- `setup_complete`: Controls transition from setup to interview
- `rounds`: List of round names
- `current_round`: Index of active round (0-based)
- `round_message_count`: Total messages in current round
- `round_question_count`: Questions answered (excluding intro)
- `intro_message_sent`: Flag to track if introduction was completed
- `round_messages`: Chat history for current round
- `all_rounds_history`: Complete history for transcript generation
- `round_feedback`: Array of per-round feedback objects
- `chat_complete`: Triggers final feedback generation
- `feedback_generated`: Prevents duplicate feedback generation
- `final_feedback`: Aggregated evaluation report

### System Prompts
Each round uses a tailored system prompt to guide the AI interviewer:

- **Behavioral**: HR executive persona focusing on soft skills and STAR method
- **Technical**: Technical interviewer persona assessing domain knowledge
- **Case Study**: Senior interviewer persona presenting business scenarios

### Feedback Generation
Two-stage feedback process:

1. **Per-Round Feedback**: Generated immediately after round completion using only that round's conversation
2. **Final Feedback**: Aggregates all round feedbacks for comprehensive evaluation

### PDF Generation
Uses ReportLab library to create professional PDF documents with:
- Custom styling and formatting
- Proper text escaping for special characters
- Hierarchical structure with headers and sections
- Consistent typography and spacing

## File Structure

```
AI_enginering/
├── app.py                          # Main application

├── requirements.txt                # Python dependencies
├── .streamlit/
│   └── secrets.toml               # OpenAI API key (gitignored)
├── README.md                       # This file
```

## Dependencies

- **streamlit** (1.50.0): Web application framework
- **openai** (1.99.1): OpenAI API client
- **streamlit-js-eval** (0.1.7): JavaScript execution for page reload
- **reportlab** (4.0.7): PDF generation library

## Troubleshooting

### Cannot Start Interview
**Cause**: Required fields are empty  
**Solution**: Ensure Name, Experience, and Skills fields are filled before clicking "Start Interview"

### Character Limit Exceeded
**Cause**: Input exceeds maximum allowed characters  
**Solution**: Shorten your response according to the displayed character limits

### Feedback Not Generating
**Cause**: Missing or invalid OpenAI API key  
**Solution**: Verify `.streamlit/secrets.toml` contains a valid `OPENAI_API_KEY`

### Lost Progress After Refresh
**Cause**: Streamlit session state is browser-session based  
**Solution**: Download PDF reports before refreshing or closing the browser

### PDF Generation Error
**Cause**: Special characters or formatting issues  
**Solution**: The system automatically escapes special characters, but ensure responses don't contain extremely unusual formatting

### API Rate Limits
**Cause**: Too many requests to OpenAI API  
**Solution**: Wait a few moments between interview sessions or upgrade your OpenAI plan

## Best Practices

### For Candidates

**During Setup**
- Be thorough and specific in describing experience and skills
- This information helps the AI tailor questions to your background

**During Behavioral Round**
- Use the STAR method for structured responses
- Provide concrete examples from past experiences
- Be honest about challenges and how you overcame them

**During Technical Round**
- Be specific about technologies, tools, and methodologies
- Explain your problem-solving process
- Demonstrate depth of knowledge in your domain

**During Case Study Round**
- Show your analytical thinking process
- Ask clarifying questions if needed
- Structure your response logically

### For Administrators

**Customizing Prompts**
- Modify system prompts to match your company's interview style
- Adjust evaluation criteria in feedback prompts
- Test changes with sample interviews

**Managing Questions**
- Adjust `MAX_MESSAGES_PER_ROUND` based on desired interview depth
- Consider reducing for screening interviews (2 questions)
- Consider increasing for detailed assessments (5 questions)

**Storing Results**
- Encourage candidates to download PDF reports immediately after completion
- Consider implementing database storage for record-keeping
- Maintain consistency in evaluation criteria across candidates

## Privacy and Data

### Data Storage
- Interview data is stored only in browser session state during active sessions
- No conversation data is permanently stored by the application
- PDF downloads are generated client-side and saved locally

### OpenAI Data Usage
- Conversations are sent to OpenAI for processing
- Subject to OpenAI's data usage policies
- Review OpenAI's privacy policy for enterprise use cases

### Recommendations
- Inform candidates about AI-assisted interview process
- Store downloaded PDFs securely
- Consider implementing additional encryption for sensitive information
- Review compliance requirements for your jurisdiction

## Limitations

- Requires active internet connection for OpenAI API access
- Session state does not persist across page refreshes
- Maximum 1000 characters per response
- Limited to configured interview rounds and questions
- PDF generation may have formatting limitations with very long responses

## Future Enhancements

Potential improvements for future versions:

- Database integration for persistent storage
- Video/audio recording capabilities
- Multiple language support
- Customizable evaluation rubrics
- Batch interview processing
- Interview scheduling system
- Email notification of results
- Advanced analytics dashboard
- Role-based access control
- Integration with applicant tracking systems

## Support

For issues, questions, or contributions:

1. Review this README and supporting documentation
2. Check the troubleshooting section
3. Verify your OpenAI API key and configuration

## License

This project is provided as-is for educational and commercial use. Ensure compliance with OpenAI's terms of service when deploying.

## Version

Current Version: 2.0  
Last Updated: October 2025  
Compatibility: Python 3.8+, Streamlit 1.50.0+
