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


# 查看服务器的服务
systemctl list-units --type=service --all|grep astdc

# 查看服务器的配置
systemctl cat astdc.service


# java服务启动命令：java命令
/usr/local/java/jdk1.8.0_381/bin/java -jar -Dspring.profiles.active=prod -Xms12g -Xmx12g -XX:NewRatio=2 -XX:+UseG1GC -XX:+UseCompressedOops -Dfile.encoding=UTF-8 /app/datacenter/ast.jar

# 用服务的方式启动java服务

sudo systemctl restart astdc.service

sudo systemctl start astdc.service

sudo systemctl stop astdc.service

# 关机、重启命令
sudo shutdown now

sudo reboot


# 变更记录
## 2025-06-28 配置外网服务

这个配置已经持久化了，对内网服务没有影响
修改NGINX配置：/etc/nginx/nginx.conf 并重启了nginx
\# listen       80;
\# server\_name  localhost;
listen       0.0.0.0:80;
server\_name  219.134.191.74;

修改防火墙  这个步骤是未生效的，因为服务器未启动ufw
sudo ufw allow 80/tcp

修改spring配置，这个配置看起来是无效的，就回退了
增加：address: 0.0.0.0

现在缺的就是在路由器将外网IP的80端口请求转发到内网的192.168.1.60的80端口。

## 2025-6-28

ubuntu的开机启动服务，服务的配置文件：
/etc/systemd/system/astdc.service

## 2025-06-14

## 前端打包

1.  安装npm 环境
    npm install --legacy-peer-deps
2.  执行前端打包命令

进入 D:\code\javaproject\AST\web
npm run build\:prod
打包后，代码在：D:\code\javaproject\AST\web\dist

## 后端打包

jar包 打包命令
进入 D:\code\javaproject\AST
mvn clean install -Pprod
