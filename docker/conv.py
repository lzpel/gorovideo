import json, sys, os, logging, time
import requests

if len(sys.argv)==1:
    host="http://localhost:8080"
else:
    host='https://video-161819.appspot.com'

while True:
    r = requests.post("{0}/post/doga/conv".format(host))
    j = r.json()
    print(j)
    if j and j["main"]:
        # 保存
        file = open(".{0}input.dat".format(os.sep), 'wb')
        rdl = requests.get("{0}/blob/{1}".format(host,j["main"]["blob"][0]), stream=True)
        print "{0}/blob/{1}".format(host,j["main"]["blob"][0])
        for chunk in rdl.iter_content(chunk_size=1024 ** 2):
            if chunk:
                file.write(chunk)
                logging.warning("download {0}".format(j["main"]["key"]["id"]))
        file.close()
        # 変換
        file = {}
        shell = [
            "rm .{0}{1}", "del .{0}{1}",
            "rm .{0}{2}", "del .{0}{2}",
            "avconv -y -i .{0}input.dat -f mp4 -movflags faststart -crf 26 -r 60 -s 1280x720 -t 0300 .{0}{1}",
            "avconv -y -i .{0}input.dat -f mp4 -movflags faststart -crf 26 -r 30 -s  640x360 -t 1800 .{0}{2}",
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
        data = {
            'id': j["main"]["key"]["id"]
        }
        # 送信
        r = requests.post(j["doga"], data=data, files=file)
        # 終了
        logging.warning("send {0} file to id:{1}".format(len(file), data["id"]))
    else:
        logging.warning("now it do not need convert files")
    time.sleep(5)
