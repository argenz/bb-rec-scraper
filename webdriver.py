from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import logging as log
import time
from courses_dicts import course_url_codes
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

#NEW
from selenium.webdriver.common.action_chains import ActionChains

log.basicConfig(level=log.INFO, format='%(asctime)s|%(module)s:%(lineno)s|%(levelname)s|%(message)s')
log.info('Imported logging config')

class SeleniumWebdriver(): 

    # Start selenium webdriver
    def __init__(self, url='https://blackboard.unibocconi.it/ultra/'): 
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        self.driver.get(url)
        self.cookies = self.driver.get_cookies()
        self.driver_wait = WebDriverWait(self.driver, 15)
        self.parent_window = 0

    # Login 
    def login(self, username, password):
        user = self.driver.find_element(By.ID, 'username')
        pswd = self.driver.find_element(By.ID,'password')

        user.send_keys(username)
        pswd.send_keys(password)

        self.driver.find_element(By.NAME,'_eventId_proceed').click()
        log.warning("Succesfully logged in.")
        
    # Get session cookies
    def get_cookies_dict(self):
        cookie_dict = {}
        for cookie in self.cookies:
            cookie_dict[cookie['name']] = cookie['value']
        return cookie_dict

    # Naivgate to course
    def nav_to_course(self, courseId):
        url_code = course_url_codes.get(courseId)
        self.driver.get(f"https://blackboard.unibocconi.it/ultra/courses/{url_code}/outline")   
    
    # Open dropdown with video recordings view option 
    def view_recordings(self): 
        button = self.driver_wait.until(
            EC.element_to_be_clickable((By.XPATH, "//*[@id='main-content']/div[3]/div/div[3]/div/div/div/div[2]/div/div[2]/div[2]/div/div[1]/div[2]/aside/div/div[7]/bb-overflow-menu/button"))
        )
        button.click()
        log.warning('Dots clicked.')

        dropdown = self.driver_wait.until(
            EC.presence_of_element_located((By.ID, "collab-dropdown_video_li"))
        )
        dropdown.click()
        log.warning('View recordings clicked.')
        
        try:
            time.sleep(5)
            embedded_iframe = self.driver_wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, 'iframe')))[0]
            iframe = embedded_iframe.get_attribute('src')
            self.driver.get(iframe)
            log.warning("Successfully switched to iframe.")

        except TimeoutException as err: 
            print(f"Timeout Exception: Could not load iframe.")
                
    def get_course_recordings_buttons(self):
        #store main tab 
        self.parent_window = self.driver.window_handles[0]

        rec_buttons = self.driver_wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'show-launch-details')))
        return rec_buttons

    #FROM HERE ON TO BE USED AS ITERATION OVER THE BUTTONS OBTAINED
    def get_lecture_name_from_button(self, button): 
        button_wait = WebDriverWait(button, 20)
        children = button_wait.until(EC.presence_of_all_elements_located((By.XPATH, ".//*")))
        name_elem = [child.text.replace(" ", "") for child in children]
        return "_".join(name_elem)

    
    def click_rec_button_and_open_rec_link(self, rec_button, i): 
        rec_button.click()
        watch_now_dropdown = self.driver_wait.until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "loading-button"))
        )[i]

        action = ActionChains(self.driver)
        action.move_to_element(watch_now_dropdown).click().perform()
                
        child = self.driver.window_handles[1]
        #switch to browser tab
        self.driver.switch_to.window(child)
    
    def get_recording_url(self): 
        video = self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'vjs-tech')))
        url = video.get_attribute('src')
        return url

    def close_rec_tab(self): 
        self.driver.close()
        self.driver.switch_to.window(self.parent_window)

    # When finished: Quit 
    def quit(self): 
        self.driver.quit()

    def check_announcemements_and_skip(self): 
        try:
            self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "title-modal"))) 
            try:
                button_close = self.driver_wait.until(EC.presence_of_element_located((By.CLASS_NAME, "close-modal-button")))
                button_close.click()
                log.warning("Announcement found and closed.")
            except: 
                log.warning("Cannot find close button.")

        except TimeoutException as err: 
            log.warning("No Announcements.")



