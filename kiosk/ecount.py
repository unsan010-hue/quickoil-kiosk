"""
이카운트 ERP 연동 모듈
매출·매입전표 II 자동분개 API (InvoiceAuto/SaveInvoiceAuto)
"""
import json
import logging
import math
import urllib.request
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# 세션 캐시 (프로세스 레벨)
_session_cache = {
    'session_id': None,
    'host_url': None,
    'logged_in_at': None,
}


def _login():
    """이카운트 로그인 → SESSION_ID 반환"""
    zone = settings.ECOUNT_ZONE
    url = f'https://oapi{zone}.ecount.com/OAPI/V2/OAPILogin'
    data = {
        'COM_CODE': settings.ECOUNT_COM_CODE,
        'USER_ID': settings.ECOUNT_USER_ID,
        'API_CERT_KEY': settings.ECOUNT_API_KEY,
        'LAN_TYPE': 'ko-KR',
        'ZONE': zone,
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(data).encode('utf-8'),
        headers={'Content-Type': 'application/json'},
    )
    resp = urllib.request.urlopen(req, timeout=10)
    result = json.loads(resp.read().decode('utf-8'))

    if result.get('Data', {}).get('Code') != '00':
        raise Exception(f"이카운트 로그인 실패: {result}")

    datas = result['Data']['Datas']
    _session_cache['session_id'] = datas['SESSION_ID']
    _session_cache['host_url'] = datas['HOST_URL']
    _session_cache['logged_in_at'] = datetime.now()

    logger.info("이카운트 로그인 성공")
    return datas['SESSION_ID']


def _get_session():
    """캐시된 세션 반환, 20분 초과 시 재로그인"""
    if _session_cache['session_id'] and _session_cache['logged_in_at']:
        elapsed = (datetime.now() - _session_cache['logged_in_at']).total_seconds()
        if elapsed < 1080:  # 18분 (여유 2분)
            return _session_cache['session_id']
    return _login()


def _build_remarks(order):
    """
    적요 문자열 생성 - 기존 수기 형식에 맞춤:
    시간 차종 차번 전화 오일 금액 추가서비스 주행거리
    예: 12:50 싼타페 DM 13나0845 010-3314-2214 메0w30es 161,384 디톡스
    """
    from .models import ServiceOrder

    parts = []

    # 순번: 오늘 완료된 주문 중 현재 주문보다 먼저 완료된 건수 + 1
    completed = order.completed_at or order.created_at
    local_time = timezone.localtime(completed) if completed else None
    if local_time:
        day_start = local_time.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        seq = ServiceOrder.objects.filter(
            status='completed',
            completed_at__gte=day_start,
            completed_at__lt=completed,
        ).count() + 1
        parts.append(f"{seq}.")
    else:
        parts.append('-.')

    # 시간
    parts.append(local_time.strftime('%H:%M') if local_time else '-')

    # 차종
    if order.car_model:
        if order.car_model.parent:
            parts.append(f"{order.car_model.parent.name} {order.car_model.name}")
        else:
            parts.append(order.car_model.name)
    else:
        parts.append('-')

    # 차번
    parts.append(order.car_number or '-')

    # 전화번호
    parts.append(order.customer_phone or '-')

    # 오일
    parts.append(order.oil_product_name or '-')

    # 금액
    parts.append(f"{order.total_price:,}")

    # 추가 서비스
    services = list(order.services.all())
    parts.append(' '.join(svc.name for svc in services) if services else '-')

    # 주행거리
    parts.append(f"{order.mileage_current:,}km" if order.mileage_current else '-km')

    return ' '.join(parts)


