from django.db import models
from django.core.exceptions import ValidationError
from PIL import Image
from django.contrib.auth.models import User



def validate_image(image):
    img = Image.open(image)
    if img.width != 350 or img.height != 180:
        raise ValidationError("Image must be exactly 350 × 180 pixels.")
    
    
class Subject(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=200,help_text="Description must be under 200 characters.")
    logo_image  = models.ImageField(upload_to='logos/', blank=True, null=True,help_text="Upload an image of size 350 × 180 px.",validators=[validate_image])

    class Meta:
        db_table = 'quiz_subject'
    
    def __str__(self):
        return self.name

class Question(models.Model):
    TEXT = 'text'
    IMAGE = 'image'
    QUESTION_TYPES = [
        (TEXT, 'Text Question'),
        (IMAGE, 'Image Question'),
    ]
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES, default=TEXT)
    text_content = models.TextField(blank=True, null=True)
    image_content = models.ImageField(upload_to='questions/', blank=True, null=True)
    hint = models.TextField(blank=True, null=True)
    
    class Meta:
        db_table = 'quiz_question'
    
    def __str__(self):
        return f"Question {self.id} for {self.subject.name}"

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    text_content = models.TextField(blank=True, null=True)
    image_content = models.ImageField(upload_to='options/', blank=True, null=True)
    is_correct = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'quiz_option'
    
    def __str__(self):
        return f"Option {self.id} for Question {self.question.id}"

class Explanation(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    text_content = models.TextField(blank=True, null=True)
    image_content = models.ImageField(upload_to='explanations/', blank=True, null=True)
    
    class Meta:
        db_table = 'quiz_explanation'
    
    def __str__(self):
        return f"Explanation for Question {self.question.id}"





class UserProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)

    # ✅ New field to track user’s last chosen option
    selected_option = models.ForeignKey(
    Option, on_delete=models.SET_NULL, null=True, blank=True
     )

    attempts = models.IntegerField(default=0)
    answered_correctly = models.BooleanField(default=False)
    hint_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'quiz_userprogress'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'question'],
                name='unique_user_per_question'
            )
        ]
        indexes = [
            models.Index(fields=['user', 'subject']),
        ]

    def __str__(self):
        username = self.user.username if self.user else "Anonymous"
        return f"Progress for {username} on Question {self.question.id}"

