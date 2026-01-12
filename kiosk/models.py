from django.db import models


class StoreSettings(models.Model):
    """지점 설정 (싱글톤)"""
    store_name = models.CharField(max_length=100, default='QuickOil', verbose_name='지점명')
    phone = models.CharField(max_length=20, blank=True, verbose_name='전화번호')
    address = models.CharField(max_length=200, default='경기도 광명시', verbose_name='주소')
    estimated_time = models.PositiveIntegerField(default=30, verbose_name='예상 소요시간(분)')
    welcome_message = models.TextField(blank=True, verbose_name='환영 메시지')

    class Meta:
        verbose_name = '지점 설정'
        verbose_name_plural = '지점 설정'

    def __str__(self):
        return self.store_name

    def save(self, *args, **kwargs):
        # 싱글톤: 항상 pk=1로 저장
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class CarBrand(models.Model):
    """차량 브랜드 (현대, 기아, BMW 등)"""
    name = models.CharField(max_length=50, verbose_name='브랜드명')
    logo = models.ImageField(upload_to='brands/', blank=True, null=True, verbose_name='로고')
    order = models.PositiveIntegerField(default=0, verbose_name='정렬순서')

    class Meta:
        verbose_name = '차량 브랜드'
        verbose_name_plural = '차량 브랜드'
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class CarModel(models.Model):
    """차종 (쏘나타, K5 등)"""
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name='models', verbose_name='브랜드')
    name = models.CharField(max_length=100, verbose_name='차종명')
    order = models.PositiveIntegerField(default=0, verbose_name='정렬순서')

    class Meta:
        verbose_name = '차종'
        verbose_name_plural = '차종'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.brand.name} {self.name}"


class FuelType(models.Model):
    """연료 타입 (휘발유, 경유)"""
    name = models.CharField(max_length=20, verbose_name='연료타입')
    order = models.PositiveIntegerField(default=0, verbose_name='정렬순서')

    class Meta:
        verbose_name = '연료 타입'
        verbose_name_plural = '연료 타입'
        ordering = ['order']

    def __str__(self):
        return self.name


class EngineOil(models.Model):
    """엔진오일 종류"""
    name = models.CharField(max_length=100, verbose_name='오일명')
    description = models.TextField(blank=True, verbose_name='설명')
    price = models.PositiveIntegerField(verbose_name='가격')
    fuel_types = models.ManyToManyField(FuelType, related_name='oils', verbose_name='적용 연료타입')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    order = models.PositiveIntegerField(default=0, verbose_name='정렬순서')

    class Meta:
        verbose_name = '엔진오일'
        verbose_name_plural = '엔진오일'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.price:,}원)"


class AdditionalService(models.Model):
    """추가 서비스 (에어컨 필터, 와이퍼 등)"""
    name = models.CharField(max_length=100, verbose_name='서비스명')
    description = models.TextField(blank=True, verbose_name='설명')
    price = models.PositiveIntegerField(verbose_name='가격')
    is_active = models.BooleanField(default=True, verbose_name='활성화')
    order = models.PositiveIntegerField(default=0, verbose_name='정렬순서')

    class Meta:
        verbose_name = '추가 서비스'
        verbose_name_plural = '추가 서비스'
        ordering = ['order', 'name']

    def __str__(self):
        return f"{self.name} ({self.price:,}원)"


class ServiceOrder(models.Model):
    """시공 주문"""
    STATUS_CHOICES = [
        ('pending', '대기'),
        ('in_progress', '진행중'),
        ('completed', '완료'),
        ('cancelled', '취소'),
    ]

    # 차량 정보
    car_number = models.CharField(max_length=20, blank=True, verbose_name='차량번호')
    customer_phone = models.CharField(max_length=20, blank=True, verbose_name='고객 전화번호')
    brand = models.ForeignKey(CarBrand, on_delete=models.SET_NULL, null=True, verbose_name='브랜드')
    car_model = models.ForeignKey(CarModel, on_delete=models.SET_NULL, null=True, verbose_name='차종')
    fuel_type = models.ForeignKey(FuelType, on_delete=models.SET_NULL, null=True, verbose_name='연료타입')

    # 오일 정보 (주문 시점 스냅샷)
    oil_tier = models.CharField(max_length=20, verbose_name='오일 등급')
    oil_name = models.CharField(max_length=50, verbose_name='오일명')
    oil_product_name = models.CharField(max_length=100, verbose_name='제품명')
    oil_price = models.PositiveIntegerField(verbose_name='오일 가격')

    # 주행거리
    mileage_current = models.PositiveIntegerField(null=True, blank=True, verbose_name='현재 주행거리')
    mileage_next = models.PositiveIntegerField(null=True, blank=True, verbose_name='다음 교체 주행거리')

    # 상태 및 메모
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='상태')
    notes = models.TextField(blank=True, verbose_name='메모')

    # 시간
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='생성일시', db_index=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='완료일시')

    class Meta:
        verbose_name = '시공 주문'
        verbose_name_plural = '시공 주문'
        ordering = ['-created_at']

    def __str__(self):
        car_info = f"{self.brand.name} {self.car_model.name}" if self.brand and self.car_model else "차량정보없음"
        return f"[{self.get_status_display()}] {self.car_number or '번호없음'} - {car_info}"

    @property
    def total_price(self):
        services_total = sum(item.price for item in self.services.all())
        return self.oil_price + services_total

    @property
    def services_total(self):
        return sum(item.price for item in self.services.all())


