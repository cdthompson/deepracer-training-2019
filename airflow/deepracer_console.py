#
# Helper for driving headless chrome.  Useful for linking to web accounts
#
from selenium import webdriver as wd
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
import selenium.common.exceptions
from pyvirtualdisplay import Display
from selenium.webdriver.chrome.options import Options
import os
import subprocess

def launch_webdriver():
    # Some context from trying to get a working webdriver
    #subprocess.call(["/usr/bin/chromium-browser", "--version"])
    #subprocess.call(["dpkg", "-s", "chromium-browser"])
    #subprocess.call(["sudo", "apt-get", "-s", "-V", "upgrade", "chromium-browser"])
    options = wd.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1024,768")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--verbose")
    options.binary_location = "/usr/bin/chromium-browser"
    #subprocess.call(["which", "chromium-browser"])
    service_log_path = os.getcwd() + "/chromedriver.log"
    service_args=["--verbose"]
    os.environ['DISPLAY'] = ':99'
    display=Display(visible=0, size=(1024, 768)).start()
    browser = wd.Chrome(chrome_options=options, service_args=service_args)
    browser.implicitly_wait(10)
    return browser

def find_by_xpath_or_none(browser, xpath):
    try:
        element = browser.find_element_by_xpath(xpath)
        print("Found element at '%s'" % xpath)
        return element
    except selenium.common.exceptions.NoSuchElementException:
        print("Did not find element at '%s'" % xpath)
        return None

def deepracer_submit_model_to_virtual_race(model, account, username, password):
    try:
        browser = launch_webdriver()
        console_url = "https://console.aws.amazon.com/deepracer/home?region=us-east-1#model/%s" % model
        browser.get(console_url)
        # Check if browser redirected to sign-in
        submit_button = find_by_xpath_or_none(browser, "//button[span/text()='Submit to virtual race']")
        if submit_button is None:
            print("No race submit button found, must have redirected to sign in")
            print("Current URL: ", browser.current_url)
            # In case of some unexpeted pre-filled account id, use the switch account link
            switch_account_link = find_by_xpath_or_none(browser, "//a[@id='aws-login-switchaccount-link']")
    
            # may or may not have the user name field visible, depending on browser cookies
            next_button = find_by_xpath_or_none(browser, "//button[@id='next_button']")
            if next_button:
                print("Found first sign-in page")
                account_text_field = browser.find_element_by_class_name("aws-signin-textfield")
                account_text_field.clear()
                account_text_field.send_keys(account)
                next_button.click()
    
            account_text_field = browser.find_element_by_xpath("//input[@name='account']")
            account_text_field.clear()
            account_text_field.send_keys(account)
            username_text_field = browser.find_element_by_xpath("//input[@name='username']")
            username_text_field.clear()
            username_text_field.send_keys(username)
            password_text_field = browser.find_element_by_xpath("//input[@name='password']")
            password_text_field.clear()
            password_text_field.send_keys(password)
            sign_in_button = browser.find_element_by_xpath("//a[@id='signin_button']")
            print("Current URL: ", browser.current_url)
            sign_in_button.click()
            WebDriverWait(browser, 10).until(EC.url_changes(console_url))
            print("Redirect after login")
            print("Current URL: ", browser.current_url)
            submit_button = find_by_xpath_or_none(browser, "//button[span/text()='Submit to virtual race']")
            if submit_button is None:
                # Must have landed back on AWS landing screen after successful sign in
                browser.get(console_url)
                # Don't catch exceptions if here, the final place to find the submit buton
                print("Current URL: ", browser.current_url)
                submit_button = browser.find_element_by_xpath("//button[span/text()='Submit to virtual race']")
    
        print("Current URL: ", browser.current_url)
    
        print("Ready to drive the console")
        if submit_button.is_enabled():
            print("Submit button is enabled")
            submit_button.click()
            #submit_form_url = "https://console.aws.amazon.com/deepracer/home?region=us-east-1#model/%s/submitModel" % model
            #WebDriverWait(browser, 10).until(EC.url_changes(submit_form_url))
            submit_model_button = browser.find_element_by_xpath("//button[@type='submit'][span/text()='Submit model']")
            print("Current URL: ", browser.current_url)
            submit_model_button.click()
            #leaderboard_url = "https://console.aws.amazon.com/deepracer/home?region=us-east-1#leaderboard/Toronto%20Turnpike"
            #WebDriverWait(browser, 10).until(EC.url_changes(leaderboard_url))
            rank_text = browser.find_element_by_xpath("//h5[text()='Your rank']")
            print("Current URL: ", browser.current_url)
            result = True
        else:
            print("Submit button was disabled!")
            result = False
    
        return result
    finally:
        browser.quit()

