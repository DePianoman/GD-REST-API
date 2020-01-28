from flask import Flask, render_template, redirect, url_for, request, jsonify, send_from_directory
from flask_restful import Api, Resource, reqparse
from urllib.parse import unquote
import requests, base64

app = Flask(__name__, static_folder="client")
api = Api(app)

def gjpe(s):
    if(len(s) > 5):
        s2 = ""
        if(len(s) < 5):
            for i in range(len(s)):
                s2 = s2 + "37526"[i]
        elif(len(s) > 5):
            while(len(s2) < len(s)):
                s2 = s2 + "37526"
            while(len(s2) != len(s)):
                s2 = list(s2)
                s2.pop(-1)
                s2 = ''.join(s2)
        out = ''.join(chr(ord(a) ^ ord(b)) for a,b in zip(s,s2))
        out = base64.b64encode(out.encode('utf-8'))
        return out
    else:
        return "0"

def rted(s):
    s = base64.b64decode(s.encode('utf-8')).decode()
    s2 = ""
    if (len(s) < 5):
        for i in range(len(s)):
            s2 = s2 + "26364"[i]
    elif (len(s) > 5):
        while (len(s2) < len(s)):
            s2 = s2 + "26364"
        while (len(s2) != len(s)):
            s2 = list(s2)
            s2.pop(-1)
            s2 = ''.join(s2)
    out = ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(s, s2))
    return out

def xor(s, s2):
    return ''.join(chr(ord(a) ^ ord(b)) for a, b in zip(s, s2))

def get_level_pass(lid):
    payload = {'gameVersion':'21', 'binaryVersion':'35', 'gdw':'0', 'levelID': lid, 'inc': '1', 'extras': '0', 'secret':'Wmfd2893gb7'}
    f = requests.post('http://www.boomlings.com/database/downloadGJLevel22.php', data=payload).text
    return rted(f.split(':')[-1].split('#')[0])[1:] if f.split(':')[-1].split('#')[0] != "0" and f.split(':')[-1].split('#')[0] != "10" and f.split(':')[-1].split('#')[0] != "1" and f.split(':')[-1].split('#')[0] != "" and rted(f.split(':')[-1].split('#')[0])[1:] != "" else 0

def get_accid_from_user(f):
    payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "str": f, "total": "0", "page": "0", "secret": "Wmfd2893gb7"}
    x = requests.post('http://www.boomlings.com/database/getGJUsers20.php', data=payload)
    if(x.text == "-1"):
        return 0
    return x.text.split(':')[21]

def get_userid_from_user(f):
    payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "str": f, "total": "0", "page": "0", "secret": "Wmfd2893gb7"}
    x = requests.post('http://www.boomlings.com/database/getGJUsers20.php', data=payload)
    if(x.text == "-1"):
        return 0
    return x.text.split(':')[3]

def get_difficulty(f):
    if(f[11] == "50"):
        if(f[21] == "1"):
            return "Extreme Demon"
        elif(f[25] == "1"):
            return "Auto"
        else:
            return "Insane"
    elif(f[11] == "40"):
        if(f[27] == "10"):
            return "Insane Demon"
        else:
            return "Harder"
    elif(f[11] == "30"):
        if(f[27] == "10"):
            return "Hard Demon"
        else:
            return "Hard"
    elif(f[11] == "20"):
        if(f[27] == "10"):
            return "Medium Demon"
        else:
            return "Normal"
    elif(f[11] == "10"):
        if(f[27] == "10"):
            return "Easy Demon"
        else:
            return "Easy"
    else:
        return "N/A"

def get_newgrounds_song(id):
    x = requests.get("https://www.newgrounds.com/audio/listen/{}".format(id)).text
    out = []
    out.append(x.split('title>')[1].split("</")[0])
    out.append(x.split('"item-details-main"')[1].split("</a")[0].split(">")[-1])
    out.append("https://audio.ngfiles.com/{}/{}_{}.mp3".format(str(id)[:3] + "0"*3, id, ''.join([i for i in x.split('itemprop="name"')[1].split("</")[0] if i.lower() in "1234567890qwertyuiopasdfghjklzxcvbnm -_"]).replace(' ', '-')))
    return out

