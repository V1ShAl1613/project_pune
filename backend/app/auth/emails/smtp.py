from __future__ import annotations

import smtplib
from dataclasses import dataclass

from app.core.settings import AppSettings
from app.auth.emails.templates import EmailTemplate


@dataclass(slots=True)
class SmtpEmailClient:
    settings: AppSettings

    def is_configured(self) -> bool:
        return bool(self.settings.smtp_host and self.settings.smtp_from_address)

    def send(self, recipient_email: str, template: EmailTemplate) -> bool:
        if not self.is_configured():
            return False
        message = (
            f"From: {self.settings.smtp_from_address}\n"
            f"To: {recipient_email}\n"
            f"Subject: {template.subject}\n\n"
            f"{template.body}"
        )
        if self.settings.smtp_use_ssl:
            with smtplib.SMTP_SSL(self.settings.smtp_host, self.settings.smtp_port or 465) as client:
                self._login(client)
                client.sendmail(self.settings.smtp_from_address, [recipient_email], message)
        else:
            with smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port or 587) as client:
                if self.settings.smtp_use_tls:
                    client.starttls()
                self._login(client)
                client.sendmail(self.settings.smtp_from_address, [recipient_email], message)
        return True

    def _login(self, client: smtplib.SMTP) -> None:
        if self.settings.smtp_username and self.settings.smtp_password:
            client.login(self.settings.smtp_username, self.settings.smtp_password)
