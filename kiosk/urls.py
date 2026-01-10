from django.urls import path
from . import views

urlpatterns = [
    # 고객용 키오스크
    path('', views.start, name='start'),
    path('car/', views.select_car, name='select_car'),
    path('oil/', views.select_oil, name='select_oil'),
    path('service/', views.select_service, name='select_service'),
    path('estimate/', views.estimate, name='estimate'),
    path('complete/', views.order_complete, name='order_complete'),

    # API
    path('api/order/create/', views.create_order, name='create_order'),
    path('api/order/<int:order_id>/send-alimtalk/', views.send_alimtalk, name='send_alimtalk'),

    # 직원용
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('staff/search/', views.order_search, name='order_search'),
    path('staff/settings/', views.store_settings, name='store_settings'),
]
