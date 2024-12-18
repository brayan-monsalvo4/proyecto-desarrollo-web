# Generated by Django 5.1.3 on 2024-11-22 23:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id_cliente', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('direccion', models.TextField()),
                ('fecha_registro', models.DateField(auto_now_add=True)),
                ('activo', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Cliente',
                'verbose_name_plural': 'Clientes',
                'db_table': 'clientes',
                'ordering': ['nombre'],
            },
        ),
        migrations.CreateModel(
            name='Impresora3D',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('marca', models.CharField(max_length=100)),
                ('nombre', models.CharField(max_length=100)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('velocidad_mm_s', models.IntegerField()),
                ('stock', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'impresoras_3d',
            },
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id_venta', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_venta', models.DateField()),
                ('cantidad', models.IntegerField()),
                ('precio_unitario', models.DecimalField(decimal_places=2, max_digits=10)),
                ('total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('metodo_pago', models.CharField(max_length=50)),
                ('id_cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_rosa.cliente')),
                ('id_impresora', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app_rosa.impresora3d')),
            ],
            options={
                'db_table': 'ventas',
            },
        ),
    ]
