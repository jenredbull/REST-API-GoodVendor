
from types import MethodType
import pymongo,json
from pymongo import MongoClient
from flask import Flask,request
import math, random
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
app = Flask(__name__)

client = MongoClient()
db=client["GoodVendor"]

#print(client.list_database_names())


@app.route('/api')
def home():
    return "Hello World"


def genotp():    
    digits = "0123456789"
    OTP = ""
    for i in range(4) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

def addNumberUser(phonenumber,otp):
    db.user.insert_one({'numberphone':phonenumber,'otp':otp})
    
#generate OTP 
@app.route('/GetOTP',methods=['POST'])
def enerateOTP() :    
    numberphone=request.json["numberphone"]  
    otp=genotp()
    account_sid = "AC972c43f1b33f1b1fdf504a65febf75a4"
    auth_token = "5d6a71159871486360bad3976e31778f"
    client = Client(account_sid, auth_token)
    client.api.account.messages.create(
    to="+66"+numberphone,
    from_="+13868537656",
    body="Your OTP : "+str(otp))
    addNumberUser(numberphone,otp)
    return {"message":"SEND OTP To mobile"}
   

#add user to DB 
@app.route('/Adduser',methods=['POST'])
def Adduser():
    if request.method == 'POST':
        email=request.json["email"]
        name=request.json["name"]
        lastname=request.json["lastname"]
        phoneNumber=request.json["phoneNumber"]
        return {"email":email,"name":name,"lastname":lastname,"phoneNumber":phoneNumber}


#get product from shop url 
@app.route('/GetProduct',methods = ['GET'])
def Getproduct():
     if request.method == 'GET':
        return 


#add product to db 
@app.route('/addproduct',methods = ['POST'])
def Addproduct():
    if request.method == 'POST':
        if db.product.find_one({'proname':request.json["proname"]}):
            print(request.json["proname"])
            return {"messags":"product name is Alerdy"}
        else:
            db.product.insert_one({'proname':request.json["proname"],'price':request.json["price"]})
            return {"messags":"Add product success"}


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='localhost')
   

