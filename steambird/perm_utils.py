from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.models import User

from steambird.models_user import Teacher, StudyAssociation


class IsTeacherMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               Teacher.objects.filter(user=self.request.user).exists()

class IsStudyAssociationMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_authenticated and \
               StudyAssociation.objects.filter(users=self.request.user).exists()
