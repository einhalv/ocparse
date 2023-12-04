# ARMV4T analyzer-example

This is an example of how one can use ocparse to analyze and manipulate the ARMV4T instruction set. The technical content is based on the defintions given in the "ARM Architecture Reference Manual" document number ARM DDI 0100E.

We we will use Analyzer object to make unique opcode descriptions for the entire ARM instruction set in a way that can be useful for a parser for a disassembler or an emulator.

## Defining the instructions set in an Analyzer objects
We can start by importing Analyzer objects corresponding to figures 3.1, 3.2 and 3.3 of the reference manual and listing the content of the three analyzer objects `m31`, `m32` and `m33` defined in [armv4t_spec.py](armv4t_spec.py) using the `ls` method:
```python
>>> from armv4t_spec import *
>>> m31.ls()
 0  cccc|000|oo o o|S|nnnn|dddd|sssss |TT|0|mmmm  Data_Processing_Immediate_Shift[1]
 1  cccc|000|10 * *|0|**** **** *****  **|0|****  Miscellaneous_Fig_3.3[1]
 2  cccc|000|oo o o|S|nnnn|dddd|ssss|0|TT|1|mmmm  Data_Processing_Register_Shift[1][2]
 3  cccc|000|10 * *|0|**** **** ****|0|**|1|****  Miscellaneous_Fig_3.3[1]
 4  cccc|000|** * * * **** **** ****|1|**|1|****  Multiplies_extra_load/stores_Fig_3.2[1]
 5  cccc|001|oo o o|S|nnnn|dddd|RRRR|   IIIIIIII  Data_Processing_Immediate[1][2]
 6  cccc|001|10|*|0 0|**** **** **** * ** * ****  Undefined_instruction[1]
 7  cccc|001|10|R|1 0|MMMM|OOOO|RRRR|   IIIIIIII  Move_immediate_to_status_register[1]
 8  cccc|010|PU B W L|nnnn|dddd|    IIIIIIIIIIII  Load/store_immediate_offset[1]
 9  cccc|011|PU B W L|nnnn|dddd|sssss |TT|0|mmmm  Load/store_register_offset[1]
10  cccc|011|** * * * **** **** *****  **|1|****  Undefined_instruction[1]
11  1111|0|**** * * * **** **** *****  ** * ****  UNPREDICTABLE
12  cccc|100|PU S W L|nnnn|     llllllllllllllll  Load/store_multiple[1]
13  1111|100|** * * * **** **** *****  ** * ****  UNPREDICTABLE
14  cccc|101|L|    oooo oooo oooo oooo oooo oooo  Branch_and_branch_with_link[1]
15  1111|101|H|    oooo oooo oooo oooo oooo oooo  UNPREDICTABLE
16  cccc|110|PU N W L|nnnn|dddd|####|  oooo oooo  Coprocessor_load/store_and_double_register_transfers[5][6]
17  cccc|111 0|  oooo|nnnn|dddd|####|ppp|0| mmmm  Coprocessor_data_processing[5]
18  cccc|111 0| ooo|L|nnnn|dddd|####|ppp|1| mmmm  Coprocessor_register_transfers[5]
19  cccc|1111|     iiii iiii iiii iiii iiii iiii  Software_Interrupt[1]
20  1111|1111|     **** **** **** **** **** ****  UNPREDICTABLE
>>> m32.ls()
0  cccc|0000|0 0|A |S|dddd|nnnn|ssss|1001|mmmm  Multiply_(accumulate)
1  cccc|0000|1 U|A |S|hhhh|llll|ssss|1001|mmmm  Multiply_(accumulate)_long
2  cccc|0001 0|B|0  0|nnnn|dddd|ZZZZ|1001|mmmm  Swap/swap_byte
3  cccc|000|P|U|0|W|L|nnnn|dddd|ZZZZ|1011|mmmm  Load/store_halfword_register_offset
4  cccc|000|P|U|1|W|L|nnnn|dddd|hhhh|1011|llll  Load/store_halfword_immediate_offset
5  cccc|000|P|U|0|W|0|nnnn|dddd|ZZZZ|11S1|mmmm  Load/store_two_words_register_offset[2]
6  cccc|000|P|U|0|W|1|nnnn|dddd|ZZZZ|11H1|mmmm  Load_signed_halfword/byte_register_offset
7  cccc|000|P|U|1|W|0|nnnn|dddd|hhhh|11S1|llll  Load/store_two words_immediate_offset[2]
8  cccc|000|P|U|1|W|1|nnnn|dddd|hhhh|11H1|llll  Load_signed_halfword/byte_immediate_offset
>>> m33.ls()
0  cccc|00010|R|0|0|OOOO|dddd|ZZZZ|0000|ZZZZ  Move_status_register_to_register
1  cccc|00010|R|1|0|pppp|OOOO|ZZZZ|0000|mmmm  Move_register_to_status_register
2  cccc|00010|0 1|0|OOOO|OOOO|OOOO|0001|mmmm  Branch_and_Exchange
3  cccc|00010|1 1|0|OOOO|dddd|OOOO|0001|mmmm  Undefined_instruction
4  cccc|00010|0 1|0|OOOO|OOOO|OOOO|0011|mmmm  Undefined_instruction
5  cccc|00010|o o|0|nnnn|dddd|ZZZZ|0101|mmmm  Enhanced_DSP_add/subtracts[4]
6  cccc|00010|0 1|0|IIII IIII IIII|0111|iiii  Software_breakpoint2][3]
7  cccc|00010|o o|0|dddd|nnnn|ssss|1yx0|mmmm  Enhanced_DSP_multiplies[4]
>>>
```

Note that the reference manual also covers higher versions than v4t. In the present Analyzer objects
this has been accounted for by declaring some opcodes as UNPREDICTABLE which are so for v4, but not
necessarily for, say, v5. It is worth checking which simplifications follows for our problem.
Furthermore, In m31, opcode patterns 1 and 3 apparently represent instructions defined in m33
and opcode pattern 4 represents patterns in m32. We must eventually merge these in.

## Instructions deemed 'UNPREDICTABLE'
Starting with m31, we note that the "UNPREDICTABLE" patterns (no. 11, 13, 15 and 20)  all start with 1111 while the others start with the generic field cccc representing the condition code for the instructions. The footnote [1] refers to a statement in the manual that the condition code can not be 1111 for the pattern in question and that that particular situation is taken care of by other patterns. Hence we can disregard the possibility of this condition code for patterns 0-10, 12, 14 and 19. For the remaining opcode patterns 16, 17 and 18 the manual states the a condition field of 1111 renders the instruction "UNPREDICTABLE" for version prior to 5, so we can count these out also. Therefore let us split the patterns into to sets, one with generic condition bits cccc different from 1111 and another with cccc = 1111:
```Python
>>> a = m31.copy_current()
>>> a.delcodes([11, 13, 15, 20])
>>> unpred = m31.copy_current([11, 13, 15, 16, 17, 18, 20])
>>> unpred.rmbits([31, 30, 29, 28])
>>> unpred.ls()
0  |0|**** * * * **** **** *****  ** * ****  UNPREDICTABLE
1  |100|** * * * **** **** *****  ** * ****  UNPREDICTABLE
2  |101|H|    oooo oooo oooo oooo oooo oooo  UNPREDICTABLE
3  |110|PU N W L|nnnn|dddd|####|  oooo oooo  Coprocessor_load/store_and_double_register_transfers[5][6]
4  |111 0|  oooo|nnnn|dddd|####|ppp|0| mmmm  Coprocessor_data_processing[5]
5  |111 0| ooo|L|nnnn|dddd|####|ppp|1| mmmm  Coprocessor_register_transfers[5]
6  |1111|     **** **** **** **** **** ****  UNPREDICTABLE
>>> 
```
We see that of the latter patterns 4 and 5 together is equivalent to ```1110 **** **** **** **** ****``` which together with pattern 6 yields ```111* **** **** **** **** ****```. Combining this pattern with 3 then yields ```11** **** **** **** **** ****```. Patterns 1 and 2 combines to ```10** **** **** **** **** ****``` which combined with ```11** **** **** **** **** ****```
gives ```1*** **** **** **** **** ****```. This last pattern combined with pattern zero finally gives ```**** **** **** **** **** ****``` showing that all the patterns are covered. Hence, all possible opcodes with condition bits 1111 are defined as 'UNPREDICTABLE' by the manual. We can now proceed with the remaining opcodes.

## Merging miscellaneous opcode patterns

