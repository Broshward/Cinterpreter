#!/usr/bin/python2

import sys
import os
import serial
import re
import time

embedded=1 #Temporarily action

""" driver variable may be defined as: 
    'UART' - for UART connection interpreter targets
    'internal' - for direct access memory on target
"""
driver='UART' # For UART connection interpreter targets


def port_setup(dev):
	global port
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
defines={}		# dict of defines in parsing code. Example: #define foo foooo
files=[]		# List of includes (for log info)
functions={}   # functions contents

cvars={}
last={'struct':0,'union':0,'enum':0}

#----- Standart base types of C -----------------
types={ 'char':1, 'short':2, 'int':4, 'float':4, 'double':8, 'void':0 }
#sizes={ 'char':1, 'short':2 'int':4, 'float':4, 'double':8, 'void':0 }
#types={}

#C_char  = type('char',(),{})
#C_char.size=1
#C_int   = type('int' ,(),{})
#C_int.size=4
#C_void  = type('void',(),{})
#C_void.size=0
#----- Standart base types of C -----------------

#types={
#    'char':globals()['C_char'],
#    'int':globals()['C_int'],
#    'void':globals()['C_void'],
#} #temporarily contains many types (some library defined, example in /usr/include/stdint.c'). Reason of this - BUG in the parse_logic_expr function

global_inc=['/usr/include'] # Path to search global system include files
local_inc=['.']				# Path to search local includes. Equivalent of -I gcc compiler options
        
def write_var(dest,source): # This funtion is interface (driver) of memory or external device content usage
	if embedded: #This is temporarily solve. At the time this expressions will changed with universally interface function for interraction with ports and memory
		global port
		if 'port' in globals():
			print dest.addr
			device_addr = pre_compile('PIPE_ADDRESS').value
			if dest.addr: # write to embedded memory
				command = 9 + dest.Type.size
			elif temp_var.addr: # read to embedded memory
				command = -9 - dest.Type.size
				#read_var(var,temp_var)
			if dest.Type.size==0:
				print 'Undeclared identifier: ', dest.text
			elif dest.Type.size == 1:
				content=[12,10,0,5]
				data=[source.value]
			elif dest.Type.size == 2:
				content=[12,11,0,6]
				data=[source.value>>i*8 & 0xFF for i in range(dest.Type.size)]
			elif dest.Type.size == 4:
				content=[12,14,0,8]
				data=[source.value>>i*8 & 0xFF for i in range(dest.Type.size)]
			for i in range(4):
				content.append((dest.addr>>(i*8)) & 0xFF)
			content+=data
			CS=0
			for i in content:
				CS^=i
			content.append(CS)
			print port.write(content)
		else:
			print 'port not exist'
		dest.value = source.value
	else:
		dest.value = source.value
	return

def vargen (Type,addr=None,value=None): #generate variables
    global cvars
    var=Type()
    var.addr = addr
    var.value = value
    return var


def typegen (in_str): #generate or search types
        global types, cvars, last
        return_str = in_str[:in_str.find(';')+1]
        if '{' in return_str:
            m,n=find_block(in_str)
            type_descr=in_str[:n].strip().rsplit(None,1)[1]
            if type_descr in ['struct','union','enum']: #parse fields of complex type ';'
                Type={}
                fields=in_str[n,m].split(';')
                addr=0
                for i in range(fields.count())):
                    type_str,name=fields[i].strip(),split()
                    if type_str in types.keys():
                        Type[name] = [type_str,addr]
                        addr += sizeof(type_str)
                    

            end=in_str[n:].find(';')
            end=n+1 if end<0 else end+n+1
                import pdb; pdb.set_trace()
            return_str = in_str[:end]
        type_str = return_str[:-1]
        print 'New type string: \n',type_str

        if type_str.startswith('typedef'):
            type_str=type_str[7:].lstrip()
            names = type_str.split(',')
            type_str,names[0] = names[0].rstrip().rsplit(None,1)
            print type_str, names
            if type_str in types.keys():
                Type=type_str
            else:
                Type=typegen(type_str)
            for i in names:
                types[i.strip()]=Type
            return Type,return_str
