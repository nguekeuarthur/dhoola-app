import csv
import os
import firebase_admin
from firebase_admin import credentials, firestore

# Initialiser Firebase
cred = credentials.Certificate("C:/Users/nguek/dhoolaTestFront/myDhoola/myDhoola.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def fetch_parent_document_ids(collection_name, document_name):
    subcollections = db.collection(collection_name).document(document_name).collections()
    data = {}
    for subcollection in subcollections:
        subcollection_name = subcollection.id
        documents = subcollection.stream()
        subcollection_data = []
        for doc in documents:
            subdoc_data = doc.to_dict()
            subcollection_data.append(subdoc_data)
        data[subcollection_name] = subcollection_data
    return data

def fetch_all_collections_except_analyse():
    collections = db.collections()
    data = {}
    for collection in collections:
        collection_name = collection.id
        if collection_name != "Analyse":
            documents = collection.stream()
            collection_data = []
            for doc in documents:
                doc_data = doc.to_dict()
                collection_data.append(doc_data)
            data[collection_name] = collection_data
    return data

def write_data_to_csv(data):
    for collection, documents in data.items():
        if documents:
            filename = f"{collection}.csv"
            # Collecter tous les champs
            all_fieldnames = set()
            for doc in documents:
                all_fieldnames.update(doc.keys())
            fieldnames = list(all_fieldnames)
            
            with open(filename, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                for doc in documents:
                    writer.writerow(doc)

if __name__ == "__main__":
    # Exporter la collection "Analyse"
    collection_name = "Analyse"
    document_names = ["appOpenedTime", "buttonPressedTime", "infos_device", "pageOpenedTime."]
    for doc_name in document_names:
        firebase_data_subcollection = fetch_parent_document_ids(collection_name, doc_name)
        write_data_to_csv(firebase_data_subcollection)
    
    # Exporter toutes les autres collections
    firebase_data_all_collections = fetch_all_collections_except_analyse()
    write_data_to_csv(firebase_data_all_collections)
    
    print("Données extraites et enregistrées dans des fichiers CSV avec succès !")
