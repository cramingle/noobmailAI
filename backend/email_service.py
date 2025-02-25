import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formatdate, make_msgid, formataddr
import uuid
from datetime import datetime
from bs4 import BeautifulSoup

def validate_html_content(html_content):
    """Validate HTML content for potential spam triggers"""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Check image-to-text ratio
    text_content = soup.get_text()
    images = soup.find_all('img')
    image_count = len(images)
    text_length = len(text_content)
    
    warnings = []
    if image_count > 0 and text_length / image_count < 100:
        warnings.append("High image-to-text ratio detected")
    
    # Check for common spam trigger words
    spam_triggers = ['free', 'guarantee', 'no cost', 'winner', 'won', 'prize']
    for trigger in spam_triggers:
        if trigger in text_content.lower():
            warnings.append(f"Potential spam trigger word found: {trigger}")
    
    return warnings

def send_email(content: str, recipients: list, smtp_config: dict, campaign_name: str = 'newsletter'):
    """Send email to recipients using the provided SMTP configuration"""
    try:
        # Create HTML template from content if not already HTML
        if not content.strip().startswith('<'):
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Newsletter</title>
            </head>
            <body style="margin: 0; padding: 20px; font-family: Arial, sans-serif;">
                {content}
            </body>
            </html>
            """
        else:
            html_content = content
        
        # Validate content
        warnings = validate_html_content(html_content)
        if warnings:
            print("Content warnings:", warnings)
        
        successful_sends = 0
        failed_sends = []
        
        for recipient in recipients:
            try:
                # Create message container
                msg = MIMEMultipart('alternative')
                
                # Format sender and recipient addresses
                sender_addr = formataddr((smtp_config['name'], smtp_config['email']))
                recipient_addr = formataddr((recipient['name'], recipient['email']))
                domain = smtp_config['email'].split('@')[1]
                
                # Add headers
                msg['Subject'] = 'Newsletter'
                msg['From'] = sender_addr
                msg['To'] = recipient_addr
                msg['Date'] = formatdate(localtime=True)
                msg['Message-ID'] = make_msgid(domain=domain)
                
                # Authentication headers
                msg['Authentication-Results'] = f"spf=pass smtp.mailfrom={smtp_config['email']}"
                
                # List management headers
                msg['List-Unsubscribe'] = f'<https://research.zirodelta.com/unsubscribe?email={recipient["email"]}>'
                msg['List-ID'] = f'Zirodelta Research <newsletter.{domain}>'
                msg['Precedence'] = 'bulk'
                
                # Additional headers
                msg['X-Entity-Ref-ID'] = str(uuid.uuid4())
                msg['X-Campaign-ID'] = f'{campaign_name}-{datetime.now().strftime("%Y%m")}'
                msg['X-Message-Category'] = 'education'
                
                # Replace placeholders in content
                personalized_content = html_content.replace('[[NAME]]', smtp_config['name'])
                personalized_content = personalized_content.replace('[[RECIPIENT_NAME]]', recipient['name'])
                personalized_content = personalized_content.replace('[[RECIPIENT_EMAIL]]', recipient['email'])
                if recipient.get('organization'):
                    personalized_content = personalized_content.replace('[[ORGANIZATION]]', recipient['organization'])
                
                # Add HTML content
                msg.attach(MIMEText(personalized_content, 'html', 'utf-8'))
                
                # Create secure connection and send
                if smtp_config['port'] == "465":
                    server = smtplib.SMTP_SSL(smtp_config['server'], int(smtp_config['port']))
                else:
                    server = smtplib.SMTP(smtp_config['server'], int(smtp_config['port']))
                    server.starttls()
                
                server.login(smtp_config['email'], smtp_config['password'])
                server.sendmail(smtp_config['email'], recipient['email'], msg.as_string())
                server.quit()
                
                successful_sends += 1
                print(f"✓ Sent to {recipient['name']} <{recipient['email']}>")
                
            except Exception as e:
                failed_sends.append({
                    'email': recipient['email'],
                    'error': str(e)
                })
                print(f"✗ Failed to send to {recipient['email']}: {str(e)}")
        
        return {
            'success': True,
            'successful_sends': successful_sends,
            'failed_sends': failed_sends
        }
        
    except Exception as e:
        raise Exception(f"Failed to send emails: {str(e)}")

def improve_content(content: str) -> str:
    """Improve email content using AI"""
    # For now, return a simple modification
    # TODO: Integrate with actual AI service
    improved = content.strip()
    improved = f"{improved}\n\nBest regards,\nZirodelta Research"
    return improved 