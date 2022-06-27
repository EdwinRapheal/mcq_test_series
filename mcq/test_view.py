import json
from pytz import utc
from datetime import datetime, timedelta
from django.http import JsonResponse
from django.views import View
from mcq.models import *
from mcq.views import QuestionView

class TestView(QuestionView):
    def __init__(self):
        self.response = {"status": True}
        self.status_code = 200
    
    def create_error_response(self, error_string):
        self.response["status"] = False
        self.response["errString"] = error_string
        return self.response

    def post(self, request):
        try:
            json_data = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            error_string = f"Error while fetching the payload is {e}"
            self.status_code = 400
            return JsonResponse(self.create_error_response(error_string), status=self.status_code)

        title = json_data.get("title", "")
        question_ids = json_data.get("questions", "")
        duration = json_data.get("duration", 0)
        prescribed_time_string = json_data.get("prescribed_time", "")
        owner_id = json_data.get("created_by", 0)

        try:
            date_format = '%m/%d/%Y %H:%M:%S'
            prescribed_time = datetime.strptime(prescribed_time_string, date_format)
            prescribed_time = utc.localize(prescribed_time)
        except ValueError:
            error_string = 'Incorrect data format, should be MM-DD-YYYY Hr:Min:Sex'
            self.status_code = 400
            return JsonResponse(self.create_error_response(error_string), status = self.status_code)
        
        test_end_time = prescribed_time + timedelta(minutes=60)

        test, duplicate = Test.objects.get_or_create(title = title)
        test.title = title
        test.duration = duration
        test.prescribed_time = prescribed_time
        test.end_time = test_end_time

        try:
            teacher = Teacher.objects.get(id = owner_id)
        except:
            teacher = None

        test.owner = teacher
        test.save()

        for question_id in question_ids:
            test.questions.add(Question.objects.get(id=question_id))
        
        self.response["message"] = "Test saved successfully"

        return JsonResponse(self.response, status = self.status_code)


    def create_test_response(self, test):
        test_resp = {}
        test_resp["title"] = test.title
        test_resp["duration"] = test.duration
        test_resp["prescribed_time"] = test.prescribed_time

        questions = test.questions.all()
        test_resp["questions"] = self.get_question_response(questions)

        return test_resp


    def get(self, request, teacher_id):
        tests = Test.objects.filter(owner__id = teacher_id)

        resp = {}
        for test in tests:
            resp[test.id] = self.create_test_response(test)

        return JsonResponse(resp, status=self.status_code)        
        
        