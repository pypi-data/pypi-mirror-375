"""
FastMCP quickstart example.

cd to the `examples/snippets/clients` directory and run:
    uv run server fastmcp_quickstart stdio
"""

import datetime
from typing import List, Tuple, Union, Dict, Any, Optional
from mcp.server.fastmcp import FastMCP
from .tengods import Tengods
from .MyLunar import MyLunar
from .shensha import get_shen_sha,get_dayan_liunian_shen_sha,get_bazi_shen_sha

# Create an MCP server
mcp = FastMCP("tengods.bazi")

#region 大运流年

# 获取大运
@mcp.tool()
def GetDayun(
    bazi: List[Union[Tuple[str, str], str, float]],
    birthday: Optional[str] = None
) -> Dict[str, Any]:
    """
    根据八字信息和生日获取大运信息
    
    Args:
        bazi: 八字信息，格式为:
            [
                ('癸', '酉'),  # 年柱: (天干, 地支)
                ('壬', '戌'),  # 月柱
                ('壬', '午'),  # 日柱
                ('乙', '巳'),  # 时柱
                '女',          # 性别
                3.4            # 起运时间，float
            ]
        birthday: 生日日期，格式为 "YYYY-MM-DD HH:MM" (可选)
        
    Returns:
        包含大运信息的结构化字典
    """
    try:
        # 验证输入格式
        if len(bazi) < 6:  # 需要至少6个元素，包括起运时间
            return {
                "error": True,
                "message": "输入格式错误，需要6个元素: 年柱、月柱、日柱、时柱、性别、起运时间"
            }
        
        # 将生日字符串转换为 datetime 对象
        birthday_obj = None
        if birthday:
            try:
                birthday_obj = datetime.datetime.strptime(birthday, "%Y-%m-%d %H:%M")
            except ValueError:
                return {
                    "error": True,
                    "message": "生日日期格式错误，请使用 'YYYY-MM-DD HH:MM' 格式"
                }
        
        # 调用 Tengods 函数获取大运信息
        dayun_output = Tengods.get_dayan(bazi, birthday_obj)
        
        # 返回结构化的结果
        return {
            "success": True,
            "dayun": dayun_output,
            "bazi": bazi,
            "birthday": birthday
        }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"获取大运信息时发生错误: {str(e)}"
        }

@mcp.tool()
def GetLiunian(
    bazi: List[Union[Tuple[str, str], str, float]],
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    birthday: Optional[str] = None
) -> Dict[str, Any]:
    """
    根据八字信息获取流年信息
    
    Args:
        bazi: 八字信息，格式为:
            [
                ('癸', '酉'),  # 年柱: (天干, 地支)
                ('壬', '戌'),  # 月柱
                ('壬', '午'),  # 日柱
                ('乙', '巳'),  # 时柱
                '女',          # 性别
                3.4            # 起运时间，float
            ]
        start_year: 起始年份 (可选)
        end_year: 结束年份 (可选)
        birthday: 生日日期，格式为 "YYYY-MM-DD HH:MM" (可选)
        
    Returns:
        包含流年信息的结构化字典
    """
    try:
        # 验证输入格式
        if len(bazi) < 5:
            return {
                "error": True,
                "message": "输入格式错误，至少需要5个元素: 年柱、月柱、日柱、时柱、性别"
            }
        
        # 如果没有提供起始年份和结束年份，使用默认值
        if start_year is None or end_year is None:
            if birthday:
                # 如果有生日，计算当前年份为中间的前后十年
                current_year = datetime.datetime.now().year
                start_year = current_year - 10
                end_year = current_year + 10
            else:
                # 没有生日，使用虚岁 1 到 10 年
                start_year = 1
                end_year = 11
        
        # 如果有生日参数，将其转换为 datetime 对象
        birthday_obj = None
        if birthday:
            try:
                birthday_obj = datetime.datetime.strptime(birthday, "%Y-%m-%d %H:%M")
            except ValueError:
                return {
                    "error": True,
                    "message": "生日日期格式错误，请使用 'YYYY-MM-DD HH:MM' 格式"
                }
        
        # 调用 Tengods 函数获取流年信息
        liunian_output = Tengods.get_liunian(
            bazi, 
            start_year=start_year, 
            end_year=end_year, 
            birthday=birthday_obj
        )
        
        # 返回结构化的结果
        return {
            "success": True,
            "liunian": liunian_output,
            "bazi": bazi,
            "start_year": start_year,
            "end_year": end_year,
            "birthday": birthday
        }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"获取流年信息时发生错误: {str(e)}"
        }
    
