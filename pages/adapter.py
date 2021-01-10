# from allauth.account.adapter import DefaultAccountAdapter
# from django.core.mail import send_mail


# class SendgridEmailAdapter(DefaultAccountAdapter):
#   def send_mail(self, template_prefix, email, context):
#     """
#     `render_mail` renders an email to `email`
#     `template_prefix` identifies email to be sent
#     `msg` already includes subject, body, from_email, and to
#     """
#     msg = self.render_mail(template_prefix, email, context)
#     send_mail(
#         msg,
#         fail_silently=False
#     )
