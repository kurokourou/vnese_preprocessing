import json
import re 

def is_consonant(char):
    return (char.lower() in ['b','c','d','đ','f','g','h','j','k',
                     'l','m','n','p','q','r','s','t','v','w','x','z'])

def is_vowel(char):
    return not is_consonant(char)

def first(word, condition = lambda x: True, reverse=False): 
    ''' Trả về vị trí của ký tự nguyên âm đầu.
        Nếu reverse= True thì sẽ trả về ký tự nguyên âm cuối
    '''
    try:
        charlist = list(word)
        if reverse == True:
            charlist.reverse()
        f_c = next(x for x in charlist if condition(x))
        return charlist.index(f_c)
    except Exception:
        return None

class VowelProcessing:
    ''' Class để xử lý các nguyên âm trong các từ tiếng Việt
    '''
    def __init__(self):
        self.origin = ['a','ă','â','e','ê','i','o','ô','ơ','u','ư','y']
        self.acute = ['á','ắ','ấ','é','ế','í','ó','ố','ớ','ú','ứ','ý']
        self.grave = ['à','ằ','ầ','è','ề','ì','ò','ồ','ờ','ù','ừ','ỳ']
        self.tilde = ['ã','ẵ','ẫ','ẽ','ễ','ĩ','õ','ỗ','ỡ','ũ','ữ','ỹ']
        self.hook_above = ['ả','ẳ','ẩ','ẻ','ể','ỉ','ỏ','ổ','ở','ủ','ử','ỷ']
        self.dot_below = ['ạ','ặ','ậ','ẹ','ệ','ị','ọ','ộ','ợ','ụ','ự','ỵ']
        self.cases = [self.origin, self.acute, self.grave, self.tilde, self.hook_above, self.dot_below]
        self.diacritic = ['-', ',', '`', '~', '?', '.']

    def single_get_origin(self, svowel):
        ''' Tách các nguyên âm đơn
        Return: Nguyên âm gốc và dấu 
        '''
        for c in self.cases:
            if svowel in c:
                return self.origin[c.index(svowel)],self.diacritic[self.cases.index(c)]
            # print('%s không phải là nguyên âm đơn'%svowel)
        return None

    def single_add_diacritic(self, svowel, diacritic):
        ''' Thêm dấu vào nguyên âm đơn
        Các dấu:
        '-': Không dấu, ',': Sắc, '`': Huyền, '~': Ngã, '?': Hỏi, '.': Nặng
        '''
        if svowel in self.origin:
            if diacritic in self.diacritic:
                return self.cases[self.diacritic.index(diacritic)][self.origin.index(svowel)]
            else:
                print('Dấu %s không hợp lệ!')
                return svowel
        else:
            # print('%s không phải là nguyên âm đơn'%svowel)
            return None
    
    def add_diacritic(self, vowel, diacritic, tail=False):
        ''' Thêm dấu vào nguyên âm. Nếu sau nguyên âm có phụ âm cuối thì tail=True
        '''
        ret = []
        if len(vowel) == 1:
            return self.single_add_diacritic(vowel, diacritic)
        else:
            spec = [x for x in vowel if x in ['ă','â','ê','ơ','ư','ô']]
            # không chứa nguyên âm mũ 
            if len(spec) == 0:
                # Có phụ âm cuối 
                if tail==True or vowel in ['oa','oe','uy']:
                    _ = [ret.append(x) for x in vowel[:-1]]
                    ret.append(self.single_add_diacritic(vowel[-1], diacritic))
                # Không có phụ âm cuối
                else:
                    if len(vowel) > 2:
                        _ = [ret.append(x) for x in vowel[:-2]]
                    ret.append(self.single_add_diacritic(vowel[-2], diacritic))
                    ret.append(vowel[-1])
            # ươ 
            elif len(spec) == 2:
               for sv in vowel:
                    if sv == 'ơ':
                        ret.append(self.single_add_diacritic(sv,diacritic))
                    else:
                        ret.append(sv)
            # có 1 nguyên âm mũ    
            else:
                for sv in vowel:
                    if sv in spec:
                        ret.append(self.single_add_diacritic(sv,diacritic))
                    else:
                        ret.append(sv)
        return ''.join(ret)

    def get_origin(self, vowel):
        ''' Tách các nguyên âm (đơn/ghép) cùng dấu
        '''
        if len(vowel):
            temp =[self.single_get_origin(x) for x in vowel]
        try:
            diacritic = [x[1] for x in temp if x[1] != '-']
        except TypeError:
            # print('%s không là nguyên âm hợp lệ'%vowel)
            return None 
        origin = ''.join([x[0] for x in temp])
        if len(diacritic) :
            if len(diacritic) == 1:
                return origin,diacritic[0]
            else:
                # print('%s không là nguyên âm hợp lệ'%vowel)
                return None
        else:
            return origin,'-'

    def single_get_variations(self, svowel):
        if svowel in self.origin:
            temp_vowel = svowel
        else:
            temp_vowel = self.single_get_origin(svowel)[0]
        return [c[self.origin.index(temp_vowel)] for c in self.cases]

    def multi_get_variations(self,svowels):
        ret  = []
        for svowel in svowels:
            [ret.append(x) for x in self.single_get_variations(svowel)]
        return ret
 
