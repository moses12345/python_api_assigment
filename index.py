from logging import error
from flask.typing import StatusCode
import jwt
import uuid
from flask import Flask,jsonify,request,make_response


app = Flask(__name__)
app.debug = True
app.config['SECRET_KEY'] = 'super-secret'

class User(object):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

    def __str__(self):
        return "User(id='%s')" % self.id

users = []   
advisors = []

def authenticate(email,password):
    for user in users:
        if user['email'] == email and user['password'] == password:
            return user['userid']
    return False
#user
@app.route('/user/register/',methods=['POST'])
def register():
    userid = uuid.uuid4().int
    users.append({"userid":userid,"email":request.json["email"],"name":request.json["name"],"password":request.json["password"]})
    jwttoken = jwt.encode({"email":request.json["email"]},app.config['SECRET_KEY'], algorithm="HS256").decode()
    return make_response(jsonify(jwttoken=jwttoken,uid=userid),200) 


@app.route('/user/login/',methods=['POST'])
def login():
    request_data = request.json
    try:
        if(request_data["email"] and request_data["password"]):
            if(authenticate(request_data["email"],request_data["password"])):
                jwttoken = jwt.encode({"email":request_data["email"]},app.config['SECRET_KEY'], algorithm="HS256").decode()
                return jsonify(data= {"jwttoken":jwttoken , "userid" : authenticate(request_data["email"],request_data["password"])}, status="200_OK"),200
            return jsonify("401_AUTHENTICATION_ERROR"),401    
    except:
        return jsonify("400_BAD_REQUEST"),400  

    return jsonify("400")

@app.route('/user/<int:id>/advisor')
def fetchadvisorbyid(id):
    for adv in advisors:
        if (adv['advisorid']==id):
            return jsonify(status="200_OK",advisor=[adv]),200

    return jsonify("No such advisor on this ID"),400

@app.route('/user/<int:userid>/advisor/<int:advisorid>',methods=['POST'])
def booking(userid,advisorid):
    bookingid = uuid.uuid4().int
    appointments =[]
    for user in users:
        if (user['userid']==userid):      
            appointments.append({"advisorid":advisorid,"BookingId":bookingid,"BookingTime":request.json["BookingTime"]})
            user["appointments"]= appointments  
            return jsonify(status="200_ok")
    return jsonify(status="400")

@app.route('/user/<int:userid>/advisor/booking/')
def fetchbooking(userid):
    userpresent=False
    advisorid=None
    res=None
    appointments=None
    for user in users: 
        if user['userid'] == userid:
            userpresent = True
            appointments=user['appointments']
    if(not userpresent):
        return jsonify(status="400_user not present")

    for appointment in appointments:
        advisorid = appointment['advisorid']
        res={'advisorid':advisorid,"bookingid":appointment['BookingId'],"bookingtime":appointment['BookingTime']}
    for advisor in advisors:
        if advisor['advisorid'] == advisorid:
            res['advisorname'] = advisor['name']
            res['advisorurl'] = advisor['url']    
    return jsonify(data=res,Status="200_ok")


#admin
@app.route("/admin/advisor/",methods=['POST'])
def addanadvisor():
    request_data  = request.json    
    advisorid = uuid.uuid4().int
    try:
        if(request_data["name"] and request_data["url"]):
            advisors.append({"name":request_data["name"],"url":request_data["url"],"advisorid":advisorid})
            return jsonify("200_OK"),200
    except:
        return "400_BAD_REQUEST",400  


if __name__ == '__main__':
    app.run()    