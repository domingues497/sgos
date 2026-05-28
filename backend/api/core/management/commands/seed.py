from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
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

        urg = {o.nome: o for o in OpcaoUrgencia.objects.all()}
        pri = {o.nome: o for o in OpcaoPrioridade.objects.all()}
        dep = {o.nome: o for o in OpcaoDepartamento.objects.all()}
        tip = {o.nome: o for o in OpcaoTipo.objects.all()}
        cat = {o.nome: o for o in OpcaoCategoria.objects.all()}

        # ── Usuários ───────────────────────────────────────────────────────────
        user_specs = [
            {
                'username': 'admin',
                'email': 'admin@sgos.com',
                'password': 'admin123',
                'first_name': 'Administrador',
                'last_name': '',
                'is_superuser': True,
                'departamento': 'TI',
            },
            {
                'username': 'rafael',
                'email': 'rafael@sgos.com',
                'password': 'rafael123',
                'first_name': 'Rafael',
                'last_name': 'Domingues',
                'is_superuser': False,
                'departamento': 'Suporte',
            },
            {
                'username': 'gustavo',
                'email': 'gustavo@sgos.com',
                'password': 'gustavo123',
                'first_name': 'Gustavo',
                'last_name': 'Monteiro',
                'is_superuser': False,
                'departamento': 'TI',
            },
            {
                'username': 'ana',
                'email': 'ana@sgos.com',
                'password': 'ana123',
                'first_name': 'Ana',
                'last_name': 'Costa',
                'is_superuser': False,
                'departamento': 'Financeiro',
            },
            {
                'username': 'juliana',
                'email': 'juliana@sgos.com',
                'password': 'juliana123',
                'first_name': 'Juliana',
                'last_name': 'Mendes',
                'is_superuser': False,
                'departamento': 'RH',
            },
            {
                'username': 'bruno',
                'email': 'bruno@sgos.com',
                'password': 'bruno123',
                'first_name': 'Bruno',
                'last_name': 'Ramos',
                'is_superuser': False,
                'departamento': 'Comercial',
            },
        ]

        for s in user_specs:
            if User.objects.filter(username=s['username']).exists():
                u = User.objects.get(username=s['username'])
            else:
                if s['is_superuser']:
                    u = User.objects.create_superuser(
                        s['username'],
                        s['email'],
                        s['password'],
                        first_name=s['first_name'],
                        last_name=s['last_name'],
                    )
                else:
                    u = User.objects.create_user(
                        s['username'],
                        s['email'],
                        s['password'],
                        first_name=s['first_name'],
                        last_name=s['last_name'],
                    )

            p, _ = PerfilUsuario.objects.get_or_create(
                usuario=u,
                defaults={'departamento': dep.get(s['departamento'])},
            )
            if not p.departamento:
                p.departamento = dep.get(s['departamento'])
                p.save(update_fields=['departamento'])

        func = User.objects.get(username='rafael')
        staff_users = [User.objects.get(username=u['username']) for u in user_specs if not u['is_superuser']]
        staff_by_dept = {}
        for u in staff_users:
            depto = getattr(getattr(u, 'perfil', None), 'departamento', None)
            key = depto.nome if depto else None
            if key:
                staff_by_dept.setdefault(key, []).append(u)

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
            {'nome':'Empresa Alfa LTDA','telefone':'(11) 4002-8922','email':'contato@alfa.com.br', 'endereco':'Rua do Comércio, 10 – São Paulo'},
            {'nome':'Empresa Beta SA',  'telefone':'(21) 3222-1100','email':'ti@beta.com.br',      'endereco':'Av. Atlântica, 250 – Rio de Janeiro'},
            {'nome':'Clínica Saúde',    'telefone':'(41) 3030-9090','email':'suporte@clinic.com.br','endereco':'Rua das Palmeiras, 900 – Curitiba'},
            {'nome':'Loja Centro',      'telefone':'(43) 3333-2222','email':'financeiro@lojacentro.com.br','endereco':'Av. Central, 55 – Londrina'},
            {'nome':'TransLog',         'telefone':'(44) 9999-1212','email':'operacoes@translog.com.br','endereco':'Rod. PR-317, Km 2 – Maringá'},
            {'nome':'Universidade X',   'telefone':'(42) 3123-4567','email':'helpdesk@univx.edu.br','endereco':'Av. Universitária, 1 – Ponta Grossa'},
            {'nome':'Condomínio Vista', 'telefone':'(41) 3555-6677','email':'sindico@vistacond.com.br','endereco':'Rua das Araucárias, 300 – Pinhais'},
            {'nome':'Fábrica Norte',    'telefone':'(11) 2888-0001','email':'manutencao@fabnorte.com.br','endereco':'Av. Industrial, 700 – São Paulo'},
            {'nome':'Padaria Bons Pães','telefone':'(42) 3255-4141','email':'dono@bonspaes.com.br','endereco':'Rua do Pão, 12 – Ponta Grossa'},
            {'nome':'Escritório Delta', 'telefone':'(43) 3777-1122','email':'adm@deltaoffice.com.br','endereco':'Rua das Acácias, 80 – Londrina'},
        ]
        clientes = [Cliente.objects.get_or_create(email=d['email'], defaults=d)[0] for d in dados_clientes]
        clientes_by_email = {c.email: c for c in clientes}

        # ── Ordens de Serviço ──────────────────────────────────────────────────
        seq = OrdemServico.STATUS_ORDER
        now = timezone.now()
        os_specs = [
            {'cliente_email':'joao@email.com','titulo':'Computador não liga',           'descricao':'Máquina do setor financeiro não está ligando.','tipo':'Incidente',             'prioridade':'Alta',   'urgencia':'Alta',     'departamento':'TI',         'categoria':'Hardware',       'status_alvo':'aberta',       'dias_atras': 2,  'etapa':'triagem',    'valor_total': None},
            {'cliente_email':'maria@empresa.com','titulo':'Solicitação de acesso ao ERP','descricao':'Novo colaborador precisa de login no ERP Totvs.','tipo':'Solicitação de Serviço','prioridade':'Média',  'urgencia':'Média',    'departamento':'TI',         'categoria':'Acesso',         'status_alvo':'aberta',       'dias_atras': 1,  'etapa':'cadastro',   'valor_total': None},
            {'cliente_email':'pedro@gmail.com','titulo':'Impressora da recepção',      'descricao':'Impressora HP apresenta erro de papel.',         'tipo':'Incidente',             'prioridade':'Baixa',  'urgencia':'Baixa',    'departamento':'Suporte',    'categoria':'Hardware',       'status_alvo':'aguardando',   'dias_atras': 5,  'etapa':'aguardando_cliente','valor_total': None},
            {'cliente_email':'ana@corp.com','titulo':'Sistema travando – relatório',   'descricao':'Módulo de relatórios trava com +500 linhas.',    'tipo':'Problema',              'prioridade':'Alta',   'urgencia':'Alta',     'departamento':'TI',         'categoria':'Software',       'status_alvo':'em_andamento', 'dias_atras': 9,  'etapa':'execucao',   'valor_total': None},
            {'cliente_email':'carlos@ramos.net','titulo':'Sem internet – ramal 302',   'descricao':'Perdeu internet após atualização do Windows.',   'tipo':'Incidente',             'prioridade':'Crítica','urgencia':'Imediata', 'departamento':'TI',         'categoria':'Rede',           'status_alvo':'em_andamento', 'dias_atras': 3,  'etapa':'diagnostico','valor_total': None},
            {'cliente_email':'lucia@email.com','titulo':'Atualização de driver de vídeo','descricao':'Monitor com resolução incorreta.',            'tipo':'Manutenção',            'prioridade':'Baixa',  'urgencia':'Baixa',    'departamento':'Suporte',    'categoria':'Hardware',       'status_alvo':'em_avaliacao', 'dias_atras': 14, 'etapa':'validacao',  'valor_total': 120.00},
            {'cliente_email':'roberto@nunes.com','titulo':'Reinstalação do Office 365','descricao':'Licença do Office expirou.',                    'tipo':'Solicitação de Serviço','prioridade':'Média',  'urgencia':'Média',    'departamento':'TI',         'categoria':'Software',       'status_alvo':'encerrada',    'dias_atras': 25, 'etapa':'entrega',    'valor_total': 80.00},
            {'cliente_email':'fernanda@alves.io','titulo':'Backup servidor não executa','descricao':'Job de backup noturno falha silenciosamente.', 'tipo':'Problema',              'prioridade':'Crítica','urgencia':'Imediata', 'departamento':'TI',         'categoria':'Software',       'status_alvo':'encerrada',    'dias_atras': 40, 'etapa':'pos_mortem', 'valor_total': 560.00},
            {'cliente_email':'contato@alfa.com.br','titulo':'VPN cai ao conectar',     'descricao':'Usuários remotos perdem conexão após 3–5 minutos.','tipo':'Incidente',            'prioridade':'Alta',   'urgencia':'Alta',     'departamento':'TI',         'categoria':'Rede',           'status_alvo':'aguardando',   'dias_atras': 6,  'etapa':'coleta_logs','valor_total': None},
            {'cliente_email':'ti@beta.com.br','titulo':'Erro de permissão no compartilhamento','descricao':'Pasta \\\\fileserver\\financeiro retorna acesso negado.','tipo':'Solicitação de Serviço','prioridade':'Média','urgencia':'Média','departamento':'TI','categoria':'Acesso','status_alvo':'em_andamento','dias_atras': 7,'etapa':'ajuste_acl','valor_total': None},
            {'cliente_email':'suporte@clinic.com.br','titulo':'Sistema de agendamento lento','descricao':'Tela de agenda demora mais de 20s para carregar.','tipo':'Problema','prioridade':'Alta','urgencia':'Média','departamento':'TI','categoria':'Banco de Dados','status_alvo':'em_avaliacao','dias_atras': 18,'etapa':'tuning','valor_total': 300.00},
            {'cliente_email':'financeiro@lojacentro.com.br','titulo':'Emissão de NF-e falha','descricao':'Aplicativo retorna erro 599 ao transmitir.','tipo':'Incidente','prioridade':'Crítica','urgencia':'Imediata','departamento':'Financeiro','categoria':'Software','status_alvo':'em_andamento','dias_atras': 2,'etapa':'contato_fornecedor','valor_total': None},
            {'cliente_email':'operacoes@translog.com.br','titulo':'Coletor não sincroniza','descricao':'Dispositivo Zebra não envia dados para o sistema.','tipo':'Incidente','prioridade':'Alta','urgencia':'Alta','departamento':'Operações','categoria':'Rede','status_alvo':'aguardando','dias_atras': 4,'etapa':'teste_conectividade','valor_total': None},
            {'cliente_email':'helpdesk@univx.edu.br','titulo':'Criar contas para laboratório','descricao':'Precisa criar 30 usuários para a turma do período noturno.','tipo':'Solicitação de Serviço','prioridade':'Baixa','urgencia':'Baixa','departamento':'TI','categoria':'Acesso','status_alvo':'aberta','dias_atras': 1,'etapa':'levantamento','valor_total': None},
            {'cliente_email':'sindico@vistacond.com.br','titulo':'CFTV sem imagem em 2 câmeras','descricao':'Câmeras 3 e 7 aparecem com tela preta.','tipo':'Incidente','prioridade':'Média','urgencia':'Média','departamento':'Suporte','categoria':'Hardware','status_alvo':'em_avaliacao','dias_atras': 12,'etapa':'validacao','valor_total': 200.00},
            {'cliente_email':'manutencao@fabnorte.com.br','titulo':'Wi‑Fi instável no galpão','descricao':'Oscilações frequentes após troca de AP.','tipo':'Problema','prioridade':'Alta','urgencia':'Alta','departamento':'Operações','categoria':'Rede','status_alvo':'em_andamento','dias_atras': 10,'etapa':'site_survey','valor_total': None},
            {'cliente_email':'dono@bonspaes.com.br','titulo':'Troca de SSD e reinstalação','descricao':'Máquina do caixa com disco falhando.','tipo':'Manutenção','prioridade':'Média','urgencia':'Média','departamento':'Suporte','categoria':'Hardware','status_alvo':'encerrada','dias_atras': 22,'etapa':'entrega','valor_total': 450.00},
            {'cliente_email':'adm@deltaoffice.com.br','titulo':'Outlook não envia e‑mails','descricao':'Fila de envio fica travada com erro 0x800ccc0e.','tipo':'Incidente','prioridade':'Média','urgencia':'Média','departamento':'Suporte','categoria':'Software','status_alvo':'aguardando','dias_atras': 3,'etapa':'coleta_informacoes','valor_total': None},
            {'cliente_email':'contato@alfa.com.br','titulo':'Instalar impressora em 5 PCs','descricao':'Necessário instalar e mapear impressora de rede na filial.','tipo':'Solicitação de Serviço','prioridade':'Baixa','urgencia':'Baixa','departamento':'Suporte','categoria':'Hardware','status_alvo':'aberta','dias_atras': 1,'etapa':'levantamento','valor_total': None},
            {'cliente_email':'ti@beta.com.br','titulo':'Atualizar antivírus corporativo','descricao':'Estações com assinatura expirada. Precisa padronizar política.','tipo':'Manutenção','prioridade':'Média','urgencia':'Média','departamento':'TI','categoria':'Software','status_alvo':'aguardando','dias_atras': 8,'etapa':'janela_manutencao','valor_total': None},
            {'cliente_email':'suporte@clinic.com.br','titulo':'Recuperar senha de e-mail','descricao':'Usuário não consegue acessar a conta de e-mail institucional.','tipo':'Solicitação de Serviço','prioridade':'Baixa','urgencia':'Baixa','departamento':'TI','categoria':'Acesso','status_alvo':'encerrada','dias_atras': 16,'etapa':'entrega','valor_total': None},
            {'cliente_email':'financeiro@lojacentro.com.br','titulo':'Ajuste de permissão no sistema','descricao':'Perfil do caixa precisa acesso ao relatório de fechamento.','tipo':'Solicitação de Serviço','prioridade':'Média','urgencia':'Média','departamento':'Financeiro','categoria':'Acesso','status_alvo':'em_avaliacao','dias_atras': 6,'etapa':'validacao','valor_total': None},
            {'cliente_email':'operacoes@translog.com.br','titulo':'Troca de roteador da expedição','descricao':'Roteador atual reinicia sozinho. Necessário substituição.','tipo':'Manutenção','prioridade':'Alta','urgencia':'Alta','departamento':'Operações','categoria':'Rede','status_alvo':'em_andamento','dias_atras': 11,'etapa':'substituicao','valor_total': 980.00},
            {'cliente_email':'helpdesk@univx.edu.br','titulo':'Configurar projetor sala 12','descricao':'Projetor não reconhece HDMI de notebooks novos.','tipo':'Incidente','prioridade':'Média','urgencia':'Média','departamento':'Suporte','categoria':'Hardware','status_alvo':'aguardando','dias_atras': 2,'etapa':'testes','valor_total': None},
            {'cliente_email':'sindico@vistacond.com.br','titulo':'Interfone com ruído','descricao':'Unidade 204 relata ruído alto ao acionar interfone.','tipo':'Incidente','prioridade':'Baixa','urgencia':'Baixa','departamento':'Suporte','categoria':'Hardware','status_alvo':'aberta','dias_atras': 1,'etapa':'triagem','valor_total': None},
            {'cliente_email':'manutencao@fabnorte.com.br','titulo':'Servidor de arquivos com pouco espaço','descricao':'Volume D: com 98% de uso. Precisa análise e expansão.','tipo':'Problema','prioridade':'Alta','urgencia':'Alta','departamento':'TI','categoria':'Hardware','status_alvo':'em_andamento','dias_atras': 13,'etapa':'planejamento','valor_total': None},
            {'cliente_email':'dono@bonspaes.com.br','titulo':'Relógio de ponto não exporta','descricao':'Sistema de ponto não gera arquivo para contabilidade.','tipo':'Problema','prioridade':'Média','urgencia':'Média','departamento':'RH','categoria':'Software','status_alvo':'em_avaliacao','dias_atras': 9,'etapa':'validacao','valor_total': None},
            {'cliente_email':'adm@deltaoffice.com.br','titulo':'Atualizar Windows 11','descricao':'Agendar atualização para Windows 11 em 12 máquinas.','tipo':'Manutenção','prioridade':'Baixa','urgencia':'Baixa','departamento':'TI','categoria':'Software','status_alvo':'aguardando','dias_atras': 4,'etapa':'janela_manutencao','valor_total': None},
            {'cliente_email':'joao@email.com','titulo':'Teclado não funciona', 'descricao':'Teclado USB parou de responder após queda de energia.','tipo':'Incidente','prioridade':'Baixa','urgencia':'Baixa','departamento':'Suporte','categoria':'Hardware','status_alvo':'encerrada','dias_atras': 28,'etapa':'entrega','valor_total': 45.00},
            {'cliente_email':'maria@empresa.com','titulo':'Criar e-mail para novo funcionário', 'descricao':'Configurar conta e-mail e assinatura padrão.','tipo':'Solicitação de Serviço','prioridade':'Média','urgencia':'Média','departamento':'RH','categoria':'Acesso','status_alvo':'em_andamento','dias_atras': 3,'etapa':'provisionamento','valor_total': None},
            {'cliente_email':'pedro@gmail.com','titulo':'Notebook aquecendo', 'descricao':'Notebook desliga após alguns minutos de uso. Suspeita de ventoinha.','tipo':'Problema','prioridade':'Alta','urgencia':'Média','departamento':'Suporte','categoria':'Hardware','status_alvo':'em_avaliacao','dias_atras': 6,'etapa':'diagnostico','valor_total': None},
            {'cliente_email':'ana@corp.com','titulo':'Falha ao abrir PDF', 'descricao':'Aplicação padrão não abre PDFs baixados do portal.','tipo':'Incidente','prioridade':'Média','urgencia':'Média','departamento':'TI','categoria':'Software','status_alvo':'aberta','dias_atras': 1,'etapa':'triagem','valor_total': None},
            {'cliente_email':'carlos@ramos.net','titulo':'Rede lenta no 3º andar', 'descricao':'Usuários relatam lentidão no acesso a sites e intranet.','tipo':'Problema','prioridade':'Alta','urgencia':'Alta','departamento':'TI','categoria':'Rede','status_alvo':'aguardando','dias_atras': 8,'etapa':'coleta_logs','valor_total': None},
            {'cliente_email':'lucia@email.com','titulo':'Trocar toner impressora', 'descricao':'Impressora do setor está com alerta de toner baixo.','tipo':'Manutenção','prioridade':'Baixa','urgencia':'Baixa','departamento':'Suporte','categoria':'Hardware','status_alvo':'encerrada','dias_atras': 35,'etapa':'entrega','valor_total': 160.00},
            {'cliente_email':'roberto@nunes.com','titulo':'Configurar backup do notebook', 'descricao':'Definir rotina de backup para pasta Documentos.','tipo':'Solicitação de Serviço','prioridade':'Baixa','urgencia':'Baixa','departamento':'TI','categoria':'Outros','status_alvo':'em_andamento','dias_atras': 4,'etapa':'configuracao','valor_total': None},
            {'cliente_email':'fernanda@alves.io','titulo':'Erro 500 no sistema interno', 'descricao':'Página de cadastro retorna erro 500 ao salvar.','tipo':'Incidente','prioridade':'Crítica','urgencia':'Imediata','departamento':'TI','categoria':'Software','status_alvo':'em_andamento','dias_atras': 1,'etapa':'hotfix','valor_total': None},
        ]

        created_os = 0
        created_iter = 0
        created_hist = 0

        for idx, s in enumerate(os_specs):
            cliente = clientes_by_email.get(s['cliente_email'])
            if not cliente:
                continue

            existing = OrdemServico.objects.filter(cliente=cliente, titulo=s['titulo'], descricao=s['descricao']).first()
            if existing:
                os_obj = existing
            else:
                dept_name = s['departamento']
                candidates = staff_by_dept.get(dept_name) or staff_users
                assigned = candidates[idx % len(candidates)] if candidates else None

                os_obj = OrdemServico.objects.create(
                    cliente=cliente,
                    titulo=s['titulo'],
                    descricao=s['descricao'],
                    tipo=tip.get(s['tipo']),
                    prioridade=pri.get(s['prioridade']),
                    urgencia=urg.get(s['urgencia']),
                    departamento=dep.get(dept_name),
                    categoria=cat.get(s['categoria']),
                    criado_por=func,
                    atribuido_para=assigned,
                    etapa=s.get('etapa') or '',
                    etapa_alterada_em=now,
                    valor_total=s.get('valor_total'),
                )
                created_os += 1

                aberta_em = now - timedelta(days=int(s.get('dias_atras') or 0))
                OrdemServico.objects.filter(pk=os_obj.pk).update(aberta_em=aberta_em, status_alterado_em=aberta_em)

                hs0 = HistoricoStatus.objects.create(
                    os=os_obj,
                    status_anterior='',
                    status_novo='aberta',
                    alterado_por=func,
                    observacao='OS criada.',
                )
                HistoricoStatus.objects.filter(pk=hs0.pk).update(alterado_em=aberta_em)
                created_hist += 1

                alvo = s['status_alvo']
                idx_alvo = seq.index(alvo)
                for i in range(1, idx_alvo + 1):
                    os_obj.status = seq[i]
                    os_obj.save(update_fields=['status'])
                    hs = HistoricoStatus.objects.create(
                        os=os_obj,
                        status_anterior=seq[i - 1],
                        status_novo=seq[i],
                        alterado_por=func,
                        observacao='',
                    )
                    HistoricoStatus.objects.filter(pk=hs.pk).update(alterado_em=aberta_em + timedelta(hours=i * 6))
                    created_hist += 1

            if not os_obj.atribuido_para:
                dept_name = os_obj.departamento.nome if os_obj.departamento else None
                candidates = staff_by_dept.get(dept_name) or staff_users
                if candidates:
                    os_obj.atribuido_para = candidates[idx % len(candidates)]
                    os_obj.save(update_fields=['atribuido_para'])

            desired_texts = [
                'Análise inicial registrada.',
                'Contato com cliente realizado e informações coletadas.',
                'Próximos passos definidos. Aguardando retorno/execução.',
                'Atualização de status registrada no histórico.',
            ]
            missing = max(0, 3 - os_obj.iteracoes.count())
            for j in range(missing):
                it = Iteracao.objects.create(os=os_obj, criado_por=os_obj.atribuido_para or func, texto=desired_texts[j])
                created_iter += 1
                try:
                    base = os_obj.aberta_em if os_obj.aberta_em else now
                    Iteracao.objects.filter(pk=it.pk).update(criado_em=base + timedelta(hours=(j + 1) * 3))
                except Exception:
                    pass

        self.stdout.write(self.style.SUCCESS(
            f'Seed OK! OS criadas: {created_os} | Historicos: {created_hist} | Iteracoes: {created_iter} | Usuarios: admin/admin123, rafael/rafael123, gustavo/gustavo123, ana/ana123, juliana/juliana123, bruno/bruno123'
        ))
