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
    path('staff/login/', views.staff_login, name='staff_login'),
    path('staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('staff/search/', views.order_search, name='order_search'),
    path('staff/settings/', views.store_settings, name='store_settings'),

    # 예약 관리
    path('staff/reservations/', views.reservation_list, name='reservation_list'),
    path('staff/reservations/add/', views.reservation_add, name='reservation_add'),
    path('staff/reservations/<int:reservation_id>/', views.reservation_edit, name='reservation_edit'),
    path('api/check-reservation/', views.check_reservation, name='check_reservation'),

    # 가격 관리
    path('staff/oil-prices/', views.oil_price_management, name='oil_price_management'),
    path('staff/services/', views.service_management, name='service_management'),
    path('api/oil-prices/save/', views.oil_price_save, name='oil_price_save'),
    path('api/car-models/add/', views.car_model_add, name='car_model_add'),
    path('api/car-models/<int:model_id>/delete/', views.car_model_delete, name='car_model_delete'),

    # 추가 서비스 관리
    path('api/services/save/', views.service_save, name='service_save'),
    path('api/services/add/', views.service_add, name='service_add'),
    path('api/services/<int:service_id>/delete/', views.service_delete, name='service_delete'),
]
