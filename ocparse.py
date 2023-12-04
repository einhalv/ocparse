"""Module for parsing and analyzing machine code instructions

   The module provides a class **Parser** for a machine code parsers and a
   corresponding class **Opcode** for opcode-patterns that defines bitpatterns
   and/or bitfields of which the parser can extract the values.
   It also has an analyzer class **Analyzer** with its own opocde class
   **AnalyzerOpcode** that can be used for analysis of
   instruction sets and their decoding.

   The module is written with fixed-width instructions in mind.

"""
from __future__ import annotations
import math


def strip_sep(s: str, seps=(' ', '_', '|')) -> str:
    """remove separator characters from string

    """
    return ''.join(c for c in s if c not in seps)


def nibble_sep(s: str, sep='_', seps=(' ', '_', '|')) -> str:
    """ remove all separator characters and insert new separator for
        each nibble

    """
    s = strip_sep(s, seps=seps)
    sn = ''
    n = 0
    m = 0
    ls = len(s)
    for c in s[::-1]:
        sn = c + sn
        n += 1
        m += 1
        if n == 4 and m != ls:
            n = 0
            sn = sep + sn
    return sn


def unzip_sep(s: str, seps=(' ', '_', '|')) -> tuple[str, list[str, ...]]:
    """split into string without separators and a list of separators

       Returns tuple of stripped string and list of separators.
       There is one separator per character of the stripped string and
       one at the end. A separator string in the list is '' if
       there is no separator.

    """
    sbare = ''
    sepl = []
    cs = ''
    for c in s[::-1]:
        if c in seps:
            cs += c
        else:
            sbare += c
            sepl.append(cs[::-1])
            cs = ''
    sepl.append(cs)
    return (sbare[::-1], sepl)


def zip_sep(s: str, sepl: list[str, ...]) -> str:
    """combine string and list of separators into string with separators

    """
    s = s[::-1]
    sout = ''
    for n in range(len(s)):
        sout += sepl[n] + s[n]
    sout += sepl[-1]
    return sout


class Opcode():
    """Opcode pattern for use by the opcode parser

    :param name:  Name of opcode
    :param pattern: Pattern of opcode.
        '0' means bit must be zero, '1' means bit must be one,
        and '*' means bit can take any value. If the field is a letter,
        e.g. 'A', the bit belongs to parameter A and can take any value.
        ' ', '|' and '_' are separators and are stripped away before pattern
        is used.
    :param param_filter:  Logical function with dictionary as parameter.
                          Dictionary holds values opcode fields.
                          Returns True if values are valid, otherwise False.

    """
    def __init__(self, name: str, pattern_str: str,
                 param_filter=lambda x: True):
        """Constructor method

        """
        self.name = name
        pattern_str = strip_sep(pattern_str)
        self.pattern_str = pattern_str
        self._len = len(pattern_str)
        self.pattern = 0
        self.mask = 0
        self.params = {}
        self.param_filter = param_filter
        cp = None
        cmask = 0
        rshift = 0
        d = 1
        n = 0
        for c in pattern_str[::-1]:
            if c == '1':
                self.pattern += d
                self.mask += d
            elif c == '0':
                self.mask += d
            if c in '10*' and cp is not None:
                if cp in self.params:
                    raise Exception(
                        "parameter \"{}\" already defined".format(c))
                self.params[cp] = (cmask, rshift)
                cp = None
            elif c not in '10*' and cp is not None and c != cp:
                if cp in self.params:
                    raise Exception(
                        "parameter \"{}\" already defined".format(cp))
                self.params[cp] = (cmask, rshift)
                cp = c
                rshift = n
                cmask = d
            elif c not in '10*' and cp is None:
                cp = c
                rshift = n
                cmask = d
            elif c == cp:
                cmask += d
            n += 1
            d *= 2
        if cp is not None:
            if cp in self.params:
                raise Exception(
                    "parameter \"{}\" already defined".format(c))
            self.params[cp] = (cmask, rshift)

    def __repr__(self):
        fmt = "{{:0{}b}}\n".format(self._len)
        str = self.name + '\n'
        str += fmt.format(self.pattern)
        str += fmt.format(self.mask)
        for k in self.params:
            str += k + '\n'
            str += fmt.format(self.params[k][0])
        return str

    def __len__(self):
        return self._len
        """Return number of bits

        """

    def rename_field(self, *pairs):
        """Rename parameter field(s)

        rename_field(self, kold1, knew1, kold2, knew2, ...)
            kold1  old field name (default is character used in pattern)
            knew1  new field name, string without whitespace

        """
        for p in zip(pairs[0::2], pairs[1::2]):
            self.params[p[1]] = self.params[p[0]]
            self.params.pop(p[0])

    def decode(self, code: int) -> None | dict:
        """ Return dictionary of parameters if code matches opcode

        """
        if code >= 2**self._len:
            return None
        if 0 == (code ^ self.pattern) & self.mask:
            d = {}
            d['name'] = self.name
            for k in self.params:
                d[k] = (code & self.params[k][0]) >> self.params[k][1]
            if self.param_filter(d):
                return d
            else:
                return None

    def intersect(self, oc: Opcode) -> int:
        """Check if opcode patterns can overlap

        """
        if 0 == (oc.pattern ^ self.pattern) & self.mask & oc.mask:
            return 1
        else:
            return 0


