import imaplib
import email
from bs4 import BeautifulSoup

def get_amazon_otp(email_address, password):
    otp_found = False
    try:
        # Connect to the mail server
        mail = imaplib.IMAP4_SSL('outlook.office365.com', 993)
        mail.login(email_address, password)

        # List all mailboxes/folders including 'Junk'
        status, folders = mail.list()
        all_folders = [folder.decode().split(' "/" ')[-1] for folder in folders] + ['Junk']

        amazon_domains = ['amazon.com', 'amazon.de', 'amazon.co.uk', 'amazon.ca', 'amazon.nl', 'amazon.fr', 'amazon.it',
                          'amazon.es', 'amazon.com.br', 'amazon.com.mx', 'amazon.co.jp', 'amazon.in', 'amazon.com.au',
                          'amazon.sg']

        for folder_name in all_folders:
            mail.select(folder_name)

            for domain in amazon_domains:
                # Search for all emails from each Amazon domain in the current folder
                status, email_ids = mail.search(None, f'(FROM "{domain}")')
                email_ids = email_ids[0].split()

                if not email_ids:
                    continue

                for e_id in email_ids:
                    _, data = mail.fetch(e_id, '(RFC822)')
                    raw_email = data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    email_content = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            if "attachment" not in content_disposition and content_type == "text/html":
                                email_content += part.get_payload(decode=True).decode()
                    else:
                        # If email isn't multipart, just extract the content
                        email_content = msg.get_payload(decode=True).decode()

                    # Parse the HTML content with BeautifulSoup
                    soup = BeautifulSoup(email_content, 'html.parser')
                    otp_content = soup.find('p', class_='otp')
                    if otp_content:
                        print(otp_content.text)
                        otp_found = True
                        break

        # Logout and close the connection
        mail.logout()
    except Exception as e:
        print(f"Error fetching emails for {email_address}. Error: {e}")

    if not otp_found:
        print("Dont have OTP. Try check it again.")

if __name__ == "__main__":
    user_input = input("Enter your email address and password in the format emailaddress|password: ")
    email_address, password = user_input.split('|')
    get_amazon_otp(email_address, password)
