import sys

def putFunc(File):
    print("Implement put")

def getFunc(File):
    print("Implement get")

def changeFunc(File):
    print("Implement change")
    
def helpFunc():
    print("Implement help")


while 1:
    userCommand = input("myftp> ")
    userCommand = userCommand.split()
    

    if userCommand[0]  == 'put':
        if len(userCommand) < 2:
            print('Error: must include file name after "get"')
        else:
            putFunc()
    elif userCommand[0] == 'get':
        if len(userCommand) < 2:
            print('Error: must include file name after "put"')
        else:
            getFunc()
    elif userCommand[0] == 'change':
        if len(userCommand) < 3:
            print('Error: must include both file names after "change"')
        else:
            changeFunc()
    elif userCommand[0] == 'help':
        helpFunc()
    elif userCommand[0] == 'bye':
        print('Bye')
        sys.exit()
    else:
        print('This is not a valid command')