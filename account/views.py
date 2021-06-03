import requests
from requests.adapters import HTTPAdapter
from rest_framework.decorators import api_view
from urllib3 import Retry
import threading
from .serializers import UserSerializer
from collections import Counter
from rest_framework.views import APIView
import time
from dateutil.parser import parse
from django.utils import timezone
from datetime import datetime
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import UpdateAPIView,CreateAPIView
from rest_framework.permissions import AllowAny
from .models import Account,Door,QR,Inside,Camera,ReturnedValueFromScript
from .serializers import UserRegistrSerializer,DoorSerializer,QRSerializer,InsideSerializer,\
    ChangePasswordSerializer,UpdateUserInfoSerializer,MyTokenObtainPairSerializer,CameraSerializer,\
    ReturnedValueSerializer
import os
from rest_framework import viewsets
#from rest_framework.authentication import JWTAuthentication
from rest_framework.authentication import TokenAuthentication, SessionAuthentication,BasicAuthentication
from rest_framework_simplejwt.views import TokenObtainPairView
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

class IsSuperUser(IsAdminUser):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)

class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = Account.objects.all()

class RegistrUserView(CreateAPIView):
    queryset = Account.objects.all()
    serializer_class = UserRegistrSerializer
    permission_classes = [IsAuthenticated,IsSuperUser]

    def post(self, request, *args, **kwargs):

        serializer = UserRegistrSerializer(data={"username":request.data['username'],
                                          "name":request.data['name'],
                                          "surname":request.data['surname'],
                                          "image1":request.FILES["image1"],
                                          "image2": request.FILES["image2"],
                                          "image3": request.FILES["image3"],
                                          "password":request.data['username'],
                                          "password2": request.data['username'],
                                                 })
        data = {}
        if serializer.is_valid():
            serializer.save()
            #data['response'] = True
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            data = serializer.errors
            return Response(data)
        #put
        #images
        #is_authenticated
        #manager


class UserDetails(APIView):
    permission_classes = [IsAuthenticated]
    def get_object(self, id):
        try:
            return Account.objects.get(id=id)

        except Account.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, id):
        user = self.get_object(id)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self,request,id):
        user = self.get_object(id)
        user.delete()
        return Response({"user_deleted":True},status=status.HTTP_204_NO_CONTENT)