#type(i,(Type,),{})

        if type_str.startswith('struct') or type_str.startswith('union'):
            type_descr,type_str=type_str.split(None,1)
            if not type_str.startswith('{'):
                name,type_str=type_str.split('{',1)
                name.strip()
            else:
                name = str(last[type_str])
                last[type_str]+=1
         ??   type_str = type_str.rsplit('}',1)
            if len(type_str)==2:
                type_str,var_names = type_str
            else:
                type_str,var_names = type_str[0],None
            type_str = type_str[1:].strip()
            while 'struct' in type_str or 'union' in type_str:
                struct_inside = type_str.find('struct')
                if struct_inside > type_str.find('union'):
                    struct_inside = type_str.find('union')
                    temp=typegen(type_str[struct_inside:])

            fields=type_str.split(';')
            Type=type(type_descr+'_'+name,(),{})
            faddr=0
            for i in fields:
                try:ftype,fname = i.rsplit(None,1)
                except:import pdb; pdb.set_trace()
                ftype=ftype.strip()
                fname=fname.strip()
                ftype=typegen(ftype)
                f=vargen(ftype,faddr)
                faddr+=ftype.size #f.size
                setattr(Type,fname,f)
            if var_names != None:
                for i in var_names.split(','):
                    v_name=i.strip()
                    if v_name not in cvars.keys():
                        cvars[vname] = vargen(Type)
                    else:
                        print 'Variable %s already defined' %(vname)

        if type_str in types.keys():
            Type = types[type_str]
        else:
            print 'Type not defined %s' %(type_str)
            Type = type('typestr', (), {})

        return Type,return_str

def var_gen(var_str,var=None): #vars detection define or expression solve
	global cvars
	var_str = var_str.strip()

	if re.search('^0x|X[0-9a-fA-F]+$',var_str):
		var = VAR(types['int'])
		var.value = int(var_str,16)
		return var
	elif re.search('^[0-9]+$',var_str):
		var = VAR(types['int'])
		var.value = int(var_str)
		return var
	elif re.search('^0b|B[01]+$',var_str):
		var = VAR(types['int'])
		var.value = int(var_str)
		return var
	elif re.search('^[0-9]*\.[0-9]+$',var_str):
		var = VAR(types['float'])
		var.value = float(var_str)
		return var
		
	elif var_str in types.keys():
		var = VAR(types[var_str],'',None)
		return var
	elif var_str in cvars.keys():#search addr_str in cvars
		return cvars[var_str]
	else:
		temp = re.search('^(\w+)\s*(\**)\s*$',var_str) 
		if temp:
			if temp.group(1) in types.keys():
				var = VAR(types[temp.group(1)],temp.group(2),None)
				return var
			else:
				print 'file - line - : Unknown type %s' %(temp.group(1))
				print 'content: %s' %(var_str)
				exit()

	#ss = re.search('\([^()]*\)',var_str) # Internal bracket pattern (brackets without included brackets) May be useful

	temp_var,operator=None,None
	while len(var_str)>0:
		var_str=var_str.strip()
		if var_str[0] == '(':
			temp_var = var_gen(var_str[1:find_block(var_str,'(',')')[1]])
			var_str = var_str[find_block(var_str,'(',')')[1]+1:].strip()
		elif var_str[0] == '=':
			temp_var = var_gen(var_str[1:])
			operator = '='
			var_str=''
		else:
			temp = re.search('^\w+',var_str)
			if temp:
				var_str = var_str[temp.end():].strip()
				temp_var = var_gen(temp.group())
				if not temp_var:
					temp_var = temp.group() # string text variable
			else:	
				temp = re.search('^[^\w\s]+',var_str)
				if temp:
					var_str = var_str[temp.end():].strip()
					operator = temp.group()
				else:
					print 'file _ line _: unexpected symbol "%s"' %(var_str[0])
					print 'content: %s' %(var_str)
					exit()
		if not var:
			if temp_var:
				var = temp_var
				if operator:
					var.description+=operator
				temp_var=None
				operator=None
		else:
			if operator and operator in '->.':
				temp = re.search('^\w+',var_str)
				if not temp:
					print 'file _ line _: expected struct field'
					print 'content: %s' %(var_str)
					#break
					exit()
				bias = flag = 0
				for i in var.Type.types: #search field of struct
					if i.name == temp.group():
						i.addr = var.value + bias
						var=i
						flag=1
						break
					bias += i.Type.size
				var_str=var_str[temp.end():]
				temp_var = operator = None
				if flag ==0:
					print 'file _ line _: This struct do not contained field %s' %(temp.group())
					print 'content: %s' %(var_str)
					exit()
			elif operator == '=':
				write_var(var,temp_var)
			elif temp_var:
				if operator:
					var.value = eval(str(var.value) + operator + str(temp_var.value)) 
				else: # typecasting
					if var.value==None:
						var.value = temp_var.value 
					else:
						print 'file _ line _: Expected operator ', var_str
						print 'content: %s' %(var_str)
	return var
	

def if_endif_remove(in_str):
	while '#if' in in_str:
		beg_if = in_str.find('#if')
		in_str = in_str[:beg_if] + if_def_parser(in_str[beg_if:])
	return in_str

def comment_remove(in_str):
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
	if not dirname.endswith('/'):
		dirname+='/'
	listdir = os.listdir(dirname)
	if filename in listdir:
		file = (dirname+filename)
	else:file=None
