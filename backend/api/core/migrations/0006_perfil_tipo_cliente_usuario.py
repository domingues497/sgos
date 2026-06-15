from django.db import migrations, models
from django.contrib.auth.hashers import make_password
import django.db.models.deletion


def _split_name(nome):
    nome = (nome or '').strip()
    if not nome:
        return '', ''
    parts = nome.split()
    return parts[0], ' '.join(parts[1:])


def _unique_username(User, base_username):
    base = (base_username or 'cliente').strip().lower()
    base = ''.join(ch for ch in base if ch.isalnum() or ch in '._-')
    base = base or 'cliente'
    username = base[:150]
    index = 1
    while User.objects.filter(username=username).exists():
        suffix = f'.{index}'
        username = f'{base[:150-len(suffix)]}{suffix}'
        index += 1
    return username


def backfill_users_and_roles(apps, schema_editor):
    User = apps.get_model('auth', 'User')
    Group = apps.get_model('auth', 'Group')
    Cliente = apps.get_model('core', 'Cliente')
    PerfilUsuario = apps.get_model('core', 'PerfilUsuario')

    tecnico_group = Group.objects.filter(name='Tecnicos').first()
    tecnico_ids = set()
    if tecnico_group:
        tecnico_ids = set(tecnico_group.user_set.values_list('id', flat=True))

    for user in User.objects.all().iterator():
        perfil, _ = PerfilUsuario.objects.get_or_create(usuario_id=user.id)
        if user.is_superuser:
            perfil.tipo = 'admin'
        elif user.id in tecnico_ids:
            perfil.tipo = 'tecnico'
        else:
            perfil.tipo = 'somente_cliente'
        perfil.save(update_fields=['tipo'])

    for cliente in Cliente.objects.filter(usuario_id__isnull=True).iterator():
        base_username = cliente.email.split('@')[0] if cliente.email else cliente.nome
        username = _unique_username(User, base_username)
        first_name, last_name = _split_name(cliente.nome)
        user = User.objects.create(
            username=username,
            email=cliente.email or '',
            first_name=first_name,
            last_name=last_name,
            is_active=True,
            is_staff=False,
            is_superuser=False,
            password=make_password(None),
        )
        perfil, _ = PerfilUsuario.objects.get_or_create(usuario_id=user.id)
        perfil.tipo = 'somente_cliente'
        if getattr(cliente, 'departamento_id', None):
            perfil.departamento_id = cliente.departamento_id
        perfil.save()
        cliente.usuario_id = user.id
        cliente.save(update_fields=['usuario'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_cliente_departamento'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.AddField(
            model_name='cliente',
            name='usuario',
            field=models.OneToOneField(blank=True, db_column='usuario_id', null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cliente_vinculado', to='auth.user'),
        ),
        migrations.AddField(
            model_name='perfilusuario',
            name='tipo',
            field=models.CharField(choices=[('admin', 'Administrador'), ('tecnico', 'Técnico'), ('somente_cliente', 'Somente Cliente')], default='somente_cliente', max_length=20),
        ),
        migrations.RunPython(backfill_users_and_roles, migrations.RunPython.noop),
    ]