def get_level_info(f):
    info = {
        "id": int(f[1]),
        "name": f[3],
        "version": int(f[5]),
        "creator": {
            "id": int(f[7]),
            "name": f[54]
        },
        "downloads": int(f[13]),
        "likes": int(f[19]),
        "b64desc": f[35],
        "description": base64.b64decode(f[35].replace("_", "/").replace("-", "+")).decode(),
        "featured": False if f[29] == "0" else True,
        "epic": False if f[31] == "0" else True,
        "difficulty": get_difficulty(f),
        "stars": int(f[27]),
        "password": int(get_level_pass(f[1])),
        "coins": int(f[43])
    }
    return info

def get_user_info(x):
    r = requests.post('http://www.boomlings.com/database/getGJUsers20.php', data={"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "str": x, "secret": "Wmfd2893gb7"}).text
    r = requests.post('http://www.boomlings.com/database/getGJUserInfo20.php', data={"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "targetAccountID": str(r).split(':')[21], "secret": "Wmfd2893gb7"}).text
    r = str(r)
    if(r == "-1"):
        return 0
    if(r.split(':')[-3] == "0"):
        mod = "None"
    elif(r.split(':')[-3] == "1"):
        mod = "Mod"
    else:
        mod = "Elder Mod"
    user = {
        "name": r.split(':')[1],
        "rank": int(r.split(':')[47]),
        "stars": int(r.split(':')[13]),
        "diamonds": int(r.split(':')[15]),
        "coins": int(r.split(':')[5]),
        "usercoins": int(r.split(':')[7]),
        "demons": int(r.split(':')[17]),
        "cp": int(r.split(':')[19]),
        "modstatus": mod
    }
    return user

class Level(Resource):
    
    def get(self, name):
        payload = {'gameVersion':'21', 'binaryVersion':'35', 'gdw':'0', 'type':'0', 'str': name, 'diff':'-', 'len':'-', 'page':'0', 'total':'0', 'unCompleted':'0', 'onlycCompleted':'0', 'featured':'0', 'original':'0', 'twoPlayer':'0', 'coins':'0', 'epic':'0', 'demonFilter':'1', 'secret':'Wmfd2893gb7'}
        x = requests.post('http://www.boomlings.com/database/getGJLevels21.php', data=payload).text
        if(x == "-1"):
            return "Level Not Found", 404
        lid = x.split(':')[1]
        payload = {'gameVersion':'21', 'binaryVersion':'35', 'gdw':'0', 'type':'0', 'str': lid, 'diff':'-', 'len':'-', 'page':'0', 'total':'0', 'unCompleted':'0', 'onlycCompleted':'0', 'featured':'0', 'original':'0', 'twoPlayer':'0', 'coins':'0', 'epic':'0', 'demonFilter':'1', 'secret':'Wmfd2893gb7'}
        f = str(requests.post('http://www.boomlings.com/database/getGJLevels21.php', data=payload).text).split(":")
        return get_level_info(f), 200

class FriendList(Resource):

    def get(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("password")
        args = parser.parse_args()
        accid = get_accid_from_user(name)
        if(accid == 0):
            return "Account Not Found", 404
        gjppass = gjpe(args['password'])
        if(gjppass == "0"):
            return "Account Not Found", 404
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "accountID": accid, "gjp": gjppass, "type": "0", "secret": "Wmfd2893gb7"}
        x = requests.post('http://www.boomlings.com/database/getGJUserList20.php', data=payload).text.split('|')
        if(x == ['-1']):
            return "Account Not found", 404
        fin = []
        for i in x:
            info = i.split(':')
            fina = {
                "name": info[1],
                "userid": int(info[3]),
                "accountid": int(info[15])
            }
            fin.append(fina)
        return fin, 200

class AccountComments(Resource):

    def get(self, name):
        accid = get_accid_from_user(name)
        if(accid == 0):
            return "Account Not Found", 404
        page = 0
        finish = False
        loc = []
        while(not finish):
            payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "accountID": str(accid), "page": str(page), "total": "100", "secret": "Wmfd2893gb7"}
            x = requests.post('http://www.boomlings.com/database/getGJAccountComments20.php', data=payload).text.split('|')
            if(x[0].startswith("#")):
                break
            for i in x:
                j = i.split('~')
                comment = {
                    "b64comment": j[1],
                    "comment": base64.b64decode(j[1].replace("_", "/").replace("-", "+")).decode(),
                    "likes": j[3],
                    "age": j[5],
                    "id": j[7].split("#")[0]
                }
                loc.append(comment)
            page += 1
        return loc, 200

class AccountLevelComments(Resource):
    
    def get(self, name):
        userid = get_userid_from_user(name)
        if(userid == 0):
            return "Account Not Found", 404
        page = 0
        finish = False
        loc = []
        while(not finish):
            payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "page": str(page), "total": "0", "secret": "Wmfd2893gb7", "mode": "0", "userID": str(userid), "count": "20"}
            x = requests.post('http://www.boomlings.com/database/getGJCommentHistory.php', data=payload).text
            if(x == ""):
                break
            x = x.split("|")
            for i in x:
                j = i.split("~")
                comment = {
                    "b64comment": j[1],
                    "comment": base64.b64decode(j[1].replace("_", "/").replace("-", "+")).decode(),
                    "levelid": int(j[3]),
                    "author": {
                        "userid": int(j[5]),
                        "name": j[14]
                    },
                    "likes": int(j[7]),
                    "age": j[11],
                    "levelpercent": int(j[9])
                }
                loc.append(comment)
            page += 1
        return loc, 200

class FriendLeaderboard(Resource):

    def get(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("password")
        args = parser.parse_args()
        accid = get_accid_from_user(name)
        gjppass = gjpe(args['password'])
        if(accid == 0 or gjppass == "0"):
            return "Account Not Found", 404
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "accountID": str(accid), "gjp": gjppass.decode(), "type": "friends", "count": "250", "secret": "Wmfd2893gb7"}
        x = requests.post("http://www.boomlings.com/database/getGJScores20.php", data=payload).text
        if(x == "-1"):
            return "Account Not Found", 404
        x = x.split("|")
        loe = []
        for j in x:
            i = j.split(":")
            entry = {
                "name": i[1],
                "userid": i[3],
                "stars": i[23],
                "demons": i[29],
                "diamonds": i[27],
                "coins": i[5],
                "usercoins": i[7],
                "cp": i[25]
            }
            loe.append(entry)
        return loe, 200

class LocalLeaderboard(Resource):

    def get(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("password")
        args = parser.parse_args()
        accid = get_accid_from_user(name)
        gjppass = gjpe(args['password'])
        if(accid == 0 or gjppass == "0"):
            return "Account Not Found", 404
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "accountID": str(accid), "gjp": gjppass.decode(), "type": "relative", "count": "100", "secret": "Wmfd2893gb7"}
        x = requests.post("http://www.boomlings.com/database/getGJScores20.php", data=payload).text
        if(x == "-1"):
            return "Account Not Found", 404
        if(x.endswith("|")):
            x = x[:-1]
        x = x.split("|")
        loe = []
        for j in x:
            i = j.split(":")
            entry = {
                "name": i[1],
                "userid": i[3],
                "stars": i[23],
                "demons": i[29],
                "diamonds": i[27],
                "coins": i[5],
                "usercoins": i[7],
                "cp": i[25]
            }
            loe.append(entry)
        return loe, 200

class TopLeaderboard(Resource):

    def get(self):
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "type": "top", "count": "100", "secret": "Wmfd2893gb7"}
        x = requests.post("http://www.boomlings.com/database/getGJScores20.php", data=payload).text
        if(x.endswith("|")):
            x = x[:-1]
        x = x.split("|")
        loe = []
        for j in x:
            i = j.split(":")
            entry = {
                "name": i[1],
                "userid": i[3],
                "stars": i[23],
                "demons": i[29],
                "diamonds": i[27],
                "coins": i[5],
                "usercoins": i[7],
                "cp": i[25]
            }
            loe.append(entry)
        return loe, 200

class CreatorLeaderboard(Resource):

    def get(self):
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "type": "creators", "count": "100", "secret": "Wmfd2893gb7"}
        x = requests.post("http://www.boomlings.com/database/getGJScores20.php", data=payload).text
        if(x.endswith("|")):
            x = x[:-1]
        x = x.split("|")
        loe = []
        for j in x:
            i = j.split(":")
            entry = {
                "name": i[1],
                "userid": i[3],
                "stars": i[23],
                "demons": i[29],
                "diamonds": i[27],
                "coins": i[5],
                "usercoins": i[7],
                "cp": i[25]
            }
            loe.append(entry)
        return loe, 200

