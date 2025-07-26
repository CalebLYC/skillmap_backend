import smtplib
from email.mime.text import MIMEText
from email.header import Header
from fastapi import HTTPException, status
from app.core.config import Settings
import ssl
import asyncio


class EmailService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.smtp_host = settings.smtp_host
        self.smtp_port = settings.smtp_port
        self.smtp_username = settings.smtp_username
        self.smtp_password = settings.smtp_password
        self.smtp_sender_email = settings.smtp_sender_email
        self.smtp_use_tls = settings.smtp_use_tls
        self.smtp_use_ssl = settings.smtp_use_ssl

    async def send_email(
        self, recipient_email: str, subject: str, body: str, is_html: bool = False
    ):
        """Envoie un e-mail via SMTP de manière asynchrone en exécutant les opérations bloquantes
        dans un thread pool executor.

        Args:
            recipient_email (str): _description_
            subject (str): _description_
            body (str): _description_

        Raises:
            e: _description_
            HTTPException: _description_
        """
        msg = MIMEText(body, "html" if is_html else "plain", "utf-8")
        msg["Subject"] = Header(subject, "utf-8")
        msg["From"] = self.smtp_sender_email
        msg["To"] = recipient_email

        try:
            await asyncio.to_thread(
                self._perform_send_email,
                recipient_email,
                msg.as_string(),
            )
            print(
                f"Email sent successfully to {recipient_email} for subject: {subject}"
            )
        except HTTPException as e:
            raise e
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"An unexpected error occurred while sending email: {e}",
            )

    def _perform_send_email(self, recipient_email: str, msg_string: str):
        """Méthode synchrone interne qui contient la logique d'envoi d'e-mail bloquante.
        Cette méthode sera exécutée dans un thread séparé par asyncio.to_thread.

        Args:
            recipient_email (str): _description_
            msg_string (str): _description_

        Raises:
            HTTPException: _description_
            HTTPException: _description_
            HTTPException: _description_
        """
        server = None
        try:
            if self.smtp_use_ssl:
                context = ssl.create_default_context()
                # Tests sans vérification du certificat(juste en mode dev/test)
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
                server = smtplib.SMTP_SSL(
                    self.smtp_host, self.smtp_port, context=context
                )
            else:
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.smtp_use_tls:
                    context = ssl.create_default_context()
                    # Tests sans vérification du certificat(juste en mode dev/test)
                    context.check_hostname = False
                    context.verify_mode = ssl.CERT_NONE
                    server.starttls(context=context)

            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.smtp_sender_email, recipient_email, msg_string)
        except smtplib.SMTPAuthenticationError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Email sending failed: SMTP Authentication Error. Check username/password. {e}",
            )
        except smtplib.SMTPConnectError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Email sending failed: SMTP Connection Error. Check host/port. {e}",
            )
        except smtplib.SMTPException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Email sending failed: {e}",
            )
        finally:
            if server:
                server.quit()
