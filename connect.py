import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
cred = credentials.Certificate("C:/Users/nguek/dhoolaTestFront/myDhoola/myDhoola.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


data = {
    'task' : 'wswswsw'
}

doc_ref = db.collection('taskCollection').document()
doc_ref.set(data)


print('Document ID', doc_ref)