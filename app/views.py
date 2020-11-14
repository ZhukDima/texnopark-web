from django.shortcuts import render
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.views.generic import ListView
from django.views.decorators.http import require_GET, require_POST
from django.http import Http404

questions = [
    {
        'id': idx,
        'title': f'Question about Pascal {idx}',
        'text': 'Mr and Mrs Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much. They were the last people youd expect to be involved in anything strange or mysterious, because they just didnt hold with such nonsense.',
        'score': f'{idx}',
        'tags': ['Pascal', 'C'],
    } for idx in range(0, 100)
]

tags = [
    'Pascal',
    'Python',
    'MySQL',
    'Mailru',
    'Texnopark',
    'C',
]

members = [
    'Agent_FSB_1',
    'Agent_FSB_2',
    'Agent_FSB_3',
    'Agent_GOS_DEP_1',
    'Agent_GOS_DEP_2',
    'Agent_GOS_DEP_3',
]

# GLOBAL CONTEXT STARTS
context = {}
context['all_tags'] = tags
context['all_members'] = members
# GLOBAL CONTEXT ENDS

# Paginate starts


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
# Paginate ends

# Infinite Scroll Paginate starts
# Infinite Scroll Paginate ends


def index(request):
    # Index page
    context.update(paginate(request, 5, questions))
    return render(request, 'index.html', context)


def ask_question(request):
    # Page for create new Question
    return render(request, 'create_question.html', context)


q_answers = [
    {
        'q_id': idx,
        'score': f'{idx}',
        'author': 'SkalikS',
        'text': 'Mr and Mrs Dursley, of number four, Privet Drive, were proud to say that they were perfectly normal, thank you very much. They were the last people youd expect to be involved in anything strange or mysterious, because they just didnt hold with such nonsense.',
    } for idx in range(0, 14)
]

def answers(request, id):
    # Page with answers on current question
    question = questions[id]
    context['question'] = question

    per_page = 5
    context.update(paginate(request, per_page, q_answers))

    return render(request, 'answers.html', context)


def tag_questions(request, tag):
    # Page with question on one tag
    tag_qs = []
    for q in questions:
        if tag in q['tags']:
            tag_qs.append(q)

    context.update(paginate(request, 5, tag_qs))
    context['tag'] = f'{tag}'

    return render(request, 'tag_questions.html', context)


user = {
    'login': 'ZhukDima',
    'email': 'zhukdo@gmail.com',
    'nickname': 'SkalikS',
}


def settings(request):
    # Page with user's settings
    context['user'] = user
    return render(request, 'settings.html', context)


errors = ['Incorrect login', 'Wrong password']


def login(request):
    # Page for login in site
    context['errors'] = errors
    return render(request, 'login.html', context)


def register(request):
    # Page for registration
    return render(request, 'register.html', context)
