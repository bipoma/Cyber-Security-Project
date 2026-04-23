# This script sends emails to a specified recipient using templates from JSON files, with timing randomized over a specified duration.
# It reads email IDs from a CSV file, matches them to templates in GenEmails.json and zendoEmails.json, and sends them via SMTP with retry logic for network issues.
# Usage: python sendingemails.py --start 1 --hours 6

#import necessary libraries
import smtplib
import csv
import json
import time
import sys
import random
import socket
import argparse
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
'''
psudo code, as key is real
SENDER_EMAIL = "1" 
APP_PASSWORD = "1" + "key"
SENDER_EMAIL = "2"
APP_PASSWORD = "2" + "key" 
CUSTOM_RECIPIENT = "3"
CUSTOM_RECIPIENT = "4"
CUSTOM_RECIPIENT = "5"
CUSTOM_RECIPIENT = "6"
'''
SENDER_EMAIL = "BLANK@BLANK.COM" #Email redacted for security
APP_PASSWORD = "000000000" # key redacted for security


#sending plain text email with retry logic for network issues
# Returns True if email sent successfully, False otherwise
def send_plain_email(sender_email, app_password, recipient, subject, body, retries=3): 
    """UTF-8 email sender with DNS/network retry logic"""
    # Attempt to send email, retrying on network-related errors
    for attempt in range(retries):
        try:
            # Construct email message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            mime_text = MIMEText(body, 'plain', 'utf-8')
            msg.attach(mime_text)

            # Connect to SMTP server and send email
            server = smtplib.SMTP('smtp.gmail.com', 587, timeout=30)
            server.starttls()
            server.login(sender_email, app_password)
            server.sendmail(sender_email, recipient, msg.as_string())
            server.quit()
            
            # Print confirmation and return success
            print(f"SENT to {recipient}")
            print(f"   Subject: {subject}")
            print(f"   Body preview: {body[:100]}...")
            print()
            return True
        
        # Handle network-related exceptions with retries
        except (OSError, socket.gaierror, smtplib.SMTPConnectError) as e:
            if attempt < retries - 1:
                # Print warning and retry after delay
                print(f"   Network error (attempt {attempt + 1}/{retries}): {str(e)}")
                print(f"   Retrying in 10s...")
                time.sleep(10)
                continue
            else:
                print(f"FAILED: {str(e)}\n")
                return False
        except Exception as e:
            print(f"FAILED: {str(e)}\n")
            return False

# Function to read email IDs from CSV file, expecting one ID per line
# Returns a list of IDs
def read_csv_ids(csv_file):
    ids = []
    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and row[0].strip():
                    ids.append(row[0].strip())
    except FileNotFoundError:
        print(f"ERROR: {csv_file} not found")
        sys.exit(1)
    return ids

# Function to calculate a variable delay with ±50% random variance, ensuring a minimum of 1 second
def get_variable_delay(base_delay):
    variance = base_delay * 0.5
    delay = base_delay + random.uniform(-variance, variance)
    return max(delay, 1.0)

# Main function to orchestrate the email sending campaign, with timing and template matching
def send_emails(csv_file, gen_json, zendo_json, start_num=1, total_hours=6):
    print(f"Campaign: {total_hours}HR timing from {SENDER_EMAIL} -> {CUSTOM_RECIPIENT}")
    print("=" * 70)

    # Read email IDs from CSV file
    ids = read_csv_ids(csv_file)

    # If start_num is greater than 1, skip to that index in the list of IDs
    if start_num > 1:
        start_idx = max(0, start_num - 1)
        ids = ids[start_idx:]
        print(f"Skipping to start #{start_num} ({len(ids)} remaining IDs)")

    # Calculate total emails and base delay for timing
    total_emails = len(ids)
    print(f"Loaded {total_emails} IDs")

    # Calculate base delay to spread emails over the specified total hours, with random variance
    total_seconds = total_hours * 60 * 60
    base_delay = total_seconds / max(total_emails, 1)
    print(f"Base delay: {base_delay:.1f}s (with ±50% random variance)")
    print(f"Estimated finish: ~{time.strftime('%H:%M', time.localtime(time.time() + total_seconds))}\n")

    # Load email templates from both JSON files into a single dictionary for quick lookup by ID
    all_emails = {}
    for json_file in [gen_json, zendo_json]:
        try:
            # Load JSON data and populate all_emails dict with ID as key
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for obj in data:
                    oid = str(obj.get('id', '')).strip()
                    if oid:
                        all_emails[oid] = obj
            print(f"Loaded {json_file}")
        except FileNotFoundError:
            print(f"{json_file} not found - skipping")
        except Exception as e:
            print(f"Error in {json_file}: {e}")

    print(f"Found {len(all_emails)} templates\n")

    sent = 0
    start_time = time.time()
    # Loop through each email ID, send the email using the template, and wait for a variable delay before the next one
    for i, tid in enumerate(ids, 1):
        elapsed = time.time() - start_time
        delay = get_variable_delay(base_delay)
        print(f"[{i}/{total_emails}] {tid} ({elapsed / 60:.1f}min) | Next in {delay:.1f}s")

        # Check if the ID exists in the loaded templates, and send the email if found
        if tid in all_emails:
            obj = all_emails[tid]
            subject = obj.get('subject', 'No Subject')
            body = obj.get('body', '')
            if send_plain_email(SENDER_EMAIL, APP_PASSWORD, CUSTOM_RECIPIENT, subject, body):
                sent += 1
        else:
            print(f"   Not found")
            print()

        if i < total_emails:
            time.sleep(delay)
    # After all emails have been processed, print a summary of the campaign results and total duration
    total_time = time.time() - start_time
    print("=" * 70)
    print(f"COMPLETE - Sent: {sent}/{total_emails}")
    print(f"Total duration: {total_time / 3600:.2f} hours ({total_time / 60:.1f} minutes)")

# Execute main function with command-line arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Email campaign sender") # Command-line arguments for starting index, total hours, and file paths
    parser.add_argument("--start", type=int, default=1, help="Start from email # (1-indexed)") # Allows resuming from a specific email number in the list
    parser.add_argument("--hours", type=float, default=6.0, help="Total campaign hours (default 6)") # Total duration over which to spread the email sending
    parser.add_argument("csv_file", nargs='?', default="Datasets\Emails\email list.csv", help="CSV file") # CSV file containing email IDs, one per line
    parser.add_argument("gen_json", nargs='?', default="Datasets\Emails\GenEmails.json", help="GenEmails JSON") # JSON file containing generated email templates
    parser.add_argument("zendo_json", nargs='?', default="Datasets\Emails\zendoEmails.json", help="ZendoEmails JSON") # JSON file containing zendo email templates

    # Parse the command-line arguments and start the email sending process with the specified parameters
    args = parser.parse_args()
    # Call the main function to send emails based on the provided CSV and JSON files, starting index, and total hours for the campaign
    send_emails(args.csv_file, args.gen_json, args.zendo_json, args.start, args.hours)
