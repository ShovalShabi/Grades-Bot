import MyKeys

class User:
    """
    User class, representation of user's details.
    """
    def __init__(self,username,user_email,user_password,year_selection,semester_selection):
        """
        Initializing instance for User Object.
        :param username: str
        :param user_email: str
        :param user_password: str
        :param year_selection: str
        :param semester_selection: str
        """
        self.username=username
        self.email=user_email
        self.password=user_password
        self.year_selection=year_selection
        self.semester_selection=semester_selection
