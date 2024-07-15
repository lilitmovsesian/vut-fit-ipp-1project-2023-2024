"""Helper functions for operands parsing in parse.py"""
import re

def opcode_regex(opcode):
    opcode_pattern = r'^[a-zA-Z0-9]+$'
    if re.fullmatch(opcode_pattern, opcode):
        return True
    else:
        return False
    
def var_validate(operand):
    """Validation of "var" argument."""
    # Regex for variable correct syntax
    var_pattern = r'[LTG]F@[A-Za-z_\-&%*$!?][A-Za-z0-9_\-&%*$!?]*'
    if re.fullmatch(var_pattern, operand):
        return True
    else:
        return False

def label_validate(operand): 
    """Validation of "label" argument."""
    # Regex for label correct syntax
    label_pattern = r'[A-Za-z_\-&%*$!?][A-Za-z0-9_\-&%*$!?]*'
    if re.fullmatch(label_pattern, operand):
        return True
    else:
        return False

def symbol_validate(operand):
    """Validation of "symbol" argument."""
    # Regex for integers and strings correct syntax
    dec_pattern = r'^int@[-+]?(_?[0-9])*$|^int@-?0(_?0)*$'
    oct_pattern = r'^int@[-+]?0[oO](_?[0-7])+$'
    hex_pattern = r'^int@[-+]?0[xX](_?[0-9a-fA-F])+$'
    string_pattern = r'^string@(?:[^#\\]|\\[0-9]{3})*$'
    
    # If argument is not a variable, script checks
    # for the constants, if the syntax is correct 
    # returns True, else False
    if not var_validate(operand):
        if operand.startswith("int@") and operand!="int@":
            if re.fullmatch(dec_pattern, operand) or\
            re.fullmatch(oct_pattern, operand) or\
            re.fullmatch(hex_pattern, operand):
                return True
        elif operand.startswith("bool@"):
            if operand == "bool@true" or\
            operand == "bool@false":
                return True
        elif operand.startswith("nil@"):
            if operand == "nil@nil":
                return True
        elif operand.startswith("string@"):
            if re.fullmatch(string_pattern, operand):
                return True
        return False
    return True

def type_validate(operand):
    """Validation of "type" argument."""
    if operand == "int" or \
    operand == "bool" or \
    operand == "nil" or \
    operand == "string":
        return True
    else:
        return False

def get_text_elenent(operand):
    """Correction of constants format."""
    if operand.startswith("int@") or operand.startswith("bool@") or operand.startswith("string@") or operand.startswith("nil@"):
        return operand.split('@', 1)[1].strip()
    else:
        return operand

def get_symbol_type(operand):
    """Determination of the type of the symbol."""
    if operand.startswith("int@"):
        return "int"
    elif operand.startswith("bool@"):
        return "bool"
    elif operand.startswith("string@"):
        return "string"
    elif operand.startswith("nil@"):
        return "nil"
    elif operand.startswith("GF@") or operand.startswith("LF@") or operand.startswith("TF@"):
        return "var"

def xml_entities(value):
    """Replacement of problematic characters with XML entities."""
    value = value.replace("&", "&amp;")
    value = value.replace("<", "&lt;")
    value = value.replace(">", "&gt;")
    return value