class WordProcessing:
    ''' Class xử lý các token ở level từ 
    '''
    def __init__(self, dict_path='text2seq/dicts'):
        self.dict_path = dict_path
        self.standard_path = dict_path + '/vi_standard.json'
        self.foreign_path = dict_path + '/foreign_words.txt'

    def _gen_standard(self):
        ''' Sinh chuẩn 
        '''
        try:
            standard = json.load(open(self.standard_path,'r',encoding='utf-8'))
            self.standard_heads = standard['head']
            self.standard_vowels = standard['vowel']
            self.standard_tails = standard['tail'] 
        except FileNotFoundError:
            print('File %s not found! '% self.standard_path)
            return None

    def is_standard(self, word):
        ''' Kiểm tra xem từ đầu vào có theo chuẩn cấu trúc C-V-C 
        '''
        if not hasattr(self, 'standard_heads'):
            self._gen_standard()
        word = word.strip().lower()
        try:
            ret = self.vc_separate(word)
            if ret['head'] not in self.standard_heads:
                return False
            if ret['vowel'] not in self.standard_vowels:
                return False
            if ret['tail'] not in self.standard_tails:
                return False 
            return True
        except TypeError:
            return False

    def _gen_foreign_dict(self):
        try:
            lines = open(self.foreign_path,'r',encoding='utf-8')
            self.foreign_words = {}
            for line in lines:
                word, read = line.split('|')
                self.foreign_words[word.strip()] = read.strip()
        except FileNotFoundError:
            print('File %s not found! '% self.standard_path)
            return None

    def is_foreign_word(self, word):
        ''' Kiểm tra trong từ có trong danh sách 
            từ ngoại lai không
        '''
        if not hasattr(self, 'foreign_words'):
            self._gen_foreign_dict()
        return (word.lower() in self.foreign_words.keys())
        
    @staticmethod
    def clean(word):
        if not word.isalpha():
            return ''.join([x for x in list(word) if x.isalpha()])
        else:
            return word

    @staticmethod
    def is_acronym(word):
        ''' Kiểm tra từ đầu vào có phải là từ viết tắt không 
        '''
        return re.match(r"\b[A-Z0-9]{2,}\b", word) is not None 
    
    @staticmethod
    def is_symbol(char):
        punctuations = [',','.',';',"'",'"',':']
        symbols = ['$','#','@','~']
        return (char in punctuations) or (char in symbols)

    def vc_separate(self, word):
        ''' Tách các từ theo chuẩn kết cấu tiếng Việt thành các
        nguyên âm và phụ âm  
        Return: Dict{ 'head': phụ_âm_đầu,'vowel': nguyên_âm,'tail': phụ_âm_cuối,
        'diacritic': dấu_câu}
        '''
        ret = {}
        word = word.strip()
        if len(word) != 0:
            try:
                first_vowel = first(word,is_vowel)
                ret['head'] = word[:first_vowel]
                last_vowel = len(word) - first(word,is_vowel,True) - 1
                ret['vowel'] = word[first_vowel:(last_vowel+1)]
                ret['tail'] = word[(last_vowel+1):]
                return ret
            except TypeError:
                return None

    # Undone
    def encode(self, input_word):
        ''' Phân tách từ thành các âm tiết để phát âm
        '''
        # word = self.clean(input_word)
        word = input_word.strip()
        ret = []
        # Từ chuẩn CVC
        if self.is_standard(word):
            vp = VowelProcessing()
            vowel = ''
            if word == 'gì':
                return ['gi','ì']
            if len(word) != 0:
                first_vowel = 2
                # Phụ âm đầu 'gi'
                if 'gi' in word:
                    head = 'gi'
                    if word[2] in vp.single_get_variations('ê'):
                        vowel = 'i'
                # Phụ âm đầu 'qu'
                elif 'qu' in word:
                    head = 'qu'
                    # + o 
                    if word[2] in vp.multi_get_variations(['a','ă','â','e']):
                        vowel = 'o' 
                    else: # + u
                        vowel = 'u'
                else:
                    first_vowel = first(word,is_vowel)
                    head = word[:first_vowel]
                last_vowel = len(word) - first(word,is_vowel,True) - 1
                vowel += word[first_vowel:(last_vowel+1)]
                tail = word[(last_vowel+1):]
                if head : ret.append(head)
                ret.append(vowel)
                if tail: ret.append(tail)
        # Từ ngoại lai
        elif self.is_foreign_word(word):
            words = self.foreign_words[word].split()
            for word in words:
                [ret.append(x) for x in self.encode(word)]
        return ret

