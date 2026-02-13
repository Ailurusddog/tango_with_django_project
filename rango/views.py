from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm

from datetime import datetime


def _parse_datetime(value: str) -> datetime:

    try:
        return datetime.fromisoformat(value)
    except Exception:
        # Fallback: handle without microseconds
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')


def visitor_session_handler(request):

    session = request.session

    visits = session.get('visits')
    last_visit = session.get('last_visit')

    if visits is None or last_visit is None:
        session['visits'] = 1
        session['last_visit'] = str(datetime.now())
        return

    last_visit_time = _parse_datetime(last_visit)

    if (datetime.now() - last_visit_time).days > 0:
        session['visits'] = int(visits) + 1
        session['last_visit'] = str(datetime.now())
    else:
        # Keep values as-is if less than a day.
        session['visits'] = int(visits)
        session['last_visit'] = last_visit


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]

    context_dict = {
        'boldmessage': 'Crunchy, creamy, cookie, candy, cupcake!',
        'categories': category_list,
        'pages': page_list,
    }

    visitor_session_handler(request)

    return render(request, 'rango/index.html', context=context_dict)


def about(request):
    visitor_session_handler(request)

    visits = request.session.get('visits', 1)

    context_dict = {
        'visits': visits
    }
    return render(request, 'rango/about.html', context=context_dict)


def show_category(request, category_name_slug):
    context_dict = {}

    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category).order_by('-views')

        context_dict['category'] = category
        context_dict['pages'] = pages
    except Category.DoesNotExist:
        context_dict['category'] = None
        context_dict['pages'] = None

    return render(request, 'rango/category.html', context=context_dict)


@login_required(login_url=reverse_lazy('rango:login'))
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return redirect(reverse('rango:index'))
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


@login_required(login_url=reverse_lazy('rango:login'))
def add_page(request, category_name_slug):
    try:
        category = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        category = None

    form = PageForm()

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            if category:
                page = form.save(commit=False)
                page.category = category
                page.views = 0
                page.save()
                return redirect(reverse('rango:show_category',
                                        kwargs={'category_name_slug': category_name_slug}))
        else:
            print(form.errors)

    context_dict = {'form': form, 'category': category}
    return render(request, 'rango/add_page.html', context_dict)


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST, request.FILES)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()

    return render(
        request,
        'rango/register.html',
        context={'user_form': user_form,
                 'profile_form': profile_form,
                 'registered': registered}
    )


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect(reverse('rango:index'))
            else:
                return HttpResponse("Your Rango account is disabled.")
        else:
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request, 'rango/login.html')


@login_required(login_url=reverse_lazy('rango:login'))
def restricted(request):
    return render(request, 'rango/restricted.html')


@login_required(login_url=reverse_lazy('rango:login'))
def user_logout(request):
    logout(request)
    return redirect(reverse('rango:index'))
