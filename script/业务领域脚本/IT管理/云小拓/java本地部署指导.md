
# 安装java
下载安装包安装即可。
注意配置jdk的安装目录为JAVA_HOME
然后将JAVA_HOME\bin配置到path就行
要确保java -version和javac -version都正常。

# 拉取代码
git clone git@gitlab.com:ast4700514/AST.git

# 安装maven
2025-10-11 参考：https://blog.csdn.net/pan_junbiao/article/details/104264644

下载地址：https://maven.apache.org/download.cgi

解压，配置环境变量：Maven_Home 并添加bin目录到path中

设置 MAVEN_OPTS 环境变量，变量名：MAVEN_OPTS，变量值：-Xms128m -Xmx512m

设置MAVEN_OPTS环境变量不是必须的，但建议设置。因为Java默认的最大可用内存往往不能够满足Maven运行的需要，比如在项目较大时，使用Maven生成项目站点需要占用大量的内存，如果没有该配置，则很容易得到java.lang.OutOfMemeoryError。因此，一开始就配置该变量是推荐的做法。

mvn -v查看版本号

mvn help:system  # 文章说这个命令可以生成.m2目录，实际上，应该是运行mvn -v就有了，或者我之前运行mvn -V就有了.m2目录。

复制 安装目录\conf\settings.xml 文件到.m2文件夹下C:\Users\用户名\.m2\settings.xml。这是一条最佳实践。
配置本地仓库目录，避免保存在C盘
<!-- 设置本地仓库位置 -->
<localRepository>D:\maven-local-repository</localRepository>

设置仓库镜像
<!-- 配置中央仓库的镜像（改用：阿里云中央仓库镜像）-->
<mirror>        
  <id>alimaven</id>
  <name>aliyun-maven</name>
  <mirrorOf>central</mirrorOf>
  <url>http://maven.aliyun.com/nexus/content/groups/public</url>
</mirror>

# 安装金蝶jar包
mvn install:install-file -Dfile=E:\appdata\maven_repository\com\k3cloud\k3cloud-webapi-sdk8.0.5.jar -DgroupId=com.k3cloud.webapi -DartifactId=k3cloud.sdk -Dversion=8.0.5 -Dpackaging=jar

重新安装整个项目的java依赖：
进入项目根目录（有项目根pom.xml文件的目录），执行
mvn clean compile

intel J注意配置jdk：File → Project Structure


java的项目生产包的打包命令：
mvn clean install -Pprod

# 配置前端打包环境
## 安装node.js
https://nodejs.org/
下载并安装即可。
node -v
npm -v 
正常即可

配置国内镜像：
配置：npm config set registry http://mirrors.cloud.tencent.com/npm/
验证：npm config get registry  返回：http://mirrors.cloud.tencent.com/npm/

在项目前端根目录运行：npm install 安装依赖
根目录应该是有这些内容的：
package.json（关键！）
vue.config.js/vite.config.js（可选）
src/ 目录
public/ 目录

因为npm会运行ps1脚本，在powershell需要设置权限：Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

前端打包命令：
npm run build:prod