class Parser():
    """Opcode parser

    """
    def __init__(self):
        """Constructor method

        """
        self.opcodes = []

    def __repr__(self):
        str = ''
        for o in self.opcodes:
            ocp = o[0]
            str += "{}, {}: ".format(ocp.name, o[1])
            str += ', '.join(s for s in ocp.params)
            str += '\n'
        return str

    def add(self, opc: Opcode):
        """Add opcode to parser

        If name of opc is unique, the opcode is added to the parser.
        If the name is already in use, an exception is raised.

        """
        names = [o[0].name for o in self.opcodes]
        if opc.name in names:
            raise Exception("opcode name already exists")
        else:
            self.opcodes.append([opc, 0])

    def set_priority(self, name: str, pri: int):
        """Set priority of named opcode

        """
        for le in self.opcodes:
            if le[0].name == name:
                le[1] = pri
                break

    def get_priority(self, name: str) -> int | None:
        """ Return priority of named opcode

        """
        for o in self.opcodes:
            if o[0].name == name:
                return o[1]
        return None

    def parse(self, code: int) -> list[dict, ...]:
        """Parse opcode

           Returns list of dictionaries each of which describes the
           an interpretation of the opcode

        """
        ocd = []
        pri = max(o[1] for o in self.opcodes)+1
        for o in self.opcodes:
            if (len(ocd) > 0 and o[1] <= pri) or len(ocd) == 0:
                d = o[0].decode(code)
                if d is not None and o[1] < pri:
                    ocd = [d]
                    pri = o[1]
                elif d is not None:
                    ocd.append(d)
        return ocd

    def ambiguity_matrix(self) -> list[list[int, ...], ...]:
        """Return list of lists whose [i][j]-element is nonzero if
        opcode i and j can not be distinguished


        """
        return [[o1[0].intersect(o2[0]) for o2 in self.opcodes]
                for o1 in self.opcodes]

    def ambiguity_list(self) -> list[tuple[str, str], ...]:
        """Return list of pairs of names of ambigous opcodes

        """
        n = len(self.opcodes)
        o = self.opcodes
        return [(o[i1][0].name, o[i2][0].name) for i1 in range(n)
                for i2 in range(i1+1, n) if o[i1][0].intersect(o[i2][0])]

    def __str__(self):
        s = ''
        for o in self.opcodes:
            s += nibble_sep(o[0].pattern_str) + '  ' + o[0].name + '\n'
        return s


