# ARMV4T Example
from armv4t_spec import *
print('>>> m31.ls()')
m31.ls()
print('>>> m32.ls()')
m32.ls()
print('>>> m33.ls()')
m33.ls()

# Instructions deemed 'UNPREDICTABLE'
a = m31.copy_current()
a.delcodes([11, 13, 15, 20])
unpred = m31.copy_current([11, 13, 15, 16, 17, 18, 20])
unpred.rmbits([31, 30, 29, 28])
print('>>> unpred.ls()')
unpred.ls()

# Merging all opcode patterns
m0 = m33.copy_current([0, 1])  # skip 7 as it was not defined in v4
m1 = m33.copy_current([2, 3, 4, 6])
m1.get_codes()[3].desc = 'Undefined instruction'  # Undefined in v4
print('>>> m0.ls()')
m0.ls()
print('>>> m1.ls()')
m1.ls()
m0.replace_field('O', '1')  # replace should be ones
m0.replace_field('Z', '0')  # replace should be zeros
m1.replace_field('O', '1', [0])  # replace should be ones
m1.replace_field('d', '*', [1])  # no need for field name in undef
m1.replace_field('O', '*', [1, 2])  # no need for field name in undef
m1.replace_field('m', '*', [1, 2])  # no need for field name in undef
m1.replace_field('I', '*', [3])  # no need for field name in undef
m1.replace_field('i', '*', [3])  # no need for field name in undef
print('>>> m0.ls()')
m0.ls()
print('>>> m1.ls()')
m1.ls()
print('>>> a.ls()')
a.ls()
a.delcodes([3])
a.merge(m1, 3)
a.delcodes([1])
a.merge(m0, 1)
a.move(14, 20)
a.move(10, 20)
a.move(7, 20)
a.move(6, 20)
a.move(5, 20)
a.delsep(list(range(0,33)), [16, 17, 18, 19, 20])
a.newcode('cccc00010010************0*11****', 'Undefined_instruction', 18)
a.delcodes([19, 20])
for ac in a.get_codes()[-4:-2]:
    ac.desc = 'Undefined_instruction'
print('>>> a.ls()')
a.ls()

# Resolving ambiguities
# define data processing operations and function for generating description
dataproc = {
    '0000': ('AND', 'Logical AND', 'Rd := Rn AND shifter_operand'),
    '0001': ('EOR', 'Logical Exclusive OR', 'Rd := Rn EOR shifter_operand'),
    '0010': ('SUB', 'Subtract', 'Rd := Rn - shifter_operand'),
    '0011': ('RSB', 'Reverse Subtract', 'Rd := shifter_operand - Rn'),
    '0100': ('ADD', 'Add', 'Rd := Rn + shifter_operand'),
    '0101': ('ADC', 'Add with Carry', 'Rd := Rn + shifter_operand + Carry Flag'),
    '0110': ('SBC', 'Subtract with Carry', 'Rd := Rn - shifter_operand - NOT(Carry Flag)'),
    '0111': ('RSC', 'Reverse Subtract with Carry', 'Rd := shifter_operand - Rn - NOT(Carry Flag)'),
    '1000': ('TST', 'Test', 'Update flags after Rn AND shifter_operand'),
    '1001': ('TEQ', 'Test Equivalence', 'Update flags after Rn EOR shifter_operand'),
    '1010': ('CMP', 'Compare', 'Update flags after Rn - shifter_operand'),
    '1011': ('CMN', 'Compare Negated', 'Update flags after Rn + shifter_operand'),
    '1100': ('ORR', 'Logical (inclusive) OR', 'Rd := Rn OR shifter_operand'),
    '1101': ('MOV', 'Move', 'Rd := shifter_operand (no first operand)'),
    '1110': ('BIC', 'Bit Clear', 'Rd := Rn AND NOT(shifter_operand)'),
    '1111': ('MVN', 'Move Not', 'Rd := NOT shifter_operand (no first operand)'),
}
# expand and remove ooooo=10** with S=0
def tag_operation(current_description, field_letter, pattern):
    return dataproc[pattern][0] + ' ' + current_description.replace('Data_Processing_', '').replace('[1]', '').replace('[2]', '')
a.expand_field('o', [0, 3, 6], tag=tag_operation)
a.expand_field('S', [8, 9, 10, 11, 26, 27, 28, 29, 44, 45, 46, 47], tag=lambda x, y, z: x)
a.delcodes([8, 10, 12, 14, 30, 32, 34, 36, 52, 54, 56, 58])
a.lsambig()

