import smtplib
import ssl
import time
import json
from copy import deepcopy
from threading import Thread
from threading import Lock
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from Course import Course
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from afeka_application import Application

#************************************************************************************ Father class Bot **************************************************************************************#
class Bot(Thread):
    """
    A class that represent a Bot for grades scarping from college site.
    Extending from Thread class for concurrent functioning.

    Attributes
    ----------
    @serviced_path: Service object that containing path for driver's installation location !--static for all instances--!
    @bot_email: str , representing the email of the bot email !--static for all instances--!
    @bot_email_password: str , representing the email password of the bot !--static for all instances--!
    @mail_lock: Lock object, designated for preventing race condition on valuable actions that has to be synchronized !--static for all instances--!
    @save_lock: Lock object, designated for preventing race condition on valuable actions that has to be synchronized !--static for all instances--!
    @load_lock: Lock object, designated for preventing race condition on valuable actions that has to be synchronized !--static for all instances--!
    """

    serviced_path = Service("C:\Program Files\WebScraping\chromedriver.exe")
    bot_email = "your-bot-email@gmail.com"
    bot_email_password = "your-bot-app-password"  # application password for Google account
    port = 465  # ssl protocol port
    mail_lock = Lock()
    save_lock = Lock()
    load_lock = Lock()

    def __init__(self,user,trgt_url):
        """
        Initializing Bot instance.
        :param user: User object, a representation of user and his personal details
        :param trgt_url: str, a target url for the bot to scrape

        Arguments:
        ---------
        :var self.driver: WebDriver object, representing the driver of the bot
        :var self.target_url: str, the target url for the bot to scrape
        :var self.user: User object, a representation of user and his personal details
        """

        super(Bot,self).__init__()  #intializing object as thread for concurrent swiping
        self.driver=None
        self.target_url=trgt_url
        self.user=user

    def send_mail(self, message, target_user) -> None:
        """
        Method that designated for notifying user by mail by using SMTP (Simple Mail Transfer Protocol).
        :param message: str, the message that designated to specific user
        :param target_user: User object, the user that meant to get the message
        :return: None
        """
        self.mail_lock.acquire()
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port=self.port, context=context) as server:
            server.login(self.bot_email, self.bot_email_password)
            server.sendmail(to_addrs=target_user.email, msg=message, from_addr=self.bot_email)
        self.mail_lock.release()

    def reconnect(self,msg,login_func) -> None:
        """
        Method that designated for connection after a loss of connection or some error the occurred while scraping data.
        :param msg: str, a message that supposed to notify to user on error
        :param login_func: func, a function that designated for login
        :return: None
        """
        while True:
            self.driver.refresh()
            time.sleep(2)
            if self.driver.title in ["ציונים - שובל שאבי","דף הבית","אפקה-נט לסטודנט אפקה - המכללה האקדמית להנדסה בתל-אביב",
                                     "אפקה-נט לסטודנט אפקה - המכללה האקדמית להנדסה בתל-אביב רשימת ציונים","מכללת אפקה"]:
                self.driver.close()
                break
        self.send_mail(msg,self.user)
        login_func()  #costumizing different login functions for different bots

    def load_from_file(self,file_name) -> dict:
        """
        Method for loading data from specific file.
        :param file_name:str, file name for saving to (should be json format)
        :return: dict
        """

        # self.load_lock.acquire()
        print(f'loading from file {file_name}...')
        try:
            data_from_file = json.loads(open(file_name, "r").read())
            # self.load_lock.release()
            return data_from_file
        except json.decoder.JSONDecodeError:
            pass

    def save_to_file(self,data,file_name) -> None:
        """
        Method for saving data from specific file.
        :param data:
        :param file_name:
        :return:
        """
        # self.save_lock.acquire()
        print(f'saving to file {file_name}...')
        json.dump(obj=data,fp=open(file_name,"w",encoding='utf-8'),ensure_ascii=False)
        # self.save_lock.release()

