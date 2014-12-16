#author Dawid Lubczynski
#client FTP supporting only passive mode

from socket import *
from string import *
import time
import os
import sys

#
#error codes
#
class ErrorCode:
    NO_ERROR = 0
    ERROR = 1

class isFolder:
    YES = 0
    NO  = 1

#
#FTP class
#
class myFTP:
	sock = socket()          #socket for trasmision commands
	sockData = socket()      #socket for trasmission data
	socketNoBlock = socket() #socket for non blocking text receive
	IPdata = ''              #IP gets from server
	bufforSize = 4096        #bufor size
	port = 21                #FTP default port
	portData = 0            
	filesCount = 1
	filenames = []           #File names in current directory
	folderlist = []          #Folders names in current directory
	depth = 0

    #
    # method analizing response code from server and return false 
    # if server send error code
    #
	def analizeServerResp(self, tm):
		retVal = ErrorCode.NO_ERROR

		if tm[:4].find('110 ') > -1:
			#print 'Restart marker reply.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('120 ') > -1:
			#print 'Service ready in nnn minutes.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('125 ') > -1:
			#print 'Data connection already open; transfer starting.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('150 ') > -1:
			#print 'File status okay; about to open data connection.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('200 ') > -1:
			#print 'Command okay.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('202 ') > -1:
			#print 'Command not implemented, superfluous at this site.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('211 ') > -1:
			#print 'System status, or system help reply.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('212 ') > -1:
			#print 'File status.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('214 ') > -1:
			#print 'Help message.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('215 ') > -1:
			#print 'Name system type.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('220 ') > -1:
			#print 'Service ready for new user.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('221 ') > -1:
			#print 'Service closing control connection.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('225 ') > -1:
			#print 'Data connection open; no transfer in progress.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('226 ') > -1:
			#print 'Closing data connection.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('227 ') > -1:
			#print 'Entering Passive Mode (h1,h2,h3,h4,p1,p2).'
			self.getIpAndPort(tm)

		elif tm[:4].find('230 ') > -1:
			print 'User logged in, proceed.'
		elif tm[:4].find('250 ') > -1:
			#print 'Requested file action okay, completed.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('257 ') > -1:
			#print 'PATHNAME created.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('331 ') > -1:
			print 'User name okay, need password.'
		elif tm[:4].find('332 ') > -1:
			print 'Need account for login.'
		elif tm[:4].find('350 ') > -1:
			#print 'Requested file action pending further information.'
			retVal = ErrorCode.NO_ERROR
		elif tm[:4].find('421 ') > -1:
			print 'Service not available, closing control connection.'
		elif tm[:4].find('425 ') > -1:
			print 'Cant open data connection.'
		elif tm[:4].find('426 ') > -1:
			print 'Connection closed; transfer aborted.'
		elif tm[:4].find('450 ') > -1:
			print 'Requested file action not taken.'
		elif tm[:4].find('451 ') > -1:
			print 'Requested action aborted: local error in processing.'
		elif tm[:4].find('452 ') > -1:
			print 'Requested action not taken.'
		elif tm[:4].find('500 ') > -1:
			print 'Syntax error, command unrecognized.'
			retVal = ErrorCode.ERROR
		elif tm[:4].find('501 ') > -1:
			print 'Syntax error in parameters or arguments.'
			retVal = ErrorCode.ERROR
		elif tm[:4].find('502 ') > -1:
			print 'Command not implemented.'
			retVal = ErrorCode.ERROR
		elif tm[:4].find('503 ') > -1:
			print 'Bad sequence of commands.'
			retVal = ErrorCode.ERROR
		elif tm[:4].find('504 ') > -1:
			print 'Command not implemented for that parameter.'
			retVal = ErrorCode.ERROR
		elif tm[:4].find('530 ') > -1:
			print 'Not logged in.'
			retVal = ErrorCode.ERROR
		elif tm[:4].find('532 ') > -1:
			print 'Need account for storing files.'
			retVal = ErrorCode.ERROR
		elif tm[:4].find('550 ') > -1:
			print 'Requested action not taken.'
			retVal = ErrorCode.ERROR
		elif tm[:4].find('551 ') > -1:
			print 'Requested action aborted: page type unknown.'
			retVal = ErrorCode.ERROR
		elif tm[:4].find('552 ') > -1:
			print 'Requested file action aborted.'
			retVal = ErrorCode.ERROR
		elif tm[:4].find('553 ') > -1:
			print 'Requested action not taken.'
			retVal = ErrorCode.ERROR

		return retVal

    #
    # method puts IP and port from server to members IPdata, portData
    #
	def getIpAndPort(self, tm):
		temp = tm.split('(')
		temp2 = temp[1].split(')')
		tempIP = temp2[0].split(',')

		self.IPdata = tempIP[0] + '.' + tempIP[1] + '.' + tempIP[2] + '.' + tempIP[3]
		self.portData = int(tempIP[4]) * 256 + int(tempIP[5])

    #
    # constructor
    #
	def __init__(self, login, password, server):
		loginCommand = 'USER ' + login + '\r\n'
		passwCommand = 'PASS ' + password + '\r\n'

		self.sock = socket(AF_INET, SOCK_STREAM)  # utworzenie gniazda
		self.sock.connect((server, self.port))
		tm = self.sock.recv(self.bufforSize)
		self.analizeServerResp(tm)

		self.sock.send(loginCommand)
		tm = self.sock.recv(self.bufforSize)
		self.analizeServerResp(tm)

		self.sock.send(passwCommand)
		tm = self.sock.recv(self.bufforSize)
		self.analizeServerResp(tm)

    #
    # notify server about end of session
    #
	def close(self):
		self.sock.send('QUIT' + '\r\n')
		tm = self.recv_timeout()
		self.analizeServerResp(tm)
		self.sock.close()

		print 'Connection closed.'

		return 1

    #
    # request servet for passive mode
    #
	def ftpPassive(self):
		time.sleep(0.2)
		self.sock.send('PASV\r\n')
		tm = self.recv_timeout()
		self.analizeServerResp(tm)
		return 1

    #
    # list files/directories in current location
    #
	def showMeWhatYouHaveInside(self):
		path = self.returnDirectory()
		self.ftpPassive()

		self.sockData = socket(AF_INET, SOCK_STREAM)
		self.sockData.connect((self.IPdata, self.portData))

		self.sock.send('LIST\r\n')

		print '\nFile list in path: ' + path

		temp = '   '
		while (len(temp) > 1):

			tm = self.sockData.recv(self.bufforSize)
			temp = tm[:len(tm) - 1] + '\0'
			print tm
		self.sockData.close()

		return 1
    
    #
    # method returns corrent directory path
    #
	def returnDirectory(self):
		self.sock.send('PWD\r\n')

		tm = self.recv_timeout()
		temp = tm.split(' ')

		return temp[1]
		
    #
    # method for changing directory
    #
	def goToDirectory(self, path):
		print 'Go to dir ' + path
		self.sock.send('CWD ' + path + '\r\n')
		tm = self.recv_timeout()
		ret = self.analizeServerResp(tm)
		self.filenames = []
		return ret
		
    #
    # method does the same think as cd ..
    #
	def goToDirectoryUp(self):
		self.sock.send('CDUP' + '\r\n')
		tm = self.recv_timeout()
		self.depth -= 1

		return 1

    #
    # receive data by non blocking socket
    #
	def recv_timeout(self, timeout=0.5):
		self.sock.setblocking(0)
		total_data = []
		data = ''

		begin = time.time()
		while 1:
			if total_data and time.time() - begin > timeout:
				break

			elif time.time() - begin > timeout * 2:
				break

			try:
				data = self.sock.recv(self.bufforSize)
				if data:
					total_data.append(data)
					begin = time.time()
					self.analizeServerResp(data)
				else:
					time.sleep(0.1)
			except:
				pass

		self.sock.settimeout(None)
		self.sock.setblocking(1)
		return ''.join(total_data)

    #
    # downoad file 
    #
	def downloadFile(self, fileName, localPath):
		self.ftpPassive()

		self.sock.send('RETR ' + fileName + '\r\n')
		tm = self.recv_timeout()
		exist = self.analizeServerResp(tm)

		if exist == ErrorCode.NO_ERROR:
			self.sockData = socket(AF_INET, SOCK_STREAM)
			try:
				self.sockData.connect((self.IPdata, self.portData))

				file = open(localPath + '\\' + fileName, 'wb')

				temp = '   '
				countDown = 0
				while (len(temp) > 1):
					tm = self.sockData.recv(self.bufforSize)
					file.write(tm)
					temp = tm[:len(tm) - 1] + '\0'
					countDown = countDown + len(tm)
				self.sockData.close()
				file.close()
				print 'File nr' + str(self.filesCount)+ ', name: ' + fileName + ': ' + str(countDown) + ' bytes'
				self.filesCount = self.filesCount + 1
			except:
				print 'I cant connect'

		return 1

	def downloadAllFilesInFolder(self, localPath):
		i = 0
		if (len(self.filenames) < 1):
			self.getFileList()

		while (i < len(self.filenames)):
			self.downloadFile(self.filenames[i],localPath)
			i += 1

    #
    # download all files recursive begining current directory
    #
	def downloadAllFilesReq(self, serverPath, localPath, a_depth=10000):

		self.downloadAllFilesInFolder(localPath)
		list = []

		list = self.getDirectoriesInCurrentFolder()

		if (len(list) > 0 and self.depth < a_depth):
			i = 0

			while (i < len(list)):

				var = self.goToDirectory(list[i])
				if (var == ErrorCode.NO_ERROR) and (list[i][0] != '.'):

					if not os.path.exists(localPath + '\\' + list[i]):
						os.makedirs(localPath + '\\' + list[i])
					self.downloadAllFilesReq('',localPath + '\\' + list[i],2)

					self.goToDirectoryUp()
				i +=1
		self.depth += 1

    #
    # get directory names in current location
    #
	def getDirectoriesInCurrentFolder(self):
		if (len(self.filenames) < 1):
			self.getFileList()
		i = 0
		list = []
		while (i < len(self.filenames)):
			result = self.checkIfIsFolder(self.filenames[i])

			if (result == isFolder.YES):
				list.append(self.filenames[i])
			i += 1


		return list

    #
    # check if it is a directory
    #
	def checkIfIsFolder(self,fileName):
		retVal = isFolder.NO

		self.ftpPassive()

		self.sockData = socket(AF_INET, SOCK_STREAM)
		self.sockData.connect((self.IPdata, self.portData))

		self.sock.send('MDTM ' + fileName + '\r\n')
		tm = self.recv_timeout()
		_temp = self.analizeServerResp(tm)

		if (_temp == ErrorCode.NO_ERROR):
			retVal = isFolder.NO
		else:
			retVal = isFolder.YES

		self.sockData.close()

		return retVal

    #
    # get file list in current folder
    #
	def getFileList(self):
		self.ftpPassive()
		self.sockData = socket(AF_INET, SOCK_STREAM)
		self.sockData.connect((self.IPdata, self.portData))

		self.sock.send('LIST\r\n')

		temp = '   '
		allData = ''
		while (len(temp) > 1):
			tm = self.sockData.recv(self.bufforSize)
			temp = tm[:len(tm) - 1] + '\0'
			allData = allData + tm
		self.sockData.close()

		lines = allData.splitlines()
		i = 0

		while (i < len(lines)):
			temp = lines[i].split(' ')
			self.filenames.append(temp[-1])
			i = i + 1

		self.sockData.close()

		return 1

