from rest_framework import serializers
from .models import Account,Door,QR,Inside,Camera,ReturnedValueFromScript
from django.contrib.auth.password_validation import validate_password
from rest_framework.response import Response
from rest_framework import status

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model=Account
        #fields=['id','title','author','email']
        fields='__all__'

class UserRegistrSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField()

    class Meta:
        model = Account
        fields = ['id','username', 'password', 'password2','image1','image2','image3','surname','name']

    def save(self, *args, **kwargs):
        user = Account(
            username=self.validated_data['username'],  # Назначаем Логин
        )
        password = self.validated_data['password']
        password2 = self.validated_data['password2']
        if(self.checkUsername(self.validated_data['username'])==False):
            raise serializers.ValidationError({'username': "Username format wrong"})

        if password != password2:
            raise serializers.ValidationError({'password': "Password does not match"})
        user.set_password(password)
        if 'image1' in self.validated_data:
            user.image1=self.validated_data['image1']
            #print("IMAGE1")
        if 'image2' in self.validated_data:
            user.image2 = self.validated_data['image2']
            #print("IMAGE2")
        if 'image3' in self.validated_data:
            user.image3 = self.validated_data['image3']
            #print("IMAGE3")
        if 'name' in self.validated_data:
            user.name = self.validated_data['name']
        if 'surname' in self.validated_data:
            user.surname = self.validated_data['surname']

        user.save()
        return user


    def checkUsername(self,username):
        if (username.isnumeric() == False):
            return False
        if (username[0] == "8"):
            if (len(username) == 11):
                if (username[1] == "7"):
                    return True
        elif (username[0:2] == "+7"):
            if (len(username) == 12):
                if (username[2] == "7"):
                    return True
        return False



class DoorSerializer(serializers.ModelSerializer):
    class Meta:
        model=Door
        fields='__all__'

class QRSerializer(serializers.ModelSerializer):
    class Meta:
        model=QR
        fields='__all__'

class ReturnedValueSerializer(serializers.ModelSerializer):
    class Meta:
        model=ReturnedValueFromScript
        fields='__all__'

class InsideSerializer(serializers.ModelSerializer):

    class Meta:
        model=Inside
        fields='__all__'

class CameraSerializer(serializers.ModelSerializer):

    class Meta:
        model=Camera
        fields='__all__'

class ChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    old_password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = Account
        fields = ( 'password', 'password2','old_password')

    def validate(self, attrs):
        print(attrs['password'])
        print(attrs['password2'])
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def validate_old_password(self, value):
        print(value)
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError({"old_password": "Old password is not correct"})
        return value

    def update(self, instance, validated_data):

        instance.set_password(validated_data['password'])
        instance.save()
        #return Response({"password":"Changed successfully"}, status=status.HTTP_200_OK)
        raise serializers.ValidationError({"changed": True})

        return instance

class UpdateUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('image1', 'image2', 'image3','name','surname')
    def update(self, instance, validated_data):

        if 'name' in self.validated_data:
            instance.name = self.validated_data['name']
        if 'surname' in self.validated_data:
            instance.surname = self.validated_data['surname']
        if 'image1' in self.validated_data:
            instance.image1=self.validated_data['image1']
        if 'image2' in self.validated_data:
            instance.image2=self.validated_data['image2']
        if 'image3' in self.validated_data:
            instance.image3=self.validated_data['image3']
        #instance.set_password(validated_data['password'])
        instance.save()
        #return Response({"password":"Changed successfully"}, status=status.HTTP_200_OK)


        return instance
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.get_token(self.user)
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        #data['id'] = self.user.id

        # Add extra responses here
        data['user'] = {"id":self.user.id,
                        "username":self.user.username,
                        "name": self.user.name,
                        "surname": self.user.surname,
                        #"data_joined": self.user.data_joined,
                        "image1":"/media/"+str(self.user.image1),
                        "image2": "/media/" + str(self.user.image2),
                        "image3": "/media/" + str(self.user.image3),
                        "is_superuser": self.user.is_superuser
                        }


        return data