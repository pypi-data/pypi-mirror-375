


from ausikor_common.utils.email.email_schema import EmailSchema


def create_email(recipient_email: str, subject: str, body: str) -> EmailSchema:
    return EmailSchema(recipient_email, subject, body)