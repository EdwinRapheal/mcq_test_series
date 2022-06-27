import json
from django.http import HttpResponse, JsonResponse
from django.views import View
from mcq.models import *

def index(request):
    return HttpResponse("Hello world, The API is working")

class QuestionView(View):
    def __init__(self):
        self.response = {"status": True}
        self.status_code = 200

    def create_error_response(self, error_string):
        self.response["status"] = False
        self.response["errString"] = error_string
        return self.response


    def create_choice(self, question, choice_string, is_answer):
        choice = Choice()
        choice.question = question
        choice.choice_string = choice_string
        choice.is_answer = is_answer
        choice.save()

        return choice

    def post(self, request):
        try:
            json_data = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            error_string = f"Error while fetching the payload is {e}"
            self.status_code = 400
            return JsonResponse(self.create_error_response(error_string), status=self.status_code)
        
        question_title = json_data.get("title")
        question_text = json_data.get("question_string")
        choices = json_data.get("choices")

        question, created = Question.objects.get_or_create(title = question_title)

        if not created:
            error_string = "A question with same title already exists"
            self.status_code = 400
            return JsonResponse(self.create_error_response(error_string), status=self.status_code)
        
        question.question_string = question_text
        question.save()

        for choice in choices:
            self.create_choice(question, choices[choice][0], choices[choice][1])
        
        self.response["message"] = "Question Successfully saved"

        return JsonResponse(self.response, status=self.status_code)
    
    
    def create_choice_response(self):
        all_choices = Choice.objects.values().order_by('question_id')

        choice_dict = {}
        for choice in all_choices:
            if choice["question_id"] in choice_dict:
                choice_dict[choice["question_id"]].append(choice)
            else:
                choice_dict[choice["question_id"]] = [choice]
        
        return choice_dict

    
    def get_question_response(self, questions):
        choice_dict = self.create_choice_response()
        question_list = []
        for question in questions:
            each_question = {}
            each_question["id"] = question.id
            each_question["title"] = question.title
            each_question["description"] = question.question_string
            each_question["choices"] = choice_dict[question.id]
            question_list.append(each_question)
                
        question_resp = {"questions": question_list}

        return question_resp

    def get(self, request):
        questions = Question.objects.all()
        
        question_resp = self.get_question_response(questions)
        
        resp = {"questions": question_resp}
        
        return JsonResponse(resp, status=self.status_code)
