from urllib import request
import re 
from django.shortcuts import render , redirect , get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from .models import Note, ChatSession, ChatMessage
from openai import OpenAI
from django.conf import settings

client = OpenAI(
    api_key=settings.GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)


def summarize_note(text):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Summarize notes into concise bullet points."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return response.choices[0].message.content


def extract_tasks(text):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
                Extract all actionable tasks from the note.
                Return only a checklist format.

                Example:
                ✅ Buy groceries
                ✅ Complete assignment
                """
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return response.choices[0].message.content


def generate_title(text):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Generate a short and professional title for this note."
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return response.choices[0].message.content


def organize_note(text):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": """
                Organize the note into sections.

                Format:
                📌 Main Idea
                📋 Key Points
                ✅ Tasks
                """
            },
            {
                "role": "user",
                "content": text
            }
        ]
    )

    return response.choices[0].message.content

# Create your views here.

from django.db.models import Q

def hello(request):

    query = request.GET.get("q", "")

    notes = Note.objects.all()

    if query:
        notes = Note.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(ai_summary__icontains=query) |
            Q(ai_tasks__icontains=query) |
            Q(ai_organized__icontains=query) |
            Q(ai_flashcards__icontains=query)
        )

    context = {
    "notes": notes,
    "query": query,
}

    return render(request, "index.html", context)

def about(request):
    return render(request, "about.html")


def contact(request):
    return render(request, "contact.html")


def savedataview(request):
    print(request.POST)
    title = request.POST.get("title", "")
    description = request.POST.get("description", "")

    if not title or not description:
        messages.error(request, "Please fill in all fields.")
        return redirect("/")

    note = Note(title=title, description=description, ispublished=True)
    note.save()
    messages.success(request, "Details saved successfully.")
    return redirect("/")

    return HttpResponse("details saved succesfully")


def deletedataview(request, id):
    note = Note.objects.get(id=id)
    note.delete()
    messages.success(request, "Details deleted successfully.")
    return redirect("/")


def updatedataview(request, id):
    note = get_object_or_404(Note, id=id)
    if request.method == "POST":
        title = request.POST.get("title", "")
        description = request.POST.get("description", "")
        published = request.POST.get("published", "off") == "on"

        if not title or not description:
            messages.error(request, "Please fill in all fields.")
            return redirect(f"/update/{id}")

        note.title = title
        note.description = description
        note.ispublished = published
        note.save()
        messages.success(request, "Details updated successfully.")
        return redirect("/")

    return render(request, "editpage.html", context={"note": note})


def summarize_view(request, id):

    note = get_object_or_404(Note, id=id)

    summary = summarize_note(note.description)

    note.ai_summary = summary
    note.save()

    return redirect("/")


def extract_tasks_view(request, id):

    note = get_object_or_404(Note, id=id)

    tasks = extract_tasks(note.description)

    note.ai_tasks = tasks
    note.save()

    messages.success(request, "Tasks extracted successfully.")
    return redirect("/")


def generate_title_view(request, id):

    note = get_object_or_404(Note, id=id)

    title = generate_title(note.description)
    note.title = (title or "").strip()
    note.save()

    messages.success(request, "Title generated successfully.")
    return redirect("/")


def organize_view(request, id):

    note = get_object_or_404(Note, id=id)

    organized = organize_note(note.description)

    note.ai_organized = organized
    note.save()

    messages.success(request, "Note organized successfully.")
    return redirect("/")


# Hardened notes-only chat implementation is in app/chat_views.py
def _tokenize(q: str):
    q = (q or "").lower()
    return set(re.findall(r"[a-z0-9']+", q))


def chat_with_notes(request):
    # Reuse/continue the existing chat session for this browser session
    session_key = "chat_session_id"
    """Notes-only chatbot.

    Debug-friendly retrieval:
    - only published notes
    - keyword scoring to select top-k notes (prevents dumping everything)
    - strict prompt: must refuse with an exact string if no evidence
    """
    notes = list(Note.objects.filter(ispublished=True))
    ai_answer = None

    # Get or create the existing ChatSession tied to this browser session.
    # This prevents creating a new chat thread every single message.
    session_id = request.session.get(session_key)
    if session_id:
        chat_session = ChatSession.objects.filter(id=session_id).first()
    else:
        chat_session = None

    if chat_session is None:
        chat_session = ChatSession.objects.create(title="New Chat")
        request.session[session_key] = chat_session.id
        request.session.modified = True


    if request.method == "POST":
        question = (request.POST.get("question", "") or "").strip()

        # Save user message to DB
        if question:
            ChatMessage.objects.create(session=chat_session, role="user", message=question)
        if question:
            q_tokens = _tokenize(question)

            scored = []
            for n in notes:
                text = f"{n.title}\n{n.description}".lower()
                score = sum(1 for t in q_tokens if t in text)
                scored.append((score, n))

            scored.sort(key=lambda x: x[0], reverse=True)
            top_k = 6
            selected = [n for score, n in scored[:top_k] if score > 0]

            notes_block = ""
            if selected:
                notes_block = "\n\n".join(
                    [
                        f"[Note {i+1}]\nTitle: {n.title}\nDescription: {n.description}"
                        for i, n in enumerate(selected)
                    ]
                )

            prompt = f"""
