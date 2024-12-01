from django.db import models
from lxml import etree

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
    
    def to_xml(self):
        impresora = etree.Element("impresora")

        etree.SubElement(impresora, "nombre").text = self.nombre
        etree.SubElement(impresora, "marca").text = self.marca
        etree.SubElement(impresora, "tipo").text = self.tipo
        etree.SubElement(impresora, "anio_lanzamiento").text = str(self.anio_lanzamiento)
        etree.SubElement(impresora, "volumen_construccion").text = self.volumen_construccion
        etree.SubElement(impresora, "precio").text = str(self.precio)
        etree.SubElement(impresora, "moneda").text = self.moneda
        etree.SubElement(impresora, "url_imagen").text = self.url_imagen
        etree.SubElement(impresora, "stock").text = str(self.stock)

        return impresora
    
    @classmethod
    def get_xml_collecion(cls, impresoras):
        impresora_raiz = etree.Element("impresoras")

        for impresora in impresoras:
            impresora_raiz.append(
                impresora.to_xml()
            )
        
        return impresora_raiz
    
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