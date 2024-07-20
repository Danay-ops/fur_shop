from django.conf import settings
from django.contrib import auth
from django.db.models import Prefetch
from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from users.forms import UserLoginForm
from django.http import HttpResponseRedirect, HttpResponse

from users.forms import UserRegistrationForm

from users.forms import ProfileForm

from carts.models import Cart

from orders.models import Order,OrderItem








# Create your views here.
def login(request):
    if request.method == 'POST':
        form = UserLoginForm(data=request.POST)
        if form.is_valid():
            username = request.POST['username']
            password = request.POST['password']
            user = auth.authenticate(username=username,password=password)
            session_key = request.session.session_key
            if user:

                if session_key:
                    Cart.objects.filter(session_key=session_key).update(user=user)

                auth.login(request, user)
                redirect_page = request.POST.get('next', None)
                if redirect_page and redirect_page != reverse('user:logout'):
                    return HttpResponseRedirect(request.POST.get('next'))
                return HttpResponseRedirect(reverse('main:index'))
    else:
        form = UserLoginForm()
    context = {
        'title' : 'Авторизация',
        'form': form
    }
    return render(request,'users/login.html',context)

def registration(request):
    if request.method == 'POST':
        form = UserRegistrationForm(data=request.POST)
        if form.is_valid():
                form.save()
                user = form.instance
                auth.login(request,user)
                return HttpResponseRedirect(reverse('main:index'))
    else:
        form = UserRegistrationForm()
    context = {
        'title' : 'Регистрация',
        'form': form
    }
    return render(request,'users/registration.html',context)




@login_required
def profile(request):
    if request.method == 'POST':
        form = ProfileForm(data=request.POST,instance=request.user, files=request.FILES)
        if form.is_valid():
                form.save()
                return HttpResponseRedirect(reverse('user:profile'))
    else:
        form = ProfileForm(instance=request.user)
    orders = Order.objects.filter(user=request.user).prefetch_related(
                     Prefetch(
                         "orderitem_set",
                         queryset=OrderItem.objects.select_related("product"),
                     )
                 ).order_by("-id")

    context = {
             'title': 'Home - Кабинет',
             'form': form,
             'orders': orders,
         }
    return render(request,'users/profile.html',context)

def users_cart(request):
    return render(request,'users/users_cart.html')



@login_required
def logout(request):
    auth.logout(request)
    return redirect(reverse('main:index'))



