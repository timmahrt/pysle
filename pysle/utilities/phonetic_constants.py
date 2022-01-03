# encoding: utf-8

STRESS_BEARING_CONSONANTS = ["r", "m", "n", "l"]
TONIC = "T"
VOWEL = "V"

FILLER = "''"

unvoiced = [
    u"f",
    u"k",
    u"p",
    u"t",
    u"s",
    u"tʃ",
    u"ɵ",
]

alveolars = [
    u"s",
    u"z",
    u"tʃ",
    u"dʒ",
]

charList = [
    u"#",
    u".",
    u"aʊ",
    u"b",
    u"d",
    u"dʒ",
    u"ei",
    u"f",
    u"g",
    u"h",
    u"i",
    u"j",
    u"k",
    u"l",
    u"m",
    u"n",
    u"oʊ",
    u"p",
    u"r",
    u"s",
    u"t",
    u"tʃ",
    u"u",
    u"v",
    u"w",
    u"z",
    u"æ",
    u"ð",
    u"ŋ",
    u"ɑ",
    u"ɑɪ",
    u"ɔ",
    u"ɔi",
    u"ə",
    u"ɚ",
    u"ɛ",
    u"ɝ",
    u"ɪ",
    u"ɵ",
    u"ɹ",
    u"ʃ",
    u"ʊ",
    u"ʒ",
    u"æ",
    u"ʌ",
]

diacriticList = [
    u"˺",
    u"ˌ",
    u"̩",
    u"̃",
    u"ˈ",
]

monophthongList = [
    u"u",
    u"æ",
    u"ɑ",
    u"ɔ",
    u"ə",
    u"i",
    u"ɛ",
    u"ɪ",
    u"ʊ",
    u"ʌ",
    u"a",
    u"e",
    u"o",
]

diphthongList = [u"ɑɪ", u"aʊ", u"ei", u"ɔi", u"oʊ", u"ae"]

syllabicConsonantList = [u"l̩", u"n̩", u"ɚ", u"ɝ"]

# ISLE words are part of speech tagged using the Penn Part of Speech Tagset
posList = [
    "cc",
    "cd",
    "dt",
    "fw",
    "in",
    "jj",
    "jjr",
    "jjs",
    "ls",
    "md",
    "nn",
    "nnd",
    "nnp",
    "nnps",
    "nns",
    "pdt",
    "prp",
    "punc",
    "rb",
    "rbr",
    "rbs",
    "rp",
    "sym",
    "to",
    "uh",
    "vb",
    "vbd",
    "vbg",
    "vbn",
    "vbp",
    "vbz",
    "vpb",
    "wdt",
    "wp",
    "wrb",
]

vowelList = monophthongList + diphthongList + syllabicConsonantList
rhotics = ["r", "ɹ", "ɾ"]
