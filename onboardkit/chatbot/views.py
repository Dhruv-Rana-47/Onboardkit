import os
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection
from PyPDF2 import PdfReader
import re

# --- Config ---
FLASK_API_BASE = "http://127.0.0.1:5000"
PDF_PATH = os.path.join(os.path.dirname(__file__), "docs", "intent.pdf")

# --- Load and parse PDF chunks ---
def extract_chunks_from_pdf():
    reader = PdfReader(PDF_PATH)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() + "\n"

    # Regex to split by ## intent_code
    chunks = {}
    sections = re.split(r'##\s*([a-zA-Z0-9_]+)', full_text)

    # sections = [ '', 'intent1', 'text1', 'intent2', 'text2', ... ]
    for i in range(1, len(sections)-1, 2):
        intent = sections[i].strip()
        content = sections[i+1].strip()
        chunks[intent] = content

    return chunks

INTENT_CHUNKS = extract_chunks_from_pdf()  # cached at startup

# --- Detect Intent Using LLM ---
def detect_intent(user_input):
    try:
        response = requests.post(f"{FLASK_API_BASE}/get_intent", json={"user_input": user_input})
        return response.json()
    except:
        return {"intent": "unknown", "answer": "❓ I couldn't recognize your intent.May be some Technical Issue Please 😓Try agian later!"}

# --- Call LLM to Generate Answer ---
def get_llm_answer(user_input, chunk):
    try:
        payload = {"question": user_input, "chunk": chunk}
        response = requests.post(f"{FLASK_API_BASE}/chat_with_context", json=payload)
        return response.json()
    except Exception as e:
        return {"answer": f"Error: {e}", "sources": [], "confidence": 0}

# --- Authority Check ---
def is_authorized(user_id, authority_code):
    with connection.cursor() as cursor:
        cursor.execute("SELECT role_id FROM accounts_user WHERE id = %s", [user_id])
        row = cursor.fetchone()
        if not row:
            return False
        role_id = row[0]

        cursor.execute("""
            SELECT A.code 
            FROM accounts_role_authorities RA
            JOIN accounts_authority A ON A.id = RA.authority_id
            WHERE RA.role_id = %s
        """, [role_id])
        allowed = [r[0] for r in cursor.fetchall()]
        return authority_code in allowed

# --- Intent-to-Authority Mapping ---
INTENT_TO_AUTHORITY = {
    "create_user_info": "create_user",
    "add_user_info": "create_user",
    "assign_task": "assign_task",
    "view_tasks_info": "view_tasks",
    "feedback_info": "give_feedback",
    "send_message_info": "send_message",
    "report_info": "export_reports",
    "create_template_info": "create_template",
    "assign_template_info": "assign_template",
    "edit_task_info": "edit_task",
    "get_authorities": "view_roles",
    "what_can_do": "get_authorities",
}

# --- Main Chat View ---
@csrf_exempt
def chatbot_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    if not request.user.is_authenticated:
        return JsonResponse({"error": "Unauthorized"}, status=401)

    try:
        body = json.loads(request.body)
        user_input = body.get("user_input", "").strip()
        if not user_input:
            return JsonResponse({"error": "Empty input"}, status=400)

        user_id = request.user.id

        # 1. Intent Detection
        intent_result = detect_intent(user_input)
        intent = intent_result.get("intent", "unknown")
        print(f"Intent: {intent}")

        if intent in ["greeting", "what_can_do", "unknown"]:
            return JsonResponse({"answer": intent_result.get("answer", "❓ I couldn't recognize your intent.")})

        # 2. Map to Authority
        authority_code = INTENT_TO_AUTHORITY.get(intent)
        if not authority_code:
            return JsonResponse({"answer": "❓ This intent is not mapped to any authority."})

        print(f"Authority Code: {authority_code}")

        # 3. Authorization
        if not is_authorized(user_id, authority_code):
            return JsonResponse({"answer": "🚫 You are not authorized to access this topic."})

        # 4. Get related chunk from intent.pdf
        chunk = INTENT_CHUNKS.get(intent, "")
        if not chunk:
            return JsonResponse({"answer": "📄 No instructional content found for this intent."})

        # 5. Get LLM Answer
        result = get_llm_answer(user_input, chunk)
        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
