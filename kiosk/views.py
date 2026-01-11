import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import date, datetime, timedelta
from .models import CarBrand, CarModel, FuelType, EngineOil, AdditionalService, ServiceOrder, ServiceOrderItem, StoreSettings, Customer, Reservation
from .services import send_service_complete_message


def start(request):
    """시작 페이지 - 차량번호 입력"""
    return render(request, 'start.html')


def select_car(request):
    """차종 선택 페이지 (브랜드/차종/연료 한 페이지에서)"""
    car_number = request.GET.get('car_number', '')
    brands = CarBrand.objects.prefetch_related('models').all()
    fuel_types = FuelType.objects.all()

    # JSON 데이터 준비 (JavaScript에서 즉시 사용)
    brands_data = []
    for brand in brands:
        brands_data.append({
            'id': brand.id,
            'name': brand.name,
            'models': [{'id': m.id, 'name': m.name} for m in brand.models.all()]
        })

    fuels_data = [{'id': f.id, 'name': f.name} for f in fuel_types]

    context = {
        'car_number': car_number,
        'brands': brands,
        'brands_json': json.dumps(brands_data, ensure_ascii=False),
        'fuels_json': json.dumps(fuels_data, ensure_ascii=False),
    }
    return render(request, 'select_car.html', context)


def select_oil(request):
    """엔진오일 선택 페이지"""
    car_number = request.GET.get('car_number', '')
    brand_id = request.GET.get('brand')
    model_id = request.GET.get('model')
    fuel_id = request.GET.get('fuel')

    brand = get_object_or_404(CarBrand, id=brand_id) if brand_id else None
    car_model = get_object_or_404(CarModel, id=model_id) if model_id else None
    fuel_type = get_object_or_404(FuelType, id=fuel_id) if fuel_id else None

    # 국산 브랜드 목록
    domestic_brands = ['현대', '기아', '제네시스', 'KG모빌리티', '르노코리아']
    is_domestic = brand.name in domestic_brands if brand else True

    # 오일 티어 데이터 (가이드라인 기반)
    all_oil_tiers = [
        {
            'id': 'economy',
            'name': '이코노미',
            'price': 50000,
            'oil_type': '합성유',
            'tagline': '경제적인 선택, 일반 주행에 적합',
            'product_name': 'Kixx DX5',
            'badge': None,
            'badge_type': None,
            'free_services': ['타이어 공기압 체크'],
        },
        {
            'id': 'standard',
            'name': '스탠다드',
            'price': 70000,
            'oil_type': '고급 합성유',
            'tagline': '균형 잡힌 성능과 보호',
            'product_name': 'Kixx GX7',
            'badge': None,
            'badge_type': None,
            'free_services': ['타이어 공기압 체크', '워셔액 보충'],
        },
        {
            'id': 'premium',
            'name': '프리미엄',
            'price': 90000,
            'oil_type': 'PAO 합성유',
            'tagline': '고급 합성유, 향상된 엔진 보호와 연비',
            'product_name': 'Kixx PAO',
            'badge': '추천',
            'badge_type': 'recommended',
            'free_services': ['타이어 공기압 체크', '워셔액 보충', '에어컨 필터 점검'],
        },
        {
            'id': 'hyperformance',
            'name': '하이퍼포먼스',
            'price': 120000,
            'oil_type': '에스터 합성유',
            'tagline': '최고급 전합성유, 고출력 엔진에 최적화',
            'product_name': '리스타 슈퍼노멀',
            'badge': '🔥 인기',
            'badge_type': 'popular',
            'free_services': ['타이어 공기압 체크', '워셔액 보충', '에어컨 필터 점검', '실내 간단 청소'],
        },
        {
            'id': 'racing',
            'name': '레이싱',
            'price': 150000,
            'oil_type': '최고급 에스터',
            'tagline': '극한 성능, 스포츠카 및 튜닝카 전용',
            'product_name': '리스타 메탈로센',
            'badge': '💎 최고급',
            'badge_type': 'premium',
            'free_services': ['타이어 공기압 체크', '워셔액 보충', '에어컨 필터 점검', '실내 간단 청소', '엔진룸 클리닝'],
        },
    ]

    # 수입차는 프리미엄부터만 표시
    if is_domestic:
        oil_tiers = all_oil_tiers
    else:
        oil_tiers = [t for t in all_oil_tiers if t['id'] in ['premium', 'hyperformance', 'racing']]

    context = {
        'car_number': car_number,
        'brand': brand,
        'car_model': car_model,
        'fuel_type': fuel_type,
        'oil_tiers': oil_tiers,
        'is_domestic': is_domestic,
        'brand_id': brand_id,
        'model_id': model_id,
        'fuel_id': fuel_id,
    }
    return render(request, 'select_oil.html', context)