Let us merge m33 into a. We first adapt to v4.
Then we split m33 according to bit 4 (and 7). 
```Python
>>> m0 = m33.copy_current([0, 1]) # skip 7 as it was not defined in v4
>>> m1 = m33.copy_current([2, 3, 4, 6])
>>> m1.get_codes()[3].desc = 'Undefined instruction'  # Undefined in v4
>>> m0.ls()
0  cccc|00010|R|0|0|OOOO|dddd|ZZZZ|0000|ZZZZ  Move_status_register_to_register
1  cccc|00010|R|1|0|pppp|OOOO|ZZZZ|0000|mmmm  Move_register_to_status_register
>>> m1.ls()
0  cccc|00010|0 1|0|OOOO|OOOO|OOOO|0001|mmmm  Branch_and_Exchange
1  cccc|00010|1 1|0|OOOO|dddd|OOOO|0001|mmmm  Undefined_instruction
2  cccc|00010|0 1|0|OOOO|OOOO|OOOO|0011|mmmm  Undefined_instruction
3  cccc|00010|0 1|0|IIII IIII IIII|0111|iiii  Undefined instruction
>>> m0.replace_field('O', '1')  # replace should be ones
>>> m0.replace_field('Z', '0')  # replace should be zeros
>>> m1.replace_field('O', '1', [0])  # replace should be ones
>>> m1.replace_field('d', '*', [1])  # no need for field name in undef
>>> m1.replace_field('O', '*', [1, 2])  # no need for field name in undef
>>> m1.replace_field('m', '*', [1, 2])  # no need for field name in undef
>>> m1.replace_field('I', '*', [3])  # no need for field name in undef
>>> m1.replace_field('i', '*', [3])  # no need for field name in undef
>>> m0.ls()
0  cccc|00010|R|0|0|1111|dddd|0000|0000|0000  Move_status_register_to_register
1  cccc|00010|R|1|0|pppp|1111|0000|0000|mmmm  Move_register_to_status_register
>>> m1.ls()
0  cccc|00010|0 1|0|1111|1111|1111|0001|mmmm  Branch_and_Exchange
1  cccc|00010|1 1|0|****|****|****|0001|****  Undefined_instruction
2  cccc|00010|0 1|0|****|****|****|0011|****  Undefined_instruction
3  cccc|00010|0 1|0|**** **** ****|0111|****  Undefined instruction
>>> a.ls()
 0  cccc|000|oo o o|S|nnnn|dddd|sssss |TT|0|mmmm  Data_Processing_Immediate_Shift[1]
 1  cccc|000|10 * *|0|**** **** *****  **|0|****  Miscellaneous_Fig_3.3[1]
 2  cccc|000|oo o o|S|nnnn|dddd|ssss|0|TT|1|mmmm  Data_Processing_Register_Shift[1][2]
 3  cccc|000|10 * *|0|**** **** ****|0|**|1|****  Miscellaneous_Fig_3.3[1]
 4  cccc|000|** * * * **** **** ****|1|**|1|****  Multiplies_extra_load/stores_Fig_3.2[1]
 5  cccc|001|oo o o|S|nnnn|dddd|RRRR|   IIIIIIII  Data_Processing_Immediate[1][2]
 6  cccc|001|10|*|0 0|**** **** **** * ** * ****  Undefined_instruction[1]
 7  cccc|001|10|R|1 0|MMMM|OOOO|RRRR|   IIIIIIII  Move_immediate_to_status_register[1]
 8  cccc|010|PU B W L|nnnn|dddd|    IIIIIIIIIIII  Load/store_immediate_offset[1]
 9  cccc|011|PU B W L|nnnn|dddd|sssss |TT|0|mmmm  Load/store_register_offset[1]
10  cccc|011|** * * * **** **** *****  **|1|****  Undefined_instruction[1]
11  cccc|100|PU S W L|nnnn|     llllllllllllllll  Load/store_multiple[1]
12  cccc|101|L|    oooo oooo oooo oooo oooo oooo  Branch_and_branch_with_link[1]
13  cccc|110|PU N W L|nnnn|dddd|####|  oooo oooo  Coprocessor_load/store_and_double_register_transfers[5][6]
14  cccc|111 0|  oooo|nnnn|dddd|####|ppp|0| mmmm  Coprocessor_data_processing[5]
15  cccc|111 0| ooo|L|nnnn|dddd|####|ppp|1| mmmm  Coprocessor_register_transfers[5]
16  cccc|1111|     iiii iiii iiii iiii iiii iiii  Software_Interrupt[1]
>>> a.delcodes([3])
>>> a.merge(m1, 3)
>>> a.delcodes([1])
>>> a.merge(m0, 1)
>>> a.move(14, 20)
>>> a.move(10, 20)
>>> a.move(7, 20)
>>> a.move(6, 20)
>>> a.move(5, 20)
>>> a.delsep(list(range(0,33)), [16, 17, 18, 19, 20])
>>> a.newcode('cccc00010010************0*11****', 'Undefined_instruction', 18)
>>> a.delcodes([19, 20])
>>> for ac in a.get_codes()[-4:-2]:
...     ac.desc = 'Undefined_instruction'
... 
>>> a.ls()
 0  cccc|000|oo o o|S|nnnn|dddd|sssss |TT|0|mmmm  Data_Processing_Immediate_Shift[1]
 1     cccc|00010|R|0|0|1111|dddd|0000|0000|0000  Move_status_register_to_register
 2     cccc|00010|R|1|0|pppp|1111|0000|0000|mmmm  Move_register_to_status_register
 3  cccc|000|oo o o|S|nnnn|dddd|ssss|0|TT|1|mmmm  Data_Processing_Register_Shift[1][2]
 4     cccc|00010|0 1|0|1111|1111|1111|0001|mmmm  Branch_and_Exchange
 5  cccc|000|** * * * **** **** ****|1|**|1|****  Multiplies_extra_load/stores_Fig_3.2[1]
 6  cccc|001|oo o o|S|nnnn|dddd|RRRR|   IIIIIIII  Data_Processing_Immediate[1][2]
 7  cccc|001|10|R|1 0|MMMM|OOOO|RRRR|   IIIIIIII  Move_immediate_to_status_register[1]
 8  cccc|010|PU B W L|nnnn|dddd|    IIIIIIIIIIII  Load/store_immediate_offset[1]
 9  cccc|011|PU B W L|nnnn|dddd|sssss |TT|0|mmmm  Load/store_register_offset[1]
10  cccc|100|PU S W L|nnnn|     llllllllllllllll  Load/store_multiple[1]
11  cccc|101|L|    oooo oooo oooo oooo oooo oooo  Branch_and_branch_with_link[1]
12  cccc|110|PU N W L|nnnn|dddd|####|  oooo oooo  Coprocessor_load/store_and_double_register_transfers[5][6]
13  cccc|111 0|  oooo|nnnn|dddd|####|ppp|0| mmmm  Coprocessor_data_processing[5]
14  cccc|111 0| ooo|L|nnnn|dddd|####|ppp|1| mmmm  Coprocessor_register_transfers[5]
15  cccc|1111|     iiii iiii iiii iiii iiii iiii  Software_Interrupt[1]
16              cccc011********************1****  Undefined_instruction
17              cccc00110*00********************  Undefined_instruction
18              cccc00010010************0*11****  Undefined_instruction
19              cccc00010110************0001****  Undefined_instruction
>>> 
```

## Resolving ambiguities
We can analyze the ambiguities in the current set of opcodes:
```Python
>>> a.lsambig()
0: Data_Processing_Immediate_Shift[1], 1: Move_status_register_to_register
0: Data_Processing_Immediate_Shift[1], 2: Move_register_to_status_register
3: Data_Processing_Register_Shift[1][2], 4: Branch_and_Exchange
3: Data_Processing_Register_Shift[1][2], 18: Undefined_instruction
3: Data_Processing_Register_Shift[1][2], 19: Undefined_instruction
6: Data_Processing_Immediate[1][2], 7: Move_immediate_to_status_register[1]
6: Data_Processing_Immediate[1][2], 17: Undefined_instruction
Number of ambiguities: 7

>>>
```
We note that all the ambiguities involve the data processing instructions. The footnote 2 from the manual states that
if the opcode field is of the form 10xx and the S field is 0, one of the following lines applies instead. That is because the instructions in question have as their sole purpose to set the status registers. Hence S=0 makes no sense. We see that the footnote only appears for opcode patterns 3 and 6, but the explanation is valid for pattern 0 also so we will take for granted that the omission of the footnote on this pattern is a typo and apply it also for this pattern. Other parts of the manual support that. To deal with the problem, we must expand the opocde field of 0, 2 and 5 and make sure those that begin with 10 all have S=1 as the only possibility. In doing so, it is convenient to also introduce mnemonics.

To expand to opcode field we first define the mnemonic and other info for possible later use for each opcode.
Then we need a function to modify the description before we can call the expand_field method to do the expansion.

