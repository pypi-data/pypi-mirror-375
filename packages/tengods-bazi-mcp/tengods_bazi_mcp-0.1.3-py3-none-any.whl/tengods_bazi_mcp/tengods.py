# 生成一个八字的完整预测，包括一个人的八字、性别和起运时间。
# 根据以上的输入信息，获取格局、大运、流年和其他有必要的信息。
# 取格局时调用Python进行运算，确保代码的稳定性。如果输入是八字的干支、性别、起运时间，则调用determine_pattern函数取格局。如果输入的是日期时间、性别，则使用determine_pattern_by_datetime函数取格局，输入中包含"农历"或"阴历"时，则将determine_pattern_by_datetime函数的isLunar参数设为True，如果输入中包含"阴历闰月"或"农历闰月"，则将determine_pattern_by_datetime函数的isLunar参数设为True和isLeap参数和设为True。

# 角色
# 你是一个熟悉易经八卦和命理占卜的命理师，擅长通过传统的子平法来预测人的格局，并进行性格分析。

## 技能
### 技能1: 格局预测
# - 使用易经八卦和子平法分析个人的生辰八字。
# - 识别出命主的五行属性及其强弱。
# - 预测命主的职业发展、财运和婚姻状况。

### 技能2: 性格分析
# - 根据命主的八字推断其性格特点。
# - 提供具体的性格建议和改善方法。
# - 结合命理知识，解释性格与命运的关系。

### 技能3: 八卦解读
# - 使用易经八卦进行深层次的命理解析。
# - 提供对生活决策的指导意见。
# - 结合八卦，给予命主适应环境变化的建议。

## 约束
# - 只讨论与命理相关的话题。
# - 保持解释简洁明了。
# - 使用传统命理术语。


## 步骤

# 1. **用户输入**：
#    - 提示用户输入要测算的八字、性别和起运时间。

# 2. **取格局**：
#    - 使用以下代码执行取格局
#    - 严格按照python代码返回的信息来显示八字和格局

# 3. **解析八字**：
#   - 根据Python程序返回的格局，进行分析，在分析结果中应该包含完整的八字信息
#   - 如果输入的是日期，则需要将Python程序中返回的八字完整输出，然后再输出八字的解析

### 代码调用示例
# ```python

import datetime
import math
from .MyLunar import MyLunar
from .shensha import get_shen_sha,get_dayan_liunian_shen_sha,get_bazi_shen_sha



class Tengods:
    # create_bazi_output方法中包括大运和流年的信息，改为MCP调用后，这个设计就失效了
    # g_showdayun = True


