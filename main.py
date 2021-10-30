
from typing import List
import certifi
from types import MethodType
from pymongo import MongoClient
from bson import ObjectId
import pymongo,json
from flask import Flask,request,jsonify
import math, random
from twilio.rest import Client
from flask_cors import CORS

from bson.timestamp import Timestamp
import datetime as dt



app = Flask(__name__)
CORS(app)
client = MongoClient("mongodb+srv://music2021:music0983460756@cluster0.wjhzl.mongodb.net/myFirstDatabase?retryWrites=true&w=majority",tlsCAFile=certifi.where())

db=client["GoodVendor"]
colpro=db["product"]

#print(list(colpro.find({})))
#print(client.list_database_names())


@app.route('/')
def home():
    return "Hello World restAPI"

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
    account_sid = "AC972c43f1b33f1b1fdf504a65febf75a4"
    auth_token = "a8cd974f91514707bbb8bb959449151a"
    client = Client(account_sid, auth_token)
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
        return {"message":"Login succes","status":True,
                "userinfo":[{"userid": str(result['_id']),
                "name":result['name'],"lastname":result['lastname']}]
                
                }
    else: 
        return{"message":"Login False"}

              

#get user one 
@app.route('/getuser',methods=['GET'])
def getuser():
    userid="617d08cc2d16ea471c1dc5b7"
    result=db.Users.find_one({"_id":ObjectId(userid)})
    return  {    "status":True,
                "userinfo":[{"userid": str(result['_id']),
                "name":result['name'],"lastname":result['lastname']}]
                
                }


#get product from store url 
@app.route('/GetProducts/<string:store_ID>',methods = ['GET'])
def Getproduct(store_ID):   
    product=[]
    for x in colpro.find({'store_ID':store_ID}):
        product.append({"product_id":str(x["_id"]),
                        "product_name":x["proname"],
                        "product_price":x["price"],
                        "product_img":x["pro_img"],
                        "number":0})   
    return jsonify(product)
     


#add product to db  from store
@app.route('/addproduct',methods = ['POST'])
def Addproduct():
    if request.method == 'POST':
        if db.product.find_one({'proname':request.json["proname"]}):
            print(request.json["proname"])
            return {"messags":"product name is Alerdy"}
        else:
            db.product.insert_one({'proname':request.json["proname"],'price':request.json["price"]})
            return {"messags":"Add product success"}



#update data product from store 
@app.route('/putProduct',methods=['PUT'])
def Updateproduct():
    productID=request.args.get('product_id')
    proname=request.json["proname"]
    price=request.json["price"]
    pro_img=request.json["pro_img"]
    prostock=request.json["stock_quantity"]
    result=db.product.update({"_id":ObjectId(productID)} ,{   
            "$set":{        
                "proname":proname,
                "price":price,
                "pro_img":pro_img,
                "stock_quantity":prostock,              
            }      
    })
    if(result):
        return {"messages":"update prodct success productID is"+productID,"status":True}



#post ordrs from user 
@app.route('/post_order/<string:userid>',methods=['POST'])
def postOrder(userid):

    orderlist={
    "userid":userid,
    "bill_id":"GV001",
    "store_ID":"gv034584",
    "date":Timestamp(int(dt.datetime.today().timestamp()), 1),
    "orderstatus":False,
    "order_products":request.json["order_products"],
    "Pickup_time":request.json["Pickup_time"],
    "note":request.json["note"]
    }

    result=db.orders.insert_one(orderlist)
    if(result):
        return {"message":"post order your success id"+userid}

#get orders from user 
@app.route('/getorder/<string:userid>',methods=['GET'])
def getorder(userid):
    orders=[]
    result_orders=db.orders.find({'userid':userid})
    for x in result_orders:
        orders.append({'bill_id':x['bill_id']})
    print(orders) 
    return {"meesage":"getorder success","order":orders}

















if __name__ == '__main__':
    app.run(debug=True,host="localhost",port=5000)
   

