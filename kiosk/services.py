"""
뿌리오 알림톡 서비스
https://www.ppurio.com/
"""
import base64
from django.conf import settings

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


class PpurioService:
    """뿌리오 알림톡 발송 서비스"""

    BASE_URL = "https://message.ppurio.com"

    def __init__(self):
        self.account = getattr(settings, 'PPURIO_ACCOUNT', '')
        self.api_key = getattr(settings, 'PPURIO_API_KEY', '')
        self.sender = getattr(settings, 'PPURIO_SENDER', '')
        self.template_code = getattr(settings, 'PPURIO_TEMPLATE_CODE', '')

    def _get_auth_token(self):
        """인증 토큰 발급"""
        if not HAS_REQUESTS:
            return None

        auth_string = f"{self.account}:{self.api_key}"
        auth_bytes = base64.b64encode(auth_string.encode()).decode()

        response = requests.post(
            f"{self.BASE_URL}/v1/token",
            headers={
                "Authorization": f"Basic {auth_bytes}",
                "Content-Type": "application/json",
            },
            json={"account": self.account}
        )

        if response.status_code == 200:
            return response.json().get("token")
        return None

    def send_alimtalk(self, phone: str, message: str, variables: dict = None) -> dict:
        """
        알림톡 발송

        Args:
            phone: 수신자 전화번호 (010-0000-0000 또는 01000000000)
            message: 발송할 메시지 (템플릿에 맞게)
            variables: 템플릿 변수 (선택)

        Returns:
            dict: 발송 결과
        """
        # 전화번호 정규화 (하이픈 제거)
        phone = phone.replace("-", "").replace(" ", "")

        if not phone or not phone.startswith("010"):
            return {"success": False, "error": "유효하지 않은 전화번호입니다."}

        if not HAS_REQUESTS:
            return {"success": False, "error": "requests 모듈이 설치되지 않았습니다. pip install requests"}

        if not self.account or not self.api_key:
            return {"success": False, "error": "뿌리오 API 설정이 필요합니다."}

        token = self._get_auth_token()
        if not token:
            return {"success": False, "error": "인증 토큰 발급 실패"}

        # 알림톡 발송 요청
        payload = {
            "account": self.account,
            "messageType": "AT",  # 알림톡
            "from": self.sender,
            "content": message,
            "targets": [
                {"to": phone}
            ],
            "refKey": f"quickoil_{phone}",
            "templateCode": self.template_code,
        }

        if variables:
            payload["targets"][0]["name"] = variables.get("name", "")

        response = requests.post(
            f"{self.BASE_URL}/v1/message",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload
        )

        if response.status_code in [200, 201]:
            return {"success": True, "data": response.json()}
        else:
            return {
                "success": False,
                "error": f"발송 실패: {response.status_code}",
                "detail": response.text
            }

    def send_sms(self, phone: str, message: str) -> dict:
        """
        SMS 발송 (알림톡 실패 시 대체)

        Args:
            phone: 수신자 전화번호
            message: 발송할 메시지

        Returns:
            dict: 발송 결과
        """
        phone = phone.replace("-", "").replace(" ", "")

        if not phone or not phone.startswith("010"):
            return {"success": False, "error": "유효하지 않은 전화번호입니다."}

        if not HAS_REQUESTS:
            return {"success": False, "error": "requests 모듈이 설치되지 않았습니다. pip install requests"}

        if not self.account or not self.api_key:
            return {"success": False, "error": "뿌리오 API 설정이 필요합니다."}

        token = self._get_auth_token()
        if not token:
            return {"success": False, "error": "인증 토큰 발급 실패"}

        # SMS 발송 요청
        payload = {
            "account": self.account,
            "messageType": "SMS",
            "from": self.sender,
            "content": message,
            "targets": [
                {"to": phone}
            ],
            "refKey": f"quickoil_sms_{phone}",
        }

        response = requests.post(
            f"{self.BASE_URL}/v1/message",
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            json=payload
        )

        if response.status_code in [200, 201]:
            return {"success": True, "data": response.json()}
        else:
            return {
                "success": False,
                "error": f"발송 실패: {response.status_code}",
                "detail": response.text
            }


def send_service_complete_message(order) -> dict:
    """
    시공 완료 메시지 발송

    Args:
        order: ServiceOrder 인스턴스

    Returns:
        dict: 발송 결과
    """
    if not order.customer_phone:
        return {"success": False, "error": "고객 전화번호가 없습니다."}

    # 메시지 생성
    message = f"""[ QuickOil 정비 명세서 ]

차량번호: {order.car_number or '-'}
차종: {order.brand.name} {order.car_model.name}
시공일: {order.completed_at.strftime('%Y.%m.%d') if order.completed_at else '-'}

────────────
{order.oil_name} ({order.oil_product_name}): {order.oil_price:,}원"""

    for item in order.services.all():
        price_str = f"{item.price:,}원" if item.price > 0 else "무료"
        message += f"\n{item.name}: {price_str}"

    message += f"""
────────────
총 금액: {order.total_price:,}원"""

    if order.mileage_current:
        message += f"""

현재 주행거리: {order.mileage_current:,}km
다음 교체: {order.mileage_next:,}km"""

    if order.notes:
        message += f"\n\n※ {order.notes}"

    message += "\n\n감사합니다 - QuickOil"

    # 발송
    service = PpurioService()
    result = service.send_alimtalk(order.customer_phone, message)

    # 알림톡 실패 시 SMS로 대체 발송
    if not result.get("success"):
        # SMS는 90바이트 제한이 있으므로 짧은 메시지로
        short_message = f"[QuickOil] 시공완료. {order.car_number or ''}. 총액:{order.total_price:,}원. 감사합니다."
        result = service.send_sms(order.customer_phone, short_message)

    return result
