from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import serial
from selenium.webdriver.chrome.service import Service

# Open the Arduino serial connection with error handling
try:
    arduino = serial.Serial('/dev/tty.usbmodem1101', 9600)  # Adjust the COM port if needed
    print("Serial connection to Arduino established.")
except serial.SerialException as e:
    print(f"Failed to connect to Arduino: {e}")
    arduino = None  # Set Arduino to None if connection fails

# Set up Selenium WebDriver with the correct path to chromedriver
service = Service('/Users/ishitachandra/Desktop/blossom/chromedriver-mac-arm64/chromedriver')
driver = webdriver.Chrome(service=service)
print("Selenium WebDriver initialized.")

# Open WhatsApp Web
driver.get("https://web.whatsapp.com")
print("WhatsApp Web opened. Please scan the QR code.")

# Allow time to scan the QR code
input("Scan QR code and press Enter to continue...")

# Define target contact's name
target_contact = "Mom"

# Search for the specified contact name on WhatsApp
try:
    search_box = driver.find_element(By.XPATH, "//div[@contenteditable='true']")
    search_box.click()
    search_box.send_keys(target_contact + Keys.ENTER)
    print(f"Contact {target_contact} selected.")
except Exception as e:
    print(f"Error locating search box or selecting contact: {e}")

# Initialize state tracking
contact_online = False  # Track online status to avoid repeated signals
last_message = None     # Track the last message to detect new ones

# Main loop to monitor online status, unread messages, and new messages
while True:
    try:
        # Section 1: Check for online/offline status
        try:
            online_status = driver.find_element(By.XPATH, "//span[@title='online']")
            if not contact_online:  # If the contact just came online
                print("Contact is online. Sending signal to Arduino.")
                if arduino:
                    arduino.write(b'4')  # Send signal '4' to Arduino
                contact_online = True  # Update the status to online
        except:
            # If "online" is not found, check for "last seen" or empty status
            if contact_online:  # If the contact just went offline
                print("Contact is offline. Sending signal to Arduino.")
                if arduino:
                    arduino.write(b'5')  # Send signal '5' to Arduino
                contact_online = False  # Update the status to offline

        # Section 2: Check for unread messages indicator
        print("Checking for unread messages indicator from Mom...")
        unread_indicator = driver.find_elements(By.XPATH, "//span[contains(text(),'unread message')]")
        
        if unread_indicator:
            print("Unread messages detected. Sending signal to Arduino.")
            if arduino:
                arduino.write(b'3')  # Send signal '3' to Arduino
            time.sleep(5)  # Wait a bit before checking again to avoid multiple signals
        else:
            print("No unread messages from Mom.")

        # Section 3: Check for new messages
        print("Checking for new messages...")
        messages = driver.find_elements(By.XPATH, "/html/body/div[1]/div/div/div[3]/div[4]/div/div[3]/div/div[2]/div[3]/div[15]/div/div/div[1]/div[1]/div[1]/div/div[1]/div/span[1]/span")
        
        print("Messages found:", len(messages))
        if messages:
            new_message = messages[-1].text  # Get the latest message text
            print(f"Latest message detected: {new_message}")
            
            if new_message != last_message:  # Check if the message is new
                print("New message received. Sending signal to Arduino.")
                if arduino:
                    arduino.write(b'1')  # Send signal '1' to Arduino
                last_message = new_message  # Update last message to avoid repeats
            else:
                print("No new message since last check.")
        else:
            print("No messages found for this contact.")

        time.sleep(5)  # Wait before rechecking

    except Exception as e:
        print(f"Error during checks or serial communication: {e}")
        time.sleep(5)  # Wait before retrying if an error occurs
