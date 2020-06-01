# DesignAlteration

### 后端部署
[Flask + Gunicorn + Nginx](https://juejin.im/entry/5b3ebfadf265da0fa8671f08)

[mysql安装](https://blog.csdn.net/weixx3/article/details/80782479)

[Gunicorn相关说明](https://lenciel.com/2013/08/why-you-need-something-like-gunicorn/)

[部署流程](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-18-04)

### 系统说明
- `OS` Ubuntu 18.04.4 LTS
- mysql Ver 14.14
  - sudo apt-get install mysql-server
  - 安装完成后，重启后mysql服务是默认启动的
  - systemctl status mysql.service查看服务状态
### 软件安装
- install nginx
  - sudo apt update
  - sudo apt install nginx (`Could not get lock /var/lib/dpkg/lock-frontend - open (11: Resource temporarily unavailable)`,出现该错误,则sudo pkill apt)
- adjusting the firewall
  - sudo ufw app list
  - sudo ufw allow 'Nginx HTTP'
  - sudo ufw status (这块目前查看，还是显示`Status: inactive`, 需要确认下是否有问题)
- python3-pip相关安装
  - sudo apt install python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools
- create python virtual environment(`确认是否必须`)
  - sudo apt install python3-venv
  - python3.6 -m venv designalterationenv
- pip env环境下安装flask & gunicorn
  - source designalterationenv/bin/activate
  - sudo ufw allow 5000
- configuring gunicorn
  - gunicorn --bind 0.0.0.0:5000 wsgi:app
  - create unix socket `nc -lU /home/designalteration.sock; chmod 007 /home/designalteration.sock` (共享文件夹路径下创建unix socket失败)
  - create systemd service unit file(refer to `designalteration.service`)
  - mv designalteration.service to `/etc/systemd/system/`
  - sudo systemctl start designalteration
  - sudo systemctl enable designalteration
- configuring nginx
  - 修改/etc/nginx/sites-available/myproject
  - sudo ln -s /etc/nginx/sites-available/myproject /etc/nginx/sites-enabled
  - sudo systemctl restart nginx
- Securing the Application(`先不考虑`)