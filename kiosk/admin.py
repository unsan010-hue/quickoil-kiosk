from django.contrib import admin
from .models import CarBrand, CarModel, FuelType, EngineOil


@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'order']
    list_filter = ['brand']
    list_editable = ['order']


@admin.register(FuelType)
class FuelTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'order']
    list_editable = ['order']


@admin.register(EngineOil)
class EngineOilAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'is_active', 'order']
    list_filter = ['fuel_types', 'is_active']
    list_editable = ['price', 'is_active', 'order']
