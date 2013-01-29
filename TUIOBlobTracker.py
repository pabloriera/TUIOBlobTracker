import tuio
import liblo, sys
from math import hypot

def check_list_miss(listBIG,listSMALL):
	ans = []

	for k in listBIG:
		if not(listSMALL.count(k)):
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

def cerca_de_pared(x,y,th):
	return x < th or (1 - x) < th or y < th or (1 - y) < th

class Blob:
	def __init__(self):
		self.xpos = 0
		self.ypos = 0
		self.state = False
		self.idle = False
		self.friend = 0

# ARRANCA SCRIPT
try:
	target = liblo.Address('10.42.0.46',12345)
	print "Connected"

except liblo.AddressError, err:
	print str(err)
	sys.exit()

# MANDA INIT
liblo.send(target, "/init")

# ARRANCA A RECIVIR TUIO
tracking = tuio.Tracking()
print "loaded profiles:", tracking.profiles.keys()
print "list functions to access tracked objects:", tracking.get_helpers()

N = 5
out_th = 0.03
col_th = 0.05

b = []

for i in range(0,N):
	b.append(Blob())

b_id= {}


idlistOLD = []

printFlag = True

try:
	while 1:

		tracking.update()

		idlist = []
		pos_id = {}
		
		for cur in tracking.cursors():
						
			idlist.append(cur.sessionid)
			pos_id[cur.sessionid] = (cur.xpos,cur.ypos)
			

		idlist.sort()

		#~ TODO IGUAL
		if idlist == idlistOLD and idlist != []:

			for l in idlist:
				c = b_id[l]
				b[c].xpos = pos_id[l][0]
				b[c].ypos = pos_id[l][1]
				liblo.send(target, "/blob" + str(c+1), b[c].xpos,b[c].ypos)
			
		#~ CAMBIOS (SE VA ALGUIEN O COLISION)
		elif idlist != idlistOLD:

			idlistMISS = check_list_miss(idlistOLD,idlist)
			
			for l in idlistMISS:
				
				c = b_id[l]
				b[c].idle = True

			for l in idlistMISS:

				c = b_id[l]
		
				#~ SE VA ALGUIEN
				if cerca_de_pared(b[c].xpos,b[c].ypos,out_th):
				
					b[c].state = False
					b[c].idle = False
					b_id.pop(l)
					liblo.send(target, "/blob"+str(c+1)+ "/state", 0) # SEND BLOB OFF
							
				#~ COLISION
				else:
					
					#~ BUSCAR FRIEND
					for cc in range(N):
						
						if b[c].state and not(b[c].idle):
							
							if cc != c:
								dist = hypot( b[c].xpos - b[cc].xpos , b[c].ypos - b[cc].ypos )
								
								if dist < col_th:
								
									b[c].friend = cc


			#~ ENTRA ALGUIEN
			
			idlistNEW = check_list_new(idlistOLD,idlist)
			
			for l in idlistNEW:

				for c in range(N):
					
					#~ POR LOS BORDES
					if not(b[c].state):
						b_id[l] = c
						
						b[c].state = True
						b[c].idle = False
						
						liblo.send(target, "/blob"+str(c+1)+ "/state", 1) # SEND BLOB ON
						
						b[c].xpos = pos_id[l][0]
						b[c].ypos = pos_id[l][1]
						liblo.send(target, "/blob"+str(c+1), b[c].xpos,b[c].ypos)
						break
						
						
					#~ DESDE ADENTRO
					elif b[c].idle:
						
						b_id[l] = c
						
						b[c].idle = False
												
						b[c].xpos = pos_id[l][0]
						b[c].ypos = pos_id[l][1]
						liblo.send(target, "/blob"+str(c+1), b[c].xpos,b[c].ypos)


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
