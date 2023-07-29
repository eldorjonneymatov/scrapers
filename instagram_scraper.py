import os
import json
from time import sleep
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class PostScrapper:
    def __init__(self, username, required_posts=12):
        try:
            self.required_posts = required_posts
            self.username = username
            self.post_count = 0
            self.post_urls = []
            self.image_urls = []
            # driver
            self.driver = webdriver.Chrome()
            self.driver.get('http://www.instagram.com')
            # login
            self.login()
            # avoid notifications
            self.avoid_notifications()
            # user`s all posts page
            self.get_all_posts_page()
            # first scraping
            completed = self.bs_scrapper()
            if completed:
                return
            # scroll down to bottom
            self.scroll_to_bottom()
            # save data
            self.write_to_json()
            self.driver.close()
        except Exception as e:
            print(e)
    

    def login(self):
        load_dotenv()
        sleep(10)
        # username
        username_input = self.driver.find_element(By.NAME, "username")
        username_input.clear()
        username_input.send_keys(os.getenv('INSTA_USERNAME'))
        # password
        password_input = self.driver.find_element(By.NAME, "password")
        password_input.clear()
        password_input.send_keys(os.getenv('INSTA_PASSWORD'))
        # submit
        login_input = self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        login_input.submit()
        sleep(10)


    def avoid_notifications(self):
        # first notification
        first_notification = self.driver.find_element(By.XPATH, '//div[text()="Not Now"]')
        first_notification.click()
        sleep(5)
        # second notification
        second_notification = self.driver.find_element(By.XPATH, '//button[text()="Not Now"]')
        second_notification.click()
        sleep(10)


    def get_all_posts_page(self):
        # profile
        self.driver.get(f'http://www.instagram.com/{self.username}')
        sleep(10)
        # all posts
        all_posts_button = self.driver.find_element(By.XPATH, "//span[text()='Posts']")
        all_posts_button.click()
        sleep(10)


    def scroll_to_bottom(self):
        scroll_pause_time = 2    
        # Get scroll height
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            # Wait to load page
            sleep(scroll_pause_time)
            completed = self.bs_scrapper()
            if completed:
                return
            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                return
            last_height = new_height


    def bs_scrapper(self):
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        for post_data, image_data in zip(soup.select('article div a'), soup.select('article div a img')):
            post_url = post_data.get('href')
            image_url = image_data.get('src')
            if post_url not in self.post_urls:
                self.post_urls.append(post_url)
                self.image_urls.append(image_url)
                self.post_count += 1
                if self.post_count >= self.required_posts:
                    self.post_urls = self.post_urls[:self.required_posts]
                    self.image_urls = self.image_urls[:self.required_posts]
                    return True
        return False


    def write_to_json(self):
        with open(f'{self.username}_{self.required_posts}.json', 'w') as f:
            for post, image in zip(self.post_urls, self.image_urls):
                json.dump({
                    'post_url': str(post),
                    'image_url': str(image)
                }, f)


ps = PostScrapper('example_username', 10)
