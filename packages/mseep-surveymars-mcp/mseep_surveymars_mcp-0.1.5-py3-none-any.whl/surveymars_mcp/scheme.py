import enum


class SurveyType(enum.Enum):
    Survey = 1, 'Survey', '调查'
    # Vote = 2, 'Vote', '投票'
    E360 = 3, '360-Degree Evaluation', '360度评估'
    Form = 4, 'Form', '表单'
    FormActivity = 5, 'FormActivity', '活动报名'
    FormSign = 6, 'FormSign', '报名签到'

    def __init__(self, value, en_name, cn_name):
        self._value = value
        self._en_name = en_name
        self._cn_name = cn_name

    @property
    def value(self):
        return self._value

    @property
    def en_name(self):
        return self._en_name

    @property
    def cn_name(self):
        return self._cn_name


class LocalizeLanguage(enum.Enum):
    ChineseSimplified = 1, 'ChineseSimplified', '简体中文'
    English = 2, 'English', '英语'
    ChineseTraditional = 3, 'ChineseTraditional', '繁体中文'
    # Japanese = 4, 'Japanese', '日本语'
    # Korean = 5, 'Korean', '韩语'
    # Arabic = 6, 'Arabic', '阿拉伯语'
    # French = 7, 'French', '法语'
    # German = 8, 'German', '德语'
    # Spanish = 9, 'Spanish', '西班牙语'
    # Portuguese = 10, 'Portuguese', '葡萄牙语'
    # Italian = 11, 'Italian', '意大利语'
    # Russian = 12, 'Russian', '俄语'
    # Thai = 13, 'Thai', '泰语'
    # Turkish = 14, 'Turkish', '土耳其语'
    # Indonesian = 15, 'Indonesian', '印尼语'
    # Vietnamese = 16, 'Vietnamese', '越南语'
    # Polish = 17, 'Polish', '波兰语'
    # Dutch = 18, 'Dutch', '荷兰语'
    # Hindi = 19, 'Hindi', '印地语'
    # Irish = 20, 'Irish', '爱尔兰语'
    # Bengali = 21, 'Bengali', '孟加拉语'
    # Hebrew = 22, 'Hebrew', '希伯来语'
    # Swedish = 23, 'Swedish', '瑞典语'
    # Ukrainian = 24, 'Ukrainian', '乌克兰语'
    # Czech = 26, 'Czech', '捷克语'
    # Danish = 27, 'Danish', '丹麦语'
    # Finnish = 28, 'Finnish', '芬兰语'
    # Hungarian = 29, 'Hungarian', '匈牙利语'
    # Malay = 30, 'Malay', '马来语'
    # Norwegian = 31, 'Norwegian', '挪威语'
    # Romanian = 32, 'Romanian', '罗马尼亚语'
    # Serbian = 33, 'Serbian', '塞尔维亚语'
    # Slovak = 34, 'Slovak', '斯洛伐克语'
    # Slovenian = 35, 'Slovenian', '斯洛文尼亚语'
    # Filipino = 36, 'Filipino', '菲律宾语'
    # Lithuanian = 37, 'Lithuanian', '立陶宛语'
    # Latvian = 38, 'Latvian', '拉脱维亚语'
    # Odia = 39, 'Odia', '奥利亚语'
    # Macedonian = 40, 'Macedonian', '马其顿语'
    # Malagasy = 41, 'Malagasy', '马尔加什语'
    # Nepali = 42, 'Nepali', '尼泊尔语'
    # Malayalam = 43, 'Malayalam', '马拉雅拉姆语'
    # Maltese = 44, 'Maltese', '马耳他语'
    # Maori = 45, 'Maori', '毛利语'
    # Marathi = 46, 'Marathi', '马拉地语'
    # Mongolian = 47, 'Mongolian', '蒙古语'
    # Burmese = 48, 'Burmese', '缅甸语'
    # Greek = 49, 'Greek', '希腊语'

    def __init__(self, value, en_name, cn_name):
        self._value = value
        self._en_name = en_name
        self._cn_name = cn_name

    @property
    def value(self):
        return self._value

    @property
    def en_name(self):
        return self._en_name

    @property
    def cn_name(self):
        return self._cn_name

SurveyTypeStr = '\n'.join([f'{member.value}: {member.en_name} {member.cn_name}' for _, member in SurveyType.__members__.items()])

LocalizeLanguageStr = '\n'.join([f'{member.value}: {member.en_name} {member.cn_name}' for _, member in LocalizeLanguage.__members__.items()])

if __name__ == '__main__':
    # print(JobStatus.Created)
    # print(JobStatus.Created.name)
    # print(JobStatus.Created.value)

    # print(SurveyType.E360.en_name)
    # print(SurveyType.E360.cn_name)

    # for name, member in SurveyType.__members__.items():
    #     print(name, member.value, member.en_name, member.cn_name)

    # print(SurveyTypeStr)
    print(LocalizeLanguageStr)