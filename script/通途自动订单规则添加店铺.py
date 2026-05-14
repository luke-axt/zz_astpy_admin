import argparse
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import openpyxl
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


DEFAULT_EXCEL_PATH = r"D:\data\eBay配置通途订单规则的店铺清单.xlsx"
DEFAULT_DRIVER_PATH = r"D:\data\chromedriver.exe"
DEFAULT_URL = "https://tuyao.tongtool.com/myaccount/orderrule/index.htm"
DEFAULT_USER_DATA_DIR = r"D:\data\chromedata\tongtool_order_rule"
DEFAULT_WAIT_SECONDS = 15


@dataclass
class ShopResult:
    shop_short_name: str
    keyword: str
    success: bool
    message: str = ""


class TongtoolOrderRuleShopSelector:
    def __init__(self, driver: webdriver.Chrome, wait_seconds: int = DEFAULT_WAIT_SECONDS, action_delay: float = 1.0):
        self.driver = driver
        self.wait = WebDriverWait(driver, wait_seconds)
        self.action_delay = max(0.2, float(action_delay))

    def select_shops(self, shop_short_names: List[str]) -> List[ShopResult]:
        results: List[ShopResult] = []
        for index, shop_short_name in enumerate(shop_short_names, start=1):
            keyword = build_search_keyword(shop_short_name)
            print(f"\n[{index}/{len(shop_short_names)}] 处理店铺简称：{shop_short_name}，搜索：{keyword}")
            try:
                self.search_account(keyword)
                checkbox = self.find_account_checkbox(keyword)
                already_checked = self.is_checked(checkbox)
                if not already_checked:
                    self.safe_click(checkbox)
                    self.pause(0.4)
                if not self.is_checked(checkbox):
                    raise RuntimeError("点击后复选框仍未选中")
                msg = "已选中" if already_checked else "勾选成功"
                print(f"[OK] {shop_short_name}：{msg}")
                results.append(ShopResult(shop_short_name, keyword, True, msg))
            except Exception as exc:  # noqa: BLE001
                message = str(exc)
                print(f"[FAILED] {shop_short_name}：{message}")
                results.append(ShopResult(shop_short_name, keyword, False, message))
        return results

    def search_account(self, keyword: str) -> None:
        search_input = self.find_search_input()
        self.clear_and_type(search_input, keyword)

        clicked = self.try_click_first(
            [
                (By.XPATH, "//button[normalize-space()='搜索']"),
                (By.XPATH, "//span[normalize-space()='搜索']/ancestor::button[1]"),
                (By.XPATH, "//button[normalize-space()='查询']"),
                (By.XPATH, "//span[normalize-space()='查询']/ancestor::button[1]"),
                (By.XPATH, "//input[@type='button' and (@value='搜索' or @value='查询')]"),
                (By.XPATH, "//a[normalize-space()='搜索' or normalize-space()='查询']"),
            ]
        )
        if not clicked:
            search_input.send_keys(Keys.ENTER)

        self.pause(1.0)
        self.wait_until_text_or_checkbox_present(keyword, timeout_seconds=10)

    def find_search_input(self):
        selectors = [
            (By.XPATH, "//input[contains(@placeholder,'帐号') and not(@disabled)]"),
            (By.XPATH, "//input[contains(@placeholder,'账号') and not(@disabled)]"),
            (By.XPATH, "//input[contains(@placeholder,'店铺') and not(@disabled)]"),
            (By.XPATH, "//input[contains(@placeholder,'eBay') and not(@disabled)]"),
            (By.XPATH, "//input[contains(@placeholder,'搜索') and not(@disabled)]"),
            (By.XPATH, "//input[contains(@placeholder,'关键字') and not(@disabled)]"),
            (By.XPATH, "//input[contains(@name,'account') and not(@disabled)]"),
            (By.XPATH, "//input[contains(@id,'account') and not(@disabled)]"),
            (By.XPATH, "//input[contains(@name,'seller') and not(@disabled)]"),
            (By.XPATH, "//input[contains(@id,'seller') and not(@disabled)]"),
            (By.XPATH, "//input[contains(@name,'shop') and not(@disabled)]"),
            (By.XPATH, "//input[contains(@id,'shop') and not(@disabled)]"),
            (By.XPATH, "//input[@type='text' and not(@disabled) and not(@readonly)]"),
            (By.XPATH, "//input[not(@type) and not(@disabled) and not(@readonly)]"),
        ]
        elements = self.find_all_visible(selectors)
        editable = [element for element in elements if self.is_editable_input(element)]
        if not editable:
            raise RuntimeError("未找到可输入的搜索框，请确认已进入订单规则店铺选择页面")

        # 通途旧页面常有多个输入框，优先选择更像“账号/店铺搜索”的输入框。
        editable.sort(key=self.search_input_score, reverse=True)
        return editable[0]

    def find_account_checkbox(self, keyword: str):
        escaped_keyword = xpath_text_literal(keyword)
        selectors = [
            (
                By.XPATH,
                f"//input[@type='checkbox' and @name='ebayAccountIdebay' "
                f"and (following-sibling::span[contains(normalize-space(.), {escaped_keyword})] "
                f"or parent::*[contains(normalize-space(.), {escaped_keyword})])]",
            ),
            (
                By.XPATH,
                f"//*[contains(normalize-space(.), {escaped_keyword})]"
                f"/preceding-sibling::input[@type='checkbox'][1]",
            ),
            (
                By.XPATH,
                f"//*[contains(normalize-space(.), {escaped_keyword})]"
                f"/ancestor::*[self::label or self::span or self::div][1]//input[@type='checkbox'][1]",
            ),
        ]

        checkbox = self.find_first_existing(selectors)
        if checkbox is not None:
            self.scroll_into_view(checkbox)
            return checkbox

        # 如果页面列表是滚动区域，逐段滚动后再找一次。
        for container in self.find_scroll_containers():
            if self.scan_container_for_checkbox(container, selectors):
                checkbox = self.find_first_existing(selectors)
                if checkbox is not None:
                    self.scroll_into_view(checkbox)
                    return checkbox

        samples = self.get_visible_account_samples()
        raise RuntimeError(f"未找到包含“{keyword}”的 eBay 帐号复选框。当前可见样例：{samples}")

    def wait_until_text_or_checkbox_present(self, keyword: str, timeout_seconds: int) -> None:
        escaped_keyword = xpath_text_literal(keyword)
        xpath = (
            f"//*[contains(normalize-space(.), {escaped_keyword})] | "
            f"//input[@type='checkbox' and @name='ebayAccountIdebay']"
        )
        try:
            WebDriverWait(self.driver, timeout_seconds).until(
                lambda driver: any(element.is_displayed() for element in driver.find_elements(By.XPATH, xpath))
            )
        except TimeoutException:
            # 搜索结果为空时这里不立即失败，后续按明确目标再报错。
            pass

    @staticmethod
    def is_checked(checkbox) -> bool:
        checked_attr = (checkbox.get_attribute("checked") or "").strip().lower()
        return checkbox.is_selected() or checked_attr in {"checked", "true", "1"}

    def safe_click(self, element) -> None:
        self.scroll_into_view(element)
        try:
            self.wait.until(lambda _driver: element.is_displayed() and element.is_enabled())
            ActionChains(self.driver).move_to_element(element).pause(0.1).click(element).perform()
            return
        except Exception:  # noqa: BLE001
            pass
        try:
            element.click()
            return
        except Exception:  # noqa: BLE001
            pass
        self.driver.execute_script("arguments[0].click();", element)

    def clear_and_type(self, element, text: str) -> None:
        self.safe_click(element)
        try:
            element.clear()
        except Exception:  # noqa: BLE001
            pass
        element.send_keys(Keys.CONTROL, "a")
        element.send_keys(Keys.BACKSPACE)
        element.send_keys(text)

    def try_click_first(self, selectors: List[Tuple[str, str]]) -> bool:
        element = self.find_first_visible(selectors)
        if element is None:
            return False
        self.safe_click(element)
        return True

    def find_first_visible(self, selectors: List[Tuple[str, str]]):
        for by, locator in selectors:
            for element in self.driver.find_elements(by, locator):
                if element.is_displayed():
                    return element
        return None

    def find_first_existing(self, selectors: List[Tuple[str, str]]):
        for by, locator in selectors:
            elements = self.driver.find_elements(by, locator)
            if elements:
                return elements[0]
        return None

    def find_all_visible(self, selectors: List[Tuple[str, str]]):
        visible = []
        seen = set()
        for by, locator in selectors:
            for element in self.driver.find_elements(by, locator):
                if element.id in seen:
                    continue
                seen.add(element.id)
                try:
                    if element.is_displayed():
                        visible.append(element)
                except Exception:  # noqa: BLE001
                    continue
        return visible

    def find_scroll_containers(self):
        candidates = self.driver.find_elements(
            By.XPATH,
            "//*[self::div or self::td or self::ul][contains(@style,'overflow') "
            "or contains(@class,'scroll') or contains(@class,'list') or contains(@class,'table')]",
        )
        containers = []
        for element in candidates:
            try:
                if not element.is_displayed():
                    continue
                scroll_height = int(self.driver.execute_script("return arguments[0].scrollHeight || 0;", element))
                client_height = int(self.driver.execute_script("return arguments[0].clientHeight || 0;", element))
                if scroll_height > client_height > 0:
                    containers.append(element)
            except Exception:  # noqa: BLE001
                continue
        return containers

    def scan_container_for_checkbox(self, container, selectors: List[Tuple[str, str]]) -> bool:
        try:
            scroll_height = int(self.driver.execute_script("return arguments[0].scrollHeight || 0;", container))
            client_height = int(self.driver.execute_script("return arguments[0].clientHeight || 0;", container))
        except Exception:  # noqa: BLE001
            return False

        step = max(120, int(client_height * 0.8))
        for scroll_top in range(0, scroll_height + step, step):
            self.driver.execute_script("arguments[0].scrollTop = arguments[1];", container, scroll_top)
            self.pause(0.25)
            if self.find_first_existing(selectors) is not None:
                return True
        return False

    def get_visible_account_samples(self, max_items: int = 10) -> List[str]:
        samples: List[str] = []
        spans = self.driver.find_elements(
            By.XPATH,
            "//input[@type='checkbox' and @name='ebayAccountIdebay']/following-sibling::span[1]",
        )
        for span in spans:
            try:
                if not span.is_displayed():
                    continue
                text = re.sub(r"\s+", " ", span.text or "").strip()
                if text:
                    samples.append(text)
            except Exception:  # noqa: BLE001
                continue
            if len(samples) >= max_items:
                break
        return samples

    def scroll_into_view(self, element) -> None:
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            self.pause(0.2)
        except Exception:  # noqa: BLE001
            pass

    def pause(self, seconds: float) -> None:
        time.sleep(self.action_delay * seconds)

    @staticmethod
    def is_editable_input(element) -> bool:
        if not element.is_enabled():
            return False
        readonly = (element.get_attribute("readonly") or "").strip().lower()
        if readonly in {"readonly", "true"}:
            return False
        input_type = (element.get_attribute("type") or "").strip().lower()
        return input_type not in {"hidden", "file", "submit", "button", "checkbox", "radio"}

    @staticmethod
    def search_input_score(element) -> int:
        text = " ".join(
            [
                element.get_attribute("placeholder") or "",
                element.get_attribute("name") or "",
                element.get_attribute("id") or "",
                element.get_attribute("class") or "",
            ]
        ).lower()
        score = 0
        for token in ("帐号", "账号", "account", "seller", "店铺", "shop", "ebay"):
            if token.lower() in text:
                score += 10
        for token in ("搜索", "查询", "关键字", "keyword", "search"):
            if token.lower() in text:
                score += 5
        return score


