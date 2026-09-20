from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import anthropic
import os
from datetime import datetime

load_dotenv()

print("Starting RV BD Agent server...")

app = Flask(__name__)
CORS(app)

api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not found in environment")
    exit(1)

print(f"✓ API Key found: {api_key[:10]}...")

try:
    client = anthropic.Anthropic(api_key=api_key)
    print("✓ Anthropic client initialized")
except Exception as e:
    print(f"ERROR creating Anthropic client: {e}")
    exit(1)

SYSTEM_PROMPT = """You are the RV Business Development Agent for Ramirez Ventures LLC, an independent federal advisory firm specializing in global payroll implementation, HR transformation, and change management.

Your mission: Help Fernando identify stale prospects, research new business opportunities, and draft compelling, personalized outreach emails.

Key context:
- Company: Ramirez Ventures LLC (SDVOSB/VOSB certified)
- Contact: Fernando I. Ramirez, Fernando@RamirezVentures.com
- Services: Global payroll, HR/benefits implementation, change management, business transformation consulting
- Target markets: Federal contractors (primes/subs nationwide), private companies (100-300 headcount, Palm Coast FL area + 100 miles)
- Website: RamirezVentures.com
- Key decision-makers: VPs of Operations, Program Managers, Business Development leads, HR Directors

Your responsibilities:
1. Scan Outlook sent folder for prospects without replies (14+ days = follow-up trigger)
2. Draft personalized follow-up emails that reference prior conversations
3. Research new prospects with specific pain points and contact information
4. Analyze Bid Match opportunities against NAICS codes
5. All drafts are for review/approval (never auto-send)
6. Keep prospect tracking updated with status, dates, and next actions

Tone: Professional, consultative, direct. Show knowledge of their business/challenges. Make it personal, not spammy."""

@app.route('/api/scan-sent', methods=['POST'])
def scan_sent_folder():
    try:
        data = request.json
        email = data.get('email', 'Fernando@RamirezVentures.com')
        
        prompt = f"""I need you to help me scan my Outlook sent folder for stale prospects.

My email: {email}
Time period: Last 12 months

Please identify any prospects who:
1. Received an email 14-21 days ago with no reply
2. Received an email 21+ days ago with no reply

For each prospect, list:
- Company name
- Contact person and title
- Email sent date
- Days since last email
- Suggested follow-up approach

Format as a clean, scannable list. Focus on business development prospects (federal contractors, corporate HR/payroll leads)."""

        message = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text if message.content else "No results found"
        
        return jsonify({
            "status": "success",
            "action": "scan_sent_folder",
            "email": email,
            "results": response_text
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/find-prospects', methods=['POST'])
def find_prospects():
    try:
        data = request.json
        prospect_type = data.get('prospect_type', 'both')
        keywords = data.get('keywords', '')
        
        prospect_desc = {
            'federal': 'federal contractors, GSA schedule holders, primes, and subs (nationwide)',
            'private': 'private companies in Palm Coast FL area + 100 miles with 100-300 headcount',
            'both': 'both federal contractors (nationwide) and private companies (Palm Coast area + 100 miles, 100-300 headcount)'
        }
        
        prompt = f"""I need you to help me identify new business development prospects for Ramirez Ventures.

Prospect Type: {prospect_desc.get(prospect_type, prospect_desc['both'])}
{f'Keywords/Focus: {keywords}' if keywords else ''}

Please research and identify high-fit prospects:
- Company name and location
- Headcount/type
- Decision-maker: Title, name (if known), email (if available)
- Pain points or recent news indicating need for our services
- Why they're a good fit for Ramirez Ventures (global payroll, HR transformation, change management)
- Fit score (1-10)

Format as a clean list with these details for each prospect. Focus on actionable intelligence."""

        message = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text if message.content else "No results found"
        
        return jsonify({
            "status": "success",
            "action": "find_prospects",
            "prospect_type": prospect_type,
            "results": response_text
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/draft-email', methods=['POST'])
def draft_email():
    try:
        data = request.json
        company = data.get('company', '')
        contact = data.get('contact', '')
        context = data.get('context', '')
        email_type = data.get('email_type', 'follow-up')
        
        if email_type == 'follow-up':
            prompt = f"""Draft a personalized follow-up email from Fernando Ramirez (Ramirez Ventures) to {contact} at {company}.

Context: {context if context else 'This is a follow-up to a previous email that went unanswered.'}

Keep it brief (under 120 words), reference the prior conversation topic subtly, focus on value (global payroll, transformation, change management), and end with a clear call-to-action for a brief call.

Format: Just the email body, ready to copy to Outlook Drafts and send."""
        else:
            prompt = f"""Draft a compelling cold outreach email from Fernando Ramirez (Ramirez Ventures, RamirezVentures.com) to {contact} at {company}.

Context: {context if context else 'This company likely needs global payroll, HR transformation, or change management consulting.'}

Keep it brief (under 120 words), consultative tone, reference their specific situation if known, and end with a clear call-to-action for a brief call.

Format: Just the email body, ready to copy to Outlook Drafts and send."""
        
        message = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=1000,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text if message.content else "Failed to draft email"
        
        return jsonify({
            "status": "success",
            "action": "draft_email",
            "company": company,
            "contact": contact,
            "email_type": email_type,
            "draft": response_text
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/scan-bidmatch', methods=['POST'])
def scan_bidmatch():
    try:
        prompt = """I need you to help me analyze my Bid Match email stream for opportunities matching my business.

I'm Fernando Ramirez at Ramirez Ventures LLC. I receive daily Bid Match emails (NAICS codes: 541600, 541611, 541618 - management, scientific, and technical consulting).

I'm SDVOSB/VOSB certified, which qualifies me for federal contracting set-asides.

Please identify from recent Bid Match alerts:
- High-fit GSA schedule or federal contracting opportunities
- Requirements matching my services (global payroll, HR transformation, change management)
- Deadlines (priority to near-term opportunities)
- Why they're a good fit

Format as a clean list with: Opportunity Title, Agency, Deadline, Priority Level, Fit Assessment."""

        message = client.messages.create(
            model="claude-opus-4-1",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        
        response_text = message.content[0].text if message.content else "No matching opportunities found"
        
        return jsonify({
            "status": "success",
            "action": "scan_bidmatch",
            "results": response_text
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "RV Business Development Agent Backend"
    }), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "RV Business Development Agent Backend",
        "status": "running",
        "endpoints": {
            "/api/scan-sent": "POST - Scan Outlook sent folder for stale prospects",
            "/api/find-prospects": "POST - Research new prospects",
            "/api/draft-email": "POST - Draft personalized email",
            "/api/scan-bidmatch": "POST - Scan Bid Match for opportunities",
            "/api/health": "GET - Health check"
        }
    }), 200

if __name__ == '__main__':
    print("✓ Server ready. Listening on http://0.0.0.0:5000")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)