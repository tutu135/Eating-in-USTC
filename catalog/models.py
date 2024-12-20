from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings

# Create your models here.

class RESTAURANT(models.Model):
    resta_ID = models.AutoField(primary_key = True)
    resta_name = models.CharField(max_length = 20, unique = True)
    location_choice = (('W', 'West Campus'), ('E', 'East Campus'), ('O', 'Other places'),('J','Jinzhai Road'),('H','Huangshan Road'))
    location = models.CharField(max_length = 1, choices = location_choice, default = 'O')
    time_open = models.TimeField(blank = True, null = True)
    time_close = models.TimeField(blank = True, null = True)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL, models.SET_NULL, blank = True, null = True)
    tag_choice=(('S', 'Spicy'), ('SW', 'Sweet'), ('D', 'Drink'),('N','Noodles'),('F','Fast Food'),('1','Good drink'),('C','Coffee'))
    tag = models.CharField(max_length = 4,choices= tag_choice,default = '', blank = True, null = True)
    AVG_grade = models.FloatField(blank = True, null = True)
    more_Info = models.CharField(max_length = 200, blank = True, null = True)
    image = models.ImageField(upload_to='restaurants/', height_field=None, width_field=None, max_length=100, default = 'restaurants/404.png')
    isopen = models.BooleanField(default = True)

    def __str__(self):
        return f'{self.resta_name}'
    
    def get_absolute_url(self):
        """
        Returns the url to access a particular restaurant instance.
        """
        return reverse('restaurant-detail', args=[str(self.resta_ID)])
    


class DISH(models.Model):
    dish_ID = models.AutoField(primary_key = True)
    resta_ID = models.ForeignKey(RESTAURANT, models.CASCADE)
    dish_name = models.CharField(max_length = 20)
    tag_choice=(('S', 'Spicy'), ('SW', 'Sweet'), ('D', 'Drink'),('N','Noodles'),('F','Fast Food'),('1','Good drink'))
    tag = models.CharField(max_length = 4,choices= tag_choice, default = '', blank = True, null = True)
    price = models.FloatField(blank = True, null = True)
    image = models.ImageField(upload_to='dishes/', height_field=None, width_field=None, max_length=100, default = 'dishes/404.png')
    onsale = models.BooleanField(default = True)
    more_Info = models.CharField(max_length = 200, blank = True, null = True)

    class Meta:
        # 在多个字段上设置复合的唯一约束
        constraints = [
            models.UniqueConstraint(fields=['resta_ID', 'dish_name'], name='unique_dish')
        ]
    
    def __str__(self):
        return f'{self.resta_ID}-{self.dish_name}'
    
    def get_absolute_url(self):
        """
        Returns the url to access a particular dish instance.
        """
        return reverse('dish-detail', args=[str(self.dish_ID)])
    


class COMMENT(models.Model):
    comm_ID = models.AutoField(primary_key = True)
    user_ID = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    resta_ID = models.ForeignKey(RESTAURANT, models.CASCADE)
    dish_ID = models.ForeignKey(DISH, models.CASCADE, blank = True, null = True)
    grade = models.FloatField()
    content = models.CharField(max_length = 200)
    
    def __str__(self):
        return f'{self.comm_ID}'
    


class REPLY(models.Model):
    reply_ID = models.AutoField(primary_key = True)
    user_ID = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    comm_ID = models.ForeignKey(COMMENT, related_name = 'replies', on_delete = models.CASCADE)
    content = models.CharField(max_length = 200)
    
    def __str__(self):
        return f'{self.reply_ID}'
    


class DELETE_RESTA(models.Model):
    delete_ID = models.AutoField(primary_key = True)
    resta_ID = models.ForeignKey(RESTAURANT, models.CASCADE)
    evidence = models.ImageField(upload_to='evidences/delete/', height_field=None, width_field=None, max_length=100)
    
    def __str__(self):
        return f'{self.delete_ID}-{self.resta_ID}'
    


class MANAGER_REG(models.Model):
    reg_ID = models.AutoField(primary_key = True)
    user_ID = models.ForeignKey(settings.AUTH_USER_MODEL, models.CASCADE)
    resta_ID = models.ForeignKey(RESTAURANT, models.CASCADE)
    evidence = models.ImageField(upload_to='evidences/restaurants/', height_field=None, width_field=None, max_length=100)
    
    def __str__(self):
        return f'{self.reg_ID}-{self.user_ID}-{self.resta_ID}'
    
    class Meta:
        # 在多个字段上设置复合的唯一约束
        constraints = [
            models.UniqueConstraint(fields=['resta_ID', 'user_ID'], name='his_restaurant')
        ]