def select_service(request):
    """추가 서비스 선택 페이지"""
    car_number = request.GET.get('car_number', '')
    brand_id = request.GET.get('brand')
    model_id = request.GET.get('model')
    fuel_id = request.GET.get('fuel')
    oil_tier_id = request.GET.get('oil')

    brand = get_object_or_404(CarBrand, id=brand_id) if brand_id else None
    car_model = get_object_or_404(CarModel, id=model_id) if model_id else None
    fuel_type = get_object_or_404(FuelType, id=fuel_id) if fuel_id else None

    # 오일 티어 데이터
    oil_tiers_map = {
        'economy': {'name': '이코노미', 'price': 50000, 'product_name': 'Kixx DX5'},
        'standard': {'name': '스탠다드', 'price': 70000, 'product_name': 'Kixx GX7'},
        'premium': {'name': '프리미엄', 'price': 90000, 'product_name': 'Kixx PAO'},
        'hyperformance': {'name': '하이퍼포먼스', 'price': 120000, 'product_name': '리스타 슈퍼노멀'},
        'racing': {'name': '레이싱', 'price': 150000, 'product_name': '리스타 메탈로센'},
    }

    oil_tier = oil_tiers_map.get(oil_tier_id, {})
    oil = type('Oil', (), {
        'name': oil_tier.get('name', ''),
        'price': oil_tier.get('price', 0),
        'product_name': oil_tier.get('product_name', ''),
    })()

    services = AdditionalService.objects.filter(is_active=True)

    # JSON for JavaScript
    services_data = [{'id': s.id, 'name': s.name, 'description': s.description, 'price': s.price} for s in services]

    context = {
        'car_number': car_number,
        'brand': brand,
        'car_model': car_model,
        'fuel_type': fuel_type,
        'oil': oil,
        'services': services,
        'services_json': json.dumps(services_data, ensure_ascii=False),
        'brand_id': brand_id,
        'model_id': model_id,
        'fuel_id': fuel_id,
        'oil_id': oil_tier_id,
    }
    return render(request, 'select_service.html', context)


def estimate(request):
    """견적서 페이지"""
    car_number = request.GET.get('car_number', '')
    brand_id = request.GET.get('brand')
    model_id = request.GET.get('model')
    fuel_id = request.GET.get('fuel')
    oil_tier_id = request.GET.get('oil')
    service_ids = request.GET.get('services', '')

    brand = get_object_or_404(CarBrand, id=brand_id) if brand_id else None
    car_model = get_object_or_404(CarModel, id=model_id) if model_id else None
    fuel_type = get_object_or_404(FuelType, id=fuel_id) if fuel_id else None

    # 오일 티어 데이터 (select_oil과 동일)
    oil_tiers_map = {
        'economy': {'name': '이코노미', 'price': 50000, 'product_name': 'Kixx DX5'},
        'standard': {'name': '스탠다드', 'price': 70000, 'product_name': 'Kixx GX7'},
        'premium': {'name': '프리미엄', 'price': 90000, 'product_name': 'Kixx PAO'},
        'hyperformance': {'name': '하이퍼포먼스', 'price': 120000, 'product_name': '리스타 슈퍼노멀'},
        'racing': {'name': '레이싱', 'price': 150000, 'product_name': '리스타 메탈로센'},
    }

    oil_tier = oil_tiers_map.get(oil_tier_id, {})
    oil = type('Oil', (), {
        'name': oil_tier.get('name', ''),
        'price': oil_tier.get('price', 0),
        'product_name': oil_tier.get('product_name', ''),
    })()

    # 선택된 추가 서비스들
    services = []
    services_total = 0
    if service_ids:
        ids = [int(x) for x in service_ids.split(',') if x.isdigit()]
        services = AdditionalService.objects.filter(id__in=ids, is_active=True)
        services_total = sum(s.price for s in services)

    total_price = oil.price + services_total

    context = {
        'car_number': car_number,
        'brand': brand,
        'car_model': car_model,
        'fuel_type': fuel_type,
        'oil': oil,
        'services': services,
        'services_total': services_total,
        'total_price': total_price,
        'brand_id': brand_id,
        'model_id': model_id,
        'fuel_id': fuel_id,
        'oil_id': oil_tier_id,
        'service_ids': service_ids,
    }
    return render(request, 'estimate.html', context)


