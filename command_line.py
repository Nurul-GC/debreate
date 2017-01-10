# -*- coding: utf-8 -*-

## \package command_line

# MIT licensing
# See: docs/LICENSE.txt


import sys

from globals.tests import available_tests


solo_args = (
    (u'h', u'help'),
    (u'v', u'version'),
)

value_args = (
    (u'l', u'log-level'),
    (u'i', u'log-interval'),
)

cmds = (
    u'clean',
    u'compile',
    u'legacy',
    u'test',
)

parsed_args_s = []
parsed_args_v = {}
parsed_commands = []
parsed_path = None

def ArgOK(arg, group):
    for s, l in group:
        if arg in (s, l,):
            return True
    
    return False

def ArgIsDefined(arg, a_type):
    for group in (solo_args, value_args):
        for SET in group:
            for A in SET:
                if arg == A:
                    return True
    
    return False

def GetArgType(arg):
    dashes = 0
    for C in arg:
        if C != u'-':
            break
        
        dashes += 1
    
    if dashes:
        if dashes == 2 and len(arg.split(u'=')[0]) > 2:
            if not arg.count(u'='):
                return u'long'
            
            if arg.count(u'=') == 1:
                return u'long-value'
        
        elif dashes == 1 and len(arg.split(u'=')[0]) == 2:
            if not arg.count(u'='):
                return u'short'
            
            if arg.count(u'=') == 1:
                return u'short-value'
        
        return None
    
    if arg in cmds:
        return u'command'
    
    # Any other arguments should be a filename path
    return u'path'


def ParseArguments(arg_list):
    global parsed_path, parsed_commands, parsed_args_s, parsed_args_v
    
    argc = len(arg_list)
    
    # Allow tests
    tests = True
    
    for AINDEX in range(argc):
        if AINDEX >= argc:
            break
        
        A = arg_list[AINDEX]
        arg_type = GetArgType(A)
        
        if arg_type == None:
            print(u'ERROR: Malformed argument: {}'.format(A))
            sys.exit(1)
        
        if arg_type == u'command':
            parsed_commands.append(A)
            
            if A == u'test' and tests:
                # NOTE: Can't reset global_arg list here???
                #       Changes arg_list to local variable.
                testcmd_index = arg_list.index(A)
                testarg_index = testcmd_index + 1
                
                for TESTARG in arg_list[testcmd_index+1:]:
                    if TESTARG in available_tests:
                        parsed_commands.append(TESTARG)
                        
                        # Remove test argument from main argumet list
                        arg_list.pop(testarg_index)
                        argc = len(arg_list)
                    
                    else:
                        # End test arguments
                        tests = False
            
            continue
        
        if arg_type == u'path':
            if parsed_path != None:
                print(u'ERROR: Extra input file detected: {}'.format(A))
                # FIXME: Use errno here
                sys.exit(1)
            
            parsed_path = A
            continue
        
        clip = 0
        for C in A:
            if C != u'-':
                break
            
            clip += 1
        
        if arg_type in (u'long', u'short'):
            parsed_args_s.append(A[clip:])
            continue
        
        # Anything else should be a value type
        key, value = A.split(u'=')
        
        # FIXME: Value args can be declared multiple times
        
        if not value.strip():
            print(u'ERROR: Value argument with empty value: {}'.format(key))
            # FIXME: Use errno here
            sys.exit(1)
        
        key = key[clip:]
        
        # Use long form
        for S, L in value_args:
            if key == S:
                key = L
                break
        
        parsed_args_v[key] = value
    
    
    # Testing arguments
    
    for A in parsed_args_s:
        if not ArgOK(A, solo_args):
            for S, L in value_args:
                if A in (S, L,):
                    print(u'ERROR: Value argument with empty value: {}'.format(A))
                    # FIXME: Use errno here:
                    sys.exit(1)
            
            print(u'ERROR: Unknown argument: {}'.format(A))
            # FIXME: Use errno here
            sys.exit(1)
        
        # Use long form
        arg_index = parsed_args_s.index(A)
        for S, L in solo_args:
            if A == S:
                parsed_args_s[arg_index] = L
    
    
    for A in parsed_args_v:
        if not ArgOK(A, value_args):
            print(u'ERROR: Unknown argument: {}'.format(A))
            # FIXME: Use errno here
            sys.exit(1)
    
    for S, L in solo_args:
        s_count = parsed_args_s.count(S)
        l_count = parsed_args_s.count(L)
        
        if s_count + l_count > 1:
            print(u'ERROR: Duplicate arguments: -{}|--{}'.format(S, L))
            # FIXME: Use errno here
            sys.exit(1)


## Checks if an argument was used
def FoundArg(arg):
    for group in (parsed_args_s, parsed_args_v):
        for A in group:
            if A == arg:
                return True
    
    return False


## Checks if a command was used
def FoundCmd(cmd):
    return cmd in parsed_commands


def GetParsedPath():
    return parsed_path
