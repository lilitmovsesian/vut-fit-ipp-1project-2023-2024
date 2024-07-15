import sys
import lib_stats
import lib_parse

# Constants for error codes
ERR_PARAMETER = 10
ERR_INPUT = 11
ERR_OUTPUT = 12
ERR_HEADER = 21
ERR_UNKNOWN_OPCODE = 22
ERR_OTHER_SYNTAX_ERROR = 23

stats_parameters = {}

def print_help():
    """Printing of the help message."""
    print("-------------------------------------------------------------------------------------------------------------------")
    print("IPP 2024 project 1. The script parses IPPcode24 source code from standard input and outputs XML representation.")
    print("-------------------------------------------------------------------------------------------------------------------")
    print("""Usage: 
    python3.10 parse.py [--help]
    python3.10 parse.py --stats=file [--loc] [--comments] [--labels] [--jumps] [--fwjumps]
                        [--backjumps] [--badjumps] [--frequent] [--eol] [--print=string]""")
    print("-------------------------------------------------------------------------------------------------------------------")
    print("""Error codes:
    10 - missing script parameter or using a prohibited combination of parameters,
    11 - error when opening input files (eg non-existence, insufficient permissions),
    12 - error when opening output files for writing (insufficient permissions, writing error),
    21 - wrong or missing header in the source code written in IPPcode24,
    22 - unknown or incorrect operation code in the source code written in IPPcode24,
    23 - other lexical or syntactic error of the source code written in IPPcode24;""")
    print("-------------------------------------------------------------------------------------------------------------------")
    print("""Parameters:
    --help: Prints this help message,
    --stats=file: Specifies the file where statistics will be written, can be used multiple times with different files,
    --loc: Counts the number of lines with instructions (excluding empty, comment-only and the header line),
    --comments: Counts the number of lines containing comments,
    --labels: Counts the number of defined unique labels,
    --jumps: Counts the total number of jump and return instructions.
    --fwjumps: Counts the number of forward jumps,
    --backjumps: Counts the number of backward jumps,
    --badjumps: Counts the number of jumps to non-existing labels,
    --frequent: Lists the most frequent operation codes in the source code,
    --print=string: Prints the specified string,
    --eol: Prints an new-line character.""")
    print("-------------------------------------------------------------------------------------------------------------------")

def error_exit(error_code):
    """Exit with given error code."""
    sys.exit(error_code)

def parse_instruction(line):
    """Parsing of an instruction line and return of XML for the instruction and its arguments."""
    # Parses only the part before the possible comment
    tokens = line.split('#')[0].strip().split() 
    if not tokens:
        return ""
    
    # Double header is a syntax error
    if tokens[0].upper() == ".IPPCODE24":
        error_exit(ERR_OTHER_SYNTAX_ERROR)
        
    # Separates the instruction and operands
    opcode = tokens[0].upper()
    operands = tokens[1:]
    operands_type = opcode_validate(opcode, operands)

    # Constructs XML for the instruction
    xml = f"    <instruction order=\"{parse_instruction.order}\" opcode=\"{opcode}\">\n"
    for i, operand in enumerate(operands, start=1):
        xml += f"        <arg{i} type=\"{operands_type[i-1]}\">{lib_parse.xml_entities(lib_parse.get_text_elenent(operand))}</arg{i}>\n"
    xml += f"    </instruction>\n"
    parse_instruction.order += 1
    return xml

def parse_source_code():
    """Parsing of the source code and generation of XML."""
    # Reads source code from standard input
    # I decided to make a copy of source code and 
    # modify the first string while parsing 
    source_code = sys.stdin.readlines()
    source_code_for_stats = source_code

    # Removes whitespaces and deletes empty and comment lines
    source_code = lib_stats.remove_lines(source_code)
    # Checks for IPPcode24 header
    if not source_code or source_code[0].split('#')[0].strip().upper() != ".IPPCODE24":
        error_exit(ERR_HEADER)
    
    parse_instruction.order = 1
    # Generates XML
    xml = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<program language=\"IPPcode24\">\n"
    for line in source_code[1:]:
        xml += parse_instruction(line)
    xml += "</program>"
    
    # When all lines are parsed, the statistics can be calculated
    if stats_parameters:
        calculate_statistics(source_code_for_stats)
    
    return xml

