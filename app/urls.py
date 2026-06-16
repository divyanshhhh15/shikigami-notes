from . import views

from .views import (
    hello,
    about,
    contact,
    savedataview,
    deletedataview,
    updatedataview,
    summarize_view,
    extract_tasks_view,
    generate_title_view,
    organize_view,
)
from django.urls import path

urlpatterns = [
    path('', hello, name='hello'),
    path('chat/', views.chat_with_notes, name='chat'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('deletedata/<int:id>/', deletedataview, name='deletedataview'),
    path('savedata/', savedataview, name='savedataview'),
    path('updatedata/<int:id>/', updatedataview, name='updatedataview'),
    path("summarize/<int:id>/", views.summarize_view, name="summarize"),
    path("extract/<int:id>/", views.extract_tasks_view, name="extract"),
    path("title/<int:id>/", views.generate_title_view, name="title"),
    path("organize/<int:id>/", views.organize_view, name="organize"),
    path("flashcards/<int:id>",views.flashcards, name="flashcards"),
    path("generate-pdf/<int:id>", views.generate_pdf, name="generate_pdf")
              
               ]