#	for i in listdir:									#for recursive search
#		if i.startswith('.'):							#for recursive search
#			continue									#for recursive search
#		if os.path.isdir(dirname+i):					#for recursive search
#			files+=file_search(dirname+i,filename)		#for recursive search
	return file

def parse_logic_expr(logic_str,true_list):
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
	#cond_str=comment_remove(cond_str)
	cond_str=cond_str.replace('defined','')
	return parse_logic_expr(cond_str,true_list)

#-----------#if #endif parse-------------
def if_def_parser(in_str):
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
	directive_index=0
	string_num = 0
#----- comment remove-----
	in_str = re.sub('/\*.*?\*/', lambda m: '\n'*m.group().count('\n'), in_str,flags=re.DOTALL)
	in_str = re.sub('//.*?\n','\n',in_str,flags=re.DOTALL)
#----- comment remove-----
	
	print 'Precompile: %s' %(parse_file) 
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
#					for i in global_inc:
#						files_to_parse=file_search(i,inc_str[1:-1]) #?-1
##					if len(files_to_parse)>0:
##						parse('',','.join(files_to_parse))
				elif inc_str[0] == '"' and inc_str[-1]=='"':
					for i in local_inc:
						file_to_parse=file_search(i,inc_str[1:-1])
						if file_to_parse:
							inc_file=open(file_to_parse,'r')
							parse(inc_file.read(),parse_file=file_to_parse)
							inc_file.close()
                                                        files.append(file_to_parse)
                                                        break
                                        if not file_to_parse:
                                            print 'Included ',file_to_parse,' file not founded'
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

def launch(in_str,autocomplete,parse_file=''):
	global defines, files_to_parse, types, cvars, files
	print 'Compile: %s' %(parse_file) 
	directive_index=string_num=0
	while directive_index<len(in_str):
		match_obj = re.search('\S+',in_str[directive_index:], re.DOTALL)
		if match_obj == None:
			break
		string_num += in_str[directive_index:match_obj.start()].count('\n')
		directive_index += match_obj.start()
		directive=match_obj.group()

		if directive in 'typedef enum struct union': # New type generation, but 'enum' is not a type, this is some const variables
		    Type,type_str=typegen(in_str[directive_index:])	
                    in_str=in_str.replace(type_str,'\n'*type_str.count('\n'),1)
		    directive_index += type_str.count('\n')+1
		    continue


#		elif directive in types.keys(): #variable or function declaration
#			block = re.search('^%s\s+(.*?);' %(directive),in_str[directive_index:],re.DOTALL)
#			if re.search('^%s(\s+\w+)+\s*\(.*?\).*?;' %(directive),block.group(),re.DOTALL): #function definition
#				if '{' in block.group(): #full function definition
#					m,n=find_block(in_str[directive_index:])
#					block = re.search('^%s\s+(\w+)\s*\(.*?\)\s*(\{.{%d})' %(directive,n-m),in_str[directive_index:],re.DOTALL) 
#                                        functions[block.group(1)]=block.group(2)[1:-1].strip()
#				else:#prototype of function
#					None
#			else: #definition variable 
#				for temp in block.group(1).split(','):
#					temp = temp.split('=')
#					name_str, value_str = (temp[0],0) if len(temp)==1 else temp
#					cvars[name_str.strip()] = VAR(types[directive],value_str)
#			directive_index += block.end()
#			continue
#			
#			
#		else: #---------Other user defined description parse (not compiler directive and not specific words)
#			block = re.search('^(.*?);|$', in_str[directive_index:],re.DOTALL)
#			if block!=None:
#				print block.group()
#				if '=' in block.group():
#					None
#					var_str,value_str = block.group(1).split('=')
#					var_str=var_str.strip()
#					value_str=value_str.strip()
#					var = var_gen(block.group(1))  #temporarily
#					#var=var_gen(var_str)		 #temporarily
#					#print var.addr					 #temporarily
#					#var.text = var_str               #temporarily
#					#try:value = eval(value_str)          #temporarily
#					#except:print parse_file
#					#write_addr(var,value)
#					#cvars.addvar(var)
#
#				directive_index += block.end()
#				continue
#			if directive.startswith('('): # to type example (char) var = foo
#				directive = re.search('\(\s*\w+\s*\)\s*=\s*({.*?})?.*?;',in_str[directive_index:],re.DOTALL)
#				type_str = re.search('\(.+?\)',directive,re.DOTALL)
#				if type_str != None:
#					Type = types.get(type_str)
#				else:continue
#				if Type == None:
#					continue
#
#					# find '=', var name or address, value, value to var
#			elif directive in types.keys():
#				temp_str = in_str[directive_index:].split(';',1)[0]
#				if '(' in temp_str:
#					# ADD function
#					None
#				else:
#					type_name,var_name=temp_str.strip().split(None,1)
#					if '=' in var_name:
#						var_name,value = var_name.split('=',1)
#					else:
#						value=0
#					var_name=var_name.strip()
#					type_name=type_name.strip()
#					cvars[var_name] = VAR(types[type_name],value)
#					
#				None
#				#in_str = in_str[:directive_index] + in_str[directive_index:].replace(directive,typedefs.get(directive), 1)
#			elif directive in cvars.keys():
#				None
#			elif directive in enums.keys():
#				None
#			elif directive in structs.keys():
#				None

