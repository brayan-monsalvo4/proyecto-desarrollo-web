from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Impresora
from .models import Venta
from .models import Cliente
from django.http import HttpResponse
import random
from django.db.models import Sum
from django.db import transaction
from datetime import datetime, timedelta
from decimal import Decimal
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder
from pykalman import KalmanFilter
from lxml import etree


def _genera_fecha_aleatoria(fecha_inicio, fecha_fin):
        dias_entre_fechas = (fecha_fin - fecha_inicio).days

        # Genera un número aleatorio de días dentro del rango
        dias_aleatorios = random.randint(0, dias_entre_fechas)

        # Suma los días aleatorios a la fecha de inicio
        fecha_aleatoria = fecha_inicio + timedelta(days=dias_aleatorios)

        return fecha_aleatoria.strftime("%Y-%m-%d")


def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Verificación simple de usuario y contraseña
        if username == 'admin' and password == 'contraseña':
            return redirect('inventario/')  # Redirige a la página principal si las credenciales son correctas
        elif username == 'usuario' and password == 'contraseña':
            return redirect('primero')  # Redirige a otro template si las credenciales son las de 'usuario2'
        else:
            error_message = 'Usuario o contraseña incorrectos'
            return render(request, 'login.html', {'error_message': error_message})

    return render(request, 'login.html')  # Muestra el formulario de login

#------ventas-------

def ventas(request):
    return render(request, "ventas.html")

def realizar_venta(request):

    return render(request, "realizar_venta.html")

def generar_ventas_aleatorias(request):
    impresoras = list(Impresora.objects.all())
    clientes = list(Cliente.objects.all())

    if not clientes or not impresoras:
        return HttpResponse("No hay clientes o impresoras!", status=404)

    numero_ventas = random.randint(1, 10)

    for _ in range(numero_ventas):
        impresora = random.choice(impresoras)
        cliente = random.choice(clientes)

        ventas_previas = Venta.objects.filter(id_impresora=impresora).aggregate(total_vendido=Sum('cantidad'))['total_vendido'] or 0

        disponibles = max(0, impresora.stock - ventas_previas)
        
        if disponibles == 0:
                print(f"no hay impresoras disponibles con el sig id. {impresora.id_impresora}, cantidad disponible: {disponibles} y en stock {impresora.stock}")
                continue
            
        cantidad = random.randint(1, min(3, disponibles))

        precio_unitario = impresora.precio

        metodos_pago = ["Efectivo", "Transferencia", "Tarjeta de Credito", "PayPal"]

        with transaction.atomic():
            venta = Venta.objects.create(
                id_impresora=impresora,
                id_cliente=cliente,
                fecha_venta=_genera_fecha_aleatoria(fecha_inicio=datetime(2020, 1, 1), fecha_fin=datetime(2024, 12, 31)),
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                total=Decimal(cantidad)*precio_unitario,
                metodo_pago=random.choice(metodos_pago)
            )
            
            print(venta)

        with transaction.atomic():
            impresora.stock = impresora.stock - cantidad

            impresora.save()

    return render(request, "ventas.html")

def consultar_ventas(request):
    ventas = Venta.objects.all().order_by("-fecha_venta")

    if not ventas:
        return HttpResponse("No hay ventas!", status=404)

    context = {
        "ventas" : ventas
    }

    return render(request, "ventas/consultar_ventas.html", context)

def descargar_ventas(request):
    if not request.method == "GET":
        return render(request, "ventas/consultar_ventas.html")
    
    raiz = Venta.get_xml_collection( Venta.objects.all() )

    response = HttpResponse(etree.tostring(raiz, pretty_print=True, encoding="utf-8", xml_declaration=True), content_type="application/xml")
    response["Content-Disposition"] = "attatchment; filename=ventas.xml"

    return response


#-----clientes------

def clientes(request):
    return render(request, "clientes.html")

def registrar_cliente(request):
    return render(request, "cliente/registrar_cliente.html")

def consultar_clientes(request):
    clientes = Cliente.objects.all().order_by("id_cliente")

    context = {
        "clientes" : clientes
    }
    
    return render(request, "clientes/consultar_clientes.html", context)

#-------inventario-------

def inventario(request):
    return render(request, "inventario.html")

def consultar_inventario(request):
    impresoras = Impresora.objects.all().order_by("stock")

    context = {
        "impresoras" : impresoras
    }

    return render(request, "inventario/consultar_inventario.html", context)

