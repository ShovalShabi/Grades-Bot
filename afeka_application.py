class Application:
    """
    Class Application a representation of application details.
    """
    def __init__(self,description,date_time,serial_number,status):
        """
        Initializing Application object instance.
        :param description: str, description of application
        :param date_time: str, a date and time of making the application
        :param serial_number: str, serial number of the application
        :param status: str, status of application
        """
        self.description=description
        self.date_time=date_time
        self.serial_number=serial_number
        self.status=status

    def is_same_application(self,other_application) -> bool:
        """
        Method that check if the two applications are the same one.
        :param other_application: Application object, comparing to this object.
        :return: bool
        """
        if self.serial_number == other_application.serial_number:
            return True
        return False

    def check_if_modified(self,updated_application) ->bool:
        """
        Method that check if the same application has been modified.
        :param updated_application: Application object, comparing to this object.
        :return: bool
        """
        if self.status != updated_application.status:
            return True
        return False
