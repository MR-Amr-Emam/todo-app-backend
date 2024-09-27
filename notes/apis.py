from django.http import HttpResponse
from django.views import View
from django.core.files import File
from django.conf import settings
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, BasePermission, SAFE_METHODS
from rest_framework.response import Response
from .models import Notes, Reminders, Goals, Month
from .serializers import (CreateNoteSerializer, NoteSerializer, CreateReminderSerializer,
        CreateGoalSerializer, GoalSerializer, PerformGoalSerializer, ReminderSerializer, MonthSerializer)

from os.path import join
import json, datetime
from io import BytesIO


# custom permissions

class IsAuthorized(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            pass
        elif request.user == obj.user:
            pass
        else:
            return False
        return True

class CanPerform(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            pass
        elif not obj.state:
            pass
        else:
            return False
        return True
        
#apis


class CreateNote(generics.CreateAPIView):
    queryset = Notes.objects.all()
    serializer_class = CreateNoteSerializer
    permission_classes = [IsAuthenticated]
   
    def perform_create(self, instance):
        return instance.create(instance.validated_data, user=self.request.user)


    

class ViewNotes(generics.ListAPIView):
    queryset = Notes.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.kwargs.get("date"):
            date = datetime.datetime.strptime(self.kwargs["date"], "%Y-%m-%d").date()
            try:
                return (Month.objects.get(month=date.replace(day=1), user=self.request.user)
                        .day_set.get(day=date.day).notes_set.all())
            except:
                return []
        return self.queryset.filter(user=self.request.user)


class PerformNote(generics.RetrieveUpdateDestroyAPIView):
    queryset = Notes.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [IsAuthenticated, IsAuthorized, CanPerform]
    lookup_field = "id"



class CreateReminder(generics.CreateAPIView):
    queryset = Reminders.objects.all()
    serializer_class = CreateReminderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.create(serializer.validated_data, user=self.request.user)


class ViewReminders(generics.ListAPIView):
    queryset = Reminders.objects.all()
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.kwargs.get("date"):
            date = datetime.datetime.strptime(self.kwargs["date"], "%Y-%m-%d").date()
            try:
                return (Month.objects.get(month=date.replace(day=1), user=self.request.user)
                        .day_set.get(day=date.day).reminders_set.all())
            except:
                return []
        return self.queryset.filter(user=self.request.user)

class PerformReminder(generics.RetrieveUpdateDestroyAPIView):
    queryset = Reminders.objects.all()
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated, IsAuthorized, CanPerform]
    lookup_field = "id"


class CreateGoal(generics.CreateAPIView):
    queryset = Goals.objects.all()
    serializer_class = CreateGoalSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, instance):
        instance.create(instance.validated_data, user=self.request.user)

class ViewGoals(generics.ListAPIView):
    queryset = Goals.objects.all()
    serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.kwargs.get("date"):
            date = datetime.datetime.strptime(self.kwargs["date"], "%Y-%m-%d").date()
            try:
                return (Month.objects.get(month=date.replace(day=1), user=self.request.user)
                        .goals_set.all())
            except:
                return []
        return self.queryset.filter(user=self.request.user)


class PerformGoal(generics.RetrieveUpdateDestroyAPIView):
    queryset = Goals.objects.all()
    serializer_class = PerformGoalSerializer
    view_serializer_class = GoalSerializer
    permission_classes = [IsAuthenticated, IsAuthorized, CanPerform]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return self.view_serializer_class
        else:
            return self.serializer_class

    def put(self, request, id):
        serializer = self.serializer_class(data=json.loads(request.body))
        self.request = request
        self.kwargs = {"id":id}
        serializer.is_valid(raise_exception=True)
        serializer.instance = self.get_object()
        self.perform_update(serializer)
        return Response()
    
class PerformMonth(generics.RetrieveUpdateDestroyAPIView):
    queryset = Month.objects.all()
    serializer_class = MonthSerializer
    permission_classes = [IsAuthenticated, IsAuthorized, CanPerform]

    def get_object(self):
        params = self.kwargs["date"].split("-")
        date = datetime.date(year=int(params[0]), month=int(params[1]), day=1)
        return Month.objects.get(user=self.request.user, month=date)


class PerformMonthPhoto(View):
    def get_object(self, request, date):
        date = datetime.date(int(date.split("-")[0]), int(date.split("-")[1]), 1)
        month = Month.objects.filter(month=date, user=request.user)
        if((not month) and self.request.method=="POST"):
            month = Month.objects.create(month=date, user=request.user)
        else:
            month = month[0]
        return month

    def get(self, request, date):
        month = self.get_object(request, date)
        if(not month):
            with open("media/default/month-image", "rb") as image:
                image = image.read()
                response_image = HttpResponse(content=image, content_type="image/jpg")
                return response_image
        else:
            image = month.month_photo
            with open(image.path, "rb") as image:
                image = image.read()
                response_image = HttpResponse(content=image, content_type="image/jpg")
                return response_image
    
    def post(self, request, date):
        if(not request.user.is_authenticated):
            return HttpResponse(b"{'error':'not authorized'}", content_type="application/json", status=401)
        image = BytesIO()
        image.write(request.body)
        image.name = "month_image"
        image = File(image)
        month = self.get_object(request, date)
        if month.month_photo.path != join(settings.BASE_DIR, "media\default\month-image.png"):
            month.month_photo.delete()
        month.month_photo = image
        month.save()
        return HttpResponse(content=b'{"message":"ok"}', content_type="application/json")


class SearchApi(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, search_param):
        search_result = get_search(request, search_param)
        return Response(search_result)


def get_search(request, search_param):
    search_param = search_param.lower()
    search_result = []
    result_length = 7
    for note in Notes.objects.filter(user=request.user):
        if(search_param in note.title.lower()):
            search_result.append({"date":note.date_planned.strftime("%Y-%m-%d"), "type":"note", "content":note.title})
            if len(search_result) >= result_length:
                return search_result
        if(search_param in note.content):
            search_result.append({"date":note.date_planned.strftime("%Y-%m-%d"), "type":"note", "content":note.content})
            if len(search_result) >= result_length:
                return search_result
    for reminder in Reminders.objects.filter(user=request.user):
        if(search_param in reminder.content.lower()):
            search_result.append({"date":reminder.date_planned.strftime("%Y-%m-%d"), "type":"reminder", "content":reminder.content})
            if len(search_result) >= result_length:
                return search_result
    
    for goal in Goals.objects.filter(user=request.user):
        if(search_param in goal.title.lower()):
            search_result.append({"date":goal.date_planned.strftime("%Y-%m-%d"), "type":"goal", "content":goal.title})
            if len(search_result) >= result_length:
                return search_result
            for minigoal in goal.miniGoals.split("###"):
                if search_param in minigoal.lower():
                    search_result.append({"date":goal.date_planned.strftime("%Y-%m-%d"), "type":"goal", "content":minigoal})
                    if len(search_result) >= result_length:
                        return search_result
    return search_result