class AnalyzerOpcode():
    """Opcode pattern for Analyzer

    :param opcode_pattern:  String of bitpatterns with separator characters
    :param description:     Description of opcode, e.g. name or mnemonic

    """
    def __init__(self, opcode_pattern: str, description: str):
        """Constructor method

        """
        p, self.seps = unzip_sep(opcode_pattern)
        # store lsb first
        self._pattern = p[::-1]
        self.desc = description.strip()

    def __len__(self):
        return len(self._pattern)

    def copy(self) -> 'AnalyzerOpcode':
        """Make a copy of opcode

        """
        oc = AnalyzerOpcode(self.pattern(), self.desc)
        oc.seps = self.seps.copy()
        return oc

    def pattern(self) -> str:
        """Make string of bitpattern without separators

        """
        return self._pattern[::-1]

    def lstr(self) -> str:
        """Make string of bitpattern with separators

        """
        nb = len(self._pattern)
        ncs = ''
        for ii in range(nb):
            ncs += self.seps[ii][::-1]
            ncs += self._pattern[ii]
        ncs += self.seps[nb][::-1]
        return ncs[::-1]

    def lstrlen(self) -> int:
        """Length of bitpattern with separators

        """
        return len(self._pattern) + sum([len(s) for s in self.seps])

    def setsep(self, sepind: list[int, ...], sep='|'):
        """Set separator at specified bit positions

        """
        for jj in sepind:
            self.seps[jj] = sep

    def delsep(self, seps: list[int, ...]):
        """Remove separators at specified bit positions

        """
        for jj in seps:
            self.seps[jj] = ''

    def rmbits(self, bl: list[int, ...]) -> 'AnalyzerOpcode':
        """Make opcode with specified bits removed

        """
        nbits = len(self._pattern)
        sn = ''.join(self._pattern[ii] for ii in range(nbits) if ii not in bl)
        newseps = []
        rem = ''
        for ii in range(nbits):
            if ii in bl:
                rem += self.seps[ii]
            else:
                newseps.append(self.seps[ii] + rem)
                rem = ''
        newseps.append(self.seps[nbits]+rem)
        oc = AnalyzerOpcode(sn[::-1], self.desc)
        oc.seps = newseps
        return oc

    def combine(self, oc: 'AnalyzerOpcode') -> None | 'AnalyzerOpcode':
        """Combine opcode patterns if possible

        :param oc: other Analyzeropcode
        :returns: None if combinations is not possible. 
                  AnalyzerOpcode with combined pattern
                  if the the two patterns differ in only one bit.

        """
        if len(self) != len(oc):
            return None
        s1 = ''.join([c if c in '01' else '*' for c in self.pattern()])
        s2 = ''.join([c if c in '01' else '*' for c in oc.pattern()])
        count = 0
        s = ''
        for t in zip(s1, s2):
            if t[0] == t[1]:
                s += t[0]
            else:
                s += '*'
                count += 1
        if count == 1:
            return AnalyzerOpcode(s, self.desc + ' ' + oc.desc)
        else:
            return None

    def intersect(self, oc: 'AnalyzerOpcode') -> bool:
        """Check if opcodes can describe same bitpattern

        """
        p1 = self._pattern
        p2 = oc.pattern()[::-1]
        l1 = len(p1)
        l2 = len(p2)
        d = l1 - l2
        if d > 0:
            p1 = p1[:l2]
        elif d < 0:
            p2 = p2[:l1]
        x = False
        for ii in range(len(p1)):
            c1 = p1[ii]
            c2 = p2[ii]
            m = (c1 in {'0', '1'}) and (c2 in {'0', '1'})
            x = x or (m and c1 != c2)
        return not x

    def replace_field(self, field: str, val: str):
        """Replace a field by a string

        :param field: field character or string
        :param val:   string to replace field

        """
        self._pattern = self._pattern.replace(field, val)

    def expand_field(self, field: str, excpt: list[str, ...] = [],
                     tag=None) -> list['AnalyzerOpcode', ...]:
        """Make list of opcodes with given field expanded

        Expands to all possible bitpatterns except those given
        in list of exceptions.

        :param field: The opcode field to be expanded
        :param excpt: Bitpatterns to be ignored
        :param tag: Function tag(desc0, field, p) that returns new description
         field. It takes as the first parameter a string desc0 which is a
         description to be modified/substituted, the single character string
         field holding the name of the bitfield and the string p holding
         the actual pattern of the field.

        """
        if field in ['1', '0', '|', '_', '*', ' ']:
            return [self]
        iis = [ii for ii in range(len(self._pattern))
               if field == self._pattern[ii]]
        iis.reverse()
        if iis:
            nb = len(iis)
            fmt = '{{:0{}b}}'.format(nb)
            patt = [fmt.format(ii) for ii in range(2**nb)]
            patt = [p for p in patt if p not in excpt]
            new = []
            for p in patt:
                s = self._pattern
                ls = len(s)
                for jj in range(len(iis)):
                    ii = iis[jj]
                    s = s[0:ii] + p[jj] + s[ii+1:ls]
                desc = tag(self.desc, field, p)
                oc = AnalyzerOpcode(s[::-1], desc)
                oc.seps = self.seps
                new.append(oc)
            return new
        else:
            return [self]


