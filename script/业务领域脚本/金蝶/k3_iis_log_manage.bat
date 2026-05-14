@REM 功能：每天将金蝶的iis日志迁移到E盘的指定目录：  E:\k3_c_inetpub
@REM 在任务计划中实现每天运行。
@REM 此脚本存放路径：  E:\k3_c_inetpub
@REM bat文件编码必须是utf8带bom的格式

@echo off
chcp 65001 >nul
set logfile="E:\k3_c_inetpub\k3_iis_log_manage.log"

call :write_log_simple "start ..." "%logfile%"
call :write_log_simple "move file to volumn e ..." "%logfile%"
call :MoveFilesByDays "C:\inetpub\logs\LogFiles\W3SVC1" "E:\k3_c_inetpub\logs\LogFiles\W3SVC1" 4
call :MoveFilesByDays "C:\inetpub\logs\LogFiles\W3SVC2" "E:\k3_c_inetpub\logs\LogFiles\W3SVC2" 4

call :write_log_simple "delete old file in volumn e ..." "%logfile%"
call :remove_old_file "E:\k3_c_inetpub\logs\LogFiles\W3SVC1" 360
call :remove_old_file "E:\k3_c_inetpub\logs\LogFiles\W3SVC2" 360
call :write_log_simple "all done ..." "%logfile%"

pause

@REM ===========================================================
@REM  函数：MoveFilesByDays
@REM  功能：将源目录下 N 天前的文件移动到目标目录
@REM  参数：
@REM    %1 = 源目录
@REM    %2 = 目标目录
@REM    %3 = 天数（负数表示早于 N 天）
@REM    %4 = 文件掩码（可选，默认 *.*）
@REM ===========================================================
:MoveFilesByDays
setlocal

set "source_dir=%~1"
set "target_dir=%~2"
set "days=-%~3"
set "mask=%~4"

if not defined mask set "mask=*.*"

@REM  检查源目录是否存在
if not exist "%source_dir%" (
    echo error: source dir not exists: %source_dir%
    endlocal
    exit /b 1
)

@REM  创建目标目录
if not exist "%target_dir%" (
    mkdir "%target_dir%" 2>nul
    if exist "%target_dir%" (
        echo 创建目录: %target_dir%
    ) else (
        echo cannot create target dir: %target_dir%
        endlocal
        exit /b 1
    )
)

@REM  执行迁移
echo moving %source_dir%  %days% days before [%mask%] files...
forfiles /p "%source_dir%" /m "%mask%" /d %days% /c "cmd /c move @path \"%target_dir%\\"" 

@REM  结束方法
endlocal
goto :eof






@REM ===========================================================
@REM  函数：remove_old_file
@REM  功能：将目录下 N 天前的文件删除
@REM  参数：
@REM    %1 = 目录
@REM    %2 = 天数（负数表示早于 N 天）
@REM    %3 = 文件掩码（可选，默认 *.*）
@REM ===========================================================
:remove_old_file
setlocal

set "target_dir=%~1"
set "days=-%~2"
set "mask=%~3"
if not defined mask set "mask=*.*"
echo "delete files in %target_dir% ..." 
forfiles /p "%target_dir%" /s /m *.* /d %days% /c "cmd /c del @path"
@REM  结束方法
endlocal
goto :eof




:write_log_simple
@REM 功能：将消息写入指定文件，会自动补充当前时间
@REM 调用方法: call :write_log_simple "消息内容" "日志文件路径"
@REM "msg=%~1" 这个语法会将最外面的双引号去掉
set "current_time=%date% %time%"
set "msg=%~1"
set "logfile=%~2"

if not exist "%logfile%" (
    type nul > "%logfile%"
)

echo %current_time% %msg% >> "%logfile%"

endlocal
goto :eof