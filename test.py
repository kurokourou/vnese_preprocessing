from text2seq import processing as p

s = p.Sentence()
sentences = ['chỉ bằng cách luôn nỗ lực thì cuối cùng bạn mới được đền đáp',
             'các bàn học nhỏ hằng ngày nay trở thành bàn thờ của các cháu',
             ' Hôm nay là thứ tư ngày 24 tháng 7 năm 2019',
             'abc12jsd',
             'Electrolux',
             ]

# Encode thử 1 câu 
# print(s.encode(sentences[-1]))

# Kiểm tra các câu đầu vào có thể encode không 
s.check_all(sentences)

# Lấy danh sách các từ phi chuẩn :
# non_standards = s.get_all_nonstandard(sentences)
# print('word           |line|number')
# print('------------------------')
# for x in non_standards.keys():
#     print('%15s|%4d|%6d'%(x,non_standards[x][0],non_standards[x][1]))

# Kiểm tra từ điển ngoại lai
# w = p.WordProcessing()
# w._gen_foreign_dict()
# print(w.foreign_words.keys())
# print(w.is_foreign_word('alphabet'))
# print(w.is_foreign_word('AlpHabEt'))
# print(w.is_foreign_word('hercules'))