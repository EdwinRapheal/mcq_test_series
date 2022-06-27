from django.urls import path

from . import views, test_view, student_view

urlpatterns = [
    path('', views.index, name='index'),
    path('create_question', views.QuestionView.as_view()),
    path('get_all_questions', views.QuestionView.as_view()),
    path('create_test', test_view.TestView.as_view()),
    path('get_all_tests/<int:teacher_id>/', test_view.TestView.as_view()),
    path('get_all_students', student_view.list_all_candidates),
    path('assign_test/<int:test_id>/<int:student_id>', student_view.assignCandidateTest),
    path('get_all_student_tests/<int:student_id>', student_view.get_all_student_tests),
    path('get_test/<int:test_id>', student_view.get_student_test),
    path('submit_test/<int:test_id>/<int:student_id>', student_view.submit_test)
]