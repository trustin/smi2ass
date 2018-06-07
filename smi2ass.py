#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
#
# Copyright (C) 2018  Trustin Heuiseung Lee and other contributors
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
# Forked from: https://github.com/hojel/service.subtitles.gomtv/blob/3a7342961e140eaf8250659b0ac6158ce5e6bc5c/resources/lib

import chardet, os, sys, re
from html.parser import HTMLParser
from collections import defaultdict
from operator import itemgetter
from bs4 import BeautifulSoup

default_lang_code = 'kor'
default_font_name = 'sans-serif'

# lang class for multiple language subtitle
langCode = {'KRCC':'kor','KOCC':'kor','KR':'kor','KO':'kor','KOREANSC':'kor','KRC':'kor',
            'ENCC':'eng','EGCC':'eng','EN':'eng','EnglishSC':'eng','ENUSCC':'eng','ERCC':'eng',
            'CNCC':'chi','JPCC':'jpn','UNKNOWNCC':'und','COMMENTARY':'commentary'
            }

script_info =\
"""[Script Info]
;This is an Advanced Sub Station Alpha v4+ script.
;Converted by smi2ass
ScriptType: v4.00+
Collisions: Normal
PlayResX: 384
PlayResY: 288
Timer: 100.0000

"""

styles=\
"""
[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,""" + default_font_name + """,22,&H00ffffff,&H0000ffff,&H00000000,&H80000000,0,0,0,0,100,100,0,0.00,1,1,1,2,20,20,20,1

"""

events=\
"""
[Events]
Format: Layer, Start, End, Style, Actor, MarginL, MarginR, MarginV, Effect, Text
"""

# for color code conversion including some common typos
css3_names_to_hex = {
    'aliceblue': '#f0f8ff',
    'antiquewhite': '#faebd7',
    'aqua': '#00ffff',
    'aquamarine': '#7fffd4',
    'azure': '#f0ffff',
    'beige': '#f5f5dc',
    'bisque': '#ffe4c4',
    'black': '#000000',
    'blanchedalmond': '#ffebcd',
    'blue': '#0000ff',
    'blueviolet': '#8a2be2',
    'brown': '#a52a2a',
    'burlywood': '#deb887',
    'cadetblue': '#5f9ea0',
    'chartreuse': '#7fff00',
    'chocolate': '#d2691e',
    'coral': '#ff7f50',
    'cornflowerblue': '#6495ed',
    'cornsilk': '#fff8dc',
    'crimson': '#dc143c',
    'cyan': '#00ffff',
    'darkblue': '#00008b',
    'darkcyan': '#008b8b',
    'darkgoldenrod': '#b8860b',
    'darkgray': '#a9a9a9',
    'darkgrey': '#a9a9a9',
    'darkgreen': '#006400',
    'darkkhaki': '#bdb76b',
    'darkmagenta': '#8b008b',
    'darkolivegreen': '#556b2f',
    'darkorange': '#ff8c00',
    'darkorchid': '#9932cc',
    'darkred': '#8b0000',
    'darksalmon': '#e9967a',
    'darkseagreen': '#8fbc8f',
    'darkslateblue': '#483d8b',
    'darkslategray': '#2f4f4f',
    'darkslategrey': '#2f4f4f',
    'darkturquoise': '#00ced1',
    'darkviolet': '#9400d3',
    'deeppink': '#ff1493',
    'deepskyblue': '#00bfff',
    'dimgray': '#696969',
    'dimgrey': '#696969',
    'dodgerblue': '#1e90ff',
    'firebrick': '#b22222',
    'floralwhite': '#fffaf0',
    'forestgreen': '#228b22',
    'fuchsia': '#ff00ff',
    'gainsboro': '#dcdcdc',
    'ghostwhite': '#f8f8ff',
    'gold': '#ffd700',
    'goldenrod': '#daa520',
    'gray': '#808080',
    'grey': '#808080',
    'green': '#008000',
    'greenyellow': '#adff2f',
    'honeydew': '#f0fff0',
    'hotpink': '#ff69b4',
    'indianred': '#cd5c5c',
    'indigo': '#4b0082',
    'ivory': '#fffff0',
    'khaki': '#f0e68c',
    'lavender': '#e6e6fa',
    'lavenderblush': '#fff0f5',
    'lawngreen': '#7cfc00',
    'lemonchiffon': '#fffacd',
    'lightblue': '#add8e6',
    'lightcoral': '#f08080',
    'lightcyan': '#e0ffff',
    'lightgoldenrodyellow': '#fafad2',
    'lightgray': '#d3d3d3',
    'lightgrey': '#d3d3d3',
    'lightgreen': '#90ee90',
    'lightpink': '#ffb6c1',
    'lightsalmon': '#ffa07a',
    'lightseagreen': '#20b2aa',
    'lightskyblue': '#87cefa',
    'lightslategray': '#778899',
    'lightslategrey': '#778899',
    'lightsteelblue': '#b0c4de',
    'lightyellow': '#ffffe0',
    'lime': '#00ff00',
    'limegreen': '#32cd32',
    'linen': '#faf0e6',
    'magenta': '#ff00ff',
    'maroon': '#800000',
    'mediumaquamarine': '#66cdaa',
    'mediumblue': '#0000cd',
    'mediumorchid': '#ba55d3',
    'mediumpurple': '#9370d8',
    'mediumseagreen': '#3cb371',
    'mediumslateblue': '#7b68ee',
    'mediumspringgreen': '#00fa9a',
    'mediumturquoise': '#48d1cc',
    'mediumvioletred': '#c71585',
    'midnightblue': '#191970',
    'mintcream': '#f5fffa',
    'mistyrose': '#ffe4e1',
    'moccasin': '#ffe4b5',
    'navajowhite': '#ffdead',
    'navy': '#000080',
    'oldlace': '#fdf5e6',
    'olive': '#808000',
    'olivedrab': '#6b8e23',
    'orange': '#ffa500',
    'orangered': '#ff4500',
    'orchid': '#da70d6',
    'palegoldenrod': '#eee8aa',
    'palegreen': '#98fb98',
    'paleturquoise': '#afeeee',
    'palevioletred': '#d87093',
    'papayawhip': '#ffefd5',
    'peachpuff': '#ffdab9',
    'peru': '#cd853f',
    'pink': '#ffc0cb',
    'plum': '#dda0dd',
    'powderblue': '#b0e0e6',
    'purple': '#800080',
    'red': '#ff0000',
    'rosybrown': '#bc8f8f',
    'royalblue': '#4169e1',
    'saddlebrown': '#8b4513',
    'salmon': '#fa8072',
    'sandybrown': '#f4a460',
    'scarlet': '#9c0606',
    'seagreen': '#2e8b57',
    'seashell': '#fff5ee',
    'sienna': '#a0522d',
    'silver': '#c0c0c0',
    'skyblue': '#87ceeb',
    'slateblue': '#6a5acd',
    'slategray': '#708090',
    'slategrey': '#708090',
    'snow': '#fffafa',
    'springgreen': '#00ff7f',
    'steelblue': '#4682b4',
    'tan': '#d2b48c',
    'teal': '#008080',
    'thistle': '#d8bfd8',
    'tomato': '#ff6347',
    'turquoise': '#40e0d0',
    'violet': '#ee82ee',
    'wheat': '#f5deb3',
    'white': '#ffffff',
    'whitesmoke': '#f5f5f5',
    'yellow': '#ffff00',
    'yellowgreen': '#9acd32',
}

