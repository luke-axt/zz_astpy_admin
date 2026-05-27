import sys
sys.path.append(r"D:\app\astpy")

from rpa.RpaAdmin import RpaAdmin
from utils.BrowserUtils import BrowserUtils

import time
import traceback
import pandas as pd
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common.ResultObj import ResultObj



class RpaDelLxBundleProductJob(RpaAdmin):
    """
帮我在这个类中实现如下功能。你不用扫描项目，这是一个完全独立的一次性功能，只能基类有关系，其他项目目录可以不用看。
1. 数据来源：读取excel文档 D:\data\需删除捆绑产品清单.xlsx，文档只有一列，列名：bsku。
2. 要操作的url地址：https://auxito.lingxing.com/erp/bundledProductManage
4. 初始化动作
4.1 检查是否在目标页面：
检查这个元素是否存在：
<button data-v-0f3e2e2c="" type="button" data-auth="auth-button" class="el-button el-button--primary el-button--small is-round" auth="true"><span class="el-tooltip text-wrap" aria-describedby="el-tooltip-3514" tabindex="-1"> 添加捆绑产品 </span></button>

4.2 检查 页面显示行数，不是200行调整为200行。
对应的元素：
<span class="el-pagination__sizes"><div class="el-select el-select--small el-select-focus"><!----><!----><div class="el-input el-input--small el-input--prefix el-input--suffix is-focus"><!----><input type="text" readonly="readonly" autocomplete="off" placeholder="" class="el-input__inner" inelement="0"><!----><span class="el-input__prefix"><span class="fake-placeholder" style="display: none;"></span><span class="fake-select-label" style="display: none;">
        200条/页
      </span><span class="fake-placeholder fake-placeholder-hidden">200条/页</span><span class="el-input__follow">
        
      </span><!----></span><span class="el-input__suffix"><span class="el-input__suffix-inner"><!----><!----><i class="el-select__caret el-input__icon iconfont lx_arrow_down_rev"></i><!----><!----><!----><!----></span><!----></span><!----><!----></div></div></span>

该元素对应的下拉框：
<div class="el-scrollbar " style=""><div class="el-select-dropdown__wrap el-scrollbar__wrap" style="margin-bottom: -11px; margin-right: -11px;"><ul class="el-scrollbar__view el-select-dropdown__list"><!----><!----><li class="el-select-dropdown__item"><span></span><span class="checkBox" style="--color: undefined;"></span><span>
      20条/页
      <!----><!----></span></li><li class="el-select-dropdown__item hover"><span></span><span class="checkBox" style="--color: undefined;"></span><span>
      50条/页
      <!----><!----></span></li><li class="el-select-dropdown__item"><span></span><span class="checkBox" style="--color: undefined;"></span><span>
      100条/页
      <!----><!----></span></li><li class="el-select-dropdown__item selected"><span></span><span class="checkBox" style="--color: undefined;"></span><span>
      200条/页
      <!----><!----></span></li></ul></div><div class="el-scrollbar__bar is-horizontal"><div class="el-scrollbar__thumb" style="transform: translateX(0%);"></div></div><div class="el-scrollbar__bar is-vertical"><div class="el-scrollbar__thumb" style="transform: translateY(0%);"></div></div></div>
      

5. 操作动作：
5.1 从数据来源读取所有数据，将数据分成200行一个数组，逐个数组执行删除，删除动作参见5.2-5.5。
5.2 每次先检查当前页面是否有筛选条件，如有，则清空筛选条件。
无筛选条件状态：<div data-v-0f3e2e2c="" class="filter-section" style="display: contents;"><!----><!----><!----><!----><!----><span data-v-0f3e2e2c="" class="close-all iconfont lx_delete" style="display: none;"></span></div>

有筛选条件状态：<div data-v-0f3e2e2c="" class="filter-section" style="display: flex;"><!----><!----><!----><!----><!----><span data-v-0f3e2e2c="" class="el-popover-span"><span class="el-popover__reference-wrapper"><div class="tag-view el-popover__reference" aria-describedby="el-popover-1737" tabindex="0"><span class="ak-pointer ak-inline-block">SKU：HGD-accord-18-21-L_1_HGD-accord-18-21-R_1, HGD-GL550-10-12L_1_HGD-GL550-10-12R_1, HGD-Q7-16-20L_1_HGD-Q7-16-20R_1等5项</span><i class="iconfont lx_close"></i></div></span></span><span data-v-0f3e2e2c="" class="close-all iconfont lx_delete" style="display: none;"></span></div>

清空筛选条件点击这个按钮即可：<i class="iconfont lx_close"></i>

5.3 逐个数组输入sku
a. 注意每sku之间要加换行符
b. 点击展开输入框
对应元素：<span class="el-tooltip wrapper-icon ak-pointer" aria-describedby="el-tooltip-1989" tabindex="-1"><i class="advanced-input-icon iconfont lx_combo_filter"></i></span>
c. 在这个输入框输入sku
<div class="popover-textarea el-textarea el-input--small"><textarea autocomplete="off" wrap="off" placeholder="精确搜索，一行一项，最多支持200行" class="el-textarea__inner" style="resize: none; min-height: 44px;"></textarea><!----></div>
d. 点击搜索按钮
<button type="button" data-auth="auth-button" class="el-button el-button--primary el-button--mini is-plain is-round"><span class="el-tooltip text-wrap" aria-describedby="el-tooltip-9989" tabindex="-1">搜索</span></button>

5.4 等待搜索结果
等待1秒钟，检查这个元素是否是大于0且小于等于200，如果是则执行5.5，否则跳过这个数组
<span class="el-pagination__total">共6条</span>

5.5 删除动作
勾选全量sku：<span class="vxe-checkbox--icon vxe-checkbox--unchecked-icon"></span>
点击批量删除：<button data-v-0f3e2e2c="" type="button" data-auth="auth-button" class="el-button el-button--default el-button--small is-round" auth="true"><span class="el-tooltip text-wrap" aria-describedby="el-tooltip-351" tabindex="-1">批量删除</span></button>
确认批量删除：<button type="button" data-auth="auth-button" class="el-button el-button--danger el-button--small is-round"><span class="el-tooltip text-wrap" aria-describedby="el-tooltip-1737" tabindex="-1">删除
        <!----></span></button>
确认删除成功：<span class="el-pagination__total">共6条</span> 这个元素有变化就是删除成功。

6. 所有sku处理完成之后，调用这个方法wait_confirm等待我确认才能退出程序

环境信息及开发要求：
1. 我的电脑已经安装好python，selenium，chrome和chromedriver.exe(chromedriver.exe路径是D:\data\chromedriver.exe)，你在此项目的venv中执行代码即可。
2. 我授权你运行代码，使用chromedriver。
3. 你可以编写代码和测试，测试要用我看得见的方式，不能使用视觉的浏览器。
4. 在action后面继续补全代码即可，运行代码直接实例化类，调用run方法即可。
    """
    def __init__(self, jobname):
        super().__init__(jobname)
        self.jobname = jobname

    def init_browser(self,browser):
        """
        """
        browser.get("https://auxito.lingxing.com/erp/bundledProductManage")

        # 等待 30 秒让用户完成登录
        time.sleep(30)

        wait = WebDriverWait(browser, 15)

        # 4.1 检查是否在目标页面（通过"添加捆绑产品"按钮判断）
        try:
            wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[.//span[contains(text(), '添加捆绑产品')]]")
            ))
            self.logger.info("[OK] 已确认在捆绑产品管理页面")
        except Exception:
            self.logger.info("[FAIL] 30 秒后仍未检测到目标页面，请检查登录是否成功")
            return ResultObj.error(ResultObj.EXT_SYS_ERROR, "30 秒后仍未检测到目标页面")

        # 4.2 检查分页，如果不是 200 条/页则切换
        pagination_input = browser.find_element(By.CSS_SELECTOR, ".el-pagination__sizes input")
        current_val = pagination_input.get_attribute("value") or ""
        if "200" not in current_val:
            pagination_input.click()
            time.sleep(0.5)
            option_200 = wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//li[contains(., '200条/页')]")
            ))
            option_200.click()
            time.sleep(1)
            self.logger.info("[OK] 分页已调整为 200 条/页")
        else:
            self.logger.info("[OK] 分页已经是 200 条/页")
    
    def action(self, **kwargs):
        excel_path = r"D:\data\需删除捆绑产品清单.xlsx"
        df = pd.read_excel(excel_path)
        sku_list = df['bsku'].dropna().astype(str).str.strip().tolist()
        if not sku_list:
            self.logger.info("Excel 中没有读取到有效的 bsku 数据")
            return ResultObj.error(ResultObj.EXT_SYS_ERROR, "Excel 中没有读取到有效的 bsku 数据")
        batches = [sku_list[i:i + 200] for i in range(0, len(sku_list), 200)]
        self.logger.info(f"共读取 {len(sku_list)} 个 SKU，分成 {len(batches)} 批处理")

        browser = None
        try:
            code, msg, browser = BrowserUtils.openChrome(
                chromdatapath=self.admin.getChromeUserPath(f'{self.__class__.__name__}.action')
            )
            if code != 0:
                self.logger.info(f"打开浏览器失败：{msg}")
                return ResultObj.error(ResultObj.EXT_SYS_ERROR, f"打开浏览器失败：{msg}")
            
            wait = WebDriverWait(browser, 15)
            self.init_browser(browser=browser)
            # browser.get("https://auxito.lingxing.com/erp/bundledProductManage")

            # # 等待 30 秒让用户完成登录
            # time.sleep(30)

            # wait = WebDriverWait(browser, 15)

            # # 4.1 检查是否在目标页面（通过"添加捆绑产品"按钮判断）
            # try:
            #     wait.until(EC.presence_of_element_located(
            #         (By.XPATH, "//button[.//span[contains(text(), '添加捆绑产品')]]")
            #     ))
            #     self.logger.info("[OK] 已确认在捆绑产品管理页面")
            # except Exception:
            #     self.logger.info("[FAIL] 30 秒后仍未检测到目标页面，请检查登录是否成功")
            #     return ResultObj.error(ResultObj.EXT_SYS_ERROR, "30 秒后仍未检测到目标页面")

            # # 4.2 检查分页，如果不是 200 条/页则切换
            # pagination_input = browser.find_element(By.CSS_SELECTOR, ".el-pagination__sizes input")
            # current_val = pagination_input.get_attribute("value") or ""
            # if "200" not in current_val:
            #     pagination_input.click()
            #     time.sleep(0.5)
            #     option_200 = wait.until(EC.element_to_be_clickable(
            #         (By.XPATH, "//li[contains(., '200条/页')]")
            #     ))
            #     option_200.click()
            #     time.sleep(1)
            #     self.logger.info("[OK] 分页已调整为 200 条/页")
            # else:
            #     self.logger.info("[OK] 分页已经是 200 条/页")

            success_count = 0
            fail_count = 0
            no_match_count = 0
            fail_details = []

            for batch_idx, batch in enumerate(batches, start=1):
                self.logger.info(f"[BATCH] 正在处理第 {batch_idx}/{len(batches)} 批，共 {len(batch)} 个 SKU...")
                try:
                    # 5.2 清空筛选条件
                    filter_section = browser.find_element(By.CSS_SELECTOR, ".filter-section")
                    section_style = filter_section.get_attribute("style") or ""
                    if "flex" in section_style:
                        try:
                            close_all = browser.find_element(By.CSS_SELECTOR, ".filter-section .close-all")
                            if close_all.is_displayed():
                                close_all.click()
                            else:
                                close_btns = browser.find_elements(By.CSS_SELECTOR, ".filter-section .lx_close")
                                for btn in close_btns:
                                    btn.click()
                        except Exception:
                            pass
                        WebDriverWait(browser, 5).until(
                            lambda d: "contents" in d.find_element(By.CSS_SELECTOR, ".filter-section").get_attribute("style")
                        )
                        time.sleep(0.5)

                    # 5.3 展开多行输入框并输入 SKU
                    expand_icon = browser.find_element(By.CSS_SELECTOR, ".advanced-input-icon")
                    expand_icon.click()
                    time.sleep(0.5)

                    textarea = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "textarea[placeholder*='精确搜索']")
                    ))
                    textarea.clear()
                    textarea.send_keys("\n".join(batch))
                    time.sleep(0.3)

                    # 点击搜索
                    search_btn = browser.find_element(By.XPATH, "//button[span[contains(text(), '搜索')]]")
                    search_btn.click()
                    time.sleep(1)

                    # 5.4 读取结果总数
                    total_el = wait.until(EC.presence_of_element_located(
                        (By.CSS_SELECTOR, ".el-pagination__total")
                    ))
                    total_text = total_el.text or ""
                    m = re.search(r'共(\d+)条', total_text)
                    total = int(m.group(1)) if m else 0
                    self.logger.info(f"   搜索结果：{total_text}")

                    if total <= 0 or total > 200:
                        no_match_count += 1
                        self.logger.info(f"   [WARN] 搜索结果为 {total}，不在 1-200 范围内，跳过本批")
                        continue

                    # 5.5 删除动作
                    select_all = browser.find_element(By.CSS_SELECTOR, ".vxe-checkbox--unchecked-icon")
                    select_all.click()
                    time.sleep(0.3)

                    batch_del_btn = browser.find_element(By.XPATH, "//button[.//span[contains(text(), '批量删除')]]")
                    batch_del_btn.click()
                    time.sleep(0.3)

                    confirm_del_btn = browser.find_element(
                        By.XPATH,
                        "//button[contains(@class, 'el-button--danger') and .//span[contains(text(), '删除')]]"
                    )
                    confirm_del_btn.click()

                    WebDriverWait(browser, 120).until(
                        lambda d: "共0条" in d.find_element(By.CSS_SELECTOR, ".el-pagination__total").text
                    )
                    success_count += 1
                    self.logger.info("   [OK] 删除成功")

                except Exception as e:
                    fail_count += 1
                    detail = f"第 {batch_idx} 批: {traceback.format_exc()}"
                    fail_details.append(detail)
                    self.logger.info(f"   [FAIL] {detail}")
                    browser.refresh()
                    time.sleep(10)
                    self.init_browser(browser=browser)
                    

            # 6. 汇总报告
            self.logger.info("\n" + "=" * 40)
            self.logger.info("[SUMMARY] 处理完成")
            self.logger.info(f"   成功：{success_count} 批")
            self.logger.info(f"   失败：{fail_count} 批")
            self.logger.info(f"   无匹配：{no_match_count} 批")
            if fail_details:
                self.logger.info("   失败详情：")
                for d in fail_details:
                    self.logger.info(f"      - {d}")
            self.logger.info("=" * 40)

            return ResultObj.success(
                f"处理完成：成功 {success_count} 批，失败 {fail_count} 批，无匹配 {no_match_count} 批"
            )

        finally:
            self.logger.info("\n[WAIT] 等待用户确认后关闭浏览器...")
            self.wait_confirm()
            if browser:
                try:
                    browser.quit()
                except Exception:
                    pass

    def wait_confirm(self)-> bool:
        """
        等待用户输入：
        - 直接回车 = 继续
        - 输入 Y/y + 回车 = 继续
        - 其他输入 = 退出
        """
        user_input = input("请按回车确认，或输入 Y 继续：").strip().upper()
        
        # 空（直接回车）或者 Y 都通过
        if user_input == "" or user_input == "Y":
            self.logger.info("[OK] 确认通过，继续执行...")
            return True
        else:
            self.logger.info("[FAIL] 取消执行")
            return False


if __name__ == '__main__':
    job = RpaDelLxBundleProductJob('删除领星捆绑产品')
    result = job.run()
    print(result)
