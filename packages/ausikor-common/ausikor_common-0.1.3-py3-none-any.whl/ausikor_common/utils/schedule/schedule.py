



def start_scheduler():
    # schedule = BackgroundScheduler(daemon=True, timezone=SCHEDULER_TIMEZONE)
    # # 휴먼고객으로 돌리기. 매일 자정에 DB 를 뒤져서 라스트 로그인이 1년이 지난 고객을 대상으로 한다.
    # schedule.add_job(CustomerController().dormant_update, trigger='cron', hour='0', minute='0', second='0')
    # # 새벽 3시 마다, s3 를 서치해서 안쓰는 이미지 파일이나 첨부파일을 s3 에 있는 임시폴더 내부의 아이템을 제거함
    # schedule.add_job(Draft53Controller().draft53_cleaner, trigger='cron', hour='3', minute='0', second='0')
    # # 배송상태가 배송준비 에서 배송중으로 변경시 매일 오후 11시 전환함. 왜 즉시 변경하지 않고, 오후 11시에 일괄 변경하는 지 이유는 기획에 있다.
    # schedule.add_job(DeliveryController().set_delivery_ready_to_ing, trigger='cron', hour='23', minute='0', second='0')
    # # 로젠택배 링크 서비스 크롤링해서 배송내용을 DB에서 배송중에서 배송완료로 바꾼다.
    # schedule.add_job(DeliveryController().set_delivery_ing_to_done, trigger='cron', minute='0', second='0')
    # # 주문할때 일단 DB 에 넣고, 주문완료를 하지 않은 오더를 삭제함.
    # schedule.add_job(OrderController().temp_order_cleaner, trigger='cron', hour='3', minute='0', second='0')
    # # 새벽 3시 마다, 비회원 customer_temp 테이블 모든 row 를 삭제함
    # schedule.add_job(CustomerController().temp_customer_cleaner, trigger='cron', hour='3', minute='0', second='0')
    # # 새벽 3시 마다, 비회원 장바구니 cart_temp 테이블 모든 row 를 삭제함
    # schedule.add_job(CartController().temp_cart_cleaner, trigger='cron', hour='3', minute='0', second='0')
    # # 새벽 3시 마다, 비회원 찜한상품 wish_temp 테이블 모든 row 를 삭제함
    # schedule.add_job(WishController().temp_wish_cleaner, trigger='cron', hour='3', minute='0', second='0')
    # schedule.start()
    pass