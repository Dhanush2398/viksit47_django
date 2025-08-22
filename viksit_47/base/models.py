from django.db import models

class Question(models.Model):
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

