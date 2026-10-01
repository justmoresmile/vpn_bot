import smtplib

from email.headerregistry import Address
from email.message import EmailMessage

from app.config import settings


class EmailService:

    def send_login_code(
        self,
        email: str,
        code: str,
    ) -> None:

        message = EmailMessage()

        message["Subject"] = "Код входа в JustVPN"

        message["From"] = Address(
            display_name="JustVPN",
            addr_spec=settings.smtp_from,
        )

        message["To"] = email

        # ============================================================
        # TEXT VERSION
        # ============================================================

        message.set_content(
            f"""
JustVPN

Код для входа:

{code}

Код действует 10 минут.

Если вы не запрашивали код входа,
просто проигнорируйте это письмо.

JustVPN
Защита вашего подключения
""".strip()
        )

        # ============================================================
        # HTML VERSION
        # ============================================================

        message.add_alternative(
            f"""
<!doctype html>
<html lang="ru">
<head>
    <meta charset="utf-8">
</head>

<body
    style="
        margin:0;
        padding:0;
        background:#f4f6f8;
        font-family:
            -apple-system,
            BlinkMacSystemFont,
            'Segoe UI',
            Arial,
            sans-serif;
    "
>

<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="background:#f4f6f8;padding:32px 16px;"
>
<tr>
<td align="center">

<table
    width="100%"
    cellpadding="0"
    cellspacing="0"
    border="0"
    style="
        max-width:520px;
        background:#ffffff;
        border-radius:20px;
        overflow:hidden;
        box-shadow:
            0 10px 35px rgba(0,0,0,0.08);
    "
>

<tr>
<td
    style="
        padding:32px 32px 18px 32px;
        text-align:center;
    "
>

<div
    style="
        font-size:30px;
        font-weight:800;
        letter-spacing:-1px;
        color:#111827;
    "
>
    JustVPN
</div>

<div
    style="
        margin-top:6px;
        font-size:14px;
        color:#6b7280;
    "
>
    Защита вашего подключения
</div>

</td>
</tr>

<tr>
<td
    style="
        padding:18px 32px 10px 32px;
        text-align:center;
    "
>

<div
    style="
        font-size:20px;
        font-weight:700;
        color:#111827;
    "
>
    Код входа
</div>

<div
    style="
        margin-top:10px;
        font-size:15px;
        line-height:1.5;
        color:#6b7280;
    "
>
    Введите этот код в приложении JustVPN
</div>

</td>
</tr>

<tr>
<td
    style="
        padding:20px 32px;
        text-align:center;
    "
>

<div
    style="
        display:inline-block;
        padding:18px 28px;
        background:#f3f4f6;
        border-radius:16px;
        font-size:36px;
        font-weight:800;
        letter-spacing:10px;
        color:#111827;
    "
>
    {code}
</div>

</td>
</tr>

<tr>
<td
    style="
        padding:4px 32px 30px 32px;
        text-align:center;
    "
>

<div
    style="
        font-size:14px;
        line-height:1.6;
        color:#6b7280;
    "
>
    Код действует <b>10 минут</b>.
    <br>
    Если вы не запрашивали вход,
    просто проигнорируйте письмо.
</div>

</td>
</tr>

<tr>
<td
    style="
        padding:20px 32px;
        background:#f9fafb;
        text-align:center;
        font-size:12px;
        color:#9ca3af;
    "
>
    JustVPN · Безопасное подключение
</td>
</tr>

</table>

</td>
</tr>
</table>

</body>
</html>
""".strip(),
            subtype="html",
        )

        # ============================================================
        # SEND
        # ============================================================

        if settings.smtp_ssl:

            with smtplib.SMTP_SSL(
                settings.smtp_host,
                settings.smtp_port,
                timeout=20,
            ) as smtp:

                smtp.login(
                    settings.smtp_user,
                    settings.smtp_password,
                )

                smtp.send_message(
                    message
                )

            return

        with smtplib.SMTP(
            settings.smtp_host,
            settings.smtp_port,
            timeout=20,
        ) as smtp:

            if settings.smtp_starttls:
                smtp.starttls()

            smtp.login(
                settings.smtp_user,
                settings.smtp_password,
            )

            smtp.send_message(
                message
            )


email_service = EmailService()