def build_search_keyword(shop_short_name: str) -> str:
    clean_name = str(shop_short_name).strip()
    if clean_name.endswith("帐号") or clean_name.endswith("账号"):
        return clean_name
    return f"{clean_name}帐号"


def parse_shop_short_names(excel_path: Path) -> List[str]:
    if not excel_path.exists():
        raise FileNotFoundError(f"Excel 文件不存在：{excel_path}")

    workbook = openpyxl.load_workbook(str(excel_path), read_only=True, data_only=True)
    sheet = workbook.active
    names: List[str] = []
    seen = set()

    for row_index, row in enumerate(sheet.iter_rows(min_row=1, values_only=True), start=1):
        value = row[0] if row else None
        if value is None:
            continue
        name = str(value).strip()
        if not name:
            continue
        if row_index == 1 and normalize_header(name) in {"店铺简称", "简称", "shopshortname", "店铺"}:
            continue
        if name in seen:
            continue
        seen.add(name)
        names.append(name)

    workbook.close()
    if not names:
        raise RuntimeError("Excel 中没有读取到店铺简称，请确认第一列有数据")
    return names


def normalize_header(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z\u4e00-\u9fff]+", "", text or "").lower()


def build_driver(chromedriver_path: str, user_data_dir: Optional[str]) -> webdriver.Chrome:
    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(f"chromedriver.exe 不存在：{chromedriver_path}")

    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--ignore-certificate-errors")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    if user_data_dir:
        Path(user_data_dir).mkdir(parents=True, exist_ok=True)
        options.add_argument(f"--user-data-dir={user_data_dir}")

    service = Service(executable_path=chromedriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver


def wait_for_order_rule_page(driver: webdriver.Chrome, timeout_seconds: int) -> bool:
    start_time = time.time()
    while time.time() - start_time < timeout_seconds:
        if is_order_rule_page_ready(driver):
            return True
        time.sleep(1)
    return False


def is_order_rule_page_ready(driver: webdriver.Chrome) -> bool:
    try:
        current_url = driver.current_url or ""
        has_url_marker = "orderrule" in current_url or "orderrule/index.htm" in current_url
        markers = [
            (By.XPATH, "//input[@type='checkbox' and @name='ebayAccountIdebay']"),
            (By.XPATH, "//*[contains(text(),'eBay') or contains(text(),'ebay')]"),
            (By.XPATH, "//input[contains(@placeholder,'帐号') or contains(@placeholder,'账号') or contains(@placeholder,'店铺')]"),
            (By.XPATH, "//button[normalize-space()='搜索' or normalize-space()='查询']"),
        ]
        has_page_marker = False
        for by, locator in markers:
            elements = driver.find_elements(by, locator)
            if any(element.is_displayed() for element in elements):
                has_page_marker = True
                break
        return has_url_marker and has_page_marker
    except Exception:  # noqa: BLE001
        return False


def xpath_text_literal(text: str) -> str:
    if "'" not in text:
        return f"'{text}'"
    if '"' not in text:
        return f'"{text}"'
    parts = text.split("'")
    return "concat(" + ", \"'\", ".join(f"'{part}'" for part in parts) + ")"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="通途订单自动规则页面批量勾选 eBay 店铺帐号。")
    parser.add_argument("--excel", default=DEFAULT_EXCEL_PATH, help="店铺简称 Excel 路径，默认读取 D:\\data 下的清单")
    parser.add_argument("--driver", default=DEFAULT_DRIVER_PATH, help="chromedriver.exe 路径")
    parser.add_argument("--url", default=DEFAULT_URL, help="通途订单规则页面地址")
    parser.add_argument("--user-data-dir", default=DEFAULT_USER_DATA_DIR, help="Chrome 用户数据目录，用于保留登录状态")
    parser.add_argument("--page-timeout", type=int, default=120, help="等待你登录并进入目标页面的秒数")
    parser.add_argument("--wait", type=int, default=DEFAULT_WAIT_SECONDS, help="Selenium 单次显式等待秒数")
    parser.add_argument("--action-delay", type=float, default=1.0, help="动作延迟倍率，页面慢时可调大，如 1.5")
    parser.add_argument("--no-final-wait", action="store_true", help="执行完成后不等待，直接关闭浏览器")
    return parser.parse_args()


