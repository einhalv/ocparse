import ocparse

# defining two patterns and a parser 
op = ocparse.Parser()
def dprocfilter(d):
    return d['cond'] != 15

oc1 = ocparse.Opcode('Data_Processing_Immediate',
                     'cccc|001ooooS|nnnnddddrrrr|iiii|iiii',
                     dprocfilter)
oc1.rename_field('c', 'cond', 'o', 'opcode', 'n', 'Rn', 'd', 'Rd',
                 'r', 'rotate_imm', 'i', 'immed_8')
op.add(oc1)
def msrfilter(d):
    return (d['cond'] != 0b1111) and (d['SBO'] == 0b1111)

oc2 = ocparse.Opcode('Move_immediate_to_status_register',
                     'cccc|00110R10|MMMMOOOOrrrr|iiii|iiii',
                     msrfilter)
oc2.rename_field('c', 'cond', 'M', 'field_mask', 'O', 'SBO',
                 'r', 'rotate_imm', 'i', 'immed_8')
op.add(oc2)

# testing instructions
i1 = 0b11100011001100011111010000100000
i2 = 0b11100011001000011111010000100000
print("Decoding instruction i1 with oc1:", oc1.decode(i1), '\n')
print("Decoding instruction i2 with oc1:", oc1.decode(i2), '\n')
print("Decoding instruction i1 with oc2:", oc2.decode(i1), '\n')
print("Decoding instruction i2 with oc2:", oc2.decode(i2), '\n')
print("Parse i1: ", op.parse(i1))
print("Parse i2: ", op.parse(i2))


# testing filter functions
i3 = 0b11110011001000011111010000100000
i4 = 0b11100011001000011101010000100000
print("Parse i3: ", op.parse(i3))
print("Parse i4: ", op.parse(i4))

# using the filter function for further decoding
print("\nMore advanced filter function")
dataproc = {
    0b0000: 'AND', 0b0001: 'EOR', 0b0010: 'SUB', 0b0011: 'RSB',
    0b0100: 'ADD', 0b0101: 'ADC', 0b0110: 'SBC', 0b0111: 'RSC',
    0b1000: 'TST', 0b1001: 'TEQ', 0b1010: 'CMP', 0b1011: 'CMN',
    0b1100: 'ORR', 0b1101: 'MOV', 0b1110: 'BIC', 0b1111: 'MVN'
}
conditions = {
    0b0000: 'EQ',
    0b0001: 'NE',
    0b0010: 'CS',
    0b0011: 'CC',
    0b0100: 'MI',
    0b0101: 'PL',
    0b0110: 'VS',
    0b0111: 'VC',
    0b1000: 'HI',
    0b1001: 'LS',
    0b1010: 'GE',
    0b1011: 'LT',
    0b1100: 'GT',
    0b1101: 'LE',
    0b1110: 'AL',
    0b1111: 'UNPREDICTABLE'
}
def dprocfilter2(d):
    cond = conditions[d['cond']]
    if cond == 'UNPREDICTABLE':
        d.clear()
        d['name'] = cond
        return True
    if cond == 'AL':
        cond = ''
    mnemonic = dataproc[d['opcode']]
    if d['S']:
        if mnemonic not in ('TST', 'TEQ', 'CMP', 'CMN'):
            cond += 'S'
    else:
        if mnemonic in ('TST', 'TEQ', 'CMP', 'CMN'):
            return False
    mnemonic += cond
    d['name'] = mnemonic + ' ' + d['name']
    return True

oc3 = ocparse.Opcode('Data_Processing_Immediate',
                     'cccc|001ooooS|nnnnddddrrrr|iiii|iiii',
                     dprocfilter2)
oc3.rename_field('c', 'cond', 'o', 'opcode', 'n', 'Rn', 'd', 'Rd',
                 'r', 'rotate_imm', 'i', 'immed_8')
op2 = ocparse.Parser()
op2.add(oc3)
def msrfilter2(d):
    OK = (d['cond'] != 0b1111) and (d['SBO'] == 0b1111)
    if OK:
        d['name'] = 'MSR ' + d['name']
    else:
        d.clear()
        d['name'] = 'UNPREDICTABLE'
    return True

oc4 = ocparse.Opcode('Move_immediate_to_status_register',
                     'cccc|00110R10|MMMMOOOOrrrr|iiii|iiii',
                     msrfilter2)
oc4.rename_field('c', 'cond', 'M', 'field_mask', 'O', 'SBO',
                 'r', 'rotate_imm', 'i', 'immed_8')
op2.add(oc4)

print("Parse i1: ", op2.parse(i1))
print("Parse i2: ", op2.parse(i2))
print("Parse i3: ", op2.parse(i3))
print("Parse i4: ", op2.parse(i4))