#region 取格部分

    # 取格的主函数
    # 增加通过日期时间取八字的功能，目前尚未实现根据地理位置获取真太阳时的功能，也没有根据农历日期时间取值
    # 通过日期获取八字并取格局的主函数
    def determine_pattern_by_datetime(dt:datetime.datetime,gender,isLunar:bool = False,isLeap:bool = False):
        result = ""
        
        # 如果是阴历，则首先转化成阳历，然后再创建MyLunar类
        if isLunar:
            lunar_instance = MyLunar()
            solar_date = lunar_instance.lunar_to_solar(dt.year,dt.month,dt.day,isLeap)
            # if solar_date:
            #     print(f"阴历日期：{dt.year}年{dt.month}月{dt.day}日 对应的阳历日期是：{solar_date.strftime('%Y-%m-%d')}")
            # else:
            #     print("无法转换阴历日期，可能年份超出范围（1901-2050）。")
            # 创建一个阴历日期对象: 年、月、日、是否为闰月
            dt = datetime.datetime(solar_date.year,solar_date.month,solar_date.day,dt.hour)
        # else:
        #     print(f"公历日期：{dt.strftime('%Y-%m-%d %H:%M:%S')}\n")

        # 检查时间是否在晚上23:00之后
        if dt.hour >= 23:
            dt = dt + datetime.timedelta(days=1)  # 日期加1
            dt = dt.replace(hour=0, minute=1, second=0, microsecond=0)  # 时间调整为00:01

        # 创建Lunar类的实例
        lunar_converter = MyLunar(dt)

        # print("农历日期是：" + lunar_converter.ln_date_str() + "\n")
        
        # 获取干支信息
        year_gz = lunar_converter.gz_year()
        month_gz = lunar_converter.gz_month()
        day_gz = lunar_converter.gz_day()
        hour_gz = lunar_converter.gz_hour()
        
        # 将干支信息显示到返回值中
        result += year_gz + "，" + month_gz + "，" +day_gz+ "，" + hour_gz + "\n"    

        # 获取距离该日期最近的两个节气
        previous_jieqi, next_jieqi = lunar_converter.closest_jie()
        if previous_jieqi is None and next_jieqi is None:
            raise ValueError("未找到任何节气信息，请检查数据和逻辑。")

        # 输出节气和距离天数的结果
        if previous_jieqi:
            days_diff_previous = (dt.date() - previous_jieqi[1]).days
            # print(f"最近的前一个节气：{previous_jieqi[0]} - 日期：{previous_jieqi[1].strftime('%Y-%m-%d')} - 距离天数：{days_diff_previous}")
        if next_jieqi:
            days_diff_next = (next_jieqi[1] - dt.date()).days
            # print(f"最近的后一个节气：{next_jieqi[0]} - 日期：{next_jieqi[1].strftime('%Y-%m-%d')} - 距离天数：{days_diff_next}")
        
        # 根据顺逆和相邻节气判断起运时间
        bIsShunpai = Tengods.is_shunpai(year_gz[0],gender)
        if bIsShunpai:
            days_diff = days_diff_next
        else:
            days_diff = days_diff_previous
        
        qiyun = days_diff / 3
        result += f"起运时间：{qiyun:.2f}\n"

        # 解析成八字元组
        bazi = (
            (year_gz[0], year_gz[1]), 
            (month_gz[0], month_gz[1]),
            (day_gz[0], day_gz[1]),
            (hour_gz[0], hour_gz[1]),
            gender,
            qiyun,
            dt
        )
        
        # 调用determine_pattern函数
        return Tengods.determine_pattern(bazi),bazi

    # 通过八字、性别和起运时间来取格的函数
    def determine_pattern(bazi):
        pattern = Tengods.determine_pattern_geju(bazi)
        
        # 创建八字的输出结构
        bazi_output = Tengods.create_bazi_output(bazi, pattern, bazi[5], "mbti")

        return bazi_output

    # 通过八字、性别和起运时间来取格的函数
    def determine_pattern_geju(bazi):
        # (year_tiangan, year_zhi), (month_tiangan, month_zhi), (day_tiangan, day_zhi), (hour_tiangan, hour_zhi),gender,start_time,birthday = bazi
            # 解包 bazi，处理可能缺失 birthday 的情况
        if len(bazi) == 7:
            (year_tiangan, year_zhi), (month_tiangan, month_zhi), (day_tiangan, day_zhi), (hour_tiangan, hour_zhi), gender, start_time, birthday = bazi
            birth_year = birthday.year
        else:
            (year_tiangan, year_zhi), (month_tiangan, month_zhi), (day_tiangan, day_zhi), (hour_tiangan, hour_zhi), gender, start_time = bazi
            birth_year = 1  # 虚岁
        
        # 根据月柱的地支，查表，获取对应的天干
        month_tiangan_list = Tengods.get_tiangan(month_zhi)

        # 检查 month_tiangan_list 的数量，如果未取到，则说明输入数据有问题
        lenList = len(month_tiangan_list)
        if lenList <=0:
            raise ValueError("未取到月支对应的天干")
        
        # 第一步，子午卯酉四正月里面都只有一个藏干，只和日干比 
        if lenList == 1:
            # 获取第一个元组的第一个元素（天干）
            tiangan = month_tiangan_list[0][0]
            # 检查月柱的地支是否为子、午、卯、或酉，对应天干为癸乙丁辛
            if tiangan in ['癸', '乙', '丁', '辛']:
                # 调用相应函数
                result = Tengods.get_ten_gods(day_tiangan, tiangan)
                return result

        
        # 第二步，依次检查月柱、年柱和时柱的天干，与根据月令取出的天干是否相匹配，如果相匹配，称为天干透出
        #result = process_ten_gods(month_tiangan_list, day_tiangan, month_tiangan, year_tiangan, hour_tiangan)
        matched_tiangan = Tengods.check_match(month_tiangan_list,month_tiangan)
        if matched_tiangan is not None:
            result = Tengods.get_ten_gods(day_tiangan, matched_tiangan[0])
            if result != "劫财" and result != "比肩":
                return result

        # 检查年柱，如果透出天干，则取值
        matched_tiangan = Tengods.check_match(month_tiangan_list,year_tiangan)
        if matched_tiangan is not None:
            result = Tengods.get_ten_gods(day_tiangan, matched_tiangan[0])
            if result != "劫财" and result != "比肩":
                return result

        # 检查时柱，如果透出天干，则取值
        matched_tiangan = Tengods.check_match(month_tiangan_list,hour_tiangan)
        if matched_tiangan is not None:
            result = Tengods.get_ten_gods(day_tiangan, matched_tiangan[0])
            if result != "劫财" and result != "比肩":
                return result

        # 第二步：天干不透出的情况
        # 根据年柱的天干和性别，获取是否为顺排
        bIsShunpai = Tengods.is_shunpai(year_tiangan,gender)

        # 当月柱的地支为“亥”时，需要特别处理
        # 1. 天干透出时，是按[('戊', 2), ('甲', 7), ('壬', 21)]处理
        # 2，天干不透的时候，按[('甲', 7), ('壬', 23)]处理
        if month_zhi == "亥":
            month_tiangan_list = [('甲', 7), ('壬', 23)]

        result = Tengods.calculate_tianganbutou(month_tiangan_list,start_time,bIsShunpai,day_tiangan,month_zhi)
        return result
        
    # 创建八字的输出格式
    def create_bazi_output(bazi, pattern, start_time, mbti):
        bazi_ten_gods = Tengods.get_bazi_ten_gods(bazi)
        gender = bazi[4]
        if len(bazi) == 7:
            birthday = bazi[6] # birthday
        else:
            birthday = None
        
        # 获取神煞 -- 假设需要的输入参数 (大运和流年列表)，根据实际情况替换
        # da_yun_list = []  # 示例大运列表
        # liu_nian_list = []  # 示例流年列表
        # shen_sha_results = get_bazi_shen_sha(bazi, da_yun_list, liu_nian_list)
        shen_sha_results = get_bazi_shen_sha(bazi)
        
        # Converting bazi to output structure
        bazi_output = [pattern]  # 格局
        
        for index, ((tg, tg_ten_god), (dz, dz_info)) in enumerate(bazi_ten_gods):
            # Get shensha from previously calculated results
            shensha = shen_sha_results[index]
            bazi_output.append(((tg, tg_ten_god), (dz, dz_info), shensha))
        
        bazi_output.append(gender)         # 性别
        bazi_output.append(start_time)     # 起运时间
        bazi_output.append(mbti)           # MBTI类型

        # 获得大运流年
        # if Tengods.g_showdayun:
        #     if bazi is not None:
        #         dayan_output = Tengods.get_dayan(bazi,birthday)
        #         bazi_output.append(dayan_output)

        #         # 获得流年
        #         if birthday:
        #             # 计算当前年份为中间的前后十年
        #             current_year = datetime.datetime.now().year
        #             start_year = current_year - 10
        #             end_year = current_year + 10
        #         else:
        #             # 没有生日，使用虚岁 1 到 10 年
        #             start_year = 1
        #             end_year = 11
        #         liunian_output = Tengods.get_liunian(bazi,start_year=start_year, end_year=end_year, birthday=birthday)
        #         bazi_output.append(liunian_output)
        
        return bazi_output

    # 天干和地支的五行属性 (示例)
    WU_XING = {
        '甲': '木', '乙': '木', '丙': '火', '丁': '火', '戊': '土',
        '己': '土', '庚': '金', '辛': '金', '壬': '水', '癸': '水',
        '子': '水', '丑': '土', '寅': '木', '卯': '木', '辰': '土',
        '巳': '火', '午': '火', '未': '土', '申': '金', '酉': '金',
        '戌': '土', '亥': '水'
    }

    # 获取八字的十神属性
    # 提示词：增加一个获取八字十神的函数，为每个八字获取一个十神的属性，输入值为八字的结构体，
    # 返回值是一个类似于这样的列表： (('癸','劫财'), ('酉','辛.正印'), # 年柱: (天干, 地支)，(('壬','比肩'), ('戌','戊.七杀'),(('壬','女'), ('午','丁.正财'), # 日柱(('乙','伤官'), ('巳','丙.偏财'),
    # 我们继续来实现地支的十神属性，调用get_tiangan函数，获取对应的天干，我们将其称为“地支藏干”或“藏干”。
    # 如果只有一个藏干，直接取藏干的十神即可；如果有三个藏干，则取与地支五行属性相同的藏干，然后获取该藏干的十神即可。
    # 如果不清楚天干地支的五行属性，我稍后可以提供这些信息。
    def get_bazi_ten_gods(bazi):
        result = []
        
        gender = bazi[4]  # 假设性别存储在 bazi 元组中的第五个位置
        
        for index, (tiangan, dizhi) in enumerate(bazi[:4]):  # 年、月、日、时四柱
            if index == 2:  # 日柱
                tiangan_ten_god = gender
            else:
                tiangan_ten_god = Tengods.get_ten_gods(bazi[2][0], tiangan)
            
            # 获取地支藏干
            zanggan_list = Tengods.get_tiangan(dizhi)
            zanggan_ten_god = "未知"
            selected_zanggan = zanggan_list[0][0]  # 默认选第一个藏干
            
            if len(zanggan_list) == 1:
                selected_zanggan = zanggan_list[0][0]
                zanggan_ten_god = Tengods.get_ten_gods(bazi[2][0], selected_zanggan)
            elif len(zanggan_list) == 3:
                dizhi_wuxing = Tengods.WU_XING[dizhi]
                for zanggan, _ in zanggan_list:
                    if Tengods.WU_XING[zanggan] == dizhi_wuxing:
                        selected_zanggan = zanggan
                        zanggan_ten_god = Tengods.get_ten_gods(bazi[2][0], selected_zanggan)
                        break
            
            # 将当前柱的信息添加到结果中
            result.append(((tiangan, tiangan_ten_god), (dizhi, f"{selected_zanggan}.{zanggan_ten_god}")))
        
        return result
        
    # 提示词
    # 编写一段代码，输入是一个人的八字和性别，首先根据八字中月柱的地支，查表获得对应的天干，表格在附件中，
    # 然后按照八字中月柱、年柱和时柱的顺序查看天干，如果天干和表中的天干相配，
    # 我们则把日柱的天干和查到的天干发送给一个取格局的函数，取格局函数稍后实现，由该函数返回该八字的格局。
    # 八字是由八个字构成，分别是年柱、月柱、日柱和时柱，每一柱里有天干和地支。
    def get_tiangan(zhi):
        mapping = {
            '子': [('癸', 30)],
            '丑': [('癸', 9), ('辛', 6), ('己', 15)],
            '寅': [('戊', 4), ('丙', 6), ('甲', 20)],
            '卯': [('乙', 30)],
            '辰': [('乙', 9), ('癸', 6), ('戊', 15)],
            '巳': [('戊', 4), ('庚', 6), ('丙', 20)],
            '午': [('丁', 30)],
            '未': [('丁', 9), ('乙', 6), ('己', 15)],
            '申': [('戊', 4),('壬', 6), ('庚', 20)],
            '酉': [('辛', 30)],
            '戌': [('辛', 9), ('丁', 6), ('戊', 15)],
            '亥': [('戊', 2), ('甲', 7), ('壬', 21)]
        }
        
        return mapping.get(zhi, [])

    def get_ten_gods(day_gan1, day_gan2):
        table = {
            '甲': {'甲': '比肩', '乙': '劫财', '丙': '食神', '丁': '伤官',
                '戊': '偏财', '己': '正财', '庚': '偏官', '辛': '正官',
                '壬': '偏印', '癸': '正印'},
            '乙': {'甲': '劫财', '乙': '比肩', '丙': '伤官', '丁': '食神',
                '戊': '正财', '己': '偏财', '庚': '正官', '辛': '偏官',
                '壬': '正印', '癸': '偏印'},
            '丙': {'甲': '偏印', '乙': '正印', '丙': '比肩', '丁': '劫财',
                '戊': '食神', '己': '伤官', '庚': '偏财', '辛': '正财',
                '壬': '偏官', '癸': '正官'},
            '丁': {'甲': '正印', '乙': '偏印', '丙': '劫财', '丁': '比肩',
                '戊': '伤官', '己': '食神', '庚': '正财', '辛': '偏财',
                '壬': '正官', '癸': '偏官'},
            '戊': {'甲': '偏官', '乙': '正官', '丙': '偏印', '丁': '正印',
                '戊': '比肩', '己': '劫财', '庚': '食神', '辛': '伤官',
                '壬': '偏财', '癸': '正财'},
            '己': {'甲': '正官', '乙': '偏官', '丙': '正印', '丁': '偏印',
                '戊': '劫财', '己': '比肩', '庚': '伤官', '辛': '食神',
                '壬': '正财', '癸': '偏财'},
            '庚': {'甲': '偏财', '乙': '正财', '丙': '偏官', '丁': '正官',
                '戊': '偏印', '己': '正印', '庚': '比肩', '辛': '劫财',
                '壬': '食神', '癸': '伤官'},
            '辛': {'甲': '正财', '乙': '偏财', '丙': '正官', '丁': '偏官',
                '戊': '正印', '己': '偏印', '庚': '劫财', '辛': '比肩',
                '壬': '伤官', '癸': '食神'},
            '壬': {'甲': '食神', '乙': '伤官', '丙': '偏财', '丁': '正财',
                '戊': '偏官', '己': '正官', '庚': '偏印', '辛': '正印',
                '壬': '比肩', '癸': '劫财'},
            '癸': {'甲': '伤官', '乙': '食神', '丙': '正财', '丁': '偏财',
                '戊': '正官', '己': '偏官', '庚': '正印', '辛': '偏印',
                '壬': '劫财', '癸': '比肩'}
        }
        
        return table.get(day_gan1, {}).get(day_gan2, "未知")

    # 根据性别和年柱的天干，判断是顺排还是逆排
    # 提示词：
    # 编写一个程序，用来获取顺排或逆排，输入是天干和性别，返回一个布尔值，ture表示顺排，flase表示逆排。
    # 如果男性阳年顺排，返回ture，女性阴年顺排，返回ture。甲是阳年，乙是阴年，丙是阳年，以此类推。
    def is_shunpai(tiangan, gender):
        # 定义阳年和阴年
        yang_nian = ['甲', '丙', '戊', '庚', '壬']
        yin_nian = ['乙', '丁', '己', '辛', '癸']
        if tiangan in yang_nian and gender == '男':
            return True  # 男性阳年顺排
        elif tiangan in yin_nian and gender == '女':
            return True  # 女性阴年顺排
        else:
            return False  # 其他情况为逆排

    # 这部分代码用于处理天干不透的情况
    def find_tianganbutou(adjusted_value, tiangan_list, is_shunpai):
        cumulative_end = 0
        if is_shunpai:
            for index, (tiangan, end_value) in enumerate(tiangan_list):
                cumulative_end += end_value
                if cumulative_end > adjusted_value >= cumulative_end - end_value:
                    return index, tiangan
        else:  # 逆排
            cumulative_start = 30
            for index, (tiangan, end_value) in enumerate(reversed(tiangan_list)):
                cumulative_start -= end_value
                if cumulative_start <= adjusted_value < cumulative_start + end_value:
                    reverse_index = len(tiangan_list) - 1 - index
                    return reverse_index, tiangan
        return None, None

    # 天干透遇比劫，当不透处理；天干不透，落在比劫上，按顺逆下取一位；
    # 如果下一位取不到，月支为“辰戌丑未”，土属性不取禄刃,则上取一位，否则取“比劫”，
    # 但是把上一位的十神也显示出来，以（比肩.X）的形式显示。
    def calculate_tianganbutou(tiangan_list, start_time: int, is_shunpai: bool, day_tiangan, month_zhi):
        if len(tiangan_list) == 1:
            return tiangan_list[0][0]
        
        range_value = start_time * 3
        adjusted_value = 30 - range_value if is_shunpai else range_value
        index, butoutiangan = Tengods.find_tianganbutou(adjusted_value, tiangan_list, is_shunpai)
        
        if butoutiangan is None:
            return None
        
        result = Tengods.get_ten_gods(day_tiangan, butoutiangan)
        if result in ["劫财", "比肩"]:
            # 寻找下一个索引
            next_index = index + 1 if is_shunpai else index - 1
            
            # 检查索引范围并根据条件调整
            if next_index < 0 or next_index >= len(tiangan_list):
                if month_zhi in ["辰", "戌", "丑", "未"]:
                    # 上取一位
                    next_index = index - 1 if is_shunpai else index + 1
                else:
                    # 当前结果显示上一位十神
                    previous_index = index - 1 if index - 1 >= 0 else len(tiangan_list) - 1
                    previous_tiangan = tiangan_list[previous_index][0]
                    secondary_result = Tengods.get_ten_gods(day_tiangan, previous_tiangan)
                    return f"{result}.{secondary_result}"
            if 0 <= next_index < len(tiangan_list):
                next_tiangan = tiangan_list[next_index][0]
                result = Tengods.get_ten_gods(day_tiangan, next_tiangan)
        
        return result

    # ！天干不透的处理

    # 检查天干是否透出
    def check_match(tiangan_list, value):
        for item in tiangan_list:
            if value == item[0]:
                return value
        
        return None