def calculate_statistics(source_code):
     """Function to calculate statistics for all groups"""
     # A loop through the dictionary with all files and stats groups
     for file_name, parameters in stats_parameters.items():
        # Rewrites the existing file
        try:
            with open(file_name, 'w') as file:
                pass
        except Exception:
            error_exit(ERR_OUTPUT)
        # Opens the file to append statistics text
        try:
            with open(file_name, 'a') as file:
                for parameter in parameters:
                    if parameter == '--loc':
                        file.write(str(lib_stats.count_loc(source_code)) + '\n')
                    elif parameter == '--comments' or parameter == '-comments':
                        file.write(str(lib_stats.count_comments(source_code)) + '\n')
                    elif parameter == '--labels' or parameter == '-labels':
                        file.write(str(lib_stats.count_unique_labels(source_code)) + '\n')
                    elif parameter == '--jumps' or parameter == '-jumps':
                        file.write(str(lib_stats.count_returns_and_jumps(source_code)) + '\n')
                    elif parameter == '--fwjumps' or parameter == '-fwjumps':
                        file.write(str(lib_stats.count_forward_jumps(source_code)) + '\n')
                    elif parameter == '--backjumps' or parameter == '-backjumps':
                        file.write(str(lib_stats.count_backward_jumps(source_code)) + '\n')
                    elif parameter == '--badjumps' or parameter == '-badjumps':
                        file.write(str(lib_stats.count_bad_jumps(source_code)) + '\n')
                    elif parameter == '--frequent' or parameter == '-frequent':
                        file.write(str(lib_stats.range_instructions_frequency(source_code)) + '\n')
                    elif parameter == '--eol' or parameter == '-eol':
                        file.write('\n')
                    elif parameter.startswith('--print=') or parameter.startswith('-print='):
                        file.write(parameter.split('=')[1])
                    else:
                        error_exit(ERR_PARAMETER)
        except Exception:
            error_exit(ERR_OUTPUT)

def parse_parameters():
    """Parameter parsing function."""
    # Parses parameter --help and checks for possible parameter errors
    if "--help" in sys.argv or "-help" in sys.argv:
        if len(sys.argv) == 2:
            print_help()
            sys.exit(0)
        if len(sys.argv) > 2:
            error_exit(ERR_PARAMETER)
    elif sys.argv[1].startswith('--stats=') or\
    sys.argv[1].startswith('-stats='):
        parse_stats_parameters()
    else:
        error_exit(ERR_PARAMETER)

def parse_stats_parameters():
    """Parsing of statictics parameters"""
    i = 1
    while i < len(sys.argv):
        if sys.argv[i].startswith('--stats=') or\
        sys.argv[i].startswith('-stats='):
            # Gets the filename and checks if it differs from other files
            file_name = sys.argv[i].split('=')[1]
            if file_name in stats_parameters:
                error_exit(ERR_OUTPUT) 
            params = []
            j = i + 1
            # Gets a group of parameters
            while j < len(sys.argv) and not (sys.argv[j].startswith('--stats=') or\
            sys.argv[j].startswith('-stats=')):
                params.append(sys.argv[j])
                j += 1
            # A dictionary for filename and parameters group
            stats_parameters[file_name] = params
            i = j
        else:
            i += 1

