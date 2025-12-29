import re

# 비밀번호 검증 정규표현식
password_pattern = re.compile(
    r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[^A-Za-z0-9]).{6,}$'
)

def check_password(password: str) -> bool:
    """
    비밀번호가 조건을 만족하면 True, 아니면 False 반환
    """
    return bool(password_pattern.match(password))
