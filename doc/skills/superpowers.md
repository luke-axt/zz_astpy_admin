# 安装 Claude Code Superpower 插件
claude
/plugin install superpowers@claude-plugins-official

重启即可。

# 使用说明
目前网上提供的配置方案都不行。
所以本机就在C:\Users\luke\.claude\CLAUDE.md 配置了全局的默认工作流。
在实际应用中，可以在任务开头直接说"用 brainstorming skill" 或 "按 superpowers 流程走"，我就会调用对应的 Skill 工具。



# superpowers是一个plugin还是skills？

● 两者都是，但有层级关系：

  1. Plugin（插件）：superpowers@claude-plugins-official
    - 这是你在 settings.json 里启用的插件包
    - 相当于一个"技能合集"
  2. Skills（技能）：插件内部提供的具体能力
    - 如 brainstorming、writing-plans、test-driven-development、verification-before-completion 等
    - 每个 skill 都是一段专门的系统提示，指导我如何工作

  关系：Plugin 是容器，Skills 是容器里的工具。

  所以你之前看到的 /set superpowers ... 命令，应该是这个插件提供的快捷配置方式——用来设置"默认自动激活哪些 skills"，避免每次手动调用。

  这也解释了为什么直接往 settings.json 里写 superpowers 字段会报验证错误：那不是 Claude Code 核心配置，而是这个插件自己的功能。



# 永久配置 Claude Code Superpower 最佳默认配置（此方法在此版本的claude无效）
## 1. 全局默认开启（最通用）
打开配置文件
```bash
claude config edit
```
粘贴写入：
```yaml
superpowers:
  - brainstorming
  - writing-plans
  - executing-plans
  - verification-before-completion
```
保存退出即可**永久生效**

## 2. 临时切换用法
- 写小脚本快速写代码
```
/set superpowers none
```
- 修bug专用
```
/set superpowers systematic-debugging,verification-before-completion
```
- 严谨开发带测试
```
/set superpowers brainstorming,writing-plans,executing-plans,test-driven-development,verification-before-completion
```

## 3. 查看当前生效技能
```
/config
```
搞定，以后默认就是最稳开发流程！



# superpowers 是否真的有用？
直白结论：**真有用，但分场景，不是万能神药**
## 一、什么时候超级好用（强烈推荐开）
1. **写复杂业务、后端、项目重构**
   强制先想清楚再动手，不会写一半推翻重写，**大幅减少返工**。
2. **写容易出bug的逻辑（支付、权限、正则、接口）**
   自带自检、流程校验，粗心错误直接变少。
3. **需求模糊、你没想明白怎么做**
   它会主动提问补全需求，比瞎写效率高太多。
4. **长期项目、规范开发**
   代码结构统一，后续回看、改代码更舒服。

## 二、什么时候**反而拖累、变慢**（直接关掉）
1. **写小脚本、单行代码、临时调试**
   还要走流程、写计划，**纯浪费时间**。
2. **改一行代码、修小bug**
   流程太重，越用越烦。
3. **赶速度、快速验证想法**
   直接 `none` 最快。

## 三、真实优缺点
### 优点
- 降低**思路混乱**
- 减少**写完不对、来回改**
- 代码更严谨，少低级错误
- 新人/思路乱的时候最救命

### 缺点
- **增加对话轮次，变慢**
- 简单任务过度正式
- 占用上下文，长会话更容易超限

## 四、最实用实战结论
1. **日常主力默认开：4件套**
 brainstorming,writing-plans,executing-plans,verification-before-completion
2. **写小东西 / 快速调试：立刻关 none**
3. **严肃项目上线级：再加 test-driven-development**
4. **纯排错：只开 systematic-debugging**

## 五、一句话总结
**思路乱、项目大 → 必开，提升巨大**
**思路清、代码小 → 关掉，速度最快**
它不是变强，是**帮你稳住心态和开发节奏**。