class AfekaBot(Bot):
    """
    AfekaBot class that designated to log in Afeknet login page and swiping grades sheet or applications to college secretary.
    """
    def __init__(self,user,trgt_url):
        """
        Initializing AfekaBot instance.
        :param user: User object, a representation of user and his personal details
        :param trgt_url: str, a target url for the bot to scrape
        """
        super(AfekaBot, self).__init__(user,trgt_url)

    def enter_afeka_site(self) -> None:
        """
        Method that designated for Afeka college login.
        :return: None
        """
        print("Entering to afeka...")
        try:
            self.driver.get(self.target_url)
            while self.driver.title != 'אפקה-נט לסטודנט אפקה - המכללה האקדמית להנדסה בתל-אביב':
                WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.XPATH,"//input"))) #finds all input objects within the page
                text_dict = {item.get_property('type'): item for item in self.driver.find_elements(By.XPATH, value='//input') if item.get_property('type') in ['password', 'text']}
                text_dict['text'].send_keys(self.user.username)
                text_dict['password'].send_keys(self.user.password)
                text_dict['password'].send_keys(Keys.RETURN)  # pressing enter to continue to next page
        except (NoSuchElementException, TimeoutException):
            self.reconnect(msg="I failed enter Afeka site, going air soon!",login_func=self.enter_afeka_site)

#*************************************************************************** Grades Bot *****************************************************************************************************#

class GradesBot(AfekaBot):
    """
    GradesBot class that representing scraping bot for grades sheet.
    """
    def __init__(self,user,trgt_url):
        """
        Initializing Bot instance.
        :param user: User object, a representation of user and his personal details
        :param trgt_url: str, a target url for the bot to scrape

        Variables:
        ---------
        :var self.semester_selection: str, representing a user's semester selection (probably current semester)
        :var self.current_courses: dict.
        Has formation of {semester selection:{course name + type course : Course object}}.
        This variable is representing the current unmodifiable courses that has been swiped before.

        :var self.temp_courses:dict
        has formation of {semester selection:{course name + type course : Course object}}
        This variable is representing the lately updated courses that been swiped recently.
        """
        super(GradesBot, self).__init__(user,trgt_url)
        self.semester_selection=user.semester_selection  # index_semester: 1-semester A , 2-semester B , 3-summer semester
        self.current_courses={}
        self.temp_courses={}

    def sweep_grades(self) -> None:
        """
        Method that designated for grades sheet swipe.
        :return: None
        """
        print("Swiping grades...")
        try:
            grades_sheet_btn = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,"רשימת ציונים")))  #Navigating to grades sheet section
            #grades_sheet_btn = self.driver.find_element(by=By.PARTIAL_LINK_TEXT, value="רשימת ציונים")
            grades_sheet_btn.click()

            year_cmb = Select(self.driver.find_element(by=By.ID, value="R1C1"))
            years = year_cmb.options  # fetching all options of year selection as web element
            for i, year in enumerate(years):
                if year.text.__contains__(self.user.year_selection):
                    year_cmb.select_by_index(i)  # selecting the target year
                    break

            semester_cmb = Select(self.driver.find_element(by=By.ID, value="R1C2"))  # fetching semester combobox
            semester_cmb.select_by_index(int(self.semester_selection))  # selecting specific semester
            confirm_btn = self.driver.find_element(by=By.PARTIAL_LINK_TEXT, value="ביצוע")
            confirm_btn.click()

            drop_down = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.ID, 'IMG111')))  #Fetching drop down
            drop_down.click()
            courses_elements = self.driver.find_elements(by=By.XPATH, value="//*[@class='col-md-4 col-xl-3 Father']")   # fetching all courses as card boxes
            if self.semester_selection not in self.temp_courses.keys():
                self.temp_courses[self.semester_selection] = {}
            for web_element in courses_elements:
                element_id = web_element.get_attribute(name="id")
                name_course = web_element.find_element(by=By.XPATH, value=f'//*[@id="{element_id}"]/div/h2')
                type_grade = web_element.find_element(by=By.XPATH, value=f'//*[@id="{element_id}"]/div/div[2]')
                grade = web_element.find_element(by=By.XPATH, value=f'//*[@id="{element_id}"]/div/div[5]/b')
                course = Course(name_course.text, type_grade.text, grade.text)
                self.temp_courses[self.semester_selection][name_course.text + " " + type_grade.text] = course
        except (NoSuchElementException, TimeoutException):
            self.reconnect(msg="I failed for sweeping your grades, going air soon!",login_func=self.enter_afeka_site)

        if not self.current_courses:
            not_coded_json=self.load_from_file(file_name="grades.json")
            if not_coded_json is not None:
                self.current_courses=self.decode_from_json(data_json=not_coded_json,user=self.user)

    def check_if_grades_modified(self) -> None:
        """
        Method that check for grades modification, in case there is one the data gets updated right away and user gets notified on the event.
        :return: None
        """
        if len(self.current_courses) ==0:
            encoded_data = self.encode_to_json(dictionary=self.temp_courses, user=self.user)
            self.save_to_file(data=encoded_data,file_name="grades.json")
            not_coded_json= self.load_from_file(file_name="grades.json")
            self.current_courses=self.decode_from_json(data_json=not_coded_json,user=self.user)
        try:
            flag_changed=False
            for course_name in self.temp_courses[self.semester_selection].keys():
                if self.temp_courses[self.semester_selection][course_name].does_grade_changed(self.current_courses[self.semester_selection][course_name]):
                    self.current_courses[self.semester_selection][course_name].grade = self.temp_courses[self.semester_selection][course_name].grade
                    grade=self.current_courses[self.semester_selection][course_name].grade
                    self.send_mail(message="Subject:New Grade in {}!\n\n"
                                           "Grade: {}".format(course_name,grade).encode('utf-8'),target_user=self.user)
                    flag_changed=True
            if flag_changed:
                encoded_data=self.encode_to_json(dictionary=self.temp_courses, user=self.user)  #saving dictionary as JSON format
                self.save_to_file(data=encoded_data, file_name="grades.json")
        except KeyError:
            self.reconnect(msg="I failed in grade modification checkup, going air soon!",login_func=self.enter_afeka_site)

    def encode_to_json(self, dictionary, user) -> dict:
        """
        Method that encode data of dictionary to serializable json.
        Data will be presented as: {"semester selection":{"course name" + "course type":{"course_name": name,"type_course": type, "grade": grade}}}
        :param dictionary: dict, not serializable object
        :param user: User object
        :return: dict, formatted as json
        """
        temp_dict=deepcopy(dictionary)  #making independent instance of the dictionary that includes objects as well
        for course_name in temp_dict[user.semester_selection].keys():
            course_dict=dictionary[user.semester_selection][course_name].__dict__
            temp_dict[user.semester_selection].update({course_name:course_dict})
        return temp_dict

    def decode_from_json(self, data_json, user):
        """
        Method that decode data of serializable json to dict as presented in the init method.
        Data will be presented as: {semester selection:{course name + course type:Course object}}
        :param data_json: dict, serializable object
        :param user: User object
        :return: dict
        """
        temp_dict=data_json.copy()
        for course_name in data_json[user.semester_selection].keys():
            course_dict=data_json[user.semester_selection][course_name]
            temp_dict[user.semester_selection][course_name]=Course(name=course_dict['name'],type_of_grade=course_dict['type_of_grade'],grade=course_dict['grade'])
        return temp_dict

    #procedure of swiping grades
    def run(self) -> None:
        """
        Functionality of the bot.
        :return: None
        """
        while True:
            self.driver = webdriver.Chrome(service=self.serviced_path)
            self.enter_afeka_site()
            self.sweep_grades()
            self.check_if_grades_modified()
            self.driver.close()
            #self.current_courses[self.user.semester_selection]["6002 אנגלית מתקדמים א' (בינוניים) סופי-הרצאה"].grade="אין פטור"
            time.sleep(1*60)

