from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_protect
from django.contrib import auth
from os import path
import sys
import pyrebase
from cryptography.fernet import Fernet
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

sys.path.append(path.abspath('C:\\Users\\gampa\\PycharmProjects\\MajorProject\\venv'))

import Predicting

firebaseConfig = {
    "apiKey": "AIzaSyCI0GZMQ--po_58Z14R-EfmKG0WVghIjD8",
    "authDomain": "majorprojectretinopathy.firebaseapp.com",
    "databaseURL": "https://majorprojectretinopathy.firebaseio.com",
    "projectId": "majorprojectretinopathy",
    "storageBucket": "majorprojectretinopathy.appspot.com",
    "messagingSenderId": "412783744974",
    "appId": "1:412783744974:web:7b8122021d618f82113d9f",
    "measurementId": "G-S3XQEZD3VD"
}

firebase = pyrebase.initialize_app(firebaseConfig)
authentication = firebase.auth()
database = firebase.database()
storage = firebase.storage()
# Create your views here.


def home(request):
    return render(request, "Retinopathy.html")


def history(request):
    if 'uid' not in request.session:
        return HttpResponse("0")
    else:
        return render(request, "history.html")


@csrf_protect
def predicting(request):
    name=request.POST.get("img", "").split("\\")[-1]
    print(name)
    ans = Predicting.predict(name)
    request.session['prediction'] = str(ans)
    return HttpResponse(ans)


@csrf_protect
def signIn(request):
    email = request.POST.get("email")
    pwd = request.POST.get("pwd")
    try:
        user = authentication.sign_in_with_email_and_password(email, encryption(pwd))
        print(user)
    except:
         return HttpResponse("0")
    print("test")
    session_id = user['localId']
    request.session['uid']=str(session_id)
    print(request.session['uid'])
    name = database.child(request.session['uid']).child('name').get()
    name = database.child(request.session['uid']).child('name').get()
    print(name.val())
    status = "1," + str(name.val())
    return HttpResponse(status)

@csrf_protect
def signUp(request):
    name = request.POST.get("name")
    email = request.POST.get("email")
    pwd = request.POST.get("pwd")
    try:
        user = authentication.create_user_with_email_and_password(email, encryption(pwd))
    except:
        return HttpResponse("-1")
    uid = user['localId']
    print("signUp")
    data = {"name":name,"imgcnt":0}
    database.child(uid).set(data)
    return HttpResponse("1")


def logout(request):
    auth.logout(request)
    return HttpResponseRedirect("/")


def session(request):
    try:
        name = database.child(request.session['uid']).child('name').get()
    except:
        return HttpResponse("0")
    name = database.child(request.session['uid']).child('name').get()
    return HttpResponse("1,"+str(name.val()))

@csrf_protect
def save(request):
    print("saving...")
    if 'uid' not in request.session:
        return HttpResponse("0")
    else:
        name = request.POST.get("img", "").split("\\")[-1]
        test_dir = "C:\\Users\\gampa\Desktop\\aptos2019-blindness-detection\\test_images\\"
        file = open(test_dir + name, "rb")
        data = {'img': name,'prediction':str(request.session['prediction'])}
        imgcnt = int(database.child(request.session['uid']).child('imgcnt').get().val())+1
        database.child(request.session['uid']).child(str(imgcnt)).set(data)
        database.child(request.session['uid']).update({"imgcnt": imgcnt})
        storage.child("images/"+name).put((test_dir + name), request.session['uid'])
        return HttpResponse("1")


def getData(request):
    data = database.child(request.session['uid']).get().val()
    data = database.child(request.session['uid']).get().val()
    print(request.session['uid'])
    print(data)
    data = list(data.items())
    tabledata=""
    table = "<table id='data-content'><th style='text-align:center'>Image</th><th style='text-align:center'>Severity</th>"
    chart = ""
    for i in data:
        i = list(i)[-1]
        severity=""
        if type(i) == type({"test": "test"}):
            if i['prediction']=='0':
                severity="No DR"
            elif i['prediction'] == '1':
                severity = "Mild"
            elif i['prediction'] == '2':
                severity = "Moderate"
            elif i['prediction'] == '3':
                severity = "Severe"
            elif i['prediction'] == '4':
                severity = "Proliferative DR"
            tabledata += "<tr style='text-align:center'><td><div  class='pic'>" + i['img'].split(".")[0] + "</div></td><td>" + \
                     severity+"("+ i['prediction']+")"+ "</td></tr>"
            chart += (i['img'].split(".")[0]+":"+str(i['prediction'])+",")
    if(len(tabledata)==0):
        tabledata="<tr style='text-align:center'><td colspan=2>No Results Found</td></tr>"
        chart="0:0,"
    table += (tabledata+"</table>")
    return HttpResponse(table+"@"+ str(chart))


def getPic(request):
    picname = request.POST.get('img')
    pic = str(picname)+".png"
    url = storage.child("images/"+pic).get_url(request.session['uid'])
    return HttpResponse(url)


def encryption(pwd):
    password = pwd.encode()
    salt = b'Z(X\xc0\xe6\x02>\xf4\xb7\xfc\xfdI\xef\xe8\x98J'
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password))
    return str(key)