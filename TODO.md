# TODO - Chat session should show in DB (SQLite)

- [x] Update `app/views.py` to pass `chat_messages` from current `ChatSession` into template.

- [x] Update `app/templates/index.html` to render `chat_messages` (user + assistant) from DB.

- [ ] (Optional) Ensure `request.session.modified = True` when saving session id.
- [ ] Run server and manually verify:
  - [ ] Send multiple chat questions
  - [ ] Confirm DB `ChatSession` and `ChatMessage` rows grow
  - [ ] Confirm UI shows full conversation

