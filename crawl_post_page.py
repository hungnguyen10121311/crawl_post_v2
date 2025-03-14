from utils.base_page import BasePage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from utils.config import Config
from selenium.webdriver.chrome.options import Options
import time
import os
import json
import random

def main():
    # Load cấu hình
    config = Config()

    # Khởi tạo Service với đường dẫn ChromeDriver
    service = Service(config.CHROME_DRIVER_PATH)
    chrome_options = Options()
    chrome_options.add_argument("--disable-notifications")  # Chặn thông báo
    # chrome_options.add_argument("--headless")  # Chế độ không giao diện
    chrome_options.add_argument("--disable-gpu")  # Vô hiệu hóa GPU khi chạy headless
    chrome_options.add_argument("--window-size=1920x1080")  # Thiết lập kích thước cửa sổ
    driver = webdriver.Chrome(service=service, options=chrome_options)

    # Mở trang web
    base_page = BasePage(driver)
    accounts_filename = "data/account.json"  # Đọc dữ liệu tài khoản từ file account.json
    output_file = "data/facebook_posts.json"
    data_filename = "data/data.json"
    
    # Đọc dữ liệu tài khoản từ account.json
    with open(accounts_filename, 'r') as file:
        accounts_data = json.load(file)
            
    with open(data_filename, 'r') as data_file:
        data = json.load(data_file)

    driver.maximize_window()

    try:
        # Đăng nhập vào Facebook một lần
        facebook_account = data.get("account_facebook", {})
        email_facebook = facebook_account["email"]
        password_facebook = facebook_account["password"]

        driver.get(config.FACEBOOK_URL)
        base_page.login_facebook(email_facebook, password_facebook)
        time.sleep(20)
        print("Đăng nhập thành công vào Facebook.")

        # Chia danh sách tài khoản thành các nhóm 10 page
        accounts_list = list(accounts_data.items())  # Chuyển dict thành list để xử lý
        group_size = 10  # Số page trong mỗi nhóm
        total_groups = (len(accounts_list) + group_size - 1) // group_size  # Số nhóm (làm tròn lên)

        for group_idx in range(total_groups):
            # Lấy nhóm tài khoản hiện tại (10 page hoặc ít hơn nếu là nhóm cuối)
            start_idx = group_idx * group_size
            end_idx = min(start_idx + group_size, len(accounts_list))
            current_group = accounts_list[start_idx:end_idx]

            print(f"\nĐang xử lý nhóm {group_idx + 1}/{total_groups} với {len(current_group)} page.")

            # Tính thời gian chờ ngẫu nhiên giữa các bài đăng trong 15 phút (900 giây)
            total_time = 600  # 15 phút = 900 giây
            num_posts_in_group = len(current_group)  # Số page trong nhóm hiện tại
            if num_posts_in_group > 1:
                avg_interval = total_time / (num_posts_in_group - 1)  # Khoảng thời gian trung bình giữa các bài đăng
            else:
                avg_interval = 0

            # Lặp qua từng tài khoản trong nhóm hiện tại
            for idx, (account_key, account_data) in enumerate(current_group):
                try:
                    print(f"\nĐang xử lý tài khoản: {account_key} (trong nhóm {group_idx + 1})")

                    # Lấy thông tin từ tài khoản (url1, url2, username, password)
                    group_url = account_data["url2"]
                    emso_username = account_data["username"]
                    emso_password = account_data["password"]
                    post_url = account_data["url1"]  # URL để đăng bài

                    # Crawl bài viết mới từ group_url
                    num_posts = 1
                    base_page.scroll_to_element_and_crawl(
                        username=emso_username,
                        password=emso_password,
                        nums_post=num_posts,
                        crawl_page=group_url,
                        post_page=post_url,
                        page=True
                    )

                    print(f"Hoàn tất xử lý tài khoản: {account_key}")

                    # Xóa thư mục media sau mỗi bài đăng
                    base_page.clear_media_folder()

                    # Tính thời gian chờ ngẫu nhiên cho bài đăng tiếp theo
                    if idx < len(current_group) - 1:  # Không chờ sau bài đăng cuối cùng trong nhóm
                        # Tạo thời gian chờ ngẫu nhiên quanh khoảng trung bình
                        random_delay = random.uniform(avg_interval * 0.5, avg_interval * 1.5)
                        print(f"Chờ {random_delay:.2f} giây trước khi đăng bài tiếp theo...")
                        time.sleep(random_delay)

                except Exception as e:
                    print(f"Đã gặp lỗi khi xử lý tài khoản {account_key}: {e}")
                    continue  # Tiếp tục với tài khoản tiếp theo nếu gặp lỗi

            # Sau khi hoàn thành một nhóm, chờ một chút trước khi chuyển sang nhóm tiếp theo (nếu có)
            if group_idx < total_groups - 1:  # Không chờ sau nhóm cuối cùng
                print(f"\nĐã hoàn tất nhóm {group_idx + 1}. Chờ 30 giây trước khi xử lý nhóm tiếp theo...")
                time.sleep(30)

        print("Đã hoàn tất xử lý tất cả các tài khoản.")

    finally:
        driver.quit()

if __name__ == "__main__":
    main()