import requests
import json
from rsa import encrypt

#hcsurl, locationCode, schoolCode 출처 : https://cafe.naver.com/nameyee/28017
hcsurl = {
        "서울": "https://senhcs.eduro.go.kr/",
        "부산": "https://penhcs.eduro.go.kr/",
        "대구": "https://dgehcs.eduro.go.kr/",
        "인천": "https://icehcs.eduro.go.kr/",
        "광주": "https://genhcs.eduro.go.kr/",
        "대전": "https://djehcs.eduro.go.kr/",
        "울산": "https://usehcs.eduro.go.kr/",
        "세종": "https://sjehcs.eduro.go.kr/",
        "경기": "https://goehcs.eduro.go.kr/",
        "강원": "https://kwehcs.eduro.go.kr/",
        "충북": "https://cbehcs.eduro.go.kr/",
        "충남": "https://cnehcs.eduro.go.kr/",
        "전북": "https://jbehcs.eduro.go.kr/",
        "전남": "https://jnehcs.eduro.go.kr/",
        "경북": "https://gbehcs.eduro.go.kr/",
        "경남": "https://gnehcs.eduro.go.kr/",
        "제주": "https://jjehcs.eduro.go.kr/"
}

locationCode = {
        "서울": "01",
        "부산": "02",
        "대구": "03",
        "인천": "04",
        "광주": "05",
        "대전": "06",
        "울산": "07",
        "세종": "08",
        "경기": "10",
        "강원": "11",
        "충북": "12",
        "충남": "13",
        "전북": "14",
        "전남": "15",
        "경북": "16",
        "경남": "17",
        "제주": "18"
}

schoolCode = {
        "유치원": "1",
        "초등학교": "2",
        "중학교": "3",
        "고등학교": "4",
        "특수학교": "5"
}

class 자가진단:
	cityCode = ""
	schoolLevel = ""
	schoolName = ""
	
	region = ""
	regionUrl = ""
	orgCode = ""
	name = ""
	birth = ""
	PW = ""
	
	def __init__(self, schoolType, schoolName, region, name, birth, PW):
		self.cityCode = locationCode[region]
		self.schoolLevel = schoolCode[schoolType]
		self.schoolName = schoolName
		self.region = region
		self.name = name
		self.birth = birth
		self.PW = PW
		
	def searchSchool(self):
		getUrl = "https://hcs.eduro.go.kr/v2/searchSchool"
		param = {"lctnScCode" : self.cityCode, "schulCrseScCode" : self.schoolLevel, "orgName" : self.schoolName, "loginType" : "school"}
		result = requests.get(getUrl, params = param)
		return result.json()["schulList"][0]["orgCode"]
		
	def login(self):
		self.regionUrl = hcsurl[self.region]
		self.orgCode = self.searchSchool()
		postUrl = self.regionUrl+"v2/findUser"
		header = {"Content-type": "application/json"}
		datum = {"birthday" : encrypt(self.birth), "loginType": "school", "name" : encrypt(self.name), "orgCode" : self.orgCode, "stdntPNo":  ""}
		result = requests.post(postUrl, data = json.dumps(datum), headers = header)
		return result.json()["token"]
		
	def hasPW(self):
		postUrl = self.regionUrl+"v2/hasPassword"
		header = {"Authorization" : self.login()}
		result = requests.post(postUrl, headers = header)
		return result.json()
		
	def verifyPW(self):
		postUrl = self.regionUrl+"v2/validatePassword"
		datum = {"deviceUuid" : "", "password" : encrypt(self.PW)}
		header = {"Authorization" : self.login(), "Content-type": "application/json"}
		result = requests.post(postUrl, data = json.dumps(datum), headers = header)
		return result.json()
		
	def selectStd(self):
		postUrl = self.regionUrl+"v2/selectUserGroup"
		datum = {}
		header = {"Authorization" : self.verifyPW()}
		result = requests.post(postUrl, data = datum, headers = header)
		return result.json()[0]["userPNo"], result.json()[0]["token"]
		
	def stdInfo(self):
		postUrl = self.regionUrl+"v2/getUserInfo"
		datum = {"orgCode" : self.orgCode, "userPNo" : self.selectStd()[0]}
		header = {"Authorization" : self.selectStd()[1], "Content-type": "application/json"}
		result = requests.post(postUrl, data = json.dumps(datum), headers = header)
		return result.json()["token"]
		
	def execute(self):
		postUrl = self.regionUrl+"registerServey"
		datum = {"deviceUuid" : "", "rspns00" : "Y", "rspns01" : "1", "rspns02" : "1", "rspns09" : "0", "upperToken" : self.stdInfo(), "upperUserNameEncpt" : self.name}
		header = {"Authorization" : self.stdInfo(), "Content-type": "application/json"}
		result = requests.post(postUrl, data = json.dumps(datum), headers = header)
		return result.json()
		
	def selfCheck(self):
		if not self.searchSchool():
			return print("학교를 찾을수 없습니다!")
		if not self.login():
			return print("로그인 실패!")
		if not self.hasPW():
			return print("비밀번호가 설정 되어 있지 않습니다")
		if not self.verifyPW():
			print("비밀번호 검증 실패!")
		if not self.selectStd():
			print("학생 선택 실패!")
		if not self.stdInfo():
			print("학생 정보가 없습니다!")
		print("학생 정보 확인 완료!")
		print("자가진단 중~..기다려 주세요")
		if self.execute():
			return print(self.execute()["registerDtm"]+"에 "+self.name+"님 자가진단 완료!")
		else:
			return print("자가진단 실패!")
