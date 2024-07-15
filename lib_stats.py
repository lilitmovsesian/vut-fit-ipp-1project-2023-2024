"""Helper functions for calculation of statistics in parse.py"""
from collections import Counter

def remove_lines(source_code):
    """Helper function which removes empty lines and comment lines."""
    return [line.strip() for line in source_code if line.strip() and not line.strip().startswith('#')]

def count_loc(source_code):
    """Calculation of the number of lines with instructions"""
    source_code = remove_lines(source_code)
    return len(source_code)-1

def count_comments(source_code):
    """Calculation of the number of lines with comments"""
    count = 0
    for line in source_code:
        if '#' in line:
            count += 1
    return count

def count_unique_labels(source_code):
    """Calculation of unique labels in the source code"""
    # A set to gather only unique labels
    labels = set()
    count = 0
    for line in source_code:
        tokens = line.split()
        if tokens and tokens[0] == "LABEL":
            count += 1
            labels.add(tokens[1])
    return count

def count_returns_and_jumps(source_code):
    """Calculation of all returns and jumps in the source code"""
    instructions = ["RETURN", "CALL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ"]
    count = 0
    for line in source_code:
        tokens = line.split()
        if tokens and tokens[0] in instructions:
            count += 1
    return count

def count_forward_jumps(source_code):
    """Calculation of jumps to label which are defined later in source code"""
    instructions = ["CALL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ"]
    count = 0
    # Iterates through lines, when a jump is encountered
    # searches for a target label in subsequent lines
    for i, line in enumerate(source_code):
        tokens = line.split()
        if tokens and tokens[0] in instructions:
            instruction_label = tokens[1]
            for next_line in source_code[i+1:]:
                if next_line.strip().startswith("LABEL"):
                    label_name = next_line.strip().split()[1]
                    if instruction_label == label_name:
                        count += 1
                        break
    return count

def count_backward_jumps(source_code):
    """Calculation of jumps to label which are defined in previous instructions in source code"""
    instructions = ["CALL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ"]
    count = 0
    # Iterates through lines, when a jump is encountered
    # searches for a target label in previous lines
    for i, line in enumerate(source_code):
        tokens = line.split()
        if tokens and tokens[0] in instructions:
            instruction_label = tokens[1]
            for prev_line in reversed(source_code[:i]):
                if prev_line.strip().startswith("LABEL"):
                    label_name = prev_line.strip().split()[1]
                    if instruction_label == label_name:
                        count += 1
                        break
    return count

def count_bad_jumps(source_code):
    """Calculation of jumps to label which are not defined"""
    instructions = ["CALL", "JUMP", "JUMPIFEQ", "JUMPIFNEQ"]
    count = 0
    # Iterates through lines, when a jump is encountered
    # searches for a target label
    for line in source_code:
        tokens = line.split()
        if tokens and tokens[0] in instructions:
            instruction_label = tokens[1]
            found = False
            for label_line in source_code:
                if label_line.strip().startswith("LABEL"):
                    label_name = label_line.strip().split()[1]
                    if instruction_label == label_name:
                        found = True
                        break
            if found == False:
                count+=1
    return count

def range_instructions_frequency(source_code):
    """Sorting od instruction by the frequency in the source code"""
    source_code = remove_lines(source_code)
    # Adds all instruction to the list
    instructions = []
    for line in source_code[1:]:
        tokens = line.split()
        if tokens:
            instructions.append(tokens[0])
    # Counts the instructions in the list, sorts them and formats correctly
    instruction_counts = Counter(instructions)
    sorted_instructions = sorted(instruction_counts.items(), key=lambda x: (-x[1], x[0]))
    formatted_instructions = ','.join(instruction[0].upper() for instruction in sorted_instructions)
    return formatted_instructions