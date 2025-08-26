from django.urls import path
from . import views

urlpatterns = [
    path('', views.subject_list, name='subject_list'),
    path('subject/<int:subject_id>/', views.subject_questions, name='subject_questions'),
    path('subject/<int:subject_id>/question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('subject/<int:subject_id>/results/', views.results, name='results'),
]