```
>>> # define data processing operations and function for generating description
>>> dataproc = {
...     '0000': ('AND', 'Logical AND', 'Rd := Rn AND shifter_operand'),
...     '0001': ('EOR', 'Logical Exclusive OR', 'Rd := Rn EOR shifter_operand'),
...     '0010': ('SUB', 'Subtract', 'Rd := Rn - shifter_operand'),
...     '0011': ('RSB', 'Reverse Subtract', 'Rd := shifter_operand - Rn'),
...     '0100': ('ADD', 'Add', 'Rd := Rn + shifter_operand'),
...     '0101': ('ADC', 'Add with Carry', 'Rd := Rn + shifter_operand + Carry Flag'),
...     '0110': ('SBC', 'Subtract with Carry', 'Rd := Rn - shifter_operand - NOT(Carry Flag)'),
...     '0111': ('RSC', 'Reverse Subtract with Carry', 'Rd := shifter_operand - Rn - NOT(Carry Flag)'),
...     '1000': ('TST', 'Test', 'Update flags after Rn AND shifter_operand'),
...     '1001': ('TEQ', 'Test Equivalence', 'Update flags after Rn EOR shifter_operand'),
...     '1010': ('CMP', 'Compare', 'Update flags after Rn - shifter_operand'),
...     '1011': ('CMN', 'Compare Negated', 'Update flags after Rn + shifter_operand'),
...     '1100': ('ORR', 'Logical (inclusive) OR', 'Rd := Rn OR shifter_operand'),
...     '1101': ('MOV', 'Move', 'Rd := shifter_operand (no first operand)'),
...     '1110': ('BIC', 'Bit Clear', 'Rd := Rn AND NOT(shifter_operand)'),
...     '1111': ('MVN', 'Move Not', 'Rd := NOT shifter_operand (no first operand)'),
... }
>>> # expand and remove ooooo=10** with S=0
>>> def tag_operation(current_description, field_letter, pattern):
...     return dataproc[pattern][0] + ' ' + current_description.replace('Data_Processing_', '').replace('[1]', '').replace('[2]', '')
... 
>>> a.expand_field('o', [0, 3, 6], tag=tag_operation)
>>> a.expand_field('S', [8, 9, 10, 11, 26, 27, 28, 29, 44, 45, 46, 47], tag=lambda x, y, z: x)
>>> a.delcodes([8, 10, 12, 14, 30, 32, 34, 36, 52, 54, 56, 58])
>>> a.lsambig()
Number of ambiguities: 0

>>> 
```

## Merging in multiplies and extra load/stores
```Python
>>> from ocparse import *
>>> mls = m32.copy_current()
>>> codes=mls.get_codes()
>>> codes[5] = AnalyzerOpcode('cccc|000|*|*|0|*|0|****|****|0000|11*1|****', 'Undefined_instruction')  # undefined in v4
>>> codes[7] = AnalyzerOpcode('cccc|000|*|*|1|*|0|****|****|****|11*1|****', 'Undefined_instruction')  # undefined in v4
>>> mls.replace_field('Z', '0', [2, 3, 6])
>>> a.delcodes([35])
>>> a.merge(mls, 35)
>>> a.move(42, 71)
>>> a.move(40, 71)
>>> a.delsep(list(range(0,33)), [70, 71])
>>> a.ls()
 0  cccc|000|00 0 0|S|nnnn|dddd|sssss |TT|0|mmmm  AND Immediate_Shift
 1  cccc|000|00 0 1|S|nnnn|dddd|sssss |TT|0|mmmm  EOR Immediate_Shift
 2  cccc|000|00 1 0|S|nnnn|dddd|sssss |TT|0|mmmm  SUB Immediate_Shift
 3  cccc|000|00 1 1|S|nnnn|dddd|sssss |TT|0|mmmm  RSB Immediate_Shift
 4  cccc|000|01 0 0|S|nnnn|dddd|sssss |TT|0|mmmm  ADD Immediate_Shift
 5  cccc|000|01 0 1|S|nnnn|dddd|sssss |TT|0|mmmm  ADC Immediate_Shift
 6  cccc|000|01 1 0|S|nnnn|dddd|sssss |TT|0|mmmm  SBC Immediate_Shift
 7  cccc|000|01 1 1|S|nnnn|dddd|sssss |TT|0|mmmm  RSC Immediate_Shift
 8  cccc|000|10 0 0|1|nnnn|dddd|sssss |TT|0|mmmm  TST Immediate_Shift
 9  cccc|000|10 0 1|1|nnnn|dddd|sssss |TT|0|mmmm  TEQ Immediate_Shift
10  cccc|000|10 1 0|1|nnnn|dddd|sssss |TT|0|mmmm  CMP Immediate_Shift
11  cccc|000|10 1 1|1|nnnn|dddd|sssss |TT|0|mmmm  CMN Immediate_Shift
12  cccc|000|11 0 0|S|nnnn|dddd|sssss |TT|0|mmmm  ORR Immediate_Shift
13  cccc|000|11 0 1|S|nnnn|dddd|sssss |TT|0|mmmm  MOV Immediate_Shift
14  cccc|000|11 1 0|S|nnnn|dddd|sssss |TT|0|mmmm  BIC Immediate_Shift
15  cccc|000|11 1 1|S|nnnn|dddd|sssss |TT|0|mmmm  MVN Immediate_Shift
16     cccc|00010|R|0|0|1111|dddd|0000|0000|0000  Move_status_register_to_register
17     cccc|00010|R|1|0|pppp|1111|0000|0000|mmmm  Move_register_to_status_register
18  cccc|000|00 0 0|S|nnnn|dddd|ssss|0|TT|1|mmmm  AND Register_Shift
19  cccc|000|00 0 1|S|nnnn|dddd|ssss|0|TT|1|mmmm  EOR Register_Shift
20  cccc|000|00 1 0|S|nnnn|dddd|ssss|0|TT|1|mmmm  SUB Register_Shift
21  cccc|000|00 1 1|S|nnnn|dddd|ssss|0|TT|1|mmmm  RSB Register_Shift
22  cccc|000|01 0 0|S|nnnn|dddd|ssss|0|TT|1|mmmm  ADD Register_Shift
23  cccc|000|01 0 1|S|nnnn|dddd|ssss|0|TT|1|mmmm  ADC Register_Shift
24  cccc|000|01 1 0|S|nnnn|dddd|ssss|0|TT|1|mmmm  SBC Register_Shift
25  cccc|000|01 1 1|S|nnnn|dddd|ssss|0|TT|1|mmmm  RSC Register_Shift
26  cccc|000|10 0 0|1|nnnn|dddd|ssss|0|TT|1|mmmm  TST Register_Shift
27  cccc|000|10 0 1|1|nnnn|dddd|ssss|0|TT|1|mmmm  TEQ Register_Shift
28  cccc|000|10 1 0|1|nnnn|dddd|ssss|0|TT|1|mmmm  CMP Register_Shift
29  cccc|000|10 1 1|1|nnnn|dddd|ssss|0|TT|1|mmmm  CMN Register_Shift
30  cccc|000|11 0 0|S|nnnn|dddd|ssss|0|TT|1|mmmm  ORR Register_Shift
31  cccc|000|11 0 1|S|nnnn|dddd|ssss|0|TT|1|mmmm  MOV Register_Shift
32  cccc|000|11 1 0|S|nnnn|dddd|ssss|0|TT|1|mmmm  BIC Register_Shift
33  cccc|000|11 1 1|S|nnnn|dddd|ssss|0|TT|1|mmmm  MVN Register_Shift
34     cccc|00010|0 1|0|1111|1111|1111|0001|mmmm  Branch_and_Exchange
35   cccc|0000|0 0|A |S|dddd|nnnn|ssss|1001|mmmm  Multiply_(accumulate)
36   cccc|0000|1 U|A |S|hhhh|llll|ssss|1001|mmmm  Multiply_(accumulate)_long
37   cccc|0001 0|B|0  0|nnnn|dddd|0000|1001|mmmm  Swap/swap_byte
38   cccc|000|P|U|0|W|L|nnnn|dddd|0000|1011|mmmm  Load/store_halfword_register_offset
39   cccc|000|P|U|1|W|L|nnnn|dddd|hhhh|1011|llll  Load/store_halfword_immediate_offset
40   cccc|000|P|U|0|W|1|nnnn|dddd|0000|11H1|mmmm  Load_signed_halfword/byte_register_offset
41   cccc|000|P|U|1|W|1|nnnn|dddd|hhhh|11H1|llll  Load_signed_halfword/byte_immediate_offset
42  cccc|001|00 0 0|S|nnnn|dddd|RRRR|   IIIIIIII  AND Immediate
43  cccc|001|00 0 1|S|nnnn|dddd|RRRR|   IIIIIIII  EOR Immediate
44  cccc|001|00 1 0|S|nnnn|dddd|RRRR|   IIIIIIII  SUB Immediate
45  cccc|001|00 1 1|S|nnnn|dddd|RRRR|   IIIIIIII  RSB Immediate
46  cccc|001|01 0 0|S|nnnn|dddd|RRRR|   IIIIIIII  ADD Immediate
47  cccc|001|01 0 1|S|nnnn|dddd|RRRR|   IIIIIIII  ADC Immediate
48  cccc|001|01 1 0|S|nnnn|dddd|RRRR|   IIIIIIII  SBC Immediate
49  cccc|001|01 1 1|S|nnnn|dddd|RRRR|   IIIIIIII  RSC Immediate
50  cccc|001|10 0 0|1|nnnn|dddd|RRRR|   IIIIIIII  TST Immediate
51  cccc|001|10 0 1|1|nnnn|dddd|RRRR|   IIIIIIII  TEQ Immediate
52  cccc|001|10 1 0|1|nnnn|dddd|RRRR|   IIIIIIII  CMP Immediate
53  cccc|001|10 1 1|1|nnnn|dddd|RRRR|   IIIIIIII  CMN Immediate
54  cccc|001|11 0 0|S|nnnn|dddd|RRRR|   IIIIIIII  ORR Immediate
55  cccc|001|11 0 1|S|nnnn|dddd|RRRR|   IIIIIIII  MOV Immediate
56  cccc|001|11 1 0|S|nnnn|dddd|RRRR|   IIIIIIII  BIC Immediate
57  cccc|001|11 1 1|S|nnnn|dddd|RRRR|   IIIIIIII  MVN Immediate
58  cccc|001|10|R|1 0|MMMM|OOOO|RRRR|   IIIIIIII  Move_immediate_to_status_register[1]
59  cccc|010|PU B W L|nnnn|dddd|    IIIIIIIIIIII  Load/store_immediate_offset[1]
60  cccc|011|PU B W L|nnnn|dddd|sssss |TT|0|mmmm  Load/store_register_offset[1]
61  cccc|100|PU S W L|nnnn|     llllllllllllllll  Load/store_multiple[1]
62  cccc|101|L|    oooo oooo oooo oooo oooo oooo  Branch_and_branch_with_link[1]
63  cccc|110|PU N W L|nnnn|dddd|####|  oooo oooo  Coprocessor_load/store_and_double_register_transfers[5][6]
64  cccc|111 0|  oooo|nnnn|dddd|####|ppp|0| mmmm  Coprocessor_data_processing[5]
65  cccc|111 0| ooo|L|nnnn|dddd|####|ppp|1| mmmm  Coprocessor_register_transfers[5]
66  cccc|1111|     iiii iiii iiii iiii iiii iiii  Software_Interrupt[1]
67              cccc011********************1****  Undefined_instruction
68              cccc00110*00********************  Undefined_instruction
69              cccc00010010************0*11****  Undefined_instruction
70              cccc000**1*0************11*1****  Undefined_instruction
71              cccc000**0*0********000011*1****  Undefined_instruction
72              cccc00010110************0001****  Undefined_instruction
>>> 
```