#endregion

#region 格局

# 根据出生时间和性别获得八字格局
@mcp.tool()
def GetPatternByDatetime(dt: str, gender: str, isLunar: bool = False, isLeap: bool = False) -> Dict[str, Any]:
    """
    根据出生年月日时和性别，获取完整的八字信息，包括大运和流年
    
    Args:
        dt: 出生日期时间，格式为 "YYYY-MM-DD HH:MM"
        gender: 性别，"男"或"女"
        isLunar: 出生日期是否为农历日期，默认值为False
        isLeap: 出生日期是否为闰月，默认值为False
        
    Returns:
        包含完整八字分析的结构化字典，格式与GetCompleteBaziAnalysis一致
    """
    # 将字符串转换为 datetime 对象
    try:
        dt_obj = datetime.datetime.strptime(dt, "%Y-%m-%d %H:%M")
    except ValueError:
        return {
            "error": True,
            "message": "日期时间格式错误，请使用 'YYYY-MM-DD HH:MM' 格式"
        }
    
    # 验证性别
    if gender not in ["男", "女"]:
        return {
            "error": True,
            "message": "性别必须是'男'或'女'"
        }
    
    # 调用 Tengods 函数，传递 datetime 对象
    try:
        result, item = Tengods.determine_pattern_by_datetime(dt_obj, gender, isLunar, isLeap)
        
        # 提取四柱信息
        year_pillar = (result[1][0][0], result[1][1][0])  # 年柱天干地支
        month_pillar = (result[2][0][0], result[2][1][0])  # 月柱天干地支
        day_pillar = (result[3][0][0], result[3][1][0])  # 日柱天干地支
        hour_pillar = (result[4][0][0], result[4][1][0])  # 时柱天干地支
        
        # 提取起运时间
        starting_age = result[6] if len(result) > 6 else 0
        
        # 构建 bazi 列表用于获取大运和流年
        bazi = [
            (year_pillar[0], year_pillar[1]),  # 年柱
            (month_pillar[0], month_pillar[1]),  # 月柱
            (day_pillar[0], day_pillar[1]),  # 日柱
            (hour_pillar[0], hour_pillar[1]),  # 时柱
            gender,  # 性别
            starting_age  # 起运时间
        ]
        
        # 获取大运信息
        dayun_output = Tengods.get_dayan(bazi, dt_obj)
        
        # 获取流年信息
        current_year = datetime.datetime.now().year
        start_year = current_year - 10
        end_year = current_year + 10
        liunian_output = Tengods.get_liunian(bazi, start_year=start_year, end_year=end_year, birthday=dt_obj)
        
        # 获取十神信息
        bazi_ten_gods = Tengods.get_bazi_ten_gods(bazi)
        
        # 获取神煞信息
        shen_sha_results = get_bazi_shen_sha(bazi)
        
        # 构建四柱信息
        pillars = []
        for index, ((tg, tg_ten_god), (dz, dz_info)) in enumerate(bazi_ten_gods):
            shensha = shen_sha_results[index] if index < len(shen_sha_results) else []
            pillars.append({
                "heavenly_stem": tg,
                "stem_relation": tg_ten_god,
                "earthly_branch": dz,
                "branch_detail": dz_info,
                "shensha": shensha
            })
        
        # 提取 MBTI 类型（如果存在）
        mbti = result[7] if len(result) > 7 else "未知"
        
        # 返回结构化的结果
        return {
            "success": True,
            "pattern": result[0] if len(result) > 0 else "未知",
            "year_pillar": pillars[0] if len(pillars) > 0 else {},
            "month_pillar": pillars[1] if len(pillars) > 1 else {},
            "day_pillar": pillars[2] if len(pillars) > 2 else {},
            "hour_pillar": pillars[3] if len(pillars) > 3 else {},
            "gender": gender,
            "starting_age": starting_age,
            "mbti": mbti,
            "dayun": dayun_output,
            "liunian": liunian_output,
            "birthday": dt,
            "raw_result": result  # 保留原始结果
        }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"计算八字格局时发生错误: {str(e)}"
        }

