from flask import Flask
from flask import request, jsonify
from alterationlogging import alterationlog
from tableman import tableman
app = Flask(__name__)

@app.route("/api/user/login", methods=['POST'])
def userlogin():
    alterationlog.info("user login called.")
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

@app.route("/api/alteration/add", methods=['POST'])
def addalteration():
    alterationlog.info("alteration add.")
    required = ["name", "validity", "classify", "major"]
    succ = True
    for key in required:
        if key not in request.json.keys():
            succ = False
            break
    rsp = {}
    if succ:
        req = {}
        req["valid"] = request.json["validity"]
        req["alterationname"] = request.json["name"]
        req["classify"] = request.json["classify"]
        req["major"] = request.json["major"]
        checktuple = tableman.addnewalteration(req)
        if checktuple[0]:
            rsp["code"] = 200
            rsp["message"] = "success"
            rsp["data"] = {}
            rsp["data"]["id"] = checktuple[1]
            rsp["data"]["name"] = request.json["name"]
            return jsonify(rsp)
    rsp["code"] = 100003
    rsp["message"] = "add alteration failed"
    rsp["data"] = {}
    return jsonify(rsp)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
