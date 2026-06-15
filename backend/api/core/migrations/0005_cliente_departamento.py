from django.db import migrations, models
import django.db.models.deletion


def backfill_cliente_departamento(apps, schema_editor):
    Cliente = apps.get_model('core', 'Cliente')
    OrdemServico = apps.get_model('core', 'OrdemServico')

    for cliente in Cliente.objects.all().iterator():
        top_departamento = (
            OrdemServico.objects
            .filter(cliente_id=cliente.id, departamento_id__isnull=False)
            .values('departamento_id')
            .annotate(total=models.Count('id'))
            .order_by('-total', 'departamento_id')
            .first()
        )
        if top_departamento:
            cliente.departamento_id = top_departamento['departamento_id']
            cliente.save(update_fields=['departamento'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_ordemservico_aguardando_em_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='departamento',
            field=models.ForeignKey(
                blank=True,
                db_column='departamento_id',
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='clientes',
                to='core.opcaodepartamento',
            ),
        ),
        migrations.RunPython(backfill_cliente_departamento, migrations.RunPython.noop),
    ]
