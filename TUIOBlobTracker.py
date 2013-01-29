import tuio
import liblo
import sys
from math import hypot

def check_list_miss(prev_list,new_list):
	ans = []

	for k in prev_list:
		if not(new_list.count(k)):
			ans.append(k)

	return ans	
	
def check_list_new(prev_list,new_list):
	ans = []

	for k in new_list:
		if not(prev_list.count(k)):
			ans.append(k)

	return ans
	
def check_list_idem(list1,list2):
	ans = []

	for k in list1:
		if list2.count(k):
			ans.append(k)

	return ans

def near_wall(x,y,th):
	return x < th or (1 - x) < th or y < th or (1 - y) < th

class Blob:
	def __init__(self):
		self.xpos = 0
		self.ypos = 0
		self.state = False
		
# START SCRIPT
try:
	target = liblo.Address('10.42.0.46',12345)
	print "Connected"

except liblo.AddressError, err:
	print str(err)
	sys.exit()

# SEND INIT
liblo.send(target, "/init")

# STARTS TUIO
tracking = tuio.Tracking()
print "loaded profiles:", tracking.profiles.keys()
print "list functions to access tracked objects:", tracking.get_helpers()


#~ NUMBER OF BLOBS
N = 5

#~ THERSHOLDS FOR GETTING OUT AND COLISSION
out_th = 0.05
col_th = 0.05

id2b = {}
b2id = {}


#~ BLOB LIST
b = []

for c in range(0,N):
	b.append(Blob())
	b2id[c]=0

idlistOLD = []

printFlag = True

try:
	while 1:

		tracking.update()

		idlist = []
		pos_id = {}
		
		
		#~ FILL IDLIST WITH LAST UPDATES
		for cur in tracking.cursors():
						
			idlist.append(cur.sessionid)
			pos_id[cur.sessionid] = (cur.xpos,cur.ypos)

		idlist.sort()

		#~ IF NOT EMPTY LIST
		if idlist!=[] or idlistOLD:

			#~ CHANGES BETWEEN OLD AND NEW
			if idlist != idlistOLD:
				print "CHANGE"
				#~ ASK MISSING ID'S
				idlistMISS = check_list_miss(idlistOLD,idlist)
				
				for l in idlistMISS:

					c = id2b[l]
			
					#~ IT'S GETTING OUT
					if near_wall(b[c].xpos,b[c].ypos,out_th):
					
						b[c].state = False
						id2b.pop(l)
						b2id[c] = 0
						liblo.send(target, "/blob"+str(c+1)+ "/state", 0) # SEND BLOB OFF
								
					#~ HAS MERGE WITH OTHERS?
					else:
						
						#~ SERCH WICH ID REMAINS AND ATE THE MISSING
						for cc in range(N):
							
							if b[c].state:# and idlist.count(b2id[cc]):
								
									dist = hypot( b[c].xpos - b[cc].xpos , b[c].ypos - b[cc].ypos )
									
									if dist < col_th:
									
										b2id[c] = b2id[cc]
										print "SI"


				#~ NEW IDs
				
				idlistNEW = check_list_new(idlistOLD,idlist)
				
				for l in idlistNEW:
					
					#~ CAME FROM OUTSIDE
					if near_wall(pos_id[l][0],pos_id[l][1],out_th):

						for c in range(N):
						
							if not(b[c].state):
								
								id2b[l] = c
								b2id[c] = l
								
								b[c].state = True
								
								liblo.send(target, "/blob"+str(c+1)+ "/state", 1) # SEND BLOB ON
								break
					
					#~ CAME FROM INSIDE
					else:
						
						blobdiv = False
						
						
						#~ BLOBDIV
						for c in range(N):
						
							dist = hypot( b[c].xpos - pos_id[l][0] , b[c].ypos - pos_id[l][1] )
												
							if dist < col_th and not(idlistNEW.count(b2id[c])):
								
								id2b[l] = c
								b2id[c] = l
								blobdiv = True
								
								break
						
						#~ MAGIC
						if not(blobdiv):
						
							for c in range(N):
							
								if not(b[c].state):
									
									id2b[l] = c
									b2id[c] = l
									
									b[c].state = True
									
									liblo.send(target, "/blob"+str(c+1)+ "/state", 1) # SEND BLOB ON
									break


			for c in range(N):
				if b[c].state:
					l = b2id[c]
					b[c].xpos = pos_id[l][0]
					b[c].ypos = pos_id[l][1]
					liblo.send(target, "/blob" + str(c+1), b[c].xpos,b[c].ypos)


		idlistOLD = idlist		

		if printFlag:
			#~ TEXTO PA PRINT
			s1 = '\r'+str(idlist)
			s2 = '\r'
			
			for c in range(N):
				if b[c].state:
					s2 = s2  + "#" + str(c+1) + " " + "%.2f" % b[c].xpos + " " + "%.2f" % b[c].ypos + "\t"
				else:
					s2 = s2  + "#" + str(c+1) + " " + "OFF" + "\t\t"

			sys.stdout.write("\r                                                                ")		
			sys.stdout.write(s1 + "\n")		
			sys.stdout.write("\r                                                                ")		
			sys.stdout.write(s2)
			sys.stdout.write("\033[F")
						
except KeyboardInterrupt:
    tracking.stop()
