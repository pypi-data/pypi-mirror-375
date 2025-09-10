from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import traceback
import time


class ChatGPTSeleniumAutomation:
    def __init__(
        self, username: str, password: str, driver_path: str = "msedgedriver.exe"
    ):
        """
        初始化ChatGPT自动化类(使用Edge浏览器)
        :param username: ChatGPT账号
        :param password: ChatGPT密码
        :param driver_path: EdgeDriver路径(默认当前目录msedgedriver.exe)
        """
        self.username = username
        self.password = password
        self.driver = None
        self.init_driver(driver_path)

    def init_driver(self, driver_path: str):
        """初始化Edge浏览器驱动"""
        try:
            print("正在启动Edge浏览器...")
            # 创建Edge浏览器服务
            edge_service = Service(executable_path=driver_path)

            # 创建Edge浏览器选项
            edge_options = Options()

            # 不开启headless模式(显示浏览器)
            # 禁用自动化控制特征检测
            edge_options.add_argument("--disable-blink-features=AutomationControlled")
            edge_options.add_experimental_option(
                "excludeSwitches", ["enable-logging", "enable-automation"]
            )
            edge_options.add_experimental_option("useAutomationExtension", False)

            # 添加用户代理和其他选项
            edge_options.add_argument("--start-maximized")  # 启动时最大化窗口
            edge_options.add_argument("--disable-infobars")
            edge_options.add_argument("--disable-extensions")

            # 初始化Edge WebDriver
            self.driver = webdriver.Edge(service=edge_service, options=edge_options)

            self.driver.set_page_load_timeout(100)  # 页面加载超时时间
            print("✓ Edge浏览器启动成功")
        except Exception as e:
            print(f"❌ 浏览器启动失败: {str(e)}")
            traceback.print_exc()
            raise

    def login(self) -> bool:
        """
        执行ChatGPT登录流程
        :return: 登录是否成功
        """
        print("→ 访问ChatGPT登录页面...")
        self.driver.get("https://chat.openai.com/auth/login")

        # 等待并点击登录按钮
        WebDriverWait(self.driver, 15).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "//button[contains(.,'Log in')] | //button[contains(.,'登录')]",
                )
            )
        ).click()
        print("✓ 进入登录表单页面")

        # 等待用户输入已完成登录
        _ = input(">>> 请在浏览器中完成登录操作，然后按回车键继续:")

        # 等待登录成功（检测聊天区域）
        try:
            self.textarea = WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div#prompt-textarea"))
            )
            print("✓ 登录成功，进入ChatGPT界面")
            return True
        except:
            print("❌ 登录失败，请检查账号密码或网络连接")
            return False

    def send_message(self, message: str) -> str:
        """
        向ChatGPT发送消息并获取回复
        :param message: 要发送的文本消息
        :return: ChatGPT的回复内容
        """
        try:
            # 定位输入框 (可能有不同的DOM结构)

            self.textarea.clear()
            for char in message:
                self.textarea.send_keys(char)
                time.sleep(0.03)  # 模拟人类输入速度
            print(f"→ 文本已输入: {message[:30]}...")

            # 定位发送按钮
            send_button_selector = "button#composer-submit-button"
            send_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, send_button_selector))
            )
            send_button.click()
            print("✓ 消息已发送")

            # 获取最新回复内容
            time.sleep(3)
            latest_responses = self.driver.find_elements(
                By.CSS_SELECTOR,
                "[data-message-author-role='assistant'] > div > div, [data-testid='conversation-turn']:last-child",
            )[-1].text
            time.sleep(1)
            response = self.driver.find_elements(
                By.CSS_SELECTOR,
                "[data-message-author-role='assistant'] > div > div, [data-testid='conversation-turn']:last-child",
            )[-1].text

            while latest_responses != response:
                # 使用JS获取更完整的文本内容
                latest_responses = response
                time.sleep(1)
                response = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "[data-message-author-role='assistant'] > div > div, [data-testid='conversation-turn']:last-child",
                )[-1].text
            print(response)
            return response

        except Exception as e:
            print(f"❌ 消息发送失败: {str(e)}")
            traceback.print_exc()

            # 保存当前截图以便调试
            self.driver.save_screenshot("message_error.png")
            print("→ 已保存消息错误截图: message_error.png")
            return ""

    def new_chat(self):
        """开始一个新会话"""
        try:
            new_chat_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href='/chat']"))
            )
            new_chat_btn.click()
            print("✓ 新建会话成功")
            return True
        except:
            print("⚠️ 新建会话失败")
            return False

    def clear_conversation(self):
        """清除当前会话"""
        try:
            # 点击清空按钮
            clear_btn = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "span:has(svg[aria-label='Clear chat'])")
                )
            )
            clear_btn.click()

            # 确认清空
            confirm_btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn-danger"))
            )
            confirm_btn.click()
            print("✓ 会话已清空")
            return True
        except:
            print("⚠️ 清空会话失败")
            return False

    def close(self):
        """关闭浏览器"""
        if self.driver:
            print("→ 正在关闭浏览器...")
            try:
                self.driver.quit()
                print("✓ 浏览器已关闭")
            except:
                print("⚠️ 关闭浏览器时出现错误")
            finally:
                self.driver = None


# 使用示例 =================================================================
if __name__ == "__main__":
    # 请替换为您的实际账号和密码
    USERNAME = "your_email@example.com"
    PASSWORD = "your_password_here"
    EDGE_DRIVER_PATH = r"D:\Program Files\EdgeDriver\msedgedriver.exe"  # EdgeDriver路径

    print("=== ChatGPT Selenium 自动化演示 ===")

    # 初始化自动化实例
    gpt_bot = ChatGPTSeleniumAutomation(
        username=USERNAME, password=PASSWORD, driver_path=EDGE_DRIVER_PATH
    )

    try:
        # 执行登录
        print("\n[步骤1] 登录ChatGPT")
        if gpt_bot.login():
            print("\n[步骤2] 开始对话测试")

            # 测试对话1
            response1 = gpt_bot.send_message("你好! 你能用简单的中文解释量子力学吗?")
            print("\n[ChatGPT回复1]:")
            print(response1[:300] + ("" if len(response1) <= 300 else "..."))

            # 测试对话2
            response2 = gpt_bot.send_message("量子纠缠在实际生活中有什么应用?")
            print("\n[ChatGPT回复2]:")
            print(response2[:300] + ("" if len(response2) <= 300 else "..."))

            # 开始新会话
            print("\n[步骤3] 开始新会话")
            gpt_bot.new_chat()

            # 测试对话3
            response3 = gpt_bot.send_message("Python中异步编程和同步编程有什么区别?")
            print("\n[ChatGPT回复3]:")
            print(response3[:300] + ("" if len(response3) <= 300 else "..."))

            print("\n✓ 所有测试完成")
        else:
            print("❌ 登录失败，无法继续测试")

    except KeyboardInterrupt:
        print("\n! 用户中断操作")
    except Exception as e:
        print(f"\n! 测试期间出现未处理错误: {str(e)}")
        traceback.print_exc()
    finally:
        # 确保退出浏览器
        print("\n[最后一步] 清理资源")
        gpt_bot.close()
        print("程序结束")