#----find block---------------
#			end_dir = in_str[directive_index:].find(';')
#			if end_dir<0:
#				print 'Warning: semicolon expected' 
#			else:end_dir+= directive_index
#			if '{' in in_str[directive_index:end_dir]:
#				end_dir = find_block(in_str[directive_index:])[1]
#				end_dir += in_str[end_dir:].find(';')
#				end_dir += directive_index
##----------------parse block---------------
#				other_str = block_thret(in_str[directive_index:end_dir])
#			else:
#				other_str = in_str[directive_index:end_dir]
##----find block---------------
#			if '=' in other_str:
#				in_str = in_str[:directive_index] + in_str[end_dir+1:]
#				try:var_str,value_str = other_str.split('=')
#				except:print other_str
#				var_str = var_str.strip()
#				if len(var_str.split()) > 1 and not var_str.startswith('('):
#					#definition 
#					None
#				else: 
#					var = calculate_addr(var_str)
#					print var.addr
#					if var.Type.size == 0:
#						# variable not defined
#						None
#				var.text = var_str
#				value = eval(value_str)
#				write_addr(var,value)
#				#cvars.addvar(var)
#			else:
#				if autocomplete==True: # for human autocomplete available
#					#resolving other_str string with all (defines,typedefs and etc.)
#					var = calculate_addr(other_str)
#					return var
#					#in_str = in_str[:directive_index]
#				else:
#					#------------add variable to vars-----------------
#					#cvars.__dict__[other_str.rsplit(None,1)[1]]
#					#eval('...')
#					#exec '....'
#					#object.__dict__
#					print 'line ', string_num, ": '", directive, "' is not declarated" 
#					#exit(1)
		directive_index += len(directive)
	return in_str

def parse(c_code, autocomplete=False,parse_file=''):
	global defines, files_to_parse, types, cvars
#	global files_to_parse
	content = c_code.splitlines(True)


#--------comment remove--------------------------------------
#	for j in range(0,len(content)):
#		content[j]=content[j].split('//',1)[0]
	line_content = ''.join(content) + ' '
#	i=0
#	comm_count=0
#	while i<len(line_content)-1:
#		if line_content[i:i+2] == '*/':
#			comm_count+=1
#			end_comm = i+2
#			i-=2
#			while line_content[i:i+2]!='/*':
#				i-=1
#				if i<0:
#					print 'comment error'
#					return None
#			beg_comm=i
#			line_content = line_content[:beg_comm] + line_content[end_comm:]
#		i+=1   

#		while '/*' in line_content:
#			comm_beg = line_content.find('/*')
#			comm_end = line_content.find('*/')
#			line_content=line_content[:comm_beg] + line_content[comm_end+2:]
#--------comment remove--------------------------------------

#---------carry remove----------------------------
	while '\\\r\n' in line_content:
		line_content = line_content.split('\\\r\n',1)[0] +' '+ line_content.split('\\\r\n',1)[1].strip()
	while '\\\n' in line_content:
		line_content = line_content.split('\\\n',1)[0] +' '+ line_content.split('\\\n',1)[1].strip()
#---------carry remove----------------------------

	line_content = pre_compile(line_content, autocomplete, parse_file=parse_file)	#------------#if #endif resolve
	line_content = launch(line_content, autocomplete, parse_file=parse_file)	#------------#if #endif resolve
	#print line_content

#---------Empty string remove-------------------------------		
#	content=[]
#	for i in line_content.split('\n'):
#		i=i.rstrip()
#		if i!='':
#			content.append(i)
#	line_content = '\n'.join(content)
#---------Empty string remove-------------------------------		

#	file=open('temp_parse.h','w')
#	file.write(line_content)
#	file.close()

        print 'Defines:'
        print defines, '\n'
        print 'Types:'
        print types, '\n'
#        print 'Vars:'
#        print cvars, '\n'
        

#	file=open('results','w')
#	file.write('Defines\n')
#	file.write(str(defines))
#	file.write('\nStructs\n')
#	file.write(str(structs))
#	file.write('\nEnums\n')
#	file.write(str(enums))
#	file.write('\nTypedefs\n')
#	file.write(str(typedefs))
#	file.close()

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
    C_code = open(sys.argv[1]).read()
    parse(C_code,parse_file=sys.argv[1])
    #print parse('',parse_file=sys.argv[1])
