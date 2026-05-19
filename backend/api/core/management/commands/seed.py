from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from core.models import (Cliente, OrdemServico, HistoricoStatus, Iteracao,
                         PerfilUsuario, OpcaoUrgencia, OpcaoPrioridade,
                         OpcaoDepartamento, OpcaoTipo, OpcaoCategoria)


class Command(BaseCommand):
    help = 'Popula o banco com dados de demonstração'

    def handle(self, *args, **options):
        # ── Tabelas de Opções ──────────────────────────────────────────────────
        for n, lv in [('Baixa',1),('Média',2),('Alta',3),('Imediata',4)]:
            OpcaoUrgencia.objects.get_or_create(nome=n, defaults={'nivel':lv})
        for n, lv in [('Baixa',1),('Média',2),('Alta',3),('Crítica',4)]:
            OpcaoPrioridade.objects.get_or_create(nome=n, defaults={'nivel':lv})
        for n in ['TI','Suporte','Financeiro','RH','Comercial','Operações']:
            OpcaoDepartamento.objects.get_or_create(nome=n)
        for n in ['Incidente','Solicitação de Serviço','Problema','Manutenção']:
            OpcaoTipo.objects.get_or_create(nome=n)
        for n in ['Hardware','Software','Rede','Acesso','Banco de Dados','Outros']:
            OpcaoCategoria.objects.get_or_create(nome=n)

        # ── Usuários ───────────────────────────────────────────────────────────
        if not User.objects.filter(username='admin').exists():
            adm = User.objects.create_superuser('admin','admin@sgos.com','admin123',
                                                first_name='Administrador')
            PerfilUsuario.objects.get_or_create(
                usuario=adm,
                defaults={
                    'departamento': OpcaoDepartamento.objects.get(nome='TI'),
                },
            )

        if not User.objects.filter(username='gustavo').exists():
            u = User.objects.create_user('gustavo','gustavo@sgos.com','gustavo123',
                                         first_name='Gustavo', last_name='Monteiro')
            PerfilUsuario.objects.get_or_create(
                usuario=u,
                defaults={
                    'departamento': OpcaoDepartamento.objects.get(nome='Suporte'),
                },
            )

        func = User.objects.get(username='gustavo')

        # ── Clientes ───────────────────────────────────────────────────────────
        dados_clientes = [
            {'nome':'João da Silva',    'telefone':'(42) 99811-2233','email':'joao@email.com',    'endereco':'Rua das Flores, 123 – Ponta Grossa'},
            {'nome':'Maria Souza',      'telefone':'(42) 98877-4455','email':'maria@empresa.com', 'endereco':'Av. Brasil, 500 – Curitiba'},
            {'nome':'Pedro Lima',       'telefone':'(41) 99766-3344','email':'pedro@gmail.com',   'endereco':'Rua XV, 77 – Londrina'},
            {'nome':'Ana Costa',        'telefone':'(43) 98855-6677','email':'ana@corp.com',      'endereco':'Rua Tiradentes, 200 – Maringá'},
            {'nome':'Carlos Ramos',     'telefone':'(42) 99733-8899','email':'carlos@ramos.net',  'endereco':'Al. Santos, 1001 – São Paulo'},
            {'nome':'Lucia Ferreira',   'telefone':'(44) 98700-1122','email':'lucia@email.com',   'endereco':'Rua Sete de Setembro, 34 – Campo Mourão'},
            {'nome':'Roberto Nunes',    'telefone':'(41) 99622-7733','email':'roberto@nunes.com', 'endereco':'Rua da Paz, 88 – Pinhais'},
            {'nome':'Fernanda Alves',   'telefone':'(42) 98511-9900','email':'fernanda@alves.io', 'endereco':'Av. Getúlio Vargas, 320 – PG'},
        ]
        clientes = [Cliente.objects.get_or_create(email=d['email'], defaults=d)[0] for d in dados_clientes]

        # ── Ordens de Serviço ──────────────────────────────────────────────────
        if OrdemServico.objects.count() == 0:
            seq = OrdemServico.STATUS_ORDER
            os_data = [
                {'cliente':clientes[0],'titulo':'Computador não liga',          'descricao':'Máquina do setor financeiro não está ligando.','tipo':'Incidente',             'prioridade':'Alta',   'urgencia':'Alta',     'departamento':'TI',     'categoria':'Hardware','status_alvo':'aberta'},
                {'cliente':clientes[1],'titulo':'Solicitação de acesso ao ERP', 'descricao':'Novo colaborador precisa de login no ERP Totvs.','tipo':'Solicitação de Serviço','prioridade':'Média',  'urgencia':'Média',    'departamento':'TI',     'categoria':'Acesso',  'status_alvo':'aberta'},
                {'cliente':clientes[2],'titulo':'Impressora da recepção',       'descricao':'Impressora HP apresenta erro de papel.',         'tipo':'Incidente',             'prioridade':'Baixa',  'urgencia':'Baixa',    'departamento':'Suporte','categoria':'Hardware','status_alvo':'aguardando'},
                {'cliente':clientes[3],'titulo':'Sistema travando – relatório', 'descricao':'Módulo de relatórios trava com +500 linhas.',    'tipo':'Problema',              'prioridade':'Alta',   'urgencia':'Alta',     'departamento':'TI',     'categoria':'Software','status_alvo':'em_andamento'},
                {'cliente':clientes[4],'titulo':'Sem internet – ramal 302',     'descricao':'Perdeu internet após atualização do Windows.',   'tipo':'Incidente',             'prioridade':'Crítica','urgencia':'Imediata', 'departamento':'TI',     'categoria':'Rede',    'status_alvo':'em_andamento'},
                {'cliente':clientes[5],'titulo':'Atualização de driver de vídeo','descricao':'Monitor com resolução incorreta.',              'tipo':'Manutenção',            'prioridade':'Baixa',  'urgencia':'Baixa',    'departamento':'Suporte','categoria':'Hardware','status_alvo':'em_avaliacao'},
                {'cliente':clientes[6],'titulo':'Reinstalação do Office 365',   'descricao':'Licença do Office expirou.',                    'tipo':'Solicitação de Serviço','prioridade':'Média',  'urgencia':'Média',    'departamento':'TI',     'categoria':'Software','status_alvo':'encerrada'},
                {'cliente':clientes[7],'titulo':'Backup servidor não executa',  'descricao':'Job de backup noturno falha silenciosamente.',  'tipo':'Problema',              'prioridade':'Crítica','urgencia':'Imediata', 'departamento':'TI',     'categoria':'Software','status_alvo':'encerrada'},
            ]

            for d in os_data:
                alvo = d.pop('status_alvo')
                d['prioridade'] = OpcaoPrioridade.objects.get(nome=d['prioridade'])
                d['tipo'] = OpcaoTipo.objects.get(nome=d['tipo'])
                d['categoria'] = OpcaoCategoria.objects.get(nome=d['categoria'])
                d['urgencia'] = OpcaoUrgencia.objects.get(nome=d['urgencia'])
                d['departamento'] = OpcaoDepartamento.objects.get(nome=d['departamento'])
                os_obj = OrdemServico.objects.create(criado_por=func, **d)
                HistoricoStatus.objects.create(
                    os=os_obj, status_anterior='', status_novo='aberta',
                    alterado_por=func, observacao='OS criada.')

                idx_alvo = seq.index(alvo)
                for i in range(1, idx_alvo + 1):
                    os_obj.status = seq[i]
                    os_obj.save()
                    HistoricoStatus.objects.create(
                        os=os_obj, status_anterior=seq[i-1], status_novo=seq[i], alterado_por=func)

                Iteracao.objects.create(os=os_obj, criado_por=func, texto='Análise inicial realizada. Aguardando resposta do cliente.')

        self.stdout.write(self.style.SUCCESS('Seed OK! admin/admin123 | gustavo/gustavo123'))
