Course Tree design
==================

Course Tree is a method for describing the structure of studies, modules and courses and potentially even more complicated future education structures. Each "level" of a study is modeled as a course, or a set thereof.

Database model
--------------

These models can be found in
:ref:`the models\_coursetree module<steambird.models\_coursetree>`.

.. graphviz:: coursetree_db_model.dot


Query routines
--------------

Retrieve all teachers that can be notified manually
***************************************************

.. code-block:: python
   :linenos:

   @property
   def all_teachers(self: 'Course') -> List[Teacher]:
       return [
           self.coordinator,
           *self.teachers,
           *[
               teacher
               for course in self.course_parents
               for teacher in course.all_teachers
           ],
           *[
               study.director
               for study in self.studies
           ]
       ]

Get study coordinators/directors/officers
*****************************************

.. code-block:: python
   :linenos:

   @property
   def coordinators(self: 'Course') -> List[Teacher]:
       "These coordinators are also to be autonotified in case of delayed MSP's"
       return [
           self.coordinator,
           *[
               teacher
               for course in self.course_parents
               for teacher in course.coordinators
           ]
       ]

   @property
   def directors(self: 'Course') -> List[Teacher]:
       return [
           *[
               director
               for course in self.course_parents
               for director in course.directors
           ],
           *map(self.studies, lambda study: study.director)
       ]

   @property
   def officers(self: 'Course') -> List[Officer]:
       return [
           *[
               officer
               for course in self.course_parents
               for officer in course.officers
           ],
           *map(self.studies, lambda study: study.officer)
       ]

Check if a teacher/officer can edit
***********************************

.. code-block:: python
   :linenos:

   def teacher_can_edit(self: 'Course', teacher: Teacher) -> bool:
       return teacher in (self.coordinators + self.directors)

   def officer_can_edit(self: 'Course', officer: Officer) -> bool:
       return officer in self.officers

Check if a teacher/officer can manage MSP's
*******************************************

.. code-block:: python
   :linenos:

   def teacher_can_manage_msp(self: 'Course', teacher: Teacher) -> bool:
       return teacher in (self.coordinators + self.directors + self.teachers)

   def officer_can_manage_msp(self: 'Course', officer: Officer) -> bool:
       return officer in self.officers
