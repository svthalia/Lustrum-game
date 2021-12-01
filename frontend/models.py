from django.db import models


class User(models.Model):
    name = models.CharField(max_length=200)
    profilePicture = models.CharField(max_length=200)


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    target = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='target')
    isDead = models.BooleanField(default=False)


class Murder(models.Model):
    murderer = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='murderer')
    victim = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='victim')
