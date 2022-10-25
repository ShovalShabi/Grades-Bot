class Course:
    """
    Class Course a representation of course details.
    """
    def __init__(self,name,type_of_grade,grade):
        """
        Initializing Application object instance.
        :param name: str, name of the course
        :param type_of_grade: str, type of the course grade
        :param grade: str, grade
        """
        self.name = name
        self.type_of_grade = type_of_grade
        self.grade = grade

    def is_same_course(self,course):
        """
        Method that check if the two courses are the same one.
        :param course: Course object, comparing to this object.
        :return: bool
        """
        if course.name==self.name:
            return True
        return False

    def does_grade_changed(self,updated_course):
        """
        Method that check if the same course has been modified.
        :param updated_course: Course object, comparing to this object.
        :return: bool
        """
        if updated_course.grade != self.grade:
            return True
        return False
