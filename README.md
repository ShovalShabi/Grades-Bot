# Grades-Bot
Automation for swiping assignments, quizzes, exam grades, and even track of applications that are sent to the college secretary.

**Why I Wrote this Code?**
One day I had enough that I can't get any notification on assignments, quizzes and exam grades, and even applications!
So I decided that  I'm starting to develop an automated bot that will scrape the grades and applications from my college website (Afeka College of Engineering).

**Functionality**
The bot is absolutely independent and covers almost every corner case that might occur.
Type of grades and application that will be swiped:
-Main courses grades (g.e final grade in a course, exercises grade, and projects grades)
-Application
-Moodle assignments
-Quizzes

There are several types of bots that have polymorphism mechanisms, In addition to the concurrent action of each bot (each bot is represented as a thread).

**Requirements:**
1. Selenium version 4.0.0 (I recommend this version), needs to be installed in the interpreter's settings.
2. Up-to-date Chrome driver, that matches your browser version (google for chrome driver installation and enter the first link that shows up).
3. Add file my keys and within it put your credentials by the order of the arguments in the User class init function.

**Attention**
**This Bot is relevant only for Afeka Students and the bot is up to date for the Afeka website and Moodle for the date 25/10/2022** 
