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

DEFAULT_VERIFICATION_TEMPLATE = """

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name} Verification Code</title>
</head>
<body style="font-family: Arial, sans-serif; margin: 0; padding: 20px; background-color: #f4f7f6; color: #333;">
    <div style="max-width: 600px; margin: 20px auto; background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
        <div style="background-color: #1a202c; padding: 25px; text-align: center; border-top-left-radius: 8px; border-top-right-radius: 8px;">
            <h1 style="color: #ffffff; margin: 0; font-size: 28px; font-weight: bold;">{project_name}</h1>
        </div>
        <div style="padding: 30px 40px;">
            <h2 style="font-size: 22px; color: #1a202c; margin-top: 0;">Confirm Your Account</h2>
            <p style="font-size: 16px; line-height: 1.6; color: #555;">
                Welcome to {project_name}! To complete your registration and secure your account, please use the verification code below.
            </p>
            <div style="text-align: center; margin: 30px 0;">
                <p style="font-size: 16px; margin: 0 0 10px 0; color: #555;">Your verification code is:</p>
                <p style="font-size: 40px; font-weight: bold; letter-spacing: 10px; margin: 0; color: #000; background-color: #f0f4f8; padding: 15px; border-radius: 8px; display: inline-block;">
                    {code}
                </p>
            </div>
            <p style="font-size: 16px; line-height: 1.6; color: #555;">
                This code is valid for 2 minutes. Please enter it on the verification page to continue.
            </p>
            <p style="font-size: 14px; color: #888; margin-top: 30px; border-top: 1px solid #e0e0e0; padding-top: 20px;">
                If you did not request this code, you can safely ignore this email. Someone may have entered your email address by mistake.
            </p>
        </div>
        <div style="background-color: #f4f7f6; text-align: center; padding: 20px; font-size: 12px; color: #888; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;">
            © {year} {project_name}. All rights reserved.
        </div>
    </div>
</body>
</html>

"""

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
            template_file    : str = None,
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
        if template_file:
            if not os.path.isfile(template_file):
                raise FileNotFoundError(f"Template file '{template_file}' does not exist.")
            if not os.access(template_file, os.R_OK):
                raise PermissionError(f"Template file '{template_file}' is not readable.")
            html_template = open(template_file).read()
        else:
            html_template = DEFAULT_VERIFICATION_TEMPLATE

        html_template = html_template.strip()
        html_body     = html_template.format(code=verification_code, year=current_year, project_name = project_name)

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
