from django.db import models
from django.contrib.auth.models import User
from PIL import Image


class Profile(models.Model):
	user=models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
	image=models.ImageField(default='mountain.jpeg', upload_to='profile-pics', blank=True, null=True, verbose_name='Profile picture')
	user_bio-models.TextField(max_length=300,blank=True, null=True)
	venue_address=models.CharField(blank=True, null=True)
	venue_1=models.ImageField(default='', upload_to='venue-pics', blank=True, null=True, verbose_name='Pictures of venue')
	venue_2=models.ImageField(default='', upload_to='venue-pics', blank=True, null=True, verbose_name='Pictures of venue')
	venue_3=models.ImageField(default='', upload_to='venue-pics', blank=True, null=True, verbose_name='Pictures of venue')
	venue_4=models.ImageField(default='', upload_to='venue-pics', blank=True, null=True, verbose_name='Pictures of venue')
	


	def __str__(self):
		return f'{self.user.username}Profile'


	def save (self, *args, **kwargs):
		super().save(*args, **kwargs)


		img=Image.open(self.image.path)


		if img.height > 150 or img.width >150:
			output_size= (150,150)
			img.thumbnail(output_size)
			img.save(self.image.path)
	


