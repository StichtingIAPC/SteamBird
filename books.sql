--
-- Table structure for table 'Vak'
--
#Course Code is the Osiris given code, Course/Vak ID is the internal representation
CREATE TABLE IF NOT EXISTS 'teacher'(
  teacher_id INT NOT NULL AUTO_INCREMENT,
  titles varchar(255),
  initials VARCHAR(255),
  first_name VARCHAR(255),
  surname_prefix VARCHAR(255),
  last_name VARCHAR(255),
  email VARCHAR(255) UNIQUE ,
  active bool not null default '1',
  retired bool NOT NULL DEFAULT '0',
  last_login datetime,
  PRIMARY KEY (teacher_id)
);

CREATE TABLE IF NOT EXISTS  'module'(
  module_id INT NOT NULL AUTO_INCREMENT,
  name VARCHAR(255),
  course_code INT UNIQUE ,
  coordinator INT,
  module_moment ENUM('1','2','3','4','5','6','7','8','9','10','11','12'),
  PRIMARY KEY (module_id),
  FOREIGN KEY (coordinator) references teacher(teacher_id)
);


CREATE TABLE IF NOT EXISTS 'vak'(
  vak_id INT NOT NULL AUTO_INCREMENT,
  module_id INT,
  course_code INT,
  teacher_id INT,
  naam varchar(255),
  PRIMARY KEY (vak_id),
  FOREIGN KEY (teacher_id) REFERENCES teacher(teacher_id),
  FOREIGN KEY (module_id) REFERENCES module(module_id)
);

CREATE TABLE IF NOT EXISTS 'study'(
  study_ID INT NOT NULL AUTO_INCREMENT,
  name varchar(255),
  study_type enum('Bachelor','Master','Pre-master'),
  PRIMARY KEY (study_ID)
);

CREATE TABLE IF NOT EXISTS 'study_vak'(
  study_ID INT,
  vak_ID INT,
  period ENUM('1','2','3','4'),
  PRIMARY KEY (study_ID,vak_ID),
  FOREIGN KEY (study_ID) REFERENCES study(study_ID),
  FOREIGN KEY (vak_ID) REFERENCES vak(vak_id)
);


#It might be interesting for this table to extract authors?
CREATE TABLE IF NOT EXISTS 'books' (
  'book_id' INT NOT NULL AUTO_INCREMENT,
  'ISBN_13' INT UNIQUE,
  'ISBN_10' INT UNIQUE, #This should be used if book is before 2007
  'Auteur' varchar(255) NOT NULL DEFAULT '',
  'Title' varchar(255) NOT NULL DEFAULT '',
  'DOI' varchar(255),
  'Edition' varchar(255),
  PRIMARY KEY (book_id)
#   'PDF' tinyint(1) NOT NULL
);

CREATE TABLE IF NOT EXISTS 'book_vak'(
  book_id INT,
  vak_id INT,
  year varchar(255),
  PRIMARY KEY (book_id,vak_id),
  FOREIGN KEY (book_id) REFERENCES books(book_id),
  FOREIGN KEY (vak_id) REFERENCES vak(vak_id)
);
