# python-main

#### 介绍
python web服务，api - module - model - db

/logRefresh：是日志配置初始化接口（开发调试用的）
/configRefresh：是配置文件初始化接口，修改了项目下的conf.ini后可以调用这个接口刷新
/etl/functionCall：调用etl脚本主入口
/etl/dbpool/refresh：修改数据库链接后，用于刷新数据库连接池 
/etl/lo

#### 软件架构
软件架构说明
目录结构参照项目目录下的Readme.txt


#### 安装教程
进入到项目主目录下
1. 安装Python 3.10.16
2. pip install -r requirement.txt


#### 使用说明
1.  运行服务器，python main.py [可选参数：dev/pro，分别为开发环境和产品环境，默认dev]，对应配置信息在conf.ini中
2.   控制台会输出对应的Swagger UI界面，可在该页面上调试api
![输入图片说明](statics/imagesimage.png)