# Merging in multiplies and extra load/stores
from ocparse import *
mls = m32.copy_current()
codes=mls.get_codes()
codes[5] = AnalyzerOpcode('cccc|000|*|*|0|*|0|****|****|0000|11*1|****', 'Undefined_instruction')  # undefined in v4
codes[7] = AnalyzerOpcode('cccc|000|*|*|1|*|0|****|****|****|11*1|****', 'Undefined_instruction')  # undefined in v4
mls.replace_field('Z', '0', [2, 3, 6])
a.delcodes([35])
a.merge(mls, 35)
a.move(42, 71)
a.move(40, 71)
a.delsep(list(range(0,33)), [70, 71])
print('>>> a.ls()')
a.ls()

# Distinguishing DEFINED, UNDEFINED and UNPREDICTABLE
b = a.copy_current()
b.rmbits([31, 30, 29, 28, 0, 1, 2, 3] + list(range(8, 20)))
print('>>> b.lsambig()')
b.lsambig()
# 
a.delcodes(list(range(67,73)))
a.delsep(list(range(0,33)))
a.newsep([28, 20, 8, 4])
print('>>> a.ls()')
a.ls()

# Determining remaining mnemonics
#
# Software interrupt
a.newcode('cccc|1111iiii|iiiiiiiiiiii|iiii|iiii', 'SWIcc', 66)
a.delcodes([67])
# Coprocessor instructions
tmp = Analyzer([
    ('cccc|110PU0W1|nnnndddd####|oooo|oooo', 'LDCcc'),
    ('cccc|110PU0W0|nnnndddd####|oooo|oooo', 'STCcc'),
    ('cccc|110PU1W1|nnnndddd####|oooo|oooo', 'LDCccL'),
    ('cccc|110PU1W0|nnnndddd####|oooo|oooo', 'STCccL'),
    ('cccc|1110oooo|nnnndddd####|ppp0|mmmm', 'CDPcc'),
    ('cccc|1110ooo0|nnnndddd####|ppp1|mmmm', 'MCRcc' ),
    ('cccc|1110ooo1|nnnndddd####|ppp1|mmmm', 'MRCcc' )
])
a.delcodes([63, 64, 65])
a.merge(tmp, 63)
# Branch instructions
a.delcodes([62])
a.newcode('cccc|1010oooo|oooooooooooo|oooo|oooo', 'Bcc', 62)
a.newcode('cccc|1011oooo|oooooooooooo|oooo|oooo', 'BLcc', 62)
a.delcodes([34])
a.newcode('cccc|00010010|111111111111|0001|mmmm', 'BXcc', 34)
#  Load and Store Multiple instructions
tmp = Analyzer([
    ('cccc|10000SW0|nnnnllllllll|llll|llll', 'STMccDA'),
    ('cccc|10001SW0|nnnnllllllll|llll|llll', 'STMccIA'),
    ('cccc|10010SW0|nnnnllllllll|llll|llll', 'STMccDB'),
    ('cccc|10011SW0|nnnnllllllll|llll|llll', 'STMccIB'),
    ('cccc|10000SW1|nnnnllllllll|llll|llll', 'LDMccDA'),
    ('cccc|10001SW1|nnnnllllllll|llll|llll', 'LDMccIA'),
    ('cccc|10010SW1|nnnnllllllll|llll|llll', 'LDMccDB'),
    ('cccc|10011SW1|nnnnllllllll|llll|llll', 'LDMccIB')
])
a.delcodes([61])
a.merge(tmp, 61)
# Load and store word or unsigned byte
tmp = Analyzer([    
    ('cccc|0110U001|nnnnddddssss|sTT0|mmmm', 'LDRcc Register_Offset Post-Indexed'),
    ('cccc|0110U011|nnnnddddssss|sTT0|mmmm', 'LDRccT Register_Offset Post-Indexed'),
    ('cccc|0111U001|nnnnddddssss|sTT0|mmmm', 'LDRcc Register_Offset'),
    ('cccc|0111U011|nnnnddddssss|sTT0|mmmm', 'LDRcc Register_Offset Pre-Indexed'),
    ('cccc|0110U101|nnnnddddssss|sTT0|mmmm', 'LDRccB Register_Offset Post-Indexed'),
    ('cccc|0110U111|nnnnddddssss|sTT0|mmmm', 'LDRccBT Register_Offset Post-Indexed'),
    ('cccc|0111U101|nnnnddddssss|sTT0|mmmm', 'LDRccB Register_Offset'),
    ('cccc|0111U111|nnnnddddssss|sTT0|mmmm', 'LDRccB Register_Offset Pre-Indexed'),
    ('cccc|0110U000|nnnnddddssss|sTT0|mmmm', 'STRcc Register_Offset Post-Indexed'),
    ('cccc|0110U010|nnnnddddssss|sTT0|mmmm', 'STRccT Register_Offset Post-Indexed'),
    ('cccc|0111U000|nnnnddddssss|sTT0|mmmm', 'STRcc Register_Offset'),
    ('cccc|0111U010|nnnnddddssss|sTT0|mmmm', 'STRcc Register_Offset Pre-Indexed'),
    ('cccc|0110U100|nnnnddddssss|sTT0|mmmm', 'STRccB Register_Offset Post-Indexed'),
    ('cccc|0110U110|nnnnddddssss|sTT0|mmmm', 'STRccBT Register_Offset Post-Indexed'),
    ('cccc|0111U100|nnnnddddssss|sTT0|mmmm', 'STRccB Register_Offset'),
    ('cccc|0111U110|nnnnddddssss|sTT0|mmmm', 'STRccB Register_Offset Pre-Indexed')
])
a.delcodes([60])
a.merge(tmp,60)
tmp = Analyzer([
    ('cccc|0100U001|nnnnddddIIII|IIII|IIII', 'LDRcc Immediate_Offset Post-Indexed'),
    ('cccc|0100U011|nnnnddddIIII|IIII|IIII', 'LDRccT Immediate_Offset Post-Indexed'),
    ('cccc|0101U001|nnnnddddIIII|IIII|IIII', 'LDRcc Immediate_Offset'),
    ('cccc|0101U011|nnnnddddIIII|IIII|IIII', 'LDRcc Immediate_Offset Pre-Indexed'),
    ('cccc|0100U101|nnnnddddIIII|IIII|IIII', 'LDRccB Immediate_Offset Post-Indexed'),
    ('cccc|0100U111|nnnnddddIIII|IIII|IIII', 'LDRccBT Immediate_Offset Post-Indexed'),
    ('cccc|0101U101|nnnnddddIIII|IIII|IIII', 'LDRccB Immediate_Offset'),
    ('cccc|0101U111|nnnnddddIIII|IIII|IIII', 'LDRccB Immediate_Offset Pre-Indexed'),
    ('cccc|0100U000|nnnnddddIIII|IIII|IIII', 'STRcc Immediate_Offset Post-Indexed'),
    ('cccc|0100U010|nnnnddddIIII|IIII|IIII', 'STRccT Immediate_Offset Post-Indexed'),
    ('cccc|0101U000|nnnnddddIIII|IIII|IIII', 'STRcc Immediate_Offset'),
    ('cccc|0101U010|nnnnddddIIII|IIII|IIII', 'STRcc Immediate_Offset Pre-Indexed'),
    ('cccc|0100U100|nnnnddddIIII|IIII|IIII', 'STRccB Immediate_Offset Post-Indexed'),
    ('cccc|0100U110|nnnnddddIIII|IIII|IIII', 'STRccBT Immediate_Offset Post-Indexed'),
    ('cccc|0101U100|nnnnddddIIII|IIII|IIII', 'STRccB Immediate_Offset'),
    ('cccc|0101U110|nnnnddddIIII|IIII|IIII', 'STRccB Immediate_Offset Pre-Indexed'),
])
a.delcodes([59])
a.merge(tmp,59)
# Move immediate to status register
a.delcodes([58])
a.newcode('cccc|00110110|MMMMOOOORRRR|IIII|IIII', 'MSRcc SPSR Immediate_Value', 58)
a.newcode('cccc|00110010|MMMMOOOORRRR|IIII|IIII', 'MSRcc CPSR Immediate_Value', 58)
# Load and Store Halfword and Load Signed Byte
tmp = Analyzer([
    ('cccc|0000U000|nnnndddd0000|1011|mmmm',  'STRccH Register_Offset Post-Indexed'),
    ('cccc|0001U000|nnnndddd0000|1011|mmmm',  'STRccH Register_Offset'),
    ('cccc|0001U010|nnnndddd0000|1011|mmmm',  'STRccH Register_Offset Pre-Indexed'),
    ('cccc|0000U001|nnnndddd0000|1011|mmmm',  'LDRccH Register_Offset Post-Indexed'),
    ('cccc|0001U001|nnnndddd0000|1011|mmmm',  'LDRccH Register_Offset'),
    ('cccc|0001U011|nnnndddd0000|1011|mmmm',  'LDRccH Register_Offset Pre-Indexed'),
    ('cccc|0000U001|nnnndddd0000|1101|mmmm',  'LDRccSB Register_Offset Post-Indexed'),
    ('cccc|0001U001|nnnndddd0000|1101|mmmm',  'LDRccSB Register_Offset'),
    ('cccc|0001U011|nnnndddd0000|1101|mmmm',  'LDRccSB Register_Offset Pre-Indexed'),
    ('cccc|0000U001|nnnndddd0000|1111|mmmm',  'LDRccSH Register_Offset Post-Indexed'),
    ('cccc|0001U001|nnnndddd0000|1111|mmmm',  'LDRccSH Register_Offset'),
    ('cccc|0001U011|nnnndddd0000|1111|mmmm',  'LDRccSH Register_Offset Pre-Indexed'),
    ('cccc|0000U100|nnnnddddhhhh|1011|llll',  'STRccH Immediate_Offset Post-Indexed'),
    ('cccc|0001U100|nnnnddddhhhh|1011|llll',  'STRccH Immediate_Offset'),
    ('cccc|0001U110|nnnnddddhhhh|1011|llll',  'STRccH Immediate_Offset Pre-Indexed'),
    ('cccc|0000U101|nnnnddddhhhh|1011|llll',  'LDRccH Immediate_Offset Post-Indexed'),
    ('cccc|0001U101|nnnnddddhhhh|1011|llll',  'LDRccH Immediate_Offset'),
    ('cccc|0001U111|nnnnddddhhhh|1011|llll',  'LDRccH Immediate_Offset Pre-Indexed'),
    ('cccc|0000U101|nnnnddddhhhh|1101|llll',  'LDRccSB Immediate_Offset Post-Indexed'),
    ('cccc|0001U101|nnnnddddhhhh|1101|llll',  'LDRccSB Immediate_Offset'),
    ('cccc|0001U111|nnnnddddhhhh|1101|llll',  'LDRccSB Immediate_Offset Pre-Indexed'),
    ('cccc|0000U101|nnnnddddhhhh|1111|llll',  'LDRccSH Immediate_Offset Post-Indexed'),
    ('cccc|0001U101|nnnnddddhhhh|1111|llll',  'LDRccSH Immediate_Offset'),
    ('cccc|0001U111|nnnnddddhhhh|1111|llll',  'LDRccSH Immediate_Offset Pre-Indexed')
])
a.delcodes([38, 39, 40, 41])
a.merge(tmp, 38)
# Semaphore instructions
a.delcodes([37])
a.newcode('cccc|00010100|nnnndddd0000|1001|mmmm',  'SWPccB', 37)
a.newcode('cccc|00010000|nnnndddd0000|1001|mmmm',  'SWPcc', 37)
# Multiply instructions
tmp = Analyzer([
    ('cccc|0000000S|dddd0000ssss|1001|mmmm', 'MULcc'),
    ('cccc|0000001S|ddddnnnnssss|1001|mmmm', 'MLAcc'),
    ('cccc|0000100S|hhhhllllssss|1001|mmmm', 'UMULLcc'),
    ('cccc|0000101S|hhhhllllssss|1001|mmmm', 'UMLALcc'),
    ('cccc|0000110S|hhhhllllssss|1001|mmmm', 'SMULLcc'),
    ('cccc|0000111S|hhhhllllssss|1001|mmmm', 'SMLALcc')    
])
def stag(d, f, p):
    if p == '1':
        return d + 'S'
    else:
        return d
tmp.expand_field('S', tag=stag)
a.delcodes([35, 36])
a.merge(tmp, 35)
# Status register access instructions
tmp = Analyzer([
    ('cccc|00010000|1111dddd0000|0000|0000', 'MRScc CPSR'),
    ('cccc|00010100|1111dddd0000|0000|0000', 'MRScc SPSR'),
    ('cccc|00010010|pppp11110000|0000|mmmm', 'MSRcc CPSR'),
    ('cccc|00010110|pppp11110000|0000|mmmm', 'MSRcc SPSR')
])
a.delcodes([16, 17])
a.merge(tmp, 16)

# Conclusion
print(">>> a.ls()")
a.ls()
a.save('armv4t_analyzer', 'armv4t_analyzer_saved.py')
