from django.urls import path
from catalog import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.RestaurantListView.as_view(), name='index'),
    path('restaurants/', views.RestaurantListView.as_view(), name='restaurants'),
    path('restaurants/<int:pk>', views.RestaurantDetailView.as_view(), name='restaurant-detail'),
    path('dishes/', views.DishListView.as_view(), name='dishes'),
    path('dishes/<int:pk>', views.DishDetailView.as_view(), name='dish-detail'),
    path('register', views.register, name='Registration'),
    path('adddishes/', views.adddishes, name='adddishes'),
    path('adddishes_form/', views.adddishes_form, name='adddishes_form'),
    path('editrestaurants/<int:pk>', views.editrestaurants, name='editrestaurants'),
    path('comment/<int:pk>', views.add_comment, name='add-comment'),
    path('addrestaurant/', views.addrestaurant, name='addrestaurant'),
    path('adddish/', views.adddish, name='adddish'),
    path('manager/<int:pk>/', views.manager, name='manager'),
    path('applyrestaurant/', views.applyrestaurant, name='applyrestaurant'),
    path('managerlogin', views.managerlogin, name='managerlogin'),
    path('reply/<int:pk>', views.add_reply, name='add-reply'),
    path('editdishes/<int:pk>', views.editdishes, name='editdishes'),
    path('commentdish/<int:pk>', views.add_comment_dish, name='add-comment-dish'),
    path('replydish/<int:pk>', views.add_reply_dish, name='add-reply-dish'),
    path('deleterestaurants/<int:pk>', views.deleterestaurants, name='deleterestaurants'),
    path('deletedishes/<int:pk>', views.deletedishes, name='deletedishes'),
    path('register_manager', views.register_manager, name='Registration_manager'),
]
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)


