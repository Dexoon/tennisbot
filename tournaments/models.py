from django.contrib.auth.models import AbstractUser
from django.db import models

nb = dict(null=True, blank=True)


class User(AbstractUser):
    telegram_id = models.PositiveBigIntegerField(verbose_name="id телеграм", **nb)


class TennisPlayer(models.Model):
    name = models.CharField(max_length=128, verbose_name="Имя теннисиста")

    def __str__(self):
        return self.name


class Tournament(models.Model):
    class STATUS:
        DRAFT = "dr"
        FORECAST = "fc"
        ONGOING = "og"
        FINISHED = "fd"
        ARCHIVE = "ar"
        CHOICES = (
            (DRAFT, "черновик"),
            (FORECAST, "сбор прогнозов"),
            (ONGOING, "идёт"),
            (FINISHED, "закончен"),
            (ARCHIVE, "архив"),
        )

    name = models.CharField(max_length=128, verbose_name="Название турнира")
    round = models.PositiveSmallIntegerField(verbose_name="количество раундов")
    status = models.CharField(
        max_length=2,
        verbose_name="статус",
        choices=STATUS.CHOICES,
        default=STATUS.DRAFT,
    )

    def add_participants(self, *players) -> bool:
        if self.match_set.count() > 0 or len(players) != 1 << self.round:
            return False
        participants = []
        stages: list[list[Match]] = [[]]
        for player in players:
            player, _ = TennisPlayer.objects.get_or_create(name=player)
            participants += [self.participant_set.create(tennis_player=player)]
        chunk_gen = lambda arr: [arr[i : i + 2] for i in range(0, len(arr), 2)]
        for (p1, p2) in chunk_gen(participants):
            stages[0] += [
                self.match_set.create(participant_one=p1, participant_two=p2, round=0)
            ]
        for i in range(1, self.round):
            stage = []
            for (m1, m2) in chunk_gen(stages[i - 1]):
                stage += [
                    self.match_set.create(
                        preceding_match_one=m1, preceding_match_two=m2, round=i
                    )
                ]
            stages += [stage]
        return True

    def __str__(self):
        return self.name

    def json(self):
        return dict(
            id=self.id,
            status=self.status,
            name=self.name,
            round=self.round,
            matches=[
                match.json() for match in self.match_set.all().order_by("round", "id")
            ],
            participants={
                participant.id: str(participant.tennis_player)
                for participant in self.participant_set.all()
            },
        )


class Participant(models.Model):
    tennis_player = models.ForeignKey(TennisPlayer, on_delete=models.CASCADE)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.tournament}: {self.tennis_player}"

    def json(self):
        return dict(id=self.id, name=str(self.tennis_player))


class Match(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    round = models.PositiveSmallIntegerField(verbose_name="номер раунда")
    participant_one = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        verbose_name="первый участник",
        **nb,
        related_name="+",
    )
    participant_two = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        verbose_name="второй участник",
        **nb,
        related_name="+",
    )
    preceding_match_one = models.OneToOneField(
        "self",
        on_delete=models.CASCADE,
        verbose_name="второй участник",
        **nb,
        related_name="succeeding_match_1",
    )
    preceding_match_two = models.OneToOneField(
        "self",
        on_delete=models.CASCADE,
        verbose_name="второй участник",
        **nb,
        related_name="succeeding_match_2",
    )

    def succeeding_match(self):
        return self.succeeding_match_1 or self.succeeding_match_2

    def json(self):
        result = dict(id=self.id, round=self.round)
        if self.participant_one:
            result["participant_one_id"] = self.participant_one.id
        if self.participant_two:
            result["participant_two_id"] = self.participant_two_id
        if self.preceding_match_one:
            result["preceding_match_one_id"] = self.preceding_match_one.id
        if self.preceding_match_two:
            result["preceding_match_two_id"] = self.preceding_match_two.id
        return result

    def __str__(self):
        p1 = (
            str(self.participant_one.tennis_player)
            if self.participant_one
            else self.preceding_match_one.id
        )
        p2 = (
            str(self.participant_two.tennis_player)
            if self.participant_two
            else self.preceding_match_two.id
        )
        return f"{self.id}: {p1}, {p2}"


class Prediction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    result = models.BooleanField(verbose_name="выиграл первый", **nb)

    def json(self):
        return dict(id=self.id, match_id=self.match.id, result=self.result)


class Text(models.Model):
    string = models.TextField(max_length=4000, verbose_name="текст")

    def __str__(self):
        return self.string
