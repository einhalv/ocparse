import ocparse

# From Fig-3.1 in ARM DDI0100E
# Have edited to UNPREDICTABLE where that applies to ARMv4T
m31 = ocparse.Analyzer([
    ('cccc|000|oo o o|S|nnnn|dddd|sssss |TT|0|mmmm', 'Data_Processing_Immediate_Shift[1]'),
    ('cccc|000|10 * *|0|**** **** *****  **|0|****', 'Miscellaneous_Fig_3.3[1]'),
    ('cccc|000|oo o o|S|nnnn|dddd|ssss|0|TT|1|mmmm', 'Data_Processing_Register_Shift[1][2]'),
    ('cccc|000|10 * *|0|**** **** ****|0|**|1|****', 'Miscellaneous_Fig_3.3[1]'),
    ('cccc|000|** * * * **** **** ****|1|**|1|****', 'Multiplies_extra_load/stores_Fig_3.2[1]'),
    ('cccc|001|oo o o|S|nnnn|dddd|RRRR|   IIIIIIII', 'Data_Processing_Immediate[1][2]'),
    ('cccc|001|10|*|0 0|**** **** **** * ** * ****', 'Undefined_instruction[1]'),
    ('cccc|001|10|R|1 0|MMMM|OOOO|RRRR|   IIIIIIII', 'Move_immediate_to_status_register[1]'),
    ('cccc|010|PU B W L|nnnn|dddd|    IIIIIIIIIIII', 'Load/store_immediate_offset[1]'),
    ('cccc|011|PU B W L|nnnn|dddd|sssss |TT|0|mmmm', 'Load/store_register_offset[1]'),
    ('cccc|011|** * * * **** **** *****  **|1|****', 'Undefined_instruction[1]'),
    ('1111|0|**** * * * **** **** *****  ** * ****', 'UNPREDICTABLE'),
    ('cccc|100|PU S W L|nnnn|     llllllllllllllll', 'Load/store_multiple[1]'),
    ('1111|100|** * * * **** **** *****  ** * ****', 'UNPREDICTABLE'),
    ('cccc|101|L|    oooo oooo oooo oooo oooo oooo', 'Branch_and_branch_with_link[1]'),
    ('1111|101|H|    oooo oooo oooo oooo oooo oooo', 'UNPREDICTABLE'),
    ('cccc|110|PU N W L|nnnn|dddd|####|  oooo oooo', 'Coprocessor_load/store_and_double_register_transfers[5][6]'),
    ('cccc|111 0|  oooo|nnnn|dddd|####|ppp|0| mmmm', 'Coprocessor_data_processing[5]'),
    ('cccc|111 0| ooo|L|nnnn|dddd|####|ppp|1| mmmm', 'Coprocessor_register_transfers[5]'),
    ('cccc|1111|     iiii iiii iiii iiii iiii iiii', 'Software_Interrupt[1]'),
    ('1111|1111|     **** **** **** **** **** ****', 'UNPREDICTABLE')
    ]
)
# Notes
# [1] The cond field is not allowed to be 1111 in this line. Other lines deal with the cases where
#     bits[31:28] of the instruction are 1111.
# [2] If the opcode field is of the form 10xx and the S field is 0, one of the following lines applies instead
# [5] If the cond field is 1111, this instruction is UNPREDICTABLE prior to ARM architecture version 5.
# [6] The coprocessor double register transfer instructions are described in Chapter A10 Enhanced DSP
#     Extension

# From Fig-3.2 "Multiplies extra load/stores" in ARM DDI0100E
m32 = ocparse.Analyzer(
    [
        ('cccc|0000|0 0|A |S|dddd|nnnn|ssss|1001|mmmm', 'Multiply_(accumulate)'),
        ('cccc|0000|1 U|A |S|hhhh|llll|ssss|1001|mmmm', 'Multiply_(accumulate)_long'),
        ('cccc|0001 0|B|0  0|nnnn|dddd|ZZZZ|1001|mmmm', 'Swap/swap_byte'),
        ('cccc|000|P|U|0|W|L|nnnn|dddd|ZZZZ|1011|mmmm', 'Load/store_halfword_register_offset'),
        ('cccc|000|P|U|1|W|L|nnnn|dddd|hhhh|1011|llll', 'Load/store_halfword_immediate_offset'),
        ('cccc|000|P|U|0|W|0|nnnn|dddd|ZZZZ|11S1|mmmm', 'Load/store_two_words_register_offset[2]'),
        ('cccc|000|P|U|0|W|1|nnnn|dddd|ZZZZ|11H1|mmmm', 'Load_signed_halfword/byte_register_offset'),
        ('cccc|000|P|U|1|W|0|nnnn|dddd|hhhh|11S1|llll', 'Load/store_two words_immediate_offset[2]'),
        ('cccc|000|P|U|1|W|1|nnnn|dddd|hhhh|11H1|llll', 'Load_signed_halfword/byte_immediate_offset')
    ]
)
# Notes
# [2] These instructions are described in Chapter A10 Enhanced DSP Extension.
#
# Any instruction with bits[27:25] = 000, bit[7] = 1, bit[4] = 1, and cond not equal to 1111, and which is not
# specified in Figure 3-2 or its notes, is an undefined instruction (or UNPREDICTABLE prior to ARM
# architecture version 4).


# From Fig-3.3 "Miscellaneous instructions" in ARM DDI0100E
m33 = ocparse.Analyzer(
    [
        ('cccc|00010|R|0|0|OOOO|dddd|ZZZZ|0000|ZZZZ', 'Move_status_register_to_register'),
        ('cccc|00010|R|1|0|pppp|OOOO|ZZZZ|0000|mmmm', 'Move_register_to_status_register'),
        ('cccc|00010|0 1|0|OOOO|OOOO|OOOO|0001|mmmm', 'Branch_and_Exchange'),
        ('cccc|00010|1 1|0|OOOO|dddd|OOOO|0001|mmmm', 'Undefined_instruction'),
        ('cccc|00010|0 1|0|OOOO|OOOO|OOOO|0011|mmmm', 'Undefined_instruction'),
        ('cccc|00010|o o|0|nnnn|dddd|ZZZZ|0101|mmmm', 'Enhanced_DSP_add/subtracts[4]'),
        ('cccc|00010|0 1|0|IIII IIII IIII|0111|iiii', 'Software_breakpoint2][3]'),
        ('cccc|00010|o o|0|dddd|nnnn|ssss|1yx0|mmmm', 'Enhanced_DSP_multiplies[4]')
    ]
)
# Notes
# [4] The enhanced DSP instructions are described in Chapter A10 Enhanced DSP Extension.

# From manual:
# Should-Be-One fields (SBO)
# Should be written as 1 (or all 1s for bit fields) by software. Values other than 1 produce UNPREDICTABLE
# results.
#
# Should-Be-Zero fields (SBZ)
# Should be written as zero (or all 0s for bit fields) by software. Non-zero values produce UNPREDICTABLE
# results.
#
# Here: SBO -> O, SBZ->Z


#  Chapter A10 Enhanced DSP Extension
#  For all instructions, this chapter lists them as valid for armv5 and above.
