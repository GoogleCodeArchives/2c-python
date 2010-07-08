"""2c.py  -- Python-to-C compiler"""
Author = "Bulatov Vladislav"

## 2c.py is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.

## 2c.py is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

import types

def _f(f): 
    if f.endswith('.pyc'):
        f = f[:-4] + '.py'
    if f.endswith('.pyo'):
        f = f[:-4] + '.py'
    assert f.endswith('.py')    
    return hash(open(f).read())

hash_2c = _f(__file__)
_c_2c = None

if type(_f.func_code) is types.CodeType and __name__ == '__main__': 
    try:
        import _c_2c
    except:
        pass
    if _c_2c is not None and hasattr(_c_2c, '__compile_hash__') and _c_2c.__compile_hash__ == hash_2c:   
        print 'Run compiled...' 
        _c_2c.main()
        exit(0) ## others -- not need

import sys
import pprint
import glob
import traceback
import gc
import os
import time

## impo = __import__

## def __import__(*a):
    ## if len(a) > 1:
        ## print '__imp__', a[0]
    ## else:    
        ## print '__imp__', a
    ## return impo(*a)

d_built = {'ArithmeticError': ArithmeticError,
'AssertionError': AssertionError,
'AttributeError': AttributeError,
'BaseException': BaseException,
'BufferError': BufferError,
'BytesWarning': BytesWarning,
'DeprecationWarning': DeprecationWarning,
'EOFError': EOFError,
'Ellipsis': Ellipsis,
'EnvironmentError': EnvironmentError,
'Exception': Exception,
'False': False,
'FloatingPointError': FloatingPointError,
'FutureWarning': FutureWarning,
'GeneratorExit': GeneratorExit,
'IOError': IOError,
'ImportError': ImportError,
'ImportWarning': ImportWarning,
'IndentationError': IndentationError,
'IndexError': IndexError,
'KeyError': KeyError,
'KeyboardInterrupt': KeyboardInterrupt,
'LookupError': LookupError,
'MemoryError': MemoryError,
'NameError': NameError,
'None': None,
'NotImplemented': NotImplemented,
'NotImplementedError': NotImplementedError,
'OSError': OSError,
'OverflowError': OverflowError,
'PendingDeprecationWarning': PendingDeprecationWarning,
'ReferenceError': ReferenceError,
'RuntimeError': RuntimeError,
'RuntimeWarning': RuntimeWarning,
'StandardError': StandardError,
'StopIteration': StopIteration,
'SyntaxError': SyntaxError,
'SyntaxWarning': SyntaxWarning,
'SystemError': SystemError,
'SystemExit': SystemExit,
'TabError': TabError,
'True': True,
'TypeError': TypeError,
'UnboundLocalError': UnboundLocalError,
'UnicodeDecodeError': UnicodeDecodeError,
'UnicodeEncodeError': UnicodeEncodeError,
'UnicodeError': UnicodeError,
'UnicodeTranslateError': UnicodeTranslateError,
'UnicodeWarning': UnicodeWarning,
'UserWarning': UserWarning,
'ValueError': ValueError,
'Warning': Warning,
'ZeroDivisionError': ZeroDivisionError,
##'__debug__': __debug__,
##'__doc__': __doc__,
'__import__': __import__,
##'__name__': __name__,
##'__package__': __package__,
'abs': abs,
'all': all,
'any': any,
'apply': apply,
'basestring': basestring,
'bin': bin,
'bool': bool,
'buffer': buffer,
'bytearray': bytearray,
'bytes': bytes,
'callable': callable,
'chr': chr,
'classmethod': classmethod,
'cmp': cmp,
'coerce': coerce,
'compile': compile,
'complex': complex,
'copyright': copyright,
'credits': credits,
'delattr': delattr,
'dict': dict,
'dir': dir,
'divmod': divmod,
'enumerate': enumerate,
'eval': eval,
'execfile': execfile,
'exit': exit,
'file': file,
'filter': filter,
'float': float,
'format': format,
'frozenset': frozenset,
'getattr': getattr,
'globals': globals,
'hasattr': hasattr,
'hash': hash,
'help': help,
'hex': hex,
'id': id,
'input': input,
'int': int,
'intern': intern,
'isinstance': isinstance,
'issubclass': issubclass,
'iter': iter,
'len': len,
'license': license,
'list': list,
'locals': locals,
'long': long,
'map': map,
'max': max,
'min': min,
'next': next,
'object': object,
'oct': oct,
'open': open,
'ord': ord,
'pow': pow,
##'print': print,
'property': property,
'quit': quit,
'range': range,
'raw_input': raw_input,
'reduce': reduce,
'reload': reload,
'repr': repr,
'reversed': reversed,
'round': round,
'set': set,
'setattr': setattr,
'slice': slice,
'sorted': sorted,
'staticmethod': staticmethod,
'str': str,
'sum': sum,
'super': super,
'tuple': tuple,
'type': type,
'unichr': unichr,
'unicode': unicode,
'vars': vars,
'xrange': xrange,
'zip': zip}
if tuple(sys.version_info)[:2] == (2,7):
    d_built['memoryview'] = memoryview
#    d_built['print'] = print
d_built_inv = dict([(y,x) for x,y in d_built.iteritems()])

import math
import StringIO
import operator
import csv
import distutils.core

out = -1
out3 = -1
debug = False
filename = ""

global Pass
global Prev_Time
global Prev_Pass
global Pass_Exit 
Pass = {}
Prev_Time = None
Prev_Pass = None
Pass_Exit = None

tags_one_step_expr = ('CONST', 'FAST', 'BUILTIN', 'TYPED_TEMP', \
                      'LOAD_CLOSURE', 'PY_TEMP', \
#                      'CODEFUNC', \
                      'f->f_locals', \
                      'f->f_builtins', 'CALC_CONST', 'PY_TYPE')

TRUE = ('CONST', True) #True #cmd2mem(('LOAD_CONST', True))

pos__a = pos__b = pos__c = pos__d = pos__e = pos__f = pos__g = pos__h = pos__i = pos__j = pos__k = pos__l = None

call = ('CALL_FUNCTION_VAR', 'CALL_FUNCTION_KW', 'CALL_FUNCTION_VAR_KW', 'CALL_FUNCTION')

set_var = ('STORE_FAST', 'STORE_NAME', 'STORE_GLOBAL', 'STORE_DEREF')
set_any = set_var + ('PyObject_SetAttr', 'PyObject_SetItem','STORE_SLICE_LV+0',\
                     'STORE_SLICE_LV+1', 'STORE_SLICE_LV+2','STORE_SLICE_LV+3',\
                      'SET_VARS')


no_compiled = {}
detected_attr_type = {}
detected_return_type = {}
default_args = {}
mnemonic_constant = {}
all_calc_const = {}
calc_const_value = {}
val_direct_code = {}
direct_code = {}
list_import = {}

redefined_builtin = {}
redefined_attribute = True
all_trin = {}

redefined_all = False
count_define_set = {}
count_define_get = {}
matched_tail_label = ''
self_attr_type = {}
global is_direct_current
is_direct_current = False
type_def = {}
##global generate_declaration
##generate_declaration = False

def _3(nm, attr, value):
    global all_trin
    ## if attr == 'ImportedM':
##    print '>Trin ', (nm, attr, value)
    all_trin[(nm,attr,value)] = True
##    pprint.pprint(all_trin.keys())

flag_stat = False

stat_3 = {}

def Val3(nm, attr):
    if flag_stat:
        if not (attr in stat_3):
            stat_3[attr] = 0
        stat_3[attr] += 1    
    for a,b,c in all_trin.keys():
        if nm is not None and a != nm:
            continue
        if attr is not None and b != attr:
            continue
        return c
    return None

def Is3(nm, attr, value=None):
    if flag_stat:
        if not (attr in stat_3):
            stat_3[attr] = 0
        stat_3[attr] += 1    
    for a,b,c in all_trin.keys():
        if nm is not None and a != nm:
            continue
        if attr is not None and b != attr:
            continue
        if value is not None and c != value:
            continue
        return True
    return False

def Iter3(nm, attr, value):
    if flag_stat:
        if not (attr in stat_3):
            stat_3[attr] = 0
        stat_3[attr] += 1    
    for a,b,c in all_trin.keys():
        if nm is not None and a != nm:
            continue
        if attr is not None and b != attr:
            continue
        if value is not None and c != value:
            continue
        yield (a,b,c)

linear_debug = True

def HideDebug(*args):
    pass

uniq_debug_messages = {}

def Debug(*args):
    if hide_debug:
        return
    if linear_debug:
        s = ' '.join([repr(v) for v in args])
#    if len(s) < 1998:
        uniq_debug_messages[s] = None
##        print '--', s
    else:
        stream = StringIO.StringIO()
        for v in args:
            pprint.pprint(v, stream, 1, 98)
        ls = stream.getvalue().split('\n')
        if ls[-1] == '':
            del ls[-1]
        stream.close()
        ls.insert(0, '<<<')
        ls.append('>>>')
        for iit in ls:
            print '--', iit
    
def FlushDebug():
    l = uniq_debug_messages.keys()
    l.sort()
    for s in l:    
        print '--', s
    uniq_debug_messages.clear()   
        
def Fatal(msg, *args):
    FlushDebug()
    print msg, args
##    Debug(*args)
##    FlushDebug()
    assert False

T_OLD_CL_TYP = 'OldClassType'
T_OLD_CL_INST = 'OldClassInstance'
T_NEW_CL_TYP = 'NewClassType'
T_NEW_CL_INST = 'NewClassInstance'
##Kl_Dict = ''
##Nm_Klass = {}
#_Kl_Simples = ()
class Klass:
    def __init__(self, descr, subdescr = None):
##        print 'ppp', descr
        assert type(descr) in (type, str)
        self.descr = descr
        self.subdescr = subdescr
    def __eq__(self, compared):
        if compared is None:
            return False
        if type(compared) in (type, str):
            assert False
            return False
        return self.descr == compared.descr and self.subdescr == compared.subdescr
    def __ne__(self, compared):
        if compared is None:
            return True
        if type(compared) in (type, str):
            assert False
            return False
        return self.descr != compared.descr or self.subdescr != compared.subdescr
    def __contains__(self, item):
        if self.__eq__(self, item):
            return True
        return False
    def is_old_class_inst(self):
        return self.descr == T_OLD_CL_INST
    def is_old_class_typ(self):
        return self.descr == T_OLD_CL_TYP
    def is_new_class_inst(self):
        return self.descr == T_NEW_CL_INST
    def is_new_class_typ(self):
        return self.descr == T_NEW_CL_TYP
    def __hash__(self):
        return hash(self.descr) ^ hash(self.subdescr)
    def __repr__(self):
        global Nm_Klass
        if self in Nm_Klass:
            return Nm_Klass[self]
        if self.descr is types.ModuleType:
            return 'Kl_Module(' + repr(self.subdescr) + ')'
        return 'Klass' + repr((self.descr, self.subdescr))
    def IsKlass(self):
        return True
    def IsInt(self):
        return self.descr is int

def IsModule(t):
    return t is not None and t.descr is types.ModuleType

def IsInt(t):
    return t is not None and t.descr is int

def IsFloat(t):
    return t is not None and t.descr is float

def IsNoneOrInt(t):
    return t is None or t.descr is int

def IsNoneOrIntOrFloat(t):
    return t is None or t.descr is int or t.descr is float

def IsIntOrFloat(t):
    return t is not None and (t.descr is int or t.descr is float)

Kl_String = Klass(str)
Kl_Unicode = Klass(unicode)
Kl_ByteArray = Klass(bytearray)
Kl_Char = Klass(str, 1)
Kl_Int = Klass(int)
Kl_Short = Klass(int, 'ssize')
Kl_Float = Klass(float)
Kl_List = Klass(list)
Kl_Tuple = Klass(tuple)
Kl_Dict = Klass(dict)    
Kl_Set = Klass(set)    
Kl_FrozenSet = Klass(frozenset)    
Kl_Long = Klass(long)
Kl_Type = Klass(type)
##Kl_TypeType = Kl_Type
Kl_None = Klass(types.NoneType)
Kl_File = Klass(types.FileType)
Kl_Slice = Klass(types.SliceType)
Kl_Buffer = Klass(types.BufferType)
Kl_XRange = Klass(types.XRangeType)
Kl_Boolean = Klass(bool)
Kl_BuiltinFunction = Klass(types.BuiltinFunctionType)
Kl_Function = Klass(types.FunctionType)
Kl_StaticMethod = Klass(types.MethodType, 'static')
Kl_ClassMethod = Klass(types.MethodType, 'class')
Kl_Method = Klass(types.MethodType, 'instance')
Kl_Generator = Klass(types.GeneratorType)
Kl_Complex = Klass(complex)
##Kl_Unicode = Klass(unicode)
Kl_OldType = Klass(T_OLD_CL_TYP)
Kl_OldInst = Klass(T_OLD_CL_INST)
Kl_NewType = Klass(T_NEW_CL_TYP)
Kl_NewInst = Klass(T_NEW_CL_INST)
Kl_RegexObject = Klass(T_OLD_CL_INST, 'RegexObject')
Kl_MatchObject = Klass(T_OLD_CL_INST, 'MatchObject')

Nm_Klass = {Kl_String : 'Kl_String', Kl_Int : 'Kl_Int', Kl_Float : 'Kl_Float', 
    Kl_List : 'Kl_List', Kl_Tuple : 'Kl_Tuple', Kl_Dict : 'Kl_Dict', 
    Kl_None : 'Kl_None', Kl_Boolean : 'Kl_Boolean', Kl_OldType : 'Kl_OldType', 
    Kl_OldInst : 'Kl_OldInst', Kl_NewType : 'Kl_NewType', Kl_NewInst : 'Kl_NewInst',
    Kl_File : 'Kl_File', Kl_Slice : 'Kl_Slice', Kl_XRange : 'Kl_XRange', 
    Kl_Buffer: 'Kl_Buffer', Kl_StaticMethod : 'Kl_StaticMethod', 
    Kl_ClassMethod : 'Kl_ClassMethod', Kl_Method : 'Kl_Method', 
    Kl_Complex : 'Kl_Complex', Kl_Char : 'Kl_Char', Kl_RegexObject : 'Kl_RegexObject',
    Kl_MatchObject : 'Kl_MatchObject', Kl_Set : 'Kl_Set', Kl_FrozenSet : 'Kl_FrozenSet', 
    Kl_Long : 'Kl_Long', Kl_Type : 'Kl_Type', Kl_ByteArray : 'Kl_ByteArray', 
    Kl_Generator : 'Kl_Generator', Kl_BuiltinFunction: 'Kl_BuiltinFunction', 
    Kl_Function: 'Kl_Function', Kl_Short : 'Kl_Short', Kl_Unicode:'Kl_Unicode'}

def Kl_Module(a):
    return Klass(types.ModuleType, a)

_Kl_Simples = frozenset((Kl_List, Kl_Tuple, Kl_Int, Kl_String, Kl_Char, Kl_Dict, 
               Kl_Float, Kl_Boolean, Kl_None, Kl_File, Kl_Complex, Kl_Buffer,
               Kl_Char, Kl_Long, Kl_Type, Kl_ByteArray, Kl_RegexObject, Kl_Set,
               Kl_Short, 'Kl_Unicode'))

matched_i = None
matched_p = None
matched_len = None

jump = ('JUMP', 'JUMP_CONTINUE', 'JUMP_BREAK')
_n2c = {}

all_co = {}
##nm_attr = {}
n_seq = 0

def subroutine_can_be_direct(nm, cnt_args):
    if can_be_direct_call(all_co[N2C(nm)].cmds[1]) == True:
        co = N2C(nm)
        if co.co_flags & 0x28 == 0 and len(co.co_cellvars) == 0 and len(co.co_freevars) == 0:
            if co.co_flags & 0x4 == 0:
                return match_count_args(nm, cnt_args)
            return True
    return False

def match_count_args(nm, cnt_args):
##    print nm, cnt_args, N2C(nm).co_argcount
    c_args = N2C(nm).co_argcount
    if cnt_args > c_args:
        return False
    if cnt_args < c_args:
        if nm in default_args:
            defau = default_args[nm]
            if defau is None or len(defau) == 0:
                pass
            elif defau[0] in ('CONST', '!BUILD_TUPLE'):
                cnt_args += len(defau[1])
            else:
                Fatal('Strange match_count_args', nm, defau)
##            print nm, cnt_args, N2C(nm).co_argcount, default_args[nm]
            if cnt_args < c_args :
                return False
        else:
            return False    
    return True        

calculated_const = {}
pregenerated = []

known_modules = ('math', 'cmath', 'operator', 'string', 
                 'binascii', 'marshal', 're', 'struct', 'sys', 'os', 'types', 
                 'array', 'exceptions', 'Tkinter', 'ctypes', 
                 'code', 'new')

CFuncFloatOfFloat = {('math', 'exp'):'exp', ('math', 'sin'):'sin', ('math', 'cos'):'cos'}
t_imp = {}

######################(

######################)

def add_math_float(a):
    global t_imp
    for f in a:
        t_imp[('math', f, '()')] = Kl_Float
    
add_math_float(('fabs', 'factorial', 'fmod', 'fsum', 'ldexp', 'exp', \
                'log', 'log1p', 'log10', 'pow', 'sqrt', 'acos', 'asin', 'atan', \
                'atan2', 'hypot', 'cos', 'sin', 'tan', 'degrees', 'radians', \
                'acosh', 'asinh', 'atanh', 'cosh', 'sinh', 'tanh', 'floor'))

t_imp[('math', 'frexp', '()')] = Kl_Tuple                
t_imp[('math', 'isnan', '()')] = Kl_Boolean                
t_imp[('math', 'isinf', '()')] = Kl_Boolean                

t_imp[('types', 'CodeType', 'val')] = Kl_Type
t_imp[('types', 'ModuleType', 'val')] = Kl_Type
t_imp[('types', 'NoneType', 'val')] = Kl_Type
t_imp[('types', 'FunctionType', 'val')] = Kl_Type
t_imp[('types', 'InstanceType', 'val')] = Kl_Type
t_imp[('types', 'EllipsisType', 'val')] = Kl_Type
t_imp[('re', 'compile', '()')] = Kl_RegexObject 
t_imp[('re', 'sub', '()')] = Kl_String 
t_imp[('re', 'subn', '()')] = Kl_Tuple 
t_imp[('re', 'search', '()')] = None 
t_imp[('re', 'match', '()')] = None 
#t_imp[('array', 'array', 'val')] = Klass(T_OLD_CL_INST, 'array') 
#t_imp[('UserDict', 'UserDict', 'val')] = Klass(T_OLD_CL_INST, 'UserDict') 

t_imp[('tempfile', 'mktemp', '()')] = Kl_String               
#t_imp[('threading', 'Thread', 'val')] = Klass(T_OLD_CL_INST, 'Thread') 

t_imp[('zipfile', 'ZipFile', 'val')] = Klass(T_OLD_CL_TYP, 'ZipFile')             
t_imp[('zipfile', 'ZipFile', '()')] = Klass(T_OLD_CL_INST, 'ZipFile')             

t_imp[('cStringIO', 'StringIO', 'val')] = Klass(T_NEW_CL_TYP, 'StringIO')  
      
t_imp[('inspect', 'getsourcefile', '()')] = Kl_String             
t_imp[('inspect', 'getmembers', '()')] = Kl_List    
t_imp[('inspect', 'getmodule', '()')] = None    
t_imp[('inspect', 'currentframe', '()')] = Klass(types.FrameType)

t_imp[('getopt', 'getopt', '()')] = Kl_Tuple    
t_imp[('locale', 'getdefaultlocale', '()')] = Kl_Tuple  
t_imp[('locale', 'getpreferredencoding', '()')] = Kl_String    
t_imp[('codecs', 'lookup', '()')] = Klass(T_NEW_CL_INST, 'CodecInfo')
t_imp[('tarfile', 'open', '()')] = Klass(T_NEW_CL_INST, 'TarFile')

t_imp[('string', 'atoi', '()')] = Kl_Int               
t_imp[('string', 'atof', '()')] = Kl_Float               
t_imp[('string', 'split', '()')] = Kl_List               
t_imp[('string', 'rsplit', '()')] = Kl_List               
t_imp[('string', 'replace', '()')] = Kl_String                
t_imp[('string', 'upper', '()')] = Kl_String                
t_imp[('string', 'lower', '()')] = Kl_String                
t_imp[('string', 'strip', '()')] = Kl_String                
t_imp[('string', 'rstrip', '()')] = Kl_String                
t_imp[('string', 'rfind', '()')] = Kl_Int                
t_imp[('string', 'find', '()')] = Kl_Int                
t_imp[('string', 'rjust', '()')] = Kl_String                
t_imp[('string', 'ljust', '()')] = Kl_String                

t_imp[('code', 'InteractiveInterpreter', 'val')] = Klass(T_NEW_CL_TYP, 'InteractiveInterpreter')               
t_imp[('code', 'InteractiveConsole', 'val')] = Klass(T_NEW_CL_TYP, 'InteractiveConsole')               

t_imp[('cPickle', 'load', '()')] = None  
t_imp[('glob', 'glob', '()')] = Kl_List  

t_imp[('imp', 'load_source', '()')] = None  

t_imp[('copy', 'copy', '()')] = None  
t_imp[('copy', 'deepcopy', '()')] = None  
t_imp[('subprocess', 'Popen', 'val')] = Klass(T_NEW_CL_TYP, 'Popen') 
t_imp[('tempfile', 'gettempprefix', '()')] = Kl_String  
t_imp[('tempfile', 'mkdtemp', '()')] = Kl_String  

t_imp[('doctest', 'testmod', '()')] = Kl_Tuple  

t_imp[('time', 'ctime', '()')] = Kl_String

t_imp[('repr', 'repr', '()')] = Kl_String

t_imp[('os', 'system', '()')] = Kl_Int  
t_imp[('os', 'uname', '()')] = Kl_Tuple  
t_imp[('os', 'listdir', '()')] = Kl_List  
t_imp[('os', 'popen', '()')] = Kl_File  
t_imp[('os', 'getenv', '()')] = None  
t_imp[('os', 'getpid', '()')] = None  
t_imp[('os', 'getcwd', '()')] = Kl_String  
t_imp[('os.path', 'split', '()')] = Kl_Tuple  
t_imp[('os.path', 'join', '()')] = Kl_String  
t_imp[('os.path', 'dirname', '()')] = Kl_String  

t_imp[('urllib', 'urlretrieve', '()')] = Kl_Tuple  

t_imp[('time', 'time', '()')] = Kl_Float   
t_imp[('time', 'clock', '()')] = Kl_Float   
t_imp[('tempfile', 'gettempdir', '()')] = Kl_String   
t_imp[('parser', 'expr', '()')] = None   
t_imp[('parser', 'suite', '()')] = None   
      
t_imp[('ctypes', 'pointer', 'val')] = Klass(T_NEW_CL_TYP, 'ctypes_pointer')   
t_imp[('ctypes', 'POINTER', '()')] = Klass(T_NEW_CL_INST, 'ctypes_pointer')   
t_imp[('ctypes', 'sizeof', '()')] = Kl_Int 
t_imp[('ctypes', 'create_string_buffer', '()')] = None 
t_imp[('ctypes', 'c_void_p', 'val')] = Klass(T_NEW_CL_TYP, 'ctypes_c_c_void_p')   
t_imp[('ctypes', 'c_int', 'val')] = Klass(T_NEW_CL_TYP, 'ctypes_c_int')   
t_imp[('ctypes', 'c_uint', 'val')] = Klass(T_NEW_CL_TYP, 'ctypes_c_uint')   
t_imp[('ctypes', 'CFUNCTYPE', 'val')] = Klass(T_NEW_CL_TYP, 'ctypes_CFUNCTYPE')   
t_imp[('ctypes', 'Structure', 'val')] = Klass(T_NEW_CL_TYP, 'ctypes_Structure')   
      
             
t_imp[('random', 'random', '()')] = Kl_Float                
t_imp[('binascii', 'hexlify', '()')] = Kl_String                
t_imp[('binascii', 'unhexlify', '()')] = Kl_String                
t_imp[('marshal', 'loads', '()')] = None                
t_imp[('struct', 'pack', '()')] = Kl_String                
t_imp[('struct', 'unpack', '()')] = Kl_Tuple                
t_imp[('struct', 'calcsize', '()')] = Kl_Int  
  
t_imp[('sys', 'stdin', 'val')] = Kl_File    
t_imp[('sys', 'stdout', 'val')] = Kl_File    
t_imp[('sys', 'stderr', 'val')] = Kl_File    
t_imp[('sys', 'modules', 'val')] = Kl_Dict    
t_imp[('sys', 'exc_info', '()')] = Kl_Tuple   
 
t_imp[('random', 'choice', '()')] = None
   
t_imp[('math', 'pi', 'val')] = Kl_Float   
t_imp[('exceptions', 'Exception', 'val')] = Kl_NewType   
t_imp[('struct', 'calcsize', '()')] = Kl_Int                


#################
_unjump_cmds = ('.:', '3CMP_BEG_3', 'BASE_LIST_COMPR', 'BUILD_LIST',
 'BUILD_MAP', 'BUILD_TUPLE', 'CALL_FUNCTION_1', 'CALL_FUNCTION_KW_1',
 'CALL_FUNCTION_VAR_1', 'CALL_FUNCTION_VAR_KW_1', 'CHECK_EXCEPTION',
 'COMPARE_OP', 'CONTINUE_LOOP', 'DUP_TOP', 'END_FINALLY', 'GET_ITER',
 'IMPORT_AND_STORE_AS', 'LIST_APPEND', 'LOAD_ATTR_1', 'PyObject_GetAttr',
 'LOAD_CLOSURE', 'LOAD_CODEFUNC', 'LOAD_DEREF', 'LOAD_GLOBAL',
 'LOAD_LOCALS', 'LOAD_NAME', 'MAKE_CLOSURE', 'MAKE_FUNCTION',
 'MK_CLOSURE', 'MK_FUNK', 'POP_BLOCK', 'POP_TOP', 'POP_TOP3',
 'PRINT_ITEM_0', 'PRINT_ITEM_TO_0', 'PRINT_NEWLINE_TO_0', 'ROT_THREE',
 'ROT_TWO', 'SEQ_ASSIGN_0', 'SET_VARS', 'STORE_MAP', 'STORE_SLICE+1',
 'STORE_SLICE+2', 'STORE_SLICE+3', 'STORE_SLICE+0', 'STORE_SUBSCR_0', 'STORE_ATTR_1',
 'UNPACK_SEQ_AND_STORE', 'WITH_CLEANUP', 'CONST', 'FAST', 'PyList_Append',
 'YIELD_VALUE', 'BUILD_SET')                

anagr = {}

def set_anagr(a,b):
    global anagr
    anagr[a] = b
    anagr[b] = a
    
set_anagr('JUMP_IF2_FALSE_POP_CONTINUE', 'JUMP_IF2_TRUE_POP_CONTINUE')
set_anagr('JUMP_IF_FALSE_POP_CONTINUE', 'JUMP_IF_TRUE_POP_CONTINUE')
set_anagr('JUMP_IF2_FALSE_POP', 'JUMP_IF2_TRUE_POP')
set_anagr('JUMP_IF_FALSE_POP', 'JUMP_IF_TRUE_POP')
set_anagr('JUMP_IF_FALSE', 'JUMP_IF_TRUE')

#collect_stat = False
p2l = {}
used_cmpl = {}
used_cmp = {}
used_line = {}

matched_cmpl = {}
matched_cmp = {}
matched_line = {}

op_2_c_op = {'<':'PyCmp_LT', '<=':'PyCmp_LE', '==':'PyCmp_EQ', '!=':'PyCmp_NE',
             '>':'PyCmp_GT', '>=':'PyCmp_GE'} #, 'is':'PyCmp_IS', 'is not':'PyCmp_IS_NOT'}
c_2_op_op = {'PyCmp_LT':'<', 'PyCmp_LE':'<=', 'PyCmp_EQ':'==', 'PyCmp_NE':'!=',
             'PyCmp_GT':'>', 'PyCmp_GE':'>='} #, 'is':'PyCmp_IS', 'is not':'PyCmp_IS_NOT'}
             
## ##op_2_inv_op = {} #'<':'>=', '<=':'>', '==':'!=', '!=':'==',
             ## #'>':'<=', '>=':'<'}
## op_2_inv_op_ = {} #'<':'>', '<=':'>=', '==':'!=', '!=':'==',
             ## #'>=':'<=', '>':'<'}

recode_binary = {'BINARY_POWER': 'PyNumber_Power+Py_None', 'BINARY_MULTIPLY':'PyNumber_Multiply',
                 'BINARY_DIVIDE':'PyNumber_Divide', 'BINARY_TRUE_DIVIDE':'PyNumber_TrueDivide',
                 'BINARY_FLOOR_DIVIDE':'PyNumber_FloorDivide', 'BINARY_MODULO':'PyNumber_Remainder',
                 'BINARY_ADD':'PyNumber_Add', 'BINARY_SUBTRACT':'PyNumber_Subtract',
                 'BINARY_SUBSCR':'PyObject_GetItem', 'BINARY_LSHIFT':'PyNumber_Lshift',
                 'BINARY_RSHIFT':'PyNumber_Rshift', 'BINARY_AND':'PyNumber_And',
                 'BINARY_XOR':'PyNumber_Xor', 'BINARY_OR':'PyNumber_Or'}

recode_unary = {'UNARY_POSITIVE':'PyNumber_Positive', 'UNARY_NEGATIVE':'PyNumber_Negative',
                'UNARY_CONVERT':'PyObject_Repr', 'UNARY_INVERT':'PyNumber_Invert'}

recode_inplace = {'INPLACE_POWER':'PyNumber_InPlacePower+',
                'INPLACE_MULTIPLY':'PyNumber_InPlaceMultiply',
                'INPLACE_ADD':'PyNumber_InPlaceAdd',
                'INPLACE_SUBTRACT':'PyNumber_InPlaceSubtract',
                'INPLACE_DIVIDE':'PyNumber_InPlaceDivide',
                'INPLACE_TRUE_DIVIDE':'PyNumber_InPlaceTrueDivide',
                'INPLACE_FLOOR_DIVIDE':'PyNumber_InPlaceFloorDivide',
                'INPLACE_MODULO':'PyNumber_InPlaceRemainder',
                'INPLACE_LSHIFT':'PyNumber_InPlaceLshift',
                'INPLACE_RSHIFT':'PyNumber_InPlaceRshift',
                'INPLACE_AND':'PyNumber_InPlaceAnd',
                'INPLACE_XOR':'PyNumber_InPlaceXor',
                'INPLACE_OR':'PyNumber_InPlaceOr'}

from opcode import HAVE_ARGUMENT, hasjrel, opname, EXTENDED_ARG, \
                    hasconst, hasname, haslocal, hascompare, hasfree, cmp_op

# PARAMETERS
detect_float = True
full_pycode = True
print_cline = False
print_pyline = False
opt_flag = None
stat_func = ''
range2for = True
enumerate2for = True
calc_ref_total = False
recalc_refcnt = False
direct_call = True
##c_line_exceptions = False
no_generate_comment = False
dirty_iteritems = False
hide_debug = True
##simple_generate = False
##fast_instance = True - all
###fast_global = False # It' too early - don't use
check_recursive_call = True
expand_BINARY_SUBSCR = False
make_indent = False
line_number = True
no_build = False
##use_cash_refcnt = False
checkmaxref = 0

try_jump_context = [False]
dropped_temp = []

filename = ""
genfilename = ''
func = ""
current_co = '?'

tempgen = []
typed_gen = []

labels = []    
labl = ''

CO_GENERATOR = 0x0020

## cfuncs = {}

len_family = ('!PyObject_Size', '!PyString_GET_SIZE', '!PyString_Size', 
              '!PySet_GET_SIZE', '!PySet_Size', '!PyList_GET_SIZE',
              '!PyList_Size', '!PyTuple_GET_SIZE', '!PyTuple_Size', 
              '!PyDict_Size', '!PyUnicode_GET_SIZE', '!PyUnicode_GetSize',
              '!PyByteArray_GET_SIZE', '!PyByteArray_Size')

CFuncNeedINCREF = ('PyDict_GetItem', 'PyObject_GenericGetAttr', 'PyList_GET_ITEM', \
                   'PyTuple_GetItem', 'PyList_GetItem', 'PyTuple_GET_ITEM')
CFuncNotNeedINCREF = ('PyObject_GetAttr', 'PyObject_GetItem', \
                      'PyDict_New', 'PyNumber_Add', \
           'PyCell_Get', \
           'PyNumber_Divide', 'PyNumber_TrueDivide', 'PyNumber_Multiply', 'PyNumber_Negative', \
           'PyNumber_Power', 'PyNumber_Remainder', 'PyNumber_Subtract',\
           'PyNumber_Positive',\
           'PyNumber_Absolute',\
           'PyNumber_And', 'PyNumber_Or', 'PyNumber_Rshift', 'PyNumber_Lshift',\
           'PyNumber_InPlaceSubtract', 'PyNumber_InPlaceAdd', 'PyNumber_InPlaceAnd', \
           'PyNumber_Invert', 'PyNumber_FloorDivide', \
           'PyNumber_InPlaceMultiply', 'PyNumber_FloorDivide', 'PyNumber_Xor',\
           'PyNumber_InPlaceDivide', 'PyNumber_InPlaceTrueDivide',\
           'PyNumber_InPlaceOr', 'PyNumber_InPlaceFloorDivide',\
           'PyNumber_InPlacePower',\
           'PyNumber_InPlaceRshift',\
           'PyNumber_InPlaceLshift',\
           'PyNumber_InPlaceRemainder',\
           'PyNumber_InPlaceXor',\
           'PyObject_Dir', 'PyObject_Format', \
           'PySlice_New', '_PyEval_ApplySlice', \
           'PyTuple_Pack', 'PyObject_Call', 'PyObject_GetIter', 'PyIter_Next',\
           'Py2CFunction_New_Simple', 'Py2CFunction_New', 'PyFunction_New', \
           'PyObject_RichCompare', 'c_LOAD_NAME',\
           'c_LOAD_GLOBAL', 'PyNumber_InPlaceAdd', '_PyEval_BuildClass',\
           'PySequence_GetSlice', 'PyInt_FromSsize_t', 'PyEval_CallObject',
           'from_ceval_BINARY_SUBSCR', 'Py_CLEAR', 'Py_BuildValue', \
           '_PyDict_NewPresized', 'PyInt_FromSsize_t', 'PyTuple_New', 'PyList_New',\
           'from_ceval_BINARY_ADD_Int', 'from_ceval_BINARY_SUBTRACT_Int',\
           'PyDict_New', 'PyDict_Copy', 'PyBool_FromLong', 'PyObject_Type', 'PyObject_Repr',\
           'PyObject_Dir', 'PySet_New', 'PyFrozenSet_New', 'PySequence_Tuple', 'PySequence_List',\
           'PyFloat_FromDouble', 'PyObject_Str', 'PyCFunction_Call', \
           'PyLong_FromVoidPtr', 'PyNumber_ToBase', \
           'PyComplex_Type.tp_new',
           'PyInt_Type.tp_new', 'PyLong_Type.tp_new', 'PyFloat_Type.tp_new', \
           'PyBool_Type.tp_new', 'PyBaseObject_Type.tp_new', 'PyUnicode_Type.tp_new', \
           'PyString_FromStringAndSize', 'PyInt_FromLong', 'PyString_Format', \
           'STR_CONCAT2', 'STR_CONCAT3', 'PySequence_Repeat', 'FirstCFunctionCall', 'FastCall', 'FastCall0',\
           'UNICODE_CONCAT2', 'UNICODE_CONCAT3', 'c_BINARY_SUBSCR_SUBSCR_Int_Int',\
           '_c_BINARY_SUBSCR_Int', '_c_BINARY_SUBSCR_ADDED_INT',\
           'PyInstance_New', 'PyInstance_NewRaw', '_PyString_Join', '_PyList_Extend', 'PyList_AsTuple',\
           'PyDict_Keys', 'PyDict_Items', 'PyDict_Values', 'PyFile_FromString',\
           '_PyInt_Format', '_PyList_Pop')
# PyObject_Type eq o->ob_type without incref           
           
CFuncVoid =    ('PyFrame_FastToLocals', 'PyFrame_LocalsToFast', 'SETLOCAL', \
           'COPYTEMP', 'PyList_SET_ITEM', 'SET_CODE_C_FUNC', \
           '_PyEval_DoRaise', 'printf', 'Py_INCREF', 'Py_CLEAR', \
           'PyTuple_SET_ITEM', 'PyFrame_BlockSetup', 'PyFrame_BlockPop',\
           'PyErr_Restore', 'PyErr_Fetch', 'PyErr_NormalizeException',\
           '_PyEval_set_exc_info', '_PyEval_reset_exc_info', 'PyDict_Clear')      
CFuncNoCheck = ('SETLOCAL', 'COPYTEMP', 'PyList_SET_ITEM', 'SET_CODE_C_FUNC',\
            '_PyEval_DoRaise', 'PyIter_Next', 'printf', 'Py_INCREF', 'Py_CLEAR',\
            'PyInt_AsSsize_t', 'PyTuple_SET_ITEM', 'PyObject_HasAttr',\
            'PyFrame_FastToLocals', 'PyFrame_LocalsToFast', 'PyErr_ExceptionMatches',\
            'PyFloat_AS_DOUBLE', 'PyInt_AsLong', 'PyInt_AS_LONG', 'PyFloat_AsDouble',\
            '(double)PyInt_AsLong')
CFuncPyObjectRef = ('FirstCFunctionCall', 'FastCall', 'FastCall0', 'GETLOCAL', 'PyBaseObject_Type.tp_new',\
 'PyBool_FromLong', 'PyBool_Type.tp_new', 'PyCFunction_Call', 'PyCell_Get', \
 'PyDict_GetItem', 'PyDict_Items', 'PyDict_Keys', 'PyDict_New', 'PyDict_Values', 'PyDict_Copy',\
 'PyEval_CallObject', 'PyFile_FromString',\
 'PyFloat_FromDouble', 'PyFloat_Type.tp_new',\
 'PyFrozenSet_New', 'PyFunction_New', 'Py2CFunction_New_Simple', 'Py2CFunction_New', \
 'PyInstance_New', 'PyInstance_NewRaw',\
 'PyInt_FromLong', 'PyInt_FromSsize_t', 'PyInt_Type.tp_new', 'PyComplex_Type.tp_new',\
 'PyList_GET_ITEM', 'PyList_GetItem', 'PyList_New', 'PyList_AsTuple', \
 'PyLong_FromSsize_t', 'PyLong_FromVoidPtr', 'PyLong_Type.tp_new',\
 'PyNumber_Absolute', 'PyNumber_Add', 'PyNumber_And', 'PyNumber_Divide',\
 'PyNumber_FloorDivide', 'PyNumber_InPlaceAdd', 'PyNumber_InPlaceAdd',\
 'PyNumber_InPlaceAnd', 'PyNumber_InPlaceDivide', 'PyNumber_InPlaceFloorDivide',\
 'PyNumber_InPlaceLshift', 'PyNumber_InPlaceMultiply', 'PyNumber_InPlaceOr',\
 'PyNumber_InPlacePower', 'PyNumber_InPlaceRemainder', 'PyNumber_InPlaceRshift',\
 'PyNumber_InPlaceSubtract', 'PyNumber_InPlaceTrueDivide', 'PyNumber_InPlaceXor',\
 'PyNumber_Invert', 'PyNumber_Lshift', 'PyNumber_Multiply', 'PyNumber_Negative',\
 'PyNumber_Or', 'PyNumber_Positive', 'PyNumber_Power', 'PyNumber_Remainder',\
 'PyNumber_Rshift', 'PyNumber_Subtract', 'PyNumber_ToBase', 'PyNumber_TrueDivide',\
 'PyNumber_Xor',\
 'PyObject_Call', 'PyObject_Dir', 'PyObject_GetAttr', 'PyObject_GenericGetAttr', 'PyObject_GetItem',\
 'PyObject_GetIter', 'PyObject_Repr', 'PyObject_RichCompare', 'PyObject_Str',\
 'PyObject_Type', 'PyObject_Dir', 'PyObject_Format', \
 'PySequence_GetSlice', 'PySequence_List', 'PySequence_Repeat', 'PySequence_Tuple',\
 'PySet_New', 'PySlice_New',\
 'PyString_Format',  'PyString_FromStringAndSize',\
 'PyTuple_GET_ITEM',  'PyTuple_GetItem', 'PyTuple_New', 'PyTuple_Pack',\
 'PyUnicode_Type.tp_new', 'Py_BuildValue', \
 'STR_CONCAT2', 'STR_CONCAT3', 'UNICODE_CONCAT2', 'UNICODE_CONCAT3',\
 '_PyDict_NewPresized', '_PyEval_ApplySlice', '_PyEval_BuildClass',\
 '_PyList_Extend',  '_PyString_Join',\
 '_c_BINARY_SUBSCR_ADDED_INT', '_c_BINARY_SUBSCR_Int', 'c_BINARY_SUBSCR_SUBSCR_Int_Int',\
 'from_ceval_BINARY_ADD_Int', 'from_ceval_BINARY_SUBSCR', 'from_ceval_BINARY_SUBTRACT_Int',\
 'c_LOAD_GLOBAL', 'c_LOAD_NAME', '_PyInt_Format', '_PyList_Pop')

CFuncIntCheck = ('PyCell_Set', \
'PyDict_DelItem', 'PyDict_SetItem', 'PyDict_Size', 'PyDict_Update', 'PyDict_Contains',\
'PyDict_MergeFromSeq2', 'PyDict_DelItem', \
'PyFunction_SetClosure', 'PyFunction_SetDefaults',\
'Py2CFunction_SetClosure', 'Py2CFunction_SetDefaults',\
'PyList_Append', 'PyList_GET_SIZE', 'PyList_Insert', 'PyList_Reverse', \
'PyList_SetItem', 'PyList_SetSlice', 'PyList_Sort', \
'PyObject_DelItem', 'PyObject_IsInstance', 'PyObject_IsSubclass', \
'PyObject_IsTrue', 'PyObject_Not', 'PyObject_RichCompareBool',\
'PyObject_SetAttr', 'PyObject_SetItem', 'PyObject_Size',\
'PySequence_Contains', 'PySet_Contains', \
'PyString_GET_SIZE', 'PyTuple_GET_SIZE', 'PySet_Size', \
'PyUnicode_GetSize', 'PySet_Add', \
'_PyEval_AssignSlice', '_PyEval_ExecStatement', '_PyEval_ImportAllFrom',\
'_PyEval_PRINT_ITEM_1', '_PyEval_PRINT_ITEM_TO_2', '_PyEval_PRINT_NEWLINE_TO_1',\
'c_PyCmp_EQ_Int', 'c_PyCmp_EQ_String', 'c_PyCmp_GE_Int', 'c_PyCmp_GE_String',\
'c_PyCmp_GT_Int', 'c_PyCmp_GT_String', 'c_PyCmp_LE_Int', 'c_PyCmp_LE_String',\
'c_PyCmp_LT_Int', 'c_PyCmp_LT_String', 'c_PyCmp_NE_Int', 'c_PyCmp_NE_String',\
'PyString_AsStringAndSize', 'PyObject_Cmp')

API_cmp_2_PyObject = ('!PySequence_Contains', '!PyObject_HasAttr', \
               '!PyObject_IsSubclass', '!PyObject_IsInstance', '!PyDict_Contains', '!PySet_Contains')

CFuncIntNotCheck = ('PyInt_AsSsize_t', 'PyObject_HasAttr', 'PyErr_ExceptionMatches')
CFuncFloatNotCheck = ('PyFloat_AS_DOUBLE', 'PyFloat_AsDouble', '(double)PyInt_AsLong')
CFuncLongNotCheck = ('PyInt_AsLong', 'PyInt_AS_LONG')
CFuncLongCheck = ('PyObject_Hash', )
               
CFuncIntAndErrCheck = ()                

set_IntCheck = set(CFuncIntCheck + CFuncLongCheck + CFuncIntAndErrCheck)

consts = []
consts_dict = {}
loaded_builtin = []

def nmrecode(n):
    if n == '<genexpr>':
        n = 'genexpr__'
    elif n == '<module>':
        n = 'Init_filename'
    elif n[:8] == '<lambda>':
        n = 'lambda_' + n[8:]
    elif n == '<dictcomp>':
        n = 'dict_comp__'
    elif n == '<setcomp>':
        n = 'set_comp__'
    return n    
    
def C2N(c):
    global n_seq
    global _n2c, all_co
    if c in all_co:
        if hasattr(all_co[c], 'c_name'):
            n = all_co[c].c_name
            return n
    n = c.co_name
    n = nmrecode(n)
    if n in _n2c and not c in all_co:
        i = 1
        n2 = n
        while n2 in _n2c:
            n2 = n + repr(i)
            i = i + 1
        n = n2 
    if not c in all_co:       
        cco = DDic()
        cco.co = c
        cco.n_seq = n_seq
        all_co[c] = cco
        n_seq += 1
    all_co[c].c_name = n
    _n2c[n] = c   
    return n
 
def N2C(n):
    return _n2c[n]    

def dis(x=None):
    """Disassemble classes, methods, functions, or code.
    With no argument, disassemble the last traceback.
    """
    ## if x is None:
        ## distb()
        ## return
#    if type(x) is types.InstanceType:
#        x = x.__class__
    if hasattr(x, 'im_func'):
        x = x.im_func
    if hasattr(x, 'func_code'):
        x = x.func_code
    if hasattr(x, '__dict__'):
        items = x.__dict__.items()
        items.sort()
        for name, x1 in items:
            if type(x1) in (types.MethodType,
                            types.FunctionType,
                            types.CodeType,
                            types.ClassType):
                    dis(x1)
    elif hasattr(x, 'co_code'):
        pre_disassemble(x)
    else:
        raise TypeError ( \
              "don't know how to disassemble %s objects" % \
              type(x).__name__)

from dis import findlabels, findlinestarts
global nm_pass
nm_pass = {}

def line2addr(co):
    pairs = list(findlinestarts(co))
    pairs.sort()
    lines = {}
    for addr, line in pairs:
        if not line in lines:
            lines[line] = addr
    return lines        

def SetPass(p):
    global Pass, Prev_Pass, Prev_Time, Pass_Exit
    if p == Pass_Exit:
        Fatal('Cancelled at pass %s' % p)
##    print 'Pass ', p, sys.getrefcount(None)    
    if p in nm_pass:
        p = nm_pass[p]
    else:
        s = str(len(nm_pass))
        if len(s) < 2:
            s = '0' + s
        nm_pass[p] = s + ':' + p
        p = nm_pass[p]        
    ti = time.clock()
    if Prev_Time is not None:
        Pass[Prev_Pass] = ti - Prev_Time
    Prev_Time = ti
    Prev_Pass = p
     
def disassemble_base(co):
    """Disassemble a code object."""
    code = co.co_code
    labels = findlabels(code)
    linestarts = dict(findlinestarts(co))
    n = len(code)
    i = 0
    extended_arg = 0
    free = None
    cmds = []
    N = C2N(co)
    cmds.append(('(BEGIN_DEF', N))
    while i < n:
        label, opcmd, codearg, arg, nline = (None,None,None,None,None)
        c = code[i]
        op = ord(c)
        if i in linestarts:
            nline = linestarts[i]
        if i in labels: 
            label = i
        opcmd = opname[op] #.ljust(20),
        i = i+1
        recalc = False
        if op >= HAVE_ARGUMENT:
            oparg = ord(code[i]) + ord(code[i+1])*256 + extended_arg
            extended_arg = 0
            i = i+2            
            if op == EXTENDED_ARG:
                extended_arg = oparg*65536
            codearg = oparg  
            recalc = False
            if op in hasconst:
                arg = co.co_consts[oparg]  
                recalc = True
            elif op in hasname:
                arg = co.co_names[oparg]  
                recalc = True
            elif op in hasjrel:
                arg = i + oparg  
                recalc = True
            elif op in haslocal:
                arg = co.co_varnames[oparg]  
                recalc = True
            elif op in hascompare:
                arg = cmp_op[oparg]   
                recalc = True
            elif op in hasfree:
                if free is None:
                    free = co.co_cellvars + co.co_freevars
                arg = free[oparg]  
                recalc = True
        if label is not None:        
           cmds.append(('.:', label))
        if nline is not None:       
           cmds.append(('.L', nline ))
        if opcmd == 'JUMP_ABSOLUTE' or opcmd == 'JUMP_FORWARD':
           opcmd = 'JUMP'
        if opcmd == 'FOR_ITER':
            opcmd = 'J_FOR_ITER'   
        if opcmd == 'SETUP_LOOP':
            opcmd = 'J_SETUP_LOOP'   
        if opcmd == 'SETUP_EXCEPT':
            opcmd = 'J_SETUP_EXCEPT'   
        if opcmd == 'SETUP_FINALLY':
            opcmd = 'J_SETUP_FINALLY'   
        if opcmd == 'PRINT_ITEM':
            opcmd = 'PRINT_ITEM_0'   
        if opcmd == 'PRINT_ITEM_TO':
            opcmd = 'PRINT_ITEM_TO_0'   
        if opcmd == 'PRINT_NEWLINE_TO':
            opcmd = 'PRINT_NEWLINE_TO_0'   
        if opcmd == 'STORE_SUBSCR':
            opcmd = 'STORE_SUBSCR_0'   
        if opcmd == 'STORE_ATTR':
            opcmd = 'STORE_ATTR_1'   
        if opcmd == 'DELETE_ATTR':
            opcmd = 'DELETE_ATTR_1'  
        if opcmd == 'LOAD_ATTR':
            opcmd = 'LOAD_ATTR_1'   
        if opcmd == 'CONTINUE_LOOP':
            opcmd = 'JUMP_CONTINUE'
        if opcmd == 'POP_JUMP_IF_FALSE':
            opcmd = 'JUMP_IF_FALSE_POP'
        if opcmd == 'POP_JUMP_IF_TRUE':
            opcmd = 'JUMP_IF_TRUE_POP'
        if opcmd == 'SETUP_WITH':
            opcmd = 'J_SETUP_WITH'
            
        ## if type(opcmd) is str and opcmd in codes:
            ## opcmd = codes[opcmd]
        if opcmd == 'JUMP_IF_FALSE_OR_POP': 
            cmds.append(('JUMP_IF_FALSE', codearg))
            cmds.append(('POP_TOP', ))
        elif opcmd == 'JUMP_IF_TRUE_OR_POP': 
            cmds.append(('JUMP_IF_TRUE', codearg))
            cmds.append(('POP_TOP', ))
        elif recalc:
            cmds.append((opcmd, arg))
        elif arg is None and codearg is None:   
           cmds.append((opcmd,))
        elif arg is None: # and opcmd != 'LOAD_CONST':
           if opcmd in call:
                if opcmd == 'CALL_FUNCTION':
                    opcmd = 'CALL_FUNCTION_1'
                cmds.append((opcmd, codearg & 255, (), codearg >> 8, ()))             
           else:     
                cmds.append((opcmd,codearg))
        else:   
           cmds.append((opcmd, codearg, arg ))
    return cmds

def find_redefined_builtin(cmds):
    global redefined_all, count_define_set, count_define_get
    for i,cmd in enumerate(cmds):
        ## if cmd[0] == 'IMPORT_STAR':
            ## redefined_all = True
        if cmd[0] in ('DELETE_GLOBAL', 'STORE_GLOBAL', 'DELETE_NAME', 'STORE_NAME') and \
           cmd[1] in d_built and cmd[1] != '__doc__':
            redefined_builtin[cmd[1]] = True
        if cmd[0] in ('LOAD_GLOBAL', 'LOAD_NAME'): #, 'LOAD_DEREF', 'LOAD_CLOSURE'):
            if not (cmd[1] in count_define_get):
                count_define_get[cmd[1]] = 1
            else:    
                count_define_get[cmd[1]] += 1
            if not (cmd[1] in count_define_set):
                count_define_set[cmd[1]] = 2
        if cmd[0] in ('STORE_GLOBAL', 'STORE_NAME'):
            if cmd[1] in count_define_set:
                count_define_set[cmd[1]] += 1
            else:
                count_define_set[cmd[1]] = 1    
        if cmd[0] in ('DELETE_GLOBAL', 'DELETE_NAME'):
            if cmd[1] in count_define_set:
                count_define_set[cmd[1]] += 2
            else:
                count_define_set[cmd[1]] = 2    
        if cmd == ('IMPORT_NAME', '__builtin__'):
            redefined_all = True
        if cmd[0] == 'IMPORT_NAME' and cmds[i+1][0] == 'IMPORT_STAR':
            CheckExistListImport(cmd[1])
##            li = get_list_names_module_raw(cmd[1])
            if cmd[1] in list_import:
                for x in list_import[cmd[1]]:
                    if x in count_define_set:
                        count_define_set[x] += 1
                    else:
                        count_define_set[x] = 1    

def light_opt_at_cmd_level(cmds):
    for i,cmd in enumerate(cmds):
        if cmd[0] == 'LOAD_CONST' and type(cmd[1]) is types.CodeType:
            cmds[i] = ('LOAD_CODEFUNC', (C2N(cmd[1])))
    find_redefined_builtin(cmds)        
    NoGoToGo(cmds)
    set_conditional_jump_popped(cmds)
    NoGoToGo(cmds)
    del_dead_code(cmds)
    revert_conditional_jump_over_uncond_jump(cmds)
    NoGoToGo(cmds)

def clear_module(nm):
    assert nm != '__name__'
    if sys.modules[nm] is None:
        del sys.modules[nm]
        return
    v = sys.modules[nm]        
    todel = []
    for k1,v1 in v.__dict__.iteritems():
        if type(v1) is types.ModuleType:
            todel.append(k1)
    for k1 in todel:
##        print 'del ', v.__name__, k1
        del v.__dict__[k1]        
    del sys.modules[nm]
    if nm in list_import:
        del list_import[nm]
    if nm in imported_modules:
        del imported_modules[nm]

def clear_after_all_files():
    clear_one_file()
    list_import.clear()
    self_attr_type.clear()
    sys._clear_type_cache()
    imported_modules.clear()

    ## for k,v in sys.modules.iteritems():
        ## if k not in start_sys_modules:
            ## print ';', k, sys.getrefcount(v),type(v)
    start_sys_modules.clear()         

def clear_one_file():
    global n_seq, redefined_all
    global Pass, Prev_Time, Prev_Pass, start_sys_modules
    
    all_co.clear()
##    nm_attr.clear()
    n_seq = 0    
    _n2c.clear()  
    all_trin.clear()
    redefined_all = False
    count_define_set.clear()
    count_define_get.clear()
    del consts[:]
    consts_dict.clear()
    del pregenerated[:]
    del loaded_builtin[:]
    calculated_const.clear()
    Pass.clear()
    Prev_Time = None
    Prev_Pass = None
    no_compiled.clear()
    detected_attr_type.clear()
    detected_return_type.clear()
    default_args.clear()
    mnemonic_constant.clear()
    all_calc_const.clear()
    direct_code.clear()
    val_direct_code.clear()
    calc_const_value.clear()
    redefined_builtin.clear()
    uniq_debug_messages.clear()
    type_def.clear()
    del try_jump_context[:]
    try_jump_context.append(False)
    del dropped_temp[:]
    del tempgen[:]
    del typed_gen[:]
    del labels[:]
    del g_acc2[:]
    del g_refs2[:]
    del g_len_acc[:]
    end_sys_modules = sys.modules.copy()
    for k in end_sys_modules:
        if k not in start_sys_modules and not k.startswith('distutils.'):
            clear_module(k)
##            print 'clear_module', k
    
    self_attr_type.clear()
    self_attr_type['object'] = {None:True}
    self_attr_type['am_pm'] = {Kl_List:True}
    self_attr_type['co_flags'] = {Kl_Int:True}
    self_attr_type['co_stacksize'] = {Kl_Int:True}
    self_attr_type['co_nlocals'] = {Kl_Int:True}
    self_attr_type['co_fistlineno'] = {Kl_Int:True}
    self_attr_type['co_argcount'] = {Kl_Int:True}
    self_attr_type['co_name'] = {Kl_String:True}
    self_attr_type['co_filename'] = {Kl_String:True}
    self_attr_type['co_lnotab'] = {Kl_String:True}
    self_attr_type['co_code'] = {Kl_String:True}
    self_attr_type['co_cellvars'] = {Kl_Tuple:True}
    self_attr_type['co_freevars'] = {Kl_Tuple:True}
    self_attr_type['co_consts'] = {Kl_Tuple:True}
    self_attr_type['co_varnames'] = {Kl_Tuple:True}
    self_attr_type['co_names'] = {Kl_Tuple:True}
    
      
def dump(obj):
    print_to(out, 'Code ' + obj.co_name)
    for attr in dir(obj):
        if attr.startswith('co_') and attr not in ( 'co_code', 'co_lnotab'):
            val = getattr(obj, attr)
            if attr == 'co_flags':
                print_to(out,"\t" + attr + ' ' + hex(val))
            elif attr in ('co_consts', 'co_name'):
                pass
            else:    
                print_to(out,"\t" + attr + ' ' + repr(val))
class DDic:
    def __init__(self):
        self.self_dict_getattr_used = False
        self.method_old_class = False
        self.method_new_class = False
        self.method_any_class = False
        self.self_dict_setattr_used = False
        self.method_class = None
        self.dict_getattr_used = {}
        
    
def pre_disassemble(co):
    global n_seq
    if not co in all_co:
        cco = DDic()
        cco.co = co
        cco.n_seq = n_seq
        all_co[co] = cco
        n_seq += 1
    cmds = disassemble_base(co)
    light_opt_at_cmd_level(cmds)
    all_co[co].cmds = cmds[:]
    
def can_be_direct_call(it):
    if tag_in_expr('!IMPORT_NAME', it):
        return 'statement IMPORT_NAME'
    if tag_in_expr('EXEC_STMT', it):
        return 'exec stmt'
    if tag_in_expr('EXEC_STMT_3', it):
        return 'exec stmt'
    if tag_in_expr('IMPORT_FROM_AS', it):
        return 'import from as'
    ## if '_getframe' in s:
        ## return 'probably get frame'
    ## if 'thread' in s:
        ## return 'probably threads'
    ## if 'Thread' in s:
        ## return 'probably threads'
    if tag_in_expr('(TRY', it):
        return 'statement try:'
    if tag_in_expr('(TRY_FINALLY', it):
        return 'statement try finally:'
    if tag_in_expr('(WITH', it):
        return 'statement with:'
    if tag_in_expr('YEILD', it):
        return 'statement yeild'
    if tag_in_expr('LOAD_NAME', it):
        return 'command LOAD_NAME'
    if tag_in_expr('STORE_NAME', it):
        return 'command STORE_NAME'
    return True    

def IsBegEnd(tag):
    return type(tag) is str and tag[0] in ')('

def IsBeg(tag):
    return type(tag) is str and tag[0] == '('

def post_disassemble():
    global no_build, redefined_all, current_co
    SetPass('HalfRecompile')
    seq = [(cco.co.co_firstlineno, cco.n_seq, cco.co, cco.cmds) for cco in all_co.itervalues()]       
    seq.sort()
    seq = [(b,c,d) for a,b,c,d in seq]
    for x, co, cmds in seq:
        current_co = co
        jump_to_continue_and_break(cmds)
        half_recompile(cmds, co)

    SetPass('ParseClasses-0')

    for x, co, cmds in seq:
        if '__metaclass__' in repr(cmds[1]):
            _3(cmds[0][1], 'HaveMetaClass', '???')

    SetPass('FirstRepl')
    single_define = [k for k,v in count_define_set.iteritems() \
                           if v == 1 and (k in count_define_get or k == '__all__')]
    for x, co, cmds in seq:
        current_co = co
        cmds[1] = ortogonal(cmds[1], repl) 

    SetPass('FindCalcConst')
    initcod = None
    for x, co, cmds in seq:
        if cmds[0][1] == 'Init_filename':
            current_co = co
            initcod = cmds[1]
    do_del = []        
 
    if initcod is not None:
        initcod = [st for st in initcod if type(st) is tuple and \
                   len(st) > 0 and not IsBegEnd(st[0])]
        for st in initcod:
            for k in single_define:
                p = find_statement_calculate_const(st, k) 
                if p != False:
                    filter_founded_calc_const(p, k, do_del)
    for k in do_del:       
        if k in single_define:
            del single_define[single_define.index(k)] 
                 
    res = False
    SetPass('ImportManipulation')

    ## for k, attr, v in Iter3(None, 'ImportedM',None):
        ## if v in known_modules:
             ## _3(k, 'ImportedKnownM', v)
    for x, co, cmds in seq:
        if tag_in_expr('IMPORT_STAR', cmds[1]):
            redefined_all = True
    SetPass('UpgardeOp')
 
    for x, co, cmds in seq:
        current_co = co
        cmds[1] = tree_pass(cmds[1], upgrade_op, None, cmds[0][1]) 
    SetPass('UpgardeOp2')

    for x, co, cmds in seq:
        current_co = co
        cmds[1] = tree_pass(cmds[1], upgrade_op2, None, cmds[0][1]) 

    global type_def, self_attr_type, self_attr_store, self_attr_use
    type_def.clear()
 
    SetPass('RecursiveTypeDetect-1')

    for x, co, cmds in seq:
        current_co = co
        cmds[1] = recursive_type_detect(cmds[1], cmds[0][1]) 

    SetPass('UpgradeRepl-3')
    for x, co, cmds in seq:
        current_co = co
        cmds[1] = tree_pass(cmds[1], upgrade_repl, None, cmds[0][1]) 

    SetPass('CollectTypeReturn')
    for x, co, cmds in seq:
        current_co = co
        if co.co_flags & CO_GENERATOR:
            detected_return_type[cmds[0][1]] = Kl_Generator 
        else:    
            cmds[1] = tree_pass(cmds[1], collect_type_return, None, cmds[0][1]) 

    for k1, v1 in type_def.iteritems():
        v = v1.keys()
        if len(v) == 1 and v[0] is not None:
            detected_return_type[k1] = v[0] 

    SetPass('ParseClasses')

    type_def.clear()
 
    for x, co, cmds in seq:
        current_co = co
        if IsAnyClass(cmds[0][1]) and cmds[1][-1] == ('RETURN_VALUE', ('f->f_locals',)):
            parse_class_def(cmds[0][1], cmds[1][:-1])
        elif Is3(cmds[0][1], 'IsClassCreator', None) and \
           cmds[1][-1] == ('RETURN_VALUE', ('f->f_locals',)):
            parse_for_special_slot_class(cmds[0][1], cmds[1][:-1], Val3(cmds[0][1], 'IsClassCreator'))

    SetPass('UpgardeRepl-1')
    for x, co, cmds in seq:
        current_co = co
        cmds[1] = tree_pass(cmds[1], upgrade_repl, None, cmds[0][1]) 

    SetPass('CollectSetAttr')

    for x, co, cmds in seq:
        current_co = co
        cmds[1] = tree_pass(cmds[1], collect_set_attr, None, cmds[0][1]) 
    for x, co, cmds in seq:
        current_co = co
        cmds[1] = tree_pass(cmds[1], collect_set_attr, None, cmds[0][1]) 

    for k1, v1 in self_attr_type.iteritems():
        v = v1.keys()
        if len(v) == 1 and v[0] is not None and v[0] != Kl_None:
            detected_attr_type[k1] = v[0] 
                   
    SetPass('RecursiveTypeDetect-2')
    for x, co, cmds in seq:
        current_co = co
        cmds[1] = recursive_type_detect(cmds[1], cmds[0][1]) 

    SetPass('UpgradeRepl-4')
    for x, co, cmds in seq:
        current_co = co
        cmds[1] = tree_pass(cmds[1], upgrade_repl, None, cmds[0][1]) 

    if direct_call:
        SetPass('ConcretizeDirectCall')
        prevli = []
        li = [None]
        while li != prevli:
            prevli = li
            li = [(co,cmds) for x, co, cmds in seq \
                     if Is3(cmds[0][1], 'ArgCallCalculatedDef') and can_generate_c(co)]
            for co, cmds in li:
                a = all_co[co]
                current_co = co
                a.direct_cmds, a.hidden_arg_direct = concretize_code_direct_call(cmds[0][1], cmds[1], co)

    SetPass('LabelMethod')
    for x, co, cmds in seq:
        current_co = co
        label_method_class(co)

    SetPass('Formire')
    for x, co, cmds in seq:
        current_co = co
        dump(co)
        print_cmds(cmds)
        if hasattr(all_co[co], 'direct_cmds'):
            if len(a.hidden_arg_direct) == 0 and all_co[co].direct_cmds == cmds[1]:
                pass
            else:
                print >>out, 'Hidden args', a.hidden_arg_direct
                print_cmds([('(DIRECT_DEF', cmds[0][1]), all_co[co].direct_cmds])
        if not all_co[co].decompile_fail:
            newcmds = generate(cmds, co, filename, C2N(co))
            newcmds = generate_direct(cmds, co, filename, C2N(co))
    c_fname, nmmodule = Pynm2Cnm(filename)
    SetPass('WriteAsC')
    write_as_c(out3, nmmodule)   
    out3.close()
    
    FlushDebug()
    
    if make_indent:
        SetPass('Indent')
        os.system('indent ' + c_fname)
    if no_build:
        pass
    else:    
        SetPass('Compile')
        compile_c(filename, c_fname)
    SetPass('WorkDone')
    global Pass
    if flag_stat:
        print 'Passess...'
        its = Pass.items()
        its.sort()
        for k,v in its:
            print '  ', k, round(v, 3)
        print 'Attribute uses...'  
        its = [(s,k) for k,s in stat_3.iteritems()]
        its.sort()
        for s,k in its:
            print '  ', k, s
    return None
        
def is_const_value1(v):
    if v[0] == 'CONST':
        return True
    if v[0] == '!LOAD_NAME' and (type(v[1]) is float or v[1] in ('nan', 'inf')):
        return True
    if v[0] == 'CALC_CONST':
        return True
    if v[0] == '!CLASS_CALC_CONST':
        return True
    if v[0] == '!BUILD_LIST':        
        v1 = v[1]
        return all([is_const_value1(x) for x in v1])
    if v[0] == '!BUILD_TUPLE':        
        v1 = v[1]
        return all([is_const_value1(x) for x in v1])
    if v[0] == '!PyObject_GetAttr':        
        return is_const_value1(v[1]) and is_const_value1(v[2])
    if v == ('!PyDict_New',):
        return True
    if v[0] in ('!LOAD_BUILTIN',):
        return True
    if v[0] == '!MK_FUNK':
        return is_const_value1(v[2])
    if v[0] == '!PyObject_Type':
        return is_const_value1(v[1])
    print 'not const', v
    return False
    
def is_const_default_value(v):
    if v[0] == 'CONST':
        return True
    if v[0] == '!BUILD_TUPLE':
        v1 = v[1]
        return all([is_const_value1(x) for x in v1])
    if v[0] == '!PyDict_New' and len(v) == 1:
        Fatal('??? where ???')
        return True    
    print 'not const', v
    return False  

def get_default_value1(v):
#    if v[0] == 'CONST':
    return v
#    Fatal('', '')
#    return v[1]  

def is_simple_attr(expr):
    t = TypeExpr(expr)
    if t is not None and (t in _Kl_Simples or t.descr in (types.ModuleType, T_OLD_CL_TYP, T_NEW_CL_TYP)):                 
        return True
    if expr[0].startswith('PyNumber_'):
        if len(expr) == 3:
            return is_simple_attr(expr[1]) or is_simple_attr(expr[2])
        if len(expr) == 4:
            return is_simple_attr(expr[1]) or is_simple_attr(expr[2]) or is_simple_attr(expr[2])
        if len(expr) == 2:
            return is_simple_attr(expr[1])
    return False    

def get_nmcode(nmcl, expr):
    nm_code = None
    if expr[0] == '!MK_FUNK':
        nm_code, default_arg = expr[1:3]
        if is_const_default_value(default_arg):
            default = get_default_value1(default_arg)
            default_args[nm_code] = default
            return nm_code
        Debug('*Not const default args  meth|attr', expr)        
    if expr[0] == '!LOAD_NAME':
        nm_prev = expr[1]
        if Is3(nmcl, ('Method', nm_prev)):
            nm_code = Val3(nmcl, ('Method', nm_prev))
    if expr[0] == 'PY_TYPE' and expr[3][0] == '!LOAD_NAME':
        nm_prev = expr[3][1]
        if Is3(nmcl, ('Method', nm_prev)):
            nm_code = Val3(nmcl, ('Method', nm_prev))
    if nm_code is None: 
        t = TypeExpr(expr)
        if t is not None and t.descr is types.FunctionType and t.subdescr is not None:
            nm_code = t.subdescr        
    return nm_code        

def one_store_clause(nmcl, nmslot, expr):
    v2 = []
    if nmslot in ('__doc__', '__module__'):
        return True
    if nmslot in ('__new__', '__del__'):
        nm_code = get_nmcode(nmcl, expr)
        if nm_code is None and expr[0] == '!MK_CLOSURE':
            nm_code = expr[1]
        if nm_code is not None:    
            no_compiled[nm_code] = True
        else:
            Fatal('', expr, 'Is', 'NoCompiled')    
    if is_simple_attr(expr):
        _3(nmcl, ('Attribute', nmslot), expr)
        return True
    nm_code = get_nmcode(nmcl, expr)
    if nm_code is not None:    
        _3(nmcl, ('Method', nmslot), nm_code)  
        if nmslot == '__init__':
            parse_constructor(nmcl, nm_code)          
        return True
    if expr[0] == '!PyObject_Call':
        if TCmp(expr, v2, ('!PyObject_Call', ('!LOAD_BUILTIN', 'property'), '?', '?')):
            _3(nmcl, 'Property', nmslot)  
            return one_store_property_clause(nmcl, nmslot, v2[0], v2[1])
        if TCmp(expr, v2, ('!PyObject_Call', \
                      ('!LOAD_BUILTIN', 'staticmethod'),\
                        ('!BUILD_TUPLE', ('?',)), ('NULL',)) ):
            return one_store_modificator_clause(nmcl, nmslot, 'StaticMethod', v2[0])                
        if TCmp(expr, v2, ('!PyObject_Call', \
                      ('!LOAD_BUILTIN', 'classmethod'),\
                        ('!BUILD_TUPLE', ('?',)), ('NULL',)) ):
            return one_store_modificator_clause(nmcl, nmslot, 'ClassMethod', v2[0])                
    return False

def one_store_modificator_clause(nmcl, nmslot, Modificator, expr):
    nm_code = get_nmcode(nmcl, expr)
    if nm_code is not None:    
        _3(nmcl, ('Method', nmslot), nm_code)            
        _3(nmcl, (Modificator, nmslot), nm_code)            
        return True
    Debug('*Not const default args %s meth|attr' % Modificator, expr)        
    return False

def one_store_property_clause(nmcl, nmslot, tupl, dic):
    getter, setter, deleter, doc = None, None, None, None
    if tupl[0] == '!BUILD_TUPLE':
        _tupl = list(tupl[1])
        while len(_tupl) < 4:
            _tupl.append(None)
        getter, setter, deleter, doc = _tupl
    elif tupl == ('CONST', ()):
        pass    
    else:
        Debug('*Undefined property positional arg', nmcl, nmslot, tupl, dic)       
    if dic == ('NULL',):
        pass
    elif dic[0] == '!BUILD_MAP':
        for (k,v) in dic[1]:
            if k == ('CONST', 'doc'):
                assert doc is None
                doc = v
            elif k == ('CONST', 'fget'):            
                assert getter is None
                getter = v      
            elif k == ('CONST', 'fset'):            
                assert setter is None
                setter = v      
            elif k == ('CONST', 'fdel'):            
                assert deleter is None
                deleter = v      
    else:        
        Debug('*Undefined property key arg', nmcl, nmslot, tupl, dic)   
        return False
    for k,v in (('Getter', getter), ('Setter', setter), ('Deleter', deleter)):
        if v is None or v == ('CONST', None):
            continue
        nm_code = get_nmcode(nmcl, v)
        if nm_code is not None:    
            _3(nmcl, (k, nmslot), nm_code)            
            continue
        Debug('*Access %s property class %s -> %s UNPARSE method %s ' % (k, nmcl, nmslot, nm_code))    
        return False
    return True                
     
def parse_class_def(nm, seq):
    i = -1
    while i < len(seq)-1:
        i += 1
        v = seq[i]
        if v[0] == '.L':
            continue
        if v[0] == 'UNPUSH':
            Debug('*Ignored stmt in class def', v)
            continue
        v2 = []
        if TCmp(v, v2, ('STORE', (('STORE_NAME', '?'),), ('?',))):
            if not one_store_clause(nm, v2[0], v2[1]):
                Debug('*Parse store clause illegal', v)
            continue
        if TCmp(v, v2, ('STORE', (('PyObject_SetItem', ('!LOAD_NAME', '?'), '?'),), ('?',))):
            continue
        if TCmp(v, v2, ('STORE', (('PyObject_SetItem', ('PY_TYPE', '?', '?', ('!LOAD_NAME', '?'), None), '?'),), ('?',))):
            continue
        if TCmp(v, v2, ('STORE', (('PyObject_SetAttr', ('!LOAD_NAME', '?'), '?'),), ('?',))):
            continue
        if TCmp(v, v2, ('STORE', (('PyObject_SetAttr', ('PY_TYPE', '?', '?', ('!LOAD_NAME', '?'), None), '?'),), ('?',))):
            continue
        ## if TCmp(v, v2, ('SEQ_ASSIGN', '?', '?')):
            ## for v2_0 in v2[0]:
                ## v2__ = []
                ## if TCmp(v2_0, v2__,  ('STORE_NAME', '?')):
                    ## if not one_store_clause(nm, v2__[0], None):
                        ## Debug('*Parse store clause illegal', v2_0)
                    ## continue
            ## continue
        if IsBeg(v[0]):
            oldi = i
            i = get_closed_pair(seq[:],i)
            _3(nm, 'ComplcatedClassDef', True)
            Debug('*Complicated meth|attr', seq[oldi:i+1])
            continue
        Debug('*Parse class def error', v) 

def parse_for_special_slot_class(nmcod, seq, nmcl):
    i = -1
    while i < len(seq)-1:
        i += 1
        v = seq[i]
        if v[0] == '.L':
            continue
        if v[0] == 'UNPUSH':
            continue
        v2 = []
        if TCmp(v, v2, ('STORE', (('STORE_NAME', '?'),), ('?',))) and v2[0] in ('__new__', '__del__'):
            v3 = []
            if TCmp(v2[1], v3, ('!PyObject_Call',('!LOAD_BUILTIN', 'staticmethod'), \
                                ('!BUILD_TUPLE', ('?',)), ('NULL',))):
                v2[1] = v3[0]
            elif TCmp(v2[1], v3, ('!PyObject_Call',('!LOAD_NAME', 'staticmethod'), \
                                ('!BUILD_TUPLE', ('?',)), ('NULL',))):
                v2[1] = v3[0]            
            nm_code = get_nmcode(nmcl, v2[1])
            if nm_code is None and v2[1][0] == '!MK_CLOSURE':
                nm_code = v2[1][1]
            if nm_code is not None:    
                no_compiled[nm_code] = True
            else:
                pprint.pprint(v)
                pprint.pprint(v2)
                Fatal(nmcod, v2, v)
        continue
    
def parse_constructor(nmclass, nmcode):
    seq = all_co[N2C(nmcode)].cmds[1]   
    for v in seq:
        v2 = []
        if TCmp(v, v2, ('STORE', (('PyObject_SetAttr', ('?', 'self'), ('CONST', '?')),), ('?',))):
            _3(nmclass, 'AttributeInstance', v2[1])
        
def repl_in_if_store(ret, old, new, stor, dele):
    ret = list(ret)
    if not (repr(stor) in repr(ret[0])) and ret[0][0] == '(IF':
        ret[0] = replace_subexpr(ret[0], old, new)
    else:
        return ret    
    if len(ret) == 3:
        ret[1] = repl_in_list_if_store(ret[1], old, new, stor, dele)
    elif len(ret) == 5:   
        ret[1] = repl_in_list_if_store(ret[1], old, new, stor, dele)
        ret[3] = repl_in_list_if_store(ret[3], old, new, stor, dele)
    return ret    

def repl_in_list_if_store(ret, old, new, stor, dele):
    j = 0
    while j < len(ret):
        if IsBeg(ret[j][0]):
            j1 = get_closed_pair(ret[:],j)
            if repr(stor) in repr(ret[j:j1]) or repr(dele) in repr(ret[j:j1]):
                if ret[j][0] == '(IF':
                    ret[j:j1] = repl_in_if_store(ret[j:j1], old, new, stor, dele)
                break
            ret[j:j1] = replace_subexpr(ret[j:j1], old, new)
            j = j1 + 1
        else:
            if repr(stor) in repr(ret[j]):
                if ret[j][0] == 'STORE' and len(ret[j][1]) == 1 and \
                    ret[j][1][0] == stor and len(ret[j][2]) == 1:
                    v2 = replace_subexpr(ret[j][2][0], old, new)
                    ret[j] = ('STORE', ret[j][1], (v2,))
                break
            elif repr(dele) in repr(ret[j]):
                break
            ret[j] = replace_subexpr(ret[j], old, new)
            j = j + 1
    return ret

def apply_typ(ret, d):
    for old, typ in d.iteritems():    
        if typ is None: 
            continue
        t = Klass(typ)
        new = ('PY_TYPE', t.descr, t.subdescr, old, None)   
        ret = replace_subexpr(ret, old, new)
    return ret   
    
def type_in_if(ret, d):
    if ret[0] == '!BOOLEAN':
        return ('!BOOLEAN', type_in_if(ret[1], d))
    if ret[0] in ('!AND_JUMP', '!AND_BOOLEAN'):
        return (ret[0],) + tuple([type_in_if(r, d) for r in ret[1:]])
    if ret[0] in ('!OR_JUMP', '!OR_BOOLEAN'):
        return apply_typ((ret[0],) + tuple([type_in_if(r, {}) for r in ret[1:]]), d)
    v = []
    old, nm = None, None
    if TCmp(ret, v, ('!_EQ_', ('!PyObject_Type', '?'), \
                                        ('!LOAD_BUILTIN', '?'))):
        old, nm = v                                       
    elif TCmp(ret, v, ('!_EQ_', ('!LOAD_BUILTIN', '?'), \
                                            ('!PyObject_Type', '?'))):
        nm, old = v
    elif TCmp(ret, v, ('!PyObject_RichCompare(', ('!LOAD_BUILTIN', '?'),  \
                ('!PyObject_Type', '?'), 'PyCmp_EQ')): 
        nm, old = v           
    elif TCmp(ret, v, ('!PyObject_RichCompare(', ('!PyObject_Type', '?'), \
                        ('!LOAD_BUILTIN', '?'), 'PyCmp_EQ')): 
        old, nm = v           
    if nm in d_built:
        ret = apply_typ(ret, d)
        if not old in d:
            d[old] = d_built[nm]
        else:
            d[old] = None
        return ret
    return apply_typ(ret, d)
        
def only_fast(d):
    d2 = {}
    for k,v in d.iteritems():
        if k[0] == 'FAST':
            d2[k] = v
    return d2
                
def recursive_type_detect(ret, nm):
    if type(ret) != list:
        return ret
    ret = ret[:]
    i = 0
    while i < len(ret):
        v = ret[i]
        head = v[0]
        ## if v[0] == '(FOR':
            ## _v = []
            ## if TCmp(v, _v,  ('(FOR', (('STORE_FAST', '?'),), \
                             ## ('!PyObject_Call', ('!LOAD_BUILTIN', 'range'), \
                              ## '?', ('NULL',)))):

                ## stor = ('STORE_FAST', _v[0])
                ## dele = ('DELETE_FAST', _v[0])
                ## old = ('FAST', _v[0])
                ## new = ('PY_TYPE', int, None, old, None)             
                ## j = i+1    
                ## if not repr(dele) in repr(ret[j]) and not repr(stor) in repr(ret[j]):
                    ## ret[j] = replace_subexpr(ret[j], old, new)
                ## i = i + 1
                ## continue    

        if v[0] == '(IF':
            d = {}
            ret[i] = ('(IF', type_in_if(v[1], d))
            d = only_fast(d)
            ## old, new, nm_typ = type_in_if(v[1])
            ## if old is not None and old[0] == 'FAST':
                ## dele = ('DELETE_FAST', old[1])
                ## stor = ('STORE_FAST', old[1])
                ## print 'repl type', old, new
## ##                ret[i+1] = apply_type_to_list(ret[i+1], old, new, stor, dele)
            i += 1
            continue    
        if v[0] == 'STORE' and len(v[1]) == 1 and v[1][0][0] in ('STORE_FAST', 'STORE_NAME') and \
           len(v[2]) == 1:
            t = TypeExpr(v[2][0])
            if t is not None:
                assert t.__class__.__name__ == 'Klass'
            if t == Kl_None and v[1][0][0] == 'STORE_NAME' and nm == 'Init_filename':
                pass
            elif t is not None :
                stor = v[1][0]
                dele = v[1][0]
                dele = ('DELETE_' + dele[0][6:], dele[1])
                nm = v[1][0][1]   
                if v[1][0][0] == 'STORE_FAST':
                    nm2 = ('FAST', nm)
                else:      
                    nm2 = ('!LOAD_NAME', nm)
                old = nm2
                new = ('PY_TYPE', t.descr, t.subdescr, nm2, None)             
                if t in _Kl_Simples and v[2][0][0] == 'CONST':
                    new = v[2][0]
                if v[2][0][0] == '!CLASS_CALC_CONST':    
                    new = ('PY_TYPE', t.descr, v[2][0][1], nm2, None)
                elif v[2][0][0] == '!CLASS_CALC_CONST_NEW':    
                    new = ('PY_TYPE', t.descr, v[2][0][1], nm2, None)
                j = i+1    
                while j < len(ret):
                    if IsBeg(ret[j][0]):
                        j1 = get_closed_pair(ret[:],j)
                        if repr(stor) in repr(ret[j:j1]):
                            if ret[j][0] == '(IF':
                                ret[j:j1] = repl_in_if_store(ret[j:j1], old, new, stor, dele)
                            break
                        ret[j:j1] = replace_subexpr(ret[j:j1], old, new)
                        j = j1 + 1
                    else:
                        if repr(stor) in repr(ret[j]):
                            if ret[j][0] == 'STORE' and len(ret[j][1]) == 1 and \
                               ret[j][1][0] == stor and len(ret[j][2]) == 1:
                                v2 = replace_subexpr(ret[j][2][0], old, new)
                                ret[j] = ('STORE', ret[j][1], (v2,))
                            break
                        elif repr(dele) in repr(ret[j]):
                            break
                        ret[j] = replace_subexpr(ret[j], old, new)
                        j = j + 1
        if type(ret[i]) is list:
            ret[i] = recursive_type_detect(ret[i], nm)            
        i += 1
    return ret                

def join_defined_calls(_calls, argcount, nm, is_varargs):
    l = []
    if is_varargs:
        argcount += 1    
    for c in _calls:
        a = []
        if c[0] == 'CONST':
            for _a in c[1]:
                a.append(('CONST', _a))
        elif c[0] == '!BUILD_TUPLE':
            for _a in c[1]:
                if _a[0] == 'CONST':
                    a.append(_a)
                elif _a[0] == 'PY_TYPE':
                    a.append((_a[1], _a[2])) 
                else:
                    t = TypeExpr(_a)
                    if t is not None:
                        a.append((t.descr, t.subdescr)) 
                    else:
                        a.append((None, None))    
        else:
            Fatal('Can\'t join calls', c, _calls)
        if argcount != len(a) and not is_varargs:
            if argcount > len(a):
                if nm in default_args:
                    cc = default_args[nm]
                    if cc[0] == 'CONST':
                        _refs2 = [('CONST', x) for x in cc[1]]
                    else:    
                        assert cc[0] == '!BUILD_TUPLE'
                        _refs2 = [x for x in cc[1]]
                    add_args = argcount - len(a)
                    pos_args = len(_refs2) - add_args
                    a = a + _refs2[pos_args:]
        elif is_varargs:
            if argcount -1 > len(a):
                if nm in default_args:
                    cc = default_args[nm]
                    if cc[0] == 'CONST':
                        _refs2 = [('CONST', x) for x in cc[1]]
                    else:    
                        assert cc[0] == '!BUILD_TUPLE'
                        _refs2 = [x for x in cc[1]]
                    add_args = ( argcount - 1 ) - len(a)
                    pos_args = len(_refs2) - add_args
                    a = a + _refs2[pos_args:]
            new_a = []
            for i in range(argcount-1):
                new_a.append(a[i])
            new_a.append((tuple, None))
            a = new_a     
        assert len(a) == argcount                    
        l.append(a)
    l2 = []    
    for i in range(argcount):
        d = {}
        for j,ll in enumerate(l):
            d[ll[i]] = True
        if len(d) > 1:
            d2 = {}
            for k,v in d.iteritems():
                if type(k) is tuple and k[0] == 'CONST':
                    k = (type(k[1]), None)
                d2[k] = v
            d = d2   
        if len(d) > 1:
            d = {None:True}
        l2.append(d.keys()[0])
    l = l2           
    return l

def dotted_name_to_first_name(nm):
    if '.' in nm:
        return nm.split('.')[0]
    return nm

def filter_founded_calc_const(p, k, do_del):
    v = []
    if TCmp(p, v, ('STORE', (('STORE_NAME', '?'),), \
                       (('!IMPORT_NAME', '?', ('CONST', -1), ('CONST', None)),))):
        if v[0] == k:
            all_calc_const[k] = p[2][0]
            _3(k, 'ImportedM', dotted_name_to_first_name(v[1]))
    elif p[0] == 'STORE' and len(p[1]) == len(p[2]) == 1:
        if p[2][0][0] in ('!LOAD_NAME', '!LOAD_GLOBAL') and  p[2][0][1] in all_calc_const:
            if p[1][0][0] in ('STORE_NAME', 'STORE_GLOBAL') and p[1][0][1] == k:
                ok = p[2][0][1]
                all_calc_const[k] =  all_calc_const[ok]
                if ok in no_compiled:
                    no_compiled[k] = no_compiled[ok]
                if ok in default_args:
                    default_args[k] = default_args[ok]
                if ok in mnemonic_constant:
                    mnemonic_constant[k] = mnemonic_constant[ok]
                if ok in direct_code:
                    direct_code[k] = direct_codet[ok]
                if ok in val_direct_code:
                    val_direct_code[k] = val_direct_codet[ok]
                if ok in detected_return_type:
                    detected_return_type[k] = detected_return_type[ok]
                if ok in calc_const_value:
                    calc_const_value[k] = calc_const_value[ok]
                for a,b,c in Iter3(ok, None, None):
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    _3(k, b,c)
        elif p[2][0][0] == 'CONST' or\
             TCmp(p[2][0], v, ('!PyObject_GetAttr', ('CONST', '?'), ('CONST', '?'))):
            if p[2][0][1] is not None:
                if p[1][0][0] in ('STORE_NAME', 'STORE_GLOBAL') and p[1][0][1] == k:
                    all_calc_const[k] = p[2][0]
                    mnemonic_constant[k] = p[2][0]
                elif p[1][0][0] == 'SET_VARS' and (('STORE_NAME', k) in p[1][0][1] or ('STORE_GLOBAL', k) in p[1][0][1]):
                    all_calc_const[k] = p[2][0]
                    mnemonic_constant[k] = p[2][0]
                else:
                    Fatal('--590--', p)
            return    
            
#        elif p[2][0][0] == 'CALC_CONST':
#            if p[1][0][0] in ('STORE_NAME', 'STORE_GLOBAL') and p[1][0][1] == k:
        
        elif p[2][0][0] == '!IMPORT_NAME':
            if p[1][0][0] in ('STORE_NAME', 'STORE_GLOBAL') and p[1][0][1] == k and\
                p[2][0][2] == ('CONST', -1) and p[2][0][3] == ('CONST', None):
                all_calc_const[k] = p[2][0]
                _3(k, 'ImportedM', dotted_name_to_first_name(p[2][0][1]))
            else:
                Fatal('--597--', p)
            return    
        else:
            if p[1][0][0] in ('STORE_NAME', 'STORE_GLOBAL') and p[1][0][1] == k:
                all_calc_const[k] = p[2][0]
            return
#        if p[2][0][0][0] == '!':
#            return
    elif p[0] == 'IMPORT_STAR':
        print p
    elif p[0] == 'IMPORT_FROM_AS' and\
        TCmp(p, v, ('IMPORT_FROM_AS', '?', ('CONST', '?'), ('CONST', '?'), '?')):
        sreti = []
        del v[1] ## Hack !!!!!!!!!!!!!!!!!!!!!!!!!!!
        imp, consts_, stores = v
        for i, reti in enumerate(stores):
            v = []
            if reti[0] in ('STORE_NAME', 'STORE_GLOBAL') and reti[1] == k:
                all_calc_const[k] = '???'
                v = IfConstImp(imp, consts_[i])
                if v is not None:
                    mnemonic_constant[k] = v
                else:
                    _3(k, 'ImportedM', (imp, consts_[i]))                
                    if (imp, consts_[i], 'val') in t_imp:
                        t = t_imp[(imp, consts_[i], 'val')]
                        if t.is_new_class_typ():
                            _3(k, 'CalcConstNewClass', '???')
                        elif t.is_old_class_typ():
                            _3(k, 'CalcConstOldClass', '???')
        return
    elif p[0] in (')(EXCEPT', '(FOR'):
        do_del.append(k)    
        return
    elif p[0] == 'SEQ_ASSIGN':
        if ('STORE_NAME', k) in p[1]:
            all_calc_const[k] = p[2]
        else:
            for pi in p[1]:
                if pi[0] == 'SET_VARS':
                    if ('STORE_NAME', k) in pi[1]:
                        all_calc_const[k] = p[2]     
    elif p[0] == 'SEQ_ASSIGN' and ('STORE_NAME', k) in p[1]:
        all_calc_const[k] = p[2]
    elif p[0] == 'SET_EXPRS_TO_VARS' and ('STORE_NAME', k) in p[1]:
        all_calc_const[k] = p[2]    
    elif p[0] == 'UNPUSH':
        return
    elif p[0] == '!LIST_COMPR':
        return
    elif p[0] == 'PRINT_ITEM_1':
        return
    else:
        Fatal('can\'t handle CALC_CONST', p, k)
 
list_ext = []
 
def compile_c(base, cname):
    optio = '-O0'
    if opt_flag is not None:
      optio = opt_flag
    example_mod = distutils.core.Extension(cname[0:-2], sources = [cname], \
                                           extra_compile_args = [optio], \
                                           extra_link_args = [])
    a = distutils.core.setup(name = cname[0:-2],
        version = "1.0",
        description = "Compiled to C Python code " + base,
        ext_modules = [example_mod],
        script_name = 'install' ,
        script_args = ['build_ext']
        )
    list_ext.append(example_mod)    

def link_c():
    a = distutils.core.setup(name = 'install_all',
        version = "1.0",
        description = "Compiled to C Python code",
        ext_modules = list_ext,
        script_name = 'install' ,
        script_args = ['install']
        )

def unjumpable(cmd):
  if len(cmd) == 1:
      if cmd[0] in ('RETURN_VALUE', 'EXEC_STMT'):
        return False
      if cmd[0][0:6] in ('BINARY', 'UNARY_'):
        return False
  if cmd[0] in set_any:
      return False
  if cmd[0] in _unjump_cmds:              
      return False
  if cmd[0] == 'RAISE_VARARGS' and cmd[1] != 0:
      return False
  if cmd[0] in ('STORE', 'SEQ_ASSIGN', 'SET_EXPRS_TO_VARS', 'UNPUSH'):
      return True
  if cmd[0][0] in ('J', '(', ')')  :
      return False
  if cmd[0] == 'LOAD_CONST':
      return False
  return not type(cmd) is list and \
         cmd[0] is not None and cmd[0][0] != '!' and cmd[0] not in ('LOAD_FAST', 'LOAD_CLOSURE') and \
         cmd[0][0] not in ('J', '(', ')') and cmd[0][0:2] != '.:'

def linear_to_seq(cmds):
    ret = []
    i = 0
    while i < len(cmds):
        cmd = cmds[i]
        if not unjumpable(cmd):
            ret.append(cmd)
            i = i + 1
            continue
        ret2 = []
        while unjumpable(cmd) or type(cmd) is list:
            if type(cmd) is list:
                ret2.extend(cmd[:])
            else:    
                ret2.append(cmd)
            i = i + 1
            if  i < len(cmds):
              cmd = cmds[i]
            else:
                break  
        if len(ret) > 0 and type(ret[-1]) is list:
            ret[-1] = ret[-1] + ret2
        else:    
            ret.append(ret2)
        continue
    cmds[:] = ret[:]    
        
def jump_to_continue_and_break(cmds):        
    i = 0
    loops = [(i,pos_label(cmds, x[1])) for i,x in enumerate(cmds) if x[0] in ('J_SETUP_LOOP', 'J_SETUP_LOOP_FOR')]
    breaks = {}
    continues = {}
    ranges = {}
    for a,b in loops:
        j = a + 1
        while j < len(cmds) and j < b:
            if cmds[j][0] == '.:':
                continues[a] = cmds[j][1]
                break
            if (cmds[j][0][0:4] == 'JUMP' or cmds[j][0][0:7] == 'J_SETUP'):
                break
            j = j + 1 
        ranges[a] = set([i for i in range(a,b) if cmds[i][0][0] == 'J'])
    inter = [(a1,b1, a2,b2) for a1,b1 in loops for a2,b2 in loops if a2 > a1 and b2 < b1]
    for a1,b1,a2,b2 in inter:
        ranges[a1] = ranges[a1] - ranges[a2]
    for a,b in loops:
        for i in ranges[a]:
            cmd = cmds[i]
            if cmd[0] in jump and a in continues and cmd[1] == continues[a]:
                cmds[i] = ('JUMP_CONTINUE',) + cmd[1:]
            if cmd[0] == 'JUMP_IF_TRUE_POP' and a in continues and cmd[1] == continues[a]:
                cmds[i] = ('JUMP_IF_TRUE_POP_CONTINUE',) + cmd[1:]
            if cmd[0] == 'JUMP_IF_FALSE_POP' and a in continues and cmd[1] == continues[a]:
                cmds[i] = ('JUMP_IF_FALSE_POP_CONTINUE',) + cmd[1:]
            if cmd[0] == 'JUMP_IF2_TRUE_POP' and a in continues and cmd[1] == continues[a]:
                cmds[i] = ('JUMP_IF2_TRUE_POP_CONTINUE',) + cmd[1:]
            if cmd[0] == 'JUMP_IF2_FALSE_POP' and a in continues and cmd[1] == continues[a]:
                cmds[i] = ('JUMP_IF2_FALSE_POP_CONTINUE',) + cmd[1:]

def prin(n,cmd,cmds = None):
    if isblock(cmd):
        print >>out,n, '{'
        print_cmds2(cmd, 2)
        print >>out,'}'
    elif cmd[0] == '.:':
        print >>out,n,cmd, CntJump(cmd[1],cmds) 
    else:
        print >>out,n,cmd 
          
def label(j,l):
    return j[0][0] == 'J' and l[0] == '.:' and l[1] == j[1]

def endlabel(j,l):
    return j[0][0] == 'J' and (l[0] == '.:' or l[0] in jump) and l[1] == j[1]                            

def cmds_join(i,cmds):
    if i >= len(cmds):
        return
    if i > 0 and type(cmds[i]) is list and type(cmds[i-1]) is list:
        cmds[i-1] = cmds[i-1] + cmds[i]
        del cmds[i]
        cmds_join(max(0,i-1),cmds)
        cmds_join(i,cmds)
        cmds_join(min(len(cmds)-1,i+1),cmds)
        return
    if i < len(cmds)-1 and type(cmds[i]) is list and type(cmds[i+1]) is list:
        cmds[i] = cmds[i] + cmds[i+1]
        del cmds[i+1]
        cmds_join(max(0,i-1),cmds)
        cmds_join(i,cmds)
        cmds_join(min(len(cmds)-1,i+1),cmds)
        return
    if i < len(cmds)-1 and i > 0 and \
        type(cmds[i-1]) is list and unjumpable(cmds[i]) and type(cmds[i+1]) is list:
        cmds[i] = cmds[i-1] + [cmds[i]] + cmds[i+1]
        del cmds[i-1]
        del cmds[i]
        cmds_join(max(0,i-1),cmds)
        cmds_join(i,cmds)
        cmds_join(min(len(cmds)-1,i+1),cmds)
        return
    if i > 0 and unjumpable(cmds[i]) and type(cmds[i-1]) is list:
        cmds[i-1] = cmds[i-1] + [cmds[i]]
        del cmds[i]
        cmds_join(max(0,i-1),cmds)
        cmds_join(i,cmds)
        cmds_join(min(len(cmds)-1,i+1),cmds)
        return
    if i < len(cmds)-1 and type(cmds[i]) is list and unjumpable(cmds[i+1]):
        cmds[i] = cmds[i] + [cmds[i+1]]
        del cmds[i+1]
        cmds_join(max(0,i-1),cmds)
        cmds_join(i,cmds)
        cmds_join(min(len(cmds)-1,i+1),cmds)
        return
    if i < len(cmds)-1 and type(cmds[i+1]) is list and unjumpable(cmds[i]):
        cmds[i] = [cmds[i]] + cmds[i+1]
        del cmds[i+1]
        cmds_join(max(0,i-1),cmds)
        cmds_join(i,cmds)
        cmds_join(min(len(cmds)-1,i+1),cmds)
        return
    if i > 0 and unjumpable(cmds[i]) and not type(cmds[i]) is list and\
       not type(cmds[i-1]) is list and cmds[i-1][0] == '.L':
        cmds[i-1] = [cmds[i-1],cmds[i]]
        del cmds[i]
        cmds_join(max(0,i-1),cmds)        
        return
    if unjumpable(cmds[i]) and not type(cmds[i]) is list :
        cmds[i] = [cmds[i]]
        return
    
def print_pr(cmds):    
    global pos__a,pos__b,pos__c,pos__d,pos__e,pos__f,pos__g,pos__h,pos__i,pos__j,pos__k,pos__l
    prin (1,pos__a, cmds)
    prin (2,pos__b, cmds)
    prin (3,pos__c, cmds)
    prin (4,pos__d, cmds)
    prin (5,pos__e, cmds)
    prin (6,pos__f, cmds)        
    prin (7,pos__g, cmds) 
    prin (8,pos__h, cmds)        
    prin (9,pos__i, cmds) 
    prin (10,pos__j, cmds) 
    prin (11,pos__k, cmds) 
    prin (12,pos__l, cmds) 
    print >>out, ''     
                            
def half_recompile(cmds, co):
    global debug
    global pos__a,pos__b,pos__c,pos__d,pos__e,pos__f,pos__g,pos__h,pos__i,pos__j,pos__k,pos__l
    i = 0
    totemp = [(None,)] * 12
    oldi = -1
    first = True
    last = False
    added_pass = False
#    debug = False
    only_matched = False
    if debug:
        print >>out, 'Step 0'
        print_cmds(cmds)
    while i <= len(cmds):   
        if first and i == len(cmds):
            if debug:
                print >>out, 'Step 1'
                print_cmds(cmds)
            linear_to_seq(cmds)
            NoGoToGo(cmds)
            jump_to_continue_and_break(cmds)
            i = 0
            first = False
        elif not first and i == len(cmds) and not last and len(cmds) > 2:   
            if debug:
                print >>out, 'Step 2'
                print_cmds(cmds)
            added_pass = True
            NoGoToGo(cmds)
            NoGoToReturn(cmds)
            jump_to_continue_and_break(cmds)
            i = 0
            first = False
            last = True
            i = 0
            while i < len(cmds):
                if islineblock(cmds[i]):
                    del cmds[i]
                    continue
                i = i + 1
            i = 0      
        bingo = False    
        if oldi == i:
            bingo = True
            prevlen = len(cmds)
            if debug == True:
                tempor = cmds[i:i+12]
                while len(tempor) < 12:
                    tempor.append((None,))
                pos__a,pos__b,pos__c,pos__d,pos__e,pos__f,pos__g,pos__h,pos__i,pos__j,pos__k,pos__l = tempor
                print >>out, '!!!!!!',i, '!!!!!!'
                print_pr(cmds)
            _len = len(cmds)           
            cmds_join(i,cmds)
            i -= 12
            if len(cmds) < _len:
                i -= _len - len(cmds)
        if i < 0:
            i = 0 
        oldi = i
        tempor = cmds[i:i+12]
        if len(tempor) < 12:
            tempor = (tempor + totemp)[:12]
        pos__a,pos__b,pos__c,pos__d,pos__e,pos__f,pos__g,pos__h,pos__i,pos__j,pos__k,pos__l = tempor
        if debug == True and not only_matched:
            if bingo:
                print >>out, '*****',i, '*****'
            else:
                print >>out, '--',i, '--'
            print_pr(cmds)

        begin_cmp()
        if type(pos__a) is tuple and len(pos__a) >= 1:
            if pos__a[0] is not None and pos__a[0][0:4] == 'JUMP' and\
            pos__a[0] != 'JUMP_IF_NOT_EXCEPTION_POP':
                changed_jump = process_jump(cmds,i,added_pass)
                if changed_jump:
                    continue
            if pos__a[0] == 'J_FOR_ITER':
                if pos__b[0] in set_any:
                    cmds[i:i+2] = [('J_LOOP_VARS', pos__a[1], (pos__b,))]
                    continue
                if islineblock(pos__b) and pos__c[0] in set_any:
                    cmds[i:i+3] = [('J_LOOP_VARS', pos__a[1], (pos__c,))]
                    continue
                if pos__b[0] == 'UNPACK_SEQ_AND_STORE' and pos__b[1] == 0:
                    b2 = pos__b[2]
                    if len(b2) == 1:
                        b2 += (None,)
                    cmds[i:i+2] = [('J_LOOP_VARS', pos__a[1], b2)]
                    continue
            if pos__a[0] == '.:':
                if SCmp(cmds, i, ((':', 4), 'J_LOOP_VARS', '>', \
                                'LIST_APPEND', 'JUMP', '.:')) and \
                                pos__a[1] != pos__b[1] and pos__f[0] != pos__b[1] and len(pos__d) == 2:  
                    rpl(cmds, [pos__a, ('J_BASE_LIST_COMPR', pos__b[1], (cmd2mem(pos__c),), (pos__b[2], None, ())),pos__f]                )
                    continue    
                if SCmp(cmds, i, ((':', 4), 'J_LOOP_VARS', '>', \
                                ('SET_ADD', 2), 'JUMP', '.:')) and \
                                pos__a[1] != pos__b[1] and pos__f[0] != pos__b[1] :  
                    rpl(cmds, [pos__a, ('J_BASE_SET_COMPR', pos__b[1], (cmd2mem(pos__c),), (pos__b[2], None, ())),pos__f]                )
                    continue    
                if SCmp(cmds, i, ((':', 4), 'J_LOOP_VARS', '>', '>', \
                                ('MAP_ADD', 2), 'JUMP', '.:')) and \
                                pos__a[1] != pos__b[1] and pos__g[0] != pos__b[1] :  
                    rpl(cmds, [pos__a, ('J_BASE_MAP_COMPR', pos__b[1], (cmd2mem(pos__d),cmd2mem(pos__c),), (pos__b[2], None, ())),pos__g]   )
                    continue    
                if SCmp(cmds, i, ((':', 5), 'J_LOOP_VARS', 'JUMP_IF2_TRUE_POP', '>', \
                                'LIST_APPEND', 'JUMP', '.:')) and \
                                pos__a[1] != pos__b[1] and pos__g[0] != pos__b[1] and len(pos__e) == 2:  
                    rpl(cmds, [pos__a, ('J_BASE_LIST_COMPR', pos__b[1], (cmd2mem(pos__d),), (pos__b[2], None, (Not(pos__c[2]),))),pos__g]                )
                    continue    
                if SCmp(cmds, i, ((':', 5), 'J_LOOP_VARS', 'JUMP_IF2_FALSE_POP', '>', \
                                'LIST_APPEND', 'JUMP', '.:')) and \
                                pos__a[1] != pos__b[1] and pos__g[0] != pos__b[1] and len(pos__e) == 2:  
                    rpl(cmds, [pos__a, ('J_BASE_LIST_COMPR', pos__b[1], (cmd2mem(pos__d),), (pos__b[2], None, (pos__c[2],))),pos__g]                )
                    continue    
                
            if pos__a[0] == '.L':
                if pos__b[0] in jump and len(pos__b) == 2:
                    cmds[i:i+2] = [(pos__b[0], pos__b[1], pos__a[1])]
                    continue
                if pos__b[0] == 'J_SETUP_LOOP' and len(pos__b) == 2:
                    cmds[i:i+2] = [('J_SETUP_LOOP', pos__b[1], pos__a[1])]
                    continue
                if pos__b[0] == '.L':
                    cmds[i:i+2] = [pos__b]
                    continue
                if pos__b[0] == 'DUP_TOP' and is_cmdmem(pos__c) and \
                    len(pos__d) == 2 and pos__d[0] == 'COMPARE_OP' and pos__d[1] == 'exception match':
                    cmds[i:i+4] = [('CHECK_EXCEPTION', cmd2mem(pos__c), pos__a[1])]
                    continue  
    
            if pos__a[0] == 'DELETE_FAST' and pos__a[1][0:2] == '_[':
                cmds[i] = (')END_LIST_COMPR', ('FAST', pos__a[1]))
                continue
            if pos__a[0] == 'DELETE_NAME' and pos__a[1][0:2] == '_[':
                cmds[i] = (')END_LIST_COMPR', ('NAME', pos__a[1]))
                continue
            if pos__a[0] == 'UNPACK_SEQUENCE' and len(pos__a) == 2 and pos__a[1] > 0 and pos__b[0] in set_any:
                cmds[i] = ('UNPACK_SEQ_AND_STORE', pos__a[1], ())
                continue
            if pos__a[0] == 'UNPACK_SEQUENCE' and len(pos__a) == 2 and pos__a[1] > 0 and pos__b[0] == 'UNPACK_SEQ_AND_STORE':
                cmds[i] = ('UNPACK_SEQ_AND_STORE', pos__a[1], ())
                continue
            if pos__a[0] == 'UNPACK_SEQ_AND_STORE':
                if pos__a[1] == 0:
                    cmds[i] = ('SET_VARS', pos__a[2])
                    continue
                if pos__a[1] > 0 and pos__b[0] == '.L' and pos__c[0] in set_any:
                    cmds[i:i+3] = [('UNPACK_SEQ_AND_STORE', pos__a[1]-1, pos__a[2] + (pos__c,))]
                    continue
                if pos__a[1] > 0 and pos__b[0] in set_any:
                    cmds[i:i+2] = [('UNPACK_SEQ_AND_STORE', pos__a[1]-1, pos__a[2] + (pos__b,))]
                    continue
                if pos__a[1] > 0 and pos__b[0] == 'UNPACK_SEQ_AND_STORE' and pos__b[1] == 0 :
                    cmds[i:i+2] = [('UNPACK_SEQ_AND_STORE', pos__a[1]-1, pos__a[2] + (pos__b,))]
                    continue
            if pos__a[0] == 'LOAD_CODEFUNC' and pos__b[0] == 'MAKE_FUNCTION':
                cmds[i:i+2] = [('MK_FUNK', pos__a[1], pos__b[1], ())]
                continue
            if pos__a[0] == 'MK_FUNK' and pos__a[2] == 0:
                cmds[i:i+1] = [('!MK_FUNK', pos__a[1], TupleFromArgs(pos__a[3]))]
                continue
            if pos__a[0] == 'MK_CLOSURE' and pos__a[2] == 0:
                cmds[i:i+1] = [('!MK_CLOSURE', pos__a[1], pos__a[3], TupleFromArgs(pos__a[4]))]
                continue
            if pos__a[0] == 'IMPORT_FROM' and pos__b[0] in set_any:
                cmds[i:i+2] = [('IMPORT_AND_STORE_AS', (pos__a[1],), (pos__b,))] 
                continue
                continue
            if pos__a[0] == 'IMPORT_AND_STORE_AS' and pos__b[0] == 'IMPORT_AND_STORE_AS':
                cmds[i:i+2] = [('IMPORT_AND_STORE_AS', pos__a[1] + pos__b[1], pos__a[2] + pos__b[2])] 
                continue
            if pos__a[0] == '!IMPORT_NAME' and pos__b[0] == 'IMPORT_AND_STORE_AS' and pos__c[0] == 'POP_TOP' and pos__a[3][1] == pos__b[1]:
                cmds[i:i+3] = [('IMPORT_FROM_AS', pos__a[1], pos__a[2], pos__a[3], pos__b[2])]
                continue    
    # LOAD_CLOSURE  and LOAD_DEREF marked as 'pure' ? or not ?        
            if pos__a[0] in ('LOAD_GLOBAL', 'LOAD_NAME'):
                if pos__a[1] in ('True', 'False', 'None'):
                    if pos__a[1] == 'True':
                        cmds[i] = ('LOAD_CONST', True)
                    elif pos__a[1] == 'False':
                        cmds[i] = ('LOAD_CONST', False)
                    elif pos__a[1] == 'None':
                        cmds[i] = ('LOAD_CONST', None)
                    continue
                if not redefined_all and pos__a[1] in d_built and \
                (pos__a[1][0:2] != '__' or pos__a[1] in ('__import__',) )and \
                    not  pos__a[1] in redefined_builtin:
                        cmds[i] = ('!LOAD_BUILTIN', pos__a[1])
                        continue
                if pos__a[0] == 'LOAD_GLOBAL':
                    cmds[i] = ('!LOAD_GLOBAL', pos__a[1])
                    continue
                if pos__a[0] == 'LOAD_NAME':
                    cmds[i] = ('!LOAD_NAME', pos__a[1])
                    continue
            if pos__a[0] == 'LOAD_DEREF':
                cmds[i] = ('!LOAD_DEREF', pos__a[1])
                continue
            if pos__a[0] == 'BUILD_LIST' and pos__a[1] == 0:
                if len(pos__a) == 3:
                    cmds[i] = ('!BUILD_LIST', pos__a[2])
                else:
                    cmds[i] = ('!BUILD_LIST', ())
                continue
            if pos__a == ('!BUILD_LIST', ()) and pos__b[0] == '!GET_ITER':
                changed_list_compr = process_list_compr_2(cmds,i,added_pass)
                if changed_list_compr:
                    continue
                
            if pos__a[0] == 'BUILD_TUPLE' and pos__a[1] == 0:
                if len(pos__a) == 3:
                    cmds[i] = TupleFromArgs(pos__a[2])
                else:
                    cmds[i] = ('CONST', ())
                continue
            if pos__a[0] == 'BUILD_SET':
                if pos__a[1] == 0 and len(pos__a) == 3 :
                    cmds[i] = ('!BUILD_SET', pos__a[2])
                    continue            
                if pos__a[1] == 0 and len(pos__a) == 2:
                    cmds[i] = ('!BUILD_SET', ())
                    continue         

            if pos__a == ('!BUILD_SET', ()) and pos__b == ('LOAD_FAST', '.0') and \
               pos__c[0] == 'J_BASE_SET_COMPR' and pos__d == ('.:', pos__c[1]):
                if pos__c[3][1] is None:
                    if pos__c[3][2] == ():
                        cmds[i:i+4] = [('!SET_COMPR', pos__c[2], (pos__c[3][0], (cmd2mem(pos__b),), None))]
                        continue 
                    else:
                        cmds[i:i+4] = [('!SET_COMPR', pos__c[2], (pos__c[3][0], (cmd2mem(pos__b),), pos__c[3][2]))]
                        continue   
                    
            if pos__a == ('!PyDict_New',) and pos__b == ('LOAD_FAST', '.0') and \
               pos__c[0] == 'J_BASE_MAP_COMPR' and pos__d == ('.:', pos__c[1]):
                if pos__c[3][1] is None:
                    if pos__c[3][2] == ():
                        cmds[i:i+4] = [('!MAP_COMPR', pos__c[2], (pos__c[3][0], (cmd2mem(pos__b),), None))]
                        continue 
                    else:
                        cmds[i:i+4] = [('!MAP_COMPR', pos__c[2], (pos__c[3][0], (cmd2mem(pos__b),), pos__c[3][2]))]
                        continue   

                     
            if pos__a[0] == 'BUILD_MAP':
                if pos__a[1] == 0 and len(pos__a) == 2:
                    cmds[i] = ('!PyDict_New',)
                    continue
                if pos__a[1] > 0 and len(pos__a) == 2:
                    cmds[i] = ('BUILD_MAP', pos__a[1], ())
                    continue
                if pos__a[1] > 0 and len(pos__a) == 3 and pos__b[0] == 'STORE_MAP':
                    cmds[i:i+2] = [('BUILD_MAP', pos__a[1]-1, pos__a[2] + ((pos__b[1], pos__b[2]),))]
                    continue
                if pos__a[1] == 0 and len(pos__a) == 3 :
                    cmds[i] = ('!BUILD_MAP', pos__a[2])
                    continue
                if pos__a[1] > 0 and len(pos__a) == 3 and pos__b[0] == '.L':
                    cmds[i:i+2] = [pos__a]
                    continue  
            if pos__a[0] == 'YIELD_VALUE' and len(pos__a) == 2 and pos__b[0] == 'POP_TOP':
                cmds[i:i+2] = [('YIELD_STMT', pos__a[1])]
                continue
            if pos__a[0] == 'LOAD_LOCALS' and pos__b[0] == 'RETURN_VALUE' and len(pos__b) == 1:
                cmds[i:i+2] = [(pos__b[0], ('f->f_locals',))]
                continue
            if pos__a[0] == 'RAISE_VARARGS' and pos__a[1] == 0 and pos__b[0] == 'POP_TOP':
                cmds[i:i+2] = [('RAISE_VARARGS_STMT',) + pos__a[1:]]
                continue            
            if pos__a[0] == '.:':
                if CntJump(pos__a[1], cmds) == 0:
                    del cmds[i]
                    continue
                if pos__b[0] == 'J_LOOP_VARS' and pos__c[0] == 'JUMP_IF2_FALSE_POP_CONTINUE' and\
                        pos__c[1] == pos__a[1] and isretblock(pos__d) and pos__e[0] == '.:' and pos__b[1] == pos__e[1]:
                    cmds[i:i+5] = [pos__a,pos__b,[('(IF',) + pos__c[2:], pos__d, (')ENDIF',)],('JUMP_CONTINUE', pos__a[1]),pos__e]
                    continue
                if pos__b[0] == 'J_LOOP_VARS' and pos__c[0] == 'JUMP_IF2_FALSE_POP_CONTINUE' and\
                        pos__c[1] == pos__a[1] and isblock(pos__d) and pos__e[0] == '.:' and pos__b[1] == pos__e[1]:
                    cmds[i:i+5] = [pos__a,pos__b,[('(IF',) + pos__c[2:], pos__d, (')(ELSE',), [('CONTINUE',)],(')ENDIF',)],pos__e]
                    continue
                if  SCmp(cmds,i, ('.:', '.:')):
                    for iii in range(len(cmds)):
                        if cmds[iii][0][0] == 'J' and cmds[iii][1] == pos__a[1]:
                            li = list(cmds[iii])
                            li[1] = pos__b[1]
                            cmds[iii] = tuple(li)
                    del cmds[i]
                    continue        
    
            if pos__a[0] == 'DUP_TOP' and is_cmdmem(pos__b) and \
            len(pos__c) == 2 and pos__c[0] == 'COMPARE_OP' and pos__c[1] == 'exception match':
                cmds[i:i+3] = [('CHECK_EXCEPTION', cmd2mem(pos__b))]
                continue  
            if pos__a[0] == 'CHECK_EXCEPTION':
                if pos__b[0] == 'JUMP_IF_FALSE_POP' and\
                pos__c[0] == 'POP_TOP3' :
                    cmds[i:i+3] = [('JUMP_IF_NOT_EXCEPTION_POP', pos__b[1], pos__a[1:],())]
                    continue
                if pos__b[0] == 'JUMP_IF_FALSE_POP' and\
                pos__c[0] == 'POP_TOP' and pos__d[0] in set_any and\
                pos__e[0] == 'POP_TOP':
                    cmds[i:i+5] = [('JUMP_IF_NOT_EXCEPTION_POP', pos__b[1], pos__a[1:], (pos__d,))]
                    continue
                if pos__b[0] == 'JUMP_IF_FALSE_POP' and\
                pos__c[0] == 'POP_TOP' and pos__d[0] in ('UNPACK_SEQ_AND_STORE',) and pos__d[1] == 0 and\
                pos__e[0] == 'POP_TOP':
                    cmds[i:i+5] = [('JUMP_IF_NOT_EXCEPTION_POP', pos__b[1], pos__a[1:], pos__d[:])]
                    continue
            if pos__a[0] == 'POP_TOP' and pos__b[0] == 'POP_TOP' and pos__c[0] == 'POP_TOP':
                cmds[i:i+3] = [('POP_TOP3',)]
                continue    
            if pos__a[0] == '!GET_ITER':
                if  pos__b[0] == '.:' and\
                    pos__c[0] == 'J_LOOP_VARS' and\
                    pos__d[0] in ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_FALSE_POP_CONTINUE') and\
                    pos__e[0] == 'PyList_Append' and \
                    pos__f[0] in ('JUMP', 'JUMP_CONTINUE') and\
                    pos__g[0] == '.:'and\
                    pos__h[0] == ')END_LIST_COMPR':
                        cmds[i:i+8] = [('BASE_LIST_COMPR', pos__e[2:], (pos__c[2], pos__a[1:], (pos__d[2],))),pos__g,pos__h] # vars in for, iter in fors, condidion 
                        continue
                if  pos__b[0] == '.:' and\
                    pos__c[0] == 'J_LOOP_VARS' and\
                    pos__d[0] in ('JUMP_IF2_TRUE_POP', 'JUMP_IF2_TRUE_POP_CONTINUE') and\
                    pos__e[0] == 'PyList_Append' and \
                    pos__f[0] in ('JUMP', 'JUMP_CONTINUE') and\
                    pos__g[0] == '.:'and\
                    pos__h[0] == ')END_LIST_COMPR':
                        cmds[i:i+8] = [('BASE_LIST_COMPR', pos__e[2:], (pos__c[2], pos__a[1:], (Not(pos__d[2]),))),pos__g,pos__h] # vars in for, iter in fors, condidion 
                        continue
                if  pos__b[0] == '.:' and\
                    pos__c[0] == 'J_LOOP_VARS' and\
                    pos__d[0] == 'PyList_Append' and \
                    pos__e[0] in ('JUMP', 'JUMP_CONTINUE') and\
                    pos__f[0] == '.:'and\
                    pos__g[0] == ')END_LIST_COMPR':
                        cmds[i:i+7] = [('BASE_LIST_COMPR', pos__d[2:], (pos__c[2], pos__a[1:], None)),pos__f,pos__g] # vars in for, iter in fors, condidion 
                        continue
                if  pos__b[0] == '.:' and\
                    pos__c[0] == 'J_LOOP_VARS' and\
                    pos__d[0] in ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_FALSE_POP_CONTINUE') and\
                    pos__e[0] == 'BASE_LIST_COMPR' and\
                    pos__f[0] == '.:' and \
                    pos__g[0] == ')END_LIST_COMPR':
                        cmds[i:i+7] = [('BASE_LIST_COMPR', pos__e[1], (pos__c[2], pos__a[1:], (pos__d[2],)) +pos__e[2]),pos__f,pos__g]
                        continue
                if  pos__b[0] == '.:' and\
                    pos__c[0] == 'J_LOOP_VARS' and\
                    pos__d[0] == 'JUMP_IF2_TRUE_POP' and\
                    pos__e[0] == 'BASE_LIST_COMPR' and\
                    pos__f[0] == '.:' and \
                    pos__g[0] == ')END_LIST_COMPR':
                        cmds[i:i+7] = [('BASE_LIST_COMPR', pos__e[1], (pos__c[2], pos__a[1:], (pos__d[2],)) +pos__e[2]),pos__f,pos__g]
                        continue
                if  pos__b[0] == '.:' and\
                    pos__c[0] == 'J_LOOP_VARS' and\
                    pos__d[0] == 'BASE_LIST_COMPR' and\
                    pos__e[0] == '.:' and \
                    pos__f[0] == ')END_LIST_COMPR':
                        cmds[i:i+6] = [('BASE_LIST_COMPR', pos__d[1], (pos__c[2], pos__a[1:], None) +pos__d[2]),pos__e,pos__f]
                        continue
                if  pos__b[0] == '.:' and\
                    pos__c[0] == 'J_LOOP_VARS' and\
                    pos__d[0] == '.L' and\
                    pos__e[0] == 'BASE_LIST_COMPR' and\
                    pos__f[0] == '.:' and \
                    pos__g[0] == ')END_LIST_COMPR':
                        cmds[i:i+7] = [('BASE_LIST_COMPR', pos__e[1], (pos__c[2], pos__a[1:], None) +pos__e[2]),pos__f,pos__g]
                        continue
            if pos__a[0] == '(BEGIN_LIST_COMPR':
                if pos__b[0] == '.L' and pos__c[0] == 'BASE_LIST_COMPR' and pos__d[0] == ')END_LIST_COMPR':
                    cmds[i:i+4] = [('!LIST_COMPR', pos__c[1], pos__c[2])]
                    continue
                if pos__b[0] == 'BASE_LIST_COMPR' and pos__c[0] == ')END_LIST_COMPR':
                    cmds[i:i+3] = [('!LIST_COMPR', pos__b[1], pos__b[2])]
                    continue
            if pos__a[0] == 'RAISE_VARARGS' and pos__a[1] == 0 and pos__b[0] == 'POP_TOP':
                cmds[i:i+2] = [('RAISE_VARARGS_STMT',) + pos__a[1:]]
                continue
        if type(pos__a) is list and isblock(pos__a):
            if pos__b[0] == 'JUMP_IF2_TRUE_POP_CONTINUE' and islineblock(pos__c):
                if type(pos__c) is tuple:
                    cmds[i:i+3] = [pos__a+[('(IF',) + pos__b[2:], [pos__c,('CONTINUE',)], (')ENDIF',)]]
                    continue
                if type(pos__c) is list:
                    cmds[i:i+3] = [pos__a+[('(IF',) + pos__b[2:], pos__c+[('CONTINUE',)], (')ENDIF',)]]
                    continue
            if pos__b[0] == 'JUMP_IF2_FALSE_POP_CONTINUE' and isretblock(pos__c):
                    cmds[i:i+3] = [pos__a+[('(IF',) + pos__b[2:], pos__c, (')ENDIF',)], ('JUMP_CONTINUE', pos__b[1])]
                    continue
        if type(pos__a) is tuple and len(pos__a) >= 1:
            if pos__a[0] == '3CMP_BEG_3':
                if SCmp(cmds,i, ('3CMP_BEG_3', 'JUMP_IF_FALSE', 'POP_TOP', \
                                '>', 'COMPARE_OP', 'JUMP', (':', 1,1), \
                                'ROT_TWO', 'POP_TOP', ('::', 5))):
                    rpl(cmds, [New_3Cmp(('!3CMP',) + pos__a[1:] + (pos__e[1],) + (cmd2mem(pos__d),))])
                    continue
                if SCmp(cmds,i, ('3CMP_BEG_3', 'JUMP_IF_FALSE', \
                                'POP_TOP', '>', 'DUP_TOP', 'ROT_THREE', 'COMPARE_OP', \
                                'JUMP_IF_FALSE')) and pos__b[1] == pos__h[1]:
                    rpl(cmds, [('J_NCMP', pos__h[1]) + pos__a[1:] + (pos__g[1], cmd2mem(pos__d))])
                    continue
                if SCmp(cmds,i, ('3CMP_BEG_3', 'JUMP_IF_FALSE', 'POP_TOP', \
                                '>', 'COMPARE_OP', 'RETURN_VALUE', (':', 1,1), \
                                'ROT_TWO', 'POP_TOP', 'RETURN_VALUE')):
                    rpl(cmds, [('RETURN_VALUE',New_3Cmp(('!3CMP',) + pos__a[1:] + (pos__e[1],) + (cmd2mem(pos__d),)))])
                    continue
            if pos__a[0] == 'J_NCMP':
                if SCmp(cmds,i, ('J_NCMP', \
                                'POP_TOP', '>', 'DUP_TOP', 'ROT_THREE', 'COMPARE_OP', \
                                'JUMP_IF_FALSE')) and pos__a[1] == pos__g[1]:
                    rpl(cmds, [pos__a + (pos__f[1], cmd2mem(pos__c))])
                    continue
                if SCmp(cmds,i, ('J_NCMP', \
                                'POP_TOP', '.L', '>', 'DUP_TOP', 'ROT_THREE', 'COMPARE_OP', \
                                'JUMP_IF_FALSE')) and pos__a[1] == pos__h[1]:
                    rpl(cmds, [pos__a + (pos__g[1], cmd2mem(pos__d))])
                    continue
                if SCmp(cmds,i, ('J_NCMP', 'POP_TOP', \
                                '>', 'COMPARE_OP', 'JUMP', (':', 0,1), \
                                'ROT_TWO', 'POP_TOP', ('::', 4))):       #  1
                    rpl(cmds, [New_NCmp(pos__a[2:] + (pos__d[1], cmd2mem(pos__c)))])
                    continue
                if SCmp(cmds,i, ('J_NCMP', 'POP_TOP', \
                                '.L', '>', 'COMPARE_OP', 'JUMP', (':', 0,1), \
                                'ROT_TWO', 'POP_TOP', ('::', 5))):       #  1
                    rpl(cmds, [New_NCmp(pos__a[2:] + (pos__e[1], cmd2mem(pos__d)))])
                    continue
                if SCmp(cmds,i, ('J_NCMP', 'POP_TOP', \
                                '>', 'COMPARE_OP', 'RETURN_VALUE', (':', 0,1), \
                                'ROT_TWO', 'POP_TOP', 'RETURN_VALUE')):
                    rpl(cmds, [('RETURN_VALUE', New_NCmp(pos__a[2:] + (pos__d[1], cmd2mem(pos__c))))])
                    continue
                if SCmp(cmds,i, ('J_NCMP', 'POP_TOP', \
                                '.L', '>', 'COMPARE_OP', 'RETURN_VALUE', (':', 0,1), \
                                'ROT_TWO', 'POP_TOP', 'RETURN_VALUE')):
                    rpl(cmds, [('RETURN_VALUE', New_NCmp(pos__a[2:] + (pos__e[1], cmd2mem(pos__d))))])
                    continue
            if SCmp(cmds,i, ('LOAD_CODEFUNC', 'MAKE_FUNCTION', '!GET_ITER', 'CALL_FUNCTION_1')) and\
            pos__b[1] == 0 and pos__d[1] == 1: 
                cmds[i:i+4] = [('!GENERATOR_EXPR_NOCLOSURE',) + pos__a[1:] + (pos__c[1],)]
                continue
            if pos__a[0] == '!MK_CLOSURE':
                if pos__b[0] == 'GET_ITER' and\
                pos__c[0] == 'CALL_FUNCTION_1' and pos__c[1] == 1:
                    cmds[i:i+3] = [('!GENERATOR_EXPR',) + pos__a[1:] + (pos__b[1],)]
                    continue   
                if pos__b[0] == '.L':
                    cmds[i:i+2] = [pos__a]
                    continue  
            if pos__a[0] == 'MAKE_CLOSURE' and pos__b[0] == '.L':
                cmds[i:i+2] = [pos__a]
                continue   
    
            if pos__a[0] == 'LOAD_CONST':
                changed_load_const = process_load_const(cmds,i, added_pass)
                if changed_load_const:
                    continue
            if pos__a[0] == 'J_SETUP_FINALLY':
                changed_j_setup_fin = process_j_setup_finally(cmds,i, added_pass)
                if changed_j_setup_fin:
                    process_after_try_detect(cmds,i)
                    continue
            if pos__a[0] == 'J_BEGIN_WITH':
                changed_j_with = process_j_begin_with(cmds,i, added_pass)
                if changed_j_with:
                    continue
            if pos__a[0] == 'J_SETUP_LOOP':
                changed_loop = process_j_setup_loop(cmds,i, added_pass)
                if changed_loop:
                    continue
            if pos__a[0] == 'J_SETUP_LOOP_FOR':
                changed_loopfor = process_j_setup_loop_for(cmds,i)
                if changed_loopfor:
                    continue
            if pos__a[0] == '(BEGIN_TRY':
                changed_exc = process_begin_try(cmds,i)
                if changed_exc:
                    process_after_try_detect(cmds,i)
                    continue
            if pos__a[0] == 'J_SETUP_EXCEPT':
                changed_exc = process_setup_except(cmds,i)
                if changed_exc:
                    process_after_try_detect(cmds,i)
                    continue
            if pos__a[0] in ('JUMP_IF_NOT_EXCEPTION_POP', 'POP_TOP3'):
                changed_exc = process_except_clause(cmds,i)
                if changed_exc:
                    continue
            if is_cmdmem(pos__a):
                if is_cmdmem(pos__b):
                    changed_push = process_push2(cmds,i, added_pass)
                    if changed_push:
                        continue
                else:
                    changed_push = process_push(cmds,i, added_pass)
                    if changed_push:
                        continue
            if pos__a[0] == 'SEQ_ASSIGN_0':   
                if SCmp(cmds,i, ('SEQ_ASSIGN_0', '=')) and pos__a[1] > 0:          
                    rpl(cmds,[('SEQ_ASSIGN_0', pos__a[1]-1, pos__a[2] + (pos__b,), pos__a[3])])
                    continue    
                if SCmp(cmds,i, ('SEQ_ASSIGN_0', 'DUP_TOP')):          
                    rpl(cmds,[('SEQ_ASSIGN_0', pos__a[1]+1, pos__a[2], pos__a[3])])
                    continue    
                if pos__a[1] == 0:      
                    assert len(pos__a) == 4 
                    cmds[i] = ('SEQ_ASSIGN', pos__a[2], pos__a[3])
                    continue    
            if SCmp(cmds,i, ('LOAD_FAST', '>', 'ROT_TWO')):
                rpl(cmds,[pos__b[:], pos__a[:]])
                continue
            if SCmp(cmds,i, ('LOAD_NAME', '>', 'ROT_TWO')):
                rpl(cmds,[pos__b[:], pos__a[:]])
                continue
            if SCmp(cmds,i, ((':', 3,0), 'J_LOOP_VARS', '*n', 'xJUMP_IF2_FALSE_POP_CONTINUE', '*')):
                rpl(cmds,[pos__a,pos__b,pos__c+[('(IF', Not(pos__d[2])), [('CONTINUE',)], (')ENDIF',)]+pos__e])
                continue
            if SCmp(cmds,i, ((':', 3,0), 'J_LOOP_VARS', '*n', 'xJUMP_IF2_FALSE_POP_CONTINUE', '*l')):
                if type(pos__e) is tuple:
                    rpl(cmds,[pos__a,pos__b,pos__c+[('(IF', Not(pos__d[2])), [('CONTINUE',)], (')ENDIF',)],pos__e])
                else:
                    rpl(cmds,[pos__a,pos__b,pos__c+[('(IF', Not(pos__d[2])), [('CONTINUE',)], (')ENDIF',)]+pos__e])
                continue
            if SCmp(cmds,i, ((':', 3,0), 'J_LOOP_VARS', '*n', 'xJUMP_IF2_FALSE_POP_CONTINUE')):
                rpl(cmds,[pos__a,pos__b,pos__c+[('(IF', Not(pos__d[2])), [('CONTINUE',)], (')ENDIF',)]])
                continue
            if added_pass:   
                if pos__a[0] == 'JUMP' and type(pos__b) is tuple and \
                    pos__b[0] not in ('.:', 'POP_BLOCK', 'END_FINALLY', None, '^^'):
                    del cmds[i+1]
                    continue
                if pos__a[0] == 'RETURN_VALUE' and type(pos__b) is tuple and \
                    pos__b[0] not in ('.:', 'POP_BLOCK', 'END_FINALLY', None, '^^'):
                    del cmds[i+1]
                    continue
            if SCmp(cmds,i, ('(BEGIN_DEF', '*r')) and len(cmds) > 2:
                del cmds[2:]
                continue
            if SCmp(cmds,i, ('J_COND_PUSH', 'J_COND_PUSH')) and pos__a[1] == pos__b[1]:
                rpl(cmds,[pos__a[:] + pos__b[2:]])
                continue
            if SCmp(cmds,i, ('J_COND_PUSH', '>', ('::', 0))):
                rpl(cmds,[('!COND_EXPR',) + pos__a[2:] + (cmd2mem(pos__b),)])
                continue
        i = i + 1   
    if len(cmds) > 2:   
        print filename + ':', "Can't decompile", cmds[0][1], co.co_firstlineno
        all_co[N2C(cmds[0][1])].decompile_fail = True
    else:
        all_co[N2C(cmds[0][1])].decompile_fail = False
    return cmds

def process_list_compr_2(cmds,i,added_pass):
    if SCmp(cmds, i, (('!BUILD_LIST', ()), '!GET_ITER', (':', 5, 1),\
                        'J_LOOP_VARS', '!GET_ITER', 'J_BASE_LIST_COMPR', \
                         ('::', 3))):
        if pos__f[3][2] == ():                     
            rpl(cmds, [('!LIST_COMPR', pos__f[2], (pos__d[2], (pos__b[1],), None, pos__f[3][0], (pos__e[1],), None))])
            return True   
        else:
            rpl(cmds, [('!LIST_COMPR', pos__f[2], (pos__d[2], (pos__b[1],), None, pos__f[3][0], (pos__e[1],), pos__f[3][2]))])
            return True   
        
    if SCmp(cmds, i, (('!BUILD_LIST', ()), \
                     '!GET_ITER', (':', 6, 1), 'J_LOOP_VARS', \
                     '!GET_ITER', (':', 8, 1), 'J_LOOP_VARS', \
                     '!GET_ITER', 'J_BASE_LIST_COMPR', ('::', 3))):
        if pos__i[3][2] == ():                     
            rpl(cmds, [('!LIST_COMPR', pos__i[2], (pos__d[2], (pos__b[1],), None,  pos__g[2], (pos__e[1],), None, pos__i[3][0], (pos__h[1],), None))])
            return True   
        else:
            rpl(cmds, [('!LIST_COMPR', pos__i[2], (pos__d[2], (pos__b[1],), None,  pos__g[2], (pos__e[1],), None, pos__i[3][0], (pos__h[1],), pos__i[3][2]))])
            return True   

        

    if SCmp(cmds, i, (('!BUILD_LIST', ()), '!GET_ITER', (':', (4,6)),\
                        'J_LOOP_VARS', 'JUMP_IF2_TRUE_POP','!GET_ITER', \
                        'J_BASE_LIST_COMPR', ('::', 3))):
        if pos__g[3][2] == ():                     
            rpl(cmds, [('!LIST_COMPR', pos__g[2], (pos__d[2], (pos__b[1],), (Not(pos__e[2]),), pos__g[3][0], (pos__f[1],), None))])
            return True   
        else:
            rpl(cmds, [('!LIST_COMPR', pos__g[2], (pos__d[2], (pos__b[1],), (Not(pos__e[2]),), pos__g[3][0], (pos__f[1],), pos__g[3][2]))])
            return True                                
                                                                                   
    if SCmp(cmds, i, (('!BUILD_LIST', ()), '!GET_ITER', (':', (4,6)),\
                        'J_LOOP_VARS', 'JUMP_IF2_FALSE_POP','!GET_ITER', \
                        'J_BASE_LIST_COMPR', ('::', 3))):
        if pos__g[3][2] == ():                     
            rpl(cmds, [('!LIST_COMPR', pos__g[2], (pos__d[2], (pos__b[1],), (pos__e[2],), pos__g[3][0], (pos__f[1],), None))])
            return True   
        else:
            rpl(cmds, [('!LIST_COMPR', pos__g[2], (pos__d[2], (pos__b[1],), (pos__e[2],), pos__g[3][0], (pos__f[1],), pos__g[3][2]))])
            return True                                
                                                                                   
    if SCmp(cmds,i, (('!BUILD_LIST', ()), '!GET_ITER', 'J_BASE_LIST_COMPR', ('::', 2))):
        if pos__c[3][1] is None:
            if pos__c[3][2] == ():
                rpl(cmds, [('!LIST_COMPR', pos__c[2], (pos__c[3][0], (pos__b[1],), None))])
                return True   
            else:
                rpl(cmds, [('!LIST_COMPR', pos__c[2], (pos__c[3][0], (pos__b[1],), pos__c[3][2]))])
                return True   

    if SCmp(cmds,i, (('!BUILD_LIST', ()), '!GET_ITER', (':', 6,1), \
                    'J_LOOP_VARS', '>', ('LIST_APPEND', 2), 'JUMP', \
                    ('::', 3))):
        rpl(cmds, [('!LIST_COMPR', (cmd2mem(pos__e),), (pos__d[2], (pos__b[1],), None))]                )
        return True     
    if SCmp(cmds,i, (('!BUILD_LIST', ()), '!GET_ITER', (':', 6,1), \
                    'J_LOOP_VARS', '>', ('LIST_APPEND', 2), 'JUMP_CONTINUE', \
                    ('::', 3))):
        rpl(cmds, [('!LIST_COMPR', (cmd2mem(pos__e),), (pos__d[2], (pos__b[1],), None))]                )
        return True     
    if SCmp(cmds,i, (('!BUILD_LIST', ()), '!GET_ITER', (':', (4, 7)),\
            'J_LOOP_VARS', 'JUMP_IF2_FALSE_POP', \
            '>', ('LIST_APPEND', 2), 'JUMP',\
            ('::', 3))):
        rpl(cmds, [('!LIST_COMPR', (cmd2mem(pos__f),), (pos__d[2], (pos__b[1],), (pos__e[2],)))]                )
        return True     
    if SCmp(cmds,i, (('!BUILD_LIST', ()), '!GET_ITER', (':', (4, 7)),\
            'J_LOOP_VARS', 'JUMP_IF2_FALSE_POP', \
            '>', ('LIST_APPEND', 2), 'JUMP_CONTINUE',\
            ('::', 3))):
        rpl(cmds, [('!LIST_COMPR', (cmd2mem(pos__f),), (pos__d[2], (pos__b[1],), (pos__e[2],)))]                )
        return True     
    if SCmp(cmds,i, (('!BUILD_LIST', ()), '!GET_ITER', (':', (4, 7)),\
            'J_LOOP_VARS', 'JUMP_IF2_FALSE_POP_CONTINUE', \
            '>', ('LIST_APPEND', 2), 'JUMP_CONTINUE',\
            ('::', 3))):
        rpl(cmds, [('!LIST_COMPR', (cmd2mem(pos__f),), (pos__d[2], (pos__b[1],), (pos__e[2],)))]                )
        return True     
    if SCmp(cmds,i, (('!BUILD_LIST', ()), '!GET_ITER', (':', (4, 7)),\
            'J_LOOP_VARS', 'JUMP_IF2_TRUE_POP', \
            '>', ('LIST_APPEND', 2), 'JUMP',\
            ('::', 3))):
        rpl(cmds, [('!LIST_COMPR', (cmd2mem(pos__f),), (pos__d[2], (pos__b[1],), (Not(pos__e[2]),)))]                )
        return True     
    if SCmp(cmds,i, (('!BUILD_LIST', ()), '!GET_ITER', (':', (4, 7)),\
            'J_LOOP_VARS', 'JUMP_IF2_TRUE_POP', \
            '>', ('LIST_APPEND', 2), 'JUMP_CONTINUE',\
            ('::', 3))):
        rpl(cmds, [('!LIST_COMPR', (cmd2mem(pos__f),), (pos__d[2], (pos__b[1],), (Not(pos__e[2]),)))]                )
        return True     
    if SCmp(cmds,i, (('!BUILD_LIST', ()), '!GET_ITER', (':', (4, 7)),\
            'J_LOOP_VARS', 'JUMP_IF2_TRUE_POP_CONTINUE', \
            '>', ('LIST_APPEND', 2), 'JUMP_CONTINUE',\
            ('::', 3))):
        rpl(cmds, [('!LIST_COMPR', (cmd2mem(pos__f),), (pos__d[2], (pos__b[1],), (Not(pos__e[2]),)))]                )
        return True     
    return False

def process_push(cmds,i,added_pass):
    aa = cmd2mem(pos__a)

    if SCmp(cmds,i, ('LOAD_FAST', (':', 4, 1), 'J_LOOP_VARS', '*', 'JUMP', (':', 2, 1))):
        rpl(cmds,[[('(FOR_DIRECT_ITER', aa, pos__c[2]), pos__d, (')FOR_DIRECT_ITER',)]])
        return True       

    if SCmp(cmds,i, ('LOAD_FAST', (':', 5, 1), 'J_LOOP_VARS', '!GET_ITER', (':', 7, 1), \
                     'J_LOOP_VARS', '*', 'JUMP', (':', 2, 1))):
        rpl(cmds,[[('(FOR_DIRECT_ITER2', aa, pos__c[2], pos__d[1]), pos__g, (')FOR_DIRECT_ITER2',)]])
        return True       


    if SCmp(cmds,i, ('>', 'J_SETUP_WITH', 'POP_TOP')):    
        rpl(cmds,[('J_BEGIN_WITH', pos__b[1], aa, ())])
        return True       
    if SCmp(cmds,i, ('>', 'J_SETUP_WITH', '=')):    
        rpl(cmds,[('J_BEGIN_WITH', pos__b[1], aa, (pos__c,))])
        return True       
    
    
    if SCmp(cmds,i, ('>', 'JUMP_IF_TRUE_OR_POP', '>', (':', 1, 1))):
        rpl(cmds,[Or_j_s(pos__a, pos__c)])
        return True       
    if SCmp(cmds,i, ('>', 'JUMP_IF_FALSE_OR_POP', '>', (':', 1, 1))):
        rpl(cmds,[And_j_s(pos__a, pos__c)])
        return True       

    if pos__a[0] == '!BUILD_LIST' and len(pos__a[1]) == 0 and pos__b[0] == 'DUP_TOP' and\
        pos__c[0] == 'STORE_FAST' and pos__c[1][0:2] == '_[': # and pos__d[0] == 'GET_ITER':
        cmds[i:i+3] = [('(BEGIN_LIST_COMPR', ('FAST', pos__c[1]))] #, pos__d[1])]
        return True
    if pos__a[0] == '!BUILD_LIST' and len(pos__a[1]) == 0 and pos__b[0] == 'DUP_TOP' and\
        pos__c[0] == 'STORE_NAME' and pos__c[1][0:2] == '_[':# and pos__d[0] == 'GET_ITER':
        cmds[i:i+3] = [('(BEGIN_LIST_COMPR', ('!NAME', pos__c[1]))] #, pos__d[1])]
        return True
    if pos__a[0] == '!BUILD_TUPLE' and pos__b[0] == 'POP_TOP':
        cmds[i:i+2] = [('UNPUSH', aa)]
        return True
    if pos__b is not None and pos__b[0] == 'DUP_TOP':

        if SCmp(cmds,i, ('>', 'DUP_TOP', ('LOAD_ATTR_1', '__exit__'), \
                        'ROT_TWO', ('LOAD_ATTR_1', '__enter__'), ('CALL_FUNCTION_1', 0),\
                        'POP_TOP', 'J_SETUP_FINALLY')):
                cmds[i:i+8] = [('J_BEGIN_WITH', pos__h[1], aa,())] 
                return True
        if SCmp(cmds,i, ('>', 'DUP_TOP', ('LOAD_ATTR_1', '__exit__'), 'STORE_FAST',\
                        ('LOAD_ATTR_1', '__enter__'), ('CALL_FUNCTION_1', 0), 'POP_TOP', 'J_SETUP_FINALLY')):
                cmds[i:i+8] = [('J_BEGIN_WITH', pos__h[1], aa,())] 
                return True
        if SCmp(cmds,i, ('>', 'DUP_TOP', ('LOAD_ATTR_1', '__exit__'), \
                        'ROT_TWO', ('LOAD_ATTR_1', '__enter__'), \
                        ('CALL_FUNCTION_1', 0), 'STORE_FAST', \
                        'J_SETUP_FINALLY', 'LOAD_FAST', \
                        'DELETE_FAST', '=')) and pos__g[1] == pos__i[1] and pos__g[1] == pos__j[1]:
                cmds[i:i+11] = [('J_BEGIN_WITH', pos__h[1], aa, (pos__k))] 
                return True
        if SCmp(cmds,i, ('>', 'DUP_TOP', ('LOAD_ATTR_1', '__exit__'), \
                        'ROT_TWO', ('LOAD_ATTR_1', '__enter__'), ('CALL_FUNCTION_1', 0),\
                            'STORE_FAST', 'J_SETUP_FINALLY', 'LOAD_FAST', \
                        ')END_LIST_COMPR', '=')) and pos__g[1] == pos__i[1] and pos__g[1] == pos__j[1][1]:
                cmds[i:i+11] = [('J_BEGIN_WITH', pos__h[1], aa, (pos__k))] 
                return True
            
        if (pos__a[0] == '!LOAD_DEREF' or pos__a[0] == '!LOAD_NAME' or pos__a[0] == '!LOAD_GLOBAL' or \
            pos__a[0] == '!PyDict_GetItem(glob,' or\
             pos__a[0] == 'LOAD_FAST' or pos__a[0] == '!PyObject_GetAttr'):
            cmds[i:i+2] = [pos__a[:], pos__a[:]]
            return True
                    
        if SCmp(cmds,i, ('>', 'DUP_TOP', '=', '=')):
                cmds[i:i+4] = [('SET_EXPRS_TO_VARS', (pos__d,pos__c), ('CLONE', aa))]
                return True
        if SCmp(cmds,i, ('>', 'DUP_TOP', 'UNPACK_SEQ_AND_STORE', '=')) and pos__c[1] == 0:
                cmds[i:i+4] = [('SET_EXPRS_TO_VARS', (pos__d,pos__c), ('CLONE', aa))]
                return True           
        if SCmp(cmds,i, ('>', 'DUP_TOP', '>', 'ROT_TWO', \
                        'PRINT_ITEM_TO_0', 'PRINT_NEWLINE_TO_0')):        
            cmds[i:i+6] = [('PRINT_ITEM_AND_NEWLINE_TO_2', aa, cmd2mem(pos__c))]
            return True
        if SCmp(cmds,i, ('>', 'DUP_TOP', '>', 'ROT_TWO', \
                        'PRINT_ITEM_TO_0', 
                        'DUP_TOP', '>', 'ROT_TWO', 'PRINT_ITEM_TO_0',
                        'PRINT_NEWLINE_TO_0')):        
            cmds[i:i+10] = [('PRINT_ITEM_AND_NEWLINE_TO_3', aa, cmd2mem(pos__c), cmd2mem(pos__g))]
            return True
        if SCmp(cmds,i, ('>', 'DUP_TOP', '>', 'ROT_TWO',  'PRINT_ITEM_TO_0', 'POP_TOP')):        
            rpl(cmds,[('PRINT_ITEM_TO_2', aa, cmd2mem(pos__c))])
            return True        
        if SCmp(cmds,i, ('>', 'DUP_TOP', 'LOAD_ATTR_1', '>', 'INPLACE_ADD',\
                        'ROT_TWO', 'STORE_ATTR_1')) and pos__g[1] == pos__c[1]:
            rpl(cmds,[('STORE', (('PyObject_SetAttr', aa, ('CONST', pos__h[1])),), \
                    (('!' + recode_inplace['INPLACE_ADD'], aa, cmd2mem(pos__d)),))])
            return True   
        if SCmp(cmds,i, ('>', 'DUP_TOP', 'LOAD_ATTR_1', '>', 'INPLACE_MULTIPLY',\
                        'ROT_TWO', 'STORE_ATTR_1')) and pos__g[1] == pos__c[1]:
            rpl(cmds,[('STORE', (('PyObject_SetAttr', aa, ('CONST', pos__h[1])),), 
                    (('!' + recode_inplace['INPLACE_MULTIPLY'], aa, cmd2mem(pos__d)),))])
            return True   
        if SCmp(cmds,i, ('>', 'DUP_TOP', 'STORE_GLOBAL', 'STORE_FAST')):
            rpl(cmds,[pos__a, pos__d, ('LOAD_FAST', pos__d[1]), pos__c])
            return True
        if SCmp(cmds,i, ('>', 'DUP_TOP', 'STORE_FAST', 'STORE_GLOBAL')):
            rpl(cmds,[pos__a, pos__c, ('LOAD_FAST', pos__c[1]), pos__d])
            return True
        if SCmp(cmds,i, ('>', 'DUP_TOP', '=')):
                rpl(cmds,[('SEQ_ASSIGN_0', 1, (pos__c,), aa)])
                return True    
        if SCmp(cmds,i, ('>', 'DUP_TOP', 'STORE_FAST')): 
                rpl(cmds,[pos__a, pos__c, ('LOAD_FAST', pos__c[1])])
                return True

    ## if SCmp(cmds,i, ('>', 'DUP_TOP', ('LOAD_ATTR_1', '__exit__'),\ # By CloneDigger
                    ## 'ROT_TWO', ('LOAD_ATTR_1', '__enter__'), \
                    ## ('CALL_FUNCTION_1', 0), 'STORE_FAST', \
                    ## 'J_SETUP_FINALLY', 'LOAD_FAST', \
                    ## 'DELETE_FAST', '=')) and pos__g[1] == pos__i[1] and pos__g[1] == pos__j[1]:
            ## cmds[i:i+11] = [('J_BEGIN_WITH', pos__h[1], aa, (pos__k))] 
            ## return True
    if SCmp(cmds,i, ('!PyObject_GetAttr', 'STORE', 'J_SETUP_FINALLY', \
                    'LOAD_FAST', ')END_LIST_COMPR', '=')) and\
                    pos__a[2][1] == '__exit__' and \
                    pos__b[1][0][1][:2] == '_[' and \
                    pos__d[1] == pos__b[1][0][1]:
            cmds[i:i+6] = [('J_BEGIN_WITH', pos__c[1], pos__a[1], (pos__f,))] 
            return True
    if SCmp(cmds,i, ('!PyObject_GetAttr', 'STORE', 'J_SETUP_FINALLY', '!LOAD_NAME', \
                    ')END_LIST_COMPR', '=')) and pos__a[2][1] == '__exit__' and pos__d[1] == pos__e[1][1]:
            rpl(cmds,[('J_BEGIN_WITH', pos__c[1], pos__a[1], (pos__f))])
            return True

    if isblock(pos__b) and len(pos__b) == 1 and type(pos__b[0]) is tuple:
        cmds[i+1:i+2] = pos__b
        return True

    if  is_cmdmem(pos__c) and pos__b[0] == '.L':
        del cmds[i+1]
        return True
    if pos__c[0] == 'MK_FUNK' and pos__c[2] > 0 and pos__b[0] == '.L':
        cmds[i:i+3] = [('MK_FUNK', pos__c[1], pos__c[2]-1, (aa,)+pos__c[3])]
        return True
    if pos__b[0] == 'MK_FUNK' and pos__b[2] > 0:
        cmds[i:i+2] = [('MK_FUNK', pos__b[1], pos__b[2]-1, (aa,)+pos__b[3])]
        return True
    if pos__b[0] == 'LOAD_CODEFUNC' and pos__c[0] == 'MAKE_CLOSURE':
        cmds[i:i+3] = [('MK_CLOSURE', pos__b[1], pos__c[1], aa, ())]
        return True
    if pos__b[0] == 'MK_CLOSURE' and pos__b[2] > 0:
        cmds[i:i+2] = [('MK_CLOSURE', pos__b[1], pos__b[2]-1, pos__b[3], (aa,)+pos__b[4])]
        return True       

    if SCmp(cmds,i, ('>', 'JUMP', '>', (':', 1, 1))):
        cmds[i:i+4] = [pos__a[:]]
        return True
    if SCmp(cmds,i, ('>', 'JUMP', '>', (':', 1, 2))):
        cmds[i:i+4] = [pos__a[:], pos__d[:]]
        return True

    if pos__b[0] == 'PRINT_ITEM_TO_2' and \
        pos__c[0] == 'DUP_TOP':
        cmds[i:i+3] = [pos__b[:], pos__a, pos__c]
        return True
    if pos__b[0] == 'PRINT_ITEM_TO_2' and \
        pos__c[0] == 'PRINT_NEWLINE_TO_0':
        cmds[i:i+3] = [pos__b[:], ('PRINT_NEWLINE_TO_1', aa)]
        return True
    if pos__b[0] == 'PRINT_NEWLINE_TO_0':
        cmds[i:i+2] = [('PRINT_NEWLINE_TO_1', aa)]
        return True

    if  is_cmdmem(pos__c) and pos__b[0] == '.L':
            cmds[i:i+3] = pos__b, pos__a, pos__c
            return True
    if pos__b[0] == 'STORE_ATTR_1':
        cmds[i:i+2] = [('PyObject_SetAttr', aa, ('CONST', pos__b[1]))]
        return True
    if  pos__b[0] in set_any:
        cmds[i:i+2] = [('STORE',(pos__b,), (aa,))]
        return True
    if pos__b[0] == 'PRINT_ITEM_0':
        cmds[i:i+2] = [('PRINT_ITEM_1',) + (aa,)]
        return True
    if ( pos__b[0] in ('JUMP_IF_FALSE_POP_BREAK','JUMP_IF_FALSE_POP_CONTINUE',\
                    'JUMP_IF_TRUE_POP_BREAK','JUMP_IF_TRUE_POP_CONTINUE',\
                    'JUMP_IF_FALSE_POP', 'JUMP_IF_TRUE_POP') and len(pos__b) == 2 ):
        bb = 'JUMP_IF2_' + pos__b[0][8:]     
        cmds[i:i+2] = [(bb, pos__b[1], aa)]
        return True
    if pos__b[0] == 'RETURN_VALUE' and len(pos__b) == 1:
        cmds[i:i+2] = [pos__b + (aa,)]
        return True
    if pos__b[0] == 'IMPORT_STAR' and len(pos__b) == 1 and pos__a[0] == '!IMPORT_NAME':
        cmds[i:i+2] = make_import_star(aa)
        return True
    if pos__b[0] == 'IMPORT_STAR' and len(pos__b) == 1:
        cmds[i:i+2] = [pos__b + (aa,)]
        return True
    if pos__b[0] == 'GET_ITER'  and len( pos__b) == 1 :
        cmds[i:i+2] = [('!GET_ITER',) + (aa,)]
        return True
    if pos__b[0] == 'BUILD_LIST' and pos__b[1] > 0:
        if len(pos__b) == 2:
            b_ = (pos__b[0], pos__b[1], ())
        else:
            b_ = pos__b    
        cmds[i:i+2] = [('BUILD_LIST', b_[1] - 1, (aa,) + b_[2])]
        return True
    if pos__b[0] == 'BUILD_TUPLE' and pos__b[1] > 0:
        if len(pos__b) == 2:
            b_ = (pos__b[0], pos__b[1], ())
        else:
            b_ = pos__b    
        cmds[i:i+2] = [('BUILD_TUPLE', b_[1] - 1, (aa,) + b_[2])]
        return True
    if pos__b[0] == 'BUILD_SET' and pos__b[1] > 0:
        if len(pos__b) == 2:
            b_ = (pos__b[0], pos__b[1], ())
        else:
            b_ = pos__b    
        cmds[i:i+2] = [('BUILD_SET', b_[1] - 1, (aa,) + b_[2])]
        return True
    if pos__b[0] == 'LOAD_ATTR_1':
        cmds[i:i+2] = [('!PyObject_GetAttr', aa, ('CONST', pos__b[1]))]
        return True
    if pos__b[0] == 'SLICE+0' and len(pos__b) == 1:
        cmds[i:i+2] = [('!PySequence_GetSlice', aa, 0, 'PY_SSIZE_T_MAX')]        
        return True
    if pos__b[0] == 'YIELD_VALUE' and len(pos__b) == 1 and pos__c[0] == 'POP_TOP':
        cmds[i:i+3] = [('YIELD_STMT', aa)]
        return True
    if pos__b[0] == 'YIELD_VALUE' and len(pos__b) == 1:
        cmds[i:i+2] = [('!YIELD_VALUE', aa)]
        return True
    if pos__b[0] == 'RAISE_VARARGS':
        if len(pos__b) == 2 and pos__b[1] == 1 and pos__c[0] == 'POP_TOP':
            cmds[i:i+3] = [('RAISE_VARARGS_STMT', 0, (aa,))]
            return True
        if len(pos__b) == 3 and pos__b[1] == 1 and pos__c[0] == 'POP_TOP':
            cmds[i:i+3] = [('RAISE_VARARGS_STMT', 0, (aa,)+ pos__b[2])]
            return True
        if len(pos__b) == 2 and pos__b[1] == 1:
            cmds[i:i+2] = [('RAISE_VARARGS', 0, (aa,))]
            return True
        if len(pos__b) == 2 and pos__b[1] >= 1:
            cmds[i:i+2] = [('RAISE_VARARGS', pos__b[1]-1, (aa,))]
            return True
        if len(pos__b) == 3 and pos__b[1] >= 1:
            cmds[i:i+2] = [('RAISE_VARARGS', pos__b[1]-1, (aa,) + pos__b[2])]
            return True
    if pos__b[0] in recode_unary:
        cmds[i:i+2] = [('!' +recode_unary[pos__b[0]], aa)]
        return True    
    if pos__b[0] == 'UNARY_NOT':
        cmds[i:i+2] = [Not(aa)]
        return True
    if pos__b[0][:6] == 'UNARY_':
        cmds[i:i+2] = [('!1' + pos__b[0][6:], aa)]
        return True
    if pos__b[0] == 'DELETE_SLICE+0' and len(pos__b) == 1:
                cmds[i:i+2] = [('DELETE_SLICE+0', aa)]
                return True
    if SCmp(cmds,i, ('>', 'CALL_FUNCTION_1')) and pos__b[1] > 0:
        cmds[i:i+2] =  [(pos__b[0], pos__b[1]-1, (aa,) + pos__b[2], pos__b[3], pos__b[4])]
        return True       
    if SCmp(cmds,i, ('>', 'CALL_FUNCTION_1')) and pos__b[1] == 0 and pos__b[3] == 0:
        if len(pos__b[4]) == 0:
# must be after type dectection             
            if pos__a[0] =='!LOAD_BUILTIN':
                cm = attempt_direct_builtin(pos__a[1],pos__b[2], TupleFromArgs(pos__b[2]))
                if cm is not None:
                    cmds[i:i+2] = [cm]
                    return True
            if len(pos__b[2]) == 0:
                cmds[i:i+2] =  [('!PyObject_Call', aa, ('CONST',()), ('NULL',))]
                return True
            cmds[i:i+2] =  [('!PyObject_Call', aa, TupleFromArgs(pos__b[2]), ('NULL',))]
            return True
        else:
            if len(pos__b[2]) == 0:
                cmds[i:i+2] =  [('!PyObject_Call', aa, ('CONST',()), DictFromArgs(pos__b[4]))]
                return True
            cmds[i:i+2] =  [('!PyObject_Call', aa, TupleFromArgs(pos__b[2]), DictFromArgs(pos__b[4]))]        
        return True       
    if SCmp(cmds,i, ('>', 'CALL_FUNCTION_KW')):
        cmds[i:i+2] =  [('CALL_FUNCTION_KW_1',) + pos__b[1:] + (aa,)]
        return True       
    if SCmp(cmds,i, ('>', 'CALL_FUNCTION_KW_1')) and pos__b[1] > 0:
        cmds[i:i+2] =  [(pos__b[0], pos__b[1]-1, (aa,) + pos__b[2], pos__b[3], pos__b[4], pos__b[5])]
        return True       
    if SCmp(cmds,i, ('>', 'CALL_FUNCTION_KW_1')) and pos__b[1] == 0 and pos__b[3] == 0:
        if len(pos__b[4]) == 0:
            cmds[i:i+2] =  [('!PyObject_Call', aa, TupleFromArgs(pos__b[2]), pos__b[5])]
            return True        
        else:
            cmds[i:i+2] =  [('!PyObject_Call', aa, TupleFromArgs(pos__b[2]), ('!$PyDict_SymmetricUpdate', DictFromArgs(pos__b[4]), pos__b[5]))]
            return True        
    if SCmp(cmds,i, ('>', 'CALL_FUNCTION_VAR')):
        cmds[i:i+2] =  [('CALL_FUNCTION_VAR_1',) + pos__b[1:] + (aa,)]
        return True       
    if SCmp(cmds,i, ('>', 'CALL_FUNCTION_VAR_1')) and pos__b[1] > 0:
        cmds[i:i+2] =  [(pos__b[0], pos__b[1]-1, (aa,) + pos__b[2], pos__b[3], pos__b[4], pos__b[5])]
        return True       
    if SCmp(cmds,i, ('>', 'CALL_FUNCTION_VAR_1')) and pos__b[1] == 0 and pos__b[3] == 0:
        if len(pos__b[4]) == 0:
            t = TypeExpr(pos__b[5])
            if len(pos__b[2]) == 0:
                if t == Kl_Tuple:
                    cmds[i:i+2] =  [('!PyObject_Call', aa, pos__b[5], ('NULL',))]
                elif t == Kl_List:
                    cmds[i:i+2] =  [('!PyObject_Call', aa, ('!PyList_AsTuple', pos__b[5]), ('NULL',))]
                else:
                    cmds[i:i+2] =  [('!PyObject_Call', aa, ('!PySequence_Tuple', pos__b[5]), ('NULL',))]
                return True
            if t == Kl_Tuple:
                cmds[i:i+2] =  [('!PyObject_Call', aa, ('!PyNumber_Add', TupleFromArgs(pos__b[2]), pos__b[5]), ('NULL',))]
            elif t == Kl_List:
                cmds[i:i+2] =  [('!PyObject_Call', aa, ('!PyNumber_Add', TupleFromArgs(pos__b[2]), ('!PyList_AsTuple', pos__b[5])), ('NULL',))]
            else:
                cmds[i:i+2] =  [('!PyObject_Call', aa, ('!PyNumber_Add', TupleFromArgs(pos__b[2]), ('!PySequence_Tuple', pos__b[5])), ('NULL',))]
            return True        
        else:
            t = TypeExpr(pos__b[5])
            if len(pos__b[2]) == 0:
                if t == Kl_Tuple:
                    cmds[i:i+2] =  [('!PyObject_Call', aa, pos__b[5], DictFromArgs(pos__b[4]))]
                elif t == Kl_List:
                    cmds[i:i+2] =  [('!PyObject_Call', aa, ('!PyList_AsTuple', pos__b[5]), DictFromArgs(pos__b[4]))]
                else:
                    cmds[i:i+2] =  [('!PyObject_Call', aa, ('!PySequence_Tuple', pos__b[5]), DictFromArgs(pos__b[4]))]
                return True

            if t == Kl_Tuple:
                cmds[i:i+2] =  [('!PyObject_Call', aa, ('!PyNumber_Add', TupleFromArgs(pos__b[2]), pos__b[5]), DictFromArgs(pos__b[4]))]
            elif t == Kl_List:
                cmds[i:i+2] =  [('!PyObject_Call', aa, ('!PyNumber_Add', TupleFromArgs(pos__b[2]), ('!PyList_AsTuple', pos__b[5])), DictFromArgs(pos__b[4]))]
            else:
                cmds[i:i+2] =  [('!PyObject_Call', aa, ('!PyNumber_Add', TupleFromArgs(pos__b[2]), ('!PySequence_Tuple', pos__b[5])), DictFromArgs(pos__b[4]))]
            return True        
    if SCmp(cmds,i, ('>', 'CALL_FUNCTION_VAR_KW_1')) and pos__b[1] > 0:
        cmds[i:i+2] =  [(pos__b[0], pos__b[1]-1, (aa,) + pos__b[2], pos__b[3], pos__b[4], pos__b[5],pos__b[6])]
        return True       
    if SCmp(cmds,i, ('>', 'CALL_FUNCTION_VAR_KW_1')) and pos__b[1] == 0 and pos__b[3] == 0:
        t = TypeExpr(pos__b[5])
        if len(pos__b[4]) == 0 and len(pos__b[2]) == 0:
            if t == Kl_Tuple:
                cmds[i:i+2] =  [('!PyObject_Call', aa, pos__b[5], pos__b[6])]
            elif t == Kl_List:
                cmds[i:i+2] =  [('!PyObject_Call', aa, ('!PyList_AsTuple', pos__b[5]), pos__b[6])]
            else:
                cmds[i:i+2] =  [('!PyObject_Call', aa, ('!PySequence_Tuple', pos__b[5]), pos__b[6])]
            return True        
        if len(pos__b[2]) > 0: 
            if t == Kl_Tuple:
                tup = ('!PyNumber_Add', TupleFromArgs(pos__b[2]), pos__b[5]) 
            elif t == Kl_List:
                tup = ('!PyNumber_Add', TupleFromArgs(pos__b[2]), ('!PyList_AsTuple',pos__b[5])) 
            else:
                tup = ('!PyNumber_Add', TupleFromArgs(pos__b[2]), ('!PySequence_Tuple',pos__b[5])) 
        else:
            tup = pos__b[5]
        if len(pos__b[4]) > 0: 
            dic = ('!$PyDict_SymmetricUpdate', DictFromArgs(pos__b[4]), pos__b[6])  
        else:
            dic = pos__b[6]            
        cmds[i:i+2] = [('!PyObject_Call', aa, tup, dic)]
        return True       
    if SCmp(cmds,i, ('>', '.L', 'CALL_FUNCTION_1')):
        rpl(cmds,[pos__a,pos__c])
        return True
    if SCmp(cmds,i, ('>', 'POP_TOP')):
        rpl(cmds,[('UNPUSH', aa)])
        return True       
    if SCmp(cmds,i, ('>', 'DELETE_ATTR_1')):
        rpl(cmds,[('DELETE_ATTR_2', aa, ('CONST', pos__b[1]))])
        return True
    if SCmp(cmds,i, ('>', 'STORE_SLICE+0')):
                rpl(cmds,[('STORE_SLICE_LV+0', aa)])
                return True
    if SCmp(cmds,i, ('>', 'BOXING_UNBOXING', 'UNPACK_SEQ_AND_STORE')) and pos__c[1] == 0:
        rpl(cmds,[pos__b,pos__a,pos__c])
        return True
    if SCmp(cmds,i, ('>', 'PRINT_ITEM_TO_2', 'POP_TOP')):        
        rpl(cmds,[('UNPUSH', aa), pos__b])
        return True
    if SCmp(cmds,i, ('>', 'SET_VARS')):
        rpl(cmds,[('SET_EXPRS_TO_VARS', pos__b[1], aa)])
        return True        
    if SCmp(cmds,i, ('>', 'SET_EXPRS_TO_VARS', '=')):
        rpl(cmds,[('SET_EXPRS_TO_VARS', pos__b[1] + (pos__c,), pos__b[2] + (aa,))])
        return True        
    if SCmp(cmds,i, ('>', 'SET_EXPRS_TO_VARS', 'SET_VARS')):
        rpl(cmds,[('SET_EXPRS_TO_VARS', (pos__b[1],) + (pos__c[1],), (pos__b[2],) + (aa,))])
        return True        

    if SCmp(cmds,i, ('>', 'STORE', '=')):
        if len(pos__b[1]) == len(pos__b[2]) == 1:
            rpl(cmds,[('SET_EXPRS_TO_VARS', pos__b[1] + (pos__c,), pos__b[2] + (aa,))])
        else:
            assert False   
            rpl(cmds,[('SET_EXPRS_TO_VARS', (pos__b[1],) + (pos__c,), (pos__b[2],) + (aa,))])
        return True       
    if SCmp(cmds,i, ('>', 'STORE', 'DUP_TOP')) and pos__b[2] == (aa,):
            rpl(cmds,[('SEQ_ASSIGN_0', 2, pos__b[1], aa)])
            return True    
    if SCmp(cmds,i, ('>', 'STORE', 'DUP_TOP')) and pos__b[2] == aa:
            rpl(cmds,[('SEQ_ASSIGN_0', 2, (pos__b[1],), aa)])
            return True    
    if SCmp(cmds,i, ('!PyDict_New', 'DUP_TOP', '>', 'ROT_TWO', '>', 'STORE_SUBSCR_0')):
        rpl(cmds, [('!BUILD_MAP', (cmd2mem(pos__e), cmd2mem(pos__c)))])
        return True
    if SCmp(cmds,i, ('!BUILD_MAP', 'DUP_TOP', '>', 'ROT_TWO', '>', 'STORE_SUBSCR_0')):
        rpl(cmds, [('!BUILD_MAP', pos__a[1] + ((cmd2mem(pos__e), cmd2mem(pos__c)),))])
        return True
    if pos__b is not None and pos__b[0] == 'JUMP_IF_FALSE':
        if pos__b[0] == 'JUMP_IF_FALSE' and pos__c[0] == 'POP_TOP' and is_cmdmem(pos__d): 
            if label(pos__b, pos__e):
                if OneJump(pos__e[1], cmds):
                    cmds[i:i+5] = [And_j_s(aa, pos__d)]
                else:    
                    cmds[i:i+5] = [And_j_s(aa, pos__d), pos__e]
                return True
            if pos__e[0] == 'JUMP_IF_FALSE' and pos__b[1] == pos__e[1] and pos__f[0] == 'POP_TOP':
                cmds[i:i+6] = [And_j_s(aa, pos__d),pos__b,pos__c]
                return True
        if pos__b[0] == 'JUMP_IF_FALSE' and pos__c[0] == 'POP_TOP' and islineblock(pos__d) and\
            is_cmdmem(pos__e): 
                del cmds[i+3]
                return True

        if SCmp(cmds,i, ('>', 'JUMP_IF_FALSE', 'POP_TOP', '3CMP_BEG_3', \
                        'JUMP_IF_FALSE', 'POP_TOP', '>', 'COMPARE_OP', \
                        'RETURN_VALUE', (':', 4,1), 'ROT_TWO', 'POP_TOP',\
                        (':', 1,1), 'RETURN_VALUE')):
            rpl(cmds, [('RETURN_VALUE', And_j_s(pos__a, \
                                                New_3Cmp(('!3CMP', pos__d[1], pos__d[2], pos__d[3], pos__h[1], cmd2mem(pos__g)))))])
            return True

        if SCmp(cmds,i, ('>', 'JUMP_IF_FALSE', 'POP_TOP',\
                        'JUMP_IF2_TRUE_POP_CONTINUE', '>', (':', 1,1),\
                        'JUMP_IF_TRUE_POP_CONTINUE')) and pos__d[1] == pos__g[1]:
                rpl(cmds,[And_j_s(pos__a, Or_j_s(pos__d[2],pos__e)),pos__g])
                return True       
        if SCmp(cmds,i, ('>', 'JUMP_IF_FALSE', 'POP_TOP',\
                        'JUMP_IF2_TRUE_POP', '>', (':', 1,1),\
                        'JUMP_IF_TRUE_POP')) and pos__d[1] == pos__g[1]:
                rpl(cmds,[And_j_s(pos__a, Or_j_s(pos__d[2],pos__e)),pos__g])
                return True       
        if SCmp(cmds,i, ('>', 'JUMP_IF_FALSE', 'POP_TOP', 'JUMP_IF2_FALSE_POP', \
                        '>', (':', 1,1), 'JUMP_IF_TRUE', 'POP_TOP', (':', 3, 1),\
                        '>', ('::', 6))): 
                temp1 = And_j_s(pos__a, pos__d[2])         
                temp2 = And_j_s(temp1, pos__e)
                rpl(cmds,[Or_j_s(temp2, pos__j)])
                return True 
        if SCmp(cmds,i, ('>', 'JUMP_IF_FALSE', 'POP_TOP', '>', 'JUMP')) and pos__b[1] == pos__e[1]:
                rpl(cmds, [And_j_s(pos__a, pos__d), pos__e])
                return True
    if pos__b is not None and pos__b[0] == 'JUMP_IF_TRUE':
        if pos__b[0] == 'JUMP_IF_TRUE' and pos__c[0] == 'POP_TOP' and is_cmdmem(pos__d): 
            if label(pos__b, pos__e):
                if OneJump(pos__e[1], cmds):
                    cmds[i:i+5] = [Or_j_s(aa, pos__d)]
                else:
                    cmds[i:i+5] = [Or_j_s(aa, pos__d), pos__e]
                return True
            if pos__e[0] == 'JUMP_IF_TRUE' and pos__b[1] == pos__e[1] and pos__f[0] == 'POP_TOP':
                cmds[i:i+6] = [Or_j_s(aa, pos__d),pos__b,pos__c]
                return True
        if SCmp(cmds,i, ('>', 'JUMP_IF_TRUE', 'POP_TOP', '3CMP_BEG_3', \
                        'JUMP_IF_FALSE', 'POP_TOP', '>', 'COMPARE_OP', \
                        'RETURN_VALUE', (':', 4,1), 'ROT_TWO', 'POP_TOP',\
                        (':', 1,1), 'RETURN_VALUE')):
            rpl(cmds, [('RETURN_VALUE', Or_j_s(pos__a, \
                                                New_3Cmp(('!3CMP', pos__d[1], pos__d[2], pos__d[3], pos__h[1], cmd2mem(pos__g)))))])
            return True
        if SCmp(cmds,i, ('>', 'JUMP_IF_TRUE', 'POP_TOP', 'JUMP_IF2_FALSE_POP', \
                        '>', 'JUMP_IF_TRUE', 'POP_TOP', (':', 3, 1), \
                        '>', (':', 1, 2))) and pos__b[1] == pos__f[1] and CntJump(pos__j[1],cmds) == 2:
                rpl(cmds,[Or_j_s(pos__a, Or_j_s(And_j_s(pos__d[2], pos__e), pos__i))])
                return True                                           
        if SCmp(cmds,i, ('>', 'JUMP_IF_TRUE', 'POP_TOP', 'JUMP_IF2_FALSE_POP', \
                        '>', (':', 1,1), 'JUMP_IF_FALSE_POP')) and pos__d[1] == pos__g[1]:
            rpl(cmds,[Or_j_s(aa, And_j_s(pos__d[2],pos__e)),pos__g])
            return True
        if SCmp(cmds,i, ('>', 'JUMP_IF_TRUE', 'POP_TOP', 'JUMP_IF2_FALSE_POP_CONTINUE', \
                    '>', (':', 1, 1), '=', 'ju')) and pos__d[1] == pos__h[1]:
# re.match_nl or (match_bol and re.nullable)
            rpl(cmds,[Or_j_s(pos__a, And_j_s(pos__d[2],pos__e)),pos__g,pos__h])
            return True       
        if SCmp(cmds,i, ('>', 'JUMP_IF_TRUE', 'POP_TOP', '>', 'JUMP')) and pos__b[1] == pos__e[1]:
                rpl(cmds, [Or_j_s(pos__a, pos__d), pos__e])
                return True
        if SCmp(cmds,i, ('>', 'JUMP_IF_TRUE', 'POP_TOP', 'JUMP_IF2_TRUE_POP', \
                        'LOAD_CONST', (':', 1, 1), 'STORE_FAST', ('::', 3))) and\
                        pos__d[2][0] == 'FAST' and pos__d[2][1] == pos__g[1]:
                rpl(cmds, [Or_j_s(Or_j_s(pos__a, pos__d[2]), pos__e),pos__g])
                return True

    return False

def process_push2(cmds,i,added_pass):
    aa = cmd2mem(pos__a)
    bb = cmd2mem(pos__b)

    if pos__c[0] == 'BUILD_SLICE' and len(pos__c) == 2 and pos__c[1] == 2:
            cmds[i:i+3] = [('!PySlice_New', aa, bb, 'NULL')]
            return True
    if pos__c[0] == 'STORE_MAP':
        cmds[i:i+3] = [('STORE_MAP', bb, aa)]
        return True
    if pos__c[0] == 'ROT_TWO' and pos__d[0] == 'STORE_ATTR_1':
        cmds[i:i+4] = [('STORE', (('PyObject_SetAttr', aa, ('CONST', pos__d[1])),), (pos__b,))]
        return True
    if SCmp(cmds,i, ('>','>', '>', 'BUILD_CLASS')):
            rpl(cmds,[('!_PyEval_BuildClass', cmd2mem(pos__c), bb, aa)])
            return True
    if SCmp(cmds,i, ('>','>', 'ROT_TWO')):
        cmds[i:i+3] = [pos__b[:], pos__a[:]]
        return True
    
    if pos__c[0] == 'DELETE_SLICE+1' and len(pos__c) == 1:
        cmds[i:i+3] = [('DELETE_SLICE+1', aa, bb)]
        return True
    if pos__c[0] == 'IMPORT_NAME' and len(pos__c) == 2:
            cmds[i:i+3] = [('!IMPORT_NAME', pos__c[1], aa, bb)]
            return True
    if pos__c[0] == 'COMPARE_OP':
        cmds[i:i+3] = process_compare_op(pos__c[1],pos__a,pos__b)
        return True
    if pos__c[0] == 'LIST_APPEND' and len(pos__c) == 1:
            cmds[i:i+3] = [('PyList_Append', aa, bb)]
            return True
    if pos__c[0] == 'SLICE+1' and len(pos__c) == 1:
            if isintconst(bb):
                cmds[i:i+3] = [('!PySequence_GetSlice', aa, bb[1], 'PY_SSIZE_T_MAX')]
            else:    
                cmds[i:i+3] = [('!_PyEval_ApplySlice', aa, bb, 'NULL')]
            return True
    if pos__c[0] == 'SLICE+2' and len(pos__c) == 1:
            if isintconst(bb):
                cmds[i:i+3] = [('!PySequence_GetSlice', aa, 0, bb[1])]
            else:    
                cmds[i:i+3] = [('!_PyEval_ApplySlice', aa, 'NULL', bb)]
            return True
    ## if pos__c[0] == 'BINARY_ADD' and bb[0] == 'CONST' and \
        ## type(bb[1]) is int and bb[1] >= 0:        
            ## cmds[i:i+3] = [('!from_ceval_BINARY_ADD_Int', aa, bb[1], bb)]
            ## return True
    if pos__c[0] == 'BINARY_MODULO' and aa[0] == 'CONST' and \
        type(aa[1]) is str and bb[0] == '!BUILD_TUPLE':        
            cmds[i:i+3] = [('!PyString_Format', aa, bb)]
            return True
    if pos__c[0] == 'BINARY_MULTIPLY' and (aa[0] == '!STR_CONCAT' or (aa[0] == 'CONST' and \
        (type(aa[1]) is str or type(aa[1]) is list or type(aa[1]) is tuple))):
            cmds[i:i+3] = [('!PySequence_Repeat', aa, bb)]
            return True
    if pos__c[0] == 'BINARY_ADD' and aa[0] == '!STR_CONCAT' and bb[0] == '!STR_CONCAT':        
            cmds[i:i+3] = [aa + bb[1:]]
            return True
    if pos__c[0] == 'BINARY_ADD' and aa[0] == '!PyNumber_Add' and bb[0] == '!STR_CONCAT':        
            cmds[i:i+3] = [(bb[0], aa[1], aa[2]) + bb[1:]]
            return True
    if pos__c[0] == 'BINARY_ADD' and bb[0] == '!PyNumber_Add' and aa[0] == '!STR_CONCAT':        
            cmds[i:i+3] = [(aa[0], aa[1], aa[2]) + bb[1:]]
            return True
    if pos__c[0] == 'BINARY_ADD' and bb[0] == '!STR_CONCAT':        
            cmds[i:i+3] = [('!STR_CONCAT', aa) + bb[1:]]
            return True
    if pos__c[0] == 'BINARY_ADD' and aa[0] == '!STR_CONCAT':        
            cmds[i:i+3] = [aa + (bb,)]
            return True
    if pos__c[0] == 'BINARY_ADD' and bb[0] == 'CONST' and \
        type(bb[1]) is str and aa[0] == '!PyNumber_Add':        
            cmds[i:i+3] = [('!STR_CONCAT', aa[1], aa[2], bb)]
            return True
    if pos__c[0] == 'BINARY_ADD' and bb[0] == 'CONST' and \
        type(bb[1]) is str:        
            cmds[i:i+3] = [('!STR_CONCAT', aa, bb)]
            return True
    if pos__c[0] == 'BINARY_ADD' and aa[0] == 'CONST' and \
        type(aa[1]) is str:        
            cmds[i:i+3] = [('!STR_CONCAT', aa, bb)]
            return True
    if pos__c[0] == 'BINARY_SUBSCR' and bb[0] == 'CONST' and \
        type(bb[1]) is int: # and bb[1] >= 0:        
            cmds[i:i+3] = [('!BINARY_SUBSCR_Int', aa, bb)]
            return True
    if pos__c[0] == 'BINARY_SUBSCR' :        
            cmds[i:i+3] = [('!from_ceval_BINARY_SUBSCR', aa, bb)]
            return True
    if pos__c[0] in recode_binary:
        if recode_binary[pos__c[0]] == 'PyNumber_Power+Py_None':
            cmds[i:i+3] = [('!PyNumber_Power', aa, bb, 'Py_None')]
        else:    
            cmds[i:i+3] = [('!' +recode_binary[pos__c[0]], aa, bb)]
        return True
    if pos__c[0] == 'INPLACE_POWER':
            cmds[i:i+3] = [('!PyNumber_InPlacePower', aa, bb, 'Py_None')]
            return True
    if pos__c[0] in recode_inplace:
            cmds[i:i+3] = [('!' +recode_inplace[pos__c[0]], aa, bb)]
            return True
    if pos__c[0][:8] == 'INPLACE_':
            cmds[i:i+3] = [('!#=' + pos__c[0][8:], aa, bb)]
            return True
    if pos__c[0] == 'DELETE_SUBSCR' and len(pos__c) == 1:
            cmds[i:i+3] = [('DELETE_SUBSCR', aa, bb)]
            return True
    if pos__c[0] == 'DUP_TOPX' and pos__c[1] == 2:
        cmds[i:i+3] = [pos__a,pos__b,pos__a,pos__b]
        return True
    if SCmp(cmds,i, ('>', '>', '=', '=')):
                cmds[i:i+4] = [('SET_EXPRS_TO_VARS', (pos__c,pos__d), (bb,aa))]
                return True
    if SCmp(cmds,i, ('>', '>', 'CALL_FUNCTION_KW_1')) and pos__c[3] > 0:
        cmds[i:i+3] =  [(pos__c[0], pos__c[1], pos__c[2], pos__c[3]-1, pos__c[4] + ((aa, bb),), pos__c[5])]
        return True       
    if  is_cmdmem(pos__c):    
        cc = cmd2mem(pos__c)
        if pos__d[0] == 'STORE_SUBSCR_0':
                cmds[i:i+4] = [('STORE',(('PyObject_SetItem', bb, cc),), (aa,))]
                return True
        if pos__d[0] == 'SLICE+3' and len(pos__d) == 1:
                cmds[i:i+4] = [('!_PyEval_ApplySlice',) + (aa,) + (bb,) + (cc,)]
                return True
        if pos__d[0] == 'BUILD_SLICE' and len(pos__d) == 2 and pos__d[1] == 3:
                cmds[i:i+4] = [('!PySlice_New', aa, bb, cc)]
                return True
        if pos__d[0] == 'DELETE_SLICE+3':
            cmds[i:i+4] = [('DELETE_SLICE+3', aa, bb, cc)]
            return True
        if pos__d[0] == 'DUP_TOPX' and pos__d[1] == 3:
            cmds[i:i+4] = [pos__a,pos__b,pos__c,pos__a,pos__b,pos__c]
            return True
        if pos__d[0] == 'ROT_THREE' and pos__e[0] in ('STORE_SUBSCR_0', 'STORE_SLICE+2', 'STORE_SLICE+1'):
            cmds[i:i+4] = [pos__c,pos__a,pos__b]
            return True
        if SCmp(cmds,i, ('>','>', '>', '=', '=', '=')):
                    cmds[i:i+6] = [('SET_EXPRS_TO_VARS', (pos__d,pos__e,pos__f), (cc,bb,aa))]
                    return True
        if SCmp(cmds,i, ('>', '>','>', '>', '=', '=', '=', '=')):
                    cmds[i:i+8] = [('SET_EXPRS_TO_VARS', (pos__e,pos__f,pos__g,pos__h), (cmd2mem(pos__d),cc,bb,aa))]
                    return True
        if SCmp(cmds,i, ('>', '>', '>','>', '>', '=', '=', '=', '=', '=')):
                    cmds[i:i+10] = [('SET_EXPRS_TO_VARS', (pos__f,pos__g,pos__h,pos__i,pos__j), (cmd2mem(pos__e),cmd2mem(pos__d),cc,bb,aa))]
                    return True
        if SCmp(cmds,i, ('>', '>', '>', '>','>', '>', '=', '=', '=', '=', '=', '=')):
                    cmds[i:i+12] = [('SET_EXPRS_TO_VARS', (pos__g,pos__h,pos__i,pos__j,pos__k,pos__l), (cmd2mem(pos__f),cmd2mem(pos__e),cmd2mem(pos__d),cc,bb,aa))]
                    return True
        if SCmp(cmds,i, ('>', '>', '>', 'ROT_THREE', 'ROT_TWO', '=', '=', '=')):
                    cmds[i:i+8] = [('SET_EXPRS_TO_VARS', (pos__f,pos__g,pos__h), (aa,bb,cc))]
                    return True
        if SCmp(cmds,i, ('>','>','>', 'EXEC_STMT')):
            rpl(cmds,[('EXEC_STMT_3', aa, bb, cc)])
            return True
        if SCmp(cmds,i, ('>', '>', '>', 'STORE_SLICE+3')):
                    rpl(cmds,[('STORE_SLICE_LV+3', aa, bb, cc)])
                    return True
        if SCmp(cmds,i, ('>', '>', '>', '>', 'ROT_FOUR')):
                rpl(cmds,[pos__d,pos__a,pos__b,pos__c])
                return True       
        if SCmp(cmds,i, ('>', '>', '>', 'EXEC_STMT')):
                rpl(cmds,[(aa, bb, cc)])
                return True       
                
    if SCmp(cmds,i, ('>', '>', 'DELETE_SLICE+2')) and len(pos__c) == 1:
        cmds[i:i+3] = [(pos__c[0], aa, bb)]
        return True                
    if SCmp(cmds,i, ('>', '>', 'ROT_TWO', '=', '=')):
                cmds[i:i+5] = [('SET_EXPRS_TO_VARS', (pos__d,pos__e), (aa,bb))]
                return True
    if SCmp(cmds,i, ('>', '>', 'CALL_FUNCTION_1')) and pos__c[3] > 0:
        cmds[i:i+3] =  [(pos__c[0], pos__c[1], pos__c[2], pos__c[3]-1, pos__c[4] + ((aa, bb),))]
        return True       
    if SCmp(cmds,i, ('>', '>', 'CALL_FUNCTION_VAR_1')) and pos__c[3] > 0:
        rpl(cmds, [(pos__c[0], pos__c[1], pos__c[2], pos__c[3]-1, pos__c[4] + ((aa, bb),), pos__c[5])])
        return True       
    if SCmp(cmds,i, ('>', '>', 'CALL_FUNCTION_VAR_KW')):
        cmds[i:i+3] =  [('CALL_FUNCTION_VAR_KW_1',) + pos__c[1:] + (aa,bb)]
        return True       
    if SCmp(cmds,i, ('>', '>', 'CALL_FUNCTION_VAR_KW_1')) and pos__c[3] > 0:
        cmds[i:i+3] =  [(pos__c[0], pos__c[1], pos__c[2], pos__c[3]-1, pos__c[4] + ((aa, bb),), pos__c[5],pos__c[6])]
        return True       
    if SCmp(cmds,i, ('>','>', 'STORE_SLICE+2')):
        rpl(cmds,[('STORE_SLICE_LV+2', aa, bb)])
        return True
    if SCmp(cmds,i, ('>', '>', 'STORE_SLICE+1')):
                rpl(cmds,[('STORE_SLICE_LV+1', aa, bb)])
                return True
    if SCmp(cmds,i, ('>','>', 'DUP_TOP', 'ROT_THREE', 'COMPARE_OP')):
        rpl(cmds, [('3CMP_BEG_3', aa, pos__e[1], bb)])
        return True        
    if SCmp(cmds,i, ('>', '>', 'DUP_TOP', 'EXEC_STMT')):
            rpl(cmds,[('EXEC_STMT_3', aa, bb, bb)])
            return True       

    if pos__c[0] == 'PRINT_ITEM_TO_0':
        cmds[i:i+3] = [('PRINT_ITEM_TO_2', bb,aa)]
        return True

    if pos__c[0] == 'STORE_SUBSCR_0':
            cmds[i:i+3] = [('PyObject_SetItem',) + (aa,) + (bb,)]
            return True

    return False

imported_modules = {}

def module_dict_to_type_dict(pos__d):
    d2 = dict(pos__d)      
    for k in pos__d.keys():
        v = pos__d[k]
        t = type(v)
        if t is types.InstanceType:
            t2 = None
            try:
                t2 = Klass(T_OLD_CL_INST, v.__class__.__name__)
            except:
                pass
            if t2 is not None:
                t = t2
        else:
            if type(t) != type:
                t = Klass(T_NEW_CL_INST, v.__class__.__name__)
            else:    
                t = Klass(t)    
        d2[k] = t
    return d2

def CheckExistListImport(nm, fromlist=None,level=-1):
    global filename
    if nm in ('org.python.core',):
        return
    this = None
    if nm[0:3] == '_c_':
        nm = nm[3:]    
    if nm + '.py' == filename:
        return    
    if nm in list_import:
        return    
    if nm in imported_modules:
        this = imported_modules[nm]
    elif nm in sys.modules:    
        this = sys.modules[nm]
        imported_modules[nm] = this
        list_import[nm] = module_dict_to_type_dict(this.__dict__)
        FillListImport(this)    
        return
    elif Is3(nm, 'ImportedM'):
        v = Val3(nm, 'ImportedM')
        if type(v) is tuple and len(v) == 2:
##            print 'DOT4', v, nm
            return CheckExistListImport(v[0] + '.' + v[1])
        elif type(v) is str and v != nm:
            return CheckExistListImport(v)
        if v != nm:
            Fatal(nm, v)
    if this is None:
#        if nm == '':
#            Fatal('can\'t import empty module')     
        try:
            if fromlist is None and level == -1 and nm != '':
#                print '/1', nm
                this = __import__(nm)
                imported_modules[nm] = this
            elif nm == '' and level != -1 and len(fromlist) == 1:
#                print '/2', nm, fromlist
                this = __import__()
                imported_modules[fromlist[0]] = this
            else:    
#                print '/3', nm, fromlist
                this = __import__(nm,{},{}, fromlist)
##            print this
                imported_modules[nm] = this
        except:
            print sys.exc_info()
            ## if nm == '__builtin__.__dict__':
                ## assert False
            if level == -1:
                Debug('Module %s import unsuccessful2' % nm, fromlist) 
            else:    
                Debug('Module %s relative import unsuccessful2' % nm) 
##            Fatal('')
            return 
        
    nms = nm.split('.')
    s = ''
    old_this = this
    if fromlist is not None:
        assert this.__name__ == nm
        list_import[nm] = module_dict_to_type_dict(this.__dict__)
        imported_modules[nm] = this
    else:    
        for i, v in enumerate(nms):
            if s != '':
                s += '.'
                if v not in pos__d:
                    if fromlist is None:
                        Debug('Module %s %s (%s) import unsuccessful3' % (s, v, nm), fromlist) 
                    break
                this = pos__d[v]
            pos__d = this.__dict__
            s += v    
            assert type(this) is types.ModuleType    
            list_import[s] = module_dict_to_type_dict(pos__d)
            imported_modules[s] = this
    FillListImport(old_this)    

def FillListImport(module, nm = None, list_added = []):
    if nm is None:
        nm = module.__name__
    if not nm in imported_modules:
        imported_modules[nm] = module
    if not nm in list_import:
        list_import[nm] = module_dict_to_type_dict(module.__dict__)    
    if module in list_added:
        return    
    list_added.append(module)
    for k, v in module.__dict__.iteritems():
        if type(v) is types.ModuleType:
            FillListImport(v, nm + '.' + k, list_added)  
                  

FillListImport(sys)
FillListImport(types)
FillListImport(pprint)
FillListImport(glob)
FillListImport(traceback)
FillListImport(gc)
FillListImport(os)
FillListImport(math)
FillListImport(StringIO)
FillListImport(operator)
FillListImport(csv)
FillListImport(distutils)

def MyImport(nm):
    assert nm is not None
    if nm.startswith('__main__'):
        return None, {}
##    print 'DOT3', nm
    CheckExistListImport(nm)
    if nm not in imported_modules:
        return None, {}
    this = imported_modules[nm]
    pos__d = this.__dict__
    
    if '.' in nm:
        nms = nm.split('.')
        pos__d = this.__dict__
        if hasattr(this, '__file__') and this.__file__.endswith(nms[-1] + '.pyc'):
            return this, pos__d
        if this.__name__ == nm:
            return this, pos__d
        for i in range(1, len(nms)):
            if nms[i] in this.__dict__ and type(this.__dict__[nms[i]]) is types.ModuleType:
                this = pos__d[nms[i]]
                pos__d = this.__dict__
            else:
                if nms[i] in pos__d:
                    this = pos__d[nms[i]]
                    pos__d = this.__dict__
                else:
                    Debug('Import Error', nm, this, i, nms) 
                    return None, {}

#                print nms[i] in this.__dict__, type(this.__dict__[nms[i]])
                ## print nm
                ## print nms[i]
                ## print this.__dict__[nms[i]]
                ## print this.__dict__.keys()
##                Debug('Import Error', nm, this, i, nms) 
    return this, pos__d

## def get_list_names_module_raw(nm):
## #    if nm in known_modules:
    ## try:
        ## this, pos__d = MyImport(nm)
    ## except:
        ## Debug('Module %s import unsuccessful' % nm) #, sys.exc_info(), sys.exc_traceback)     
        ## return {}
    ## return module_dict_to_type_dict(pos__d)
    ## ## if '__all__' in pos__d:
        ## ## d2 = {}
        ## ## for k in pos__d['__all__']:
            ## ## if k in pos__d:
                ## ## d2[k] = pos__d[k]
        ## ## pos__d = d2   

def make_import_star(aa):
    nm = aa[1]
    if aa[1] in known_modules and aa[2] == ('CONST', -1):
        d = None
#        try:
        this, d = MyImport(aa[1])
#        except:
#            Debug('Module %s import unsuccessful' % aa[1])     
#            return [('IMPORT_STAR', aa)]
        if '__all__' in d:
            d2 = {}
            for k in d['__all__']:
                if k in d:
                    d2[k] = d[k]
            d = d2     
        r1 = []
        r2 = []
        for v in d:
            if v not in ('__name__', '__module__', '__file__') and \
                v in count_define_get:
                r1.append(v)
                r2.append(('STORE_NAME', v))
        r1 = ('CONST', tuple(r1))
        r2 = tuple(r2)
        return [('IMPORT_FROM_AS', aa[1], ('CONST', -1), r1, r2)]   
    else:
        Debug('Module %s star import unsuccessful - not in knows' % aa[1])     
    return [('IMPORT_STAR', aa)]

def val_imp(nm, k):
    assert nm is not None
    if nm.startswith('_c_'):
        nm = nm[3:]
    if nm == filename[:-3]:
        return None
    if Is3(nm, 'ImportedM'):
        v = Val3(nm, 'ImportedM')
        if type(v) is tuple and len(v) == 2:
            if v[0] in list_import and v[1] in list_import[v[0]] and not IsModule(list_import[v[0]][v[1]]):
                return None
    this, d = MyImport(nm)
    if this is None:
        if Is3(nm, 'ImportedM'):
            v = Val3(nm, 'ImportedM')
            if type(v) is tuple and len(v) == 2:
                imp = v[0] + '.' + v[1]
                return val_imp(v[0] + '.' + v[1], k)
            elif type(v) is str and v != nm:
                return val_imp(v, k)
            
##        print 'None', nm,k
#        return None
    if k not in d:
##        print nm, k, this, d
##        print 'l', nm, k, type(this), type(d)
        this, d = MyImport(nm + '.' + k)
        if this is not None and this.__name__ == (nm + '.' + k):
            return this
    ## if this is None:
        ## if Is3(nm, 'ImportedM'):
            ## v = Val3(nm, 'ImportedM')
            ## if type(v) is tuple and len(v) == 2:
                ## return val_imp(v[0] + '.' + v[1], k)
## ##        print 'None', nm,k
        ## return None
    if this is None:
        return None    
    return d[k]
    
def _process_compare_op_const(op, pos__a,pos__b):
    try:
        if op == '==':
            return('CONST', pos__a[1] == pos__b[1])              
        if op == '!=':
            return('CONST', pos__a[1] != pos__b[1])              
        if op == '>=':
            return('CONST', pos__a[1] >= pos__b[1])              
        if op == '<=':
            return('CONST', pos__a[1] <= pos__b[1])              
        if op == '<':
            return('CONST', pos__a[1] < pos__b[1])              
        if op == '>':
            return('CONST', pos__a[1] > pos__b[1])              
    except:
        pass    
    return None    

def _process_compare_op(op, a,b):
    if a[0] in ('LOAD_CONST', 'CONST') and b[0] in ('LOAD_CONST', 'CONST'):
        const_r = _process_compare_op_const(op, a,b)
        if const_r is not None:
            return const_r
    if a[0] in ('LOAD_CONST', 'CONST') and type(a[1]) is int:
        if op in ('==', '!='):
            if op in op_2_c_op and op not in('is', 'is not'):
               return('!BOOLEAN', ('!c_' + op_2_c_op[op] + '_Int', cmd2mem(b), cmd2mem(a)))              
        ## elif op in op_2_inv_op_:
            ## op = op_2_inv_op_[op]
            ## if int(a[1]) == a[1] and \
               ## op in op_2_c_op and op not in('is', 'is not'):
               ## return('!BOOLEAN', ('!c_' + op_2_c_op[op] + '_Int', cmd2mem(b), a[1]))              

    if a[0] == '!PY_SSIZE_T' and b[0] in ('LOAD_CONST', 'CONST') and type(b[1]) is int:
        if op in op_2_c_op and op not in('is', 'is not'):
            return('!BOOLEAN', ('!SSIZE_T' + op, a[1], b[1]))              
    ## if a[0] == '!PY_SSIZE_T':
        ## if op in ('==', '!='):
            ## if op in op_2_c_op and op not in('is', 'is not'):
               ## return('!BOOLEAN', ('!c_' + op_2_c_op[op] + '_Int', a, cmd2mem(b)))
        ## elif op in op_2_inv_op:
            ## op = op_2_inv_op[op]
            ## if op in op_2_c_op and op not in('is', 'is not'):
               ## return('!BOOLEAN', ('!c_' + op_2_c_op[op] + '_Int', cmd2mem(b), a))
    if b[0] in ('LOAD_CONST', 'CONST') and type(b[1]) is int:
        if int(b[1]) == b[1] and \
            op in op_2_c_op and op not in('is', 'is not'):
            return('!BOOLEAN', ('!c_' + op_2_c_op[op] + '_Int', cmd2mem(a), cmd2mem(b)))              
    if b[0] in ('LOAD_CONST', 'CONST') and type(b[1]) is str:
        if op in ('==', '!='):
            return('!BOOLEAN', ('!c_' + op_2_c_op[op] + '_String', cmd2mem(a), cmd2mem(b)))
# 11.06.2010 !!!
    if a[0] in ('LOAD_CONST', 'CONST') and type(a[1]) is str:
        if op in ('==', '!='):
            return('!BOOLEAN', ('!c_' + op_2_c_op[op] + '_String', cmd2mem(b), cmd2mem(a)))


    ## if b[0] == '!PY_SSIZE_T':
        ## if op in op_2_c_op and op not in('is', 'is not'):
            ## return ('!BOOLEAN', ('!c_' + op_2_c_op[op] + '_Int', cmd2mem(a), b))
    if op == 'not in':            
        return Not(('!BOOLEAN', ('!PySequence_Contains(', cmd2mem(b), cmd2mem(a))))
    if op == 'in':            
        return ('!BOOLEAN', ('!PySequence_Contains(', cmd2mem(b), cmd2mem(a)))
    if op == 'is':            
        return ('!BOOLEAN',('!_EQ_', cmd2mem(a), cmd2mem(b)))
    if op == 'is not':            
        return ('!BOOLEAN',('!_NEQ_', cmd2mem(a), cmd2mem(b)))
    return None

def process_compare_op(op, a,b):
    ret = _process_compare_op(op,a,b)
    if ret is not None:
        return [ret]
    if op in op_2_c_op:            
        return [('!PyObject_RichCompare(', cmd2mem(a), cmd2mem(b), op_2_c_op[op])]
    Fatal('Can\'t handle compare_op', op, a, b)
    
def process_load_const_test1(cmds):
    try:
        if pos__a[1]:
            rpl(cmds,[pos__a, ('JUMP',) + pos__b[1:]])
        else:    
            rpl(cmds,[])
        return True
    except:
        pass
    return False

def process_load_const_test2(cmds):
    try:
        if not pos__a[1]:
            rpl(cmds,[pos__a, ('JUMP',) + pos__b[1:]])
        else:    
            rpl(cmds,[])
        return True
    except:
        pass
    return False

def process_load_const_test3(cmds):
    try:
        if pos__a[1]:
            rpl(cmds,[pos__a, ('JUMP',) + pos__b[1:]])
        else:    
            rpl(cmds,[pos__a])
        return True
    except:
        pass
    return False

def process_load_const_test4(cmds):
    try:
        if not pos__a[1]:
            rpl(cmds,[pos__a, ('JUMP',) + pos__b[1:]])
        else:    
            rpl(cmds,[pos__a])
        return True
    except:
        pass
    return False

def process_load_const(cmds,i,added_pass):
    if pos__a[0] == 'LOAD_CONST' and pos__b[0] == 'UNPACK_SEQUENCE' and pos__a[1] is not None and pos__b[1] == len(pos__a[1]):
        cmds[i:i+2] = [('LOAD_CONST', x) for x in reversed(pos__a[1])]
        return True
    if pos__a[0] == 'LOAD_CONST' and pos__b[0] == 'STORE':
        cmds[i:i+2] = [pos__b, pos__a]
        return True
    if pos__a[0] == 'LOAD_CONST' and pos__b[0] == 'DUP_TOP':
        cmds[i:i+2] = [pos__a, pos__a[:]]
        return True   
    if SCmp(cmds,i, ('LOAD_CONST', '-')):
        rpl(cmds,[pos__b,pos__a])
        return True     
    if SCmp(cmds,i,('LOAD_CONST', 'JUMP_IF_TRUE', 'POP_TOP')):
        if process_load_const_test1(cmds):
            return True
    if SCmp(cmds,i,('LOAD_CONST', 'JUMP_IF_FALSE', 'POP_TOP')):
        if process_load_const_test2(cmds):
            return True
    if SCmp(cmds,i,('LOAD_CONST', 'JUMP_IF_TRUE')):
        if process_load_const_test3(cmds):
            return True
    if SCmp(cmds,i,('LOAD_CONST', 'JUMP_IF_FALSE')):
        if process_load_const_test4(cmds):
            return True
    return False

def process_j_setup_finally(cmds,i,added_pass):
    if SCmp(cmds,i, ('J_SETUP_FINALLY', '*', 'POP_BLOCK', 'LOAD_CONST', \
                    (':',0,1), '*', 'END_FINALLY')) and pos__d[1] is None:                                    
            rpl(cmds,[[('(TRY',), pos__b, (')(FINALLY',), pos__f, (')ENDTRY',)]])
            return True
    if SCmp(cmds,i, ('J_SETUP_FINALLY', '*', 'POP_BLOCK', 'LOAD_CONST', \
                    (':',0,1), 'END_FINALLY')) and pos__d[1] is None:                                    
            rpl(cmds,[[('(TRY',), pos__b, (')(FINALLY',), [('PASS',)], (')ENDTRY',)]])
            return True
    if SCmp(cmds,i, ('J_SETUP_FINALLY', 'POP_BLOCK', 'LOAD_CONST', \
                    (':',0,1), 'END_FINALLY')) and pos__c[1] is None:                                    
            rpl(cmds,[[('(TRY',), [('PASS',)], (')(FINALLY',), [('PASS',)], (')ENDTRY',)]])
            return True
    if SCmp(cmds,i, ('J_SETUP_FINALLY', 'JUMP_CONTINUE', 'POP_BLOCK', \
                    'LOAD_CONST', (':', 0, 1), '**n', 'END_FINALLY', \
                    'JUMP_CONTINUE')) and pos__b[1] == pos__h[1]:
            rpl(cmds,[[('(TRY',), [('CONTINUE',)], (')(FINALLY',), pos__f, (')ENDTRY',)],pos__h])
            return True
    if SCmp(cmds,i, ('J_SETUP_FINALLY', '*n','JUMP_CONTINUE', 'POP_BLOCK', \
                    'LOAD_CONST', (':', 0, 1), '**n', 'END_FINALLY', \
                    'JUMP_CONTINUE')) and pos__c[1] == pos__i[1]:
            rpl(cmds,[[('(TRY',), pos__b + [('CONTINUE',)], (')(FINALLY',), pos__g, (')ENDTRY',)],pos__h])
            return True
    if SCmp(cmds,i, ('J_SETUP_FINALLY', 'POP_BLOCK', 'LOAD_CONST', \
                    (':',0,1), '*', 'END_FINALLY')) and pos__c[1] is None:                                    
            rpl(cmds,[[('(TRY',), [('PASS',)], (')(FINALLY',), pos__e, (')ENDTRY',)]])
            return True
    if SCmp(cmds,i, ('J_SETUP_FINALLY', '*r', (':',0,1), '*', 'END_FINALLY')):
        rpl(cmds,[[('(TRY',), pos__b, (')(FINALLY',), pos__d, (')ENDTRY',)]])
        return True
    if SCmp(cmds,i, ('J_SETUP_FINALLY', '*n', 'LOAD_CONST', (':',0,1), \
                    '*', 'END_FINALLY')) and pos__c[1] is None:
        rpl(cmds,[[('(TRY',), pos__b, (')(FINALLY',), pos__e, (')ENDTRY',)]])
        return True
    return False

def process_j_begin_with(cmds,i,added_pass):
    if SCmp(cmds,i, ('J_BEGIN_WITH', 'POP_BLOCK',('LOAD_CONST', None),\
                    (':', 0, 1), 'WITH_CLEANUP', 'END_FINALLY')):
            rpl(cmds,[[('(WITH',) + pos__a[2:],[('PASS',)], (')ENDWITH',)]])
            return True             
    if SCmp(cmds,i, ('J_BEGIN_WITH', '*', 'POP_BLOCK',('LOAD_CONST', None),\
                    (':', 0, 1), 'WITH_CLEANUP', 'END_FINALLY')):
            rpl(cmds,[[('(WITH',) + pos__a[2:], pos__b, (')ENDWITH',)]])
            return True             
    if SCmp(cmds,i, ('J_BEGIN_WITH', '*', 'JUMP_CONTINUE', 'POP_BLOCK',('LOAD_CONST', None),\
                    (':', 0, 1), 'WITH_CLEANUP', 'END_FINALLY')):
            rpl(cmds,[[('(WITH',) + pos__a[2:], pos__b + [('CONTINUE',)], (')ENDWITH',)]])
            return True             
    if SCmp(cmds,i, ('J_BEGIN_WITH', 'JUMP_CONTINUE', 'POP_BLOCK',('LOAD_CONST', None),\
                    (':', 0, 1), 'WITH_CLEANUP', 'END_FINALLY')):
            rpl(cmds,[[('(WITH',) + pos__a[2:], [('CONTINUE',)], (')ENDWITH',)]])
            return True             
    if SCmp(cmds,i, ('J_BEGIN_WITH', '*l', 'POP_BLOCK',('LOAD_CONST', None),\
                    (':', 0, 1), 'WITH_CLEANUP', 'END_FINALLY')):
            rpl(cmds,[[('(WITH',) + pos__a[2:], [('PASS',)], (')ENDWITH',)]])
            return True             
    if SCmp(cmds,i, ('J_BEGIN_WITH', '*r',\
                    (':', 0, 1), 'WITH_CLEANUP', 'END_FINALLY')):
            rpl(cmds,[[('(WITH',) + pos__a[2:], pos__b, (')ENDWITH',)]])
            return True             
    return False

def process_j_setup_loop(cmds,i,added_pass):
    if pos__a[0] == 'J_SETUP_LOOP':
        if len(pos__a) == 2 and pos__b[0] == '!GET_ITER' and len(pos__b) == 2:
            cmds[i:i+2] = [('J_SETUP_LOOP_FOR', pos__a[1], pos__b[1])]
            return True
        if len(pos__a) == 3 and pos__b[0] == '!GET_ITER' and len(pos__b) == 2:
            cmds[i:i+2] = [('.L', pos__a[2]),('J_SETUP_LOOP_FOR', pos__a[1], pos__b[1])]
            return True
        if len(pos__a) == 2 and pos__b[0] == '.L' and pos__c[0] == '!GET_ITER' and len(pos__c) == 2:
            cmds[i:i+3] = [('J_SETUP_LOOP_FOR', pos__a[1], pos__c[1])]
            return True
        if len(pos__a) == 3 and pos__b[0] == '.L' and pos__c[0] == '!GET_ITER' and len(pos__c) == 2:
            cmds[i:i+3] = [('.L', pos__a[2]),('J_SETUP_LOOP_FOR', pos__a[1], pos__c[1])]
            return True
        if SCmp(cmds,i, ('J_SETUP_LOOP', ('!', '(IF', '*c', ')ENDIF'), 'POP_BLOCK', 'JUMP')) and\
            pos__a[0] != pos__d[1]:
            bod = pos__b[1][:-1]
            if len(bod) == 0:
                bod = [('PASS',)]    
            cmds[i:i+4] = [[('(WHILE',) + pos__b[0][1:], bod, (')ENDWHILE',)],pos__d]
            return True
        if isblock(pos__b) and pos__c[0] == 'POP_BLOCK' and \
            pos__d[0] == '.:' and pos__d[1] == pos__a[1] and OneJump(pos__d[1], cmds) and len(pos__b) == 3 and\
            pos__b[0][0] == '(IF' and pos__b[2][0] == ')ENDIF' and type(pos__b[1]) is list:
            cmds[i:i+4] = [[('(WHILE',) + pos__b[0][1:], pos__b[1], (')ENDWHILE',)]]
            return True
        if pos__b[0] == '.:' and pos__c[0] == 'JUMP_IF2_FALSE_POP' and\
            isblock(pos__d) and  pos__e[0] in jump and pos__e[1] == pos__b[1] and \
            pos__f[0] == '.:' and pos__f[1] == pos__c[1] and pos__g[0] == 'POP_BLOCK' and \
            pos__h[0] == '.:' and pos__h[1] == pos__a[1] and\
            OneJump(pos__b[1], cmds) and\
            OneJump(pos__f[1], cmds) and\
            OneJump(pos__h[1], cmds):
            cmds[i:i+8] = [[('(WHILE',) + pos__c[2:], pos__d[:], (')ENDWHILE',)]]
            return True
        if pos__b[0] == '.:' and pos__c[0] == 'JUMP_IF2_FALSE_POP' and\
            isblock(pos__d) and  pos__e[0] in jump and pos__e[1] == pos__b[1] and \
            pos__f[0] == '.:' and pos__f[1] == pos__c[1] and pos__g[0] == 'POP_BLOCK' and \
            pos__h[0] == '.:' and pos__h[1] == pos__a[1] and\
            OneJump(pos__b[1], cmds) and\
            OneJump(pos__f[1], cmds) and\
            CntJump(pos__h[1], cmds) > 1:
            cmds[i:i+8] = [[('(WHILE',) + pos__c[2:], pos__d[:], (')ENDWHILE',)],pos__h]
            return True
        if SCmp(cmds,i, ('J_SETUP_LOOP', 'LOAD_FAST', (':', 5, 1),\
                        'J_LOOP_VARS', '*', 'JUMP_CONTINUE', (':',3,1),\
                        'POP_BLOCK', ('::', 0))) and pos__b[1][0] == '.':
            rpl(cmds,[[('(FOR_ITER',  pos__d[2], cmd2mem(pos__b)), pos__e, (')ENDFOR_ITER',)]])
            return True            
        if SCmp(cmds,i, ('J_SETUP_LOOP', 'JUMP_IF2_FALSE_POP_CONTINUE', '*r',
                        (':', 1, 1), 'POP_BLOCK', ('::',0))):
                rpl(cmds,[[('(WHILE',) + pos__b[2:] , pos__c, (')ENDWHILE',)]])
                return True   
        if SCmp(cmds,i, ('J_SETUP_LOOP', 'LOAD_FAST', (':', 5, 1), \
                        'J_FOR_ITER',\
                        '*', 'JUMP_CONTINUE', \
                        (':', 3, 1), 'POP_BLOCK', ('::', 0))) and\
            pos__e[0][0] == 'UNPACK_SEQ_AND_STORE' and pos__e[0][1] == 0 and pos__b[1][0] == '.':
                rpl(cmds,[[('(FOR_GENERATOR', pos__e[0][2]), pos__e[1:], (')ENDFOR_GENERATOR',)]])
                return True                   
        if SCmp(cmds,i, ('J_SETUP_LOOP', 'LOAD_FAST', (':', 5, 1), \
                        'J_FOR_ITER',\
                        '*', 'JUMP_CONTINUE', \
                        (':', 3, 1), 'POP_BLOCK', ('::', 0))) and\
            pos__e[0][0] == '.L' and pos__e[1][0] == 'UNPACK_SEQ_AND_STORE' and pos__e[1][1] == 0 and pos__b[1][0] == '.':
                rpl(cmds,[[('(FOR_GENERATOR', pos__e[1][2]), pos__e[2:], (')ENDFOR_GENERATOR',)]])
                return True    
        if SCmp(cmds,i, ('J_SETUP_LOOP', (':', 3, 1), '*', 'JUMP_CONTINUE', ('::', 0))):
                rpl(cmds,[[('(WHILE', TRUE), pos__c, (')ENDWHILE',)]])
                return True     
        if SCmp(cmds,i, ('J_SETUP_LOOP', (':', 4,1), 'JUMP_IF2_FALSE_POP', '*',\
                        'JUMP_CONTINUE', (':', 2, 1), 'POP_BLOCK', ('::', 0))) :
                rpl(cmds, [[('(WHILE',) + pos__c[2:], pos__d, (')ENDWHILE',)]])
                return True   
        if SCmp(cmds,i, ('J_SETUP_LOOP', (':', 4, 1), 'JUMP_IF2_TRUE_POP', \
                        '*', 'JUMP_CONTINUE', (':',2, 1), 'POP_BLOCK', ('::',0))):
            rpl(cmds,[[('(WHILE', Not(pos__c[2])), pos__d, (')ENDWHILE',)]])
            return True
    # {'*' removed
        if SCmp(cmds,i, ('J_SETUP_LOOP', ('!', '(IF', '*c', ')ENDIF'), \
                        'POP_BLOCK', '*r', (':',0,1), '*r')):
                rpl(cmds,[[('(WHILE', pos__b[0][1]), pos__b[1], (')(ELSE',), pos__d, (')ENDWHILE',)],pos__f])
                return True
        if SCmp(cmds,i, ('J_SETUP_LOOP', ('!', '(IF', '*r', ')ENDIF'), \
                        'POP_BLOCK', '*r', (':',0,1), '*r')):
                rpl(cmds,[[('(WHILE', pos__b[0][1]), pos__b[1], (')(ELSE',), pos__d, (')ENDWHILE',)],pos__f])
                return True
    # }end '*' removed
        if SCmp(cmds,i, ('J_SETUP_LOOP',  (':', 3, 1), '*', 'JUMP_CONTINUE')):
            rpl(cmds,[[('(WHILE', TRUE), pos__c, (')ENDWHILE',)]])
            return True
        if SCmp(cmds,i, ('J_SETUP_LOOP', '*r', (':', 0,1), 'POP_BLOCK')):
            rpl(cmds,[[('(WHILE', TRUE), pos__b, (')ENDWHILE',)]])
            return True
        if SCmp(cmds,i, ('J_SETUP_LOOP', '*n', ('::', 0))):
            rpl(cmds,[[('(WHILE', TRUE), pos__b, (')ENDWHILE',)]])
            return True
        if SCmp(cmds,i, ('J_SETUP_LOOP', '*r', ('::', 0))):
            rpl(cmds,[[('(WHILE', TRUE), pos__b, (')ENDWHILE',)]])
            return True
        if SCmp(cmds,i, ('J_SETUP_LOOP', ('!', '(IF', '*c', ')ENDIF'),\
                        'POP_BLOCK', '*n', ('::', 0))):
                rpl(cmds,[[('(WHILE',) + pos__b[0][1:], pos__b[1], (')(ELSE',),pos__d,(')ENDWHILE',)]])
                return True   
        if SCmp(cmds,i, ('J_SETUP_LOOP', (':', 2, 1), 'JUMP_IF2_TRUE_POP_CONTINUE', \
                        'POP_BLOCK', ('::', 0))):
            rpl(cmds,[[('(WHILE',) + pos__c[2:], [('PASS',)],(')ENDWHILE',)]])
            return True
        if SCmp(cmds,i, ('J_SETUP_LOOP', ('!', '(IF', '*c', ')ENDIF'), 'POP_BLOCK',\
                        'ju')) and pos__d[1] == pos__a[1]:
            bod = pos__b[1][:-1]
            if len(bod) == 0:
                bod = [('PASS',)]    
            rpl(cmds,[[('(WHILE',) + pos__b[0][1:], bod,(')ENDWHILE',)],pos__d])
            return True
        if SCmp(cmds,i, ('J_SETUP_LOOP', (':', 4,1), 'JUMP_IF2_FALSE_POP', \
                        '*n', 'J_SETUP_LOOP', (':', 7, 1), '*n', 'JUMP', \
                        (':', 2,1), 'POP_BLOCK', ('::', 0))):
                rpl(cmds,[[('(WHILE',) + pos__c[2:], pos__d + [('(WHILE', TRUE), pos__g, (')ENDWHILE',)], (')ENDWHILE',)]])
                return True       
        ## if SCmp(cmds,i, ('J_SETUP_LOOP', ('!', '(IF', '*c', ')ENDIF'),\ # By CloneDigger
                        ## 'POP_BLOCK', '*n', ('::',0))):
                ## rpl(cmds,[[('(WHILE',) + pos__b[0][1:], pos__b[1], (')(ELSE',), pos__d, (')ENDWHILE',)]])
                ## return True       
        if SCmp(cmds,i, ('J_SETUP_LOOP', ('!', '(IF', '*c', ')ENDIF'),\
                        'POP_BLOCK', '*n', 'jc')) and pos__a[1] == pos__e[1]:
                rpl(cmds,[[('(WHILE',) + pos__b[0][1:], pos__b[1], (')(ELSE',), pos__d, (')ENDWHILE',)]])
                return True       
        if SCmp(cmds,i, ('J_SETUP_LOOP', ('!', '(IF', '*c', ')ENDIF'),\
                        'POP_BLOCK', '*r', ('::',0))):
                rpl(cmds,[[('(WHILE',) + pos__b[0][1:], pos__b[1], (')(ELSE',), pos__d, (')ENDWHILE',)]])
                return True       
        if SCmp(cmds,i, ('J_SETUP_LOOP', ('!', '(IF', '*r', ')ENDIF'),\
                        'POP_BLOCK', '*n', ('::',0))):
                rpl(cmds,[[('(WHILE',) + pos__b[0][1:], pos__b[1], (')(ELSE',), pos__d, (')ENDWHILE',)]])
                return True    
        if SCmp(cmds,i, ('J_SETUP_LOOP', ('!', '(IF', '*c', ')ENDIF'), \
                        'POP_BLOCK', ('::', 0))):       #  4
                rpl(cmds,[[('(WHILE',) + pos__b[0][1:], pos__b[1], (')ENDWHILE',)]])
                return True       
        if SCmp(cmds,i, ('J_SETUP_LOOP', ('!', '.L', '(IF', '*c', ')ENDIF'), \
                        'POP_BLOCK', ('::', 0))):       #  4
                rpl(cmds,[[('(WHILE',) + pos__b[1][1:], pos__b[2], (')ENDWHILE',)]])
                return True       
        if SCmp(cmds,i, ('J_SETUP_LOOP', (':', 2, 1), 'JUMP_CONTINUE', ('::', 0))):
            rpl(cmds,[[('(WHILE', TRUE), [('PASS',)], (')ENDWHILE',)]])
            return True
        if SCmp(cmds,i, ('J_SETUP_LOOP', (':', 2,1), 'JUMP_IF2_TRUE_POP_CONTINUE',\
                        'POP_BLOCK', ('::', 0))):
            rpl(cmds,[[('(WHILE',) + pos__c[2:], [('PASS',)], (')ENDWHILE',)]])
            return True
        if SCmp(cmds,i, ('J_SETUP_LOOP', (':', 2,1), 'JUMP_IF2_FALSE_POP_CONTINUE',\
                        'POP_BLOCK', ('::', 0))):
            rpl(cmds,[[('(WHILE', Not(pos__c[2])), [('PASS',)], (')ENDWHILE',)]])
            return True
    return False

def process_jump(cmds,i, added_pass):
    global pos__a,pos__b,pos__c,pos__d,pos__e,pos__f,pos__g,pos__h,pos__i,pos__j,pos__k,pos__l

    if SCmp(cmds,i,('JUMP_IF2_FALSE_POP', 'JUMP_IF2_FALSE_POP')) and pos__a[2] == pos__b[2]:
        rpl(cmds,[pos__a])
        return True
    if SCmp(cmds,i,('JUMP_IF2_TRUE_POP', 'JUMP_IF2_TRUE_POP')) and pos__a[2] == pos__b[2]:
        rpl(cmds,[pos__a])
        return True
    if SCmp(cmds,i,('JUMP_IF2_FALSE_POP', 'JUMP_IF2_FALSE_POP')) and pos__a[1] == pos__b[1]:
        rpl(cmds,[('JUMP_IF2_FALSE_POP', pos__a[1], And_j(pos__a[2], pos__b[2]))])
        return True
    if SCmp(cmds,i,('JUMP_IF2_TRUE_POP', 'JUMP_IF2_TRUE_POP')) and pos__a[1] == pos__b[1]:
        rpl(cmds,[('JUMP_IF2_TRUE_POP', pos__a[1], Or_j(pos__a[2], pos__b[2]))])
        return True
    if SCmp(cmds,i,('JUMP_IF2_TRUE_POP', 'JUMP_IF2_FALSE_POP')) and pos__a[1] == pos__b[1]:
        rpl(cmds,[('JUMP_IF2_TRUE_POP', pos__a[1], Or_j(pos__a[2], Not(pos__b[2])))])
        return True
    if SCmp(cmds,i,('JUMP_IF2_FALSE_POP_CONTINUE', 'JUMP_IF2_FALSE_POP_CONTINUE')) and pos__a[1] == pos__b[1]:
        rpl(cmds,[('JUMP_IF2_FALSE_POP_CONTINUE', pos__a[1], And_j(pos__a[2], pos__b[2]))])
        return True
    if SCmp(cmds,i,('JUMP_IF2_TRUE_POP_CONTINUE', 'JUMP_IF2_TRUE_POP_CONTINUE')) and pos__a[1] == pos__b[1]:
        rpl(cmds,[('JUMP_IF2_TRUE_POP_CONTINUE', pos__a[1], Or_j(pos__a[2], pos__b[2]))])
        return True
    if SCmp(cmds,i,('JUMP_IF2_TRUE_POP_CONTINUE', 'JUMP_IF2_FALSE_POP_CONTINUE')) and pos__a[1] == pos__b[1]:
        rpl(cmds,[('JUMP_IF2_TRUE_POP_CONTINUE', pos__a[1], Or_j(pos__a[2], Not(pos__b[2]) ))])
        return True
    if SCmp(cmds,i,('JUMP_IF2_FALSE_POP', 'JUMP_IF2_TRUE_POP')) and pos__a[1] == pos__b[1]:
        rpl(cmds,[('JUMP_IF2_FALSE_POP', pos__a[1], And_j(pos__a[2], Not(pos__b[2])))])
        return True
    if SCmp(cmds,i,('JUMP_IF2_FALSE_POP_CONTINUE', 'JUMP_IF2_TRUE_POP_CONTINUE')) and pos__a[1] == pos__b[1]:
        rpl(cmds,[('JUMP_IF2_FALSE_POP_CONTINUE', pos__a[1], And_j(pos__a[2], Not(pos__b[2])))])
        return True
    if SCmp(cmds,i,('xJUMP_IF2_FALSE_POP', '*', 'ju', (':', 0,1), '*', ('::',2))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')(ELSE',), pos__e, (')ENDIF',)]])
        return True

    if SCmp(cmds,i,('xJUMP_IF2_FALSE_POP', ('!', '.L', '(IF', '*', ')ENDIF'), ('::',0))):
        rpl(cmds,[[('(IF', And_j(pos__a[2], pos__b[1][1])), pos__b[2], (')ENDIF',)]])
        return True

    if SCmp(cmds,i,('xJUMP_IF2_FALSE_POP', '*', ('::',0))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')ENDIF',)]])
        return True

    if SCmp(cmds,i,('JUMP_IF2_TRUE_POP','JUMP_IF2_FALSE_POP', ('::', 0))):
        rpl(cmds,[(pos__b[0], pos__b[1], Or_j(pos__a[2], pos__b[2]))])
        return True     
    if SCmp(cmds,i,('JUMP_IF2_TRUE_POP','JUMP_IF2_FALSE_POP_CONTINUE', ('::', 0))):
        rpl(cmds,[(pos__b[0], pos__b[1], Or_j(pos__a[2], pos__b[2]))])
        return True     
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_TRUE_POP_CONTINUE', '*l', ('::',0))):
        rpl(cmds,[(pos__b[0], pos__b[1], And_j(pos__a[2], pos__b[2])),pos__c])
        return True     
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_TRUE_POP_CONTINUE', ('::',0))):
        rpl(cmds,[(pos__b[0], pos__b[1], And_j(pos__a[2], pos__b[2]))])
        return True     
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*', 'JUMP_IF2_FALSE_POP', '*', ('::', (0,2)))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b+ [('(IF',) + pos__c[2:], pos__d, (')ENDIF',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*', 'ju', (':', 0,1), 'JUMP_IF2_FALSE_POP',\
                    '*', ('::', (2,4)))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')(ELSE',), [('(IF',) + pos__e[2:], pos__f, (')ENDIF',)],(')ENDIF',)]])
        return True 
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP', '*', ('::',0))):  
        rpl(cmds,[[('(IF', Not(pos__a[2])), pos__b, (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP', ('::',0))):  
        rpl(cmds,[('UNPUSH', (pos__a[2]))])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', ('::',0))):  
        rpl(cmds,[('UNPUSH', (pos__a[2]))])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*', 'JUMP_CONTINUE', ('::',0))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b+ [('CONTINUE',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP_CONTINUE', '*', ('::',0))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP_CONTINUE', '*c')):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP_CONTINUE', '*')):
        rpl(cmds,[[('(IF',) + pos__a[2:], [('CONTINUE',)], (')ENDIF',)]+pos__b])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*', 'JUMP_CONTINUE', (':', 0, 1), \
                    '*', ('::',2))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')(ELSE',), pos__e, (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*', 'JUMP_CONTINUE', (':', 0, 2), \
                    '*', ('::',2))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b + [('CONTINUE',)], (')ENDIF',)],pos__d,pos__e])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '>', 'JUMP_IF_TRUE', 'POP_TOP',\
                    (':', 0,1), '>', ('::', 2))):
        rpl(cmds,[Or_j_s(And_j_s(pos__a[2], pos__b),pos__f)])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP', '*', 'JUMP_CONTINUE', (':',0,1), '*', \
                    ('::',2))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__e, (')(ELSE',),pos__b, (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_TRUE_POP', (':',0,1),\
                    'JUMP_IF2_FALSE_POP', (':', 1,1), '*', 'JUMP_CONTINUE', ('::',3))):
        tt = Or_j( And_j(pos__a[2], pos__b[2]),pos__d[2])
        rpl(cmds,[[('(IF', tt), pos__f + [('CONTINUE',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_TRUE_POP', (':',0,1),\
                    'JUMP_IF2_FALSE_POP', ('::', 1))):
        tt = Or_j( And_j(pos__a[2], pos__b[2]),pos__d[2])
        rpl(cmds,[('JUMP_IF2_FALSE_POP', pos__d[1], tt) + pos__a[2:]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP', 'JUMP_IF2_FALSE_POP_CONTINUE', (':',0,1), \
                    '*', ('::',1))):
        ifexpr = Or_j(pos__a[2], pos__b[2])
        rpl(cmds,[[('(IF', ifexpr), pos__d, (')ENDIF',), ('CONTINUE',)]])
        return True
    if SCmp(cmds,i, ('ju', '.:', 'JUMP_CONTINUE')) and pos__a[1] == pos__c[1] and pos__a[1] != pos__b[1]:
        rpl(cmds,[pos__b,pos__c])
        return True     
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*r')):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')ENDIF',)], ('JUMP', pos__a[1])])
        return True                         
    if SCmp(cmds,i, ('JUMP_IF_TRUE', 'POP_TOP', '.L', '>')):
        rpl(cmds,[pos__a,pos__b,pos__d])
        return True    
    if SCmp(cmds,i, ('JUMP_IF_FALSE', 'POP_TOP', '.L', '>')):
        rpl(cmds,[pos__a,pos__b,pos__d])
        return True    
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP', '*', 'JUMP', (':',0,1), '*', ('::',2))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__e, (')(ELSE',), pos__b, (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*', 'JUMP', (':',0,1), '*', ('::',2))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')(ELSE',), pos__e, (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_CONTINUE', ('::',0))):
        rpl(cmds,[[('(IF',) + pos__a[2:], [('CONTINUE',)], (')ENDIF',)]])
        return True    
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*l', 'J_SETUP_LOOP_FOR')):
        rpl(cmds,[pos__a,pos__c])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*', 'JUMP_IF2_FALSE_POP_CONTINUE', '*r',\
                    ('::', 0))):
        rpl(cmds,[[('(IF',) +pos__a[2:] ,pos__b+ [('(IF',) + pos__c[2:], pos__d, \
                                    (')ENDIF',), ('CONTINUE',)], (')ENDIF',)]])
        return True 
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*', 'JUMP_IF2_FALSE_POP_CONTINUE', '*',\
                    ('::', 0))):
        rpl(cmds,[[('(IF',) +pos__a[2:] ,pos__b+ [('(IF',) + pos__c[2:], pos__d, \
                                    (')(ELSE',), [('CONTINUE',)], \
                                    (')ENDIF',)], (')ENDIF',)]])
        return True 
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP', ('::',0))):
        rpl(cmds,[('JUMP_IF2_TRUE_POP', pos__b[1]) + pos__a[2:]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*l', ('::',0))):
        rpl(cmds,[[pos__b, ('UNPUSH', pos__a[2])]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*', 'JUMP_IF2_FALSE_POP_CONTINUE', '*l',\
                    ('::',0,))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')(ELSE',), \
                            [('(IF', Not(pos__c[2])), [('CONTINUE',)], (')ENDIF',)], \
                            (')ENDIF',)]])
        return True        
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_FALSE_POP_CONTINUE', '*r',\
                    (':',0,1), 'JUMP_IF2_FALSE_POP_CONTINUE', '*r')) and pos__e[1] == pos__b[1]:
        rpl(cmds,[[('(IF',) + pos__a[2:],
                            [('(IF',) +pos__b[2:], pos__c, (')ENDIF',)], (')(ELSE',),\
                            [('(IF',) +pos__e[2:], pos__f, (')ENDIF',)], (')ENDIF',)], ('JUMP_CONTINUE', pos__b[1])])
        return True 
    if SCmp(cmds,i, ('JUMP', ('::',0))):
        rpl(cmds,[])
        return True    
    if SCmp(cmds,i, ('JUMP', '*', ('::',0))):
        rpl(cmds,[])
        return True    
    if SCmp(cmds,i, ('JUMP', '*', 'JUMP', ('::',0))):
        rpl(cmds,[])
        return True    
    if SCmp(cmds,i, ('JUMP', 'POP_BLOCK', 'JUMP', ('::',0))):
        rpl(cmds,[])
        return True      
    if SCmp(cmds,i, ('JUMP', (':', 4, 1), 'xJUMP_IF2_FALSE_POP', '*', 'JUMP')):
        rpl(cmds,[pos__a])
        return True
    if SCmp(cmds,i, ('JUMP_CONTINUE', 'JUMP_CONTINUE')) and pos__a[1] == pos__b[1]:
        rpl(cmds,[pos__a])
        return True    
    if SCmp(cmds,i, ('JUMP','JUMP')) and pos__a[1] == pos__b[1]:
        rpl(cmds,[pos__a])
        return True            
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '>', 'JUMP', (':', 0, 1), '*l', '>', ('::', 2))):
            rpl(cmds,[('!COND_EXPR', pos__a[2], cmd2mem(pos__b),cmd2mem(pos__f))])
            return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '>', 'JUMP', (':', 0, 1), '>', ('::', 2))):
            rpl(cmds,[('!COND_EXPR', pos__a[2], cmd2mem(pos__b),cmd2mem(pos__e))])
            return True
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP_CONTINUE', 'JUMP_IF2_TRUE_POP', '*',\
                    'JUMP_CONTINUE', (':', 1, 2))) and pos__d[1] == pos__a[1]:
            rpl(cmds,[[('(IF',) + pos__a[2:], [('CONTINUE',)],\
                            (')(ELSE',), [('(IF', Not(pos__b[2])), pos__c + [('CONTINUE',)], (')ENDIF',)](')ENDIF',)],pos__e])
            return True                             
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_FALSE_POP_CONTINUE', \
                    (':', 0,1), '*n', ('::',1))):
            rpl(cmds,[[('(IF',) + pos__a[2:], [('(IF', Not(pos__b[2])), [('CONTINUE',)], (')ENDIF',)], (')(ELSE',), pos__d,(')ENDIF',)],pos__e])
            return True             
    ## if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*', 'JUMP', (':', 0,1), '*r')):
        ## if type(pos__b) is list:
            ## rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')ENDIF',)],pos__c, pos__d])
        ## else:    
            ## rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')ENDIF',)],pos__c, pos__d])
        ## return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*l', '>', 'JUMP_IF_TRUE', 'POP_TOP',\
                    (':', 0,1), '>', ('::', 3))):
        rpl(cmds,[Or_j_s(And_j_s(pos__a[2], pos__c), pos__g)])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'J_SETUP_LOOP_FOR', 'J_LOOP_VARS', \
                    '*', (':', 2,1), 'POP_BLOCK', '*r', (':', 0,1), '*',(':', 1,1))):
            rpl(cmds,[pos__a, [('(FOR', pos__c[2], pos__b[2]) , pos__d, (')(ELSE',),pos__g, (')ENDFOR',)],pos__h,pos__i,pos__j])
            return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'J_SETUP_LOOP_FOR', 'J_LOOP_VARS', \
                    '*r', (':', 2, 1), 'POP_BLOCK', 'JUMP', (':', 0, 1))) and\
                    pos__g[1] not in (pos__a[1], pos__b[1], pos__c[1]):
            rpl(cmds,[pos__a, [('(FOR', pos__c[2], pos__b[2]) , pos__d, (')ENDFOR',)],pos__g,pos__h])
            return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'J_SETUP_LOOP_FOR', (':', 5,1),\
                    'J_LOOP_VARS', '*n', 'JUMP_CONTINUE', (':', 3,1), \
                    'POP_BLOCK', '*r', (':', 0, 1))):
            rpl(cmds,[pos__a, [('(FOR', pos__d[2], pos__b[2]) , pos__e, (')(ELSE',),pos__i, (')ENDFOR',)],pos__j])
            return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'J_SETUP_LOOP_FOR', (':', 5,1),\
                    'J_LOOP_VARS', '*n', 'JUMP_CONTINUE', (':', 3,1),\
                    'POP_BLOCK', 'JUMP', (':', 0,1))):
            rpl(cmds,[pos__a, [('(FOR', pos__d[2], pos__b[2]) , pos__e, (')ENDFOR',)],pos__i,pos__j])
            return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'J_SETUP_LOOP_FOR', \
                    (':', 6,1), 'J_LOOP_VARS', '*n', 'ju', (':', 4,1),\
                    'POP_BLOCK', 'ju', (':', 0,1))) and pos__c[1] != pos__j[1]:
            rpl(cmds,[pos__a, pos__b+[('(FOR', pos__e[2], pos__c[2]) , pos__f, (')ENDFOR',)],pos__j,pos__k])
            return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'JUMP', (':', 0, 1),\
                    'JUMP_IF2_FALSE_POP_CONTINUE', '*n', ('::', 2))):       #  1
        rpl(cmds,[[('(IF',) +pos__a[2:], pos__b, (')(ELSE',), [('(IF', Not(pos__e[2])), [('CONTINUE',)], (')ENDIF',)] + pos__f, (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP', '*', 'JUMP_CONTINUE', ('::', 0))):
        rpl(cmds,[[('(IF', Not(pos__a[2])), pos__b + [('CONTINUE',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_TRUE_POP', ('::',0))):
        rpl(cmds,[('JUMP_IF2_TRUE_POP', pos__b[1], And_j(pos__a[2], pos__b[2]))])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP', '>', 'JUMP_IF_FALSE', 'POP_TOP', ('::',0))):
        rpl(cmds,[Or_j_s(pos__a[2], pos__b), pos__c,pos__d])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP', '*l', '>', 'JUMP_IF_FALSE', 'POP_TOP', ('::',0))):
        rpl(cmds,[Or_j_s(pos__a[2], pos__c), pos__d,pos__e])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '>', 'JUMP_IF_TRUE', 'POP_TOP',\
                    (':', 0, 1), '*l', '>', ('::', 2))):
        rpl(cmds,[Or_j_s(And_j_s(pos__a[2], pos__b), pos__g)])
        return True
    if SCmp(cmds,i, ('JUMP', 'JUMP_CONTINUE')):
        rpl(cmds,[pos__a])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP_CONTINUE', '*n', ('::',0))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_FALSE_POP', '*n', 'JUMP',\
                    (':', 1,1), '*n', 'JUMP_CONTINUE', (':', (0,3), 2))):
        rpl(cmds,[pos__a,[('(IF',) + pos__b[2:], pos__c, (')(ELSE',),pos__f +[('CONTINUE',)], (')ENDIF',)],pos__h])
        return True
    if  SCmp(cmds,i, ('JUMP_CONTINUE', 'JUMP')):
        rpl(cmds,[pos__a])
        return True
    if  SCmp(cmds,i, ('JUMP', '.:', 'JUMP')) and pos__a[1] == pos__c[1]:
        rpl(cmds,[pos__b,pos__c])
        return True
    if  SCmp(cmds,i, ('JUMP_CONTINUE', '.:', 'JUMP')) and pos__a[1] == pos__c[1]:
        rpl(cmds,[pos__b,pos__a])
        return True
    if  SCmp(cmds,i, ('JUMP', '.:', 'JUMP_CONTINUE')) and pos__a[1] == pos__c[1]:
        rpl(cmds,[pos__b,pos__c])
        return True
    if  SCmp(cmds,i, ('JUMP_CONTINUE', '.:', 'JUMP_CONTINUE')) and pos__a[1] == pos__c[1]:
        rpl(cmds,[pos__b,pos__c])
        return True
    if  SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_TRUE_POP', '*r', \
                        (':', 0,1), '*n', ('::', 1))):
        rpl(cmds,[[('(IF',) + pos__a[2:],[('(IF', Not(pos__b[2])), pos__c, (')ENDIF',)],
                        (')(ELSE',), pos__e, (')ENDIF',)  ]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'JUMP_IF2_FALSE_POP_CONTINUE', ('::', 0))):
            rpl(cmds,[[('(IF',) + pos__a[2:], pos__b + [('(IF', Not(pos__c[2])), [('CONTINUE',)], (')ENDIF',)],\
                            (')ENDIF',)]])
            return True  
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_FALSE_POP_CONTINUE', ('::', 0))):
            rpl(cmds,[[('(IF',) + pos__a[2:], [('(IF', Not(pos__b[2])), [('CONTINUE',)], (')ENDIF',)],\
                            (')ENDIF',)]])
            return True  
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_FALSE_POP_CONTINUE', '*r', ('::', 0))):
            rpl(cmds,[[('(IF',Not(pos__a[2])), [('(IF',) + pos__b[2:], [('CONTINUE',)], (')ENDIF',)] + pos__c,\
                            (')ENDIF',)]])
            return True  
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'JUMP_IF2_TRUE_POP', '*n',\
                    'JUMP_CONTINUE', ('::', (0,2)))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b + [('(IF', Not(pos__c[2])), pos__d+[('CONTINUE',)], (')ENDIF',)],\
                            (')ENDIF',)]])
        return True              
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'J_SETUP_LOOP', ('!', '(IF', '*c', ')ENDIF'),\
                    'POP_BLOCK', 'JUMP', (':', 0,0))):       #  1
        rpl(cmds,[pos__a,[('(WHILE',) + pos__c[0][1:], pos__c[1], (')ENDWHILE',)],pos__e,pos__f])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'J_SETUP_LOOP', ('!', '(IF', '*c', ')ENDIF'),\
                    'POP_BLOCK', '*n', (':', (0,1),0))) and CntJump(pos__f[1],cmds) == 2:       #  1
        rpl(cmds,[pos__a,[('(WHILE',) + pos__c[0][1:], pos__c[1], (')(ELSE',), pos__e, (')ENDWHILE',)],pos__f])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP', 'J_SETUP_LOOP', ('!', '(IF', '*c', ')ENDIF'),\
                    'POP_BLOCK', '*n', (':', (0,1),0))) and CntJump(pos__f[1],cmds) == 2:       #  1
        rpl(cmds,[pos__a,[('(WHILE',) + pos__c[0][1:], pos__c[1], (')(ELSE',), pos__e, (')ENDWHILE',)],pos__f])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n', 'J_SETUP_LOOP', \
                    (':', 5, 1), '*n', 'ju', ('::', 0))):
        rpl(cmds,[[('(IF',) + pos__a[2:],pos__b + [('(WHILE', TRUE), pos__e, (')ENDWHILE',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'J_SETUP_LOOP', \
                    (':', 4, 1), '*n', 'ju', ('::', 0))):
        rpl(cmds,[[('(IF',) + pos__a[2:],[('(WHILE', TRUE), pos__d, (')ENDWHILE',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP', '*l', ('::',0))):
        rpl(cmds,[('UNPUSH', pos__a[2])])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP_CONTINUE', 'JUMP_CONTINUE')) and pos__a[1] == pos__b[1]:
        rpl(cmds,[('UNPUSH', pos__a[2]),pos__b])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'JUMP')) and pos__a[1] == pos__b[1]:
        rpl(cmds,[('UNPUSH', pos__a[2]),pos__b])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_TRUE_POP', \
                    '*n', 'JUMP', (':', 1,1), '*r', (':', 0,1), '*n',\
                    ('::', 3))):
        rpl(cmds,[[('(IF',) + pos__a[2:], \
                            [('(IF',) + pos__b[2:], pos__f,\
                            (')(ELSE',), pos__c, (')ENDIF',)],\
                            (')(ELSE',), pos__h, (')ENDIF',)]])
        return True                    
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP', 'JUMP_IF2_TRUE_POP', \
                    '*n', 'JUMP', (':', 1,1), '*r', (':', 0,1), '*n',\
                    ('::', 3))):
        rpl(cmds,[[('(IF', Not(pos__a[2])), \
                            [('(IF',) + pos__b[2:], pos__f,\
                            (')(ELSE',), pos__c, (')ENDIF',)],\
                            (')(ELSE',), pos__h, (')ENDIF',)]])
        return True                    
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'JUMP_IF2_TRUE_POP', '*r',\
                    (':', 0, 1), '*n', ('::', 2))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b + [('(IF', Not(pos__c[2])), pos__d, (')ENDIF',)], (')(ELSE',), pos__f,(')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'JUMP_IF2_FALSE_POP', '*r',\
                    (':', 0, 1), '*n', ('::', 2))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b + [('(IF',) +pos__c[2:], pos__d, (')ENDIF',)], (')(ELSE',), pos__f, (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'JUMP', (':', 0,1),\
                    'JUMP_IF2_FALSE_POP', '*n', ('::', 2))) and islooplabel(pos__e[1],cmds):       #  1
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')(ELSE',), \
                        [('(IF',) + pos__e[2:], pos__f, (')(ELSE',), [('CONTINUE',)], (')ENDIF',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'jc', (':', 0,1), '*n',\
                    (':', None, 0), ('::',2))) and pos__c[1] != pos__f[1] and pos__a[1] != pos__f[1]:    
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')(ELSE',), pos__e, (')ENDIF',)], ('JUMP_CONTINUE', pos__c[1]), pos__f,('JUMP_CONTINUE', pos__c[1])])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'ju', (':', 0,1), ('::',2))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'JUMP', (':', 0,1), \
                    'JUMP_CONTINUE',  ('::', 2))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')(ELSE',), [('CONTINUE',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_FALSE_POP_CONTINUE', \
                    '*n', 'JUMP', (':', 0,1), '*n', ('::', 3))):
        rpl(cmds,[[('(IF',) + pos__a[2:], \
                        [('(IF',) + pos__b[2:], pos__c, (')(ELSE',), [('CONTINUE',)],(')ENDIF',)],\
                        (')(ELSE',), pos__f, (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'JUMP_IF2_FALSE_POP', 'jc', \
                    (':', 0,1), '*n', ('::', 2))):
        rpl(cmds,[[('(IF',) + pos__a[2:], \
                        pos__b + [('(IF',) + pos__c[2:], [('CONTINUE',)], (')ENDIF',)],(')(ELSE',), pos__f, (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'jc', ('::', 0))):     
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b + [('CONTINUE',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP_CONTINUE', '*r')):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b , (')ENDIF',)], ('JUMP_CONTINUE', pos__a[1])])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'ju', (':', 0,1), \
                    'JUMP_IF2_FALSE_POP_CONTINUE', '*n', ('::', 2))):
        rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')(ELSE',), \
                        [('(IF',) + pos__e[2:], pos__f, (')(ELSE',),[('CONTINUE',)], (')ENDIF',)]]])
        return True
    if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP', 'JUMP_CONTINUE', ('::', 0))):
            rpl(cmds,[('JUMP_IF2_FALSE_POP_CONTINUE', pos__b[1]) + pos__a[2:]])
            return True       
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_FALSE_POP', 'JUMP_IF2_TRUE_POP', \
                    '*r', (':', 1, 1), '*n', ('::', (0,2)))):
            rpl(cmds,[[('(IF',) + pos__a[2:],\
                                [('(IF',) + pos__b[2:],  \
                                [('(IF', Not(pos__c[2])), pos__d, (')ENDIF',)],\
                                (')(ELSE',), pos__f, (')ENDIF',)],\
                            (')ENDIF',)]])
            return True       
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'JUMP_IF2_FALSE_POP', \
                    '*n', 'jc', (':', 0,1), '*n', ('::', 2))) and pos__e[1] not in (pos__f[1],pos__h[1]):
            rpl(cmds,[[('(IF',) + pos__a[2:], pos__b + \
                                [('(IF',) + pos__c[2:], pos__d+ [('CONTINUE',)], (')ENDIF',)], \
                            (')(ELSE',), pos__g, (')ENDIF',)]])
            return True       
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_TRUE_POP', '*n', 'JUMP',\
                    (':', 0,1), '*n', (':', 3,2), ('::',1))):
            rpl(cmds,[[('(IF',) + pos__a[2:], \
                                [('(IF',) + pos__b[2:], [('CONTINUE',)], (')ENDIF',)] + pos__c, \
                            (')(ELSE',), pos__f, (')ENDIF',)], pos__g,pos__h])
            return True       
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', 'JUMP_IF2_TRUE_POP', '*n', 'JUMP',\
                    (':', 0,1), '*n', (':', 3,1), ('::',1))) and pos__b[1] == pos__h[1]:
            rpl(cmds,[[('(IF',) + pos__a[2:], \
                                [('(IF',) + pos__b[2:], [('CONTINUE',)], (')ENDIF',)] + pos__c, \
                            (')(ELSE',), pos__f, (')ENDIF',)], pos__h])
            return True       
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n', 'JUMP', (':', 0,1),\
                    '*n', 'JUMP_CONTINUE', ('::', 2))):            
            rpl(cmds,[[('(IF',) + pos__a[2:], pos__b , (')(ELSE',), pos__e + [('CONTINUE',)], (')ENDIF',)]])
            return True                
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n','xJUMP_IF2_TRUE_POP', '*n', 'JUMP',\
                    (':', 0,1), '*n', (':', 4,2), ('::', 2))):
            rpl(cmds,[[('(IF',) + pos__a[2:], pos__b +\
                                [('(IF',) + pos__c[2:], [('CONTINUE',)], (')ENDIF',)] + pos__d, \
                            (')(ELSE',), pos__g, (')ENDIF',)], pos__h,pos__i])
            return True       
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n','xJUMP_IF2_TRUE_POP', '*n', 'JUMP',\
                    (':', 0,1), '*n', (':', 4,1), ('::', 2))):
            rpl(cmds,[[('(IF',) + pos__a[2:], pos__b +\
                                [('(IF',) + pos__c[2:], [('CONTINUE',)], (')ENDIF',)] + pos__d, \
                            (')(ELSE',), pos__g, (')ENDIF',)],pos__i])
            return True       
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*r', ('::',0))):
            rpl(cmds,[[('(IF',) + pos__a[2:], pos__b, (')ENDIF',)]])
            return True 
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', \
                    'JUMP_IF2_FALSE_POP', '*n', \
                    'JUMP_IF2_FALSE_POP', '*n', \
                    'JUMP_IF2_TRUE_POP', '*r', \
                    (':', 2,1), '*r', \
                    (':', (0, 4, 6), 2), '*r')) and CntJump(pos__k[1],cmds) == 3:
            rpl(cmds,[[('(IF',) + pos__a[2:], pos__b +\
                                [('(IF',) + pos__c[2:], pos__d +\
                                        [('(IF',) + pos__e[2:], pos__f +\
                                            [('(IF', Not(pos__g[2])), pos__h, (')ENDIF',)],\
                                        (')ENDIF',)],\
                                (')(ELSE',), pos__j, \
                                (')ENDIF',)],\
                            (')ENDIF',)] +pos__l])            
            return True    
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n',\
                    'JUMP_IF2_TRUE_POP', \
                    'JUMP_IF2_FALSE_POP', '*n',\
                    'JUMP_IF2_FALSE_POP', 'JUMP_CONTINUE', \
                    (':', 3,1), '*n', \
                    (':', (0,2, 5)))) and CntJump(pos__j[1],cmds) == 3:
            rpl(cmds,[[('(IF',) + pos__a[2:], pos__b +\
                                [('(IF',) + pos__c[2:], [('PASS',)], (')(ELSE',),\
                                        [('(IF',) + pos__d[2:], pos__e +\
                                            [('(IF',) + pos__f[2:], [('CONTINUE',)], (')ENDIF',)],\
                                        (')(ELSE',), pos__i,
                                        (')ENDIF',)],\
                                (')ENDIF',)],\
                            (')ENDIF',)]])           
            return True 
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', \
                    'JUMP_IF2_FALSE_POP', '*n', 'JUMP', \
                    (':', 2,1), '*n', 'JUMP_CONTINUE', \
                    (':', 0,1), '*n', ('::', 4))):
            rpl(cmds,[[('(IF',) + pos__a[2:], pos__b +\
                                [('(IF',) + pos__c[2:], pos__d, (')(ELSE',),
                                        pos__g + [('CONTINUE',)], (')ENDIF',)],\
                                (')(ELSE',), pos__j, (')ENDIF',)]])
            return True 
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '>', 'JUMP_IF_TRUE', 'POP_TOP',\
                    (':', 0,1), 'JUMP_IF2_FALSE_POP', '>', \
                    'JUMP_IF_TRUE', 'POP_TOP', (':', 5,1), '>', \
                    ('::', (2,7)))):
            rpl(cmds,[Or_j_s(And_j_s(pos__a[2],pos__b), Or_j_s(And_j_s(pos__f[2],pos__g),pos__k))])
            return True 
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP_CONTINUE', '*')):
        rpl(cmds,[[('(IF', Not(pos__a[2])), [('CONTINUE',)], (')ENDIF',)]+pos__b])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'RETURN_VALUE', ('::',0))) and len(pos__b) == 2:
        rpl(cmds,[[('(IF', pos__a[2]), [pos__b], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_TRUE_POP', '*n',\
                    'xJUMP_IF2_TRUE_POP_CONTINUE', ('::', 0))):
        rpl(cmds,[[('(IF', Not(pos__a[2])), pos__b + [('(IF', pos__c[2]), [('CONTINUE',)], (')ENDIF',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_TRUE_POP',\
                    'xJUMP_IF2_TRUE_POP_CONTINUE', ('::', 0))):
        rpl(cmds,[[('(IF', Not(pos__a[2])), [('(IF', pos__c[2]), [('CONTINUE',)], (')ENDIF',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_TRUE_POP', '*n', 'JUMP', (':', 0,1),\
                    '*n', 'JUMP_CONTINUE', ('::', 2))):
        rpl(cmds,[[('(IF', Not(pos__a[2])), pos__b, (')(ELSE',), pos__e + [('CONTINUE',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_TRUE_POP', 'JUMP', (':', 0,1),\
                    '*n', 'JUMP_CONTINUE', ('::', 1))):
        rpl(cmds,[[('(IF', pos__a[2]), pos__e + [('CONTINUE',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_TRUE_POP', '*n', 'JUMP', (':', 0,1),\
                    'JUMP_CONTINUE', ('::', 2))):
        rpl(cmds,[[('(IF', Not(pos__a[2])), pos__b, (')(ELSE',), [('CONTINUE',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_TRUE_POP', 'JUMP', (':', 0,1),\
                    'JUMP_CONTINUE', ('::', 1))):
        rpl(cmds,[[('(IF', pos__a[2]), [('CONTINUE',)], (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n', 'xJUMP_IF2_TRUE_POP', '*r',\
                    (':', 0,1), '*r', ('::', 2))):
        rpl(cmds,[[('(IF', pos__a[2]), pos__b + [('(IF', Not(pos__c[2])), pos__d, (')ENDIF',)], (')(ELSE',), pos__f , (')ENDIF',)]])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'xJUMP_IF2_TRUE_POP', '*r',\
                    (':', 0,1), '*r', ('::', 1))):
        rpl(cmds,[[('(IF', pos__a[2]), [('(IF', Not(pos__b[2])), pos__c, (')ENDIF',)], (')(ELSE',), pos__e , (')ENDIF',)]])
        return True    
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n', 'JUMP', (':', 0, 1),\
                    'xJUMP_IF2_TRUE_POP_CONTINUE', (':', 2,1), '*n', \
                    ('::', 4))):
        rpl(cmds,[[('(IF', pos__a[2]), pos__b, (')(ELSE',), [('(IF', pos__e[2]), [('CONTINUE',)], (')ENDIF',)]+pos__g, (')ENDIF',)]])
        return True    
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'JUMP', (':', 0, 1),\
                    'xJUMP_IF2_TRUE_POP_CONTINUE', (':', 1,1), '*n', \
                    ('::', 3))):
        rpl(cmds,[[('(IF', Not(pos__a[2])),[('(IF', pos__d[2]), [('CONTINUE',)], (')ENDIF',)]+pos__f, (')ENDIF',)]])
        return True    
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n', 'JUMP', (':', 0, 1),\
                    'xJUMP_IF2_TRUE_POP_CONTINUE', (':', 2,1), \
                    ('::', 4))):
        rpl(cmds,[[('(IF', pos__a[2]), pos__b, (')(ELSE',), [('(IF', pos__e[2]), [('CONTINUE',)], (')ENDIF',)], (')ENDIF',)]])
        return True    
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'JUMP', (':', 0, 1),\
                    'xJUMP_IF2_TRUE_POP_CONTINUE', (':', 1,1), \
                    ('::', 3))):
        rpl(cmds,[[('(IF', Not(pos__a[2])),[('(IF', pos__d[2]), [('CONTINUE',)], (')ENDIF',)], (')ENDIF',)]])
        return True    
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'xJUMP_IF2_FALSE_POP', '*n',\
                    'ju', (':', 0, 1), '*n', (':', 1, 1),\
                    '*n', ('::', 3))):
        rpl(cmds,[[('(IF', pos__a[2]),[('(IF', pos__b[2]), pos__c, (')(ELSE',), pos__h, (')ENDIF',)], (')(ELSE',), pos__f, (')ENDIF',)]])
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'xJUMP_IF2_FALSE_POP', \
                    'ju', (':', 0, 1), '*n', (':', 1, 1),\
                    '*n', ('::', 2))):
        pos__c,pos__d,pos__e,pos__f,pos__g,pos__h,pos__i = [('PASS',)],pos__c,pos__d,pos__e,pos__f,pos__g,pos__h                
        rpl(cmds,[[('(IF', pos__a[2]),[('(IF', pos__b[2]), pos__c, (')(ELSE',), pos__h, (')ENDIF',)], (')(ELSE',), pos__f, (')ENDIF',)]])
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n', 'JUMP', (':', 0,1),\
                    '*n', 'JUMP_CONTINUE')) and pos__c[1] not in (pos__a[1], pos__d[1], pos__f[1]):
        rpl(cmds,[[('(IF', pos__a[2]), pos__b, (')(ELSE',), pos__e + [('CONTINUE',)], (')ENDIF',)], pos__c])
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n', 'JUMP', (':', 0,1),\
                    'JUMP_CONTINUE')) and pos__c[1] not in (pos__a[1], pos__d[1], pos__e[1]):
        rpl(cmds,[[('(IF', pos__a[2]), pos__b, (')(ELSE',), [('CONTINUE',)], (')ENDIF',)], pos__c])
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'JUMP', (':', 0,1),\
                    '*n', 'JUMP_CONTINUE')) and pos__b[1] not in (pos__a[1], pos__c[1], pos__e[1]):
        rpl(cmds,[[('(IF', pos__a[2]), [('PASS',)], (')(ELSE',), pos__d + [('CONTINUE',)], (')ENDIF',)], pos__b])
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'JUMP', (':', 0,1),\
                    'JUMP_CONTINUE')) and pos__b[1] not in (pos__a[1], pos__c[1], pos__d[1]):
        rpl(cmds,[[('(IF', pos__a[2]), [('PASS',)], (')(ELSE',), [('CONTINUE',)], (')ENDIF',)], pos__b])
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_TRUE_POP_CONTINUE', 'xJUMP_IF2_FALSE_POP', \
                    'JUMP_CONTINUE')) and pos__a[1] == pos__c[1]:
        rpl(cmds,[[('(IF', Or_j(pos__a[2], pos__b[2])), [('CONTINUE',)], (')ENDIF',)], ('JUMP', pos__b[1])])
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n', 'JUMP_CONTINUE')):
        rpl(cmds,[[('(IF', pos__a[2]), pos__b + [('CONTINUE',)], (')ENDIF',)], ('JUMP', pos__a[1])])
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n', 'JUMP', (':', 0,1), '*r', \
                    '.:')) and pos__c[1] != pos__f[1]:
        rpl(cmds,[[('(IF', pos__a[2]), pos__b , (')(ELSE',), pos__e, (')ENDIF',)], pos__c,pos__f])
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n', 'JUMP', (':', 0,1), '*n',\
                    'jc', ('::', 2))):
        rpl(cmds,[[('(IF', pos__a[2]), pos__b , (')(ELSE',), pos__e + [('CONTINUE',)], (')ENDIF',)]])
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'xJUMP_IF2_FALSE_POP', '**n', \
                    'xJUMP_IF2_FALSE_POP', 'JUMP_CONTINUE', (':', 0, 1), \
                    '**n', ('::', (1, 3)))):
        rpl(cmds,[[('(IF', pos__a[2]), [('(IF', pos__b[2]), \
                                      pos__c + [('(IF', pos__d[2]), [('CONTINUE',)], (')ENDIF',)], \
                                      (')ENDIF',)],\
                      (')(ELSE',), pos__g, (')ENDIF',)]])                
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '**n', 'xJUMP_IF2_FALSE_POP', '**n', \
                    'xJUMP_IF2_FALSE_POP', 'JUMP_CONTINUE', (':', 0, 1), \
                    '**n', ('::', (2, 4)))):
        rpl(cmds,[[('(IF', pos__a[2]), pos__b + [('(IF', pos__c[2]), \
                                      pos__d + [('(IF', pos__e[2]), [('CONTINUE',)], (')ENDIF',)], \
                                      (')ENDIF',)],\
                      (')(ELSE',), pos__h, (')ENDIF',)]])                
        return True  
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '**n', 'xJUMP_IF2_FALSE_POP', '**n', \
                    'xJUMP_IF2_FALSE_POP', '**n', 'JUMP_CONTINUE', (':', 0, 1), \
                    '**n', ('::', (2, 4)))):
        rpl(cmds,[[('(IF', pos__a[2]), pos__b + [('(IF', pos__c[2]), \
                                      pos__d + [('(IF', pos__e[2]), pos__f + [('CONTINUE',)], (')ENDIF',)], \
                                      (')ENDIF',)],\
                      (')(ELSE',), pos__i, (')ENDIF',)]])                
        return True  
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*r', (':', None,0), 'END_FINALLY', ('::', 0))):
        rpl(cmds,[[('(IF', pos__a[2]), pos__b, (')ENDIF',)], pos__c,pos__d])
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_TRUE_POP', '*r', '.:', '*n', (':', 0, 0))):
        rpl(cmds,[[('(IF', Not(pos__a[2])), pos__b, (')ENDIF',)], ('JUMP', pos__a[1]), pos__c,pos__d,pos__e])
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '(BEGIN_TRY', '*n', ')END_BEGIN_TRY',\
                    'J_IF_NO_EXCEPT_IN_TRY', '*e', 'J_AFTER_EXCEPT_HANDLE', \
                    'END_FINALLY', (':', 4, 1), '*r', (':', 0, 1), '*r', ('::', 6))):
                rpl(cmds,[[('(IF', pos__a[2]), concatenate_try_except(pos__c,pos__f, pos__j), (')(ELSE',), pos__l, (')ENDIF',)]])
                return True 
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '(BEGIN_TRY', '*n', ')END_BEGIN_TRY',\
                    'J_IF_NO_EXCEPT_IN_TRY', '*e', 'J_AFTER_EXCEPT_HANDLE', \
                    'END_FINALLY', (':', 4, 1), '*r', (':', 0, 1), '*n', ('::', 6))):
                rpl(cmds,[[('(IF', pos__a[2]), concatenate_try_except(pos__c,pos__f, pos__j), (')(ELSE',), pos__l, (')ENDIF',)]])
                return True                     
    if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP', '*n', 'JUMP_CONTINUE', (':', 0, 1),\
                    '*n', 'JUMP_CONTINUE')) and pos__c[1] == pos__f[1]:
        rpl(cmds,[[('(IF', pos__a[2]), pos__b , (')(ELSE',), pos__e , (')ENDIF',)], pos__f])
        return True   
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '(BEGIN_TRY', '*n', ')END_BEGIN_TRY',\
                    'J_IF_NO_EXCEPT_IN_TRY', '*e', 'J_AFTER_EXCEPT_HANDLE', \
                    'END_FINALLY', 'JUMP', (':', 0,None))) and pos__e[1] == pos__i[1]:
        rpl(cmds,[pos__a, concatenate_try_except(pos__c, pos__f),pos__j])
        return True                    
    if SCmp(cmds,i, ('xJUMP_IF2_TRUE_POP', '**n', 'J_SETUP_LOOP_FOR', (':', 6,1),\
                    'J_LOOP_VARS', '**n', 'JUMP_CONTINUE', (':', 4, 1),\
                    'POP_BLOCK', 'JUMP', (':', 0,1), '*n', (':', 2,1),\
                    'JUMP')):
        cmds[i:i+9] = [pos__a,pos__b+[('(FOR', pos__e[2], pos__c[2]), pos__f[:], (')ENDFOR',)]]
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'J_SETUP_LOOP_FOR', (':', 5, 1),\
                    'J_LOOP_VARS', '*n', 'JUMP_CONTINUE', (':', 3, 1),\
                    'POP_BLOCK', '*n', 'JUMP_CONTINUE', (':', 0, 1), '*n',\
                    (':', 1,1), ('::', 9))):
        rpl(cmds,[pos__a, [('(FOR', pos__d[2], pos__b[2]), pos__e[:], (')(ELSE',), pos__i,(')ENDFOR',)],pos__j,pos__k,pos__l,cmds[i+12]])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_TRUE_POP', 'J_SETUP_LOOP_FOR', (':', 5, 1),\
                    'J_LOOP_VARS', '*n', 'JUMP_CONTINUE', (':', 3, 1),\
                    'POP_BLOCK', 'JUMP_CONTINUE', (':', 0, 0))) and \
                    pos__i[1] not in (pos__a[1], pos__b[1], pos__d[1], pos__f[1]):
        rpl(cmds,[pos__a, [('(FOR', pos__d[2], pos__b[2]), pos__e[:], (')ENDFOR',)],pos__i,pos__j])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n', 'J_SETUP_LOOP', \
                    ('!', '(IF', '*c', ')ENDIF'), 'POP_BLOCK', '*n', \
                    'JUMP_CONTINUE', (':', 0,0))) and pos__c[1] != pos__a[1] != pos__g[1]:
        rpl(cmds,[pos__a, pos__b + [('(WHILE',) + pos__d[0][1:], pos__d[1][:-1], (')(ELSE',), pos__f, (')ENDWHILE',)],pos__g,pos__h])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_TRUE_POP', '*n', 'J_SETUP_LOOP_FOR', \
                    (':', 6, 1), 'J_LOOP_VARS', '*n', 'JUMP_CONTINUE', \
                    (':', 4, 1), 'POP_BLOCK', 'JUMP_CONTINUE', (':', 0, 0))) and \
                    pos__a[1] != pos__c[1] != pos__j[1]:
        rpl(cmds,[pos__a, pos__b +[('(FOR', pos__e[2], pos__c[2]), pos__f[:], (')ENDFOR',)],pos__j, pos__k])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n', 'J_SETUP_LOOP', \
                    ('!', '(IF', '*r', ')ENDIF'), 'POP_BLOCK',  ('::', (0,2)))):
        rpl(cmds,[pos__a, pos__b + [('(WHILE',) + pos__d[0][1:], pos__d[1][:-1], (')ENDWHILE',)],pos__f])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '*n', 'J_SETUP_LOOP', \
                    ('!', '(IF', '*r', ')ENDIF'), 'POP_BLOCK', 'JUMP', (':', 0, 0))) and\
                    pos__a[1] != pos__c[1] and pos__a[1] != pos__f[1]:
            rpl(cmds,[pos__a,pos__b+[('(WHILE',) + pos__d[0][1:], pos__d[1], (')ENDWHILE',)],pos__f,pos__g])
            return True       
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', '>', 'JUMP', ('::', 0))) and pos__c[1] != pos__d[1]:
        rpl(cmds,[('J_COND_PUSH', pos__c[1], pos__a[2], cmd2mem(pos__b))])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'J_COND_PUSH', (':', 0, 1),\
                    '>', ('::', 1))):
        rpl(cmds,[('!COND_EXPR', pos__a[2], ('!COND_EXPR',) + pos__b[2:] + (cmd2mem(pos__d),), cmd2mem(pos__d))])
        return True
    if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'J_SETUP_LOOP_FOR', (':', 5, 1),\
                    'J_LOOP_VARS', '*n', 'JUMP_CONTINUE', (':', 3, 1), \
                    'POP_BLOCK', '*n', 'JUMP', ('::', 0))) and pos__b[1] != pos__j[1] and \
                    pos__b[1] not in (pos__a[1],pos__c[1], pos__d[1]):       #  1
        rpl(cmds,[pos__a, [('(FOR', pos__d[2], pos__b[2]), pos__e[:], (')(ELSE',), pos__i,(')ENDFOR',)],pos__j,pos__k])
        return True
    if added_pass:
        if SCmp(cmds,i, ('xJUMP_IF2_TRUE_POP_CONTINUE',)):
            rpl(cmds,[[('(IF', pos__a[2]), [('CONTINUE',)], (')ENDIF',)]])
            return True   
        if SCmp(cmds,i, ('JUMP_IF2_TRUE_POP',)) and islooplabel(pos__a[1],cmds):
            rpl(cmds,[('JUMP_IF2_TRUE_POP_CONTINUE',) + pos__a[1:]])
            return True   
        if SCmp(cmds,i, ('JUMP_IF2_FALSE_POP',)) and islooplabel(pos__a[1],cmds):
            rpl(cmds,[('JUMP_IF2_FALSE_POP_CONTINUE',) + pos__a[1:]])
            return True   
        if SCmp(cmds,i, ('JUMP',)) and islooplabel(pos__a[1],cmds):
            rpl(cmds,[('JUMP_CONTINUE',) + pos__a[1:]])
            return True   
        if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'xJUMP_IF2_FALSE_POP', 'JUMP_CONTINUE', \
                    (':', 0,0), '*n', (':', 1,0))):
            rpl(cmds,[pos__a,[('(IF', pos__b[2]), [('CONTINUE',)], (')ENDIF',)],('JUMP', pos__b[1]), pos__d,pos__e,pos__f])
            return True           
        if SCmp(cmds,i, ('xJUMP_IF2_FALSE_POP', 'JUMP_CONTINUE', '.:')) and pos__a[1] != pos__b[1] != pos__c[1]: 
            rpl(cmds,[[('(IF', pos__a[2]), [('CONTINUE',)], (')ENDIF',)],('JUMP', pos__a[1]),pos__c])
            return True           
    return False

def process_j_setup_loop_for(cmds,i):
    global pos__a,pos__b,pos__c,pos__d,pos__e,pos__f,pos__g,pos__h,pos__i,pos__j,pos__k,pos__l

    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':',4,1), 'J_LOOP_VARS', '*', 'ju',
                        (':',2,1), 'POP_BLOCK', ('::',0))):
        rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]), pos__d[:], (')ENDFOR',)]])
        return True 
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', 'J_LOOP_VARS', '*', (':',1,1), 'POP_BLOCK',\
                    'JUMP')) and pos__a[1] == pos__f[1]:
        rpl(cmds,[[('(FOR', pos__b[2], pos__a[2]), pos__c[:], (')ENDFOR',)],pos__f])
        return True
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':',4,1), 'J_LOOP_VARS', '*n',\
                    'ju', (':',2,1), 'POP_BLOCK', '*n', 'jc', ('::',0)))and\
                    pos__i[1] != pos__e[1]:
            rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]), pos__d[:], (')(ELSE',), pos__h + [('CONTINUE',)],(')ENDFOR',)]])
            return True 
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', 'J_LOOP_VARS', '*', (':', 1, 1),\
                    'POP_BLOCK', ('::',0))):
        rpl(cmds,[[('(FOR', pos__b[2], pos__a[2]), pos__c[:], (')ENDFOR',)]])
        return True
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 3,0), 'J_LOOP_VARS',\
                    'xJUMP_IF2_FALSE_POP_CONTINUE', '*r')):
            rpl(cmds,[pos__a,pos__b,pos__c,[('(IF',) + pos__d[2:], pos__e, (')ENDIF',)], ('JUMP_CONTINUE',pos__d[1])])
            return True
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 3,0), 'J_LOOP_VARS',\
                    'xJUMP_IF2_FALSE_POP', '*r')):
            rpl(cmds,[pos__a,pos__b,pos__c,[('(IF',) + pos__d[2:], pos__e, (')ENDIF',)], ('JUMP',pos__d[1])])
            return True
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', 'J_LOOP_VARS', '*', (':',1,1), 'POP_BLOCK', ('::', 0))):
            rpl(cmds,[[('(FOR', pos__b[2], pos__a[2]) , pos__c, (')ENDFOR',)]])
            return True 
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 3, 2), 'J_LOOP_VARS', \
                    'xJUMP_IF2_TRUE_POP_CONTINUE', '*', 'JUMP_CONTINUE', \
                    (':', 2, 1), 'POP_BLOCK', ('::', 0))) and pos__d[1] == pos__f[1]:
            rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]) , [('(IF',) +pos__d[2:],\
                                                    [('CONTINUE',)],(')ENDIF',)]+ pos__e, (')ENDFOR',)]])
            return True
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 3, 1), 'J_LOOP_VARS', \
                    'JUMP_CONTINUE', (':', 2, 1), 'POP_BLOCK', ('::', 0))):
            rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]) , [('PASS',)], (')ENDFOR',)]])
            return True
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', 'J_LOOP_VARS', '*n', (':', 1,1),\
                    'POP_BLOCK', '*r', ('::', 0))):
            rpl(cmds,[[('(FOR', pos__b[2], pos__a[2]) , pos__c, (')(ELSE',),pos__f, (')ENDFOR',)]])
            return True
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,1), 'J_LOOP_VARS', '*n',\
                    'xJUMP_IF2_FALSE_POP_CONTINUE', '*n', (':', 2, 1),\
                    'POP_BLOCK', ('::', 0))):       #  1
            rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]) , \
                            pos__d + [('(IF',) + pos__e[2:], pos__f, (')ENDIF',)], \
                            (')ENDFOR',)]])
            return True
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,2), 'J_LOOP_VARS', '*n',\
                    'xJUMP_IF2_FALSE_POP_CONTINUE', '*n', 'JUMP_CONTINUE')):       
            rpl(cmds,[pos__a,pos__b,pos__c,pos__d + [('(IF',) +pos__e[2:], pos__f, (')ENDIF',)], pos__g])
            return True
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 3, 2), 'J_LOOP_VARS', \
                     'xJUMP_IF2_TRUE_POP')):
            if type(cmds[i+4]) is list:
                cmds[i:i+5] = [pos__a,pos__b,pos__c, [('(IF',) +pos__d[2:], [('CONTINUE',)], (')ENDIF',)]+cmds[i+4]]
            else:          
                cmds[i:i+4] = [pos__a,pos__b,pos__c, [('(IF',) +pos__d[2:], [('CONTINUE',)], (')ENDIF',)]]
            return True
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 3,1), 'J_LOOP_VARS', \
                     'xJUMP_IF2_TRUE_POP')):
            if type(cmds[i+4]) is list:
                cmds[i:i+5] = [pos__a,pos__c, [('(IF',) +pos__d[2:], [('CONTINUE',)], (')ENDIF',)]+cmds[i+4]]
            else:                 
                cmds[i:i+4] = [pos__a,pos__c, [('(IF',) +pos__d[2:], [('CONTINUE',)], (')ENDIF',)]]
            return True
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,2), 'J_LOOP_VARS', '*n',\
                    'xJUMP_IF2_FALSE_POP_CONTINUE', '*n')):       
            rpl(cmds,[pos__a,pos__b,pos__c,pos__d+ [('(IF', Not(pos__e[2])), [('CONTINUE',)], (')ENDIF',)]+pos__f])
            return True
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,0), 'J_LOOP_VARS', '*n', 'JUMP')):
        rpl(cmds,[pos__a,pos__b,pos__c,pos__d,('JUMP_CONTINUE',) + pos__e[1:]])
        return True
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', 'J_LOOP_VARS', '*r', (':', 1,1),\
                    'POP_BLOCK', '*n', ('::', 0))):
        rpl(cmds,[[('(FOR', pos__b[2], pos__a[2]), pos__c[:], (')(ELSE',),pos__f,(')ENDFOR',)]])
        return True    
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,1), 'J_LOOP_VARS', '*n',\
                    'JUMP_CONTINUE', (':', 2,1), 'POP_BLOCK', '*n', ('::', 0))):
        rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]), pos__d[:], (')(ELSE',),pos__h,(')ENDFOR',)]])
        return True    
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,1), 'J_LOOP_VARS', '*n',\
                    'ju', (':', 2,1), 'POP_BLOCK', '*r', ('::', 0))):
        rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]), pos__d[:], (')(ELSE',),pos__h,(')ENDFOR',)]])
        return True    
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4, 1), 'J_LOOP_VARS', '*n', 'ju',\
                    (':', 2,1), 'POP_BLOCK', '*n', 'ju')) and pos__a[1] == pos__i[1]:
        rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]), pos__d[:], (')(ELSE',),pos__h,(')ENDFOR',)],pos__i])
        return True    
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,1), 'J_LOOP_VARS', '*n',\
                    'JUMP_CONTINUE', (':', 2, 1), 'POP_BLOCK', 'JUMP')) and pos__h[1] == pos__a[1]:
        rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]), pos__d[:], (')ENDFOR',)],pos__h])
        return True  
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,1), 'J_LOOP_VARS', '*n',\
                    'JUMP_CONTINUE', (':', 2, 1), 'POP_BLOCK', 'JUMP_CONTINUE')) and pos__h[1] == pos__a[1]:
        rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]), pos__d[:], (')ENDFOR',)],pos__h])
        return True  
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,1), 'J_LOOP_VARS', '*n',\
                    'JUMP_CONTINUE', (':', 2,1), 'POP_BLOCK', 'jc',\
                    ('::', 0))) and pos__h[1] not in (pos__b[1],pos__f[1],pos__i[1]):
        rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]), pos__d[:], (')(ELSE',), [('CONTINUE',)],(')ENDFOR',)]])
        return True  
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,1), 'J_LOOP_VARS', '*n',\
                    'JUMP_CONTINUE', (':', 2,1), 'POP_BLOCK', 'ju', \
                    '.:', 'END_FINALLY', ('::', 0))) and \
                    pos__h[1] not in (pos__a[1], pos__b[1],pos__c[1],pos__e[1],pos__f[1]) and\
                    pos__i[1] not in (pos__a[1], pos__b[1],pos__c[1],pos__e[1],pos__f[1]):
        rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]), pos__d[:], (')ENDFOR',)],pos__h,pos__i,pos__j])
        return True  
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,1), 'J_LOOP_VARS', '*n',\
                    'JUMP_CONTINUE', (':', 2, 1), 'POP_BLOCK', '*r',\
                    '.:', 'END_FINALLY', ('::', 0))) and pos__i[1] not in [pos__b[1], pos__f[1],pos__k[1]]:
        rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]), pos__d[:], (')(ELSE',), pos__h,(')ENDFOR',)],pos__i,pos__j])
        return True         
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', 'J_LOOP_VARS', '*r', (':', 1,1), \
                    'POP_BLOCK', '*r', ('::', 0))):
        rpl(cmds,[[('(FOR', pos__b[2], pos__a[2]), pos__c[:], (')(ELSE',), pos__f,(')ENDFOR',)]])
        return True         
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', 'J_LOOP_VARS', '*r', (':', 1,1),\
                    'POP_BLOCK', 'JUMP_CONTINUE')) and pos__a[1] == pos__f[1]:
        rpl(cmds,[[('(FOR', pos__b[2], pos__a[2]), pos__c[:], (')ENDFOR',)],pos__f])
        return True        
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', 'J_LOOP_VARS', '*r', (':', 1,1),\
                    'POP_BLOCK', 'JUMP')) and pos__a[1] == pos__f[1]:
        rpl(cmds,[[('(FOR', pos__b[2], pos__a[2]), pos__c[:], (')ENDFOR',)],pos__f])
        return True   
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,1), 'J_LOOP_VARS', '*n',\
                    'JUMP_CONTINUE', (':', 2,1), 'POP_BLOCK', '*r', '.:')) \
                    and pos__i[1] != pos__a[1]:
        rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]), pos__d[:], (')(ELSE',), pos__h, (')ENDFOR',)],pos__i])
        return True   
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,2), 'J_LOOP_VARS', '*n',\
                    'xJUMP_IF2_TRUE_POP')):
        rpl(cmds,[pos__a,pos__b,pos__c,pos__d,('JUMP_IF2_TRUE_POP_CONTINUE',)+pos__e[1:]])
        return True   
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4,1), 'J_LOOP_VARS', '*n',\
                    'xJUMP_IF2_TRUE_POP')):
        rpl(cmds,[pos__a,pos__c,pos__d,('JUMP_IF2_TRUE_POP_CONTINUE',)+pos__e[1:]])
        return True       
    if SCmp(cmds,i, ('J_SETUP_LOOP_FOR', (':', 4, 1), 'J_LOOP_VARS', '*n', \
                    'JUMP_CONTINUE', (':', 2, 1), 'POP_BLOCK', '*r',\
                    'END_FINALLY', ('::', 0))):
        rpl(cmds,[[('(FOR', pos__c[2], pos__a[2]), pos__d[:], (')(ELSE',), pos__h, (')ENDFOR',)],pos__i])
        return True   
    return False

def process_begin_try(cmds,i):
    global pos__a,pos__b,pos__c,pos__d,pos__e,pos__f,pos__g,pos__h,pos__i,pos__j,pos__k,pos__l

    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', '*', 'JUMP_CONTINUE', (':', 4, 1),\
                    'END_FINALLY', (':', 3, 1), '*r')):
             rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], pos__f, (')(ELSE',),pos__k, (')ENDTRY',)],pos__g])
             return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', '*', 'JUMP', (':', 4, 1),\
                    'END_FINALLY', (':', 3, 1), '*r')) and pos__g[1] not in (pos__d[1],pos__e[1]):
             rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], pos__f, (')(ELSE',),pos__k, (')ENDTRY',)],pos__g])
             return True      
    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', 'JUMP', (':', 4, 1), 'END_FINALLY',\
                    (':', 3, 1), '*r', ('::', 5))):
             rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], [('PASS',)], (')(ELSE',),pos__j, (')ENDTRY',)]])
             return True      
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY',\
                    'JUMP_IF_NOT_EXCEPTION_POP', '*n', 'JUMP', (':', 4,1), 'END_FINALLY',\
                    (':', 3, 1), '*n', ('::', 6))):
             rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], pos__f, (')(ELSE',),pos__k, (')ENDTRY',)]])
             return True      
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', 'JUMP', (':', 4, 1), 'END_FINALLY',\
                    (':', 3, 1), '*n', ('::', 5))):
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], [('PASS',)], (')(ELSE',),pos__j, (')ENDTRY',)]])
                return True 
                  
    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', 'JUMP', (':', 4, 1),\
                    'END_FINALLY', ('::', (3,5)))):
             rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], [('PASS',)],(')ENDTRY',)]])
             return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', 'JUMP', (':', 3, 1),\
                    'END_FINALLY', ('::', 4))):
             rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__d[2:], [('PASS',)],(')ENDTRY',)]])
             return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', '*', 'JUMP', (':', 4, 1),\
                    'END_FINALLY', ('::', (3,6)))):
            rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], pos__f, (')ENDTRY',)]])
            return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*l', 'POP_TOP3', '*', 'JUMP', 'END_FINALLY', ('::', (3,7)))):
            rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',), pos__g, (')ENDTRY',)]])
            return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*l', 'POP_TOP3', 'JUMP', 'END_FINALLY', ('::', (3,6)))):
            rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',), [('PASS',)], (')ENDTRY',)]])
            return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'POP_TOP3', '*n', 'END_FINALLY', ('::', 3))):
            rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',), pos__f, (')ENDTRY',)]])
            return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'JUMP_IF_NOT_EXCEPTION_POP', \
                    '*', 'JUMP', (':', 3, 1), 'END_FINALLY', ('::', 5))):
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__d[2:], pos__e, (')ENDTRY',)]])
                return True               
    ## if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'JUMP_IF_NOT_EXCEPTION_POP',\ # By CloneDigger
                    ## 'JUMP', (':', 3, 1), 'END_FINALLY', ('::', 4))):
                ## rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__d[2:], [('PASS',)], (')ENDTRY',)]])
                ## return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'JUMP_IF_NOT_EXCEPTION_POP', \
                    '*', 'JUMP', (':', 3, 1), 'END_FINALLY', 'JUMP')) and pos__f[1] == pos__i[1]:
             rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__d[2:], pos__e, (')ENDTRY',)],pos__i])
             return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'JUMP_IF_NOT_EXCEPTION_POP', \
                    'JUMP', (':', 3,1), 'END_FINALLY', 'JUMP')) and pos__e[1] == pos__h[1]:
             rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__d[2:], [('PASS',)], (')ENDTRY',)],pos__h])
             return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'JUMP_IF_NOT_EXCEPTION_POP', \
                    '*r', (':', 3,1), 'END_FINALLY')):         
             rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__d[2:], pos__e, (')ENDTRY',)]])
             return True     
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY',\
                    'JUMP_IF_NOT_EXCEPTION_POP', '*r', (':', 4, 1), 'END_FINALLY',\
                    (':', 3,1), '*n', 'JUMP')) and pos__k[1] not in(pos__d[1],pos__e[1]):
             rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], pos__f, (')(ELSE',),pos__j, (')ENDTRY',)],pos__k])
             return True     
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY',\
                    'JUMP_IF_NOT_EXCEPTION_POP', '*r', (':', 4, 1), 'END_FINALLY',\
                    ('::', 3))):
             rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], pos__f, (')ENDTRY',)]])
             return True     
    if SCmp(cmds,i, ('(BEGIN_TRY', ('!', 'PASS'), ')END_BEGIN_TRY',\
                    'J_IF_NO_EXCEPT_IN_TRY', 'J_AFTER_EXCEPT_HANDLE', \
                    'END_FINALLY', (':', 3,1), '*n', ('::', 4))):
             rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',), [('PASS',)],(')(ELSE',),pos__h, (')ENDTRY',)]])
             return True     
    if SCmp(cmds,i, ('(BEGIN_TRY', ('!', 'PASS'), ')END_BEGIN_TRY',\
                    'J_IF_NO_EXCEPT_IN_TRY', 'J_AFTER_EXCEPT_HANDLE', \
                    'END_FINALLY', ('::', (3,4)))):
             rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',), [('PASS',)],(')ENDTRY',)]])
             return True     
    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', 'JUMP_CONTINUE', \
                    (':', 4,1), 'END_FINALLY', (':', 3,1), '*n', 'JUMP_CONTINUE')) and pos__f[1] == pos__k[1]:
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], [('CONTINUE',)], (')(ELSE',),pos__j, (')ENDTRY',)],pos__k])
                return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', 'JUMP_CONTINUE', \
                    (':', 4,1), 'END_FINALLY', (':', 3,1), '*n', 'JUMP')) and pos__f[1] == pos__k[1]:
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], [('CONTINUE',)], (')(ELSE',),pos__j, (')ENDTRY',)],pos__k])
                return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'END_FINALLY', ('::', 3))):
            rpl(cmds,[concatenate_try_except(pos__b, pos__e)])
            return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', '*', 'JUMP', (':', 4, 1),\
                    'END_FINALLY', 'JUMP')) and pos__d[1] == pos__g[1] and pos__d[1] == pos__j[1]:
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], pos__f, (')ENDTRY',)],pos__g])
                return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', '*', 'JUMP_CONTINUE', (':', 4, 1),\
                    'END_FINALLY', 'JUMP_CONTINUE')) and pos__d[1] == pos__g[1] and pos__d[1] == pos__j[1]:
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], pos__f, (')ENDTRY',)],pos__g])
                return True               
    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', 'JUMP_CONTINUE', (':', 4, 1),\
                    'END_FINALLY', 'JUMP_CONTINUE')) and pos__d[1] == pos__f[1] and pos__d[1] == pos__i[1]:
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], [('PASS',)], (')ENDTRY',)],pos__f])
                return True 
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', \
                    'J_IF_NO_EXCEPT_IN_TRY', '*e',\
                    'J_AFTER_EXCEPT_HANDLE_CONTINUE', 'END_FINALLY',\
                    'JUMP_CONTINUE')) and\
                    pos__d[1] == pos__f[1] and pos__d[1] == pos__h[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__e), pos__h])
                return True 
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', \
                    'J_IF_NO_EXCEPT_IN_TRY', '*e',\
                    'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY',\
                    '.:', 'ju')) and\
                    pos__d[1] == pos__f[1] and pos__d[1] == pos__i[1] and pos__h[1] not in (pos__d[1], pos__f[1], pos__i[1]):
                rpl(cmds,[concatenate_try_except(pos__b,pos__e), pos__h, pos__i])
                return True             
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', \
                    'J_IF_NO_EXCEPT_IN_TRY', '*e',\
                    'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY',\
                    'ju')) and\
                    pos__d[1] == pos__f[1] and pos__d[1] == pos__h[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__e), pos__h])
                return True 
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', \
                    'J_IF_NO_EXCEPT_IN_TRY', '*e',\
                    'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY',\
                    ('::', (3,5)))):
           rpl(cmds,[concatenate_try_except(pos__b,pos__e)])
           return True 
    ## if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \ # By CloneDigger
                    ## 'JUMP_IF_NOT_EXCEPTION_POP', '*r', (':', 4, 1), 'END_FINALLY',\
                    ## ('::', 3))):
                ## rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], pos__f, (')ENDTRY',)]])
                ## return True 
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'END_FINALLY', 'JUMP')) and pos__d[1] == pos__g[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__e), pos__g])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'END_FINALLY', 'JUMP_CONTINUE')) and pos__d[1] == pos__g[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__e), pos__g])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', '*n', 'JUMP_CONTINUE', \
                    (':', 4,1), 'END_FINALLY', ('::', 3))):
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], pos__f + [('CONTINUE',)], (')ENDTRY',)]])
                return True 
    if  SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', (':', 3, 1),\
                    '*n', ('::', 5))):
                rpl(cmds,[concatenate_try_except(pos__b,pos__e,pos__i)])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', '*e', 'J_AFTER_EXCEPT_HANDLE', \
                    'END_FINALLY', ('::', 4))):
                rpl(cmds,[concatenate_try_except(pos__b,pos__d)])
                return True
    ## if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \ # By CloneDigger
                    ## '*e', 'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', (':', 3, 1),\
                    ## '*n', ('::', 5))):
                ## rpl(cmds,[concatenate_try_except(pos__b,pos__e,pos__i)])
                ## return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', 'JUMP', (':', 4,1), 'END_FINALLY', \
                    (':', 3, 1), '*n', ('::', 5))):
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__e[2:], [('PASS',)], (')(ELSE',),pos__j, (')ENDTRY',)]])
                return True 
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'JUMP_IF_NOT_EXCEPTION_POP', \
                    '*n', (':', 3, 1), 'END_FINALLY')):            
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) + pos__d[2:], pos__e, (')ENDTRY',)]])
                return True 
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', 'JUMP_CONTINUE')) and\
                    pos__d[1] == pos__f[1] and pos__f[1] == pos__h[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__e),pos__h])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'J_AFTER_EXCEPT_HANDLE_CONTINUE', 'END_FINALLY',\
                    (':', 3, 1), '*n', 'JUMP_CONTINUE')) and pos__f[1] == pos__j[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__e,pos__i),pos__j])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', '*e', 'J_AFTER_EXCEPT_HANDLE_CONTINUE',\
                    'END_FINALLY', 'JUMP_CONTINUE')) and pos__e[1] == pos__g[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__d),pos__g])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', '*e', 'J_AFTER_EXCEPT_HANDLE',\
                    'END_FINALLY', 'JUMP')) and pos__e[1] == pos__g[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__d),pos__g])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*l', 'POP_TOP3', 'JUMP', 'END_FINALLY', (':', 3,1),\
                    '*n', ('::', 6))):
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',), [('PASS',)], (')(ELSE',),pos__j, (')ENDTRY',)]])
                return True 
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', 'JUMP', (':', 4, 1), 'END_FINALLY',\
                    'JUMP')) and pos__d[1] == pos__f[1] and pos__f[1] ==pos__i[1]:
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) +pos__e[2:], [('PASS', )], (')ENDTRY',)],pos__i])
                return True 
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', '*r', (':', 4,1), 'END_FINALLY',\
                    'JUMP')) and pos__d[1] == pos__i[1]:
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) +pos__e[2:], pos__f, (')ENDTRY',)],pos__i])
                return True 
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                   'JUMP_IF_NOT_EXCEPTION_POP', '*r', (':', 4,1), 'END_FINALLY',\
                   'JUMP_CONTINUE')) and pos__d[1] == pos__i[1]:
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) +pos__e[2:], pos__f, (')ENDTRY',)],pos__i])
                return True 
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    'JUMP_IF_NOT_EXCEPTION_POP', 'JUMP_CONTINUE', (':', 4, 1),\
                    'END_FINALLY', ('::', 3))):       #  1
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',) +pos__e[2:], [('CONTINUE',)], (')ENDTRY',)]])
                return True 
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'END_FINALLY', ('::',3))):
                rpl(cmds,[concatenate_try_except(pos__b,pos__e)])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', '*e', \
                    'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', ('::', 4))):
                rpl(cmds,[concatenate_try_except(pos__b,pos__d)])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY',\
                    ('!', '(EXCEPT1', '*n', ')ENDEXCEPT'), 'J_AFTER_EXCEPT_HANDLE_CONTINUE', \
                    'END_FINALLY', 'JUMP')) and\
                    pos__d[1] == pos__h[1] and pos__f[1] != pos__d[1]:
                tempor = pos__e[:-1]
                if len(tempor[-1][0]) > 0 and tempor[-1][0][0] == 'PASS':
                    tempor[-1] = [('CONTINUE',)]
                else:   
                    tempor[-1].append(('CONTINUE',))        
                tempor = tempor + [pos__e[-1]]                
                rpl(cmds,[concatenate_try_except(pos__b,tempor), pos__h])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY',\
                    ('!', '(EXCEPT1', '*n', ')ENDEXCEPT'), 'J_AFTER_EXCEPT_HANDLE_CONTINUE', \
                    'END_FINALLY', ('::',3))) and pos__f[1] != pos__d[1]:
                tempor = pos__e[:-1]
                if len(tempor[-1][0]) > 0 and tempor[-1][0][0] == 'PASS':
                    tempor[-1] = [('CONTINUE',)]
                else:   
                    tempor[-1].append(('CONTINUE',))        
                tempor = tempor + [pos__e[-1]]
                rpl(cmds,[concatenate_try_except(pos__b,tempor)])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', (':', 3, 1),\
                    '*r', ('::', 5))):       #  1            
                rpl(cmds,[concatenate_try_except(pos__b,pos__e,pos__i)])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*c', ')END_BEGIN_TRY', '*e', 'J_AFTER_EXCEPT_HANDLE', \
                    'END_FINALLY', ('::', 4))):
                rpl(cmds,[concatenate_try_except(pos__b,pos__d)])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', (':', 3,1),\
                    '*n', 'JUMP')) and pos__f[1] == pos__j[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__e,pos__i),pos__j])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                     '*e', 'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', ('::', (3,5)))):
        rpl(cmds,[concatenate_try_except(pos__b,pos__e)])
        return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'END_FINALLY', 'JUMP')) and pos__d[1] == pos__g[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__e),pos__g])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'END_FINALLY', ('::', 3))):       #  2
                rpl(cmds,[concatenate_try_except(pos__b,pos__e)])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', 'JUMP')) and\
                    pos__d[1] == pos__f[1] == pos__h[1]:            
                rpl(cmds,[concatenate_try_except(pos__b,pos__e),pos__h])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'END_FINALLY', 'ju')) and pos__d[1] == pos__g[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__e),pos__g])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', (':', 3,1), '*n',\
                    'JUMP_CONTINUE')) and pos__f[1] == pos__j[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__e,pos__i),pos__j])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY',\
                    '*e', 'J_AFTER_EXCEPT_HANDLE_CONTINUE', 'END_FINALLY', 'JUMP_CONTINUE')) and\
                    pos__d[1] == pos__f[1] == pos__h[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__e),pos__h])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY',\
                    ('!', '(EXCEPT1', ('!', 'PASS'), ')ENDEXCEPT'), \
                    'J_AFTER_EXCEPT_HANDLE_CONTINUE', 'END_FINALLY', ('::', 3))):
                rpl(cmds,[[('(TRY',), pos__b, ('(EXCEPT',) + pos__e[0][1:], [('CONTINUE',)], (')ENDTRY',)]])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', \
                    'J_IF_NO_EXCEPT_IN_TRY', 'JUMP_IF_NOT_EXCEPTION_POP', \
                    '*n', 'JUMP_CONTINUE', (':', 4,1), 'END_FINALLY', ('::', 3))):
                rpl(cmds,[[('(TRY',), pos__b, ('(EXCEPT',) + pos__e[2:], pos__f+[('CONTINUE',)], (')ENDTRY',)]])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', '*e', \
                    'J_AFTER_EXCEPT_HANDLE_CONTINUE', 'END_FINALLY',\
                    'JUMP_CONTINUE')) and pos__e[1] == pos__g[1]:
                rpl(cmds,[concatenate_try_except(pos__b,pos__d),pos__g])
                return True                        
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', (':', 3,1),\
                    '*n', ('::', 5))):
                rpl(cmds,[concatenate_try_except(pos__b,pos__e,pos__i)])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY',\
                    'J_IF_NO_EXCEPT_IN_TRY', '*e', \
                    'J_AFTER_EXCEPT_HANDLE_CONTINUE', 'END_FINALLY',\
                    (':', 3, 1), '*r')):                   
                rpl(cmds,[concatenate_try_except(pos__b,pos__e,pos__i),('JUMP_CONTINUE', pos__f[1])])
                return True
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    ('!', '.L', '(EXCEPT0', ('!', 'PASS'), ')ENDEXCEPT'),\
                    'J_AFTER_EXCEPT_HANDLE_CONTINUE', 'END_FINALLY', ('::', 3))):       #  2             
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',), [('CONTINUE',)], (')ENDTRY',)]])
                return True 
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    ('!', '(EXCEPT0', ('!', 'PASS'), ')ENDEXCEPT'),\
                    'J_AFTER_EXCEPT_HANDLE_CONTINUE', 'END_FINALLY', ('::', 3))):       #  2             
                rpl(cmds,[[('(TRY',), pos__b, (')(EXCEPT',), [('CONTINUE',)], (')ENDTRY',)]])
                return True                     
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    ('!', '.L', '(EXCEPT1', ('!', 'PASS'), ')ENDEXCEPT'),\
                    'J_AFTER_EXCEPT_HANDLE_CONTINUE', 'END_FINALLY', ('::', 3))):       #  2             
                rpl(cmds,[[('(TRY',pos__e[1][1]), pos__b, (')(EXCEPT',), [('CONTINUE',)], (')ENDTRY',)]])
                return True 
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    ('!', '(EXCEPT1', ('!', 'PASS'), ')ENDEXCEPT'),\
                    'J_AFTER_EXCEPT_HANDLE_CONTINUE', 'END_FINALLY', ('::', 3))):       #  2             
                rpl(cmds,[[('(TRY',pos__e[0][1]), pos__b, (')(EXCEPT',), [('CONTINUE',)], (')ENDTRY',)]])
                return True    
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', 'JUMP_CONTINUE', \
                    ('::', 5))) and pos__d[1] == pos__h[1]:       #  1            
                rpl(cmds,[concatenate_try_except(pos__b,pos__e,[('CONTINUE',)])])
                return True                                    
    if SCmp(cmds,i, ('(BEGIN_TRY', '*', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', (':', 3, 1),\
                    '*', '.:', 'END_FINALLY', ('::', 5))) and not islineblock(pos__i) and\
                    pos__j[1] not in (pos__d[1],pos__f[1]):
                rpl(cmds,[concatenate_try_except(pos__b,pos__e,pos__i), pos__j,pos__k])
                return True                                    
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY', '*e', 'END_FINALLY')):
                rpl(cmds,[concatenate_try_except(pos__b,pos__d)])
                return True      
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY',\
                    'J_IF_NO_EXCEPT_IN_TRY', '*e', 'J_AFTER_EXCEPT_HANDLE', \
                    'END_FINALLY', 'JUMP_CONTINUE', '.:', '*n', (':', (3,5), 1),\
                    'JUMP_CONTINUE')) and pos__h[1] == pos__l[1] and pos__i[1] not in (pos__d[1], pos__h[1]):
                rpl(cmds,[concatenate_try_except(pos__b,pos__e),pos__h,pos__i,pos__j,pos__l])
                return True      
    if SCmp(cmds,i, ('(BEGIN_TRY', '*n', ')END_BEGIN_TRY',\
                    'J_IF_NO_EXCEPT_IN_TRY', '*e', 'J_AFTER_EXCEPT_HANDLE', \
                    'END_FINALLY', 'JUMP_CONTINUE', '.:', '*n', (':', (3,5), 2),\
                    'JUMP_CONTINUE')) and pos__h[1] == pos__l[1] and pos__i[1] not in (pos__d[1], pos__h[1]):
                rpl(cmds,[concatenate_try_except(pos__b,pos__e),pos__h,pos__i,pos__j,pos__k,pos__l])
                return True              
    if SCmp(cmds,i, ('(BEGIN_TRY', '*r', ')END_BEGIN_TRY', 'J_IF_NO_EXCEPT_IN_TRY', \
                    '*e', 'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', (':', 3, 1),\
                    '*r', ('::', 5))):
                rpl(cmds,[concatenate_try_except(pos__b,pos__e,pos__i)])
                return True              
    return False

def process_except_clause(cmds,i):
    global pos__a,pos__b,pos__c,pos__d,pos__e,pos__f,pos__g,pos__h,pos__i,pos__j,pos__k,pos__l

    if SCmp(cmds,i, ('POP_TOP3', '*r', 'END_FINALLY')):
        rpl(cmds,[[('(EXCEPT0',), pos__b, (')ENDEXCEPT',)],pos__c])
        return True
    if SCmp(cmds,i, ('POP_TOP3', '*n', 'JUMP_CONTINUE', 'END_FINALLY')):
        rpl(cmds,[[('(EXCEPT0',), pos__b + [('CONTINUE',)], (')ENDEXCEPT',)],pos__d])
        return True
    if SCmp(cmds,i, ('POP_TOP3', 'JUMP_CONTINUE', 'END_FINALLY')):
        rpl(cmds,[[('(EXCEPT0',), [('CONTINUE',)], (')ENDEXCEPT',)],pos__c])
        return True
    if SCmp(cmds,i, ('POP_TOP3', 'JUMP', 'END_FINALLY')):
        if not islooplabel(pos__b[1],cmds):
           rpl(cmds,[[('(EXCEPT0',), [('PASS',)], (')ENDEXCEPT',)],('J_AFTER_EXCEPT_HANDLE', pos__b[1]),pos__c])
        else:   
           rpl(cmds,[[('(EXCEPT0',), [('CONTINUE',)], (')ENDEXCEPT',)],pos__c])
        return True
    if SCmp(cmds,i, ('POP_TOP3', '*n', 'JUMP', 'END_FINALLY')):
        rpl(cmds,[[('(EXCEPT0',), pos__b, (')ENDEXCEPT',)],('J_AFTER_EXCEPT_HANDLE', pos__c[1]),pos__d])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*n', 'JUMP', (':', 0,1), 'END_FINALLY')):
        rpl(cmds,[[('(EXCEPT1',) +pos__a[2:], pos__b, (')ENDEXCEPT',)],('J_AFTER_EXCEPT_HANDLE', pos__c[1]),pos__e])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*n', 'JUMP_CONTINUE', (':', 0,1), 'END_FINALLY')):
        rpl(cmds,[[('(EXCEPT1',) +pos__a[2:], pos__b + [('CONTINUE',)], (')ENDEXCEPT',)],pos__e])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*r', (':', 0,1), 'END_FINALLY')):
        rpl(cmds,[[('(EXCEPT1',) +pos__a[2:], pos__b, (')ENDEXCEPT',)],pos__d])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', 'JUMP', (':', 0,1), 'END_FINALLY')):
        rpl(cmds,[[('(EXCEPT1',) +pos__a[2:], [('PASS',)], (')ENDEXCEPT',)],('J_AFTER_EXCEPT_HANDLE', pos__b[1]),pos__d])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', 'JUMP_CONTINUE', (':', 0,1), 'END_FINALLY')):
        rpl(cmds,[[('(EXCEPT1',) +pos__a[2:], [('CONTINUE',)], (')ENDEXCEPT',)],pos__d])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*n', (':', 0,1), 'END_FINALLY')):
        rpl(cmds,[[('(EXCEPT1',) +pos__a[2:], pos__b, (')ENDEXCEPT',)], pos__d])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', 'xJUMP_IF2_FALSE_POP', '*r',\
                    (':', 0, 1), 'END_FINALLY', '.:', '*n', ('::', 1))) and\
                    pos__a[1] != pos__f[1] != pos__b[1]:
        rpl(cmds,[pos__a, [('(IF', pos__b[2]), pos__c, (')ENDIF',)], pos__d,pos__e,pos__f,pos__g])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*n',\
                    'xJUMP_IF2_FALSE_POP', '*n', \
                    'JUMP_CONTINUE', (':',0 ,1), \
                    'END_FINALLY', ('::', 2))):
        rpl(cmds,[[('(EXCEPT1',) +pos__a[2:], pos__b + \
                                 [('(IF',) + pos__c[2:], pos__d + [('CONTINUE',)], (')ENDIF',)],\
                         (')ENDEXCEPT',)], pos__g])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*n', 'JUMP_CONTINUE', (':', 0, 1), \
                    ('!', '(EXCEPT1', '*r', ')ENDEXCEPT'), 'END_FINALLY')):
        cmds[i:i+6] = [concatenate_except(pos__a[2:], pos__b + [('CONTINUE',)], pos__e),pos__f]
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*n', 'JUMP_CONTINUE', (':', 0, 1), \
                    '*e', 'J_AFTER_EXCEPT_HANDLE')) and pos__c[1] == pos__f[1]:
        cmds[i:i+6] = [concatenate_except(pos__a[2:], pos__b + [('CONTINUE',)], pos__e),pos__f]
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*n', 'JUMP', (':', 0, 1), \
                    '*e', 'J_AFTER_EXCEPT_HANDLE')) and pos__c[1] == pos__f[1]:
        cmds[i:i+6] = [concatenate_except(pos__a[2:], pos__b, pos__e),pos__f]
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', 'JUMP_CONTINUE', (':', 0, 1), \
                    '*e', 'J_AFTER_EXCEPT_HANDLE_CONTINUE')) and pos__b[1] == pos__e[1]:
        cmds[i:i+5] = [concatenate_except(pos__a[2:], [('PASS',)], pos__d),pos__e]
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*n', 'JUMP_CONTINUE', (':', 0, 1), \
                    '*e', 'END_FINALLY', 'JUMP_CONTINUE')) and pos__c[1] == pos__g[1]:
        cmds[i:i+7] = [concatenate_except(pos__a[2:], pos__b, pos__e),pos__f,pos__g]
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*n', 'JUMP_CONTINUE', \
                    (':', 0, 1), '*e', 'J_AFTER_EXCEPT_HANDLE')) and pos__c[1] != pos__f[1]:
        rpl(cmds,[concatenate_except(pos__a[2:], pos__b + [('CONTINUE',)], pos__e),pos__f])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', 'JUMP', (':', 0, 1), \
                    '*e', 'J_AFTER_EXCEPT_HANDLE')) and pos__b[1] == pos__e[1]:
        cmds[i:i+5] = [concatenate_except(pos__a[2:], [('PASS',)], pos__d),pos__e]
        return True
    ## if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', 'JUMP', (':', 0, 1), \ # By CloneDigger
                    ## '*e', 'J_AFTER_EXCEPT_HANDLE')) and pos__b[1] == pos__e[1]:
        ## cmds[i:i+5] = [concatenate_except(pos__a[2:], [('PASS',)], pos__d),pos__e]
        ## return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*', 'JUMP', (':', 0,1), '*e',
                    'END_FINALLY', ('::', 2))):
        rpl(cmds,[concatenate_except(pos__a[2:], pos__b, pos__e),pos__f])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*r', (':', 0, 1), '*e',\
                    'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', (':', 4, 2))):
        cmds[i:i+7] = [concatenate_except(pos__a[2:], pos__b, pos__d),pos__e,pos__f,pos__g]
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*r', (':', 0, 1), '*e',\
                    'J_AFTER_EXCEPT_HANDLE', 'END_FINALLY', (':', 4, 1))):
        cmds[i:i+7] = [concatenate_except(pos__a[2:], pos__b, pos__d),pos__f]
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*r', (':', 0, 1), '*e',\
                    'END_FINALLY')):
        cmds[i:i+5] = [concatenate_except(pos__a[2:], pos__b, pos__d),pos__e]
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*r', (':', 0,1), '*e')):       
        cmds[i:i+4] = [concatenate_except(pos__a[2:], pos__b, pos__d)]
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*ra', 'JUMP', (':', 0,1), '*e')) and\
                    pos__c[1] != pos__a[1]:
        rpl(cmds,[concatenate_except(pos__a[2:], pos__b, pos__e)])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', 'JUMP', (':', 0, 1), '*e',\
                    'END_FINALLY', ('::', 1))):
        rpl(cmds,[concatenate_except(pos__a[2:], [('PASS',)], pos__d),pos__e])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', '*n', 'JUMP_CONTINUE', \
                    (':', 0, 1), '*e', 'END_FINALLY')):          
        rpl(cmds,[concatenate_except(pos__a[2:], pos__b + [('CONTINUE',)], pos__e),pos__f])
        return True
    if SCmp(cmds,i, ('JUMP_IF_NOT_EXCEPTION_POP', 'JUMP_CONTINUE', \
                    (':', 0, 1), '*e', 'END_FINALLY')):          
        rpl(cmds,[concatenate_except(pos__a[2:], [('CONTINUE',)], pos__d),pos__e])
        return True
    return False
    
def process_after_try_detect(cmds,_i):
    global count_define_set
    aa = cmds[_i]
    v0,v1,v2 = [], [], []
    i = 0
    if len(aa) == 5 and aa[0] == ('(TRY',) and \
       len(aa[1]) == 2 and aa[1][0][0] == '.L' and\
       TCmp(aa[1][1], v0, ('STORE', (('STORE_NAME', '?'),), \
                                 (('!IMPORT_NAME', '?', '?', '?'),))) and \
       TCmp(aa[2], v1, (')(EXCEPT', (('!LOAD_BUILTIN', 'ImportError'), '?'), ())) and\
       len(aa[3]) == 2 and aa[3][0][0] == '.L' and\
       TCmp(aa[3][1], v2, ('STORE', (('STORE_NAME', '?'),), (('CONST', None),))) and \
       aa[4] == (')ENDTRY',) and v0[0] == v0[1] and v0[0] == v2[0]:
            this, d = None, None
#            try:
            this, d = MyImport(v0[1])
            cmds[_i] = aa[1]
#            except:
#                cmds[_i] = aa[3]
            if v0[0] in count_define_set and count_define_set[v0[0]] > 1:
                count_define_set[v0[0]] -= 1
    
def process_setup_except(cmds,i):
    global pos__a,pos__b,pos__c,pos__d,pos__e,pos__f,pos__g,pos__h,pos__i,pos__j,pos__k,pos__l

    if SCmp(cmds,i, ('J_SETUP_EXCEPT', 'xJUMP_IF2_TRUE_POP_CONTINUE', '*l', 'POP_BLOCK')):
        if type(pos__c) is tuple:
            rpl(cmds,[pos__a, [('(IF',) + pos__b[2:], [('CONTINUE',)], (')ENDIF',)]+[pos__c],pos__d])
        else:    
            rpl(cmds,[pos__a, [('(IF',) + pos__b[2:], [('CONTINUE',)], (')ENDIF',)]+pos__c,pos__d])
        return True
    if SCmp(cmds,i, ('J_SETUP_EXCEPT', '*', 'POP_BLOCK', 'JUMP', ('::', 0))) and pos__d[1] != pos__e[1]:
        rpl(cmds,[('(BEGIN_TRY',), pos__b, (')END_BEGIN_TRY',), ('J_IF_NO_EXCEPT_IN_TRY', pos__d[1])])
        return True
    if SCmp(cmds,i, ('J_SETUP_EXCEPT', 'POP_BLOCK', 'JUMP', ('::', 0))) and pos__d[1] != pos__c[1]:
        rpl(cmds,[('(BEGIN_TRY',), [('PASS',)], (')END_BEGIN_TRY',), ('J_IF_NO_EXCEPT_IN_TRY', pos__c[1])])
        return True
    if SCmp(cmds,i, ('J_SETUP_EXCEPT', 'JUMP_CONTINUE', 'POP_BLOCK', 'JUMP_CONTINUE', \
                    (':', 0, 1))) and pos__b[1] == pos__d[1]:
        rpl(cmds,[('(BEGIN_TRY',), [('CONTINUE',)], (')END_BEGIN_TRY',)])
        return True
    if SCmp(cmds,i, ('J_SETUP_EXCEPT', 'POP_BLOCK', 'JUMP_CONTINUE', \
                    (':', 0, 1))):
        rpl(cmds,[('(BEGIN_TRY',), [('CONTINUE',)], (')END_BEGIN_TRY',)])
        return True
    if SCmp(cmds,i, ('J_SETUP_EXCEPT', '*', 'JUMP_CONTINUE', \
                    'POP_BLOCK', 'JUMP', ('::', 0))) and pos__e[1] != pos__f[1]:
        rpl(cmds,[('(BEGIN_TRY',), pos__b + [('CONTINUE',)], (')END_BEGIN_TRY',), \
                       ('J_IF_NO_EXCEPT_IN_TRY', pos__e[1])])
        return True
    if SCmp(cmds,i, ('J_SETUP_EXCEPT', '*n', 'JUMP', ('::', 0))) and pos__c[1] != pos__d[1]:
        rpl(cmds,[('(BEGIN_TRY',), pos__b, (')END_BEGIN_TRY',), ('J_IF_NO_EXCEPT_IN_TRY', pos__c[1])])
        return True
    if SCmp(cmds,i, ('J_SETUP_EXCEPT', '*n', 'JUMP_CONTINUE', ('::', 0))) and pos__c[1] != pos__d[1]:
        rpl(cmds,[('(BEGIN_TRY',), pos__b +[('CONTINUE',)], (')END_BEGIN_TRY',)])
        return True
    if SCmp(cmds,i, ('J_SETUP_EXCEPT', '*n', 'JUMP_CONTINUE', 'POP_BLOCK',\
                    'JUMP_CONTINUE', (':', 0,1), '*e')):
        rpl(cmds,[('(BEGIN_TRY',), pos__b +[('CONTINUE',)], (')END_BEGIN_TRY',),pos__g])
        return True
    if SCmp(cmds,i, ('J_SETUP_EXCEPT', '*', 'POP_BLOCK', 'JUMP_CONTINUE', ('::', 0))) and pos__d[1] != pos__e[1]:
        rpl(cmds,[('(BEGIN_TRY',), pos__b, (')END_BEGIN_TRY',), ('J_IF_NO_EXCEPT_IN_TRY', pos__d[1])])
        return True
    if SCmp(cmds,i, ('J_SETUP_EXCEPT', '*r', ('::', 0))):
        rpl(cmds,[('(BEGIN_TRY',), pos__b, (')END_BEGIN_TRY',)])
        return True
    if SCmp(cmds,i, ('J_SETUP_EXCEPT', 'JUMP_CONTINUE', 'POP_BLOCK',\
                    'JUMP_CONTINUE', (':', 0,1), '*e', \
                    'J_AFTER_EXCEPT_HANDLE_CONTINUE', 'END_FINALLY',\
                    'JUMP_CONTINUE')) and pos__b[1] == pos__d[1] == pos__g[1] == pos__i[1]:
        rpl(cmds,[concatenate_try_except([('CONTINUE',)],pos__f), pos__i])
        return True
    if SCmp(cmds,i, ('J_SETUP_EXCEPT', 'POP_BLOCK', 'JUMP_CONTINUE', (':', 0, 1),\
                    '*e', 'J_AFTER_EXCEPT_HANDLE_CONTINUE', 'END_FINALLY',\
                    'JUMP_CONTINUE')) and pos__c[1] == pos__f[1] == pos__h[1]:
        rpl(cmds,[concatenate_try_except([('PASS',)],pos__e), pos__h])
        return True    
    return False
    
def concatenate_try_except(bl1, exc_tail, else_tail = None):
    out = []
    out.append(('(TRY',))
    out.append(bl1)
    if exc_tail is None:
       if else_tail is not None: 
          out.append((')(ELSE',))
          out.append(else_tail)
       out.append((')ENDTRY',) )
       return out
    tail = exc_tail[:]
    while len(tail) > 0 and tail[0][0] == '.L':
        del tail[0]
    if tail[0][0] in ('(EXCEPT','(EXCEPT0','(EXCEPT1'):
        t1 = (')(EXCEPT',) + tail[0][1:]
        out.append(t1)
        return add_endtry(out, tail, bl1, exc_tail, else_tail)
    elif tail[0][0] == '(EXCEPT0':
        out.append((')(EXCEPT',))
        return add_endtry(out, tail, bl1, exc_tail, else_tail)
    Fatal('Error in exception sequence', bl1, exc_tail, else_tail)
    return '~'

def add_endtry(out, tail, bl1, exc_tail, else_tail):
    del tail[0]
    out.extend(tail[:-1])
    if tail[-1][0] != ')ENDEXCEPT':
        Fatal('Must be ENDEXCEPT', bl1, exc_tail, else_tail)
        return '%%'
    if else_tail is not None: 
        out.append((')(ELSE',))
        out.append(else_tail)
    out.append((')ENDTRY',))
    return out
    
def concatenate_except(cond, bl1, exc_tail):
    out = []
    out.append(('(EXCEPT',) + cond)
    out.append(bl1)
    if exc_tail is None:
       out.append((')ENDEXCEPT',) )
       return out
    tail = exc_tail[:]
    while len(tail) > 0 and tail[0][0] == '.L':
        del tail[0]
    if len(tail) == 0:
       out.append((')ENDEXCEPT',) )
       return out
    if tail[0][0] in ('(EXCEPT','(EXCEPT0','(EXCEPT1'):
        t1 = (')(EXCEPT',) + tail[0][1:]
        out.append(t1)
        del tail[0]
        out.extend(tail)
        return out
    elif tail[0][0] == '(EXCEPT0':
        t1 = (')(EXCEPT',)
        out.append(t1)
        del tail[0]
        out.extend(tail)
        return out
    Fatal('Error in concatenate except', filename)
    return '~'

def New_3Cmp(tupl):
  
    t = ('!NCMP', tuple(tupl[1:]))
    return ('!BOOLEAN', t)                 
    
    t = And_j(process_compare_op(tupl[2], tupl[1], tupl[3])[0],
                      process_compare_op(tupl[4], tupl[3], tupl[5])[0])
    return ('!BOOLEAN', t)                 

def New_NCmp(tupl):
    print tupl
    t = ('!NCMP', tupl)
    return ('!BOOLEAN', t)                 
    if len(tupl) == 5:
        t = And_j(process_compare_op(tupl[1], tupl[0], tupl[2])[0],
                        process_compare_op(tupl[3], tupl[2], tupl[4])[0])
    else:                    
        t = And_j(process_compare_op(tupl[1], tupl[0], tupl[2])[0],
                        New_NCmp(tupl[2:]))
    return ('!BOOLEAN', t)                 

def isintconst(b):
    return type(b) is tuple and len(b) == 2 and b[0] == 'CONST' \
            and type(b[1]) is int

## def printcmpstat():
    ## lines = [(k,v) for k,v in used_line.iteritems()]
    ## lines.sort()
    ## lines = [(l,v,p,v2) for l,v in lines for (p,l2),v2 in used_cmpl.iteritems() if l == l2]
    ## lines.sort()
    ## writer = csv.writer(open("stat2c.csv", "wb"), dialect='excel', delimiter=';')
    ## for l,v,p,v2 in lines:
        ## s = repr(p)
        ## writer.writerow((l,v, matched_line.get(l,0), v2, matched_cmpl.get((p,l),0),s))
    ## listerr = {}    
    ## for p in used_cmp.keys():
        ## list_p = list_variant(p)
        ## pos__d = {}
        ## for p2 in list_p:
            ## d[p2] = True
        ## list_p = d.keys()
        ## list_p.sort()    
        ## for p2 in list_p:
                ## listerr[(p,p2)] = True
          
    ## li = listerr.keys()
    ## l3 = []
    ## for p,p2 in li:
        ## if p in p2l:
            ## l3.append((p2l[p],p,p2))
        ## else:    
            ## l3.append((0,p,p2))
    ## l3.sort()   
    ## l_o = {}    
    ## for l,p,p2 in l3:
        ## if (l,p) not in l_o:
            ## l_o[(l,p)] = [p2]
        ## else:
            ## l_o[(l,p)].append(p2)
    ## li = list(l_o.iteritems())        
    ## li.sort()
    ## for (l,p),v in li:   
       ## p3 = [p22 for p22 in v if p22 not in p2l]
       ## co = ''
       ## if len(p3) == 0:
            ## co = '#'         
       ## if len(v) == 1:
            ## continue
       ## print co, l, p #repr(p)
       ## for p2 in v:
           ## if p2 == p:
               ## continue
           ## if p2 in p2l:
              ## print co,'->', p2l[p2], '->', repr(p2)             
           ## else:    
              ## print co,'->', p2 #repr(p2)             

## def list_variant(p, i = 0):
    ## if i >= len(p):
      ## return [p]
    ## if p[i] in anagr:
        ## var1 = list_variant(p,i+1)
        ## p2 = p[:i] + (anagr[p[i]],) + p[i+1:]
        ## var2 = list_variant(p2,i+1)
        ## return var1 + var2
    ## elif i + 1 == len(p) and type(p[i]) is tuple and len(p[i]) == 3 and\
                        ## p[i][0] == ':' and p[i][2] in (1,2) and p[i][1] is not None:
        ## lb = p[i]
        ## if lb[2] == 1:
            ## lb2 = (lb[0], lb[1], 2)
        ## else:                  
            ## lb2 = (lb[0], lb[1], 1)
        ## var1 = list_variant(p,i+1)
        ## p2 = p[:i] + (lb2,)
        ## var2 = list_variant(p2,i+1)
        ## return var1 + var2
    ## elif p[i] in ('*', '*n', '*l'):
        ## var1 = list_variant(p,i+1)
        ## p2 = new_p_without(p, i)
        ## if p2 is None:
            ## return var1
        ## var2 = list_variant(p2,i)
        ## return var1 + var2
    ## else:                 
        ## return list_variant(p,i+1)

## def new_p_without(p,pos):
    ## p = list(p)
    ## if pos > 0 and pos < (len(p) - 1) and\
        ## type(p[pos-1]) is tuple and\
        ## type(p[pos+1]) is tuple and\
        ## p[pos-1][0] in (':','::') and p[pos+1][0] in (':','::'):
            ## return None
    ## for i in range(len(p)):
        ## if type(p[i]) is tuple and len(p[i]) == 3 and\
              ## p[i][0] == ':' and p[i][1] is not None:
                  ## p[i] = list(p[i])
                  ## p3 = p[i][1]                  
                  ## if p3 == pos:
                      ## return None
                  ## if type(p3) is tuple:
                      ## p3 = list(p3)
                      ## for j in range(len(p3)):
                          ## if p3[j] == pos:
                              ## return None
                          ## elif p3[j] > pos:
                              ## p3[j] -= 1
                      ## p3 = tuple(p3)
                      ## p[i][1] = p3
                  ## elif p[i][1] > pos:
                      ## p[i][1] -= 1
                  ## p[i] = tuple(p[i])
        ## if type(p[i]) is tuple and len(p[i]) == 2 and\
              ## p[i][0] == '::' and p[i][1] is not None:
                  ## p[i] = list(p[i])
                  ## p3 = p[i][1]                  
                  ## if p3 == pos:
                      ## return None
                  ## if type(p3) is tuple:
                      ## p3 = list(p3)
                      ## for j in range(len(p3)):
                          ## if p3[j] == pos:
                              ## return None
                          ## elif p3[j] > pos:
                              ## p3[j] -= 1
                      ## p3 = tuple(p3)
                      ## p[i][1] = p3
                  ## elif p[i][1] > pos:
                      ## p[i][1] -= 1
                  ## p[i] = tuple(p[i])

    ## del p[pos]              
    ## p = tuple(p)
    ## return p

def rpl(cmds,new):
    global matched_tail_label
    if matched_tail_label is not None and (matched_tail_label[1] > 0 or matched_tail_label[3]):
        new = new + [matched_tail_label[2]]
    if len(new) >= 2 and type(new[-1]) is tuple and type(new[-2]) is tuple and\
       len(new[-1]) == 2 and len(new[-2]) == 2 and new[-1][0] == '.:'  and new[-2][0] == '.:' and\
       new[-1][1] == new[-2][1]:
           Fatal("Dublicate label")
    cmds[matched_i:matched_i+matched_len] = new
    return 

def begin_cmp():
    global matched_i
    global matched_p
    global matched_len
    global matched_tail_label
    mathed_i = None
    matched_p = None
    matched_len = None
    matched_tail_label = None

def SCmp(cmds,i0,pattern,recursive=False):
    global matched_i
    global matched_p
    global matched_len
    global matched_tail_label
    global used_cmpl, used_cmp, used_line, matched_cmpl, matched_cmp,matched_line,collect_stat,p2l
    global pos__a,pos__b,pos__c,pos__d,pos__e,pos__f,pos__g,pos__h,pos__i,pos__j,pos__k,pos__l

    tempor = cmds[i0:i0+len(pattern)]

    ## line = 0     
    ## if collect_stat and not recursive:
        ## if pattern in p2l:
            ## line = p2l[pattern]
        ## else:    
            ## line = traceback.extract_stack(None,2)[-2][1]
            ## p2l[pattern] = line
        ## used_line[line] = used_line.get(line,0) + 1
        ## used_cmpl[(pattern,line)] = used_cmpl.get((pattern,line),0) + 1
        ## used_cmp[pattern] = used_cmp.get(pattern,0) + 1
    if len(tempor) != len(pattern):
        return False
    for i,p in enumerate(pattern):
        ## if debugp:
              ## print >>out,i, '->', p, '= ',
              ## prin(i0+i, tempor[i],cmds)
        if i >= len(tempor):
            return False
        tempi = tempor[i]

        if type(tempi) != int and tempi[0] == p:
            continue
        if p[:9] == 'xJUMP_IF2':
            if p[1:] in anagr:
                if tempi[0] == p[1:]:
                    continue
                elif tempi[0] == anagr[p[1:]]:
                    tempi = list(tempi)
                    tempi[2] = Not(tempi[2])
                    tempi[0] = p[1:]
                    tempi = tempor[i] = tuple(tempi)
                    continue
            return False    
        if p == 'ju':
            if tempi[0] not in ('JUMP', 'JUMP_CONTINUE'):
                return False
            continue
        elif p == 'jc':
            if tempi[0] not in ('JUMP', 'JUMP_CONTINUE') or not islooplabel(tempi[1],cmds):
                return False
            continue
        elif p == '>':
            if type(tempi) is tuple and len(tempi) >= 1 and\
               (tempi[0] in ('CONST', 'FAST', 'LOAD_FAST', 'LOAD_CONST', 'LOAD_CLOSURE', 'PY_TYPE') or\
                tempi[0][0] == '!'):
                    continue
            return False   
        elif p == '=':
            if tempi[0] in set_any:
                continue
            return False
        elif p == '*':
            if type(tempi) is list and (len(tempi) > 1 or tempi[0][0] != '.L'):
                continue
            return False
        elif p == '*r':
            if type(tempi) is list and tempi[-1][0] == 'RETURN_VALUE':
                continue
            return False
        elif p == '*ra':
            if type(tempi) is list and tempi[-1][0] == 'RAISE_VARARGS':
                continue
            return False
        elif p == '*c':
            if type(tempi) is list and tempi[-1][0] == 'CONTINUE':
                continue
            return False
        elif p == '*l':
            if type(tempi) is list and len(tempi) == 1 and tempi[0][0] == '.L':
                continue
            elif tempi[0] == '.L':    
                continue
            return False  
        elif p == '*e':
            if not (type(tempi) is list):
                return False
            if not isexceptblock(tempi):
                return False
            continue
        elif p == '*n':
            if type(tempi) is list and (len(tempi) > 1 or tempi[0][0] != '.L'):
                if tempi[-1][0] == 'RETURN_VALUE' or isexceptblock(tempi):
                    return False
                continue
            return False
        elif p == '**n':
            if type(tempi) is list and (len(tempi) > 1 or tempi[0][0] != '.L'):
                if tempi[-1][0] == 'RETURN_VALUE' or isexceptblock(tempi):
                    return False
            else:                
                tempor[i:i+1] = [[('PASS',)], tempi]
                tempor = tempor[0:len(pattern)]
            continue
        elif type(p) is tuple:
            if p[0] == '!':
                if len(tempi) == len(p[1:]) and SCmp(tempi,0, p[1:],True):
                    continue
                return False                
            elif p[0] == ':':
                if len(p) == 3:
                    if type(p[1]) is tuple:
                        for pp in p[1]:
                            if pp>= len(tempor) or not label(tempor[pp], tempi):
                                return False
                    elif p[1] is not None:
                        if p[1] >= len(tempor) or not label(tempor[p[1]], tempi):
                            return False
                    if p[2] == 1 and not OneJump(tempi[1],cmds):
                        return False
                    if p[2] == 2 and OneJump(tempi[1],cmds):
                        return False
            elif p[0] == '::':
                if len(p) == 2:
                    ltemp = 0
                    isjump = False
                    if tempi[0] == '.:': 
                        if type(p[1]) is tuple:
                            ltemp = len(p[1])
                            for pp in p[1]:
                                if not label(cmds[i0+pp], tempi):
                                    return False
                        elif p[1] is not None:
                            ltemp = 1
                            if not label(cmds[i0+p[1]], tempi):
                                return False
                        if CntJump(tempi[1],cmds) == 0:
                            return False
                    elif tempi[0] in jump: 
                        isjump = True
                        if type(p[1]) is tuple:
                            ltemp = len(p[1])
                            for pp in p[1]:
                                if not endlabel(cmds[i0+pp], tempi):
                                    return False
                        elif p[1] is not None:
                            ltemp = 1
                            if not endlabel(cmds[i0+p[1]], tempi):
                                return False
                        if CntJump(tempi[1],cmds) == 0:
                            return False
                    else:
                        return False    
                    if i == len(pattern)-1:
                        matched_tail_label = (p, CntJump(tempi[1],cmds)-ltemp, tempi, isjump)
            elif len(p) == 2:
                if len(tempi) < 2 or not (p[0] == tempi[0] and p[1] == tempi[1]):
                    return False
            continue
        if type(tempi) is int or tempi[0] != p:
            return False
    ## if collect_stat:    
        ## matched_line[line] = matched_line.get(line,0) + 1
        ## matched_cmpl[(pattern,line)] = matched_cmpl.get((pattern,line),0) + 1
        ## matched_cmp[pattern] = matched_cmp.get(pattern,0) + 1

    ## if debug or debugp:    
       ## print >>out, line, i0, '*** Matched ***'
       ## pprint.pprint(pattern,out)
    if not recursive:   
       matched_i = i0   
       matched_p = pattern
       matched_len = len(pattern)
##    if not recursive:
       tempor = tempor[0:min(len(pattern),12)]
       while len(tempor) < 12:
           tempor.append('^^') # ibo nefig
       pos__a,pos__b,pos__c,pos__d,pos__e,pos__f,pos__g,pos__h,pos__i,pos__j,pos__k,pos__l = tempor       
    return True    

def islineblock(a):
    if type(a) is list:
        if len(a) == 1 and a[0][0] == '.L':
            return True
    elif a[0] == '.L':
        return True    
    return False  

def isblock(a):
    if type(a) is list:
        if len(a) > 1:
            return True
        if a[0][0] == '.L':
            return False
        else:
            return True
    else:
        return False 

def isretblock(a):
    return type(a) is list and a[-1][0] == 'RETURN_VALUE'

def islooplabel(label,cmds):
    lab = ('.:', label)
    for i in range(len(cmds)-2):
        a = cmds[i][0]
        if a == 'J_SETUP_LOOP_FOR' and cmds[i+1] == lab and cmds[i+2][0] == 'J_LOOP_VARS':
               return True
        if a == 'J_SETUP_LOOP' and cmds[i+1] == lab:
               return True
    return False       

def isexceptblock(a):
    if type(a) is list:
        if a[-1][0] == ')ENDEXCEPT':
            if a[0][0] in ('(EXCEPT', '(EXCEPT0', '(EXCEPT1'):
                return True
            if a[0][0] == '.L' and a[1][0]  in ('(EXCEPT', '(EXCEPT0', '(EXCEPT1'):
                return True
    return False

def revert_conditional_jump_over_uncond_jump(cmds):
    i = 0
    while i < ( len(cmds) - 4):            
        a = cmds[i]
        if a[0][:8] == 'JUMP_IF_' and a[0][-4:] == '_POP':
            b,c, d = cmds[i+1], cmds[i+2], cmds[i+3]
            if b[0] == '.L' and c[0] in jump and d[0] == '.:' and a[1] == d[1]:
                if a[0] == 'JUMP_IF_FALSE_POP':
                    e = 'JUMP_IF_TRUE_POP'
                else:
                    e = 'JUMP_IF_FALSE_POP'
                oldlabel = a[1]    
                cmds[i:i+4] = [(e, c[1]),b,d] 
                del_if_unused_label(cmds, oldlabel)
                continue
            elif b[0] in jump and c[0] == '.:' and a[1] == c[1]:
                if a[0] == 'JUMP_IF_FALSE_POP':
                    e = 'JUMP_IF_TRUE_POP'
                else:
                    e = 'JUMP_IF_FALSE_POP'
                oldlabel = a[1]
                cmds[i:i+3] = [(e, b[1]),c] 
                del_if_unused_label(cmds, oldlabel)
                continue
        i = i + 1    
    
def del_dead_code(cmds):
    i = 0
    while i < (len(cmds) - 1):            
        cmd = cmds[i]
        if cmd[0] in jump:
            cmd2 = cmds[i+1]
            if cmd2[0] not in ('END_FINALLY', 'POP_BLOCK') and (type(cmd2[0]) != str or cmd2[0][0] != '.'):
                del cmds[i+1]
                continue
            elif cmd2[0] == '.L':
                del cmds[i+1]
                continue
            elif cmd2[0] == '.:' and cmd2[1] == cmd[1]:
                oldlabel = cmd[1]
                del cmds[i]
                del_if_unused_label(cmds, oldlabel)
                i = max(0, i-3)
                continue
        i = i + 1        
    i = 0
    while i < (len(cmds) - 1):            
        cmd = cmds[i]
        if cmd[0] == 'RETURN_VALUE' and \
        (type(cmds[i+1][0]) != str or cmds[i+1][0][0] != '.') and \
        cmds[i+1][0]  not in ('END_FINALLY', 'POP_BLOCK'):
            del cmds[i+1]
            continue
        elif cmd[0] == 'RETURN_VALUE' and cmds[i+1][0] == '.L':
            del cmds[i+1]
            continue
        i = i + 1    

def set_conditional_jump_popped(cmds):
    i = 0
    while i < (len(cmds) - 1):            
        cmd,b = cmds[i], cmds[i+1]
        if (( cmd[0] == 'JUMP_IF_FALSE' or cmd[0] == 'JUMP_IF_TRUE' ) and b[0] == 'POP_TOP'):
           to_label, pos_to_label = after_label(cmds, cmd[1], 3)
           oldlabel = cmd[1]
           if to_label[1][0] == 'POP_TOP':
               if to_label[2][0] == '.:':
                    cmds[i:i+2] = [(cmd[0] + '_POP', to_label[2][1])]
                    del_if_unused_label(cmds, oldlabel)
                    i = max(0, i-3)
                    continue
               elif pos_to_label > i+2:
                      new_label = gen_new_label(cmds)
                      cmds.insert(pos_to_label+2, ('.:', new_label))              
                      cmds[i:i+2] = [(cmd[0] + '_POP', new_label)]
                      del_if_unused_label(cmds, oldlabel)
                      i = max(0, i-3)
                      continue
               elif pos_to_label < i:
                      new_label = gen_new_label(cmds)
                      cmds[i:i+2] = [(cmd[0] + '_POP', new_label)]
                      cmds.insert(pos_to_label+2, ('.:', new_label))              
                      del_if_unused_label(cmds, oldlabel)
                      i = max(0, pos_label-3)
                      continue
        i = i + 1        
    i = 0
    while i < (len(cmds) - 1):            
        cmd,b = cmds[i], cmds[i+1]
        if (( cmd[0] == 'JUMP_IF_FALSE' or cmd[0] == 'JUMP_IF_TRUE' ) and b[0] == 'POP_TOP'):
           to_label, pos_to_label = after_label(cmds, cmd[1], 3)
           oldlabel = cmd[1]
           if ( to_label[1][0] == 'JUMP_IF_FALSE_POP' and cmd[0] == 'JUMP_IF_FALSE') or\
              ( to_label[1][0] == 'JUMP_IF_TRUE_POP' and cmd[0] == 'JUMP_IF_TRUE'):
                cmds[i:i+2] = [(cmd[0] + '_POP', to_label[1][1])]
                del_if_unused_label(cmds, oldlabel)
                i = max(0, i-3)
                continue
        i = i + 1        

    i = 0
    while i < (len(cmds) - 1):            
        cmd,b = cmds[i], cmds[i+1]
        if (( cmd[0] == 'JUMP_IF_FALSE' or cmd[0] == 'JUMP_IF_TRUE' ) and b[0] == 'POP_TOP'):
           to_label, pos_to_label = after_label(cmds, cmd[1], 3)
           oldlabel = cmd[1]
           if len(to_label) >= 3 and to_label[2][0] == '.:' and \
             (( to_label[1][0] == 'JUMP_IF_FALSE_POP' and cmd[0] == 'JUMP_IF_TRUE') or\
              ( to_label[1][0] == 'JUMP_IF_TRUE_POP' and cmd[0] == 'JUMP_IF_FALSE')):
                cmds[i:i+2] = [(cmd[0] + '_POP', to_label[2][1])]
                del_if_unused_label(cmds, oldlabel)
                i = max(0, i-3)
                continue
        i = i + 1      
    i = 1
    while i < (len(cmds) - 1) and i > 0:            
        prev,cmd,b = cmds[i-1],cmds[i], cmds[i+1]
        if (( cmd[0] == 'JUMP_IF_FALSE' or cmd[0] == 'JUMP_IF_TRUE' ) and b[0] == 'POP_TOP' and prev[0] == 'LOAD_FAST'):
           to_label, pos_to_label = after_label(cmds, cmd[1], 3)
           oldlabel = cmd[1]
           if ( to_label[1][0] == 'STORE_FAST' and \
               to_label[1][1] == prev[1]):
               if to_label[2][0] == '.:':
                    cmds[i:i+2] = [(cmd[0] + '_POP', to_label[2][1])]
                    del_if_unused_label(cmds, oldlabel)
                    i = max(0, i-3)
                    continue
               elif pos_to_label > i+2:
                      new_label = gen_new_label(cmds)
                      cmds.insert(pos_to_label+2, ('.:', new_label))              
                      cmds[i:i+2] = [(cmd[0] + '_POP', new_label)]
                      del_if_unused_label(cmds, oldlabel)
                      i = max(0, i-3)
                      continue
               elif pos_to_label < i:
                      new_label = gen_new_label(cmds)
                      cmds[i:i+2] = [(cmd[0] + '_POP', new_label)]
                      cmds.insert(pos_to_label+2, ('.:', new_label))              
                      del_if_unused_label(cmds, oldlabel)
                      i = max(0, pos_label-3)
                      continue
        i = i + 1        
    
def print_cmds2(cmds, skip):
    skip += 4
    for cmd in cmds:    
        if type(cmd) is list:
            print >>out, '{'
            print_cmds2(cmd, skip)
            print >>out, '}'
            continue
        if cmd[0] == '.L':
            print >>out, '                    .L', cmd[1]
        elif cmd[0] == '.:':
#            decompile_fail = True            
            print >>out, '^^',' ' * skip, cmd, '      # ', len(ref_to_label(cmd[1], cmds))   
#            print cmd[1], ':'    
        elif is_cmdmem(cmd):    
#            decompile_fail = True            
            print >>out, '^^', ' ' * skip, cmd   
        else:    
            print >>out, ' ' * skip, cmd   

def print_cmds(cmds):
    print >>out, 'co_const:'
    pprint.pprint(consts_from_cmds(cmds),out)
    skip = 0
    for cmd in cmds:        
        if type(cmd) is list:
            print  >>out, '{'
            print_cmds2(cmd, skip)
            print >>out, '}'
            continue
        if cmd[0] == '.L':
            print >>out, '^^','                    .L', cmd[1]
        elif cmd[0] == '.:':
            print >>out, '^^',' ' * skip, cmd, '      # ', len(ref_to_label(cmd[1], cmds))   
        elif cmd[0][0] == 'J':    
            print >>out, '^^',' ' * skip, cmd, '      # ', len(ref_to_label(cmd[1], cmds))    
        elif is_cmdmem(cmd):    
            print >>out, '^^', ' ' * skip, cmd   
        elif is_cmdmem(cmd):    
            print >>out, '^^', ' ' * skip, cmd   
        else:    
            print >>out, ' ' * skip, cmd   
 
def ref_to_label(label, cmds):
    return [i for i, x in enumerate(cmds) if x[0][0] == 'J' and x[1] == label]

def CntJump(label, cmds):
    return len([x for x in cmds if x[0][0] == 'J' and x[1] == label])

def OneJump(label, cmds):
    return len([x for x in cmds if x[0][0] == 'J' and x[1] == label]) == 1

def TupleFromArgs(args):
    if len(args) > 0 and args[0] in ('!BUILD_TUPLE', 'CONST'):
        return args
    if len([x for x in args if x[0] != 'CONST']) == 0:
        return ('CONST', tuple([x[1] for x in args]))
    return ('!BUILD_TUPLE', args)

def DictFromArgs(args):
    return ('!BUILD_MAP', args)    

def cmd2mem(cmd):
    cm = cmd[0]
    if cm == 'LOAD_CLOSURE':
        return ('LOAD_CLOSURE', cmd[1])
    if cm == 'LOAD_FAST':
        return ('FAST', cmd[1])
    if cm == 'LOAD_CONST':
        return ('CONST', cmd[1])
    if cm[0:1] == '!':
        return cmd
    if cm in ('CONST', 'FAST'):
        return cmd
    if cm == 'PY_TYPE':
        return cmd
    Fatal('Illegal cms2mem', cmd)

def is_cmdmem(cmd):
    a = cmd[0]
    return a in ('CONST', 'FAST', 'LOAD_FAST', 'LOAD_CONST', 'LOAD_CLOSURE', 'PY_TYPE') \
        or (a is not None and a[0] == '!')

def del_if_unused_label(cmds, oldlabel):
    la = [x[1] for x in cmds if x[0][0] == 'J']
    if oldlabel not in la:
        i = 0
        while i < len(cmds):            
            cmd = cmds[i]
            if cmd[0] == '.:' and cmd[1] == oldlabel:
                if i > 0 and cmds[i-1][0] in jump and i < (len(cmds) - 1) and cmds[i+1][0] == 'POP_TOP':
                  del cmds[i]
                  del cmds[i]
                  continue
                else:    
                  del cmds[i]
                if i > 0 and cmds[i][0] == '.L' and cmds[i-1][0] == '.L':
                    del cmds[i]
                    continue
                return
            i = i + 1
            
def gen_new_label(cmds):
    return max( [x[1] for x in cmds if x[0] == '.:']) + 1

def after_label(cmds, label, n):
    i = 0
    while i < len(cmds):            
        cmd = cmds[i]
        if cmds[i][0] == '.:' and cmds[i][1] == label:
            return cmds[i:i+n], i
        i = i + 1
        
def pos_label(cmds, label):
    i = 0
    while i < len(cmds):            
        cmd = cmds[i]
        if cmds[i][0] == '.:' and cmds[i][1] == label:
            return i
        i = i + 1
        
def NoGoToGo(cmds):
    while True:
        crossjump = {}
        updated = False
        for i in range(len(cmds) - 1):
            a,b = cmds[i], cmds[i+1]
            if a[0] == '.:' and ((b[0] == 'JUMP_ABSOLUTE' or \
                                  b[0] in jump) and a[1] != b[1]):
                crossjump[a[1]] = b[1]
        loopes = {}
        for i in range(len(cmds)):
            a = cmds[i]
            if a[0] in ('J_SETUP_LOOP', 'J_SETUP_LOOP_FOR') and a[1] in crossjump:
                loopes[a[1]] = i
        i = 0
        while i < len(cmds):   
            pre_cmd = ('',)
            if i > 0:
                pre_cmd = cmds[i-1]         
            cmd = cmds[i]
            if cmd[0][0] == 'J' and cmd[1] in crossjump: 
                if cmd[1] not in loopes or (cmd[1] in loopes and loopes[cmd[1]] > i):
                    oldlabel = cmd[1]
                    cmds[i] = (cmd[0], crossjump[cmd[1]]) + cmd[2:]
                    del_if_unused_label(cmds, oldlabel)
                    updated = True
                    continue
            i = i + 1
        if not updated:
            return    
 
def NoGoToReturn(cmds):
    crossjump = {}
    return None
    for i in range(len(cmds) - 1):
        a,b = cmds[i], cmds[i+1]
        if a[0] == '.:' and b[0] == 'RETURN_VALUE' and len(b) == 2:
            crossjump[a[1]] = b
        elif a[0] == '.:' and type(b) is list and len(b) == 1 and \
                b[0][0] == 'RETURN_VALUE' and len(b[0]) == 2:
            crossjump[a[1]] = b[0]
        elif a[0] == '.:' and type(b) is list and len(b) == 2 and \
                b[0][0] == '.L' and b[1][0] == 'RETURN_VALUE' and len(b[0]) == 2:
            crossjump[a[1]] = b[1]
    i = 0
    while i < len(cmds):   
        pre_cmd = ('',)
        if i > 0:
            pre_cmd = cmds[i-1]         
        cmd = cmds[i]
        if cmd[0] in jump and cmd[1] in crossjump: 
                oldlabel = cmd[1]
                cmds[i] = crossjump[cmd[1]]
                if type(cmds[i-1]) is list:
                    cmds[i-1] += [cmds[i]]
                    del cmds[i]    
                del_if_unused_label(cmds, oldlabel)
                continue
        i = i + 1

def consts_from_cmds(cmds):
    return dict.fromkeys([x[1] for x in cmds if x[0] == 'LOAD_CONST']).keys()

def walk(co, match=None):
    if match is None or co.co_name == match:
        dis(co)
    for obj in co.co_consts:
        if type(obj) is types.CodeType:
            walk(obj, match)

def Pynm2Cnm(filename):
    pair = os.path.split(filename)
    nmmodule = nmvar_to_loc(pair[1][:-3])
    outnm = '_c_' + nmmodule + '.c'
    outnm = os.path.join(pair[0], outnm)
    return outnm, nmmodule

def Usage(nm):
    print 'Usage:', nm, '<compiled_filenames.py>'
    
def main():
    global out
    global out3
    global debug
#    global collect_stat
    global filename
    global TRUE
    global no_build
    global print_cline 
    global print_pyline
    global make_indent
    global direct_call
    global stat_func
    global Pass_Exit
    global flag_stat
    global opt_flag
    global start_sys_modules
    global hash_compile
    global hide_debug
    global dirty_iteritems
    global redefined_attribute
    global line_number
    global no_generate_comment
    TRUE = cmd2mem(('LOAD_CONST', True))
    
    debug = False
    codename = None
    argv = sys.argv[1:]
##    gc.enable()
    while len(argv) > 0 and argv[0][0] == '-':
        ## if argv[0] == '-S':
            ## collect_stat = True
            ## argv = argv[1:]
        if argv[0] == '-P_C':
            Pass_Exit = argv[1]
            argv = argv[2:]
        elif argv[0] == '-show-debug':
            hide_debug = False
            argv = argv[1:]
        elif argv[0] == '-dirty-iteritems':
            dirty_iteritems = True
            argv = argv[1:]
        elif argv[0] == '-stat':
            flag_stat = True
            argv = argv[1:]
        elif argv[0] in ('-O', '-O0', '-O1', '-O2', '-O3'):
            opt_flag = argv[0]
            argv = argv[1:]
        elif argv[0] == '-no-line-numbers':
            line_number = False    
            argv = argv[1:]
        elif argv[0] == '-no-generate-comment':
            no_generate_comment = True    
            argv = argv[1:]
        elif argv[0] == '-c':
            no_build = True
            argv = argv[1:]
        elif argv[0] == '-d':
            debug = True
            argv = argv[1:]
        elif argv[0] == '-i':
            make_indent = True
            argv = argv[1:]
        elif argv[0] == '-l':
            print_cline = True
            print_pyline = True
            argv = argv[1:]
        elif argv[0] == '-L':
            print_cline = False
            print_pyline = True
            argv = argv[1:]
        elif argv[0] == '--stat-func':
            stat_func = argv[1]
            argv = argv[2:]
        elif argv[0] == '-nd':
            direct_call = False
            argv = argv[1:]
        else:    
            Usage(sys.argv[0])
            exit(1)
    if len(argv) == 0:
        Usage(sys.argv[0])
        exit(1)
    filenames = argv[0:]
    listf1 = []
    for filename in filenames:    
        listf = glob.glob(filename)
        listf1.extend(listf)
    listf = listf1 
    if len(listf) == 0:
        print 'Files not found'
        exit(1)
    start_sys_modules = sys.modules.copy()   
    for filename in listf:          
        clear_one_file()
        compilable = True
        if filename.endswith('.py') or filename.endswith('.PY'):
            print 'Compile', filename
            buf = open(filename).read()
            redefined_attribute =  ( '__slots__' in buf or '__get__' in buf or \
                                    '__set__' in buf or '__delete__' in buf or \
                                    '__getattribute__' in buf or \
                                    '__delattr__' in buf or '__getattr__' in buf or \
                                    '__delattr__' in buf )\
                                        and filename != '2c.py'
            outnm = filename[:-3] + '.pycmd'
            out = open(outnm, 'w')
            outnm, nmmodule = Pynm2Cnm(filename)
            out3 = open(outnm, 'w')
            is_compile = True
            hash_compile = hash(buf) 
            try:
                co = compile(buf, filename, "exec")
            except SyntaxError:
                buf = buf.replace('\r\n', '\n')
                is_compile = False
            if not is_compile:    
                try:
                    co = compile(buf, filename, "exec")
                except:
                    print 'Error in', filename  
                    compilable = False
            if compilable:   
                if co.co_flags & 0x10000:
                    import __builtin__ as b
                    d_built['print'] = b.__dict__["print"]
                    b = None
                else:
                    if 'print' in d_built:
                        del d_built['print']    
                SetPass('DisAssemble')
##                try:
                walk(co)
                
                post_disassemble()
                ## except AssertionError:
                    ## print 'Assert error'
                    ## return    
#                finally:    
                ## l = list(Iter3(None,None, None))
                ## l.sort()
                ## pprint.pprint(l)
                clear_one_file()
                co = None
                current_co = None
                if out is not None:
                    out.close()
                if out3 is not None:    
                    out3.close()
##                gc.set_debug(gc.DEBUG_LEAK)    
                gc.collect()    
#            if decompile_fail:         
#                print filename, 'Decompilation error'
#                decompile_fail = False  
            ## out.close()
            ## out3.close()
#            gc.collect()
    ## if collect_stat:
        ## printcmpstat()  
    link_c()    
    co = compile('print 1\n', 'test.py', "exec")
    clear_after_all_files()
    co = None
    current_co = None
#    if generate_declaration:
#        output_dcl()          
        
def And_j_s(a,b):
    a,b = cmd2mem(a), cmd2mem(b)
    if a[0] == '!BOOLEAN' == b[0]:
        return ('!BOOLEAN', And_bool(a,b))
    if b[0] == '!AND_JUMPED_STACKED':
        return ('!AND_JUMPED_STACKED', a) + b[1:]
    if a[0] == '!AND_JUMPED_STACKED':
        return a + (b,)
    return ('!AND_JUMPED_STACKED', a,b)
        
def Or_j_s(a,b):
    a,b = cmd2mem(a), cmd2mem(b)
    if a[0] == '!BOOLEAN' == b[0]:
        return ('!BOOLEAN', Or_bool(a,b))
    if b[0] == '!OR_JUMPED_STACKED':
        return ('!OR_JUMPED_STACKED', a) + b[1:]
    if a[0] == '!OR_JUMPED_STACKED':
        return a + (b,)
    return ('!OR_JUMPED_STACKED', a,b)

def And_j(a,b):
    a,b = cmd2mem(a), cmd2mem(b)
    if a[0] == '!BOOLEAN' == b[0]:
        return ('!BOOLEAN', And_bool(a,b))
    if b[0] == '!AND_JUMP' == a[0]:
        return  a + b[1:]
    if b[0] == '!AND_JUMP':
        return ('!AND_JUMP', a) + b[1:]
    if a[0] == '!AND_JUMP':
        return a + (b,)
    return ('!AND_JUMP', a,b)

def And_bool(a,b):
    a,b = cmd2mem(a), cmd2mem(b)
    if b[1][0] == '!AND_BOOLEAN' == a[1][0]:
        return  a[1] + b[1][1:]
    if b[1][0] == '!AND_BOOLEAN':
        return ('!AND_BOOLEAN', a) + b[1][1:]
    if a[1][0] == '!AND_BOOLEAN':
        return a[1] + (b,)
    return ('!AND_BOOLEAN', a,b)

def Or_j(a,b):
    a,b = cmd2mem(a), cmd2mem(b)
    if a[0] == '!BOOLEAN' == b[0]:
        return ('!BOOLEAN', Or_bool(a,b))
    if b[0] == '!OR_JUMP' == a[0]:
        return  a + b[1:]
    if b[0] == '!OR_JUMP':
        return ('!OR_JUMP', a) + b[1:]
    if a[0] == '!OR_JUMP':
        return a + (b,)
    return ('!OR_JUMP', a,b)

def Or_bool(a,b):
    a,b = cmd2mem(a), cmd2mem(b)
    if b[1][0] == '!OR_BOOLEAN' == a[1][0]:
        return  a[1] + b[1][1:]
    if b[1][0] == '!OR_BOOLEAN':
        return ('!OR_BOOLEAN', a) + b[1][1:]
    if a[1][0] == '!OR_BOOLEAN':
        return a[1] + (b,)
    return ('!OR_BOOLEAN', a,b)
        
def Not(b):    
    if b[0] == '!1NOT':
        return b[1]
    return ('!1NOT', b)

def formire_call(t):
    if '(' in t[2] and ')' in t[2]:
        if t[2][-1] == ')':
            t = list(t)
            i = t[2].index('(')
            t[2] = t[2][0:-1]
            i = t[2].index('(')
            t[2:3] = [t[2][:i], '(', t[2][i+1:]]
            t = tuple(t) + (')',)   
    elif t[2][-1] != ')':        
        if t[2][-1] == '(':
            t = list(t)
            t[2] = t[2][0:-1]
            t = tuple(t)   
        t = list(t)      
        t[2:3] = [t[2], '(']
        i = 4
        while i < len(t)-1:
            if t[i+1] != ',':
                t[i:i+1] = [t[i], ',']
            i += 2
        t = tuple(t) + (')',)
    return t    

class Out(list):
    def append_cline(self):
        if print_cline :
            self.append('if (PyErr_Occurred()) {printf (\"ERROR %s\\n\",PyObject_REPR(PyErr_Occurred()));}')
            self.append('printf (\"cline %d\\n\", __LINE__);')
    def Cls(self, *vv):
        for v in vv:
            if istempref(v):
                clearref(self, v)
            elif istemptyped(v):
                clear_typed(v)
            else:
                pass
    def ZeroTemp(self, g):
        if istempref(g):
            self.Raw(g, ' = 0;')
            if len(self) > 1 and self[-1] == self[-2]:
                del self[-1]

    def CLEAR(self, ref): 
        assert istempref(ref) or ref.startswith('temp_') or ref.startswith('GETLOCAL(') or ref.startswith('GETFREEVAR(')    
        self.append('Py_CLEAR(' + CVar(ref) + ');')

    def INCREF(self, ref): 
##        assert istempref(ref)       
        self.append('Py_INCREF(' + CVar(ref) + ');')
    def DECREF(self, ref): 
##        assert istempref(ref)       
        self.append('Py_DECREF(' + CVar(ref) + ');')
    def XINCREF(self, ref): 
##        assert istempref(ref)       
        self.append('Py_XINCREF(' + CVar(ref) + ');')
        
    def ClsFict(self, v):
        if istempref(v):
            clearref(self, v, True)
        elif istemptyped(v):
            clear_typed(v)
        else:
            pass
    def Comment(self, it):
        if no_generate_comment:
            return None
        if not isinstance(it, types.StringTypes):
            stream = StringIO.StringIO()
            pprint.pprint(it, stream, 1, 98)
            ls = stream.getvalue().split('\n')
            if ls[-1] == '':
                del ls[-1]
            stream.close()
            self.append('')
            for iit in ls:
                iit = iit.replace('/*', '/?*').replace('*/', '*?/')    
                s = '/* ' + iit + ' */'    
                self.append(s)
                
    def check_err(self, t0, eq):
        self.Raw('if (', t0, ' == ', eq, ') goto ', labl, ';')
        ## add2 = ('if (', t0, '==', eq, ') goto', labl)
        UseLabl()
        ## s = do_str(add2)
        ## self.append(s)

    def Raw(self, *t):
        s = ''
        for it in t:
            s += CVar(it)
        self.append(s)
                
    def Stmt(self, *t):
        if len(t) == 1 and t[0] == '':
            self.append('')
            return self
        elif len(t) == 2 and t[0] == 'CLEARREF' and istempref(t[1]):
            t = ('CLEARTEMP('+str(t[1][1]) + ')',)
        elif len(t) == 3 and type(t[0]) is tuple and IsCalcConst(t[0]) and t[1] == '=':
            t = tuple([CVar(x) for x in t])
            s = do_str(t)
            self.append(s)
            self.append_cline()
            return
            
        elif t[0] in CFuncVoid:
            Used(t[0])
            t2 = [t[0], '(']
            for v in t[1:]:
                t2.append(v)
                t2.append(',')
            if len(t) == 1:
                t2.append(')')    
            t2 = t2[:-1]
            t2.append(')')
            t = tuple([CVar(x) for x in t2])
            s = do_str(t)
            self.append(s)
            self.append_cline()
            return self

        elif t[0] in CFuncIntCheck:
            Used(t[0])
            t2 = mk_t2(t)
            t2.append(') == -1) goto ' + CVar(labl))
            UseLabl()
            t = tuple([CVar(x) for x in t2])
            s = do_str(t)
            self.append(s)
            self.append_cline()
            return self
        elif t[0] in CFuncIntAndErrCheck:
            Used(t[0])
            t2 = mk_t2(t)
            t2.append(') == -1 && PyErr_Occurred()) goto ' + CVar(labl))
            UseLabl()
            t = tuple([CVar(x) for x in t2])
            s = do_str(t)
            self.append(s)
            self.append_cline()
            return self
        elif t[0] in CFuncPyObjectRef:
            Used(t[0])
            t2 = mk_t2(t)
            assert labl is not None
            t2.append(') == NULL) goto ' + CVar(labl))
            UseLabl()
            t = tuple([CVar(x) for x in t2])
            s = do_str(t)
            self.append(s)
            self.append_cline()
            return self
        elif len(t) >= 3 and t[1] == '=' and t[0] != 'f->f_lineno' and \
               (type(t[2]) != int and type(t[2]) != long and (type(t[2]) != tuple or t[2][0] != 'CONST')):
            if len(t) == 5 and t[3] in ('==', '!='):       
                t = tuple([CVar(x) for x in t])
                s = do_str(t)
                self.append(s)
                self.append_cline()
                return
            if len(t) == 3 and t[2][0] == 'FAST' and t[0][0] == 'PY_TEMP':
                t = tuple([CVar(x) for x in t])
                s = do_str(t)
                self.append(s)
                self.append_cline()
                return
            if len(t) == 4 and t[2][0] == '!' and t[0][0] == 'TYPED_TEMP' and t[3][0] == 'TYPED_TEMP':
                t = tuple([CVar(x) for x in t])
                s = do_str(t)
                self.append(s)
                self.append_cline()
                return
            if istemptyped(t[2]) and istemptyped(t[0]):
                t = tuple([CVar(x) for x in t])
                s = do_str(t)
                self.append(s)
                self.append_cline()
                return self    
            if istempref(t[0]) and t[2] in ('Py_True', 'Py_False'):
                t = tuple([CVar(x) for x in t])
                s = do_str(t)
                self.append(s)
                self.append_cline()
                return self    
            if type(t[2]) is str and t[2].endswith('(glob,'):
                t = list(t)
                t[2:3] = [t[2][:-6], 'glob']
                t = tuple(t)
            t = formire_call(t)
            if t[2] in CFuncNoCheck:
                Used(t[2])
                assign_py = t[0][0] == 'PY_TEMP'                
                t = tuple([CVar(x) for x in t])
                s = do_str(t)
                self.append(s)
                self.append_cline()
                if assign_py:
                    if t[2] not in ( 'PyIter_Next', 'Py_INCREF'):
                       Fatal(t, '???', t[2], 'Py_INCREF(' + t[0] + ');')
                elif t[2] not in CFuncIntNotCheck and t[2] not in CFuncFloatNotCheck \
                     and t[2] not in CFuncLongNotCheck:    
                    Fatal(t)
                return self                   

            if t[2] in CFuncPyObjectRef:
                Used(t[2])
                assign_py = type(t[0]) is tuple and \
                    (t[0][0] == 'PY_TEMP' or t[0][:9] == 'GETLOCAL(')
                t = tuple([CVar(x) for x in t])
                s = do_str(t)
                self.append(s)
                self.append_cline()
                if assign_py:
                    if self[-1].startswith(ConC(t[0], ' = ')) and self[-1].endswith(';'):
                        s0 = '(' + self[-1][:-1] + ')'
                        del self[-1]
                        self.check_err(s0, 'NULL')
                    else:    
                        self.check_err(t[0], 'NULL')
                    if t[2] in CFuncNeedINCREF:
                        s = 'Py_INCREF(' + t[0] + ');'
                        self.append(s)
                    elif not t[2] in CFuncNotNeedINCREF:
                        s = 'Py_INCREF(' + t[0] + ');'
                        Debug('INCREF?', t)
                        self.append(s)
                    if checkmaxref != 0:
                        self.append('if ((' + t[0] + ')->ob_refcnt > ' + str(checkmaxref) + ') printf("line %5d, refcnt %6d \\n", __LINE__,(' + t[0] + ')->ob_refcnt);')
                else:    
                    Fatal(t)
                return self                   
            if t[2] in set_IntCheck: #CFuncIntCheck or t[2] in CFuncLongCheck:
                Used(t[2])
                assign_temp = t[0][0] == 'TYPED_TEMP'                
                t = tuple([CVar(x) for x in t])
                s = do_str(t)
                self.append(s)
                self.append_cline()
                if assign_temp:
                    if self[-1].startswith(ConC(t[0], ' = ')) and self[-1].endswith(';'):
                        s0 = '(' + self[-1][:-1] + ')'
                        del self[-1]
                        self.check_err(s0, '-1' if t[2] not in CFuncIntAndErrCheck else '-1 && PyErr_Occurred()')
                    else:    
                        self.check_err(t[0], '-1' if t[2] not in CFuncIntAndErrCheck else '-1 && PyErr_Occurred()')
#                    self.check_err(t[0], '-1' if t[2] not in CFuncIntAndErrCheck else '-1 && PyErr_Occurred()')
                else:    
                    Fatal(t)
                return self     
            elif type(t[2]) is str and t[2].startswith('_Direct_'):
                assign_py = type(t[0]) is tuple and \
                    (t[0][0] == 'PY_TEMP' or t[0][:9] == 'GETLOCAL(')
                t = tuple([CVar(x) for x in t])
                s = do_str(t)
                self.append(s)
                self.append_cline()
                if assign_py:
                    if self[-1].startswith(ConC(t[0], ' = ')) and self[-1].endswith(';'):
                        s0 = '(' + self[-1][:-1] + ')'
                        del self[-1]
                        self.check_err(s0, 'NULL')
                    else:    
                        self.check_err(t[0], 'NULL')
                    if checkmaxref != 0:
                        self.append('if ((' + t[0] + ')->ob_refcnt > ' + str(checkmaxref) + ') printf("line %5d, refcnt %6d \\n", __LINE__,(' + t[0] + ')->ob_refcnt);')
                else:    
                    Fatal(t)
                return self                   
            Fatal('Call undefined C-function', t[2], t)
        elif t[0] == 'if':
            pass
        elif t[0] in ( '}', '{'):
            pass
        elif maybe_call(t[0]):
            t = list(t)      
            t[0:1] = [t[0], '(']
            i = 2
            while i < len(t)-1:
                if t[i+1] != ',':
                   t[i:i+1] = [t[i], ',']
                i += 2
            t = tuple(t) + (')',)
            Used(t[0])
            if t[0] not in CFuncVoid:
                Fatal('Call undefined C-function', t[0],t)
        t = tuple([CVar(x) for x in t])  
        s = do_str(t)  
        self.append(s)

def ConC(*t):
    s = ''
    for it in t:
        s += CVar(it)
    return s


def mk_t2(t):
    t2 = ['if (', t[0], '(']
    for v in t[1:]:
        t2.append(v)
        t2.append(',')
    if len(t) == 1:
        t2.append(')')    
    return t2[:-1]

def maybe_call(to):
    return to != 'f->f_lineno' and not istempref(to) and \
               not istemptyped(to) and to[0] not in ('{', '}') and\
               to[-1] not in ('{', '}') and to[0:3] != 'if ' and \
               to not in ('continue;', 'break;', 'return') and \
               to[0:4] not in ('for ', 'for(') and to != 'goto' 

def do_str(add2):
    add2 = tuple([CVar(x) for x in add2]) 
    s = ''
    if add2[0] in ('{', '}') and len(add2) == 1:
        return add2[0]
    for i, st in enumerate(add2):
        if i != len(add2)-1:
            s += st + ' '
        elif st[-1] in ('{', '}'):
            s += st    
        else:
            if st[-1] != ';':
                s += st + ';' 
            else:
                s += st  
    ## cons = [const_by_n(int(x[7:-1])) 
                 ## for x in add2 if x.startswith('consts[') and \
                                  ## x.endswith(']') ]
    ## cons = [x for x in cons if type(x) != types.CodeType]                         
    ## if len (cons) > 0 and not no_generate_comment:
        ## s += ' /* '
        ## for cco in cons:
            ## s += repr(cco).replace('/*', '/?*').replace('*/', '*?/') + ', '
        ## s += ' */'    
    return s        

def label_method_class(co):
    nm_for_c = C2N(co)
    if Is3(None, ('Method', co.co_name), nm_for_c) and\
       not Is3(None, ('ClassMethod', co.co_name), nm_for_c) and\
       not Is3(None, ('StaticMethod', co.co_name), nm_for_c) and \
       co.co_argcount > 0 and len(co.co_cellvars) == 0 and len(co.co_freevars) == 0 and\
       len(co.co_varnames) > 0 and co.co_varnames[0] == 'self':
       
        li = list(Iter3(None, ('Method', co.co_name), nm_for_c))
        assert len(li) == 1
        cl = li[0][0]
        all_co[co].method_class = cl
        if Is3(cl, 'CalcConstNewClass') and not Is3(cl, 'CalcConstOldClass'):
            all_co[co].method_new_class = True
            all_co[co].method_any_class = True
        elif Is3(cl, 'CalcConstOldClass') and not Is3(cl, 'CalcConstNewClass') :
            all_co[co].method_old_class = True
            all_co[co].method_any_class = True
    

def generate(cmds, co, filename_, nm_for_c):
    global filename, func, tempgen, typed_gen, _n2c, pregenerated,\
            genfilename, current_co, is_direct_current, Line2Addr
    assert len(cmds) == 2
    func = nm_for_c
    filename = filename_
    
    genfilename, nmmodule = Pynm2Cnm(filename)
    if not can_generate_c(co): ##co.co_flags & CO_GENERATOR:
        stub_generator(co)
        return
    is_direct_current = False
    del tempgen[:]
    del typed_gen[:]
    o = Out()
    global try_jump_context, dropped_temp
    del try_jump_context[:]
    del dropped_temp[:]
    label_exc = New('label')
    set_toerr_new(o, label_exc)
    current_co = co
    Line2Addr = line2addr(co)


    if Is3(func, 'ArgCallCalculatedDef') and direct_call:
        seq2 = all_co[co].direct_cmds
        hidden = all_co[co].hidden_arg_direct
        if seq2 == cmds[1] and len(hidden) == 0:
            generate_from_frame_to_direct_stube(co, o, nm_for_c, cmds)
            return
    ## if Is3(None, ('Method', co.co_name), nm_for_c):
        ## li = list(Iter3(None, ('Method', co.co_name), nm_for_c))
        ## assert len(li) == 1
        ## cl = li[0][0]
        ## if Is3(cl, 'CalcConstNewClass'):
            ## is_new_class = True
        ## elif Is3(cl, 'CalcConstOldClass'):
            ## is_new_class = False
        ## print 'Not direct method %s (%s) of %s' % (co.co_name, nm_for_c, cl)    
    if stat_func == func:
        o.Raw('{')
        o.Raw('FILE * _refs = fopen(\"%s_start\", \"w+\");' % func)
        o.Raw('_Py_PrintReferences2(_refs);')   
        o.Raw('fclose(_refs);')     
        o.Raw('}')
    o = generate_list(cmds[1], o)
    generate_default_exception_handler(o)
    o.Raw('}')
    set_toerr_back(o)
    generate_header(cmds[0][1], o, co, len(tempgen), typed_gen)
    pregenerated.append((cmds, o, co, cmds[0][1], nm_for_c))    

def concretize_code_direct_call(nm, seq, co):
    calls = [c for a,b,c in Iter3(nm, 'ArgCallCalculatedDef', None)]
    call = join_defined_calls(calls, co.co_argcount, nm, (co.co_flags & 0x4) != 0)

    srepr = repr(seq)
    for i, arg in enumerate(call):
        assert i < co.co_argcount or (co.co_flags & 0x4 and i == co.co_argcount)
        s = ('STORE_FAST', co.co_varnames[i])
        if repr(s) in srepr:
            call[i] = None
        s = ('DELETE_FAST', co.co_varnames[i])
        if repr(s) in srepr:
            call[i] = None
    seq2 = seq[:]            
    for i, arg in enumerate(call):
        if type(arg) is tuple and arg[0] == 'CONST':
            seq2 = replace_subexpr(seq2, ('FAST', co.co_varnames[i]), arg)
        elif arg is not None and arg != (None, None):
            seq2 = replace_subexpr(seq2, ('FAST', co.co_varnames[i]), ('PY_TYPE',) + arg + (('FAST', co.co_varnames[i]),None))
    seq2 = tree_pass(seq2, upgrade_repl, None, nm) 
    seq2 = recursive_type_detect(seq2, nm) 
    if co.co_flags & 0x4:
        hidden = []
    else:    
        hidden = [i for i, arg in enumerate(call) if type(arg) is tuple and arg[0] == 'CONST']
    seq2 = tree_pass(seq2, upgrade_repl, None, nm)         
    return seq2, hidden    

def generate_direct(cmds, co, filename_, nm_for_c):
    global filename, func, tempgen, typed_gen, _n2c, pregenerated,\
            genfilename, current_co, is_direct_current
    assert len(cmds) == 2
    func = nm_for_c
    filename = filename_
    genfilename, nmmodule = Pynm2Cnm(filename)
    if not can_generate_c(co): ##co.co_flags & CO_GENERATOR:
        stub_generator(co)
        return

    is_direct_current = False
    if Is3(func, 'ArgCallCalculatedDef') and direct_call:
        is_direct_current = True
    else:
        return None

    del tempgen[:]
    del typed_gen[:]
    o = Out()
    global try_jump_context, dropped_temp
    del try_jump_context[:]
    del dropped_temp[:]
    label_exc = New('label')
    set_toerr_new(o, label_exc)
    current_co = co
    
    seq2 = all_co[co].direct_cmds
    hidden = all_co[co].hidden_arg_direct
    if stat_func == func:
        o.Raw('{')
        o.Raw('FILE * _refs = fopen(\"%s_start\", \"w+\");' % func)
        o.Raw('_Py_PrintReferences2(_refs);')   
        o.Raw('fclose(_refs);')     
        o.Raw('}')     
    o = generate_list(seq2, o)
    generate_default_exception_handler(o)
    o.Raw('}')
    set_toerr_back(o)
    generate_header_direct(cmds[0][1], o, co, len(tempgen), typed_gen, hidden)
    pregenerated.append((cmds, o, co, cmds[0][1], nm_for_c))    

def generate_default_exception_handler(o):  
    if Is3(func, 'UseLabel', labl):        
        o.Stmt('if (0) { ', labl, ':')
        if not is_direct_current:
            o.Raw('PyTraceBack_Here(f);')
            ## if c_line_exceptions:
                ## o += 'printf(\"Handle raise at C line ' + func +' %d from %d\\n\", __LINE__, f->f_lineno);'
                ## o += 'if (PyErr_Occurred()) {printf (\"ERROR %s\\n\",PyObject_REPR(PyErr_Occurred()));}'
            ## o += 'if (tstate->c_tracefunc != NULL)'
            ## Used('from_ceval_call_exc_trace')
            ## o += 'from_ceval_call_exc_trace(tstate->c_tracefunc, tstate->c_traceobj, f);'

        else:    
            cod = const_to(current_co)
            Used('Direct_AddTraceback')
            if line_number:
                o.Raw('Direct_AddTraceback((PyCodeObject *)', cod, ', PyLine, PyAddr);') 
            else:
                o.Raw('Direct_AddTraceback((PyCodeObject *)', cod, ', 0, 0);') 
                ## if c_line_exceptions:
                    ## o += 'printf(\"Handle raise at C line ' + func +' %d from %d\\n\", __LINE__, PyLine);'
                    ## o += 'if (PyErr_Occurred()) {printf (\"ERROR %s\\n\",PyObject_REPR(PyErr_Occurred()));}'

        if is_direct_current:
            for i,v in enumerate(current_co.co_varnames):
                nmvar = nmvar_to_loc(v)
                o.CLEAR('GETLOCAL(' + nmvar + ')')

        for i in range(len(tempgen)):
            o.Raw('CLEARTEMP(', str(i), ');')
        if calc_ref_total:
            o.Raw('if ((_Py_RefTotal - l_Py_RefTotal) > 0) {printf ("func ', current_co.co_name, ' delta ref = %d\\n", (int)(_Py_RefTotal - l_Py_RefTotal));}')
        if not is_direct_current:
            if check_recursive_call:
                o.Raw('Py_LeaveRecursiveCall();')
        if not is_direct_current:
            o.Raw('tstate->frame = f->f_back;')
        if is_direct_current and IsRetVoid(all_co[current_co].cmds[0][1]):
            o.Raw('return -1;')        
        else:    
            o.Stmt('return', 'NULL;')        
        o.Raw('}')        
      
c_head = """
/* Generated by 2C Python */

#include "Python.h"
#include "frameobject.h" 
#include "funcobject.h" 
#include "code.h" 
#include "opcode.h" 
#include "dictobject.h" 
#include "listobject.h" 
#include "abstract.h" 

#include "structmember.h"
#include "object.h"

PyTypeObject Py2CCode_Type;

PyTypeObject Py2CFunction_Type;

#define Py2CCode_Check(op) (Py_TYPE(op) == &Py2CCode_Type)
#define Py2CFunction_Check(op) (Py_TYPE(op) == &Py2CFunction_Type)


/* Bytecode object */
typedef struct {
    PyCodeObject _body;
    void *co_function;        /* Python code compiled to C function */
} Py2CCodeObject;

/* Public interface */
static Py2CCodeObject * Py2CCode_New(
	int, int, int, int, PyObject *, PyObject *, PyObject *, PyObject *,
	PyObject *, PyObject *, PyObject *, PyObject *, int, PyObject *, void *); 

static PyObject * b = NULL;
static PyObject * bdict = NULL;


/*#define DEBUG_LOCAL_REFCNT*/

/* Local variable macros */
#ifdef DEBUG_LOCAL_REFCNT
#define GETLOCAL(i)	(printf("Get local %s line %5d refcnt %d\\n", #i, __LINE__, fastlocals[Loc_##i]->ob_refcnt),(fastlocals[Loc_##i]))
#else
#define GETLOCAL(i)	(fastlocals[Loc_##i])
#endif
#define GETFREEVAR(i)	(freevars[Loc2_##i])
/* The SETLOCAL() macro must not DECREF the local variable in-place and
   then store the new value; it must copy the old value to a temporary
   value, then store the new value, and then DECREF the temporary value.
   This is because it is possible that during the DECREF the frame is
   accessed by other code (e.g. a __del__ method or gc.collect()) and the
   variable would be pointing to already-freed memory. */
#ifdef DEBUG_LOCAL_REFCNT
#define SETLOCAL(i, value)	do { PyObject *tmp = fastlocals[Loc_##i]; \
                                     if (tmp != NULL) \
                                     printf("Replace local %s line %5d refcnt %d\\n", #i, __LINE__, tmp->ob_refcnt);\
				     fastlocals[Loc_##i] = value; \
                                     printf("New local %s line %5d refcnt %d\\n", #i, __LINE__, fastlocals[Loc_##i]->ob_refcnt);\
                                     Py_XDECREF(tmp); } while (0)
#else
#define SETLOCAL_(i, value)	do { PyObject *tmp = fastlocals[Loc_##i]; \
				     fastlocals[Loc_##i] = value; \
                                     Py_XDECREF(tmp); } while (0)
                                     
#define SETLOCAL(i, value)	do { Py_XDECREF(fastlocals[Loc_##i]); \
				     fastlocals[Loc_##i] = value; \
                                     } while (0)
#endif
#define COPYTEMP(new, old)	do { new = old; \
				     old = NULL; } while (0)
#define CLEARTEMP(x) Py_CLEAR(temp_##x)

typedef char *charref;
static PyObject * consts[]; 
static PyObject * loaded_builtin[];
static PyObject * calculated_const[];
static PyObject * glob;
static PyObject * empty_tuple;
/*void static check_const_refcnt(void);*/

/* Status code for main loop (reason for stack unwind) */
enum why_code {
		WHY_NOT =	0x0001,	/* No error */
		WHY_EXCEPTION = 0x0002,	/* Exception occurred */
		WHY_RERAISE =	0x0004,	/* Exception re-raised by 'finally' */
		WHY_RETURN =	0x0008,	/* 'return' statement */
		WHY_BREAK =	0x0010,	/* 'break' statement */
		WHY_CONTINUE =	0x0020,	/* 'continue' statement */
		WHY_YIELD =	0x0040	/* 'yield' operator */
};

#define NAME_ERROR_MSG \
	"name '%.200s' is not defined"
#define GLOBAL_NAME_ERROR_MSG \
	"global name '%.200s' is not defined"
#define UNBOUNDLOCAL_ERROR_MSG \
	"local variable '%.200s' referenced before assignment"
#define UNBOUNDFREE_ERROR_MSG \
	"free variable '%.200s' referenced before assignment" \
        " in enclosing scope"

#define c_PyCmp_GT_Int(v,l,w) ((PyInt_CheckExact(v))?(PyInt_AS_LONG(v) > l) : (PyObject_RichCompareBool(v, w, PyCmp_GT)))
#define c_PyCmp_LT_Int(v,l,w) ((PyInt_CheckExact(v))?(PyInt_AS_LONG(v) < l) : (PyObject_RichCompareBool(v, w, PyCmp_LT)))
#define c_PyCmp_GE_Int(v,l,w) ((PyInt_CheckExact(v))?(PyInt_AS_LONG(v) >= l) : (PyObject_RichCompareBool(v, w, PyCmp_GE)))
#define c_PyCmp_LE_Int(v,l,w) ((PyInt_CheckExact(v))?(PyInt_AS_LONG(v) <= l) : (PyObject_RichCompareBool(v, w, PyCmp_LE)))
#define c_PyCmp_EQ_Int(v,l,w) ((PyInt_CheckExact(v))?(PyInt_AS_LONG(v) == l) : (PyObject_RichCompareBool(v, w, PyCmp_EQ)))
#define c_PyCmp_NE_Int(v,l,w) ((PyInt_CheckExact(v))?(PyInt_AS_LONG(v) != l) : (PyObject_RichCompareBool(v, w, PyCmp_NE)))

#define c_PyCmp_EQ_String(v,l,w,w2) ((PyString_CheckExact(v))?(PyString_GET_SIZE(v) == l && memcmp(PyString_AS_STRING(v),w,l) == 0) : (PyObject_RichCompareBool(v, w2, PyCmp_EQ)))
#define c_PyCmp_NE_String(v,l,w,w2) ((PyString_CheckExact(v))?(PyString_GET_SIZE(v) != l || memcmp(PyString_AS_STRING(v),w,l) != 0) : (PyObject_RichCompareBool(v, w2, PyCmp_NE)))

#define _c_PyCmp_EQ_String(v,l,w)  ((PyString_GET_SIZE(v) == l) && memcmp(PyString_AS_STRING(v),w,l) == 0) 
#define _c_PyCmp_NE_String(v,l,w)  ((PyString_GET_SIZE(v) != l) || (memcmp(PyString_AS_STRING(v),w,l) != 0)) 

#define FirstCFunctionCall(a,b,c)  ((PyCFunction_Check (a)) ? ( PyCFunction_Call(a,b,c) ) : ( PyObject_Call(a,b,c) ))

static void patch_code2c(void);

static PyObject *
PyImport_Exec2CCodeModuleEx(char *name, PyObject *co);


"""
c_tail = """

#define NAME_CHARS \
	"0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz"

/* all_name_chars(s): true iff all chars in s are valid NAME_CHARS */

static int
all_name_chars(unsigned char *s)
{
	static char ok_name_char[256];
	static unsigned char *name_chars = (unsigned char *)NAME_CHARS;

	if (ok_name_char[*name_chars] == 0) {
		unsigned char *p;
		for (p = name_chars; *p; p++)
			ok_name_char[*p] = 1;
	}
	while (*s) {
		if (ok_name_char[*s++] == 0)
			return 0;
	}
	return 1;
}

static void
intern_strings(PyObject *tuple)
{
	Py_ssize_t i;

	for (i = PyTuple_GET_SIZE(tuple); --i >= 0; ) {
		PyObject *v = PyTuple_GET_ITEM(tuple, i);
		if (v == NULL || !PyString_CheckExact(v)) {
			Py_FatalError("non-string found in code slot");
		}
		PyString_InternInPlace(&PyTuple_GET_ITEM(tuple, i));
	}
}

static Py2CCodeObject *
Py2CCode_New(int argcount, int nlocals, int stacksize, int flags,
	   PyObject *code, PyObject *consts, PyObject *names,
	   PyObject *varnames, PyObject *freevars, PyObject *cellvars,
	   PyObject *filename, PyObject *name, int firstlineno,
	   PyObject *lnotab, void * func)
{
	PyCodeObject *co;
	Py_ssize_t i;
	/* Check argument types */
	if (argcount < 0 || nlocals < 0 ||
	    code == NULL ||
	    consts == NULL || !PyTuple_Check(consts) ||
	    names == NULL || !PyTuple_Check(names) ||
	    varnames == NULL || !PyTuple_Check(varnames) ||
	    freevars == NULL || !PyTuple_Check(freevars) ||
	    cellvars == NULL || !PyTuple_Check(cellvars) ||
	    name == NULL || !PyString_Check(name) ||
	    filename == NULL || !PyString_Check(filename) ||
	    lnotab == NULL || !PyString_Check(lnotab) ||
            func == NULL ||
	    !PyObject_CheckReadBuffer(code)) {
		PyErr_BadInternalCall();
		return NULL;
	}
	intern_strings(names);
	intern_strings(varnames);
	intern_strings(freevars);
	intern_strings(cellvars);
	/* Intern selected string constants */
	for (i = PyTuple_Size(consts); --i >= 0; ) {
		PyObject *v = PyTuple_GetItem(consts, i);
		if (!PyString_Check(v))
			continue;
		if (!all_name_chars((unsigned char *)PyString_AS_STRING(v)))
			continue;
		PyString_InternInPlace(&PyTuple_GET_ITEM(consts, i));
	}
	co = (PyCodeObject *)PyObject_NEW(Py2CCodeObject, &Py2CCode_Type);
	if (co != NULL) {
		co->co_argcount = argcount;
		co->co_nlocals = nlocals;
		co->co_stacksize = stacksize;
		co->co_flags = flags;
		Py_INCREF(code);
		co->co_code = code;
		Py_INCREF(consts);
		co->co_consts = consts;
		Py_INCREF(names);
		co->co_names = names;
		Py_INCREF(varnames);
		co->co_varnames = varnames;
		Py_INCREF(freevars);
		co->co_freevars = freevars;
		Py_INCREF(cellvars);
		co->co_cellvars = cellvars;
		Py_INCREF(filename);
		co->co_filename = filename;
		Py_INCREF(name);
		co->co_name = name;
		co->co_firstlineno = firstlineno;
		Py_INCREF(lnotab);
		co->co_lnotab = lnotab;
                co->co_zombieframe = NULL;
                ((Py2CCodeObject *)co)->co_function = func;
	}
	return ((Py2CCodeObject *)co);
}

static PyObject *
code_repr(PyCodeObject *co)
{
	char buf[500];
	int lineno = -1;
	char *filename = "???";
	char *name = "???";

	if (co->co_firstlineno != 0)
		lineno = co->co_firstlineno;
	if (co->co_filename && PyString_Check(co->co_filename))
		filename = PyString_AS_STRING(co->co_filename);
	if (co->co_name && PyString_Check(co->co_name))
		name = PyString_AS_STRING(co->co_name);
	PyOS_snprintf(buf, sizeof(buf),
		      "<code object %.100s at %p(%p), file \\"%.300s\\", line %d>",
		      name, co, ((Py2CCodeObject *)co)->co_function, filename, lineno);
	return PyString_FromString(buf);
}

static int
code_compare(PyCodeObject *co, PyCodeObject *cp)
{
	int cmp;
	cmp = PyObject_Compare(co->co_name, cp->co_name);
	if (cmp) return cmp;
	cmp = co->co_argcount - cp->co_argcount;
	if (cmp) goto normalize;
	cmp = co->co_nlocals - cp->co_nlocals;
	if (cmp) goto normalize;
	cmp = co->co_flags - cp->co_flags;
	if (cmp) goto normalize;
	cmp = co->co_firstlineno - cp->co_firstlineno;
	if (cmp) goto normalize;
	cmp = PyObject_Compare(co->co_code, cp->co_code);
	if (cmp) return cmp;
	cmp = PyObject_Compare(co->co_consts, cp->co_consts);
	if (cmp) return cmp;
	cmp = PyObject_Compare(co->co_names, cp->co_names);
	if (cmp) return cmp;
	cmp = PyObject_Compare(co->co_varnames, cp->co_varnames);
	if (cmp) return cmp;
	cmp = PyObject_Compare(co->co_freevars, cp->co_freevars);
	if (cmp) return cmp;
	cmp = PyObject_Compare(co->co_cellvars, cp->co_cellvars);
	if (cmp) return cmp;
        cmp = ((Py2CCodeObject *)co)->co_function - ((Py2CCodeObject *)cp)->co_function;
	if (cmp) goto normalize;
        return cmp;
	
 normalize:
	if (cmp > 0)
		return 1;
	else if (cmp < 0)
		return -1;
	else
		return 0;
}

static PyObject *
code_richcompare(PyObject *self, PyObject *other, int op)
{
	PyCodeObject *co, *cp;
	int eq;
	PyObject *res;

	if ((op != Py_EQ && op != Py_NE) ||
	    !Py2CCode_Check(self) ||
	    !Py2CCode_Check(other)) {

		/* Py3K warning if types are not equal and comparison
		isn't == or !=  */
		if (PyErr_WarnPy3k("code inequality comparisons not supported "
				   "in 3.x", 1) < 0) {
			return NULL;
		}

		Py_INCREF(Py_NotImplemented);
		return Py_NotImplemented;
	}

	co = (PyCodeObject *)self;
	cp = (PyCodeObject *)other;

	eq = PyObject_RichCompareBool(co->co_name, cp->co_name, Py_EQ);
	if (eq <= 0) goto unequal;
	eq = co->co_argcount == cp->co_argcount;
	if (!eq) goto unequal;
	eq = co->co_nlocals == cp->co_nlocals;
	if (!eq) goto unequal;
	eq = co->co_flags == cp->co_flags;
	if (!eq) goto unequal;
	eq = co->co_firstlineno == cp->co_firstlineno;
	if (!eq) goto unequal;
	eq = PyObject_RichCompareBool(co->co_code, cp->co_code, Py_EQ);
	if (eq <= 0) goto unequal;
	eq = PyObject_RichCompareBool(co->co_consts, cp->co_consts, Py_EQ);
	if (eq <= 0) goto unequal;
	eq = PyObject_RichCompareBool(co->co_names, cp->co_names, Py_EQ);
	if (eq <= 0) goto unequal;
	eq = PyObject_RichCompareBool(co->co_varnames, cp->co_varnames, Py_EQ);
	if (eq <= 0) goto unequal;
	eq = PyObject_RichCompareBool(co->co_freevars, cp->co_freevars, Py_EQ);
	if (eq <= 0) goto unequal;
	eq = PyObject_RichCompareBool(co->co_cellvars, cp->co_cellvars, Py_EQ);
	if (eq <= 0) goto unequal;
	eq = ((Py2CCodeObject *)co)->co_function == ((Py2CCodeObject *)cp)->co_function;
	if (!eq) goto unequal;

	if (op == Py_EQ)
		res = Py_True;
	else
		res = Py_False;
	goto done;

  unequal:
	if (eq < 0)
		return NULL;
	if (op == Py_NE)
		res = Py_True;
	else
		res = Py_False;

  done:
	Py_INCREF(res);
	return res;
}

static long
code_hash(PyCodeObject *co)
{
	long h, h0, h1, h2, h3, h4, h5, h6, h7;
	h0 = PyObject_Hash(co->co_name);
	if (h0 == -1) return -1;
	h1 = PyObject_Hash(co->co_code);
	if (h1 == -1) return -1;
	h2 = PyObject_Hash(co->co_consts);
	if (h2 == -1) return -1;
	h3 = PyObject_Hash(co->co_names);
	if (h3 == -1) return -1;
	h4 = PyObject_Hash(co->co_varnames);
	if (h4 == -1) return -1;
	h5 = PyObject_Hash(co->co_freevars);
	if (h5 == -1) return -1;
	h6 = PyObject_Hash(co->co_cellvars);
	if (h6 == -1) return -1;
	h7 = (long)(((Py2CCodeObject *)co)->co_function);
	if (h7 == -1) return -1;
	h = h0 ^ h1 ^ h2 ^ h3 ^ h4 ^ h5 ^ h6 ^
		co->co_argcount ^ co->co_nlocals ^ co->co_flags ^ h7;
	if (h == -1) h = -2;
	return h;
}

PyTypeObject Py2CCode_Type;

/* Function object implementation */

#include "eval.h"

static PyObject *
function_call(PyObject *func, PyObject *arg, PyObject *kw)
{
	PyObject *result;
	PyObject *argdefs;
	PyObject **d, **k;
	Py_ssize_t nk, nd;

	argdefs = PyFunction_GET_DEFAULTS(func);
	if (argdefs != NULL && PyTuple_Check(argdefs)) {
		d = &PyTuple_GET_ITEM((PyTupleObject *)argdefs, 0);
		nd = PyTuple_Size(argdefs);
	}
	else {
		d = NULL;
		nd = 0;
	}

	if (kw != NULL && PyDict_Check(kw)) {
		Py_ssize_t pos, i;
		nk = PyDict_Size(kw);
		k = PyMem_NEW(PyObject *, 2*nk);
		if (k == NULL) {
			PyErr_NoMemory();
			return NULL;
		}
		pos = i = 0;
		while (PyDict_Next(kw, &pos, &k[i], &k[i+1]))
			i += 2;
		nk = i/2;
		/* XXX This is broken if the caller deletes dict items! */
	}
	else {
		k = NULL;
		nk = 0;
	}

	result = PyEval_Eval2CCodeEx(
		(PyCodeObject *)PyFunction_GET_CODE(func),
		(PyObject *)NULL,
		&PyTuple_GET_ITEM(arg, 0), PyTuple_Size(arg),
		k, nk, d, nd,
		PyFunction_GET_CLOSURE(func));

	if (k != NULL)
		PyMem_DEL(k);

	return result;
}

#define ISINDEX(x) ((x) == NULL || \
		    PyInt_Check(x) || PyLong_Check(x) || PyIndex_Check(x))

/* Remove name from sys.modules, if it's there. */
static void
_RemoveModule(const char *name)
{
	PyObject *modules = PyImport_GetModuleDict();
	if (PyDict_GetItemString(modules, name) == NULL)
		return;
	if (PyDict_DelItemString(modules, name) < 0)
		Py_FatalError("import:  deleting existing key in"
			      "sys.modules failed");
}


static PyObject *
PyImport_Exec2CCodeModuleEx(char *name, PyObject *co)
{
	PyObject *modules = PyImport_GetModuleDict();
	PyObject *m, *d, *v;

	m = PyImport_AddModule(name);
	if (m == NULL)
		return NULL;
	/* If the module is being reloaded, we get the old module back
	   and re-use its dict to exec the new code. */
	d = PyModule_GetDict(m);
	if (PyDict_GetItemString(d, "__builtins__") == NULL) {
		if (PyDict_SetItemString(d, "__builtins__",
					 PyEval_GetBuiltins()) != 0)
			goto error;
	}
 	/* Remember the filename as the __file__ attribute */ 
		v = ((PyCodeObject *)co)->co_filename;
/*                v = PyString_FromString(src_name);*/
		Py_INCREF(v);
	if (PyDict_SetItemString(d, "__file__", v) != 0)
		PyErr_Clear(); /* Not important enough to report */
	Py_DECREF(v);
        v = PyString_FromString(name);
        Py_INCREF(v);
	if (PyDict_SetItemString(d, "__name__", v) != 0)
		PyErr_Clear(); /* Not important enough to report */
	Py_DECREF(v);
        glob = d;
	v = PyEval_Eval2CCodeEx((PyCodeObject *)co,
			  d,
			  (PyObject **)NULL, 0,
			  (PyObject **)NULL, 0,
			  (PyObject **)NULL, 0,
			  NULL);

	if (v == NULL)
		goto error;
	Py_DECREF(v);

	if ((m = PyDict_GetItemString(modules, name)) == NULL) {
		PyErr_Format(PyExc_ImportError,
			     "Loaded module %.200s not found in sys.modules",
			     name);
		return NULL;
	}

	Py_INCREF(m);

	return m;

  error:
	_RemoveModule(name);
	return NULL;
}

static void patch_code2c(void){
    Py2CCode_Type = PyCode_Type;
    Py2CCode_Type.ob_type = &PyType_Type;
    Py2CCode_Type.tp_richcompare = code_richcompare;
    Py2CCode_Type.tp_compare = (cmpfunc)code_compare;
    Py2CCode_Type.tp_repr = (reprfunc)code_repr;
    Py2CCode_Type.tp_hash = (hashfunc)code_hash;
    Py2CCode_Type.tp_new = 0;
    Py2CCode_Type.tp_name = "code2c";
    Py2CCode_Type.tp_basicsize = sizeof(Py2CCodeObject);

    Py2CFunction_Type = PyFunction_Type;
    Py2CFunction_Type.ob_type = &PyType_Type;
    Py2CFunction_Type.tp_new = 0;
    Py2CFunction_Type.tp_name = "function2c";
    Py2CFunction_Type.tp_call = function_call;
}    
"""

def UseLabl():
    _3(func, 'UseLabel', labl)
    
def Used(nm):
    depends = {'_PyEval_PRINT_ITEM_1' : ('_PyEval_PRINT_ITEM_TO_2',),\
               'from_ceval_call_exc_trace' : ('from_ceval_call_trace',)}
    _3(nm, 'Used', True)
    if nm in depends:
        for nm2 in depends[nm]:
            Used(nm2)

_Libr = {}
def IsLibr(nm):
    return nm in _Libr

def Libr(nm, dcl, defin):
    _Libr[nm] = (dcl, defin)

def LibrDcl(nm):
    return _Libr[nm][0]

def LibrDef(nm):
    return _Libr[nm][1]

if tuple(sys.version_info)[:2] == (2,6):
    Libr('PyEval_Eval2CCodeEx', 
"""
static PyObject *
PyEval_Eval2CCodeEx(PyCodeObject *, PyObject *,
	   PyObject **, int , PyObject **, int ,
	   PyObject **, int , PyObject *);
""",
"""
/* Local variable macros */

#undef GETLOCAL
#undef SETLOCAL
#define GETLOCAL(i)	(fastlocals[i])

#define SETLOCAL(i, value)	do { PyObject *tmp = GETLOCAL(i); \
				     GETLOCAL(i) = value; \
                                     Py_XDECREF(tmp); } while (0)

static PyObject *
PyEval_Eval2CCodeEx(PyCodeObject *co, PyObject *locals,
	   PyObject **args, int argcount, PyObject **kws, int kwcount,
	   PyObject **defs, int defcount, PyObject *closure)
{
	register PyFrameObject *f;
	register PyObject *retval = NULL;
	register PyObject **fastlocals, **freevars;
	PyThreadState *tstate = PyThreadState_GET();
	PyObject *x, *u;
        PyObject *(*c_func)(PyFrameObject *);

	assert(tstate != NULL);
	f = PyFrame_New(tstate, co, glob, locals);
	if (f == NULL)
		return NULL;

	fastlocals = f->f_localsplus;
	freevars = f->f_localsplus + co->co_nlocals;

	if (co->co_argcount > 0 ||
	    co->co_flags & (CO_VARARGS | CO_VARKEYWORDS)) {
		int i;
		int n = argcount;
		PyObject *kwdict = NULL;
		if (co->co_flags & CO_VARKEYWORDS) {
			kwdict = PyDict_New();
			if (kwdict == NULL)
				goto fail;
			i = co->co_argcount;
			if (co->co_flags & CO_VARARGS)
				i++;
			SETLOCAL(i, kwdict);
		}
		if (argcount > co->co_argcount) {
			if (!(co->co_flags & CO_VARARGS)) {
				PyErr_Format(PyExc_TypeError,
				    "%.200s() takes %s %d "
				    "%sargument%s (%d given)",
				    PyString_AsString(co->co_name),
				    defcount ? "at most" : "exactly",
				    co->co_argcount,
				    kwcount ? "non-keyword " : "",
				    co->co_argcount == 1 ? "" : "s",
				    argcount);
				goto fail;
			}
			n = co->co_argcount;
		}
		for (i = 0; i < n; i++) {
			x = args[i];
			Py_INCREF(x);
			SETLOCAL(i, x);
		}
		if (co->co_flags & CO_VARARGS) {
			u = PyTuple_New(argcount - n);
			if (u == NULL)
				goto fail;
			SETLOCAL(co->co_argcount, u);
			for (i = n; i < argcount; i++) {
				x = args[i];
				Py_INCREF(x);
				PyTuple_SET_ITEM(u, i-n, x);
			}
		}
		for (i = 0; i < kwcount; i++) {
			PyObject **co_varnames;
			PyObject *keyword = kws[2*i];
			PyObject *value = kws[2*i + 1];
			int j;
			if (keyword == NULL || !PyString_Check(keyword)) {
				PyErr_Format(PyExc_TypeError,
				    "%.200s() keywords must be strings",
				    PyString_AsString(co->co_name));
				goto fail;
			}
			/* Speed hack: do raw pointer compares. As names are
			   normally interned this should almost always hit. */
			co_varnames = PySequence_Fast_ITEMS(co->co_varnames);
			for (j = 0; j < co->co_argcount; j++) {
				PyObject *nm = co_varnames[j];
				if (nm == keyword)
					goto kw_found;
			}
			/* Slow fallback, just in case */
			for (j = 0; j < co->co_argcount; j++) {
				PyObject *nm = co_varnames[j];
				int cmp = PyObject_RichCompareBool(
					keyword, nm, Py_EQ);
				if (cmp > 0)
					goto kw_found;
				else if (cmp < 0)
					goto fail;
			}
			/* Check errors from Compare */
			if (PyErr_Occurred())
				goto fail;
			if (j >= co->co_argcount) {
				if (kwdict == NULL) {
					PyErr_Format(PyExc_TypeError,
					    "%.200s() got an unexpected "
					    "keyword argument '%.400s'",
					    PyString_AsString(co->co_name),
					    PyString_AsString(keyword));
					goto fail;
				}
				PyDict_SetItem(kwdict, keyword, value);
				continue;
			}
kw_found:
			if (GETLOCAL(j) != NULL) {
				PyErr_Format(PyExc_TypeError,
						"%.200s() got multiple "
						"values for keyword "
						"argument '%.400s'",
						PyString_AsString(co->co_name),
						PyString_AsString(keyword));
				goto fail;
			}
			Py_INCREF(value);
			SETLOCAL(j, value);
		}
		if (argcount < co->co_argcount) {
			int m = co->co_argcount - defcount;
			for (i = argcount; i < m; i++) {
				if (GETLOCAL(i) == NULL) {
					PyErr_Format(PyExc_TypeError,
					    "%.200s() takes %s %d "
					    "%sargument%s (%d given)",
					    PyString_AsString(co->co_name),
					    ((co->co_flags & CO_VARARGS) ||
					     defcount) ? "at least"
						       : "exactly",
					    m, kwcount ? "non-keyword " : "",
					    m == 1 ? "" : "s", i);
					goto fail;
				}
			}
			if (n > m)
				i = n - m;
			else
				i = 0;
			for (; i < defcount; i++) {
				if (GETLOCAL(m+i) == NULL) {
					PyObject *def = defs[i];
					Py_INCREF(def);
					SETLOCAL(m+i, def);
				}
			}
		}
	}
	else {
		if (argcount > 0 || kwcount > 0) {
			PyErr_Format(PyExc_TypeError,
				     "%.200s() takes no arguments (%d given)",
				     PyString_AsString(co->co_name),
				     argcount + kwcount);
			goto fail;
		}
	}
	/* Allocate and initialize storage for cell vars, and copy free
	   vars into frame.  This isn't too efficient right now. */
	if (PyTuple_GET_SIZE(co->co_cellvars)) {
		int i, j, nargs, found;
		char *cellname, *argname;
		PyObject *c;

		nargs = co->co_argcount;
		if (co->co_flags & CO_VARARGS)
			nargs++;
		if (co->co_flags & CO_VARKEYWORDS)
			nargs++;

		/* Initialize each cell var, taking into account
		   cell vars that are initialized from arguments.

		   Should arrange for the compiler to put cellvars
		   that are arguments at the beginning of the cellvars
		   list so that we can march over it more efficiently?
		*/
		for (i = 0; i < PyTuple_GET_SIZE(co->co_cellvars); ++i) {
			cellname = PyString_AS_STRING(
				PyTuple_GET_ITEM(co->co_cellvars, i));
			found = 0;
			for (j = 0; j < nargs; j++) {
				argname = PyString_AS_STRING(
					PyTuple_GET_ITEM(co->co_varnames, j));
				if (strcmp(cellname, argname) == 0) {
					c = PyCell_New(GETLOCAL(j));
					if (c == NULL)
						goto fail;
					GETLOCAL(co->co_nlocals + i) = c;
					found = 1;
					break;
				}
			}
			if (found == 0) {
				c = PyCell_New(NULL);
				if (c == NULL)
					goto fail;
				SETLOCAL(co->co_nlocals + i, c);
			}
		}
	}
	if (PyTuple_GET_SIZE(co->co_freevars)) {
		int i;
		for (i = 0; i < PyTuple_GET_SIZE(co->co_freevars); ++i) {
			PyObject *o = PyTuple_GET_ITEM(closure, i);
			Py_INCREF(o);
			freevars[PyTuple_GET_SIZE(co->co_cellvars) + i] = o;
		}
	}

        c_func = ((Py2CCodeObject *)co)->co_function;
        retval = c_func(f);

fail: /* Jump here from prelude on failure */

	/* decref'ing the frame can cause __del__ methods to get invoked,
	   which can call back into Python.  While we're done with the
	   current Python frame (f), the associated C stack is still in use,
	   so recursion_depth must be boosted for the duration.
	*/
	assert(tstate != NULL);
	++tstate->recursion_depth;
	Py_DECREF(f);
	--tstate->recursion_depth;
	return retval;
}
""")
elif tuple(sys.version_info)[:2] == (2,7):
    Libr('PyEval_Eval2CCodeEx', 
"""
static PyObject *
PyEval_Eval2CCodeEx(PyCodeObject *, PyObject *,
	   PyObject **, int , PyObject **, int ,
	   PyObject **, int , PyObject *);
static PyObject * kwd_as_string(PyObject *);
""",
"""
/* Local variable macros */

#undef GETLOCAL
#undef SETLOCAL
#define GETLOCAL(i)	(fastlocals[i])

#define SETLOCAL(i, value)	do { PyObject *tmp = GETLOCAL(i); \
				     GETLOCAL(i) = value; \
                                     Py_XDECREF(tmp); } while (0)

static PyObject *
PyEval_Eval2CCodeEx(PyCodeObject *co, PyObject *locals,
	   PyObject **args, int argcount, PyObject **kws, int kwcount,
	   PyObject **defs, int defcount, PyObject *closure)
{
	register PyFrameObject *f;
	register PyObject *retval = NULL;
	register PyObject **fastlocals, **freevars;
	PyThreadState *tstate = PyThreadState_GET();
	PyObject *x, *u;
        PyObject *(*c_func)(PyFrameObject *);

        assert(tstate != NULL);
        f = PyFrame_New(tstate, co, glob, locals);
	if (f == NULL)
		return NULL;

	fastlocals = f->f_localsplus;
	freevars = f->f_localsplus + co->co_nlocals;

	if (co->co_argcount > 0 ||
	    co->co_flags & (CO_VARARGS | CO_VARKEYWORDS)) {
		int i;
		int n = argcount;
		PyObject *kwdict = NULL;
		if (co->co_flags & CO_VARKEYWORDS) {
			kwdict = PyDict_New();
			if (kwdict == NULL)
				goto fail;
			i = co->co_argcount;
			if (co->co_flags & CO_VARARGS)
				i++;
			SETLOCAL(i, kwdict);
		}
		if (argcount > co->co_argcount) {
			if (!(co->co_flags & CO_VARARGS)) {
				PyErr_Format(PyExc_TypeError,
				    "%.200s() takes %s %d "
				    "%sargument%s (%d given)",
				    PyString_AsString(co->co_name),
				    defcount ? "at most" : "exactly",
				    co->co_argcount,
				    kwcount ? "non-keyword " : "",
				    co->co_argcount == 1 ? "" : "s",
				    argcount);
				goto fail;
			}
			n = co->co_argcount;
		}
		for (i = 0; i < n; i++) {
			x = args[i];
			Py_INCREF(x);
			SETLOCAL(i, x);
		}
		if (co->co_flags & CO_VARARGS) {
			u = PyTuple_New(argcount - n);
			if (u == NULL)
				goto fail;
			SETLOCAL(co->co_argcount, u);
			for (i = n; i < argcount; i++) {
				x = args[i];
				Py_INCREF(x);
				PyTuple_SET_ITEM(u, i-n, x);
			}
		}
		for (i = 0; i < kwcount; i++) {
			PyObject **co_varnames;
			PyObject *keyword = kws[2*i];
			PyObject *value = kws[2*i + 1];
			int j;
                        if (keyword == NULL || !(PyString_Check(keyword)
#ifdef Py_USING_UNICODE
                                     || PyUnicode_Check(keyword)
#endif
                            )) {
				PyErr_Format(PyExc_TypeError,
				    "%.200s() keywords must be strings",
				    PyString_AsString(co->co_name));
				goto fail;
			}
			/* Speed hack: do raw pointer compares. As names are
			   normally interned this should almost always hit. */
                        co_varnames = ((PyTupleObject *)(co->co_varnames))->ob_item;
                        for (j = 0; j < co->co_argcount; j++) {
                            PyObject *nm = co_varnames[j];
                            if (nm == keyword)
                                goto kw_found;
                        }
                        /* Slow fallback, just in case */
                        for (j = 0; j < co->co_argcount; j++) {
                            PyObject *nm = co_varnames[j];
                            int cmp = PyObject_RichCompareBool(
                                keyword, nm, Py_EQ);
                            if (cmp > 0)
                                goto kw_found;
                            else if (cmp < 0)
                                goto fail;
                        }
                        if (kwdict == NULL) {
                            PyObject *kwd_str = kwd_as_string(keyword);
                            if (kwd_str) {
                                PyErr_Format(PyExc_TypeError,
                                            "%.200s() got an unexpected "
                                            "keyword argument '%.400s'",
                                            PyString_AsString(co->co_name),
                                            PyString_AsString(kwd_str));
                                Py_DECREF(kwd_str);
                            }
                            goto fail;
                        }
                        PyDict_SetItem(kwdict, keyword, value);
                        continue;

kw_found:
			if (GETLOCAL(j) != NULL) {
                            PyObject *kwd_str = kwd_as_string(keyword);
                            if (kwd_str) {
                                PyErr_Format(PyExc_TypeError,
                                            "%.200s() got multiple "
                                            "values for keyword "
                                            "argument '%.400s'",
                                            PyString_AsString(co->co_name),
                                            PyString_AsString(kwd_str));
                                Py_DECREF(kwd_str);
                            }
			}
			Py_INCREF(value);
			SETLOCAL(j, value);
		}
		if (argcount < co->co_argcount) {
			int m = co->co_argcount - defcount;
			for (i = argcount; i < m; i++) {
				if (GETLOCAL(i) == NULL) {
                                    int j, given = 0;
                                    for (j = 0; j < co->co_argcount; j++)
                                        if (GETLOCAL(j))
                                            given++;
                                    PyErr_Format(PyExc_TypeError,
                                        "%.200s() takes %s %d "
                                        "argument%s (%d given)",
                                        PyString_AsString(co->co_name),
                                        ((co->co_flags & CO_VARARGS) ||
                                        defcount) ? "at least"
                                                : "exactly",
                                        m, m == 1 ? "" : "s", given);
                                    goto fail;
				}
			}
			if (n > m)
				i = n - m;
			else
				i = 0;
			for (; i < defcount; i++) {
				if (GETLOCAL(m+i) == NULL) {
					PyObject *def = defs[i];
					Py_INCREF(def);
					SETLOCAL(m+i, def);
				}
			}
		}
	}
	else {
		if (argcount > 0 || kwcount > 0) {
			PyErr_Format(PyExc_TypeError,
				     "%.200s() takes no arguments (%d given)",
				     PyString_AsString(co->co_name),
				     argcount + kwcount);
			goto fail;
		}
	}
	/* Allocate and initialize storage for cell vars, and copy free
	   vars into frame.  This isn't too efficient right now. */
	if (PyTuple_GET_SIZE(co->co_cellvars)) {
		int i, j, nargs, found;
		char *cellname, *argname;
		PyObject *c;

		nargs = co->co_argcount;
		if (co->co_flags & CO_VARARGS)
			nargs++;
		if (co->co_flags & CO_VARKEYWORDS)
			nargs++;

		/* Initialize each cell var, taking into account
		   cell vars that are initialized from arguments.

		   Should arrange for the compiler to put cellvars
		   that are arguments at the beginning of the cellvars
		   list so that we can march over it more efficiently?
		*/
		for (i = 0; i < PyTuple_GET_SIZE(co->co_cellvars); ++i) {
			cellname = PyString_AS_STRING(
				PyTuple_GET_ITEM(co->co_cellvars, i));
			found = 0;
			for (j = 0; j < nargs; j++) {
				argname = PyString_AS_STRING(
					PyTuple_GET_ITEM(co->co_varnames, j));
				if (strcmp(cellname, argname) == 0) {
					c = PyCell_New(GETLOCAL(j));
					if (c == NULL)
						goto fail;
					GETLOCAL(co->co_nlocals + i) = c;
					found = 1;
					break;
				}
			}
			if (found == 0) {
				c = PyCell_New(NULL);
				if (c == NULL)
					goto fail;
				SETLOCAL(co->co_nlocals + i, c);
			}
		}
	}
	if (PyTuple_GET_SIZE(co->co_freevars)) {
		int i;
		for (i = 0; i < PyTuple_GET_SIZE(co->co_freevars); ++i) {
			PyObject *o = PyTuple_GET_ITEM(closure, i);
			Py_INCREF(o);
			freevars[PyTuple_GET_SIZE(co->co_cellvars) + i] = o;
		}
	}

        assert(!(co->co_flags & CO_GENERATOR));

        c_func = ((Py2CCodeObject *)co)->co_function;
        retval = c_func(f);

fail: /* Jump here from prelude on failure */

	/* decref'ing the frame can cause __del__ methods to get invoked,
	   which can call back into Python.  While we're done with the
	   current Python frame (f), the associated C stack is still in use,
	   so recursion_depth must be boosted for the duration.
	*/
	assert(tstate != NULL);
	++tstate->recursion_depth;
	Py_DECREF(f);
	--tstate->recursion_depth;
	return retval;
}

static PyObject *
kwd_as_string(PyObject *kwd) {
#ifdef Py_USING_UNICODE
    if (PyString_Check(kwd)) {
#else
        assert(PyString_Check(kwd));
#endif
        Py_INCREF(kwd);
        return kwd;
#ifdef Py_USING_UNICODE
    }
    return _PyUnicode_AsDefaultEncodedString(kwd, "replace");
#endif
}

""")

Libr('from_ceval_2_7_special_lookup',
"""
static PyObject * from_ceval_2_7_enter = NULL;
static PyObject * from_ceval_2_7_exit = NULL;
static PyObject * from_ceval_2_7_special_lookup(PyObject *, char *, PyObject **);
""",
"""
static PyObject *
from_ceval_2_7_special_lookup(PyObject *o, char *meth, PyObject **cache)
{
    PyObject *res;
    if (PyInstance_Check(o)) {
        if (!*cache)
            return PyObject_GetAttrString(o, meth);
        else
            return PyObject_GetAttr(o, *cache);
    }
    res = _PyObject_LookupSpecial(o, meth, cache);
    if (res == NULL && !PyErr_Occurred()) {
        PyErr_SetObject(PyExc_AttributeError, *cache);
        return NULL;
    }
    return res;
}
""")

Libr('Direct_AddTraceback',
"""
static void Direct_AddTraceback (PyCodeObject *, int, int);
""",
"""
static void Direct_AddTraceback (PyCodeObject * py_code, int lineno, int addr)
{
  PyFrameObject *py_frame = 0;

  py_frame = PyFrame_New (PyThreadState_GET (),	/*PyThreadState *tstate, */
			  py_code,	/*PyCodeObject *code, */
			  glob,	/*PyObject *globals, */
			  0	/*PyObject *locals */
    );
  if (!py_frame)
    goto bad;
  py_frame->f_lineno = lineno;
  py_frame->f_lasti = addr;
  PyTraceBack_Here (py_frame);
bad:
  Py_XDECREF (py_frame);
}
""")   
  
Libr('STR_CONCAT2',
"""
static PyObject * STR_CONCAT2( PyObject *, PyObject * );
""",
"""
static PyObject * STR_CONCAT2( PyObject *a, PyObject * b)
{
   if (PyString_CheckExact(a) && PyString_CheckExact(b)) {
      PyObject * r;
      char buf[1024];
      Py_ssize_t l_a, l_b, l_r;
      l_a = PyString_GET_SIZE(a); 
      l_b = PyString_GET_SIZE(b);
      if (l_b == 0) {
        Py_INCREF(a);
        return a;
      }
      if (l_a == 0) {
        Py_INCREF(b);
        return b;
      }
      if ((l_r = (l_a + l_b)) < 1024) {
        Py_MEMCPY(buf, PyString_AS_STRING(a), l_a);
        Py_MEMCPY(buf + l_a, PyString_AS_STRING(b), l_b);
        r = PyString_FromStringAndSize(buf, l_r);
      } else {  
        r = PyString_FromStringAndSize(PyString_AS_STRING(a), l_a);
        PyString_Concat(&r, b);
      }  
      return r;
   } else {
      return PyNumber_Add(a,b);
   }
}
""")   
  
Libr('STR_CONCAT3',
"""
static PyObject * STR_CONCAT3( PyObject *, PyObject *, PyObject *);
""",
"""
static PyObject * STR_CONCAT3( PyObject *a, PyObject * b, PyObject * c)
{
   PyObject * r, *r1;
   if (PyString_CheckExact(a) && PyString_CheckExact(b) && PyString_CheckExact(c)) {
      char buf[1024];
      Py_ssize_t l_a, l_b, l_c, l_r;
      l_a = PyString_GET_SIZE(a); 
      l_b = PyString_GET_SIZE(b);
      l_c = PyString_GET_SIZE(c);
      if ((l_r = (l_a + l_b + l_c)) < 1024) {
        Py_MEMCPY(buf, PyString_AS_STRING(a), l_a);
        Py_MEMCPY(buf + l_a, PyString_AS_STRING(b), l_b);
        Py_MEMCPY(buf + (l_a + l_b), PyString_AS_STRING(c), l_c);
        r = PyString_FromStringAndSize(buf, l_r);
      } else {  
        r = PyString_FromStringAndSize(PyString_AS_STRING(a), l_a);
        PyString_Concat(&r, b);
        PyString_Concat(&r, c);
      }  
      return r;
   } else {
      r = PyNumber_Add(a,b);
      r1 = PyNumber_Add(r,b);
      Py_DECREF(r);
      return r1;
   }
}
""")   
  
Libr('from_ceval_call_exc_trace',
"""
static void
from_ceval_call_exc_trace(Py_tracefunc, PyObject *, PyFrameObject *);
""",
"""
static void
from_ceval_call_exc_trace(Py_tracefunc func, PyObject *self, PyFrameObject *f)
{
	PyObject *type, *value, *traceback, *arg;
	int err;
	PyErr_Fetch(&type, &value, &traceback);
	if (value == NULL) {
		value = Py_None;
		Py_INCREF(value);
	}
	arg = PyTuple_Pack(3, type, value, traceback);
	if (arg == NULL) {
		PyErr_Restore(type, value, traceback);
		return;
	}
	err = from_ceval_call_trace(func, self, f, PyTrace_EXCEPTION, arg);
	Py_DECREF(arg);
	if (err == 0)
		PyErr_Restore(type, value, traceback);
	else {
		Py_XDECREF(type);
		Py_XDECREF(value);
		Py_XDECREF(traceback);
	}
}
""")   
  
Libr('from_ceval_call_trace',
"""
static int
from_ceval_call_trace(Py_tracefunc , PyObject *, PyFrameObject *,
	   int , PyObject *);
""",
"""
static int
from_ceval_call_trace(Py_tracefunc func, PyObject *obj, PyFrameObject *frame,
	   int what, PyObject *arg)
{
	register PyThreadState *tstate = frame->f_tstate;
	int result;
	if (tstate->tracing)
		return 0;
	tstate->tracing++;
	tstate->use_tracing = 0;
	result = func(obj, frame, what, arg);
	tstate->use_tracing = ((tstate->c_tracefunc != NULL)
			       || (tstate->c_profilefunc != NULL));
	tstate->tracing--;
	return result;
}
""")   
  
Libr('from_ceval_BINARY_SUBSCR',
"""
static PyObject * from_ceval_BINARY_SUBSCR ( PyObject *, PyObject *);
""",
"""
static PyObject * from_ceval_BINARY_SUBSCR ( PyObject *v, PyObject *w)
{
    PyObject * x = NULL;
/*#    goto slow_get;*/
    if (PyList_CheckExact(v) && PyInt_CheckExact(w)) {
            /* INLINE: list[int] */
            Py_ssize_t i = PyInt_AS_LONG(w);
            if (i < 0)
                    i += PyList_GET_SIZE(v);
            if (i >= 0 && i < PyList_GET_SIZE(v)) {
                    x = PyList_GET_ITEM(v, i);
                    Py_INCREF(x);
                    return x;
            }
            else
                    goto slow_get;
    }
    else if (PyTuple_CheckExact(v) && PyInt_CheckExact(w)) {
            /* INLINE: list[int] */
            Py_ssize_t i = PyInt_AS_LONG(w);
            if (i < 0)
                    i += PyTuple_GET_SIZE(v);
            if (i >= 0 && i < PyTuple_GET_SIZE(v)) {
                    x = PyTuple_GET_ITEM(v, i);
                    Py_INCREF(x);
                    return x;
            }
            else
                    goto slow_get;
    }
        slow_get:
            x = PyObject_GetItem(v, w);
    return x;
}
""")   
  
Libr('c_LOAD_NAME',
"""
static PyObject * c_LOAD_NAME (PyFrameObject *, PyObject *);
""",
"""
static PyObject * c_LOAD_NAME (PyFrameObject *f, PyObject *w)
{
        PyObject * v;
        PyObject * x;
        if ((v = f->f_locals) == NULL) {
                PyErr_Format(PyExc_SystemError,
                                "no locals when loading %s",
                                PyObject_REPR(w));
                return NULL;
        }
        if (PyDict_CheckExact(v)) {
                x = PyDict_GetItem(v, w);
                Py_XINCREF(x);
        }
        else {
                x = PyObject_GetItem(v, w);
                if (x == NULL && PyErr_Occurred()) {
                        if (!PyErr_ExceptionMatches(
                                        PyExc_KeyError))
                                return NULL;
                        PyErr_Clear();
                }
        }
        if (x == NULL) {
                x = PyDict_GetItem(glob, w);
                if (x == NULL) {
                        x = PyDict_GetItem(bdict, w);
                        if (x == NULL) {
                            char *obj_str;
                            obj_str = PyString_AsString(w);
                            if (obj_str)
                                PyErr_Format(PyExc_NameError, NAME_ERROR_MSG, obj_str);
                                return NULL;
                        }
                }
                Py_INCREF(x);
        }
        return x;
}
""")   
  
Libr('c_LOAD_GLOBAL',
"""
static PyObject * c_LOAD_GLOBAL ( PyObject *, long);
""",
"""
static PyObject * c_LOAD_GLOBAL ( PyObject *w, long hash)
{
        PyObject * x;
                /* Inline the PyDict_GetItem() calls.
                    WARNING: this is an extreme speed hack.
                    Do not try this at home. */
        if (hash != -1) {
                PyDictObject *d;
                PyDictEntry *e;
                d = (PyDictObject *)(glob);
                e = d->ma_lookup(d, w, hash);
                if (e == NULL) {
                        x = NULL;
                        return NULL;
                }
                x = e->me_value;
                if (x != NULL) {
                        Py_INCREF(x);
                        return x;
                }
                d = (PyDictObject *)(bdict);
                e = d->ma_lookup(d, w, hash);
                if (e == NULL) {
                        x = NULL;
                        return NULL;
                }
                x = e->me_value;
                if (x != NULL) {
                        Py_INCREF(x);
                        return x;
                }
                goto load_global_error;
        }
        /* This is the un-inlined version of the code above */
        x = PyDict_GetItem(glob, w);
        if (x == NULL) {
                x = PyDict_GetItem(b, w);
                if (x == NULL) {
                    load_global_error:
                        PyErr_Format(PyExc_NameError, GLOBAL_NAME_ERROR_MSG, 
                                        PyString_AsString(w));
                        return NULL;
                }
        }
        Py_INCREF(x);
        return x;
}
""")   
  
Libr('c_BINARY_SUBSCR_SUBSCR_Int_Int',
"""
static PyObject * c_BINARY_SUBSCR_SUBSCR_Int_Int(PyObject *, int, PyObject *, int, PyObject *);
""",
"""
static PyObject * c_BINARY_SUBSCR_SUBSCR_Int_Int(PyObject *v, Py_ssize_t i1, 
PyObject *const_i1, Py_ssize_t i2, PyObject * const_i2)
{
    PyObject * x = NULL;
    PyObject * x0 = NULL;
    if (PyList_CheckExact(v)) {
            Py_ssize_t l = PyList_GET_SIZE(v);
            /* INLINE: list[int] */
            if (i1 < 0)
                    i1 += l;
            if (i1 >= 0 && i1 < l) {
                    x = PyList_GET_ITEM(v, i1);
                    Py_INCREF(x);
                    goto next;
            }
            else
                    goto slow_get;
    }
    else if (PyTuple_CheckExact(v)) {
            Py_ssize_t l = PyTuple_GET_SIZE(v);
            /* INLINE: list[int] */
            if (i1 < 0)
                    i1 += l;
            if (i1 >= 0 && i1 < l) {
                    x = PyTuple_GET_ITEM(v, i1);
                    Py_INCREF(x);
                    goto next;
            }
            else
                    goto slow_get;
    }
    else
        slow_get:
            x = PyObject_GetItem(v, const_i1);
    next:        
    x0 = x;
    v = x;        
    if (v == NULL) return v;
    if (PyList_CheckExact(v)) {
            Py_ssize_t l = PyList_GET_SIZE(v);
            /* INLINE: list[int] */
            if (i2 < 0)
                    i2 += l;
            if (i2 >= 0 && i2 < l) {
                    x = PyList_GET_ITEM(v, i2);
                    Py_INCREF(x);
                    Py_DECREF(x0);
                    return x;
            }
            else
                    goto slow_get2;
    }
    else if (PyTuple_CheckExact(v)) {
            Py_ssize_t l = PyTuple_GET_SIZE(v);
            /* INLINE: list[int] */
            if (i2 < 0)
                    i2 += l;
            if (i2 >= 0 && i2 < l) {
                    x = PyTuple_GET_ITEM(v, i2);
                    Py_INCREF(x);
                    Py_DECREF(x0);
                    return x;
            }
            else
                    goto slow_get2;
    }
    else
        slow_get2:
            x = PyObject_GetItem(v, const_i2);
    Py_DECREF(x0);
    return x;
}
""")   
  
Libr('_c_BINARY_SUBSCR_Int',
"""
static PyObject * _c_BINARY_SUBSCR_Int(PyObject *, Py_ssize_t, PyObject *);
""",
"""
static PyObject * _c_BINARY_SUBSCR_Int(PyObject *v, Py_ssize_t i1, PyObject *const_i1)
{
    PyObject * x = NULL;
    if (PyList_CheckExact(v)) {
            Py_ssize_t l;
            /* INLINE: list[int] */
            l = PyList_GET_SIZE(v);
            if (i1 < 0)
                    i1 += l;
            if (i1 >= 0 && i1 < l) {
                    x = PyList_GET_ITEM(v, i1);
                    Py_INCREF(x);
                    return x;
            }
            else
                    goto slow_get;
    }
    else if (PyTuple_CheckExact(v)) {
            Py_ssize_t l;
            /* INLINE: list[int] */
            l = PyTuple_GET_SIZE(v);
            if (i1 < 0)
                    i1 += l;
            if (i1 >= 0 && i1 < l) {
                    x = PyTuple_GET_ITEM(v, i1);
                    Py_INCREF(x);
                    return x;
            }
            else
                    goto slow_get;
    }
    else
        slow_get:
            x = PyObject_GetItem(v, const_i1);
    return x;
}
""")   
  
Libr('_c_BINARY_SUBSCR_ADDED_INT',
"""
static PyObject * _c_BINARY_SUBSCR_ADDED_INT(PyObject *, PyObject *, int, PyObject *);
""",
"""
static PyObject * _c_BINARY_SUBSCR_ADDED_INT(PyObject *v0, PyObject *v, int b, PyObject * const_add)
{
    PyObject * x = NULL;
    PyObject * x2 = NULL;

    if (PyInt_CheckExact(v)) {
        register long a, i1;
        a = PyInt_AS_LONG(v);
        i1 = a + b;
        if ((i1^a) < 0 && (i1^b) < 0)
            goto slow;
        if (PyList_CheckExact(v0)) {
            /* INLINE: list[int] */
            if (i1 < 0)
                i1 += PyList_GET_SIZE(v0);
                if (i1 >= 0 && i1 < PyList_GET_SIZE(v0)) {
                    x = PyList_GET_ITEM(v0, i1);
                    Py_INCREF(x);
                    return x;
                }
            else
                goto slow;
        } else if (PyTuple_CheckExact(v0)) {
            if (i1 < 0)
                i1 += PyTuple_GET_SIZE(v0);
                if (i1 >= 0 && i1 < PyTuple_GET_SIZE(v0)) {
                    x = PyTuple_GET_ITEM(v0, i1);
                    Py_INCREF(x);
                    return x;
                }
            else
                goto slow;
        } else { goto slow; }
    } else { goto slow; }    
    slow:
        x2 = PyNumber_Add(v, const_add);
        if (x2 == NULL) return NULL;
        x = PyObject_GetItem(v0, x2);
        Py_CLEAR(x2);
    return x;
}
""")   
  
Libr('Py2CFunction_New',
"""
static PyObject * Py2CFunction_New(PyObject *);
""",
"""
static PyObject * Py2CFunction_New(PyObject *code)
{
	PyFunctionObject *op = PyObject_GC_New(PyFunctionObject,
					    &Py2CFunction_Type);
	static PyObject *__name__ = 0;
	if (op != NULL) {
		PyObject *doc;
		PyObject *consts;
		PyObject *module;
		op->func_weakreflist = NULL;
		Py_INCREF(code);
		op->func_code = code;
		Py_INCREF(glob);
		op->func_globals = glob;
		op->func_name = ((PyCodeObject *)code)->co_name;
		Py_INCREF(op->func_name);
		op->func_defaults = NULL; /* No default arguments */
		op->func_closure = NULL;
		consts = ((PyCodeObject *)code)->co_consts;
		if (PyTuple_Size(consts) >= 1) {
			doc = PyTuple_GetItem(consts, 0);
			if (!PyString_Check(doc) && !PyUnicode_Check(doc))
				doc = Py_None;
		}
		else
			doc = Py_None;
		Py_INCREF(doc);
		op->func_doc = doc;
		op->func_dict = NULL;
		op->func_module = NULL;

		/* __module__: If module name is in globals, use it.
		   Otherwise, use None.
		*/
		if (!__name__) {
			__name__ = PyString_InternFromString("__name__");
			if (!__name__) {
				Py_DECREF(op);
				return NULL;
			}
		}
		module = PyDict_GetItem(glob, __name__);
		if (module) {
		    Py_INCREF(module);
		    op->func_module = module;
		}
	}
	else
		return NULL;
	PyObject_GC_Track(op);
	return (PyObject *)op;
}
""")   
  
Libr('Py2CFunction_New_Simple',
"""
static PyObject * Py2CFunction_New_Simple(PyObject *, PyTypeObject *);
""",
"""
static PyObject * Py2CFunction_New_Simple(PyObject *code, PyTypeObject * ty)
{
	PyFunctionObject *op = PyObject_GC_New(PyFunctionObject,
					    ty);
	static PyObject *__name__ = 0;
	if (op != NULL) {
		PyObject *doc;
		PyObject *consts;
		PyObject *module;
		op->func_weakreflist = NULL;
		Py_INCREF(code);
		op->func_code = code;
		Py_INCREF(glob);
		op->func_globals = glob;
		op->func_name = ((PyCodeObject *)code)->co_name;
		Py_INCREF(op->func_name);
		op->func_defaults = NULL; /* No default arguments */
		op->func_closure = NULL;
		consts = ((PyCodeObject *)code)->co_consts;
		if (PyTuple_Size(consts) >= 1) {
			doc = PyTuple_GetItem(consts, 0);
			if (!PyString_Check(doc) && !PyUnicode_Check(doc))
				doc = Py_None;
		}
		else
			doc = Py_None;
		Py_INCREF(doc);
		op->func_doc = doc;
		op->func_dict = NULL;
		op->func_module = NULL;

		/* __module__: If module name is in globals, use it.
		   Otherwise, use None.
		*/
		if (!__name__) {
			__name__ = PyString_InternFromString("__name__");
			if (!__name__) {
				Py_DECREF(op);
				return NULL;
			}
		}
		module = PyDict_GetItem(glob, __name__);
		if (module) {
		    Py_INCREF(module);
		    op->func_module = module;
		}
	}
	else
		return NULL;
	PyObject_GC_Track(op);
	return (PyObject *)op;
}
""")   
  
Libr('Py2CFunction_SetClosure',
"""
static int
Py2CFunction_SetClosure(PyObject *, PyObject *);
""",
"""
static int
Py2CFunction_SetClosure(PyObject *op, PyObject *closure)
{
	if (closure == Py_None)
		closure = NULL;
	else if (PyTuple_Check(closure)) {
		Py_INCREF(closure);
	}
	else {
		PyErr_Format(PyExc_SystemError, 
			     "expected tuple for closure, got '%.100s'",
			     closure->ob_type->tp_name);
		return -1;
	}
	Py_XDECREF(((PyFunctionObject *) op) -> func_closure);
	((PyFunctionObject *) op) -> func_closure = closure;
	return 0;
}
""")   
  
Libr('Py2CFunction_SetDefaults',
"""
static int
Py2CFunction_SetDefaults(PyObject *o, PyObject *);
""",
"""
static int
Py2CFunction_SetDefaults(PyObject *op, PyObject *defaults)
{
	if (defaults == Py_None)
		defaults = NULL;
	else if (defaults && PyTuple_Check(defaults)) {
		Py_INCREF(defaults);
	}
	else {
		PyErr_SetString(PyExc_SystemError, "non-tuple default args");
		return -1;
	}
	Py_XDECREF(((PyFunctionObject *) op) -> func_defaults);
	((PyFunctionObject *) op) -> func_defaults = defaults;
	return 0;
}
""")  
   
Libr('_PyEval_PRINT_ITEM_1',
"""
static int _PyEval_PRINT_ITEM_1 ( PyObject * );
""",
"""
static int _PyEval_PRINT_ITEM_1 ( PyObject * v)
{
    return _PyEval_PRINT_ITEM_TO_2 ( NULL, v );
}
""") 
    
Libr('_PyEval_PRINT_ITEM_TO_2',
"""
static int _PyEval_PRINT_ITEM_TO_2 ( PyObject * , PyObject *);
""",
"""
static int _PyEval_PRINT_ITEM_TO_2 ( PyObject * stream, PyObject * v)
{
        PyObject * w = stream; 
        int err = 0;
        if (stream == NULL || stream == Py_None) {
                w = PySys_GetObject("stdout");
                if (w == NULL) {
                        PyErr_SetString(PyExc_RuntimeError,
                                        "lost sys.stdout");
                        err = -1;
                }
        }
        /* PyFile_SoftSpace() can exececute arbitrary code
            if sys.stdout is an instance with a __getattr__.
            If __getattr__ raises an exception, w will
            be freed, so we need to prevent that temporarily. */
        Py_XINCREF(w);
        if (w != NULL && PyFile_SoftSpace(w, 0))
                err = PyFile_WriteString(" ", w);
        if (err == 0)
                err = PyFile_WriteObject(v, w, Py_PRINT_RAW);
        if (err == 0) {
            /* XXX move into writeobject() ? */
            if (PyString_Check(v)) {
                char *s = PyString_AS_STRING(v);
                Py_ssize_t len = PyString_GET_SIZE(v);
                if (len == 0 ||
                    !isspace(Py_CHARMASK(s[len-1])) ||
                    s[len-1] == ' ')
                        PyFile_SoftSpace(w, 1);
            }
#ifdef Py_USING_UNICODE
            else if (PyUnicode_Check(v)) {
                Py_UNICODE *s = PyUnicode_AS_UNICODE(v);
                Py_ssize_t len = PyUnicode_GET_SIZE(v);
                if (len == 0 ||
                    !Py_UNICODE_ISSPACE(s[len-1]) ||
                    s[len-1] == ' ')
                    PyFile_SoftSpace(w, 1);
            }
#endif
            else
                    PyFile_SoftSpace(w, 1);
        }
        Py_XDECREF(w);
   /*     Py_DECREF(v); */
        if (w != stream) {
            Py_XDECREF(stream);
        }
        stream = NULL;
        return err;
}
""") 
    
Libr('_PyEval_PRINT_NEWLINE_TO_1',
"""
static int _PyEval_PRINT_NEWLINE_TO_1 ( PyObject * );
""",
"""
static int _PyEval_PRINT_NEWLINE_TO_1 ( PyObject * stream )
{
        PyObject * w;
        w = stream;
        int err = 0;
        if (stream == NULL || stream == Py_None) {
                w = PySys_GetObject("stdout");
                if (w == NULL) {
                        PyErr_SetString(PyExc_RuntimeError,
                                        "lost sys.stdout");
                        return -1;
                }                    
        }
        if (w != NULL) {
                /* w.write() may replace sys.stdout, so we
                    * have to keep our reference to it */
                Py_INCREF(w);
                err = PyFile_WriteString("\\n", w);
                if (err == 0)
                        PyFile_SoftSpace(w, 0);                        
                Py_DECREF(w);
        }
        if (w != stream) {
            Py_XDECREF(stream);
        }
        stream = NULL;
        return err;
}
""") 
    
Libr('_PyEval_set_exc_info',
"""
static void
_PyEval_set_exc_info(PyThreadState *tstate,
	     PyObject *type, PyObject *value, PyObject *tb);
""",
"""
static void
_PyEval_set_exc_info(PyThreadState *tstate,
	     PyObject *type, PyObject *value, PyObject *tb)
{
	PyFrameObject *frame = tstate->frame;
	PyObject *tmp_type, *tmp_value, *tmp_tb;

	assert(type != NULL);
	assert(frame != NULL);
	if (frame->f_exc_type == NULL) {
		assert(frame->f_exc_value == NULL);
		assert(frame->f_exc_traceback == NULL);
		/* This frame didn't catch an exception before. */
		/* Save previous exception of this thread in this frame. */
		if (tstate->exc_type == NULL) {
			/* XXX Why is this set to Py_None? */
			Py_INCREF(Py_None);
			tstate->exc_type = Py_None;
		}
		Py_INCREF(tstate->exc_type);
		Py_XINCREF(tstate->exc_value);
		Py_XINCREF(tstate->exc_traceback);
		frame->f_exc_type = tstate->exc_type;
		frame->f_exc_value = tstate->exc_value;
		frame->f_exc_traceback = tstate->exc_traceback;
	}
	/* Set new exception for this thread. */
	tmp_type = tstate->exc_type;
	tmp_value = tstate->exc_value;
	tmp_tb = tstate->exc_traceback;
	Py_INCREF(type);
	Py_XINCREF(value);
	Py_XINCREF(tb);
	tstate->exc_type = type;
	tstate->exc_value = value;
	tstate->exc_traceback = tb;
	Py_XDECREF(tmp_type);
	Py_XDECREF(tmp_value);
	Py_XDECREF(tmp_tb);
	/* For b/w compatibility */
	PySys_SetObject("exc_type", type);
	PySys_SetObject("exc_value", value);
	PySys_SetObject("exc_traceback", tb);
}
""")

Libr('_PyEval_reset_exc_info',
"""
static void _PyEval_reset_exc_info(PyThreadState *);
""",
"""
static void
_PyEval_reset_exc_info(PyThreadState *tstate)
{
	PyFrameObject *frame;
	PyObject *tmp_type, *tmp_value, *tmp_tb;

	/* It's a precondition that the thread state's frame caught an
	 * exception -- verify in a debug build.
	 */
	assert(tstate != NULL);
	frame = tstate->frame;
	assert(frame != NULL);
	assert(frame->f_exc_type != NULL);

	/* Copy the frame's exception info back to the thread state. */
	tmp_type = tstate->exc_type;
	tmp_value = tstate->exc_value;
	tmp_tb = tstate->exc_traceback;
	Py_INCREF(frame->f_exc_type);
	Py_XINCREF(frame->f_exc_value);
	Py_XINCREF(frame->f_exc_traceback);
	tstate->exc_type = frame->f_exc_type;
	tstate->exc_value = frame->f_exc_value;
	tstate->exc_traceback = frame->f_exc_traceback;
	Py_XDECREF(tmp_type);
	Py_XDECREF(tmp_value);
	Py_XDECREF(tmp_tb);

	/* For b/w compatibility */
	PySys_SetObject("exc_type", frame->f_exc_type);
	PySys_SetObject("exc_value", frame->f_exc_value);
	PySys_SetObject("exc_traceback", frame->f_exc_traceback);

	/* Clear the frame's exception info. */
	tmp_type = frame->f_exc_type;
	tmp_value = frame->f_exc_value;
	tmp_tb = frame->f_exc_traceback;
	frame->f_exc_type = NULL;
	frame->f_exc_value = NULL;
	frame->f_exc_traceback = NULL;
	Py_DECREF(tmp_type);
	Py_XDECREF(tmp_value);
	Py_XDECREF(tmp_tb);
}
""")
   
Libr('_PyEval_ApplySlice',
"""
static PyObject *
_PyEval_ApplySlice(PyObject *, PyObject *, PyObject *);
""",
"""
static PyObject *
_PyEval_ApplySlice(PyObject *u, PyObject *v, PyObject *w) /* return u[v:w] */
{
	PyTypeObject *tp = u->ob_type;
	PySequenceMethods *sq = tp->tp_as_sequence;

	if (sq && sq->sq_slice && ISINDEX(v) && ISINDEX(w)) {
		Py_ssize_t ilow = 0, ihigh = PY_SSIZE_T_MAX;
		if (!_PyEval_SliceIndex(v, &ilow))
			return NULL;
		if (!_PyEval_SliceIndex(w, &ihigh))
			return NULL;
		return PySequence_GetSlice(u, ilow, ihigh);
	}
	else {
		PyObject *slice = PySlice_New(v, w, NULL);
		if (slice != NULL) {
			PyObject *res = PyObject_GetItem(u, slice);
			Py_DECREF(slice);
			return res;
		}
		else
			return NULL;
	}
}
""")     

Libr('_PyEval_AssignSlice',
"""
static int
_PyEval_AssignSlice(PyObject *, PyObject *, PyObject *, PyObject *);
""",
"""
static int
_PyEval_AssignSlice(PyObject *u, PyObject *v, PyObject *w, PyObject *x)
	/* u[v:w] = x */
{
	PyTypeObject *tp = u->ob_type;
	PySequenceMethods *sq = tp->tp_as_sequence;

	if (sq && sq->sq_ass_slice && ISINDEX(v) && ISINDEX(w)) {
		Py_ssize_t ilow = 0, ihigh = PY_SSIZE_T_MAX;
		if (!_PyEval_SliceIndex(v, &ilow))
			return -1;
		if (!_PyEval_SliceIndex(w, &ihigh))
			return -1;
		if (x == NULL)
			return PySequence_DelSlice(u, ilow, ihigh);
		else
			return PySequence_SetSlice(u, ilow, ihigh, x);
	}
	else {
		PyObject *slice = PySlice_New(v, w, NULL);
		if (slice != NULL) {
			int res;
			if (x != NULL)
				res = PyObject_SetItem(u, slice, x);
			else
				res = PyObject_DelItem(u, slice);
			Py_DECREF(slice);
			return res;
		}
		else
			return -1;
	}
}
""")

Libr('_Call_CompiledWithFrame',
"""
static PyObject * _Call_CompiledWithFrame(void *, PyObject *, int, ...);
""",
"""
static PyObject * _Call_CompiledWithFrame(void * func, PyObject *_co, int cnt_arg, ...)
{
        PyCodeObject *co = (PyCodeObject *)_co;
        PyFrameObject *f;
        PyObject *retval = NULL;
        PyThreadState *tstate = PyThreadState_GET();
        PyObject **fastlocals;
        PyObject *o;
        int i;
        PyObject *(*c_func)(PyFrameObject *);
        va_list vargs;
        va_start(vargs, cnt_arg);
		/* XXX Perhaps we should create a specialized
		   PyFrame_New() that doesn't take locals, but does
		   take builtins without sanity checking them.
		*/
        assert(tstate != NULL);
        f = PyFrame_New(tstate, co, glob, NULL);
        if (f == NULL)
                return NULL;

        fastlocals = f->f_localsplus;
        
        for (i = 0; i < cnt_arg; i++) {
                o = va_arg(vargs, PyObject *);
                Py_INCREF(o);
                fastlocals[i] = o;
        }
        va_end(vargs);
        c_func = func;
        retval = c_func(f);
        ++tstate->recursion_depth;
        Py_DECREF(f);
        --tstate->recursion_depth;
        return retval;
}
""")

Libr('FastCall',
"""
static PyObject * FastCall(int, PyObject *, ...);
""",
"""
static PyObject * FastCall(int na, PyObject *v,...)
{
    typedef PyObject * pyref;
    pyref args[18];
    pyref * r_arg;
    PyObject *func;
    int i;
    va_list vargs;
    r_arg = args+1;
//    printf ("=fastcall\\n");
    func = v;    
    Py_INCREF(func);

    va_start(vargs, v);
    args[0] = NULL;
    for (i = 0; i < na; i++) 
        args[i+1] = va_arg(vargs, PyObject *);
    va_end(vargs);
    r_arg = args+1;
            
    if (PyCFunction_Check(func)) {
        int flags = PyCFunction_GET_FLAGS(func);
        PyObject *x;
    
//        printf ("=cfunc 1\\n");
        if (flags & (METH_NOARGS | METH_O)) {
            PyCFunction meth = PyCFunction_GET_FUNCTION(func);
            PyObject *self = PyCFunction_GET_SELF(func);
            if (flags & METH_NOARGS && na == 0) {
                x = (*meth)(self,NULL);
                Py_DECREF(func);
                return x;
            }
            else if (flags & METH_O && na == 1) {
                Py_INCREF(args[1]);                           
                x = (*meth)(self,args[1]);
                Py_DECREF(args[1]);
                Py_DECREF(func);
                return x;
            } else
            goto stand_c;
        }
        else {  stand_c: 
            { 
                PyObject *callargs = PyTuple_New(na);
                for (i = 0; i < na; i++) {
                    Py_INCREF(args[i+1]);
                    PyTuple_SET_ITEM(callargs, i, args[i+1]);
                }
                x = PyCFunction_Call(func,callargs,NULL);
                Py_XDECREF(callargs);
                Py_DECREF(func);
                return x;
            }        
        }
        Py_DECREF(func);
        return x;
    } 
    if (PyMethod_Check(func) && PyMethod_GET_SELF(func) != NULL) {
        PyObject *oldfunc = func;
        args[0] = PyMethod_GET_SELF(func);
        func = PyMethod_GET_FUNCTION(func);
        Py_INCREF(func);
        Py_DECREF(oldfunc);
        na++;
//        printf ("=meth 1\\n");
        r_arg = args;
    } // else {
      //  Py_INCREF(func);  
    //}
    if (Py2CFunction_Check(func)) {
        Py2CCodeObject *co = (Py2CCodeObject *)PyFunction_GET_CODE(func);
        PyObject *globals = PyFunction_GET_GLOBALS(func);
        PyObject *argdefs = PyFunction_GET_DEFAULTS(func);
        PyObject **d = NULL;
        PyObject *(*c_func)(PyFrameObject *);
        int nd = 0;

//        printf ("=2Cfunc 1\\n");
        if (argdefs == NULL && co->_body.co_argcount == na && 
                co->_body.co_flags == (CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE)) {
            PyFrameObject *f;
            PyObject *retval = NULL;
            PyThreadState *tstate = PyThreadState_GET();
            PyObject **fastlocals;
            int i;

            assert(globals != NULL);
            assert(tstate != NULL);
            f = PyFrame_New(tstate, (PyCodeObject *)co, globals, NULL);
            if (f == NULL) {
                return NULL;
            }

            fastlocals = f->f_localsplus;
            for (i = 0; i < na; i++) {
                Py_INCREF(r_arg[i]);
                fastlocals[i] = r_arg[i];
            }
            c_func = co->co_function;
            retval = c_func(f);
            ++tstate->recursion_depth;
            Py_DECREF(f);
            --tstate->recursion_depth;
            Py_DECREF(func);
            return retval;
        }
        if (argdefs != NULL) {
            d = &PyTuple_GET_ITEM(argdefs, 0);
            nd = Py_SIZE(argdefs);
        }
        Py_DECREF(func);
        return PyEval_Eval2CCodeEx((PyCodeObject *)co,
                                (PyObject *)NULL, r_arg, na,
                                NULL, 0, d, nd,
                                PyFunction_GET_CLOSURE(func));
    }
    else if (PyFunction_Check(func)) {
        PyCodeObject *co = (PyCodeObject *)PyFunction_GET_CODE(func);
        PyObject *globals = PyFunction_GET_GLOBALS(func);
        PyObject *argdefs = PyFunction_GET_DEFAULTS(func);
        PyObject **d = NULL;
        int nd = 0;

//        printf ("=Func 1\\n");
        if (argdefs == NULL && co->co_argcount == na && 
                co->co_flags == (CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE)) {
            PyFrameObject *f;
            PyObject *retval = NULL;
            PyThreadState *tstate = PyThreadState_GET();
            PyObject **fastlocals;
            int i;

            assert(globals != NULL);
            assert(tstate != NULL);
            f = PyFrame_New(tstate, (PyCodeObject *)co, globals, NULL);
            if (f == NULL)
                return NULL;

            fastlocals = f->f_localsplus;
            for (i = 0; i < na; i++) {
                Py_INCREF(r_arg[i]);
                fastlocals[i] = r_arg[i];
            }
            retval = PyEval_EvalFrameEx(f,0);
            ++tstate->recursion_depth;
            Py_DECREF(f);
            --tstate->recursion_depth;
            Py_DECREF(func);
            return retval;
        }
        if (argdefs != NULL) {
            d = &PyTuple_GET_ITEM(argdefs, 0);
            nd = Py_SIZE(argdefs);
        }
        Py_DECREF(func);
        return PyEval_EvalCodeEx(co, globals,
                                (PyObject *)NULL, r_arg, na,
                                NULL, 0, d, nd,
                                PyFunction_GET_CLOSURE(func));
    } else {
//        printf ("=others 1\\n");
        PyObject *callargs = PyTuple_New(na);
        PyObject *x;
        for (i = 0; i < na; i++) {
            Py_INCREF(r_arg[i]);
            PyTuple_SET_ITEM(callargs, i, r_arg[i]);
        }
        x = PyObject_Call(func,callargs,NULL);
        Py_XDECREF(callargs);
        Py_DECREF(func);
        return x;
    }
}
""")

Libr('FastCall0',
"""
static PyObject * FastCall0(PyObject *);
""",
"""
static PyObject * FastCall0(PyObject *v)
{
    typedef PyObject * pyref;
    PyObject *func;
    PyObject *self = NULL;

    func = v;    
    Py_INCREF(func);
            
    if (PyCFunction_Check(func)) {
        int flags = PyCFunction_GET_FLAGS(func);
        PyObject *self = PyCFunction_GET_SELF(func);
        PyObject *x;
    
        if (flags & METH_NOARGS) {
            PyCFunction meth = PyCFunction_GET_FUNCTION(func);
            x = (*meth)(self,NULL);
        }
        else { 
            Py_INCREF(empty_tuple);
            x = PyCFunction_Call(func,empty_tuple,NULL);
        }
        Py_DECREF(func);
        return x;
    } 
    if (PyMethod_Check(func) && PyMethod_GET_SELF(func) != NULL) {
        PyObject *oldfunc = func;
        self = PyMethod_GET_SELF(func);
        func = PyMethod_GET_FUNCTION(func);
        Py_INCREF(func);
        Py_DECREF(oldfunc);
    
        if (Py2CFunction_Check(func)) {
            Py2CCodeObject *co = (Py2CCodeObject *)PyFunction_GET_CODE(func);
            PyObject *globals = PyFunction_GET_GLOBALS(func);
            PyObject *argdefs = PyFunction_GET_DEFAULTS(func);
            PyObject **d = NULL;
            PyObject *(*c_func)(PyFrameObject *);
            int nd = 0;
    
            if (argdefs == NULL && co->_body.co_argcount == 1 && 
                    co->_body.co_flags == (CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE)) {
                PyFrameObject *f;
                PyObject *retval = NULL;
                PyThreadState *tstate = PyThreadState_GET();
                PyObject **fastlocals;
    
                assert(globals != NULL);
                assert(tstate != NULL);
                f = PyFrame_New(tstate, (PyCodeObject *)co, globals, NULL);
                if (f == NULL) {
                    return NULL;
                }
    
                fastlocals = f->f_localsplus;
                Py_INCREF(self);
                fastlocals[0] = self;
                c_func = co->co_function;
                retval = c_func(f);
                ++tstate->recursion_depth;
                Py_DECREF(f);
                --tstate->recursion_depth;
                Py_DECREF(func);
                return retval;
            }
            if (argdefs != NULL) {
                d = &PyTuple_GET_ITEM(argdefs, 0);
                nd = Py_SIZE(argdefs);
            }
            Py_DECREF(func);
            return PyEval_Eval2CCodeEx((PyCodeObject *)co,
                                    (PyObject *)NULL, &self, 1,
                                    NULL, 0, d, nd,
                                    PyFunction_GET_CLOSURE(func));
        }
        else if (PyFunction_Check(func)) {
            PyCodeObject *co = (PyCodeObject *)PyFunction_GET_CODE(func);
            PyObject *globals = PyFunction_GET_GLOBALS(func);
            PyObject *argdefs = PyFunction_GET_DEFAULTS(func);
            PyObject **d = NULL;
            int nd = 0;
    
            if (argdefs == NULL && co->co_argcount == 1 && 
                    co->co_flags == (CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE)) {
                PyFrameObject *f;
                PyObject *retval = NULL;
                PyThreadState *tstate = PyThreadState_GET();
                PyObject **fastlocals;
    
                assert(globals != NULL);
                assert(tstate != NULL);
                f = PyFrame_New(tstate, (PyCodeObject *)co, globals, NULL);
                if (f == NULL)
                    return NULL;
    
                fastlocals = f->f_localsplus;
                Py_INCREF(self);
                fastlocals[0] = self;
    
                retval = PyEval_EvalFrameEx(f,0);
                ++tstate->recursion_depth;
                Py_DECREF(f);
                --tstate->recursion_depth;
                Py_DECREF(func);
                return retval;
            }
            if (argdefs != NULL) {
                d = &PyTuple_GET_ITEM(argdefs, 0);
                nd = Py_SIZE(argdefs);
            }
            Py_DECREF(func);
            return PyEval_EvalCodeEx(co, globals,
                                    (PyObject *)NULL, &self, 1,
                                    NULL, 0, d, nd,
                                    PyFunction_GET_CLOSURE(func));
        } else {
            PyObject *callargs = PyTuple_Pack(1, self);
            PyObject *x;
            x = PyObject_Call(func,callargs,NULL);
            Py_XDECREF(callargs);
            Py_DECREF(func);
            return x;
        }

    } else {
        if (Py2CFunction_Check(func)) {
            Py2CCodeObject *co = (Py2CCodeObject *)PyFunction_GET_CODE(func);
            PyObject *globals = PyFunction_GET_GLOBALS(func);
            PyObject *argdefs = PyFunction_GET_DEFAULTS(func);
            PyObject **d = NULL;
            PyObject *(*c_func)(PyFrameObject *);
            int nd = 0;
    
            if (argdefs == NULL && co->_body.co_argcount == 0 && 
                    co->_body.co_flags == (CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE)) {
                PyFrameObject *f;
                PyObject *retval = NULL;
                PyThreadState *tstate = PyThreadState_GET();
    
                assert(globals != NULL);
                assert(tstate != NULL);
                f = PyFrame_New(tstate, (PyCodeObject *)co, globals, NULL);
                if (f == NULL) {
                    return NULL;
                }
                c_func = co->co_function;
                retval = c_func(f);
                ++tstate->recursion_depth;
                Py_DECREF(f);
                --tstate->recursion_depth;
                Py_DECREF(func);
                return retval;
            }
            if (argdefs != NULL) {
                d = &PyTuple_GET_ITEM(argdefs, 0);
                nd = Py_SIZE(argdefs);
            }
            Py_DECREF(func);
            return PyEval_Eval2CCodeEx((PyCodeObject *)co,
                                    (PyObject *)NULL, NULL, 0,
                                    NULL, 0, d, nd,
                                    PyFunction_GET_CLOSURE(func));
        }
        else if (PyFunction_Check(func)) {
            PyCodeObject *co = (PyCodeObject *)PyFunction_GET_CODE(func);
            PyObject *globals = PyFunction_GET_GLOBALS(func);
            PyObject *argdefs = PyFunction_GET_DEFAULTS(func);
            PyObject **d = NULL;
            int nd = 0;
    
            if (argdefs == NULL && co->co_argcount == 0 && 
                    co->co_flags == (CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE)) {
                PyFrameObject *f;
                PyObject *retval = NULL;
                PyThreadState *tstate = PyThreadState_GET();
    
                assert(globals != NULL);
                assert(tstate != NULL);
                f = PyFrame_New(tstate, (PyCodeObject *)co, globals, NULL);
                if (f == NULL)
                    return NULL;
    
                retval = PyEval_EvalFrameEx(f,0);
                ++tstate->recursion_depth;
                Py_DECREF(f);
                --tstate->recursion_depth;
                Py_DECREF(func);
                return retval;
            }
            if (argdefs != NULL) {
                d = &PyTuple_GET_ITEM(argdefs, 0);
                nd = Py_SIZE(argdefs);
            }
            Py_DECREF(func);
            return PyEval_EvalCodeEx(co, globals,
                                    (PyObject *)NULL, NULL, 0,
                                    NULL, 0, d, nd,
                                    PyFunction_GET_CLOSURE(func));
        } else {
            PyObject *x;
            x = PyObject_Call(func,empty_tuple,NULL);
            Py_DECREF(func);
            return x;
        }


    } 
}
""")


Libr('_PyEval_DoRaise',
"""
static int
_PyEval_DoRaise(PyObject *, PyObject *, PyObject *);
""",
"""
static int
_PyEval_DoRaise(PyObject *type, PyObject *value, PyObject *tb)
{
	if (type == NULL) {
		/* Reraise */
		PyThreadState *tstate = PyThreadState_GET();
		type = tstate->exc_type == NULL ? Py_None : tstate->exc_type;
		value = tstate->exc_value;
		tb = tstate->exc_traceback;
		Py_XINCREF(type);
		Py_XINCREF(value);
		Py_XINCREF(tb);
	}

	/* We support the following forms of raise:
	   raise <class>, <classinstance>
	   raise <class>, <argument tuple>
	   raise <class>, None
	   raise <class>, <argument>
	   raise <classinstance>, None
	   raise <string>, <object>
	   raise <string>, None

	   An omitted second argument is the same as None.

	   In addition, raise <tuple>, <anything> is the same as
	   raising the tuple's first item (and it better have one!);
	   this rule is applied recursively.

	   Finally, an optional third argument can be supplied, which
	   gives the traceback to be substituted (useful when
	   re-raising an exception after examining it).  */

	/* First, check the traceback argument, replacing None with
	   NULL. */
	if (tb == Py_None) {
		Py_DECREF(tb);
		tb = NULL;
	}
	else if (tb != NULL && !PyTraceBack_Check(tb)) {
		PyErr_SetString(PyExc_TypeError,
			   "raise: arg 3 must be a traceback or None");
		goto raise_error;
	}

	/* Next, replace a missing value with None */
	if (value == NULL) {
		value = Py_None;
		Py_INCREF(value);
	}

	/* Next, repeatedly, replace a tuple exception with its first item */
	while (PyTuple_Check(type) && PyTuple_Size(type) > 0) {
		PyObject *tmp = type;
		type = PyTuple_GET_ITEM(type, 0);
		Py_INCREF(type);
		Py_DECREF(tmp);
	}

	if (PyExceptionClass_Check(type))
		PyErr_NormalizeException(&type, &value, &tb);

	else if (PyExceptionInstance_Check(type)) {
		/* Raising an instance.  The value should be a dummy. */
		if (value != Py_None) {
			PyErr_SetString(PyExc_TypeError,
			  "instance exception may not have a separate value");
			goto raise_error;
		}
		else {
			/* Normalize to raise <class>, <instance> */
			Py_DECREF(value);
			value = type;
			type = PyExceptionInstance_Class(type);
			Py_INCREF(type);
		}
	}
	else {
		/* Not something you can raise.  You get an exception
		   anyway, just not what you specified :-) */
		PyErr_Format(PyExc_TypeError,
			"exceptions must be classes or instances, not %s",
			type->ob_type->tp_name);
		goto raise_error;
	}

	assert(PyExceptionClass_Check(type));
	if (Py_Py3kWarningFlag && PyClass_Check(type)) {
		if (PyErr_WarnEx(PyExc_DeprecationWarning,
				"exceptions must derive from BaseException "
				"in 3.x", 1) < 0)
			goto raise_error;
	}

	PyErr_Restore(type, value, tb);
	if (tb == NULL)
		return WHY_EXCEPTION;
	else
		return WHY_RERAISE;
 raise_error:
	Py_XDECREF(value);
	Py_XDECREF(type);
	Py_XDECREF(tb);
	return WHY_EXCEPTION;
}
""")     
Libr('_PyEval_ImportAllFrom',
"""
static int
_PyEval_ImportAllFrom(PyObject *, PyObject *);
""",
"""
static int
_PyEval_ImportAllFrom(PyObject *locals, PyObject *v)
{
	PyObject *all = PyObject_GetAttrString(v, "__all__");
	PyObject *dict, *name, *value;
	int skip_leading_underscores = 0;
	int pos, err;

	if (all == NULL) {
		if (!PyErr_ExceptionMatches(PyExc_AttributeError))
			return -1; /* Unexpected error */
		PyErr_Clear();
		dict = PyObject_GetAttrString(v, "__dict__");
		if (dict == NULL) {
			if (!PyErr_ExceptionMatches(PyExc_AttributeError))
				return -1;
			PyErr_SetString(PyExc_ImportError,
			"from-import-* object has no __dict__ and no __all__");
			return -1;
		}
		all = PyMapping_Keys(dict);
		Py_DECREF(dict);
		if (all == NULL)
			return -1;
		skip_leading_underscores = 1;
	}

	for (pos = 0, err = 0; ; pos++) {
		name = PySequence_GetItem(all, pos);
		if (name == NULL) {
			if (!PyErr_ExceptionMatches(PyExc_IndexError))
				err = -1;
			else
				PyErr_Clear();
			break;
		}
		if (skip_leading_underscores &&
		    PyString_Check(name) &&
		    PyString_AS_STRING(name)[0] == '_')
		{
			Py_DECREF(name);
			continue;
		}
		value = PyObject_GetAttr(v, name);
		if (value == NULL)
			err = -1;
		else if (PyDict_CheckExact(locals))
			err = PyDict_SetItem(locals, name, value);
		else
			err = PyObject_SetItem(locals, name, value);
		Py_DECREF(name);
		Py_XDECREF(value);
		if (err != 0)
			break;
	}
	Py_DECREF(all);
	return err;
}
""")
Libr('_PyEval_BuildClass', 
"""
static PyObject *
_PyEval_BuildClass(PyObject *, PyObject *, PyObject *);
""",
"""
static PyObject *
_PyEval_BuildClass(PyObject *methods, PyObject *bases, PyObject *name)
{
	PyObject *metaclass = NULL, *result, *base;

	if (PyDict_Check(methods))
		metaclass = PyDict_GetItemString(methods, "__metaclass__");
	if (metaclass != NULL)
		Py_INCREF(metaclass);
	else if (PyTuple_Check(bases) && PyTuple_GET_SIZE(bases) > 0) {
		base = PyTuple_GET_ITEM(bases, 0);
		metaclass = PyObject_GetAttrString(base, "__class__");
		if (metaclass == NULL) {
			PyErr_Clear();
			metaclass = (PyObject *)base->ob_type;
			Py_INCREF(metaclass);
		}
	}
	else {
		PyObject *g = PyEval_GetGlobals();
		if (g != NULL && PyDict_Check(g))
			metaclass = PyDict_GetItemString(g, "__metaclass__");
		if (metaclass == NULL)
			metaclass = (PyObject *) &PyClass_Type;
		Py_INCREF(metaclass);
	}
	result = PyObject_CallFunctionObjArgs(metaclass, name, bases, methods,
					      NULL);
	Py_DECREF(metaclass);
	if (result == NULL && PyErr_ExceptionMatches(PyExc_TypeError)) {
		/* A type error here likely means that the user passed
		   in a base that was not a class (such the random module
		   instead of the random.random type).  Help them out with
		   by augmenting the error message with more information.*/

		PyObject *ptype, *pvalue, *ptraceback;

		PyErr_Fetch(&ptype, &pvalue, &ptraceback);
		if (PyString_Check(pvalue)) {
			PyObject *newmsg;
			newmsg = PyString_FromFormat(
				"Error when calling the metaclass bases\\n"
				"    %s",
				PyString_AS_STRING(pvalue));
			if (newmsg != NULL) {
				Py_DECREF(pvalue);
				pvalue = newmsg;
			}
		}
		PyErr_Restore(ptype, pvalue, ptraceback);
	}
	return result;
}
""")
     

Libr('_PyEval_ExecStatement',
"""static int
_PyEval_ExecStatement(PyFrameObject * , PyObject *, PyObject *, PyObject *);
""",
"""
static int
_PyEval_ExecStatement(PyFrameObject * f, PyObject *prog, PyObject *globals,
	       PyObject *locals)
{
	int n;
	PyObject *v;
	int plain = 0;

	if (PyTuple_Check(prog) && globals == Py_None && locals == Py_None &&
	    ((n = PyTuple_Size(prog)) == 2 || n == 3)) {
		/* Backward compatibility hack */
		globals = PyTuple_GetItem(prog, 1);
		if (n == 3)
			locals = PyTuple_GetItem(prog, 2);
		prog = PyTuple_GetItem(prog, 0);
	}
	if (globals == Py_None) {
		globals = PyEval_GetGlobals();
		if (locals == Py_None) {
			locals = PyEval_GetLocals();
			plain = 1;
		}
		if (!globals || !locals) {
			PyErr_SetString(PyExc_SystemError,
					"globals and locals cannot be NULL");
			return -1;
		}
	}
	else if (locals == Py_None)
		locals = globals;
	if (!PyString_Check(prog) &&
	    !PyUnicode_Check(prog) &&
	    !PyCode_Check(prog) &&
	    !PyFile_Check(prog)) {
		PyErr_SetString(PyExc_TypeError,
			"exec: arg 1 must be a string, file, or code object");
		return -1;
	}
	if (!PyDict_Check(globals)) {
		PyErr_SetString(PyExc_TypeError,
		    "exec: arg 2 must be a dictionary or None");
		return -1;
	}
	if (!PyMapping_Check(locals)) {
		PyErr_SetString(PyExc_TypeError,
		    "exec: arg 3 must be a mapping or None");
		return -1;
	}
	if (PyDict_GetItemString(globals, "__builtins__") == NULL)
		PyDict_SetItemString(globals, "__builtins__", b);
	if (PyCode_Check(prog)) {
		if (PyCode_GetNumFree((PyCodeObject *)prog) > 0) {
			PyErr_SetString(PyExc_TypeError,
		"code object passed to exec may not contain free variables");
			return -1;
		}
		v = PyEval_EvalCode((PyCodeObject *) prog, globals, locals);
	}
	else if (PyFile_Check(prog)) {
		FILE *fp = PyFile_AsFile(prog);
		char *name = PyString_AsString(PyFile_Name(prog));
		PyCompilerFlags cf;
		if (name == NULL)
			return -1;
		cf.cf_flags = 0;
		if (PyEval_MergeCompilerFlags(&cf))
			v = PyRun_FileFlags(fp, name, Py_file_input, globals,
					    locals, &cf);
		else
			v = PyRun_File(fp, name, Py_file_input, globals,
				       locals);
	}
	else {
		PyObject *tmp = NULL;
		char *str;
		PyCompilerFlags cf;
		cf.cf_flags = 0;
#ifdef Py_USING_UNICODE
		if (PyUnicode_Check(prog)) {
			tmp = PyUnicode_AsUTF8String(prog);
			if (tmp == NULL)
				return -1;
			prog = tmp;
			cf.cf_flags |= PyCF_SOURCE_IS_UTF8;
		}
#endif
		if (PyString_AsStringAndSize(prog, &str, NULL))
			return -1;
		if (PyEval_MergeCompilerFlags(&cf))
			v = PyRun_StringFlags(str, Py_file_input, globals,
					      locals, &cf);
		else
			v = PyRun_String(str, Py_file_input, globals, locals);
		Py_XDECREF(tmp);
	}
	if (plain)
		PyFrame_LocalsToFast(f, 0);
	if (v == NULL)
		return -1;
	Py_DECREF(v);
	return 0;
}
""")
     

def write_as_c(cfile, nmmodule):
    global pregenerated
    print_to(cfile,c_head)
    Used('PyEval_Eval2CCodeEx')
    for cmds, o, co, nm, nm_for_c in pregenerated:
        print_to(cfile, 'static PyObject * codefunc_' + nm_for_c +'(PyFrameObject *);')
        if nm != nm_for_c and (Is3(nm, 'ArgCallCalculatedDef') or \
                               Is3(nm_for_c, 'ArgCallCalculatedDef')):
            Fatal('Dirrect !!!', nm, nm_for_c)
        if nm == nm_for_c  and Is3(nm, 'ArgCallCalculatedDef'): # and direct_call and subroutine_can_be_direct(nm):
            arg = ""
            coarg = co.co_argcount
            hidden = all_co[co].hidden_arg_direct
            if co.co_flags & 0x4:
                assert len(hidden) == 0
                coarg += 1
            if coarg == 0:
                arg = '(void)'
            else:    
                arg = ''
                i = 0
                while coarg > 1:
                    if i not in hidden:
                        arg += ', PyObject *'
                    coarg -= 1
                    i += 1
                if i not in hidden:    
                    arg += ', PyObject *'
                if arg == '':
                    arg = '  void'    
                arg = '(' + arg[2:] + ')'
            if IsRetVoid(nm_for_c):    
                print_to(cfile, 'static int _Direct_' + nm_for_c + arg + ';')    
            else:
                print_to(cfile, 'static PyObject * _Direct_' + nm_for_c + arg + ';')    
    for a,b,c in Iter3(None, 'Used', True):
        if IsLibr(a):
            print_to(cfile, LibrDcl(a))
    for cmds, o, co, nm, nm_for_c in pregenerated:
        for p in o:
            print_to(cfile, p)
    pregenerate_code_objects()
    generate_consts(cfile)    
    generate_calculated_consts(cfile)    
    generate_builtin(cfile)
    generate_init(cfile, nmmodule)    
    print_to(cfile, c_tail)
    for a,b,c in Iter3(None, 'Used', True):
        if IsLibr(a):
            print_to(cfile, LibrDef(a))
 
def generate_init(cfile, nmmodule):
    global labl
    print_to(cfile, 'PyMODINIT_FUNC init'+ '_c_' + nmmodule+'(void);')
    print_to(cfile, 'PyMODINIT_FUNC init' + '_c_' + nmmodule+'(void){')
    print_to(cfile, '    patch_code2c();')
    print_to(cfile, '    b = PyImport_AddModule("__builtin__");')
    print_to(cfile, '    bdict = PyModule_GetDict(b);')
    if len(loaded_builtin) > 0:
        print_to(cfile, '    load_builtin();')
    print_to(cfile, '    init_consts();')
    o = Out()
    print_to(cfile, '    PyImport_Exec2CCodeModuleEx(\"_c_' + nmmodule +'", '  +const_to(_n2c['Init_filename']) +');')
    print_to(cfile, '    PyDict_SetItemString(glob, \"__compile_hash__\", PyInt_FromString(\"' + str(hash_compile) + '\", NULL, 0));')
    print_to(cfile, '}')
     
def nmvar_to_loc(v):
    if '(' in v or ')' in v or '[' in v or ']' in v or '.' in v or '-' in v:
        v = v.replace('[', '_1_')    
        v = v.replace(']', '_9_')            
        v = v.replace('(', '_2_')    
        v = v.replace(')', '_7_')            
        v = v.replace('.', '_5_')    
        v = v.replace('-', '_6_')    
    return v

def generate_stand_header(l, co, ltemp, typed, o):
    orepr = repr(o)
    if ltemp != 0:
        for i in range(ltemp):
            l.append('PyObject * temp_'+str(i)+' = 0;')
    for i,(f,t) in enumerate(typed):
        nm = t + '_' + str(i)
        if t != 'label' and nm in orepr:
            l.append(t + ' ' + t +'_' + str(i) + ';')
    s = 'enum{' 
    for i,v in enumerate(co.co_varnames):        
        if i > 0:
            s += ', '
        v = nmvar_to_loc(v)
        s += 'Loc_' + v 
    s += '};'
    if s != 'enum{};':
        l.append(s)  
        
def generate_header(nm, o, co, ltemp, typed):
    l = []
    l.append('')        

    l.append('static PyObject * codefunc_' + nm +'(PyFrameObject *f) {')
    if nm == 'Init_filename':
        l.append('glob = f->f_locals;')
    generate_stand_header(l, co, ltemp, typed, o)
    s = 'enum{' 
    for i,v in enumerate(co.co_cellvars + co.co_freevars):    
        if i > 0:
            s += ', '
        v = nmvar_to_loc(v)
        s += 'Loc2_' + v 
    s += '};'
    if s != 'enum{};':
        l.append(s)  
    l.append('register PyObject **fastlocals, **freevars;')
    l.append('PyThreadState *tstate = PyThreadState_GET();')
    if not redefined_attribute:
        _ddic = all_co[current_co]    
        if _ddic.self_dict_getattr_used:
            if _ddic.method_new_class:
                l.append('PyObject **self_dict;')
            elif _ddic.method_old_class:
                l.append('PyObject *self_dict;')
            else:
                Fatal('')    
        for k in _ddic.dict_getattr_used.iterkeys():
            l.append('PyObject *_%s_dict = 0;' %k)
    if calc_ref_total:
        l.append('Py_ssize_t l_Py_RefTotal;')
    l.append('if (f == NULL) return NULL;')
    if check_recursive_call:
        l.append('if (Py_EnterRecursiveCall("")) return NULL;')
    l.append('tstate->frame = f;')
    l.append('fastlocals = f->f_localsplus;')
    l.append('freevars = fastlocals + f->f_code->co_nlocals;')
    l.append('f->f_stacktop = NULL;')
    if not redefined_attribute:
        _ddic = all_co[current_co]    
        if _ddic.self_dict_getattr_used:
            if _ddic.method_new_class:
                l.append('self_dict = _PyObject_GetDictPtr(GETLOCAL(self));')
            elif _ddic.method_old_class:
                l.append('self_dict = ((PyInstanceObject *)GETLOCAL(self))->in_dict;')
            else:
                Fatal('')    
        for k in _ddic.dict_getattr_used.iterkeys():
            l.append('if (PyInstance_Check(GETLOCAL(%s))) {' % k)
            l.append('_%s_dict = ((PyInstanceObject *)GETLOCAL(%s))->in_dict;' %(k,k))
            l.append('}else {')
            l.append('PyObject **refdict = _PyObject_GetDictPtr(GETLOCAL(%s));' %k)
            l.append('if (refdict && *refdict) _%s_dict = *refdict;' %k )
            l.append('}')
##    if ltemp > 0:
##        for n in range(ltemp):
##            l.append('temp[' + str(n) + '] = 0;')
    if calc_ref_total:
        l.append('l_Py_RefTotal = _Py_RefTotal;')
    l.append('')        
    l.extend(o)
    o[:] = l[:]         
    return   

def generate_from_frame_to_direct_stube(co, o, nm, cmds):
    l = []
    l.append('')        

    l.append('static PyObject * codefunc_' + nm +'(PyFrameObject *f) {')
    generate_stand_header(l, co, 0, [], o)
    s = 'enum{' 
    for i,v in enumerate(co.co_cellvars + co.co_freevars):    
        if i > 0:
            s += ', '
        v = nmvar_to_loc(v)
        s += 'Loc2_' + v 
    s += '};'
    if s != 'enum{};':
        l.append(s)  
    l.append('register PyObject **fastlocals;')
    l.append('PyThreadState *tstate = PyThreadState_GET();')
    if not IsRetVoid(nm):
            l.append('PyObject * ret;')
    l.append('if (f == NULL) return NULL;')
##    if check_recursive_call:
##        l.append('if (Py_EnterRecursiveCall("")) return NULL;')
    l.append('tstate->frame = f;')
    l.append('fastlocals = f->f_localsplus;')
    l.append('')        

    arg = ""
    coarg = co.co_argcount
    if co.co_flags & 0x4:
        coarg += 1
    cnt_arg = coarg    
    arg = ''
    i = 0
    for i in range(coarg):
        v = nmvar_to_loc(co.co_varnames[i])
        if i != 0:
            arg += ', '
        arg += 'GETLOCAL(' + v + ')'
    arg = '(' + arg + ')'
    if IsRetVoid(nm):
        l.append('if (_Direct_' + nm + arg + ' == -1) {')
        l.append('tstate->frame = f->f_back;')
        l.append('return NULL;')
        l.append('} else {')
        l.append('tstate->frame = f->f_back;')
        l.append('Py_INCREF(Py_None);')
        l.append('return Py_None;')
        l.append('}')
    else:
        l.append('ret = _Direct_' + nm + arg + ';')
        l.append('tstate->frame = f->f_back;')
        l.append('return ret;')
    o[:] = l[:]    
    o.Raw('}')     
    pregenerated.append((cmds, o, co, cmds[0][1], nm))    

def generate_header_direct(nm, o, co, ltemp, typed, hidden):
    l = []
    l.append('')        
    arg = ""
    coarg = co.co_argcount
    if co.co_flags & 0x4:
        assert len(hidden) == 0
        coarg += 1
    cnt_arg = coarg    
    if coarg == 0:
        arg = '(void)'
    else:    
        arg = ''
        i = 0
        while coarg > 1:
            if not i in hidden:
                arg += ', PyObject * Arg_' + str(i) 
            i += 1
            coarg -= 1
        if not i in hidden:
            arg += ', PyObject * Arg_' + str(i)
        if arg == '':
            arg = '  void'    
        arg = '(' + arg[2:] + ')'
    if IsRetVoid(nm):     
        l.append('static int _Direct_' + nm + arg + '{')
    else:    
        l.append('static PyObject * _Direct_' + nm + arg + '{')
    generate_stand_header(l, co, ltemp, typed, o)
    s = 'enum{' 
    if len(co.co_varnames) > 0:
        l.append('register PyObject *fastlocals[' + str(len(co.co_varnames)) +'];')
    if calc_ref_total:
        l.append('Py_ssize_t l_Py_RefTotal;')
        l.append('l_Py_RefTotal = _Py_RefTotal;')
    for i,v in enumerate(co.co_varnames):
        if i >= cnt_arg or i in hidden:
            l.append('fastlocals[' + str(i) + '] = NULL;')   
    if line_number:
        l.append('int PyLine = ' + str(co.co_firstlineno) + ';')     
        l.append('int PyAddr = 0;')     
    if not redefined_attribute:
        _ddic = all_co[current_co]    
        if _ddic.self_dict_getattr_used:
            if _ddic.method_new_class:
                l.append('PyObject **self_dict;')
            elif _ddic.method_old_class:
                l.append('PyObject *self_dict;')
        for k in _ddic.dict_getattr_used.iterkeys():
            l.append('PyObject *_%s_dict = 0;' %k)
    for i in range(cnt_arg):
        if i in hidden:
            continue
        l.append('fastlocals[' + str(i) + '] = Arg_' + str(i) + ';')    
        l.append('Py_INCREF(Arg_' + str(i) +');')    
    if not redefined_attribute:
        _ddic = all_co[current_co]    
        if _ddic.self_dict_getattr_used:
            if _ddic.method_new_class:
                l.append('self_dict = _PyObject_GetDictPtr(GETLOCAL(self));')
            elif _ddic.method_old_class:
                l.append('self_dict = ((PyInstanceObject *)GETLOCAL(self))->in_dict;')
        for k in _ddic.dict_getattr_used.iterkeys():
            l.append('if (PyInstance_Check(GETLOCAL(%s))) {' % k)
            l.append('_%s_dict = ((PyInstanceObject *)GETLOCAL(%s))->in_dict;' %(k,k))
            l.append('}else {')
            l.append('PyObject **refdict = _PyObject_GetDictPtr(GETLOCAL(%s));' %k)
            l.append('if (refdict && *refdict) _%s_dict = *refdict;' %k )
            l.append('}')
##    if ltemp > 0:
##        for n in range(ltemp):
##            l.append('temp[' + str(n) + '] = 0;')
    l.append('')        
    l.extend(o)
    o[:] = l[:]         
    return   

    
def stub_generator(co):
    pass    
    
def generate_list(lis, o = None):
    i = 0
    if o is None:
        o = []
    have_compaund = False    
    len_o = 0
    if o is not None:
        len_o = len(o)
    if recalc_refcnt:
        cnt_prev = New('Py_ssize_t')
        line_prev = New('int')
        o.Raw(cnt_prev, '= _Py_RefTotal;')
        o.Raw(line_prev, '= __LINE__;')
    while i < len(lis):
        it = lis[i]
        head = it[0]
        assert head[0] != ')' and head[0:2] != ')(' 
        if IsBeg(head):
            i1 = get_closed_pair(lis[:],i)
            o.Comment(it)
            generate_compaund_statement(head[1:], lis[i:i1+1], o)
            i = i1 + 1
            have_compaund = True
        else:
            o.Comment(it)
            generate_statement(head, it, o)
            i += 1
        if recalc_refcnt:
            o.Raw('if ((int)(_Py_RefTotal -', cnt_prev, ')) { printf("\\nfunc %s, line %5d:%5d, refcnt %d\\n", "', func, '", ',\
                   line_prev, ',__LINE__, (int)(_Py_RefTotal -', cnt_prev, '));} ',\
                   cnt_prev, '= _Py_RefTotal; ', line_prev, '= __LINE__;')
    if recalc_refcnt:
        o.Cls(cnt_prev, line_prev)
    return o

def get_closed_pair(lis,i):
    i1 = i+1
    while i1 < len(lis):
       if lis[i1][0][0] == ')' and lis[i1][0][0:2] != ')(':
           return i1
       i1 += 1
    Fatal('Can\'t get closet pair', lis[i:])
    
def IsRetVoid(nm_c):
    return nm_c in detected_return_type and detected_return_type[nm_c] == Kl_None

def generate_statement(head,it, o):
    global current_co
    if head == '.L':
        if line_number:
            if is_direct_current:
                o.Raw('PyLine = ', str(it[1]), ';')
                o.Raw('PyAddr = ', str(Line2Addr[it[1]]), ';')
            else:    
                o.Stmt('f->f_lineno', '=', it[1])
                o.Raw('f->f_lasti = ', str(Line2Addr[it[1]]), ';')
            if print_pyline:
                o.Stmt('printf', '\"Py:' + filename +':%5d\\n\"', it[1])
        
        return

    if head == 'STORE':
        if len(it[2]) == 1 and len(it[1]) == 1:
            if is_like_float(it[2][0]) and it[2][0][0] != 'CONST':
                acc = []
                isfloat = {}
                if parse_for_float_expr(it[2][0], acc, isfloat):
                    if len(acc) >= 2 or \
                       (len(acc) == 1 and acc[0][0] == 'CONST' and \
                        type(acc[0][1]) is float):
                       return generate_mixed_float_expr(it,acc,o, isfloat)
            ref = Expr1(it[2][0], o)
            if it[2][0][0] == 'FAST':
                stor = ('STORE_FAST', it[2][0][1])
                if repr(stor) in repr(it[1][0]):
                    ref2 = New()
                    o.Raw(ref2, ' = ', ref, ';')
                    o.INCREF(ref2)
                    ref = ref2
                    ref2 = None
            generate_store(it[1][0], ref, o, it[2][0])
            o.Cls(ref)
            if ref not in g_refs2:
                o.ZeroTemp(ref)
            return
        Fatal('MultyStore', it)

    if head == 'SEQ_ASSIGN':
        ref = Expr1(it[2], o)
        PushAcc([ref], [ref])
        for i in range(len(it[1])-1):
            o.INCREF(ref)
        for iit in it[1]:
          generate_store(iit, ref, o, it[2])
        PopAcc(o, False)
        o.Cls(ref)
        return

    if head == 'SET_EXPRS_TO_VARS':
        if len(it[1]) == 2 and it[2][0] == 'CLONE':
            ref = Expr1(it[2][1],o)
            o.ClsFict(ref)
            generate_store(it[1][0], ref, o, it[2][1])
            generate_store(it[1][1], ref, o, it[2][1])
            if istempref(ref):
                o.CLEAR(ref)
            return
        assert len(it[2]) == len(it[1])
        stor = dict.fromkeys([x[0] for x in it[1]]).keys()
        if len(stor) == 1 and stor[0] == 'STORE_FAST':
            gets = [('FAST', x[1]) for x in it[1]]
            gets.extend([('LOAD_FAST', x[1]) for x in it[1]])
            pure = True
            for ge in gets:
                if repr(ge) in repr(it[2]):
                    pure = False
            if pure:
                for i,iit in enumerate(it[1]):
                    ref1 = Expr1(it[2][i], o)
                    generate_store(iit,ref1,o, it[2][i])
                    o.Cls(ref1)
                return
        expr = TupleFromArgs(it[2])
        ref = Expr1(expr, o)
        its = it[1]
        s_ref = CVar(ref)
        for i,iit in enumerate(its):
            ref1 = New()
            o.Stmt(ref1, '=', 'PyTuple_GET_ITEM', ref, i)
            generate_store(iit,ref1,o, ('!PyTuple_GET_ITEM',))
            o.Cls(ref1)
        o.Cls(ref)
        return

    if head == 'RETURN_VALUE':
        _ddic = all_co[current_co]    
        for drop in dropped_temp:
            for t in drop[1]:
                if istempref(t):
                    o.Raw('Py_CLEAR(', t, ');')
        try_jump = try_jump_context[:]
        if len(it[1]) == 1 and it[1][0] == 'f->f_locals':
            assert not is_direct_current
            ref = New()
            o.Raw(ref, ' = ', it[1][0], ';')
            o.INCREF(ref)
            PopClearAll(o)
            if checkmaxref != 0:
                o.Raw('if ((', ref, ')->ob_refcnt > ', checkmaxref, ') printf("line %5d, line %6d \\n", __LINE__,(', ref, ')->ob_refcnt);')
            if not is_direct_current:
                if check_recursive_call:
                    o.Raw('Py_LeaveRecursiveCall();')
            if not is_direct_current:
                o.Raw('tstate->frame = f->f_back;')
            o.Raw('return ', ref, ';')
            o.Cls(ref)
            return
        isvoid = is_direct_current and IsRetVoid(_ddic.cmds[0][1])
        if isvoid:
            assert TypeExpr(it[1]) == Kl_None
        ref = Expr1(it[1], o)
        if isvoid:
            o.Cls(ref)
            ref = None
        elif not istempref(ref) and not ( is_direct_current and ref[0] == 'FAST'):
            o.INCREF(ref) 

        if not is_direct_current:
            while len(try_jump) > 0:
                if try_jump[-1]:
                    if type(try_jump[-1]) is list:
                        o.Comment((')(FINALLY',))
                        o.Stmt('{')
                        generate_list(try_jump[-1],o)
                        o.Raw('}')                    
                del try_jump[-1]

        if is_direct_current:
            for i,v in enumerate(current_co.co_varnames):
                nmvar = nmvar_to_loc(v)
                if isvoid or (len(ref) != 2 or ref[0] != 'FAST' or ref[1] != nmvar): 
                    o.CLEAR('GETLOCAL(' + nmvar + ')')
        for i,v in enumerate(current_co.co_freevars):
            nmvar = nmvar_to_loc(v)
            if isvoid or (len(ref) != 2 or ref[0] != 'LOAD_CLOSURE' or ref[1] != nmvar): 
                o.CLEAR('GETFREEVAR(' + nmvar + ')')

        PopClearAll(o)
        if calc_ref_total:
            o.Raw('if ((_Py_RefTotal - l_Py_RefTotal) > 0) {printf ("func ', current_co.co_name, ' delta ref = %d\\n", (int)(_Py_RefTotal - l_Py_RefTotal));}')
        if stat_func == func:
            o.Raw('{')
            o.Raw('FILE * _refs = fopen(\"%s_end\", \"w+\");' % func)
            o.Raw('_Py_PrintReferences2(_refs);')  
            o.Raw('fclose(_refs);')     
            o.Raw('}')    
        if not is_direct_current:
            o.Raw('if (tstate->frame->f_exc_type != NULL) {')
            o.Stmt('_PyEval_reset_exc_info', 'f->f_tstate')       
            o.Raw('}')
            if not is_direct_current:
                if check_recursive_call:
                    o.Raw('Py_LeaveRecursiveCall();')
            o.Raw('tstate->frame = f->f_back;')
        if isvoid:
            o.Raw('return 0;')
        else:        
            o.Stmt('return', ref)   
            o.ClsFict(ref)
        return

    if head == 'CALL_PROC':
        Fatal('Illegal', it)
        return
    if head == 'UNPUSH':
        if like_append(it[1]):
            generate_may_be_append(it[1], o)
            return
        _v = []
        if like_append_const(it[1], _v):
            generate_may_be_append_const(it[1], o, _v)
            return
        ref = Expr1(it[1], o)
        o.Cls(ref)
        return
    if head == 'PYAPI_CALL':
        iit = it[1]
        gen = []
        for i in range(len(iit)):
            if i > 0:
                if type(iit[i]) is tuple and len(iit[i]) > 0:
                    gen.append(Expr1(iit[i], o))
                else:
                    gen.append(iit[i])
        if iit[0] in CFuncIntCheck:        
#            Debug('iiy', iit, gen)
            args = (iit[0],) + tuple(gen)       
            o.Stmt(*args)
            o.Cls(*gen)
            return    
        elif iit[0] in CFuncVoid:        
            args = (iit[0],) + tuple(gen)       
            o.Stmt(*args)
            o.Cls(*gen)
            return    
        else:
            Fatal('', it)

    if head == 'IMPORT_FROM_AS':
        if it[3][0] == 'CONST' and len(it[3][1]) == len(it[4]):
            ref = Expr1(('!IMPORT_NAME', it[1],it[2],it[3]), o)
            for i in range(len(it[4])):
                ref1 = New()
                o.Raw('if ((', ref1, ' = PyObject_GetAttr( ', ref, ', ', ('CONST', it[3][1][i]), ')) == NULL) {')
                o.Raw('if (PyErr_ExceptionMatches(PyExc_AttributeError)) {')
                o.Raw('PyErr_Format(PyExc_ImportError, ', ('"cannot import name %s"' % it[3][1][i]), ');')
                o.Raw('}')
                o.Raw('goto ', labl, ';')
                UseLabl()
                o.Raw('}')
                generate_store(it[4][i], ref1,o, it)
            o.Cls(ref)
            return
        Fatal('', it)
        return
    if head == 'PRINT_ITEM_TO_2':
        ref1, ref2 = Expr(o, it[1:])
        o.Stmt('_PyEval_PRINT_ITEM_TO_2', ref1, ref2)
        o.Cls(ref1, ref2)
        return
    if head == 'PRINT_ITEM_AND_NEWLINE_TO_2':
        ref1, ref2 = Expr(o, it[1:])
        o.Stmt('_PyEval_PRINT_ITEM_TO_2', ref1, ref2)
        o.Stmt('_PyEval_PRINT_NEWLINE_TO_1', ref1)
        o.Cls(ref1, ref2)
        return
    if head == 'PRINT_ITEM_AND_NEWLINE_TO_3':
        ref1, ref2, ref3 = Expr(o, it[1:])
        o.Stmt('_PyEval_PRINT_ITEM_TO_2', ref1, ref2)
        o.Stmt('_PyEval_PRINT_ITEM_TO_2', ref1, ref3)
        o.Stmt('_PyEval_PRINT_NEWLINE_TO_1', ref1)
        o.Cls(ref1, ref2, ref3)
        return
    if head == 'PRINT_ITEM_1':
        ref1 = Expr1(it[1], o)
        o.Stmt('_PyEval_PRINT_ITEM_1', ref1)
        o.Cls(ref1)
        return
    if head == 'PRINT_NEWLINE_TO_1':
        ref1 = Expr1(it[1], o)
        o.Stmt('_PyEval_PRINT_NEWLINE_TO_1', ref1)
        o.Cls(ref1)
        return
    if head == 'PRINT_NEWLINE':
        o.Stmt('_PyEval_PRINT_NEWLINE_TO_1', 'NULL')
        return
    if head == 'DELETE_ATTR_2':
        ref1, ref2 = Expr(o, it[1:])
        o.Stmt('PyObject_SetAttr', ref1, ref2, 'NULL')
        o.Cls(ref1, ref2)
        return
    if head == 'DELETE_SUBSCR':
        t = TypeExpr(it[1])
        t_ind = TypeExpr(it[2])
        if t == Kl_List and IsInt(t_ind):
            ref1 = Expr1(it[1],o)
                
            o2,ind1 = shortage(generate_ssize_t_expr(it[2]))
            o.extend(o2)
            ind2 = New('long')
            o.Raw(ind2, ' = PyList_GET_SIZE(', ref1, ');')
            if type(ind1) is int:
                if ind1 < 0:
                    _ind1 = New('long')
                    o.Stmt(_ind1, '=', ind1, '+', ind2)
                    ind1 = _ind1
            elif ind1[0] == 'CONST':
                if ind1[1] < 0:
                    _ind1 = New('long')
                    o.Stmt(_ind1, '=', ind1[1], '+', ind2)
                    ind1 = _ind1
            else:   
                if not istemptyped(ind1):
                    ind_ = New('long')
                    o.Raw(ind_, ' = ', ind1, ';')
                    ind1 = ind_
                o.Stmt('if (', ind1, '< 0) {')
                o.Stmt(ind1, '=', ind1, '+', ind2)
                o.Raw('}')                        
            o.Stmt(ind2, '=', ind1, '+', 1)
            o.Stmt('PyList_SetSlice', ref1, ind1, ind2, 'NULL')
            o.Cls(ref1, ind1, ind2)
            return    
            
        if t is not None and t != Kl_Dict:
            Debug('Typed ' + head, t, it)
        ref1, ref2 = Expr(o, it[1:])
        if t == Kl_Dict:
            o.Stmt('PyDict_DelItem', ref1, ref2)
        else:    
            o.Stmt('PyObject_DelItem', ref1, ref2)
        o.Cls(ref1, ref2)
        return
    if head == 'DELETE_SLICE+0':
        t = TypeExpr(it[1])
        if t == Kl_List:
            assign_list_slice(it, o, 'NULL')
            return    
        if t is not None:
            Debug('Typed ' + head, t, it)
        ref1 = Expr1(it[1], o)
        o.Stmt('_PyEval_AssignSlice', ref1, 'NULL', 'NULL', 'NULL')
        o.Cls(ref1)
        return    
    if head == 'DELETE_SLICE+1':
        t = TypeExpr(it[1])
        if t == Kl_List:
            assign_list_slice(it, o, 'NULL')
            return    
            
        if t is not None:
            Debug('Typed ' + head, t, it)
        ref1, ref2 = Expr(o, it[1:])
        o.Stmt('_PyEval_AssignSlice', ref1, ref2, 'NULL', 'NULL')
        o.Cls(ref1, ref2)
        return    
    if head == 'DELETE_SLICE+2':
        t = TypeExpr(it[1])
        if t is not None:
            Debug('Typed ' + head, t, it)
        ref1, ref2 = Expr(o, it[1:])
        o.Stmt('_PyEval_AssignSlice', ref1, 'NULL', ref2, 'NULL')
        o.Cls(ref1, ref2)
        return    
    if head == 'DELETE_SLICE+3':
        t = TypeExpr(it[1])
        if t is not None:
            Debug('Typed ' + head, t, it)
        ref1, ref2, ref3 = Expr(o, it[1:])
        o.Stmt('_PyEval_AssignSlice', ref1, ref2, ref3, 'NULL')
        o.Cls(ref1, ref2, ref3)
        return    
    if head == 'DELETE_GLOBAL':
        ref1 =  Expr1(('CONST', it[1]),o)
        o.Stmt('PyDict_DelItem', ('glob',), ref1)
        o.Cls(ref1)
        return
    if head == 'CONTINUE':
        if try_jump_context[-1]:
            if type(try_jump_context[-1]) is list:
                o.Comment((')(FINALLY',))
                o.Stmt('{')
                generate_list(try_jump_context[-1],o)
                o.Raw('}')                    
##            o.Stmt('PyFrame_BlockPop', 'f')
        o.Stmt('continue;')
        return
    if head == 'BREAK_LOOP':
        if try_jump_context[-1]:
            if type(try_jump_context[-1]) is list:
                o.Comment((')(FINALLY',))
                o.Stmt('{')
                generate_list(try_jump_context[-1],o)
                o.Raw('}')                    
##            o.Stmt('PyFrame_BlockPop', 'f')
        o.Stmt('break;')
        return
    if head == 'EXEC_STMT_3':
        r1, r2, r3 = Expr(o, it[1:])
        plain = False
        
        if r2 == ('CONST', None) == r3:
            if it[1][0] == '!BUILD_TUPLE' and len(it[1][1]) in (2,3):
                pass
            else:
                r2 = 'glob'
                o.Raw('PyFrame_FastToLocals(f);')
                r3 = 'f->f_locals'
                plain = True
        if r2 != ('CONST', None) and ('CONST', None) == r3:
            r3 = r2
        ## o.INCREF(r1)    
        ## o.INCREF(r2)    
        ## o.INCREF(r3)    
        o.Stmt('_PyEval_ExecStatement', 'f', r1,r2,r3)
        if plain:
            o.Raw('PyFrame_LocalsToFast(f, 0);')
        ## o.DECREF(r1)    
        ## o.DECREF(r2)    
        ## o.DECREF(r3)    
        o.Cls(r1, r2, r3)
        return
    if head == 'DELETE_NAME':
        ref1 = Expr1(('CONST', it[1]),o)
        o.Stmt('PyObject_DelItem', 'f->f_locals', ref1)
        o.Cls(ref1)
        return
    if head == 'RAISE_VARARGS_STMT' or head == 'RAISE_VARARGS':
        assert it[1] == 0
        if len(it) < 3:
            refn = []
        else:    
            refn = Expr(o, it[2])
        while len(refn) < 3:
            refn.append('NULL')
        assert len(refn) == 3    
        o.Stmt('_PyEval_DoRaise', refn[0], refn[1], refn[2])
#        if not istempref(refn[0]):
        if refn[0] != 'NULL':
             o.INCREF(refn[0])
        if refn[1] != 'NULL':
            o.INCREF(refn[1])
        if refn[2] != 'NULL':
            o.INCREF(refn[2])
        o.Cls(*refn)
        o.Stmt('goto', labl)
        UseLabl()
        return
    if head == 'IMPORT_STAR':
        o.Stmt('PyFrame_FastToLocals', 'f')
        ref1 = Expr1(it[1],o)
        o.Stmt('_PyEval_ImportAllFrom', 'f->f_locals', ref1);
        o.Stmt('PyFrame_LocalsToFast', 'f', 0)
        o.Cls(ref1)
        return
    if head == 'DELETE_FAST':
        o.Stmt('SETLOCAL', it[1], 'NULL')
        return
    if head == 'PASS':
        pass
        return
    Fatal('HEAD', head, it)
    
def like_append(it):
    v = []
    return TCmp(it,v,('!PyObject_Call', ('!PyObject_GetAttr', '?', ('CONST', 'append')),\
                    ('!BUILD_TUPLE', ('?',)), ('NULL',)))
                    
def like_append_const(it, v):
    return TCmp(it,v,('!PyObject_Call', ('!PyObject_GetAttr', '?', ('CONST', 'append')),\
                    ('CONST', ('?',)), ('NULL',)))          
                        
    ## try:
        ## return it[0] == '!PyObject_Call' and it[1][0] == '!PyObject_GetAttr' and\
            ## it[1][2][0] == 'CONST' and it[1][2][1] == 'append' and \
            ## it[2][0] == '!BUILD_TUPLE' and len(it[2][1]) == 1 and \
            ## len(it[2]) == 2 and it[3][0] == 'NULL'
    ## except:
        ## pass
    ## return False

def generate_may_be_append(it, o):
    ref_list = Expr1(it[1][1], o)
    ref_value = Expr1(it[2][1][0], o)
    t = TypeExpr(it[1][1])
    islist = False
    if t is None:
        pass
    elif t == Kl_List:
        islist = True
    elif t.descr == T_NEW_CL_INST and Is3(t.subdescr, 'Derived', ('!LOAD_BUILTIN', 'list')):
        islist = True
##    print 'lllappend', t, islist
    _generate_may_be_append(ref_list, ref_value, o, islist)
    o.Cls(ref_value, ref_list)

def generate_may_be_append_const(it, o, v):
    ref_list = Expr1(v[0], o)
##    ref_value = Expr1(it[2][1][0], o)
    t = TypeExpr(v[0])
    islist = False
    if t is None:
        pass
    elif t == Kl_List:
        islist = True
    elif t.descr == T_NEW_CL_INST and Is3(t.subdescr, 'Derived', ('!LOAD_BUILTIN', 'list')):
        islist = True
    _generate_may_be_append_const(ref_list, v[1], o, islist)
    o.Cls(ref_list)

def _generate_may_be_append_const(ref_list, v1, o, islist = False):
    if not islist:
        o.Stmt('if (PyList_CheckExact(', ref_list, ')) {')
    o.Stmt('PyList_Append', ref_list, ('CONST', v1))
    if not islist:
        o.Raw('} else {')
        ref_attr = New()
        o.Stmt(ref_attr, '=', 'PyObject_GetAttr', ref_list, ('CONST', 'append'))    
        ref_return = New()
        o.Stmt(ref_return, '=', 'FirstCFunctionCall', ref_attr, ('CONST', (v1,)), ('NULL',))
        o.Cls(ref_return, ref_attr)
        o.Raw('}')


def _generate_may_be_append(ref_list, ref_value, o, islist = False):
    if not islist:
        o.Stmt('if (PyList_CheckExact(', ref_list, ')) {')
    o.Stmt('PyList_Append', ref_list, ref_value)
    if not islist:
        o.Raw('} else {')
        ref_attr = New()
        o.Stmt(ref_attr, '=', 'PyObject_GetAttr', ref_list, ('CONST', 'append'))    
        ref_tuple = New()
        o.Stmt(ref_tuple, '=', 'PyTuple_New', 1)
        o.INCREF(ref_value)
        o.Stmt('PyTuple_SET_ITEM', ref_tuple, 0, ref_value)
        ref_return = New()
        o.Stmt(ref_return, '=', 'FirstCFunctionCall', ref_attr, ref_tuple, ('NULL',))
        o.Cls(ref_return, ref_tuple, ref_attr)
        o.Raw('}')
 
def _detect_r_subexpr(e, acc2):
    if not (type(e) is tuple) or len(e) == 0 or \
       e[0] in ('CONST', 'FAST', 'CALC_CONST', 'TYPED_TEMP', '!@PyInt_FromSsize_t'):
        return
    if e in acc2:
        acc2[e] = acc2[e] + 1
    else:    
        acc2[e] = 1    
    if type(e) is tuple and len(e) > 0:
        if e[0] == '!BUILD_MAP':
            e = e[1]    
            for i,it in enumerate(e):
                if i == 0 or not (type(it[0]) is tuple) or len(it[0]) == 0 or \
                it[0][0] in ('CONST', 'FAST', 'CALC_CONST', 'TYPED_TEMP', '!@PyInt_FromSsize_t'):
                    pass
                else:
                    _detect_r_subexpr(it[0], acc2)     
                if i == 0 or not (type(it[1]) is tuple) or len(it[1]) == 0 or \
                it[1][0] in ('CONST', 'FAST', 'CALC_CONST', 'TYPED_TEMP', '!@PyInt_FromSsize_t'):
                    pass
                else:
                    _detect_r_subexpr(it[1], acc2)     
            return        
        if e[0] in ('!BUILD_LIST', '!BUILD_TUPLE'):
            e = e[1]    
        for i,it in enumerate(e):
                if i == 0 or not (type(it) is tuple) or len(it) == 0 or \
                    it[0] in ('CONST', 'FAST', 'CALC_CONST', 'TYPED_TEMP', '!@PyInt_FromSsize_t'):
                    continue
                _detect_r_subexpr(it, acc2)     
    return
    
def cond_in_expr(e):    
    return 'AND' in repr(e) or 'OR' in repr(e) or 'COND' in repr(e)
    
def detect_repeated_subexpr(store, expr):
    acc2 = {}
    if cond_in_expr(expr):
        return {}
    _detect_r_subexpr(expr,acc2)    
    if len(store) > 0 and store[0] in ('PyObject_SetItem', 'PyObject_SetAttr'):
        if cond_in_expr(store[1]) or cond_in_expr(store[2]):
            return {}
        _detect_r_subexpr(store[1],acc2)
        _detect_r_subexpr(store[2],acc2)
    d = {}
    for k,v in acc2.iteritems():
        if v > 1:
            d[k] = v
    todel = {}
    for k,v in d.iteritems():        
        if k[0] in ('!BUILD_LIST', '!BUILD_TUPLE', '!BUILD_MAP', 'CONST', \
                    '!CLASS_CALC_CONST', '!CLASS_CALC_CONST_NEW', \
                    '!PyObject_Call', '!FirstCFunctionCall', '!FastCall'):
            todel[k] = True
        else:
            try:
                t = TypeExpr(k)
            except:
                t = None
            if not t in (Kl_Float, Kl_Int):
                todel[k] = True
                    
    for k in todel.keys():
        del d[k]
    todel = {}  
    for k,v in d.iteritems():        
        for k1,v1 in d.iteritems():        
            if k != k1 and repr(k1) in repr(k) and v1 == v:
               todel[k1] = True
    for k in todel.keys():
        del d[k]  
    return d    

def find_common_subexpr_for_float(it,acc):
    d = detect_repeated_subexpr(it[1][0], it[2][0])
    subfloat = {}
    upfloat = {}
    todel = {}
    for k in d.iterkeys():
        for x in acc:
            if k == x:
                todel[k] = True
    for k in todel.keys():
        del d[k]            
    for k in d.iterkeys():
        for x in acc:
            if repr(k) in repr(x):
                subfloat[k] = subfloat.get(k,0) + 1
            if repr(x) in repr(k):
                upfloat[k] = upfloat.get(k,0) + 1
# k1 and k2 is uniq => todel is uniq
#--
# I don't know... And I don't                 
    for k in [k1 for k1 in upfloat.iterkeys() \
                              for k2 in subfloat.iterkeys() if k1 == k2]:
        del subfloat[k]            
        del upfloat[k]  
    return subfloat.keys()
    
def generate_mixed_float_expr(it,acc,o,isfloat):
    assert (it[1] is None or len(it[1]) == 1) and len(it[2]) == 1
    acc_subfloat = find_common_subexpr_for_float(it,acc)
    refs_subfloat = Expr(o, acc_subfloat) #[Expr1(x, o) for x in acc_subfloat]
    PushAcc(acc_subfloat, refs_subfloat)
    refs = Expr(o, acc) #[Expr1(x, o) for x in acc]
    PopAcc(o)
    seq = 'if ('
    for i,x in enumerate(refs):
        if x[0] != 'CONST':
            seq = seq + 'PyFloat_CheckExact(' + CVar(x) + ')'
            seq = seq + ' && '
    if seq == 'if (':
       seq = 'if (1) {'
    else:    
        seq = seq[:-4] + ') {'
    o.append(seq)
    floats = []
    for x in refs:
        if x[0] == 'CONST':
            if math.isnan(x[1]):
                if not '-' in str(x[1]):
                    floats.append('Py_NAN')
                else:    
                    floats.append('(-(Py_NAN))')
            elif math.isinf(x[1]):
                if not '-' in str(x[1]):
                    floats.append('Py_HUGE_VAL')
                else:
                    floats.append('-Py_HUGE_VAL')    
            else:    
                floats.append(x)
        else:
            floats.append(New('double'))
    text_floats = []        
    for x in floats:
        if x[0] == 'CONST':
            text_floats.append(str(x[1]))
        else:
            text_floats.append(CVar(x))
    for i, x in enumerate(floats):
        if istemptyped(x):
            o.Stmt(x, '=', 'PyFloat_AS_DOUBLE', refs[i])        
    float_seq = generate_float_expr(it[2][0], acc, text_floats)    
    ref = New()
    o.Stmt(ref, '=', 'PyFloat_FromDouble', float_seq)
    o.Cls(*floats)
    o.Raw('} else {')
##    o.Raw('/* ((( ' + repr((acc_subfloat+acc, refs_subfloat+refs)) + '*/' )
    PushAcc(acc_subfloat+acc, refs_subfloat+refs)
##    o.Raw('/* +++ */')
    ref = GenExpr(it[2][0], o, ref,None,True)
##    o.Raw('/* --- */')
    PopAcc(o, False)
##    o.Raw('/* ))) */')
    o.Raw('}')
    o.Cls(*refs)
    PushAcc(acc_subfloat, refs_subfloat)
    if it[1] is not None:
        generate_store(it[1][0], ref, o, acc)
    PopAcc(o, False)
    o.Cls(*refs_subfloat)    
    if it[1] is not None:
        o.Cls(ref)
    else:
        return ref    
    return
    
def generate_compaund_statement(head,it,o):
    if head == 'IF':
        generate_if(it,o)
        return
    if head == 'PREEXPR':
        generate_preexpr(it,o)
        return
    if head == 'WHILE':
        generate_while(it,o)
        return
    if head == 'FOR':
        generate_for_new(it,o)
        return
    if head == 'TRY': 
        if attempt_iteration_try(it, o):
            return
        ## if 'StopIteration' in repr(it):
            ## print 'May be "StopIteratin" handled incorrectly'
        generate_try(it,o)
        return
    if head == 'TRY_FINALLY': 
        generate_try_finally(it,o)
        return
    if head == 'WITH':
        generate_with(it,o)
        return
    Fatal('', it)

def generate_with(it,o):
    global try_jump_context, dropped_temp
    global traced_tempgen
    
##    raised = None
    try_j = try_jump_context[:]
    assert len(it) == 3 and it[2] == (')ENDWITH',) and len(it[0]) == 3 and it[0][0] == '(WITH'
    r0 = Expr1(it[0][1], o)
    o.INCREF(r0)
    r1 = New()
    r2 = New()
    ref1 = New()
    if tuple(sys.version_info)[:2] < (2,7):
        o.Raw('if ((', r1, ' = PyObject_GetAttr(', r0, ', ', ('CONST', '__enter__'), ')) == 0) goto ', labl, ';')
        o.Raw('if ((', r2, ' = PyObject_GetAttr(', r0, ', ', ('CONST', '__exit__'), ')) == 0) goto ', labl, ';')
    else:    
        o.Raw('if ((', r1, ' = from_ceval_2_7_special_lookup(', r0, ', "__enter__", &from_ceval_2_7_enter)) == 0) goto ', labl, ';')
        o.Raw('if ((', r2, ' = from_ceval_2_7_special_lookup(', r0, ', "__exit__", &from_ceval_2_7_exit)) == 0) goto ', labl, ';')
        Used('from_ceval_2_7_special_lookup')
    o.Raw('if ((', ref1, ' = PyObject_Call(', r1, ', ', ('CONST', ()), ', NULL)) == 0) goto ', labl, ';')
    o.Cls(r1)

    if it[0][2] == (): 
        pass
    elif len(it[0][2]) == 1 and it[0][2][0][0] in set_any:
        generate_store(it[0][2][0], ref1, o, 'Store clause at WITH statement')
    elif it[0][2][0] == 'SET_VARS':
        generate_store(it[0][2], ref1, o, 'Multy store clause at WITH statement')
    elif len(it[0][2]) == 2 and it[0][2][0] in set_any:
        generate_store(it[0][2], ref1, o, 'Store clause at WITH statement')
    elif len(it[0][2]) == 3 and it[0][2][0] in ('PyObject_SetAttr', 'PyObject_SetItem'):
        generate_store(it[0][2], ref1, o, 'Store clause at WITH statement')
    else:
        Fatal('WITH error', len(it[0][2]), it[0][2], it)
        raise     
    o.Cls(ref1) 
        
    ## if it[1] == [('PASS',)]:     
        ## ref2 = New()
        ## o.Raw('if ((', ref2, ' = PyObject_Call(', r2, ', ', ('CONST', (None,None,None)), ', NULL)) == 0) goto ', labl, ';')
        ## UseLabl()
        ## o.Cls(r2, ref2, r0)
        ## try_jump_context[:] = try_j
        ## return
    try_jump_context.append(True)
    o.Stmt('{')
    label_exc = New('label')  
    global traced_tempgen
    a,b,c = New(), New(), New()
    o.Stmt('PyErr_Fetch', ('&', a), ('&', b), ('&', c)) 
    set_toerr_new(o, label_exc)
    o.XINCREF(a)
    o.XINCREF(b)
    o.XINCREF(c)
    o.Stmt('PyFrame_BlockSetup', 'f', 'SETUP_EXCEPT',-1, -1)
    dropped_temp.append(('WITH', (ref1, r2, a,b,c)))
    traced_tempgen.append({})
    generate_list(it[1],o)
    traced_temp = traced_tempgen[-1].keys()
    del traced_tempgen[-1]
    if len(traced_tempgen) > 0:
        for k in traced_temp:
            traced_tempgen[-1][k] = True
    o.Stmt('PyFrame_BlockPop', 'f')
    set_toerr_back(o)
    o.Stmt('PyErr_Restore', a,b,c)   
    ref2 = New()
    o.Raw('if ((', ref2, ' = PyObject_Call(', r2, ', ', ('CONST', (None,None,None)), ', NULL)) == 0) goto ', labl, ';')
    bool_ret = None
##    o.Cls(ref2, r2)
    UseLabl()
    raised = None
##        ref2 = Expr1(('!PyObject_Call', r2, ('CONST', (None,None,None)), 'NULL'),o)
    if Is3(func, 'UseLabel', label_exc):   
        raised = New('int')
        o.Raw(raised, ' = 0;')
        o.Stmt('if (0) { ', label_exc, ':')
        o.Stmt(raised, '=', 1)
        o.Raw('PyTraceBack_Here(f);') 
        generate_clear_temp_on_exception(o, traced_temp)
        ae,be,ce = get_exc_info(o)
        o.XINCREF(ae)
        o.XINCREF(be)
        o.XINCREF(ce)
        tupl = New()
        o.Raw(tupl, ' = PyTuple_Pack(3, ', ae, ', ', be, ', ', ce, ');')
        ref2 = New()
        o.Raw('if ((', ref2, ' = PyObject_Call(', r2, ', ', tupl, ', NULL)) == 0) goto ', labl, ';')
        o.Cls(tupl, r2)
        bool_ret = New('int')
        o.Raw('if (', ref2, ' == Py_None) ', bool_ret, ' = 0;')
        o.Raw('else {')
        o.Raw('if ((', bool_ret, ' = PyObject_IsTrue(', ref2, ')) == -1) goto ', labl, ';')
        o.Raw('}')
        o.Cls(ref2)
        UseLabl()

        o.Stmt('PyFrame_BlockPop', 'f')
        o.Raw('if (', bool_ret, ') {')
        o.Stmt('PyErr_Restore', a,b,c)
        o.Stmt('_PyEval_reset_exc_info', 'f->f_tstate')       
        o.Raw('} else {')
        o.Stmt('PyErr_Restore', ae,be,ce)   
        o.Raw('}')
        o.Cls(ae, be, ce)
##            o.Stmt('PyErr_Restore', a,b,c)
        o.Raw('}')
    o.Raw('}')
    o.DECREF(r0)
    o.Cls(ref2, a, b, c, r0, r2, r1)
#        o.Cls(*refs) 
    if raised is not None:
        o.Raw('if (', raised, ' && !', bool_ret,') { goto ',labl, '; }')
    UseLabl()
    o.Cls(raised, bool_ret)
    set_toerr_final(o)
    del dropped_temp[-1]
    try_jump_context[:] = try_j
    return


def generate_try_finally_new(it,o2):
    global try_jump_context, dropped_temp
    o = Out()
    i = 2
    while i < len(it):
        if it[i][0] == ')ENDTRY_FINALLY':
            del it[i]    
        elif it[i][0] == ')(FINALLY':
            finally_cod = it[i+1]
            del it[i]
            del it[i]
            continue
        else:
            Fatal('', it, i, it[i])
    try_jump_context.append(finally_cod)
    label_exc = New('label') 

    global traced_tempgen
    a = New()
    b = New()
    c = New()
    o.Stmt('PyErr_Fetch', ('&', a), ('&', b), ('&', c))
    dropped_temp.append(('TRY', (a,b,c)))

    set_toerr_new(o, label_exc)
    o.Stmt('PyFrame_BlockSetup', 'f', 'SETUP_FINALLY',-1, -1)

    traced_tempgen.append({})
    generate_list(it[1],o)
    traced_temp = traced_tempgen[-1].keys()
    del traced_tempgen[-1]
    if len(traced_tempgen) > 0:
        for k in traced_temp:
            traced_tempgen[-1][k] = True
    o.Stmt('PyFrame_BlockPop', 'f')
    set_toerr_back(o)
    o.Stmt('PyErr_Restore', a,b,c)   

    a1,b1,c1 = None,None,None
    i = 2
    first_except = True
    if not Is3(func, 'UseLabel', label_exc):        
        del try_jump_context[-1]     
        generate_list(finally_cod,o)
        o.Cls(a, b, c)
        set_toerr_final(o)
        o2.extend(o)
        del dropped_temp[-1]
        return None
    global tempgen
    raised = New('int')
    o.Raw(raised, ' = 0;')
    o.Stmt('if (0) { ', label_exc, ':')
    o.Raw('PyTraceBack_Here(f);')
    o.Stmt(raised, '=', 1)
    generate_clear_temp_on_exception(o, traced_temp)
    o.Raw('}')
    if i < len(it):
        Fatal('', it, i, it[i])
    del try_jump_context[-1]        
    o.Comment((')(FINALLY',))
    generate_list(finally_cod,o)
    global tempgen
    o.Cls(a, b, c, a1, b1, c1, raised)
    o.Raw('if (', raised, ') { goto ',labl, '; }')
    UseLabl()
    del dropped_temp[-1]
    set_toerr_final(o)
    o2.extend(o)


def attempt_iteration_try(it, o):
    if len(it) != 5:
        return False
    body = it[1]
    exc = it[2]
    handle = it[3]
    while len(body) > 0 and body[0][0] == '.L':
        body = body[1:]
    if len(body) == 0:
        return False    
    stmt = body[0]    
    no_append = False
    iter = None
    if stmt[0] == 'STORE':
        if len(stmt[1]) != 1 or len(stmt[2]) != 1:
            return False
        action = stmt[2][0]
        iter = is_attr_next_call(action)
        if iter == False:
            return False
        no_append = True
    elif 'next' in repr(stmt):
        if stmt[0] != 'UNPUSH':
            return False
        if not like_append(stmt[1]):
            return False
        expr_list = stmt[1][1][1]
        expr_value = stmt[1][2][1][0]
        iter = is_attr_next_call(expr_value)
        if iter == False:
            return False
        no_append = False
    if exc[0] != ')(EXCEPT':
        return False
    if len(exc) >= 3 and exc[2] != ():
        return False
    if len(exc) < 2:
        return False
    excarg = exc[1]
    if len(excarg) == 2:
        if type(excarg[1]) is int:
            excarg = (excarg[0],)
    if len(excarg) == 1 and type(excarg) is tuple:
        excarg = excarg[0]
    if len(excarg) != 2:
        return False
    if excarg[1] != 'StopIteration':
        return False 
    if iter is None:
##        print 'Sto
        return False
    ref_iter = Expr1(iter,o)
    o.Stmt('if (PyIter_Check(', ref_iter, ')) {')
    val_iter = New()
    o.Stmt(val_iter, '=', 'PyIter_Next', ref_iter)
    o.Raw('if (PyErr_Occurred()) goto ', labl, ';')
    UseLabl()
    o.Stmt('if (', val_iter, '!= NULL ) {')
    o.Cls(ref_iter)    
    if no_append:
        generate_store(stmt[1][0], val_iter, o, stmt)
        o.ZeroTemp(val_iter)  
    else:
        ref_list = Expr1(stmt[1][1][1], o)
        _generate_may_be_append(ref_list, val_iter, o, TypeExpr(stmt[1][1][1]) == Kl_List)
        o.Cls(ref_list)
    o.Cls(val_iter)
    generate_list(body[1:], o)   
    o.Raw('} else {')
    generate_list(handle, o)   
    o.Raw('}')
    o.Raw('} else {')
    generate_try(it, o)   
    o.Raw('}')
    return True

def is_attr_next_call(action):
    if action[0] != '!PyObject_Call':
        return False
    if len(action[2]) != 2:
        return False
    if action[2][0] != 'CONST':
        return False
    if action[2][1] != ():
        return False
    if len(action[3]) != 1:
        return False
    if action[3][0] != 'NULL':
        return False
    if len(action[1]) != 3:
        return False
    if action[1][0] != '!PyObject_GetAttr':
        return False
    if len(action[1][2]) != 2:
        return False
    if action[1][2][0] != 'CONST':
        return False
    if action[1][2][1] != 'next':
        return False
    return action[1][1]         

def generate_try(it,o2):
    global try_jump_context, dropped_temp
    o = Out()

    else_cod = None
    i = 2
    while i < len(it):
        if it[i][0] == ')(EXCEPT':
            i += 2
            continue
        elif it[i][0] == ')(ELSE':
            else_cod = it[i+1]
            del it[i]
            del it[i]
            continue
        elif it[i][0] == ')ENDTRY':
            del it[i]    
        else:
            Fatal('', it, i, it[i])
    try_jump_context.append(True)
##    o.Stmt('{')
    to_else = New('int')
    o.Stmt(to_else, '=', 1)
    label_exc = New('label') 

    global traced_tempgen
    a = New()
    b = New()
    c = New()
    o.Stmt('PyErr_Fetch', ('&', a), ('&', b), ('&', c))
    dropped_temp.append(('TRY', (a,b,c)))
    ## o.XINCREF(a)
    ## o.XINCREF(b)
    ## o.XINCREF(c)
    set_toerr_new(o, label_exc)
    o.Stmt('PyFrame_BlockSetup', 'f', 'SETUP_EXCEPT',-1, -1)

    traced_tempgen.append({})
    generate_list(it[1],o)
    traced_temp = traced_tempgen[-1].keys()
    del traced_tempgen[-1]
    if len(traced_tempgen) > 0:
        for k in traced_temp:
            traced_tempgen[-1][k] = True
    o.Stmt('PyFrame_BlockPop', 'f')
    set_toerr_back(o)
    o.Stmt('PyErr_Restore', a,b,c)   

    a1,b1,c1 = None,None,None
    i = 2
    first_except = True
    if not Is3(func, 'UseLabel', label_exc):        
        del try_jump_context[-1]     
        if else_cod is not None:
            o.Comment((')(ELSE',))
            o.Stmt('if (', to_else, ') {')
            generate_list(else_cod,o)
            o.Raw('}')
        o.Cls(a, b, c)
##      if else_cod is not None:
        o.Cls(to_else)
        set_toerr_final(o)
        o2.extend(o)
        del dropped_temp[-1]
        return None
    global tempgen
    o.Stmt('if (0) { ', label_exc, ':')
    o.Raw('PyTraceBack_Here(f);')
##    to_else = New('int')
##    o.Stmt(to_else, '=', 1)
#    finally_cod = None
    handled = False
    generate_clear_temp_on_exception(o, traced_temp)
    while i < len(it):
        if it[i][0] == ')(EXCEPT' and len(it[i]) == 1:
            o.Comment(it[i])
##            if else_cod is not None:
            o.Raw('if (', to_else, ') {')
            ae,be,ce = get_exc_info(o)
            o.Cls(ae, be, ce)
            o.Stmt('PyFrame_BlockPop', 'f')
            o.Stmt('PyErr_Restore', a,b,c)
            o.Stmt(to_else, '=', 0)
            generate_list(it[i+1],o)
            o.Stmt('_PyEval_reset_exc_info', 'f->f_tstate')       
            o.Raw('}')
            handled = True
            i += 2
            continue
        if it[i][0] == ')(EXCEPT' and len(it[i]) > 1:
            if ((len (it[i][1]) == 2 and type(it[i][1][1]) is int) or len (it[i][1]) == 1) and \
               len(it[i][2]) == 0:
                    iti = it[i]
                    o.Comment(iti)
                    assert not is_direct_current
                    o.Raw('if (', to_else, ') {')
                    if len (iti[1]) == 2 and type(iti[1][1]) is int:
                        o.Stmt('f->f_lineno', '=', iti[1][1])
                        o.Raw('f->f_lasti = ', str(Line2Addr[iti[1][1]]), ';')
                    ref_ = Expr1(iti[1][0],o)
                    ref1 = New('int')
                    o.Stmt(ref1, '=', 'PyErr_ExceptionMatches', ref_)
                    o.Cls(ref_)
                    o.Stmt('if (', ref1, ') {')
                    ae,be,ce = get_exc_info(o)
                    o.Cls(ae, be, ce)

                    o.Stmt('PyFrame_BlockPop', 'f')
                    o.Stmt('PyErr_Restore', a,b,c)
                    o.Stmt(to_else, '=', 0)
                    generate_list(it[i+1],o)
                    o.Stmt('_PyEval_reset_exc_info', 'f->f_tstate')       
                    o.Raw('}')
                    o.Cls(ref1)
                    o.Raw('}')
                    i += 2
                    continue
            if ((len (it[i][1]) == 2 and type(it[i][1][1]) is int) or len (it[i][1]) == 1) and \
               len(it[i][2]) >= 1:
                    iti = it[i]
                    o.Comment(iti)
                    assert not is_direct_current
                    o.Raw('if (', to_else, ') {')
                    if len (iti[1]) == 2 and type(iti[1][1]) is int:
                        o.Stmt('f->f_lineno', '=', iti[1][1])
                        o.Raw('f->f_lasti = ', str(Line2Addr[iti[1][1]]), ';')
                    ref_ = Expr1(iti[1][0],o)
                    ref1 = New('int')
                    o.Stmt(ref1, '=', 'PyErr_ExceptionMatches', ref_)
                    o.Cls(ref_)
                    o.Stmt('if (', ref1, ') {')
                    ae,be,ce = get_exc_info(o)
                    if len(it[i][2]) == 1 and it[i][2][0][0] in set_any:
                        generate_store(it[i][2][0], be, o, 'Object Exception')
                    elif len(it[i][2]) >= 1 and it[i][2][0] == 'UNPACK_SEQ_AND_STORE':
                        generate_store(it[i][2], be, o, 'Object Exception')
                    else:
                        Fatal('TRY error', it[i])
                    o.Cls(ae, be, ce)

                    o.Stmt('PyFrame_BlockPop', 'f')
                    o.Stmt('PyErr_Restore', a,b,c)
##                    if else_cod is not None:
                    o.Stmt(to_else, '=', 0)
                    generate_list(it[i+1],o)
                    o.Stmt('_PyEval_reset_exc_info', 'f->f_tstate')       
                    o.Raw('}')
                    o.Cls(ref1)
                    o.Raw('}')
                    i += 2
                    continue
            Fatal('TRY error', it[i], it[i][0], it[i][1], it[i][1][0], it[i][2], it[i][2][0])
        else:
            Fatal('', it, i, it[i])
    del try_jump_context[-1]        
    if not handled:
        assert not is_direct_current
        o.Stmt('if (', to_else, ') {')
        o.Stmt('PyFrame_BlockPop', 'f')
##        o.Stmt('PyErr_Restore', a,b,c)
        o.Raw('}')
    if not handled and else_cod is None:
        assert not is_direct_current
        o.Stmt('if (', to_else, ') {')
        o.Stmt('goto', labl)
        UseLabl()
        o.Raw('}')
                
    o.Raw('}')
    if else_cod is not None:
        o.Comment((')(ELSE',))
        o.Stmt('if (', to_else, ') {')
        generate_list(else_cod,o)
        o.Raw('}')
        handled = True
##    o.Raw('}')
    global tempgen
    o.Cls(a, b, c)
    o.Cls(a1, b1, c1)
##    o.Stmt('_PyEval_reset_exc_info', 'f->f_tstate')       
    del dropped_temp[-1]
    if else_cod is not None:
        o.Cls(to_else)
    set_toerr_final(o)
    o2.extend(o)

def generate_try_finally(it,o2):
    global try_jump_context, dropped_temp
    o = Out()
    i = 2
    while i < len(it):
        if it[i][0] == ')ENDTRY_FINALLY':
            del it[i]    
        elif it[i][0] == ')(FINALLY':
            finally_cod = it[i+1]
            del it[i]
            del it[i]
            continue
        else:
            Fatal('', it, i, it[i])
    try_jump_context.append(finally_cod)
##    o.Stmt('{')
    label_exc = New('label') 

    global traced_tempgen
    a = New()
    b = New()
    c = New()
    o.Stmt('PyErr_Fetch', ('&', a), ('&', b), ('&', c))
    dropped_temp.append(('TRY', (a,b,c)))
    ## o.XINCREF(a)
    ## o.XINCREF(b)
    ## o.XINCREF(c)

    set_toerr_new(o, label_exc)
    o.Stmt('PyFrame_BlockSetup', 'f', 'SETUP_FINALLY',-1, -1)

    traced_tempgen.append({})
    generate_list(it[1],o)
    traced_temp = traced_tempgen[-1].keys()
    del traced_tempgen[-1]
    if len(traced_tempgen) > 0:
        for k in traced_temp:
            traced_tempgen[-1][k] = True
    o.Stmt('PyFrame_BlockPop', 'f')
    set_toerr_back(o)
    o.Stmt('PyErr_Restore', a,b,c)   

    a1,b1,c1 = None,None,None
    i = 2
    first_except = True
    if not Is3(func, 'UseLabel', label_exc):        
        del try_jump_context[-1]     
        generate_list(finally_cod,o)
        o.Cls(a, b, c)
        set_toerr_final(o)
        o2.extend(o)
        del dropped_temp[-1]
        return None
    global tempgen
    raised = New('int')
    o.Stmt(raised, '=', 0)
    o.Stmt('if (0) { ', label_exc, ':')
    o.Raw('PyTraceBack_Here(f);')
    o.Stmt(raised, '=', 1)
    generate_clear_temp_on_exception(o, traced_temp)
    o.Raw('}')
    if i < len(it):
        Fatal('', it, i, it[i])
    del try_jump_context[-1]        
#    assert not is_direct_current
#    o.Stmt('if (', to_else, ') {')
#    o.Stmt('PyFrame_BlockPop', 'f')
#    o.Stmt('PyErr_Restore', a,b,c)
#    o.Raw('}')
#    o.Raw('}')
    o.Comment((')(FINALLY',))
## if not handled:
    ## o.Stmt('if (', to_else, ') {')
    ## a1,b1,c1 = get_exc_info(o)
    ## o.INCREF(a1)
    ## o.INCREF(b1)
    ## o.INCREF(c1)
    ## o.INCREF(a)
    ## o.INCREF(b)
    ## o.INCREF(c)
    ## o.Stmt('PyErr_Restore', a,b,c)
    ## o.Raw('}')
    ## generate_list(finally_cod,o)
    ## o.Stmt('if (', to_else, ') {')
    ## o.Stmt('PyErr_Restore', a1,b1,c1)
    ## o.Stmt('goto', labl)
    ## UseLabl()
    ## o.Raw('}')
## else:        
#    o.Stmt('{')
    generate_list(finally_cod,o)
    global tempgen
    o.Cls(a, b, c)
    o.Cls(a1, b1, c1)
    o.Cls(raised)
    o.Raw('if (', raised, ') { goto ',labl, '; }')
    UseLabl()
    del dropped_temp[-1]
    set_toerr_final(o)
    o2.extend(o)
  
def generate_clear_temp_on_exception(o, traced_temp):
    for k, n in traced_temp:
        o.CLEAR('temp_' + str(n))
  
def get_exc_info(o):
    ae,be,ce = New(), New(), New()
    o.Stmt('PyErr_Fetch', ('&', ae), ('&', be), ('&', ce))
    ## o.XINCREF(ae)
    ## o.XINCREF(be)
    ## o.XINCREF(ce)
    o.Stmt('if (', be, '== NULL) {')
    o.Raw(be, '= Py_None;')
    o.INCREF(be)
    o.Raw('}')
    o.Stmt('PyErr_NormalizeException', ('&', ae), ('&', be), ('&', ce))
    if is_direct_current:
        o.Stmt('_PyEval_set_exc_info', 'f->f_tstate', ae, be, ce)       
    else:    
        o.Stmt('_PyEval_set_exc_info', 'tstate', ae, be, ce)       
    o.Stmt('if (', ce, '== NULL) {')
    o.Raw(ce, '= Py_None;')
    o.INCREF(ce)
    o.Raw('}')
    return ae, be, ce

def set_toerr_new(o, label_err):
    global labels, labl
    labels.append(label_err)
    labl = label_err

def set_toerr_back(o):
    global labels, labl
    del labels[-1]
    if len(labels) > 0:
        labl = labels[-1]
    else:
        labl = None  
        
def set_toerr_final(o):
    pass 

IsObject = ('!LOAD_NAME', '!LOAD_GLOBAL', 'FAST', '!PyObject_Call', '!CALL_CALC_CONST', '!CALL_CALC_CONST_INDIRECT',\
            '!PyDict_GetItem(glob,', '!BINARY_SUBSCR_Int',\
            '!PyObject_GetAttr', '!PyNumber_And', '!PyNumber_Or', \
            '!from_ceval_BINARY_SUBSCR', '!PySequence_GetSlice', '!LOAD_DEREF', 'CALC_CONST',\
            '!BUILD_MAP', '!BUILD_SET',  '!MK_FUNK', '!_PyEval_ApplySlice', \
            '!LIST_COMPR', '!BUILD_TUPLE', '!ORD_BUILTIN')

IsFloatOp = {'!PyNumber_Add':'+', \
            '!PyNumber_Divide':'/', '!PyNumber_Multiply':'*', '!PyNumber_Negative':'-', \
            '!PyNumber_Subtract':'-', '!PyNumber_Power':None}
           
def parse_for_float_expr(it, acc, isfloat):
    if it in acc:
        return True
    if type(it) is tuple :
        if it[0] == 'CONST' and type(it[1]) is float:
            acc.append(it)
            return True
        if it[0] == 'CONST' and type(it[1]) is int:
            acc.append(it)
            return True
        if it[0] == '!PyNumber_Power':
            if not parse_for_float_expr(it[1], acc, isfloat):
                return False
            if it[2][0] == 'CONST' and type(it[2][1]) is int and\
            it[3] == 'Py_None' and it[2][1] >= 2 and it[2][1] <= 5:
                return True
            return False
    
        if it[0] in IsFloatOp:
            ret = True
            for i in it[1:]:
                ret = ret and parse_for_float_expr(i, acc, isfloat)
            return ret    
        if it[0] == '!PyObject_Call' and it[1][0] == 'CALC_CONST':
            t = it[1][1]    
            if len(t) == 2:
                t = (Val3(t[0], 'ImportedM'), t[1])
                if t in CFuncFloatOfFloat:
                    return parse_for_float_expr(it[2][1][0], acc,isfloat)
        if it[0] in IsObject:
            acc.append(it)
            isfloat[it] = True
            return True
    return False    
    
def generate_float_expr(it, acc, refs):
    if it[0] in IsFloatOp:
        op = IsFloatOp[it[0]]
        if op is None:
            if it[2] == ('CONST', 2):
                iit = generate_float_expr(it[1], acc, refs)
                return '(' + iit + ') * (' + iit + ')'
            elif it[2] == ('CONST', 3):
                iit = generate_float_expr(it[1], acc, refs)
                return '(' + iit + ') * (' + iit + ') * (' + iit + ')'
            elif it[2] == ('CONST', 4):
                iit = generate_float_expr(it[1], acc, refs)
                return '(' + iit + ') * (' + iit + ') * (' + iit + ') * (' + iit + ')'
            elif it[2] == ('CONST', 5):
                iit = generate_float_expr(it[1], acc, refs)
                return '(' + iit + ') * (' + iit + ') * (' + iit + ') * (' + iit + ') * (' + iit + ')'
            Fatal('generate float EXPR', it)
        if len(it) == 3:     
            iit = generate_float_expr(it[1], acc, refs)
            return '(' + generate_float_expr(it[1], acc, refs) + ') ' + op + ' (' + generate_float_expr(it[2], acc, refs) + ')'
        if len(it) == 2:     
            iit = generate_float_expr(it[1], acc, refs)
            return op + '(' + generate_float_expr(it[1], acc, refs) + ')'
        Fatal('generate float EXPR', it)
    if it[0] == '!PyObject_Call' and it[1][0] == 'CALC_CONST':
        t = it[1][1]    
        if len(t) == 2:
            t = (Val3(t[0], 'ImportedM'), t[1])
            if t in CFuncFloatOfFloat:
                return CFuncFloatOfFloat[t] + '(' + generate_float_expr(it[2][1][0], acc, refs) +')'
    if it in acc:
        i = acc.index(it)
        return refs[i]
    Fatal('generate float EXPR', it)
    
def generate_ssize_t_expr(it):
    if type(it) is int:
        return Out(), it
    if it[0] == 'PY_TYPE' and IsInt(TypeExpr(it)):
        return generate_ssize_t_expr(it[3])
    if it[0] == '!PY_SSIZE_T':
        return generate_ssize_t_expr(it[1])
    if it[0] == 'CONST' and type(it[1]) is int:
        return Out(), it[1]
    if it[0] in len_family:
        if it[0] != '!PyObject_Size':
            nm = it[0][1:]
        else:    
            nm = 'PyObject_Size'
            t = TypeExpr(it[1])
            if t is not None:
#                Debug('', t, it[1])
#                assert t != types.NoneType
                if t == Kl_List:
                    nm  = 'PyList_GET_SIZE'
                elif t == Kl_Tuple:
                    nm  = 'PyTuple_GET_SIZE'
                elif t == Kl_String:
                    nm = 'PyString_GET_SIZE'
                elif t == Kl_Dict:
                    nm = 'PyDict_Size'
                elif t == Kl_Set:
                    nm = 'PySet_Size'
                elif t == Kl_Unicode:
                    nm = 'PyUnicode_GetSize'
                elif t == Kl_Buffer:
                    nm = 'PyObject_Size'
                elif t == Kl_XRange:
                    nm = 'PyObject_Size'
                elif t in (Kl_Generator, Kl_Int, Kl_Short):
                    nm = 'PyObject_Size'
                elif t == Kl_None:
                    Debug("len(None) construction detected", it)
                    nm = 'PyObject_Size'
                elif t.descr in (T_OLD_CL_INST, T_NEW_CL_INST):
                    nm = 'PyObject_Size'
                elif t is not None:
                    nm = 'PyObject_Size'
                    Debug('len of new known type', t, it[1], func)
        size_t = New('Py_ssize_t')
        o = Out()
        ref1 = Expr1(it[1], o)
        if nm.endswith('_GET_SIZE'):
            o.Raw(size_t, ' = ', nm, '(', ref1, ');')
        else:    
            o.Stmt(size_t, '=', nm, ref1)
        o.Cls(ref1)
        return o, size_t
    plusminus = {'!PyNumber_Add':0, '!PyNumber_Subtract':1}
    if it[0] in plusminus:
        t1 = TypeExpr(it[1])
        t2 = TypeExpr(it[2])
        if IsInt(t1) and IsInt(t2):
            o1, v1 = shortage(generate_ssize_t_expr(it[1]))
            o2, v2 = shortage(generate_ssize_t_expr(it[2]))
            size_t = New('Py_ssize_t')
            o = Out()
            o.extend(o1)
            o.extend(o2)
            op = (' + ', ' - ')[plusminus[it[0]]]
            o.Raw(size_t, ' = ', v1, op, v2, ';')
            o.Cls(v1, v2)
            return o, size_t
    if it[0] == '!PyNumber_Negative':
        t1 = TypeExpr(it[1])
        if IsInt(t1):
            o1, v1 = shortage(generate_ssize_t_expr(it[1]))
            size_t = New('Py_ssize_t')
            o = Out()
            o.extend(o1)
            o.Raw(size_t, ' = 0 - ', v1, ';')
            o.Cls(v1)
            return o, size_t
    if it[0] == '!@PyInt_FromSsize_t':
##        print '/2', it
        return Out(), ConC(it[1]) # for prevent Cls of temp 'for' count 
    else:
        o = Out()
        ref2 = Expr1(it, o)
        ind = New('Py_ssize_t')
        o.Stmt(ind, '=', 'PyInt_AsSsize_t', ref2)
        return o, ind
            
    Fatal('', it)

type_to_check = {'tuple' : 'PyTuple_CheckExact', 'list' : 'PyList_CheckExact',
                 'dict' : 'PyDict_CheckExact', 'int' : 'PyInt_CheckExact',
                 'str' : 'PyString_CheckExact', 'long' : 'PyLong_CheckExact',
                 'float' : 'PyFloat_CheckExact', 'complex' : 'PyComplex_CheckExact',
                 'unicode' : 'PyUnicode_CheckExact', 'bool' : 'PyBool_Check'}  

op_to_oper = {'PyCmp_EQ':' == ', 'PyCmp_NE':' != ', 'PyCmp_LT':' < ', \
              'PyCmp_LE':' <= ', 'PyCmp_GT':' > ', 'PyCmp_GE':' >= '}
              
def generate_rich_compare(it,logic,o):
    v = []
    it1 = it[1]
    it2 = it[2]
    t1 = TypeExpr(it1)
    t2 = TypeExpr(it2)
    op = it[3]
    if t1 == Kl_Type and t2 == Kl_Type and op in ('PyCmp_EQ', 'PyCmp_NE'):
        oper = op_to_oper[op]
        built = None
        valu = None 
        if it1[0] == '!LOAD_BUILTIN' and it2[0] == '!PyObject_Type': 
            built = it1[1]
            valu = it2[1]
        elif it2[0] == '!LOAD_BUILTIN' and it2[0] == '!PyObject_Type': 
            built = it2[1]
            valu = it1[1]
        if built in type_to_check:
            ref1 = Expr1(valu, o)
            ret = ConC(type_to_check[built], '(', ref1, ');')
            if op == 'PyCmp_NE':
                ret = '!' + ret
            o.Raw(logic, ' = ', ret)
            o.Cls(ref1)
            return o, logic
        if it1[0] == '!PyObject_Type':
            ref1 = Expr1(it1[1], o)
            op1 = ConC('((PyObject *)(((PyObject*)(',Expr1(it1[1], o),'))->ob_type))')
        else:
            op1 = ref1 = Expr1(it1, o)    
        if it2[0] == '!PyObject_Type':
            ref2 = Expr1(it2[1], o)
            op2 = ConC('((PyObject *)(((PyObject*)(',Expr1(it2[1], o),'))->ob_type))')
        else:
            op2 = ref2 = Expr1(it2, o)    
        o.Raw(logic, ' = ', op1, oper, op2, ';')
        o.Cls(ref1, ref2)
        return o, logic
 
    if IsInt(t1) and IsInt(t2):
        if op in op_to_oper:
            if t1 == Kl_Short:
                o1,int1 = shortage(generate_ssize_t_expr(it[1]))
                o.extend(o1)
            else:
                ref1 = Expr1(it[1],o)   
                if not istempref(ref1):
                    int1 = ConC('PyInt_AS_LONG(',ref1,')') 
                else:
                    int1 = New('long')
                    o.Raw(int1, ' = PyInt_AS_LONG(',ref1,');') 
                o.Cls(ref1)
            if t2 == Kl_Short:
                o2,int2 = shortage(generate_ssize_t_expr(it[2]))
                o.extend(o2)
            else:
                ref2 = Expr1(it[2],o)   
                if not istempref(ref2):
                    int2 = ConC('PyInt_AS_LONG(',ref2,')') 
                else:
                    int2 = New('long')
                    o.Raw(int2, ' = PyInt_AS_LONG(',ref2,');') 
                o.Cls(ref2)
            o.Raw(logic, ' = ', int1, op_to_oper[op], int2, ';')
            o.Cls(int1, int2)
            return o, logic

    if t1 == Kl_Tuple and t2 == Kl_Tuple:
        ref1, ref2 = Expr(o, it[1:3])
        if op in ('PyCmp_EQ', 'PyCmp_NE'):
            o.Raw('if (PyTuple_GET_SIZE(', ref1,') != PyTuple_GET_SIZE(', ref2, ')) {')
            if op == 'PyCmp_EQ':        
                o.Raw(logic, ' = 0;')
            else:    
                o.Raw(logic, ' = 1;')
            o.Raw('} else {')
            ref0 = New()
            o.Raw(ref0, ' = PyTuple_Type.tp_richcompare(', ref1, ', ', ref2, ', ', op, ');')
            ToTrue(o, logic, ref0, it)
            o.Raw('}')
        else:    
            ref0 = New()
            o.Raw(ref0, ' = PyTuple_Type.tp_richcompare(', ref1, ', ', ref2, ', ', op, ');')
            ToTrue(o, logic, ref0, it)
        o.Cls(ref1, ref2)
        return o, logic
    if t1 is None and t2 == Kl_Tuple:
        ref1, ref2 = Expr(o, it[1:3])
        o.Raw('if (PyTuple_CheckExact(', ref1, ')) {')
        ref0 = New()
        o.Raw(ref0, ' = PyTuple_Type.tp_richcompare(', ref1, ', ', ref2, ', ', op, ');')
        ToTrue(o, logic, ref0, it)
        o.Cls(ref0)
        o.Raw('} else {')    
        o.Stmt(logic, '=', 'PyObject_RichCompareBool', ref1, ref2, it[3])
        o.Raw('}')
        o.Cls(ref1, ref2)
        return o, logic
    if t2 is None and t1 == Kl_Tuple:
        ref1, ref2 = Expr(o, it[1:3])
        o.Raw('if (PyTuple_CheckExact(', ref2, ')) {')
        ref0 = New()
        o.Raw(ref0, ' = PyTuple_Type.tp_richcompare(', ref1, ', ', ref2, ', ', op, ');')
        ToTrue(o, logic, ref0, it)
        o.Cls(ref0)
        o.Raw('} else {')    
        o.Stmt(logic, '=', 'PyObject_RichCompareBool', ref1, ref2, it[3])
        o.Raw('}')
        o.Cls(ref1, ref2)
        return o, logic
    if t1 == Kl_String and t2 == Kl_String:
        ref1, ref2 = Expr(o, it[1:3])
        if op == 'PyCmp_EQ':
            o.Raw(logic, ' = (PyString_GET_SIZE(', ref1,') == PyString_GET_SIZE(', ref2, ')) && ', \
                  '(((PyStringObject *)',ref1,')->ob_sval[0] == ((PyStringObject *)',ref2, ')->ob_sval[0]) && ', \
                  '(memcmp(((PyStringObject *)',ref1,')->ob_sval, ((PyStringObject *)',ref2,')->ob_sval, ',
                        'PyString_GET_SIZE(', ref1,')) == 0);')
        elif op == 'PyCmp_NE':
            o.Raw(logic, ' = (PyString_GET_SIZE(', ref1,') != PyString_GET_SIZE(', ref2, ')) || ', \
                  '(((PyStringObject *)',ref1,')->ob_sval[0] != ((PyStringObject *)',ref2, ')->ob_sval[0]) || ', \
                  '(memcmp(((PyStringObject *)',ref1,')->ob_sval, ((PyStringObject *)',ref2,')->ob_sval, ',
                        'PyString_GET_SIZE(', ref1,')) != 0);')
        else:    
            ref0 = New()
            o.Raw(ref0, ' = PyString_Type.tp_richcompare(', ref1, ', ', ref2, ', ', op, ');')
            ToTrue(o, logic, ref0, it)
        o.Cls(ref1, ref2)
        return o, logic
    if t1 == Kl_String and t2 is None and op in ('PyCmp_EQ', 'PyCmp_NE'):
        ref1, ref2 = Expr(o, it[1:3])
        o.Raw('if (PyString_CheckExact(', ref2, ')) {')
        if op == 'PyCmp_EQ':
            o.Raw(logic, ' = (PyString_GET_SIZE(', ref1,') == PyString_GET_SIZE(', ref2, ')) && ', \
                  '(((PyStringObject *)',ref1,')->ob_sval[0] == ((PyStringObject *)',ref2, ')->ob_sval[0]) && ', \
                  '(memcmp(((PyStringObject *)',ref1,')->ob_sval, ((PyStringObject *)',ref2,')->ob_sval, ',
                        'PyString_GET_SIZE(', ref1,')) == 0);')
        else:
            o.Raw(logic, ' = (PyString_GET_SIZE(', ref1,') != PyString_GET_SIZE(', ref2, ')) || ', \
                  '(((PyStringObject *)',ref1,')->ob_sval[0] != ((PyStringObject *)',ref2, ')->ob_sval[0]) || ', \
                  '(memcmp(((PyStringObject *)',ref1,')->ob_sval, ((PyStringObject *)',ref2,')->ob_sval, ',
                        'PyString_GET_SIZE(', ref1,')) != 0);')
        o.Raw('} else {')    
        o.Stmt(logic, '=', 'PyObject_RichCompareBool', ref1, ref2, it[3])
        o.Raw('}')
        o.Cls(ref1, ref2)
        return o, logic

    if t1 is None and t2 == Kl_Int:
        if op in op_to_oper:
            ref1 = Expr1(it[1],o)   
            ref2 = Expr1(it[2],o)   
            o.Raw('if (PyInt_CheckExact(', ref1, ')) {')
            int1 = ConC('PyInt_AS_LONG(',ref1,')') 
            int2 = ConC('PyInt_AS_LONG(',ref2,')') 
            o.Raw(logic, ' = ', int1, op_to_oper[op], int2, ';')
            o.Raw('} else {')
            o.Stmt(logic, '=', 'PyObject_RichCompareBool', ref1, ref2, it[3])
            o.Raw('}')
            o.Cls(ref1, ref2)
            return o, logic
    
    if t1 == Kl_Short and t2 is None and op in op_to_oper:
        o1,size_t_1 = shortage(generate_ssize_t_expr(it[1]))
        o.extend(o1)
        ref2 = Expr1(it[2], o)
        o.Raw('if (PyInt_CheckExact(', ref2, ')) {')
        o.Raw(logic, ' = ', size_t_1, op_to_oper[op], 'PyInt_AS_LONG(', ref2, ');')
        o.Raw('} else {')
        ref1 = New()
        o.Raw('if ((', ref1, ' = PyInt_FromSsize_t(', size_t_1, ')) == NULL) goto ', labl, ';')
        UseLabl()
        o.Stmt(logic, '=', 'PyObject_RichCompareBool', ref1, ref2, it[3])
        o.Cls(ref1)
        o.Raw('}')
        o.Cls(ref2, size_t_1)
        return o, logic

    if t2 == Kl_Short and t1 is None and op in op_to_oper:
        ref1 = Expr1(it[1], o)
        o2,size_t_2 = shortage(generate_ssize_t_expr(it[2]))
        o.extend(o2)
        o.Raw('if (PyInt_CheckExact(', ref1, ')) {')
        o.Raw(logic, ' = PyInt_AS_LONG(', ref1, ')', op_to_oper[op], size_t_2, ';')
        o.Raw('} else {')
        ref2 = New()
        o.Raw('if ((', ref2, ' = PyInt_FromSsize_t(', size_t_2, ')) == NULL) goto ', labl, ';')
        UseLabl()
        o.Stmt(logic, '=', 'PyObject_RichCompareBool', ref1, ref2, it[3])
        o.Cls(ref2)
        o.Raw('}')
        o.Cls(ref1, size_t_2)
        return o, logic

            
    if t1 is not None and t2 is not None:    
        Debug('Typed comparison unrecognized %s %s %s' % (t1, op, t2), it[1], it[2])
    elif t1 is not None or t2 is not None:    
        Debug('Half-typed comparison unrecognized %s %s %s' % (t1, op, t2), it[1], it[2])
                
    ref1, ref2 = Expr(o, it[1:3])
    o.Stmt(logic, '=', 'PyObject_RichCompareBool', ref1, ref2, it[3])
    o.Cls(ref1, ref2)
    return o, logic
    
def generate_logical_expr(it, logic = None):
    it0 = it[0]
    if type(it0) is str and it0[-1] == '(':
        it0 = it0[:-1]
    if logic is None:    
        logic = New('int')
    o = Out()    
    if it0 == '!PyObject_RichCompare':
        return generate_rich_compare(it,logic,o)
    if it0 == '!BOOLEAN':
        return generate_logical_expr(it[1], logic) 
    if it0 == 'CONST':
        if it[1]:
            o.Stmt(logic, '=', 1)
            return o, logic
        if not it[1]:
            o.Stmt(logic, '=', 0)
            return o, logic
        Fatal('shd', it)
    if it0 == '!1NOT':
        if it[1] == ('CONST', False):
            o.Stmt(logic, '=', 1)
            return o, logic
        if it[1] == ('CONST', True):
            o.Stmt(logic, '=', 0)
            return o, logic
        if it[1][0] in IsObject:
            ref1 = Expr1(it[1], o)
            o.Stmt(logic, '=', 'PyObject_Not', ref1)
            o.Cls(ref1)
            return o, logic
        o,logic = generate_logical_expr(it[1], logic)
        if istemptyped(logic):
            o.Raw(logic, ' = !(', logic,');')
            return o, logic
        else:    
            logic2 = New('int')
            o.Raw(logic2, ' = !(', logic,');')
            return o, logic2
    if it0 in API_cmp_2_PyObject:
        ref1, ref2 = Expr(o, it[1:3])
        o.Stmt(logic, '=', it0[1:], ref1, ref2)
        o.Cls(ref1, ref2)
        return o, logic

    if it0 in ('!_EQ_', '!_NEQ_'):
        if it[1][0] == '!PyObject_Type' and it[2][0] == '!LOAD_BUILTIN' and it[2][1] in type_to_check:
            ref1 = Expr1(it[1][1], o)
            if it0 == '!_EQ_':
                o.Raw(logic, ' = ', type_to_check[it[2][1]], '(', ref1, ');')
            else:
                o.Raw(logic, ' = !', type_to_check[it[2][1]], '(', ref1, ');')
            o.Cls(ref1)
            return o, logic
        if it[2][0] == '!PyObject_Type' and it[1][0] == '!LOAD_BUILTIN' and it[1][1] in type_to_check:
            ref1 = Expr1(it[2][1], o)
            if it0 == '!_EQ_':
                o.Raw(logic, ' = ', type_to_check[it[1][1]], '(', ref1, ');')
            else:
                o.Raw(logic, ' = !', type_to_check[it[1][1]], '(', ref1, ');')
            o.Cls(ref1)
            return o, logic
        if it[1][0] == '!PyObject_Type' and it[2][0] == 'CALC_CONST' and IsAnyClass(it[2][1]):
            ref1 = Expr1(it[1][1], o)
            if it0 == '!_EQ_':
                o.Raw(logic, ' =  ((PyObject *)(((PyObject*)(',ref1,'))->ob_type)) == ', it[2], ';')
            else:
                o.Raw(logic, ' = ((PyObject *)(((PyObject*)(',ref1,'))->ob_type)) != ', it[2], ';')
            o.Cls(ref1)
            return o, logic
        if it[2][0] == '!PyObject_Type' and it[1][0] == 'CALC_CONST' and IsAnyClass(it[1][1]):
            ref1 = Expr1(it[2][1], o)
            if it0 == '!_EQ_':
                o.Raw(logic, ' = ((PyObject *)(((PyObject*)(',ref1,'))->ob_type)) == ', it[1], ';')
            else:
                o.Raw(logic, ' = ((PyObject *)(((PyObject*)(',ref1,'))->ob_type)) != ', it[1], ';')
            o.Cls(ref1)
            return o, logic
        
        ref1 = Expr1(it[1], o)
        o2 = Out()
        ref2 = Expr1(it[2], o2)
        skip1 = False
        skip2 = False
        if istempref(ref1) and o[-1] == ConC('Py_INCREF(', ref1, ');') and len(o2) == 0:
            del o[-1]
            skip1 = True
        if istempref(ref2) and o2[-1] == ConC('Py_INCREF(', ref2, ');') and len(o) == 0:
            del o2[-1]
            skip2 = True
        o.extend(o2)    
        if it0 == '!_EQ_':
            o.Stmt(logic, '=', ref1, '==', ref2)
        else:    
            o.Stmt(logic, '=', ref1, '!=', ref2)
        if skip1:    
            o.ClsFict(ref1)
        else:   
            o.Cls(ref1)
        if skip2:    
            o.ClsFict(ref2)
        else:   
            o.Cls(ref2)
        return o, logic
    if it0 in ('!OR_JUMP', '!OR_BOOLEAN', '!OR_JUMPED_STACKED'):
        o = generate_and_or_logical(it[1:], False, logic)
        return o, logic
    if it0 in ('!AND', '!AND_JUMP', '!AND_BOOLEAN', '!AND_JUMPED_STACKED'):
        o = generate_and_or_logical(it[1:], True, logic)
        return o, logic
    if it0 in ('!SSIZE_T==', '!SSIZE_T>', '!SSIZE_T>=', '!SSIZE_T!=', \
               '!SSIZE_T<', '!SSIZE_T<='):
        o1,size_t_1 = shortage(generate_ssize_t_expr(it[1]))
        o2,size_t_2 = shortage(generate_ssize_t_expr(it[2]))
        o1.extend(o2)
        o1.Raw(logic, ' = ', size_t_1, ' ', it0[8:], ' ', size_t_2, ';')
        o1.Cls(size_t_1, size_t_2)
        return o1, logic
    if it0 == '!PY_SSIZE_T':
        o1,size_t_1 = shortage(generate_ssize_t_expr(it[1]))
        o1.Raw(logic, ' = ', size_t_1, ' != ', 0, ';')
        o1.Cls(size_t_1)
        return o1,logic
    if it0 in ('!c_PyCmp_EQ_Int', '!c_PyCmp_NE_Int', '!c_PyCmp_LT_Int', \
               '!c_PyCmp_LE_Int', '!c_PyCmp_GT_Int', '!c_PyCmp_GE_Int'):
        op = it0[3:-4]           
        oper = op_to_oper[op]           
        t = TypeExpr(it[1])
        if t is not None and t.descr not in (int, float): 
            return generate_logical_expr(('!PyObject_RichCompare(', it[1], it[2], op), logic)
        ref = Expr1(it[1], o)
        if t is not None and not IsInt(t):
            Debug('typed compare', t,it)
        o2 = Out()
        if it[2][0] in ('CONST', 'LOAD_CONST') and type(it[2][1]) is int:
            int_t = it[2][1]    
            int_2 = const_to(int_t)   
        else:
            Fatal('', it, type(it[2][1]))
        o.extend(o2)     
        if IsInt(t):
            o.Raw(logic, ' = PyInt_AS_LONG( ', ref, ' )', oper, int_t, ';')
            o.Cls(ref, int_t)
            return o,logic
        if IsFloat(t):
            o.Raw(logic, ' = PyFloat_AS_DOUBLE( ', ref, ' )', oper, int_t, ';')
            o.Cls(ref, int_t)
            return o,logic
        if t is not None:
            Debug('Typed %s (%s, %s)' % (it0, t, it[2]), it) 
            ## if type(it[2]) is int:
                ## return generate_logical_expr(('!PyObject_RichCompare(', it[1], ('CONST', it[2]), op), logic)
            ## return generate_logical_expr(('!PyObject_RichCompare(', it[1], it[2], op), logic)
        o.Stmt(logic,'=', it0[1:], ref, int_t, int_2)
        o.Cls(ref, int_t)
        return o,logic

    if it0 in ('!c_PyCmp_EQ_String', '!c_PyCmp_NE_String'):
        ref = Expr1(it[1], o)
        if it[2][0] == 'CONST' and type(it[2][1]) is str:
            s_t = it[2][1]    
            s_2 = const_to(s_t)   
        else:
            Fatal('', it)
        t1 = TypeExpr(it[1])  
        ## if t1 == Kl_String:  
## ##            o.Raw('if (!PyString_CheckExact(', ref,')) {printf(\"ooo %d ooo\", __LINE__); exit(1);}')
            ## o.Raw(logic,' = _', it0[1:], '(', ref, ', ', len(s_t), ', ', generate_chars_literal(s_t), ');')
            ## o.Cls(ref)
            ## return o,logic
        if t1 is not None:
            Debug('Typed %s (%s, <str>)' % ( it0, t1), it[1], it[2])     
        o.Raw(logic,' = ', it0[1:], '(', ref, ', ', len(s_t), ', ', generate_chars_literal(s_t), ', ', s_2, ');')
        o.Cls(ref)
        return o,logic
    if it0 == '!NCMP':
        tu = list(it[1])
        to_cls = []
        logic2 = New('int')
        o.Raw(logic, ' = 0;')
        ref1 = Expr1(tu[0], o)
        ref2 = Expr1(tu[2], o)
        if tu[1] == 'is':
            o.Stmt(logic2, '=', ref1, '==', ref2)
        elif tu[1] == 'is not':    
            o.Stmt(logic2, '=', ref1, '!=', ref2)
        elif tu[1] == 'in':    
            o.Stmt(logic2, '=', 'PySequence_Contains', ref2, ref1)
        elif tu[1] == 'not in':    
            o.Stmt(logic2, '=', 'PySequence_Contains', ref2, ref1)
            o.Raw(logic2, ' = ! ', logic2, ';')
        else:    
            o.Stmt(logic2, '=', 'PyObject_RichCompareBool', ref1, ref2, op_2_c_op[tu[1]])
        del tu[:3]
        to_cls.append(ref1)
        ref1 = ref2 
        o.Raw('if (', logic2, ') {')
        while len(tu) > 1:
            ref2 = Expr1(tu[1], o)
            if tu[0] == 'is':
                o.Stmt(logic2, '=', ref1, '==', ref2)
            elif tu[0] == 'is not':    
                o.Stmt(logic2, '=', ref1, '!=', ref2)
            elif tu[0] == 'in':    
                o.Stmt(logic2, '=', 'PySequence_Contains', ref2, ref1)
            elif tu[0] == 'not in':    
                o.Stmt(logic2, '=', 'PySequence_Contains', ref2, ref1)
                o.Raw(logic2, ' = ! ', logic2, ';')
            else:    
                o.Stmt(logic2, '=', 'PyObject_RichCompareBool', ref1, ref2, op_2_c_op[tu[0]])
            del tu[:2]
            to_cls.append(ref1)
            ref1 = ref2 
            o.Raw('if (', logic2, ') {')
        o.Raw(logic, ' = 1;')
        for r in range(len(to_cls)):
            o.Raw('}')
        o.Cls(logic2)
        o.Cls(*to_cls) 
        o.Cls(ref1)            
        return o, logic
        
    ref1 = Expr1(it, o)
    return ToTrue(o,logic,ref1, it)
 
def ToTrue(o, logic, ref1, it):
    last = o[-3:]
    del_check = False
    if len(last) > 0:
        che = ('if ( %s == NULL ) goto %s;' % (CVar(ref1), CVar(labl)))
        UseLabl()
        if last[-1] == che:
            del_check = True
            del last[-1]
    if len(last) > 0:
        beg = CVar(ref1) + ' = PyBool_FromLong ('
        if last[-1].startswith(beg) and last[-1].endswith(');'):
            if del_check:
                del o[-1]
            c_expr = o[-1][len(beg):-2]
            del o[-1]
            o.ClsFict(ref1)
            o.Raw(logic, ' = ', c_expr, ';')
            return o, logic      
        beg = CVar(ref1) + ' = PyInt_FromLong('
        if last[-1].startswith(beg) and last[-1].endswith(');'):
            if del_check:
                del o[-1]
            c_expr = o[-1][len(beg):-2]
            del o[-1]
            o.ClsFict(ref1)
            o.Raw(logic, ' = ', c_expr, ';')
            return o, logic  #    Debug('generate_logical_expr', it, o[-3:])    
    if IsInt(TypeExpr(it)):    
        o.Raw(logic, ' = PyInt_AS_LONG( ', ref1, ' ) != 0;')
        o.Cls(ref1)
        return o, logic
    o.Stmt(logic, '=', 'PyObject_IsTrue', ref1)
    o.Cls(ref1)
    return o, logic

def generate_and_or_logical(it, is_and, logic):
    o,logic1 = generate_logical_expr(it[0], logic)
    if len(it) == 1:
        return o
    if type(logic1) is int:
        logic2 = New('int')
        o.Stmt(logic2, '=', logic1)
        logic1 = logic2
    if not istemptyped(logic1) and logic is None:
        logic2 = New('int')
        o.Stmt(logic2, '=', logic1)
        logic1 = logic2
    if is_and:    
        o.Stmt('if (', logic1, ') {')
    else:    
        o.Stmt('if (!(', logic1, ')) {')
    o2 = generate_and_or_logical(it[1:], is_and, logic1)
    o.extend(o2)
    o.Raw('}')
    return o  

def generate_preexpr(it,o):
    assert len(it) == 3
    assert it[0][0] == '(PREEXPR'
    assert it[2][0] == ')PREEXPR'
    acc = it[1]
    refs = Expr(o, acc) #[Expr1(x, o) for x in acc]
    PushAcc(acc, refs)            
    generate_list(it[1],o)
    PopAcc(o, False)     
    o.Cls(*refs)       
    ## for x in refs:
        ## o.Cls(x)            

def shortage(l):
    o, logic = l
    if len(o) == 0:
        return o, logic
    if not istemptyped(logic):
        return o, logic
    if len(o) == 1 and o[0].startswith(ConC(logic, ' = ')) and\
       o[0].endswith(';'):
       s = o[0].split(' = ')
       if len(s) != 2:
            return o, logic
       if s[0] != ConC(logic):
            return o, logic
       o2 = Out()
       o2.Cls(logic)
       return o2, '(' + s[1][:-1] + ')'
    if len(o) > 1 and o[-1].startswith(ConC(logic, ' = ')) and\
       o[-1].endswith(';'):
       s = o[-1].split(' = ')
       if len(s) != 2:
            return o, logic
       if s[0] != ConC(logic):
            return o, logic
       o2 = Out()
       o2.extend(o[:-1])
       o2.Cls(logic)
       return o2, '(' + s[1][:-1] + ')'
    return o, logic
    
def generate_if(it,o):
    if it[0][1][0] == '!1NOT' and len(it) > 3:
       if_ = list(it[0])
       if_[1] = if_[1][1]
       it[0] = tuple(if_)
       it[1], it[3] = it[3], it[1]
    if it[0][1] == ('CONST', True):
        generate_list(it[1], o)
        return
    if it[0][1] == ('CONST', False):
        if len(it) == 3:
            return
        generate_list(it[3], o)
        return

    o1, logic = shortage(generate_logical_expr(it[0][1]))
    o.extend(o1)
    o.Stmt('if (', logic, ') {')
    o.Cls(logic)
    generate_list(it[1], o)
    if len(it) == 3:
        o.Raw('}')
        return
    assert it[2][0] == ')(ELSE'
    o.Raw('} else {')
    generate_list(it[3], o)
    o.Raw('}')
    assert it[4][0] == ')ENDIF'

def generate_while(it,o):
    global try_jump_context, dropped_temp
    have_else = it[2][0] == ')(ELSE'
    if have_else:
        else_cond = New('int')
        o.Stmt(else_cond, '=', 1)
    try_jump_context.append(False)    
    dropped_temp.append(('WHILE', ()))
    o.Stmt('for (;;) {')
    o1, logic = shortage(generate_logical_expr(it[0][1]))
    o.extend(o1)
    if logic != '1' and logic != '(1)':
        o.Stmt('if (!(', logic, ')) break')
    o.Cls(logic)
    if have_else:
        o.Stmt(else_cond, '=', 0)
    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    if have_else:
        o.Stmt ('if (', else_cond,') {')
        o.Cls(else_cond)
        generate_list(it[3], o)
        o.Raw('}')
        assert len(it) == 5
        return
    assert len(it) == 3

def generate_for_and_else_new(it,o): 
    global try_jump_context, dropped_temp
    iter = it[0][2]
    riter = Expr1(iter, o)
    riter2 = New()
    o.Stmt(riter2, '=', 'PyObject_GetIter', riter)
    o.Cls(riter)
    try_jump_context.append(False)
    to_else = New('int')
    o.Raw(to_else, ' = 1;')
    dropped_temp.append(('FOR', (riter2,)))
    o.Stmt('for (;;) {')
    ref = New()
    o.Stmt(ref, '=', 'PyIter_Next', riter2)
    o.Raw('if (PyErr_Occurred()) goto ', labl, ';')
    UseLabl()
    o.Stmt('if (!', ref, '){ break; }')
    if len(it[0][1]) == 1:
       generate_store(it[0][1][0], ref, o, 'PyIter_Next')
    else:  
       generate_store(('SET_VARS', it[0][1]), ref, o, 'PyIter_Next')
    o.Cls(ref)
    o.Raw(to_else, ' = 0;')
    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(riter2) 
    o.Stmt('if (', to_else, ') {')
    generate_list(it[3], o)
    o.Raw('}')
    o.Cls(to_else)

    assert len(it) in (3,5)

def generate_for_body_range_one_arg(o, hdr, body, pos_iter):
    if len(hdr[1]) == 1 and hdr[1][0][0] == 'STORE_FAST' and not have_subexpr(body, hdr[1][0]):
        body2 = replace_subexpr(body, ('FAST', hdr[1][0][1]), ('!@PyInt_FromSsize_t', pos_iter, ('FAST', hdr[1][0][1])))
        generate_list(body2, o)
    else:            
        generate_list(body, o)

def generate_for_range_one_arg(it, o, range_arg):
    global try_jump_context, dropped_temp

    try_jump_context.append(False)
    if type(range_arg) != int:
        ref_arg = Expr1(range_arg, o)
        cnt = New('Py_ssize_t')
        o.Stmt(cnt, '=', 'PyInt_AsSsize_t', ref_arg)
        o.Cls(ref_arg)
    else:
        cnt = range_arg    
    dropped_temp.append(('FOR', ()))
    pos_iter = New('Py_ssize_t')
    o.Raw('for (', pos_iter, ' = 0;', pos_iter, ' < ', cnt, ';', pos_iter, ' ++) {')
    ref = New()
    o.Stmt(ref, '=', 'PyInt_FromSsize_t', pos_iter)
    if len(it[0][1]) == 1:        
        generate_store(it[0][1][0], ref, o, 'PyInt_FromSsize_t')
    else:  
        generate_store(('SET_VARS', it[0][1]), ref, o, 'PyInt_FromSsize_t')
    o.Cls(ref)
    generate_for_body_range_one_arg(o, it[0], it[1], pos_iter)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(pos_iter, cnt) 
    
def generate_for_list_new(it,o): 
    global try_jump_context, dropped_temp

    iter = it[0][2]
    v = []
    if TCmp(iter, v, ('!PyObject_Call', \
                      ('!LOAD_BUILTIN', 'range'), \
                      ('CONST', ('?',)), ('NULL',))) and\
                      type(v[0]) is int:
        generate_for_range_one_arg(it, o, v[0])
        return                  
    if TCmp(iter, v, ('!PyObject_Call', \
                      ('!LOAD_BUILTIN', 'range'), \
                      ('!BUILD_TUPLE', ('?',)), ('NULL',))):
        generate_for_range_one_arg(it, o, v[0])
        return                  
    riter = Expr1(iter, o)
    try_jump_context.append(False)
    dropped_temp.append(('FOR', (riter,)))
    pos_iter = New('int')
    o.Stmt(pos_iter, '=', 0)
    o.Raw('assert(PyList_CheckExact(', riter,'));')
    o.Raw('for (',pos_iter,' = 0;', pos_iter, ' < PyList_GET_SIZE(', riter, ');',pos_iter, '++) {')
    ref = New()
    o.Stmt(ref, '=', 'PyList_GET_ITEM', riter, pos_iter)
    if len(it[0][1]) == 1:
        generate_store(it[0][1][0], ref, o, 'PyList_GET_ITEM')
    else:  
        generate_store(('SET_VARS', it[0][1]), ref, o, 'PyList_GET_ITEM')
    o.Cls(ref)
    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(riter, pos_iter) 

def generate_for_universal_new(it,o): 
    global try_jump_context, dropped_temp

    iter = it[0][2]
    riter = Expr1(iter, o)
    riter2 = New()
    pos_iter = New('int')
    o.Raw(pos_iter, ' = 0;')
    o.Raw(riter2, ' = NULL;')
    o.Raw('if (!PyList_CheckExact(', riter, ') && !PyTuple_CheckExact(', riter, ')) {')
    o.Stmt(riter2, '=', 'PyObject_GetIter', riter)
    o.Raw('}')
    try_jump_context.append(False)
    dropped_temp.append(('FOR', (riter2,  riter)))
    o.Stmt('for (;;) {')
    ref = New()
    o.Raw('if (PyList_CheckExact(', riter, ')) {')
    o.Stmt('if (', pos_iter, '>= PyList_GET_SIZE(', riter, ')) break;')
    o.Stmt(ref, '=', 'PyList_GET_ITEM', riter, pos_iter)
    o.Raw(pos_iter, '++;')
    o.Raw('} else if (PyTuple_CheckExact(', riter, ')) {')
    o.Stmt('if (', pos_iter, '>= PyTuple_GET_SIZE(', riter, ')) break;')
    o.Stmt(ref, '=', 'PyTuple_GET_ITEM', riter, pos_iter)
    o.Raw(pos_iter, '++;')
    o.Raw('} else {')
    o.Stmt(ref, '=', 'PyIter_Next', riter2)
    o.Raw('if (PyErr_Occurred()) goto ', labl, ';')
    UseLabl()
    o.Stmt('if (!', ref, '){ break; }')
    o.Raw('}')
    if len(it[0][1]) == 1:
        generate_store(it[0][1][0], ref, o, 'PyIter_Next')
    else:  
        generate_store(('SET_VARS', it[0][1]), ref, o, 'PyIter_Next')
    o.Cls(ref)
    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(riter, riter2, pos_iter) 

def generate_for_tuple_new(it,o): 
    global try_jump_context, dropped_temp

    iter = it[0][2]
    riter = Expr1(iter, o)
    try_jump_context.append(False)
    dropped_temp.append(('FOR', (riter,)))
    pos_iter = New('int')
    o.Stmt(pos_iter, '=', 0)
    o.Raw('assert(PyTuple_CheckExact(', riter,'));')
    o.Raw('for (',pos_iter,' = 0;', pos_iter, ' < PyTuple_GET_SIZE(', riter, ');',pos_iter, '++) {')
    ref = New()
    o.Stmt(ref, '=', 'PyTuple_GET_ITEM', riter, pos_iter)
    if len(it[0][1]) == 1:
        generate_store(it[0][1][0], ref, o, 'PyTuple_GET_ITEM')
    else:  
        generate_store(('SET_VARS', it[0][1]), ref, o, 'PyTuple_GET_ITEM')
    o.Cls(ref)
    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(riter, pos_iter) 

def generate_for_enumerate_new(it,o, store1, store2, iter): 
    global try_jump_context, dropped_temp

    riter = Expr1(iter, o)
    riter2 = New()
    pos_iter = New('int')
    o.Raw(pos_iter, ' = 0;')
    o.Raw(riter2, ' = NULL;')
    o.Raw('if (!PyList_CheckExact(', riter, ') && !PyTuple_CheckExact(', riter, ')) {')
    o.Stmt(riter2, '=', 'PyObject_GetIter', riter)
    o.Raw('}')
    try_jump_context.append(False)
    dropped_temp.append(('FOR', (riter2,  riter)))
    o.Stmt('for (;;) {')
    ref = New()
    o.Raw('if (PyList_CheckExact(', riter, ')) {')
    o.Stmt('if (', pos_iter, '>= PyList_GET_SIZE(', riter, ')) break;')
    o.Stmt(ref, '=', 'PyList_GET_ITEM', riter, pos_iter)
    o.Raw('} else if (PyTuple_CheckExact(', riter, ')) {')
    o.Stmt('if (', pos_iter, '>= PyTuple_GET_SIZE(', riter, ')) break;')
    o.Stmt(ref, '=', 'PyTuple_GET_ITEM', riter, pos_iter)
    o.Raw('} else {')
    o.Stmt(ref, '=', 'PyIter_Next', riter2)
    o.Raw('if (PyErr_Occurred()) goto ', labl, ';')
    UseLabl()
    o.Stmt('if (!', ref, '){ break; }')
    o.Raw('}')
    if len(it[0][1]) != 2:
        Fatal('Strange enumerate', it[0])
    ref_ind = New()
    o.Stmt(ref_ind, '=', 'PyInt_FromLong', pos_iter)
    generate_store(it[0][1][0], ref_ind, o, 'PyIter_Next')
    o.Cls(ref_ind)
    generate_store(it[0][1][1], ref, o, 'PyIter_Next')
    o.Cls(ref)
    o.Raw(pos_iter, '++;')
    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(riter, riter2, pos_iter) 

def generate_for_enumerate_list_new(it,o, store1, store2, iter): 
    global try_jump_context, dropped_temp

    riter = Expr1(iter, o)
    pos_iter = New('int')
    try_jump_context.append(False)
    dropped_temp.append(('FOR', (riter,)))
    o.Raw('assert(PyList_CheckExact(', riter,'));')
    o.Raw('for (',pos_iter,' = 0;', pos_iter, ' < PyList_GET_SIZE(', riter, ');',pos_iter, '++) {')
    ref = New()
    o.Stmt(ref, '=', 'PyList_GET_ITEM', riter, pos_iter)
    if len(it[0][1]) != 2:
        Fatal('Strange enumerate', it[0])
    ref_ind = New()
    o.Stmt(ref_ind, '=', 'PyInt_FromLong', pos_iter)
    generate_store(it[0][1][0], ref_ind, o, 'PyList_GET_ITEM')
    o.Cls(ref_ind)
    generate_store(it[0][1][1], ref, o, 'PyList_GET_ITEM')
    o.Cls(ref)
    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(riter, pos_iter) 

def generate_for_enumerate_tuple_new(it,o, store1, store2, iter): 
    global try_jump_context, dropped_temp

    riter = Expr1(iter, o)
    pos_iter = New('int')
    try_jump_context.append(False)
    dropped_temp.append(('FOR', (riter,)))
    o.Raw('assert(PyTuple_CheckExact(', riter,'));')
    o.Raw('for (',pos_iter,' = 0;', pos_iter, ' < PyTuple_GET_SIZE(', riter, ');',pos_iter, '++) {')
    ref = New()
    o.Stmt(ref, '=', 'PyTuple_GET_ITEM', riter, pos_iter)
    if len(it[0][1]) != 2:
        Fatal('Strange enumerate', it[0])
    ref_ind = New()
    o.Stmt(ref_ind, '=', 'PyInt_FromLong', pos_iter)
    generate_store(it[0][1][0], ref_ind, o, 'PyTuple_GET_ITEM')
    o.Cls(ref_ind)
    generate_store(it[0][1][1], ref, o, 'PyTuple_GET_ITEM')
    o.Cls(ref)
    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(riter, pos_iter) 

def generate_for_iteritems_generator_standard(it,o):
    global try_jump_context, dropped_temp

    iter = it[0][2]
    riter = Expr1(iter, o)
    try_jump_context.append(False)
    dropped_temp.append(('FOR', (riter,)))
    o.Stmt('for (;;) {')
    ref = New()
    o.Stmt(ref, '=', 'PyIter_Next', riter)
    o.Raw('if (PyErr_Occurred()) goto ', labl, ';')
    UseLabl()
    o.Stmt('if (!', ref, '){ break; }')
    assert len(it[0][1]) == 2

    ref1 = New()
    o.Stmt(ref1, '=', 'PyTuple_GetItem', ref, 0)
    generate_store(it[0][1][0], ref1, o, 'PyIter_Next')
    o.Cls(ref1)
    ref1 = New()
    o.Stmt(ref1, '=', 'PyTuple_GetItem', ref, 1)
    generate_store(it[0][1][1], ref1, o, 'PyIter_Next')
    o.Cls(ref1)

    o.Cls(ref)
    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(riter)

def generate_for_iteritems_generator_new(it,o, v): 
    global try_jump_context, dropped_temp

    d = Expr1(v[2], o)
    pos = New('int')
    
    try_jump_context.append(False)
    dropped_temp.append(('FOR', (d, pos)))
    o.Raw(pos, ' = 0;')
    k, v = New(), New()
    o.Raw('while (PyDict_Next(', d, ', ', ('&', pos), ', ', ('&', k), ', ', ('&', v), ')) {')
    assert len(it[0][1]) == 2
    o.INCREF(k)       
    o.INCREF(v)       
    generate_store(it[0][1][0], k, o, 'PyDict_Next')
    generate_store(it[0][1][1], v, o, 'PyDict_Next')
    o.Cls(k,v)

    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(d,pos) 

def generate_for_iterkeys_generator_new(it,o, v): 
    global try_jump_context, dropped_temp

    d = Expr1(v[1], o)
    pos = New('int')
    
    try_jump_context.append(False)
    dropped_temp.append(('FOR', (d, pos)))
    o.Raw(pos, ' = 0;')
    k, v = New(), New()
    o.Raw('while (PyDict_Next(', d, ', ', ('&', pos), ', ', ('&', k), ', ', ('&', v), ')) {')
    assert len(it[0][1]) == 1
    o.INCREF(k)       
    o.INCREF(v)       
    generate_store(it[0][1][0], k, o, 'PyDict_Next')
    o.Cls(k,v)

    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(d,pos) 

def generate_for_itervalues_generator_new(it,o, v): 
    global try_jump_context, dropped_temp

    d = Expr1(v[1], o)
    pos = New('int')
    
    try_jump_context.append(False)
    dropped_temp.append(('FOR', (d, pos)))
    o.Raw(pos, ' = 0;')
    k, v = New(), New()
    o.Raw('while (PyDict_Next(', d, ', ', ('&', pos), ', ', ('&', k), ', ', ('&', v), ')) {')
    assert len(it[0][1]) == 1
    o.INCREF(k)       
    o.INCREF(v)       
    generate_store(it[0][1][0], v, o, 'PyDict_Next')
    o.Cls(k,v)

    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(d,pos) 

def generate_for_new(it,o): 
    global try_jump_context, dropped_temp
    if len(it) == 5 and it[2][0] == ')(ELSE':
        generate_for_and_else_new(it,o)
        return
    iter = it[0][2]
    type_for = TypeExpr(iter)
    if type_for == Kl_List:
        generate_for_list_new(it,o)
        return
    if type_for == Kl_Tuple:
        generate_for_tuple_new(it,o)
        return
    if type_for == Kl_Generator:
        v = []
        if TCmp(it[0], v,  ('(FOR', ('?', '?'), \
                             ('!PyObject_Call', ('!LOAD_BUILTIN', 'enumerate'), \
                                     ('!BUILD_TUPLE', ('?',)), ('NULL',)))):
            t = TypeExpr(v[2])
            if t == Kl_List:                             
                generate_for_enumerate_list_new(it, o, v[0], v[1], v[2])
            elif t == Kl_Tuple:                             
                generate_for_enumerate_tuple_new(it, o, v[0], v[1], v[2])
            else:
                generate_for_enumerate_new(it, o, v[0], v[1], v[2])
            return
        elif TCmp(it[0], v,  ('(FOR', ('?', '?'), \
                             ('!PyObject_Call', ('!PyObject_GetAttr', '?', ('CONST', 'iteritems')), \
                                     ('CONST', ()), ('NULL',)))):
            t = TypeExpr(v[2])
            if t == Kl_Dict:
                if dirty_iteritems:
                    generate_for_iteritems_generator_new(it,o, v)
                    return
                else:
                    generate_for_iteritems_generator_standard(it,o)
                    return
        elif TCmp(it[0], v,  ('(FOR', ('?',), \
                             ('!PyObject_Call', ('!PyObject_GetAttr', '?', ('CONST', 'iterkeys')), \
                                     ('CONST', ()), ('NULL',)))) and dirty_iteritems:
            t = TypeExpr(v[1])
            if t == Kl_Dict:
                generate_for_iterkeys_generator_new(it,o, v)
                return
        elif TCmp(it[0], v,  ('(FOR', ('?',), \
                             ('!PyObject_Call', ('!PyObject_GetAttr', '?', ('CONST', 'itervalues')), \
                                     ('CONST', ()), ('NULL',)))) and dirty_iteritems:
            t = TypeExpr(v[1])
            if t == Kl_Dict:
                generate_for_itervalues_generator_new(it,o, v)
                return
        generate_for_generator_new(it,o)
        return
    if type_for == Kl_XRange:
        generate_for_xrange_new(it,o)
        return
    return generate_for_universal_new(it,o)
 
def generate_for_generator_new(it,o): 
    global try_jump_context, dropped_temp
    iter = it[0][2]
    riter = Expr1(iter, o)
    try_jump_context.append(False)
    dropped_temp.append(('FOR', (riter,)))
    o.Stmt('for (;;) {')
    ref = New()
    o.Stmt(ref, '=', 'PyIter_Next', riter)
    o.Raw('if (PyErr_Occurred()) goto ', labl, ';')
    UseLabl()
    o.Stmt('if (!', ref, '){ break; }')
    if len(it[0][1]) == 1:
        generate_store(it[0][1][0], ref, o, 'PyIter_Next')
    else:  
        generate_store(('SET_VARS', it[0][1]), ref, o, 'PyIter_Next')
    o.Cls(ref)
    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(riter) 

def generate_for_xrange_new(it,o): 
    global try_jump_context, dropped_temp
    iter = it[0][2]

    v = []
    if TCmp(iter, v, ('!PyObject_Call', \
                      ('!LOAD_BUILTIN', 'xrange'), \
                      ('CONST', ('?',)), ('NULL',))) and\
                      type(v[0]) is int:
        generate_for_range_one_arg(it, o, v[0])
        return                  
    if TCmp(iter, v, ('!PyObject_Call', \
                      ('!LOAD_BUILTIN', 'xrange'), \
                      ('!BUILD_TUPLE', ('?',)), ('NULL',))):
        generate_for_range_one_arg(it, o, v[0])
        return                  

    riter = Expr1(iter, o)
 
    riter2 = New()
    o.Stmt(riter2, '=', 'PyObject_GetIter', riter)
    o.Cls(riter)
    
    try_jump_context.append(False)
    dropped_temp.append(('FOR', (riter2,)))
    o.Stmt('for (;;) {')
    ref = New()
    o.Stmt(ref, '=', 'PyIter_Next', riter2)
    o.Raw('if (PyErr_Occurred()) goto ', labl, ';')
    UseLabl()
    o.Stmt('if (!', ref, '){ break; }')
    if len(it[0][1]) == 1:
        generate_store(it[0][1][0], ref, o, 'PyIter_Next')
    else:  
        generate_store(('SET_VARS', it[0][1]), ref, o, 'PyIter_Next')
    o.Cls(ref)
    generate_list(it[1], o)
    o.Raw('}')
    del try_jump_context[-1]
    del dropped_temp[-1]
    o.Cls(riter2) 

    assert len(it) in (3,5)

def expanded_range(iter):
    v = []
    if TCmp(iter, v, ('!BUILD_LIST', '?')):
        li = v[0]
        rn = []
        for it in li:
            if it[0] != 'CONST':
                return None
            rn.append(it[1])
        if tuple(rn) == tuple(range(len(rn))):
            return ('!PyObject_Call', ('!LOAD_BUILTIN', 'range'), ('CONST', ('?',)), ('NULL',)) 
    return None

def is_like_float(a):
    if detect_float and have_floatmul(a):
        return True
    return False
        
def have_floatmul(a):
    if type(a) is tuple and len(a) > 0 and a != ('NULL',) and \
           type(a[0]) is str and TypeExpr(a) == Kl_Float:
        return True
    if type(a) is tuple:
        if len(a) >= 2 and a[0] == '!PyNumber_Multiply' and not (a[1][0] in ('!BUILD_LIST', '!BUILD_TUPLE')):
            return True
        if len(a) > 0 and a[0] == '!PyNumber_Divide':
            return True
        if len(a) > 0 and a[0] == 'CONST':
            return False
        for i in a:
            if type(i) is tuple and len(i) > 0 and i != ('NULL',):
                if have_floatmul(i):
                    return True
        return False
    if type(a) is list:
        for i in a:
            if have_floatmul(i):
                return True
        return False
    return False    
 
def have_subexpr(a,b):
    if type(a) == type(b) and a == b:
        return True
    if type(a) is tuple:
        if len(a) > 0 and a[0] == 'CONST':
            return False
        for i in a:
            if have_subexpr(i,b):
                return True
        return False
    if type(a) is list:
        for i in a:
            if have_subexpr(i,b):
                return True
        return False
    return False    

def find_statement_calculate_const(a, b):
    if type(a) is tuple and len(a) >= 2 and a[1] == b and \
       type(a[0]) is str and a[0][:6] == 'STORE_':
        return a
    if type(a) is tuple and len(a) >= 2 and \
       type(a[0]) is str and a[0] == 'IMPORT_FROM_AS' and b in a[3][1]:
           return a
    if type(a) is tuple:
        if len(a) > 0 and a[0] == 'CONST':
            return False
        for i in a:
            ret = find_statement_calculate_const(i,b)
            if ret == True:    
                return a
            if type(ret) is tuple:
                if ret[0] in ('STORE', 'SEQ_ASSIGN', 'SET_EXPRS_TO_VARS'):
                    return ret
                return a
        return False
    if type(a) is list:
        for i in a:
            ret = find_statement_calculate_const(i,b)
            if type(ret) is tuple:
                if ret[0] in ('STORE', 'SEQ_ASSIGN', 'SET_EXPRS_TO_VARS'):
                    return ret
                return ret
    return False    

def TCmp(e,v,p, trace = None):
    if trace is not None:
        pprint.pprint(( 'Parameters:', e,v,p))
    if p == '?':
        v.append(e)
        if trace is not None: print 'Cmp success ', e,v,p
        return True
    if type(p) is str:
        if e == p:
            if trace is not None: print 'Cmp success ', e,v,p
            return True
        if p[0] == ':' and p[-1] == ':':
            s = p[1:-1]
            if Is3(e, s):
                v.append((e,s, Val3(e,s)))
                if trace is not None: print 'Cmp success ', e,v,p
                return True
              
        del v[:]
        return False
    if type(p) is type:
        if type(e) is p:
            v.append(e)
            if trace is not None: print 'Cmp success ', e,v,p
            return True
        del v[:]
        return False        
    if type(p) is tuple:
        if len(p) > 0 and p[0] == '|':
            if e in p[1:]:
                if trace is not None: print 'Cmp success ', e,v,p
                return True
        if type(e) == type(p):
            if len(e) != len(p):
                del v[:]
                return False
            for i,p0 in enumerate(p):
                if trace is not None: print 'Cmp', i, p0
                if p0 == '*':
                    v.append(e[i:])
                    if trace is not None: print 'Cmp success ', e,v,p
                    return True
                if not TCmp(e[i], v, p0, trace):
                    del v[:]
                    return False
            if trace is not None: print 'Cmp success ', e,v,p
            return True
        del v[:]
        return False        
    if type(p) is list:
        if type(e) == type(p):
            if len(e) != len(p):
                del v[:]
                return False
            for i,p0 in enumerate(p):
                if not TCmp(e[i], v, p0):
                    del v[:]
                    return False
            if trace is not None: print 'Cmp success ', e,v,p
            return True
        del v[:]
        return False        
    if type(p) is dict:
        if e in p:
            v.append(e)
            if trace is not None: print 'Cmp success ', e,v,p
            return True
        del v[:]
        return False
    if e == p:
        if trace is not None: print 'Cmp success ', e,v,p
        return True
    del v[:]
    return False
  
def update_v_0_1(v):
    try:
        if v[0]:
            v[0] = True
        else:
            v[0] = False
    except:
        pass
           
def repl_list(a, up):
    i = 0
    aa = a[:]
    updated = False

    while i < len(aa):
        if i < 0:
            i = 0
            continue
        s = aa[i]
        v = []
        v0 = []
        v1 = []
        v2 = []
                
        if TCmp(s, v, ('SET_EXPRS_TO_VARS', (('STORE_FAST', '?'), '?'), ('CLONE', '?'))):            
            s1 = [('STORE', (('STORE_FAST', v[0]),), (v[2],)), ('STORE', (v[1],), (('FAST', v[0]),))]
            aa[i:i+1] = s1
            updated = True
            i -= 10
            continue
        
        if i < len(aa) - 2 and \
           TCmp(s, v, ('STORE', (('STORE_NAME', '?'),), (('!MK_FUNK', '?', ('CONST', ())),))) and\
           i+2 < len(aa) and aa[i+1][0] == '.L' and\
           TCmp(aa[i+2], v2, ('STORE', ('?',), \
                        (('!PyObject_Call', ('!LOAD_NAME', v[0]), \
                          ('CONST', ()), ('NULL',)),))):  
            ret2 = ('!PyObject_Call', ('!LOAD_NAME', v[0]), ('CONST', ()), ('NULL',)) # unchanged
            newstor = ('STORE', (v2[0],), (call_calc_const(v[1], ('CONST', ()), ret2),))
            if aa[i+2] != newstor:
                aa[i+2] = newstor    
                updated = True
                i -= 10
                continue

        if i < len(aa) - 2 and aa[i][0] == '.L' == aa[i+1][0]:
                del aa[i]
                updated = True
                i -= 10
                continue

        v = []
        v2 = []
        if TCmp(s, v, ('UNPUSH', ('CALC_CONST', '?'))):
            del aa[i]
            updated = True
            i -= 10
            continue
        if TCmp(s, v, ('SET_EXPRS_TO_VARS',
            (('STORE_NAME', '?'), ('STORE_NAME', '?')),
            (('CONST', '?'), ('CONST', '?')))):        
            s1 = [('STORE', (('STORE_NAME', v[0]),), (('CONST', v[2]),)), \
                  ('STORE', (('STORE_NAME', v[1]),), (('CONST', v[2]),))]
            aa[i:i+1] = s1
            updated = True
            i -= 10
            continue
        if i+1 < len(aa) and len(s) > 0 and s[0] == 'RETURN_VALUE' and \
           aa[i+1][0] in ('STORE', 'UNPUSH', '.L', 'RETURN_VALUE'):
            del aa[i+1]
            updated = True
            i -= 10
            continue
            
        if TCmp(s, v, ('UNPUSH', ('!PyObject_Call', 
                                ('!LOAD_BUILTIN', 'delattr'),
                                ('!BUILD_TUPLE', ('?', '?')), ('NULL',)))):
            s1 = [('PYAPI_CALL', ('PyObject_SetAttr', v[0], v[1], 'NULL'))]
            aa[i:i+1] = s1
            updated = True
            i -= 10
            continue
        s_ = []
        if type(s) is tuple and len(s) > 1 and s[0] == 'UNPUSH' and s[1][0] == '!PyObject_Call' and\
            TCmp(s, s_, ('UNPUSH', ('!PyObject_Call', \
                            ('!PyObject_GetAttr', '?', ('CONST', '?')), '?', ('NULL',)))):
            s_ = tuple(s_)                    
            if TCmp(s_, v, ('?', 'sort', ('CONST', ()))):
                if TypeExpr(v[0]) == Kl_List:
                    s1 = [('PYAPI_CALL', ('PyList_Sort', v[0]))]
                    aa[i:i+1] = s1
                    updated = True
                    i -= 10
                    continue
            ## if TCmp(s_, v, ('?', 'remove', ('CONST', ('?',)))): # worked like .index() -- not
                ## if TypeExpr(v[0]) == Kl_List and v[1] >= 0:
                    ## print 'v[1]', v[1]
                    ## s1 = [('PYAPI_CALL', ('PyList_SetSlice', v[0], v[1], v[1]+1, 'NULL'))]
                    ## aa[i:i+1] = s1
                    ## updated = True
                    ## i -= 10
                    ## continue
            if TCmp(s_, v, ('?', 'append', ('CONST', ('?',)))):
                if TypeExpr(v[0]) == Kl_List:
                    s1 = [('PYAPI_CALL', ('PyList_Append', v[0], ('CONST', v[1])))]
                    aa[i:i+1] = s1
                    updated = True
                    i -= 10
                    continue
            if TCmp(s_, v, ('?', 'append', ('!BUILD_TUPLE', ('?',)))):
                if TypeExpr(v[0]) == Kl_List:
                    s1 = [('PYAPI_CALL', ('PyList_Append', v[0], v[1]))]
                    aa[i:i+1] = s1
                    updated = True
                    i -= 10
                    continue
            ## if TCmp(s_, v, ('?', 'update', ('!BUILD_TUPLE', ('?',)))):
                ## if TypeExpr(v[0]) == Kl_Dict:
                    ## s1 = [('PYAPI_CALL', ('PyDict_MergeFromSeq2', v[0], v[1], 1))]
                    ## aa[i:i+1] = s1
                    ## updated = True
                    ## i -= 10
                    ## continue
            v = []    
            ## if TCmp(s_, v, ('!PyObject_GetAttr', '?', ('CONST', '__dict__'), \
                    ## 'update', ('!BUILD_TUPLE', ('?',)))):
                    ## s1 = [('PYAPI_CALL', ('PyDict_MergeFromSeq2', ('!PyObject_GetAttr', v[0], ('CONST', '__dict__')), v[1], 1))]
                    ## aa[i:i+1] = s1
                    ## updated = True
                    ## i -= 10
                    ## continue
            if TCmp(s_, v, ('?', 'clear', ('CONST', ()))):
                if TypeExpr(v[0]) == Kl_Dict:
                    s1 = [('PYAPI_CALL', ('PyDict_Clear', v[0]))]
                    aa[i:i+1] = s1
                    updated = True
                    i -= 10
                    continue
            if TCmp(s_, v, ('?', 'reverse', ('CONST', ()))):
                if TypeExpr(v[0]) == Kl_List:
                    s1 = [('PYAPI_CALL', ('PyList_Reverse', v[0]))]
                    aa[i:i+1] = s1
                    updated = True
                    i -= 10
                    continue
            if TCmp(s_, v, ('?', 'insert', ('CONST', ('?', '?')))):
                if TypeExpr(v[0]) == Kl_List:
                    s1 = [('PYAPI_CALL', ('PyList_Insert', v[0], v[1], ('CONST', v[2])))]
                    aa[i:i+1] = s1
                    updated = True
                    i -= 10
                    continue
            if TCmp(s_, v, ('?', 'insert', ('!BUILD_TUPLE', (('CONST', '?'), '?')))):
                if TypeExpr(v[0]) == Kl_List:
                    s1 = [('PYAPI_CALL', ('PyList_Insert', v[0], v[1], v[2]))]
                    aa[i:i+1] = s1
                    updated = True
                    i -= 10
                    continue

        if type(s) is tuple and len(s) > 0 and s[0] == 'STORE':
            if TCmp(s, v, \
                ('STORE', \
                    (('STORE_FAST', '?'),), \
                    (('!PyNumber_InPlaceAdd', \
                        ('PY_TYPE', '?', None, ('FAST', '?'), None), \
                        ('!BUILD_LIST', '?')),))):
                if v[0] == v[2] and v[1] is list:
                    new_a = []
                    for li in v[3]:
                        new_a.append(('PYAPI_CALL', ('PyList_Append', ('FAST', v[0]), li)))
                    aa[i:i+1] = new_a
                    updated = True
                    i -= 10
                    continue

        if i+5 <= len(aa) and s == ('(TRY',) and type(aa[i+1]) is list and \
           len(aa[i+1]) == 1 and aa[i+1][0][0] == '.L' and\
           aa[i+2][0] == ')(EXCEPT' and type(aa[i+3]) is list and\
           aa[i+4] == (')ENDTRY',):
            aa[i:i+5] = aa[i+1]
            updated = True
            i -= 10
            continue
        v = []
        if i+5 <= len(aa) and s == ('(TRY',) and type(aa[i+1]) is list and \
           len(aa[i+1]) == 2 and aa[i+1][0][0] == '.L' and\
           TCmp(aa[i+1][1], v, ('STORE', (('STORE_FAST', '?'),), (('CALC_CONST', '?'),))) and\
           aa[i+2][0] == ')(EXCEPT' and type(aa[i+3]) is list and\
           aa[i+4] == (')ENDTRY',):
            aa[i:i+5] = aa[i+1]
            updated = True
            i -= 10
            continue

        v = []
        if i+5 <= len(aa) and s == ('(TRY',) and type(aa[i+1]) is list and \
           len(aa[i+1]) == 1 and aa[i+1][0] == ('PASS',) and\
           aa[i+2][0] == ')(EXCEPT' and type(aa[i+3]) is list and\
           aa[i+4] == (')ENDTRY',):
            del aa[i:i+5] 
            updated = True
            i -= 10
            continue
        if i+7 <= len(aa) and s == ('(TRY',) and type(aa[i+1]) is list and \
           len(aa[i+1]) == 1 and aa[i+1][0][0] == '.L' and\
           aa[i+2][0] == ')(EXCEPT' and type(aa[i+3]) is list and\
           aa[i+4] == (')(ELSE',) and type(aa[i+5]) is list and\
           aa[i+6] == (')ENDTRY',):

            aa[i:i+7] = aa[i+5]
            updated = True
            i -= 10
            continue
        if i+7 <= len(aa) and s == ('(TRY',) and type(aa[i+1]) is list and \
           len(aa[i+1]) == 1 and aa[i+1][0] == ('PASS',) and\
           aa[i+2][0] == ')(EXCEPT' and type(aa[i+3]) is list and\
           aa[i+4] == (')(ELSE',) and type(aa[i+5]) is list and\
           aa[i+6] == (')ENDTRY',):
            aa[i:i+7] = aa[i+5]
            updated = True
            i -= 10
            continue

          
        if s == ('(TRY',):
            i1 = get_closed_pair(aa,i)
            stm = aa[i:i1+1]
            if stm[-3] == (')(FINALLY',):
                tr = stm[1]
                if len(stm) == 5:
                    aa[i:i1+1] = [('(TRY_FINALLY',), stm[1], (')(FINALLY',), stm[3], (')ENDTRY_FINALLY',)]
                    updated = True
                    i -= 10
                    continue
                if tr[0] == ('(TRY',) and get_closed_pair(stm[1],0)+1 == len(stm[1]):
                    old1 = aa[i+1]
                    new1 = stm[-2]
                    aa[i:i1+1] = [('(TRY_FINALLY',), old1, (')(FINALLY',), new1, (')ENDTRY_FINALLY',)]
                    updated = True
                    i -= 10
                    continue
                
                new1 = aa[i1-1]
                del aa[i1-2:i1-1]
                old1 = aa[i:i1-2]
                aa[i:i1-2] = [('(TRY_FINALLY',), old1, (')(FINALLY',), new1, (')ENDTRY_FINALLY',)]
                updated = True
                i -= 10
                continue
                
        if TCmp(s, v, ('STORE', (('SET_VARS', '?'),), (('!BUILD_LIST', '?'),))) and len(v[0]) == len(v[1]):
            if v[0][0][0] == 'STORE_NAME' and not v[0][0][1] in repr(v[1][1:]) and not v[0][0][1] in repr(v[0][1:]):
                s1 = [('STORE', (('STORE_NAME', v[0][0][1]),), (v[1][0],))]
                if len(v[0]) > 1:
                    s1.append( ('STORE', (('SET_VARS', v[0][1:]),), (('!BUILD_LIST', v[1][1:]),)) )
                aa[i:i+1] = s1
                updated = True
                i -= 10
                continue
        v = []    
        if TCmp(s, v, ('UNPUSH', ('CONST', '?'))):
            aa[i:i+1] = []
            updated = True
            i -= 10
            continue
        if type(s) is tuple and len(s) > 0 and s[0] == '(IF':
            if TCmp(s, v, ('(IF', ('CONST', '?'), '?')):
                if v[0] not in (True, False):
                    update_v_0_1(v)
                    aa[i] = ('(IF', ('CONST', v[0]), v[1])
                    updated = True
                    i -= 10
                    continue            
            v = []
            if TCmp(s, v, ('(IF', ('CONST', '?'))):
                if v[0] not in (True, False):
                    update_v_0_1(v)
                    aa[i] = ('(IF', ('CONST', v[0]))
                    updated = True
                    i -= 10
                    continue            
            v = []                    
            if TCmp(s, v, ('(IF', ('CONST', False), '?')) and type(aa[i+1]) is list and \
            TCmp(aa[i+2],v0, (')ENDIF',)):
                del aa[i:i+3]
                updated = True
                i -= 10
                continue
            if TCmp(s, v, ('(IF', ('CONST', True), '?')) and type(aa[i+1]) is list and \
            TCmp(aa[i+2],v0, (')ENDIF',)):
                aa[i:i+3] = aa[i+1]
                updated = True
                i -= 10
                continue
    
    
            if TCmp(s, v, ('(IF', ('CONST', False))) and type(aa[i+1]) is list and \
            TCmp(aa[i+2],v0, (')ENDIF',)):
                del aa[i:i+3]
                updated = True
                i -= 10
                continue
            if TCmp(s, v, ('(IF', ('CONST', True))) and type(aa[i+1]) is list and \
            TCmp(aa[i+2],v0, (')ENDIF',)):
                aa[i:i+3] = aa[i+1]
                updated = True
                i -= 10
                continue
    
            if TCmp(s, v, ('(IF', ('CONST', False), '?')) and type(aa[i+1]) is list and \
            TCmp(aa[i+2],v0, (')(ELSE',)) and type(aa[i+3]) is list and \
            TCmp(aa[i+4],v0, (')ENDIF',)):
                aa[i:i+5] = aa[i+3]
                updated = True
                i -= 10
                continue
            if TCmp(s, v, ('(IF', ('CONST', True), '?')) and type(aa[i+1]) is list and \
            TCmp(aa[i+2],v0, (')(ELSE',)) and type(aa[i+3]) is list and \
            TCmp(aa[i+4],v0, (')ENDIF',)):
                aa[i:i+5] = aa[i+1]
                updated = True
                i -= 10
                continue
    
            if TCmp(s, v, ('(IF', ('CONST', False))) and type(aa[i+1]) is list and \
            TCmp(aa[i+2],v0, (')(ELSE',)) and type(aa[i+3]) is list and \
            TCmp(aa[i+4],v0, (')ENDIF',)):
                aa[i:i+5] = aa[i+3]
                updated = True
                i -= 10
                continue
            if TCmp(s, v, ('(IF', ('CONST', True))) and type(aa[i+1]) is list and \
            TCmp(aa[i+2],v0, (')(ELSE',)) and type(aa[i+3]) is list and \
            TCmp(aa[i+4],v0, (')ENDIF',)):
                aa[i:i+5] = aa[i+1]
                updated = True
                i -= 10
                continue
        if TCmp(s, v, ('RETURN_VALUE', \
                         ('!PyObject_Call', \
                             ('!LOAD_BUILTIN', 'setattr'), \
                             ('!BUILD_TUPLE', ('?', '?', '?')), \
                             ('NULL',)))):
            aa[i:i+1] = [('UNPUSH', s[1]), (s[0], ('CONST', None))]
            updated = True
            i -= 10
            continue
        i += 1    
    if updated:
        if len(aa) == 0:
            return [('PASS',)]
        return aa
    return a           

def can_generate_c(co):
    if C2N(co) in no_compiled:
        return False
    return not (co.co_flags & CO_GENERATOR)
       
def to_tuple_const(v):
    try:
        return ('CONST', tuple(v[0]))
    except:
        pass
    return None

def to_const_meth_1(obj, meth, args):
    try:
        meth = operator.methodcaller(meth, *args[1])
        v_s = meth(obj[2][1][0])
        if type(v_s) is list:
            v_s = [('CONST', x) for x in v_s]
            return ('!BUILD_LIST', tuple(v_s))
        assert type(v_s) != dict
        try:
            if len(v_s) > 5000:
                pass
            else:
                return ('CONST', v_s)
        except:
            return ('CONST', v_s)
    except:
        pass
    return None
           
def to_const_meth_2(obj, meth, args):
    try:
        meth = operator.methodcaller(meth, *args[1])
        v_s = meth(obj[1])
        if type(v_s) is list:
            v_s = [('CONST', x) for x in v_s]
            return ('!BUILD_LIST', tuple(v_s))
        assert type(v_s) != dict
        try:
            if len(v_s) > 5000:
                pass
            else:
                return ('CONST', v_s)
        except:
            return ('CONST', v_s)
    except:
        pass
    return None       

def cond_expr_module(t, ret):
    this,d2 = MyImport(t.subdescr)
    return ret[2]

def if_expr_1(ret):
    try:
        if ret[0] == '(IF' and ret[1][0] == 'CONST' and ret[1][1]:
            ret = list(ret)
            ret[1] = ('CONST', True)
            return tuple(ret)
        if ret[0] == '(IF' and ret[1][0] == 'CONST' and not ret[1][1]:
            ret = list(ret)
            ret[1] = ('CONST', False)
            return tuple(ret)
    except:
        pass    
    return None
           
def calc_expr_1(op, v):
    try:
        if op == '!PyObject_Repr':
            return ('CONST', repr(v))
        elif op == '!PyObject_Str':
            return ('CONST', str(v))
        elif op == '!PyNumber_Negative':
            return ('CONST', - v)
        elif op == '!PyNumber_Positive':
            return ('CONST', + v)
        elif op == '!PyNumber_Absolute':
            return ('CONST', abs(v))
        elif op == '!PyNumber_Invert':
            return ('CONST', ~ v)
        elif op == '!PyObject_Str':
            return ('CONST', str(v))
        elif op in ('!ORD_BUILTIN', ):
            return ('CONST', ord(v))
        elif op in ('!CHR_BUILTIN', ):
            return ('CONST', chr(v))
        elif op == '!1NOT':
            return ('CONST', not v)
        elif op in len_family:
            return ('CONST', len(v))
        elif op == '!PY_SSIZE_T':
            ret = ('CONST', v)
        elif op == '!PyObject_Type':
            if v is not None:
                ret = ('CONST', type(v))
    except:
        pass    
    return None

def calc_pow_1(ret):
    try:
        return ('CONST', pow(ret[1][1],ret[2][1]))
    except:
        pass    
    return None
           
def calc_expr_2(op, v1, v2, ret):
    try:
        if op == '!PyNumber_Multiply':
            v_2 = ('CONST', v1 * v2)
            try:
                if len(v_2[1]) > 5000:
                    pass
                else:
                    return v_2
            except:
                return v_2               
        elif op == '!PyNumber_Divide':
            if v2 != 0:
                return ('CONST', v1 / v2)
            else:
                return ('!?Raise', ('BUILTIN', 'ZeroDivisionError'), ('CONST', "division by 0"))
        elif op == '!PyNumber_FloorDivide':
            if v2 != 0:
                return ('CONST', v1 // v2)
            else:
                return ('!?Raise', ('BUILTIN', 'ZeroDivisionError'), ('CONST', "division by 0"))
        elif op == '!PyNumber_Remainder':
            if type(v1) is int and v2 != 0:
                return ('CONST', v1 % v2)
            if type(v1) is float and v2 != 0:
                return ('CONST', v1 % v2)
            if type(v1) is str and len(v1 % v2) <= 255:
                return ('CONST', v1 % v2)
            if type(v1) is int and v2 == 0:
                return ('!?Raise', ('BUILTIN', 'ZeroDivisionError'), ('CONST', "division by 0"))
            if type(v1) is float and v2 == 0:
                return ('!?Raise', ('BUILTIN', 'ZeroDivisionError'), ('CONST', "division by 0"))
        elif op == '!STR_CONCAT':
            ret = ('!STR_CONCAT', ('CONST', v1 + v2)) + ret[3:]
            if len(ret) == 2:
                return ret[1]
            else:
                return repl(ret)
        elif op == '!PyNumber_Add':
            return ('CONST', v1 + v2)
        elif op == '!PyNumber_InPlaceAdd':
            return ('CONST', v1 + v2)
        elif op == '!PyNumber_Subtract':
            return ('CONST', v1 - v2)
        elif op == '!PyNumber_Lshift':
            return ('CONST', v1 << v2)
        elif op == '!PyNumber_Rshift':
            return ('CONST', v1 >> v2)
        elif op == '!PyNumber_Or':
            return ('CONST', v1 | v2)
        elif op == '!PyNumber_Xor':
            return ('CONST', v1 ^ v2)
        elif op == '!PyNumber_And':
            return ('CONST', v1 & v2)
        elif op == '!OR_JUMP':
            return ('CONST', v1 or v2)
        elif op == '!AND_JUMP':
            return ('CONST', v1 and v2)
        elif op == '!PySequence_Repeat':
            ret2 = ('CONST', v2 * v1)
            if len(ret2[1]) > 5000:
                return ret 
                
            ## if type(ret2[1]) is tuple and len(ret2[1]) > 10000:
                ## return ret 
            return ret2
        elif op == '!PyString_Format':
            return ('CONST', v1 % v2)
        elif op in ('!PySequence_Contains(', '!PySequence_Contains'):
            return ('CONST', v2 in v1)
        elif op == '!PyObject_GetAttr' and v2 == 'join' and type(v1) is str:
            pass # _PyString_Join    
        elif op in ('!BINARY_SUBSCR_Int', '!from_ceval_BINARY_SUBSCR'):
            return ('CONST', v1[v2])
        elif op in ('!ORD_BUILTIN', ):
            return ('CONST', ord(v1))
        elif op in ('!CHR_BUILTIN', ):
            return ('CONST', chr(v1))
        elif op == '!_EQ_':
            return ('CONST', v1 == v2)
        elif op == '!_NEQ_':
            return ('CONST', v1 != v2)
        else:
            pass #Debug('rre Constant op2 unhandled', ret)
    except:
        pass
    return None

def call_calc_const(func, tupl, ret):
    co = N2C(func)
    if subroutine_can_be_direct(func, len(tupl[1])):
        _3(func, 'ArgCallCalculatedDef', tupl)
        return ('!CALL_CALC_CONST', func, tupl)
    elif co.co_flags & 0x28 == 0 and co.co_flags == 0x43 and \
         len(co.co_cellvars) == 0 and len(co.co_freevars) == 0 and co.co_argcount == len(tupl[1]):
        return ('!CALL_CALC_CONST_INDIRECT', func, tupl)
    elif co.co_flags & CO_GENERATOR: # interpreted generator
        return ret
    else:
        Debug('Unfortunelly ', ret, hex(co.co_flags))
        return ret
##        return ('!CALL_CALC_CONST_INDIRECT', func, tupl)
           
def repl(ret):
    v = []

    if type(ret) is tuple and len(ret) >= 1:
        r0 = ret[0]
        if r0 == '!PySequence_Tuple' and TypeExpr(ret[1]) == Kl_Tuple:
            ret = ret[1]
        ## if ret == ('!LOAD_GLOBAL', '__file__') or ret ==  ('!LOAD_NAME', '__file__'):
            ## ret = ('CONST', current_co.co_filename)
        if r0 == '!IMPORT_NAME':
            CheckExistListImport(dotted_name_to_first_name(ret[1]))   
        if r0 == 'IMPORT_FROM_AS':
            CheckExistListImport(ret[1], ret[3][1], ret[2][1])   
        if r0 == '!PyObject_Repr':
            if IsInt(TypeExpr(ret[1])):
                return ('!_PyInt_Format', ret[1], 10, 0)            
        if len(ret) == 2 and r0 == 'CONST' and type(ret[1]) == type:
            if ret[1] in d_built_inv:
                ret = ('!LOAD_BUILTIN', d_built_inv[ret[1]])
            else:
                Fatal ('???', ret, type(ret[1]))    

        if direct_call:
            v = []
            if r0 == '!CLASS_CALC_CONST' and can_generate_c(current_co):
                if TCmp(ret, v, ('!CLASS_CALC_CONST', '?', ('!BUILD_TUPLE', '?'))):
                    if Is3(v[0], ('Method', '__init__')):
                        if subroutine_can_be_direct(Val3(v[0], ('Method', '__init__')),\
                                                len(v[1]) +1):
                            slf = ('PY_TYPE', T_OLD_CL_INST, v[0], ('PSEVDO', 'self'), None)
                            _3(Val3(v[0], ('Method', '__init__')), 'ArgCallCalculatedDef', ('!BUILD_TUPLE', (slf,) +v[1]))
                            ret = ('!CLASS_CALC_CONST_DIRECT', v[0], \
                                Val3(v[0], ('Method', '__init__')), ('!BUILD_TUPLE', v[1]))
                elif TCmp(ret, v, ('!CLASS_CALC_CONST', '?', ('CONST', '?'))):
                    if Is3(v[0], ('Method', '__init__')):
                        if subroutine_can_be_direct(Val3(v[0], ('Method', '__init__')), len(v[1])+1):
                            slf = ('PY_TYPE', T_OLD_CL_INST, v[0], ('PSEVDO', 'self'), None)
                            tu = tuple([('CONST', x) for x in v[1]])
                            _3(Val3(v[0], ('Method', '__init__')), 'ArgCallCalculatedDef', ('!BUILD_TUPLE', (slf,) +tu))
                            ret = ('!CLASS_CALC_CONST_DIRECT', v[0], \
                                Val3(v[0], ('Method', '__init__')), ('CONST', v[1]))
            ## elif r0 == '!CLASS_CALC_CONST_NEW' and can_generate_c(current_co):
                ## if TCmp(ret, v, ('!CLASS_CALC_CONST_NEW', '?', ('!BUILD_TUPLE', '?'))):
                    ## if Is3(v[0], ('Method', '__init__')):
                        ## if subroutine_can_be_direct(Val3(v[0], ('Method', '__init__')),\
                                                    ## len(v[1]) +1) and len(v[1]) > 0:
                            ## slf = ('PY_TYPE', T_NEW_CL_INST, v[0], ('PSEVDO', 'self'), None)
                            ## _3(Val3(v[0], ('Method', '__init__')), 'ArgCallCalculatedDef', ('!BUILD_TUPLE', (slf,) +v[1]))
                            ## ret = ('!CLASS_CALC_CONST_NEW_DIRECT', v[0], \
                                ## Val3(v[0], ('Method', '__init__')), ('!BUILD_TUPLE', v[1]))
                ## elif TCmp(ret, v, ('!CLASS_CALC_CONST_NEW', '?', ('CONST', '?'))):
                    ## if Is3(v[0], ('Method', '__init__')):
                        ## if subroutine_can_be_direct(Val3(v[0], ('Method', '__init__')), len(v[1])+1) and len(v[1]) > 0:
                            ## slf = ('PY_TYPE', T_NEW_CL_INST, v[0], ('PSEVDO', 'self'), None)
                            ## tu = tuple([('CONST', x) for x in v[1]])
                            ## _3(Val3(v[0], ('Method', '__init__')), 'ArgCallCalculatedDef', ('!BUILD_TUPLE', (slf,) +tu))
                            ## ret = ('!CLASS_CALC_CONST_NEW_DIRECT', v[0], \
                                ## Val3(v[0], ('Method', '__init__')), ('CONST', v[1]))
                    



        if r0 == '!PyObject_Call':
            _v = []
            if TCmp(ret, _v, ('!PyObject_Call', ('!LOAD_BUILTIN', '?'), '?', ('NULL',))):
                tag,args = _v
                v = []    
                if tag == 'apply' and TCmp(args, v, ('!BUILD_TUPLE', ('?', '?'))):
                    return ('!PyObject_Call', v[0] , v[1], ('NULL',))
                elif tag == 'apply' and TCmp(args, v, ('!BUILD_TUPLE', ('?', '?', '?'))):
                    return ('!PyObject_Call', v[0] , v[1], v[2])
                elif tag == 'getattr' and TCmp(args, v, ('!BUILD_TUPLE', ('?', '?'))):
                    return ('!PyObject_GetAttr', v[0], v[1])
                elif tag == 'getattr' and TCmp(args, v, ('!BUILD_TUPLE', ('?', '?', '?'))):
                    return ('!PyObject_GetAttr3', v[0], v[1], v[2])
                elif tag == 'dict' and args == ('CONST', ()):
                    return ('!PyDict_New', )
                elif tag == 'slice' and TCmp(args, v, ('!BUILD_TUPLE', '?')):
                    if len(v[0]) == 3:                  
                        return ('!PySlice_New', v[0][0], v[0][1], v[0][2])
                    elif len(v[0]) == 2:                  
                        return ('!PySlice_New', v[0][0], v[0][1], 'NULL')
                    elif len(v[0]) == 1:                  
                        return ('!PySlice_New', 'NULL', v[0][0], 'NULL')
                    else:
                        Fatal('Strange arg Slice', ret)
                elif tag == 'slice' and TCmp(args, v, ('CONST', '?')):
                    if len(v[0]) == 3:                  
                        return ('!PySlice_New', ('CONST', v[0][0]), ('CONST', v[0][1]), ('CONST', v[0][2]))
                    elif len(v[0]) == 2:                  
                        return ('!PySlice_New', ('CONST', v[0][0]), ('CONST', v[0][1]), 'NULL')
                    elif len(v[0]) == 1:                  
                        return ('!PySlice_New', 'NULL', ('CONST', v[0][0]), 'NULL')
                    else:
                        Fatal('Strange arg Slice', ret)
                elif tag == 'tuple' and TCmp(args, v, ('CONST', '?')):
                    ret_tupl = to_tuple_const(v)
                    if ret_tupl is not None:
                        return ret_tupl
                elif tag == 'callable':
                    if args[0] == '!BUILD_TUPLE' and TypeExpr(args[1][0]) is not None:
                        Debug('callable, ', TypeExpr(args[1][0]))
                        Debug(args)
                elif tag == 'list' and args == ('CONST', ()):  
                    return ('!BUILD_LIST', ())    
            _v = []
            if direct_call and can_generate_c(current_co):
                if TCmp(ret, v, \
                    ('!PyObject_Call',  
                        ('!PyObject_GetAttr', '?', ('CONST', '?')), ('!BUILD_TUPLE', '?'), ('NULL',))):
                    t = TypeExpr(v[0])
                    if t is not None:
                        classmeth = Is3(t.subdescr, ('ClassMethod', v[1]))
                        staticmeth = Is3(t.subdescr, ('StaticMethod', v[1]))
                        ismeth = Is3(t.subdescr, ('Method', v[1]))
                        codemethnm = Val3(t.subdescr, ('Method', v[1]))
                        isoldclass = Is3(t.subdescr, 'CalcConstOldClass')
                        isnewclass = Is3(t.subdescr, 'CalcConstNewClass')
                        if t.is_old_class_inst() and isoldclass and ismeth and not isnewclass:
                            if classmeth:
                                Debug('No direct call of class method', ret)
                            elif staticmeth:
                                tupl = ('!BUILD_TUPLE', v[2])
                                return call_calc_const(codemethnm, tupl, ret)
                            else:                        
                                tupl = ('!BUILD_TUPLE', (v[0],) + v[2])
                                return call_calc_const(codemethnm, tupl, ret)
                        elif t.is_old_class_typ() and isoldclass and ismeth and not isnewclass:
                            if classmeth:
                                tupl = ('!BUILD_TUPLE', (v[0],) + v[2])
                                return call_calc_const(codemethnm, tupl, ret)
                            elif staticmeth:
                                tupl = ('!BUILD_TUPLE', v[2])
                                return call_calc_const(codemethnm, tupl, ret)
                            else:                        
                                tupl = ('!BUILD_TUPLE', v[2])
                                return call_calc_const(codemethnm, tupl, ret)
        
                        elif t.is_new_class_inst() and isnewclass and ismeth and not isoldclass:
                            if classmeth:
                                Debug('No direct call of class method', ret)
                            elif staticmeth:
                                tupl = ('!BUILD_TUPLE', v[2])
                                return call_calc_const(codemethnm, tupl, ret)
                            else:                        
                                tupl = ('!BUILD_TUPLE', (v[0],) + v[2])
                                return call_calc_const(codemethnm, tupl, ret)
                        elif t.is_new_class_typ() and isnewclass and ismeth and not isoldclass:
                            if classmeth:
                                tupl = ('!BUILD_TUPLE', (v[0],) + v[2])
                                return call_calc_const(codemethnm, tupl, ret)
                            elif staticmeth:
                                tupl = ('!BUILD_TUPLE', v[2])
                                return call_calc_const(codemethnm, tupl, ret)
                            else:                        
                                tupl = ('!BUILD_TUPLE', v[2])
                                return call_calc_const(codemethnm, tupl, ret)
    
                if TCmp(ret, v, \
                    ('!PyObject_Call',  
                        ('!PyObject_GetAttr', '?', ('CONST', '?')), ('CONST', '?'), ('NULL',))):
                    t = TypeExpr(v[0])
                    if t is not None:
                        classmeth = Is3(t.subdescr, ('ClassMethod', v[1]))
                        staticmeth = Is3(t.subdescr, ('StaticMethod', v[1]))
                        ismeth = Is3(t.subdescr, ('Method', v[1]))
                        codemethnm = Val3(t.subdescr, ('Method', v[1]))
                        isoldclass = Is3(t.subdescr, 'CalcConstOldClass')
                        isnewclass = Is3(t.subdescr, 'CalcConstNewClass')                    
                        if t.is_old_class_inst() and isoldclass and ismeth and not isnewclass:
                            if classmeth:
                                Debug('No direct call of class method', ret)
                            elif staticmeth:
                                tupl = ('CONST', v[2])
                                return call_calc_const(codemethnm, tupl, ret)
                            else:    
                                v2 = tuple([('CONST', x) for x in v[2]])
                                tupl = ('!BUILD_TUPLE', (v[0],) + v2)
                                return call_calc_const(codemethnm, tupl, ret)
        
                        elif t.is_old_class_typ() and isoldclass and ismeth and not isnewclass:
                            if classmeth:
                                Debug('No direct call of class method', ret)
                            elif staticmeth:
                                tupl = ('CONST', v[2])
                                return call_calc_const(codemethnm, tupl, ret)
                            else:    
                                v2 = tuple([('CONST', x) for x in v[2]])
                                tupl = ('CONST', v2)
                                return call_calc_const(codemethnm, tupl, ret)
                        
                        elif t.is_new_class_inst() and isnewclass and ismeth and not isoldclass:
                            if classmeth:
                                Debug('No direct call of class method', ret)
                            elif staticmeth:
                                tupl = ('CONST', v[2])
                                return call_calc_const(codemethnm, tupl, ret)
                            else:    
                                v2 = tuple([('CONST', x) for x in v[2]])
                                tupl = ('!BUILD_TUPLE', (v[0],) + v2)
                                return call_calc_const(codemethnm, tupl, ret)
        
                        elif t.is_new_class_typ() and isnewclass and ismeth and not isoldclass:
                            if classmeth:
                                tupl = ('!BUILD_TUPLE', (v[0],) + v[2])
                                return call_calc_const(codemethnm, tupl, ret) 
                            elif staticmeth:
                                tupl = ('CONST', v[2])
                                return call_calc_const(codemethnm, tupl, ret)
                            else:    
                                v2 = tuple([('CONST', x) for x in v[2]])
                                tupl = ('CONST', v2)
                                return call_calc_const(codemethnm, tupl, ret)
                        
            _v = []
            v = []
            if TCmp(ret, _v, ('!PyObject_Call', ('!PyObject_GetAttr', '?', ('CONST', '?')), '?', ('NULL',))):
                obj, meth, args = _v
                t = TypeExpr(obj)
                if t == Kl_List:
                    if meth == 'pop':
                        if TCmp(args, v, ('CONST', ('?',))):
                            return ('!_PyList_Pop', obj, ('CONST', v[0]))
                        elif TCmp(args, v, ('CONST', ())):
                            return ('!_PyList_Pop', obj)
                        elif TCmp(args, v, ('!BUILD_TUPLE', ('?',))):
                            return ('!_PyList_Pop', obj, v[0])
                    elif meth == 'len' and args == ('CONST', ()) :
                        return ('!PY_SSIZE_T', ('!PyList_GET_SIZE', obj))
                    elif meth == 'extend':
                        v2 = []
                        if TCmp(args, v2, ('!BUILD_TUPLE', ('?',))):
                            return ('!_PyList_Extend', obj, v2[0])
                elif t == Kl_String:
                    if meth == 'startswith' and TCmp(args, v, ('CONST', ('?',))) and\
                        type(v[0]) is str:
                        return ('!_PyString_StartSwith', obj, v[0])
                    if meth == 'endswith' and TCmp(args, v, ('CONST', ('?',))) and\
                        type(v[0]) is str:
                        return ('!_PyString_EndSwith', obj, v[0])
                elif t == Kl_Dict:
                    if meth == 'copy':
                        if TCmp(args, v, ('CONST', ())):
                            return ('!PyDict_Copy', obj)
                    elif meth == 'get':
                        if TCmp(args, v, ('!BUILD_TUPLE', ('?','?'))):
                            return ('!_PyDict_Get', obj, v[0], v[1])
                        elif TCmp(args, v, ('!BUILD_TUPLE', ('?',))):
                            return ('!_PyDict_Get', obj, v[0], ('CONST', None))
                        elif TCmp(args, v, ('CONST', ('?','?'))):
                            return ('!_PyDict_Get', obj, ('CONST',v[0]), ('CONST', v[1]))
                        elif TCmp(args, v, ('CONST', ('?',))):
                            return ('!_PyDict_Get', obj, ('CONST',v[0]), ('CONST', None))
                    elif meth == 'has_key':
                        if TCmp(args, v, ('!BUILD_TUPLE', ('?',))):
                            return ('!BOOLEAN', ('!PyDict_Contains', obj, v[0]))
                        elif TCmp(args, v, ('CONST', ('?',))):
                            return ('!BOOLEAN', ('!PyDict_Contains', obj, ('CONST', v[0])))
                    elif meth == 'keys' and args == ('CONST', ()) :
                        return ('!PyDict_Keys', obj)
                    elif meth == 'values' and args == ('CONST', ()) :
                        return ('!PyDict_Values', obj)
                    elif meth == 'items' and args == ('CONST', ()) :
                        return ('!PyDict_Items', obj)
                    elif meth == 'len' and args == ('CONST', ()) :
                        return ('!PY_SSIZE_T', ('!PyDict_Size', obj))
# TypeError: 'int' object is not iterable !!!!!!!!
                if len(obj) == 4 and obj[-1] == 'NULL' and obj[1][0] == '&' and \
                        obj[0].endswith('.tp_new') and obj[0][0] == '!' and \
                        obj[0][1:-7] == obj[1][1:] and obj[2][0] == 'CONST' and\
                        len(obj[2][1]) == 1:
                    t1 = TypeExpr(obj)
                    t2 = TypeExpr(('CONST', obj[2][1][0]))
                    if t1 == t2 and t1 is not None:
                            if args[0] == 'CONST':
                                ret_co = to_const_meth_1(obj, meth, args)
                                if ret_co is not None:
                                    return ret_co
                if obj[0] == 'CONST':
                    if args[0] == 'CONST':
                        ret_co = to_const_meth_2(obj, meth, args)
                        if ret_co is not None:
                            return ret_co
                    else:
                        Debug('Call const meth', obj, meth, args)
    
    
        if ret == ('!BOOLEAN', ('CONST', True)):
            return ('CONST', True)
        if ret == ('!BOOLEAN', ('CONST', False)):
            return ('CONST', False)
    
        v = []
        if r0 == '!COND_EXPR' and TCmp(ret,v, ('!COND_EXPR', ('CALC_CONST', '?'), '?', '?')):
            t = TypeExpr(ret[1])
            if t is not None and t.descr is types.ModuleType and t.subdescr is not None:
                ret_modl = cond_expr_module(t, ret)
                if ret_modl is not None:
                    return ret_modl
    
        if r0 == '!PySequence_Tuple' and \
                TCmp(ret, v, ('!PySequence_Tuple', '?')) and \
                TypeExpr(v[0]) == Kl_List:
            return ('!PyList_AsTuple', v[0])
        
        if r0 == '!PySequence_Contains(' and \
                TCmp(ret, v, ('!PySequence_Contains(', '?', '?')):
            t =  TypeExpr(v[0])
            if t == Kl_Dict:
                return ('!PyDict_Contains', v[0], v[1])
            elif t == Kl_Set:
                return ('!PySet_Contains', v[0], v[1])
    
        if r0 == 'PY_TYPE':
            if TCmp(ret, v, ('PY_TYPE', '?', None, ('!PyNumber_Add', '?', '?'), '?')) and v[0] is int:
                n1 = v[1]
                n2 = v[2]
                t = v[3]
                if n1[0] not in ('PY_TYPE', 'CONST'):
                    n1 = ('PY_TYPE', int, None, n1, t)
                if n2[0] not in ('PY_TYPE', 'CONST'):
                    n2 = ('PY_TYPE', int, None, n1, t)
                return ('PY_TYPE', int, None, ('!PyNumber_Add', n1, n2), t)
            if TCmp(ret, v, ('PY_TYPE', '?', None, ('!PyNumber_Subtract', '?', '?'), '?')) and v[0] is int:
                n1 = v[1]
                n2 = v[2]
                t = v[3]
                if n1[0] not in ('PY_TYPE', 'CONST'):
                    n1 = ('PY_TYPE', int, None, n1, t)
                if n2[0] not in ('PY_TYPE', 'CONST'):
                    n2 = ('PY_TYPE', int, None, n1, t)
                return ('PY_TYPE', int, None, ('!PyNumber_Subtract', n1, n2), t)
            if TCmp(ret, v, ('PY_TYPE', '?', None, ('!PyNumber_Negative', '?'), '?')) and v[0] is int:
                n1 = v[1]
                t = v[2]
                if n1[0] not in ('PY_TYPE', 'CONST'):
                    n1 = ('PY_TYPE', int, None, n1, t)
                return ('PY_TYPE', int, None, ('!PyNumber_Negative', n1), t)
        v = []    
        if len(ret) >= 2 and r0 == '(IF':
            ret_n = if_expr_1(ret)
            if ret_n is not None:
                return ret_n
        v = []
        if r0 == '!BINARY_SUBSCR_Int' and TCmp(ret, v, \
            ('!BINARY_SUBSCR_Int', ('!BUILD_LIST', '?'), ('CONST', int))):
                l = len(v[0])
                pos = v[1]
                if pos < 0:
                    pos = pos + l
                if pos < l:    
                    return v[0][v[1]]
    
        v = []    
        if r0 == '!c_PyCmp_EQ_String' and \
                TCmp(ret, v, ('!c_PyCmp_EQ_String', ('CONST', '?'), ('CONST', '?'))):
            return ('CONST', v[0] == v[1])    
        if r0 == '!c_PyCmp_NE_String' and \
                TCmp(ret, v, ('!c_PyCmp_NE_String', ('CONST', '?'), ('CONST', '?'))):
            return ('CONST', v[0] != v[1])    
        v = []    
        if len(ret) == 2 and type(r0) is str and \
            type(ret[1]) is tuple and len(ret[1]) >= 1 and ret[1][0] == 'CONST':
            op, v = r0, ret[1][1]
            ret_ret = calc_expr_1(op, v)
            if ret_ret is not None:
                return ret_ret
        v = []    
        if len(ret) == 4 and type(r0) is str and \
            type(ret[1]) is tuple and len(ret[1]) >= 1 and ret[1][0] == 'CONST' and \
            type(ret[2]) is tuple and len(ret[2]) >= 1 and ret[2][0] == 'CONST' and\
            ret[3] == 'Py_None':
            if r0 == '!PyNumber_Power':
                ret_ret = calc_pow_1(ret)
                if ret_ret is not None:
                    return ret_ret
        v = []    
        if len(ret) == 3 and    type(r0) is str and \
            type(ret[1]) is tuple and len(ret[1]) >= 1 and ret[1][0] == 'CONST' and \
            type(ret[2]) is tuple and len(ret[2]) >= 1 and ret[2][0] == 'CONST':
            op, v1, v2 = r0, ret[1][1], ret[2][1]
            ret_ret = calc_expr_2(op, v1, v2, ret)
            if ret_ret is not None:
                return ret_ret
        if r0 == '!PyNumber_Divide' and \
                TCmp(ret, v, ('!PyNumber_Divide', '?', ('CONST', 0))):
            return ('!?Raise', ('BUILTIN', 'ZeroDivisionError'), ('CONST', "division by 0"), v[0])    
        v = []
        if r0 == '!PySequence_Repeat' and \
                TCmp(ret, v, ('!PySequence_Repeat', \
                              ('!BUILD_LIST', (('CONST', '?'),)), \
                              ('CONST', int))) and v[1] >= 0 and v[1] < 256:
            return ('!BUILD_LIST', (('CONST', v[0]),) * v[1]) 
        v = []
        if r0 == 'UNPUSH' and TCmp(ret, v, ('UNPUSH', ('!PyObject_Call', 
                                ('?', 'setattr'),
                                ('!BUILD_TUPLE', ('?', '?', '?')), ('NULL',)))):
            arg1,arg2, arg3 = v[1], v[2], v[3]   
            if v[0] == '!LOAD_BUILTIN':
                return ('STORE', (('PyObject_SetAttr', arg1, arg2),), (arg3,))
            elif v[0] in ('!LOAD_GLOBAL', '!LOAD_NAME', '!PyDict_GetItem(glob,'):
                return ('STORE', (('?PyObject_SetAttr', arg1, arg2, (v[0], 'setattr')),), (arg3,))
            else:
                return ret 
        if r0 == '!PySequence_GetSlice' and \
                TCmp(ret, v, ('!PySequence_GetSlice', ('CONST', '?'), \
                              int, 'PY_SSIZE_T_MAX')):
            return ('CONST', v[0][v[1]:])
        if r0 == '!AND_JUMPED_STACKED' and \
                TCmp(ret, v, ('!AND_JUMPED_STACKED', ('!BOOLEAN', '?' ), '?' )):
            return ('!COND_EXPR', ('!BOOLEAN', v[0]), v[1], ('CONST', False))
        if r0 == '!OR_JUMPED_STACKED' and \
                TCmp(ret, v, ('!OR_JUMPED_STACKED', ('!BOOLEAN', '?' ), '?' )):
            return ('!COND_EXPR', ('!BOOLEAN', v[0]), ('CONST', True), v[1])
        v = []
            
        if r0 == '!from_ceval_BINARY_SUBSCR' and \
                TCmp(ret, v, ('!from_ceval_BINARY_SUBSCR', '?', \
                            ('!PyNumber_Add', '?', ('CONST', int)))):
            return ('!_c_BINARY_SUBSCR_ADDED_INT', v[0], v[1], v[2], ('CONST', v[2]))                
                        
        if r0 == '!BINARY_SUBSCR_Int' and \
                TCmp(ret, v, ('!BINARY_SUBSCR_Int', \
                            ('!BINARY_SUBSCR_Int', '?', ('CONST', int)), ('CONST', int))):
            return ('!c_BINARY_SUBSCR_SUBSCR_Int_Int', v[0], v[1], ('CONST', v[1]), v[2], ('CONST', v[2]))                
                
    
        if r0 == '!PyNumber_InPlaceAdd' and \
                TCmp(ret, v, ('!PyNumber_InPlaceAdd', '?', '?')):
            if TypeExpr(v[0]) == TypeExpr(v[1]) == Kl_String:
                if v[0][0] == v[1][0] == 'CONST':
                    return ('CONST', v[0][1] + v[1][1])
                return ('!STR_CONCAT', v[0], v[1])
        v = []
        if r0 == '!PyNumber_Add':                
            if TCmp(ret, v, ('!PyNumber_Add', ('CONST', str), ('!STR_CONCAT', '*'))):
                return ('!STR_CONCAT', ('CONST', v[0])) + v[1]
            if TCmp(ret, v, ('!PyNumber_Add', ('CONST', str), '?')):
                return ('!STR_CONCAT', ('CONST', v[0]), v[1])
            if TCmp(ret, v, ('!PyNumber_Add', ('!STR_CONCAT', '*'), ('CONST', str))):
                return ('!STR_CONCAT',) + v[0] + (('CONST', v[1]),)
            if TCmp(ret, v, ('!PyNumber_Add', '?', ('CONST', str))):
                return ('!STR_CONCAT', v[0], ('CONST', v[1]))
            if TCmp(ret, v, ('!PyNumber_Add', ('!STR_CONCAT', '*'), ('!STR_CONCAT', '*'))):
                return ('!STR_CONCAT',) +  v[0] + v[1]
            if TCmp(ret, v, ('!PyNumber_Add', ('!STR_CONCAT', '*'), '?')):
                return ('!STR_CONCAT',) +  v[0] + (v[1],)
            if TCmp(ret, v, ('!PyNumber_Add', '?', ('!STR_CONCAT', '*'))):
                return ('!STR_CONCAT', v[0]) + v[1]
    
        if r0 == '!PyNumber_Multiply':                
            if TCmp(ret, v, ('!PyNumber_Multiply', ('CONST', str), '?')):
                return ('!PySequence_Repeat', ('CONST', v[0]), v[1])
            if TCmp(ret, v, ('!PyNumber_Multiply', ('CONST', unicode), '?')):
                return ('!PySequence_Repeat', ('CONST', v[0]), v[1])
            if TCmp(ret, v, ('!PyNumber_Multiply', ('CONST', list), '?')):
                return ('!PySequence_Repeat', ('CONST', v[0]), v[1])
            if TCmp(ret, v, ('!PyNumber_Multiply', ('CONST', tuple), '?')):
                return ('!PySequence_Repeat', ('CONST', v[0]), v[1])
            if TCmp(ret, v, ('!PyNumber_Multiply', ('!STR_CONCAT', '*'), '?')):
                return ('!PySequence_Repeat', ('!STR_CONCAT',) + v[0], v[1])
            if TCmp(ret, v, ('!PyNumber_Multiply', ('!UNICODE_CONCAT', '*'), '?')):
                return ('!PySequence_Repeat', ('!UNICODE_CONCAT',) + v[0], v[1])
            if TCmp(ret, v, ('!PyNumber_Multiply', ('!BUILD_LIST', '*'), '?')):
                return ('!PySequence_Repeat', ('!BUILD_LIST',) + v[0], v[1])
            if TCmp(ret, v, ('!PyNumber_Multiply', ('!BUILD_LIST', '*'), '?')):
                return ('!PySequence_Repeat', ('!BUILD_TUPLE',) + v[0], v[1])
        if len(ret) == 2 and r0 == '!BUILD_TUPLE':
            isconst = True
            for i,x in enumerate(ret[1]):
                if x[0] != 'CONST':
                    isconst = False
            if isconst:
                return ('CONST', tuple([x[1] for x in ret[1]]))
        if TCmp(ret, v, ('!PyObject_RichCompare(', '?', '?', c_2_op_op)) or \
                TCmp(ret, v, ('!PyObject_RichCompare', '?', '?', c_2_op_op)):
            n = _process_compare_op(c_2_op_op[v[2]], v[0],v[1])
            if n is not None:
                return n
                
        v = []       
        if r0 == '!_PyEval_BuildClass':
            if TCmp(ret, v, ('!_PyEval_BuildClass', \
                    ('!PyObject_Call', \
                        ('!MK_CLOSURE', '?', '?', '?'), \
                        '?', '?'), '?', ('CONST', '?'))): 
                _3(v[0], 'IsClassCreator', v[6])   
            elif TCmp(ret, v, ('!_PyEval_BuildClass', \
                    ('!PyObject_Call', \
                        ('!MK_FUNK', '?', '?'), '?', '?'), \
                    '?', ('CONST', '?'))): 
                _3(v[0], 'IsClassCreator', v[5])   
                
                
        v0 = []       
        if r0 == 'STORE':
            if TCmp(ret, v0, ('STORE', (('STORE_CALC_CONST', ('?', '?')),), ('?',))) and \
                    v0[0] in ('STORE_NAME', 'STORE_GLOBAL') and v0[1] in all_calc_const:
                v = [(v0[1], '', all_calc_const[v0[1]]), v0[2]]
                if v[1] == ('!MK_FUNK', v[0][0], ('CONST', ())):
                    val_direct_code[v[0][0]] = v[1]
                    direct_code[v[0][0]] = v[1][1]
                elif v[0][2][0] == '!MK_FUNK' and v[0][2][2] != v[0][0] and v[0][2][2] == ('CONST', ()):
                    val_direct_code[v[0][0]] = v[0][2]
                    direct_code[v[0][0]] = v[0][2][1]
                elif v[1][0] == '!MK_FUNK' and v[1][1] == v[0][0] and \
                    v[1][2][0] == 'CONST' and len(v[1][2][1]) > 0:
                    val_direct_code[v[0][0]] = v[1]
                    direct_code[v[0][0]] = v[1][1]
                    default_args[v[0][0]] = v[1][2]
                elif v[1][0] == '!_PyEval_BuildClass':
                    v1 = v[1]
                    v1_1 = []
                    if TCmp(v1, v1_1, ('!_PyEval_BuildClass',\
                                        ('!PyObject_Call',\
                                            ('!MK_FUNK', v[0][0], ('CONST', ())),\
                                            ('CONST', ()), ('NULL',)),\
                                        '?', ('CONST', v[0][0]))):
                        if v1_1[0] == ('CONST', ()):     
                            if not Is3(v[0][0], 'HaveMetaClass'): 
                                _3(v[0][0], 'CalcConstOldClass', v[1])
                    else:
                        Fatal('calcConst???Class', v1)   
            v0 = []
            if TCmp(ret, v0, ('STORE', (('?', '?'),), ('?',))) and \
                    v0[0] in ('STORE_NAME', 'STORE_GLOBAL') and v0[1] in all_calc_const:
                v = [(v0[1], '', all_calc_const[v0[1]]), v0[2]]
                if v[1] == ('!MK_FUNK', v[0][0], ('CONST', ())):
                    val_direct_code[v[0][0]] = v[1]
                    direct_code[v[0][0]] = v[1][1]
                elif v[0][2][0] == '!MK_FUNK' and v[0][2][2] != v[0][0] and v[0][2][2] == ('CONST', ()):
                    val_direct_code[v[0][0]] = v[0][2]
                    direct_code[v[0][0]] = v[0][2][1]
                elif v[1][0] == '!MK_FUNK' and v[1][1] == v[0][0] and \
                    v[1][2][0] == 'CONST' and len(v[1][2][1]) > 0:
                    val_direct_code[v[0][0]] = v[1]
                    direct_code[v[0][0]] = v[1][1]
                    default_args[v[0][0]] = v[1][2]
                elif v[1][0] == '!_PyEval_BuildClass':
                    v1 = v[1]
                    v1_1 = []
                    if TCmp(v1, v1_1, ('!_PyEval_BuildClass',\
                                        ('!PyObject_Call',\
                                            ('!MK_FUNK', v[0][0], ('CONST', ())),\
                                            ('CONST', ()), ('NULL',)),\
                                        '?', ('CONST', v[0][0]))):  
                        vv = []                    
                        if v1_1[0] == ('CONST', ()):                    
                            if not Is3(v[0][0], 'HaveMetaClass'): 
                                _3(v[0][0], 'CalcConstOldClass', v[1])
                        elif v1_1[0][0] ==  '!BUILD_TUPLE':
                            f = v1_1[0][1]
                            for der in f:
                                if der[0] == '!LOAD_BUILTIN':
                                    _3(v[0][0], 'CalcConstNewClass', v[1])
                                    _3(v[0][0], 'Derived', der)
                                elif der[0] in ('!LOAD_NAME', '!LOAD_GLOBAL'):    
                                    if Is3(der[1], 'CalcConstOldClass'):
                                        if not Is3(v[0][0], 'HaveMetaClass'): 
                                            _3(v[0][0], 'CalcConstOldClass', v[1])
                                        _3(v[0][0], 'Derived', ('!CALC_CONST', der[1]))
                                    if Is3(der[1], 'CalcConstNewClass'):
                                        _3(v[0][0], 'CalcConstNewClass', v[1])
                                        _3(v[0][0], 'Derived', ('!CALC_CONST', der[1]))
                                    else:
                                        Debug('Not name CalcConst???Class', v1)
                                elif der[0] == '!PyObject_GetAttr':        
                                    pass
                                elif der[0] == '!PyObject_Type':        
                                    Debug('Not name CalcConst???Class', v1)
                                elif der[0] == '!PyObject_Call':        
                                    Debug('Not name CalcConst???Class', v1)
                                else:
                                    Debug('Not name CalcConst???Class', v1, der)
                        else:    
                            print v1_1[0], v1_1[0][0], v1_1
                            Fatal('?k', v1)
                    else:
                        Fatal('?k', v1)
    return ret

def collect_modules_attr(ret):
    v = []
    if TCmp(ret, v, ('!PyObject_GetAttr', \
                     (('|', 'CALC_CONST', \
                            '!LOAD_NAME', \
                            '!LOAD_GLOBAL', \
                            '!PyDict_GetItem(glob,'), \
                        ':ImportedM:'), ('CONST', '?'))) and \
                        ModuleHaveAttr(v[0][0], v[1]):
        if v[0][2][:6] == '__buil' and v[0][2][6:] == 'tin__':
           pass
        elif v[0][2] == 'sys' and v[1] in sys_const:
            return ('CONST', getattr(sys,v[1]))
        else:
            if v[0][2] != 'sys' and v[0][2] not in variable_module_attr:
                v2 = IfConstImp(v[0][0], v[1])
                if v2 is not None:
                    return v2
            if ModuleHaveAttr(v[0][0], v[1]) and v[0][2] not in variable_module_attr:
                _3(v[0][0], 'ModuleAttr', v[1])  


variable_module_attr = ('time', 'strptime', '_strptime', 'textwrap')

sys_const = ('byteorder', 'subversion', 'builtin_module_names', 
             'copyright', 'hexversion', 'maxint', 'maxsize', 'maxunicode',
             'platform', 'version', 'api_version')

def is_right_const_value(v2):
    if type(v2) in (int,long,bool,complex,float):
        return True
    ## if type(v2) is tuple and len([x for x in v2 if not is_right_const_value(x)]) == 0:
        ## return True
    return False

def IfConstImp(imp,nm):
    assert imp is not None
    v2 = val_imp(imp, nm)
    if is_right_const_value(v2):
        return ('CONST', v2)
    return None

def ModuleHaveAttr(imp,nm):
##    print '/4', imp, nm
    if imp[:6] == '__buil' and imp[6:] == 'tin__':
        return nm in d_built
    if imp == 'sys' or imp in variable_module_attr or (imp[:6] == '__buil' and imp[6:] == 'tin__'):
        return False
    if Is3(imp, 'ImportedM'):
        v = Val3(imp, 'ImportedM')
        if type(v) is tuple and len(v) == 2:
            imp = v[0] + '.' + v[1]
            if v[0] in list_import and v[1] in list_import[v[0]] and not IsModule(list_import[v[0]][v[1]]):
                return False
        elif type(v) is str and v != imp:
            imp = v
        elif v != imp:
            Fatal(imp, v, nm)
    if imp == 'sys' or imp in variable_module_attr:
        return False
    v2 = val_imp(imp, nm)
    if v2 is None:
        return False
    return True

def repl_collected_module_attr(ret):
#    global all_calculated_const
    v = []
    if TCmp(ret, v, ('!PyObject_GetAttr', '?', ('CONST', '?'))):
        t = TypeExpr(v[0])
        if t is not None and t.descr is types.ModuleType and t.subdescr == 'sys' and v[1] in sys_const:
            return ('CONST', getattr(sys,v[1]))
        elif t is not None and t.descr is types.ModuleType and t.subdescr != 'sys' and\
             t.subdescr is not None and t.subdescr  not in variable_module_attr:
            v2 = IfConstImp(t.subdescr, v[1])
            if v2 is not None:
                return v2
#        ret = calc_const_to((v[0][0], v[1]))
    v = []
    if TCmp(ret, v, ('!PyObject_GetAttr', 
                     (('|', 'CALC_CONST',
                            '!LOAD_NAME', 
                            '!LOAD_GLOBAL', 
                            '!PyDict_GetItem(glob,'),
                        ':ImportedM:'), ('CONST', '?'))):
        if v[0][2] == 'sys' and v[1] in sys_const:
            return ('CONST', getattr(sys,v[1]))
        elif v[0][2] != 'sys' and v[0][2] not in variable_module_attr:
            v2 = IfConstImp(v[0][0], v[1])
            if v2 is not None:
                return v2
        if v[0][2] != 'sys' and ModuleHaveAttr(v[0][0], v[1]) and v[0][2] not in variable_module_attr:
            _3(v[0][0], 'ModuleAttr', v[1])                    
            ret = calc_const_to((v[0][0], v[1]))
        v = []

    if TCmp(ret, v, ('!PyObject_GetAttr', ('CALC_CONST', '?'), ('CONST', '?'))):
        t = TypeExpr(('CALC_CONST', v[0]))
        if not redefined_attribute and t != None and \
           t.descr in (T_NEW_CL_INST, T_OLD_CL_INST) and\
           Is3(t.subdescr, 'AttributeInstance', v[1]) and v[1][0:2] != '__': 
            _3(v[0], 'ModuleAttr', '.__dict__') 
            calc_const_to((v[0], '.__dict__'))                  
   
            ## ret = ('PY_TYPE', dict, None, calc_const_to((v[0], '.__dict__')), None)                
            ## ret = ('!from_ceval_BINARY_SUBSCR', ret, ('CONST', v[1]))
        v = []


    if type(ret) is tuple and len(ret) == 2 and \
       ret[0] in ('!LOAD_NAME', '!LOAD_GLOBAL', '!PyDict_GetItem(glob,') and \
       ret[1] in all_calc_const:
        ret = calc_const_to(ret[1])    
    return ret

def upgrade_op(ret, nm = None):   
    if type(ret) is tuple and len(ret) == 2 and \
       ret[0] in ('!LOAD_NAME', '!LOAD_GLOBAL', '!PyDict_GetItem(glob,') and \
       ret[1] in mnemonic_constant:
           return mnemonic_constant[ret[1]]
    collect_modules_attr(ret)    
    return repl(ret)

methods_type = {(Kl_String, 'find'): Kl_Short,
                (Kl_String, 'index'): Kl_Short,
                (Kl_String, 'split'): Kl_List,
                (Kl_String, 'splitlines'): Kl_List,
                (Kl_String, 'ljust'): Kl_String,
                (Kl_String, 'rjust'): Kl_String,
                (Kl_String, 'zfill'): Kl_String,
                (Kl_String, 'lower'): Kl_String,
                (Kl_String, 'upper'): Kl_String,
                (Kl_String, 'encode'): None,
                (Kl_String, 'replace'): Kl_String,
                (Kl_String, 'strip'): Kl_String,
                (Kl_String, 'rstrip'): Kl_String,
                (Kl_String, 'lstrip'): Kl_String,
                (Kl_String, 'center'): Kl_String,
                (Kl_String, 'join'): Kl_String,
                (Kl_String, 'startswith'): Kl_Boolean,
                (Kl_String, 'endswith'): Kl_Boolean,
                (Kl_File, 'close'): Kl_None,
                (Kl_File, 'write'): Kl_None,
                (Kl_File, 'seek'): Kl_None,
                (Kl_File, 'fileno'): Kl_Int,
                (Kl_File, 'tell'): Kl_Long,
                (Kl_File, 'read'): Kl_String,
                (Kl_File, 'getvalue'): Kl_String,
                (Kl_File, 'readline'): Kl_String,
                (Kl_File, 'readlines'): Kl_List,
                
                (Kl_Dict, 'iteritems'): Kl_Generator,
                (Kl_Dict, 'iterkeys'): Kl_Generator,
                (Kl_Dict, 'copy'): Kl_Dict,
                (Kl_Dict, 'keys'): Kl_List,
                (Kl_Dict, 'values'): Kl_List,
                (Kl_Dict, 'items'): Kl_List,
                (Kl_Dict, 'itervalues'): Kl_Generator,
                (Kl_Dict, 'setdefault'): None,
                (Kl_Dict, 'get'): None,
                (Kl_List, 'popitem'): Kl_Tuple,
                (Kl_List, 'pop'): None,
                (Kl_List, 'append'): Kl_None,
                (Kl_List, 'insert'): Kl_None,
                (Kl_List, 'sort'): Kl_None,
                (Kl_List, 'remove'): Kl_None,
                (Kl_List, 'index'): Kl_Short,
                (Kl_List, 'count'): Kl_Short,
                (Kl_List, 'pop'): None,
                (Klass(T_NEW_CL_INST, 'StringIO'), 'getvalue') : Kl_String,
#                (Klass(T_NEW_CL_INST, 'Popen'), 'stdin') : None,
                (Klass(T_OLD_CL_INST, 'ZipFile'), 'getinfo') : Klass(T_OLD_CL_INST, 'ZipInfo'),
                (Klass(T_OLD_CL_INST, 'ZipFile'), 'infolist') : Kl_List,
                (Klass(T_OLD_CL_INST, 'ZipFile'), 'namelist') : Kl_List,
                (Kl_MatchObject, 'group'): None,
                (Kl_MatchObject, 'groups'): Kl_Tuple,
                (Kl_MatchObject, 'span'): Kl_Tuple,
                (Kl_RegexObject, 'subn'): Kl_Tuple,
                (Kl_RegexObject, 'search'): None,
                (Kl_RegexObject, 'finditer'): Kl_Generator,
                (Kl_RegexObject, 'findall'): Kl_List,
                (Kl_RegexObject, 'split'): Kl_List,
                (Kl_RegexObject, 'match'): None,
                (Kl_RegexObject, 'sub'): Kl_String
                }

klass_attr = {(Klass('NewClassInstance', 'Popen'), 'stdin') : None,
              (Klass('NewClassInstance', 'Popen'), 'stdout') : None,
              (Klass('NewClassInstance', 'Popen'), 'stderr') : None}
                
tag_type = {}

def TypeDef(kl, *words):
    for w in words:
        tag_type[w] = kl
        
TypeDef(Kl_String, '!CHR_BUILTIN', '!_PyString_Join')
TypeDef(Kl_List, '!BUILD_LIST', '!PyDict_Keys', '!PyDict_Items', \
                  '!PyDict_Values', '!PySequence_List', '!LIST_COMPR', '!PyObject_Dir')
TypeDef(Kl_Tuple, '!BUILD_TUPLE', '!PyList_AsTuple', '!PySequence_Tuple')
TypeDef(Kl_Dict, '!BUILD_MAP', '!PyDict_New', '!_PyDict_New', '!_PyDict_NewPresized')
TypeDef(Kl_String, '!PyObject_Repr', '!CHR_BUILTIN', '!STR_CONCAT2', \
                  '!STR_CONCAT3', '!PyString_Format', '!STR_CONCAT', \
                  '!PyObject_Str', '!PyNumber_ToBase', '!_PyInt_Format')
TypeDef(Kl_Int, '!PyInt_FromLong', '!PyInt_Type.tp_new')
TypeDef(Kl_Short, '!PY_SSIZE_T', '!@PyInt_FromSsize_t', '!ORD_BUILTIN', \
                  '!PyInt_FromSsize_t')
TypeDef(Kl_Short, *len_family)                
TypeDef(Kl_Long, '!PyLong_Type.tp_new')
TypeDef(Kl_Set, '!PySet_New', '!BUILD_SET')
TypeDef(Kl_FrozenSet, '!PyFrozenSet_New')
TypeDef(Kl_Type, '!PyObject_Type')
TypeDef(Kl_Slice, '!PySlice_New')
TypeDef(Kl_Boolean, '!AND_JUMP', '!OR_JUMP', '!PyObject_IsInstance', '!PyObject_IsSubclass', \
                  '!PySequence_Contains(', '!_EQ_', '!OR_BOOLEAN', '!AND_BOOLEAN'\
                  '!1NOT', '!_PyString_StartSwith',  '!_PyString_EndSwith')
TypeDef(Kl_Float, '!PyFloat_Type.tp_new')
TypeDef(Kl_Generator, '!GET_ITER')

tag_builtin = {}

def TypeBuilt(kl, *words):
    for w in words:
        tag_builtin[w] = kl
        
TypeBuilt(Kl_Tuple, 'divmod', 'tuple')
TypeBuilt(Kl_List, 'map', 'range', 'zip', 'list', 'dir', 'sorted')
TypeBuilt(Kl_Boolean, 'all', 'any', 'callable', 'isinstance', 'issubclass')
TypeBuilt(Kl_Int, 'hash', 'int')
TypeBuilt(Kl_Short, 'cmp', 'len', 'ord')
TypeBuilt(Kl_Dict, 'dict', 'globals', 'locals', 'vars')
TypeBuilt(Kl_Float, 'float', 'round')
TypeBuilt(Kl_String, 'hex', 'oct', 'str', 'repr', 'chr', 'raw_input', 'bin', 'bytes')
TypeBuilt(Kl_Unicode, 'unicode', 'unichr')
TypeBuilt(Kl_File, 'file', 'open')
TypeBuilt(Kl_Slice, 'slice')
TypeBuilt(Kl_Buffer, 'buffer')
TypeBuilt(Kl_XRange, 'xrange')
TypeBuilt(Kl_Complex, 'complex')
TypeBuilt(Kl_Set, 'set')
TypeBuilt(Kl_FrozenSet, 'frozenset')
TypeBuilt(Kl_StaticMethod, 'staticmethod')
TypeBuilt(Kl_Module(None), '__import__')
TypeBuilt(Kl_ClassMethod, 'classmethod')
TypeBuilt(Kl_Generator, 'enumerate', 'reversed', 'iter')
TypeBuilt(None, 'min', 'max', 'property', 'reduce', 'eval', 'super', \
                          'sum', 'compile', 'ValueError', 'IOError', \
                          'SyntaxError', 'input', 'bytearray', \
                          'filter')

##undefi = {}

def TypeExpr(ret):
    if type(ret) != tuple:
        return None
    if len(ret) < 1:
        return None
    if ret[0] == '!?Raise':
        return Klass('Raise', ret[1])
    if ret[0] == '!LOAD_BUILTIN':
        if ret[1] in d_built and type(d_built[ret[1]]) == type(len):
            return Kl_BuiltinFunction
        elif ret[1] in d_built and type(d_built[ret[1]]) == type(int):
            return Kl_Type
        
    if ret[0] == '!MK_FUNK':
        return Klass(types.FunctionType, ret[1])
    if ret[0] == 'PY_TYPE':
        return Klass(ret[1], ret[2])
    if ret[0] == 'CONST':
        if type(ret[1]) is int and ret[1] >= -30000 and ret[1] <= 30000:
            return Kl_Short
        return Klass(type(ret[1]))
    if ret[0] in tag_type:
        return tag_type[ret[0]]
    if ret[0] == '!CLASS_CALC_CONST':
        return Klass(T_OLD_CL_INST, ret[1])
    if ret[0] == '!CLASS_CALC_CONST_DIRECT':
        return Klass(T_OLD_CL_INST, ret[1])
    if ret[0] == '!CLASS_CALC_CONST_NEW':
        return Klass(T_NEW_CL_INST, ret[1])
    if ret[0] == '!CLASS_CALC_CONST_NEW_DIRECT':
        return Klass(T_NEW_CL_INST, ret[1])
    if ret[0] == '!_PyEval_BuildClass' and ret[2] == ('CONST', ()) and ret[3][0] == 'CONST':
        return Klass(T_OLD_CL_TYP, ret[3][1])
    if ret[0] == '!PyObject_GetAttr' and ret[2][0] == 'CONST':
        t = TypeExpr(ret[1])
        if t is not None and (t, ret[2][1]) in klass_attr:
            return klass_attr[(t, ret[2][1])]
        if t is not None and (t, ret[2][1]) in methods_type:
            return Klass(types.MethodType)
        if t is not None:
            if IsAnyClass(t.subdescr):
                pass
            elif t.descr is types.ModuleType:
                tupl = (t.subdescr, ret[2][1], 'val')
                if tupl in t_imp:
                    return t_imp[tupl]
                tupl = (t.subdescr, ret[2][1], '()')
                if tupl in t_imp:
                    return Klass(types.MethodType)
                if t.subdescr in list_import:
                    d2 = list_import[t.subdescr]
                    if ret[2][1] not in d2 and len(d2) != 0:
                        Debug('Module attrib is not valid: %s -> %s ()' % (t, ret[2][1]), ret)
                    if ret[2][1] in d2:
                        t2 = d2[ret[2][1]]
                        if t2.descr is types.ModuleType and t2.subdescr is None:
                            nm2 = t.subdescr + '.' + ret[2][1]
                            CheckExistListImport(nm2)
                            return Klass(types.ModuleType, nm2)
                        return t2
                    if len(d2) == 0:
                        return None
                Debug('Undefined type attrib: %s -> %s ()' % (t, ret[2][1]), ret)
                if t == Kl_None:
                    Fatal('')
            else:
                Debug('Undefined type attrib: %s -> %s ()' % (t, ret[2][1]), ret)
                if t == Kl_None:
                    Fatal('')
##        if debug: print 'Module 0'
        if ret[2][1] in detected_attr_type:
            r = detected_attr_type[ret[2][1]]
            r.IsKlass()
##            if ret[2][1] == 'prefix': print '/4.5', r, t, ret
            if r == Kl_BuiltinFunction and (not IsModule(t) or 'self' in repr(ret)):
                if t in (Kl_Dict, Kl_Tuple, Kl_List, Kl_Set) and ret[2][1][:2] != '__':
                    return r
                if t is not None:
                    Debug('May by CFunction attribute of %s ?' % repr(t), ret)
                return None
            return r
        return None
    if ret[0] == '!CALL_CALC_CONST':
        if ret[1] in detected_return_type:
            r = detected_return_type[ret[1]]
            r.IsKlass()
            return r
        return None
    if ret[0] == '!CALL_CALC_CONST_INDIRECT':
        if ret[1] in detected_return_type:
            r = detected_return_type[ret[1]]
            r.IsKlass()
            return r
        return None
    
    if ret[0] == 'CALC_CONST':
        nm = ret[1]    
        if type(nm) is tuple and len(nm) == 2:
            tupl = (Val3(nm[0], 'ImportedM'), nm[1], 'val')
            tuplcall = (Val3(nm[0], 'ImportedM'), nm[1], '()')
            if tupl in t_imp:
                return t_imp[tupl]
            elif tuplcall in t_imp:
                return Klass('lazycall', t_imp[tuplcall])
        if Is3(ret[1], 'CalcConstOldClass'):
            return Klass(T_OLD_CL_TYP, ret[1])
        if Is3(ret[1], 'CalcConstNewClass'):
            return Klass(T_NEW_CL_TYP, ret[1])
        if ret[1] not in calc_const_value:
            return None
        ret = calc_const_value[ret[1]]
        return TypeExpr(ret) #Klass(ret)
    if ret[0] == '!PySequence_Repeat':
        return TypeExpr(ret[1])
    if ret[0] in ('!PyNumber_Lshift', '!PyNumber_Rshift'):
        t = TypeExpr(ret[1])
        if t == Kl_Long:
            return t
        if IsInt(t) and ret[0] == '!PyNumber_Rshift' :
            return t
    v = []
    if ret[0] == '!PyObject_Call':
        if ret[1][0] == '!LOAD_BUILTIN':
            v0 = ret[1][1]
            if v0 in tag_builtin:
                return tag_builtin[v0]
            else:
                Debug('Undefined type builtin: %s' % (v0,), ret)
                return None
        if ret[1][0] == 'CALC_CONST':    
            nm = ret[1][1]    
            if type(nm) is tuple and len(nm) == 2:
                tuplcall = (Val3(nm[0], 'ImportedM'), nm[1], '()')
                if tuplcall in t_imp:
                    return t_imp[tuplcall]
        t2 = TypeExpr(ret[1])
        if t2 is not None and t2.descr == 'lazycall':
#            Debug('Lazycall detected', t2, ret)
            return t2.subdescr    
        if ret[1][0] == 'CALC_CONST':
            nm = ret[1][1]    
            if len(nm) == 2:
                tupl = (Val3(nm[0], 'ImportedM'), nm[1], '()')
                if tupl in t_imp:
                    return t_imp[tupl]
        _v = [] 
        if TCmp(ret[1], _v, ('!PyObject_GetAttr', '?', ('CONST', '?'))):
            t = TypeExpr(_v[0])
            if t is not None and (t, _v[1]) in methods_type:
                return methods_type[(t, _v[1])]
            elif t is not None:
                if IsAnyClass(t.subdescr):
                    pass
                elif t.descr is types.ModuleType:
                    tupl = (t.subdescr, _v[1], '()')
                    if tupl in t_imp:
                        return t_imp[tupl]
                    tupl = (t.subdescr, _v[1], 'val')
                    if tupl in t_imp:
                        t2 = t_imp[tupl]
                        if t2.descr == T_OLD_CL_TYP:
                            return Klass(T_OLD_CL_INST, _v[1])
                        elif t2.descr == T_NEW_CL_TYP:
                            return Klass(T_NEW_CL_INST, _v[1])
                        ## else:
                            ## return None
                        
                        
                    Debug('Undefined type method: %s -> %s ()' % (t, _v[1]), ret)
                else:
                    Debug('Undefined type method: %s -> %s ()' % (t, _v[1]), ret)
        return None            
    if ret[0] == '!PyNumber_Remainder' and TypeExpr(ret[1]) == Kl_String:
        return Kl_String       
    if ret[0] == '!PyNumber_Power':
        if Kl_Float == TypeExpr(ret[1]) and Kl_Float == TypeExpr(ret[2]):
           return Kl_Float
        return None
    if ret[0] in ('!PyNumber_And', '!PyNumber_Or'):
        t1 = TypeExpr(ret[1])
        t2 = TypeExpr(ret[2])
        if (t1,t2) == (Kl_Short, Kl_Short):
            return Kl_Short
        if IsInt(t1) and IsInt(t2):
            return Kl_Int
    if ret[0] in ('!PyNumber_Add', '!PyNumber_InPlaceAdd'):
#        Debug(ret)
        t1 = TypeExpr(ret[1])
        t2 = None
        if Kl_Float == t1:
            t2 = TypeExpr(ret[2])
            if Kl_Float == t2:
                return Kl_Float
        if t1 == Kl_Tuple and ret[2][0] == '!PySequence_GetSlice':
            return t1
        if t2 is None:    
            t2 = TypeExpr(ret[2])
        ty = (t1,t2)
        if Kl_Boolean in ty and (IsInt(t1) or IsInt(t2))   :
#        if (t1,t2) in ((Kl_Boolean, Kl_Int), (Kl_Int, Kl_Boolean)):
            if Kl_Short in ty:
                return Kl_Short
            return Kl_Int
        if t1 == Kl_Short and t2 == Kl_Short:
            return Kl_Int
        if t1 is not None and not IsInt(t1) and t1 == t2:
            return t1
        if t2 == Kl_Tuple and ret[1][0] == '!PySequence_GetSlice':
            return t2        
        return None
    if ret[0] in ('!PyNumber_Multiply', '!PyNumber_Divide', \
                  '!PyNumber_Subtract', '!PyNumber_InPlaceSubtract'):
        t1 = TypeExpr(ret[1])
        t2 = None
        if t1 == Kl_Float:
            if t2 is None:
                t2 = TypeExpr(ret[2])
            if t2 == Kl_Float:    
                return Kl_Float
        if t2 is None:
            t2 = TypeExpr(ret[2])
        if t1 == t2 == Kl_Short and ret[0] in ('!PyNumber_InPlaceSubtract', '!PyNumber_Subtract', '!PyNumber_Multiply'):
            return Kl_Int   
    if ret[0] == '!PyNumber_Negative':
        t = TypeExpr(ret[1])
        if IsInt(t) or t == Kl_Long:
            return t

    if ret[0] in ('!PySequence_GetSlice', '!_PyEval_ApplySlice'):
        t2 = TypeExpr(ret[1])
        if t2 in (Kl_String, Kl_List, Kl_Tuple):
            return t2 
        return None   
    if ret[0] == '!BOOLEAN' and TypeExpr(ret[1]) == Kl_Boolean:
        return Kl_Boolean
    if ret[0] == '!IMPORT_NAME':
        return Klass(types.ModuleType, dotted_name_to_first_name(ret[1]))
    if ret[0] in ( '!from_ceval_BINARY_SUBSCR', '!_c_BINARY_SUBSCR_ADDED_INT') and\
       TypeExpr(ret[1]) == Kl_String:
        return Kl_String   

    if type(ret[0]) is tuple or ret[0] == 'NULL':
        Fatal ('Not tag', ret)
#    if ret[0] not in ('FAST', '!_PyList_Pop'):    
#        Debug('Undefine typer', ret)
    return None

def upgrade_op2(ret, nm = None):    
    v = []
    if direct_call and can_generate_c(current_co):
        if TCmp(ret, v, ('!PyObject_Call', ('CALC_CONST', '?'),\
                    ('!BUILD_TUPLE', '?'), ('NULL',))) and \
                    v[0] in val_direct_code: ## and \
            return call_calc_const(direct_code[v[0]], ('!BUILD_TUPLE', v[1]), ret)
        elif TCmp(ret, v, ('!PyObject_Call', ('CALC_CONST', '?'),\
                    ('CONST', '?'), ('NULL',))) and \
                    v[0] in val_direct_code: # and \
            return call_calc_const(direct_code[v[0]], ('CONST', v[1]), ret)
    v  = []            
    if TCmp(ret, v, ('!PyObject_Call', ('CALC_CONST', ':CalcConstOldClass:'),\
                ('!BUILD_TUPLE', '?'), ('NULL',))) :
            if not Is3(v[0][0], 'HaveMetaClass') and not Is3(v[0][0], 'CalcConstNewClass'): #have_metaclass(v[0][0]):
                ret = ('!CLASS_CALC_CONST', v[0][0], ('!BUILD_TUPLE', v[1]))
    elif TCmp(ret, v, ('!PyObject_Call', ('CALC_CONST', ':CalcConstOldClass:'),\
                ('CONST', '?'), ('NULL',))):
            if not Is3(v[0][0], 'HaveMetaClass') and not Is3(v[0][0], 'CalcConstNewClass'):  ## and not have_metaclass(v[0][0]):
                ret = ('!CLASS_CALC_CONST', v[0][0], ('CONST', v[1]))
    elif TCmp(ret, v, ('!PyObject_Call', ('CALC_CONST', ':CalcConstNewClass:'),\
                ('!BUILD_TUPLE', '?'), ('NULL',))):
            if not Is3(v[0][0], 'CalcConstOldClass'):        
                ret = ('!CLASS_CALC_CONST_NEW', v[0][0], ('!BUILD_TUPLE', v[1]))
    elif TCmp(ret, v, ('!PyObject_Call', ('CALC_CONST', ':CalcConstNewClass:'),\
                ('CONST', '?'), ('NULL',))):
            if not Is3(v[0][0], 'CalcConstOldClass'):        
                ret = ('!CLASS_CALC_CONST_NEW', v[0][0], ('CONST', v[1]))
    v = []
    if TCmp(ret, v, ('IMPORT_FROM_AS', '?', ('CONST', -1), ('CONST', '?'), '?')):
        sreti = []
        imp, consts_, stores = v
        for i, reti in enumerate(stores):
            v = []
            if type(reti) is tuple and len(reti) == 2 and \
               reti[0] in ('STORE_NAME', 'STORE_GLOBAL') and \
               reti[1] in all_calc_const:
                reti = ('STORE_CALC_CONST', reti)
            sreti.append(reti)        
        return ret[:4] + (tuple(sreti),)    
    v0 = []
    if len(ret) == 3 and ret[0] == 'SEQ_ASSIGN':
        sreti = []
        for reti in ret[1]:
            v = []
            if type(reti) is tuple and len(reti) == 2 and \
               reti[0] in ('STORE_NAME', 'STORE_GLOBAL') and \
               reti[1] in all_calc_const:
                ## pprint.pprint(ret)
                ## pprint.pprint(v)   
                ## pprint.pprint((reti[1], ret[2]))
                calc_const_value[reti[1]] = ret[2]
                reti = ('STORE_CALC_CONST', reti)
            elif reti[0] == 'SET_VARS':    
                sretii = []
                for retii in reti[1]:
                    if type(retii) is tuple and len(retii) == 2 and \
                       retii[0] in ('STORE_NAME', 'STORE_GLOBAL') and \
                       retii[1] in all_calc_const:
                        retii = ('STORE_CALC_CONST', retii)
                    sretii.append(retii)
                reti = ('SET_VARS', tuple(sretii))        
            sreti.append(reti)        
        return (ret[0], tuple(sreti), ret[2])    
    elif len(ret) == 3 and ret[0] == 'SET_EXPRS_TO_VARS':    
        sretii = []
        for retii in ret[1]:
            if type(retii) is tuple and len(retii) == 2 and \
                retii[0] in ('STORE_NAME', 'STORE_GLOBAL') and \
                retii[1] in all_calc_const:
                retii = ('STORE_CALC_CONST', retii)
            sretii.append(retii)
        return ('SET_EXPRS_TO_VARS', tuple(sretii), ret[2])        

    elif TCmp(ret, v0, ('STORE', (('?', '?'),), ('?',))) and \
       v0[0] in ('STORE_NAME', 'STORE_GLOBAL') and v0[1] in all_calc_const:
        v = [(v0[1], '', all_calc_const[v0[1]]), v0[2]]
        calc_const_value[v[0][0]] = v[1]
        return ('STORE', (('STORE_CALC_CONST', ret[1][0]),), ret[2])    
    elif type(ret) is tuple and len(ret) == 2 and \
       ret[0] in ('!LOAD_NAME', '!LOAD_GLOBAL', '!PyDict_GetItem(glob,') and \
       ret[1] in all_calc_const:
        ret = calc_const_to(ret[1])    
    v = []    
    ret = repl_collected_module_attr(ret)    
    ret = repl(ret) 
    return ret        

def upgrade_repl(ret, nm = None):    
    v = []    
    ret = repl_collected_module_attr(ret)    
    ret = repl(ret) 
    return ret        

def collect_type_return(ret, nm):    
    global type_def
    v = []    
    if TCmp(ret, v, ('RETURN_VALUE', '?')):
        if nm not in type_def:
            type_def[nm] = {}
        type_def[nm][TypeExpr(v[0])] = True
    return ret      

def attempt_module_import_1(nm):
    try:
        if nm.startswith('_c_'):
            nm = nm[3:]
        if nm == filename[:-3]:
            return None
        this = __import__(nm)
        d = this.__dict__
        return this, d
    except:
        Debug('Module %s import unsuccessful1' % nm)     
        return None

def old_class_1(v):
    try:
        return Klass(T_OLD_CL_INST, v.__class__.__name__)
    except:
        pass
    return None

def collect_module_type_attr(nm, acc = []):
    d = None
    if type(nm) is types.ModuleType:
        this = nm
        d = this.__dict__
    elif nm in sys.modules:    
        this = sys.modules[nm]
        d = this.__dict__
    else:
        ret_ret = attempt_module_import_1(nm)
        if ret_ret is None:
            return
        this, d = ret_ret
    if type(this) is types.ModuleType and this in acc:
        return   
    acc.append(this)
    for k in d.keys():
        v = getattr(this, k)
##        if k == 'prefix': print '/0', k,v, nm
        if type(v) is types.ModuleType and v == this:
            continue
        t = type(v)
        if t is types.ModuleType:
            collect_module_type_attr(v, acc) 
        if t is types.InstanceType:
            t2 = old_class_1(v)
            if t2 is not None:
                t = t2
        else:
            if type(t) != type:
                t = Klass(T_NEW_CL_INST, v.__class__.__name__)
            else:    
                t = Klass(t)    
        if k not in self_attr_type:
            pass
##            self_attr_type[k] = {}
##        print '/// 1', k, t    
        else:
            self_attr_type[k][t] = True  
##        self_attr_type[k][Kl_None] = True  

def collect_set_attr(ret, nm):    
    global self_attr_type

    v = []  
    if TCmp(ret, v, ('STORE', '?', '?')):
        [ collect_module_type_attr (expr[1]) for expr in v[1] if expr[0] == '!IMPORT_NAME']

    v = []  
    if nm != 'Init_filename':
        if TCmp(ret, v, ('STORE', (('STORE_NAME', '?'),), ('?',))):
            if v[0] not in self_attr_type:
                self_attr_type[v[0]] = {}
##            print '/// 2', v[0], TypeExpr(v[1])    
            self_attr_type[v[0]][TypeExpr(v[1])] = True  

    if TCmp(ret, v, ('STORE', (('PyObject_SetAttr', '?', ('CONST', '?')),), ('?',))):
        if v[1] not in self_attr_type:
            self_attr_type[v[1]] = {}
##        print '/// 3', v[1], TypeExpr(v[2])    
        self_attr_type[v[1]][TypeExpr(v[2])] = True  
    elif TCmp(ret, v, ('STORE', (('SET_VARS', '?'),), ( '?',))):
        if len(v[1]) > 0 and (v[1][0] in tags_one_step_expr or v[1][0][0] == '!'):
            for set2 in v[0]:
                v2 = []
                if TCmp(set2, v2, ('PyObject_SetAttr', '?', ('CONST', '?'))):
                    if v2[1] not in self_attr_type:
                        self_attr_type[v2[1]] = {}
##                    print '/// 4', v2[1], None    
                    self_attr_type[v2[1]][None] = True  
        else:
            Fatal('Unhandled SetAttr in SET_VARS', ret)
    elif TCmp(ret, v, ('STORE', '?', '?')):
        if len(v[0]) == 1 and (type(v[0][0][0]) is int or v[0][0][0][0:6] == 'STORE_'):
            pass
        elif len(v[0]) == 1 and v[0][0][0] == 'PyObject_SetItem':
            pass
        elif len(v[0]) == 1 and v[0][0][0] == '?PyObject_SetAttr':
            pass ##Debug('Variable arg PyObject_SetAttr', ret)
        elif len(v[0]) == 1 and v[0][0][0] == 'PyObject_SetAttr':
            pass ##Debug('Variable arg PyObject_SetAttr', ret)
        elif len(v[0]) == 1 and v[0][0][0] == 'UNPACK_SEQ_AND_STORE' and v[0][0][1] == 0:  
            for set2 in v[0][0][2]:              
                v2 = []
                if TCmp(set2, v2, ('PyObject_SetAttr', '?', ('CONST', '?'))):
                    if v2[1] not in self_attr_type:
                        self_attr_type[v2[1]] = {}
##                    print '/// 5', v2[1], None    
                    self_attr_type[v2[1]][None] = True  
        else:
            Fatal('Unhandled STORE', ret)
    ## elif TCmp(ret, v, ('!PyObject_GetAttr', ('?', 'self'), ('CONST', '?'))):
        ## if nm not in self_attr_use:
            ## self_attr_use[nm] = {}
        ## if v[1] not in self_attr_use[nm]:
            ## self_attr_use[nm][v[1]] = 0  
        ## self_attr_use[nm][v[1]] += 1   
    return ret    
  
def tree_pass(a, upgrade_op, up, nm):
    if type(a) is tuple:
        if len(a) > 0 and a[0] == 'CONST':
            return a
        while True:   
            r = tuple([tree_pass(i, upgrade_op,a, nm) for i in a])
            notchanged = len(r) == len(a) and all([r[i] is a[i] for i,x in enumerate(r)])
            if notchanged:
                r = a
            r2 = upgrade_op(r,nm)
            notchanged = notchanged and r2 == r 
            if notchanged:
                break
            a = r2
        return r
    if type(a) is list:
        assert len(a) > 0 
        while True:   
            a = repl_list(a,up)
            r = [tree_pass(i, upgrade_op, a, nm) for i in a]
            notchanged = len(r) == len(a) and all([r[i] is a[i] for i,x in enumerate(r)])
            if notchanged:
                r = a
            assert len(r) > 0
            r2 = upgrade_op(r,nm)
            notchanged = notchanged and r2 == r 
            if notchanged:
                break
            a = r2
        return r
    return a

def ortogonal(a, upgrade,up=None):
    if type(a) is tuple:
        if len(a) > 0 and a[0] == 'CONST':
            return a
        r = tuple([ortogonal(i, upgrade,a) for i in a])
        if all([r[i] is a[i] for i,x in enumerate(r)]):
            r = a
        while True:   
            r2 = upgrade(r)
            if r2 == r:
                break
            r = r2
        return r
    if type(a) is list:
        a = repl_list(a,up)
        r = [ortogonal(i, upgrade, a) for i in a]
        if all([r[i] is a[i] for i,x in enumerate(r)]):
            r = a
        while True:   
            r2 = upgrade(r)
            if r2 == r:
                break
            r = r2
        return r
    return a

def have_oper(a,b):
    if type(a) is tuple and len(a) > 0 and a[0] == b:
        return True
    if type(a) is tuple:
        if len(a) > 0 and a[0] == 'CONST':
            return False
        for i in a:
            if have_oper(i,b):
                return True
        return False
    if type(a) is list:
        for i in a:
            if have_oper(i,b):
                return True
        return False
    return False    

def replace_subexpr(a,b,c):
    if type(a) == type(b) and a == b:
        return c
    if type(a) == type(c) and a == c:
        return a
    if type(a) is tuple:
        return tuple([replace_subexpr(i,b,c) for i in a])
    if type(a) is list:
        return [replace_subexpr(i,b,c) for i in a]
    return a    
    
def is_expandable_enumerate(iter):
    if not enumerate2for:
        return False
    v = []
    return TCmp(iter, v, ('!PyObject_Call', ('!LOAD_BUILTIN', 'enumerate'), \
                                            ('!BUILD_TUPLE', ('?',)), \
                                            ('NULL',)))
    
def generate_list_compr_enumerate(acc, val, store_ind, store_val, enumerated, cond, o): 
    assert cond is None or len(cond) == 1 
    ref_expr = Expr1(enumerated, o)
    t = TypeExpr(enumerated)
    if t is not None:
        Debug('Known type enumerate list complete', t, enumerated)
    ref_iter = New()
    n_iter = New('int')
    o.Stmt(ref_iter, '=', 'PyObject_GetIter', ref_expr)
    o.Cls(ref_expr)
    o.Stmt(n_iter, '=', 0)
    o.Stmt('for (;;) {')
    ref_temp = New()
    o.Stmt(ref_temp, '=', 'PyIter_Next', ref_iter)
    o.Raw('if (PyErr_Occurred()) goto ', labl, ';')
    UseLabl()
    o.Stmt('if (!', ref_temp, '){ break; }')
    generate_store(store_val, ref_temp, o, 'PyIter_Next')
    o.ZeroTemp(ref_temp)  
    ref_int = New()
    o.Stmt(ref_int, '=', 'PyInt_FromSsize_t', n_iter)   
    generate_store(store_ind, ref_int, o, ('PyInt_FromSsize_t', n_iter))
    o.Cls(ref_int)
    o.Stmt(n_iter, '++')
    if cond is not None:
        o1, cond_var = shortage(generate_logical_expr(cond[0]))
        o.extend(o1)
        o.Stmt('if (', cond_var, '){')
    ref_val = Expr1(val[0], o)
    o.Stmt('PyList_Append', acc, ref_val)
    o.Cls(ref_val)
    if cond is not None:
        o.Raw('}')
#    o.Cls(ref_val)
#    if cond is not None:
        o.Cls(cond_var)
    o.Raw('}')
    o.Cls(ref_iter, n_iter, ref_expr)
    return acc    

def generate_list_compr_iteritems(acc, val, store_1, store_2, dic, cond, o): 
    assert cond is None or len(cond) == 1 
    ref_expr = Expr1(dic, o)
    
    pos = New('int')
    o.Stmt(pos, '=', 0)
    k, v = New(), New()
    o.Raw('while (PyDict_Next(', ref_expr, ', ', ('&', pos), ', ', ('&', k), ', ', ('&', v), ')) {')
    o.INCREF(k)       
    o.INCREF(v)       
    generate_store(store_1, k, o, 'PyDict_Next')
    generate_store(store_2, v, o, 'PyDict_Next')
    o.Cls(k,v)
 
    if cond is not None:
        o1, cond_var = shortage(generate_logical_expr(cond[0]))
        o.extend(o1)
        o.Stmt('if (', cond_var, '){')
    ref_val = Expr1(val[0], o)
    o.Stmt('PyList_Append', acc, ref_val)
    o.Cls(ref_val)
    if cond is not None:
        o.Raw('}')
#    o.Cls(ref_val)
#    if cond is not None:
        o.Cls(cond_var)
    o.Raw('}')
    o.Cls(pos, ref_expr)
    return acc    

def generate_list_compr_iterkeys(acc, val, store, dic, cond, o): 
    assert cond is None or len(cond) == 1 
    ref_expr = Expr1(dic, o)
    
    pos = New('int')
    o.Stmt(pos, '=', 0)
    k, v = New(), New()
    o.Raw('while (PyDict_Next(', ref_expr, ', ', ('&', pos), ', ', ('&', k), ', ', ('&', v), ')) {')
    o.INCREF(k)       
    o.INCREF(v)       
    generate_store(store, k, o, 'PyDict_Next')
    o.Cls(k,v)
 
    if cond is not None:
        o1, cond_var = shortage(generate_logical_expr(cond[0]))
        o.extend(o1)
        o.Stmt('if (', cond_var, '){')
    ref_val = Expr1(val[0], o)
    o.Stmt('PyList_Append', acc, ref_val)
    o.Cls(ref_val)
    if cond is not None:
        o.Raw('}')
#    o.Cls(ref_val)
#    if cond is not None:
        o.Cls(cond_var)
    o.Raw('}')
    o.Cls(pos, ref_expr)
    return acc    

def generate_list_compr_itervalues(acc, val, store, dic, cond, o): 
    assert cond is None or len(cond) == 1 
    ref_expr = Expr1(dic, o)
    
    pos = New('int')
    o.Stmt(pos, '=', 0)
    k, v = New(), New()
    o.Raw('while (PyDict_Next(', ref_expr, ', ', ('&', pos), ', ', ('&', k), ', ', ('&', v), ')) {')
    o.INCREF(k)       
    o.INCREF(v)       
    generate_store(store, v, o, 'PyDict_Next')
    o.Cls(k,v)
 
    if cond is not None:
        o1, cond_var = shortage(generate_logical_expr(cond[0]))
        o.extend(o1)
        o.Stmt('if (', cond_var, '){')
    ref_val = Expr1(val[0], o)
    o.Stmt('PyList_Append', acc, ref_val)
    o.Cls(ref_val)
    if cond is not None:
        o.Raw('}')
#    o.Cls(ref_val)
#    if cond is not None:
        o.Cls(cond_var)
    o.Raw('}')
    o.Cls(pos, ref_expr)
    return acc  

def generate_list_compr(val, descr_compr, o, forcenewg):
    acc0 = GenExpr(('!BUILD_LIST', ()),o, forcenewg)
    store,expr,cond = descr_compr[0:3]

    v = []
    if len(descr_compr) == 3 and len(store) == 2 and len(expr) == 1 and \
        TCmp(descr_compr, v, (('?', '?'), (('!PyObject_Call', \
        ('!PyObject_GetAttr', '?', ('CONST', 'iteritems')), \
        ('CONST', ()), \
        ('NULL',)),), \
        '?')) and TypeExpr(v[2]) == Kl_Dict:    
        generate_list_compr_iteritems(acc0, val, store[0], store[1], v[2], cond, o)
        return acc0                             
    if len(descr_compr) == 3 and len(store) == 1 and len(expr) == 1 and \
        TCmp(descr_compr, v, (('?',), (('!PyObject_Call', \
        ('!PyObject_GetAttr', '?', ('CONST', 'iterkeys')), \
        ('CONST', ()), \
        ('NULL',)),), \
        '?')) and TypeExpr(v[1]) == Kl_Dict:    
        generate_list_compr_iterkeys(acc0, val, store[0], v[1], cond, o)
        return acc0    
    if len(descr_compr) == 3 and len(store) == 1 and len(expr) == 1 and \
        TCmp(descr_compr, v, (('?',), (('!PyObject_Call', \
        ('!PyObject_GetAttr', '?', ('CONST', 'itervalues')), \
        ('CONST', ()), \
        ('NULL',)),), \
        '?')) and TypeExpr(v[1]) == Kl_Dict:    
        generate_list_compr_itervalues(acc0, val, store[0], v[1], cond, o)
        return acc0    
    if len(descr_compr) == 3 and len(store) == 2 and len(expr) == 1 and \
                is_expandable_enumerate(expr[0]):
        generate_list_compr_enumerate(acc0, val, store[0], store[1], \
                                      expr[0][2][1][0], cond, o)
        return acc0                             
    recursive_gen_list_compr(acc0, val, store,expr, cond, descr_compr[3:], o)
    return acc0

def recursive_gen_list_compr(acc, val, store,expr, cond,tail, o):
    assert len(expr) == 1
    assert cond is None or len(cond) == 1
    ref_expr = Expr1(expr[0], o)
    ref_iter = New()
    o.Stmt(ref_iter, '=', 'PyObject_GetIter', ref_expr)
    o.Cls(ref_expr)
    o.Stmt('for (;;) {')
    ref_temp = New()
    o.Stmt(ref_temp, '=', 'PyIter_Next', ref_iter)
    o.Raw('if (PyErr_Occurred()) goto ', labl, ';')
    UseLabl()
    o.Stmt('if (!', ref_temp, '){ break; }')
    if len(store) == 1:
        generate_store(store[0], ref_temp, o, 'PyIter_Next')
    else:  
        if store is not None:  
            generate_store(('SET_VARS', store), ref_temp, o, 'PyIter_Next')
    o.ZeroTemp(ref_temp)  

    if cond is not None:
        o1, cond_var = shortage(generate_logical_expr(cond[0]))
        o.extend(o1)
        o.Stmt('if (', cond_var, '){')
        o.Cls(cond_var)
    if len(tail) == 0:
        ref_val = Expr1(val[0], o)
        o.Stmt('PyList_Append', acc, ref_val)
        o.Cls(ref_val)
    else:
        store1,expr1, cond1 = tail[0:3]
        recursive_gen_list_compr(acc, val, store1,expr1, cond1, tail[3:], o)
    if cond is not None:
        o.Raw('}')
    o.Raw('}')
    o.Cls(ref_iter)
    return acc

def generate_set_compr(val, descr_compr, o, forcenewg):
    acc0 = GenExpr(('!BUILD_SET', ()),o, forcenewg)
    store,expr,cond = descr_compr[0:3]

    v = []
    recursive_gen_set_compr(acc0, val, store,expr, cond, descr_compr[3:], o)
    return acc0

def recursive_gen_set_compr(acc, val, store,expr, cond,tail, o):
    assert len(expr) == 1
    assert cond is None or len(cond) == 1
    ref_iter = Expr1(expr[0], o)
    o.Stmt('for (;;) {')
    ref_temp = New()
    o.Stmt(ref_temp, '=', 'PyIter_Next', ref_iter)
    o.Raw('if (PyErr_Occurred()) goto ', labl, ';')
    UseLabl()
    o.Stmt('if (!', ref_temp, '){ break; }')
    if len(store) == 1:
        generate_store(store[0], ref_temp, o, 'PyIter_Next')
    else:  
        if store is not None:  
            generate_store(('SET_VARS', store), ref_temp, o, 'PyIter_Next')
    o.ZeroTemp(ref_temp)  

    if cond is not None:
        o1, cond_var = shortage(generate_logical_expr(cond[0]))
        o.extend(o1)
        o.Stmt('if (', cond_var, '){')
        o.Cls(cond_var)
    if len(tail) == 0:
        ref_val = Expr1(val[0], o)
        o.Stmt('PySet_Add', acc, ref_val)
        o.Cls(ref_val)
    else:
        store1,expr1, cond1 = tail[0:3]
        recursive_gen_set_compr(acc, val, store1,expr1, cond1, tail[3:], o)
    if cond is not None:
        o.Raw('}')
    o.Raw('}')
    o.Cls(ref_iter)
    return acc

def generate_map_compr(val, descr_compr, o, forcenewg):
    acc0 = GenExpr(('!BUILD_MAP', ()),o, forcenewg)
    store,expr,cond = descr_compr[0:3]

    v = []
    recursive_gen_map_compr(acc0, val, store,expr, cond, descr_compr[3:], o)
    return acc0

def recursive_gen_map_compr(acc, val, store,expr, cond,tail, o):
    assert len(expr) == 1
    assert cond is None or len(cond) == 1
    ref_iter = Expr1(expr[0], o)
    o.Stmt('for (;;) {')
    ref_temp = New()
    o.Stmt(ref_temp, '=', 'PyIter_Next', ref_iter)
    o.Raw('if (PyErr_Occurred()) goto ', labl, ';')
    UseLabl()
    o.Stmt('if (!', ref_temp, '){ break; }')
    if len(store) == 1:
        generate_store(store[0], ref_temp, o, 'PyIter_Next')
    else:  
        if store is not None:  
            generate_store(('SET_VARS', store), ref_temp, o, 'PyIter_Next')
    o.ZeroTemp(ref_temp)  

    if cond is not None:
        o1, cond_var = shortage(generate_logical_expr(cond[0]))
        o.extend(o1)
        o.Stmt('if (', cond_var, '){')
        o.Cls(cond_var)
    if len(tail) == 0:
        ref_k = Expr1(val[0], o)
        ref_v = Expr1(val[1], o)
        o.Stmt('PyDict_SetItem', acc, ref_k, ref_v)
        o.Cls(ref_k, ref_v)
    else:
        store1,expr1, cond1 = tail[0:3]
        recursive_gen_map_compr(acc, val, store1,expr1, cond1, tail[3:], o)
    if cond is not None:
        o.Raw('}')
    o.Raw('}')
    o.Cls(ref_iter)
    return acc


def AssignCalcConst(nm, ref, o, expr):
    if nm in mnemonic_constant:
##        Fatal('??? Assign mnemoconst', nm, ref, expr, o)
        return
    o.Stmt(calc_const_to(nm), '=', ref);
##    o.INCREF(ref) not need
    for a,b,c in Iter3(nm, 'ModuleAttr', None):
        if c != '.__dict__':
            r = New()
            o.Stmt(r, '=', 'PyObject_GetAttr', ref, ('CONST', c))
            o.INCREF(r)
            o.Stmt(calc_const_to((nm, c)), '=', r)
            o.Cls(r)
        else:
            t = TypeExpr(expr)
            if t is None:
                Fatal('Can\'t detect old/new class of calculated const %s' % nm, expr)
            if t.descr == T_NEW_CL_INST:
                o.Raw(calc_const_to((nm, c)), ' = *_PyObject_GetDictPtr(', calc_const_to(nm), ');')
            elif t.descr == T_OLD_CL_INST:
                o.Raw(calc_const_to((nm, c)), ' = ((PyInstanceObject *)', calc_const_to(nm), ')->in_dict;')
            else:
                Fatal('Can\'t detect any class of calculated const %s' % nm, expr)

def generate_store(it, ref, o, expr):
    global func
    assert type(it) is tuple
    if it[0] == 'STORE_CALC_CONST':
        it = it[1]
        AssignCalcConst(it[1], ref, o, expr)
        if it[0] == 'STORE_GLOBAL' or (it[0] == 'STORE_NAME' and func == 'Init_filename'):
            ## if not istempref(ref) and is notconstref(ref) and is notfast(ref):
                ## o.INCREF(ref)
            o.Stmt('PyDict_SetItem', 'glob', ('CONST', it[1]), ref)
            if istempref(ref):
                o.Cls(ref)
        elif it[0] == 'STORE_NAME':
            o.Stmt('PyObject_SetItem', 'f->f_locals', ('CONST', it[1]), ref)
        else:
            Fatal('generate_store', it)
        o.ClsFict(ref)
        return
    if it[0] == 'STORE_GLOBAL' or (it[0] == 'STORE_NAME' and func == 'Init_filename'):
        ## if not istempref(ref) and is notconstref(ref) and is notfast(ref):
                ## o.INCREF(ref)
        o.Stmt('PyDict_SetItem', 'glob', ('CONST', it[1]), ref)
        if istempref(ref):
            o.Cls(ref)
        o.ClsFict(ref)
        return
    if it[0] == 'STORE_NAME':
        o.Stmt('PyObject_SetItem', 'f->f_locals', ('CONST', it[1]), ref)
        o.Cls(ref)
        return
    if it[0] == 'STORE_FAST':
        if not istempref(ref):
            o.INCREF(ref)
        o.Stmt('SETLOCAL', it[1], ref)
        o.ClsFict(ref)
        if istempref(ref) and ref not in g_refs2:
            o.Raw(ref, ' = 0;')
        return
    if it[0] == 'STORE_DEREF':
        o.Stmt('PyCell_Set', ('LOAD_CLOSURE',it[1]), ref)
        o.Cls(ref)
        return
    if it[0] == 'PyObject_SetAttr':
        generate_SetAttr(it, ref, o, expr)
        return
    if it[0] == '?PyObject_SetAttr':
        ref1, ref2 = Expr(o, it[1:3])
        o.Stmt('PyObject_SetAttr', ref1, ref2, ref)
        proc = Expr1(it[3], o)   
        o.Stmt('if (', proc, '==', load_builtin(it[3][1]), ') {')
        o.Stmt('PyObject_SetAttr', ref1, ref2, ref)
        o.Cls(ref, ref1, ref2)
        o.Raw('} else {')
        ref4 = New()
        tupl = Expr1(('!BUILD_TUPLE', (ref1, ref2, ref)), o)
        o.Stmt(ref4, '=', 'PyObject_Call', proc, tupl, ('NULL',))
        o.Cls(tupl, ref4)
        o.Raw('}')
        o.Cls(proc)
        return
# Code crash unknown -- no crash currently   
    if it[0] == 'PyObject_SetItem' and it[2][0] == '!@PyInt_FromSsize_t':
##        print '/3', it
        ref1 = Expr1(it[1], o)
        islist = TypeExpr(it[1]) == Kl_List
        o.ClsFict(ref)
        if not islist:
            o.Stmt('if (PyList_CheckExact(', ref1, ')) {')
        if not istempref(ref):
            o.INCREF(ref)
        o.Stmt('PyList_SetItem', ref1, it[2][1], ref)
        if not islist:
            o.Raw('} else {')
            ref2 = Expr1(it[2][2],o)
            o.Stmt('PyObject_SetItem', ref1, ref2, ref)
            o.Cls(ref2)
            if istempref(ref):
                o.CLEAR(ref)
            o.Raw('}')
        o.Cls(ref1)
        return
    if it[0] == 'PyObject_SetItem' and it[2][0] == 'CONST' and type(it[2][1]) is int:
        ref1 = Expr1(it[1], o)
        o.ClsFict(ref)
        ty = TypeExpr(it[1])
        islist = ty == Kl_List
        if islist:
            if not istempref(ref):
                o.INCREF(ref)
            if it[2][1] >= 0:    
                o.Stmt('PyList_SetItem', ref1, it[2][1], ref)
            else:    
                n = New('long')
                o.Raw(n, ' = PyList_GET_SIZE(', ref1, ') + ', it[2][1], ';')
                o.Stmt('PyList_SetItem', ref1, n, ref)
                o.Cls(n)
        elif ty == Kl_Dict:        
#            if not istempref(ref):
#                o.INCREF(ref)
            o.Stmt('PyDict_SetItem', ref1, it[2], ref)
        else:
            if it[2][1] >= 0:    
                o.Stmt('if (PyList_CheckExact(', ref1, ')) {')
                if not istempref(ref):
                    o.INCREF(ref)
                o.Stmt('PyList_SetItem', ref1, it[2][1], ref)
                o.Raw('} else {')
                o.Stmt('PyObject_SetItem', ref1, it[2], ref)
                if istempref(ref):
                    o.CLEAR(ref)
                o.Raw('}')
            else:    
                o.Stmt('PyObject_SetItem', ref1, it[2], ref)
        o.Cls(ref1)
        return
    if it[0] == 'PyObject_SetItem':
        ty = TypeExpr(it[1])
        ty_ind = TypeExpr(it[2])
        if ty == Kl_Dict:        
            ref1, ref2 = Expr(o, it[1:3])
#            if not istempref(ref):
#                o.INCREF(ref)
            o.Stmt('PyDict_SetItem', ref1, ref2, ref)
            o.Cls(ref, ref1, ref2)
        elif ty == Kl_List and IsInt(ty_ind):        
            ref1 = Expr1(it[1],o)
            if not istempref(ref):
                o.INCREF(ref)
            o2,ind = shortage(generate_ssize_t_expr(it[2]))
            o.extend(o2)
            if type(ind) is int:
                if ind < 0:
                    ind2 = New('long')
                    o.Raw(ind2, ' = ', ind, ' + PyList_GET_SIZE(', ref1, ');')
                    ind = ind2
                else:
                    pass    
            else:    
                if not istemptyped(ind):
                    ind_ = New('long')
                    o.Raw(ind_, ' = ', ind, ';')
                    ind = ind_
                o.Stmt('if (', ind, '< 0) {')
                o.Raw(ind, ' += PyList_GET_SIZE(', ref1, ');')
                o.Raw('}')
            o.Stmt('PyList_SetItem', ref1, ind, ref)
            o.ClsFict(ref)
            o.Cls(ind, ref, ref1)
        elif ty == Kl_List:        
            ref1 = Expr1(it[1],o)
            if not istempref(ref):
                o.INCREF(ref)
            refind = Expr1(it[2], o)
            o.Raw('if (PyInt_CheckExact(', refind,')) {')
            ind = New('long')
            o.Raw(ind, ' = PyInt_AS_LONG(', refind,');')
            o.Stmt('if (', ind, '< 0) {')
            o.Raw(ind, ' += PyList_GET_SIZE(', ref1, ');')
            o.Raw('}')
            o.Stmt('PyList_SetItem', ref1, ind, ref)
            o.Cls(ind)
            o.Raw('} else {')
            o.Stmt('PyObject_SetItem', ref1, refind, ref)
            o.Raw('}')    
            o.ClsFict(ref)
            o.Cls(ind, ref, ref1, refind)
        else:    
            if ty is not None:
                Debug( 'typed SetItem', ty, it)
            ref1, ref2 = Expr(o, it[1:3])
            o.Stmt('PyObject_SetItem', ref1, ref2, ref)
            o.Cls(ref, ref1, ref2)
        return
    
    if it[0] == 'STORE_SLICE_LV+0':
        t = TypeExpr(it[1])
        if t == Kl_List:
            assign_list_slice(it, o, ref)
            return    
        if t is not None:
            Debug('typed Store slice', t,it)
        ref1 = Expr1(it[1],o)
        o.Stmt('_PyEval_AssignSlice', ref1, 'NULL', 'NULL', ref)
        o.Cls(ref, ref1)
        return    
    if it[0] == 'STORE_SLICE_LV+3':
        t = TypeExpr(it[1])
        if t is not None:
            Debug('typed Store slice', t, it)
        ref1, ref2, ref3 = Expr(o, it[1:])
        o.Stmt('_PyEval_AssignSlice', ref1, ref2, ref3, ref)
        o.Cls(ref, ref1, ref2, ref3)
        return    
    if it[0] == 'STORE_SLICE_LV+1':
        t = TypeExpr(it[1])
        if t == Kl_List:
            assign_list_slice(it, o, ref)
            return    
        elif t is not None:
            Debug('typed Store slice', TypeExpr(it[1]),it)

        ref1, ref2 = Expr(o, it[1:])
        o.Stmt('_PyEval_AssignSlice', ref1, ref2, 'NULL', ref)
        o.Cls(ref, ref1, ref2)
        return    
    if it[0] == 'STORE_SLICE_LV+2':
        t = TypeExpr(it[1])
        if t is not None:
            Debug('typed Store slice', t, it)
        ref1, ref2 = Expr(o, it[1:])
        o.Stmt('_PyEval_AssignSlice', ref1, 'NULL', ref2, ref)
        o.Cls(ref, ref1, ref2)
        return    
    if it[0] == 'SET_VARS':  
        mass_store(o,ref,it[1],expr)
        return       
    if it[0] == 'UNPACK_SEQ_AND_STORE' and it[1] == 0:  
        mass_store(o,ref,it[2],expr)
        return       
    Fatal('', it)
    
def assign_list_slice(it, o, ref, plus_1 = False):
    ref1 = Expr1(it[1],o)
    if it[0] == 'DELETE_SLICE+0':
        ind2 = New('long')
        o.Raw(ind2, ' = PyList_GET_SIZE(', ref1, ');')
        o.Stmt('PyList_SetSlice', ref1, 0, ind2, 'NULL')
        o.Cls(ref1, ind2)
        return    
    if it[0] == 'STORE_SLICE_LV+0':
        ind2 = New('long')
        o.Raw(ind2, ' = PyList_GET_SIZE(', ref1, ');')
        o.Stmt('PyList_SetSlice', ref1, 0, ind2, ref)
        o.Cls(ref1, ind2, ref)
        return    
        
    o2,ind1 = shortage(generate_ssize_t_expr(it[2]))
    o.extend(o2)
    ind2 = New('long')
    o.Raw(ind2, ' = PyList_GET_SIZE(', ref1, ');')
    if type(ind1) is int:
        if ind1 < 0:
            _ind1 = New('long')
            o.Stmt(_ind1, '=', ind1, '+', ind2)
            ind1 = _ind1
    elif ind1[0] == 'CONST':
        if ind1[1] < 0:
            _ind1 = New('long')
            o.Stmt(_ind1, '=', ind1[1], '+', ind2)
            ind1 = _ind1
    else:        
        if not istemptyped(ind1):
            ind_ = New('long')
            o.Raw(ind_, ' = ', ind1, ';')
            ind1 = ind_
        o.Stmt('if (', ind1, '< 0) {')
        o.Stmt(ind1, '=', ind1, '+', ind2)
        o.Raw('}')                        
    if plus_1:    
        o.Stmt(ind2, '=', ind1, '+', 1)
    o.Stmt('PyList_SetSlice', ref1, ind1, ind2, ref)
    o.Cls(ref, ref1, ind1, ind2)
    return    
        
    
def isfast(ref):
    return ref[0] == 'FAST'    

def handle_unpack_except(o, src_len, trg_len):
    o.Raw('if (', src_len, ' > ', trg_len, ') {')
    o.Raw('PyErr_Format(PyExc_ValueError, "too many values to unpack");')
    o.Raw('goto ', labl, ';')
    UseLabl()
    o.Raw('}')    
    o.Raw('if (', src_len, ' < ', trg_len, ') {')
    add_s = '%s, %s == 1 ? "" : "s"' % (CVar(src_len), CVar(src_len))
    o.Raw('PyErr_Format(PyExc_ValueError, "need more than %d value%s to unpack", ', add_s, ');')
    o.Raw('goto ', labl, ';')
    UseLabl()
    o.Raw('}')    

def mass_store(o,ref,its,expr):
    islist = False
    t = TypeExpr(expr)
    PushAcc([expr], [ref])
    src_len = New('Py_ssize_t')
    trg_len = len([x for x in its if x is not None])
    ## if t != Kl_List and t != Kl_Tuple:
        ## print '?mass-store', its, t, ref, expr
    if t == Kl_List:
        o.Raw(src_len, ' = PyList_GET_SIZE(', ref, ');')
        handle_unpack_except(o, src_len, trg_len)        
        for i,iit in enumerate(its):
            if iit is None: continue
            ref1 = New()
            o.Stmt(ref1, '=', 'PyList_GetItem', ref, i)
            generate_store(iit,ref1,o, ('!PyList_GetItem', expr, i))
            o.Cls(ref1)
    elif t == Kl_Tuple:
        o.Stmt(src_len, '=', 'PyTuple_GET_SIZE', ref)
        handle_unpack_except(o, src_len, trg_len)        
        for i,iit in enumerate(its):
            if iit is None: continue
            ref1 = New()
            o.Stmt(ref1, '=', 'PyTuple_GetItem', ref, i)
            generate_store(iit,ref1,o, ('!PyTuple_GetItem', expr, i))
            o.Cls(ref1)
    else:        
        if t is not None:
            Debug( 'UNused type expr in mass store', t, expr)
        o.Stmt('if (PyList_CheckExact(', ref, ') ) {')
        o.Raw(src_len, ' = PyList_GET_SIZE(', ref, ');')
        handle_unpack_except(o, src_len, trg_len)        
        for i,iit in enumerate(its):
            if iit is None: continue
            ref1 = New()
            o.Stmt(ref1, '=', 'PyList_GetItem', ref, i)
            generate_store(iit,ref1,o, ('!PyList_GetItem', expr, i))
            o.Cls(ref1)
        o.Stmt('} else if (PyTuple_CheckExact(', ref, ') ) {')
        o.Raw(src_len, ' = PyTuple_GET_SIZE(', ref, ');')
        handle_unpack_except(o, src_len, trg_len)        
        for i,iit in enumerate(its):
            if iit is None: continue
            ref1 = New()
            o.Stmt(ref1, '=', 'PyTuple_GetItem', ref, i)
            generate_store(iit,ref1,o, ('!PyTuple_GetItem', expr, i))
            o.Cls(ref1)
        o.Raw('} else {')
        ref2 = New()
        o.Stmt(ref2, '=', 'PySequence_Tuple', ref)
        o.Raw(src_len, ' = PyTuple_GET_SIZE(', ref2, ');')
        handle_unpack_except(o, src_len, trg_len)        
        for i,iit in enumerate(its):
            if iit is None: continue
            ref1 = New()
            o.Stmt(ref1, '=', 'PyTuple_GetItem', ref2, i)
            generate_store(iit,ref1,o, ('!PyTuple_GetItem', expr, i))
            o.Cls(ref1)
        o.Cls(ref2)
        o.Raw('}')
    if istempref(ref):    
        o.Raw('Py_CLEAR(',  ref,');')    
    PopAcc(o)
    o.Cls(ref, src_len)
    return       
    
g_acc2 = []
g_refs2 = []
g_len_acc = []

def PopAcc(o, clear = True):
    global g_acc2, g_refs2
    to_clear = []
    if clear:
        to_clear = g_refs2[g_len_acc[-1]:]
        ## for g in g_refs2[g_len_acc[-1]:]:
            ## if istempref(g):
                ## o.Raw('Py_CLEAR(',  g,');')    
## ##            o.ZeroTemp(g)  
    del g_acc2[g_len_acc[-1]:]
    del g_refs2[g_len_acc[-1]:]
    del g_len_acc[-1]
    for g in to_clear:
        if istempref(g):
            o.Cls(g)    
##            o.ZeroTemp(g)  

def PushAcc(acc,refs):
    global g_acc2, g_refs2
    g_len_acc.append(len(g_acc2))
    g_acc2.extend(acc)
    g_refs2.extend(refs)
    
def PopClearAll(o):
    global g_acc2, g_refs2, g_len_acc
    grefs = g_refs2[:]
    while len(grefs) > 0:
        r = grefs[-1]
        if istempref(r):
            o.CLEAR(r)
        del grefs[-1]

def is_mkfunc_const(proc, expr):
    if expr[0] in ('!MK_FUNK', '!_PyEval_BuildClass'):
        return True
    if len(proc) != 2:
        return False
    if not (type(proc[0]) is str):
        return False
    if proc[0] != 'CALC_CONST':
        return False
    if proc[1] in calc_const_value and \
       calc_const_value[proc[1]][0] in ('!MK_FUNK', '!_PyEval_BuildClass'):
            return True
    return False

def standart_BINARY_SUBSCR(it, o, forcenewg):
    ref0, ref1 = Expr(o, it[1:3])
    ref = New(None, forcenewg)
    o.Stmt(ref, '=', 'PyObject_GetItem', ref0, ref1)
    o.Cls(ref1, ref0)
    return ref

def Expr1(it, o):
    return GenExpr(it, o)

def Expr(o, it):
    return [GenExpr(x, o) for x in it]
    
def Str_for_C(s):
    r = ''
    for c in s:
        ## if '0' >= c >='9':
            ## r += c
        ## elif 'a' >= c >= 'z':        
            ## r += c
        ## elif 'A' >= c >= 'Z':        
            ## r += c
        ## elif c in ' ~!@#$%^&*()_+;:<>,./?|{}[]':        
            ## r += c
        ## elif c == '\n':
            ## r += '\\n'
        ## else:
            h = hex(ord(c))
            assert h.startswith('0x')
            h = h[2:]
            if len(h) < 2:
                h = '0' + h
            r += '\\x' + h    
    return '"' + r + '"'            

def generate_SetAttr(it, ref, o, expr):
    t = TypeExpr(it[1])
    _ddic = all_co[current_co]   
##    print 'SetAttr', t, _ddic.__dict__, current_co, it 
    ## if not redefined_attribute and \
       ## (it[1] == ('FAST', 'self') or \
        ## (it[1][0] == 'PY_TYPE' and it[1][3] == ('FAST', 'self') and it[1][2] == _ddic.method_class))\
            ## and it[2][0] == 'CONST' and \
            ## Is3(_ddic.method_class, 'AttributeInstance', it[2][1]) and \
            ## it[2][1][0:2] != '__': 
        ## if current_co.co_name != '__init__':        
            ## if _ddic.method_new_class: 
                ## o.Stmt('PyDict_SetItem', '*self_dict', it[2], ref)
                ## _ddic.self_dict_getattr_used = True
                ## o.Cls(ref)
                ## return
            ## elif _ddic.method_old_class: 
                ## o.Stmt('PyDict_SetItem', 'self_dict', it[2], ref)
                ## _ddic.self_dict_getattr_used = True
                ## o.Cls(ref)
                ## return
        ## else:
            ## if _ddic.method_new_class: 
                ## if _ddic.self_dict_setattr_used:
                    ## o.Stmt('PyDict_SetItem', '*self_dict', it[2], ref)
                    ## _ddic.self_dict_getattr_used = True
                    ## o.Cls(ref)
                    ## return
                ## else:
                    ## _ddic.self_dict_setattr_used = True
            ## elif _ddic.method_old_class: 
                ## o.Stmt('PyDict_SetItem', 'self_dict', it[2], ref)
                ## _ddic.self_dict_getattr_used = True
                ## o.Cls(ref)
                ## return
    if not redefined_attribute and it[2][0] == 'CONST' and it[2][1][0:2] != '__' and it[1][0] == 'FAST':
        isattrs = list(Iter3(None, 'AttributeInstance', it[2][1]))
        ismeth = len (list(Iter3(None, ('Method', it[2][1]), None))) > 0
        if not ismeth and len(isattrs) > 0 and it[1][1] in current_co.co_varnames and \
            current_co.co_varnames.index(it[1][1]) < current_co.co_argcount:
            s1 = ('STORE_FAST', it[1][1])
            s2 = ('DELETE_FAST', it[1][1])
            srepr = repr(_ddic.cmds[1])
            if not repr(s1) in srepr and not repr(s2) in srepr:
                o.Raw('if (_' + it[1][1] + '_dict) {')
                o.Raw('if (PyDict_SetItem(_', it[1][1], '_dict, ', it[2], ', ', ref, ') == -1) goto ', labl, ';')
                UseLabl()
                _ddic.dict_getattr_used[it[1][1]] = True
                o.Raw('} else {')
                o.Stmt('PyObject_SetAttr', it[1], it[2], ref)
                o.Raw('}')
                o.Cls(ref)
                return
    if t is not None and t.descr == T_OLD_CL_INST:
        ismeth = len (list(Iter3(None, ('Method', it[2][1]), None))) > 0
        if  not ismeth and it[2][0] == 'CONST' and Is3(t.subdescr, 'AttributeInstance', it[2][1]) and \
              it[2][1][0:2] != '__':
            ref1 = Expr1(it[1], o)
            o.Stmt('PyDict_SetItem', '((PyInstanceObject *)' + CVar(ref1) + ')->in_dict', it[2], ref)
            o.Cls(ref1, ref)
            return

    elif t is not None and t.descr == T_OLD_CL_INST and it[1][0] == 'CALC_CONST':
        if it[2][0] == 'CONST' and Is3(t.subdescr, 'AttributeInstance', it[2][1]) and \
              it[2][1][0:2] != '__':
            if Is3(it[1][1], 'ModuleAttr', '.__dict__'):
                o.Stmt('PyDict_SetItem', calc_const_to((it[1][1], '.__dict__')), it[2], ref)
                o.Cls(ref)
                return
    elif t is not None and t.descr == T_NEW_CL_INST and it[1][0] == 'CALC_CONST':
        if it[2][0] == 'CONST' and Is3(t.subdescr, 'AttributeInstance', it[2][1]) and \
              it[2][1][0:2] != '__':
            if Is3(it[1][1], 'ModuleAttr', '.__dict__'):
                o.Stmt('PyDict_SetItem', calc_const_to((it[1][1], '.__dict__')), it[2], ref)
                o.Cls(ref)
                return
            r = Expr1(it[1], o)
            dic = New()
            o.Raw(dic, ' = *_PyObject_GetDictPtr(',r,');')
            o.INCREF(dic)
            o.Cls(r)
            o.Stmt('PyDict_SetItem', dic, it[2], ref)
            o.Cls(dic)
            o.Cls(ref)
            return


    ## if t is not None and t.descr == T_NEW_CL_INST:
        ## if it[2][0] == 'CONST' and Is3(t.subdescr, 'AttributeInstance', it[2][1]) and \
            ## it[2][1][0:2] != '__':
            ## ref1 = Expr1(it[1], o)
            ## o.Stmt('PyObject_GenericSetAttr', ref1, it[2], ref)
            ## o.Cls(ref1, ref)
            ## return
    ref1, ref2 = Expr(o, it[1:])
    o.Stmt('PyObject_SetAttr', ref1, ref2, ref)
    o.Cls(ref, ref1, ref2)
    return
    
def generate_GetAttr(it,o, forcenewg, typed):
    t = TypeExpr(it[1])
    _ddic = all_co[current_co]
    if not redefined_attribute and it[2][0] == 'CONST' and it[2][1][0:2] != '__':
        ## if (it[1] == ('FAST', 'self') or \
            ## (it[1][0] == 'PY_TYPE' and it[1][3] == ('FAST', 'self') and it[1][2] == _ddic.method_class))\
           ## and Is3(_ddic.method_class, 'AttributeInstance', it[2][1]):
            ## if _ddic.method_new_class: 
                ## ref = New(None, forcenewg)
                ## o.Stmt(ref, '=', 'PyDict_GetItem', '*self_dict', it[2])
                ## _ddic.self_dict_getattr_used = True
                ## return ref
            ## elif _ddic.method_old_class: 
                ## ref = New(None, forcenewg)
                ## o.Stmt(ref, '=', 'PyDict_GetItem', 'self_dict', it[2])
                ## _ddic.self_dict_getattr_used = True
                ## return ref
        ismeth = len (list(Iter3(None, ('Method', it[2][1]), None))) > 0
        if it[1][0] == 'FAST':
            isattrs = list(Iter3(None, 'AttributeInstance', it[2][1]))
            if not ismeth and len(isattrs) > 0 and it[1][1] in current_co.co_varnames and \
               current_co.co_varnames.index(it[1][1]) < current_co.co_argcount:
                s1 = ('STORE_FAST', it[1][1])
                s2 = ('DELETE_FAST', it[1][1])
                srepr = repr(_ddic.cmds[1])
                if not repr(s1) in srepr and not repr(s2) in srepr:
                    ref = New(None, forcenewg)
                    o.Raw('if (_' + it[1][1] + '_dict) {')
                    o.Raw('if ((',ref, ' = PyDict_GetItem(_', it[1][1], '_dict, ', it[2], ')) == 0) {')
                    o.Raw('PyErr_Format(PyExc_AttributeError, "Object has no attribute \'%s\'");' % it[2][1])
                    o.Raw('goto ', labl, ';')
                    UseLabl()
                    o.Raw('}')
                    o.INCREF(ref)
                    _ddic.dict_getattr_used[it[1][1]] = True
                    o.Raw('} else {')
                    o.Stmt(ref, '=', 'PyObject_GetAttr', it[1], it[2])
                    o.Raw('}')
                    return ref
        elif not ismeth and t is not None and Is3(t.subdescr, 'AttributeInstance', it[2][1]):
            if t.descr == T_OLD_CL_INST:
                if it[1][0] == 'CALC_CONST':
                    if Is3(it[1][1], 'ModuleAttr', '.__dict__'):
                        ref = New(None, forcenewg)
                        o.Stmt(ref, '=', 'PyDict_GetItem', calc_const_to((it[1][1], '.__dict__')), it[2])
                        return ref
                r = Expr1(it[1], o)
                ref = New(None, forcenewg)
                o.Stmt(ref, '=', 'PyDict_GetItem', '((PyInstanceObject *)' + CVar(r) + ')->in_dict', it[2])
                o.Cls(r)
                return ref
            elif t.descr == T_NEW_CL_INST:
                if it[1][0] == 'CALC_CONST':
                    if Is3(it[1][1], 'ModuleAttr', '.__dict__'):
                        ref = New(None, forcenewg)
                        o.Stmt(ref, '=', 'PyDict_GetItem', calc_const_to((it[1][1], '.__dict__')), it[2])
                        return ref

                r = Expr1(it[1], o)
                dic = New()
                o.Raw(dic, ' = *_PyObject_GetDictPtr(',r,');')
                o.INCREF(dic)
                o.Cls(r)
                ref = New(None, forcenewg)
                o.Stmt(ref, '=', 'PyDict_GetItem', dic, it[2])
                o.Cls(dic)
                return ref
        elif t is not None and t.descr is types.ModuleType:
            if t.subdescr is not None and ModuleHaveAttr(t.subdescr, it[2][1]):
                r = Expr1(it[1], o)
                ref = New(None, forcenewg)
                o.Raw('if ((', ref, ' = PyDict_GetItem(PyModule_GetDict(' + CVar(r) + '), ', it[2], ')) == NULL) goto ', labl, ';')
                o.INCREF(ref)
                o.Cls(r)
##                o.Raw('if (', ref, ' == NULL) goto ', labl, ';')
                UseLabl()
                return ref
    elif t is not None:
        Debug('Non-Generic GetAttr type', t, it[2], it[1])
    Debug('Standard Getattr', it)
    ref,attr = [Expr1(x, o) if type(x) is tuple and len(x) > 0 else x \
              for i,x in enumerate(it) if i > 0]
    newg = New(None, forcenewg)  
    o.Stmt(newg, '=', 'PyObject_GetAttr', ref, attr)
    o.Cls(ref,attr)
    return newg   
    
def IsAnyClass(nm):
    if Is3(nm, 'CalcConstOldClass') or Is3(nm, 'CalcConstNewClass'):
        return True
    return False

def GenExpr(it,o, forcenewg=None,typed=None, skip_float = None):
    global _n2c, g_acc2, g_refs2
    _v = []
 
    if forcenewg is not None and it[0] in tags_one_step_expr:
        Debug('Copy unhandled', forcenewg, '=', it)
    if TCmp(it, _v, ('!PyObject_Call', ('!PyObject_GetAttr', '?', ('CONST', '?')), '?', '?')):
        t = TypeExpr(_v[0])
        if t is not None and _v[3] == ('NULL',):
            if t not in _Kl_Simples and t.subdescr is not None:
                if IsAnyClass(t.subdescr) and not Is3(t.subdescr, ('Attribute', _v[1])):
                    if Is3(t.subdescr, 'AttributeInstance', _v[1]):       
                        pass
                    elif not Is3(t.subdescr, ('Method', _v[1])):       
                        Debug( 'Call UNKNOWN method known classes: %s -> %s' % (t, _v[1]),it)
                        ## if _v[1] == 'append':
                            ## Fatal('')
                    else:
                        HideDebug( 'Call method known classes: %s -> %s' % (t, _v[1]),it)
#        elif t is None:
#            Debug('Undefined class method', it)            
                
    for ind,x in enumerate(g_acc2):        
        if it == x:
            if it[0] == 'CONST' and type(x[1]) != type(it[1]):
                continue
            ind = g_acc2.index(it)
            if forcenewg is None or forcenewg == g_refs2[ind]:
                return g_refs2[ind]    
    if type(it) is int:
        return it
    head = it[0]
 
    if head == 'PY_TYPE':
        if typed is not None:
            Debug(typed, it[4], it)
            assert typed == it[4]
        if typed is None and it[4] is not None:
            Debug('Unhandled C-type', it)   
        if it[1] is float:    
            return GenExpr(it[3],o,forcenewg, typed, False)
        else:
            return GenExpr(it[3],o,forcenewg, typed, True)

    if not isinstance(head, types.StringTypes) and type(head) != int:
        pprint.pprint(head)
        pprint.pprint(it)
    assert isinstance(head, types.StringTypes) or type(head) is int
#    o.append('/*---*/')
    tempor = False    

    if head[0] == '!':
        tempor = True
        head = head[1:]
    elif head[0] == '=':
        head = 'INPLACE_' + head[1:]
        tempor = True    
    if not tempor:
        if len(it) > 1:
            if not head in tags_one_step_expr:
                Fatal('', it)
            assert head in tags_one_step_expr
        return it  
 
    if type(it) is tuple and len(it) == 3 and type(it[0]) is str and \
        type(it[1]) is tuple and len(it[1]) >= 1 and it[1][0] == 'CONST' and \
        type(it[2]) is tuple and len(it[2]) >= 1 and it[2][0] == 'CONST':
        if it[2] != ('CONST', 'join'):    
            Debug('Constant binary operation unhandled', it)
    if type(it) is tuple and len(it) == 2 and type(it[0]) is str and \
        type(it[1]) is tuple and len(it[1]) >= 1 and it[1][0] == 'CONST':            
        Debug('Constant unary operation unhandled', it)
 
    if tempor and head == 'LOAD_NAME':
        return GenExpr(('!c_LOAD_NAME', 'f', ('CONST', it[1])),o, forcenewg)
    if tempor and head == 'LOAD_GLOBAL' and it[1] not in d_built and it[1][0] != '_' and not redefined_all:
        ref = New(None, forcenewg)
        o.Raw('if((', ref, ' = PyDict_GetItem( glob, ', ('CONST', it[1]), ')) == 0) {')
        o.Raw('PyErr_Format(PyExc_NameError, GLOBAL_NAME_ERROR_MSG, ', '"%s"' % it[1], ');')
        o.Raw('goto ', labl, ';')
        UseLabl()
        o.Raw('}') 
        o.INCREF(ref)
        return ref
    
    if tempor and head == 'LOAD_GLOBAL':
        return GenExpr(('!c_LOAD_GLOBAL', ('CONST', it[1]), hash(it[1])),o, forcenewg)
    if tempor and head == 'LOAD_BUILTIN':
        tempor = False
        return ('BUILTIN', it[1])
    if head in ('OR_JUMPED_STACKED', 'AND_JUMPED_STACKED'):
        ref = forcenewg
        if ref is None:
            ref = New()
        return generate_and_or_jumped_stacked(it[1:], o, ref, head == 'AND_JUMPED_STACKED', 0)
    if head in ('AND_BOOLEAN', 'OR_BOOLEAN'):
        o1, logical = generate_logical_expr(it) 
        o.extend(o1)
        return logical

    if head in ('AND_JUMP', 'OR_JUMP'):
        o2,logic = shortage(generate_logical_expr(it))
        o.extend(o2)
        ref = New(None, forcenewg)
        o.Stmt(ref, '=','PyBool_FromLong', logic)
        o.Cls(logic)
        return ref

    if head == 'BUILD_TUPLE':
      li = []
      repeat_expr = False
      for x in it[1]:  
         g = Expr1(x, o)
         if not istempref(g):
             o.INCREF(g) 
         elif g in g_refs2:
             if repeat_expr:
                Fatal('Repeated expr', it)
                o.INCREF(g) 
             repeat_expr = True   
         li.append(g)    
      newg = New(None,forcenewg)  
      o.Stmt(newg,'=', 'PyTuple_New', len(it[1]))
      for i,g in enumerate(li):
         o.Stmt('PyTuple_SET_ITEM', newg, i, g)
         if g not in g_refs2:
            o.ZeroTemp(g)  
         o.ClsFict(g)
      return newg
    if head == 'GET_ITER':
        ref = Expr1(it[1], o)
        ref2 = New(None,forcenewg)
        o.Stmt(ref2, '=', 'PyObject_GetIter', ref)
        return ref2
 
    if head == 'PySequence_Repeat':
#### Trouble at count < 0 
        if it[1][0] == 'CONST' and type(it[1][1]) is str and\
           len(it[1][1]) == 1 and TypeExpr(it[2]) == Kl_Int:
            n2 = New('Py_ssize_t')
            if it[2][0] == 'CONST':
                o.Stmt(n2, '=', it[2][1])
                n = None
            else:   
                n = Expr1(it[2], o)
                o.Stmt(n2, '=', 'PyInt_AsSsize_t', n)
            ref2 = New(None,forcenewg)
            o.Raw('if (', n2, ' <= 0) {')
            o.Stmt(ref2, '=', 'PyString_FromStringAndSize', 'NULL', 0)
            if istempref(n):
                o.CLEAR(n)
            o.Raw('}')    
            cref = New('charref')
            o.Raw(cref, ' = PyMem_Malloc(', n2, ');')
            n1 = New('Py_ssize_t')
            sn1 = CVar(n1)
            o.Raw('for(', sn1, ' = 0; ', sn1, ' < ', n2, '; ', sn1, '++){')
            o.Raw(cref, '[', sn1, '] = ', str(ord(it[1][1])), ';')
            o.Raw('}')
            o.Stmt(ref2, '=', 'PyString_FromStringAndSize', cref, n2)
            o.Raw('PyMem_Free(', cref, ');')
            o.Cls(n1, n2, cref)
            if n is not None:
                o.Cls(n)
            return ref2
        if TypeExpr(it[2]) == Kl_Int:       
            ref = Expr1(it[1], o)
            n2 = New('Py_ssize_t')
            if it[2][0] == 'CONST':
                o.Stmt(n2, '=', it[2][1])
                n = None
            else:   
                n = Expr1(it[2], o)
                o.Stmt(n2, '=', 'PyInt_AsSsize_t', n)
            ref2 = New(None,forcenewg)
            o.Stmt(ref2, '=', 'PySequence_Repeat', ref, n2)
            o.Cls(ref)
            if n is not None:
                o.Cls(n)
            o.Cls(n2)
            return ref2
        ref1 = Expr1(it[1], o)
        ref2 = Expr1(it[2], o)

        if forcenewg is not None:
            new = forcenewg
        else:
            new = New()    
        o.Stmt(new, '=', 'PyNumber_Multiply', ref1, ref2)
        o.Cls(ref1, ref2)
        return new
        
    if head == 'BUILD_LIST':
      li = []
      repeat_expr = False
      for x in it[1]:  
         g = Expr1(x, o)
         if not istempref(g):
             o.INCREF(g) 
         elif g in g_refs2:
             if repeat_expr:
                Fatal('Repeated expr', it)
                o.INCREF(g) 
             repeat_expr = True   
         li.append(g)    
      newg = New(None,forcenewg)  
      o.Stmt(newg,'=', 'PyList_New', len(it[1]))
      for i,g in enumerate(li):
         o.Stmt('PyList_SET_ITEM', newg, i, g)
         if g not in g_refs2:
            o.ZeroTemp(g)  
         o.ClsFict(g)
      return newg

    if head == 'IMPORT_NAME':
        importer = Expr1(('!PyDict_GetItem', 'f->f_builtins', ('CONST', '__import__')),o)
        if it[2][0] == 'CONST' and it[2][1] == -1:
            it3 = it[3]
            if it3 == ('CONST', None):
                it3 = ('Py_None',)
            tupl = ('!BUILD_TUPLE', ( ('CONST',it[1]), \
                                     ('glob',), \
                                     ('f->f_locals == NULL ? Py_None : f->f_locals',),\
                                        it3))  

        else:        
            tupl = ('!BUILD_TUPLE', ( ('CONST',it[1]), \
                                     ('glob',), \
                                     ('f->f_locals == NULL ? Py_None : f->f_locals',),\
                                        it[3], it[2]))  
        arg = Expr1(tupl,o)
        ret = Expr1(('!PyEval_CallObject', importer, arg),o )   
        o.Cls(arg, importer)
        return ret

    if head == 'BUILD_SET':
      newg = New(None, forcenewg)  
      o.Stmt(newg,'=', 'PySet_New', 'NULL') 
      for v in it[1]:
          v = Expr1(v, o)
          o.Stmt('PySet_Add', newg, v)
          o.Cls(v)
      return newg    
        
    if head == 'BUILD_MAP':
      newg = New(None, forcenewg)  
      if len(it[1]) > 5:
        o.Stmt(newg,'=', '_PyDict_NewPresized', len(it[1])) 
      else:
        o.Stmt(newg,'=', 'PyDict_New') 
      for k, v in it[1]:
          k = Expr1(k, o)
          v = Expr1(v, o)
          o.Stmt('PyDict_SetItem', newg, k, v)
          o.Cls(k, v)
      return newg
    if head == 'MK_CLOSURE':
        assert len(it) == 4
        co = _n2c[it[1]]
        if not can_generate_c(co): ## co.co_flags & CO_GENERATOR:
            ref1 = New()
            o.Stmt(ref1, '=', 'PyFunction_New', const_to(co), 'glob')
            ref2 = Expr1(it[2], o)
            o.Stmt('PyFunction_SetClosure', ref1, ref2)
            o.Cls(ref2)
            if it[3][0] == 'CONST' and type(it[3][1]) is tuple:
                if len(it[3][1]) > 0:
                    o.Stmt('PyFunction_SetDefaults', ref1, it[3])
                return ref1
            if it[3][0] == '!BUILD_TUPLE' and type(it[3][1]) is tuple:
                ref2 = Expr1(it[3], o)
                o.Stmt('PyFunction_SetDefaults', ref1, ref2)
                o.Cls(ref2)
                return ref1
            Fatal('GenExpr', it)

        ref1 = New()
        o.Stmt(ref1, '=', 'Py2CFunction_New', const_to( _n2c[it[1]]))
        ref2 = Expr1(it[2], o)
        o.Stmt('Py2CFunction_SetClosure', ref1, ref2)
        o.Cls(ref2)
        if it[3][0] == 'CONST' and type(it[3][1]) is tuple:
            if len(it[3][1]) > 0:
                o.Stmt('Py2CFunction_SetDefaults', ref1, it[3])
            return ref1
        if it[3][0] == '!BUILD_TUPLE' and type(it[3][1]) is tuple:
            ref2 = Expr1(it[3], o)
            o.Stmt('Py2CFunction_SetDefaults', ref1, ref2)
            o.Cls(ref2)
            return ref1
        Fatal('GenExpr', it)
    if head == 'LOAD_CLOSURE':
        return ('LOAD_CLOSURE', it[1])    
    if head == 'LOAD_DEREF':
        return GenExpr(('!PyCell_Get',('LOAD_CLOSURE', it[1])), o, forcenewg, typed)
    if head == 'MK_FUNK':
        co = _n2c[it[1]]
        if not can_generate_c(co):
            if len(it) == 3 and it[2][0] == 'CONST' and type(it[2][1]) is tuple:
                ref1 = New(None, forcenewg)
                if len(it[2][1]) > 0: # or len(co.co_cellvars + co.co_freevars) != 0:
                    o.Stmt(ref1, '=', 'PyFunction_New', const_to(co), 'glob')
                    o.Stmt('PyFunction_SetDefaults', ref1, it[2])
                else:
                    o.Stmt(ref1, '=', 'PyFunction_New', const_to( co), 'glob')
                        
                return ref1
            if len(it) == 3 and it[2][0] == '!BUILD_TUPLE' and type(it[2][1]) is tuple:
                ref1 = New(None, forcenewg)
                o.Stmt(ref1, '=', 'PyFunction_New', const_to(co), 'glob')
                ref2 = Expr1(it[2], o)
                o.Stmt('PyFunction_SetDefaults', ref1, ref2)
                o.Cls(ref2)
                return ref1
            Fatal('GenExpr', it)
            return None

        if len(it) == 3 and it[2][0] == 'CONST' and type(it[2][1]) is tuple:
            ref1 = New(None, forcenewg)
            if len(it[2][1]) > 0: # or len(co.co_cellvars + co.co_freevars) != 0:
                o.Stmt(ref1, '=', 'Py2CFunction_New', const_to( co))
                o.Stmt('Py2CFunction_SetDefaults', ref1, it[2])
            else:
                o.Stmt(ref1, '=', 'Py2CFunction_New', const_to( co))
                    
            return ref1
        if len(it) == 3 and it[2][0] == '!BUILD_TUPLE' and type(it[2][1]) is tuple:
            ref1 = New(None, forcenewg)
            o.Stmt(ref1, '=', 'Py2CFunction_New', const_to(co))
            ref2 = Expr1(it[2], o)
            o.Stmt('Py2CFunction_SetDefaults', ref1, ref2)
            o.Cls(ref2)
            return ref1
        Fatal('GenExpr', it)

    if head == 'BINARY_SUBSCR_Int':
        ref = Expr1(it[1], o)
        ref1 = New(None, forcenewg)
        t = TypeExpr(it[1])
        islist = t == Kl_List
        if expand_BINARY_SUBSCR or islist:
            if not islist:
                o.Stmt('if (PyList_CheckExact(', ref, ')) {')
            if it[2][1] >= 0:
                o.Stmt(ref1, '=', 'PyList_GetItem', ref, it[2][1])
            else:
                o.Stmt(ref1, '=', 'PyList_GetItem', ref, 'PyList_GET_SIZE(' + CVar(ref) + ') ' + str(it[2][1]))
            if not islist:
                o.Raw('} else {')
                o.Stmt(ref1, '=', 'PyObject_GetItem', ref, it[2])
                o.Raw('}')
        elif t == Kl_Dict:        
            ref2 = Expr1(it[2], o)
            o.Raw('if((', ref1, ' = PyDict_GetItem(', ref, ', ', ref2, ')) == 0) {')
            tup = New()
            o.Raw('if (!(', tup, ' = PyTuple_Pack(1, ', ref2, '))) goto ', labl, ';') 
            o.Raw('PyErr_SetObject(PyExc_KeyError, ', tup, ');')
            o.Cls(tup)            
            o.Raw('goto ', labl, ';')
            UseLabl()
            o.Raw('}') 
            o.INCREF(ref1)
            o.Cls(ref, ref2)
            return ref1
        elif t == Kl_Tuple:        
            if it[2][1] >= 0:
                o.Stmt(ref1, '=', 'PyTuple_GetItem', ref, it[2][1])
            else:
                o.Stmt(ref1, '=', 'PyTuple_GetItem', ref, 'PyTuple_GET_SIZE(' + CVar(ref) + ') ' + str(it[2][1]))
        elif t == Kl_String: # after. Too many low-lewel code.
            o.Stmt(ref1, '=', 'PyObject_GetItem', ref, it[2])
        else:
            if t is not None and t != Kl_Buffer:
                Debug('not None', it, t)
                o.Stmt(ref1, '=', 'PyObject_GetItem', ref, it[2])
            else:    
                o.Stmt(ref1, '=', '_c_BINARY_SUBSCR_Int', ref, it[2][1], it[2])
        o.Cls(ref)
        return ref1
    if head == 'from_ceval_BINARY_SUBSCR' and it[2][0] == '!PyInt_FromSsize_t':
        t = TypeExpr(it[1])
        islist = t == Kl_List
        if not islist and t is not None:
            pprint.pprint(('not islist', it, t))

        ref = Expr1(it[1], o)
        ref1 = New(None, forcenewg)
        if not islist:
            o.Stmt('if (PyList_CheckExact(', ref, ')) {')
        o.Stmt(ref1, '=', 'PyList_GetItem', ref, it[2][1])
        if not islist:
            o.Raw('} else {')
            ref2 = Expr1(it[2],o)
            o.Stmt(ref1, '=', 'PyObject_GetItem', ref, ref2)
            o.Cls(ref2)
            o.Raw('}')
        o.Cls(ref)
        return ref1
    if head == 'from_ceval_BINARY_SUBSCR' and it[2][0] == '!@PyInt_FromSsize_t':
##        print '/5'
        t = TypeExpr(it[1])
        islist = t == Kl_List
        if not islist and t is not None and t != Kl_Dict and t != Kl_Tuple:
            pprint.pprint(('not islist? is notdict', it, t))
        ref = Expr1(it[1], o)
        ref1 = New(None, forcenewg)
        if t == Kl_Dict:
            ref2 = Expr1(it[2][2], o)
            o.Raw('if((', ref1, ' = PyDict_GetItem(', ref, ', ', ref2, ')) == 0) {')
            tup = New()
            o.Raw('if (!(', tup, ' = PyTuple_Pack(1, ', ref2, '))) goto ', labl, ';') 
            o.Raw('PyErr_SetObject(PyExc_KeyError, ', tup, ');')
            o.Cls(tup)            
            o.Raw('goto ', labl, ';')
            UseLabl()
            o.Raw('}') 
            o.INCREF(ref1)
            o.Cls(ref, ref2)
            return ref1
            
            return ref1
        if t == Kl_Tuple:
            o.Stmt(ref1, '=', 'PyTuple_GetItem', ref, it[2][1])
            o.Cls(ref)
            return ref1
        elif expand_BINARY_SUBSCR or islist: 
            if not islist:
                o.Stmt('if (PyList_CheckExact(', ref, ')) {')
            o.Stmt(ref1, '=', 'PyList_GetItem', ref, it[2][1])
            if not islist:
                o.Raw('} else {')
                ref2 = Expr1(it[2][2],o)
                o.Stmt(ref1, '=', 'PyObject_GetItem', ref, ref2)
                o.Cls(ref2)
                o.Raw('}')
        else:    
            ref2 = Expr1(it[2][2],o)
            o.Stmt(ref1, '=', '_c_BINARY_SUBSCR_Int', ref, it[2][1], ref2)
            o.Cls(ref2)
        o.Cls(ref)
        return ref1
    if head == 'from_ceval_BINARY_SUBSCR' and TypeExpr(it[1]) == Kl_List:
        ty_ind = TypeExpr(it[2])
        ref0, ref1 = Expr(o, it[1:3])
        ref = New(None, forcenewg)
        ind = None
        if ty_ind is None or IsInt(ty_ind):    
            ind = New('long')
        if ty_ind is None:
            o.Raw('if (PyInt_CheckExact(', ref1, ')) {')
        if ty_ind is None or IsInt(ty_ind):    
            o.Stmt(ind, '=', 'PyInt_AsLong', ref1)
            o.Stmt('if (', ind, '< 0) {')
            o.Raw(ind, ' += PyList_GET_SIZE(', ref0, ');')
            o.Raw('}')
            o.Stmt(ref, '=', 'PyList_GetItem', ref0, ind)
            o.Cls(ind)
        if ty_ind is None:
            o.Raw('} else {')
        if not IsInt(ty_ind):
            o.Stmt(ref, '=', 'PyObject_GetItem', ref0, ref1)
        if ty_ind is None:
            o.Raw('}')
        o.Cls(ref1)
        o.Cls(ref0)
        return ref
    if head == 'c_BINARY_SUBSCR_ADDED_INT' and TypeExpr(it[1]) == Kl_List and IsInt(TypeExpr(it[2])):
        ref0, ref1 = Expr(o, it[1:3])
        ref = New(None, forcenewg)
        ind = New('long')
        o.Stmt(ind, '=', 'PyInt_AsLong', ref1)
        o.Cls(ref1)
        o.Stmt(ind, '=', ind, '+', it[3])
        o.Stmt(ref, '=', 'PyList_GetItem', ref0, ind)
        o.Cls(ind, ref0)
        return ref

    if head == 'from_ceval_BINARY_SUBSCR' and TypeExpr(it[1]) == Kl_Dict:
        ref0, ref1 = Expr(o, it[1:3])
        ref = New(None, forcenewg)
        o.Raw('if((', ref, ' = PyDict_GetItem(', ref0, ', ', ref1, ')) == 0) {')
        ## o.Raw(ref, ' = PyDict_GetItem( ', ref0, ', ', ref1, ');')
        ## o.Raw('if(', ref, '== 0) {')
        tup = New()
        o.Raw('if (!(', tup, ' = PyTuple_Pack(1, ', ref1, '))) goto ', labl, ';') 
        ## o.Raw(tup, ' = PyTuple_Pack(1, ', ref1, ');')
        ## o.Raw('if (!', tup, ') goto ', labl, ';') 
        o.Raw('PyErr_SetObject(PyExc_KeyError, ', tup, ');')
        o.Cls(tup)            
        o.Raw('goto ', labl, ';')
        UseLabl()
        o.Raw('}') 

##        o.append('if 
        o.INCREF(ref)
        o.Cls(ref0, ref1)
        return ref
    if head == '_PyString_StartSwith' and TypeExpr(it[1]) == Kl_String:
        ref0 = Expr1(it[1], o)
        s_l, s_ref, ref = New('int'), New('charref'), New(None, forcenewg)
        o.Stmt('PyString_AsStringAndSize', ref0, ('&', s_ref), ('&', s_l))
        cond = CVar(s_l) + ' >= ' + str(len(it[2]))
        cond += ' && 0 == memcmp(' + Str_for_C(it[2]) + ', ' + CVar(s_ref) + ', ' + str(len(it[2])) + ')'
        o.Stmt(ref, '=', 'PyBool_FromLong', cond) 
        o.Cls(s_l, s_ref, ref0)
        return ref
    if head == 'PyObject_Hash':
        ref1 = Expr1(it[1], o)
        long = New('long')  
        o.Stmt(long, '=', head, ref1)
        o.Cls(ref1)
        newg = New(typed, forcenewg)  
        o.Stmt(newg, '=', 'PyInt_FromLong', long)
        o.Cls(long)
        return newg
    if head == '_PyObject_Cmp':
        ref1 = Expr1(it[1], o)
        ref2 = Expr1(it[2], o)
        lon = New('int')  
        o.Stmt('PyObject_Cmp', ref1, ref2, ('&', lon))
        o.Cls(ref1, ref2)
        newg = New(typed, forcenewg)  
        o.Stmt(newg, '=', 'PyInt_FromLong', lon)
        o.Cls(lon)
        return newg
    if head == '_PyString_EndSwith' and TypeExpr(it[1]) == Kl_String:
        ref0 = Expr1(it[1], o)
        s_l, s_ref, ref = New('int'), New('charref'), New(None, forcenewg)
        o.Stmt('PyString_AsStringAndSize', ref0, ('&', s_ref), ('&', s_l))
        cond = CVar(s_l) + ' >= ' + str(len(it[2]))
        s_i2, s_ref2 = New('int'), New('charref')
        o.Stmt(s_i2, '=', s_l, '-', len(it[2]))
        o.Stmt(s_ref2, '=', s_ref, '+', s_i2)
        cond += ' && 0 == memcmp(' + Str_for_C(it[2]) + ', ' + CVar(s_ref2) + ', ' + str(len(it[2])) + ')'
        o.Stmt(ref, '=', 'PyBool_FromLong', cond) 
        o.Cls(s_l, s_ref, ref0, s_i2, s_ref2)
        return ref
    if head == '_PyList_Pop':
        assert TypeExpr(it[1]) == Kl_List
        ref0 = Expr1(it[1], o)
        ref = New(None, forcenewg)
        if len(it) == 3:
            if it[2][0] == 'CONST':
                ind1 = New('long')
                if it[2][1] < 0:
                    o.Raw(ind1, ' = PyList_GET_SIZE(', ref0, ') - ', abs(it[2][1]), ';')
                else:    
                    o.Stmt(ind1, '=', it[2][1])
            else:
                o2,ind1 = shortage(generate_ssize_t_expr(it[2]))
                o.extend(o2)
                if not istemptyped(ind1):
                    ind_ = New('long')
                    o.Raw(ind_, ' = ', ind1, ';')
                    ind1 = ind_
                o.Stmt('if (', ind1, '< 0) {')
                o.Raw(ind1, ' += PyList_GET_SIZE(', ref0, ');')
                o.Raw('}')                        
        elif len(it) == 2:        
            ind1 = New('long')
            o.Raw(ind1, ' = PyList_GET_SIZE(', ref0, ') - 1;')
        o.Stmt(ref, '=', 'PyList_GetItem', ref0, ind1)
        ind2 = New('long')
        o.Stmt(ind2, '=', ind1, '+', 1)
#        o.Stmt(ind2, '+=', 1)
        o.Stmt('PyList_SetSlice', ref0, ind1, ind2, 'NULL')
        o.Cls(ind1, ind2, ref0)
        return ref

    if head == '_PyDict_Get' and TypeExpr(it[1]) == Kl_Dict:
        ref0, ref1 = Expr(o, it[1:3])
        ref = New(None, forcenewg)
        if istempref(ref):
            o.Raw(ref, ' =  PyDict_GetItem(', ref0, ', ', ref1, ');')
            o.Raw('if (', ref, ' == NULL) {') 
#            print 'll', ref, it[3]
            ref3 = GenExpr(it[3], o, ref)
            if istempref(ref3) and istempref(ref) and ref3 != ref:
                Fatal('Not eq tempref', it, ref3, ref, it[3])
            elif ref3 != ref:
                o.Raw(ref, ' = ', ref3, ';')
                o.INCREF(ref)        
            o.Raw('} else {')
            o.INCREF(ref)        
            o.Raw('}')
            if ref3 != ref:
                o.Cls(ref3)
        else:
            Fatal('', it)
#        o.append
        o.Cls(ref0, ref1)
        return ref

    if head == 'PyObject_GetAttr':
        return generate_GetAttr(it,o, forcenewg, typed)

    if head == 'PyObject_GetAttr3':
        t = TypeExpr(it[1])
        if t is not None:
            Debug('Typed GetAttr3', t, it)
        ref0, ref1 = Expr(o, it[1:3])
        ref = New(None, forcenewg)
        if istempref(ref):
            o.Raw(ref, ' = PyObject_GetAttr(', ref0, ', ', ref1, ');')
            o.Cls(ref0, ref1)
            o.Raw('if (', ref, ' == NULL && PyErr_ExceptionMatches(PyExc_AttributeError)) {')
            o.Raw('PyErr_Clear();')
            ref3 = GenExpr(it[3], o, ref)
            if istempref(ref3) and istempref(ref) and ref3 != ref:
                Fatal('Not eq tempref', it, ref3, ref)
            elif ref3 != ref:
                o.Raw(ref, ' = ', ref3, ';')
                o.INCREF(ref)        
#            o.append('Py_INCREF(' + CVar(ref) + ');')        
            if ref3 != ref:
                o.Cls(ref3)
            o.Raw('}')
        else:
            Fatal('', it)
##        o.append
        return ref

    if head == 'from_ceval_BINARY_SUBSCR' and TypeExpr(it[1]) == Kl_Tuple:
        ty_ind = TypeExpr(it[2])
        ref0, ref1 = Expr(o, it[1:3])
        ref = New(None, forcenewg)
        ind = None
        if ty_ind is None or IsInt(ty_ind):    
            ind = New('long')
        if ty_ind is None:
            o.Raw('if (PyInt_CheckExact(', ref1, ')) {')
        if ty_ind is None or IsInt(ty_ind):    
            o.Stmt(ind, '=', 'PyInt_AsLong', ref1)
            o.Stmt('if (', ind, '< 0) {')
            o.Raw(ind, ' += PyTuple_GET_SIZE(',ref0,');')
            o.Raw('}')
            o.Cls(ref1)
            o.Stmt(ref, '=', 'PyTuple_GetItem', ref0, ind)
            o.Cls(ind)
        if ty_ind is None:
            o.Raw('} else {')
        if not IsInt(ty_ind):
            o.Stmt(ref, '=', 'PyObject_GetItem', ref0, ref1)
        if ty_ind is None:
            o.Raw('}')
        o.Cls(ref1)
        o.Cls(ref0)
        return ref
    if head == 'from_ceval_BINARY_SUBSCR' and TypeExpr(it[1]) == Kl_String:
        return standart_BINARY_SUBSCR(it, o, forcenewg)
    if head == 'from_ceval_BINARY_SUBSCR':
        t = TypeExpr(it[1]) 
        if t is not None:
            if t.descr in ('NewClassInstance', 'OldClassInstance'):
                return standart_BINARY_SUBSCR(it, o, forcenewg)
            Debug('Typed BINARY_SUBSCR not specialised: %s ( %s, %s )' % (head, t, TypeExpr(it[2])), it)
    if head == 'c_BINARY_SUBSCR_ADDED_INT' and TypeExpr(it[1]) is not None:
        Fatal('GenExpr', it)
    if head == '@PyInt_FromSsize_t':
##        print '/1', it[2]
        return GenExpr(it[2],o, forcenewg)
        
    if head in ('c_PyCmp_EQ_Int', 'c_PyCmp_NE_Int', 'c_PyCmp_LT_Int', 'c_PyCmp_LE_Int', 'c_PyCmp_GT_Int', 'c_PyCmp_GE_Int'):
        ref = Expr1(it[1], o)
        int_2 = 'NULL'
        t = TypeExpr(it[1])
        if t is not None:
            Debug('typed compare', t,it)
        if type(it[2]) is int:
            int_t = it[2] 
            int_2 = const_to(int_t)   
        elif it[2][0] == 'CONST' and type(it[2][1]) is int:
            int_t = it[2][1]    
            int_2 = const_to(int_t)   
        elif it[2][0] in ('!PY_SSIZE_T',):
            int_t = GenExpr(it[2][1],o, forcenewg, 'Py_ssize_t')
        else:
            Fatal('CMP', it)
        newg = New('int')    
        o.Stmt(newg,'=', head, ref, int_t, int_2)
        o.Cls(ref, int_t)
        return newg
    if head == 'CHR_BUILTIN':
        t = TypeExpr(it[1])
        if not IsNoneOrInt(t):
            Fatal('Illegal typed CHR', t, it)
        ref = Expr1(it[1],o)
        Long = New('long')
        o.Stmt(Long, '=', 'PyInt_AsLong', ref)
        o.Cls(ref)
        o.Stmt('if (', Long, ' < 0 || ', Long, ' >= 256) {')
        o.Raw('PyErr_SetString(PyExc_ValueError, \"chr() arg not in range(256)\");')
        o.Raw('goto ', labl, ';')
        UseLabl()
        o.Raw('}')
        o.Raw('{')
        o.Raw('char __s[1];')        
        o.Raw('__s[0] = (char)', Long, ';')
        ref = New(None, forcenewg)
        o.Stmt(ref, '=', 'PyString_FromStringAndSize', '__s', '1')        
        o.Raw('}')
        o.Cls(Long)
        return ref    
    if head == 'ORD_BUILTIN':
        t = TypeExpr(it[1])
        if t != Kl_String:
            if t is not None:
                Debug('typed ORD', t, it)
            ## else:
                ## Debug('Untyped ORD', it[1], it)    
        ref = Expr1(it[1],o)
        Long = New('long')
        ref2 = New(None, forcenewg)
        if t == Kl_String:
            o.Stmt('if (PyString_CheckExact(', ref, ') && PyString_GET_SIZE(', ref,') == 1) {')
            o.Raw(Long, ' = (long)((unsigned char)*PyString_AS_STRING(', ref, '));')
            o.Stmt(ref2, '=', 'PyInt_FromLong', Long)
            o.Raw('} else {') 
            GenExpr(('!PyCFunction_Call', (load_builtin('ord'),), ('!BUILD_TUPLE', (ref,)), ('NULL',)), o, ref2)
            o.Raw('}')
            o.Cls(Long, ref)
            if istempref(ref):
                o.Raw('Py_CLEAR(', ref, ');')
            return ref2 

        o.Stmt('if (PyString_Check(', ref, ') && PyString_GET_SIZE(', ref,') == 1) {')
        o.Raw(Long, ' = (long)((unsigned char)*PyString_AS_STRING(', ref, '));')
        o.Stmt(ref2, '=', 'PyInt_FromLong', Long)
        o.Stmt('} else if (PyByteArray_Check(', ref, ') && PyByteArray_GET_SIZE(', ref,') == 1) {')
        o.Raw(Long, ' = (long)((unsigned char)*PyByteArray_AS_STRING(', ref, '));')
        o.Stmt(ref2, '=', 'PyInt_FromLong', Long)
        o.Stmt('} else if (PyUnicode_Check(', ref, ') && PyUnicode_GET_SIZE(', ref,') == 1) {')
        o.Raw(Long, ' = (long)((wchar_t)*PyUnicode_AS_UNICODE(', ref, '));')
        o.Stmt(ref2, '=', 'PyInt_FromLong', Long)
        o.Raw('} else {') 
        GenExpr(('!PyCFunction_Call', (load_builtin('ord'),), ('!BUILD_TUPLE', (ref,)), ('NULL',)), o, ref2)
        o.Raw('}')
        o.Cls(Long, ref)
        if istempref(ref):
           o.Raw('Py_CLEAR(', ref, ');')
        return ref2 
    if head == 'PY_SSIZE_T':
        o2,size_t = shortage(generate_ssize_t_expr(it[1]))
        o.extend(o2)
        if type(size_t) is int:
            return ('CONST', size_t)
        ref = New(None, forcenewg)
        o.Stmt(ref, '=', 'PyInt_FromSsize_t', size_t)
        o.Cls(size_t)
        return ref     
    if head == 'STR_CONCAT':
        if len(it) == 4:
            return GenExpr(('!STR_CONCAT3', it[1], it[2], it[3]), o, forcenewg)
        elif len(it) == 3:
            return GenExpr(('!STR_CONCAT2', it[1], it[2]), o, forcenewg)
        elif len(it) > 4:
            return GenExpr(('!STR_CONCAT3', it[1], it[2],('!STR_CONCAT',) + it[3:]), o, forcenewg)
        else:
            Fatal('GenExpr', it)
    if head == 'LIST_COMPR':
        assert len(it) == 3
#        print it
        return generate_list_compr(it[1],it[2],o, forcenewg)  
    if head == 'SET_COMPR':
        assert len(it) == 3
#        print it
        return generate_set_compr(it[1],it[2],o, forcenewg)  
    if head == 'MAP_COMPR':
        assert len(it) == 3
#        print it
        return generate_map_compr(it[1],it[2],o, forcenewg)  
    if head == 'BOOLEAN':
        o2,logic = shortage(generate_logical_expr(it[1]))
        o.extend(o2)
        ref = New(None, forcenewg)
        o.Stmt(ref, '=','PyBool_FromLong', logic)
        o.Cls(logic)
        return ref
    if head == '1NOT' and it[1][0] == '!BOOLEAN':
        o1, int_val = shortage(generate_logical_expr(it[1]))
        o.extend(o1)
        ref = New(None, forcenewg)
        o.Stmt(ref, '=','PyBool_FromLong', ConC('!(', int_val, ')'))
        o.Cls(int_val)
        return ref

    if head in ('_EQ_', '_NEQ_'):
        Fatal('GenExpr', it)
    if head == 'AND_BOOLEAN':
        Fatal('GenExpr', it)
    if head == '1NOT':
        ref1 = Expr1(it[1], o)
        int_r = New('int')
        o.Stmt(int_r, '=', 'PyObject_Not', ref1)
        o.Cls(ref1)
        ref = New(None, forcenewg)
        o.Stmt('if (', int_r, '== 1) {')
        o.Stmt(ref, '=', 'Py_True')
        o.Raw('} else {')
        o.Stmt(ref, '=', 'Py_False')
        o.Raw('}')
        o.Cls(int_r)
        o.INCREF(ref)
        return ref
    if head == '$PyDict_SymmetricUpdate':
        if it[1][0] == '!BUILD_MAP':
            ref1, ref2 = Expr(o, it[1:3])
            o.Stmt('PyDict_Update', ref1, ref2)
            o.Cls(ref2)
            return ref1
        Fatal('GenExpr', it)
    if head == 'CLASS_CALC_CONST':
        ref = New(None, forcenewg)
        ref1 = Expr1(it[2], o)
        o.Stmt(ref, '=', 'PyInstance_New', ('CALC_CONST',it[1]), ref1, 'NULL')
        o.Cls(ref1)
        return ref
    if head == 'CLASS_CALC_CONST_DIRECT':
        ref = New(None, forcenewg)
#        ref1 = Expr1(it[2], o)
        o.Stmt(ref, '=', 'PyInstance_NewRaw', ('CALC_CONST',it[1]), 'NULL')
        if it[3][0] == 'CONST':
            tup = tuple([('CONST', x) for x in it[3][1]])
        else:
            tup = it[3][1]    
        PushAcc([ref],[ref])
        ref2 = Expr1(('!CALL_CALC_CONST', it[2], ('!BUILD_TUPLE', (ref,) + tup)), o)
        PopAcc(o, False)
        o.Raw('assert(', ref2, ' == Py_None);')
        o.Cls(ref2)
        return ref
    if head == 'CLASS_CALC_CONST_NEW':
#        ref = New(None, forcenewg)
        ref = GenExpr(('!PyObject_Call', ('CALC_CONST', it[1]), it[2], ('NULL',)), o, forcenewg)
#        o.Stmt(ref, '=', 'PyInstance_New', ('CALC_CONST',it[1]), ref1, 'NULL')
#        o.Cls(ref1)
        return ref
    ## if head == 'CLASS_CALC_CONST_NEW_DIRECT':
        ## if it[3][0] == 'CONST':
            ## tup = tuple([('CONST', x) for x in it[3][1]])
        ## else:
            ## tup = it[3][1]    
        ## args = Expr1(('!BUILD_TUPLE', (('CALC_CONST',it[1]),) + tup), o)
        ## ref = New(None, forcenewg)
        ## o.Raw(ref, ' = ((PyTypeObject *)', ('CALC_CONST',it[1]), ')->tp_new( ((PyTypeObject *)', ('CALC_CONST',it[1]), '), ', args, ', NULL);')
        ## o.Raw('if (', ref, ' == NULL) goto ', labl, ';')
        ## UseLabl()
        ## o.Raw('if (PyType_IsSubtype(', ref, '->ob_type, (PyTypeObject *)', ('CALC_CONST',it[1]), ')) {')
        ## PushAcc([ref],[ref])
        ## ref2 = Expr1(('!CALL_CALC_CONST', it[2], ('!BUILD_TUPLE', (ref,) + tup)), o)
        ## PopAcc(o, False)
        ## o.Raw('assert(', ref2, ' == Py_None);')
        ## o.Cls(ref2)
        ## o.Raw('}')
        ## return ref

    if head == 'CALL_CALC_CONST':
        d_nm = '_Direct_' + it[1]
        is_const_default = True
        if it[1] in default_args and default_args[it[1]][0] != 'CONST':
            is_const_default = False
        if it[2] == ('CONST', ()):
            refs = []
        elif it[2][0] == '!BUILD_TUPLE':
            refs = Expr(o, it[2][1])
        elif it[2][0] == 'CONST':
            refs = [('CONST', x) for x in it[2][1]]
        else:
            Fatal('GenExpr', it)
        co = N2C(it[1])    
        argcount = co.co_argcount
        is_varargs = co.co_flags & 0x4
        hidden = all_co[co].hidden_arg_direct
        if not is_varargs:
            if argcount != len(refs):
                if argcount > len(refs):
                    if it[1] in default_args:
                        if is_const_default:
                            _refs2 = [('CONST', x) for x in default_args[it[1]][1]]
                        else:
                            _refs2 = [Expr1(x, o) for x in default_args[it[1]][1]]
                        add_args = argcount - len(refs)
                        pos_args = len(_refs2) - add_args
                        refs = refs + _refs2[pos_args:]
        else: 
            assert len(hidden) == 0
            if argcount > len(refs):
                if it[1] in default_args:
                    if is_const_default:
                        _refs2 = [('CONST', x) for x in default_args[it[1]][1]]
                    else:
                        print '/111 !!', 'Strange default value', default_args[it[1]]
                        _refs2 = [Expr1(x, o) for x in default_args[it[1]]]
                    add_args = argcount - len(refs)
                    pos_args = len(_refs2) - add_args
                    refs = refs + _refs2[pos_args:]
            rargs = refs[:argcount]
            rtupl = refs[argcount:]
            rtupl2 = Expr1(('!BUILD_TUPLE', tuple(rtupl)), o)
            argcount += 1
            refs = rargs + [rtupl2]
        ## if not len(refs) == argcount:
            ## Debug(len(refs), argcount, refs, it)    
        assert len(refs) == argcount      
        _refs2 = []
        for i,x in enumerate(refs):              
            if i not in hidden:
                _refs2.append(x)
        if not IsRetVoid(it[1]):        
            ref = New(None, forcenewg)
            tupl = (ref, '=', d_nm) + tuple(_refs2)
            o.Stmt(*tupl)
            if len(_refs2) > 0:
                o.Cls(*_refs2)
                ## for r in _refs2:
                ## o.Cls(r)
            return ref
        else:
            tupl = (d_nm,) + tuple(_refs2)
            li = ['if (',d_nm, '(']
            for i, re in enumerate(_refs2):
                if i > 0:
                    li.append(', ')
                li.append(re)
            li.append(') == -1) goto ')
            li.append(labl)
            li.append(';')
            UseLabl()
            tupl = tuple(li)    
            o.Raw(*tupl)
            if len(_refs2) > 0:
                o.Cls(*_refs2)
                ## for r in _refs2:
                ## o.Cls(r)
            return ('CONST', None)

    if head == 'CALL_CALC_CONST_INDIRECT':
        d_nm = 'codefunc_' + it[1]
        is_const_default = True
        ref = New(None, forcenewg)
        if it[2] == ('CONST', ()):
            refs = []
        elif it[2][0] == '!BUILD_TUPLE':
            refs = Expr(o, it[2][1])
        elif it[2][0] == 'CONST':
            refs = [('CONST', x) for x in it[2][1]]
        else:
            Fatal('GenExpr', it)
        co = N2C(it[1])    
        argcount = co.co_argcount
        assert len(refs) == argcount      
        tupl = (ref, ' = _Call_CompiledWithFrame(', d_nm, ', ', const_to(co), ', ', argcount)
        Used('_Call_CompiledWithFrame')
        for _r in refs:
            tupl = tupl + (', ', _r)
        tupl = tupl + (')',)    
        tupl = ('if ((',) + tupl + (') == NULL) goto ', labl, ';') 
        o.Raw(*tupl)
#        o.Raw('if (', ref, ' == NULL) goto ', labl, ';')
        UseLabl()
        if len(refs) > 0:
            o.Cls(*refs)
        return ref



            
    if head == 'PyObject_Call':
        if it[3] == 'NULL' or (len(it[3]) == 1 and it[3][0] == 'NULL'):
            return generate_PyObject_Call_nokey(it, o, forcenewg)

    if head.startswith('PyNumber_'):
        return GenNumberExpr(it, o, forcenewg, typed, skip_float)
    if head == '?Raise':
        gen = [Expr1(x, o) if type(x) is tuple and len(x) > 0 else x \
                for i,x in enumerate(it) if i > 2]
        o.Cls(*gen)

        refn = [('BUILTIN', 'ZeroDivisionError'), ('CONST', "division by 0"), 'NULL']
        o.Stmt('_PyEval_DoRaise', refn[0], refn[1], refn[2])
        if refn[0] != 'NULL':
             o.INCREF(refn[0])
        if refn[1] != 'NULL':
            o.INCREF(refn[1])
        if refn[2] != 'NULL':
            o.INCREF(refn[2])        
#        if istempref(refn[0]):
#        o.INCREF(refn[0])
        o.Cls(*refn)
        o.Stmt('goto', labl)
        UseLabl()
        
        ## o += 'PyErr_SetString(PyExc_ZeroDivisionError, "division by 0");'
        ## o.Stmt('goto', labl)
        ## UseLabl()
        return ('CONST', None)
    if head == 'COND_EXPR':
        o1, logic = shortage(generate_logical_expr(it[1]))
        o.extend(o1)
        ref_prev = None
        if forcenewg is not None:
            assert istempref(forcenewg)
            ref_prev = forcenewg
            o.CLEAR(ref_prev)
        else:
            ref_prev = New()    
        assert ref_prev is not None
        o.Stmt('if (', logic, ') {')
        ref = GenExpr(it[2], o, ref_prev)

        if ref != ref_prev:
            if istempref(ref):
                pprint.pprint((ref,ref_prev))
                pprint.pprint(it)
            assert not istempref(ref)
##            o.append('Py_CLEAR(' + CVar(ref_prev) + ');')
            o.Raw(ref_prev, ' = ', ref, ';')
            o.INCREF(ref_prev)        
        o.Raw('} else {')
        ref = GenExpr(it[3], o, ref_prev)
        if ref != ref_prev:
            assert not istempref(ref)
##            o.append('Py_CLEAR(' + CVar(ref_prev) + ');')
            o.Raw(ref_prev, ' = ', ref, ';')
            o.INCREF(ref_prev)        
        o.Raw('}')
        return ref_prev        
                
#
# Base part
#
    return common_call(head, it, o, typed, forcenewg)

def call_fastcall(it, o, ref1, forcenewg):
    is_const_default = True
    if it[2] == ('CONST', ()):
        refs = []
    elif it[2][0] == '!BUILD_TUPLE':
        refs = Expr(o, it[2][1])
    elif it[2][0] == 'CONST':
        refs = [('CONST', x) for x in it[2][1]]
    else:
        Fatal('GenExpr call fastcall', it)
    ref = New(None, forcenewg)
    if len(refs) == 0:
        tupl = (ref, ' = FastCall0(', ref1, ')')
        Used('FastCall0')
    else:    
        tupl = (ref, ' = FastCall(', len(refs), ', ', ref1)
        Used('FastCall')
        for _r in refs:
            tupl = tupl + (', ', _r)
        tupl = tupl + (')',)    
    tupl = ('if ((',) + tupl + (') == NULL) goto ', labl, ';') 
    o.Raw(*tupl)
##    o.Raw('if (', ref, ' == NULL) goto ', labl, ';')
    UseLabl()
    if len(refs) > 0:
        o.Cls(*refs)
    o.Cls(ref1)    
    return ref

def CanBeMethodOf(it):
    _v = []
    if TCmp(it, _v, ('!PyObject_Call', ('!PyObject_GetAttr', '?', ('CONST', '?')), '?', '?')):
        islis = list(Iter3(None, ('Method', _v[1]), None))
        if len(islis) == 0:
            return []
        di = dict([(a,c) for a,b,c in islis])
        while True:
            l = len(di)
            for k in di.keys():
                for a1, b1, c1 in Iter3(None, 'Derived', ('!CALC_CONST', k)):
                    if a1 not in di:
                        di[a1] = di[k]
            if len(di) == l:
                break 
        if len(dict.fromkeys(di.values())) == 1:
            pass
        elif len(dict.fromkeys(di.values())) == len(di):
            pass    
        pprint.pprint(di)               
#        pprint.pprint (islis)
        pprint.pprint (it)

def generate_PyObject_Call_nokey(it, o, forcenewg):
   
    if it[1][0] == '!LOAD_GLOBAL' and it[1][1] in d_built:
        skip_built = False
        if it[2][0] == '!BUILD_TUPLE':
            args = it[2][1]
        elif it[2][0] == 'CONST':
            args = [('CONST', x) for x in it[2][1]]
        else:
            skip_built = True
        if not skip_built:    
            cm = attempt_direct_builtin(it[1][1],args, it[2])
            if cm is not None:
                proc = Expr1(it[1], o)   
                o.Stmt('if (', proc, '==', load_builtin(it[1][1]), ') {')
                ref = GenExpr(cm, o,forcenewg)
                o.Raw('} else {')
                tupl = Expr1(it[2], o)
                o.Stmt(ref, '=', 'FirstCFunctionCall', proc, tupl, ('NULL',))
                o.Cls(tupl)
                o.Raw('}')
                o.Cls(proc)
                return ref

    ## ## variant = not is_mkfunc_const(proc, it[1])
    ## ## t = TypeExpr(it[1])
    ## if it[1][0] == '!PyObject_GetAttr' and \
       ## it[2][0] in ('!BUILD_TUPLE', 'CONST') and len(it[2][1]) < 15:
        ## return call_fastcall(it, o, None, forcenewg) 
#    _v = []
#    CanBeMethodOf(it)
    ## ('CALL_METHOD_CONDITIONAL', obj, attr, {tuple_of_nmclass, codenm}, args)
    ## if TCmp(it, _v, ('!PyObject_Call', ('!PyObject_GetAttr', '?', ('CONST', '?')), '?', '?')):
        
        ## islis = list(Iter3(None, ('Method', _v[1]), None))
        ## l = []
        ## l.extend(islis)
        ## di = {}
        ## for a,b,c in islis:
            ## di[a] = True
        ## print di.keys()    
        ## l = len(di)
        ## for a,b,c in islis:
            ## for a1, b1, c1 in Iter3(None, 'Derived', ('!CALC_CONST', a)):
                ## if a1 not in di:
                    ## print 'a1 b1 c1', a1, b1, c1
        ## print 'may be'
## #        pprint.pprint (islis)
        ## pprint.pprint (it)
    proc = GenExpr(it[1],o)
    if TypeExpr(it[1]) != Kl_BuiltinFunction and not is_mkfunc_const(proc, it[1]) and \
       it[2][0] in ('!BUILD_TUPLE', 'CONST') and len(it[2][1]) < 15 and it[1][0] != '!LOAD_BUILTIN':
        return call_fastcall(it, o, proc, forcenewg) 
    ref = New(None, forcenewg)
            
    ## if it[1][0] == '!LOAD_BUILTIN':
        ## if it[1][1] in d_built and type(d_built[it[1][1]]) == type(len):
            ## ## if it[1][1] in ('min', 'max', "compile", "__import__", "open", "round"):
                ## ## proc, tupl = Expr(o, it[1:3])   
                ## ## meth = New('PyCFunction')
                ## ## o.Raw(meth, ' = PyCFunction_GET_FUNCTION(', proc, ');')
                ## ## o.Raw(ref, ' = (*(PyCFunctionWithKeywords)', meth, ')(NULL,', tupl, ', NULL);')
                ## ## o.Cls(meth, proc, tupl)
                ## ## return ref
            ## ## elif it[1][1] in ('hex', 'all') and len(it[2][1]) == 1 and\
                    ## ## it[2][0] in ('CONST', '!BUILD_TUPLE'):
                ## ## proc  = Expr1(it[1], 0)
                ## ## if it[2][0] == 'CONST':
                    ## ## b_arg = ('CONST', it[2][1][0])
                ## ## else:    
                    ## ## b_arg =  it[2][1][0]
                ## ## meth = New('PyCFunction')
                ## ## o.Raw(meth, ' = PyCFunction_GET_FUNCTION(', proc, ');')
                ## ## tupl = Expr1(b_arg, o)  
                ## ## o.Raw(ref, ' = (*', meth, ')(NULL, ', tupl, ');')  
                ## ## o.Cls(meth, proc, tupl)
                ## ## return ref
            
    tupl = GenExpr(it[2], o)   
    variant = not is_mkfunc_const(proc, it[1])
    t = TypeExpr(it[1])
    if t == Kl_BuiltinFunction:
        o.Stmt(ref, '=', 'PyCFunction_Call', proc, tupl, ('NULL',))
    elif variant:    
        if it[1][0] == '!LOAD_BUILTIN':
            if it[1][1] in d_built and type(d_built[it[1][1]]) == type(len):
##                Debug('+Call PycFunction_Call builtin (variant)', it[1], TypeExpr(it[1]))
                o.Stmt(ref, '=', 'PyCFunction_Call', proc, tupl, ('NULL',))
            else:    
                Debug('+Call PyObject_Call builtin (variant)', it[1], TypeExpr(it[1]))
                o.Stmt(ref, '=', 'PyObject_Call', proc, tupl, ('NULL',))
        else:        
            o.Stmt(ref, '=', 'FirstCFunctionCall', proc, tupl, ('NULL',))
    else:
        ## if it[1][0] == '!LOAD_BUILTIN':
            ## Debug('+Call PyObject_Call builtin', it[1], TypeExpr(it[1]))
##        Debug('+Call PyObject_Call compiled? code',it, TypeExpr(it[1]))    
        o.Stmt(ref, '=', 'PyObject_Call', proc, tupl, ('NULL',))
    o.Cls(proc, tupl)
    return ref
    
def common_call(head, it, o, typed, forcenewg):
    gen = [Expr1(x, o) if type(x) is tuple and len(x) > 0 else x \
              for i,x in enumerate(it) if i > 0]
    if head == '_PyInt_Format':
        gen[0] = ('TYPE_CONVERSION', '(PyIntObject *)', gen[0])      
    if head == '_PyList_Extend':
        gen[0] = ('TYPE_CONVERSION', '(PyListObject *)', gen[0])      
    newg = New(typed, forcenewg)  
    args = (newg, '=', head)  + tuple(gen)       
    o.Stmt(*args)
    o.Cls(*gen)
    return newg   

def GenNumberExpr(it, o, forcenewg, typed, skip_float):
    head = it[0]
    if head in ('!PyNumber_And', '!PyNumber_Or', '!PyNumber_Xor') or\
       (head == '!PyNumber_Lshift' and it[1][0] == '!ORD_BUILTIN' and \
       it[2][0] == 'CONST' and 0 <= it[2][1] <= 24):
        ref1, ref2 = Expr(o, it[1:3])
        if forcenewg is not None:
            new = forcenewg
        else:
            new = New()    
        check = True    
        skip_int = not_int_op(ref1, ref2, it[1], it[2])
        if not skip_int:
            t1 = TypeExpr(it[1])
            t2 = TypeExpr(it[2])
            check = not IsInt(t1) or not IsInt(t2)
            if it[1][0] != 'CONST' and it[2][0] != 'CONST':
                if check:
                    o.Stmt('if (PyInt_CheckExact(', ref1, ') && PyInt_CheckExact(', ref2, ')) {')
                n1 = 'PyInt_AsLong(' + CVar(ref1) + ')'
                n2 = 'PyInt_AsLong(' + CVar(ref2) + ')'
            elif it[1][0] == 'CONST' and it[2][0] != 'CONST' and type(it[1][1]) is int:
                if check:
                    o.Stmt('if (PyInt_CheckExact(', ref2, ')) {')
                n1 = str(it[1][1])
                n2 = 'PyInt_AsLong(' + CVar(ref2) + ')'
            elif it[1][0] != 'CONST' and it[2][0] == 'CONST' and type(it[2][1]) is int:
                if check:
                    o.Stmt('if (PyInt_CheckExact(', ref1, ')) {')
                n1 = 'PyInt_AsLong(' + CVar(ref1) + ')'
                n2 = str(it[2][1])
            else:
                skip_int = True
        op = '???'
        if not skip_int:
            if head == '!PyNumber_And':
                op = '&'
            elif head == '!PyNumber_Or':
                op = '|'
            elif head == '!PyNumber_Xor':
                op = '^'
            elif head == '!PyNumber_Rshift':
                op = '>>'
            elif head == '!PyNumber_Lshift':
                op = '<<'
            o.Raw(new, ' = PyInt_FromLong(', n1, op, n2, ');')
        if check and not skip_int:
            o.Raw('} else {')
            o.Stmt(new, '=', head[1:], ref1, ref2)
            o.Raw('}')
        elif check and skip_int:    
            o.Stmt(new, '=', head[1:], ref1, ref2)
        elif not check and not skip_int:
            pass
        else:
            o.Stmt(new, '=', head[1:], ref1, ref2)
        o.Cls(ref1, ref2)
        return new
    
    arifm = ('!PyNumber_Multiply', '!PyNumber_Divide', '!PyNumber_Add', '!PyNumber_Subtract')
    if head in arifm and TypeExpr(it) == Kl_Float:
        if forcenewg is not None:
            new = forcenewg
        else:
            new = New()    
        fl = GenFloatExpr(it,o)
        o.Stmt(new, '=', 'PyFloat_FromDouble', fl)
        o.Cls(fl)
        return new  
    if head == '!PyNumber_Multiply':
        ref1 = GenExpr(it[1], o, None, None, skip_float)
        ref2 = GenExpr(it[2], o, None, None, skip_float)
        if forcenewg is not None:
            new = forcenewg
        else:
            new = New()    
        if skip_float is None:
            skip_float = False
        if it[1][0] == '!BUILD_LIST' or it[1][0] == '!BUILD_TUPLE' or it[1][0] == '!ORD_BUILTIN':    
            skip_float = True
        if not skip_float:
            if not_float_op(ref1,ref2):
                skip_float = True    
        skip_int = not_int_op(ref1, ref2, it[1], it[2])
        if skip_int and typed == 'Py_ssize_t':
            skip_int = False
        if not skip_float:    
            bin_arg_float(o, ref1, ref2, True)
            o.Raw(new, ' = PyFloat_FromDouble(PyFloat_AS_DOUBLE(', ref1, ') * PyFloat_AS_DOUBLE(', ref2, '));')
        if not skip_int:
            if not skip_float:
                o.Stmt('} else if (PyInt_CheckExact(', ref1, ') && PyInt_CheckExact(', ref2, ')) {')
            else:
                o.Stmt('if (PyInt_CheckExact(', ref1, ') && PyInt_CheckExact(', ref2, ')) {')
            o.Raw(new, ' = PyInt_Type.tp_as_number->nb_multiply(', ref1, ', ', ref2, ');')
            o.Raw('} else {')
        else:    
            if not skip_float:    
                o.Raw('} else {')
            else:    
                o.Stmt('{')
        o.Stmt(new, '=', head[1:], ref1, ref2)
        o.Raw('}')
        o.Cls(ref1, ref2)
        return new

    if head in ('!PyNumber_Divide', '!PyNumber_Remainder'):
        if IsInt(TypeExpr(it[1])) and IsInt(TypeExpr(it[2])):
            ref1 = GenExpr(it[1], o, None, None, skip_float)
            ref2 = GenExpr(it[2], o, None, None, skip_float)
            if forcenewg is not None:
                new = forcenewg
            else:
                new = New()    
                
            n1,n2,n3 = None,None,None
            n3 = New('long')
                
            if ref1[0] == 'CONST':
                n1 = ref1[1]
            else:
                n1 = New('long')
                o.Stmt(n1, '=', 'PyInt_AsLong', ref1)
            if ref2[0] == 'CONST':
                n2 = ref2[1]
            else:
                n2 = New('long')
                o.Stmt(n2, '=', 'PyInt_AsLong', ref2)
            if head == '!PyNumber_Divide':
                o.Stmt(n3, '=', n1, '/', n2)
            elif head == '!PyNumber_Remainder':    
                o.Stmt(n3, '=', n1, '%', n2)
            else:
                Fatal('', it)   
            o.Stmt(new, '=', 'PyInt_FromLong', n3)
            o.Cls(n1, n2, n3, ref1, ref2)
            return new

        if IsInt(TypeExpr(it[1])) and TypeExpr(it[2]) == Kl_Float and \
                head == '!PyNumber_Divide':
            ref1 = GenExpr(it[1], o, None, None, skip_float)
            ref2 = GenExpr(it[2], o, None, None, skip_float)
            if forcenewg is not None:
                new = forcenewg
            else:
                new = New()    
                
            n1,n2,n3 = None,None,None
            n3 = New('double')
                
            if ref1[0] == 'CONST':
                n1 = ref1[1]
            else:
                n1 = New('long')
                o.Stmt(n1, '=', 'PyInt_AsLong', ref1)
            if ref2[0] == 'CONST':
                n2 = str(ref2[1])
            else:
                n2 = New('double')
                o.Stmt(n2, '=', 'PyFloat_AsDouble', ref2)
            o.Stmt(n3, '=', n1, '/', n2)
            o.Stmt(new, '=', 'PyFloat_FromDouble', n3)
            o.Cls(n1, n2, n3, ref1, ref2)
            return new

    if head == '!PyNumber_Power':
        if it[2] == ('CONST', 2) and it[3] == 'Py_None':
            ref1 = Expr1(it[1], o)
            ref2 = GenExpr(('!PyNumber_Multiply', ref1, ref1), o, forcenewg, typed, skip_float)
            o.Cls(ref1)
            return ref2
        if IsInt(TypeExpr(it[1])) and TypeExpr(it[2]) == Kl_Float and it[3] == 'Py_None':
            ref1 = Expr1(it[1], o)
            dbl = Expr1(it[2], o)
            fl = New('double')
            if dbl[0] != 'CONST':
                o.Stmt(fl, '=', 'PyFloat_AsDouble', dbl)
            else:    
                o.Raw(fl, ' = ', str(dbl[1]), ';')
            o.Raw(fl, ' = pow( (double) PyInt_AsLong(', ref1, '), ', fl, ');')
            ref3 = New()
            o.Raw(ref3, ' = PyFloat_FromDouble( ', fl, ' );')
            o.Cls(ref1, dbl, fl)
            return ref3
            
    if head == '!PyNumber_Add' and IsInt(TypeExpr(it[1])) and TypeExpr(it[2]) == Kl_Boolean:        
        if it[1][0] == 'CONST':
            r2 = Expr1(it[2],o)
            add = New('long')
            o, add = ToTrue(o,add,r2, it[2])            
            n1 = str(it[1][1])
#            o.Stmt(add, '=', 'PyObject_IsTrue', r2)
            o.Stmt(add, '=', add, '+', n1)
            new = New(None, forcenewg)
            o.Stmt(new, '=', 'PyInt_FromLong', add)
            o.Cls(add, n1)
            return new
        r1,r2 = Expr(o, it[1:])
        n1 = New('long')
        o.Stmt(n1, '=', 'PyInt_AS_LONG', r1)
        add = New('int')
        o.Stmt(add, '=', 'PyObject_IsTrue', r2)
        o.Stmt(n1, '=', n1, '+', add)
        new = New(None, forcenewg)
        o.Stmt(new, '=', 'PyInt_FromLong', n1)
        o.Cls(r1,r2, add, n1)
        return new
        
    if head in ('!PyNumber_Subtract', '!PyNumber_Add', '!PyNumber_InPlaceSubtract', '!PyNumber_InPlaceAdd'):
        return GenPlusMinus(head[1:],it,o,forcenewg, skip_float)

    if head in ('!PyNumber_Negative',):
        if len(it) > 3:
            Fatal('GenNumberExpr', it)
        t = TypeExpr(it) 
        t1 = TypeExpr(it[1])    
        ref1 = GenExpr(it[1], o, None, None, skip_float)
        if forcenewg is not None:
            new = forcenewg
        else:
            new = New()    
            
        n1,n2,n3 = None,None, None
        canbeint = IsNoneOrInt(t1)
        canbefloat = t1 in (None, Kl_Float) and not skip_float
        act = [] 
        onlyint = False
        onlyfloat = False
        if canbeint:
            cmp = IsInt(t1)
            n3 = New('long')
            
            if not cmp:
                o.Stmt('if (PyInt_CheckExact(', ref1, ')) {')
            else:
                onlyint = True
##                o.Stmt('if (1) {')

            if ref1[0] == 'CONST':
                n1 = ref1[1]
            else:
                n1 = New('long')
                o.Stmt(n1, '=', 'PyInt_AS_LONG', ref1)
            
            nlabel = New('label')
            if t == Kl_Short:
                o.Stmt(n3, '=', 0, '-', n1)
                o.Stmt(new, '=', 'PyInt_FromLong', n3)
            else:
                o.Stmt(n3, '=', 0, '-', n1)
                o.Stmt('if ((', n3, '^', 0, ') < 0 || (', n3, '^~', n1, ') < 0) goto ', nlabel, ';')
                o.Stmt(new, '=', 'PyInt_FromLong', n3)
            o.Cls(n1, n3)
        if canbefloat and not onlyint:
            cmp = t1 in (Kl_Float,)
            if canbeint:
                pre = '} else '
            else:
                pre = ''     
            if not cmp:
                o.Stmt(pre + 'if (PyFloat_CheckExact(', ref1, ')) {')
                t1 = Kl_Float
            else:
                if canbeint:
##                    Fatal('',it)
                    o.Stmt(pre + 'if (1) {')
                else:
                    onlyfloat = True    
            if t1 == Kl_Float:
                s1 = 'PyFloat_AS_DOUBLE('+ CVar(ref1)+')'    
            else:    
                s1 = 'PyFloat_AsDouble('+ CVar(ref1)+')'    
            if ref1[0] == 'CONST':
                s1 = '((double)' + str(ref1[1]) +')'
            o.Raw(new, ' = PyFloat_FromDouble(-(', s1, '));')
        if onlyint and t != Kl_Short:
            o.Stmt('if (0) {', nlabel, ':')
            o.Stmt(new, '=', head[1:], ref1)
            o.Raw('}')
        elif onlyint or onlyfloat:
            pass
        else:
            if canbeint:
                o.Stmt('} else {', nlabel, ':')
                o.Stmt(new, '=', head[1:], ref1)
                o.Raw('}')
            elif canbefloat:    
                o.Raw('} else {')
                o.Stmt(new, '=', head[1:], ref1)
                o.Raw('}')
            else:
                o.Stmt(new, '=', head[1:], ref1)
        o.Cls(ref1)
        return new
                
#
# Base part
#   
    return common_call(head[1:], it, o, typed, forcenewg)

def GenPlusMinus(head,it,o,forcenewg, skip_float):
    if len(it) > 3:
        Fatal('GenNumberExpr', it) 
    t = TypeExpr(it) 
    t1 = TypeExpr(it[1])    
    t2 = TypeExpr(it[2]) 
    ref1 = GenExpr(it[1], o, None, None, skip_float)
    ref2 = GenExpr(it[2], o, None, None, skip_float)
    if ref1 == ('CONST', None):
        return ref1
    if ref2 == ('CONST', None):
        return ref2
    if forcenewg is not None:
        new = forcenewg
    else:
        new = New()    
            
    n1,n2,n3 = None,None,None
    canbeint = CanBeInt(t1,t2)
    canbefloat = CanBeFloat(t1,t2) and not skip_float
    act = [] 
    can_else = True 
    if canbeint:
        cmp = (IsInt(t1), IsInt(t2))
        nooverflow = t1 == Kl_Short == t2
        n3 = New('long')
            
        if cmp == (False, False):
            o.Stmt('if (PyInt_CheckExact(', ref1, ') && PyInt_CheckExact(', ref2, ')) {')
        elif cmp == (True, False):
            o.Stmt('if (PyInt_CheckExact(', ref2, ')) {')
        elif cmp == (False, True):
            o.Stmt('if (PyInt_CheckExact(', ref1, ')) {')
        else:
            if t1 == Kl_Short == t2 and not canbefloat:
                can_else = False
            else:
##                    Fatal('',it)
                o.Stmt('if (1) {')

        if ref1[0] == 'CONST':
            n1 = ref1[1]
        else:
            n1 = New('long')
            o.Stmt(n1, '=', 'PyInt_AS_LONG', ref1)
        if ref2[0] == 'CONST':
            n2 = ref2[1]
        else:
            n2 = New('long')
            o.Stmt(n2, '=', 'PyInt_AS_LONG', ref2)
            
        nlabel = New('label')
        if head in ('PyNumber_Add', 'PyNumber_InPlaceAdd'):
            o.Stmt(n3, '=', n1, '+', n2)
            if t1 == Kl_Short == t2:
                pass
            else:
                o.Stmt('if ((', n3, '^', n1, ') < 0 || (', n3, '^', n2, ') < 0) goto ', nlabel, ';')
        else:   
            o.Stmt(n3, '=', n1, '-', n2)
            if t1 == Kl_Short == t2:
                pass
            else:
                o.Stmt('if ((', n3, '^', n1, ') < 0 || (', n3, '^~', n2, ') < 0) goto ', nlabel, ';')
        o.Stmt(new, '=', 'PyInt_FromLong', n3)
        o.Cls(n1, n2, n3)
    if canbefloat:
        cmp = (IsIntOrFloat(t1), IsIntOrFloat(t2))
        if canbeint:
            pre = '} else '
        else:
            pre = ''     
        if cmp == (False, False):
            o.Stmt(pre + 'if (PyFloat_CheckExact(', ref1, ') && PyFloat_CheckExact(', ref2, ')) {')
            t1 = Kl_Float
            t2 = Kl_Float
        elif cmp == (True, False):
            o.Stmt(pre + 'if (PyFloat_CheckExact(', ref2, ')) {')
            t2 = Kl_Float
        elif cmp == (False, True):
            o.Stmt(pre + 'if (PyFloat_CheckExact(', ref1, ')) {')
            t1 = Kl_Float
        else:
##                Fatal('',it)
            o.Stmt(pre + 'if (1) {')
        if t1 == Kl_Float:
            s1 = 'PyFloat_AS_DOUBLE('+ CVar(ref1)+')'    
        else:    
            s1 = 'PyFloat_AsDouble('+ CVar(ref1)+')'    
        if t2 == Kl_Float:
            s2 = 'PyFloat_AS_DOUBLE('+ CVar(ref2)+')'    
        else:    
            s2 = 'PyFloat_AsDouble('+ CVar(ref2)+')'    
        if ref1[0] == 'CONST':
            s1 = '((double)' + str(ref1[1]) +')'
        if ref2[0] == 'CONST':
            s2 = '((double)' + str(ref2[1]) +')'
        if head in ('PyNumber_Add', 'PyNumber_InPlaceAdd'):
            o.Raw(new, ' = PyFloat_FromDouble(', s1, ' + ', s2, ');')
        else:    
            o.Raw(new, ' = PyFloat_FromDouble(', s1, ' - ', s2, ');')
    if canbeint:
        if not canbefloat and not can_else:
            pass ##o.Raw('}')
        else:    
            o.Stmt('} else {', nlabel, ':')
            o.Stmt(new, '=', head, ref1, ref2)
            o.Raw('}')
    elif canbefloat:    
        o.Raw('} else {')
        o.Stmt(new, '=', head, ref1, ref2)
        o.Raw('}')
    else:
        o.Stmt(new, '=', head, ref1, ref2)
    o.Cls(ref1, ref2)
    return new


def CanBeFloat(t1, t2):
    if IsNoneOrIntOrFloat(t1) and IsNoneOrIntOrFloat(t2) and\
       (not IsInt(t1) or not IsInt(t2)):
           return True
    return False   
   
def CanBeInt(t1, t2):
    if (t1 is None or t1.IsInt()) and (t2 is None or t2.IsInt()):
           return True
    return False   

arifm = ('!PyNumber_Multiply', '!PyNumber_Divide', '!PyNumber_Add', '!PyNumber_Subtract')

def genHalfFloat(it1, o):
    if it1[0] == 'CONST' and type(it1[1]) is float:
        return repr(it1[1])
    elif it1[0] in arifm and TypeExpr(it1) == Kl_Float:
        return GenFloatExpr(it1, o)
    elif it1[0] == '!PyObject_Call' and it1[1][0] == 'CALC_CONST':
        t = it1[1][1]    
        if len(t) == 2:
            t = (Val3(t[0], 'ImportedM'), t[1])
            if t in CFuncFloatOfFloat:
                s0 = genHalfFloat(it1[2][1][0], o)
                s1 = New('double')
                o.Raw(s1, ' = ', CFuncFloatOfFloat[t], ' ( ', s0, ');')
                o.Cls(s0)
                return s1
    ref1 = Expr1(it1, o)
    s1 = New('double')
    o.Stmt(s1, '=', 'PyFloat_AsDouble', ref1)
    o.Cls(ref1)
    return s1    
    
def GenFloatExpr(it, o):
    arifm = ('!PyNumber_Multiply', '!PyNumber_Divide', '!PyNumber_Add', '!PyNumber_Subtract')
    if it[0] in arifm and TypeExpr(it) == Kl_Float:
        op4 = ('*', '/', '+', '-')
        op = op4[arifm.index(it[0])]
        s1 = genHalfFloat(it[1], o)
        s2 = genHalfFloat(it[2], o)
        new = New('double')
        o.Raw(new, ' = ', s1, ' ', op, ' ', s2, ';')  
        o.Cls(s1, s2)    
        return new  
    Fatal('', it)

def not_float_op(ref1,ref2):
    l1 = isconstref(ref1) 
    l2 = isconstref(ref2)
    l1_0 = True
    l2_0 = True 
    if l1:
        l1_0 = type(ref1[1]) is float    
    if l2:
        l2_0 = type(ref2[1]) is float    
    if not l1_0 or not l2_0:
        return True
    return False    

def not_int_op(ref1,ref2, e1,e2):
    l1 = isconstref(ref1) 
    l2 = isconstref(ref2)
    l1_0 = True
    l2_0 = True 
    if l1:
        l1_0 = type(ref1[1]) is int    
    if l2:
        l2_0 = type(ref2[1]) is int    
    if not IsNoneOrInt(TypeExpr(e1)):
        return True    
    if not IsNoneOrInt(TypeExpr(e2)):
        return True    
    if not l1_0 or not l2_0:
        return True
    return False    

def bin_arg_float(o, ref1, ref2, first):
    l1 = isconstref(ref1) 
    l2 = isconstref(ref2) 
    if l1:
        l1_0 = type(ref1[1]) is float    
    if l2:
        l2_0 = type(ref2[1]) is float    
    if not first:
        pre = '} else '
    else:
        pre = ''        
    if not l1 and not l2:
        o.Stmt(pre + 'if (PyFloat_CheckExact(', ref1, ') && PyFloat_CheckExact(', ref2, ')) {')
    elif l1 and l2:
        if l1_0 and l2_0:
##            Fatal('',it)
            o.Stmt(pre + 'if (1) {')
        else:        
##            Fatal('',it)
            o.Stmt(pre + 'if (0) {')
    elif l1:    
        if l1_0:
            o.Stmt(pre + 'if (PyFloat_CheckExact(', ref2, ')) {')
        else:        
            o.Stmt(pre + 'if (0) {')
    elif l2:    
        if l2_0:
            o.Stmt(pre + 'if (PyFloat_CheckExact(', ref1, ')) {')
        else:        
            o.Stmt(pre + 'if (0) {')
    else:
        Fatal('bin_arg_float', ref1, ref2, first)
    return None    

type_recode = {'int': 'PyInt_Type','long':'PyLong_Type',\
               'float':'PyFloat_Type', 'bool':'PyBool_Type',\
               'object':'PyBaseObject_Type', 'unicode':'PyUnicode_Type',\
               'complex':'PyComplex_Type'}

def calc_range_1(tupl):
    try:
        l = range(*tupl[1])
        if len(l) < 16:
            ll = [('CONST', x) for x in l]
            return ('!BUILD_LIST', tuple(ll))
    except:
        pass   
    return None 

def attempt_direct_builtin(nm_builtin, args, tupl):
    if nm_builtin == 'range' and tupl[0] == 'CONST':
        l = calc_range_1(tupl)
        if l is not None:
            return l
    if nm_builtin == 'chr'  and len(args) == 1:
        return ('!CHR_BUILTIN', args[0])
    if nm_builtin == 'ord'  and len(args) == 1:
        return ('!ORD_BUILTIN', args[0], tupl)
    if nm_builtin in type_recode:
        typ = type_recode[nm_builtin]
        return  ('!' + typ + '.tp_new', '&' + typ, tupl, 'NULL')
    if nm_builtin == 'dir' and len(args) == 1:
        return ('!PyObject_Dir', args[0])
    ## if nm_builtin == 'hex' and len(args) == 1:
        ## return ('!PyNumber_ToBase', args[0], 16)
    if nm_builtin == 'bin' and len(args) == 1:
        return ('!PyNumber_ToBase', args[0], 2)
    ## if nm_builtin == 'oct' and len(args) == 1:
        ## return ('!PyNumber_ToBase', args[0], 8)
    if nm_builtin == 'id' and len(args) == 1:
        return ('!PyLong_FromVoidPtr', args[0])
    if nm_builtin == 'set' and len(args) == 0:
        return ('!PySet_New', 'NULL')
    ## if nm_builtin == 'frozenset' and len(args) == 0:
        ## return ('!PyFrozenSet_New', 'NULL')
    if nm_builtin == 'set' and len(args) == 1:
        return ('!PySet_New', args[0])
    ## if nm_builtin == 'frozenset' and len(args) == 1:
        ## return ('!PyFrozenSet_New', args[0])
    if nm_builtin == 'len' and len(args) == 1:
        t = TypeExpr(args[0])
        if t == Kl_List:
            return ('!PY_SSIZE_T', ('!PyList_GET_SIZE', args[0]))
        if t == Kl_Tuple:
            return ('!PY_SSIZE_T', ('!PyTuple_GET_SIZE', args[0]))
        if t == Kl_Dict:
            return ('!PY_SSIZE_T', ('!PyDict_Size', args[0]))
        if t == Kl_Set:
            return ('!PY_SSIZE_T', ('!PySet_Size', args[0]))
        if t == Kl_String:
            return ('!PY_SSIZE_T', ('!PyString_GET_SIZE', args[0]))
        return ('!PY_SSIZE_T', ('!PyObject_Size', args[0]))
    if nm_builtin == 'repr' and len(args) == 1:
        return ('!PyObject_Repr', args[0])
    if nm_builtin == 'str' and len(args) == 1: # test_compile not pass
        return ('!PyObject_Str', args[0])
    if nm_builtin == 'bytes' and len(args) == 1:
        return ('!PyObject_Str', args[0])
    if nm_builtin == 'unicode' and len(args) == 1:
        return ('!PyObject_Unicode', args[0])
    if nm_builtin == 'type' and len(args) == 1:
        return ('!PyObject_Type', args[0])
    if nm_builtin == 'dir' and len(args) == 1:
        return ('!PyObject_Dir', args[0])
    if nm_builtin == 'iter' and len(args) == 1:
        return ('!PyObject_GetIter', args[0])
### !!!!!!  replace to direct call !!!!!!    
    if nm_builtin == 'hash' and len(args) == 1:
        return ('!PyObject_Hash', args[0])
    if nm_builtin == 'cmp' and len(args) == 2:
        return ('!_PyObject_Cmp', args[0], args[1])
    if nm_builtin == 'unicode' and len(args) == 1:
        return ('!PyObject_Unicode', args[0])
    if nm_builtin == 'abs' and len(args) == 1:
        return ('!PyNumber_Absolute', args[0])
    if nm_builtin == 'format' and len(args) == 1:
        return ('!PyObject_Format', args[0], 'NULL')
    if nm_builtin == 'format' and len(args) == 2:
        return ('!PyObject_Format', args[0], args[1])
    if nm_builtin == 'tuple' and len(args) == 1:
        if TypeExpr(args[0]) == Kl_List:
            return ('!PyList_AsTuple', args[0])
        return ('!PySequence_Tuple', args[0])
    if nm_builtin == 'list' and len(args) == 1:
        return ('!PySequence_List', args[0])
    if nm_builtin == 'pow' and len(args) == 2:
        return ('!PyNumber_Power', args[0], args[1], 'Py_None')
    if nm_builtin == 'pow' and len(args) == 3:
        return ('!PyNumber_Power', args[0], args[1], args[2])
    if nm_builtin == 'hasattr' and len(args) == 2:
        return ('!BOOLEAN',('!PyObject_HasAttr', args[0], args[1]))
    if nm_builtin == 'isinstance' and len(args) == 2:
        return ('!BOOLEAN',('!PyObject_IsInstance', args[0], args[1]))
    if nm_builtin == 'issubclass' and len(args) == 2:
        return ('!BOOLEAN',('!PyObject_IsSubclass', args[0], args[1]))
    if nm_builtin == 'getattr' and len(args) == 2:
        return ('!PyObject_GetAttr', args[0], args[1])
    return None

def generate_and_or_jumped_stacked(it, o, prevref, is_and, n):
    ref1 = GenExpr(it[0], o, prevref)
#    if 'PyBool_FromLong' in repr(o[l_o:]):
#        Fatal('Over bool conversion', it[0], o[l_o:])
    assert istempref(prevref)
    if prevref != ref1:
        if n == 0:
            if istempref(ref1):
                Fatal('and_or_jumped_stacked', it)
        else:    
            o.CLEAR(prevref)
        o.Raw(prevref, ' = ', ref1, ';')
        if istempref(ref1):
            assert n != 0
            o.Raw(ref1, ' = NULL;')
        else:    
            o.INCREF(prevref)
    if len(it) == 1:
        return ref1
    assert is_and in (True, False)
    or_and = New('int')

    _prevlast1_1 = ConC('if ((', prevref, ' = PyBool_FromLong (')
    _prevlast2_1 = ')) == NULL) goto label_0;'

    if len(o) >= 1 and \
       o[-1].startswith(_prevlast1_1) and o[-1].endswith(_prevlast2_1):
        intlast = o[-1][len(_prevlast1_1):-len(_prevlast2_1)]
        if is_and:    
            o.Raw(or_and, ' = ', intlast, ';')
        else:    
            o.Raw(or_and, ' = !', intlast, ';')
    else:        
        if is_and:    
            o.Stmt(or_and, '=', 'PyObject_IsTrue', prevref)
        else:    
            o.Stmt(or_and, '=', 'PyObject_Not', prevref)
    o.Stmt('if (', or_and, ') {')
    o.CLEAR(prevref)
    generate_and_or_jumped_stacked(it[1:], o, prevref, is_and, n + 1)
    o.Raw('}')
    o.Cls(or_and)
    return prevref  

def tag_in_expr(tag, expr):
##    return tag in repr(expr)
    if type(expr) is tuple and len(expr) > 0:
        if expr[0] == tag:
            return True
        if expr[0] == 'CONST':
            return False
        for r in expr:
            if tag_in_expr(tag, r):
                return True
        return False
    if type(expr) is list:
        for r in expr:
            if tag_in_expr(tag, r):
                return True
        return False
    return False

def New(type=None, forcenewg=None):
    if forcenewg is not None:
        return forcenewg
    if type is None:
        return newgen(forcenewg)
    else:
        return new_typed(type, forcenewg)

traced_tempgen=[]

def newgen(forcenewg=None):
    global tempgen, traced_tempgen
    if forcenewg is not None:
        assert not tempgen[forcenewg[1]]
        return forcenewg  
    n = None  
    for i, f in enumerate(tempgen):
        if f:
            tempgen[i] = not f
            n = ('PY_TEMP',i)
            break
    if n is None:
        tempgen.append(False)
        n = ('PY_TEMP',len(tempgen)-1)
    if len(traced_tempgen) > 0:
        dict_tempgen = traced_tempgen[-1]
        dict_tempgen[n] = True
    return n    

def clearref(o,g, fictive=False):
    global tempgen
    global g_refs2
    if g in g_refs2:
        return
    if type(g) is tuple and g[0] == 'PY_TEMP' and g[1] < len(tempgen) and g[1] >= 0 and \
       not tempgen[g[1]]:
            if fictive:
                tempgen[g[1]] = True
                return
            tempgen[g[1]] = True
            o.Stmt('CLEARREF', g)   
            
def istempref(g):
    global tempgen
    if type(g) is tuple and len(g) == 2 and g[0] == 'PY_TEMP':
        i = g[1]
        if i >= 0 and i < len(tempgen):
            return True
    return False    

def isconstref(ref):
    return type(ref) is tuple and len(ref) > 1 and ref[0] == 'CONST'

def new_typed(type, forcenewg=None):
    global typed_gen
    if forcenewg is not None:
        assert forcenewg[0] == 'TYPED_TEMP' 
        return forcenewg        
    for i, (f, t) in enumerate(typed_gen):
        if f and t == type:
            typed_gen[i] = (not f, t)
            return ('TYPED_TEMP', i)
    typed_gen.append((False, type))
    return ('TYPED_TEMP', len(typed_gen)-1)
    
def clear_typed(g):
    global typed_gen
    if type(g) is tuple and g[0] == 'TYPED_TEMP' and g[1] < len(typed_gen) and g[1] >= 0 and \
       not typed_gen[g[1]][0]:
           typed_gen[g[1]] = (True, typed_gen[g[1]][1])

def istemptyped(g):
    global typed_gen
    if type(g) is tuple and len(g) == 2 and g[0] == 'TYPED_TEMP':
        i = g[1]
        if type(i) is int and i >= 0 and i < len(typed_gen):
            return True
    return False

def IsCalcConst(g):
    return g[0] == 'CALC_CONST'

def CVar(g):
    global typed_gen
    if type(g) is tuple:
        len_g = len(g)
        if len_g == 2 and g[0] == '&' and istempref(g[1]):
            return '&temp_' + str(g[1][1])
        if len_g == 2 and g[0] == '&' and istemptyped(g[1]):
            return '&' + CVar(g[1])
        if istempref(g):
            return 'temp_' + str(g[1])
        if istemptyped(g):
            return typed_gen[g[1]][1] + '_' + str(g[1])
        if g[0] == 'CALC_CONST':
            return 'calculated_const[' + str(calculated_const[g[1]]) + ']' #calc_const_to(g[1])
        if g[0] == 'CONST':
            return const_to(g[1])
        if g[0] == 'BUILTIN':
            return load_builtin(g[1])
        if g[0] == 'CODEFUNC':
            return '(PyObject *)code_' + g[1]
        if g[0] == 'TYPE_CONVERSION':
            return g[1] + ' ' +  CVar(g[2])
        if len(g) == 1:
            return g[0]
        if g[0] == 'FAST':
            return 'GETLOCAL(' + nmvar_to_loc(g[1]) + ')'
        if g[0] == 'LOAD_CLOSURE':
            return 'GETFREEVAR(' + g[1] + ')'


    if type(g) is int:
        return str(g)
    if g is None:
        return 'Py_None'
    return g

def load_builtin(c):
    global loaded_builtin
    assert c in d_built
    if c in loaded_builtin:
        return 'loaded_builtin[' + str(loaded_builtin.index(c)) + ']'
    loaded_builtin.append(c)    
    return 'loaded_builtin[' + str(loaded_builtin.index(c)) + ']'
 
def generate_builtin(cfile):
    if len(loaded_builtin) == 0:
        return
    print_to(cfile, 'static PyObject * loaded_builtin[' + str(len(loaded_builtin)) + '];')
    print_to(cfile, 'static void load_builtin(void){')
    for i, c in enumerate(loaded_builtin):
        print_to(cfile, ConC('loaded_builtin[',i,'] = PyDict_GetItemString(bdict, "' + str(c) + '");' ))
        print_to(cfile, ('if (loaded_builtin[' + str(i) + '] == NULL) {printf("no builtin %s\\n");}') %c)
#    print_to(cfile, 'if (0) {L0:')
#    print_to(cfile, 'printf(\"Handle raise at load builtin %d\\n\", __LINE__);')
#    print_to(cfile, 'if (PyErr_Occurred()) {printf (\"ERROR %s\\n\",PyObject_REPR(PyErr_Occurred()));}')
#    print_to(cfile, '}')
    print_to(cfile, '}')

def generate_calculated_consts(cfile):
    if len(calculated_const) > 0:
        print_to(cfile, 'static PyObject * calculated_const[' + str(len(calculated_const)) + '];')

def expand_const():
    const_to(filename)
    for k in _n2c.keys():
        const_to(k)
    i = 0
    while i < len(consts):
        c,type_c = consts[i]    
        if type(c) is tuple:
            li = [const_to(x) for x in c]
        elif type(c) is types.CodeType:
            ## nm = ''
            ## for k,v in _n2c.iteritems():
                ## if v == c:
                    ## nm = k
            if not can_generate_c(c) or full_pycode:
                const_to(c.co_code)
                const_to(c.co_consts)
                const_to(c.co_lnotab)
            else:   
                const_to("\x00")
                const_to(c.co_consts[:1])    
            const_to(c.co_name)
            const_to(c.co_names)
            const_to(c.co_varnames)
            const_to(c.co_freevars)
            const_to(c.co_cellvars)
        i += 1    
                        
def generate_consts(cfile):
    const_to(())
    expand_const()
    for i, (c,type_c) in enumerate(consts):
        if type(c) is str:
            s = ''
            create_chars_const(cfile, i, s, c)
        if type(c) is long:
            if c <= 30000 and c >= -30000:
                pass
            elif c > 0:
                s = ''
                c = str(c)
                create_chars_const(cfile, i, s, c)
            else:
                s = ''
                c = str(-c)
                create_chars_const(cfile, i, s, c)
        if type(c) is unicode:
            s = ''
            for j,code in enumerate(c):
                s += str(ord(code))
                if j < len(c)-1:
                    s += ','
            print_to(cfile, 'static wchar_t const_unicode_' + str(i) + \
                        '[' + str(len(c)) + '] = {' + s + '};')
    print_to(cfile, 'static PyObject * consts[' + str(len(consts)) + '];')
    print_to(cfile, 'static void init_consts(void){')
    change_ob = False
    for i, (c,type_c) in enumerate(consts):
        if type(c) is tuple:
            codes = [(j,c1) for j,c1 in enumerate(c) if type(c1) is types.CodeType]
            for j, c1 in codes:
                change_ob = True
    if change_ob:            
        print_to(cfile, 'int __ob;')
    for i, (c,type_c) in enumerate(consts):
        if type(c) is types.CodeType:
##            print_to(cfile, 'consts[' + str(i) + '] = Py_None;')
##            print_to(cfile, 'Py_INCREF(consts[' + str(i) + ']);')
##            co = c
            print_to(cfile, 'consts[' + str(i) + '] = Py_None;')
##            print_to(cfile, 'Py_INCREF(consts[' + str(i) + ']);')

        elif type(c) is bool :    
            if c:
                print_to(cfile, 'consts[' + str(i) + '] = Py_True;')
            else:    
                print_to(cfile, 'consts[' + str(i) + '] = Py_False;')
            print_to(cfile, 'Py_INCREF(consts[' + str(i) + ']);')
        elif type(c) is long:
            if c <= 30000 and c >= -30000:
                print_to(cfile, 'consts[' + str(i) + '] = PyLong_FromLong(' + str(c) + ');')
            elif c > 0:    
                print_to(cfile, 'consts[' + str(i) + '] = PyLong_FromString(const_string_' + str(i) + ',NULL,10);')
            else:    
                print_to(cfile, 'consts[' + str(i) + '] = PyNumber_Negative(PyLong_FromString(const_string_' + str(i) + ',NULL,10));')
        elif type(c) is int:
            print_to(cfile, 'consts[' + str(i) + '] = PyInt_FromLong(' + str(c) + 'L);')
        elif type(c) is float:
            if math.isnan(c):
                if not '-' in str(c):
                    print_to(cfile, 'consts[' + str(i) + '] = PyFloat_FromDouble(Py_NAN);')
                else:    
                    print_to(cfile, 'consts[' + str(i) + '] = PyFloat_FromDouble(-Py_NAN);')
            elif math.isinf(c):
                if not '-' in str(c):
                    print_to(cfile, 'consts[' + str(i) + '] = PyFloat_FromDouble(Py_HUGE_VAL);')
                else:
                    print_to(cfile, 'consts[' + str(i) + '] = PyFloat_FromDouble(-Py_HUGE_VAL);')
            else:    
                print_to(cfile, 'consts[' + str(i) + '] = PyFloat_FromDouble(' + repr(c) + ');')
        elif type(c) is complex:
            print_to(cfile, 'consts[' + str(i) + '] = PyComplex_FromDoubles(' + str(c.real) + ', ' + str(c.imag) + ');')
        elif type(c) is str: # and '"' not in c and '\n' not in c:
            print_to(cfile, 'consts[' + str(i) + '] = PyString_FromStringAndSize(const_string_' + str(i) + ', '+str(len(c))+');')
        elif type(c) is unicode: # and '"' not in c and '\n' not in c:
            print_to(cfile, 'consts[' + str(i) + '] = PyUnicode_FromWideChar(const_unicode_' + str(i) + ', '+str(len(c))+');')
        elif type(c) is types.EllipsisType:
            print_to(cfile, 'consts[' + str(i) + '] = &_Py_EllipsisObject;')
            print_to(cfile, 'Py_INCREF(consts[' + str(i) + ']);')
        elif type(c) is tuple:
            li = [const_to(x) for x in c]
            if len (li) == 0:
                print_to(cfile, 'consts[' + str(i) + '] = PyTuple_Pack(0);')
                print_to(cfile, 'empty_tuple = consts[' + str(i) + '];')
            else:    
                s = 'consts[' + str(i) + '] = PyTuple_Pack(' + str(len(li)) +', '
                for j,it in enumerate(li):
                    s +=  str(it) 
                    if j < len(li) - 1:
                        s += ', '
                s += ');'        
                print_to(cfile, s)
        elif c in d_built_inv:
            nm = d_built_inv[c]
            print_to(cfile, 'consts[' + str(i) + '] = ' + load_builtin(nm) + ';')
            print_to(cfile, 'Py_INCREF(consts[' + str(i) + ']);')
        else:
            Fatal('', type(c), c)
#        print_to(cfile, 'if (consts[' + str(i) + '] == NULL) { printf(\"Oops %d\\n\", __LINE__);}')
    for i, (c,type_c) in enumerate(consts):
        if type(c) is types.CodeType:
            nm = all_co[c].c_name
            ## nm = ''
            ## for k,v in _n2c.iteritems():
                ## if v == c:
                    ## nm = k
            co = c    
            if nm == '':
                Fatal('', c)
            if not can_generate_c(co): ##co.co_flags & CO_GENERATOR:
                print_to(cfile, 'consts[' + str(i) + '] = (PyObject *)PyCode_New(' +\
                    str(co.co_argcount) +', ' +\
                    str(co.co_nlocals) +', ' +\
                    str(co.co_stacksize) +', ' +\
                    str(co.co_flags) +', ' +\
                    const_to(co.co_code) +', ' +\
                    const_to(co.co_consts) +', ' +\
                    const_to(co.co_names) +', ' +\
                    const_to(co.co_varnames) +', ' +\
                    const_to(co.co_freevars) +', ' +\
                    const_to(co.co_cellvars) +', ' +\
                    const_to(filename) +', ' +\
                    const_to(co.co_name) +', ' +\
                    str(co.co_firstlineno) +', ' +\
                    const_to(co.co_lnotab) +');')
            elif full_pycode:        
                print_to(cfile, 'consts[' + str(i) + '] = (PyObject *)Py2CCode_New(' +\
                    str(co.co_argcount) +', ' +\
                    str(co.co_nlocals) +', ' +\
                    str(co.co_stacksize) +', ' +\
                    str(co.co_flags) +', ' +\
                    const_to(co.co_code) +', ' +\
                    const_to(co.co_consts) +', ' +\
                    const_to(co.co_names) +', ' +\
                    const_to(co.co_varnames) +', ' +\
                    const_to(co.co_freevars) +', ' +\
                    const_to(co.co_cellvars) +', ' +\
                    const_to(filename) +', ' +\
                    const_to(c.co_name) +', ' +\
                    str(co.co_firstlineno) +', ' +\
                    const_to(co.co_lnotab) +', codefunc_' + nm +');')
            else:
                print_to(cfile, 'consts[' + str(i) + '] = (PyObject *)Py2CCode_New(' +\
                    str(co.co_argcount) +', ' +\
                    str(co.co_nlocals) +', ' +\
                    str(co.co_stacksize) +', ' +\
                    str(co.co_flags) +', ' +\
                    const_to("\x00") +', ' +\
                    const_to(co.co_consts[:1]) +', ' +\
                    const_to(co.co_names) +', ' +\
                    const_to(co.co_varnames) +', ' +\
                    const_to(co.co_freevars) +', ' +\
                    const_to(co.co_cellvars) +', ' +\
                    const_to(filename) +', ' +\
                    const_to(c.co_name) +', ' +\
                    str(co.co_firstlineno) +', ' +\
                    const_to("\x00") +', codefunc_' + nm +');')

#            if not (co.co_flags & CO_GENERATOR):
#                print_to(cfile, 'SET_CODE_C_FUNC(consts[' + str(i) + '], codefunc_' + nm +');')
#            print_to(cfile,'assert (' +    const_to(co.co_code)  + ' != NULL);')
#            print_to(cfile,'assert (' +    const_to(co.co_consts)  + ' != NULL);')
            print_to(cfile,'assert (' +    const_to(co.co_names)  + ' != NULL);')
            print_to(cfile,'assert (' +    const_to(co.co_varnames)  + ' != NULL);')
            print_to(cfile,'assert (' +    const_to(co.co_freevars)  + ' != NULL);')
            print_to(cfile,'assert (' +    const_to(co.co_cellvars)  + ' != NULL);')
            print_to(cfile,'assert (' +    const_to(filename)  + ' != NULL);')
            print_to(cfile,'assert (' +    const_to(co.co_name)  + ' != NULL);')
#            print_to(cfile,'assert (' +    const_to(co.co_lnotab)  + ' != NULL);')
    for i, (c,type_c) in enumerate(consts):
        if type(c) is tuple:
            codes = [(j,c1) for j,c1 in enumerate(c) if type(c1) is types.CodeType]
            for j, c1 in codes:
                s1 = const_to(c1)
                s_inc = 'Py_INCREF(' + s1 + ');'
                s2 = const_to(c)
                s_set = 'PyTuple_SetItem(' + s2 + ', ' + str(j) + ', ' + s1 + ');'
                print_to(cfile, s_inc)
                print_to(cfile, '__ob = (' +s2 +')->ob_refcnt;')
                print_to(cfile, '(' +s2 +')->ob_refcnt = 1;')
                print_to(cfile, s_set)
                print_to(cfile, '(' +s2 +')->ob_refcnt = __ob;')
    print_to(cfile, '}')

visibl = set('-=+_~!@#$%^&*()[]{};:/?.>,< ')
def is_c(c):
    for _c in c:
        if _c.isalnum() or _c in visibl:
            pass
        else:
            return False
    return True

def generate_chars_literal(c):
    s = ''
    for j,code in enumerate(c):
        s += str(ord(code))
        if j < len(c)-1:
            s += ','
    if is_c(c):
        return '"' + c + '"'
    else:            
        return Str_for_C(c)
    
def create_chars_const(cfile, i, s, c):
    for j,code in enumerate(c):
        s += str(ord(code))
        if j < len(c)-1:
            s += ','
    if is_c(c):
        print_to(cfile, 'static char const_string_' + str(i) + \
                '[' + str(len(c)+1) + '] = "' + c + '";')
    else:            
        print_to(cfile, 'static char const_string_' + str(i) + \
                '[' + str(len(c)) + '] = {' + s + '};')
    

def print_to(c_f,v):
    print >> c_f, v

def const_to(c):
    global consts
    global consts_dict
#    print c
    if type(c) is tuple and len(c) > 0 and type(c[0]) is tuple and len(c[0]) > 0 and c[0][0] == '!':
        Fatal('', c)
    if c is None:
        return 'Py_None'
#    if c in obj_builtin:
#        i = obj_builtin.index(c)
#        nm = key_builtin[i]
#        return load_builtin(nm) 
    c_ = c,const_type(c)    
    if c_ in consts_dict:
        i = consts_dict[c_]
        return 'consts[' + str(i) + ']'
    if type(c) is tuple:
        li = [const_to(x) for x in c]
    if type(c_[0]) is float:
        for i, (cc, cc_typ) in enumerate(consts):
            if type(cc) is float and math.isinf(cc) and  math.isinf(c_[0]) and str(cc) == str(c_[0]):
                return 'consts[' + str(i) + ']'
            if type(cc)  is float and math.isnan(cc) and  math.isnan(c_[0]) and str(cc) == str(c_[0]):
                return 'consts[' + str(i) + ']'
            ## if cc_typ == c[1] and cc == c[0]:
## #    if c in consts:
            ## return 'consts[' + str(i) + ']'
    consts.append(c_)   
    consts_dict[c_] = len(consts) - 1 
    return 'consts[' + str(len(consts)-1) + ']'

def const_type(c):
    if type(c) is tuple:
        return tuple([const_type(x) for x in c])
    if type(c) in (float, complex):
        return type(c) , repr(c)
    return type(c)
 
def pregenerate_code_objects():
    for co in _n2c.values(): 
        if not can_generate_c(co) or full_pycode: ##co.co_flags & CO_GENERATOR:
            const_to(co.co_code)
            const_to(co.co_consts)
            const_to(co.co_lnotab)
        else:
            const_to(co.co_consts[:1])    
        const_to(co.co_name)
        const_to(co.co_names)
        const_to(co.co_varnames)
        const_to(co.co_freevars)
        const_to(co.co_cellvars)
        const_to(co)

def const_by_n(n):
    global consts
    return consts[n][0]

def calc_const_to(k):
    global calculated_const
    if k in calculated_const:
        return ('CALC_CONST', k)
    calculated_const[k] = len(calculated_const) 
    return ('CALC_CONST', k)
            
if __name__ == "__main__":
    print 'Run uncompiled...'
    main ()

