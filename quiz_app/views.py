# views.py
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Subject, Question, Explanation, UserProgress

def custom_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("subject_list")
    return render(request, "login.html")
# ----------------- SUBJECT LIST -----------------
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, "subject_list.html", {"subjects": subjects})


# ----------------- START QUIZ -----------------
def subject_questions(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    first_question = subject.question_set.first()
    if first_question:
        return redirect("question_detail", subject_id=subject_id, question_id=first_question.id)
    return render(request, "no_questions.html", {"subject": subject})


# ----------------- QUESTION DETAIL -----------------
@login_required(login_url="login")
def question_detail(request, subject_id, question_id):
    subject = get_object_or_404(Subject, id=subject_id)
    question = get_object_or_404(Question, id=question_id, subject=subject)
    options = question.options.all()
    explanation = getattr(question, "explanation", None)

    # Next question
    next_question = Question.objects.filter(
        subject=subject, id__gt=question.id
    ).order_by("id").first()

    # Track progress
    progress, _ = UserProgress.objects.get_or_create(
        user=request.user, subject=subject, question=question
    )

    feedback, show_hint_option = None, False
    highlight_correct, highlight_wrong = False, False
    wrong_option_ids, show_next = [], False

    if request.method == "POST":
        selected_option_id = request.POST.get("answer")

        if not selected_option_id:
            feedback = {
                "type": "warning",
                "icon": "exclamation-triangle",
                "title": "No Answer Selected",
                "message": "Please select an option before submitting.",
            }
        else:
            selected_option = get_object_or_404(options, id=selected_option_id)

            # Update progress
            is_correct = selected_option.is_correct
            progress.attempts += 1
            progress.answered_correctly = is_correct
            progress.selected_option = selected_option
            progress.save(update_fields=["attempts", "answered_correctly", "selected_option"])

            if is_correct:
                # ✅ Auto redirect to next question or results
                if request.headers.get("x-requested-with") == "XMLHttpRequest":
                    next_url = (
                        reverse("question_detail", args=[subject.id, next_question.id])
                        if next_question else reverse("results", args=[subject.id])
                    )
                    return JsonResponse({
                        "auto_redirect": True,
                        "next_url": next_url,
                        "next_is_finish": next_question is None,
                    })
                return redirect("question_detail", subject.id, next_question.id) if next_question else redirect("results", subject.id)

            else:
                # ❌ Wrong answer → Show hint + retry (max 2 attempts)
                if progress.attempts == 1:
                    feedback = {
                        "type": "error",
                        "icon": "times-circle",
                        "title": "Wrong Answer",
                        "message": "That's not correct. Try again or use a hint.",
                    }
                    show_hint_option = True
                    wrong_option_ids.append(selected_option.id)

                elif progress.attempts >= 2:
                    correct_option = next(opt for opt in options if opt.is_correct)
                    feedback = {
                        "type": "error",
                        "icon": "times-circle",
                        "title": "Attempts Completed",
                        "message": f"The correct answer is: {correct_option.text_content}",
                        "explanation": explanation.text_content if explanation else None,
                    }
                    highlight_correct, highlight_wrong, show_next = True, True, True
                    wrong_option_ids = [opt.id for opt in options if not opt.is_correct]

    context = {
        "subject": subject,
        "question": question,
        "options": options,
        "feedback": feedback,
        "show_hint_option": show_hint_option,
        "highlight_correct": highlight_correct,
        "highlight_wrong": highlight_wrong,
        "wrong_option_ids": wrong_option_ids,
        "show_next": show_next,
        "next_question": next_question,
        "current_question": question.id,
        "total_questions": subject.question_set.count(),
        "attempts": progress.attempts,
        "max_attempts": 2,
        
    }
    return render(request, "quiz.html", context)


# ----------------- RESULTS -----------------
@login_required(login_url="login")
def results(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    user_id = request.user.pk

    progress_list = UserProgress.objects.filter(
        user_id=user_id, subject=subject
    ).select_related("question")

    total_questions = subject.question_set.count()
    correct_answers = progress_list.filter(answered_correctly=True).count()
    score_percentage = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0

    results = []
    for progress in progress_list:
        question_text = progress.question.text_content or "Unnamed Question"
        if progress.answered_correctly:
            status = "Correct"
        elif progress.attempts >= 2:
            status = "Incorrect"
        else:
            status = "Incomplete"
        results.append({
            "question_text": question_text,
            "attempts": progress.attempts,
            "hints_used": progress.hint_used,
            "status": status,
        })

    return render(request, "results.html", {
        "subject": subject,
        "results": results,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "score_percentage": score_percentage,
    })
