from django.db import migrations


def seed_data(apps, schema_editor):
    FuelType = apps.get_model('kiosk', 'FuelType')
    OilProduct = apps.get_model('kiosk', 'OilProduct')

    # 하이브리드 연료 타입 추가
    FuelType.objects.get_or_create(
        name='하이브리드',
        defaults={'order': 3},
    )

    # 오일 제품 시드 데이터
    products = [
        {
            'tier': 'economy',
            'name': '킥스 GX5/DX5',
            'oil_type': '합성유',
            'tagline': '경제적인 선택, 일반 주행에 적합',
            'mileage_interval': 6000,
            'badge': '',
            'badge_type': '',
            'is_visible': True,
            'order': 1,
        },
        {
            'tier': 'standard',
            'name': '킥스 GX7/토탈쿼츠',
            'oil_type': '고급 합성유',
            'tagline': '균형 잡힌 성능과 보호',
            'mileage_interval': 8000,
            'badge': '',
            'badge_type': '',
            'is_visible': True,
            'order': 2,
        },
        {
            'tier': 'premium',
            'name': '킥스 PAO',
            'oil_type': 'PAO 합성유',
            'tagline': '고급 합성유, 향상된 엔진 보호와 연비',
            'mileage_interval': 10000,
            'badge': '추천',
            'badge_type': 'recommended',
            'is_visible': True,
            'order': 3,
        },
        {
            'tier': 'premium_hybrid',
            'name': '벤졸 0w20',
            'oil_type': 'PAO 합성유',
            'tagline': '하이브리드 전용 프리미엄 오일',
            'mileage_interval': 10000,
            'badge': '',
            'badge_type': '',
            'is_visible': False,
            'order': 4,
        },
        {
            'tier': 'hyperformance',
            'name': '리스타 슈퍼노멀',
            'oil_type': '에스터 합성유',
            'tagline': '최고급 전합성유, 고출력 엔진에 최적화',
            'mileage_interval': 12000,
            'badge': '인기',
            'badge_type': 'popular',
            'is_visible': True,
            'order': 5,
        },
        {
            'tier': 'racing',
            'name': '리스타 메탈로센',
            'oil_type': '최고급 에스터',
            'tagline': '극한 성능, 스포츠카 및 튜닝카 전용',
            'mileage_interval': 15000,
            'badge': '최고급',
            'badge_type': 'premium',
            'is_visible': True,
            'order': 6,
        },
    ]

    for p in products:
        OilProduct.objects.update_or_create(
            tier=p['tier'],
            defaults=p,
        )


def reverse_seed(apps, schema_editor):
    FuelType = apps.get_model('kiosk', 'FuelType')
    OilProduct = apps.get_model('kiosk', 'OilProduct')
    FuelType.objects.filter(name='하이브리드').delete()
    OilProduct.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('kiosk', '0009_add_oil_product_price_and_car_generation'),
    ]

    operations = [
        migrations.RunPython(seed_data, reverse_seed),
    ]