class DailyLevel(Resource):

    def get(self):
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "levelID": "-1", "secret": "Wmfd2893gb7"}
        x = requests.post('http://www.boomlings.com/database/downloadGJLevel22.php', data=payload).text
        lid = x.split(":")[1]
        payload = {'gameVersion':'21', 'binaryVersion':'35', 'gdw':'0', 'type':'0', 'str': lid, 'diff':'-', 'len':'-', 'page':'0', 'total':'0', 'unCompleted':'0', 'onlycCompleted':'0', 'featured':'0', 'original':'0', 'twoPlayer':'0', 'coins':'0', 'epic':'0', 'demonFilter':'1', 'secret':'Wmfd2893gb7'}
        f = str(requests.post('http://www.boomlings.com/database/getGJLevels21.php', data=payload).text).split(":")
        return get_level_info(f), 200

class WeeklyLevel(Resource):

    def get(self):
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "levelID": "-2", "secret": "Wmfd2893gb7"}
        x = requests.post('http://www.boomlings.com/database/downloadGJLevel22.php', data=payload).text
        lid = x.split(":")[1]
        payload = {'gameVersion':'21', 'binaryVersion':'35', 'gdw':'0', 'type':'0', 'str': lid, 'diff':'-', 'len':'-', 'page':'0', 'total':'0', 'unCompleted':'0', 'onlycCompleted':'0', 'featured':'0', 'original':'0', 'twoPlayer':'0', 'coins':'0', 'epic':'0', 'demonFilter':'1', 'secret':'Wmfd2893gb7'}
        f = str(requests.post('http://www.boomlings.com/database/getGJLevels21.php', data=payload).text).split(":")
        return get_level_info(f), 200

