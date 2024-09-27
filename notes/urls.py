from django.urls import path

from .apis import (CreateNote, ViewNotes, PerformNote, CreateReminder, ViewReminders, PerformReminder,
            CreateGoal, ViewGoals, PerformGoal, PerformMonth, PerformMonthPhoto, SearchApi)

urlpatterns = [
    path('create_note', CreateNote.as_view()),
    path('view_notes', ViewNotes.as_view()),
    path('view_notes/<str:date>', ViewNotes.as_view()),
    path('perform_note/<int:id>', PerformNote.as_view()),
    path('create_reminder', CreateReminder.as_view()),
    path('view_reminders', ViewReminders.as_view()),
    path('view_reminders/<str:date>', ViewReminders.as_view()),
    path('perform_reminder/<int:id>', PerformReminder.as_view()),
    path('create_goal', CreateGoal.as_view()),
    path('view_goals', ViewGoals.as_view()),
    path('view_goals/<str:date>', ViewGoals.as_view()),
    path('perform_goal/<int:id>', PerformGoal.as_view()),
    path('perform_month/<str:date>', PerformMonth.as_view()),
    path('perform_month_photo/<str:date>', PerformMonthPhoto.as_view()),
    path('search/<str:search_param>', SearchApi.as_view()),
]