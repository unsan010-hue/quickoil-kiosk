import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from kiosk.models import CarBrand, CarModel, FuelType, EngineOil, AdditionalService

# Clear existing data
AdditionalService.objects.all().delete()
EngineOil.objects.all().delete()
CarModel.objects.all().delete()
CarBrand.objects.all().delete()
FuelType.objects.all().delete()

# Fuel types
fuel_gasoline = FuelType.objects.create(name='휘발유', order=1)
fuel_diesel = FuelType.objects.create(name='경유', order=2)

# === 국산 브랜드 ===
hyundai = CarBrand.objects.create(name='현대', order=1)
for name in ['아반떼', '쏘나타', '그랜저', '투싼', '싼타페', '팰리세이드', '코나', '스타리아', '포터']:
    CarModel.objects.create(brand=hyundai, name=name)

kia = CarBrand.objects.create(name='기아', order=2)
for name in ['K3', 'K5', 'K8', 'K9', '스포티지', '쏘렌토', '카니발', '셀토스', '모하비', '봉고']:
    CarModel.objects.create(brand=kia, name=name)

genesis = CarBrand.objects.create(name='제네시스', order=3)
for name in ['G70', 'G80', 'G90', 'GV70', 'GV80']:
    CarModel.objects.create(brand=genesis, name=name)

kg = CarBrand.objects.create(name='KG모빌리티', order=4)
for name in ['토레스', '티볼리', '코란도', '렉스턴', '무쏘']:
    CarModel.objects.create(brand=kg, name=name)

renault = CarBrand.objects.create(name='르노코리아', order=5)
for name in ['SM6', 'XM3', 'QM6', '마스터', '아르카나']:
    CarModel.objects.create(brand=renault, name=name)

# === 수입 브랜드 ===
benz = CarBrand.objects.create(name='벤츠', order=10)
for name in ['E클래스', 'S클래스', 'C클래스', 'GLE', 'GLC', 'A클래스', 'CLA']:
    CarModel.objects.create(brand=benz, name=name)

bmw = CarBrand.objects.create(name='BMW', order=11)
for name in ['3시리즈', '5시리즈', '7시리즈', 'X3', 'X5', 'X7']:
    CarModel.objects.create(brand=bmw, name=name)

audi = CarBrand.objects.create(name='아우디', order=12)
for name in ['A4', 'A6', 'A8', 'Q3', 'Q5', 'Q7']:
    CarModel.objects.create(brand=audi, name=name)

vw = CarBrand.objects.create(name='폭스바겐', order=13)
for name in ['골프', '티구안', '파사트', '아테온', '투아렉']:
    CarModel.objects.create(brand=vw, name=name)

volvo = CarBrand.objects.create(name='볼보', order=14)
for name in ['S60', 'S90', 'XC40', 'XC60', 'XC90', 'V60']:
    CarModel.objects.create(brand=volvo, name=name)

toyota = CarBrand.objects.create(name='토요타', order=15)
for name in ['캠리', 'RAV4', '프리우스', '하이랜더', '시에나']:
    CarModel.objects.create(brand=toyota, name=name)

lexus = CarBrand.objects.create(name='렉서스', order=16)
for name in ['ES', 'LS', 'NX', 'RX', 'UX', 'LX']:
    CarModel.objects.create(brand=lexus, name=name)

honda = CarBrand.objects.create(name='혼다', order=17)
for name in ['어코드', '시빅', 'CR-V', 'HR-V', '파일럿']:
    CarModel.objects.create(brand=honda, name=name)

porsche = CarBrand.objects.create(name='포르쉐', order=18)
for name in ['카이엔', '파나메라', '마칸', '911', '718']:
    CarModel.objects.create(brand=porsche, name=name)

landrover = CarBrand.objects.create(name='랜드로버', order=19)
for name in ['레인지로버', '디펜더', '디스커버리', '이보크', '벨라']:
    CarModel.objects.create(brand=landrover, name=name)

jeep = CarBrand.objects.create(name='지프', order=20)
for name in ['랭글러', '그랜드체로키', '체로키', '레니게이드', '글래디에이터']:
    CarModel.objects.create(brand=jeep, name=name)

ford = CarBrand.objects.create(name='포드', order=21)
for name in ['머스탱', '익스플로러', '브롱코', 'F-150', '레인저']:
    CarModel.objects.create(brand=ford, name=name)

chevrolet = CarBrand.objects.create(name='쉐보레', order=22)
for name in ['트레일블레이저', '타호', '콜로라도', '이쿼녹스']:
    CarModel.objects.create(brand=chevrolet, name=name)

mini = CarBrand.objects.create(name='미니', order=23)
for name in ['쿠퍼', '클럽맨', '컨트리맨']:
    CarModel.objects.create(brand=mini, name=name)

peugeot = CarBrand.objects.create(name='푸조', order=24)
for name in ['208', '308', '408', '508', '2008', '3008', '5008']:
    CarModel.objects.create(brand=peugeot, name=name)

# Engine oils (5 types)
oil1 = EngineOil.objects.create(
    name='이코노미',
    description='경제적인 선택, 일반 주행에 적합',
    price=50000,
    order=1
)
oil1.fuel_types.add(fuel_gasoline, fuel_diesel)

oil2 = EngineOil.objects.create(
    name='스탠다드',
    description='합성유 기반, 균형 잡힌 성능과 보호',
    price=70000,
    order=2
)
oil2.fuel_types.add(fuel_gasoline, fuel_diesel)

oil3 = EngineOil.objects.create(
    name='프리미엄',
    description='고급 합성유, 향상된 엔진 보호와 연비',
    price=90000,
    order=3
)
oil3.fuel_types.add(fuel_gasoline, fuel_diesel)

oil4 = EngineOil.objects.create(
    name='하이퍼포먼스',
    description='최고급 전합성유, 고출력 엔진에 최적화',
    price=120000,
    order=4
)
oil4.fuel_types.add(fuel_gasoline, fuel_diesel)

oil5 = EngineOil.objects.create(
    name='레이싱',
    description='극한 성능, 스포츠카 및 튜닝카 전용',
    price=150000,
    order=5
)
oil5.fuel_types.add(fuel_gasoline, fuel_diesel)

# Additional Services
AdditionalService.objects.create(
    name='에어컨 필터 교체',
    description='깨끗한 실내 공기를 위한 에어컨 필터 교체',
    price=30000,
    order=1
)
AdditionalService.objects.create(
    name='와이퍼 블레이드 교체',
    description='전/후면 와이퍼 블레이드 교체',
    price=25000,
    order=2
)
AdditionalService.objects.create(
    name='에어 필터 교체',
    description='엔진 흡기 에어 필터 교체',
    price=20000,
    order=3
)
AdditionalService.objects.create(
    name='브레이크 오일 교체',
    description='제동 성능 유지를 위한 브레이크 오일 교체',
    price=50000,
    order=4
)
AdditionalService.objects.create(
    name='냉각수 보충',
    description='엔진 냉각수 점검 및 보충',
    price=15000,
    order=5
)
AdditionalService.objects.create(
    name='타이어 공기압 점검',
    description='4륜 타이어 공기압 점검 및 조정 (무료)',
    price=0,
    order=6
)

print('Done! Brands:', CarBrand.objects.count(), '/ Models:', CarModel.objects.count(), '/ Oils:', EngineOil.objects.count(), '/ Services:', AdditionalService.objects.count())
