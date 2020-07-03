from flask import Flask
from flask import request, jsonify
from alterationlogging import alterationlog
from tableman import tableman
app = Flask(__name__)

@app.route("/api/user/login", methods=['POST'])
def userlogin():
    alterationlog.info("user login called.")
    groupid = 0
    checktuple = tableman.checkuserlogin(request.json["username"], request.json["password"])
    rsp = {}
    if checktuple[0]:
        rsp["code"] = 200
        rsp["message"] = "success"
        rsp["data"] = {}
        rsp["data"]["username"] = request.json["username"]
        rsp["data"]["groupid"] = checktuple[1]
    else:
        rsp["code"] = 100001
        rsp["message"] = "authentication failed"
    return jsonify(rsp)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
