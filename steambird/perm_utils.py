"""
Set of Permision Utilities, granting different users different levels of access
"""
from django.contrib.auth.mixins import UserPassesTestMixin

from steambird.models.user import Teacher, StudyAssociation


class IsTeacherMixin(UserPassesTestMixin):
    """
    Checks if user has Teacher permissions, otherwise redirects to 404
    """
    def test_func(self):
        """
        Tests if user is Teacher

        :return: boolean. Used in Views
        """
        return self.request.user.is_authenticated and \
               Teacher.objects.filter(user=self.request.user).exists()


class IsStudyAssociationMixin(UserPassesTestMixin):
    """
    Checks if user has Study Association permissions, otherwise redirects to 404
    """
    def test_func(self):
        """
        Tests if user is a StudyAssociation

        :return: boolean. Used in Views
        """
        return self.request.user.is_authenticated and \
               StudyAssociation.objects.filter(users=self.request.user).exists()


class IsBoecieMixin(UserPassesTestMixin):
    """
    Checks if user is SuperUser, otherwise throws an Error
    """
    def test_func(self):
        """
        Tests whether user is a SuperUser (for now)

        :return: boolean. Used in views
        """
        return self.request.user.is_authenticated and \
               self.request.user.is_superuser
