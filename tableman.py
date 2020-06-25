import pymysql
import sys

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
      print("create db")
      self.__cur.execute(self.__sql)
    except:
      return False
    return True
  
  def createuserinfo(self):
    print(sys._getframe().f_code.co_name)
    return True
  def createalteration(self):
    print(sys._getframe().f_code.co_name)
    return True
  def createauthorized(self):
    print(sys._getframe().f_code.co_name)
    return True
  def createpreaudit(self):
    print(sys._getframe().f_code.co_name)
    return True
  def createaudit(self):
    print(sys._getframe().f_code.co_name)
    return True
  def createreply(self):
    print(sys._getframe().f_code.co_name)
    return True
  def createextension(self):
    print(sys._getframe().f_code.co_name)
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