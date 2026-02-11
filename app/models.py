from tortoise import fields
from tortoise.models import Model

from app.managers import TournamentManager


class Tournament(Model):
    objects = TournamentManager()

    id = fields.IntField(primary_key=True)
    name = fields.TextField()
    created = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Event(Model):
    id = fields.IntField(primary_key=True)
    name = fields.TextField()
    tournament = fields.ForeignKeyField("models.Tournament", related_name="events")
    participants = fields.ManyToManyField(
        "models.Team", related_name="events", through="event_team"
    )
    modified = fields.DatetimeField(auto_now=True)
    prize = fields.DecimalField(max_digits=10, decimal_places=2, null=True)

    def __str__(self):
        return self.name


class Team(Model):
    id = fields.IntField(primary_key=True)
    name = fields.TextField()

    def __str__(self):
        return self.name
