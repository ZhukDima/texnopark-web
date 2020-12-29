from django.core.management.base import BaseCommand, CommandError
from app.models import Question, Answer, Tag, User, QuestionVote, AnswerVote, Profile
from random import choice, sample, randint
from faker import Faker

quantity_values = {
    'small': {
        'questions': 10,
        'answers': 20,
        'tags': 5,
        'users': 5
    },
    'medium': {
        'questions': 100,
        'answers': 200,
        'tags': 50,
        'users': 50
    },
    'large': {
        'questions': 1000,
        'answers': 2000,
        'tags': 500,
        'users': 500
    }
}

fake = Faker()


class Command(BaseCommand):
    help = 'Seed fake data into database'

    def fill_users(self, count):
        for i in range(count):
            profile = fake.simple_profile()
            u = User.objects.create(
                is_superuser=False,
                username=profile['username'],
                email=profile['mail']
            )
            u.set_password('password')
            u.save(update_fields=['password'])
            new_profile = Profile.objects.get(pk=u.pk)
            new_profile.nickname = profile['username']
            new_profile.save(update_fields=['nickname'])

    def fill_questions(self, count):
        author_ids = list(
            User.objects.values_list(
                'id', flat=True
            )
        )
        tags_ids = list(
            Tag.objects.values_list(
                'id', flat=True
            )
        )

        for i in range(count):
            q = Question.objects.create(
                author_id=choice(author_ids),
                text='. '.join(fake.sentences(fake.random_int(min=2, max=5))),
                title=fake.sentence()[:128]
            )
            q.tags.set(sample(tags_ids, k=randint(1, 5)))

    def fill_answers(self, count):
        author_ids = list(
            User.objects.values_list(
                'id', flat=True
            )
        )
        q_ids = list(
            Question.objects.values_list(
                'id', flat=True
            )
        )

        for i in range(count):
            Answer.objects.create(
                author_id=choice(author_ids),
                question_id=choice(q_ids),
                text='. '.join(fake.sentences(randint(2, 5)))
            )

    def fill_tags(self, count):
        for i in range(count):
            Tag.objects.create(
                tag=fake.word()
            )

    def handle(self, *args, **options):
        print(options['size'])
        quantity = quantity_values[options['size']]

        # ================= USERS =================
        self.fill_users(quantity['users'])

        # ================= TAGS =================
        self.fill_tags(quantity['tags'])

        # ================= QUESTIONS =================
        self.fill_questions(quantity['questions'])

        # ================= ANSWERS =================
        self.fill_answers(quantity['answers'])


    def add_arguments(self, parser):
        parser.add_argument(
            '-s',
            '--size',
            nargs='?',
            type=str,
            action='store',
            choices=[
                'small',
                'medium',
                'large',
            ],
            default='small'
        )
