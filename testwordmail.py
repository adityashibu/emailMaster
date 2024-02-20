import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
from credentials import MAIL_PASSWORD, MAIL_ID

email_receiver = 'aadithyashibu@gmail.com'

subject = "Hello world!"
body = """
<html>
<head></head>
<body style="font-family: 'Verdana';">
  <p>Dear Guest</p>
  <p style="margin-top:0px">Thank you for your booking</p>
  <p style="padding-top:20px">We Welcome you to Dubai.</p>
  <p>We have received Your Combo reservation with below details. <br>
  <strong>DF+MOTF | Dubai Frame + Museum of The Future Combo</strong></p>
  <p>-------</p>
  <p style="color:red;"><strong><span style="background-color: yellow;">Please read</span></strong></p>
  <p style="padding-top:15px; color:red"><strong>MUSEUM OF THE FUTURE (MOTF)</strong></p>
  <p>We will issue the Museum pass as per the Available Time slots provided by the Museum and will advise the entry time soon. <br>
  <strong>You are requested to adjust other activities as per Dubai Museum Entry time.</strong>
  <p style="padding-top:15px; color:red"><strong>DUBAI FRAME (DF)</strong></p>
  <p>Operates from 09am to 07 Pm, granting you flexible entry throughout the day. <br><br>
  We wish you a pleasant stay in Dubai and an enchanting experience during your visit. <br>
  Should you have any inquiries, questions, or feedback, our team is always at your disposal.</p>
  <p style="padding-top:15px">Thanks & Regards <br>
  Reservation Team</p>
</body>
</html>
"""

# Create a MIMEText object with HTML content
msg = MIMEMultipart()
msg['From'] = MAIL_ID
msg['To'] = email_receiver
msg['Subject'] = subject
msg.attach(MIMEText(body, 'html'))

context = ssl.create_default_context()

with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
    smtp.login(MAIL_ID, MAIL_PASSWORD)
    smtp.sendmail(MAIL_ID, email_receiver, msg.as_string())
