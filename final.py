import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ssl
import imaplib
import email
from email.header import decode_header
import re
import time
from credentials import MAIL_ID, MAIL_PASSWORD

IMAP_SERVER = 'imap.gmail.com'
IMAP_PORT = 993

def decode_subject(subject):
    decoded_subject = decode_header(subject)[0][0]
    if isinstance(decoded_subject, bytes):
        decoded_subject = decoded_subject.decode()
    return decoded_subject

def extract_customer_info(body):
    try:
        # Extracting customer name
        customer_name_match = re.search(r'Main customer:\s*(.*?)\n', body, re.DOTALL)
        customer_name = customer_name_match.group(1).strip() if customer_name_match else None

        # Extracting email address
        email_address_match = re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', body)
        email_address = email_address_match.group(0) if email_address_match else None
        
        # Extracting nationality
        nationality_match = re.search(r'([^@\n]+)\n{}'.format(re.escape(email_address)), body)
        nationality = nationality_match.group(1).strip() if nationality_match else None

        # Extracting phone number
        phone_number_match = re.search(r'Phone:\s*(.*?)\n', body)
        phone_number = phone_number_match.group(1).strip() if phone_number_match else None

        # Extracting product information
        product_match = re.search(r'\*\s*(.*?)\s*\*\nOption: Combo : Dubai Frame \+ Museum of the Future \(DF\+MOTF\)', body, re.DOTALL)
        product = product_match.group(1).strip() if product_match else None
        
        # Extracting reference number from the subject
        reference_number_match = re.search(r'Booking - .* - (.*)$', subject)
        reference_number = reference_number_match.group(1).strip() if reference_number_match else None

        return customer_name, nationality, email_address, phone_number, product, reference_number
    except AttributeError:
        print("Failed to extract customer information. Email body:\n", body)
        return None, None, None, None, None

def send_email(email_receiver, customer_name, reference_number, nationality, phone):
    first_name = customer_name.split()[0]
    
    subject = "Thank you for your booking"
    body = """
    <html>
    <head></head>
    <body style="font-family: 'Verdana';">
      <p>Hi {},</p>
      <p style="margin-top:0px">Thank you for your booking</p>
      <p>We have received Your Combo reservation with below details. <br>
      <strong>DF+MOTF | Dubai Frame + Museum of The Future Combo</strong></p><br>
      <strong>Reference Number:</strong> {}<br>
      <strong>Main Customer:</strong> {}<br>
      <strong>Nationality:</strong> {}<br>
      <strong>Phone No:</strong> {}<br>
      <p>-------</p>
      <p style="color:red;"><strong><span style="background-color: yellow;">Please read</span></strong></p>
      <p style="padding-top:15px; color:red"><strong>MUSEUM OF THE FUTURE (MOTF)</strong></p>
      <p>We will issue the Museum pass <strong>as per the Available Time slots provided by the Museum</strong> and will advise the entry time soon. <br>
      <strong>You are requested to adjust other activities as per Dubai Museum Entry time.</strong>
      <p style="padding-top:15px; color:red"><strong>DUBAI FRAME (DF)</strong></p>
      <p>Operates from 09am to 07 Pm, granting you flexible entry throughout the day. <br><br>
      We wish you a pleasant stay in Dubai and an enchanting experience during your visit. <br>
      Should you have any inquiries, questions, or feedback, our team is always at your disposal.</p>
      <p style="padding-top:15px">Thanks & Regards <br>
      Reservation Team</p>
    </body>
    </html>
    """.format(first_name, reference_number, customer_name, nationality, phone)

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

while True:
    try:
        # Connect to Gmail's IMAP server
        mail = imaplib.IMAP4_SSL(IMAP_SERVER, IMAP_PORT)

        # Authenticate using OAuth
        mail.login(MAIL_ID, MAIL_PASSWORD)

        # Select the inbox mailbox
        mail.select("inbox")

        # Search for emails with the specific criteria
        result, data = mail.search(None, '(UNSEEN SUBJECT "Booking -")')

        # Process the search results
        if result == 'OK':
            for num in data[0].split():
                result, data = mail.fetch(num, '(RFC822)')
                if result == 'OK':
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)
                    subject = decode_subject(msg['subject'])
                    if subject.startswith("Booking -"):
                        if msg.is_multipart():
                            for part in msg.walk():
                                if part.get_content_type() == "text/plain":
                                    body = part.get_payload(decode=True).decode()
                        else:
                            body = msg.get_payload(decode=True).decode()
                        customer_name, nationality, email_address, phone_number, product, reference_number = extract_customer_info(body)
                        if customer_name is not None:
                            print("--------")
                            print("Mail received with subject:", subject)
                            print("Product:", product)
                            print("Customer Name:", customer_name)
                            print("Nationality:", nationality)
                            print("Email Address:", email_address)
                            print("Phone Number:", phone_number)
                            print("--------")
                            send_email(email_address, customer_name, reference_number, nationality, phone_number)

    except Exception as e:
        print("An error occurred:", e)
    
    finally:
        # Close the connection
        try:
            mail.close()
        except:
            pass
        mail.logout()

    # Add a delay before the next iteration
    time.sleep(5)  # Adjust the delay time as needed