#***************************************************************************** Application Bot **********************************************************************************************#

class ApplicationBot(AfekaBot):
    """
    ApplicationBot class that representing scraping bot for applications for college secretary.
    """
    def __init__(self,user,trgt_url):
        """
        Initializing AfekaBot instance.
        :param user: User object, a representation of user and his personal details
        :param trgt_url: str, a target url for the bot to scrape

        Variables:
        ---------
        :var self.current_applications: dict.
        Has formation of {no.application:Application object}.
        This variable is representing the current unmodifiable applications that has been swiped before.

        :var self.temp_applications:dict.
        Has formation of {no.application:Application object}.
        This variable is representing the lately updated applications that been swiped recently.
        """
        super(ApplicationBot, self).__init__(user,trgt_url)
        self.current_applications={}
        self.temp_applications={}

    def go_to_applications_sheet(self) -> None:
        """
        Method for locating and entering application page within college site.
        :return: None
        """
        applications = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.PARTIAL_LINK_TEXT,"מעקב פניות")))
        applications.click()

    def swipe_applications(self) -> None:
        """
        Method that designated for swiping applications.
        :return: None
        """
        print("Swiping applications...")
        try:
            all_rows = WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.XPATH,"//*[@role='row']")))
            for row in all_rows:
                columns_elements = [obj for obj in row.find_elements(by=By.XPATH, value="td") if obj.text != ""]
                app_dict = {}
                for element, description in zip(columns_elements, ["description", "date&time", "no.application", "status"]):
                    app_dict.update({description: element.text})
                if app_dict:
                    application = Application(description=app_dict["description"], date_time=app_dict["date&time"], serial_number=app_dict["no.application"], status=app_dict["status"])
                    self.temp_applications[application.serial_number] = application
        except NoSuchElementException:
            self.send_mail("Cannot locate object while swiping applications",self.user)

        if not self.current_applications:
            not_coded_json = self.load_from_file(file_name="applications.json")
            if not_coded_json is not None:
                self.current_applications = self.decode_from_json(not_coded_json)

    def check_if_status_changed(self) -> None:
        """
        Method that designated for checking if any status of any application has been changed, if so the bot will notify it to the relevant user.
        :return: None
        """
        if len(self.current_applications) == 0:
            encoded_data = self.encode_to_json(dictionary=self.temp_applications)
            self.save_to_file(data=encoded_data, file_name="applications.json")
            not_coded_json = self.load_from_file(file_name="applications.json")
            self.current_applications = self.decode_from_json(not_coded_json)
        try:
            flag_changed=False
            for serial_key in self.temp_applications.keys():
                if serial_key not in self.current_applications.keys():  #Entering the new application that appeared in the last swipe
                    self.current_applications.update({serial_key:self.temp_applications[serial_key]})
                    flag_changed=True

                if self.current_applications[serial_key].check_if_modified(self.temp_applications[serial_key]):  #Matching statuses of existing applications
                    self.current_applications[serial_key].status=self.temp_applications[serial_key].status
                    serial_number=self.current_applications[serial_key].serial_number
                    description=self.current_applications[serial_key].description
                    afeka_url=self.target_url
                    #Every argument take place in other brackets by order
                    self.send_mail(message=str("Subject:You got update on application no.{}-{}\n\n"
                                               "Enter to afeka site to see the corresponding!\n"
                                               "Afeka site:{}").format(serial_number,description,afeka_url).encode("utf-8"),target_user=self.user)
                    flag_changed = True

            if flag_changed:
                encoded_data=self.encode_to_json(dictionary=self.temp_applications)
                self.save_to_file(data=encoded_data,file_name="applications.json")
        except KeyError:
            encoded_data = self.encode_to_json(dictionary=self.temp_applications)
            self.save_to_file(data=encoded_data, file_name="applications.json")
            decoded_data=self.load_from_file(file_name="applications.json")
            self.current_applications=self.decode_from_json(data_json=decoded_data)
            self.reconnect(msg="I failed in applications modification checkup, going air soon!",login_func=self.enter_afeka_site)

    def encode_to_json(self, dictionary) -> dict:
        """
        Method that encode data of dictionary to serializable json.
        Data will be presented as: {"no.application":{"description":description,"date_time":date_time,"serial_number":serial_number,"status":status}} , values in inner dict are str.
        :param dictionary: dict,not serializable object
        :return: dict, formatted as json.
        """
        temp_dict=deepcopy(dictionary)  #Making independent instance of the dictionary that includes objects as well
        for serial_number in temp_dict.keys():
            course_dict=dictionary[serial_number].__dict__
            temp_dict.update({serial_number:course_dict})
        return temp_dict

    def decode_from_json(self, data_json) -> dict:
        """
        Method that decode data of dictionary as represented in the init method.
        Data will be presented as: {"no.application":{"description":description,"date_time":date_time,"serial_number":serial_number,"status":status}} , values in inner dict are str.
        :param data_json:dict, serializable object
        :return: dict
        """
        temp_dict=data_json.copy()
        for serial_number in data_json.keys():
            app_dict=data_json[serial_number]
            temp_dict[serial_number]=Application(description=app_dict['description'],date_time=app_dict['date_time'],serial_number=app_dict['serial_number'],status=app_dict['status'])
        return temp_dict

    def run(self) -> None:
        """
        Functionality of the bot.
        :return: None
        """
        while True:
            self.driver = webdriver.Chrome(service=self.serviced_path)
            self.enter_afeka_site()
            self.go_to_applications_sheet()
            self.swipe_applications()
            self.check_if_status_changed()
            self.driver.close()
            #self.current_applications["847092"].status="טיפול"
            time.sleep(1*60)

