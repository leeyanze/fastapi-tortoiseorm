from decimal import Decimal

from tortoise.manager import Manager


class TournamentManager(Manager):
    def with_prize_gt(
        self, threshold: Decimal = Decimal("2E+3")
    ):
        return self.get_queryset().filter(events__prize__gt=threshold).distinct()
