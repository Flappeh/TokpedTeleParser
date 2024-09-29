from appium import webdriver
from typing import Dict, Any
from appium.options.common.base import AppiumOptions
from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.webelement import WebElement
from .environment import ANDROID_SERVER_URL, TIMEOUT_LIMIT
from .utils import get_logger, store_phrase, get_wallet_account, PiAccount, delete_wallet_account
from .exceptions import PiAccountError
from time import sleep,time
from multiprocessing import Process, Queue

TIMEOUT = TIMEOUT_LIMIT
logger = get_logger(__name__)
running_bot = []

capabilities: Dict[str, Any] = {
    "platformName": "Android",
    "automationName": "uiautomator2",
    # "appPackage":"pi.browser", 
    # "appActivity": "com.pinetwork.MainActivity",
    "deviceName": "Android",
    "language": "en"
}

class AndroidBot():
    def __init__(self) -> None:
        self.driver: webdriver.Remote = webdriver.Remote(ANDROID_SERVER_URL, options=AppiumOptions().load_capabilities(capabilities))
        self.current_page = ""
        self.age = time()
        
    def click_update(self) -> None:
        try:
            logger.debug("Clicking Update")
            updateParent = self.driver.find_element(by=AppiumBy.XPATH, value='//android.app.Dialog')
            children = updateParent.find_elements(by=AppiumBy.CLASS_NAME, value="android.widget.Button")
            children[0].click()
        except:
            logger.error("Unable to click Update")
            pass
    def click_notif(self) -> None:
        try:
            logger.debug("Clicking notification")
            notif = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Not Now"]')
            notif.click()
        except:
            pass

    def verify_wallet(self) -> None:
        try:
            logger.debug("Verifying wallet ownership")
            self.driver.find_element(by=AppiumBy.XPATH, value="//android.widget.Button[contains(@text,'Continue')]").click()
        except:
            logger.warning("Unable to verify")

    def check_is_loading(self):
        loading_screen = self.driver.find_element(by=AppiumBy.XPATH, value='//*[@text="Loading..."]')
        if loading_screen:
            self.click_notif()
            self.click_update()
            return True
        return False

    def check_current_page(self):
        Page_Source = self.driver.page_source
        if "Welcome to the Pi Browser" in Page_Source:
            return "home"
        if "Loading" in Page_Source:
            return "loading"
        if "Unlock Pi Wallet" in Page_Source:
            return "wallet_home"
        if "Turn on notifications!" in Page_Source:
            self.click_notif()
            return "notification"
        if "Update your app" in Page_Source:
            self.click_update()
            return "update"
        if "This is your identity on the Pi" in Page_Source:
            self.verify_wallet()
            return "verification"
        if "Available Balance" in Page_Source:
            return "wallet_page"
        if "Translation loading ..." in Page_Source:
            self.click_update()
            return "update"
        return ""

    def check_current_wallet_balance(self):
        logger.debug("Checking current wallet balance")
        current_page = self.check_current_page()
        while current_page != "wallet_page":
            if current_page == "notification":
                self.click_notif()
            if current_page == "update":
                self.click_update()
            if current_page == "verification":
                self.verify_wallet()
            current_page = self.check_current_page()
        try:
            logger.debug("Trying to get available balance")
            balance = self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text," Pi")][1]')
            return balance.text
        except Exception as e:
            logger.error(f"Error checking curent balance, error : {e}")
        
    def reload_wallet_page(self):
        try:
            logger.debug("Finding send/receive element")
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Send / Receive")]').click()
        except:
            logger.error("Error clicking send receive button on reloading")
        try:
            logger.debug("Finding back button element")
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[@resource-id="address-bar-back-button"]').click()
        except:
            logger.error("Error clicking back button on reloading wallet page")
            raise
        while self.check_current_page() != "wallet_home":
            logger.info("Not in wallet home")
            self.click_notif()
            pass
        
    def open_wallet_sub_page(self):
        try:
            logger.debug("Opening wallet sub page")
            self.driver.tap([(160,330)])
        except:
            logger.error("Error going to sub page")
        while self.check_current_page() != "wallet_home":
            self.click_notif()
            pass
            
    def navigate_to_wallet_home(self):
        current_page = self.check_current_page()
        while current_page != "wallet_home": 
            logger.debug(f"Current page before match: {current_page}")  # Debugging line
            match current_page:
                case "wallet_home":
                    break
                case "wallet_page":
                    self.reload_wallet_page()
                case "home":
                    self.open_wallet_sub_page()
                case "loading":
                    logger.debug("Still loading")
                case "notification":
                    logger.debug("Notification Found")
                case "update":
                    logger.debug("Update notification found")
                case "verification":
                    self.verify_wallet()
                case _:
                    logger.warning("Got undefined while navigating to wallet home")
            current_page = self.check_current_page()
            logger.debug(f"Current page after match: {current_page}")  # Debugging line
    
    def try_enter_wallet(self, pwd:str):
        try:
            logger.debug("Trying to enter wallet phrase")
            login_box = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.EditText')
            login_box.clear()
            login_box.send_keys(pwd)
            self.driver.hide_keyboard()
            self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[contains(@text, "Unlock With")]').click()
            return True
        except Exception as e:
            logger.error("Error entering wallet phrase")
            return False
    
    def enter_wallet_phrase(self, pwd:str)-> str:
        logger.debug("Received enter wallet phrase command")
        page = self.driver.page_source
        error_check = 0
        while self.try_enter_wallet(pwd) != True:
            self.try_enter_wallet(pwd)
            page = self.driver.page_source
            if "Available Balance" in page:
                break
            if error_check == 5:
                return "error"
            if "An error" in page:
                error_check += 1
            if "Invalid" in page:
                error_check += 1
            if "This is your identity on the Pi Blockchain" in self.driver.page_source:
                self.verify_wallet()
        if "An error" in page:
            return "error"
        elif "Invalid" in page:
            return "invalid"
        elif "Available Balance" in page:
            return "ok"
        else:
            return "exception"
        
    def sign_out_user(self):
        logger.debug("Received sign out user command")
        result = False
        while result == False:
            try:
                self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Sign Out")]').click()
                sleep(0.4)
                self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Sign Out")]').click()
                result = True
            except:
                logger.error("Unable to sign out")
            sleep(0.3)
        
    def open_profile_page(self) -> None:
        logger.debug("Opening profile page")
        if "Referral Team" not in self.driver.page_source and "Node" not in self.driver.page_source:
            sleep(0.3)
            self.driver.tap([(30,50)])
        sleep(0.35)
        self.driver.flick(100,500,100,200)
        sleep(0.3)
        try:
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Profile")]').click()
        except:
            logger.error("Error clicking profile button")
        self.sign_out_user()
        
    def enter_keyboard_indonesia(self):
        self.driver.press_keycode(37)
        self.driver.press_keycode(42)
        self.driver.press_keycode(32)
        self.driver.press_keycode(43)
        self.driver.press_keycode(42)
    
    def insert_phone_number(self, account: PiAccount)-> bool:
        try:
            logger.debug("Inserting phone number")
            while "Register with phone number" not in self.driver.page_source:
                self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "with phone number")]').click()
                sleep(0.2)
            country_box = self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "United States")]')
            country_box.click()
            sleep(0.2)
            self.enter_keyboard_indonesia()
            self.driver.hide_keyboard()
            self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.TextView[contains(@text, "Phone number")]').click()
            phone_box = self.driver.find_element(by=AppiumBy.XPATH, value='//android.view.View[@resource-id="root"]/android.view.View/android.view.View/android.view.View/android.view.View[3]/android.widget.EditText')
            phone_box.send_keys(account.phone)
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Submit")]').click()
            sleep(0.5)
            return True
        except:
            logger.error("Error inserting phone number")
            return False
    
    def enter_phone_number(self, account: PiAccount) -> bool:
        try:
            while "Enter your password" in self.driver.page_source:
                logger.debug("Trying to insert phone number")
                password_box = self.driver.find_element(by=AppiumBy.XPATH, value='//android.widget.EditText')
                password_box.send_keys(account.password)
                self.driver.hide_keyboard()
                self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Submit")]').click()
                sleep(0.5)
            return True
        except:
            logger.error("Error inserting phone number")
          
    def login_with_phone_number(self) -> bool:
        try:
            logger.debug("Getting new wallet account")
            account = get_wallet_account()
        except:
            logger.error("Error getting new wallet account")
            return False
        try:
            logger.debug("Logging in with new phone number")
            self.insert_phone_number(account)
            self.enter_phone_number(account)
            while "Enter your password" in self.driver.page_source:
                logger.warning("Still in password form")
                self.driver.hide_keyboard()
                if "Invalid phone number" in self.driver.page_source:
                    self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text, "Return to login")]').click()
                    delete_wallet_account(account)
                    return False
            return True
        except Exception as e:
            logger.error(f"Error occured while logging in with phone number, {e}")
    
    def navigate_to_pi_network(self) -> None:
        try:
            logger.debug("Navigation to pi network, clicking keep on mining")
            while "Keep on mining" not in self.driver.page_source:
                self.driver.tap([(260,300)])
                self.driver.tap([(260,310)])
                self.driver.tap([(260,340)])
                self.driver.tap([(260,360)])
                if "Mine by confirming" in self.driver.page_source:
                    self.driver.tap([(150,570)])
                    sleep(0.3)
                    self.driver.tap([12,74])
                    break
                if "Mining Session Ends" in self.driver.page_source:
                    self.driver.tap([(40,50)])
                    break
                sleep(0.2)
            self.driver.find_element(by=AppiumBy.XPATH, value='//*[contains(@text,"Not Now")]').click()
            self.driver.tap([(50,350)])
        except:
            logger.error("Error navigating to pi network")
    
    def login_to_browser(self) -> bool:
        try:
            logger.debug("Logging in to pi browser after signing in")
            if "Referral Team" not in self.driver.page_source and "Node" not in self.driver.page_source:
                sleep(0.3)
                self.driver.tap([(30,50)])
            sleep(0.35)
            self.driver.flick(100,200,100,300)
            sleep(0.3)
            self.driver.tap([(110,200)])
            sleep(0.3)
            self.driver.flick(100,300,100,200)
            sleep(1)
            self.driver.tap([(150,620)])
            current_tries = 0
            result = False
            while current_tries < 5:
                if "Welcome to the Pi Browser" in self.driver.page_source:
                    logger.debug("Successfully logged into browser")
                    result = True
                    break
                if "Unlock Pi Wallet" in self.driver.page_source:
                    logger.debug("Successfully logged into browser")
                    result = True
                    break
                if "If above button doesn't" in self.driver.page_source:
                    self.driver.tap([(150,620)])
                else:
                    sleep(1)
                    current_tries += 1
            return result
        except:
            logger.error("Error logging in to pi browser")
            return False
            
    def start_login_user(self) -> None:
        try:
            logger.debug("Start logging in new user")
            while "Continue with phone" not in self.driver.page_source:
                pass
            login_result = self.login_with_phone_number()
            if login_result == False:
                while login_result == False:
                    login_result = self.login_with_phone_number()
            self.navigate_to_pi_network()
            if self.login_to_browser() == False:
                self.change_user()
        except:
            logger.error("Error logging in user")
    
    def check_if_user_verif_needed(self) -> bool:
        try:
            logger.debug("Handling user verification")
            if "Sign out" in self.driver.page_source:
                return True
            self.driver.tap([(20,50)])
            sleep(1)
            if "Chat" in self.driver.page_source and "Roles" in self.driver.page_source and "Referral" in self.driver.page_source:
                return True
            self.driver.tap([(20,50)])
            sleep(1)
            if "Chat" in self.driver.page_source and "Roles" in self.driver.page_source and "Referral" in self.driver.page_source:
                return True
            elif "Continue with phone" in self.driver.page_source or "Please verify your identity" in self.driver.page_source:
                return True
            else:
                return False
        except Exception as e:
            logger.error(f"Error in handling user verification, {e}")
    
    def change_user(self) -> None:
        logger.debug("Received command to change user")
        self.driver.activate_app('com.blockchainvault/com.pinetwork.MainActivity')
        sleep(1)
        if self.check_if_user_verif_needed() == False:
            logger.debug("Need user Verification")
            self.navigate_to_pi_network()
        page = self.driver.page_source
        if "code to share" in page or "Settings" in page or "Hide real name" in page:
            logger.debug("Already on profile page")
            self.sign_out_user()
            self.start_login_user()
        elif "Continue with phone" in self.driver.page_source:
            self.start_login_user()
        else:
            logger.debug("Not in profile page")
            self.open_profile_page()
            self.start_login_user()
        
    def open_wallet_from_passphrase(self, pwd: str):
        self.driver.activate_app('pi.browser/com.pinetwork.MainActivity')
        logger.info(f"Received new request for phrase: {pwd}")
        if self.check_current_page() != "wallet_home":
            self.navigate_to_wallet_home()
        result = self.enter_wallet_phrase(pwd)
        if result == "exception":
            while result == "exception":
                result = self.enter_wallet_phrase(pwd)
                if result == "error":
                    break
        if result == "error":
            return "Error butuh ganti ke user lain"
        if result == "invalid":
            i = 0
            while i < 3:
                result = self.enter_wallet_phrase(pwd)
                i += 1
            if result == "ok":
                self.check_current_page()
            elif result == "error":
                return "Error butuh ganti ke user lain"
            else:
                return "Invalid passphrase given"
        else:
            self.check_current_page()
        logger.debug(f"Current value = {result}")
        value = self.check_current_wallet_balance()
        store_phrase(pwd, value)
        return value
    
    def open_wallet_after_error(self, pwd: str):
        self.change_user()
        data = self.open_wallet_from_passphrase(pwd)
        while data == "Error butuh ganti ke user lain":
            self.change_user()
            data = self.open_wallet_from_passphrase(pwd)
        return self.open_wallet_from_passphrase(pwd)
        
    def print_current_page(self):
        return self.driver.page_source
    
    def change_user_command(self) -> str:
        self.change_user()
    
    def kill_all_apps(self) -> None:
        self.driver.terminate_app('pi.browser')
        self.driver.terminate_app('com.blockchainvault')
       
    def __del__(self):
        logger.info("Finished running script")
        self.driver.quit()