## Distinguishing UNDEFINED and UNPREDICTABLE

According to the manual, which instructions are UNDEFINED or UNPREDICTABLE is determined by the rules for ARMv4:

1. The decode bits of an instruction are defined to be bits[27:20] and bits[7:4].
2. If the decode bits of an instruction are equal to those of a defined instruction, but the whole instruction
is not a defined instruction, then the instruction is UNPREDICTABLE.
3. If the decode bits of an instruction are not equal to those of any defined instruction, then the instruction is UNDEFINED.

Let us therefore check the decode bits of the patterns defined to assert that the undefined instuctructions do not overlap any of the other 
```
>>> b = a.copy_current()
>>> b.rmbits([31, 30, 29, 28, 0, 1, 2, 3] + list(range(8, 20)))
>>> b.lsambig()
Number of ambiguities: 0

>>> 
```

With this settled, we can focus on the defined instructions.
```
>>> a.delcodes(list(range(67,73)))
>>> a.delsep(list(range(0,33)))
>>> a.newsep([28, 20, 8, 4])
>>> a.ls()
 0  cccc|0000000S|nnnnddddssss|sTT0|mmmm  AND Immediate_Shift
 1  cccc|0000001S|nnnnddddssss|sTT0|mmmm  EOR Immediate_Shift
 2  cccc|0000010S|nnnnddddssss|sTT0|mmmm  SUB Immediate_Shift
 3  cccc|0000011S|nnnnddddssss|sTT0|mmmm  RSB Immediate_Shift
 4  cccc|0000100S|nnnnddddssss|sTT0|mmmm  ADD Immediate_Shift
 5  cccc|0000101S|nnnnddddssss|sTT0|mmmm  ADC Immediate_Shift
 6  cccc|0000110S|nnnnddddssss|sTT0|mmmm  SBC Immediate_Shift
 7  cccc|0000111S|nnnnddddssss|sTT0|mmmm  RSC Immediate_Shift
 8  cccc|00010001|nnnnddddssss|sTT0|mmmm  TST Immediate_Shift
 9  cccc|00010011|nnnnddddssss|sTT0|mmmm  TEQ Immediate_Shift
10  cccc|00010101|nnnnddddssss|sTT0|mmmm  CMP Immediate_Shift
11  cccc|00010111|nnnnddddssss|sTT0|mmmm  CMN Immediate_Shift
12  cccc|0001100S|nnnnddddssss|sTT0|mmmm  ORR Immediate_Shift
13  cccc|0001101S|nnnnddddssss|sTT0|mmmm  MOV Immediate_Shift
14  cccc|0001110S|nnnnddddssss|sTT0|mmmm  BIC Immediate_Shift
15  cccc|0001111S|nnnnddddssss|sTT0|mmmm  MVN Immediate_Shift
16  cccc|00010R00|1111dddd0000|0000|0000  Move_status_register_to_register
17  cccc|00010R10|pppp11110000|0000|mmmm  Move_register_to_status_register
18  cccc|0000000S|nnnnddddssss|0TT1|mmmm  AND Register_Shift
19  cccc|0000001S|nnnnddddssss|0TT1|mmmm  EOR Register_Shift
20  cccc|0000010S|nnnnddddssss|0TT1|mmmm  SUB Register_Shift
21  cccc|0000011S|nnnnddddssss|0TT1|mmmm  RSB Register_Shift
22  cccc|0000100S|nnnnddddssss|0TT1|mmmm  ADD Register_Shift
23  cccc|0000101S|nnnnddddssss|0TT1|mmmm  ADC Register_Shift
24  cccc|0000110S|nnnnddddssss|0TT1|mmmm  SBC Register_Shift
25  cccc|0000111S|nnnnddddssss|0TT1|mmmm  RSC Register_Shift
26  cccc|00010001|nnnnddddssss|0TT1|mmmm  TST Register_Shift
27  cccc|00010011|nnnnddddssss|0TT1|mmmm  TEQ Register_Shift
28  cccc|00010101|nnnnddddssss|0TT1|mmmm  CMP Register_Shift
29  cccc|00010111|nnnnddddssss|0TT1|mmmm  CMN Register_Shift
30  cccc|0001100S|nnnnddddssss|0TT1|mmmm  ORR Register_Shift
31  cccc|0001101S|nnnnddddssss|0TT1|mmmm  MOV Register_Shift
32  cccc|0001110S|nnnnddddssss|0TT1|mmmm  BIC Register_Shift
33  cccc|0001111S|nnnnddddssss|0TT1|mmmm  MVN Register_Shift
34  cccc|00010010|111111111111|0001|mmmm  Branch_and_Exchange
35  cccc|000000AS|ddddnnnnssss|1001|mmmm  Multiply_(accumulate)
36  cccc|00001UAS|hhhhllllssss|1001|mmmm  Multiply_(accumulate)_long
37  cccc|00010B00|nnnndddd0000|1001|mmmm  Swap/swap_byte
38  cccc|000PU0WL|nnnndddd0000|1011|mmmm  Load/store_halfword_register_offset
39  cccc|000PU1WL|nnnnddddhhhh|1011|llll  Load/store_halfword_immediate_offset
40  cccc|000PU0W1|nnnndddd0000|11H1|mmmm  Load_signed_halfword/byte_register_offset
41  cccc|000PU1W1|nnnnddddhhhh|11H1|llll  Load_signed_halfword/byte_immediate_offset
42  cccc|0010000S|nnnnddddRRRR|IIII|IIII  AND Immediate
43  cccc|0010001S|nnnnddddRRRR|IIII|IIII  EOR Immediate
44  cccc|0010010S|nnnnddddRRRR|IIII|IIII  SUB Immediate
45  cccc|0010011S|nnnnddddRRRR|IIII|IIII  RSB Immediate
46  cccc|0010100S|nnnnddddRRRR|IIII|IIII  ADD Immediate
47  cccc|0010101S|nnnnddddRRRR|IIII|IIII  ADC Immediate
48  cccc|0010110S|nnnnddddRRRR|IIII|IIII  SBC Immediate
49  cccc|0010111S|nnnnddddRRRR|IIII|IIII  RSC Immediate
50  cccc|00110001|nnnnddddRRRR|IIII|IIII  TST Immediate
51  cccc|00110011|nnnnddddRRRR|IIII|IIII  TEQ Immediate
52  cccc|00110101|nnnnddddRRRR|IIII|IIII  CMP Immediate
53  cccc|00110111|nnnnddddRRRR|IIII|IIII  CMN Immediate
54  cccc|0011100S|nnnnddddRRRR|IIII|IIII  ORR Immediate
55  cccc|0011101S|nnnnddddRRRR|IIII|IIII  MOV Immediate
56  cccc|0011110S|nnnnddddRRRR|IIII|IIII  BIC Immediate
57  cccc|0011111S|nnnnddddRRRR|IIII|IIII  MVN Immediate
58  cccc|00110R10|MMMMOOOORRRR|IIII|IIII  Move_immediate_to_status_register[1]
59  cccc|010PUBWL|nnnnddddIIII|IIII|IIII  Load/store_immediate_offset[1]
60  cccc|011PUBWL|nnnnddddssss|sTT0|mmmm  Load/store_register_offset[1]
61  cccc|100PUSWL|nnnnllllllll|llll|llll  Load/store_multiple[1]
62  cccc|101Loooo|oooooooooooo|oooo|oooo  Branch_and_branch_with_link[1]
63  cccc|110PUNWL|nnnndddd####|oooo|oooo  Coprocessor_load/store_and_double_register_transfers[5][6]
64  cccc|1110oooo|nnnndddd####|ppp0|mmmm  Coprocessor_data_processing[5]
65  cccc|1110oooL|nnnndddd####|ppp1|mmmm  Coprocessor_register_transfers[5]
66  cccc|1111iiii|iiiiiiiiiiii|iiii|iiii  Software_Interrupt[1]
>>> 
```

