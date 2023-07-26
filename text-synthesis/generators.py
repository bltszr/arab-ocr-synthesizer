import random
import numpy as np
import re

class Generator:
  def __init__(self):
    pass
  def generate(self):
    raise NotImplementedError

class NumberGenerator(Generator):
  def __init__(self):
    self.alphabet = list('١٢٣٤٥٦٧٨٩٠ ')
  def generate(self):
    return random.choice(self.alphabet)

class PegonJawaGenerator(Generator):
  sukun = 'ْ'
  def __init__(self, pepet=None, prefix_prob=0.1, suffix_prob=0.1,
               full_stop_prob=0.01, newline_prob=0.025, comma_prob=0.05,
               full_stop='.', comma='،', p=None, dh=None, g=None):
    self.pepet = pepet if pepet != None else random.choice(['ࣤ', 'ٓ'])
    self.p = p if p != None else random.choice(['ف', 'ڤ'])
    self.dh = dh if dh != None else random.choice(['ڎ', 'ڊ', 'ࢮ'])
    self.g = g if g != None else random.choice(['ࢴ', 'ڮ'])
    self.comma_prob = comma_prob
    self.prefix_prob = prefix_prob
    self.suffix_prob = suffix_prob
    self.full_stop_prob = full_stop_prob
    self.newline_prob = newline_prob
    self.full_stop = full_stop
    self.comma = comma
    self.par_delimiter = '.\n\n'
    
    self.rng = np.random.default_rng()
    self.consonants = [
      'ب',
      'ت',
      'ث',
      'ج',
      'چ',
      'ح',
      'خ',
      'د',
      self.dh,
      'ر',
      'ز',
      'س',
      'ش',
      'ص',
      'ض',
      'ط',
      'ڟ',
      'ظ',
      'ع',
      'غ',
      'ڠ',
      self.p,
      'ق',
      'ك',
      self.g,
      'ل',
      'م',
      'ن',
      'ۑ',
      'و',
      'ۏ',
      'ه',
      # 'ء',
      'ي'
    ]
    
    """
    1) homorganic (nasal + plosive) --> [mp, mb, mw?, nt, nd, nyc?, nyj?, ngk, ngg]
    2) any plosive + liquid/semivowel --> [p, b, t, d, th, dh, c, j, k, g] x [l, r, y]
    3) homorganic (nasal + liquid/semivowel) --> [nl, nr]
    """
    plosives = [self.p, 'ب', 'ت', 'د', 'ڟ', self.dh, 'چ', 'ج', 'ك', self.g]
    liquids_semivowels = ['ر', 'ل', 'ي']
    self.consonant_clusters = [
      'مْ' + self.p,
      'مْب',
      'نْت',
      'نْد',
      'ڠْك',
      'ڠْ' + self.g,
      'نْل',
      'نْر',
    ] + np.array([[f'{p}{self.sukun}{ls}' for ls in liquids_semivowels] for p in plosives]).flatten().tolist()
    self.short_vowels = [
      'َ',
      'ِ',
      'ُ',
      'َو',
      'َي',
      self.pepet
    ]
    self.long_vowels = [
      'َا',
      'ِي',
      'ُو',
      'َو',
      'َي',
      self.pepet
    ]
    self.vowels = list(set(self.short_vowels + self.long_vowels))
    
    self.initial_vowels = [
      'أ',
      'اَ',
      'إ',
      'اِ',
      'إي',
      'اِي',
      'اُو',
      'اَي',
      'اَو',
      'ا' + self.pepet,
    ]
    
    self.mutating_prefix = {
      self.p: 'م',
      'ت': 'ن',
      'چ': 'ي',
      'س': 'ي',
    }
    self.hanuswara_prefixes = [
      'م',
      'ن',
      'ي',
      'ڠ',
    ]
    self.mutating_vowel_prefix = {
      'ا': 'َ',
      'إ': 'ِ',
      'أُ': 'ُ',
    }

    self.liyane_prefixes = [
      'مَ',
      'كَ',
      'ك' + self.pepet,
      'سَ',
      self.p + 'َ',
      self.p + self.sukun + 'ر',
      'كُمَ',
      'كَمِ',
      'كَ' + self.p + 'ِ',
      'تَر'
    ]

    self.panambang_suffixes = [
      'ا',
      'ءَكَيْ',
      'ءَيْ',
      'مُ',
      'نَا',
    ]
    
    self.panambang_vowel_suffixes = [
      self.pepet + 'نْ'
      'ِيْ',
      'َنَا',
    ]
    
  def hanuswara(self, word):
    try:
      return self.mutating_prefix[word[0]] + word[1:]
    except KeyError:
      pass
    try:
      return self.rng.choice(self.hanuswara_prefixes) + self.mutating_vowel_prefix[word[0]] + word[1:]
    except KeyError:
      pass
    return random.choice(self.hanuswara_prefixes) + self.sukun + word
  def tripurasa(self, word):
    return random.choice(['دَكْ', 'دِ']) + word
  def liyane(self, word):
    return random.choice(self.liyane_prefixes) + word

  def panambang(self, word):
    return word + random.choice(self.panambang_vowel_suffixes)
    
  def panambang_vowel(self, word):
    suffix = random.choice(self.panambang_vowel_suffixes)
    if word.endswith(self.sukun):
      return word[:-1] + suffix
    else:
      return word + suffix

  def prefix(self, word):
    return (self.rng.choice((self.hanuswara,self.tripurasa,self.liyane), 1,
                            p=(0.3, 0.05, 0.65)).item())(word)
  def suffix(self, word):
    return (self.rng.choice((self.panambang,self.panambang_vowel), 1,
                            p=(5/8, 3/8)).item())(word)
    
  def _generate_csvc(self):
    cs = random.choice(self.consonant_clusters)
    v = random.choice(self.vowels)
    c2 = random.choice(self.consonants)
    return f'{cs}{v}{c2}{self.sukun}'
    
  def _generate_csv(self):
    cs = random.choice(self.consonant_clusters)
    v = random.choice(self.long_vowels)
    return f'{cs}{v}{self.sukun}'
    
  def _generate_cvc(self):
    c1 = random.choice(self.consonants)
    v = random.choice(self.vowels)
    c2 = random.choice(self.consonants)
    return f'{c1}{v}{c2}{self.sukun}'
    
  def _generate_cv(self):
    c = random.choice(self.consonants)
    v = random.choice(self.long_vowels)
    return f'{c}{v}{self.sukun}'

  def _generate_vc(self):
    c = random.choice(self.consonants)
    v = random.choice(self.initial_vowels)
    return f'{v}{c}{self.sukun}'
  
  def _generate_v(self):
    v = random.choice(self.initial_vowels)
    return f'{v}{self.sukun if v.endswith("و") or v.endswith("ي") else ""}'
    
  def generate(self):    
    num_syllables = self.rng.choice([1, 2, 3], 1,
                                    p=(0.1, 0.85, 0.05)).item()
    word = ''
    for syll in range(num_syllables):
      word += self.rng.choice([
        self._generate_csvc,
        self._generate_csv,
        self._generate_cv,
        self._generate_cvc,
        self._generate_vc,
        self._generate_v
      ], 1, p=[0.05, 0.1, 0.2, 0.5, 0.1, 0.05]).item()()
    for pattern, result in [
      # ('َاَ', 'َااَ'), # this might not be possible to achieve anyway
      ('َاَيْ', 'َائَيْ'),
      ('َا' + self.pepet, 'َاا' + self.pepet),
      ('َ(اِ|إ)(ي)?', 'َائِي'),
      # ('َاَو', 'َاَو'),
      ('َيْا', 'َيْئَا'),
      ('َيْاَو', 'َيْئَو'),
      ('َيْاُو', 'َيْئُو'),
      (self.pepet + '(اِ|إ)(ي)?', self.pepet + 'ئِي'),
      ('ِيْ(اَ|أ)', 'ِيَْا'),
      ('ِيْ(اِ|إ)', 'ِيْئِي'),
      ('ِيْاَو', 'ِيْئَو'),
      ('َوْ(اَ|أ)', 'َوْوَا'),
      ('ُوْ(اَ|أ)', 'ُوْوَا'),
      ('ُوْاُو', 'ُؤُوْ'),
      # ('', ''),
    ]:
      word = re.sub(pattern, result, word)
    if random.random() < self.prefix_prob:
      word = self.prefix(word)
    if random.random() < self.suffix_prob:
      word = self.suffix(word)

    if random.random() < self.full_stop_prob:
      return word + self.full_stop
    elif random.random() < self.newline_prob:
      return word + self.par_delimiter
    elif random.random() < self.comma_prob:
      return word + self.comma
    else:
      return word
