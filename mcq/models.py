from django.db import models
from datetime import datetime

class Teacher(models.Model):
    """
    Table created for teacher
    """
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=254, null=False)

    def get_json(self):
        return {
            "first_name": self.first_name, 
            "last_name": self.last_name,
            "email": self.email}
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}, email: {self.email}"

class Student(models.Model):
    """
    Table created for Student
    """
    first_name = models.CharField(max_length=100, null=False)
    last_name = models.CharField(max_length=100, null=True)
    email = models.EmailField(max_length=254, null=False)

    def get_json(self):
        return {
            "first_name": self.first_name, 
            "last_name": self.last_name,
            "email": self.email}

    def __str__(self):
        return f"{self.first_name} {self.last_name}, email: {self.email}"

class Question(models.Model):
    """
    Table for each MCQ Question
    """
    title = models.CharField(max_length=200, null=False)
    question_string = models.CharField(max_length=500, null=True)

class Choice(models.Model):
    """
    Table for each choice
    """
    question = models.ForeignKey('Question', on_delete=models.CASCADE)
    choice_string = models.CharField(max_length=500, null=False)
    is_answer = models.BooleanField(default=False)

class Test(models.Model):
    """
    Table for a test
    """
    title = models.CharField(max_length=50, null=False, default="sample test 1")
    questions = models.ManyToManyField('Question')

    # Duration will be saved in minutes
    duration = models.IntegerField(default=0, null=False)

    prescribed_time = models.DateTimeField(default=datetime.now, null=False)
    end_time = models.DateTimeField(default=datetime.now)
    create_time = models.DateTimeField(default=datetime.now, null=False)
    owner = models.ForeignKey('Teacher', on_delete=models.SET_NULL, null=True)

class Test_Assign(models.Model):
    """
    Table to store the details of each test assignment
    """
    student = models.ForeignKey('Student', on_delete=models.CASCADE)
    test = models.ForeignKey('Test', on_delete=models.CASCADE)
    score = models.FloatField(default=0.0, null=False)
    time_taken = models.IntegerField(default=0)
    