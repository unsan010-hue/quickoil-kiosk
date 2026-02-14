import json
from functools import wraps
from django.conf import settings
from django.core.paginator import Paginator
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import date, datetime, timedelta
from .models import CarBrand, CarModel, FuelType, EngineOil, AdditionalService, ServiceOrder, ServiceOrderItem, StoreSettings, Customer, Reservation, OilProduct, OilPrice
from .services import send_service_complete_message
from .ecount import create_sales_slip, create_purchase_slip


# ============================================
# 스태프 인증
# ============================================

def staff_required(view_func):
    """스태프 인증 데코레이터 - 세션 기반 24시간 유효"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_time = request.session.get('staff_auth_time')
        if auth_time:
            auth_dt = datetime.fromisoformat(auth_time)
            if timezone.now() - auth_dt < timedelta(hours=24):
                return view_func(request, *args, **kwargs)
        # 인증 안 됨 → 로그인 페이지로
        return redirect(f'/staff/login/?next={request.get_full_path()}')
    return wrapper


def staff_login(request):
    """스태프 로그인 페이지"""
    error = ''
    if request.method == 'POST':
        password = request.POST.get('password', '')
        if password == settings.STAFF_PASSWORD:
            request.session['staff_authenticated'] = True
            request.session['staff_auth_time'] = timezone.now().isoformat()
            next_url = request.GET.get('next') or request.POST.get('next') or '/staff/'
            return redirect(next_url)
        error = '비밀번호가 올바르지 않습니다.'

    return render(request, 'staff/login.html', {
        'error': error,
        'next': request.GET.get('next', '/staff/'),
    })


def start(request):
    """시작 페이지 - 차량번호 입력 + 오늘의 예약/시공 사이드바"""
    today = date.today()

    # 예약 목록
    reservations = Reservation.objects.filter(
        date=today,
    ).select_related('brand', 'car_model').order_by('time')

    # 시공(ServiceOrder) 목록
    start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end_of_day = start_of_day + timedelta(days=1)
    orders = ServiceOrder.objects.filter(
        created_at__gte=start_of_day,
        created_at__lt=end_of_day,
    ).select_related('brand', 'car_model').order_by('created_at')

    STATUS_BADGE = {
        'reserved': '예약',
        'arrived': '도착',
        'in_progress': '시공중',
        'completed': '완료',
        'cancelled': '취소',
        'no_show': '노쇼',
    }

    sidebar_items = []

    for r in reservations:
        if r.car_number:
            display_label = r.car_number[-4:]
        elif r.customer_name:
            name = r.customer_name
            if len(name) == 2:
                display_label = name[0] + '*'
            elif len(name) >= 3:
                display_label = name[0] + '*' * (len(name) - 2) + name[-1]
            else:
                display_label = name
        else:
            display_label = '예약'

        model_name = r.car_model.name if r.car_model else '-'
        badge = STATUS_BADGE.get(r.status, r.status)

        sidebar_items.append({
            'type': 'reservation',
            'id': r.id,
            'time': r.time.strftime('%H:%M'),
            'sort_key': r.time.strftime('%H%M'),
            'display_label': display_label,
            'model_name': model_name,
            'badge': badge,
            'status': r.status,
            'car_number': r.car_number or '',
            'brand_id': r.brand_id or '',
            'model_id': r.car_model_id or '',
        })

    for o in orders:
        local_time = timezone.localtime(o.created_at)
        if o.car_number:
            display_label = o.car_number[-4:]
        else:
            display_label = '-'

        model_name = o.car_model.name if o.car_model else '-'
        badge = '완료' if o.status == 'completed' else '시공'

        sidebar_items.append({
            'type': 'order',
            'id': o.id,
            'time': local_time.strftime('%H:%M'),
            'sort_key': local_time.strftime('%H%M'),
            'display_label': display_label,
            'model_name': model_name,
            'badge': badge,
            'status': o.status,
            'car_number': o.car_number or '',
            'brand_id': o.brand_id or '',
            'model_id': o.car_model_id or '',
        })

    sidebar_items.sort(key=lambda x: x['sort_key'])

    context = {
        'sidebar_items': sidebar_items,
    }
    return render(request, 'start.html', context)


def _build_brands_data(include_generations=True):
    """브랜드/차종/세대 JSON 데이터 빌드"""
    brands = CarBrand.objects.prefetch_related('models', 'models__generations').all()
    brands_data = []
    for brand in brands:
        models_data = []
        for m in brand.models.filter(parent=None):
            model_info = {'id': m.id, 'name': m.name}
            if include_generations:
                gens = list(m.generations.all())
                if gens:
                    model_info['generations'] = [{'id': g.id, 'name': g.name} for g in gens]
            models_data.append(model_info)
        brands_data.append({
            'id': brand.id,
            'name': brand.name,
            'models': models_data,
        })
    return brands, brands_data


def select_car(request):
    """차종 선택 페이지 (브랜드/차종/연료 한 페이지에서)"""
    car_number = request.GET.get('car_number', '')
    brands, brands_data = _build_brands_data()
    fuel_types = FuelType.objects.all()

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
    car_model = get_object_or_404(CarModel.objects.select_related('parent'), id=model_id) if model_id else None
    fuel_type = get_object_or_404(FuelType, id=fuel_id) if fuel_id else None

    # DB에서 차종×연료 조합의 가격 조회
    prices = OilPrice.objects.filter(
        car_model=car_model, fuel_type=fuel_type
    ).select_related('oil_product')
    price_map = {p.oil_product.tier: p.price for p in prices}

    # 하이브리드면 premium 가격을 벤졸(premium_hybrid) 가격으로 교체
    if fuel_type and fuel_type.name == '하이브리드' and 'premium_hybrid' in price_map:
        price_map['premium'] = price_map['premium_hybrid']

    # 가시적인 오일 제품 목록 생성
    oil_products = OilProduct.objects.filter(is_active=True, is_visible=True).order_by('order')
    has_db_prices = bool(price_map)

    # 폴백 가격 (DB에 가격 데이터가 없는 수입차 등)
    FALLBACK_PRICES = {
        'economy': 50000,
        'standard': 70000,
        'premium': 90000,
        'hyperformance': 120000,
        'racing': 150000,
    }

    oil_tiers = []
    for op in oil_products:
        if has_db_prices:
            price = price_map.get(op.tier)
            if price is None:
                continue  # 이 티어는 해당 차종에 미제공
        else:
            price = FALLBACK_PRICES.get(op.tier, 0)

        oil_tiers.append({
            'id': op.tier,
            'product_id': op.id,
            'name': op.get_tier_display(),
            'price': price,
            'oil_type': op.oil_type,
            'tagline': op.tagline,
            'product_name': op.name,
            'badge': op.badge or None,
            'badge_type': op.badge_type or None,
        })

    is_domestic = has_db_prices  # DB에 가격이 있으면 국산

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
    oil_price_param = request.GET.get('oil_price', '0')

    brand = get_object_or_404(CarBrand, id=brand_id) if brand_id else None
    car_model = get_object_or_404(CarModel.objects.select_related('parent'), id=model_id) if model_id else None
    fuel_type = get_object_or_404(FuelType, id=fuel_id) if fuel_id else None

    # OilProduct DB에서 조회
    oil_product = OilProduct.objects.filter(tier=oil_tier_id).first()
    oil_price = int(oil_price_param) if oil_price_param.isdigit() else 0

    oil = type('Oil', (), {
        'name': oil_product.get_tier_display() if oil_product else '',
        'price': oil_price,
        'product_name': oil_product.name if oil_product else '',
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
        'oil_price': oil_price,
    }
    return render(request, 'select_service.html', context)


def estimate(request):
    """견적서 페이지"""
    car_number = request.GET.get('car_number', '')
    brand_id = request.GET.get('brand')
    model_id = request.GET.get('model')
    fuel_id = request.GET.get('fuel')
    oil_tier_id = request.GET.get('oil')
    oil_price_param = request.GET.get('oil_price', '0')
    service_ids = request.GET.get('services', '')

    brand = get_object_or_404(CarBrand, id=brand_id) if brand_id else None
    car_model = get_object_or_404(CarModel.objects.select_related('parent'), id=model_id) if model_id else None
    fuel_type = get_object_or_404(FuelType, id=fuel_id) if fuel_id else None

    # OilProduct DB에서 조회
    oil_product = OilProduct.objects.filter(tier=oil_tier_id).first()
    oil_price = int(oil_price_param) if oil_price_param.isdigit() else 0

    oil = type('Oil', (), {
        'name': oil_product.get_tier_display() if oil_product else '',
        'price': oil_price,
        'product_name': oil_product.name if oil_product else '',
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
        'oil_price': oil_price,
        'service_ids': service_ids,
    }
    return render(request, 'estimate.html', context)


# ============================================
# 직원용 기능
# ============================================

@require_POST
def create_order(request):
    """시공 주문 생성 (견적서에서 '시공 진행' 클릭 시)"""
    data = json.loads(request.body)

    brand = get_object_or_404(CarBrand, id=data.get('brand_id')) if data.get('brand_id') else None
    car_model = get_object_or_404(CarModel, id=data.get('model_id')) if data.get('model_id') else None
    fuel_type = get_object_or_404(FuelType, id=data.get('fuel_id')) if data.get('fuel_id') else None

    oil_tier_id = data.get('oil_id', '')
    oil_price = int(data.get('oil_price', 0))

    # OilProduct에서 정보 조회
    oil_product = OilProduct.objects.filter(tier=oil_tier_id).first()

    # 주문 생성
    order = ServiceOrder.objects.create(
        car_number=data.get('car_number', ''),
        customer_phone=data.get('customer_phone', ''),
        brand=brand,
        car_model=car_model,
        fuel_type=fuel_type,
        oil_tier=oil_tier_id,
        oil_name=oil_product.get_tier_display() if oil_product else '',
        oil_product_name=oil_product.name if oil_product else '',
        oil_price=oil_price,
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


@staff_required
def staff_dashboard(request):
    """직원용 대시보드 - 미완료/완료 목록"""
    status_filter = request.GET.get('status', 'pending')
    time_filter = request.GET.get('time', 'today')  # today or all

    # 기본 쿼리셋
    if time_filter == 'today':
        today = timezone.now().date()
        base_qs = ServiceOrder.objects.filter(created_at__date=today)
    else:
        base_qs = ServiceOrder.objects.all()

    if status_filter == 'completed':
        orders = base_qs.filter(status='completed').order_by('-completed_at')
    else:
        # 미완료 (pending, in_progress 모두)
        orders = base_qs.exclude(status='completed').order_by('-created_at')

    # 통계
    stats = {
        'pending': base_qs.exclude(status='completed').count(),
        'completed': base_qs.filter(status='completed').count(),
    }

    # 페이지네이션
    paginator = Paginator(orders, 20)
    page = request.GET.get('page', 1)
    orders_page = paginator.get_page(page)

    context = {
        'orders': orders_page,
        'status_filter': status_filter,
        'time_filter': time_filter,
        'stats': stats,
    }
    return render(request, 'staff/dashboard.html', context)


@staff_required
def order_detail(request, order_id):
    """주문 상세 / 편집 페이지"""
    order = get_object_or_404(ServiceOrder, id=order_id)

    # 오일별 교체 주기 - OilProduct DB에서 조회
    oil_product = OilProduct.objects.filter(tier=order.oil_tier).first()
    mileage_interval = oil_product.mileage_interval if oil_product else 10000

    if request.method == 'POST':
        action = request.POST.get('action', '')
        order.mileage_current = request.POST.get('mileage_current') or None
        order.notes = request.POST.get('notes', '')
        order.membership_discount = request.POST.get('membership_discount') == 'on'

        if order.mileage_current:
            order.mileage_current = int(order.mileage_current)
            order.mileage_next = order.mileage_current + mileage_interval

        if action == 'complete':
            order.status = 'completed'
            order.completed_at = timezone.now()

        order.save()

        # 이카운트 ERP 연동
        if settings.ECOUNT_API_KEY:
            # 시공 완료 시 매출전표 생성
            if action == 'complete':
                ecount_result = create_sales_slip(order)
                if ecount_result.get('success'):
                    order.ecount_slip_no = ecount_result['slip_no']
                    order.save(update_fields=['ecount_slip_no'])
                else:
                    messages.error(request, f'이카운트 매출전표 생성 실패: {ecount_result.get("error", "알 수 없는 오류")}')

            # 멤버십 할인 ON + 아직 매입전표 없음 → 생성
            if order.membership_discount and not order.ecount_purchase_slip_no:
                purchase_result = create_purchase_slip(order)
                if purchase_result.get('success'):
                    order.ecount_purchase_slip_no = purchase_result['slip_no']
                    order.save(update_fields=['ecount_purchase_slip_no'])
                else:
                    messages.error(request, f'이카운트 매입전표 생성 실패: {purchase_result.get("error", "알 수 없는 오류")}')

        # 예약↔시공 상태 연동
        if hasattr(order, 'reservation') and order.reservation:
            res = order.reservation
            if order.status == 'completed' and res.status != 'completed':
                res.status = 'completed'
                res.save(update_fields=['status'])

        # 완료된 주문은 상세페이지로, 미완료는 대시보드로
        if order.status == 'completed':
            return redirect('order_detail', order_id=order.id)
        return redirect('staff_dashboard')

    context = {
        'order': order,
        'mileage_interval': mileage_interval,
    }
    return render(request, 'staff/order_detail.html', context)


@staff_required
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


@staff_required
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


@staff_required
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

@staff_required
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

    # 쿼리 최적화: select_related로 JOIN
    reservations = list(Reservation.objects.filter(date=target_date)
        .select_related('brand', 'car_model')
        .order_by('time'))

    # 시간대를 고려해서 해당 날짜의 주문 조회
    start_of_day = timezone.make_aware(datetime.combine(target_date, datetime.min.time()))
    end_of_day = start_of_day + timedelta(days=1)
    orders = list(ServiceOrder.objects.filter(
        created_at__gte=start_of_day,
        created_at__lt=end_of_day
    ).select_related('brand', 'car_model').order_by('created_at'))

    # 주문별 로컬 시간 미리 계산
    for order in orders:
        order.local_hour = timezone.localtime(order.created_at).hour

    # 시간대별 그룹핑 (9시~19시)
    time_slots = []
    for hour in range(9, 20):
        slot_reservations = [r for r in reservations if r.time.hour == hour]
        slot_orders = [o for o in orders if o.local_hour == hour]
        time_slots.append({
            'hour': hour,
            'display': f"{hour:02d}:00",
            'reservations': slot_reservations,
            'orders': slot_orders,
        })

    # 통계 계산 (리스트에서 직접 계산)
    stats = {
        'total': len(reservations) + len(orders),
        'reserved': sum(1 for r in reservations if r.status == 'reserved'),
        'arrived': sum(1 for r in reservations if r.status == 'arrived'),
        'completed': sum(1 for r in reservations if r.status == 'completed') + sum(1 for o in orders if o.status == 'completed'),
        'orders_pending': sum(1 for o in orders if o.status != 'completed'),
    }

    context = {
        'target_date': target_date,
        'prev_date': target_date - timedelta(days=1),
        'next_date': target_date + timedelta(days=1),
        'reservations': reservations,
        'orders': orders,
        'time_slots': time_slots,
        'stats': stats,
    }

    return render(request, 'staff/reservation_list.html', context)


@staff_required
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
    brands, brands_data = _build_brands_data(include_generations=False)

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


@staff_required
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
            if reservation.order:
                reservation.order.status = 'cancelled'
                reservation.order.save(update_fields=['status'])
            return redirect('reservation_list')

        if action == 'no_show':
            reservation.status = 'no_show'
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

        # 예약↔시공 상태 연동
        if reservation.order:
            STATUS_MAP = {
                'completed': 'completed',
                'cancelled': 'cancelled',
                'in_progress': 'in_progress',
            }
            mapped = STATUS_MAP.get(reservation.status)
            if mapped and reservation.order.status != mapped:
                reservation.order.status = mapped
                if mapped == 'completed':
                    reservation.order.completed_at = timezone.now()
                reservation.order.save(update_fields=['status'] + (['completed_at'] if mapped == 'completed' else []))

        return redirect('reservation_list')

    # GET
    brands, brands_data = _build_brands_data(include_generations=False)

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


# ============================================
# 오일 가격 관리
# ============================================

@staff_required
def oil_price_management(request):
    """오일 가격 관리 - 엑셀 스타일 스프레드시트"""
    brands = CarBrand.objects.all()
    fuel_types = FuelType.objects.all()

    # 기본값: 첫 번째 브랜드, 첫 번째 연료
    brand_id = request.GET.get('brand')
    fuel_id = request.GET.get('fuel')

    selected_brand = None
    selected_fuel = None

    if brand_id:
        selected_brand = CarBrand.objects.filter(id=brand_id).first()
    if not selected_brand:
        selected_brand = brands.first()

    if fuel_id:
        selected_fuel = FuelType.objects.filter(id=fuel_id).first()
    if not selected_fuel:
        selected_fuel = fuel_types.first()

    # 오일 제품 목록 (premium_hybrid 포함, 스태프용이라 is_visible 무시)
    oil_products = list(OilProduct.objects.filter(is_active=True).order_by('order'))

    # 해당 브랜드의 차종 (parent=None) + 세대(generations) prefetch
    car_models = CarModel.objects.filter(
        brand=selected_brand, parent=None
    ).prefetch_related('generations').order_by('order', 'name')

    # 세대 모델 ID 목록 수집
    all_model_ids = []
    for model in car_models:
        gens = list(model.generations.all())
        if gens:
            all_model_ids.extend([g.id for g in gens])
        else:
            all_model_ids.append(model.id)

    # OilPrice 벌크 쿼리
    prices = OilPrice.objects.filter(
        car_model_id__in=all_model_ids,
        fuel_type=selected_fuel,
    ).select_related('oil_product')

    # price_map: {(model_id, product_id): price}
    price_map = {}
    for p in prices:
        price_map[(p.car_model_id, p.oil_product_id)] = p.price

    # 테이블 행 데이터 구성
    rows = []
    for model in car_models:
        gens = list(model.generations.all())
        if gens:
            for gen in gens:
                price_list = []
                for op in oil_products:
                    price_list.append({
                        'product_id': op.id,
                        'price': price_map.get((gen.id, op.id)),
                    })
                rows.append({
                    'model_id': gen.id,
                    'parent_id': model.id,
                    'parent_name': model.name,
                    'name': gen.name,
                    'is_first_in_group': gen == gens[0],
                    'group_size': len(gens),
                    'prices': price_list,
                })
        else:
            price_list = []
            for op in oil_products:
                price_list.append({
                    'product_id': op.id,
                    'price': price_map.get((model.id, op.id)),
                })
            rows.append({
                'model_id': model.id,
                'parent_id': None,
                'parent_name': None,
                'name': model.name,
                'is_first_in_group': True,
                'group_size': 1,
                'prices': price_list,
            })

    context = {
        'brands': brands,
        'fuel_types': fuel_types,
        'selected_brand': selected_brand,
        'selected_fuel': selected_fuel,
        'oil_products': oil_products,
        'rows': rows,
    }
    return render(request, 'staff/oil_prices.html', context)


@staff_required
@require_POST
def oil_price_save(request):
    """오일 가격 일괄 저장 API"""
    try:
        data = json.loads(request.body)
        changes = data.get('changes', [])

        created = 0
        updated = 0
        deleted = 0

        for item in changes:
            model_id = item.get('model_id')
            product_id = item.get('product_id')
            fuel_id = item.get('fuel_id')
            price = item.get('price')

            if not all([model_id, product_id, fuel_id]):
                continue

            if price is None or price == '':
                # 빈 값이면 삭제
                count, _ = OilPrice.objects.filter(
                    car_model_id=model_id,
                    oil_product_id=product_id,
                    fuel_type_id=fuel_id,
                ).delete()
                if count:
                    deleted += count
            else:
                price = int(price)
                obj, was_created = OilPrice.objects.update_or_create(
                    car_model_id=model_id,
                    oil_product_id=product_id,
                    fuel_type_id=fuel_id,
                    defaults={'price': price},
                )
                if was_created:
                    created += 1
                else:
                    updated += 1

        return JsonResponse({
            'success': True,
            'created': created,
            'updated': updated,
            'deleted': deleted,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@staff_required
@require_POST
def car_model_add(request):
    """차종 추가 API"""
    try:
        data = json.loads(request.body)
        brand_id = data.get('brand_id')
        name = data.get('name', '').strip()
        parent_id = data.get('parent_id')  # 세대 추가 시

        if not brand_id or not name:
            return JsonResponse({'success': False, 'error': '브랜드와 차종명을 입력하세요.'}, status=400)

        brand = get_object_or_404(CarBrand, id=brand_id)
        parent = CarModel.objects.filter(id=parent_id, brand=brand).first() if parent_id else None

        model, created = CarModel.objects.get_or_create(
            brand=brand,
            name=name,
            parent=parent,
            defaults={'order': 0},
        )

        if not created:
            return JsonResponse({'success': False, 'error': '이미 존재하는 차종입니다.'}, status=400)

        return JsonResponse({
            'success': True,
            'model': {'id': model.id, 'name': model.name},
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@staff_required
@require_POST
def car_model_delete(request, model_id):
    """차종 삭제 API (가격도 함께 삭제)"""
    try:
        model = get_object_or_404(CarModel, id=model_id)

        # 시공 주문에서 참조 중인지 확인
        order_count = ServiceOrder.objects.filter(car_model=model).count()
        if order_count > 0:
            return JsonResponse({
                'success': False,
                'error': f'시공 주문 {order_count}건에서 사용 중이라 삭제할 수 없습니다.',
            }, status=400)

        # 세대 모델이면 세대만 삭제, 부모 모델이면 세대까지 모두 삭제
        if model.parent is None:
            # 자식 세대들도 주문 참조 확인
            children = model.generations.all()
            child_order_count = ServiceOrder.objects.filter(car_model__in=children).count()
            if child_order_count > 0:
                return JsonResponse({
                    'success': False,
                    'error': f'하위 세대가 시공 주문 {child_order_count}건에서 사용 중입니다.',
                }, status=400)
            # 자식 가격 + 자식 모델 삭제
            OilPrice.objects.filter(car_model__in=children).delete()
            children.delete()

        # 본인 가격 + 모델 삭제
        OilPrice.objects.filter(car_model=model).delete()
        model.delete()

        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)
