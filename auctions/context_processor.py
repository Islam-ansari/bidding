from .models import Watchlist
from django.contrib.auth import authenticate, login, logout

def extras(request):
    if request.user.is_authenticated:
        count = Watchlist.objects.filter(user=request.user).count()
    else:
        count = 0
    return {'watchlist_count':count}