class Gauntlets(Resource):

    def get(self):
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "secret": "Wmfd2893gb7"}
        x = requests.post('http://www.boomlings.com/database/getGJGauntlets21.php', data=payload).text.split("#")[0].split("|")
        fin = {}
        for k in x:
            l = k.split(":")
            gno = str(l[1])
            lol = []
            gl = l[-1].split(",")
            for lid in gl:
                payload = {'gameVersion':'21', 'binaryVersion':'35', 'gdw':'0', 'type':'0', 'str': lid, 'diff':'-', 'len':'-', 'page':'0', 'total':'0', 'unCompleted':'0', 'onlycCompleted':'0', 'featured':'0', 'original':'0', 'twoPlayer':'0', 'coins':'0', 'epic':'0', 'demonFilter':'1', 'secret':'Wmfd2893gb7'}
                f = str(requests.post('http://www.boomlings.com/database/getGJLevels21.php', data=payload).text).split(":")
                lol.append(get_level_info(f))
            fin[gno] = lol
        return fin, 200

class FeaturedLevels(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("page")
        page = parser.parse_args()['page']
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "type": "6", "str": "", "diff": "-", "len": "-", "page": str(int(page) - 1), "total": "0", "uncompleted": "0", "onlyCompleted": "0", "featured": "0", "original": "0", "twoPlayer": "0", "coins": "0", "epic": "0", "secret": "Wmfd2893gb7"}
        x = requests.post("http://www.boomlings.com/database/getGJLevels21.php", data=payload)
        if(x.text == "-1"):
            return "Page Not Available", 404
        lids = [i.split(":")[1] for i in x.text.split("|")[:10]]
        fin = []
        for lid in lids:
            payload = {'gameVersion':'21', 'binaryVersion':'35', 'gdw':'0', 'type':'0', 'str': lid, 'diff':'-', 'len':'-', 'page':'0', 'total':'0', 'unCompleted':'0', 'onlycCompleted':'0', 'featured':'0', 'original':'0', 'twoPlayer':'0', 'coins':'0', 'epic':'0', 'demonFilter':'1', 'secret':'Wmfd2893gb7'}
            f = str(requests.post('http://www.boomlings.com/database/getGJLevels21.php', data=payload).text).split(":")
            fin.append(get_level_info(f))
        return fin, 200