## Determining remaining mnemonics
Let us now determine mnemonics for all instructions as well as addressing modes where applicable.

### Software interrupt
This one has one one mnemonic, SWI, and takes an immediate operand.
```
>>> a.newcode('cccc|1111iiii|iiiiiiiiiiii|iiii|iiii', 'SWI', 66)
>>> a.delcodes([67])
>>>
```

### Coprocessor instructions
The coprocessor instructions are
* CDP (Coprocessor Data Operations) given by  pattern 64, CDP{<cond>}
* LDC (Load Coprocessor Register) given by pattern 63 with L=1, LDC{<cond>}{L}
* MCR (Move to Coprocessor from ARM Register) given by pattern 65 with L=0, MCR{<cond>}
* MRC (Move to ARM Register from Coprocessor) given by pattern 65 with L=1, MRC{<cond>}
* STC (Store Coprocessor Register) given by pattern 63 with L=0, STC{<cond>}{L}

For LDC and STC the L-suffix denotes a long load/store and corresponds to N=1.
Instructions with N=0 correspond to short load/store.

```
>>> tmp = Analyzer([
... ('cccc|110PU0W1|nnnndddd####|oooo|oooo', 'LDCcc'),
... ('cccc|110PU0W0|nnnndddd####|oooo|oooo', 'STCcc'),
... ('cccc|110PU1W1|nnnndddd####|oooo|oooo', 'LDCccL'),
... ('cccc|110PU1W0|nnnndddd####|oooo|oooo', 'STCccL'),
... ('cccc|1110oooo|nnnndddd####|ppp0|mmmm', 'CDPcc'),
... ('cccc|1110ooo0|nnnndddd####|ppp1|mmmm', 'MCRcc' ),
... ('cccc|1110ooo1|nnnndddd####|ppp1|mmmm', 'MRCcc' )
... ])  
>>> a.delcodes([63, 64, 65])
>>> a.merge(tmp, 63)
```

### Branch instructions 
The branch instructions are
* B (Branch) given by pattern 62 with L=0, B{<cond>}
* BL (Branch with Link ) given by pattern 62 with L=1, BL{<cond>}
* BX (Branch and Exchange Instruction Set) given by pattern 34, BX{<cond>}
```
>>> a.delcodes([62])
>>> a.newcode('cccc|1010oooo|oooooooooooo|oooo|oooo', 'Bcc', 62)
>>> a.newcode('cccc|1011oooo|oooooooooooo|oooo|oooo', 'BLcc', 62)
>>> a.delcodes([34])
>>> a.newcode('cccc|00010010|111111111111|0001|mmmm', 'BXcc', 34)
>>>
```

### Load and Store Multiple instructions
Load and store multiple instructions are given by varieties of pattern 61 depending on the value
of the P-, U-, S-, W- and L-bits. L=0  denotes stores (STM) and L=1 loads (LDM).

There are four adressing modes governed by the P- and U-bits:
Addressing mode | P | U
:---|---|---
DA (Decrement After)  | 0 | 0
IA (Increment After)  | 0 | 1
DB (Decrement Before) | 1 | 0
IB (Increment Before) | 1 | 1

Not all combinations of S- and W-bits are shown on the manual, but it is different to see that they should not be defined.

In summary, we do as follows:
```
>>> tmp = Analyzer([
...     ('cccc|10000SW0|nnnnllllllll|llll|llll', 'STMccDA'),
...     ('cccc|10001SW0|nnnnllllllll|llll|llll', 'STMccIA'),
...     ('cccc|10010SW0|nnnnllllllll|llll|llll', 'STMccDB'),
...     ('cccc|10011SW0|nnnnllllllll|llll|llll', 'STMccIB'),
...     ('cccc|10000SW1|nnnnllllllll|llll|llll', 'LDMccDA'),
...     ('cccc|10001SW1|nnnnllllllll|llll|llll', 'LDMccIA'),
...     ('cccc|10010SW1|nnnnllllllll|llll|llll', 'LDMccDB'),
...     ('cccc|10011SW1|nnnnllllllll|llll|llll', 'LDMccIB')
... ])
>>> a.delcodes([61])
>>> a.merge(tmp, 61)
>>>
```

### Load and store word or unsigned bytes
The instructions are 
* LDR  (Load Word) given by patterns 59 or 60 dependent on addressing mode and with B=0, L=1.
* LDRB (Load Byte) given by patterns 59 or 60 dependent on addressing mode and with B=1, L=1.
* STR  (Store Word) given by patterns 59 or 60 dependent on addressing mode and with B=0, L=0.
* STRB (Store Byte) given by patterns 59 or 60 dependent on addressing mode and with B=1, L=0.

In addition we have varieties of the same instructions which give unprivileged memory access in
a privileged mode (for post-indexed addressing only). These are
* LDRT (Load Word with User Mode Privilege).
* LDRBT (Load Byte with User Mode Privilege).
* STRT (Store Word with User Mode Privilege).
* STRBT (Store Byte with User Mode Privilege).

Which is used depends on the P- and W-bits:
P | W | Addressing mode | Instructions
---|---|---|---
0 | 0 | Post-Indexed | LDR, LDRB, STR, STRB
0 | 1 | Post-Indexed | LDRT, LDRBT, STRT, STRBT
1 | 0 | Offset | LDR, LDRB, STR, STRB
1 | 1 | Pre-Indexed | LDR, LDRB, STR, STRB

For the LDR, LDRB, STR and STRB instructions we then have these three alternatives for each of the choices of immediate offset, register (only) offset and scaled register offset giving a  total of nine adressing modes as listed in the manual. However the register offset and scaled register offset are distinguished by bits 4-11 being zero for register offset and nonzero for scaled register offset. Hence, we treat the together as in pattern 60 so that we only get six different cases.

