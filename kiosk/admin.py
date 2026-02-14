from django.contrib import admin
from .models import CarBrand, CarModel, FuelType, EngineOil, OilProduct, OilPrice


@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'parent', 'order']
    list_filter = ['brand', 'parent']
    list_editable = ['order']
    search_fields = ['name']


@admin.register(FuelType)
class FuelTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']


@admin.register(EngineOil)
class EngineOilAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active', 'order']
    list_filter = ['fuel_types', 'is_active']
    list_editable = ['price', 'is_active', 'order']


@admin.register(OilProduct)
class OilProductAdmin(admin.ModelAdmin):
    list_display = ['tier', 'name', 'oil_type', 'mileage_interval', 'is_visible', 'is_active', 'order']
    list_filter = ['is_visible', 'is_active']
    list_editable = ['is_visible', 'is_active', 'order']


class OilPriceInline(admin.TabularInline):
    model = OilPrice
    extra = 0


@admin.register(OilPrice)
class OilPriceAdmin(admin.ModelAdmin):
    list_display = ['car_model', 'oil_product', 'fuel_type', 'price']
    list_filter = ['oil_product', 'fuel_type', 'car_model__brand']
    search_fields = ['car_model__name', 'car_model__parent__name']
    list_editable = ['price']