def descargar_inventario(request):
    if not request.method == "GET":
        return render(request, "inventario/consultar_inventario.html")
    
    raiz = Impresora.get_xml_collecion( Impresora.objects.all() )

    response = HttpResponse(etree.tostring(raiz, pretty_print=True, encoding="utf-8", xml_declaration=True), content_type="application/xml")

    response["Content-Disposition"] = "attachment; filename=impresoras.xml"
    
    return response


#--------analisis---------

def analisis(request):
    return render(request, "analisis.html")

def regresion_lineal(request): 
    fecha_base = pd.to_datetime("2020-01-01")

    nombre_producto = request.GET.get("nombre_producto", "")

    print(f"nombre del producto: {nombre_producto}")

    if not nombre_producto or len( Venta.objects.filter(id_impresora__nombre=nombre_producto) ) == 0:
        return render(request, "analisis.html")
    

    ventas = Venta.objects.filter(id_impresora__nombre=nombre_producto).values("cantidad", "fecha_venta", "id_impresora__nombre")
    print(f"venta {ventas}")
    df = pd.DataFrame(ventas)

    df["fecha_venta"] = pd.to_datetime(df["fecha_venta"])

    df["fecha_venta"] = (df["fecha_venta"] - fecha_base).dt.days

    x = pd.DataFrame(df["fecha_venta"])
    y = df["cantidad"]

    #x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=1, test_size=None, random_state=42)

    modelo = LinearRegression().fit(x, y)

    plt.figure(figsize=(4, 3), dpi=300)  # Aumenta tamaño y resolución
    #plt.style.use('seaborn')  # Estilo más moderno

    fig, ax = plt.subplots(figsize=(4, 3), dpi=300)

    # Scatter plot con más detalles
    ax.scatter(x, y, color='green', alpha=0.7, label='Historial de compras')

    # Línea de regresión
    ax.plot(x, modelo.predict(x), color='red', linewidth=1, label='Predicción')

    # Personalización de ejes
    ax.set_title('Regresión Lineal', fontsize=10)
    ax.set_xlabel('Días', fontsize=8)
    ax.set_ylabel('Impresoras vendidas', fontsize=8)

    ax.tick_params(axis='both', which='major', labelsize=8)

    # Ecuación de la regresión
    pendiente = modelo.coef_[0]
    print(f"pendiente {pendiente}")
    print(f"{"positiva" if pendiente > 0 else "negativa"}")

    # Rejilla
    ax.grid(True, linestyle='--', alpha=0.7)

    # Leyenda
    ax.legend()

    # Ajustar márgenes
    plt.tight_layout()

    # Guardar con mayor calidad
    nombre_plot = f"images/regresion_lineal/plot.png"
    fig.savefig(f"app_rosa/static/{nombre_plot}", dpi=300)

    # Cerrar la figura para liberar memoria
    plt.close(fig)

    print(f"desviacion estandar: {np.std(x)["fecha_venta"]}")

    context = {
        "nombre_plot" : nombre_plot,
        "nombre_producto" : ventas[0]["id_impresora__nombre"],
        "pendiente" : "positiva" if pendiente > 0 else "negativa",
        "media_x" : np.mean(x),
        "media_y" : np.mean(y),
        "desviacion_estandar_x" : float(np.std(x)),
        "desviacion_estandar_y" : np.std(y)
    }

    return render(request, "modelos/regresion_lineal.html", context)

