Material Selection Process design
=================================

The material selection process is a process for making an intermediate party
(Study association, IAPC), the teacher and the store (SBC) agree on a book for a
course.

This is achieved by a few steps:

State machine
-------------

.. graphviz:: msp_statemachine.dot

This flow is designed this way to allow teachers and the intermediate party to
have an extended "discussion" on which material to choose, in case this material
is hard to find.
As it also describes, to create a new MSP, one simply needs to create the actual
:code:`MSP` row and an :code:`MSPLine` of type :code:`REQUEST_MATERIAL` with a
material the course requires.

If a course requires multiple books, multiple :code:`MSP`'s need to be created.
One for each book (or material).

Database model
--------------

These models can be found in
:ref:`the models.msp module<steambird.models.msp>`.

.. graphviz:: msp_db_model.dot

Query routines
--------------

Get all teachers/officers that can edit
***************************************

.. code-block:: python
   :linenos:

   @property
   def all_teachers(self: MSP) -> List[Teacher]:
       return self.teachers + [
           teacher
           for course in self.courses
           for teacher in course.all_teachers
       ]

   @property
   def officers(self: MSP) -> List[Officer]:
       return [
           officer
           for course in self.courses
           for officer in course.officers
       ]

Check wether teacher/officer can touch
**************************************

.. code-block:: python
   :linenos:

   def teacher_can_edit(self: MSP, teacher: Teacher) -> bool:
       return teacher in self.teachers

   def officer_can_edit(self: MSP, officer: Officer) -> bool:
       return officer in self.officers
