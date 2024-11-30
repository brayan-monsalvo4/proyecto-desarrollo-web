from django.db import models

class Impresora(models.Model):
    id_impresora = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    marca = models.CharField(max_length=100)
    tipo = models.CharField(max_length=20)
    anio_lanzamiento = models.IntegerField()
    volumen_construccion = models.CharField(max_length=20)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    moneda = models.CharField(max_length=20)
    url_imagen = models.CharField(max_length=100)
    stock = models.IntegerField(default=20)

    class Meta:
        db_table = 'impresoras'  # Nombre exacto de la tabla en la base de datos

    def __str__(self):
        return f"{self.marca} {self.nombre}"
    
class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    id_impresora = models.ForeignKey('Impresora', on_delete=models.CASCADE, db_column='id_impresora')
    id_cliente = models.ForeignKey('Cliente', on_delete=models.CASCADE, db_column='id_cliente')
    fecha_venta = models.DateField()
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=50)

    class Meta:
        db_table = 'ventas'

    def save(self, *args, **kwargs):
        # Calcular el total automáticamente
        self.total = self.cantidad * self.precio_unitario
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Venta {self.id_venta} - {self.id_impresora.nombre}"
    
class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    email = models.CharField(unique=True, max_length=100)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    direccion = models.TextField()

    class Meta:
        db_table = 'clientes'
        #ordering = ['nombre']
        #verbose_name = 'Cliente'
        #verbose_name_plural = 'Clientes'

    #def __str__(self):
    #    return f"{self.nombre} ({self.email})"

    #def get_ventas_totales(self):
    #    return self.venta_set.count()

    #def get_monto_total_compras(self):
    #    return self.venta_set.aggregate(total=models.Sum('total'))['total'] or 0