

from ausikor_common.utils.email.email_schema import EmailSchema


class EmailTemplate:
    """이메일 템플릿 클래스"""
    
    @staticmethod
    def welcome_email(user_name: str, user_email: str) -> EmailSchema:
        """환영 이메일 템플릿"""
        subject = f"Dover Platform에 오신 것을 환영합니다, {user_name}님!"
        body = f"""
        <html>
        <body>
            <h2>환영합니다! 🎉</h2>
            <p>안녕하세요 <strong>{user_name}</strong>님,</p>
            <p>Dover Platform에 가입해주셔서 감사합니다.</p>
            <p>이제 다양한 서비스를 이용하실 수 있습니다.</p>
            <br>
            <p>문의사항이 있으시면 언제든 연락주세요.</p>
            <p>감사합니다.</p>
            <hr>
            <small>Dover Platform Team</small>
        </body>
        </html>
        """
        return EmailSchema(user_email, subject, body, "html")
    
    @staticmethod
    def password_reset_email(user_name: str, user_email: str, reset_token: str) -> EmailSchema:
        """비밀번호 재설정 이메일 템플릿"""
        subject = "Dover Platform 비밀번호 재설정"
        reset_url = f"https://dover-platform.com/reset-password?token={reset_token}"
        body = f"""
        <html>
        <body>
            <h2>비밀번호 재설정 요청</h2>
            <p>안녕하세요 <strong>{user_name}</strong>님,</p>
            <p>비밀번호 재설정을 요청하셨습니다.</p>
            <p>아래 링크를 클릭하여 새로운 비밀번호를 설정해주세요:</p>
            <p><a href="{reset_url}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">비밀번호 재설정</a></p>
            <p><small>이 링크는 24시간 후 만료됩니다.</small></p>
            <br>
            <p>만약 비밀번호 재설정을 요청하지 않으셨다면, 이 이메일을 무시해주세요.</p>
            <hr>
            <small>Dover Platform Team</small>
        </body>
        </html>
        """
        return EmailSchema(user_email, subject, body, "html")