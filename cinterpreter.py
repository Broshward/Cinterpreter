#!/usr/bin/python2
#coding:utf8

import sys
import os
import serial
import re
import time

debug = True
embedded=True #Temporarily action. For using variables in outside system(Brygði-OS microcontroller) throught USART interaction
PATH='/home/leha/work/Electronics/greenhouse/Brig-iOS'

sys.path.append(PATH)
from interact import *
interact=interact()

""" driver variable may be defined as: 
    'UART' - for UART connection interpreter targets
    'internal' - for direct access memory on target
"""
driver='UART' # For UART connection interpreter targets

def get_addr_from_elf(name):
    addr = os.popen('readelf -s %s/main.elf |grep -o \'.*%s$\'' %(PATH,name)).read().strip().split()[1]
    if debug:
        print 'Current function is %s!' %(sys._getframe().f_code.co_name)
        print 'Name = %s, addr = %s' %(name,addr)
    return int(addr,16)
    

def port_setup(dev):
    global port
    if debug:
        print 'Current function is %s in file %s!' %(sys._getframe().f_code.co_name,parse_file)
    try:
        if port.isOpen():
            port.close()
    except:None
    try:
        port=serial.Serial(port=dev,baudrate=pre_compile('USART_SPEED').value)
        port.open()
    except:print 'Could not conigure port ',dev

    return


pre_defines=[] # equivalent of -D compiler options.Example: -Dfoo
defines={}      # dict of defines in parsing code. Example: #define foo foooo
files=[]        # List of includes (for log info)
functions={}   # functions contents

cvars={}
last={'struct':0,'union':0,'enum':0}

#----- Standart base types of C -----------------
#types={ 'char':1, 'short':2, 'int':4, 'float':4, 'double':8, 'void':0 }
types={ 'char':'b', 'short':'h', 'int':'w', 'float':4, 'double':8, 'void':0 }
# Simple TYPE is a Number, which described size of type

global_inc=['/usr/include'] # Path to search global system include files
local_inc=['.']             # Path to search local includes. Equivalent of -I gcc compiler options

def set_var(var,value): # This funtion is interface (driver) of memory or external device content usage
    global embedded
    if debug:
        print 'Current function is %s!' %(sys._getframe().f_code.co_name)
        print 'var = ',var
        print 'value = ',value

    _type = var['type']
    
    if embedded: #This is temporarily solve. At the time this expressions will changed with universally interface function for interraction with ports and memory
        if _type.startswith('*'):
            cmd="Ww:%x=%x" %(var['addr'],value)
        else:
            cmd="W%s:%x=%x" %(types[var['type']],var['addr'],value)
        print cmd
        #interract.interact(cmd)
        var['value'] = value
    else:
        var['value'] = value

def get_var(var):
    return

def if_endif_remove(in_str):
    if debug:
        print 'Current function is %s!' %(sys._getframe().f_code.co_name)
    while '#if' in in_str:
        beg_if = in_str.find('#if')
        in_str = in_str[:beg_if] + if_def_parser(in_str[beg_if:])
    return in_str

def comment_remove(in_str):
    if debug:
        print 'Current function is %s in file %s!' %(sys._getframe().f_code.co_name,parse_file)
    while '//' in in_str:
        beg = in_str.find('//')
        end = in_str.find('\n')+1 if beg!=-1 else -1
        in_str = in_str[:beg] + in_str[end:]
    while '/*' in in_str:
        beg = in_str.find('/*')
        end = in_str.find('*/')+2 if beg!=-1 else -1
        in_str = in_str[:beg] + in_str[end:]
    return in_str

def find_block(in_str,beg_ch='{',end_ch='}'):
    if debug:
        print 'Current function is %s!' %(sys._getframe().f_code.co_name)
    power=0
    i=beg=end=0
    while i<len(in_str):
        if in_str[i]==beg_ch:
            if power == 0:
                beg=i
            power +=1
        elif in_str[i]==end_ch:
            if power<2:
                end=i
                break
            power -= 1
        i+=1   
    return beg,end #begin and end is relative indexes of block

def file_search(dirname,filename):
    if debug:
        print 'Current function is %s!' %(sys._getframe().f_code.co_name)
    if not dirname.endswith('/'):
        dirname+='/'
    listdir = os.listdir(dirname)
    if filename in listdir:
        file = (dirname+filename)
    else:file=None
#   for i in listdir:                                   #for recursive search
#       if i.startswith('.'):                           #for recursive search
#           continue                                    #for recursive search
#       if os.path.isdir(dirname+i):                    #for recursive search
#           files+=file_search(dirname+i,filename)      #for recursive search
    return file

