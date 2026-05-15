"""
SGOS – Testes de Cadastro de Cliente (RF004, RF005, RF006, RF010, RN001)
Execute: python manage.py test core --settings=sgos.settings_dev -v 2
"""
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status

from .models import Cliente, OrdemServico, PerfilUsuario


def make_user(username='tester', password='senha123'):
    u = User.objects.create_user(username=username, password=password,
                                 email=f'{username}@sgos.com')
    PerfilUsuario.objects.get_or_create(usuario=u, defaults={'departamento': 'TI'})
    return u


def auth_client(username='tester', password='senha123'):
    """Retorna APIClient já autenticado via JWT."""
    user = make_user(username, password)
    client = APIClient()
    res = client.post('/api/auth/login/',
                      {'username': username, 'password': password},
                      format='json')
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {res.data['access']}")
    return client, user


PAYLOAD_VALIDO = {
    'nome':     'Maria da Silva',
    'telefone': '(42) 99811-2233',
    'email':    'maria@teste.com',
    'endereco': 'Rua das Flores, 100',
}


# ══════════════════════════════════════════════════════════════════════════════
class TestCadastroCliente(TestCase):
    """RF004 — POST /api/clientes/"""

    def setUp(self):
        self.client, self.user = auth_client()
        self.url = '/api/clientes/'

    # ── Sucesso ──────────────────────────────────────────
    def test_cadastra_cliente_valido(self):
        res = self.client.post(self.url, PAYLOAD_VALIDO, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['nome'], 'Maria da Silva')
        self.assertEqual(res.data['email'], 'maria@teste.com')
        self.assertEqual(res.data['total_os'], 0)
        self.assertIn('id', res.data)
        self.assertIn('criado_em', res.data)

    def test_cadastra_cliente_sem_endereco(self):
        payload = {**PAYLOAD_VALIDO, 'endereco': '', 'email': 'sem_end@teste.com'}
        res = self.client.post(self.url, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    # ── Sem autenticação ─────────────────────────────────
    def test_rejeita_sem_token(self):
        c = APIClient()
        res = c.post(self.url, PAYLOAD_VALIDO, format='json')
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # ── Validação de nome ────────────────────────────────
    def test_rejeita_nome_vazio(self):
        res = self.client.post(self.url, {**PAYLOAD_VALIDO, 'nome': ''}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('nome', res.data)

    def test_rejeita_nome_curto(self):
        res = self.client.post(self.url, {**PAYLOAD_VALIDO, 'nome': 'Ab'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Validação de e-mail ──────────────────────────────
    def test_rejeita_email_invalido(self):
        res = self.client.post(self.url, {**PAYLOAD_VALIDO, 'email': 'nao-e-email'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', res.data)

    def test_rejeita_email_duplicado(self):
        self.client.post(self.url, PAYLOAD_VALIDO, format='json')
        res = self.client.post(self.url, {**PAYLOAD_VALIDO, 'nome': 'Outro Nome'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', res.data)

    def test_email_case_insensitive(self):
        self.client.post(self.url, PAYLOAD_VALIDO, format='json')
        res = self.client.post(self.url,
                               {**PAYLOAD_VALIDO, 'nome': 'Outro', 'email': 'MARIA@TESTE.COM'},
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    # ── Validação de telefone ────────────────────────────
    def test_rejeita_telefone_curto(self):
        res = self.client.post(self.url, {**PAYLOAD_VALIDO, 'telefone': '99999'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('telefone', res.data)

    def test_aceita_telefone_com_mascara(self):
        res = self.client.post(self.url,
                               {**PAYLOAD_VALIDO, 'email': 't2@t.com', 'telefone': '(41) 98765-4321'},
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_aceita_celular_11_digitos(self):
        res = self.client.post(self.url,
                               {**PAYLOAD_VALIDO, 'email': 't3@t.com', 'telefone': '41987654321'},
                               format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)


# ══════════════════════════════════════════════════════════════════════════════
class TestEdicaoCliente(TestCase):
    """RF005 — PUT/PATCH /api/clientes/{id}/"""

    def setUp(self):
        self.client, self.user = auth_client('editor')
        self.url = '/api/clientes/'
        res = self.client.post(self.url, PAYLOAD_VALIDO, format='json')
        self.cliente_id = res.data['id']

    def test_edicao_completa(self):
        payload = {**PAYLOAD_VALIDO, 'nome': 'Maria Editada', 'email': 'editado@teste.com'}
        res = self.client.put(f'{self.url}{self.cliente_id}/', payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['nome'], 'Maria Editada')

    def test_edicao_parcial(self):
        res = self.client.patch(f'{self.url}{self.cliente_id}/',
                                {'nome': 'Maria Parcial'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['nome'], 'Maria Parcial')

    def test_email_unico_ignora_proprio(self):
        """PUT com o mesmo e-mail do próprio registro não deve dar erro."""
        res = self.client.put(f'{self.url}{self.cliente_id}/',
                              {**PAYLOAD_VALIDO, 'nome': 'Novo Nome'}, format='json')
        self.assertEqual(res.status_code, status.HTTP_200_OK)


# ══════════════════════════════════════════════════════════════════════════════
class TestExclusaoCliente(TestCase):
    """RF006 / RN001 — DELETE /api/clientes/{id}/"""

    def setUp(self):
        self.client, self.user = auth_client('excluidor')
        res = self.client.post('/api/clientes/', PAYLOAD_VALIDO, format='json')
        self.cliente_id = res.data['id']

    def test_exclui_cliente_sem_os(self):
        res = self.client.delete(f'/api/clientes/{self.cliente_id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Cliente.objects.filter(pk=self.cliente_id).exists())

    def test_bloqueia_exclusao_com_os_ativa(self):
        """RN001: não pode excluir cliente com OS aberta."""
        cliente = Cliente.objects.get(pk=self.cliente_id)
        OrdemServico.objects.create(
            cliente=cliente, criado_por=self.user,
            titulo='OS teste', descricao='desc',
            tipo='Incidente', prioridade='Alta',
            urgencia='Alta', departamento='TI',
            status='aberta',
        )
        res = self.client.delete(f'/api/clientes/{self.cliente_id}/')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', res.data)
        self.assertTrue(Cliente.objects.filter(pk=self.cliente_id).exists())

    def test_permite_exclusao_com_os_encerrada(self):
        """RN001: pode excluir se todas as OS estiverem encerradas."""
        cliente = Cliente.objects.get(pk=self.cliente_id)
        OrdemServico.objects.create(
            cliente=cliente, criado_por=self.user,
            titulo='OS encerrada', descricao='desc',
            tipo='Incidente', prioridade='Baixa',
            urgencia='Baixa', departamento='TI',
            status='encerrada',
        )
        res = self.client.delete(f'/api/clientes/{self.cliente_id}/')
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)


# ══════════════════════════════════════════════════════════════════════════════
class TestPesquisaCliente(TestCase):
    """RF010 — GET /api/clientes/?search="""

    def setUp(self):
        self.api, _ = auth_client('pesquisador')
        for nome, email, tel in [
            ('Ana Lima',     'ana@ex.com',    '(41) 99999-0001'),
            ('Bruno Silva',  'bruno@ex.com',  '(42) 99999-0002'),
            ('Carla Mendes', 'carla@ex.com',  '(43) 99999-0003'),
        ]:
            self.api.post('/api/clientes/',
                          {'nome': nome, 'email': email, 'telefone': tel, 'endereco': ''},
                          format='json')

    def test_lista_todos(self):
        res = self.api.get('/api/clientes/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['count'], 3)

    def test_busca_por_nome(self):
        res = self.api.get('/api/clientes/?search=Ana')
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['results'][0]['nome'], 'Ana Lima')

    def test_busca_por_email(self):
        res = self.api.get('/api/clientes/?search=bruno@ex.com')
        self.assertEqual(res.data['count'], 1)

    def test_busca_por_telefone(self):
        res = self.api.get('/api/clientes/?search=43')
        self.assertEqual(res.data['count'], 1)
        self.assertEqual(res.data['results'][0]['nome'], 'Carla Mendes')

    def test_busca_sem_resultado(self):
        res = self.api.get('/api/clientes/?search=naoexiste')
        self.assertEqual(res.data['count'], 0)

    def test_ordenacao_por_nome(self):
        res = self.api.get('/api/clientes/?ordering=nome')
        nomes = [r['nome'] for r in res.data['results']]
        self.assertEqual(nomes, sorted(nomes))