def print_summary(results: List[ShopResult]) -> None:
    success = [result for result in results if result.success]
    failed = [result for result in results if not result.success]

    print("\n====== 执行完成 ======")
    print(f"成功：{len(success)}")
    print(f"失败：{len(failed)}")
    if failed:
        print("\n失败明细：")
        for result in failed:
            print(f"- {result.shop_short_name}（{result.keyword}）：{result.message}")


def main() -> None:
    args = parse_args()
    excel_path = Path(args.excel)
    shop_short_names = parse_shop_short_names(excel_path)
    print(f"Excel 已读取：{excel_path}")
    print(f"待处理店铺数：{len(shop_short_names)}")

    driver = build_driver(args.driver, args.user_data_dir)
    try:
        driver.get(args.url)
        print("\n如果系统要求登录，请在打开的 Chrome 中登录，并进入订单自动规则配置页面。")
        ready = wait_for_order_rule_page(driver, args.page_timeout)
        if not ready:
            input("还没有检测到目标页面。请手动切到订单规则店铺选择页面后，按 Enter 继续...")
            if not is_order_rule_page_ready(driver):
                print("[WARN] 未检测到典型页面标记，仍将继续执行；如失败请检查当前页面是否正确。")

        selector = TongtoolOrderRuleShopSelector(driver, wait_seconds=args.wait, action_delay=args.action_delay)
        results = selector.select_shops(shop_short_names)
        print_summary(results)
    finally:
        if args.no_final_wait:
            driver.quit()
        else:
            print("\n浏览器将在 10 秒后关闭，必要时可先查看页面状态。")
            time.sleep(10)
            driver.quit()


if __name__ == "__main__":
    main()