def parse_logic_expr(logic_str,true_list):
    if debug:
        print 'Current function is %s!' %(sys._getframe().f_code.co_name)
    save_str=logic_str
    logic_str=logic_str.strip()
    i=0
#-------------Bracket recurive parser--------------------
    while i<len(logic_str):
        if logic_str[i]==')':
            end=i+1
            while logic_str[i]!='(':
                i-=1
                if i<0:
                    print 'Brackets error'
                    return None
            beg=i
            try:
                logic_str=logic_str[:beg]+parse_logic_expr(logic_str[beg+1:end-1],true_list)+logic_str[end:]
            except:
                print logic_str
        i+=1   
#-------------Bracket recurive parser--------------------

#-------------List generate from string----------
    logic_str=logic_str.replace('||',' or ')
    logic_str=logic_str.replace('&&',' and ')
    logic_str=logic_str.replace('!',' not ')
    logic_list=logic_str.split()
#-------------List generate from string----------

#-------------Resolve logic items----------------
    for i in range(len(logic_list)):
        if (logic_list[i] not in ['or','and','not']): 
            if (logic_list[i] in (true_list+['True'])):
                logic_list[i]=False if logic_list[i-1]=='not' else True
            else:
                logic_list[i]=True if logic_list[i-1]=='not' else False
#-------------Resolve logic items----------------

#-------------Remove 'not'-------------------------
    while 'not' in logic_list:
        try:
            logic_list.remove('not')
        except:
            None
#-------------Remove 'not'-------------------------

#-------------Resolve logic expression----------------
    while len(logic_list)>1:
        if logic_list[1]=='or':
            logic_list[2]=logic_list[0] or logic_list[2]
        elif logic_list[1]=='and':
            logic_list[2]=logic_list[0] and logic_list[2]
        logic_list = logic_list[2:]
#-------------Resolve logic expression----------------
    try:
        return 'True' if logic_list[0] else 'False'
    except:
        print save_str

def parse_cond(cond_str,true_list):
    if debug:
        print 'Current function is %s!' %(sys._getframe().f_code.co_name)
    #cond_str=comment_remove(cond_str)
    cond_str=cond_str.replace('defined','')
    return parse_logic_expr(cond_str,true_list)

#-----------#if #endif parse-------------
def if_def_parser(in_str):
    if debug:
        print 'Current function is %s!' %(sys._getframe().f_code.co_name)
    power=0
    res_beg_pos = res_end_pos = 0
    i=0
    while i<len(in_str):
        if in_str[i:i+len('#if')] == '#if' or in_str[i:i+len('#elif')] == '#elif':
            if in_str[i:i+len('#if')] == '#if':
                power+=1
            if power==1:
                if in_str.split(None,1)[0]=='#ifndef':
                    cond_str='!('+in_str.split(None,1)[1].split('\n',1)[0]+')'
                else:
                    cond_str=in_str.split(None,1)[1].split('\n',1)[0]
                if parse_cond(cond_str,pre_defines+defines.keys())=='True':
                    res_beg_pos = in_str[i:].find('\n')+1
                elif res_beg_pos !=0:
                    res_end_pos = i
        elif in_str[i:i+len('#else')] == '#else':
            if power==1:
                if res_beg_pos == res_end_pos == 0:
                    res_beg_pos = i + len('#else')
                elif res_beg_pos !=0 and res_end_pos == 0:
                    res_end_pos = i
        elif in_str[i:i+len('#endif')] == '#endif':
            if power==1:
                if res_beg_pos !=0 and res_end_pos == 0:
                    res_end_pos = i
                if res_beg_pos !=0 and res_end_pos != 0:
                    return in_str[res_beg_pos:res_end_pos] + in_str[i+len('#endif')+1:]
                else:
                    return in_str[i+len('#endif')+1:]
            power-=1
        i+=1
#-----------#if #endif parse-------------

def pre_compile(in_str,autocomplete,parse_file=''):
    global defines, files_to_parse, types, cvars, files
    if debug:
        print 'Current function is %s in file %s!' %(sys._getframe().f_code.co_name,parse_file)
    directive_index=0
    string_num = 0
#----- comment remove-----
    in_str = re.sub('/\*.*?\*/', lambda m: '\n'*m.group().count('\n'), in_str,flags=re.DOTALL)
    in_str = re.sub('//.*?\n','\n',in_str,flags=re.DOTALL)
