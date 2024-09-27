from rest_framework.exceptions import NotAcceptable

from django.db import models
from django.utils import timezone
import pytz, datetime, calendar

def check_state(self):
    timezone = pytz.timezone(self.user.timezone)
    date_now = datetime.datetime.now(timezone)
    if((not self.state) and date_now.date()>self.date_planned):
        self.state = True
        self.save()
        if not self.day.state:
            self.day.state=True
            self.day.save()
    elif(not getattr(self, "dead_line", False) or date_now.date()!=self.date_planned):
        pass
    else:
        dead_line = datetime.datetime(year=date_now.year, month=date_now.month, day=date_now.day,
            hour=self.dead_line.hour, minute=self.dead_line.minute, tzinfo=timezone)
        if(date_now>dead_line):
            self.state=True
            self.save()

def check_month_state(self):
    if((not self.state) and datetime.datetime.now(datetime.timezone.utc).date().replace(day=1)>self.date_planned):
        self.state = True
        self.save()
        if not self.month.state:
            self.month.state=True
            self.month.save()


class Objects(models.Manager):
    def create(self, *args, **kwargs):
        if datetime.date.today() > kwargs["date_planned"]:
            raise NotAcceptable()
        month, bool = Month.objects.get_or_create(month=kwargs["date_planned"].replace(day=1), user=kwargs["user"])
        day, bool = Day.objects.get_or_create(month=month, user=kwargs["user"], day=kwargs["date_planned"].day)
        return super().create(*args, **kwargs, day=day)
    

class GoalObjects(models.Manager):
    def create(self, *args, **kwargs):
        kwargs["date_planned"]=kwargs["date_planned"].replace(day=1)
        if datetime.date.today().replace(day=1) > kwargs["date_planned"]:
            raise NotAcceptable()
        month, bool = Month.objects.get_or_create(month=kwargs["date_planned"], user=kwargs["user"])
        return super().create(*args, **kwargs, month=month)



class Notes(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        check_state(self)
    title = models.CharField(max_length=150, null=False)
    content = models.TextField(null=False)
    date = models.DateTimeField(default=timezone.now)
    state = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    category = models.CharField(max_length=150, null=False, choices=[("SD","self_development"), ("SL","social_life"), ("LS","life_style")])
    theme = models.IntegerField(null=False, choices=[(1,1), (2,2), (3,3), (4,4)])
    edited = models.BooleanField(default=False)
    date_planned = models.DateField()
    day = models.ForeignKey("notes.Day", on_delete=models.CASCADE)
    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE)
    objects = Objects()


class Reminders(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        check_state(self)
        if not self.state:
            pass
        
    content = models.TextField(null=False)
    date = models.DateTimeField(default=timezone.now)
    dead_line = models.TimeField(null=False)
    state = models.BooleanField(default=False)
    date_planned = models.DateField()
    day = models.ForeignKey("notes.Day", on_delete=models.CASCADE)
    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE)
    objects = Objects()



class Goals(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        check_month_state(self)
    title = models.CharField(max_length=150)
    miniGoals = models.TextField()
    miniGoalsNum = models.IntegerField()
    miniGoalsState = models.IntegerField(default = 0)
    date = models.DateTimeField(default=timezone.now)
    theme = models.IntegerField(null=False, choices=[(1,1), (2,2), (3,3), (4,4)])
    state = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    date_planned = models.DateField()
    month = models.ForeignKey("notes.Month", on_delete=models.CASCADE)
    user = models.ForeignKey("authentication.User", on_delete=models.CASCADE)
    objects = GoalObjects()

    
    def set_miniGoals(self, miniGoals):
        miniGoals_str = self.miniGoals
        for miniGoal in miniGoals:
            miniGoals_str += miniGoal + "###"
        self.miniGoals = miniGoals_str
    
    def get_miniGoals(self):
        return self.miniGoals.split("###")


class Day(models.Model):
    day = models.IntegerField()
    month = models.ForeignKey("notes.Month", on_delete=models.CASCADE)
    num_notes = models.IntegerField(default=0)
    num_notes_completed = models.IntegerField(default=0)
    state = models.BooleanField(default=False)
    user = models.ForeignKey("authentication.user", on_delete=models.CASCADE)

def month_image_storage(month, file_name):
    return f"{month.user.username}/month-images/{month.month.year}-{month.month.month}.jpg"

class Month(models.Model):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not len(args):
            self.days_progress = self.set_initial_progress()
    month = models.DateField()
    days_progress = models.TextField()
    num_notes = models.IntegerField(default=0)
    num_notes_completed = models.IntegerField(default=0)
    bio = models.CharField(blank=True, default="", max_length=150)
    state = models.BooleanField(default=False)
    month_photo = models.ImageField(upload_to=month_image_storage, default="default/month-image.png")
    user = models.ForeignKey("authentication.user", on_delete=models.CASCADE)

    def set_initial_progress(self):
        progress = ""
        for day in range(1, calendar.monthrange(year=self.month.year, month=self.month.month)[1]):
            progress += "0#"
        progress += "0"
        return progress
