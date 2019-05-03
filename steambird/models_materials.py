from django.db import models
from django.utils.translation import ugettext_lazy as _

from polymorphic.models import PolymorphicModel


class StudyMaterial(models.Model):
    name = models.CharField(
        null=False, blank=False, max_length=255,
        verbose_name=_('Category name of this article'))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Study Material")
        verbose_name_plural = _("Study Materials")


class StudyMaterialEdition(PolymorphicModel):
    # Could be derived from either OID or ISBN
    name = models.CharField(
        null=False, blank=False, max_length=255,
        verbose_name=_("Name of the material"))

    # The type if material, e.g. the list of different revisions of the book
    material_type = models.ForeignKey(
        StudyMaterial,
        on_delete=models.DO_NOTHING, null=True, blank=True,
        verbose_name=_("Material collection"))

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("StudyMaterial Edition")
        verbose_name_plural = _("StudyMaterials Editions")


class OtherMaterial(StudyMaterialEdition):
    """"
    Use if material is any material other than a scientific article or a book
    """
    pass

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Other Material")
        verbose_name_plural = _("Other Materials")


class Book(StudyMaterialEdition):
    ISBN = models.CharField(null=False, unique=True,
                            verbose_name=_("ISBN 10 or ISBN 13"),
                            max_length=13)
    # Authors should be derived from the ISBN
    author = models.CharField(null=False, blank=False, verbose_name=_(
        "Author names, comma separated"), max_length=1000)
    # Cover image of the book, should be derived from ISBN
    img = models.URLField(verbose_name=_("Link to cover image of book"), blank=True, null=True)

    # Year of publishing, should be derived from ISBN
    year_of_publishing = models.IntegerField(
        verbose_name="Year this revision of the book was published.")

    # noinspection PyPep8Naming,PyMethodMayBeStatic
    def validate_ISBN(self, ISBN):
        if len(ISBN) == 10 or len(ISBN) == 13:
            return
        else:
            raise ValueError("ISBN does not match either known lengths")

    def __str__(self):
        return "{}: {}".format(self.ISBN, self.name)

    class Meta:
        verbose_name = _("Book")
        verbose_name_plural = _("Books")


class ScientificArticle(StudyMaterialEdition):
    DOI = models.CharField(null=False, blank=True, verbose_name=_(
        "Digital Object Identifier"),
                           max_length=255)

    # List of authors, comma separated, should be derived from DOI
    author = models.CharField(null=False, blank=False, verbose_name=_(
        "Author names, comma separated"), max_length=1000)

    # Year of publishing, should be derived from OID
    year_of_publishing = models.IntegerField(
        verbose_name="Year this revision of the book was published.")

    def __str__(self):
        return "{}: {}".format(self.DOI, self.name)

    class Meta:
        verbose_name = _("Scientific Article")
        verbose_name_plural = _("Scientific Articles")