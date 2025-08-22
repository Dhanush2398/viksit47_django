from django.db import models

class Mock(models.Model):
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('difficult', 'Difficult'),
    ]

    title = models.CharField(max_length=255)  
    image = models.ImageField(upload_to="mock_tests/", blank=True, null=True)  
    time_limit = models.PositiveIntegerField(help_text="Time limit in minutes", default=30)  
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')  

    def __str__(self):
        return f"{self.title} - {self.get_difficulty_display()}"
    
class Question(models.Model):
    mock = models.ForeignKey(Mock, related_name="questions", on_delete=models.CASCADE,null=True, blank=True)
    text = models.CharField(max_length=255)
    image = models.ImageField(upload_to="mock_questions/", blank=True, null=True)

    def __str__(self):
        return self.text


class Option(models.Model):
    question = models.ForeignKey(Question, related_name="options", on_delete=models.CASCADE)
    text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.text} ({'Correct' if self.is_correct else 'Wrong'})"

