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
	
#~ def check_list_idem(list1,list2):
	#~ ans = []
#~ 
	#~ for k in list1:
		#~ if list2.count(k):
			#~ ans.append(k)

	return ans

def near_wall(x,y,th):
	return x < th or (1 - x) < th or y < th or (1 - y) < th
	
	
def near_blob(blobs,x,y,th):
	
	ans = []
	
	for cc in range(len(blobs)):
	
		if blobs[cc].state:
		
			dist = hypot(x - blobs[cc].xpos , y - blobs[cc].ypos )
			
			if dist < th:
				
				ans.append(cc)
	return ans	

def main():										

	class Blob:
		def __init__(self):
			self.xpos = 0
			self.ypos = 0
			self.state = False
			
	# START SCRIPT
	try:
		target = liblo.Address('10.42.0.46',12345)
		#~ target = liblo.Address('192.168.0.100',12345)
		print "Connected"

	except liblo.AddressError, err:
		print str(err)
		sys.exit()

	# SEND INIT
	liblo.send(target, "/init")

	# STARTS TUIO
	tracking = tuio.Tracking()
	#print "loaded profiles:", tracking.profiles.keys()
	#print "list functions to access tracked objects:", tracking.get_helpers()



	#~ THERSHOLDS FOR GETTING OUT AND COLISSION
	out_th = 0.05
	col_th = 0.2

	id2b = {}
	b2id = {}

	#~ BLOB LIST
	blobs = []

	#~ NUMBER OF BLOBS
	N = 30

	for c in range(0,N):
		blobs.append(Blob())
		b2id[c]=0

	idlistOLD = []

	printFlag = False

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

			#~ IF NOT EMPTY LIST, OR IDLISTOLD EMPTY
			if idlist!=[] or idlistOLD:

				#~ CHANGES BETWEEN OLD AND NEW
				if idlist != idlistOLD:
									
					#~ ASK MISSING ID'S
					idlistMISS = check_list_miss(idlistOLD,idlist)
					
					for l in idlistMISS:

						c = id2b[l]
				
						#~ IT'S GETTING OUT
						near_wall_flag = near_wall(blobs[c].xpos,blobs[c].ypos,out_th)
						
						#~ HAS MERGE WITH OTHERS?
						near_blob_list = near_blob(blobs,blobs[c].xpos,blobs[c].ypos,col_th)
				
						if len(near_blob_list)>1 and not(near_wall_flag):
							
							#~ SEARCH WICH ID REMAINS AND MERGE THE MISSING
							
							for cc in near_blob_list:
								if idlist.count(b2id[cc]) and c!=cc:
										b2id[c] = b2id[cc]
						
						
						else:	#~ DISAPPEARED
						
							blobs[c].state = False
							id2b.pop(l)
							b2id[c] = 0
							liblo.send(target, "/blob"+str(c+1)+ "/state", 0) # SEND BLOB OFF
					
					
					#~ NEW IDs
					
					idlistNEW = check_list_new(idlistOLD,idlist)
					
					for l in idlistNEW:
						
						near_wall_flag = near_wall(pos_id[l][0],pos_id[l][1],out_th)
						
						near_blob_list = near_blob(blobs,pos_id[l][0], pos_id[l][1],col_th)
						
						#~ BLOB DIV
						if len(near_blob_list)>1 and not(near_wall_flag):
							
							for c in near_blob_list:
								
								if not(idlistNEW.count(b2id[c])):
									
									#~ REASSIGN IDENTITY
									
									id2b[l] = c
									b2id[c] = l
									
									break
									
						
						else: #~ CAME FROM OUTSIDE
							
							for c in range(N):
							
								if not(blobs[c].state):
									
									id2b[l] = c
									b2id[c] = l
									
									blobs[c].state = True
									
									liblo.send(target, "/blob"+str(c+1)+ "/state", 1) # SEND BLOB ON
									break
						
				#~ SEND ALL POSITIONS
				for c in range(N):
					if blobs[c].state:
						l = b2id[c]
						if pos_id.keys().count(l):
							blobs[c].xpos = pos_id[l][0]
							blobs[c].ypos = pos_id[l][1]
							liblo.send(target, "/blob" + str(c+1) + "/pos", blobs[c].xpos,blobs[c].ypos)  # SEND POSITION
						else:
							blobs[c].state = False
							
							

			idlistOLD = idlist		

			if printFlag:
				#~ TEXT PRINT
				s1 = '\r'+str(idlist)
				s2 = '\r'
				
				for c in range(N):
					if blobs[c].state:
						s2 = s2  + "#" + str(c+1) + " " + "%.2f" % blobs[c].xpos + " " + "%.2f" % blobs[c].ypos + "\t"
					else:
						s2 = s2  + "#" + str(c+1) + " " + "OFF" + "\t\t"

				sys.stdout.write("\r                                                                ")		
				sys.stdout.write(s1 + "\n")		
				sys.stdout.write("\r                                                                ")		
				sys.stdout.write(s2)
				sys.stdout.write("\033[F")
							
				
	except KeyboardInterrupt:
		tracking.stop()
	except:
		tracking.stop()
		print "Error inesperado:", sys.exc_info()[0]
		main()
	
		
		
if __name__ == "__main__":
    main()
	
	
	
	
