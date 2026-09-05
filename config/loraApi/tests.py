from django.test import TestCase
import json


class DeletionQueueTests(TestCase):
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
