# ORM 테이블 모델을 선언하면, 테이블을 한번 읽는다.
# 이곳에 명시를 안하면, atoms 에 선언해도, 테이블이 생성되지 않으며
# 존재하지 않는다. 단, 제거할 때는 쿼리까지 실행해야 한다.






from ausikor_common.database import db_factory


def init_models():
    """ORM 테이블을 초기화하는 함수"""
    models = db_factory.get_models()
    for model in models:
        model()  # ✅ ORM 테이블 인스턴스화

init_models()