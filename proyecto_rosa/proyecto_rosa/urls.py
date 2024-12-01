"""
URL configuration for proyecto_rosa project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from app_rosa import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.login, name='login'),
    path("inventario/", views.inventario, name="inventario/"),
    path("inventario/consultar_inventario/", views.consultar_inventario, name="inventario/consultar_inventario/"),
    path("inventario/descargar_inventario/", views.descargar_inventario, name="inventario/descargar_inventario/"),
    path("analisis/", views.analisis, name="analisis/"),
    path("modelos/regresion_lineal/", views.regresion_lineal, name="modelos/regresion_lineal/"),
    path("modelos/regresion_polinomial/", views.regresion_polinomial, name="modelos/regresion_polinomial/"),
    path("modelos/algoritmo_kalman/", views.algoritmo_kalman, name="modelos/algoritmo_kalman/"),
    path("ventas/", views.ventas, name="ventas/"),
    path("ventas/consultar_ventas/", views.consultar_ventas, name="ventas/consultar_ventas/"),
    path("ventas/descargar_ventas/", views.descargar_ventas, name="ventas/descargar_ventas/"),
    path("ventas/generar_ventas_aleatorias/", views.generar_ventas_aleatorias, name="ventas/generar_ventas_aleatorias/"),
    path("clientes/", views.clientes, name="clientes/"),
    path("clientes/consultar_clientes/", views.consultar_clientes, name="clientes/consultar_clientes/")
]
