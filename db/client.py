from pymongo import MongoClient

# Descomentar quando senha fica codificada
# db_client = MongoClient(host = "mongodb+srv://db_timer_nicot:<db_password>@cluster0.zprfax4.mongodb.net/?appName=Cluster0")   

db_client = MongoClient("mongodb+srv://db_timer_nicot:X5rrYhC8uFVsY4V2@cluster0.zprfax4.mongodb.net/?appName=Cluster0").db_timer_nicot

# db_client = MongoClient("mongodb+srv://nicotafle:cook1312@cluster0.9yqopqd.mongodb.net/?appName=Cluster0").nicotafle
