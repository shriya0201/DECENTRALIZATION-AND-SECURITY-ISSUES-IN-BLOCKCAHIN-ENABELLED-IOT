from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from Blockchain import *
from Block import *
import datetime
import pyaes, pbkdf2, binascii, os, secrets
import base64

blockchain = Blockchain()
if os.path.exists('blockchain_contract.txt'):
    with open('blockchain_contract.txt', 'rb') as fileinput:
        blockchain = pickle.load(fileinput)
    fileinput.close()

def getKey(): #generating key with PBKDF2 for AES
    password = "s3cr3t*c0d3"
    passwordSalt = '76895'
    key = pbkdf2.PBKDF2(password, passwordSalt).read(32)
    return key

def encrypt(plaintext): #AES data encryption
    aes = pyaes.AESModeOfOperationCTR(getKey(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    ciphertext = aes.encrypt(plaintext)
    return ciphertext

def decrypt(enc): #AES data decryption
    aes = pyaes.AESModeOfOperationCTR(getKey(), pyaes.Counter(31129547035000047302952433967654195398124239844566322884172163637846056248223))
    decrypted = aes.decrypt(enc)
    return decrypted

def AccessData(request):
    if request.method == 'GET':
       return render(request, 'AccessData.html', {})	

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def CreateProfile(request):
    if request.method == 'GET':
       return render(request, 'CreateProfile.html', {})

def Agency(request):
    if request.method == 'GET':
       return render(request, 'Agency.html', {})

def Patient(request):
    if request.method == 'GET':
       return render(request, 'Patient.html', {})

def AgencySignup(request):
    if request.method == 'GET':
       return render(request, 'AgencySignup.html', {})

def AgencySignupAction(request):
    if request.method == 'POST':
        user = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        email = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        agency = request.POST.get('t6', False)
        record = 'none'
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                data = base64.b64decode(data)
                data = str(decrypt(data))
                data = data[2:len(data)-1]
                print(data)
                arr = data.split("#")
                if arr[0] == "agency":
                    if arr[1] == user:
                        record = "exists"
                        break
        if record == 'none':
            data = "agency#"+user+"#"+password+"#"+contact+"#"+email+"#"+address+"#"+agency
            enc = encrypt(str(data))
            enc = str(base64.b64encode(enc),'utf-8')
            blockchain.add_new_transaction(enc)
            hash = blockchain.mine()
            b = blockchain.chain[len(blockchain.chain)-1]
            print("Encrypted Data : "+str(b.transactions[0])+" Previous Hash : "+str(b.previous_hash)+" Block No : "+str(b.index)+" Current Hash : "+str(b.hash))
            bc = "Encrypted Data : "+str(b.transactions[0])+" Previous Hash : "+str(b.previous_hash)+"<br/>Block No : "+str(b.index)+"<br/>Current Hash : "+str(b.hash)
            blockchain.save_object(blockchain,'blockchain_contract.txt')
            context= {'data':'Signup process completd and record saved in Blockchain with below hashcodes.<br/>'+bc}
            return render(request, 'AgencySignup.html', context)
        else:
            context= {'data':username+'Username already exists'}
            return render(request, 'AgencySignup.html', context)    
      
def PatientLogin(request):
    if request.method == 'POST':
        pid = request.POST.get('t1', False)
        strdata = '<table border=1 align=center width=100%><tr><th><font size='' color=black>Patient ID</th><th><font size='' color=black>Patient Name</th>'
        strdata+='<th><font size='' color=black>Age</th><th><font size='' color=black>Problem Description</th><th><font size='' color=black>Profile Date</th><th><font size='' color=black>Access Control</th>'
        strdata+='<th><font size='' color=black>Gender</th><th><font size='' color=black>Contact No</th><th><font size='' color=black>Address</th><th><font size='' color=black>Block Chain Hashcode</th></th></tr><tr>'
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                data = base64.b64decode(data)
                data = str(decrypt(data))
                data = data[2:len(data)-1]
                print(data)
                row = data.split("#")
                if row[0] == "patients" and row[1] == pid:
                    strdata+='<td><font size='' color=black>'+str(row[1])+'</td><td><font size='' color=black>'+row[2]+'</td><td><font size='' color=black>'+str(row[3])+'</td><td><font size='' color=black>'+str(row[4])+'</td><td><font size='' color=black>'+str(row[5])+'</td><td><font size='' color=black>'+row[6]+'</td><td><font size='' color=black>'+row[7]+'</td><td><font size='' color=black>'+row[8]+'</td><td><font size='' color=black>'+row[9]+'</td><td>'+str(b.hash)+'</td></tr><tr>'
        context= {'data':strdata}
        return render(request, 'ViewData.html', context)


     

def AgencyLogin(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        utype='none'
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                data = base64.b64decode(data)
                data = str(decrypt(data))
                data = data[2:len(data)-1]
                print(data)
                arr = data.split("#")
                if arr[0] == "agency":
                    if arr[1] == username and arr[2] == password:
                        utype = arr[6]
                        break
        if utype != 'none':
            file = open('session.txt','w')
            file.write(utype)
            file.close()   
            context= {'data':'welcome '+username}
            return render(request, 'AgencyScreen.html', context)
        else:
            context= {'data':'login failed'}
            return render(request, 'Agency.html', context)


def PatientDataAccess(request):
    if request.method == 'GET':
        user = ''
        with open("session.txt", "r") as file:
            for line in file:
                user = line.strip('\n')
        file.close()
        strdata = '<table border=1 align=center width=100%><tr><th><font size='' color=black>Patient ID</font></th><th><font size='' color=black>Patient Name</th>'
        strdata+='<th><font size='' color=black>Age</th><th><font size='' color=black>Problem Description</th><th><font size='' color=black>Profile Date</th>'
        strdata+='<th><font size='' color=black>Access Control</th><th><font size='' color=black>Gender</th><th><font size='' color=black>Contact No</th></th></tr><tr>'
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                data = base64.b64decode(data)
                data = str(decrypt(data))
                data = data[2:len(data)-1]
                row = data.split("#")
                if row[0] == "patients":
                    arr = row[6].split(" ")
                    if len(arr) == 1:
                        if arr[0] == user:
                            strdata+='<td>'+str(row[1])+'</td><td>'+row[2]+'</td><td>'+str(row[3])+'</td><td>'+str(row[4])+'</td><td>'+str(row[5])+'</td><td>'+row[6]+'</td><td>'+row[7]+'</td><td>'+row[8]+'</td></tr><tr>'
                    if len(arr) == 2:
                        if arr[0] == user or arr[1] == user:
                            strdata+='<td>'+str(row[1])+'</td><td>'+row[2]+'</td><td>'+str(row[3])+'</td><td>'+str(row[4])+'</td><td>'+str(row[5])+'</td><td>'+row[6]+'</td><td>'+row[7]+'</td><td>'+row[8]+'</td></tr><tr>'
                    if len(arr) == 3:
                        if arr[0] == user or arr[1] == user or arr[2] == user:
                            strdata+='<td>'+str(row[1])+'</td><td>'+row[2]+'</td><td>'+str(row[3])+'</td><td>'+str(row[4])+'</td><td>'+str(row[5])+'</td><td>'+row[6]+'</td><td>'+row[7]+'</td><td>'+row[8]+'</td></tr><tr>'   
        context= {'data':strdata}
        return render(request, 'ViewAccessData.html', context)
        
def getProfileID():
    count = 0
    for i in range(len(blockchain.chain)):
        if i > 0:
            b = blockchain.chain[i]
            data = b.transactions[0]
            data = base64.b64decode(data)
            data = str(decrypt(data))
            data = data[2:len(data)-1]
            print(data)
            arr = data.split("#")
            if arr[0] == "patientprofile":
                count = count + 1
    count = count + 1            
    return count

def CreateProfileData(request):
    if request.method == 'POST':
        name = request.POST.get('t1', False)
        age = request.POST.get('t2', False)
        problem = request.POST.get('t3', False)
        access_list = request.POST.getlist('t4', False)
        gender = request.POST.get('t5', False)
        contact = request.POST.get('t6', False)
        address = request.POST.get('t7', False)
        count = 0
        access = ''
        for i in range(len(access_list)):
            access+=access_list[i]+" "
        access = access.strip()
        count = getProfileID()
        now = datetime.datetime.now()
        current_time = now.strftime("%Y-%m-%d %H:%M:%S")
        data = "patients#"+str(count)+"#"+name+"#"+age+"#"+problem+"#"+str(current_time)+"#"+str(access)+"#"+gender+"#"+contact+"#"+address
        enc = encrypt(str(data))
        enc = str(base64.b64encode(enc),'utf-8')
        blockchain.add_new_transaction(enc)
        hash = blockchain.mine()
        b = blockchain.chain[len(blockchain.chain)-1]
        print("Encrypted Data : "+str(b.transactions[0])+" Previous Hash : "+str(b.previous_hash)+" Block No : "+str(b.index)+" Current Hash : "+str(b.hash))
        bc = "Encrypted Data : "+str(b.transactions[0])+" Previous Hash : "+str(b.previous_hash)+"<br/>Block No : "+str(b.index)+"<br/>Current Hash : "+str(b.hash)
        blockchain.save_object(blockchain,'blockchain_contract.txt')
        context= {'data':'Signup process completd and record saved in Blockchain with below hashcodes.<br/>'+bc}
        return render(request, 'CreateProfile.html', context)
    