class HallOfFame(Resource):

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument("page")
        page = parser.parse_args()['page']
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "type": "16", "str": "", "diff": "-", "len": "-", "page": str(int(page) - 1), "total": "0", "uncompleted": "0", "onlyCompleted": "0", "featured": "0", "original": "0", "twoPlayer": "0", "coins": "0", "epic": "0", "secret": "Wmfd2893gb7"}
        x = requests.post("http://www.boomlings.com/database/getGJLevels21.php", data=payload)
        if(x.text == "-1"):
            return "Page Not Available", 404
        lids = [i.split(":")[1] for i in x.text.split("|")[:10]]
        fin = []
        for lid in lids:
            payload = {'gameVersion':'21', 'binaryVersion':'35', 'gdw':'0', 'type':'0', 'str': lid, 'diff':'-', 'len':'-', 'page':'0', 'total':'0', 'unCompleted':'0', 'onlycCompleted':'0', 'featured':'0', 'original':'0', 'twoPlayer':'0', 'coins':'0', 'epic':'0', 'demonFilter':'1', 'secret':'Wmfd2893gb7'}
            f = str(requests.post('http://www.boomlings.com/database/getGJLevels21.php', data=payload).text).split(":")
            fin.append(get_level_info(f))
        return fin, 200

class MapPacks(Resource):
    
    def get(self):
        page = 0
        lomp = {}
        while(True):
            payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "page": str(page), "secret": "Wmfd2893gb7"}
            x = requests.post("http://www.boomlings.com/database/getGJMapPacks21.php", data=payload).text
            if(x.startswith("#")):
                break
            x = x.split("|")
            for j in x:
                i = j.split(":")
                difficulties = {"1": "Easy", "2": "Normal", "3": "Hard", "4": "Harder", "5": "Insane", "6": "Demon"}
                lol = []
                for lid in i[5].split(","):
                    payload = {'gameVersion':'21', 'binaryVersion':'35', 'gdw':'0', 'type':'0', 'str': lid, 'diff':'-', 'len':'-', 'page':'0', 'total':'0', 'unCompleted':'0', 'onlycCompleted':'0', 'featured':'0', 'original':'0', 'twoPlayer':'0', 'coins':'0', 'epic':'0', 'demonFilter':'1', 'secret':'Wmfd2893gb7'}
                    f = str(requests.post('http://www.boomlings.com/database/getGJLevels21.php', data=payload).text).split(":")
                    lol.append(get_level_info(f))
                info = {
                    "name": i[3],
                    "stars": i[7],
                    "coins": i[9],
                    "difficulty": difficulties[i[11]],
                    "levels": lol
                }
                lomp[i[3]] = info
            page += 1
        return lomp, 200

class SendFriendRequest(Resource):

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("name")
        parser.add_argument("password")
        parser.add_argument("comment")
        args = parser.parse_args()
        accid = get_accid_from_user(name)
        accidto = get_accid_from_user(args['name'])
        gjppass = gjpe(args['password'])
        comment = base64.b64encode(args['comment'].encode())
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "accountID": str(accid), "gjp": gjppass.decode(), "toAccountID": str(accidto), "comment": comment.decode(), "secret": "Wmfd2893gb7"}
        x = requests.post("http://www.boomlings.com/database/uploadFriendRequest20.php", data=payload)
        if(x.text == "-1"):
            return "Error Occurred", 404
        else:
            return "Friend Request Sent", 201

class AcceptFriendRequest(Resource):

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("name")
        parser.add_argument("password")
        args = parser.parse_args()
        accid = get_accid_from_user(name)
        gjppass = gjpe(args['password'])
        accidfrom = get_accid_from_user(args['name'])
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "accountID": str(accid), "gjp": gjppass.decode(), "targetAccountID": str(accidfrom), "secret": "Wmfd2893gb7"}
        print(payload)
        x = requests.post("http://www.boomlings.com/database/acceptGJFriendRequest20.php", data=payload)
        if(x.text == "-1"):
            return "Error Occurred", 404
        else:
            return "Friend Request Accepted", 201

class DenyFriendRequest(Resource):

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("name")
        parser.add_argument("password")
        args = parser.parse_args()
        accid = get_accid_from_user(name)
        gjppass = gjpe(args['password'])
        accidfrom = get_accid_from_user(args['name'])
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "accountID": str(accid), "gjp": gjppass.decode(), "targetAccountID": str(accidfrom), "isSender": "0", "secret": "Wmfd2893gb7"}
        print(payload)
        x = requests.post("http://www.boomlings.com/database/deleteGJFriendRequests20.php", data=payload)
        if(x.text == "-1"):
            return "Error Occurred", 404
        else:
            return "Friend Request Denied", 201

