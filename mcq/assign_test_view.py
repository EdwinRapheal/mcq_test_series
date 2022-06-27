import json
from pytz import utc
from datetime import datetime
from django.http import JsonResponse
from django.views import View
from mcq.models import *

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

class AssignTestView(View):
    def __init__(self):
        self.response = {"status": True}
        self.status_code = 200

    def create_error_response(self, error_string):
        self.response["status"] = False
        self.response["errString"] = error_string
        return self.response
