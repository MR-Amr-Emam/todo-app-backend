from rest_framework import serializers
from rest_framework.exceptions import PermissionDenied, NotAcceptable
from django.conf import settings
from .models import Notes, Reminders, Goals, Month

import datetime, math

class CreateNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ["id", "title", "content", "category", "theme", "date_planned"]

    def create(self, validated_data, **kwargs):
        note = Notes.objects.create(**validated_data, **kwargs)
        note.day.num_notes += 1
        note.day.save()
        progress = note.day.month.days_progress.split("#")
        progress[note.day.day-1] = str(math.floor(note.day.num_notes_completed/note.day.num_notes * 100))
        note.day.month.days_progress = "#".join(progress)
        note.day.month.num_notes += 1
        note.day.month.save()
        self.instance = note
        return note
      


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = ["id", "state", "done", "theme", "title", "content", "edited"]
        read_only_fields = ["id", "date", "theme", "user", "day", "state"]
        extra_kwargs = {"title":{"required":False}, "content":{"required":False},
                        "state":{"required":False}, "done":{"required":False}}
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["category"]=instance.get_category_display()
        return data

    def update(self, instance, validated_data):
        if (instance.state):
            raise PermissionDenied()
        else:
            note = super().update(instance, validated_data)
            if(validated_data.get("done")):
                note.state = True
                note.save()
                note.day.num_notes_completed += 1
                note.day.save()
                note.day.month.num_notes_completed += 1
                progress = note.day.month.days_progress.split("#")
                progress[note.day.day-1] = str(math.floor(note.day.num_notes_completed/note.day.num_notes * 100))
                note.day.month.days_progress = "#".join(progress)
                note.day.month.save()
            return note
            

    
class CreateReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminders
        fields = ["id", "content", "dead_line", "date_planned"]

    def create(self, validated_data, **kwargs):
        if(datetime.datetime.now().time() > validated_data["dead_line"]):
            raise NotAcceptable()
        reminder = Reminders.objects.create(**validated_data, **kwargs)
        self.instance = reminder
        return reminder


class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminders
        fields = ["id", "content", "dead_line", "state"]
        read_only_fields = ["content", "dead_line", "id"]




class CreateGoalSerializer(serializers.ModelSerializer):
    def __init__(self, instance=None, data=..., **kwargs):
        super().__init__(instance, data, **kwargs)
        self.initial_data = {"title":data["title"], "miniGoals": "###".join(data["miniGoals"]), "theme":data["theme"], "date_planned":data["date_planned"]}
    class Meta:
        model = Goals
        fields = ["id", "title", "miniGoals", "theme", "date_planned"]
    def create(self, validated_data, **kwargs):
        goal = Goals.objects.create(**validated_data, **kwargs, miniGoalsNum=len(validated_data["miniGoals"].split("###")))
        self.instance = goal
        return goal


class GoalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Goals
        exclude = ["user"]
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["miniGoals"] = data["miniGoals"].split("###")
        return data

class PerformGoalSerializer(serializers.Serializer):
    set_miniGoal = serializers.IntegerField(required=False, write_only=True)
    miniGoal = serializers.CharField(required=False, write_only=True)
    def save(self):
        if self.validated_data.get("miniGoal"):
            self.instance.miniGoals += "###" + self.validated_data["miniGoal"]
            self.instance.miniGoalsNum += 1
        
        if (self.validated_data.get("set_miniGoal") and self.validated_data["set_miniGoal"]<=self.instance.miniGoalsNum and
        self.validated_data["set_miniGoal"]>0):
            self.instance.miniGoalsState = self.instance.miniGoalsState | 1<<(self.validated_data["set_miniGoal"]-1)
            if(self.instance.miniGoalsState == 2**self.instance.miniGoalsNum - 1):
                self.instance.state = True
                self.instance.done = True
        self.instance.save()

class MonthSerializer(serializers.ModelSerializer):
    class Meta:
        model=Month
        exclude = ["id", "user"]
        read_only_fields = ["month", "days_progress", "num_notes", "num_notes_completed", "state"]
        extra_kwargs = {"bio":{"required":False}, "month_photo":{"required":False}}
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        response_data = data
        response_data["days_progress"] = data["days_progress"].split("#")
        response_data["month_photo"] = f"{settings.DOMAIN_ORIGIN}/notes/perform_month_photo/{instance.month.year}-{instance.month.month}"
        return response_data