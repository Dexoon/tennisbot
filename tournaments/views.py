from django.http import JsonResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
import json

# Create your views here.
from django.views.decorators.csrf import csrf_exempt
from telegram import Bot
from sesame.utils import get_query_string
from .models import Tournament, Prediction, User, Text


def tournament(request, pk):
    if request.user.is_anonymous:
        raise Http404()
    tournament = get_object_or_404(Tournament, id=pk)
    if not request.user.is_superuser:
        if tournament.status == Tournament.STATUS.DRAFT:
            raise Http404()

    predictions = {}
    for match in tournament.match_set.all():
        prediction, _ = Prediction.objects.get_or_create(user=request.user, match=match)
        predictions[prediction.match_id] = prediction
    context = tournament.json()
    context["predictions"] = {
        match_id: prediction.result for match_id, prediction in predictions.items()
    }
    return render(request, "frontend/index.html", {"context": context})


def predictions(request, pk):
    if request.user.is_anonymous:
        raise Http404()
    tournament = get_object_or_404(Tournament, id=pk)
    if not request.user.is_superuser:
        if tournament.status == Tournament.STATUS.DRAFT:
            raise Http404()
    predictions = {}
    for match in tournament.match_set.all():
        prediction, _ = Prediction.objects.get_or_create(user=request.user, match=match)
        predictions[prediction.match_id] = prediction
    if request.body and tournament.status in (
        Tournament.STATUS.DRAFT,
        Tournament.STATUS.FORECAST,
    ):
        body = json.loads(request.body)
        modified_predictions = []
        for match_id, result in body.items():
            match_id = int(match_id)
            if predictions[match_id].result != result:
                predictions[match_id].result = result
                modified_predictions += [predictions[match_id]]
        Prediction.objects.bulk_update(modified_predictions, ["result"])
    return JsonResponse(
        {match_id: prediction.result for match_id, prediction in predictions.items()},
        safe=False,
    )


@csrf_exempt
def telegram(request):
    bot = Bot("864989220:AAG-AwuGMji5kXkvlHJl3DJ0ROnUAlL610U")
    text = str(Text.objects.first())
    body = json.loads(request.body)
    if "message" in body:
        telegram_id = body["message"]["from"]["id"]
        if "username" in body["message"]["from"]:
            username = body["message"]["from"]["username"]
        else:
            username = body["message"]["from"]["first_name"]
        defaults = {"username": username}
        user, created = User.objects.update_or_create(
            telegram_id=body["message"]["from"]["id"], defaults=defaults
        )
        if user.is_superuser:
            tournaments = Tournament.objects.all()
        else:
            tournaments = Tournament.objects.exclude(status=Tournament.STATUS.DRAFT)

        text += "\n\n".join(
            [""]
            + [
                f"[{str(t)}](https://telegram-bot.website/tournament/{t.id}/{get_query_string(user)})"
                for t in tournaments
            ]
        )
        bot.send_message(chat_id=telegram_id, text=text or "123", parse_mode="Markdown")
    return JsonResponse({"ok": True})