class Analyzer():
    """Class for analyzing instruction set

    :param opcode_patterns: Instruction set as list of AnalyzerOpcode objects

    """
    def __init__(self, opcode_patterns: list[AnalyzerOpcode, ...]):
        """Constructor method

        """
        self.codes = [[AnalyzerOpcode(*p) for p in opcode_patterns]]
        self.cp = 0

    def __repr__(self):
        s = 'Analyzer(['
        codes = self.codes[self.cp]
        if len(codes) == 0:
            return 'Analyzer([])'
        for c in codes:
            s += '(\'{}\', \'{}\'), '.format(c.pattern(), c.desc)
        s = s[:-2] + '])'
        return s

    def __str__(self):
        codes = self.codes[self.cp]
        s = ''
        if len(codes) == 0:
            return s
        for c in codes:
            s += '{}  {}\n'.format(c.pattern(), c.desc)
        s = s[:-1]
        return s

    def __len__(self):
        """Number of opcode patterns defined

        """
        return len(self.codes[self.cp])

    def __add__(self, other):
        a = self.copy_current()
        b = other.copy_current()
        a.codes[0] += b.codes[0]
        return a

    def copy_current(self, codenos: list[int, ...] = None) -> 'Analyzer':
        """Make a deep copy of current analyzer state

        :param codenos: list of opcode pattern numbers

        """
        an = Analyzer([])
        if codenos:
            codes = [self.codes[self.cp][ii] for ii in codenos]
        else:
            codes = self.codes[self.cp]
        an.codes = [[c.copy() for c in codes]]
        return an

    def ls(self):
        """List opcode patterns

        """
        codes = self.codes[self.cp]
        nc = len(codes)
        if not nc:
            print('-- no opcodes defined --')
            return
        w = math.ceil(math.log(nc)/math.log(10.0))
        cl = max([c.lstrlen() for c in codes])
        fmt = "{{:>{}}}  {{:>{}}}  {{}}".format(w, cl)
        for n in range(nc):
            code = codes[n]
            if len(code):
                s = fmt.format(n, code.lstr(), code.desc)
            else:
                s = fmt.format(n, code.seps[0]+code.desc, '')
            print(s)

    def newsep(self, seps: list[int, ...], ins: None | list[int, ...] = None,
               sep: str = '|'):
        """Introduce separators in listing of opcodes

        Only affects current opcode set

        :param seps:  position of separators (0-#bits)
        :param  ins:  index to opcodes which are affected
        :param  sep:  separator character

        """
        codes = self.codes[self.cp]
        if ins is None:
            ins = list(range(len(codes)))
        for ii in ins:
            codes[ii].setsep(seps, sep)

    def delsep(self, seps: list[int, ...], ins: None | list[int, ...] = None):
        """Delete separators

        Only affects current opcode set

        :param seps:  position of separators (0-#bits)
        :param  ins:  index to opcodes which are affected

        """
        codes = self.codes[self.cp]
        if ins is None:
            ins = list(range(len(codes)))
        for ii in ins:
            codes[ii].delsep(seps)

    def rmbits(self, bl: list[int, ...]):
        """Remove bits from opcodes

        :param bl: list of bits to remove

        """
        codes = self.codes[self.cp]
        self.cp += 1
        self.codes = self.codes[:self.cp]
        self.codes.append([c.rmbits(bl) for c in codes])

    def lsambig(self):
        """List ambiguities between opcode patterns

        Checks all pairs of opcode patterns to see if there
        exists a bit pattern that matches both opcode patterns.
        Lists all such ambiguities that are found.

        """
        amb = self.ambiguities()
        for a in amb:
            print("{}: {}, {}: {}".format(a[0][0], a[0][1], a[1][0], a[1][1]))
        print('Number of ambiguities: {}\n'.format(len(amb)))

    def ambiguities(self):
        """Checks opcode patterns for possible ambiguities

        Checks all pairs of opcode patterns to see if there
        exists a bit pattern that matches both opcode patterns.

        :returns:  list of tuples of mutually ambiguous opcode patterns
                   each specified as a tuple of opcode index and description

        """
        codes = [c for c in self.codes[self.cp] if len(c)]
        nc = len(codes)
        count = 0
        amb = []
        for ii in range(nc):
            c1 = codes[ii]
            for jj in range(ii+1, nc):
                if c1.intersect(codes[jj]):
                    amb.append(((ii, c1.desc), (jj, codes[jj].desc)))
        return amb

    def bitworth(self) -> list[int, ...]:
        """Calculate each bit's worth

        The worth is calculated as the increase in the number of ambiguities
        in the instruction set if the bit is removed.

        :returns:  List of each bit's worth

        """
        nbits = max(len(c) for c in self.codes[self.cp])
        worth = []
        an = self.copy_current()
        a0 = len(an.ambiguities())
        for n in range(nbits):
            an.rmbits([n])
            worth.append(len(an.ambiguities())-a0)
            an.undo()
        return worth

    def undo(self):
        """Sets the previous opcode-pattern set to current set

        """
        if self.cp:
            self.cp -= 1
        else:
            print("nothing to undo!")

    def redo(self):
        """Set the next opcode-pattern set, if any, to current set

        """
        if self.cp == len(self.codes) - 1:
            print("nothing to redo!")
        else:
            self.cp += 1

    def when(self):
        """Print where current opcode-pattern set is in history

        """
        print("At {} in history of 0-{}".format(self.cp, len(self.codes)-1))

    def rmfuture(self):
        """Delete opcode-pattern sets newer than the current

        """
        self.codes = self.codes[:self.cp + 1]

    def rmpast(self):
        """Delete opcode-pattern sets older than the current

        """
        self.codes = self.codes[self.cp:]
        self.cp = 0

    def replace_field(self, field: str, val: str, cno: list[int, ...] = None):
        """Replace a field by a string

        :param field: field character or string
        :param val:   string to replace field

        """
        codes = [c.copy() for c in self.codes[self.cp]]
        nc = len(codes)
        if cno is None:
            cno = list(range(nc))
        for ii in cno:
            codes[ii].replace_field(field, val)
        self.cp += 1
        self.codes = self.codes[:self.cp]
        self.codes.append(codes)

    def expand_field(self, field: str, cno: None | list[int, ...] = None,
                     excpt: list[int, ...] = [],
                     tag=lambda d, f, v: d + '_' + f + v):
        """Expand an opcode field

        Replaces opocode pattern by opcode patterns where a named field
        has bin substituted for all its possible bit patterns except
        those given list of exceptions. The operation can be carried out on
        all opcode patters or on patterns given in a list.

        :param field: Character naming the field to expand to binary.
        :param cno:   List of numbers of the codes this should be done for.
                      An argument of None results in all codes containing
                      the field being expanded.
        :param excpt: List of values that should not be included.
        :param tag:   Function tag(desc0, field, p) to generate new
                      description string. The first parameter is a string
                      desc0 with the description to be modified/substituted.
                      The second, field, is a single character string holding
                      the name of the bitfield. The third string parameter p
                      holds the actual pattern of the field.

        """
        if field in ['1', '0', '|', '_', '*', ' ']:
            return
        codes = self.codes[self.cp]
        nc = len(codes)
        if cno is None:
            cno = list(range(nc))
        expanded = []
        for ii in range(nc):
            if ii in cno:
                expanded += codes[ii].expand_field(field, excpt, tag)
            else:
                expanded.append(codes[ii])
        self.cp += 1
        self.codes = self.codes[:self.cp]
        self.codes.append(expanded)

    def delcodes(self, cl: list[int, ...]):
        """Delete opocde patterns

        Takes a list of opcode-pattern number and deletes patterns with the
        given number.

        """
        cl.sort(reverse=True)
        nc = self.codes[self.cp]
        for ii in cl:
            nc.pop(ii)
        self.cp += 1
        self.codes = self.codes[:self.cp]
        self.codes.append(nc)

    def combinecodes(self):
        """Combine as many code patterns as possible

        """
        self.dup()
        codes = self.get_codes()
        combined = 1
        while combined:
            combined = 0
            nc = len(codes)
            pp = [(ii, jj) for ii in range(nc) for jj in range(ii+1, nc)]
            deletes = []
            while len(pp):
                p = pp.pop()
                c1 = codes[p[0]]
                c2 = codes[p[1]]
                c = c1.combine(c2)
                if c is not None:
                    pp = [p0 for p0 in pp if not (p0[0] in p or p0[1] in p)]
                    codes[p[0]] = c
                    deletes.append(p[1])
                    combined += 1
            deletes.sort(reverse=True)
            for ii in deletes:
                del codes[ii]

    def newcode(self, pattern: str, description: str, pos: None | int = None):
        """Add a new opcode pattern to the analyzer

        Add the pattern AnalyzerOpcode(pattern, description) in
        opcode position pos. If pos is not given, the code is added
        to the end.

        """
        nc = self.codes[self.cp]
        if pos is None:
            pos = len(nc)
        nc.insert(pos, AnalyzerOpcode(pattern, description))
        self.cp += 1
        self.codes = self.codes[:self.cp]
        self.codes.append(nc)

    def title(self, pos, text):
        """Add a title

        Equivalent to adding a new, empty opcode pattern with the title
        text as description.

        """
        self.newcode('', text, pos)

    def get_codes(self) -> list[AnalyzerOpcode, ...]:
        """Return list of opcodes

        """
        return self.codes[self.cp]

    def merge(self, other: 'Analyzer', pos: int = None):
        """Merge in another analyzer

        :param other: The analyzer to be merged in.
        :param pos: The position at which to merge in (optional)

        """
        oc = self.codes[self.cp]
        if pos is None:
            pos = len(oc)
        self.cp += 1
        self.codes = self.codes[:self.cp]
        self.codes.append(oc[:pos] + other.get_codes() + oc[pos:])

    def dup(self) -> list[AnalyzerOpcode, ...]:
        """Duplicate current codes

        :returns: The duplicate
        """
        codes = [c.copy() for c in self.codes[self.cp]]
        self.cp += 1
        self.codes = self.codes[:self.cp]
        self.codes.append(codes)
        return codes

    def move(self, src: int, to: int):
        """Move code within list

        :param src: Position of code pattern in list
        :param to: New position of code pattern

        """
        if src < 0 or src >= len(self):
            return
        codes = self.dup()
        c = codes.pop(src)
        codes.insert(max(0, to), c)

    def save(self, name, filename):
        """Save analyzer as pyton code
        
        :param name: Variable name or analyzer
        :param filename: File to write to

        """
        with open(filename, "w") as file:
            codes = self.codes[self.cp]
            file.write("import ocparse\n\n")
            file.write("{} = ocparse.Analyzer([\n".format(name))
            file.write(",\n".join(["   (\'{}\', \'{}\')".format(c.lstr(),
                                                    c.desc) for c in codes]))
            file.write("\n])")