You are a chatbot for a notes application.

You MUST answer using ONLY the provided notes block.
If the notes do not contain the answer, respond with EXACTLY:
No relevant information in notes

Rules:
- Do not use any external knowledge.
- Do not guess.
- If you answer, include a line starting with: Evidence:
  followed by the exact note text you used (quote 1–2 short sentences).
- Keep the answer short (max 5 sentences).

Notes block:
{notes_block if notes_block else '(no notes provided)'}
---
User question:
{question}
""".strip()

            # Save assistant message to DB
            try:
                response = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "Follow strict instructions. Refuse if evidence is missing."},
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.0,
                )
                ai_answer = response.choices[0].message.content.strip()
                if "No relevant information in notes" in ai_answer:
                    ai_answer = "No relevant information in notes"
            # Save assistant message to DB
                if ai_answer:
                    ChatMessage.objects.create(session=chat_session, role="assistant", message=ai_answer)

            except Exception as e:
                print("AI ERROR:", e)
                ai_answer = "AI error occurred. Check API key or model."

    # Load chat history from DB for this session
    chat_messages = chat_session.messages.order_by("created_at")

    return render(
        request,
        "index.html",
        {
            "notes": notes,
            "ai_answer": ai_answer,
            "chat_session": chat_session,
            "chat_messages": chat_messages,
        },
    )

def flashcards(request, id):
    note = Note.objects.get(id=id)

    prompt = f"""
    Create 5 flashcards from this note.

    Format:

    Q: Question
    A: Answer

    Note:
    {note.description}
    """

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    flashcards = response.choices[0].message.content

    note.ai_flashcards = flashcards
    note.save()

    return redirect("/")

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer
)

from reportlab.lib.styles import getSampleStyleSheet

from .models import Note

def generate_pdf(request, id):

    note = Note.objects.get(id=id)

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = f'attachment; filename="{note.title}.pdf"'

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    story = []

    story.append(
        Paragraph(
            note.title,
            styles["Title"]
        )
    )

    story.append(Spacer(1, 12))

    story.append(
        Paragraph(
            f"<b>Description:</b><br/>{note.description}",
            styles["BodyText"]
        )
    )

    story.append(Spacer(1, 12))

    if note.ai_summary:
        story.append(
            Paragraph(
                f"<b>AI Summary:</b><br/>{note.ai_summary}",
                styles["BodyText"]
            )
        )

    story.append(Spacer(1, 12))

    if note.ai_tasks:
        story.append(
            Paragraph(
                f"<b>AI Tasks:</b><br/>{note.ai_tasks}",
                styles["BodyText"]
            )
        )

    story.append(Spacer(1, 12))

    if note.ai_organized:
        story.append(
            Paragraph(
                f"<b>AI Organized:</b><br/>{note.ai_organized}",
                styles["BodyText"]
            )
        )

    story.append(Spacer(1, 12))

    if note.ai_flashcards:
        story.append(
            Paragraph(
                f"<b>Flashcards:</b><br/>{note.ai_flashcards}",
                styles["BodyText"]
            )
        )

    doc.build(story)

    return response



