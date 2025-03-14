from utils.base_page import BasePage
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from utils.config import Config
from selenium.webdriver.chrome.options import Options
import time
import os
from selenium_stealth import stealth
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
    stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )
    # Mở trang web
    base_page = BasePage(driver)
    accounts_filename = "data/account_create_moment_lab.json"  # Đọc dữ liệu tài khoản từ file account.json
    
    # Đọc dữ liệu tài khoản từ account.json
    with open(accounts_filename, 'r') as file:
        accounts_data = json.load(file)

    driver.maximize_window()
    try:
        driver.get("https://www.tiktok.com/foryou?lang=vi-VN")
        time.sleep(30)
        
        nums_post = 200  # Tổng số lượng bài viết cần crawl

        # Biến đếm tổng số bài viết đã xử lý
        total_processed_posts = 0

        # Lặp qua các tài khoản
        while total_processed_posts < nums_post:
            for account_key, account_data in accounts_data.items():
                try:
                    print(f"\nĐang xử lý tài khoản: {account_key}")

                    # Lấy thông tin từ tài khoản
                    emso_username = account_data["username"]
                    emso_password = account_data["password"]

                    # Tính số bài viết cần xử lý còn lại
                    remaining_posts = nums_post - total_processed_posts
                    print(f"Số bài viết cần crawl còn lại: {remaining_posts}")

                    # Gọi hàm get_and_create_tiktok để thu thập bài viết
                    base_page.get_and_create_tiktok(
                        username=emso_username,
                        password=emso_password,
                    )

                    # Cập nhật số lượng bài viết đã xử lý sau mỗi lần đăng tải
                    total_processed_posts += 1
                    print(f"Đã xử lý {total_processed_posts}/{nums_post} bài viết")

                    # Kiểm tra nếu đã đủ số lượng bài viết thì dừng
                    if total_processed_posts >= nums_post:
                        print("Đã hoàn tất xử lý đủ số lượng bài viết")
                        break  # Thoát khỏi vòng lặp `for` và kết thúc quá trình

                    # Xóa thư mục media và làm mới trình duyệt
                    base_page.clear_media_folder()
                    driver.refresh()

                except Exception as e:
                    print(f"Đã gặp lỗi khi xử lý tài khoản {account_key}: {e}")
                    continue  # Tiếp tục với tài khoản tiếp theo nếu gặp lỗi

            # Kiểm tra nếu đủ số lượng bài viết, dừng vòng lặp ngoài
            if total_processed_posts >= nums_post:
                break

                
    finally:
        driver.quit()

if __name__ == "__main__":
    main()
