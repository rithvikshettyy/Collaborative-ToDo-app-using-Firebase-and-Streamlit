import pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyDrY0_UyjkoUJKfc3TAtwMEmbHScgW-KLk",
    "authDomain": "todo-collab-e2c15.firebaseapp.com",
    "databaseURL": "https://todo-collab-e2c15-default-rtdb.firebaseio.com",
    "projectId": "todo-collab-e2c15",
    "storageBucket": "todo-collab-e2c15.firebasestorage.app",
    "messagingSenderId": "71667769805",
    "appId": "1:71667769805:web:a68c323ef99b7ce35f6484",
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
db = firebase.database()