# 根据八字、性别和起运时间获得八字格局
@mcp.tool()
def GetPatternByBazi(
    bazi: List[Union[Tuple[str, str], str, float]],
    birthday: Optional[str] = None
) -> Dict[str, Any]:
    """
    获取完整的八字分析，包括格局、大运和流年
    
    Args:
        bazi: 八字信息，格式为:
            [
                ('癸', '酉'),  # 年柱: (天干, 地支)
                ('壬', '戌'),  # 月柱
                ('壬', '午'),  # 日柱
                ('乙', '巳'),  # 时柱
                '女',          # 性别
                3.4            # 起运时间，float
            ]
        birthday: 生日日期，格式为 "YYYY-MM-DD HH:MM" (可选)
        
    Returns:
        包含完整八字分析的结构化字典
    """
    try:
        # 验证输入格式
        if len(bazi) < 5:
            return {
                "error": True,
                "message": "输入格式错误，至少需要5个元素: 年柱、月柱、日柱、时柱、性别"
            }
        
        # 获取八字格局
        pattern_result = Tengods.determine_pattern(bazi)
        
        # 获取大运信息
        birthday_obj = None
        if birthday:
            try:
                birthday_obj = datetime.datetime.strptime(birthday, "%Y-%m-%d %H:%M")
            except ValueError:
                return {
                    "error": True,
                    "message": "生日日期格式错误，请使用 'YYYY-MM-DD HH:MM' 格式"
                }
        
        bazi_with_birthday = bazi + [birthday_obj] if birthday_obj else bazi
        dayun_output = Tengods.get_dayan(bazi_with_birthday, birthday_obj)
        
        # 获取流年信息
        if birthday_obj:
            current_year = datetime.datetime.now().year
            start_year = current_year - 10
            end_year = current_year + 10
        else:
            start_year = 1
            end_year = 11
        
        liunian_output = Tengods.get_liunian(
            bazi, 
            start_year=start_year, 
            end_year=end_year, 
            birthday=birthday_obj
        )
        
        # 获取十神信息
        bazi_ten_gods = Tengods.get_bazi_ten_gods(bazi)
        
        # 获取神煞信息
        shen_sha_results = get_bazi_shen_sha(bazi)
        
        # 构建完整的输出结构
        gender = bazi[4]
        start_time = bazi[5] if len(bazi) > 5 else None
        
        # 构建四柱信息
        pillars = []
        for index, ((tg, tg_ten_god), (dz, dz_info)) in enumerate(bazi_ten_gods):
            shensha = shen_sha_results[index] if index < len(shen_sha_results) else []
            pillars.append({
                "heavenly_stem": tg,
                "stem_relation": tg_ten_god,
                "earthly_branch": dz,
                "branch_detail": dz_info,
                "shensha": shensha
            })
        
        # 返回结构化的结果
        return {
            "success": True,
            "pattern": pattern_result[0] if pattern_result and len(pattern_result) > 0 else "未知",
            "year_pillar": pillars[0] if len(pillars) > 0 else {},
            "month_pillar": pillars[1] if len(pillars) > 1 else {},
            "day_pillar": pillars[2] if len(pillars) > 2 else {},
            "hour_pillar": pillars[3] if len(pillars) > 3 else {},
            "gender": gender,
            "starting_age": start_time,
            "dayun": dayun_output,
            "liunian": liunian_output,
            "birthday": birthday
        }
        
    except Exception as e:
        return {
            "error": True,
            "message": f"获取完整八字分析时发生错误: {str(e)}"
        }

#endregion


def main() -> None:
    mcp.run(transport='stdio')
