# -*- coding: utf-8 -*-
"""
<license>
  * Copyright (C) 2024-2025 Abdelmathin Habachi, contact@abdelmathin.com.
  *
  * https://abdelmathin.com
  * https://github.com/Abdelmathin/tachyons
  *
  * Permission is hereby granted, free of charge, to any person obtaining
  * a copy of this software and associated documentation files (the
  * "Software"), to deal in the Software without restriction, including
  * without limitation the rights to use, copy, modify, merge, publish,
  * distribute, sublicense, and/or sell copies of the Software, and to
  * permit persons to whom the Software is furnished to do so, subject to
  * the following conditions:
  *
  * The above copyright notice and this permission notice shall be
  * included in all copies or substantial portions of the Software.
  *
  * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
  * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
  * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
  * CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
  * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
  * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
  *
  * File   : tachyons/integrations/gmail.py
  * Created: 2025/08/30 22:49:13 GMT+1
  * Updated: 2025/08/30 23:44:36 GMT+1
</license>
"""
__author__ = "Abdelmathin Habachi"
__github__ = "https://github.com/Abdelmathin/tachyons"

import os
import random
import string
import smtplib
import datetime
import traceback
from email.mime.text      import MIMEText
from email.mime.multipart import MIMEMultipart 

class GmailIntegration:

    def __init__(self):
        pass

    @staticmethod
    def send_verification_mail(
            sender_email     : str,
            sender_password  : str,
            verification_code: str,
            recipient        : str,
            project_name     : str,
            template_file    : str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "templates", "verification.html"),
            smtp_server      : str = "smtp.gmail.com",
            smtp_port        : int = 587,
        ) -> bool:
        """
        Sends a verification email to the recipient with the provided verification code.
        Args:
            sender_email (str): The email address of the sender.
            sender_password (str): The password for the sender's email account.
            verification_code (str): The verification code to be sent.
            recipient (str): The email address of the recipient.
        """
        if not isinstance(sender_email, str) or not sender_email.strip():
            raise ValueError("Sender email cannot be empty.")
        if not isinstance(sender_password, str) or not sender_password.strip():
            raise ValueError("Sender password cannot be empty.")
        if not isinstance(verification_code, str):
            raise TypeError("Verification code must be a string.")
        if not isinstance(recipient, str) or not recipient.strip():
            raise ValueError("Recipient email cannot be empty.")
        sender_email = sender_email.lower().strip()
        recipient    = recipient.lower().strip()
        subject      = f"Your {project_name} Verification Code"
        current_year = datetime.datetime.now().year
        text_body    = f"""
        Welcome to {project_name}!

        Your verification code is: {verification_code}

        This code will expire in 2 minutes.

        If you did not request this, please ignore this email.

        Thanks,
        The {project_name} Team
        """
        try:
            html_template = open(template_file).read()
        except Exception as e:
            traceback.print_exc()
            raise RuntimeError("Failed to read HTML template") from e
        html_body = html_template.format(code=verification_code, year=current_year, project_name = project_name)

        try:
            msg = MIMEMultipart("alternative")
            msg['Subject'] = subject
            msg['From']    = sender_email
            msg['To']      = recipient
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))
            if smtp_port == 465:
                with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
            else:
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
            return True
        except smtplib.SMTPException as e:
            raise RuntimeError(f"Failed to send email: {e}") from e
        return False