'''
    def put(self, request, id):
        user = self.get_object(id)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''

class ChangePasswordView(UpdateAPIView):
    queryset = Account.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

class UpdateUserInfo(UpdateAPIView):

    queryset = Account.objects.all()
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserInfoSerializer

class UserAPIView(APIView):
    permission_classes = [IsAuthenticated,]

    def get(self,request):
        if request.user.is_superuser:
            # Create the Data Object

            users = Account.objects.all()
            serializer = UserSerializer(users, many=True)
            return Response(serializer.data,status=status.HTTP_200_OK)
        else:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

#RETURNED VALUE
class ReturnedValueSuccess(APIView):
    def get(self, request):
        returned_value = ReturnedValueFromScript.objects.get(id=1)
        serializer = ReturnedValueSerializer(returned_value,data={"returned_value": 0})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReturnedValueError(APIView):
    def get(self, request):
        returned_value = ReturnedValueFromScript.objects.get(id=1)
        serializer = ReturnedValueSerializer(returned_value,data={"returned_value": 1})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReturnedValueNull(APIView):
    def get(self, request):
        returned_value = ReturnedValueFromScript.objects.get(id=1)
        serializer = ReturnedValueSerializer(returned_value,data={"returned_value": -1})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#CAMERA

class CameraDetails(APIView):
    def get(self, request):
        camera = Camera.objects.get(id=1)
        serializer = CameraSerializer(camera)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CameraClose(APIView):
    def get(self, request):
        camera = Camera.objects.get(id=1)
        serializer = CameraSerializer(camera,data={"is_open":False,
                                                   "user_id":None})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#DOOR

class DoorAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    def get(self, request):
        users = Door.objects.all()
        serializer = DoorSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self,request):
        serializer = DoorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def open_gate():
    url = "http://10.200.18.120/io_set_pulse.cgi"
    headers = {
        "Content-Type": "application/x-javascript; charset=windows-1251"
    }
    data = {
        "data": "010a"
    }
    session = requests.Session()
    retry = Retry(connect=1, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    session.auth = ('visor', 'ping')

    session.post(url, headers=headers, data=data)

@api_view(['POST'])
def testing(request):
    open_gate()
    return Response('it worked')




class DoorDetails(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    def get_object(self, id):
        try:
            return Door.objects.get(id=id)

        except Door.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    def get(self, request, id):
        user = self.get_object(id)
        serializer = DoorSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        door = self.get_object(id)
        serializer = DoorSerializer(door, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, {'message': 'Try to scan face again'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id):
        qr = self.get_object(id)
        qr.delete()
        return Response({"door_deleted":True},status=status.HTTP_204_NO_CONTENT)

#QR
''''''
class QRAPIGetView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    def get(self,request):
        qrs = QR.objects.all()
        serializer = QRSerializer(qrs, many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)

class QRAPIView1(APIView):

    def post(self,request):
        serializer = QRSerializer(data=request.data)

        if serializer.is_valid():
            cmd = "python C:/Users/Malika/Desktop/technodom/technodom/1/deep-face-real-time.py "+str(request.data['user_id'])
            returned_value=os.system(cmd)
            door = Door.objects.get(qr_string=request.data['qr_string'])

            user=Account.objects.get(id=request.data['user_id'])
            serializer_user=UserSerializer(user)
            serializer_door = DoorSerializer(door)
            #serializer_user_status = UserSerializer(user, data={"status": "В помещении"})

            if(returned_value==0):
                serializer.save()
                #if(serializer_user_status.is_valid()):
                #    serializer_user_status.save()
                #------------------
                serializer_opendoor = DoorSerializer(door, data={"is_open":True})
                serializer_inside = InsideSerializer(data={"user_id":serializer_user.data['id'],
                                                           "door_id":serializer_door.data['id']})
                if serializer_inside.is_valid():
                    serializer_inside.save()

                if serializer_opendoor.is_valid():
                    serializer_opendoor.save()


                return Response({"open":True},
                                status=status.HTTP_200_OK)
            else:
                return Response({"open":False},
                                status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class QRAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        serializer = QRSerializer(data=request.data)
        #print(request.data)
        #<QueryDict: {'user_id': ['21'], 'qr_string': ['2']}>
        if serializer.is_valid():
            if(int(request.data['qr_string'])<0):
                serializer.save()
                door = Door.objects.get(qr_string=abs(int(request.data['qr_string'])))
                user = Account.objects.get(id=request.data['user_id'])
                serializer_user = UserSerializer(user)
                serializer_door = DoorSerializer(door)

                users_inside = Inside.objects.filter(user_id=request.data['user_id']).order_by('-entry_time')
                users_inside_serializer = InsideSerializer(users_inside, many=True)
                users_inside_new = Inside.objects.get(id=users_inside_serializer.data[0]['id'])
                users_inside_serializer_new = InsideSerializer(users_inside_new, data={"exit_time": datetime.now()
                    , 'spent_time': str(
                        datetime.now() - datetime.strptime(users_inside_serializer.data[0]['entry_time'],
                                                           "%Y-%m-%dT%H:%M:%S.%fZ")),
                                        "door_id_exit":abs(int(request.data['qr_string']))})
                # datetime.strptime(''.join(users_inside_serializer.data[0]['entry_time'].rsplit(':', 1)), '%Y-%m-%dT%H:%S%z')})

                serializer_opendoor = DoorSerializer(door, data={"is_open": True})
                if serializer_opendoor.is_valid():
                    serializer_opendoor.save()
                tr = TestThreading(door)
                if users_inside_serializer_new.is_valid():
                    users_inside_serializer_new.save()
                    result={"is_exit":True,
                            "inside":users_inside_serializer_new.data}
                    return Response(result, status=status.HTTP_200_OK)

            else:
                camera = Camera.objects.get(id=1)
                serializer_camera = CameraSerializer(camera, data={"is_open": True,
                                                            "user_id": request.data['user_id']})
                if serializer_camera.is_valid():
                    serializer_camera.save()
                    returned_value=-1

                    while(returned_value==-1):
                        time.sleep(0.5)
                        returned_value_class = ReturnedValueFromScript.objects.get(id=1)
                        serializer_returned_value = ReturnedValueSerializer(returned_value_class)
                        returned_value=serializer_returned_value.data['returned_value']
                        print("returned_value: -1")

                    returned_value=serializer_returned_value.data['returned_value']


                    door = Door.objects.get(qr_string=request.data['qr_string'])
                    user=Account.objects.get(id=request.data['user_id'])
                    serializer_user=UserSerializer(user)
                    serializer_door = DoorSerializer(door)
                    #serializer_user_status = UserSerializer(user, data={"status": "В помещении"})
                    print("returned_value: "+str(returned_value))
                    if(returned_value==0):
                        serializer.save()

                        #if(serializer_user_status.is_valid()):
                        #    serializer_user_status.save()
                        #------------------
                        serializer_opendoor = DoorSerializer(door, data={"is_open":True})
                        serializer_inside = InsideSerializer(data={"user_id":serializer_user.data['id'],
                                                                   "door_id":serializer_door.data['id']})
                        if serializer_inside.is_valid():
                            serializer_inside.save()

                        if serializer_opendoor.is_valid():
                            serializer_opendoor.save()

                        returned_value_new=ReturnedValueFromScript.objects.get(id=1)
                        returned_value_new_serializer=ReturnedValueSerializer(returned_value_new,{"returned_value":-1})

                        if returned_value_new_serializer.is_valid():
                            returned_value_new_serializer.save()
                        tr = TestThreading(door)
                        return Response({"open":True},
                                        status=status.HTTP_200_OK)
                    else:
                        returned_value_new = ReturnedValueFromScript.objects.get(id=1)
                        returned_value_new_serializer = ReturnedValueSerializer(returned_value_new, {"returned_value": -1})
                        if returned_value_new_serializer.is_valid():
                            returned_value_new_serializer.save()
                        return Response({"open":False},
                                        status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class QRDetails(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    def get_object(self,id):
        try:
            return QR.objects.get(id=id)

        except QR.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    def get(self,request,id):
        qr=self.get_object(id)
        serializer = QRSerializer(qr)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def put(self,request,id):
        qr = self.get_object(id)
        serializer = QRSerializer(qr, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, {'message': 'Try to scan face again'}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id):
        qr = self.get_object(id)
        qr.delete()
        return Response({"qr_deleted":True},status=status.HTTP_204_NO_CONTENT)
class QRExitAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        serializer = QRSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            door = Door.objects.get(qr_string=abs(int(request.data['qr_string'])))
            user = Account.objects.get(id=request.data['user_id'])
            serializer_user = UserSerializer(user)
            serializer_door = DoorSerializer(door)

            users_inside=Inside.objects.filter(user_id=request.data['user_id']).order_by('-entry_time')

            users_inside_serializer=InsideSerializer(users_inside,many=True)
            users_inside_new=Inside.objects.get(id=users_inside_serializer.data[0]['id'])
            users_inside_serializer_new=InsideSerializer(users_inside_new,data={"exit_time":datetime.now()
            ,'spent_time':str(datetime.now()-datetime.strptime(users_inside_serializer.data[0]['entry_time'], "%Y-%m-%dT%H:%M:%S.%fZ")
                )})
                          #datetime.strptime(''.join(users_inside_serializer.data[0]['entry_time'].rsplit(':', 1)), '%Y-%m-%dT%H:%S%z')})





            serializer_opendoor = DoorSerializer(door, data={"is_open": True})

            if serializer_opendoor.is_valid():
                serializer_opendoor.save()

            tr = TestThreading(door)
            if users_inside_serializer_new.is_valid():
                users_inside_serializer_new.save()
                return Response(users_inside_serializer_new.data,status=status.HTTP_200_OK)

class TestThreading(object):

    def __init__(self,door, interval=1):
        self.interval = interval
        self.door=door
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        time.sleep(10)
        door_serializer = DoorSerializer(self.door, data={"is_open": False})
        if door_serializer.is_valid():
            door_serializer.save()



#INSIDE
class UserHistoryAllAPIView(APIView):
    permission_classes = [IsAuthenticated,IsSuperUser]
    def get(self,request):
        ids = Inside.objects.all()
        ids_serializer = InsideSerializer(ids, many=True)
        all_id = []

        for i in range(len(ids_serializer.data)):
            if (ids_serializer.data[i]['user_id'] not in all_id):
                all_id.append(ids_serializer.data[i]['user_id'])

        result = []
        for id in all_id:
            user=Account.objects.get(id=id)
            user_serializer=UserSerializer(user)
            insides=Inside.objects.filter(user_id=id).order_by('-entry_time')
            inside_serializer=InsideSerializer(insides,many=True)
            result.append({'user':user_serializer.data,
                    'history':inside_serializer.data})

        return Response(result, status=status.HTTP_200_OK)

class UserHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated,IsSuperUser]
    def get(self,request,id):

        user=Account.objects.get(id=id)
        user_serializer=UserSerializer(user)
        insides=Inside.objects.filter(user_id=id).order_by('-entry_time')
        inside_serializer=InsideSerializer(insides,many=True)
        result={'user':user_serializer.data,
                'history':inside_serializer.data}

        return Response(result, status=status.HTTP_200_OK)

class InsideStatistics(APIView):
    permission_classes = [IsAuthenticated,IsSuperUser]
    def get(self,request):

        insides = Inside.objects.all()
        insides_serializer = InsideSerializer(insides, many=True)
        seq=[]
        for i in range(len(insides_serializer.data)):
            a=insides_serializer.data[i]['entry_time'].split(":")[0]
            try:
                b=insides_serializer.data[i]['exit_time'].split(":")[0]
            except:
                b=a;
            a_h=a.split("T")[1]
            b_h=b.split("T")[1]
            day=b.split("T")[0]
            #seq.append(a)
            #seq.append(b)
            #print(a)

            for j in range(int(a_h),int(b_h)+1):
                new_time=day+"T"+str(j)
                seq.append(new_time)
                #print(day+"T"+str(j))
            #print(b)
            #print()
        histagram=Counter(seq)
        #print((histagram))
        histagram=dict(sorted(histagram.items(), key=lambda item: int(item[0].split("T")[1])))
        #print((histagram))
        result={}
        w1={};w2={};w3={};w4={};w5={};w6={};w7={}
        for key in histagram.keys():
            num=histagram[key]
            #print(key.split("T")[0])
            w=datetime.strptime(key.split("T")[0], '%Y-%m-%d').strftime('%a')
            key=key.split("T")[1]+":00"
            if(w == "Mon"):
                if (key in w1.values()):
                    w1[key] = num
                else:
                    w1[key] = num
            if (w == "Tue"):
                if (key in w2.values()):
                    w2[key]=num
                else:
                    w2[key]= num
            if (w == "Wed"):
                if (key in w3.values()):
                    w3[key] = num
                else:
                    w3[key] = num
            if (w == "Thu"):
                if (key in w4.values()):
                    w4[key] = num
                else:
                    w4[key] = num
            if (w == "Fri"):
                if (key in w5.values()):
                    w5[key] = num
                else:
                    w5[key] = num
            if (w == "Sat"):
                if (key in w6.values()):
                    w6[key] = num
                else:
                    w6[key] = num
            if (w == "Sun"):
                if (key in w7.values()):
                    w7[key] = num
                else:
                    w7[key] = num
            #print(w,key,num)

        ww1=[];ww2=[];ww3=[];ww4=[];ww5=[];ww6=[];ww7=[]
        for key in w1.keys():
            ww1.append({"hour":key,"index":1,"value":w1[key]})
        for key in w2.keys():
            ww2.append({"hour": key, "index": 1, "value": w2[key]})
        for key in w3.keys():
            ww3.append({"hour":key,"index":1,"value":w3[key]})
        for key in w4.keys():
            ww4.append({"hour":key,"index":1,"value":w4[key]})
        for key in w5.keys():
            ww5.append({"hour":key,"index":1,"value":w5[key]})
        for key in w6.keys():
            ww6.append({"hour":key,"index":1,"value":w6[key]})
        for key in w7.keys():
            ww7.append({"hour":key,"index":1,"value":w7[key]})
        result={"Пн":ww1,"Вт":ww2, "Ср":ww3, "Чт":ww4, "Пт":ww5, "Сб":ww6, "Вс":ww7}
        return Response(result, status=status.HTTP_200_OK)


class UserHistoryByUsernameAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    def post(self,request):
        username = request.data['username']
        user=Account.objects.get(username=username)
        user_serializer=UserSerializer(user)

        insides = Inside.objects.filter(user_id=user_serializer.data['id']).order_by('-entry_time')
        inside_serializer = InsideSerializer(insides, many=True)
        result = {'user': user_serializer.data,
                  'history': inside_serializer.data}

        return Response(result, status=status.HTTP_200_OK)
class UserHistoryLeaveAPIView(APIView):
    permission_classes = [IsAuthenticated,IsSuperUser]
    def get(self,request,boo):
        ids=Inside.objects.all()
        ids_serializer=InsideSerializer(ids,many=True)
        all_id=[]

        for i in range(len(ids_serializer.data)):
            if(ids_serializer.data[i]['user_id'] not in all_id):
                all_id.append(ids_serializer.data[i]['user_id'])
        print(all_id)

        result=[]
        for id in all_id:
            user=Account.objects.get(id=id)
            user_serializer=UserSerializer(user)
            insides=Inside.objects.filter(user_id=id).order_by('-entry_time')
            inside_serializer=InsideSerializer(insides,many=True)
            result_user={'user':user_serializer.data,
                    'last_entrance':inside_serializer.data[0]}
            result.append(result_user)
        result_fin=[]
        if(boo==0):
            for i in range(len(result)):
                if(result[i]['last_entrance']['exit_time']==None):
                    result_fin.append(result[i])
        if(boo==1):
            for i in range(len(result)):
                if(result[i]['last_entrance']['exit_time']!=None):
                    result_fin.append(result[i])
        return Response(result_fin, status=status.HTTP_200_OK)

class InsideAPIViewUserWithName(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    
    def get(self,request):
        user_array=[]
        user_dict={}
        users=Account.objects.all()
        serializerUser=UserSerializer(users, many=True)
        usersInside = Inside.objects.all().order_by('-entry_time')
        serializerInside = InsideSerializer(usersInside, many=True)
        for inside_user in serializerInside.data:
            #print(inside_user['user_id'])
            user_all=Account.objects.get(id=inside_user['user_id'])
            user_all_ser=UserSerializer(user_all)
            #user_array.append(user_all_ser.data)
            user_dict={"id":inside_user['id'],
                      "user_id":inside_user['user_id'],
                      "entry_time":inside_user['entry_time'],
                       "exit_time": inside_user['exit_time'],
                       "spent_time": inside_user['spent_time'],
                      "name":user_all_ser.data['name'],
                       "surname": user_all_ser.data['surname'],
                       "username": user_all_ser.data['username']

                      }
            user_array.append(user_dict)
        return Response(user_array,status=status.HTTP_200_OK)
class InsideAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]

    def get(self,request):
        user_array=[]
        user_dict={}
        users=Account.objects.all()
        serializerUser=UserSerializer(users, many=True)
        usersInside = Inside.objects.all()
        serializerInside = InsideSerializer(usersInside, many=True)
        for inside_user in serializerInside.data:
            #print(inside_user['user_id'])
            user_all=Account.objects.get(id=inside_user['user_id'])
            user_all_ser=UserSerializer(user_all)
            #user_array.append(user_all_ser.data)
            user_dict={"id":inside_user['id'],
                      "user_id":inside_user['user_id'],
                      "entry_time":inside_user['entry_time'],
                       "exit_time": inside_user['exit_time'],
                       "spent_time": inside_user['spent_time'],
                      "user":user_all_ser.data
                      }
            user_array.append(user_dict)
        return Response(user_array,status=status.HTTP_200_OK)

    def post(self,request):
        serializer = InsideSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InsideDetails(APIView):
    permission_classes = [IsAuthenticated, IsSuperUser]
    def get_object(self,id):
        try:
            return Inside.objects.get(id=id)

        except Inside.DoesNotExist:
            return HttpResponse(status=status.HTTP_404_NOT_FOUND)

    def get(self,request,id):
        user=self.get_object(id)
        serializer = InsideSerializer(user)
        return Response(serializer.data,status=status.HTTP_200_OK)

    def put(self,request,id):
        user = self.get_object(id)
        serializer = InsideSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data,status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self,request,id):
        user = self.get_object(id)
        user.delete()
        return Response({"inside_deleted":True},status=status.HTTP_204_NO_CONTENT)

def do_something():
    returned_value = ReturnedValueFromScript.objects.get(id=1)
    serializer = ReturnedValueSerializer(returned_value, data={"returned_value": -1})
    if serializer.is_valid():
        serializer.save()

    camera = Camera.objects.get(id=1)
    serializer = CameraSerializer(camera, data={"is_open": False,
                                                "user_id": None})
    if serializer.is_valid():
        serializer.save()
    #requests.get(api_url + "api/returned_value_null/")
    print("Start")
