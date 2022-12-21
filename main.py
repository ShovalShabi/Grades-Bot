import sys
import MyKeys

from User import User
from all_bots import GradesBot, ApplicationBot, MoodleBot

if __name__ == '__main__':
    print("*** Started Session ***",file=sys.stderr)
    user=User(username=MyKeys.afeka_username,user_email=MyKeys.user_email,user_password=MyKeys.user_password,year_selection="2023",semester_selection="1")
    grades_bot = GradesBot(user,"https://yedion.afeka.ac.il/yedion/fireflyweb.aspx")
    application_bot = ApplicationBot(user,"https://yedion.afeka.ac.il/yedion/fireflyweb.aspx")
    moodle_bot = MoodleBot(user,"https://moodle.afeka.ac.il/my/")
    threads=[grades_bot,application_bot,moodle_bot]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

