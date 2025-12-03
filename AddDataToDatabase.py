import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred,{
    'databaseURL': "https://faceattendanceproject-e9b0d-default-rtdb.firebaseio.com/",
})

#initializing the root or the {Parent}
ref = db.reference('Students')

# storing information
data = { # key
    "000123": # key / value
        { #value
            "name": "Elon Musk",
            "major": "Robotics",
            "starting_year": 2017,
            "total_attendance": 6,
            "standing": "Good",
            "year": 4,
            "last_attendance_time": "2022-12-11 00:54:34",
        },

    "000143":  # key
        {  # value
            "name": "Clark",
            "major": "Data Science",
            "starting_year": 2021,
            "total_attendance": 32,
            "standing": "Outstanding",
            "year": 3,
            "last_attendance_time": "2024-8-12 10:31:54",
        },

    "000187":  # key
        {  # value
            "name": "Snoop Dog",
            "major": "Weeders",
            "starting_year": 2010,
            "total_attendance": 102,
            "standing": "Poor",
            "year": 69,
            "last_attendance_time": "2019-2-23 14:02:11",
        }
}

# This snippet of code - is to execute all above code into Firebase Database
for key,value in data.items():
    ref.child(key).set(value)