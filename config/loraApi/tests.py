from django.test import TestCase
from django.contrib.auth import get_user_model
import json


class DeletionQueueTests(TestCase):
	def setUp(self):
		self.client.force_login(get_user_model().objects.create_user(
			username='operator', password='OperatorPass4182!'
		))

	def test_dashboard_counts_saved_pending_record(self):
		response = self.client.post(
			'/api/cancel-sale/',
			data=json.dumps({'invoice': 'INV-100', 'branch': 'Branch A'}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 202)
		self.assertEqual(self.client.get('/api/main-sync/').json()['pending_count'], 1)

	def test_confirmation_moves_record_to_processed_count(self):
		response = self.client.post(
			'/api/cancel-sale/',
			data=json.dumps({'invoice': 'INV-200', 'branch': 'Branch A'}),
			content_type='application/json',
		)
		deletion_id = response.json()['deletion_id']

		response = self.client.post(
			'/api/confirm-deletion/',
			data=json.dumps({
				'deletion_id': deletion_id,
				'deleted_rows': 1,
				'branch': 'Branch A',
				'success': True,
			}),
			content_type='application/json',
		)

		self.assertEqual(response.status_code, 200)
		summary = self.client.get('/api/main-sync/').json()
		self.assertEqual(summary['pending_count'], 0)
		self.assertEqual(summary['processed_count'], 1)

	def test_history_returns_confirmed_invoices_newest_first(self):
		older = self.client.post(
			'/api/cancel-sale/',
			data=json.dumps({'invoice': 'INV-OLD', 'branch': 'Branch A'}),
			content_type='application/json',
		).json()['deletion_id']
		newer = self.client.post(
			'/api/cancel-sale/',
			data=json.dumps({'invoice': 'INV-NEW', 'branch': 'Branch B'}),
			content_type='application/json',
		).json()['deletion_id']

		for deletion_id, branch in [(older, 'Branch A'), (newer, 'Branch B')]:
			self.client.post(
				'/api/confirm-deletion/',
				data=json.dumps({'deletion_id': deletion_id, 'deleted_rows': 1, 'branch': branch}),
				content_type='application/json',
			)

		response = self.client.get('/api/cancellation-history/?branch=Branch')
		self.assertEqual(response.status_code, 200)
		self.assertEqual([item['invoice'] for item in response.json()['cancellations']], ['INV-NEW', 'INV-OLD'])


class AuthenticationTests(TestCase):
	def setUp(self):
		self.admin = get_user_model().objects.create_superuser(
			username='Admin', password='Tash1nga4182', email='admin@example.com'
		)

	def test_dashboard_requires_login(self):
		response = self.client.get('/')
		self.assertRedirects(response, '/login/?next=/')

	def test_admin_can_create_user_and_change_password(self):
		self.client.force_login(self.admin)
		response = self.client.post('/users/', {
			'action': 'create',
			'username': 'operator',
			'password1': 'OperatorPass4182!',
			'password2': 'OperatorPass4182!',
		})
		self.assertEqual(response.status_code, 200)
		operator = get_user_model().objects.get(username='operator')
		self.assertFalse(operator.is_superuser)

		response = self.client.post('/users/', {
			'action': 'change_password',
			'user_id': operator.pk,
			'new_password1': 'ChangedPass4182!',
			'new_password2': 'ChangedPass4182!',
		})
		self.assertEqual(response.status_code, 200)
		self.assertTrue(operator.__class__.objects.get(pk=operator.pk).check_password('ChangedPass4182!'))
