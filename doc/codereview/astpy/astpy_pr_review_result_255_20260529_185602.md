# PR 代码评审报告

- **PR**: [#255](https://github.com/luke-axt/astpy/pull/255)
- **评审时间**: 2026-05-29 18:56:02
- **变更文件数**: 4
- **变更行数**: +82 / -191

---

## 🔴 高危（必须修复）

### 1. 移除空响应校验导致 `json.loads` 崩溃
- **位置**: `CoreBussiness/LingXingService.py:679`（删除行）
- **问题**: PR 删除了对 `api_res.get_data()` 为 `None` 或空字符串的校验，随后直接执行 `json.loads(api_res.get_data())`。若领星接口返回空 body 或网络异常导致数据为空，`json.loads` 将抛出 `TypeError` 或 `json.JSONDecodeError`，使整个任务异常终止而非返回结构化的错误结果。
- **影响**: 生产环境任务偶发崩溃，无法被外层重试或告警机制正确捕获。
- **修复方案**: 恢复空值判断，或在外层添加 `try...except (TypeError, json.JSONDecodeError)` 并返回 `ResultObj.error`。

### 2. 清空历史数据的条件误用最后一页变量
- **位置**: `rpa/lingxing/LxParseMskuJob.py:673`
- **问题**: `ImportLxPlatformMapDataUnmatch` 在分页采集结束后，使用 `if len(res_dict_data) > 0:` 判断是否清空 `astdc.lx_sku_platform_unmatch` 表。但 `res_dict_data` 是循环体内变量，循环正常退出时它必然为空列表（`while` 循环的终止条件），因此该条件恒为假，历史数据永远不会被删除。
- **影响**: 新采集的数据会重复追加到旧数据之上，导致 `lx_sku_platform_unmatch` 表数据膨胀、重复，下游配对逻辑处理大量脏数据。
- **修复方案**: 将判断条件恢复为 `if len(import_data_list) > 0:`。

---

## 🟠 严重（推荐修复）

本次 PR 未识别到严重级别问题。

---

## 🟡 一般（建议修复）

### 3. 大量方法删除，需确认无外部引用
- **位置**: `rpa/lingxing/LxMskuMapJob.py`（删除 `pair_lx_sku_bundled_multi_platform`、`send_error_msg`、`select_unmatch_lx_local_info`、`select_pair_lx_ebay_combination_sku`、`select_lx_sku_ebay_multi_sku_map` 等）
- **问题**: 上述方法被直接删除。若调度框架、反射调用或兄弟模块仍通过字符串/配置引用这些方法，将在运行时抛出 `AttributeError`。
- **影响**: 潜在的生产环境运行时异常。
- **修复方案**: 全局搜索（含配置文件、调度表、字符串常量）确认这些方法无外部引用后再删除。

### 4. 每次运行全量清空解析失败日志
- **位置**: `rpa/lingxing/LxParseMskuJob.py:227`
- **问题**: 新增 `delete from astdc.lx_bundled_prod_parse_fail_log where 1=1`，在每次插入前无条件清空整张表。
- **影响**: 历史解析失败记录完全丢失，无法追溯趋势或做根因分析。
- **修复方案**: 确认业务是否仅需保留最近一次失败记录；若需历史数据，建议改为逻辑删除（增加 `batch_id` / `create_time` 分区）或按时间清理。

### 5. `req_time_sequence` 参数值被修改
- **位置**: `rpa/lingxing/LxParseMskuJob.py:620`
- **问题**: URL 中的 `req_time_sequence` 从 `$$13` 改为 `$$2`。该参数语义不明，部分内部接口可能将其用于请求签名、序列校验或防重放。
- **影响**: 若接口对 `req_time_sequence` 有校验规则，随意变更可能导致请求被拒或触发风控。
- **修复方案**: 确认该参数在领星内部的生成规则；如为动态签名，应使用正确算法实时生成。

### 6. `qty` 转换未处理非数字异常
- **位置**: `rpa/lingxing/LxParseMskuJob.py:448`
- **问题**: `qty = int(t_data[1])` 未包裹异常处理。当 `sku*qty` 片段中 `qty` 为非数字字符串（如 `sku*abc`）时，将抛出未捕获的 `ValueError`。
- **影响**: 单条脏数据导致整个解析任务崩溃。
- **修复方案**: 添加 `try: qty = int(t_data[1]) except ValueError: return ResultObj.error(ResultObj.INVALID_INPUT, f"数量格式错误: {item}")`。

### 7. 移除按店铺分批拉取逻辑
- **位置**: `rpa/lingxing/LxParseMskuJob.py:630-673`
- **问题**: `ImportLxPlatformMapDataUnmatch` 从“按店铺分批请求”简化为“不分店铺全量请求”。若接口在无 `store_id[]` 参数时仅返回默认/部分店铺数据，或接口对全量查询有更严格的限流/超时策略，将导致数据缺失或任务失败。
- **影响**: 数据采集不完整或频繁触发限流。
- **修复方案**: 在测试环境验证无店铺参数时的接口行为（返回数据量、是否全量、限流阈值），确认安全后再上线。

### 8. 缺少测试覆盖
- **位置**: 全部变更
- **问题**: PR 未包含任何单元测试或集成测试的新增/修改。本次涉及 SKU 解析格式校验、去重逻辑、大小写匹配修正等核心业务逻辑。
- **影响**: 无法通过自动化测试保障后续回归安全。
- **修复方案**: 为核心解析逻辑（如 `parse_sku_qty` 的 `sku*qty*beishu` 格式校验、`parsed_msku_set` 去重逻辑）补充单元测试。

---

## 🟢 优化（可选）

### 9. 新增凭据需同步密钥与文档
- **位置**: `admin/service/adminconfig.py:150-152`
- **问题**: 新增 `pair_rpa_usr` / `pair_rpa_pw`，密文格式符合项目现有 Fernet 加密惯例。
- **影响**: 若加解密使用的密钥与加密时不一致，运行时解密会失败。
- **修复方案**: 确认部署环境的 Fernet 密钥与密文匹配，并同步更新运维配置文档。

### 10. 循环内逐条 UPDATE 可改为批量
- **位置**: `rpa/lingxing/LxMskuMapJob.py:101-115`
- **问题**: 大小写匹配分支中，对 `lx_bundled_prod_create_log` 和 `lx_bundled_prod_parse` 逐条执行单条 `UPDATE`。
- **影响**: 若存在大量大小写不一致记录，数据库往返次数多，性能较差。
- **修复方案**: 收集待更新数据后，使用 `CASE WHEN` 批量更新或 `REPLACE INTO` 减少 IO。

### 11. 重复 SKU 跳过时缺少日志
- **位置**: `rpa/lingxing/LxParseMskuJob.py:267-270`
- **问题**: `parsed_msku_set` 去重逻辑中，重复记录被直接 `continue`，无任何日志输出。
- **影响**: 排查数据缺失问题时难以定位是否被去重逻辑静默丢弃。
- **修复方案**: 在 `continue` 前增加 `self.logger.debug(f"跳过重复平台msku: {msku}, platform: {platform_code}")`。

### 12. 返回值变更需确认调用方兼容
- **位置**: `rpa/lingxing/LxParseMskuJob.py:679`
- **问题**: `ImportLxPlatformMapDataUnmatch.action` 的返回值从 `ResultObj.success(import_data_list)` 改为 `ResultObj.success()`。
- **影响**: 若调度器或其他 Job 依赖返回列表的长度或内容进行后续判断（如空数据跳过），可能产生兼容性问题。
- **修复方案**: 全局搜索确认无调用方依赖该返回值。

---

## 评审结论

**❌ 不允许合并**

本次 PR 存在 **2 项高危问题（🔴）**，分别可能导致：
1. 接口空响应时任务异常崩溃；
2. 采集数据重复插入，造成脏数据膨胀。

这两项问题逻辑清晰、影响明确，必须在修复后重新提交审查。此外建议处理 `🟡` 级别的问题（尤其是方法删除的外部引用确认、全量删表的历史数据保留、以及 `qty` 的非数字异常处理），以提升代码健壮性。
