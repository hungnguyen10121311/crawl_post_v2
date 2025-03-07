from utils.base_page import BasePage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from utils.config import Config
from selenium.webdriver.chrome.options import Options
import time
import os
import json

def main():
    # Load cấu hình
    config = Config()

    # Khởi tạo Service với đường dẫn ChromeDriver
    service = Service(config.CHROME_DRIVER_PATH)
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")  # Chặn thông báo
    # chrome_options.add_argument("--headless")  # Chế độ không giao diện
    chrome_options.add_argument("--disable-gpu")  # Vô hiệu hóa GPU khi chạy headless
    chrome_options.add_argument("--window-size=1920x1080")  # Thiết lập kích thước cửa sổ để tránh một số vấn đề hiển thị
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    # Mở trang web
    base_page = BasePage(driver)
    accounts_filename = "data/account.json"  # Đọc dữ liệu tài khoản từ file account.json
    data_filename = "data/data.json"
    
    # Đọc dữ liệu tài khoản từ account.json
    with open(accounts_filename, 'r') as file:
        accounts_data = json.load(file)
            
    with open(data_filename, 'r') as data_file:
        data = json.load(data_file)


    try:
        # Đăng nhập vào Facebook một lần
        facebook_account = data.get("account_facebook", {})
        email_facebook = facebook_account["email"]
        password_facebook = facebook_account["password"]

        driver.get(config.FACEBOOK_URL)
        base_page.login_facebook(email_facebook, password_facebook)
        time.sleep(20)

        print("Đăng nhập thành công vào Facebook.")

        # Lặp qua tất cả các tài khoản và xử lý
        for account_key, account_data in accounts_data.items():
            try:
                print(f"\nĐang xử lý tài khoản: {account_key}")

                # Lấy thông tin từ tài khoản (url1, url2, username, password)
                group_url = account_data["url2"]
                emso_username = account_data["username"]
                emso_password = account_data["password"]
                post_url = account_data["url1"]  # URL để đăng bài

                # Crawl bài viết mới từ group_url
                num_posts = 1
                base_page.get_and_create_watch(
                    username=emso_username,
                    password=emso_password,
                    nums_post=num_posts,
                    crawl_page=group_url,
                    post_page=post_url
                )

                print(f"Hoàn tất xử lý tài khoản: {account_key}")
                base_page.clear_media_folder()
            except Exception as e:
                print(f"Đã gặp lỗi khi xử lý tài khoản {account_key}: {e}")
                continue  # Tiếp tục với tài khoản tiếp theo nếu gặp lỗi

        print("Đã hoàn tất xử lý tất cả các tài khoản.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()