class PostUpdate(Resource):

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("comment")
        parser.add_argument("password")
        args = parser.parse_args()
        accid = get_accid_from_user(name)
        gjppass = gjpe(args['password'])
        comment = base64.b64encode(args['comment'].encode()).decode()
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "accountID": str(accid), "gjp": gjppass, "comment": comment, "secret": "Wmfd2893gb7"}
        x = requests.post("http://www.boomlings.com/database/uploadGJAccComment20.php", data=payload)
        if(x.text == "-1"):
            return "Error Occurred", 404
        else:
            return "Comment Posted", 201

class GetUserInfo(Resource):

    def get(self, name):
        x = get_user_info(name)
        if(x == 0):
            return "User Not Found", 404
        else:
            return get_user_info(name), 200

class GetUserLevels(Resource):

    def get(self, name):
        counter = 0
        lol = []
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "type": "5", "str": str(get_userid_from_user(name)), "page": "0", "secret": "Wmfd2893gb7"}
        x = requests.post("http://www.boomlings.com/database/getGJLevels21.php", data=payload).text
        if(x == "-1"):
            return "Account Not Found", 404
        while(True):
            payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "type": "5", "str": str(get_userid_from_user(name)), "page": str(counter), "secret": "Wmfd2893gb7"}
            x = requests.post("http://www.boomlings.com/database/getGJLevels21.php", data=payload).text
            if(x == "-1"):
                break
            y = x.split("#")[0].split("|")
            for i in y:
                payload = {'gameVersion':'21', 'binaryVersion':'35', 'gdw':'0', 'type':'0', 'str': i.split(":")[1], 'diff':'-', 'len':'-', 'page':'0', 'total':'0', 'unCompleted':'0', 'onlycCompleted':'0', 'featured':'0', 'original':'0', 'twoPlayer':'0', 'coins':'0', 'epic':'0', 'demonFilter':'1', 'secret':'Wmfd2893gb7'}
                f = str(requests.post('http://www.boomlings.com/database/getGJLevels21.php', data=payload).text).split(":")
                lol.append(get_level_info(f))
            counter += 1
        return lol, 200

class BlockUser(Resource):

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("name")
        parser.add_argument("password")
        args = parser.parse_args()
        accid = get_accid_from_user(name)
        gjppass = gjpe(args['password'])
        accidto = get_accid_from_user(args['name'])
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "accountID": str(accid), "gjp": gjppass.decode(), "targetAccountID": str(accidto), "secret": "Wmfd2893gb7"}
        x = requests.post("http://www.boomlings.com/database/blockGJUser20.php", data=payload)
        if(x.text == "1"):
            return "Account Blocked", 201
        elif(x.text == "-1"):
            return "Account Not Found", 404

class UnblockUser(Resource):
    
    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("name")
        parser.add_argument("password")
        args = parser.parse_args()
        accid = get_accid_from_user(name)
        gjppass = gjpe(args['password'])
        accidto = get_accid_from_user(args['name'])
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "accountID": str(accid), "gjp": gjppass.decode(), "targetAccountID": str(accidto), "secret": "Wmfd2893gb7"}
        x = requests.post("http://www.boomlings.com/database/unblockGJUser20.php", data=payload)
        if(x.text == "1"):
            return "Account Unblocked", 201
        elif(x.text == "-1"):
            return "Account Not Found", 404

class UpdateAccSettings(Resource):

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("password")
        parser.add_argument("amf")
        parser.add_argument("afrf")
        parser.add_argument("scht")
        parser.add_argument("yt")
        parser.add_argument("twitter")
        parser.add_argument("twitch")
        args = parser.parse_args()
        amf = args['amf']
        if(amf == "all"):
            amf = "0"
        elif(amf == "friends"):
            amf = "1"
        elif(amf == "none"):
            amf = "2"
        else:
            return "Params not Correct", 404
        afrf = args['afrf']
        if(afrf == "all"):
            afrf = "0"
        elif(afrf == "none"):
            afrf = "1"
        else:
            return "Params not Correct", 404
        scht = args['scht']
        if(scht == "all"):
            scht = "0"
        elif(scht == "friends"):
            scht = "1"
        elif(scht == "none"):
            scht = "2"
        else:
            return "Params not Correct", 404
        if(args['yt'] == None or args['twitch'] == None or args['twitter'] == None):
            return "Params not Correct", 404
        accid = get_accid_from_user(name)
        payload = {"accountID": accid, "gjp": gjpe(args['password']).decode(), "mS": amf, "frS": afrf, "cS": scht, "yt":  args['yt'].replace("https://youtube.com/c/", "").replace("https://youtube.com/channel/", "").replace("https://www.youtube.com/channel/", "").replace("https://www.youtube.com/c/", "").replace("http://www.youtube.com/channel/", "").replace("http://www.youtube.com/c/", "").replace("http://youtube.com/channel/", "").replace("http://youtube.com/c/", "").replace("www.youtube.com/channel/", "").replace("www.youtube.com/c/", "").replace("youtube.com/channel/", "").replace("youtube.com/c/", ""), "twitter": args['twitter'].replace("http://www.twitter.com/@", "").replace("http://twitter.com/@", "").replace("https://twitter.com/@", "").replace("https://www.twitter.com/@", "").replace("https://twitter.com/@", "").replace("www.twitter.com/@", "").replace("twitter.com/@", ""), "twitch": args['twitch'].replace("https://twitch.tv/", "").replace("https://www.twitch.tv/", "").replace("http://twitch.tv/", "").replace("http://www.twitch.tv/", "").replace("www.twitch.tv/", "").replace("twitch.tv/", ""), "secret": "Wmfv3899gc9"}
        x = requests.post("http://www.boomlings.com/database/updateGJAccSettings20.php", data=payload)
        if(x == "-1"):
            return "Error Occurred", 404
        else:
            return "Account Settings Updated", 201

