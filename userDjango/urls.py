"""userDjango URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from account.views import RegistrUserView,UserAPIView,DoorDetails,DoorAPIView,QRDetails,QRAPIView,QRAPIGetView,UserViewSet,\
    UserDetails,ChangePasswordView,UpdateUserInfo,MyTokenObtainPairView,CameraClose,ReturnedValueError,ReturnedValueSuccess,\
    CameraDetails,ReturnedValueNull,InsideAPIView,InsideDetails,UserHistoryAPIView,UserHistoryLeaveAPIView,UserHistoryByUsernameAPIView,\
UserHistoryAllAPIView,InsideAPIViewUserWithName,InsideStatistics

from rest_framework.routers import DefaultRouter
from account.views import do_something
from account import views
from userDjango import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,TokenVerifyView
)
router=DefaultRouter()
router.register('user',UserViewSet,basename='user')

do_something()
urlpatterns = [
    path('admin/', admin.site.urls),

    #QR
    path('api/qr/', QRAPIGetView.as_view()),#getQRList
    path('api/qr/<int:id>/',QRDetails.as_view()),#getQRById,put,delete
    path('api/send_qr/',QRAPIView.as_view()),#postQR user_id door_id
    #path('api/send_qr_exit/',QRExitAPIView.as_view()),

    #Returned Value
    path('api/returned_value_success/',ReturnedValueSuccess.as_view()),
    path('api/returned_value_not_found/',ReturnedValueError.as_view()),
    path('api/returned_value_null/',ReturnedValueNull.as_view()),

    #Door
    path('api/door/<int:id>/',DoorDetails.as_view()),#getDoorById,put,delete
    path('api/door/',DoorAPIView.as_view()),#getDoorList,post

    #Camera
    path('api/camera/',CameraDetails.as_view()),#get,put Camera
    path('api/camera/close/',CameraClose.as_view()),#get/close


    #authorization token
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),

    #USER
    path('api/viewset/',include(router.urls)),#api for ml script
    path('api/viewset/<int:pk>/',include(router.urls)),#api for ml script
    path('api/users/<int:id>/', UserDetails.as_view()),  # getUserById,put,delete
    #path for regstrating users
    path('api/registration/', RegistrUserView.as_view(), name='registr'),#post
    #changnig password
    path('api/change_password/<int:pk>/', ChangePasswordView.as_view(), name='auth_change_password'),

    path('api/update_user_info/<int:pk>/', UpdateUserInfo.as_view(), name='auth_change_image'),
    #path for displaying users
    path('api/users/', UserAPIView.as_view(), name='users'),#getUserList
    path('api/turnstile/', views.testing),

    #insides
    path('api/insides/all_history/', InsideAPIViewUserWithName.as_view()),

    path('api/insides/', InsideAPIView.as_view(), name='users'),
    path('api/insides/<int:id>/', InsideDetails.as_view()),  # getUserById,put,delete
    path('api/insides/history/<int:id>/',UserHistoryAPIView.as_view()),
    path('api/insides/history_by_username/',UserHistoryByUsernameAPIView.as_view()),
    path('api/insides/history/',UserHistoryAllAPIView.as_view()),


    path('api/insides/leave/<int:boo>/',UserHistoryLeaveAPIView.as_view()),
    path('api/insides/statistics/',InsideStatistics.as_view())

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
