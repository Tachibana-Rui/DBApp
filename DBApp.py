import mysql.connector
import prettytable as pt
import os
import time


class DBAppException(Exception):
    def __init__(self, arg):
        self.arg = arg


def disp(cursor, *column_names):
    myresult = cursor.fetchall()
    tb = pt.PrettyTable()
    for row in myresult:
        tb.add_row(row)
    try:
        tb.field_names = column_names[0]
    except:
        pass
    print(tb)


def show_table(tableName):
    tb = pt.PrettyTable()
    try:
        mycursor.execute(
            f"select distinct COLUMN_NAME from information_schema.COLUMNS where table_name = '{tableName}';")
    except mysql.connector.Error as err:
        raise DBAppException(f"***Error. {tableName} doesn't exist")
    _column_name = mycursor.fetchall()
    column_name = []
    for tuples in _column_name:
        temp = tuples[0]
        column_name.append(temp)
    tb.field_names = column_name

    try:
        mycursor.execute(f"select * from {tableName}")
    except mysql.connector.Error as err:
        raise DBAppException(f"***Error. {tableName} doesn't exist")
    myresult = mycursor.fetchall()
    for row in myresult:
        tb.add_row(row)
    print(tb)


def show_all_tables(*arg):
    mycursor.execute("show tables")
    myresult = mycursor.fetchall()
    disp(mycursor, ['Table'])
    for _tableName in myresult:
        time.sleep(0.5)
        show_table(f"'{_tableName[0]}'")

# MySQL command window


def MySQL_mode(query):
    query = str(query)
    mycursor.execute(query)
    tb = pt.PrettyTable()
    myresult = mycursor.fetchall()
    for row in myresult:
        tb.add_row(row)
    print(tb)


def get_final_price(pid):
    query = f'''
			SELECT
				RetailPriceNoVAT, VATPercent, Discount
			FROM
				Product
			WHERE PID='{pid}'
			'''

    mycursor.execute(query)
    price, vat, discount = mycursor.fetchall()[0]
    return float(price) * float(1.0 + vat) + float(1.0 - discount)


def list_childs(DID):
    query = f'''
			SELECT
				PID, Title
			FROM
				Product
			WHERE
				DID='{DID}'
			'''
    mycursor.execute(query)
    r = mycursor.fetchall()
    if len(r) != 0:
        tb = pt.PrettyTable()
        tb.field_names = ["PID", "Title", "PriceAfterDiscount"]
        for pid, title in r:
            price = get_final_price(pid)
            tb.add_row((pid, title, price))
        print(tb)
    else:
        query = f'''
			SELECT
				DID, Title
			FROM
				Department
			WHERE
				ParentDID='{DID}'
			'''
        mycursor.execute(query)

        myresult = mycursor.fetchall()
        tb = pt.PrettyTable()
        for row in myresult:
            tb.add_row(row)
        try:
            tb.field_names = ['DID', 'Title']
        except:
            pass
        print(tb)

        for did, title in myresult:
            list_childs(did)


def get_discount(PID):
    mycursor.execute(
        f"select Discount from Product where PID='{PID}'")
    r = mycursor.fetchall()
    return r[0][0]


def change_discount(PID):
    print(f"Discount: {get_discount(PID)}")
    discount = -1.0
    while discount < 0 or discount > 1:
        try:
            discount = float(input('Enter discout (range [0:1]): '))
        except:
            print('Invalid input. Try again.')
    mycursor.execute(
        f"update Product set Discount={discount} where PID='{PID}'")
    print(f"Discount: {get_discount(PID)}")


def help(*funcName):
    if not funcName[0]:
        print('Two-letters commands are short form of their corresponding long commands')
        for i in funcDict.keys():
            print(i)
    else:
        try:
            print(helpDict[funcName[0]])
        except KeyError:
            pass


tipsDict = {'list childs': 'Input Department ID.',
            'lc': 'Input Department ID.',
            'change discount': 'Input Product ID.',
            'cd': 'Input Product ID.',
            'help': "Input function name to get specified help, or just press enter to list all commands."}

helpDict = {'list childs': '''Ask the user for a department ID (i.e., the value of the primary key)
and list all its products (outputting the ID, the title and the retail price after the discount)
if the given department is a leaf department, otherwise list all its child departments (outputting the ID and the title).''',
            'lc': '''Ask the user for a department ID (i.e., the value of the primary key)
and list all its products (outputting the ID, the title and the retail price after the discount)
if the given department is a leaf department, otherwise list all its child departments (outputting the ID and the title).''',
            'change discount': 'Ask for a product ID, show the current discount and allow the user to change it.',
            'cd': 'Ask for a product ID, show the current discount and allow the user to change it.',
            }


funcDict = {'show table': show_table, 'st': show_table,
            'MySQL mode': MySQL_mode, 'mm': MySQL_mode,
            'list childs': list_childs, 'lc': list_childs,
            'change discount': change_discount, 'cd': change_discount,
            'help': help, 'show all tables': show_all_tables,
            }

if __name__ == '__main__':
    group_number = "77"
    schema = ["ht20_2_project_group_"+group_number]
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
        try:
            if line == 'exit':
                mydb.close()
                exit()
            elif line == 'clearall':
                os.system('cls')
            elif line in funcDict.keys():
                try:
                    print(tipsDict[line])
                except KeyError:
                    pass
                if line == 'cp' or line == 'change_price':
                    mycursor.execute("select PID,Discount from Product")
                    disp(mycursor, ['PID', 'Discount'])
                arg = input(f'{line} > ')
                funcDict[line](arg)
            else:
                print('***Error. Unknown command')
                raise DBAppException('***Error. Unknown command')
        except DBAppException as e:
            print(e)
        except:
            print('***Oops. Something went wrong')