def opcode_validate(opcode, operands):
    """Opcode validation and creation of list of instruction operands types"""
    if not lib_parse.opcode_regex(opcode):
        error_exit(ERR_OTHER_SYNTAX_ERROR)
    # 0 operands
    if opcode == "CREATEFRAME" or \
    opcode == "PUSHFRAME" or \
    opcode == "POPFRAME" or \
    opcode == "RETURN" or \
    opcode == "BREAK":
        if len(operands) != 0:
            error_exit(ERR_OTHER_SYNTAX_ERROR)

    # 1 operand - label
    elif opcode == "CALL" or \
    opcode == "LABEL" or\
    opcode == "JUMP":
        if len(operands) != 1 or \
        not lib_parse.label_validate(operands[0]):
            error_exit(ERR_OTHER_SYNTAX_ERROR)
        return ["label"]
    
    # 1 operand - var
    elif opcode == "DEFVAR" or \
    opcode == "POPS":
        if len(operands) != 1 or\
        not lib_parse.var_validate(operands[0]):
            error_exit(ERR_OTHER_SYNTAX_ERROR)
        return ["var"]
    
    # 1 operand - symbol 
    elif opcode == "PUSHS" or \
    opcode == "WRITE" or \
    opcode == "EXIT" or \
    opcode == "DPRINT":
        if len(operands) != 1 or \
        not lib_parse.symbol_validate(operands[0]):
            error_exit(ERR_OTHER_SYNTAX_ERROR)
        return [lib_parse.get_symbol_type(operands[0])]
    
    # 2 operands - var symbol
    elif opcode == "MOVE" or \
    opcode == "INT2CHAR" or \
    opcode == "STRLEN" or \
    opcode == "TYPE" or \
    opcode == "NOT":
        if len(operands) != 2 or \
        not lib_parse.var_validate(operands[0]) or \
        not lib_parse.symbol_validate(operands[1]):
            error_exit(ERR_OTHER_SYNTAX_ERROR)
        return ["var", lib_parse.get_symbol_type(operands[1])]
    
    # 2 operands - var type
    elif opcode == "READ":
        if len(operands) != 2 or \
        not lib_parse.var_validate(operands[0]) or \
        not lib_parse.type_validate(operands[1]):
            error_exit(ERR_OTHER_SYNTAX_ERROR)
        return ["var", "type"]
    
    # 3 operands - var symbol1 symbol2
    elif opcode == "ADD" or \
    opcode == "SUB" or \
    opcode == "MUL" or \
    opcode == "IDIV" or \
    opcode == "LT" or \
    opcode == "GT" or \
    opcode == "EQ" or \
    opcode == "AND" or \
    opcode == "OR" or \
    opcode == "STRI2INT" or \
    opcode == "CONCAT" or \
    opcode == "GETCHAR" or \
    opcode == "SETCHAR":
        if len(operands) != 3 or \
        not lib_parse.var_validate(operands[0]) or \
        not lib_parse.symbol_validate(operands[1]) or \
        not lib_parse.symbol_validate(operands[2]):
            error_exit(ERR_OTHER_SYNTAX_ERROR)
        return ["var", lib_parse.get_symbol_type(operands[1]), lib_parse.get_symbol_type(operands[2])]
    
    # 3 operands - label symbol1 symbol2
    elif opcode == "JUMPIFEQ" or \
    opcode == "JUMPIFNEQ":
        if len(operands) != 3 or \
        not lib_parse.label_validate(operands[0]) or \
        not lib_parse.symbol_validate(operands[1]) or \
        not lib_parse.symbol_validate(operands[2]):
            error_exit(ERR_OTHER_SYNTAX_ERROR)
        return ["label", lib_parse.get_symbol_type(operands[1]), lib_parse.get_symbol_type(operands[2])]
    else:
        error_exit(ERR_UNKNOWN_OPCODE)

def main():
    """Main function."""
    if len(sys.argv)>1:
        parse_parameters()
    
    # If stdin is valid, the source code is parsed
    if not sys.stdin.isatty():
        xml_representation = parse_source_code()
        print(xml_representation)
        sys.exit(0)
    else:
        error_exit(ERR_INPUT)

if __name__ == "__main__":
    main()