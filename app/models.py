from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404
from django.db.models import Sum


# =============================== NEW VOTES STRATS ===============================
class VoteInterface():
    def like(self):
        if self.vote == self.LIKE:
            self.vote = self.UNVOTED
        else:
            self.vote = self.LIKE
        self.save(update_fields=['vote'])
        return True

    def dislike(self):
        if self.vote == self.DISLIKE:
            self.vote = self.UNVOTED
        else:
            self.vote = self.DISLIKE
        self.save(update_fields=['vote'])
        return True


class QuestionVoteManager(models.Manager):
    def find_or_create(self, question, user):
        try:
            vote = self.get(question=question, user=user)
        except ObjectDoesNotExist as identifier:
            vote = self.create(question=question, user=user)
        return vote


class AnswerVoteManager(models.Manager):
    def find_or_create(self, answer, user):
        try:
            vote = self.get(answer=answer, user=user)
        except ObjectDoesNotExist as identifier:
            vote = self.create(answer=answer, user=user)
        return vote


class QuestionVote(models.Model, VoteInterface):
    LIKE = 1
    DISLIKE = -1
    UNVOTED = 0
    VOTES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
        (UNVOTED, 'Unvoted'),
    ]

    vote = models.SmallIntegerField(
        choices=VOTES,
        default=UNVOTED,
        verbose_name='Vote'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='q_votes'
    )
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE,
        related_name='estimates'
    )

    objects = QuestionVoteManager()

    def __str__(self):
        return f'{self.question.title} Vote: {self.vote}'

    class Meta():
        unique_together = [
            'user',
            'question',
        ]


class AnswerVote(models.Model, VoteInterface):
    LIKE = 1
    DISLIKE = -1
    UNVOTED = 0
    VOTES = [
        (LIKE, 'Like'),
        (DISLIKE, 'Dislike'),
        (UNVOTED, 'Unvoted'),
    ]

    vote = models.SmallIntegerField(
        choices=VOTES,
        default=UNVOTED,
        verbose_name='Vote'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='a_votes'
    )
    answer = models.ForeignKey(
        'Answer',
        on_delete=models.CASCADE,
        related_name='estimates'
    )

    objects = AnswerVoteManager()

    def __str__(self):
        return f'{self.answer.__str__()} Vote: {self.vote}'

    class Meta():
        unique_together = [
            'user',
            'answer',
        ]


# =============================== NEW VOTES ENDS ===============================

# =============================== MANAGERS STARTS ===============================

class QuestionManager(models.Manager):
    def most_popular(self):
        return self.all().order_by('-score').prefetch_related('author', 'tags')

    def new(self):
        return self.all().order_by('-date_create').prefetch_related('author', 'tags')

    def find_by_tag(self, tag):
        questions = self.filter(
            tags__tag__iexact=tag).prefetch_related('author')
        if not questions:
            raise Http404
        return questions

    def find_by_id(self, id):
        try:
            question = self.get(pk=id)
        except ObjectDoesNotExist:
            raise Http404
        return question


class AnswerManager(models.Manager):
    def most_popular(self, question):
        return self.filter(question=question).order_by('-is_correct', '-score')

    def find_by_id(self, id):
        try:
            answer = self.get(pk=id)
        except ObjectDoesNotExist:
            raise Http404
        return answer


class ProfileManager(models.Manager):
    def top_ten(self):
        return self.all().order_by('-score')[:10]

# =============================== MANAGERS ENDS ===============================

class Question(models.Model):
    title = models.CharField(
        max_length=1024,
        verbose_name='Title'
    )
    text = models.TextField(
        verbose_name='Text'
    )
    date_create = models.DateField(
        auto_now_add=True,
        verbose_name='Date of creation'
    )
    last_modified = models.DateField(
        auto_now=True,
        verbose_name='Last modified'
    )
    tags = models.ManyToManyField('Tag')
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='questions'
    )
    score = models.IntegerField(
        default=0
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'

    # Manager
    objects = QuestionManager()

    def update_score(self):
        vote_sum = self.estimates.aggregate(Sum('vote'))
        self.score = vote_sum['vote__sum']
        self.save(update_fields=['score'])
        return self.score


class Answer(models.Model):
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.SET_NULL,
        related_name='answers'
    )
    text = models.TextField(
        verbose_name='Text'
    )
    score = models.IntegerField(
        default=0
    )
    question = models.ForeignKey(
        'Question',
        on_delete=models.CASCADE
    )
    is_correct = models.BooleanField(
        verbose_name='Is Correct',
        default=False
    )
    date_create = models.DateField(
        auto_now_add=True,
        verbose_name='Date of creation'
    )
    last_modified = models.DateField(
        auto_now=True,
        verbose_name='Last modified'
    )

    def __str__(self):
        return self.author.profile.nickname

    class Meta:
        verbose_name = 'Answer'
        verbose_name_plural = 'Answers'

    # Manager
    objects = AnswerManager()

    def update_score(self):
        vote_sum = self.estimates.aggregate(Sum('vote'))
        self.score = vote_sum['vote__sum']
        self.save(update_fields=['score'])
        return self.score


class Tag(models.Model):
    tag = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.tag

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    avatar = models.ImageField(
        upload_to='profiles_avatars/',
        blank=True
    )
    nickname = models.CharField(
        max_length=128,
        verbose_name='NickName'
    )
    score = models.IntegerField(
        default=0
    )

    def __str__(self):
        return self.nickname

    class Meta:
        verbose_name = 'Profile'
        verbose_name_plural = 'Profiles'

    # Manager
    objects = ProfileManager()

    def get_score_from_questions(self):
        questions_scores = self.user.questions.aggregate(Sum('score'))
        return questions_scores['score__sum']

    def get_score_from_answers(self):
        answers_scores = self.user.answers.aggregate(Sum('score'))
        return answers_scores['score__sum']

    def update_score(self):
        self.score = self.get_score_from_questions() + self.get_score_from_answers()
        self.save(update_fields=['score'])
        return self.score


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
