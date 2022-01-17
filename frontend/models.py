from django.conf import settings
from django.db import models


class User(models.Model):
    name = models.CharField(max_length=200)
    profilePicture = models.CharField(max_length=200)

    def __str__(self):
        return 'User: {}'.format(self.name)


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    target = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='target', null=True)
    is_dead = models.BooleanField(default=False)

    def __str__(self):
        return 'Player: {}'.format(self.user.name)

    def get_score(self):
        total = 0
        try:
            kills = Murder.objects.filter(murderer=self, agreed_on=True)
            total += kills.count()
        except Murder.DoesNotExist:
            pass

        try:
            kills = Murder.objects.filter(victim=self, agreed_on=True)
            total -= 2*kills.count()
        except Murder.DoesNotExist:
            pass

        return total

class Murder(models.Model):
    murderer = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='murderer')
    victim = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='victim')
    agreed_on = models.BooleanField(default=False)

    def __str__(self):
        return 'Murder: {}'.format(self.murderer.user.name + " X " + self.victim.user.name)