```
>>> tmp = Analyzer([    
...     ('cccc|0110U001|nnnnddddssss|sTT0|mmmm', 'LDRcc Register_Offset Post-Indexed'),
...     ('cccc|0110U011|nnnnddddssss|sTT0|mmmm', 'LDRccT Register_Offset Post-Indexed'),
...     ('cccc|0111U001|nnnnddddssss|sTT0|mmmm', 'LDRcc Register_Offset'),
...     ('cccc|0111U011|nnnnddddssss|sTT0|mmmm', 'LDRcc Register_Offset Pre-Indexed'),
...     ('cccc|0110U101|nnnnddddssss|sTT0|mmmm', 'LDRccB Register_Offset Post-Indexed'),
...     ('cccc|0110U111|nnnnddddssss|sTT0|mmmm', 'LDRccBT Register_Offset Post-Indexed'),
...     ('cccc|0111U101|nnnnddddssss|sTT0|mmmm', 'LDRccB Register_Offset'),
...     ('cccc|0111U111|nnnnddddssss|sTT0|mmmm', 'LDRccB Register_Offset Pre-Indexed'),
...     ('cccc|0110U000|nnnnddddssss|sTT0|mmmm', 'STRcc Register_Offset Post-Indexed'),
...     ('cccc|0110U010|nnnnddddssss|sTT0|mmmm', 'STRccT Register_Offset Post-Indexed'),
...     ('cccc|0111U000|nnnnddddssss|sTT0|mmmm', 'STRcc Register_Offset'),
...     ('cccc|0111U010|nnnnddddssss|sTT0|mmmm', 'STRcc Register_Offset Pre-Indexed'),
...     ('cccc|0110U100|nnnnddddssss|sTT0|mmmm', 'STRccB Register_Offset Post-Indexed'),
...     ('cccc|0110U110|nnnnddddssss|sTT0|mmmm', 'STRccBT Register_Offset Post-Indexed'),
...     ('cccc|0111U100|nnnnddddssss|sTT0|mmmm', 'STRccB Register_Offset'),
...     ('cccc|0111U110|nnnnddddssss|sTT0|mmmm', 'STRccB Register_Offset Pre-Indexed')
... ])
>>> a.delcodes([60])
>>> a.merge(tmp,60)
>>> tmp = Analyzer([
...     ('cccc|0100U001|nnnnddddIIII|IIII|IIII', 'LDRcc Immediate_Offset Post-Indexed'),
...     ('cccc|0100U011|nnnnddddIIII|IIII|IIII', 'LDRccT Immediate_Offset Post-Indexed'),
...     ('cccc|0101U001|nnnnddddIIII|IIII|IIII', 'LDRcc Immediate_Offset'),
...     ('cccc|0101U011|nnnnddddIIII|IIII|IIII', 'LDRcc Immediate_Offset Pre-Indexed'),
...     ('cccc|0100U101|nnnnddddIIII|IIII|IIII', 'LDRccB Immediate_Offset Post-Indexed'),
...     ('cccc|0100U111|nnnnddddIIII|IIII|IIII', 'LDRccBT Immediate_Offset Post-Indexed'),
...     ('cccc|0101U101|nnnnddddIIII|IIII|IIII', 'LDRccB Immediate_Offset'),
...     ('cccc|0101U111|nnnnddddIIII|IIII|IIII', 'LDRccB Immediate_Offset Pre-Indexed'),
...     ('cccc|0100U000|nnnnddddIIII|IIII|IIII', 'STRcc Immediate_Offset Post-Indexed'),
...     ('cccc|0100U010|nnnnddddIIII|IIII|IIII', 'STRccT Immediate_Offset Post-Indexed'),
...     ('cccc|0101U000|nnnnddddIIII|IIII|IIII', 'STRcc Immediate_Offset'),
...     ('cccc|0101U010|nnnnddddIIII|IIII|IIII', 'STRcc Immediate_Offset Pre-Indexed'),
...     ('cccc|0100U100|nnnnddddIIII|IIII|IIII', 'STRccB Immediate_Offset Post-Indexed'),
...     ('cccc|0100U110|nnnnddddIIII|IIII|IIII', 'STRccBT Immediate_Offset Post-Indexed'),
...     ('cccc|0101U100|nnnnddddIIII|IIII|IIII', 'STRccB Immediate_Offset'),
...     ('cccc|0101U110|nnnnddddIIII|IIII|IIII', 'STRccB Immediate_Offset Pre-Indexed'),
... ])
>>> a.delcodes([59])
>>> a.merge(tmp,59)
>>> 
```

### Move immediate to status register
Opcode pattern no. 58 determines the setting of either of the status register by an immediate value.
```
>>> a.delcodes([58])
>>> a.newcode('cccc|00110110|MMMMOOOORRRR|IIII|IIII', 'MSRcc SPSR Immediate_Value', 58)
>>> a.newcode('cccc|00110010|MMMMOOOORRRR|IIII|IIII', 'MSRcc CPSR Immediate_Value', 58)
>>> 
```

### Load and Store Halfword and Load Signed Byte
Remaining load store instructions are
* LDRH (Load Unsigned Halfword).
* LDRSB (Load Signed Byte).
* LDRSH (Load Signed Halfword).
* STRH (Store Halfword).

These are defined by patterns 38-41 with further details in sections 3.8.3 and 5.3. Perhaps suprisingly,
the description in 3.8.3 defines the pattern cccc\|000PUIW0\|nnnnddddhhhh\|11H1\|mmmm as UNPREDICTABLE.
The P- and W-bits determine post-/preindexing as follows:
P | W | Addressing mode
---|---|---
0 | 0 | Post-Indexed 
0 | 1 | UNPREDICTABLE 
1 | 0 | Offset 
1 | 1 | Pre-Indexed 

Applying the rules to patterns 38-41, also the patterns cccc\|0000UB1L\|\*\*\*\*\*\*\*\*\*\*\*\*\|1011\|\*\*\*\* and cccc\|0000UB11\|\*\*\*\*\*\*\*\*\*\*\*\*\|11H1\|\*\*\*\*
gives UNPREDICTABLE results. The remaining patterns are included in the instructions set:
```
>>> tmp = Analyzer([
...     ('cccc|0000U000|nnnndddd0000|1011|mmmm',  'STRccH Register_Offset Post-Indexed'),
...     ('cccc|0001U000|nnnndddd0000|1011|mmmm',  'STRccH Register_Offset'),
...     ('cccc|0001U010|nnnndddd0000|1011|mmmm',  'STRccH Register_Offset Pre-Indexed'),
...     ('cccc|0000U001|nnnndddd0000|1011|mmmm',  'LDRccH Register_Offset Post-Indexed'),
...     ('cccc|0001U001|nnnndddd0000|1011|mmmm',  'LDRccH Register_Offset'),
...     ('cccc|0001U011|nnnndddd0000|1011|mmmm',  'LDRccH Register_Offset Pre-Indexed'),
...     ('cccc|0000U001|nnnndddd0000|1101|mmmm',  'LDRccSB Register_Offset Post-Indexed'),
...     ('cccc|0001U001|nnnndddd0000|1101|mmmm',  'LDRccSB Register_Offset'),
...     ('cccc|0001U011|nnnndddd0000|1101|mmmm',  'LDRccSB Register_Offset Pre-Indexed'),
...     ('cccc|0000U001|nnnndddd0000|1111|mmmm',  'LDRccSH Register_Offset Post-Indexed'),
...     ('cccc|0001U001|nnnndddd0000|1111|mmmm',  'LDRccSH Register_Offset'),
...     ('cccc|0001U011|nnnndddd0000|1111|mmmm',  'LDRccSH Register_Offset Pre-Indexed'),
...     ('cccc|0000U100|nnnnddddhhhh|1011|llll',  'STRccH Immediate_Offset Post-Indexed'),
...     ('cccc|0001U100|nnnnddddhhhh|1011|llll',  'STRccH Immediate_Offset'),
...     ('cccc|0001U110|nnnnddddhhhh|1011|llll',  'STRccH Immediate_Offset Pre-Indexed'),
...     ('cccc|0000U101|nnnnddddhhhh|1011|llll',  'LDRccH Immediate_Offset Post-Indexed'),
...     ('cccc|0001U101|nnnnddddhhhh|1011|llll',  'LDRccH Immediate_Offset'),
...     ('cccc|0001U111|nnnnddddhhhh|1011|llll',  'LDRccH Immediate_Offset Pre-Indexed'),
...     ('cccc|0000U101|nnnnddddhhhh|1101|llll',  'LDRccSB Immediate_Offset Post-Indexed'),
...     ('cccc|0001U101|nnnnddddhhhh|1101|llll',  'LDRccSB Immediate_Offset'),
...     ('cccc|0001U111|nnnnddddhhhh|1101|llll',  'LDRccSB Immediate_Offset Pre-Indexed'),
...     ('cccc|0000U101|nnnnddddhhhh|1111|llll',  'LDRccSH Immediate_Offset Post-Indexed'),
...     ('cccc|0001U101|nnnnddddhhhh|1111|llll',  'LDRccSH Immediate_Offset'),
...     ('cccc|0001U111|nnnnddddhhhh|1111|llll',  'LDRccSH Immediate_Offset Pre-Indexed')
... ])
>>> a.delcodes([38, 39, 40, 41])
>>> a.merge(tmp, 38)
>>> 
```

### Semaphore instructions
The semaphore instructions SWP and SWPB are given by Swap/Swapbyte in pattern 37:
```
>>> a.delcodes([37])
>>> a.newcode('cccc|00010100|nnnndddd0000|1001|mmmm',  'SWPccB', 37)
>>> a.newcode('cccc|00010000|nnnndddd0000|1001|mmmm',  'SWPcc', 37)
>>> 
```

