import json, sys, os, logging, time
import requests

if len(sys.argv) == 1:
	host = "http://localhost:8080"
else:
	host = 'https://video-161819.appspot.com'

def getstatus():
	stat=requests.post("{0}/post/doga/conv".format(host)).json()
	print stat
	if stat and stat["main"]:
		return stat
	else:
		return None

while True:
	print "\n##LOOPBEGIN##\n"
	# 受信
	stat=getstatus()
	if stat:
		# 保存
		print("\ndownload {0}\n".format(stat["main"]["key"]["id"]))
		tmp = open(".{0}input.dat".format(os.sep), 'wb')
		req = requests.get("{0}/blob/{1}".format(host, stat["main"]["blob"][0]), stream=True)
		for chunk in req.iter_content(chunk_size=1024 ** 2):
			if chunk:
				tmp.write(chunk)
		tmp.close()
		# 変換
		shell = [
			"rm .{0}{1}", "del .{0}{1}",
			"rm .{0}{2}", "del .{0}{2}",
			".{0}ffmpeg -y -i .{0}input.dat -f mp4 -movflags faststart -crf 26 -r 30 -s  640x360 -t 1800 .{0}{1}",
			".{0}ffmpeg -y -i .{0}input.dat -f mp4 -movflags faststart -crf 26 -r 60 -s 1280x720 -t 0300 .{0}{2}",
			"add {1} .{0}{1}",
			"add {2} .{0}{2}",
		]
		stat["file"] = {}
		for i in shell:
			i = i.format(os.sep, "01r30s0640x0360.dat", "02r60s1280x0720.dat")
			s = i.split()
			if s[0] == "add":
				if os.path.exists(s[2]):
					stat["file"][s[1]]=open(s[2], 'rb')
			else:
				print("\n{0}\n".format(i))
				os.system(i)
		# 送信
		r = requests.post(getstatus()["doga"], data={'id': stat["main"]["key"]["id"]}, files=stat["file"])
		for i in stat["file"].values():
			i.close()
		# 終了
		print("\nsend {0} file to id:{1}\n".format(len(stat["file"]), stat["main"]["key"]["id"]))
	# 休止
	print("\nsleep\n")
	time.sleep(5)