#*********************************************************************************** Moodle Bot *********************************************************************************************#

class MoodleBot(Bot):
    """
    MoodleBot class that representing scraping bot for assignment and exams grades of a student in Moodle platform.
    """
    def __init__(self,user,trgt_url):
        """
         Initializing MoodleBot instance.
        :param user: User object, a representation of user and his personal details
        :param trgt_url: str, a target url for the bot to scrape

        Variables:
        ---------
        :var self.courses_links: list, representing the upcoming links for course assignments for scraping.

        :var self.current_assignments: dict.
        Has formation of {course name:{assignment name: Course object}}.
        This variable is representing the current unmodifiable assignments that has been swiped before.

        :var self.temp_applications:dict.
        Has formation of {course name:{assignment name: Course object}}.
        This variable is representing the lately updated assignments that been swiped recently.
        """
        super(MoodleBot,self).__init__(user,trgt_url)
        self.courses_links= []
        self.temp_assignments={}
        self.current_assignments={}

    def enter_to_moodle(self) -> None:
        """
        Method that designated for Moodle platform entry.
        :return: None
        """
        try:
            print("Entering Moodle...")
            self.driver.get(self.target_url)  # entering moodle
            WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.NAME,"username")))  # Waiting for page to load
            username = self.driver.find_element(by=By.NAME, value="username")
            password = self.driver.find_element(by=By.NAME, value="password")
            username.send_keys(self.user.username)
            password.send_keys(self.user.password)
            password.send_keys(Keys.RETURN)
        except (NoSuchElementException, TimeoutException):
            self.reconnect(msg="I failed to enter moodle, going on air soon!",login_func=self.enter_to_moodle)

    def select_year_of_swipe(self) -> None:
        """
        Method for selection relevant year of courses.
        :return: None
        """
        try:
            year_element = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.ID,"0")))  # Clicking on year selection list
            year_element.click()
            all_years = self.driver.find_elements(by=By.CLASS_NAME, value="dropdown-item")
            for item in all_years:
                if self.user.year_selection in item.text:
                    item.click()
                    break
        except (NoSuchElementException, TimeoutException):
            self.reconnect(msg="I failed to select year in moodle, going on air soon!", login_func=self.enter_to_moodle)

    def go_to_grades_table(self) -> None:
        """
        Method that designated for locating grade table page and scrape it.
        :return: None
        """
        try:
            # going to grades table
            print("Going to assignments table...")
            properties = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.ID,"usermenu")))
            properties.click()
            grades_btn = self.driver.find_element(by=By.PARTIAL_LINK_TEXT, value="ציונים")
            grades_btn.click()
        except (NoSuchElementException, TimeoutException):
            self.reconnect(msg="I failed to enter grades table in moodlr, going air soon",login_func=self.enter_to_moodle)

    def fetch_all_courses_links(self) -> None:
        """
        Method that fetch all the target course for assignment swipe.
        :return: None
        """
        try:
            grades_table = WebDriverWait(self.driver,10).until(EC.presence_of_element_located((By.ID,"overview-grade")))  # Fetching assignments table
            rows_elements = list(element for element in grades_table.find_elements(by=By.XPATH, value="//table/tbody/tr") if
                                 element.get_attribute("class") != "emptyrow")  # fetching all rows elements and filtering out the empty rows
            links_courses = []
            for element in rows_elements:
                links_courses.append(self.driver.find_element(by=By.XPATH, value=f'//*[@id="{element.get_attribute("id") + "_c0"}"]/a'))
            self.courses_links = links_courses
        except (NoSuchElementException, TimeoutException):
            self.reconnect(msg="I failed to fetch courses links in moodle, going on air soon!", login_func=self.enter_to_moodle)

    def swipe_assignments(self) -> None:
        """
        Method that swipe assignment for each course page.
        :return: None
        """
        try:
            print("Swiping assignments...")
            for item in self.courses_links:
                course_name = item.text
                item.click()  # Entering to course assignments

                assignments_elements = WebDriverWait(self.driver,10).until(EC.presence_of_all_elements_located((By.CLASS_NAME,"gradeitemheader")))  # Fetching assignments elements
                grades_elements = self.driver.find_elements(By.XPATH, value='//*[@class="level2 leveleven item b1b itemcenter  column-grade"]')  # fetching grades elements
                for assignment_name, grade in zip(assignments_elements, grades_elements):
                    if course_name not in self.temp_assignments.keys():
                        self.temp_assignments[course_name] = {}
                    self.temp_assignments[course_name][assignment_name.text] = Course(name=course_name, type_of_grade=assignment_name.text, grade=grade.text)
                self.driver.back()  # Going back to all courses table assignments
        except (NoSuchElementException, TimeoutException):
            self.reconnect(msg="I failed to swipe assignments grades in moodle, going on air soon!", login_func=self.enter_to_moodle)
        if not self.current_assignments:
            not_coded_json = self.load_from_file(file_name="assignments.json")
            if not_coded_json is not None:
                self.current_assignments = self.decode_from_json(not_coded_json)

    def check_if_changed(self) -> None:
        """
        Method that check for modification in assignments and exams.
        :return: None
        """
        print("Checking if assignments changed...")
        if len(self.current_assignments) == 0:
            encoded_data = self.encode_to_json(dictionary=self.temp_assignments)
            self.save_to_file(data=encoded_data, file_name="assignments.json")
            not_coded_json = self.load_from_file(file_name="assignments.json")
            self.current_assignments = self.decode_from_json(not_coded_json)
        try:
            flag_changed = False
            for course_name in self.temp_assignments.keys():
                for assignment in self.temp_assignments[course_name].keys():
                    # In case that some assignment has been added recently
                    if assignment not in self.current_assignments[course_name].keys():
                        self.current_assignments[course_name].update({assignment: self.temp_assignments[course_name][assignment]})
                        flag_changed = True
                    # Checking modification
                    if self.temp_assignments[course_name][assignment].does_grade_changed(self.current_assignments[course_name][assignment]):
                        self.current_assignments[course_name][assignment].grade = self.temp_assignments[course_name][assignment].grade
                        grade=self.temp_assignments[course_name][assignment].grade
                        # Every argument take place in other brackets by order
                        self.send_mail(message="Subject:New assignment grade: {}!\n\n"
                                               "Name of the assignment:{}\n"
                                               "Grade:{}".format(course_name,assignment,grade).encode('utf-8'),target_user= self.user)
                        flag_changed = True
            if flag_changed:
                encoded_data = self.encode_to_json(dictionary=self.temp_assignments)  # saving dictionary as JSON format
                self.save_to_file(data=encoded_data, file_name="assignments.json")
        except KeyError:
            encoded_data = self.encode_to_json(dictionary=self.temp_assignments)
            self.save_to_file(data=encoded_data, file_name="assignments.json")
            decoded_data = self.load_from_file(file_name="assignments.json")
            self.current_assignments = self.decode_from_json(data_json=decoded_data)
            self.reconnect(msg="I failed in assignment grade modification checkup, going air soon!", login_func=self.enter_to_moodle)

    def encode_to_json(self, dictionary) -> dict:
        """
        Method that encode data of dictionary to serializable json.
        Data will be presented as: {"course name":{"assignment name":{"course name" + "course type":{"course_name": name,"type_course": type, "grade": grade}}}}
        :param dictionary: dict, not serializable object
        :return: dict, formatted as json
        """
        temp_dict=deepcopy(dictionary)  #making independent instance of the dictionary that includes objects as well
        for course_name in temp_dict.keys():
            for assignment_name in temp_dict[course_name].keys():
                course_dict = dictionary[course_name][assignment_name].__dict__
                temp_dict[course_name].update({assignment_name: course_dict})
        return temp_dict

    def decode_from_json(self, data_json) -> dict:
        """
        Method that decode data of dictionary as represented in the init method.
        Data will be presented as: {"no.application":{"description":description,"date_time":date_time,"serial_number":serial_number,"status":status}} , values in inner dict are str.
        :param data_json:dict, serializable object
        :return: dict
        """
        temp_dict=data_json.copy()
        for course_name in data_json.keys():
            for assignment_name in data_json[course_name].keys():
                course_dict = data_json[course_name][assignment_name]
                temp_dict[course_name][assignment_name] = Course(name=course_dict['name'], type_of_grade=course_dict['type_of_grade'], grade=course_dict['grade'])
        return temp_dict

    def run(self) -> None:
        """
        Functionality of the bot.
        :return: None
        """
        while True:
            self.driver = webdriver.Chrome(service=self.serviced_path)
            self.enter_to_moodle()
            self.select_year_of_swipe()
            self.go_to_grades_table()
            self.fetch_all_courses_links()
            self.swipe_assignments()
            self.check_if_changed()
            self.driver.close()
            #self.current_assignments["פיזיקה חשמל ומגנטיות תרגול - חמישי 10-12"]["תרגילי בית ל 28/10"].grade=90
            time.sleep(1 * 60)

