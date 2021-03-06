import pymysql
import sys
import random
import string
import time, datetime
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
  
  def updateextension(self, jsondata):
    keys = ["authorized", "preaudit", "audit", "reply"]
    for key in keys:
      if key in jsondata.keys():
        try:
          self.__sql = "SELECT stage from extension where stage='%s';" % key
          self.__cur.execute(self.__sql)
          if len(self.__cur.fetchall()) > 0:
            subseq = ""
            for item in jsondata[key].keys():
              subseq = subseq + ("%s='%s',") % (item, jsondata[key][item])
            subseq = subseq.rstrip(',')
            self.__sql = "UPDATE extension SET %s WHERE stage='%s';" % (subseq, key)
            alterationlog.info(self.__sql)
            self.__cur.execute(self.__sql)
            self.__conn.commit()
          else:
            items = ['ext1', 'ext2', 'ext3', 'ext4', 'ext5']
            subitem = "stage,"
            values = "'" + key + "',"
            for item in items:
              if item in jsondata[key].keys():
                subitem = subitem + item + ','
                values = values + "'" + jsondata[key][item] + "',"
            subitem = subitem.rstrip(',')
            values = values.rstrip(',')
            self.__sql = "INSERT INTO extension \
              (%s) \
              VALUES \
              (%s);" % \
              (subitem, values)
            alterationlog.info(self.__sql)
            self.__cur.execute(self.__sql)
            self.__conn.commit()
        except:
          return False
    return True

  def getextensionlist(self, data):
    keys = ["authorized", "preaudit", "audit", "reply"]
    self.__sql = "SELECT * from extension;"
    self.__cur.execute(self.__sql)
    res = self.__cur.fetchall()
    for index in range(0, len(res)):
      if res[index][0] in keys:
        data[res[index][0]] = {}
        for id in range(1, len(res[index])):
          if res[index][id] != None:
            data[res[index][0]]["ext%d" % id] = res[index][id]
    return True

  def getalterationlist(self, current, pagesize, data):
    alterationlog.info("get alteration list called")
    limitcnt = current * pagesize
    startcnt = (current - 1) * pagesize
    #todo：优化内存的角度，可以优化
    self.__sql = "SELECT * from alteration ORDER BY alterationid DESC limit %d;" % limitcnt
    self.__cur.execute(self.__sql)
    res = self.__cur.fetchall()
    # alterationid valid alterationname classify major createtime
    for index in range(startcnt, len(res)):
      tmp = {}
      tmp["id"] = res[index][0]
      if res[index][1] == 0:
        tmp["isvalid"] = False
      else:
        tmp["isvalid"] = True
      tmp["name"] = res[index][2]
      tmp["classify"] = res[index][3]
      tmp["domain"] = res[index][4]
      tmp["createtime"] = str(res[index][5])
      self.__sql = "SELECT status from authorized where alterid=%d;" % res[index][0]
      self.__cur.execute(self.__sql)
      if len(self.__cur.fetchall()) > 0:
        tmp["authorized"] = self.__cur.fetchall()[0][0]
      self.__sql = "SELECT status from preaudit where alterid=%d;" % res[index][0]
      self.__cur.execute(self.__sql)
      if len(self.__cur.fetchall()) > 0:
        tmp["preaudit"] = self.__cur.fetchall()[0][0]
      self.__sql = "SELECT status from audit where alterid=%d;" % res[index][0]
      self.__cur.execute(self.__sql)
      if len(self.__cur.fetchall()) > 0:
        tmp["audit"] = self.__cur.fetchall()[0][0]
      data.append(tmp)
    return True

  def alterationcnt(self):
    alterationlog.info("alteration count called")
    self.__sql = "SELECT COUNT(*) FROM alteration;"
    self.__cur.execute(self.__sql)
    return self.__cur.fetchall()[0][0]
  
  def getnewid(self):
    id = int(time.time())
    while True:
      self.__sql = "SELECT alterationid from alteration where alterationid=%d;" % id
      self.__cur.execute(self.__sql)
      if 0 == len(self.__cur.fetchall()):
        break
      id = id + 1
    return id
  
  # return (true/false, alterationid)
  def addnewalteration(self, kvmap):
    alterationlog.info("add alteration called")
    required = ["valid", "alterationname", "classify", "major"]
    for key in required:
      if key not in kvmap.keys():
        return (False, 0)
    id = self.getnewid()
    try:
      self.__sql = "INSERT INTO alteration \
            (alterationid, valid, alterationname, classify, major) \
            VALUES \
            (%d, %r, %s, %d, %d);" % \
            (id, kvmap["valid"], repr(kvmap["alterationname"]), kvmap["classify"], kvmap["major"])
      alterationlog.info(self.__sql)
      self.__cur.execute(self.__sql)
      self.__conn.commit()
    except:
      alterationlog.info("add alteration %s failed" % kvmap["alterationname"])
      return (False, 0)
    return (True, id)
  
  def checkuserlogin(self, name, passwd):
    alterationlog.info("userlogin call [%s, %s]" % (name, passwd))
    self.__sql = "SELECT passwd,groupid from userinfo where user=%s;" % (repr(name))
    self.__cur.execute(self.__sql)
    passwdtuple = self.__cur.fetchall()
    if 0 == len(passwdtuple):
      return (False, 0)
    alterationlog.info(passwdtuple[0][0])
    alterationlog.info(passwdtuple[0][1])
    if passwd != passwdtuple[0][0]:
      return (False, 0)
    groupid = passwdtuple[0][1]
    return (True, groupid)

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