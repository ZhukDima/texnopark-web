
from .models import Tag, Profile


def all_tags_processor(request):
    tags = Tag.objects.all()
    return {'all_tags': tags}


def best_members_processsor(request):
    top_users = Profile.objects.top_ten()
    return {'best_members': top_users}