# Số 
class NumberProcessing:
    ''' Đọc số 
    '''
    def __init__(self):
        self.digits = ['0','1','2','3','4','5','6','7','8','9']
        self.reads = ['không','một','hai','ba','bốn','năm','sáu','bảy','tám','chín']
        self.stack = ['','nghìn','triệu']
        self.wp = WordProcessing()
    
    @staticmethod
    def is_number(number):
        return number.strip().isdigit()
    
    @staticmethod
    def number_clean(number,clear_head=True):
        if number.isdigit():
            temp = number 
        else:
            temp = ''.join([x for x in list(number) if x.isdigit()])
        if clear_head:
            return str(int(temp))
        else:
            return temp
    
    # Đọc số 
    def read_digit(self, digit):
        if digit in self.digits:
            return self.reads[self.digits.index(digit)]
        else:
            print('%s không hợp lệ')
            return None 
    
    def normal(self, number):
        ''' Đọc số theo cách thường 
        '''        
        nums = list(self.number_clean(number,False))
        return ' '.join([self.read_digit(x) for x in nums])

    def three(self, number):
        ret = []
        if len(number) == 3:
            if number != '000':
                ret.append(self.read_digit(number[0]))
                ret.append('trăm')
                if number[1:] != '00':
                    [ret.append(x) for x in self.two(number[1:])]
        elif len(number) < 3:
            return self.two(number)
        return ret 

    def two(self, number):
        ret = []
        try: # number != ''
            if int(number) != 0:
                if len(number)== 2:
                    # Chữ số đầu 
                    if number[0] == '0':
                        ret.append('linh')
                    elif number[0] == '1':
                        ret.append('mười')
                    else:
                        ret.append(self.read_digit(number[0]))
                        ret.append('mươi')
                    # Chữ số cuối 
                    if number[1] == '1':
                        if int(number[0]) > 1:
                            ret.append('mốt')
                        else:
                            ret.append('một')
                    elif number[1] == '4':
                        if int(number[0]) > 1:
                            ret.append('tư')
                        else:
                            ret.append('bốn')
                    elif number[1] == '5':
                        if int(number[0]) > 0:
                            ret.append('lăm')
                        else:
                            ret.append('năm')
                    elif number[1] == '0':
                        pass
                    else:
                        ret.append(self.read_digit(number[1]))  
                else:
                    ret.append(self.read_digit(number))
        except Exception:
            pass
        return ret    
    
    def ubillion(self, number):
        ''' Đọc các số dưới 1 tỷ 
        '''  
        temp = self.number_clean(number)
        ret = []
        if len(temp) < 10:
            residual = len(temp)%3
            times = int(len(temp)/3)
            stacks = [temp[len(temp)-(i+1)*3:len(temp)-i*3] for i in range(times)]
            if residual:
                stacks.append(temp[:residual])
                times += 1
        while(times > 0):
            [ret.append(x) for x in self.three(stacks[times-1])]
            if times > 1 and int(stacks[times-1])!=0:
                ret.append(self.stack[times-1])
            times -= 1    
        return ret 

    def read(self, number):
        ''' Đọc theo cách chia thành cụm 3 chữ số 
        '''
        temp = self.number_clean(number)
        ret = []
        if len(temp) < 10:
            return self.ubillion(number)
        elif len(temp) in range(10,29):
            residual = len(temp)%9
            times = int(len(temp)/9)
            stacks = [temp[len(temp)-(i+1)*9:len(temp)-i*9] for i in range(times)]
            if residual:
                stacks.append(temp[:residual])
                times += 1
            while(times > 0):
                [ret.append(x) for x in self.ubillion(stacks[times-1])]
                if times > 1:
                    ret.append(' '.join(['tỷ']*(times-1)))
                times -= 1  
        else:
            print('Số to quá đọc không nổi ...')
              
        return ret 
    
    def encode(self, number):
        ''' Encode số đầu vào thành từng âm tiết 
        ''' 
        ret = []
        seps = self.read(number)
        for word in seps:
            [ret.append(x) for x in self.wp.encode(word)]
            ret.append('[sp]')
        del ret[-1]
        return ret

