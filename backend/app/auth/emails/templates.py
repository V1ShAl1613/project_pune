from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class EmailTemplate:
    subject: str
    body: str


def verification_email_template(display_name: str, verification_link: str) -> EmailTemplate:
    return EmailTemplate(
        subject="Verify your Sentinel Fusion AI account",
        body=f"Hello {display_name},\n\nVerify your account using the following link:\n{verification_link}\n",
    )


def reset_password_email_template(display_name: str, reset_link: str) -> EmailTemplate:
    return EmailTemplate(
        subject="Reset your Sentinel Fusion AI password",
        body=f"Hello {display_name},\n\nReset your password using the following link:\n{reset_link}\n",
    )


def welcome_email_template(display_name: str) -> EmailTemplate:
    return EmailTemplate(
        subject="Welcome to Sentinel Fusion AI",
        body=f"Hello {display_name},\n\nYour account has been created successfully.\n",
    )


def notification_email_template(title: str, body: str) -> EmailTemplate:
    return EmailTemplate(subject=title, body=body)
