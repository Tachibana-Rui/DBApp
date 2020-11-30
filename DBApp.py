import mysql.connector
import prettytable as pt
import os
import time

#Global containers
nodes={} #Key is DID, value is the node pointer (address)

'''
class DBAppException(Exception):
	def __init__(self,arg):
		self.arg=arg
'''
class tree:
	class node:
		def __init__(self,DID,child=[]):
			self.DID=str(DID)
			self.child=child

		def get_child_DID(self):
			result=[]
			if not self.child:
				for c in self.child:
					result.append(c.DID)
			return result

		def __str__(self):
			return self.DID+'|'+','.join(self.get_child_DID())

	def create():#Create tree in python based on database
		mycursor.execute(f"select DID,ParentDID from Department")
		myresult = mycursor.fetchall()
		#[('0', None), ('1', '0'), ('2', '0'), ('E11', '1'), ('E12', '1'), ('E13', '1'), ('F1', '2'), ('F2', '2'), ('FT1', 'F1'), ('FT2', 'F1')]
		for t in myresult:
			nodes[t[0]] = tree.node(t[0]) #Create node instances and store them in dictionary 'nodes' 
#		print(nodes)
		#Transform parent record into child record
		for d in myresult:
			if d[1]!=None:
				watch = globals()['nodes']
				nodes[d[1]].child.append(nodes[d[0]])


	def list_childs(DID):
		pass

	def _list_childs(DID):
		mycursor.execute(f"select * from Department where DID = {DID}")

def disp(cursor,*column_names):
	myresult = cursor.fetchall()
	tb = pt.PrettyTable()
	for row in myresult:
		tb.add_row(row)
	try:tb.field_names = column_names[0]
	except:pass
	print(tb)

def show_table(tableName):
	tb = pt.PrettyTable()
	try:
		mycursor.execute(f"select distinct COLUMN_NAME from information_schema.COLUMNS where table_name = '{tableName}';")
	except mysql.connector.errors.ProgrammingError:
		raise DBAppException(f"***Error. {tableName} doesn't exist")
	_column_name=mycursor.fetchall()
	column_name=[]
	for tuples in _column_name:
		temp=tuples[0]
		column_name.append(temp)
	tb.field_names = column_name

	mycursor.execute(f"select * from {tableName}")
	myresult = mycursor.fetchall()
	for row in myresult:
		tb.add_row(row)
	print(tb)

def show_all_tables(*arg):
	mycursor.execute("show tables")
	myresult = mycursor.fetchall()
	disp(mycursor,['Table'])
	for _tableName in myresult:
		time.sleep(0.5)
		show_table(f"'{_tableName[0]}'")

#MySQL command window
def MySQL_mode(query):
	query=str(query)
	mycursor.execute(query)
	tb = pt.PrettyTable()
	myresult = mycursor.fetchall()
	for row in myresult:
		tb.add_row(row)
	print(tb)

def list_childs(DID):
	tree.create()


def _list_childs(DID):
	mycursor.execute(f"select * from Department where DID = {DID}")

def change_discount(PID):
	show_table('Product')
	discount=-1.0
	while discount<0 or discount>1:
		try:discount = float(input('Enter discout (range [0:1]): '))
		except:print('Invalid input. Try again.')
	mycursor.execute(f"update Product set Discount={discount} where PID='{PID}'")
	mycursor.execute(f"select PID,Title,Discount from Product where PID='{PID}'")
	disp(mycursor,['PID','Title','Discount'])

def help(*funcName):
	if not funcName[0]:
		print('Two-letters commands are short form of their corresponding long commands')
		for i in funcDict.keys():
			print(i)
	else:
		try:print(helpDict[funcName[0]])
		except KeyError:pass

tipsDict = {'list childs':'Input Department ID.',
			'lc':'Input Department ID.',
			'change discount':'Input Product ID.',
			'cd':'Input Product ID.',
			'help':"Input function name to get specified help, or just press enter to list all commands."}

helpDict = {'list childs':'''Ask the user for a department ID (i.e., the value of the primary key) 
and list all its products (outputting the ID, the title and the retail price after the discount) 
if the given department is a leaf department, otherwise list all its child departments (outputting the ID and the title).''',
			'lc':'''Ask the user for a department ID (i.e., the value of the primary key) 
and list all its products (outputting the ID, the title and the retail price after the discount) 
if the given department is a leaf department, otherwise list all its child departments (outputting the ID and the title).''',
			'change discount':'Ask for a product ID, show the current discount and allow the user to change it.',
			'cd':'Ask for a product ID, show the current discount and allow the user to change it.',
			}


funcDict = {'show table':show_table,'st':show_table,
			'MySQL mode':MySQL_mode,'mm':MySQL_mode,
			'list childs':list_childs, 'lc':list_childs,
			'change discount':change_discount,'cd':change_discount,
			'help':help,'show all tables':show_all_tables,
			}

if __name__ == '__main__':
	group_number="77" 
	schema=["ht20_2_project_group_"+group_number]
	mydb = mysql.connector.connect(
		host="127.0.0.1",
		user="ht20_2_group_"+group_number,
		passwd="pwd_"+group_number,
		database="ht20_2_project_group_"+group_number
	)
	mycursor = mydb.cursor()
	print("Connection Successful. Type 'help' for more commands.")
	while True:
		line = input('> ')
#		try:
		if line =='exit':
			mydb.close()
			exit()
		elif line == 'clearall':
			os.system('cls')
		elif line in funcDict.keys():
			try:
				print(tipsDict[line])
			except KeyError:
				pass
			if line=='cp' or line=='change_price':
				mycursor.execute("select PID,Discount from Product")
				disp(mycursor,['PID','Discount'])
			arg = input(f'{line} > ')
			funcDict[line](arg)
		else:
			print('***Error. Unknown command')
#				raise DBAppException('***Error. Unknown command')
#		except DBAppException as e:
#			print(e)
#		except:
#			print('***Oops. Something went wrong')