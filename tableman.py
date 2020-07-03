import pymysql
import sys
import random
import string
from alterationlogging import alterationlog

class TableMan:
  def __init__(self):
    # check db & tables created
    self.__running = False
    if not self.checkconnect():
      return
    if not self.checkdb():
      return
    if not self.checktable():
      return
    self.__running = True
  
  def checkdb(self):
    self.__cur = self.__conn.cursor()
    self.__sql = "show databases;"
    self.__cur.execute(self.__sql)
    dbtuple = self.__cur.fetchall()
    for i in range(len(dbtuple)):
      if dbtuple[i][0] == "alteration":
        return True
    self.__sql = "create database alteration"
    try:
      alterationlog.info("create db")
      self.__cur.execute(self.__sql)
    except:
      return False
    return True
  
  def createuserinfo(self):
    alterationlog.info(sys._getframe().f_code.co_name)
    self.__sql = "CREATE TABLE IF NOT EXISTS `userinfo`( \
                  `user` VARCHAR(20) NOT NULL, \
                  `passwd` VARCHAR(20) NOT NULL, \
                  `groupid` INT NOT NULL DEFAULT 2, \
                  PRIMARY KEY ( `user` ) \
                )ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    self.__cur.execute(self.__sql)
    self.__sql = "SELECT COUNT(*) FROM userinfo;"
    self.__cur.execute(self.__sql)
    for i in range(1, 11):
      userid = "yg%03d" % i
      password = ''.join(random.sample(string.ascii_letters + string.digits, 8))
      group = 2
      if i < 4:
        group = 1
      self.__sql = "INSERT INTO userinfo \
            (`user`, `passwd`, `groupid`) \
            VALUES \
            (%s, %s, %d);" % (repr(userid), repr(password), group)
      self.__cur.execute(self.__sql)
    self.__conn.commit()
    return True
  def createalteration(self):
    self.__sql = "CREATE TABLE IF NOT EXISTS `alteration`( \
                  `alterationid` INT NOT NULL, \
                  `valid` BOOLEAN NOT NULL, \
                  `alterationname` VARCHAR(20) NOT NULL, \
                  `classify` INT NOT NULL, \
                  `major` INT NOT NULL, \
                  `createtime` datetime NOT NULL DEFAULT NOW(), \
                  PRIMARY KEY ( `alterationid` ) \
                )ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    self.__cur.execute(self.__sql)
    return True
  def createauthorized(self):
    self.__sql = "CREATE TABLE IF NOT EXISTS `authorized`( \
                  `status` INT NOT NULL DEFAULT 0, \
                  `cost` DECIMAL(20, 2), \
                  `clearway` INT, \
                  `alterid` INT NOT NULL, \
                  `major` INT NOT NULL, \
                  `ext1` VARCHAR(20) DEFAULT NULL, \
                  `ext2` VARCHAR(20) DEFAULT NULL, \
                  `ext3` VARCHAR(20) DEFAULT NULL, \
                  `ext4` VARCHAR(20) DEFAULT NULL, \
                  `ext5` VARCHAR(20) DEFAULT NULL, \
                  PRIMARY KEY ( `alterid` ), \
                  CONSTRAINT `foreign_alter` FOREIGN KEY (`alterid`) \
                    REFERENCES `alteration` (`alterationid`) ON DELETE CASCADE \
                    ON UPDATE CASCADE \
                  )ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    self.__cur.execute(self.__sql)
    return True
  def createpreaudit(self):
    self.__sql = "CREATE TABLE IF NOT EXISTS `preaudit`( \
                  `status` INT NOT NULL DEFAULT 0, \
                  `cost` DECIMAL(20, 2) DEFAULT NULL, \
                  `category` INT, \
                  `alterid` INT NOT NULL, \
                  `bureau` VARCHAR(20) DEFAULT NULL, \
                  `pricereportno` VARCHAR(20) DEFAULT NULL, \
                  `ext1` VARCHAR(20) DEFAULT NULL, \
                  `ext2` VARCHAR(20) DEFAULT NULL, \
                  `ext3` VARCHAR(20) DEFAULT NULL, \
                  `ext4` VARCHAR(20) DEFAULT NULL, \
                  `ext5` VARCHAR(20) DEFAULT NULL, \
                  PRIMARY KEY ( `alterid` ), \
                  CONSTRAINT `foreign_preaudit` FOREIGN KEY (`alterid`) \
                    REFERENCES `alteration` (`alterationid`) ON DELETE CASCADE \
                    ON UPDATE CASCADE \
                  )ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    self.__cur.execute(self.__sql)
    return True
  def createaudit(self):
    self.__sql = "CREATE TABLE IF NOT EXISTS `audit`( \
                  `status` INT NOT NULL DEFAULT 0, \
                  `cost` DECIMAL(20, 2), \
                  `alterid` INT NOT NULL, \
                  `replyno` VARCHAR(20), \
                  `ext1` VARCHAR(20) DEFAULT NULL, \
                  `ext2` VARCHAR(20) DEFAULT NULL, \
                  `ext3` VARCHAR(20) DEFAULT NULL, \
                  `ext4` VARCHAR(20) DEFAULT NULL, \
                  `ext5` VARCHAR(20) DEFAULT NULL, \
                  PRIMARY KEY ( `alterid` ), \
                  CONSTRAINT `foreign_audit` FOREIGN KEY (`alterid`) \
                    REFERENCES `alteration` (`alterationid`) ON DELETE CASCADE \
                    ON UPDATE CASCADE \
                  )ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    self.__cur.execute(self.__sql)
    return True
  def createreply(self):
    self.__sql = "CREATE TABLE IF NOT EXISTS `reply`( \
                  `cost` DECIMAL(20, 2), \
                  `alterid` INT NOT NULL, \
                  `src` INT NOT NULL, \
                  `ext1` VARCHAR(20) DEFAULT NULL, \
                  `ext2` VARCHAR(20) DEFAULT NULL, \
                  `ext3` VARCHAR(20) DEFAULT NULL, \
                  `ext4` VARCHAR(20) DEFAULT NULL, \
                  `ext5` VARCHAR(20) DEFAULT NULL, \
                  PRIMARY KEY ( `alterid` ), \
                  CONSTRAINT `foreign_reply` FOREIGN KEY (`alterid`) \
                    REFERENCES `alteration` (`alterationid`) ON DELETE CASCADE \
                    ON UPDATE CASCADE \
                  )ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    self.__cur.execute(self.__sql)
    return True
  def createextension(self):
    self.__sql = "CREATE TABLE IF NOT EXISTS `extension`( \
                  `stage` VARCHAR(20) NOT NULL, \
                  `ext1` VARCHAR(20) DEFAULT NULL, \
                  `ext2` VARCHAR(20) DEFAULT NULL, \
                  `ext3` VARCHAR(20) DEFAULT NULL, \
                  `ext4` VARCHAR(20) DEFAULT NULL, \
                  `ext5` VARCHAR(20) DEFAULT NULL, \
                  PRIMARY KEY ( `stage` ) \
                  )ENGINE=InnoDB DEFAULT CHARSET=utf8;"
    self.__cur.execute(self.__sql)
    return True

  def checktable(self):
    self.__sql = "use alteration;"
    self.__cur.execute(self.__sql)
    self.__sql = "show tables;"
    self.__cur.execute(self.__sql)
    #用户表，变更详情表，编制状态表，预审状态表，局审状态表，批复信息表，
    #扩展字段表（扩展字段均为text，重命名后再使用）
    target = ["userinfo", "alteration", "authorized", "preaudit", "audit", "reply", "extension"]
    tabletuple = self.__cur.fetchall()
    for i in range(len(tabletuple)):
      if tabletuple[i][0] in target:
        target.remove(tabletuple[i][0])
    if len(target) == 0:
      return True
    for i in range(len(target)):
      getattr(self, "create" + target[i])()
    return True

  def checkconnect(self):
    try:
      self.__conn = pymysql.connect(host='localhost',
                        user='root',
                        password='root')
    except:
      return False
    return True
    
    
  def running(self):
    return self.__running
tableman = TableMan()