# TODO: Datetime
# class DateTime():

class Sentence:
    ''' Class xử lý câu đầu vào 
    '''
    def __init__(self):
         self.word_processer = WordProcessing()
         self.number_processer = NumberProcessing()

    def encode(self, sentence):
        ret = ["[cls]"]
        words = sentence.lower().split()
        for word in words:
            processer = self.number_processer if self.number_processer.is_number(word) else self.word_processer
            [ret.append('[%s]'%x) for x in processer.encode(word)]
            ret.append('[sp]')
        del ret[-1]
        return ret
       
    def check_all(self, sentences):
        ''' Kiểm tra tất cả các câu đầu vào 
        '''
        i = 1
        hav_prob = {}
        for sentence in sentences:
            try: 
                self.encode(sentence)
                i += 1 
            except Exception:
                hav_prob[i] = [Exception.__name__, sentence]
        print('Checking Done!')
        print('Problem: %s senteces'%len(hav_prob.keys()))
        _ = [print('%s %s \n %s\n'%(x, hav_prob[x][0], hav_prob[x][1])) for x in hav_prob.keys()]

    def get_all_nonstandard(self, sentences):
        ''' Lấy ra danh sách tất cả các từ phi chuẩn 
        '''   
        non_standards = {}
        for sentence in sentences:
            words = sentence.lower().split()
            for word in words:
                # Không phải là số
                if not self.number_processer.is_number(word):
                    if not self.word_processer.is_standard(word):
                        if not self.word_processer.is_foreign_word(word):
                            if not self.word_processer.is_acronym(word):
                                if not self.word_processer.is_symbol(word):
                                    non_standards[word] = [sentences.index(sentence), words.index(word)]
        return non_standards