# ============================================
# 직원용 기능
# ============================================

# 오일 티어 데이터 (공통 사용)
OIL_TIERS_MAP = {
    'economy': {'name': '이코노미', 'price': 50000, 'product_name': 'Kixx DX5', 'mileage_interval': 6000},
    'standard': {'name': '스탠다드', 'price': 70000, 'product_name': 'Kixx GX7', 'mileage_interval': 8000},
    'premium': {'name': '프리미엄', 'price': 90000, 'product_name': 'Kixx PAO', 'mileage_interval': 10000},
    'hyperformance': {'name': '하이퍼포먼스', 'price': 120000, 'product_name': '리스타 슈퍼노멀', 'mileage_interval': 12000},
    'racing': {'name': '레이싱', 'price': 150000, 'product_name': '리스타 메탈로센', 'mileage_interval': 15000},
}


@require_POST
def create_order(request):
    """시공 주문 생성 (견적서에서 '시공 진행' 클릭 시)"""
    data = json.loads(request.body)

    brand = get_object_or_404(CarBrand, id=data.get('brand_id')) if data.get('brand_id') else None
    car_model = get_object_or_404(CarModel, id=data.get('model_id')) if data.get('model_id') else None
    fuel_type = get_object_or_404(FuelType, id=data.get('fuel_id')) if data.get('fuel_id') else None

    oil_tier_id = data.get('oil_id', '')
    oil_tier = OIL_TIERS_MAP.get(oil_tier_id, {})

    # 주문 생성
    order = ServiceOrder.objects.create(
        car_number=data.get('car_number', ''),
        customer_phone=data.get('customer_phone', ''),
        brand=brand,
        car_model=car_model,
        fuel_type=fuel_type,
        oil_tier=oil_tier_id,
        oil_name=oil_tier.get('name', ''),
        oil_product_name=oil_tier.get('product_name', ''),
        oil_price=oil_tier.get('price', 0),
        status='pending',
    )

    # 추가 서비스 저장
    service_ids = data.get('service_ids', '')
    if service_ids:
        ids = [int(x) for x in service_ids.split(',') if x.isdigit()]
        services = AdditionalService.objects.filter(id__in=ids, is_active=True)
        for service in services:
            ServiceOrderItem.objects.create(
                order=order,
                service=service,
                name=service.name,
                price=service.price,
            )

    return JsonResponse({'success': True, 'order_id': order.id})


def staff_dashboard(request):
    """직원용 대시보드 - 미완료/완료 목록"""
    status_filter = request.GET.get('status', 'pending')

    if status_filter == 'completed':
        orders = ServiceOrder.objects.filter(status='completed')
    else:
        # 미완료 (pending, in_progress 모두)
        orders = ServiceOrder.objects.exclude(status='completed')

    # 오늘 통계
    today = timezone.now().date()
    today_orders = ServiceOrder.objects.filter(created_at__date=today)
    stats = {
        'pending': today_orders.exclude(status='completed').count(),
        'completed': today_orders.filter(status='completed').count(),
    }

    context = {
        'orders': orders[:100],
        'status_filter': status_filter,
        'stats': stats,
    }
    return render(request, 'staff/dashboard.html', context)


def order_detail(request, order_id):
    """주문 상세 / 편집 페이지"""
    order = get_object_or_404(ServiceOrder, id=order_id)

    # 오일별 교체 주기
    oil_tier = OIL_TIERS_MAP.get(order.oil_tier, {})
    mileage_interval = oil_tier.get('mileage_interval', 10000)

    if request.method == 'POST':
        action = request.POST.get('action', '')
        order.mileage_current = request.POST.get('mileage_current') or None
        order.notes = request.POST.get('notes', '')

        if order.mileage_current:
            order.mileage_current = int(order.mileage_current)
            order.mileage_next = order.mileage_current + mileage_interval

        if action == 'complete':
            order.status = 'completed'
            order.completed_at = timezone.now()

        order.save()

        # 완료된 주문은 상세페이지로, 미완료는 대시보드로
        if order.status == 'completed':
            return redirect('order_detail', order_id=order.id)
        return redirect('staff_dashboard')

    context = {
        'order': order,
        'mileage_interval': mileage_interval,
    }
    return render(request, 'staff/order_detail.html', context)


def order_search(request):
    """시공 내역 검색"""
    query = request.GET.get('q', '')
    orders = []

    if query:
        orders = ServiceOrder.objects.filter(car_number__icontains=query).order_by('-created_at')[:50]

    context = {
        'query': query,
        'orders': orders,
    }
    return render(request, 'staff/order_search.html', context)


