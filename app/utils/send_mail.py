# app/utils/send_mail.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_templated_email(subject, to_email, template_name, context, from_email=None):
    """
    Gửi email sử dụng template HTML.
    
    Args:
        subject (str): Tiêu đề email
        to_email (str or list): Địa chỉ người nhận
        template_name (str): Đường dẫn template (VD: 'emails/welcome_email.html')
        context (dict): Dữ liệu sẽ binding vào template
        from_email (str): Địa chỉ người gửi (nếu không có sẽ lấy từ settings.DEFAULT_FROM_EMAIL)
    """
    from_email = from_email or settings.DEFAULT_FROM_EMAIL

    html_content = render_to_string(template_name, context)
    text_content = render_to_string(template_name, context).strip()  # hoặc dùng strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=[to_email] if isinstance(to_email, str) else to_email
    )
    email.attach_alternative(html_content, "text/html")
    email.send()