space_chars = [
    u'\u00A0', u'\u180E', u'\u2000', u'\u2001', u'\u2002', u'\u2003', u'\u2004', u'\u2005', u'\u2006',
    u'\u2007', u'\u2008', u'\u2009', u'\u200A', u'\u200B', u'\u202F', u'\u205F', u'\u3000' ]

def smi2ass(smi_sgml):
    # CRLF, LF or tab to a whitespace
    smi_sgml = smi_sgml.replace(u'\u000D\u000A', u' ')
    smi_sgml = smi_sgml.replace(u'\u000A', u' ')
    smi_sgml = smi_sgml.replace(u'\u000D', u' ')
    smi_sgml = smi_sgml.replace('\t', ' ')

    # Close the <sync> tags to avoid tag recursion.
    smi_sgml = re.sub(r'</ *[Ss][Yy][Nn][Cc] *>', '', smi_sgml) # Remove </sync>
    smi_sgml = re.sub(r'< *[Ss][Yy][Nn][Cc] +', '</sync><sync ', smi_sgml) # Add </sync> right before <sync>
    
    # Replace special space characters so that BeautifulSoup can't remove them.
    for spaceChar in space_chars:
        smi_sgml = smi_sgml.replace(spaceChar, 'smi2ass_unicode(' + str(ord(spaceChar)) + ')')

    # Replace spaces around a tag with '&nbsp;' so that they are not stripped when we replace a tag.
    smi_sgml = re.sub(r'> +<', '>smi2ass_unicode(32)<', smi_sgml)
    smi_sgml = re.sub(r'> +', '>smi2ass_unicode(32)', smi_sgml)
    smi_sgml = re.sub(r' +<', 'smi2ass_unicode(32)<', smi_sgml)
    # but not <rt> tags
    smi_sgml = re.sub(r'< *[Rr][Tt] *>(smi2ass_unicode\([0-9]+\))+', '<rt>', smi_sgml)
    smi_sgml = re.sub(r'(smi2ass_unicode\([0-9]+\))+</ *[Rr][Tt] *>', '</rt>', smi_sgml)

    #Parse lines with BeautifulSoup based on sync tag
    soup = BeautifulSoup(smi_sgml, 'html.parser')
    smi_lines = soup.find_all('sync')

    #separate multi-language subtitle into a sperate list
    mln, longlang = separate_by_lang(smi_lines)
    ass_dict = {}
    for lang_idx, lang in enumerate(mln):
        ass_lines = smi2ass_internal (mln[lang])
        if len(ass_lines) > 0:
            asscontents = (script_info+styles+events+''.join(ass_lines)).encode('utf-8')
            ass_dict[longlang[lang_idx]] = asscontents

    return ass_dict

