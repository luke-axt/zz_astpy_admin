# 操作系统

## 下载ubuntu 镜像

制作启动u盘，使用rufus软件
制作usb启动盘参考链接：<http://mofazhu.com/jiaocheng/soft/39016.html>

## 安装ubuntu及配置

默认安装即可
## 配置静态IP：192.168.1.60

cd /etc/netplan/
vi 01-network-manager-all.yaml


添加以下内容：
---- eth0 这个位置主要要检查，跟ip a 保持一致，比如实际配置的是：enp5s0
ethernets:
    eth0:
      dhcp4: no
      addresses:
        - 192.168.1.60/24
      gateway4: 192.168.1.254
      nameservers:
        addresses:
          - 202.96.128.86
          - 202.96.134.133



网关：192.168.1.254
DNS设置：
202.96.128.86
202.96.134.133

## 创建应用用户

adduser appusr
usermod -aG sudo appusr
mkhomedir\_helper appusr

# 安装工具包

## 安装ssh工具

apt-get install openssh openssh-server

## 创建默认目录

mkdir -p /app
mkdir -p /appdata

## 安装java

使用root用户
mkdir -m755 /usr/local/java
解压java包
配置环境变量
vi /etc/profile
\#set java environment
\#安装目录
export JAVA\_HOME=/usr/local/java/jdk1.8.0\_341
\#下面都一样
export CLASSPATH=.:`$JAVA_HOME/lib:$`JRE\_HOME/lib:`$CLASSPATH
export PATH=$`JAVA\_HOME/bin:`$JRE_HOME/bin:$`PATH
export JRE\_HOME=\$JAVA\_HOME/jre
刷新环境变量
source /etc/profile

## 安装nginx

检查是否有nginx
ps -ef | grep nginx
安装
sudo apt-get install nginx
检查服务是否启动
ps -ef | grep nginx

卸载nginx
sudo apt-get purge nginx

## 安装redis

sudo apt-get install redis-server
检查是否安装完成
redis-cli ping
service redis status

卸载
sudo apt-get autoremove --purge redis-server

## 生产环境重启redis

配置redis需要密码
vi /etc/redis/redis.conf
requirepass Fe!2nTt31
cd /etc/init.d
./redis-server stop
./redis-server start