###  Multiply instructions
Mutliply instructions are given by patterns 35 and 36
and are 
* MLA Multiply Accumulate. MLAcc{S} from pattern 35 with A=1
* MUL Multiply. MULcc{S} from pattern 35 with  A=0 and Rn=0
* SMLAL Signed Multiply Accumulate Long. SMLALcc{S} from 36 with U=1, A=1
* SMULL Signed Multiply Long. SMULLcc{S} from 36 with U=1, A=0.
* UMLAL Unsigned Multiply Accumulate Long. UMLALcc{S} from 36 with U=0, A=1.
* UMULL Unsigned Multiply Long. UMULLcc{S} from 36 with U=0, A=0.

```
>>> tmp = Analyzer([
...     ('cccc|0000000S|dddd0000ssss|1001|mmmm', 'MULcc'),
...     ('cccc|0000001S|ddddnnnnssss|1001|mmmm', 'MLAcc'),
...     ('cccc|0000100S|hhhhllllssss|1001|mmmm', 'UMULLcc'),
...     ('cccc|0000101S|hhhhllllssss|1001|mmmm', 'UMLALcc'),
...     ('cccc|0000110S|hhhhllllssss|1001|mmmm', 'SMULLcc'),
...     ('cccc|0000111S|hhhhllllssss|1001|mmmm', 'SMLALcc')    
... ])
>>> def stag(d, f, p):
...     if p == '1':
...         return d + 'S'
...     else:
...         return d
... 
>>> tmp.expand_field('S', tag=stag)
>>> a.delcodes([35, 36])
>>> a.merge(tmp, 35)
>>>
```

### Status register access instructions
There are two instruction menmonics MRS and MSR representing status register access instructions. 
These instructions are covered by patterns 16, 17 and 58. The latter defines MSR with an immediate 
argument and has already been dealt with. The remaining are: 
  * MRS (Move PSR to General-purpose register) represented by pattern 16.
  * MSR (Move General-purpose Register to PSR)  represented by pattern 17.

```
>>> tmp = Analyzer([
...     ('cccc|00010000|1111dddd0000|0000|0000', 'MRScc CPSR'),
...     ('cccc|00010100|1111dddd0000|0000|0000', 'MRScc SPSR'),
...     ('cccc|00010010|pppp11110000|0000|mmmm', 'MSRcc CPSR'),
...     ('cccc|00010110|pppp11110000|0000|mmmm', 'MSRcc SPSR')
... ])
>>> a.delcodes([16, 17])
>>> a.merge(tmp, 16)
>>> 
```