def order_complete(request):
    """시공 완료 - 고객에게 보여주는 완료 페이지"""
    settings = StoreSettings.get_settings()
    context = {
        'settings': settings,
    }
    return render(request, 'order_complete.html', context)


def store_settings(request):
    """지점 설정 페이지"""
    settings = StoreSettings.get_settings()

    if request.method == 'POST':
        settings.store_name = request.POST.get('store_name', settings.store_name)
        settings.phone = request.POST.get('phone', '')
        settings.address = request.POST.get('address', '')
        settings.estimated_time = int(request.POST.get('estimated_time', 30) or 30)
        settings.welcome_message = request.POST.get('welcome_message', '')
        settings.save()
        return redirect('store_settings')

    context = {
        'settings': settings,
    }
    return render(request, 'staff/store_settings.html', context)


@require_POST
def send_alimtalk(request, order_id):
    """알림톡 발송"""
    order = get_object_or_404(ServiceOrder, id=order_id)

    # 요청에서 전화번호 가져오기
    try:
        data = json.loads(request.body)
        phone = data.get('phone', '').strip()
    except:
        phone = ''

    # 전화번호가 입력되면 주문에 저장
    if phone:
        order.customer_phone = phone
        order.save(update_fields=['customer_phone'])

    if not order.customer_phone:
        return JsonResponse({'success': False, 'error': '고객 전화번호가 없습니다.'})

    result = send_service_complete_message(order)

    return JsonResponse(result)


# ============================================
# 예약 관리
# ============================================

def reservation_list(request):
    """오늘 예약 + 시공 목록"""
    target_date = request.GET.get('date')
    if target_date:
        try:
            target_date = datetime.strptime(target_date, '%Y-%m-%d').date()
        except:
            target_date = date.today()
    else:
        target_date = date.today()

    reservations = Reservation.objects.filter(date=target_date).order_by('time')
    orders = ServiceOrder.objects.filter(created_at__date=target_date).order_by('created_at')

    # 시간대별 그룹핑 (9시~19시)
    time_slots = []
    for hour in range(9, 20):
        slot_reservations = [r for r in reservations if r.time.hour == hour]
        slot_orders = [o for o in orders if o.created_at.hour == hour]
        time_slots.append({
            'hour': hour,
            'display': f"{hour:02d}:00",
            'reservations': slot_reservations,
            'orders': slot_orders,
        })

    context = {
        'target_date': target_date,
        'prev_date': target_date - timedelta(days=1),
        'next_date': target_date + timedelta(days=1),
        'reservations': reservations,
        'orders': orders,
        'time_slots': time_slots,
        'stats': {
            'total': reservations.count() + orders.count(),
            'reserved': reservations.filter(status='reserved').count(),
            'arrived': reservations.filter(status='arrived').count(),
            'completed': reservations.filter(status='completed').count() + orders.filter(status='completed').count(),
            'orders_pending': orders.exclude(status='completed').count(),
        }
    }
    return render(request, 'staff/reservation_list.html', context)


def reservation_add(request):
    """예약 추가"""
    if request.method == 'POST':
        # 날짜/시간
        res_date = request.POST.get('date')
        res_time = request.POST.get('time')

        # 고객 정보
        customer_name = request.POST.get('customer_name', '')
        customer_phone = request.POST.get('customer_phone', '')
        car_number = request.POST.get('car_number', '')

        # 차량 정보
        brand_id = request.POST.get('brand')
        model_id = request.POST.get('model')

        # 예약 정보
        expected_oil = request.POST.get('expected_oil', '')
        source = request.POST.get('source', 'phone')
        memo = request.POST.get('memo', '')

        brand = CarBrand.objects.filter(id=brand_id).first() if brand_id else None
        car_model = CarModel.objects.filter(id=model_id).first() if model_id else None

        # 고객 조회/생성
        customer = None
        if customer_phone:
            customer, _ = Customer.objects.get_or_create(
                phone=customer_phone,
                defaults={
                    'name': customer_name,
                    'car_number': car_number,
                    'brand': brand,
                    'car_model': car_model,
                }
            )
            # 기존 고객이면 정보 업데이트
            if customer_name and not customer.name:
                customer.name = customer_name
            if car_number and not customer.car_number:
                customer.car_number = car_number
            if brand and not customer.brand:
                customer.brand = brand
            if car_model and not customer.car_model:
                customer.car_model = car_model
            customer.save()

        # 예약 생성
        Reservation.objects.create(
            date=res_date,
            time=res_time,
            customer=customer,
            customer_name=customer_name,
            customer_phone=customer_phone,
            car_number=car_number,
            brand=brand,
            car_model=car_model,
            expected_oil=expected_oil,
            source=source,
            memo=memo,
        )

        return redirect('reservation_list')

    # GET: 폼 표시
    brands = CarBrand.objects.prefetch_related('models').all()
    brands_data = []
    for brand in brands:
        brands_data.append({
            'id': brand.id,
            'name': brand.name,
            'models': [{'id': m.id, 'name': m.name} for m in brand.models.all()]
        })

    context = {
        'brands': brands,
        'brands_json': json.dumps(brands_data, ensure_ascii=False),
        'today': date.today(),
        'oil_choices': [
            '이코노미 (DX5, GX5)',
            '스탠다드 (DX7)',
            '프리미엄 (KIXX PAO, 토탈쿼츠 9000)',
            '하이퍼포먼스 (리스타 슈퍼노멀)',
            '레이싱 (리스타 메탈로센)',
        ],
        'source_choices': Reservation.SOURCE_CHOICES,
    }
    return render(request, 'staff/reservation_add.html', context)


