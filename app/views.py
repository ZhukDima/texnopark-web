from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.template import RequestContext, Template
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.views.decorators.http import require_GET, require_POST
from django.http import Http404
from django.core.files.storage import FileSystemStorage
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum

from django.contrib import auth
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from .forms import QuestionForm, AnswerForm, LoginForm, RegistrationForm, UserSettingsForm, ProfileSettingsForm

from .models import Profile, Question, Answer, Tag, QuestionVote, AnswerVote


def paginate(request, per_page, model_list):
    paginator = Paginator(model_list, per_page)
    page_number = int(request.GET.get('page', 1))
    if page_number > paginator.num_pages:
        raise Http404

    obj_list = paginator.get_page(page_number)
    max_range = int(page_number) + 5
    context = {
        "page_obj": obj_list,
        "max_range": max_range,
    }
    return context


def index(request):
    # Index page
    questions = Question.objects.new()
    context = paginate(request, 5, questions)
    return render(request, 'index.html', context)


@login_required
def ask_question(request):
    # Page for create new Question
    if request.method == 'GET':
        form = QuestionForm()
    else:
        form = QuestionForm(data=request.POST, request=request)
        if form.is_valid():
            question = form.save()
            return redirect(reverse('answers', kwargs={'question_id': question.pk}))
    return render(request, 'create_question.html', {'form': form})


def answers(request, question_id):
    # Page with answers on current question
    question = Question.objects.find_by_id(question_id)
    q_answers = Answer.objects.most_popular(question)
    context = paginate(request, 5, q_answers)
    context['question'] = question
    if request.method == 'GET':
        form = AnswerForm()
    else:
        if request.user.is_authenticated:
            form = AnswerForm(data=request.POST,
                              request=request, question_id=question_id)
            if form.is_valid():
                answer = form.save()
                return redirect(reverse('answers', kwargs={'question_id': question_id}) + f'#{answer.pk}')
        else:
            return redirect(reverse('login') + f'?next={request.path}')
    context['form'] = form
    return render(request, 'answers.html', context)


def tag_questions(request, tag):
    # Page with question on one tag
    cur_tag = Tag.objects.filter(tag=tag).first()
    if not cur_tag:
        raise Http404
    tag_qs = Question.objects.find_by_tag(tag)

    context = paginate(request, 5, tag_qs)
    context['tag'] = f'{tag}'

    return render(request, 'tag_questions.html', context)


@login_required
def settings(request):
    if request.method == 'GET':
        user_form = UserSettingsForm(instance=request.user)
        profile_form = ProfileSettingsForm(instance=request.user.profile)
    else:
        user_form = UserSettingsForm(
            data=request.POST,
            instance=request.user
        )
        profile_form = ProfileSettingsForm(
            data=request.POST,
            instance=request.user.profile,
            user=request.user,
            FILES=request.FILES
        )
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            profile_form.save()

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'settings.html', context)


def login(request):
    # Page for login on site
    if request.GET.get('next'):
        next_url = request.GET.get('next')
    elif request.session.get('next'):
        next_url = request.session.get('next')
    else:
        next_url = ''

    if request.method == 'GET':
        form = LoginForm()
    else:
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = auth.authenticate(request, **form.cleaned_data)
            if user is not None:
                auth.login(request, user)
                if next_url != '':
                    return redirect(next_url)
                else:
                    return redirect(reverse('home'))

    if request.session.get('next') != next_url:
        request.session['next'] = next_url

    context = {
        'form': form,
    }
    return render(request, 'login.html', context)

@login_required
def logout(request):
    auth.logout(request)
    if 'next' in request.GET:
        return redirect(request.GET['next'])
    else:
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


def register(request):
    # Page for registration
    if request.user.is_authenticated:
        raise Http404
    if request.method == 'POST':
        form = RegistrationForm(data=request.POST, FILES=request.FILES)
        if form.is_valid():
            user = form.save()
            raw_password = form.cleaned_data.get('password1')
            user = auth.authenticate(
                username=user.username,
                password=raw_password
            )
            if user is not None:
                auth.login(request, user)
            else:
                return redirect(reverse('signup'))
            return redirect(reverse('home'))
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})