def smi2ass_internal (sln):
    parser = HTMLParser()
    ass_lines = []
    for line_idx, item in enumerate(sln):
        try: # bad cases : '<SYNC .','<SYNC Start=479501??>'
            li = sln[line_idx]['start']
            li1 = sln[line_idx+1]['start']
        except :
            #print(ml[lang][line_idx])
            li = None
            li1 = None

        if line_idx + 1 < len(sln) and not li == None and not li1 == None:
            tcstart = ms2timecode(int(re.sub(r'\..*$', '', item['start'])))
            tcend = ms2timecode(int(re.sub(r'\..*$', '', sln[line_idx+1]['start'])))

            p_tags = item.find('p')# <SYNC Start=41991><P Class=KRCC><SYNC Start=43792><P Class=KRCC>
            if not p_tags:
                continue

            br = p_tags.find_all('br')
            for gg in br:
                gg.replaceWith('\\N')

            bold = p_tags.find_all('b')
            for bo in bold:
                if len(bo.text) != 0:
                    boldre = '{\\b1}'+bo.text+'{\\b0}'
                    bo.replaceWith(boldre)
                else:
                    bo.extract()

            italics = p_tags.find_all('i')
            for it in italics:
                if len(it.text) != 0:
                    itre = '{\\i1}'+it.text+'{\\i0}'
                    it.replaceWith(itre)
                else:
                    it.extract()

            underlines = p_tags.find_all('u')
            for un in underlines:
                if len(un.text) != 0:
                    unre = '{\\u1}'+un.text+'{\\u0}'
                    un.replaceWith(unre)
                else:
                    un.extract()

            strikes = p_tags.find_all('s')
            for st in strikes:
                if len(st.text) != 0:
                    stre = '{\\s1}'+st.text+'{\\s0}'
                    st.replaceWith(stre)
                else:
                    st.extract()

            ruby_tags = p_tags.find_all('rt')
            for rt in ruby_tags:
                if len(rt.text) != 0:
                    rt_re = '{\\fscx50}{\\fscy50}&nbsp;'+rt.text+'&nbsp;{\\fscx100}{\\fscy100}'
                    rt.replaceWith(rt_re)
                else:
                    rt.extract()

            colors = p_tags.find_all('font')
            for color in colors:
                try: # bad cases : '<font size=30>'
                    col = color['color']
                except:
                    col = None
                if not col == None:
                    hexcolor = re.search('[0-9a-fA-F]{6}',color['color'].lower()) # bad cases : '23df34'
                    if hexcolor is not None:
                        converted_color = '{\\c&H' + hexcolor.group(0)[::-1]+'&}' + color.text + '{\\c}'
                    else:
                        try:
                            converted_color = '{\\c&H' + css3_names_to_hex[color['color'].lower()][::-1].replace('#','&}') + color.text + '{\\c}'
                        except: # bad cases : 'skybule'
                            converted_color = color.text
                            print('Failed to convert a color name: %s' % color['color'].lower())
                    color.replaceWith(converted_color)

            contents = p_tags.text
            contents = re.sub(r'smi2ass_unicode\(([0-9]+)\)', r'&#\1;', contents)
            contents = parser.unescape(contents)

            if len(contents.strip()) != 0:
                line = 'Dialogue: 0,%s,%s,Default,,0000,0000,0000,,%s\n' % (tcstart,tcend, contents)
                ass_lines.append(line)

    return ass_lines


def ms2timecode(ms):
    hours = int(ms / 3600000)
    ms -= hours * 3600000
    minutes = int(ms / 60000)
    ms -= minutes * 60000
    seconds = int(ms / 1000)
    ms -= seconds * 1000
    ms = round(ms/10)
    timecode = '%01d:%02d:%02d.%02d' % (hours, minutes, seconds, ms)
    return timecode