def reservation_edit(request, reservation_id):
    """예약 수정"""
    reservation = get_object_or_404(Reservation, id=reservation_id)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'delete':
            reservation.delete()
            return redirect('reservation_list')

        if action == 'cancel':
            reservation.status = 'cancelled'
            reservation.save()
            return redirect('reservation_list')

        # 수정
        reservation.date = request.POST.get('date')
        reservation.time = request.POST.get('time')
        reservation.customer_name = request.POST.get('customer_name', '')
        reservation.customer_phone = request.POST.get('customer_phone', '')
        reservation.car_number = request.POST.get('car_number', '')
        reservation.expected_oil = request.POST.get('expected_oil', '')
        reservation.source = request.POST.get('source', 'phone')
        reservation.memo = request.POST.get('memo', '')
        reservation.status = request.POST.get('status', reservation.status)

        brand_id = request.POST.get('brand')
        model_id = request.POST.get('model')
        reservation.brand = CarBrand.objects.filter(id=brand_id).first() if brand_id else None
        reservation.car_model = CarModel.objects.filter(id=model_id).first() if model_id else None

        reservation.save()
        return redirect('reservation_list')

    # GET
    brands = CarBrand.objects.prefetch_related('models').all()
    brands_data = []
    for brand in brands:
        brands_data.append({
            'id': brand.id,
            'name': brand.name,
            'models': [{'id': m.id, 'name': m.name} for m in brand.models.all()]
        })

    context = {
        'reservation': reservation,
        'brands': brands,
        'brands_json': json.dumps(brands_data, ensure_ascii=False),
        'oil_choices': [
            '이코노미 (DX5, GX5)',
            '스탠다드 (DX7)',
            '프리미엄 (KIXX PAO, 토탈쿼츠 9000)',
            '하이퍼포먼스 (리스타 슈퍼노멀)',
            '레이싱 (리스타 메탈로센)',
        ],
        'source_choices': Reservation.SOURCE_CHOICES,
        'status_choices': Reservation.STATUS_CHOICES,
    }
    return render(request, 'staff/reservation_edit.html', context)


def check_reservation(request):
    """전화번호로 예약 조회 (API)"""
    phone = request.GET.get('phone', '').replace('-', '').replace(' ', '')

    if not phone:
        return JsonResponse({'found': False})

    # 오늘 예약 중 매칭
    today = date.today()
    reservation = Reservation.objects.filter(
        customer_phone__endswith=phone[-8:],  # 뒤 8자리 매칭
        date=today,
        status='reserved'
    ).first()

    if reservation:
        return JsonResponse({
            'found': True,
            'reservation': {
                'id': reservation.id,
                'time': reservation.time.strftime('%H:%M'),
                'customer_name': reservation.customer_name,
                'car_number': reservation.car_number,
                'brand_id': reservation.brand_id,
                'model_id': reservation.car_model_id,
                'expected_oil': reservation.expected_oil,
            }
        })

    # 고객 정보만이라도 찾기
    customer = Customer.objects.filter(phone__endswith=phone[-8:]).first()
    if customer:
        return JsonResponse({
            'found': False,
            'customer': {
                'name': customer.name,
                'car_number': customer.car_number,
                'brand_id': customer.brand_id,
                'model_id': customer.car_model_id,
            }
        })

    return JsonResponse({'found': False})
