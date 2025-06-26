import os

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

MONGO_DB = 'db_course_scheduling'
MONGO_USERS_COLLECTION = 'users'
MONGO_URLS_COLLECTION = 'urls'
MONGO_LECTURERS_COLLECTION = 'lecturers'
MONGO_COURSES_COLLECTION = 'courses'
MONGO_CLASSES_COLLECTION = 'classes'
MONGO_OPEN_COURSES_COLLECTION = 'open_courses'
MONGO_MAJOR_COLLECTION = 'major'
MONGO_SCHEDULE_COLLECTION = 'schedules'