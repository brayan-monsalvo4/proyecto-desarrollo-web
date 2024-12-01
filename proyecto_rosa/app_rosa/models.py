from django.db import models
from lxml import etree
from django.db import transaction
from decimal import Decimal
from django.db.utils import IntegrityError

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
    
    @classmethod
    def validar_dtd(cls, xml_etree, dtd_path):
        dtd = etree.DTD(open(dtd_path, "rb"))

        try:
            dtd.assertValid(xml_etree)

            return True

        except Exception as e:
            error_trace = ""
            for error in dtd.error_log:
                print(error)
                error_trace += f"Line {error.line}: {error.message}\n"

            raise Exception(error_trace)
        
        
    @classmethod
    def registrar_inventario_desde_xml(cls, xml_etree):
        with transaction.atomic():
            for producto in xml_etree:
                impresora = cls.objects.create(
                    nombre=producto[0].text,
                    marca=producto[1].text,
                    tipo=producto[2].text,
                    anio_lanzamiento=int(producto[3].text),
                    volumen_construccion=producto[4].text,
                    precio=Decimal(producto[5].text),
                    moneda=producto[6].text,
                    url_imagen=producto[7].text,
                    stock=(int(producto[8].text) if producto.find("stock") != None else 20)
                )

                impresora.save()

    @classmethod
    def eliminar_inventario_desde_xml(cls, xml_tree):
        with transaction.atomic():
            for id in xml_tree:
                cls.objects.filter(id_impresora=id.text).delete()

    @classmethod
    def modificar_inventario_desde_xml(cls, xml_tree):
        with transaction.atomic():
            for producto in xml_tree:
                impresora = cls.objects.filter(id_impresora=producto[0].text)[0]

                impresora.nombre = str(producto.find("nombre").text) if producto.find("nombre") != None else impresora.nombre
                impresora.marca = str(producto.find("marca").text) if producto.find("marca") != None else impresora.marca
                impresora.tipo = str(producto.find("tipo").text) if producto.find("tipo") != None else impresora.tipo
                impresora.anio_lanzamiento = int(producto.find("anio_lanzamiento").text) if producto.find("anio_lanzamiento") != None else impresora.anio_lanzamiento
                impresora.volumen_construccion = str(producto.find("volumen_construccion").text) if producto.find("volumen_construccion") != None else impresora.volumen_construccion
                impresora.precio = Decimal(producto.find("precio").text) if producto.find("precio") != None else impresora.precio
                impresora.moneda = str(producto.find("moneda").text) if producto.find("moneda") != None else impresora.moneda
                impresora.url_imagen = str(producto.find("url_imagen").text) if producto.find("url_imagen") != None else impresora.url_imagen
                impresora.stock = int(producto.find("stock").text) if producto.find("stock") != None else impresora.stock

                impresora.save() 
                

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

    def to_xml(self):
        venta = etree.Element("venta")

        etree.SubElement(venta, "id_venta").text = str(self.id_venta)
        etree.SubElement(venta, "id_cliente").text = str(self.id_cliente.id_cliente)
        etree.SubElement(venta, "id_impresora").text = str(self.id_impresora.id_impresora)
        etree.SubElement(venta, "fecha_venta").text = str(self.fecha_venta)
        etree.SubElement(venta, "cantidad").text = str(self.cantidad)
        etree.SubElement(venta, "precio_unitario").text = str(self.precio_unitario)
        etree.SubElement(venta, "total").text = str(self.total)
        etree.SubElement(venta, "metodo_pago").text = self.metodo_pago

        return venta
    
    @classmethod
    def get_xml_collection(cls, ventas):
        venta_raiz = etree.Element("ventas")

        for venta in ventas:
            venta_raiz.append(
                venta.to_xml()
            )

        return venta_raiz

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

    def to_xml(self):
        cliente = etree.Element("cliente")

        etree.SubElement(cliente, "id_cliente").text = str(self.id_cliente)
        etree.SubElement(cliente, "nombre").text = self.nombre
        etree.SubElement(cliente, "email").text = self.nombre
        etree.SubElement(cliente, "telefono").text = self.telefono
        etree.SubElement(cliente, "direccion").text = self.direccion

        return cliente
    
    @classmethod
    def get_xml_collection(cls, clientes):
        cliente_raiz = etree.Element("clientes")

        for cliente in clientes:
            cliente_raiz.append(
                cliente.to_xml()
            )

        return cliente_raiz