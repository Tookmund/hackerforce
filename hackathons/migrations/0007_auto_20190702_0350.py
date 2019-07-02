# Generated by Django 2.1.9 on 2019-07-02 03:50

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_auto_20190630_0943'),
        ('hackathons', '0006_sponsorship_notes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lead',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('U', 'Uncontacted'), ('C', 'Contacted')], max_length=1)),
                ('role', models.CharField(choices=[('N', 'None'), ('P', 'Primary')], max_length=1)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leads', to='contacts.Contact')),
            ],
        ),
        migrations.AddField(
            model_name='hackathon',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='hackathon',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='perk',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='perk',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='tier',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='tier',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterField(
            model_name='sponsorship',
            name='status',
            field=models.CharField(choices=[('preparing', 'Preparing'), ('contacted', 'Contacted'), ('responded', 'Responded'), ('confirmed', 'Confirmed'), ('denied', 'Denied'), ('ghosted', 'Ghosted'), ('paid', 'Paid')], max_length=12),
        ),
        migrations.AddField(
            model_name='lead',
            name='sponsorship',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='leads', to='hackathons.Sponsorship'),
        ),
    ]
