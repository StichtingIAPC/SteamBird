from django.test import tag, TestCase

from steambird.models_coursetree import Period


# pylint: disable=invalid-name
@tag('unit')
class PeriodTest(TestCase):
    def test_isQuartileReturnsCorrectly(self):
        self.assertTrue(Period.Q1.is_quartile())
        self.assertTrue(Period.Q2.is_quartile())
        self.assertTrue(Period.Q3.is_quartile())
        self.assertTrue(Period.Q4.is_quartile())
        self.assertTrue(Period.Q5.is_quartile())

        self.assertFalse(Period.S1.is_quartile())
        self.assertFalse(Period.S2.is_quartile())
        self.assertFalse(Period.S3.is_quartile())
        self.assertFalse(Period.YEAR.is_quartile())
        self.assertFalse(Period.FULL_YEAR.is_quartile())

    def test_parentReturnsCorrectly(self):
        self.assertEqual(Period.Q1.parent(), Period.S1)
        self.assertEqual(Period.Q2.parent(), Period.S1)
        self.assertEqual(Period.Q3.parent(), Period.S2)
        self.assertEqual(Period.Q4.parent(), Period.S2)
        self.assertEqual(Period.Q5.parent(), Period.S3)

        self.assertEqual(Period.S1.parent(), Period.YEAR)
        self.assertEqual(Period.S2.parent(), Period.YEAR)

        self.assertEqual(Period.S3.parent(), Period.FULL_YEAR)
        self.assertEqual(Period.YEAR.parent(), Period.FULL_YEAR)

    def test_childrenReturnsCorrectly(self):
        self.assertEqual(Period.Q1.children(), [])
        self.assertEqual(Period.Q2.children(), [])
        self.assertEqual(Period.Q3.children(), [])
        self.assertEqual(Period.Q4.children(), [])
        self.assertEqual(Period.Q5.children(), [])

        self.assertEqual(Period.S1.children(), [Period.Q1, Period.Q2])
        self.assertEqual(Period.S2.children(), [Period.Q3, Period.Q4])
        self.assertEqual(Period.S3.children(), [Period.Q5])

        self.assertEqual(Period.YEAR.children(),
                         [Period.S1, Period.S2])
        self.assertEqual(Period.FULL_YEAR.children(),
                         [Period.YEAR, Period.S3])

    def test_all_parentsReturnsCorrectly(self):
        self.assertEqual(Period.Q1.all_parents(),
                         [Period.S1, Period.YEAR, Period.FULL_YEAR])
        self.assertEqual(Period.Q2.all_parents(),
                         [Period.S1, Period.YEAR, Period.FULL_YEAR])
        self.assertEqual(Period.Q3.all_parents(),
                         [Period.S2, Period.YEAR, Period.FULL_YEAR])
        self.assertEqual(Period.Q4.all_parents(),
                         [Period.S2, Period.YEAR, Period.FULL_YEAR])
        self.assertEqual(Period.Q5.all_parents(),
                         [Period.S3, Period.FULL_YEAR])

        self.assertEqual(Period.S1.all_parents(),
                         [Period.YEAR, Period.FULL_YEAR])
        self.assertEqual(Period.S2.all_parents(),
                         [Period.YEAR, Period.FULL_YEAR])
        self.assertEqual(Period.S3.all_parents(),
                         [Period.FULL_YEAR])

        self.assertEqual(Period.YEAR.all_parents(),
                         [Period.FULL_YEAR])

    def test_all_childrenReturnsCorrectly(self):
        self.assertEqual(Period.Q1.all_children(), [])
        self.assertEqual(Period.Q2.all_children(), [])
        self.assertEqual(Period.Q3.all_children(), [])
        self.assertEqual(Period.Q4.all_children(), [])
        self.assertEqual(Period.Q5.all_children(), [])

        self.assertEqual(Period.S1.all_children(), [Period.Q1, Period.Q2])
        self.assertEqual(Period.S2.all_children(), [Period.Q3, Period.Q4])
        self.assertEqual(Period.S3.all_children(), [Period.Q5])

        self.assertEqual(Period.YEAR.all_children(),
                         [Period.Q1, Period.Q2, Period.Q3, Period.Q4,
                          Period.S1, Period.S2])
        self.assertEqual(Period.FULL_YEAR.all_children(),
                         [Period.Q1, Period.Q2, Period.Q3, Period.Q4, Period.Q5,
                          Period.S1, Period.S2, Period.S3, Period.YEAR])
