from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import render
# Create your views here.
from goods.models import Categories
def index(request):


    context = {
        'categories': ''
    }

    return render(request, 'main/index.html', context)