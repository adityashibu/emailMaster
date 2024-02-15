import imaplib
import email
from email.header import decode_header
from credentials import MAIL_ID, MAIL_PASSWORD
import time
import re

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

        # Extracting phone number
        phone_number_match = re.search(r'Phone:\s*(.*?)\n', body)
        phone_number = phone_number_match.group(1).strip() if phone_number_match else None

        # Extracting nationality
        nationality_match = re.search(r'(?<=\n)(.*?)(?={})'.format(re.escape(email_address)), body, re.DOTALL)
        nationality = nationality_match.group(0).strip() if nationality_match else None

        return customer_name, nationality, email_address, phone_number
    except AttributeError:
        print("Failed to extract customer information. Email body:\n", body)
        return None, None, None, None

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
                        customer_name, nationality, email_address, phone_number = extract_customer_info(body)
                        if customer_name is not None:
                            print("--------")
                            print("Mail received with subject:", subject)
                            print("Customer Name:", customer_name)
                            print("Nationality:", nationality)
                            print("Email Address:", email_address)
                            print("Phone Number:", phone_number)
                            print("--------")

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
    time.sleep(60)  # Adjust the delay time as needed