#----- comment remove-----
    
    while directive_index<len(in_str):
        match_obj = re.search('#?\w+',in_str[directive_index:], re.DOTALL)
        if match_obj == None:
            break
        string_num += in_str[directive_index:match_obj.start()].count('\n') #Begin of curren
        directive_index += match_obj.start()
        directive=match_obj.group()

        if directive.startswith('#'):
            if directive == '#define':
#--------- #define parse------------
                end_dir=directive_index + in_str[directive_index:].find('\n')
                temp_list=(in_str[directive_index+len('#define'):end_dir]).strip().split()
                defines[temp_list[0]] = ' '.join(temp_list[1:])
                in_str = in_str[:directive_index] + in_str[end_dir+1:] if end_dir!=-1 else ''
#--------- #define parse------------
#-----------#if #endif parse-------------
            elif directive.startswith('#if'):
                in_str = in_str[:directive_index] + if_def_parser(in_str[directive_index:])
#-----------#if #endif parse-------------
            elif directive == '#include':
                end_dir=in_str[directive_index:].find('\n')
                if end_dir!=-1:
                    end_dir+=directive_index
                else:
                    end_dir=None
                inc_str = in_str[directive_index:end_dir].split(None,1)[1].strip()
                if inc_str[0] == '<' and inc_str[-1]=='>':
                    None
#                   for i in global_inc:
#                       files_to_parse=file_search(i,inc_str[1:-1]) #?-1
##                  if len(files_to_parse)>0:
##                      parse('',','.join(files_to_parse))
                elif inc_str[0] == '"' and inc_str[-1]=='"':
                    for i in local_inc:
                        file_to_parse=file_search(i,inc_str[1:-1])
                        if file_to_parse:
                            #import pdb; pdb.set_trace()
                            inc_file=open(file_to_parse,'r')
                            parse(inc_file.read(),parse_file=file_to_parse)
                            inc_file.close()
                            files.append(file_to_parse)
                            #break
                        else:
                            print 'Included ',file_to_parse,' file not founded'
                            exit(1)
                else:
                    print 'Error #include directive in file %s, string %d' %(parse_file,in_str[:directive_index].count('\n'))
                    exit(1)
                in_str = in_str[:directive_index] + in_str[end_dir:] if end_dir!=None else ''
            else: 
                end_dir=directive_index + in_str[directive_index:].find('\n')
                in_str = in_str[:directive_index] + in_str[end_dir+1:] if end_dir!=-1 else ''

        elif directive in defines.keys(): #Replacing above defined symbols
            in_str = in_str[:directive_index] + in_str[directive_index:].replace(directive,defines.get(directive), 1)
        elif directive in ['static', 'volatile', 'inline', 'const', '__INLINE', 'extern', 'signed', 'unsigned'] : # At present ignore keywords
            in_str=in_str[:directive_index] + in_str[directive_index:].replace(directive,'',1)
        else:
            if directive=='':
                directive_index+=1
            else:
                directive_index += len(directive)
    return in_str

def type_search(in_str):
    if '{' in return_str:
        m,n=find_block(in_str)
        type_descr=in_str[:n].strip().rsplit(None,1)[1]
        if type_descr in ['struct','union','enum']: #parse fields of complex type ';'
            Type={}
            fields=in_str[n,m].split(';')
            addr=0
            for i in range(fields.count()):
                type_str,name=fields[i].strip().split()
                if type_str in types.keys():
                    Type[name] = [type_str,addr]
                    addr += sizeof(type_str)
                

        end=in_str[n:].find(';')
        end=n+1 if end<0 else end+n+1
        return_str = in_str[:end]
    type_str = return_str[:-1]
    print 'New type string: \n',type_str
    print

def var_decl(type_name,var_name):
    global types,cvars
    if debug:
        print 'Current function is %s' %(sys._getframe().f_code.co_name)
        print 'type_name = %s, var_name = %s' %(type_name,var_name)
    if type_name not in types.keys():
        print 'Error: Type \"%s\" not defined!' %(type_name)
        exit(-1)
    if var_name in cvars.keys():
        print 'Error: Duplicate variable declaration! \"%s\" = ' %(var_name), cvars[var_name]
        exit(1)
    cvars[var_name] = {'type':type_name, 'addr':get_addr_from_elf(var_name)}

