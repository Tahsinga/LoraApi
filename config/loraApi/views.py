import json
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

SYNC_QUEUE = []


@csrf_exempt
def index(request):
    """Root endpoint - returns API status"""
    return JsonResponse({
        'status': 'ok',
        'service': 'Lora POS Returns API Gateway',
        'version': '1.0.0',
        'message': 'API is running and ready to receive requests',
        'endpoints': {
            'health': '/api/health/',
            'branch_sync': '/api/branch-sync/',
            'main_sync': '/api/main-sync/'
        }
    })


@csrf_exempt
def favicon(request):
    """Favicon endpoint - returns empty response"""
    return HttpResponse('', content_type='image/x-icon')


@csrf_exempt
def health_check(request):
    return JsonResponse({
        'status': 'ok',
        'service': 'Lora API Gateway',
        'message': 'Django gateway is running.'
    })


@csrf_exempt
def branch_sync(request):
    if request.method == 'GET':
        return JsonResponse({
            'pending': SYNC_QUEUE,
            'count': len(SYNC_QUEUE),
        })

    payload = json.loads(request.body or '{}')
    item = {
        'branch': payload.get('branch', 'unknown'),
        'invoice': payload.get('invoice'),
        'product_id': payload.get('product_id'),
        'action': payload.get('action', 'sync'),
        'deleted': payload.get('deleted', False),
        'status': 'queued',
    }
    SYNC_QUEUE.append(item)

    return JsonResponse({
        'status': 'queued',
        'item': item,
        'count': len(SYNC_QUEUE),
    }, status=202)


@csrf_exempt
def main_sync(request):
    if request.method == 'GET':
        return JsonResponse({
            'branches': ['Branch A', 'Branch B', 'Branch C'],
            'sync_queue': SYNC_QUEUE,
        })

    payload = json.loads(request.body or '{}')
    branch = payload.get('branch', 'unknown')
    invoice = payload.get('invoice')
    deleted = payload.get('deleted', False)

    for item in SYNC_QUEUE:
        if item.get('branch') == branch and item.get('invoice') == invoice:
            item['status'] = 'processed'
            item['deleted_from_main'] = deleted

    return JsonResponse({
        'status': 'processed',
        'branch': branch,
        'invoice': invoice,
        'deleted': deleted,
    })
