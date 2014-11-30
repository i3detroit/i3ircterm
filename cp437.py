#!/usr/bin/env python
# -*- coding: UTF-8 -*-

CHARS = {
     #  0    1    2    3    4    5    6    7     8    9    A    B    C    D    E    F
0x20:[u' ',u'!',u'"',u'#',u'$',u'%',u'&',u'\'',u'(',u')',u'*',u'+',u',',u'-',u'.',u'/'],
0x30:[u'0',u'1',u'2',u'3',u'4',u'5',u'6',u'7',u'8',u'9',u':',u';',u'<',u'=',u'>',u'?'],
0x40:[u'@',u'A',u'B',u'C',u'D',u'E',u'F',u'G',u'H',u'I',u'J',u'K',u'L',u'M',u'N',u'O'],
0x50:[u'P',u'Q',u'R',u'S',u'T',u'U',u'V',u'W',u'X',u'Y',u'Z',u'[',u'\\',u']',u'^',u'_'],
0x60:[u'`',u'a',u'b',u'c',u'd',u'e',u'f',u'g',u'h',u'i',u'j',u'k',u'l',u'm',u'n',u'o'],
0x70:[u'p',u'q',u'r',u's',u't',u'u',u'v',u'w',u'x',u'y',u'z',u'{',u'|',u'}',u'~',u'⌂'],
0x80:[u'Ç',u'ü',u'é',u'â',u'ä',u'à',u'å',u'ç',u'ê',u'ë',u'è',u'ï',u'î',u'ì',u'Ä',u'Å'],
0x90:[u'É',u'æ',u'Æ',u'ô',u'ö',u'ò',u'û',u'ù',u'ÿ',u'Ö',u'Ü',u'¢',u'£',u'¥',u'₧',u'ƒ'],
0xA0:[u'á',u'í',u'ó',u'ú',u'ñ',u'Ñ',u'ª',u'º',u'¿',u'⌐',u'¬',u'½',u'¼',u'¡',u'«',u'»'],
0xB0:[u'░',u'▒',u'▓',u'│',u'┤',u'╡',u'╢',u'╖',u'╕',u'╣',u'║',u'╗',u'╝',u'╜',u'╛',u'┐'],
0xC0:[u'└',u'┴',u'┬',u'├',u'─',u'┼',u'╞',u'╟',u'╚',u'╔',u'╩',u'╦',u'╠',u'═',u'╬',u'╧'],
0xD0:[u'╨',u'╤',u'╥',u'╙',u'╘',u'╒',u'╓',u'╫',u'╪',u'┘',u'┌',u'█',u'▄',u'▌',u'▐',u'▀'],
0xE0:[u'α',u'ß',u'Γ',u'π',u'Σ',u'σ',u'µ',u'τ',u'Φ',u'Θ',u'Ω',u'δ',u'∞',u'φ',u'ε',u'∩'],
0xF0:[u'≡',u'±',u'≥',u'≤',u'⌠',u'⌡',u'÷',u'≈',u'°',u'∙',u'·',u'√',u'ⁿ',u'²',u'■',u' ']}

def transpose():
    chars = {}
    for msb in xrange(0x20,0x100,0x10):
        for lsb in xrange(0x00,0x10):
            chars[CHARS[msb][lsb]] = hex(msb+lsb)
    return chars

if __name__ == '__main__':
    asciiheader = '   | ' + ' '.join([hex(i)[2] + 'h' for i in xrange(0x20,0x80,0x10)])
    extheader = ' |  ' + ' '.join([hex(i)[2] + 'h' for i in xrange(0x80,0x100,0x10)])
    print asciiheader + extheader
    print '-'*3 + '+' + '-'*(len(asciiheader)-3) + '+' + '-'*(len(extheader)-2)
    for lsb in xrange(0x00,0x10):
        chars = []
        for msb in xrange(0x20,0x100,0x10):
            chars.append(CHARS[msb][lsb])
            if msb == 0x70:
                chars.append('|')
        print 'x'+hex(lsb)[2] + ' | ' + '  '.join(chars)
            
