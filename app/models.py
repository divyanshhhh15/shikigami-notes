from django.db import models

# Create your models here.
class Note(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    ispublished = models.BooleanField(default=True)

    # AI generated fields
    ai_summary = models.TextField(blank=True, null=True)
    ai_tasks = models.TextField(blank=True, null=True)
    ai_organized = models.TextField(blank=True, null=True)

    ai_flashcards = models.TextField(blank=True, null=True)
class ChatSession(models.Model):
    """
    One chat session per user (like ChatGPT conversation thread)
    """
    title = models.CharField(max_length=200, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class ChatMessage(models.Model):
    """
    Stores each message in chatbot
    """
    ROLE_CHOICES = [
        ("user", "User"),
        ("assistant", "Assistant"),
    ]

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    message = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.message[:30]}"
  