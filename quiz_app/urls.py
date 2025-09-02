from django.urls import path
from . import views

urlpatterns = [
    # 🔹 Login Page
    path("login/", views.custom_login, name="login"),

    # 🔹 Subject List (Homepage after login)
    path("", views.subject_list, name="subject_list"),

    # 🔹 Subject -> Questions
    path("subject/<int:subject_id>/", views.subject_questions, name="subject_questions"),

    # 🔹 Question Detail (per subject)
    path(
        "subject/<int:subject_id>/question/<int:question_id>/",
        views.question_detail,
        name="question_detail",
    ),

    # 🔹 Results Page
    path("subject/<int:subject_id>/results/", views.results, name="results"),
]