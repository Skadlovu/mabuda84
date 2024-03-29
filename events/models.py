from django.db import models
from django.urls import reverse
from profiles.models import Profile
from PIL import Image
from.create_landscape import create_landscape
from.create_portrait import create_portrait
from taggit.managers import TaggableManager
from schedule.models import Event as SchedulerEvent
from django.utils import timezone
from django.contrib.auth.models import User
from datetime import datetime
import datetime as time
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.text import slugify



class Comment(models.Model):
    event=models.ForeignKey('Event',on_delete=models.CASCADE,null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.event.title}'

    class Meta:
        ordering = ['-created_at']





class Category(models.Model):
    name=models.CharField( max_length=100,unique=True)
    description=models.TextField(max_length=100, default='events')
    slug=models.SlugField(default='',null=False)
    number_of_events=models.IntegerField(blank=True,default=0,null=True)
    status=models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    
    def get_absolute_url(self):
        return reverse('category',kwargs={'slug':self.slug})
    

    def update_number_of_events(self):
        # Calculate the number of events for the current category
        events_count = self.event_set.count()

        # Update the number_of_events field
        self.number_of_events = events_count
        self.save()

        # Return the updated number of events
        return events_count
    


class City(models.Model):
    name=models.CharField( max_length=100, unique=True)
    description=models.TextField(max_length=100, default='city')
    slug=models.SlugField(default='',null=False)
    number_of_events=models.IntegerField(blank=True,default=0, null=True)
    status=models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('city',kwargs={'slug':self.slug})
    
    def update_number_of_events(self):
        # Calculate the number of events for the current city
        events_count = self.event_set.count()

        # Update the number_of_events field
        self.number_of_events = events_count
        self.save()

        # Return the updated number of events
        return events_count

    

class Event(models.Model):
    title=models.CharField(max_length=100, unique=True)
    category=models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name='Category', null=True)
    uploaded_by=models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='User')
    thumb=models.ImageField(upload_to='thumbs', verbose_name='Event poster')
    portrait=models.ImageField(upload_to='potrait', blank=True, null=True)
    landscape=models.ImageField(upload_to='landscape', blank=True, null=True)
    description=models.TextField(max_length=600)
    upload_date=models.DateTimeField(auto_now_add=True)
    views=models.PositiveBigIntegerField(blank=True, default=0)
    event_date=models.DateField()
    event_time=models.TimeField()
    entry_fee=models.FloatField(blank=False, null=False, default=0)
    event_venue=models.CharField(max_length=100,)
    city=models.ForeignKey(City, on_delete=models.CASCADE, verbose_name='City',null=True)
    likes=models.ManyToManyField(User, related_name='event_likes', blank=True)
    slug=models.SlugField(default='',null=False, max_length=100)
    status=models.BooleanField(default=False)
    id=models.AutoField(primary_key=True)
    tags=TaggableManager()
    attending = models.ManyToManyField(User, related_name='events_attending', blank=True)
    comments = models.OneToOneField(Comment, on_delete=models.CASCADE, related_name='event_comments', blank=True, null=True)
    end_time = models.DateTimeField(null=True,blank=True)


    def create_scheduler_event(self):
        # Create a corresponding SchedulerEvent
        event_datetime = datetime.combine(self.event_date, self.event_time)
        # Make the datetime object timezone aware
        event_datetime_aware = timezone.make_aware(event_datetime)

        scheduler_event = SchedulerEvent(
            title=self.title,
            description=self.description,
            start=event_datetime_aware,
            end=self.end_time,
            # Add other fields as needed
        )
        scheduler_event.save()
        return scheduler_event


    def save(self, *args, **kwargs):
        created = not self.pk  # True if the instance is being created
        super().save(*args, **kwargs)

        # Create portrait only when the instance is being created
        if created:
            create_portrait(self)
            create_landscape(self)

        

    def number_of_likes(self):
        return self.likes.count


    def get_related_events(self):
        related_by_category=Event.objects.filter(category=self.category).exclude(id=self.id)
        related_by_uploaded_by=Event.objects.filter(uploaded_by=self.uploaded_by).exclude(id=self.id)
        related_by_address=Event.objects.filter(event_venue=self.event_venue).exclude(id=self.id)
        related_by_city=Event.objects.filter(city=self.city).exclude(id=self.id)

        related_events=(related_by_category|related_by_uploaded_by|related_by_address |related_by_city)

        return related_events
    

    def __str__(self):
        return self.title
    

    def get_absolute_url(self):
        return reverse ('event',kwargs={'slug':self.slug})
    

    
    class Meta:
        ordering=['upload_date']



class ReviewComment(models.Model):
    event_review=models.ForeignKey('Review',on_delete=models.CASCADE,null=True,blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} - {self.event_review}'

    class Meta:
        ordering = ['-created_at']

class ReviewRating(models.Model):
      event_review=models.ForeignKey('Review',on_delete=models.CASCADE,null=True,blank=True )
      user = models.ForeignKey(User, on_delete=models.CASCADE)
      rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])





class Review(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, verbose_name='Event')
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='User')
    user_comments = models.OneToOneField(ReviewComment,blank=True, null=True ,on_delete=models.CASCADE)
    user_ratings=models.OneToOneField(ReviewRating,on_delete=models.CASCADE, blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(default='',unique=True, null=False, blank=True)
    id=models.AutoField(primary_key=True)

    def __str__(self):
        return f'{self.user.username} - {self.event.title}'
    
    def get_absolute_url(self):
        return reverse ('review',kwargs={'slug':self.slug})
    
    class Meta:
        ordering=['created_at']