#endregion 

#region 大运流年

    TIANGAN_ORDER = ['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
    DIZHI_ORDER = ['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']

    # 提示词：我们在Tengods类里增加一个获取大运的函数，输入值为八字和起运时间，输出是一个大运的列表，
    # 一般来说我们会排10步大运（符合人类的寿命），每个大运的天干地支，以及天干地支所对应的十神，
    # 十神的查询方法应用之前的函数。具体的算法是，从起运时间后第一个整年开始计算，每步大运是十年的时间。
    # 根据八字的顺逆，如果是顺行，起运时间后的第一步大运就是从八字月柱的天干地支开始，各向后一位；
    # 如果是逆行，则从八字月柱的天干地支开始，向前一位。八字的顺逆可以通过Tengods.is_shunpai函数获得。

    # 获取大运
    def get_dayan(bazi, birthday=None):
        month_tiangan, month_dizhi = bazi[1]  # 月柱天干和地支
        gender = bazi[4]  # 性别
        start_time = bazi[5]  # 起运时间

        if birthday is None:
            birth_year = 1  # 虚岁，应该是从1岁开始
        else:
            birth_year = birthday.year  # 实岁
        
        is_shunpai = Tengods.is_shunpai(bazi[0][0], gender)  # 年柱天干判断顺逆
        start_index_tg = Tengods.TIANGAN_ORDER.index(month_tiangan)
        start_index_dz = Tengods.DIZHI_ORDER.index(month_dizhi)
        
        dayan_list = []

        # 添加小运，表示从出生到第一步大运开始
        # 起运是从起运时间后的第一个立春开始计算，所以，start_time应该是向上取整，比如start_time是3.2，则返回4
        first_dayan_start_year = birth_year + math.ceil(start_time)
        dayan_list.append((('小运', ''), ('', ''), birth_year, ['']))

        # 计算大运
        for i in range(10):  # 创建10步大运
            if is_shunpai:
                tg_index = (start_index_tg + (i + 1)) % len(Tengods.TIANGAN_ORDER)
                dz_index = (start_index_dz + (i + 1)) % len(Tengods.DIZHI_ORDER)
            else:
                tg_index = (start_index_tg - (i + 1)) % len(Tengods.TIANGAN_ORDER)
                dz_index = (start_index_dz - (i + 1)) % len(Tengods.DIZHI_ORDER)
            tg = Tengods.TIANGAN_ORDER[tg_index]
            dz = Tengods.DIZHI_ORDER[dz_index]
            tg_ten_god = Tengods.get_ten_gods(bazi[2][0], tg)  # 日柱天干为参考
            
            # 处理地支藏干及其十神
            zanggan_list = Tengods.get_tiangan(dz)
            selected_zanggan = zanggan_list[0][0]  # 默认选第一个藏干
            zanggan_ten_god = "未知"
            
            if len(zanggan_list) == 1:
                selected_zanggan = zanggan_list[0][0]
                zanggan_ten_god = Tengods.get_ten_gods(bazi[2][0], selected_zanggan)
            elif len(zanggan_list) == 3:
                dizhi_wuxing = Tengods.WU_XING[dz]
                for zanggan, _ in zanggan_list:
                    if Tengods.WU_XING[zanggan] == dizhi_wuxing:
                        selected_zanggan = zanggan
                        zanggan_ten_god = Tengods.get_ten_gods(bazi[2][0], selected_zanggan)
                        break
            # 每一步大运的起始年份计算
            start_year = first_dayan_start_year + i * 10
            # shen_sha = result = get_bazi_shen_sha(bazi, ((tg,dz)))
            dayan_list.append((
                (tg, tg_ten_god), 
                (dz, f"{selected_zanggan}.{zanggan_ten_god}"), 
                start_year,
                ""
            ))
        
        return dayan_list

# 提示词
# 根据get_dayan的函数，编写获得流年的函数：输入八字的结构体、取流年的开始时间和结束时间（如果没有，则默认取从出生开始后十年的流年），
# 出生日期为可选输入：从出生那一年的天干地支开始，每过一年，天干地支各向后一位。输出下面结构的一个列表： [
# (2017,(('丁','正财'),('酉','辛.正印'),['德秀贵人','空亡','将星','天医'])),
# (2024,(('甲','食神'),('辰','戊.七杀'),['福星贵人','元辰']))
# ] # 流年,应该列出该大运中十年的流年，为了示例简单仅列出两年，剩下的省略

    # 获取流年
    def get_liunian(bazi, start_year=None, end_year=None, birthday=None):
        year_tiangan, year_dizhi = bazi[0]  # 年柱天干和地支
        if birthday:
            birth_year = birthday.year
        else:
            birth_year = 1  # 如果没有生日信息，则假设虚岁为1
        
        if not start_year:
            start_year = birth_year
        if not end_year:
            end_year = start_year + 10  # 默认取从出生后10年的流年
        
        start_index_tg = Tengods.TIANGAN_ORDER.index(year_tiangan)
        start_index_dz = Tengods.DIZHI_ORDER.index(year_dizhi)
        liunian_list = []
        for year in range(start_year, end_year):
            tg_index = (start_index_tg + (year - birth_year)) % len(Tengods.TIANGAN_ORDER)
            dz_index = (start_index_dz + (year - birth_year)) % len(Tengods.DIZHI_ORDER)
            tg = Tengods.TIANGAN_ORDER[tg_index]
            dz = Tengods.DIZHI_ORDER[dz_index]
            tg_ten_god = Tengods.get_ten_gods(bazi[2][0], tg)  # 日柱天干为参考
            zanggan_list = Tengods.get_tiangan(dz)
            selected_zanggan = zanggan_list[0][0]  # 默认选第一个藏干
            zanggan_ten_god = "未知"
            if len(zanggan_list) == 1:
                selected_zanggan = zanggan_list[0][0]
                zanggan_ten_god = Tengods.get_ten_gods(bazi[2][0], selected_zanggan)
            elif len(zanggan_list) == 3:
                dizhi_wuxing = Tengods.WU_XING[dz]
                for zanggan, _ in zanggan_list:
                    if Tengods.WU_XING[zanggan] == dizhi_wuxing:
                        selected_zanggan = zanggan
                        zanggan_ten_god = Tengods.get_ten_gods(bazi[2][0], selected_zanggan)
                        break
            # shen_sha = Tengods.get_bazi_shen_sha((year - birth_year))
            liunian_list.append((
                year,
                ((tg, tg_ten_god), (dz, f"{selected_zanggan}.{zanggan_ten_god}")),
                ''
            ))
        
        return liunian_list

#endregion


# ```
    
