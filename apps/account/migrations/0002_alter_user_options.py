# Generated by Django 4.2.6 on 2023-11-15 15:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='user',
            options={'permissions': [('admin-panel', 'پنل مدیریت')], 'verbose_name': 'کاربر', 'verbose_name_plural': 'کاربران'},
        ),
    ]