def create_sales_slip(order):
    """
    시공 완료 시 매출전표 생성.
    Returns: {'success': True, 'slip_no': '...'} or {'success': False, 'error': '...'}
    """
    try:
        session_id = _get_session()
    except Exception as e:
        logger.error(f"이카운트 로그인 실패: {e}")
        return {'success': False, 'error': f'이카운트 로그인 실패: {e}'}

    # 총액에서 공급가액/부가세 분리 (VAT 포함가 기준)
    total = order.total_price
    supply_amt = math.floor(total / 1.1)
    vat_amt = total - supply_amt

    # 전표 일자
    completed_at = order.completed_at or timezone.now()
    trx_date = timezone.localtime(completed_at).strftime('%Y%m%d')

    remarks = _build_remarks(order)

    zone = settings.ECOUNT_ZONE
    url = f'https://oapi{zone}.ecount.com/OAPI/V2/InvoiceAuto/SaveInvoiceAuto?SESSION_ID={session_id}'

    payload = {
        'InvoiceAutoList': [{
            'BulkDatas': {
                'TRX_DATE': trx_date,
                'TAX_GUBUN': '11',
                'CUST': settings.ECOUNT_CUST,
                'CR_CODE': settings.ECOUNT_CR_CODE,
                'SUPPLY_AMT': str(supply_amt),
                'VAT_AMT': str(vat_amt),
                'ACCT_NO': settings.ECOUNT_ACCT_NO,
                'REMARKS': remarks[:200],
                'SITE_CD': settings.ECOUNT_SITE_CD,
            }
        }]
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json; charset=utf-8'},
        )
        resp = urllib.request.urlopen(req, timeout=15)
        raw = resp.read()

        # 응답 파싱
        result = json.loads(raw.decode('utf-8', errors='replace'))
        data = result.get('Data', {})

        if data.get('SuccessCnt', 0) > 0:
            slip_nos = data.get('SlipNos', [])
            slip_no = slip_nos[0] if slip_nos else ''
            logger.info(f"이카운트 매출전표 생성: {slip_no} (주문#{order.id})")
            return {'success': True, 'slip_no': slip_no}

        # 실패 시 세션 만료 가능성 → 재로그인 후 1회 재시도
        details = data.get('ResultDetails', [])
        error_msg = details[0].get('TotalError', '') if details else '알 수 없는 오류'

        # 세션 만료 감지
        if '세션' in str(raw) or result.get('Status') == '401':
            _session_cache['session_id'] = None
            try:
                session_id = _login()
                url = f'https://oapi{zone}.ecount.com/OAPI/V2/InvoiceAuto/SaveInvoiceAuto?SESSION_ID={session_id}'
                req = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode('utf-8'),
                    headers={'Content-Type': 'application/json; charset=utf-8'},
                )
                resp = urllib.request.urlopen(req, timeout=15)
                result = json.loads(resp.read().decode('utf-8', errors='replace'))
                data = result.get('Data', {})
                if data.get('SuccessCnt', 0) > 0:
                    slip_nos = data.get('SlipNos', [])
                    slip_no = slip_nos[0] if slip_nos else ''
                    logger.info(f"이카운트 매출전표 생성 (재시도): {slip_no}")
                    return {'success': True, 'slip_no': slip_no}
            except Exception:
                pass

        logger.warning(f"이카운트 매출전표 실패: {error_msg} (주문#{order.id})")
        return {'success': False, 'error': error_msg}

    except Exception as e:
        logger.error(f"이카운트 API 호출 실패: {e}")
        return {'success': False, 'error': str(e)}


def create_purchase_slip(order):
    """
    멤버십 할인 매입전표 생성.
    20% 할인, 최대 15,000원.
    Returns: {'success': True, 'slip_no': '...'} or {'success': False, 'error': '...'}
    """
    try:
        session_id = _get_session()
    except Exception as e:
        logger.error(f"이카운트 로그인 실패: {e}")
        return {'success': False, 'error': f'이카운트 로그인 실패: {e}'}

    # 할인 금액 계산 (VAT 포함)
    rate = getattr(settings, 'MEMBERSHIP_DISCOUNT_RATE', 0.2)
    cap = getattr(settings, 'MEMBERSHIP_DISCOUNT_MAX', 15000)
    discount_total = min(math.floor(order.total_price * rate), cap)
    supply_amt = math.floor(discount_total / 1.1)
    vat_amt = discount_total - supply_amt

    # 전표 일자
    completed_at = order.completed_at or timezone.now()
    trx_date = timezone.localtime(completed_at).strftime('%Y%m%d')

    remarks = _build_remarks(order) + ' 멤버쉽할인'

    zone = settings.ECOUNT_ZONE
    url = f'https://oapi{zone}.ecount.com/OAPI/V2/InvoiceAuto/SaveInvoiceAuto?SESSION_ID={session_id}'

    payload = {
        'InvoiceAutoList': [{
            'BulkDatas': {
                'TRX_DATE': trx_date,
                'TAX_GUBUN': '21',
                'CUST': settings.ECOUNT_PURCHASE_CUST,
                'DR_CODE': settings.ECOUNT_PURCHASE_DR_CODE,
                'SUPPLY_AMT': str(supply_amt),
                'VAT_AMT': str(vat_amt),
                'ACCT_NO': settings.ECOUNT_PURCHASE_ACCT_NO,
                'REMARKS': remarks[:200],
                'SITE_CD': settings.ECOUNT_SITE_CD,
            }
        }]
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json; charset=utf-8'},
        )
        resp = urllib.request.urlopen(req, timeout=15)
        result = json.loads(resp.read().decode('utf-8', errors='replace'))
        data = result.get('Data', {})

        if data.get('SuccessCnt', 0) > 0:
            slip_nos = data.get('SlipNos', [])
            slip_no = slip_nos[0] if slip_nos else ''
            logger.info(f"이카운트 매입전표(멤버십) 생성: {slip_no} (주문#{order.id})")
            return {'success': True, 'slip_no': slip_no}

        details = data.get('ResultDetails', [])
        error_msg = details[0].get('TotalError', '') if details else '알 수 없는 오류'
        logger.warning(f"이카운트 매입전표 실패: {error_msg} (주문#{order.id})")
        return {'success': False, 'error': error_msg}

    except Exception as e:
        logger.error(f"이카운트 매입전표 API 호출 실패: {e}")
        return {'success': False, 'error': str(e)}