def launch(in_str,autocomplete,parse_file=''):
    global defines, types, cvars
    if debug:
        print 'Current function is %s in file %s!' %(sys._getframe().f_code.co_name,parse_file)
    directive_index = 0
    string_num = 0
    print in_str
    while directive_index<len(in_str):
        if in_str[directive_index].isspace() or in_str[directive_index]==';':
            directive_index += len(in_str[directive_index:]) - len(in_str[directive_index:].lstrip())

        exec_str = in_str[directive_index:].split(';',1)[0]
        if '{' in exec_str:
            b,e=find_block(in_str[directive_index:])
            exec_str = in_str[e:].find(';')
            exec_str = in_str[directive_index:e+exec_str]

        if exec_str.split()[0] == 'typedef':
            # Generate type declaration
            _type = type_decl(exec_str.split(None,1)[1].rsplit('}',1)[0]+'}')
            # Remove type declaration from in_str
            in_str = in_str.replace(exec_str,'\n'*exec_str.count('\n'))
            directive_index+=len(exec_str)
            continue

        if exec_str.split()[0] in 'enum struct union': # New type generation, but 'enum' is not a type, this is some const variables
            type_name = type_decl(exec_str.rsplit('}',1)[0]+'}')
            #replace type definition with declared type and in in_str too
            in_str = in_str.replace(exec_str,'\n'*exec_str.count('\n')+type_name)
            exec_str = exec_str.replace(exec_str,type_name)

        if exec_str.split()[0] in types.keys():
            # Var declaration
            type_name,var_name = exec_str.split()[0:2]
            var_decl(type_name,var_name)
            cont = exec_str.find(exec_str.split()[1])
            in_str = in_str[:directive_index] + in_str[directive_index+cont:]
            exec_str = exec_str[cont:]

        if exec_str.split()[0] in cvars.keys():
            if '=' in exec_str:
                var,value = exec_str.split('=',1)
                var = cvars[var.strip()]
                set_var(var,eval(value))

        if exec_str.split()[0] in ['if','for','while','do']:
            # For if operator and loops
            None


        directive_index+=len(exec_str)
    return in_str

def parse(c_code, autocomplete=False,parse_file=''):
    if debug:
        print 'Current function is %s in file %s!' %(sys._getframe().f_code.co_name,parse_file)
    global defines, files_to_parse, types, cvars
#   global files_to_parse
    content = c_code.splitlines(True)

#--------comment remove--------------------------------------
#   for j in range(0,len(content)):
#       content[j]=content[j].split('//',1)[0]
    line_content = ''.join(content) + ' '
#   i=0
#   comm_count=0
#   while i<len(line_content)-1:
#       if line_content[i:i+2] == '*/':
#           comm_count+=1
#           end_comm = i+2
#           i-=2
#           while line_content[i:i+2]!='/*':
#               i-=1
#               if i<0:
#                   print 'comment error'
#                   return None
#           beg_comm=i
#           line_content = line_content[:beg_comm] + line_content[end_comm:]
#       i+=1   

#       while '/*' in line_content:
#           comm_beg = line_content.find('/*')
#           comm_end = line_content.find('*/')
#           line_content=line_content[:comm_beg] + line_content[comm_end+2:]
#--------comment remove--------------------------------------

#---------carry remove----------------------------
    while '\\\r\n' in line_content:
        line_content = line_content.split('\\\r\n',1)[0] +' '+ line_content.split('\\\r\n',1)[1].strip()
    while '\\\n' in line_content:
        line_content = line_content.split('\\\n',1)[0] +' '+ line_content.split('\\\n',1)[1].strip()
#---------carry remove----------------------------

#    if debug:
#        print 'c_code = ',c_code
#        print
#        print 'line_content = ', line_content

    line_content = pre_compile(line_content, autocomplete, parse_file=parse_file)   #------------#if #endif resolve
    line_content = launch(line_content, autocomplete, parse_file=parse_file)    #------------#if #endif resolve
    #print line_content

    if debug:
        print 'Defines:'
        print defines, '\n'
        print 'Types:'
        print types, '\n'
        print 'Vars:'
        print cvars, '\n'
        

#   file=open('results','w')
#   file.write('Defines\n')
#   file.write(str(defines))
#   file.write('\nStructs\n')
#   file.write(str(structs))
#   file.write('\nEnums\n')
#   file.write(str(enums))
#   file.write('\nTypedefs\n')
#   file.write(str(typedefs))
#   file.close()

    return line_content

if __name__=='__main__':
    i=0
    while i<len(sys.argv):
        if '-I' == sys.argv[i][:2]:
            inc_dir = sys.argv[i][2:]
            if inc_dir != '':
                local_inc.append(inc_dir)
            else:
                local_inc.append(sys.argv[i+1])
                sys.argv.pop(i+1)
            sys.argv.pop(i)
        else:
            i+=1
    if os.path.isfile(sys.argv[1]):
        C_code = open(sys.argv[1]).read()
    else: 
        C_code = ''.join(sys.argv[1:])
    parse(C_code)
    #print parse('',parse_file=sys.argv[1])