## Conclusion
The opcode patterns are now 
```
>>> a.ls()
  0  cccc|0000000S|nnnnddddssss|sTT0|mmmm  AND Immediate_Shift
  1  cccc|0000001S|nnnnddddssss|sTT0|mmmm  EOR Immediate_Shift
  2  cccc|0000010S|nnnnddddssss|sTT0|mmmm  SUB Immediate_Shift
  3  cccc|0000011S|nnnnddddssss|sTT0|mmmm  RSB Immediate_Shift
  4  cccc|0000100S|nnnnddddssss|sTT0|mmmm  ADD Immediate_Shift
  5  cccc|0000101S|nnnnddddssss|sTT0|mmmm  ADC Immediate_Shift
  6  cccc|0000110S|nnnnddddssss|sTT0|mmmm  SBC Immediate_Shift
  7  cccc|0000111S|nnnnddddssss|sTT0|mmmm  RSC Immediate_Shift
  8  cccc|00010001|nnnnddddssss|sTT0|mmmm  TST Immediate_Shift
  9  cccc|00010011|nnnnddddssss|sTT0|mmmm  TEQ Immediate_Shift
 10  cccc|00010101|nnnnddddssss|sTT0|mmmm  CMP Immediate_Shift
 11  cccc|00010111|nnnnddddssss|sTT0|mmmm  CMN Immediate_Shift
 12  cccc|0001100S|nnnnddddssss|sTT0|mmmm  ORR Immediate_Shift
 13  cccc|0001101S|nnnnddddssss|sTT0|mmmm  MOV Immediate_Shift
 14  cccc|0001110S|nnnnddddssss|sTT0|mmmm  BIC Immediate_Shift
 15  cccc|0001111S|nnnnddddssss|sTT0|mmmm  MVN Immediate_Shift
 16  cccc|00010000|1111dddd0000|0000|0000  MRScc CPSR
 17  cccc|00010100|1111dddd0000|0000|0000  MRScc SPSR
 18  cccc|00010010|pppp11110000|0000|mmmm  MSRcc CPSR
 19  cccc|00010110|pppp11110000|0000|mmmm  MSRcc SPSR
 20  cccc|0000000S|nnnnddddssss|0TT1|mmmm  AND Register_Shift
 21  cccc|0000001S|nnnnddddssss|0TT1|mmmm  EOR Register_Shift
 22  cccc|0000010S|nnnnddddssss|0TT1|mmmm  SUB Register_Shift
 23  cccc|0000011S|nnnnddddssss|0TT1|mmmm  RSB Register_Shift
 24  cccc|0000100S|nnnnddddssss|0TT1|mmmm  ADD Register_Shift
 25  cccc|0000101S|nnnnddddssss|0TT1|mmmm  ADC Register_Shift
 26  cccc|0000110S|nnnnddddssss|0TT1|mmmm  SBC Register_Shift
 27  cccc|0000111S|nnnnddddssss|0TT1|mmmm  RSC Register_Shift
 28  cccc|00010001|nnnnddddssss|0TT1|mmmm  TST Register_Shift
 29  cccc|00010011|nnnnddddssss|0TT1|mmmm  TEQ Register_Shift
 30  cccc|00010101|nnnnddddssss|0TT1|mmmm  CMP Register_Shift
 31  cccc|00010111|nnnnddddssss|0TT1|mmmm  CMN Register_Shift
 32  cccc|0001100S|nnnnddddssss|0TT1|mmmm  ORR Register_Shift
 33  cccc|0001101S|nnnnddddssss|0TT1|mmmm  MOV Register_Shift
 34  cccc|0001110S|nnnnddddssss|0TT1|mmmm  BIC Register_Shift
 35  cccc|0001111S|nnnnddddssss|0TT1|mmmm  MVN Register_Shift
 36  cccc|00010010|111111111111|0001|mmmm  BXcc
 37  cccc|00000000|dddd0000ssss|1001|mmmm  MULcc
 38  cccc|00000001|dddd0000ssss|1001|mmmm  MULccS
 39  cccc|00000010|ddddnnnnssss|1001|mmmm  MLAcc
 40  cccc|00000011|ddddnnnnssss|1001|mmmm  MLAccS
 41  cccc|00001000|hhhhllllssss|1001|mmmm  UMULLcc
 42  cccc|00001001|hhhhllllssss|1001|mmmm  UMULLccS
 43  cccc|00001010|hhhhllllssss|1001|mmmm  UMLALcc
 44  cccc|00001011|hhhhllllssss|1001|mmmm  UMLALccS
 45  cccc|00001100|hhhhllllssss|1001|mmmm  SMULLcc
 46  cccc|00001101|hhhhllllssss|1001|mmmm  SMULLccS
 47  cccc|00001110|hhhhllllssss|1001|mmmm  SMLALcc
 48  cccc|00001111|hhhhllllssss|1001|mmmm  SMLALccS
 49  cccc|00010000|nnnndddd0000|1001|mmmm  SWPcc
 50  cccc|00010100|nnnndddd0000|1001|mmmm  SWPccB
 51  cccc|0000U000|nnnndddd0000|1011|mmmm  STRccH Register_Offset Post-Indexed
 52  cccc|0001U000|nnnndddd0000|1011|mmmm  STRccH Register_Offset
 53  cccc|0001U010|nnnndddd0000|1011|mmmm  STRccH Register_Offset Pre-Indexed
 54  cccc|0000U001|nnnndddd0000|1011|mmmm  LDRccH Register_Offset Post-Indexed
 55  cccc|0001U001|nnnndddd0000|1011|mmmm  LDRccH Register_Offset
 56  cccc|0001U011|nnnndddd0000|1011|mmmm  LDRccH Register_Offset Pre-Indexed
 57  cccc|0000U001|nnnndddd0000|1101|mmmm  LDRccSB Register_Offset Post-Indexed
 58  cccc|0001U001|nnnndddd0000|1101|mmmm  LDRccSB Register_Offset
 59  cccc|0001U011|nnnndddd0000|1101|mmmm  LDRccSB Register_Offset Pre-Indexed
 60  cccc|0000U001|nnnndddd0000|1111|mmmm  LDRccSH Register_Offset Post-Indexed
 61  cccc|0001U001|nnnndddd0000|1111|mmmm  LDRccSH Register_Offset
 62  cccc|0001U011|nnnndddd0000|1111|mmmm  LDRccSH Register_Offset Pre-Indexed
 63  cccc|0000U100|nnnnddddhhhh|1011|llll  STRccH Immediate_Offset Post-Indexed
 64  cccc|0001U100|nnnnddddhhhh|1011|llll  STRccH Immediate_Offset
 65  cccc|0001U110|nnnnddddhhhh|1011|llll  STRccH Immediate_Offset Pre-Indexed
 66  cccc|0000U101|nnnnddddhhhh|1011|llll  LDRccH Immediate_Offset Post-Indexed
 67  cccc|0001U101|nnnnddddhhhh|1011|llll  LDRccH Immediate_Offset
 68  cccc|0001U111|nnnnddddhhhh|1011|llll  LDRccH Immediate_Offset Pre-Indexed
 69  cccc|0000U101|nnnnddddhhhh|1101|llll  LDRccSB Immediate_Offset Post-Indexed
 70  cccc|0001U101|nnnnddddhhhh|1101|llll  LDRccSB Immediate_Offset
 71  cccc|0001U111|nnnnddddhhhh|1101|llll  LDRccSB Immediate_Offset Pre-Indexed
 72  cccc|0000U101|nnnnddddhhhh|1111|llll  LDRccSH Immediate_Offset Post-Indexed
 73  cccc|0001U101|nnnnddddhhhh|1111|llll  LDRccSH Immediate_Offset
 74  cccc|0001U111|nnnnddddhhhh|1111|llll  LDRccSH Immediate_Offset Pre-Indexed
 75  cccc|0010000S|nnnnddddRRRR|IIII|IIII  AND Immediate
 76  cccc|0010001S|nnnnddddRRRR|IIII|IIII  EOR Immediate
 77  cccc|0010010S|nnnnddddRRRR|IIII|IIII  SUB Immediate
 78  cccc|0010011S|nnnnddddRRRR|IIII|IIII  RSB Immediate
 79  cccc|0010100S|nnnnddddRRRR|IIII|IIII  ADD Immediate
 80  cccc|0010101S|nnnnddddRRRR|IIII|IIII  ADC Immediate
 81  cccc|0010110S|nnnnddddRRRR|IIII|IIII  SBC Immediate
 82  cccc|0010111S|nnnnddddRRRR|IIII|IIII  RSC Immediate
 83  cccc|00110001|nnnnddddRRRR|IIII|IIII  TST Immediate
 84  cccc|00110011|nnnnddddRRRR|IIII|IIII  TEQ Immediate
 85  cccc|00110101|nnnnddddRRRR|IIII|IIII  CMP Immediate
 86  cccc|00110111|nnnnddddRRRR|IIII|IIII  CMN Immediate
 87  cccc|0011100S|nnnnddddRRRR|IIII|IIII  ORR Immediate
 88  cccc|0011101S|nnnnddddRRRR|IIII|IIII  MOV Immediate
 89  cccc|0011110S|nnnnddddRRRR|IIII|IIII  BIC Immediate
 90  cccc|0011111S|nnnnddddRRRR|IIII|IIII  MVN Immediate
 91  cccc|00110010|MMMMOOOORRRR|IIII|IIII  MSRcc CPSR Immediate_Value
 92  cccc|00110110|MMMMOOOORRRR|IIII|IIII  MSRcc SPSR Immediate_Value
 93  cccc|0100U001|nnnnddddIIII|IIII|IIII  LDRcc Immediate_Offset Post-Indexed
 94  cccc|0100U011|nnnnddddIIII|IIII|IIII  LDRccT Immediate_Offset Post-Indexed
 95  cccc|0101U001|nnnnddddIIII|IIII|IIII  LDRcc Immediate_Offset
 96  cccc|0101U011|nnnnddddIIII|IIII|IIII  LDRcc Immediate_Offset Pre-Indexed
 97  cccc|0100U101|nnnnddddIIII|IIII|IIII  LDRccB Immediate_Offset Post-Indexed
 98  cccc|0100U111|nnnnddddIIII|IIII|IIII  LDRccBT Immediate_Offset Post-Indexed
 99  cccc|0101U101|nnnnddddIIII|IIII|IIII  LDRccB Immediate_Offset
100  cccc|0101U111|nnnnddddIIII|IIII|IIII  LDRccB Immediate_Offset Pre-Indexed
101  cccc|0100U000|nnnnddddIIII|IIII|IIII  STRcc Immediate_Offset Post-Indexed
102  cccc|0100U010|nnnnddddIIII|IIII|IIII  STRccT Immediate_Offset Post-Indexed
103  cccc|0101U000|nnnnddddIIII|IIII|IIII  STRcc Immediate_Offset
104  cccc|0101U010|nnnnddddIIII|IIII|IIII  STRcc Immediate_Offset Pre-Indexed
105  cccc|0100U100|nnnnddddIIII|IIII|IIII  STRccB Immediate_Offset Post-Indexed
106  cccc|0100U110|nnnnddddIIII|IIII|IIII  STRccBT Immediate_Offset Post-Indexed
107  cccc|0101U100|nnnnddddIIII|IIII|IIII  STRccB Immediate_Offset
108  cccc|0101U110|nnnnddddIIII|IIII|IIII  STRccB Immediate_Offset Pre-Indexed
109  cccc|0110U001|nnnnddddssss|sTT0|mmmm  LDRcc Register_Offset Post-Indexed
110  cccc|0110U011|nnnnddddssss|sTT0|mmmm  LDRccT Register_Offset Post-Indexed
111  cccc|0111U001|nnnnddddssss|sTT0|mmmm  LDRcc Register_Offset
112  cccc|0111U011|nnnnddddssss|sTT0|mmmm  LDRcc Register_Offset Pre-Indexed
113  cccc|0110U101|nnnnddddssss|sTT0|mmmm  LDRccB Register_Offset Post-Indexed
114  cccc|0110U111|nnnnddddssss|sTT0|mmmm  LDRccBT Register_Offset Post-Indexed
115  cccc|0111U101|nnnnddddssss|sTT0|mmmm  LDRccB Register_Offset
116  cccc|0111U111|nnnnddddssss|sTT0|mmmm  LDRccB Register_Offset Pre-Indexed
117  cccc|0110U000|nnnnddddssss|sTT0|mmmm  STRcc Register_Offset Post-Indexed
118  cccc|0110U010|nnnnddddssss|sTT0|mmmm  STRccT Register_Offset Post-Indexed
119  cccc|0111U000|nnnnddddssss|sTT0|mmmm  STRcc Register_Offset
120  cccc|0111U010|nnnnddddssss|sTT0|mmmm  STRcc Register_Offset Pre-Indexed
121  cccc|0110U100|nnnnddddssss|sTT0|mmmm  STRccB Register_Offset Post-Indexed
122  cccc|0110U110|nnnnddddssss|sTT0|mmmm  STRccBT Register_Offset Post-Indexed
123  cccc|0111U100|nnnnddddssss|sTT0|mmmm  STRccB Register_Offset
124  cccc|0111U110|nnnnddddssss|sTT0|mmmm  STRccB Register_Offset Pre-Indexed
125  cccc|10000SW0|nnnnllllllll|llll|llll  STMccDA
126  cccc|10001SW0|nnnnllllllll|llll|llll  STMccIA
127  cccc|10010SW0|nnnnllllllll|llll|llll  STMccDB
128  cccc|10011SW0|nnnnllllllll|llll|llll  STMccIB
129  cccc|10000SW1|nnnnllllllll|llll|llll  LDMccDA
130  cccc|10001SW1|nnnnllllllll|llll|llll  LDMccIA
131  cccc|10010SW1|nnnnllllllll|llll|llll  LDMccDB
132  cccc|10011SW1|nnnnllllllll|llll|llll  LDMccIB
133  cccc|1011oooo|oooooooooooo|oooo|oooo  BLcc
134  cccc|1010oooo|oooooooooooo|oooo|oooo  Bcc
135  cccc|110PU0W1|nnnndddd####|oooo|oooo  LDCcc
136  cccc|110PU0W0|nnnndddd####|oooo|oooo  STCcc
137  cccc|110PU1W1|nnnndddd####|oooo|oooo  LDCccL
138  cccc|110PU1W0|nnnndddd####|oooo|oooo  STCccL
139  cccc|1110oooo|nnnndddd####|ppp0|mmmm  CDPcc
140  cccc|1110ooo0|nnnndddd####|ppp1|mmmm  MCRcc
141  cccc|1110ooo1|nnnndddd####|ppp1|mmmm  MRCcc
142  cccc|1111iiii|iiiiiiiiiiii|iiii|iiii  SWIcc
>>>
```
We stop here as we now have identified unique mnemonic and addressing mode combinations for all defined instructions. We could have proceeded with further specifications, for example the S-bit for on the remaining data processing instructions, but that would not add much to the example.

The final result can be saved for later use:
```
>>> a.save('armv4t_analyzer', 'armv4t_analyzer_saved.py')
>>>
```



