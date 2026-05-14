# ========================
# Windows 系统设置脚本（兼容性增强版）
# 功能：禁用自动更新、接通电源不睡眠、5分钟自动锁屏
# 还原配置 Set-ExecutionPolicy Restricted
# 运行方式：
# 1. 确保脚本文件编码为utf8 带bom的字符集编码，直接复制脚本到notepad另存为utf8 带bom的字符集编码
# 2. 设置系统允许运行ps1脚本的命令： Set-ExecutionPolicy RemoteSigned   （Get-ExecutionPolicy  返回Restricted就是不允许，就需要运行此命令）
# 3. 为了安全，运行结束，还原配置：Set-ExecutionPolicy Restricted
# 4. 以管理员身份运行powershell，运行方法：  脚本绝对路径\脚本名.ps1
#
# 其他
# RemoteSigned 的含义：
#  允许运行本地创建的脚本（如您桌面上的 .ps1 文件）。
#  从网络下载的脚本必须有受信任的数字签名才能运行。
#  这是最常用且安全的设置。
#
# ========================

# 🔧 设置输出编码，避免乱码
$OutputEncoding = [Console]::OutputEncoding = [Text.Encoding]::UTF8

# 检查是否以管理员身份运行
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if (-not $isAdmin) {
    Write-Warning "此脚本需要管理员权限。请以管理员身份重新运行。"
    # 尝试重新启动一个管理员权限的进程
    Start-Process powershell.exe "-File `"$($MyInvocation.MyCommand.Path)`"" -Verb RunAs
    exit
}

Write-Host "正在配置系统设置..." -ForegroundColor Green


# 2. 🔌 设置接通电源时不睡眠
Write-Host "设置接通电源时不睡眠..............................................................." -ForegroundColor Yellow

#  使用 powercfg 命令获取当前电源计划 GUID（兼容性最佳）
$activeScheme = powercfg /getactivescheme
# 示例输出：电源方案 GUID: 381b4222-f694-41f0-9685-ff5bb260df2e  (平衡)
if ($activeScheme -match "([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})") {
    $guid = $matches[1]
    Write-Host "    当前电源计划 GUID: $guid" -ForegroundColor Gray
} else {
    Write-Host "    无法获取电源计划 GUID，请手动检查。" -ForegroundColor Red
    exit 1
}

# 设置“接通电源”时的睡眠时间为“从不”（值为0）
powercfg -setacvalueindex $guid SUB_SLEEP STANDBYIDLE 0
Write-Host "    接通电源时不会睡眠" -ForegroundColor Green

# 3.  设置 5 分钟后自动锁屏
Write-Host "   正在设置 5 分钟后自动锁屏..." -ForegroundColor Yellow

# 设置“接通电源”时，5分钟后关闭显示器
powercfg -setacvalueindex $guid SUB_VIDEO VIDEOIDLE 300  # 300秒 = 5分钟
Write-Host "    5分钟后关闭屏幕" -ForegroundColor Green

# 启用屏幕保护程序并设置5分钟后启动，且启动时需密码
$scrSavPath = "HKCU:\Control Panel\Desktop"
Set-ItemProperty -Path $scrSavPath -Name "ScreenSaveActive" -Value "1"
Set-ItemProperty -Path $scrSavPath -Name "ScreenSaverIsSecure" -Value "1"
Set-ItemProperty -Path $scrSavPath -Name "ScreenSaveTimeout" -Value "300"
Write-Host "    屏幕保护程序已设置为5分钟启动并需密码解锁" -ForegroundColor Green

# 应用当前电源计划
powercfg -SetActive $guid
Write-Host "    电源计划已重新激活" -ForegroundColor Green

Write-Host "所有设置已完成！................................................" -ForegroundColor Green
Write-Host "建议重启系统以确保所有设置生效。" -ForegroundColor Yellow