class SendMessage(Resource):

    def post(self, name):
        parser = reqparse.RequestParser()
        parser.add_argument("password")
        parser.add_argument("name")
        parser.add_argument("subject")
        parser.add_argument("body")
        args = parser.parse_args()
        accountID = get_accid_from_user(name)
        gjp = gjpe(args['password']).decode()
        toAccountID = get_accid_from_user(args['name'])
        subject = base64.b64encode(args['subject'].encode()).decode()
        body = args['body']
        toxor = ("14251"*(len(body)//5 + 1))[:len(body)]
        body = base64.b64encode(xor(body, toxor).encode()).decode()
        print(body)
        payload = {"gameVersion": "21", "binaryVersion": "35", "gdw": "0", "accountID": str(accountID), "gjp": gjp, "toAccountID": toAccountID, "subject": subject, "body": body, "secret": "Wmfd2893gb7"}
        x = requests.post("http://www.boomlings.com/database/uploadGJMessage20.php", data=payload).text
        if(x == "-1"):
            return "Error Occurred", 404
        else:
            return "Message Sent!", 201

@app.route('/')
def serve_page():
    return send_from_directory('', "index.html")

api.add_resource(Level, "/level/<string:name>")
api.add_resource(FriendList, "/user/<string:name>/friends") # pass
api.add_resource(AccountComments, "/user/<string:name>/accountcomments")
api.add_resource(AccountLevelComments, "/user/<string:name>/levelcomments")
api.add_resource(FriendLeaderboard, "/leaderboard/<string:name>/friends") # pass
api.add_resource(LocalLeaderboard, "/leaderboard/<string:name>/local") # pass
api.add_resource(TopLeaderboard, "/leaderboard")
api.add_resource(CreatorLeaderboard, "/leaderboard/creators")
api.add_resource(DailyLevel, "/daily")
api.add_resource(WeeklyLevel, "/weekly")
api.add_resource(Gauntlets, "/gauntlets")
api.add_resource(FeaturedLevels, "/level/featured") # page
api.add_resource(HallOfFame, "/level/halloffame") # page
api.add_resource(MapPacks, "/level/mappacks") # page
api.add_resource(SendFriendRequest, "/user/<string:name>/friends/request") # password, name, comment
api.add_resource(AcceptFriendRequest, "/user/<string:name>/friends/accept") # password, name
api.add_resource(DenyFriendRequest, "/user/<string:name>/friends/deny") # password, name
api.add_resource(BlockUser, "/user/<string:name>/block") # name, password
api.add_resource(UnblockUser, "/user/<string:name>/unblock") # name, password
api.add_resource(PostUpdate, "/user/<string:name>/accountcomments/post") # comment, password
api.add_resource(GetUserInfo, "/user/<string:name>")
api.add_resource(GetUserLevels, "/user/<string:name>/levels")
api.add_resource(UpdateAccSettings, "/user/<string:name>/updatesettings") # password, amf, afrf, scht, youtube, twitch, twitter
api.add_resource(SendMessage, "/user/<string:name>/sendmessage") # password, name, subject, body

if __name__=="__main__":
    app.run(host="0.0.0.0", port="80")