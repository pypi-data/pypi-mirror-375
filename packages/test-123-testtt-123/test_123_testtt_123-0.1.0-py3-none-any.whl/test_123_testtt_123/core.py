import requests

def get_ip():
    """
    Получает ваш внешний IP через сервис 2ip.io
    """
    try:
        response = requests.get('http://httpbin.org/ip', timeout=30)
        data = response.json()
        return data
    except Exception as e:
        return f"Ошибка при получении IP: {e}"