class ServiceOrderItem(models.Model):
    """시공 주문 - 추가 서비스 항목"""
    order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE, related_name='services', verbose_name='주문')
    service = models.ForeignKey(AdditionalService, on_delete=models.SET_NULL, null=True, verbose_name='서비스')
    # 주문 시점 스냅샷
    name = models.CharField(max_length=100, verbose_name='서비스명')
    price = models.PositiveIntegerField(verbose_name='가격')

    class Meta:
        verbose_name = '주문 서비스 항목'
        verbose_name_plural = '주문 서비스 항목'

    def __str__(self):
        return f"{self.name} ({self.price:,}원)"


class ServiceOrderPhoto(models.Model):
    """시공 완료 사진"""
    order = models.ForeignKey(ServiceOrder, on_delete=models.CASCADE, related_name='photos', verbose_name='주문')
    image = models.ImageField(upload_to='service_photos/%Y/%m/', verbose_name='사진')
    caption = models.CharField(max_length=200, blank=True, verbose_name='설명')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='업로드일시')

    class Meta:
        verbose_name = '시공 사진'
        verbose_name_plural = '시공 사진'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.order} - 사진"


class Customer(models.Model):
    """고객 정보"""
    phone = models.CharField(max_length=20, unique=True, verbose_name='전화번호')
    name = models.CharField(max_length=50, blank=True, verbose_name='고객명')
    car_number = models.CharField(max_length=20, blank=True, verbose_name='차량번호')
    brand = models.ForeignKey(CarBrand, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='브랜드')
    car_model = models.ForeignKey(CarModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='차종')
    fuel_type = models.ForeignKey(FuelType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='연료타입')
    memo = models.TextField(blank=True, verbose_name='메모')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일')

    class Meta:
        verbose_name = '고객'
        verbose_name_plural = '고객'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name or '미등록'} ({self.phone})"


class Reservation(models.Model):
    """예약"""
    STATUS_CHOICES = [
        ('reserved', '예약'),
        ('arrived', '도착'),
        ('in_progress', '진행중'),
        ('completed', '완료'),
        ('cancelled', '취소'),
        ('no_show', '노쇼'),
    ]

    SOURCE_CHOICES = [
        ('phone', '전화'),
        ('naver', '네이버'),
        ('michael', '마이클'),
        ('walk_in', '워크인'),
        ('other', '기타'),
    ]

    # 예약 정보
    date = models.DateField(verbose_name='예약일', db_index=True)
    time = models.TimeField(verbose_name='예약시간')
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='고객')

    # 고객 정보 (Customer 없을 때 직접 입력)
    customer_name = models.CharField(max_length=50, blank=True, verbose_name='고객명')
    customer_phone = models.CharField(max_length=20, verbose_name='전화번호')
    car_number = models.CharField(max_length=20, blank=True, verbose_name='차량번호')

    # 차량 정보
    brand = models.ForeignKey(CarBrand, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='브랜드')
    car_model = models.ForeignKey(CarModel, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='차종')

    # 예상 서비스
    expected_oil = models.CharField(max_length=20, blank=True, verbose_name='예상 오일')
    expected_services = models.TextField(blank=True, verbose_name='예상 추가서비스')

    # 상태
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reserved', verbose_name='상태')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='phone', verbose_name='예약경로')

    # 연결된 주문
    order = models.OneToOneField(ServiceOrder, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='시공주문')

    # 메모
    memo = models.TextField(blank=True, verbose_name='메모')

    # 시간
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='등록일시')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='수정일시')

    class Meta:
        verbose_name = '예약'
        verbose_name_plural = '예약'
        ordering = ['date', 'time']

    def __str__(self):
        return f"{self.date} {self.time.strftime('%H:%M')} - {self.customer_name or self.customer_phone}"
