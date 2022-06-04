from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import AddPLayersForm
from .models import User, Tournament, Match, TennisPlayer, Participant, Text

admin.site.register(User, UserAdmin)


@admin.register(Tournament)
class TournamentAdmin(admin.ModelAdmin):
    actions = ["add_players"]

    def add_players(self, request, queryset):
        tournament = queryset.first()
        if "apply" in request.POST:

            players = request.POST["players"].splitlines()

            result = tournament.add_participants(*players)
            if result:
                self.message_user(request, "Добавлено %s участников" % len(players))
            else:
                self.message_user(
                    request, "Что-то пошло не так", level=messages.WARNING
                )

            # Return to previous page
            return HttpResponseRedirect(request.get_full_path())

        # Create form and pass the data which objects were selected before triggering 'broadcast' action
        # We create an intermediate page right here
        form = AddPLayersForm(
            initial={"_selected_action": queryset.values_list("id", flat=True)}
        )

        # We need to create a template of intermediate page with form - but this is really easy
        return render(
            request, "admin/add_players.html", {"items": queryset, "form": form}
        )


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    pass


@admin.register(TennisPlayer)
class TennisPlayerAdmin(admin.ModelAdmin):
    pass


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    pass


@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    pass
