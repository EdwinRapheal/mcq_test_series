import json
from this import d
from pytz import utc
from datetime import timedelta
from django.http import JsonResponse
from django.views import View
from mcq.models import *
from mcq.test_view import TestView

class AssignTestView(View):
    def __init__(self):
        self.response = {"status": True}
        self.status_code = 200

    def create_error_response(self, error_string):
        self.response["status"] = False
        self.response["errString"] = error_string
        return self.response


def list_all_candidates(request):
    students = Student.objects.all()
    student_list = []
    for student in students:
        student_list.append(student.get_json())
    
    resp = {"data": student_list, "status": True}
    
    return JsonResponse(resp, status = 200)


def assignCandidateTest(request, test_id, student_id):
    """
    Function to assign a test to a candidate
    """
    try:
        student = Student.objects.get(id=student_id)
    except:
        error_string = "Candidate does not exists with given candidate_id"
        return JsonResponse(AssignTestView().create_error_response(error_string), status=400)
    
    try:
        test = Test.objects.get(id=test_id)
    except:
        error_string = "Test does not exists with given test_id"
        return JsonResponse(AssignTestView().create_error_response(error_string), status=400)

    test_assign, not_created = Test_Assign.objects.get_or_create(student_id = student_id, test_id = test_id)

    if not not_created:
        error_string = "This test has already been assigned to this candidate"
        return JsonResponse(AssignTestView().create_error_response(error_string), status=400)

    message = "Test has succesfully assigned to the candidate"
    resp = {"status": True, "message": message}

    return JsonResponse(resp, status=200)


def get_all_student_tests(request, student_id):
    tests_assign = Test.objects.filter(id__in = Test_Assign.objects.filter(student__id = student_id).values("test_id"))

    tests_list = []
    for test in tests_assign:
        test_dict = {}
        test_dict["id"] = test.id
        test_dict["title"] = test.title
        test_dict["duration"] = test.duration
        test_dict["prescribed_time"] = test.prescribed_time
        tests_list.append(test_dict)
    
    resp = {"data": tests_list, "status": True}

    return JsonResponse(resp, status=200)

def get_student_test(request, test_id):
    import datetime
    try:
        test = Test.objects.get(id=test_id)
    except:
        error_string = "Test does not exists with given id"
        return JsonResponse(AssignTestView().create_error_response(error_string), status=400)
    
    if datetime.datetime.now(datetime.timezone.utc)+timedelta(hours=5.5) >= test.prescribed_time and\
         datetime.datetime.now(datetime.timezone.utc)+timedelta(hours=5.5) <= test.end_time:
        data = TestView().create_test_response(test)
        resp = {"data": data, "status": True}
        return JsonResponse(resp, status = 200)
    else:
        error_string = "Test cannot be opened before prescribed time"
        return JsonResponse(AssignTestView().create_error_response(error_string), status=400)


def calculate_test_score(test_result, question_ids):
    correct_answers, wrong_answers = 0,0
    for question in test_result:
        if question in question_ids:
            if test_result[question]:
                correct_answers += 1
            else:
                wrong_answers += 1
        else:
            return "Invalid Questions"
    
    score = float(correct_answers - wrong_answers/2)

    return score

def submit_test(request, test_id, student_id):
    import datetime
    try:
        json_data = json.loads(request.body.decode("utf-8"))
    except Exception as e:
        error_string = f"Error while fetching the payload is {e}"
        return JsonResponse(AssignTestView().create_error_response(error_string), status=400)

    try:
        test = Test.objects.get(id=test_id)
    except:
        error_string = "Test does not exist with this id"
        return JsonResponse(AssignTestView().create_error_response(error_string), status=400)
    
    if datetime.datetime.now(datetime.timezone.utc) > test.end_time:
        error_string = "You have exceeded the time limit for the test"
        return JsonResponse(AssignTestView().create_error_response(error_string), status=400)
    
    try:
        test_assign = Test_Assign.objects.get(test__id = test_id, student__id = student_id)
    except:
        error_string = "This test is not assigned to this student"
        return JsonResponse(AssignTestView().create_error_response(error_string), status=400)
        
    question_ids = [str(question["id"]) for question in test.questions.all().values("id")]

    student_test_score = calculate_test_score(json_data.get("test_result", {}), question_ids)

    if student_test_score == "Invalid Questions":
        error_string = "The question ids are not matching with the test assigned"
        return JsonResponse(AssignTestView().create_error_response(error_string), status=400)

    test_time_taken = json_data.get("duration", 0)

    test_assign.score = student_test_score
    test_assign.time_taken = test_time_taken

    test_assign.save()

    resp = {"message": "Test submitted successfully", "status": True}

    return JsonResponse(resp, status = 200)