def get_running_bot():
    if len(running_bot) != 0:
        logger.debug("Found running bot")
        bot: AndroidBot = running_bot[0]
        if time() - bot.age > 4800:
            logger.debug("Bot exceeds maximum time, creating a new one")
            del bot
        else:
            return bot
    logger.debug("Creating a new bot.")
    bot = AndroidBot()
    running_bot.append(bot)
    logger.info(f"Running bot count : {len(running_bot)}")
    return bot

def process_phrase(phrase:str, result_queue : Queue):
    try:
        logger.debug("Starting new request for processing phrase")
        bot = get_running_bot()
        data = bot.open_wallet_from_passphrase(phrase)
        result_queue.put(data)
    except:
        logger.error("Error processing phrase")

def process_phrase_after_error(phrase:str, result_queue : Queue):
    try:
        logger.debug("Starting new request for processing phrase")
        bot = get_running_bot()
        data = bot.open_wallet_after_error(phrase)
        result_queue.put(data)
    except:
        logger.error("Error processing phrase")

def process_change_user():
    try:
        logger.debug("Starting new request for processing phrase")
        bot = get_running_bot()
        data = bot.change_user_command()
        return data
    except:
        logger.error("Error processing phrase")

def kill_all_apps():
    bot = get_running_bot()
    bot.kill_all_apps()
    del bot

def start_background_process(target: Any, phrase: str = None):
    START_TIME = time()
    current_process = None
    if phrase:
        result = Queue()
        current_process = Process(target=target, args=(phrase,result))
    else:
        current_process = Process(target=target)
    current_process.start()
    while time() - START_TIME <= TIMEOUT:
        if not current_process.is_alive():
            break
        sleep(1)
    else:
        current_process.terminate()
        kill_all_apps()
        current_process.join()
        return "timeout"
    return result.get()
    
def start_bot_phrase_process(phrase:str):
    return start_background_process(process_phrase, phrase)

def start_change_user_process():
    return start_background_process(process_change_user)

def start_phrase_process_after_error(phrase:str):
    return start_background_process(process_phrase_after_error,phrase)