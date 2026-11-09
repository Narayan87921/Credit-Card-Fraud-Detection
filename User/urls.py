from django.urls import path 
from .import views 

urlpatterns = [
    path('',views.index,name='index'),
    path('register',views.register,name='reg'),
    path('login',views.login,name='login'),
    path('data',views.data,name='data'),
    path('predict',views.predict,name='predict'),
    path('logout',views.logout,name='logout'),
    path('adminlogin',views.adminlogin,name='adminlogin'),
    path('adminhome',views.adminhome,name='adminhome'),
    path('delete_history/<int:id>', views.delete_history, name='delete_history'),
    path('delete_all_history', views.delete_all_history, name='delete_all_history'),
]
