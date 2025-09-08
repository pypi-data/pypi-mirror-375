
import datetime

# 引入MyLunar类，来自github的HiGavin/Lunar开源项目，未实现农历到阳历的转化，也没有起运时间的计算，待后续完善
class MyLunar(object):
    # ******************************************************************************
    # 下面为阴历计算所需的数据,为节省存储空间,所以采用下面比较变态的存储方法.
    # ******************************************************************************
    # 数组g_lunar_month_day存入阴历1901年到2050年每年中的月天数信息，
    # 阴历每月只能是29或30天，一年用12（或13）个二进制位表示，对应位为1表30天，否则为29天
    g_lunar_month_day = [
        0x4ae0, 0xa570, 0x5268, 0xd260, 0xd950, 0x6aa8, 0x56a0, 0x9ad0, 0x4ae8, 0x4ae0,  # 1910
        0xa4d8, 0xa4d0, 0xd250, 0xd548, 0xb550, 0x56a0, 0x96d0, 0x95b0, 0x49b8, 0x49b0,  # 1920
        0xa4b0, 0xb258, 0x6a50, 0x6d40, 0xada8, 0x2b60, 0x9570, 0x4978, 0x4970, 0x64b0,  # 1930
        0xd4a0, 0xea50, 0x6d48, 0x5ad0, 0x2b60, 0x9370, 0x92e0, 0xc968, 0xc950, 0xd4a0,  # 1940
        0xda50, 0xb550, 0x56a0, 0xaad8, 0x25d0, 0x92d0, 0xc958, 0xa950, 0xb4a8, 0x6ca0,  # 1950
        0xb550, 0x55a8, 0x4da0, 0xa5b0, 0x52b8, 0x52b0, 0xa950, 0xe950, 0x6aa0, 0xad50,  # 1960
        0xab50, 0x4b60, 0xa570, 0xa570, 0x5260, 0xe930, 0xd950, 0x5aa8, 0x56a0, 0x96d0,  # 1970
        0x4ae8, 0x4ad0, 0xa4d0, 0xd268, 0xd250, 0xd528, 0xb540, 0xb6a0, 0x96d0, 0x95b0,  # 1980
        0x49b0, 0xa4b8, 0xa4b0, 0xb258, 0x6a50, 0x6d40, 0xada0, 0xab60, 0x9370, 0x4978,  # 1990
        0x4970, 0x64b0, 0x6a50, 0xea50, 0x6b28, 0x5ac0, 0xab60, 0x9368, 0x92e0, 0xc960,  # 2000
        0xd4a8, 0xd4a0, 0xda50, 0x5aa8, 0x56a0, 0xaad8, 0x25d0, 0x92d0, 0xc958, 0xa950,  # 2010
        0xb4a0, 0xb550, 0xb550, 0x55a8, 0x4ba0, 0xa5b0, 0x52b8, 0x52b0, 0xa930, 0x74a8,  # 2020
        0x6aa0, 0xad50, 0x4da8, 0x4b60, 0x9570, 0xa4e0, 0xd260, 0xe930, 0xd530, 0x5aa0,  # 2030
        0x6b50, 0x96d0, 0x4ae8, 0x4ad0, 0xa4d0, 0xd258, 0xd250, 0xd520, 0xdaa0, 0xb5a0,  # 2040
        0x56d0, 0x4ad8, 0x49b0, 0xa4b8, 0xa4b0, 0xaa50, 0xb528, 0x6d20, 0xada0, 0x55b0,  # 2050
    ]

    # 数组gLanarMonth存放阴历1901年到2050年闰月的月份，如没有则为0，每字节存两年
    g_lunar_month = [
        0x00, 0x50, 0x04, 0x00, 0x20,  # 1910
        0x60, 0x05, 0x00, 0x20, 0x70,  # 1920
        0x05, 0x00, 0x40, 0x02, 0x06,  # 1930
        0x00, 0x50, 0x03, 0x07, 0x00,  # 1940
        0x60, 0x04, 0x00, 0x20, 0x70,  # 1950
        0x05, 0x00, 0x30, 0x80, 0x06,  # 1960
        0x00, 0x40, 0x03, 0x07, 0x00,  # 1970
        0x50, 0x04, 0x08, 0x00, 0x60,  # 1980
        0x04, 0x0a, 0x00, 0x60, 0x05,  # 1990
        0x00, 0x30, 0x80, 0x05, 0x00,  # 2000
        0x40, 0x02, 0x07, 0x00, 0x50,  # 2010
        0x04, 0x09, 0x00, 0x60, 0x04,  # 2020
        0x00, 0x20, 0x60, 0x05, 0x00,  # 2030
        0x30, 0xb0, 0x06, 0x00, 0x50,  # 2040
        0x02, 0x07, 0x00, 0x50, 0x03  # 2050
    ]

    CHINESEYEARCODE = [
        19416,
        19168,  42352,  21717,  53856,  55632,  91476,  22176,  39632,
        21970,  19168,  42422,  42192,  53840, 119381,  46400,  54944,
        44450,  38320,  84343,  18800,  42160,  46261,  27216,  27968,
        109396,  11104,  38256,  21234,  18800,  25958,  54432,  59984,
        92821,  23248,  11104, 100067,  37600, 116951,  51536,  54432,
        120998,  46416,  22176, 107956,   9680,  37584,  53938,  43344,
        46423,  27808,  46416,  86869,  19872,  42416,  83315,  21168,
        43432,  59728,  27296,  44710,  43856,  19296,  43748,  42352,
        21088,  62051,  55632,  23383,  22176,  38608,  19925,  19152,
        42192,  54484,  53840,  54616,  46400,  46752, 103846,  38320,
        18864,  43380,  42160,  45690,  27216,  27968,  44870,  43872,
        38256,  19189,  18800,  25776,  29859,  59984,  27480,  23232,
        43872,  38613,  37600,  51552,  55636,  54432,  55888,  30034,
        22176,  43959,   9680,  37584,  51893,  43344,  46240,  47780,
        44368,  21977,  19360,  42416,  86390,  21168,  43312,  31060,
        27296,  44368,  23378,  19296,  42726,  42208,  53856,  60005,
        54576,  23200,  30371,  38608,  19195,  19152,  42192, 118966,
        53840,  54560,  56645,  46496,  22224,  21938,  18864,  42359,
        42160,  43600, 111189,  27936,  44448,  84835,  37744,  18936,
        18800,  25776,  92326,  59984,  27296, 108228,  43744,  37600,
        53987,  51552,  54615,  54432,  55888,  23893,  22176,  42704,
        21972,  21200,  43448,  43344,  46240,  46758,  44368,  21920,
        43940,  42416,  21168,  45683,  26928,  29495,  27296,  44368,
        84821,  19296,  42352,  21732,  53600,  59752,  54560,  55968,
        92838,  22224,  19168,  43476,  41680,  53584,  62034,  54560
    ]

    CHINESENEWYEAR = [
        '19000131',
        '19010219', '19020208', '19030129', '19040216', '19050204',
        '19060125', '19070213', '19080202', '19090122', '19100210',
        '19110130', '19120218', '19130206', '19140126', '19150214',
        '19160203', '19170123', '19180211', '19190201', '19200220',
        '19210208', '19220128', '19230216', '19240205', '19250124',
        '19260213', '19270202', '19280123', '19290210', '19300130',
        '19310217', '19320206', '19330126', '19340214', '19350204',
        '19360124', '19370211', '19380131', '19390219', '19400208',
        '19410127', '19420215', '19430205', '19440125', '19450213',
        '19460202', '19470122', '19480210', '19490129', '19500217',
        '19510206', '19520127', '19530214', '19540203', '19550124',
        '19560212', '19570131', '19580218', '19590208', '19600128',
        '19610215', '19620205', '19630125', '19640213', '19650202',
        '19660121', '19670209', '19680130', '19690217', '19700206',
        '19710127', '19720215', '19730203', '19740123', '19750211',
        '19760131', '19770218', '19780207', '19790128', '19800216',
        '19810205', '19820125', '19830213', '19840202', '19850220',
        '19860209', '19870129', '19880217', '19890206', '19900127',
        '19910215', '19920204', '19930123', '19940210', '19950131',
        '19960219', '19970207', '19980128', '19990216', '20000205',
        '20010124', '20020212', '20030201', '20040122', '20050209',
        '20060129', '20070218', '20080207', '20090126', '20100214',
        '20110203', '20120123', '20130210', '20140131', '20150219',
        '20160208', '20170128', '20180216', '20190205', '20200125',
        '20210212', '20220201', '20230122', '20240210', '20250129',
        '20260217', '20270206', '20280126', '20290213', '20300203',
        '20310123', '20320211', '20330131', '20340219', '20350208',
        '20360128', '20370215', '20380204', '20390124', '20400212',
        '20410201', '20420122', '20430210', '20440130', '20450217',
        '20460206', '20470126', '20480214', '20490202', '20500123',
        '20510211', '20520201', '20530219', '20540208', '20550128',
        '20560215', '20570204', '20580124', '20590212', '20600202',
        '20610121', '20620209', '20630129', '20640217', '20650205',
        '20660126', '20670214', '20680203', '20690123', '20700211',
        '20710131', '20720219', '20730207', '20740127', '20750215',
        '20760205', '20770124', '20780212', '20790202', '20800122',
        '20810209', '20820129', '20830217', '20840206', '20850126',
        '20860214', '20870203', '20880124', '20890210', '20900130',
        '20910218', '20920207', '20930127', '20940215', '20950205',
        '20960125', '20970212', '20980201', '20990121', '21000209'
    ]

    START_YEAR = 1901

    # 天干
    gan = '甲乙丙丁戊己庚辛壬癸'
    # 地支
    zhi = '子丑寅卯辰巳午未申酉戌亥'
    # 生肖
    xiao = '鼠牛虎兔龙蛇马羊猴鸡狗猪'
    # 月份
    lm = '正二三四五六七八九十冬腊'
    # 日份
    ld = '初一初二初三初四初五初六初七初八初九初十十一十二十三十四十五十六十七十八十九二十廿一廿二廿三廿四廿五廿六廿七廿八廿九三十'
    # 节气
    jie = '小寒大寒立春雨水惊蛰春分清明谷雨立夏小满芒种夏至小暑大暑立秋处暑白露秋分寒露霜降立冬小雪大雪冬至'
    # 节气划分农历干支月
    jie_qi_odd = "立春惊蛰清明立夏芒种小暑立秋白露寒露立冬大雪小寒"  # 节气节点，如立春-惊蛰是正月，两个节气一个月
    # 节气对应农历干支月
    jie_qi_month = {
        "立春": [0, "寅"],
        "惊蛰": [1, "卯"],
        "清明": [2, "辰"],
        "立夏": [3, "巳"],
        "芒种": [4, "午"],
        "小暑": [5, "未"],
        "立秋": [6, "申"],
        "白露": [7, "酉"],
        "寒露": [8, "戌"],
        "立冬": [9, "亥"],
        "大雪": [10, "子"],
        "小寒": [11, "丑"],
    }
    gz_wu_xing = {
        '甲': '木',
        '乙': '木',
        '丙': '火',
        '丁': '火',
        '戊': '土',
        '己': '土',
        '庚': '金',
        '辛': '金',
        '壬': '水',
        '癸': '水',
        '子': '水',
        '丑': '土',
        '寅': '木',
        '卯': '木',
        '辰': '土',
        '巳': '火',
        '午': '火',
        '未': '土',
        '申': '金',
        '酉': '金',
        '戌': '土',
        '亥': '水',
    }
    nian_ben_ming = {
        '甲子': '海中金命',
        '乙丑': '海中金命',
        '丙寅': '炉中火命',
        '丁卯': '炉中火命',
        '戊辰': '大林木命',
        '己巳': '大林木命',
        '庚午': '路旁土命',
        '辛未': '路旁土命',
        '壬申': '剑锋金命',
        '癸酉': '剑锋金命',
        '甲戌': '山头火命',
        '乙亥': '山头火命',
        '丙子': '涧下水命',
        '丁丑': '涧下水命',
        '戊寅': '城头土命',
        '己卯': '城头土命',
        '庚辰': '白蜡金命',
        '辛巳': '白蜡金命',
        '壬午': '杨柳木命',
        '癸未': '杨柳木命',
        '甲申': '泉中水命',
        '乙酉': '泉中水命',
        '丙戌': '屋上土命',
        '丁亥': '屋上土命',
        '戊子': '霹雳火命',
        '己丑': '霹雳火命',
        '庚寅': '松柏木命',
        '辛卯': '松柏木命',
        '壬辰': '长流水命',
        '癸巳': '长流水命',
        '甲午': '砂石金命',
        '乙未': '砂石金命',
        '丙申': '山下火命',
        '丁酉': '山下火命',
        '戊戌': '平地木命',
        '己亥': '平地木命',
        '庚子': '壁上土命',
        '辛丑': '壁上土命',
        '壬寅': '金薄金命',
        '癸卯': '金薄金命',
        '甲辰': '覆灯火命',
        '乙巳': '覆灯火命',
        '丙午': '天河水命',
        '丁未': '天河水命',
        '戊申': '大驿土命',
        '己酉': '大驿土命',
        '庚戌': '钗环金命',
        '辛亥': '钗环金命',
        '壬子': '桑柘木命',
        '癸丑': '桑柘木命',
        '甲寅': '大溪水命',
        '已卯': '大溪水命',
        '丙辰': '沙中土命',
        '丁巳': '沙中土命',
        '戊午': '天上火命',
        '己未': '天上火命',
        '庚申': '石榴木命',
        '辛酉': '石榴木命',
        '壬戌': '大海水命',
        '癸亥': '大海水命',
    }

    def __init__(self, dt=None):
        """ 初始化：参数为datetime.datetime类实例，默认当前时间  """
        self.localtime = dt if dt else datetime.datetime.today()
        self.gz_year_value = ""
        self.ln_month_value = ""
        self.wu_xing = ""

    def sx_year(self):  # 返回生肖年
        ct = self.localtime  # 取当前时间
        year = self.ln_year() - 3 - 1  # 农历年份减3 （说明：补减1）
        year = year % 12  # 模12，得到地支数
        return self.xiao[year]

    def gz_year(self):  # 返回干支纪年
        ct = self.localtime  # 取当前时间
        year = self.ln_year() - 3 - 1  # 农历年份减3 （说明：补减1）
        G = year % 10  # 模10，得到天干数
        Z = year % 12  # 模12，得到地支数
        self.gz_year_value = self.gan[G] + self.zhi[Z]
        return self.gz_year_value

    def gz_month(self):  # 返回干支纪月（原作者未实现）
        """
        干支纪月的计算规则较为复杂，是本人在前人的基础上实现的，填补了空白。
        1、首先判断当前日期所处的节气范围，
        2、特别要考虑年数是否需要增减，以立春为界，如正月尚未立春的日子年数减一，
        3、月的天干公式 （年干序号 * 2 + 月数） % 10 ，其中 0 表示最后一个天干，
        4、月的地支是固定的，查表可得。
        :return:
        """
        ct = self.localtime  # 取当前时间
        jie_qi = self.ln_jie()
        nl_month_val = self.ln_month()
        if len(jie_qi) > 0 and jie_qi in self.jie_qi_odd:   # 如果恰好是节气当日
            if self.jie_qi_month[jie_qi][0] == 0 and nl_month_val == 12:  #
                year = self.ln_year() - 3  # 虽然农历已经是腊月，但是已经立春， 所以年加一
                G = year % 10  # 模10，得到天干数
                Z = year % 12  # 模12，得到地支数
                nl_year = self.gan[G] + self.zhi[Z]
                nl_month = 0
            else:
                nl_year = self.gz_year_value  # 干支纪年
                nl_month = self.jie_qi_month[jie_qi][0]  # 计算出干支纪月
        else:      # 如果不是节气日，则循环判断后一个分月节气是什么
            nl_year = self.gz_year_value
            nl_month = 0
            for i in range(-1, -40, -1):
                var_days = ct + datetime.timedelta(days=i)
                jie_qi = self.nl_jie(var_days)
                if len(jie_qi) > 0 and jie_qi in self.jie_qi_odd:
                    if self.jie_qi_month[jie_qi][0] > 0:
                        nl_month = self.jie_qi_month[jie_qi][0]
                    elif self.jie_qi_month[jie_qi][0] == 0 and nl_month_val == 12:   #
                        year = self.ln_year() - 3    # 虽然农历已经是腊月，但是已经立春， 所以年加一
                        G = year % 10  # 模10，得到天干数
                        Z = year % 12  # 模12，得到地支数
                        nl_year = self.gan[G] + self.zhi[Z]
                        nl_month = 0
                    else:
                        nl_month = 0
                    break
        gan_str = self.gan
        # print(nl_year[0])
        month_num = (gan_str.find(nl_year[0])+1) * 2 + nl_month + 1
        M = month_num % 10
        if M == 0:
            M = 10
        gz_month = self.gan[M-1] + self.jie_qi_month[jie_qi][1]
        return gz_month

    def gz_day(self):  # 返回干支纪日
        ct = self.localtime  # 取当前时间
        C = ct.year // 100  # 取世纪数，减一
        y = ct.year % 100  # 取年份后两位（若为1月、2月则当前年份减一）
        y = y - 1 if ct.month == 1 or ct.month == 2 else y
        M = ct.month  # 取月份（若为1月、2月则分别按13、14来计算）
        M = M + 12 if ct.month == 1 or ct.month == 2 else M
        d = ct.day  # 取日数
        i = 0 if ct.month % 2 == 1 else 6  # 取i （奇数月i=0，偶数月i=6）

        # 下面两个是网上的公式
        # http://baike.baidu.com/link?url=MbTKmhrTHTOAz735gi37tEtwd29zqE9GJ92cZQZd0X8uFO5XgmyMKQru6aetzcGadqekzKd3nZHVS99rewya6q
        # 计算干（说明：补减1）
        G = 4 * C + C // 4 + 5 * y + y // 4 + 3 * (M + 1) // 5 + d - 3 - 1
        G = G % 10
        # 计算支（说明：补减1）
        Z = 8 * C + C // 4 + 5 * y + y // 4 + 3 * (M + 1) // 5 + d + 7 + i - 1
        Z = Z % 12

        # 返回 干支纪日
        return self.gan[G] + self.zhi[Z]

    def gz_hour(self):  # 返回干支纪时（时辰）
        """
        原作者计算的时干支，实际上只返回了时辰的地支，缺少天干；
        我补充了天干的计算，公式皆为原创
        时干数 = ((日干 % 5)*2 + 时辰 -2) % 10
        :return:
        """
        ct = self.localtime  # 取当前时间
        # 计算支
        Z = round((ct.hour / 2) + 0.1) % 12  # 之所以加0.1是因为round的bug!!
        gz_day_value = self.gz_day()
        gz_day_num = self.gan.find(gz_day_value[0]) + 1
        gz_day_yu = gz_day_num % 5
        hour_num = Z + 1
        if gz_day_yu == 0:
            gz_day_yu = 5
        gz_hour_num = (gz_day_yu * 2 - 1 + hour_num-1) % 10
        if gz_hour_num == 0:
            gz_hour_num = 10
        # 返回 干支纪时（时辰）
        return self.gan[gz_hour_num-1] + self.zhi[Z]

    def ln_year(self):  # 返回农历年
        year, _, _ = self.ln_date()
        return year

    def ln_month(self):  # 返回农历月
        _, month, _ = self.ln_date()
        self.ln_month_value = month
        return month

    def ln_day(self):  # 返回农历日
        _, _, day = self.ln_date()
        return day

    def ln_date(self):  # 返回农历日期整数元组（年、月、日）（查表法）
        delta_days = self._date_diff()

        # 阳历1901年2月19日为阴历1901年正月初一
        # 阳历1901年1月1日到2月19日共有49天
        if delta_days < 49:
            year = self.START_YEAR - 1
            if delta_days < 19:
                month = 11
                day = 11 + delta_days
            else:
                month = 12
                day = delta_days - 18
            return year, month, day

        # 下面从阴历1901年正月初一算起
        delta_days -= 49
        year, month, day = self.START_YEAR, 1, 1
        # 计算年
        tmp = self._lunar_year_days(year)
        while delta_days >= tmp:
            delta_days -= tmp
            year += 1
            tmp = self._lunar_year_days(year)

        # 计算月
        (foo, tmp) = self._lunar_month_days(year, month)
        while delta_days >= tmp:
            delta_days -= tmp
            if month == self._get_leap_month(year):
                (tmp, foo) = self._lunar_month_days(year, month)
                if delta_days < tmp:
                    return 0, 0, 0
                delta_days -= tmp
            month += 1
            (foo, tmp) = self._lunar_month_days(year, month)

        # 计算日
        day += delta_days
        return year, month, day

    def ln_date_str(self):  # 返回农历日期字符串，形如：农历正月初九
        year, month, day = self.ln_date()
        return '农历{}年 {}月 {}'.format(year, self.lm[month - 1], self.ld[(day - 1) * 2:day * 2])

    def ln_jie(self):  # 返回农历节气
        ct = self.localtime  # 取当前时间
        year = ct.year
        for i in range(24):
            # 因为两个都是浮点数，不能用相等表示
            delta = self._julian_day() - self._julian_day_of_ln_jie(year, i)
            if -.5 <= delta <= .5:
                return self.jie[i * 2:(i + 1) * 2]
        return ''

    def nl_jie(self,dt):
        year = dt.year
        for i in range(24):
            # 因为两个都是浮点数，不能用相等表示
            delta = self.rulian_day(dt) - self._julian_day_of_ln_jie(year, i)
            if -.5 <= delta <= .5:
                return self.jie[i * 2:(i + 1) * 2]
        return ''
    
    # 以下代码都是Ning为了八字十神实现的函数
    # 将一个农历日期转化为公历日期
    # 以下代码都是Ning为了八字十神实现的函数
    # 将一个农历日期转化为公历日期
    def lunar_to_solar(self, lunar_year, lunar_month, lunar_day, is_leap_month=False):
        """将阴历日期转换为阳历日期"""
        if lunar_year < 1900 or lunar_year > 2100:
            raise ValueError("Year out of range. Supported range is 1900 to 2100.")
        # 获取农历新年日期
        new_year_date = datetime.datetime.strptime(MyLunar.CHINESENEWYEAR[lunar_year - 1900], '%Y%m%d')
        
        # 获取年份编码
        year_code = MyLunar.CHINESEYEARCODE[lunar_year - 1900]
        
        # 获取月份天数
        month_days = self.decode(year_code)
        
        # 计算从春节开始到该日期的天数
        days_passed = self.calculate_days_passed(lunar_month, lunar_day, is_leap_month, year_code, month_days)
        
        # 返回对应的阳历日期
        return new_year_date + datetime.timedelta(days=days_passed)
    def calculate_days_passed(self, lunar_month, lunar_day, is_leap_month, year_code, month_days):
        """计算从农历新年到给定日期所经过的天数"""
        leap_month = year_code & 0xf  # 闰月月份
        days_passed_month = 0
        if leap_month == 0 or lunar_month < leap_month:
            days_passed_month = sum(month_days[:lunar_month - 1])
        elif not is_leap_month or lunar_month != leap_month:
            days_passed_month = sum(month_days[:lunar_month - 1])
        else:
            days_passed_month = sum(month_days[:lunar_month])
        return days_passed_month + (lunar_day - 1)
    @staticmethod
    def decode(year_code):
        """解析年度农历代码函数"""
        month_days = []
        for i in range(4, 16):
            month_days.insert(0, 30 if (year_code >> i) & 1 else 29)
        if year_code & 0xf:
            leap_month_days = 30 if year_code >> 16 else 29
            month_days.insert((year_code & 0xf), leap_month_days)
        return month_days

    # # 返回指定日期最近的两个节气,不包括气
    def closest_jie(self):
        """返回距离当前日期最近的之前和之后的两个特定节气"""
        ct_julian = self._julian_day()
        year = self.localtime.year
        previous_jieqi = None
        next_jieqi = None
        min_previous_delta = float('inf')
        min_next_delta = float('inf')
        # 遍历当前年的所有节气
        for i in range(24):
            jieqi_name = self.jie[i * 2:(i + 1) * 2]
            if jieqi_name in self.jie_qi_month:
                jieqi_julian = self._julian_day_of_ln_jie(year, i)
                delta_days = jieqi_julian - ct_julian
                if delta_days < 0 and abs(delta_days) < min_previous_delta:
                    min_previous_delta = abs(delta_days)
                    previous_jieqi = (jieqi_name, self._julian_to_date(jieqi_julian))
                if delta_days > 0 and delta_days < min_next_delta:
                    min_next_delta = delta_days
                    next_jieqi = (jieqi_name, self._julian_to_date(jieqi_julian))
        # 如果前后节气都为None，抛出异常
        if previous_jieqi is None and next_jieqi is None:
            raise ValueError("未找到任何节气信息，请检查数据和逻辑。")
        # 如果没有找到下一个节气，获取下一年的第一个节气
        if next_jieqi is None:
            next_year_first_jieqi_julian = self._julian_day_of_ln_jie(year + 1, 0)
            next_jieqi = (self.jie[0:2], self._julian_to_date(next_year_first_jieqi_julian))
        # 如果没有找到上一个节气，获取上一年的最后一个节气
        if previous_jieqi is None:
            last_year_last_jieqi_julian = self._julian_day_of_ln_jie(year - 1, 23)
            previous_jieqi = (self.jie[46:48], self._julian_to_date(last_year_last_jieqi_julian))
        return previous_jieqi, next_jieqi
    # def closest_jie(self):
    #     """返回距离当前日期最近的之前和之后的两个特定节气"""
    #     ct_julian = self._julian_day()
    #     year = self.localtime.year
    #     previous_jieqi = None
    #     next_jieqi = None
    #     min_previous_delta = float('inf')
    #     min_next_delta = float('inf')
    #     for i in range(24):
    #         jieqi_name = self.jie[i * 2:(i + 1) * 2]
    #         if jieqi_name in self.jie_qi_month:
    #             jieqi_julian = self._julian_day_of_ln_jie(year, i)
    #             delta_days = jieqi_julian - ct_julian
    #             if delta_days < 0 and abs(delta_days) < min_previous_delta:
    #                 min_previous_delta = abs(delta_days)
    #                 previous_jieqi = (jieqi_name, self._julian_to_date(jieqi_julian))
    #             if delta_days > 0 and delta_days < min_next_delta:
    #                 min_next_delta = delta_days
    #                 next_jieqi = (jieqi_name, self._julian_to_date(jieqi_julian))
    #     return previous_jieqi, next_jieqi
    # 返回指定日期最近的两个节气
    def closest_jieqi(self):
        """返回距离当前日期最近的之前和之后的两个节气"""
        ct_julian = self._julian_day()
        year = self.localtime.year
        previous_jieqi = None
        next_jieqi = None
        min_previous_delta = float('inf')
        min_next_delta = float('inf')
        for i in range(24):
            jieqi_julian = self._julian_day_of_ln_jie(year, i)
            delta_days = jieqi_julian - ct_julian
            if delta_days < 0 and abs(delta_days) < min_previous_delta:
                min_previous_delta = abs(delta_days)
                previous_jieqi = (self.jie[i * 2:(i + 1) * 2], self._julian_to_date(jieqi_julian))
            if delta_days > 0 and delta_days < min_next_delta:
                min_next_delta = delta_days
                next_jieqi = (self.jie[i * 2:(i + 1) * 2], self._julian_to_date(jieqi_julian))
        return previous_jieqi, next_jieqi
    def _julian_to_date(self, julian_day):
        """将儒略日转换为公历日期"""
        J = int(julian_day + 0.5)
        j = J + 32044
        g = j // 146097
        dg = j % 146097
        c = ((dg // 36524 + 1) * 3) // 4
        dc = dg - c * 36524
        b = dc // 1461
        db = dc % 1461
        a = ((db // 365 + 1) * 3) // 4
        da = db - a * 365
        y = g * 400 + c * 100 + b * 4 + a
        m = (da * 5 + 308) // 153 - 2
        d = da - (m + 4) * 153 // 5 + 122
        year = y - 4800 + (m + 2) // 12
        month = (m + 2) % 12 + 1
        day = d + 1
        return datetime.date(year, month, day)
    def _julian_day(self):
        """返回当前日期的儒略日"""
        ct = self.localtime  # 取当前时间
        year = ct.year
        month = ct.month
        day = ct.day
        if month <= 2:
            month += 12
            year -= 1
        A = int(year / 100)
        B = 2 - A + int(A / 4)
        jd = int(365.25 * (year + 4716)) + int(30.6001 * (month + 1)) + day + B - 1524.5
        return jd
    def _julian_day_of_ln_jie(self, year, st):
        """返回指定年份的节气的儒略日数"""
        s_stAccInfo = [
            0.00, 1272494.00, 2548020.00, 3830143.00, 5120225.66, 6420865.35,
            7730209.19, 9055280.48, 10388928.38, 11732976.39, 13084629.50, 14441509.06,
            15800542.11, 17159050.16, 18513757.77, 19862063.74, 21201607.67, 22530201.64,
            23846838.90, 25152645.49, 26447656.31, 27733405.21, 29011602.87, 30285178.17
        ]
        base1900_SlightColdJD = 2415025.5
        if st < 0 or st > 23:
            return 0.0
        stJd = 365.24219878 * (year - 1900) + s_stAccInfo[st] / 86400.0
        return base1900_SlightColdJD + stJd
 
    # 显示日历
    def calendar(self):
        pass

    #######################################################
    #            下面皆为私有函数  也不全是
    #######################################################

    def _date_diff(self):
        """ 返回基于1901/01/01日差数 """
        return (self.localtime - datetime.datetime(1901, 1, 1)).days

    def _get_leap_month(self, lunar_year):
        flag = self.g_lunar_month[(lunar_year - self.START_YEAR) // 2]
        if (lunar_year - self.START_YEAR) % 2:
            return flag & 0x0f
        else:
            return flag >> 4

    def _lunar_month_days(self, lunar_year, lunar_month):
        if lunar_year < self.START_YEAR:
            return 30

        high, low = 0, 29
        iBit = 16 - lunar_month

        if lunar_month > self._get_leap_month(lunar_year) and self._get_leap_month(lunar_year):
            iBit -= 1

        if self.g_lunar_month_day[lunar_year - self.START_YEAR] & (1 << iBit):
            low += 1

        if lunar_month == self._get_leap_month(lunar_year):
            if self.g_lunar_month_day[lunar_year - self.START_YEAR] & (1 << (iBit - 1)):
                high = 30
            else:
                high = 29

        return high, low

    def _lunar_year_days(self, year):
        days = 0
        for i in range(1, 13):
            (high, low) = self._lunar_month_days(year, i)
            days += high
            days += low
        return days

    # 返回指定公历日期的儒略日（http://blog.csdn.net/orbit/article/details/9210413）
    def _julian_day(self):
        ct = self.localtime  # 取当前时间
        year = ct.year
        month = ct.month
        day = ct.day

        if month <= 2:
            month += 12
            year -= 1

        B = year / 100
        B = 2 - B + year / 400

        dd = day + 0.5000115740  # 本日12:00后才是儒略日的开始(过一秒钟)*/
        return int(365.25 * (year + 4716) + 0.01) + int(30.60001 * (month + 1)) + dd + B - 1524.5

    def rulian_day(self, dt):   # 重写_julian_day 函数，变成可以传参的函数
        year = dt.year
        month = dt.month
        day = dt.day
        if month <= 2:
            month += 12
            year -= 1

        B = year / 100
        B = 2 - B + year / 400

        dd = day + 0.5000115740  # 本日12:00后才是儒略日的开始(过一秒钟)*/
        return int(365.25 * (year + 4716) + 0.01) + int(30.60001 * (month + 1)) + dd + B - 1524.5

        # 返回指定年份的节气的儒略日数（http://blog.csdn.net/orbit/article/details/9210413）
    def _julian_day_of_ln_jie(self, year, st):
        s_stAccInfo = [
            0.00, 1272494.40, 2548020.60, 3830143.80, 5120226.60, 6420865.80,
            7732018.80, 9055272.60, 10388958.00, 11733065.40, 13084292.40, 14441592.00,
            15800560.80, 17159347.20, 18513766.20, 19862002.20, 21201005.40, 22529659.80,
            23846845.20, 25152606.00, 26447687.40, 27733451.40, 29011921.20, 30285477.60]

        # 已知1900年小寒时刻为1月6日02:05:00
        base1900_SlightColdJD = 2415025.5868055555

        if (st < 0) or (st > 24):
            return 0.0

        stJd = 365.24219878 * (year - 1900) + s_stAccInfo[st] / 86400.0

        return base1900_SlightColdJD + stJd

    #######################################################
    #            下面为五行分析
    #######################################################

    def gz_to_wu_xing(self, gz_str):
        if len(gz_str) > 0:
            wu_xing = ""
            for gz in list(gz_str):
                wu_xing = wu_xing + self.gz_wu_xing[gz]
            return wu_xing
        else:
            return ""

    def gen_wu_xing(self):
        gz_year = self.gz_year()
        gz_month = self.gz_month()
        gz_day = self.gz_day()
        gz_hour = self.gz_hour()
        gz_list = [gz_year, gz_month, gz_day, gz_hour]
        wu_xing_str = ""
        for g in gz_list:
            wu_xing_str = wu_xing_str + self.gz_to_wu_xing(g)
        count = {}
        for i in wu_xing_str:
            if i not in count:
                count[i] = 1
            else:
                count[i] += 1
        return count

    def wu_xing_lack(self):
        wu_xing = ["金", "木", "水", "火", "土"]
        gen_wu_xing = self.gen_wu_xing()
        ben_ming_wu_xing = self.nian_ben_ming[self.gz_year()][-2]
        if ben_ming_wu_xing in gen_wu_xing.keys():
            gen_wu_xing[ben_ming_wu_xing] += 1
        else:
            gen_wu_xing[ben_ming_wu_xing] = 1
        gen_wu_xing[ben_ming_wu_xing[-1]] = ben_ming_wu_xing
        wu_x_lack = []
        for w in wu_xing:
            if w in gen_wu_xing.keys():
                continue
            else:
                wu_x_lack.append(w)
        return wu_x_lack
