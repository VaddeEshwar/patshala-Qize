from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.http import Http404
from .models import Subject, Question, Explanation, UserProgress



def subject_list(request):
    print("subject_list view called")
    print(Subject.objects.all())
    subjects = Subject.objects.all()
    return render(request, 'subject_list.html', {'subjects': subjects})




def question_detail(request, subject_id, question_id):
    subject = get_object_or_404(Subject, id=subject_id)

    try:
        question = Question.objects.select_related('subject').prefetch_related('options').get(
            id=question_id, subject=subject
        )
    except Question.DoesNotExist:
        raise Http404("Question not found.")

    options = list(question.options.all())
    correct_options = [opt for opt in options if opt.is_correct]
    if len(correct_options) != 1:
        raise Http404("Invalid question: must have exactly one correct answer.")
    correct_option = correct_options[0]

    explanation = Explanation.objects.filter(question=question).first()

    next_question = Question.objects.filter(subject=subject, id__gt=question_id).order_by('id').first()
    previous_question = Question.objects.filter(subject=subject, id__lt=question_id).order_by('-id').first()

    user_id = request.user.pk if request.user.is_authenticated else None
    progress, _ = UserProgress.objects.get_or_create(
        user_id=user_id,
        question=question,
        defaults={'subject': subject}
    )

    feedback = None
    hint = None
    show_next = False
    show_hint_option = False
    highlight_correct = False
    highlight_wrong = False
    wrong_option_ids = []
    max_attempts_reached = progress.attempts >= 2 and not progress.answered_correctly

    if 'hint' in request.GET and not progress.hint_used:
        progress.hint_used = True
        progress.save(update_fields=['hint_used'])
        hint = question.hint or "Think carefully!"

    if request.method == "POST" and not max_attempts_reached:
        selected_option_id = request.POST.get("answer")
        if not selected_option_id:
            feedback = {
                "type": "warning",
                "icon": "exclamation-triangle",
                "title": "No Answer Selected",
                "message": "Please select an option before submitting.",
            }
        else:
            selected_option = next((opt for opt in options if str(opt.id) == selected_option_id), None)
            if selected_option:
                is_correct = selected_option.is_correct
                progress.attempts += 1
                progress.answered_correctly = is_correct
                progress.selected_option = selected_option
                progress.save(update_fields=['attempts', 'answered_correctly', 'selected_option'])

                if is_correct:
                    feedback = {
                        "type": "success",
                        "icon": "check-circle",
                        "title": "Correct!",
                        "message": f"'{selected_option.text_content}' is the right answer.",
                        "explanation": explanation.text_content if explanation else None,
                    }
                    highlight_correct = True
                    show_next = True
                else:
                    if progress.attempts == 1:
                        feedback = {
                            "type": "error",
                            "icon": "times-circle",
                            "title": "Wrong Answer",
                            "message": "That's not correct. Would you like a hint?",
                        }
                        show_hint_option = True
                        wrong_option_ids.append(selected_option.id)
                    elif progress.attempts >= 2:
                        feedback = {
                            "type": "error",
                            "icon": "times-circle",
                            "title": "Attempts Completed",
                            "message": f"The correct answer is: {correct_option.text_content}",
                            "explanation": explanation.text_content if explanation else None,
                        }
                        highlight_correct = True
                        highlight_wrong = True
                        wrong_option_ids = [opt.id for opt in options if not opt.is_correct]
                        show_next = True

    total_questions = Question.objects.filter(subject=subject).count()
    current_index = Question.objects.filter(subject=subject, id__lte=question_id).count()

    context = {
        "subject": subject,
        "question": question,
        "options": options,
        "feedback": feedback,
        "hint": hint,
        "progress": int((current_index / total_questions) * 100),
        "current_question": current_index,
        "total_questions": total_questions,
        "attempts": min(progress.attempts, 2),
        "max_attempts": 2,
        "show_next": show_next,
        "next_question": next_question,
        "previous_question": previous_question,
        "is_first_question": previous_question is None,
        "is_last_question": next_question is None,
        "show_hint_option": show_hint_option,
        "highlight_correct": highlight_correct,
        "highlight_wrong": highlight_wrong,
        "correct_option_id": correct_option.id,
        "wrong_option_ids": wrong_option_ids,
        "max_attempts_reached": max_attempts_reached,
        "is_answer_locked": max_attempts_reached or show_next,
    }
    return render(request, "quiz.html", context)



def subject_questions(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    first_question = subject.question_set.first()
    if first_question:
        return redirect('question_detail', subject_id=subject_id, question_id=first_question.id)
    return render(request, 'no_questions.html', {'subject': subject})


def results(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    user_id = request.user.pk if request.user.is_authenticated else None

    # Use select_related to avoid N+1 when accessing question.text_content
    progress_list = UserProgress.objects.filter(
        user_id=user_id,
        subject=subject
    ).select_related('question')

    total_questions = subject.question_set.count()
    correct_answers = progress_list.filter(answered_correctly=True).count()
    score_percentage = int((correct_answers / total_questions) * 100) if total_questions > 0 else 0

    # Enrich progress objects for template
    results = []
    for progress in progress_list:
        question_text = progress.question.text_content or "Unnamed Question"
        if progress.answered_correctly:
            status = "Correct"
        elif progress.attempts >= 2:  # Failed after 2 attempts
            status = "Incorrect"
        else:
            status = "Incomplete"  # Not finished yet
        results.append({
            'question_text': question_text,
            'attempts': progress.attempts,
            'hints_used': progress.hint_used,
            'status': status,
        })

    context = {
        'subject': subject,
        'results': results,
        'total_questions': total_questions,
        'correct_answers': correct_answers,
        'score_percentage': score_percentage,
    }

    return render(request, 'results.html', context)