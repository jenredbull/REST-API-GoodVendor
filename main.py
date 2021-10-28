
from types import MethodType
from flask.wrappers import Response
import pymongo,json
from pymongo import MongoClient
from flask import Flask,request,jsonify
import math, random
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
app = Flask(__name__)


client = MongoClient()
db=client["GoodVendor"]

colpro=db["product"]

account_sid = "AC972c43f1b33f1b1fdf504a65febf75a4"
auth_token = "c7bf4cf3c0472e0ac76acac3205e4212"
client = Client(account_sid, auth_token)

#print(client.list_database_names())


@app.route('/')
def home():
    return "Hello World resAPI"

def genotp():    
    digits = "0123456789"
    OTP = ""
    for i in range(4) :
        OTP += digits[math.floor(random.random() * 10)]
    return OTP

#function for veryfy OTP 
def addNumberPhoneUser(phonenumber,otp):
    db.OTP.insert_one({'numberphone':phonenumber,'otp':otp})


#generate OTP 
@app.route('/LoginOTP',methods=['POST'])
def enerateOTP() :    
    numberphone=request.json["numberphone"]  
    otp=genotp()
    client.api.account.messages.create(
    to="+66"+numberphone,
    from_="+13868537656",
    body="Your OTP : "+str(otp))
    addNumberPhoneUser(numberphone,otp)
    return {"message":"please check OTP SentTo Your mobilephone +66"+numberphone}
   
#verify OTP 
@app.route('/verifyOTP',methods=['POST'])
def VerifyOTP():
    numberphone=request.json["numberphone"]
    OTPconfirm=request.json["confirmOTP"]
    result=db.OTP.find_one({'numberphone':numberphone,'otp':OTPconfirm})
    if(result):             
        return {"status":True,"numberphone":numberphone}
    else:
        return {"message":" please verify your OTP agian!!"}


#add user to DB 
@app.route('/Adduser',methods=['POST'])
def Adduser():
    if request.method == 'POST':
        email=request.json["email"]
        password=request.json["password"]
        name=request.json["name"]
        lastname=request.json["lastname"]
        phoneNumber=request.json["numberphone"]
        if(db.Users.find_one({'email':email,'numberphone':phoneNumber})):
            return {"messages":"email and phoneNumber has registered"}
        else:
            result=db.Users.insert_one({"email":email,"password":password,"name":name,"lastname":lastname,"numberphone":phoneNumber})
            if(result):
                return {"messages":"Successful registration"}
      
#login 
@app.route('/Login',methods=['POST'])
def Login():
    email=request.json["email"]
    password=request.json["password"]
    result=db.Users.find_one({'email':email,'password':password})
    if(result):
        print(result)
    return {"message":"Login succesfuly"}



#get user 
@app.route('/getuser',methods=['POST'])
def getuser():
    
    return {}


#get product from shop url 
@app.route('/GetProducts',methods = ['GET'])
def Getproduct():
    product=[]
    for x in colpro.find():
        product.append({"product_id":str(x["_id"]),"product_name":x["proname"],"product_price":x["price"],"product_img":x["pro_img"],"number":0})   
    return jsonify(product)
     

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
    app.run(debug=True)
   

