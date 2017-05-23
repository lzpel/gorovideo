import json, sys, os, logging, time
import requests

if len(sys.argv)==1:
    host="http://localhost:8080"
else:
    host='https://video-161819.appspot.com'

#継承
file=None
oldconv=None

while True:
    #受信
    newconv = requests.post("{0}/post/doga/conv".format(host)).json()
    if oldconv and oldconv["main"]:
        # 送信
        #r = requests.post(newconv["doga"], data={'id': oldconv["main"]["key"]["id"]}, files=file)
        logging.warning(newconv)
        logging.warning(oldconv)
        logging.warning(file)
    if newconv and newconv["main"]:
        # 保存
        tmp = open(".{0}input.dat".format(os.sep), 'wb')
        req=requests.get("{0}/blob/{1}".format(host,newconv["main"]["blob"][0]), stream=True)
        for chunk in req.iter_content(chunk_size=1024 ** 2):
            if chunk:
                tmp.write(chunk)
                logging.warning("download {0}".format(j["main"]["key"]["id"]))
        tmp.close()
        # 変換
        shell = [
            "rm .{0}{1}", "del .{0}{1}",
            "rm .{0}{2}", "del .{0}{2}",
            ".{0}ffmpeg -y -i .{0}input.dat -f mp4 -movflags faststart -crf 26 -r 60 -s 1280x720 -t 0300 .{0}{1}",
            ".{0}ffmpeg -y -i .{0}input.dat -f mp4 -movflags faststart -crf 26 -r 30 -s  640x360 -t 1800 .{0}{2}",
            "add {1} .{0}{1}",
            "add {2} .{0}{2}",
        ]
        for i in shell:
            i = i.format(os.sep, "r60s1280x0720.dat", "r30s0640x0360.dat")
            s = i.split()
            if s[0] == "add":
                if os.path.exists(s[2]):
                    file[s[1]] = open(s[2], 'rb')
            else:
                print(i)
                os.system(i)
        # 終了
        logging.warning("send {0} file to id:{1}".format(len(file), data["id"]))
    # 入替
    oldconv = newconv
    #休止
    logging.warning("sleep")
    time.sleep(5)