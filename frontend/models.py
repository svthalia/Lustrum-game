from django.db import models


class User(models.Model):
    name = models.CharField(max_length=200)
    profilePicture = models.CharField(max_length=200)

    def __str__(self):
        return 'User: {}'.format(self.name)


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')
    target = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, related_name='target')
    isDead = models.BooleanField(default=False)

    def __str__(self):
        return 'Player: {}'.format(self.user.name)


class Murder(models.Model):
    murderer = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='murderer')
    victim = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='victim')

    def __str__(self):
        return 'Murder: {}'.format(self.murderer.user.name + " X " + self.victim.user.name)
