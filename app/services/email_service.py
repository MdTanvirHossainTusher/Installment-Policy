import os
import smtplib
import logging
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.from_email = os.getenv('OTP_FROM_EMAIL')
        self.app_password = os.getenv('APPLICATION_PASSWORD')
        self.email_subject = os.getenv('INSTALLMENT_DUE_EMAIL_SUBJECT')
        self.email_body_template = os.getenv('INSTALLMENT_DUE_EMAIL_BODY')

        if not all([self.from_email, self.app_password, self.email_subject, self.email_body_template]):
            logger.error("Missing required email configuration in environment variables")
            
    def send_email_for_installment_due(self, receiver_email, customer_name, amount, due_date, product_name=None):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.from_email, self.app_password)
            
            msg = EmailMessage()
            msg['Subject'] = self.email_subject
            msg['From'] = self.from_email
            msg['To'] = receiver_email

            email_content = self.email_body_template.format(
                customer_name=customer_name,
                amount=amount,
                due_date=due_date,
                product_name=product_name or "your purchase"
            )
            msg.set_content(email_content)
            server.send_message(msg)
            server.quit()
            return "Installment due email sent successfully"
            
        except Exception as e:
            error_message = f"Failed to send email to {receiver_email}: {str(e)}"
            logger.error(error_message)
            return error_message


    def send_multi_product_reminder(self, receiver_email, customer_name, items):
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.from_email, self.app_password)
            
            msg = EmailMessage()
            msg['Subject'] = self.email_subject
            msg['From'] = self.from_email
            msg['To'] = receiver_email

            email_content = f"Dear {customer_name},\n\n"
            email_content += "You have the following installment payments due:\n\n"
            
            for item in items:
                email_content += f"- {item['product_name']}: ${item['due_amount']:.2f} due on {item['due_date']}\n"
                email_content += f"  (Installment {item['installment_count']} of {item['total_installment']})\n\n"
                
            email_content += "Please make the payments to avoid penalties.\n\nThank you."
            
            msg.set_content(email_content)
            server.send_message(msg)
            server.quit()
            return "Multi-product installment reminder sent successfully"
            
        except Exception as e:
            error_message = f"Failed to send multi-product reminder to {receiver_email}: {str(e)}"
            logger.error(error_message)
            return error_message