###############################################################################
#		                          main                                        #
###############################################################################
		
try:
	if(sys.argv[1] == '' or sys.argv[2] == ''):                 # check arguments
		print 'Bad arguments'
		print 'mirror user@ftp.server/dir/dir localdir [-n]'
	else:
		temp = sys.argv[1].split(' ')
		temp2 = temp[0].split('@')
		user = temp2[0]

		print temp2[1]
		temp3 = temp2[1].split('/',1)
		dir =  temp3[1]
		server = temp3[0]

except:
	print 'Error in args'
	print 'mirror user@ftp.server/dir/dir localdir [-n]'
	print 'mirror anonymous@ftp.man.szczecin.pl/pub/FreeBSD/tools/ /NowyFolder 3'

flag =0

if(len(sys.argv) > 3):
	flag = 1
else:
	flag = 0

print '\n\n'
password = raw_input("Get password:")       #get password from user
print '\n'

x = myFTP(user, password, server)
x.goToDirectory(dir)

if not os.path.exists(sys.argv[2]):
	os.makedirs(sys.argv[2])

if flag > 0:
	x.downloadAllFilesReq('' , sys.argv[2] , int(sys.argv[3]))
else:
	x.downloadAllFilesReq('' , sys.argv[2])


x.close()

##################################################################################