def regresion_polinomial(request):

    fecha_base = pd.to_datetime("2020-01-01")

    nombre_producto = request.GET.get("nombre_producto", "")

    ventas = Venta.objects.filter(id_impresora__nombre=nombre_producto).values("cantidad", "fecha_venta", "id_impresora__nombre")

    if not nombre_producto or len( ventas ) == 0:
        return render(request, "analisis.html")
    
    df = pd.DataFrame(ventas)

    df["fecha_venta"] = pd.to_datetime(df["fecha_venta"])

    df["fecha_venta"] = (df["fecha_venta"] - fecha_base).dt.days

    df = df.sort_values("fecha_venta")

    x = pd.DataFrame(df["fecha_venta"])
    y = df["cantidad"]

    #x_train, x_test, y_train, y_test = train_test_split(x, y, train_size=1, test_size=None, random_state=42)

    modelo = make_pipeline(
        PolynomialFeatures(degree=2),  # Grado del polinomio
        LinearRegression()
    ).fit(x, y)

    plt.figure(figsize=(4, 3), dpi=300)  # Aumenta tamaño y resolución
    #plt.style.use('seaborn')  # Estilo más moderno

    fig, ax = plt.subplots(figsize=(4.5, 3.5), dpi=300)

    # Scatter plot con más detalles
    ax.scatter(x, y, color='green', alpha=0.7, label='Historial de compras')

    # Línea de regresión
    #ax.plot(np.linspace(0, 1826, 1826), modelo.predict(np.linspace(0, 1826, 1826).reshape(-1, 1)), color='red', linewidth=1, label='Predicción')
    ax.plot(np.linspace(0, 1826, 1826), modelo.predict(np.linspace(0, 1826, 1826).reshape(-1, 1) ), color='red', linewidth=1, label='Predicción')


    # Personalización de ejes
    ax.set_title('Regresión Polinomial', fontsize=10)
    ax.set_xlabel('Días', fontsize=8)
    ax.set_ylabel('Impresoras vendidas', fontsize=8)

    ax.tick_params(axis='both', which='major', labelsize=8)

    # Ecuación de la regresión
    pendiente = modelo.named_steps['linearregression'].coef_
    print(f"pendiente {pendiente}")
    print(f"{"positiva" if sum(modelo.named_steps['linearregression'].coef_) > 0 else "negativa"}")

    # Rejilla
    ax.grid(True, linestyle='--', alpha=0.7)

    # Leyenda
    ax.legend()

    # Ajustar márgenes
    plt.tight_layout()

    # Guardar con mayor calidad
    nombre_plot = f"images/regresion_polinomial/plot.png"
    fig.savefig(f"app_rosa/static/{nombre_plot}", dpi=300)

    # Cerrar la figura para liberar memoria
    plt.close(fig)

    print(f"desviacion estandar: {np.std(x)["fecha_venta"]}")

    context = {
        "nombre_plot" : nombre_plot,
        "nombre_producto" : ventas[0]["id_impresora__nombre"],
        "pendiente" : "positiva" if modelo.named_steps['linearregression'].coef_[2] > 0  else "negativa",
        "media_x" : np.mean(x),
        "media_y" : np.mean(y),
        "desviacion_estandar_x" : float(np.std(x)),
        "desviacion_estandar_y" : np.std(y)
    }

    return render(request, "modelos/regresion_polinomial.html", context)

def algoritmo_kalman(request):
    
    fecha_base = pd.to_datetime("2020-01-01")

    nombre_producto = request.GET.get("nombre_producto")

    ventas = Venta.objects.filter(id_impresora__nombre=nombre_producto).values("cantidad", "fecha_venta", "id_impresora__nombre")

    if not nombre_producto or len( ventas ) == 0:
        return render(request, "analisis.html")
    
    df = pd.DataFrame(ventas)

    df["fecha_venta"] = pd.to_datetime(df["fecha_venta"])

    df["fecha_venta"] = (df["fecha_venta"] - fecha_base).dt.days

    df = df.sort_values("fecha_venta")  # Asegúrate de que esté ordenado
    ventas = df["cantidad"].values

    # Crear filtro de Kalman
    kf = KalmanFilter(
        transition_matrices=[[1, 1], [0, 1]],  # Modelo lineal
        observation_matrices=[[1, 0]],  # Relación estado-observación
        initial_state_mean=[ventas[0], 0],  # Inicialización
        initial_state_covariance=[[1, 0], [0, 1]],
        observation_covariance=1,  # Varianza de las observaciones
        transition_covariance=[[0.1, 0], [0, 0.1]]  # Suavizado
    )

    # Ajustar el filtro a los datos observados
    state_means, state_covariances = kf.filter(ventas)

    # Predicciones
    predicciones = state_means[:, 0]

    pendientes = np.diff(predicciones)

    # Visualización
    plt.figure(figsize=(4, 3), dpi=300)  # Alta resolución
    plt.plot(df["fecha_venta"], ventas, label="Ventas reales", color="green")
    plt.plot(df["fecha_venta"], predicciones, label="Predicciones Kalman", color="purple")

    print(f"prediccion de kalman")
    print(predicciones)

    plt.xlabel("Fecha")
    plt.ylabel("Cantidad de impresoras vendidas")
    plt.title("Predicción con Filtro de Kalman")
    plt.legend()
    plt.grid()
    plt.tight_layout()

    # Guardar la imagen
    nombre_plot = "images/algoritmo_kalman/plot.jpg"
    plt.savefig(f"app_rosa/static/{nombre_plot}", dpi=300)

    # Cerrar para liberar memoria
    plt.close()

    context = {
        "nombre_producto" : nombre_producto,
        "pendiente" : "positiva" if pendientes[-1] > 0 else "negativa",
        "nombre_plot" : nombre_plot
    }

    return render(request, "modelos/algoritmo_kalman.html", context)