def separate_by_lang(smi_lines):
    #prepare multilanguage dict with languages separated list
    multiLanguageDict = defaultdict(list)

    #loop for number of smi subtitle lines
    for line_idx, subtitleLine in enumerate(smi_lines):
        #get time code from start tag
        try:
            timeCode = int(re.sub(r'\..*$', '', subtitleLine['start']))
        except:
            print('Failed to extract time code: %s' % subtitleLine)

        #get language name from p tag
        try:
            languageTag = subtitleLine.find('p')['class']
        except:
            print('Failed to extract language class: %s' % subtitleLine)

        # seperate langs depending on p class (language tag)
        # put smiLine,  Line Index, and time code into list (ml is dictionary (key is language name from p tag) with lists)
        try:
            multiLanguageDict[languageTag].append([subtitleLine,line_idx,timeCode])
        except: # bad cases : '<SYNC Start=7630><P>'
            try: # if no p class name, add unknown as language tag and handle later
                #languageTag = smi_lines[line_idx-1].find('p')['class']
                multiLanguageDict['unknown'].append([subtitleLine,line_idx,timeCode])
            except:
                pass

    # check whether proper multiple language subtitle
    # if one language is less than 10% of the other language,
    # it is likely that misuse of class name
    # so combine or get rid of them

    # get number of lines for each langauge and sort with number of lines
    langcodes = multiLanguageDict.keys()
    langcount=[]
    for lang in langcodes:
        langcount.append([lang, len(multiLanguageDict[lang])])
    langcount = sorted(langcount, key=itemgetter(1))

    # calculate % of each language from largest, put it in langcount
    languageTagCheckFlag = 0
    for index, lang in enumerate(langcount):
        portion = float(len(multiLanguageDict[lang[0]]))/float(langcount[len(langcount)-1][1])
        langcount[index].insert(2,float(len(multiLanguageDict[lang[0]]))/float(langcount[len(langcount)-1][1]))
        try:
            langName = langCode[langcount[index][0].upper()]
            langCnvt = 1
        except:
            langName = langcount[index][0].upper()
            langCnvt = 0
        langcount[index].insert(3,langName)
        langcount[index].insert(4,langCnvt)
        if portion < 0.1:
            langcount[index].insert(5,1)
            languageTagCheckFlag = languageTagCheckFlag +1
        else:
            langcount[index].insert(5,0)

    # if there is a language with less than 10%, only two language exist than combine them
    if languageTagCheckFlag > 0 and len(langcount) == 2:
        tempml = multiLanguageDict[langcount[0][0]]
        for tr in tempml:
            multiLanguageDict[langcount[1][0]].append(tr)
        del multiLanguageDict[langcount[0][0]]

    # covert to real language name and merge to largest
    elif languageTagCheckFlag > 1 :
        for index, langc in enumerate(langcount):
            if langc[5] == 1 and langc[4] == 1: # less than 10% and coverted to real lang name
                toBeMergedLangName = langc[3]
                # find largest one with same language name
                for lg in range(len(langcount)-1,0, -1):
                    if langcount[lg][3] == toBeMergedLangName:
                        largestSameName = lg
                        break
                # merge to largest
                tempml = multiLanguageDict[langcount[index][0]]
                for tr in tempml:
                    multiLanguageDict[langcount[largestSameName][0]].append(tr)
                del multiLanguageDict[langcount[index][0]]
            # if p language Tag is not coverted to real language name, just get rid of it.
            elif langc[5] == 1 and langc[4] == 0:
                del multiLanguageDict[langcount[index][0]]

    #good to sort based on timecode before processing
    multiLanguageDictSorted = defaultdict(list)
    for lng in multiLanguageDict:
        temp_ml = sorted(multiLanguageDict[lng], key=itemgetter(2))
        for te in temp_ml:
            multiLanguageDictSorted[lng].append(te[0])

    #covert p tag language to long language name for ASS file name
    longlang=[]
    for lang in multiLanguageDictSorted:
        if len(multiLanguageDictSorted)>1:
            try :
                if langCode[lang.upper()] in longlang:
                    longlang.append(lang)
                else:
                    longlang.append(langCode[lang.upper()])
            except:
                longlang.append(lang)
        else:
            longlang.append('')
    return multiLanguageDictSorted, longlang


for smi_path in sys.argv[1:]:
    # Open as binary and detect the encoding.
    smi_file = open(smi_path, 'rb')
    smi_encoding = chardet.detect(smi_file.read())['encoding']
    smi_file.close()

    smi_file = open(smi_path, 'r', encoding = smi_encoding, errors = 'replace')
    smi_sgml = smi_file.read()
    smi_file.close()
    ass_dict = smi2ass(smi_sgml)
    for lang in ass_dict:
        if len(lang) == 0:
            ass_path = smi_path[:smi_path.rfind('.')] + '.' + default_lang_code + '.ass'
        else:
            ass_path = smi_path[:smi_path.rfind('.')] + '.' + lang + '.ass'

        ass_file = open(ass_path, "wb")
        ass_file.write(ass_dict[lang])
        ass_file.close()
