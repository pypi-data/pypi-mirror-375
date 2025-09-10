# schedule-mcp-server
from mcp.server.fastmcp import FastMCP
import sys
# import logging
import math
import random
import pandas as pd
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# logger = logging.getLogger('schedule-mcp-server')

# Fix UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stderr.reconfigure(encoding='utf-8')
    sys.stdout.reconfigure(encoding='utf-8')


# Create an MCP server
# mcp = FastMCP("schedule-mcp-server", host="0.0.0.0", port=8000)
mcp = FastMCP("schedule-mcp-server")

file_path='./schedule.csv'

def read_or_create_schedule_csv(file_path='./schedule.csv'):
    """读取csv数据文件，对数据进行基本总结描述

    Args:
        file_path: 数据文件目录地址
    """
    try:
        # 尝试读取CSV文件
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        # 如果文件不存在，创建一个新的DataFrame
        df = pd.DataFrame(columns=['user_id', 'role_name', 'date', 'year_month', 'weekday', 'start_datetime', 'end_datetime', 'activity', 'duration'])
        # 保存新的DataFrame到CSV文件
        df.to_csv(file_path, index=False)
    
    return df

def role_name_preprocess(role_name):
    # print("role_name===", role_name)
    if role_name in ['姐姐', '长公主']:
        role_name = '姐姐'
    elif role_name in ['弟弟', '小王子']:
        role_name = '弟弟'
    elif role_name in ['哥哥', '大王子']:
        role_name = '哥哥'
    elif role_name in ['妹妹', '小公主']:
        role_name = '妹妹'
    elif role_name in ['妈妈','爸爸','奶奶', '爷爷']:
        pass
    else:
        raise ValueError("role_name必须是以下列表中最接近的元素:['姐姐','长公主','哥哥','大王子','弟弟','小王子','妹妹','小公主','妈妈','爸爸','奶奶', '爷爷']")
    return role_name


# 计算器
@mcp.tool()
def calculator(python_expression: str) -> dict:
    """For mathamatical calculation, always use this tool to calculate the result of a python expression. You can use 'math' or 'random' directly, without 'import'."""
    result = eval(python_expression, {"math": math, "random": random})
    # logger.info(f"Calculating formula: {python_expression}, result: {result}")
    return str({"success": True, "result": result})


# 获取当前时间
@mcp.tool()
def get_utf8_time() -> dict:
    """获取当前的时间（中国标准时间），精确到年、月、日、时、分、秒。

    """

    # 使用 Asia/Shanghai 时区获取当前时间
    shanghai_tz = ZoneInfo("Asia/Shanghai")
    current_time = datetime.now(shanghai_tz)
    
    time_str = current_time.strftime("%Y-%m-%d %H:%M:%S")
    return str({"success": True, "result": "当前时间为：" + time_str})



# 添加日程安排
@mcp.tool()
def add_schedule(user_id: str,
                 role_name: str,
                 start_datetime: str,
                 activity: str,
                 duration: int=None, 
                 end_datetime: str=None                
                ):
    """添加新的日程安排, 输入参数包括用户ID、角色名字、开始时间、活动描述、持续时间或结束时间，其中持续时间或结束时间必须提供其中一个.

    Args:        
        user_id: 用户指定的用户ID名称, 当没有明确指定时为'测试员', 不能为空且优先取用户提示的用户ID名称, 不可以包含以下列表中任一元素:['姐姐','长公主','哥哥','大王子','弟弟','小王子','妹妹','小公主','妈妈','爸爸','奶奶', '爷爷'], 默认为'测试员'.
        role_name: 一位角色或多位角色名字，必须从以下列表中选出最接近的元素:['姐姐','长公主','哥哥','大王子','弟弟','小王子','妹妹','小公主','妈妈','爸爸','奶奶', '爷爷'], 当用户输入多个角色时用+连接，如'姐姐+妈妈'表示姐姐和妈妈同时参加.
        start_datetime: 日程开始时间，格式为 'YYYY-MM-DD HH:MM'
        activity: 日程活动简短描述, 如'舞蹈培训在索菲拉'
        duration: 日程持续时间（分钟），可选
        end_datetime: 日程结束时间，格式为 'YYYY-MM-DD HH:MM'，可选
    """
    # 输入参数预处理
    user_id = user_id.strip()
    role_name_raw = role_name
    role_name = ""
    if "+" in role_name_raw:
        role_name_list = role_name_raw.split("+")
        role_name_list = list(sorted(role_name_list))
        for rname in role_name_list:
            rname = role_name_preprocess(rname)
            if role_name != "":
                role_name = role_name + "+" + rname
            else:
                role_name = rname
    else:
        role_name = role_name_preprocess(role_name_raw)
    

    # 读取或创建CSV文件
    df = read_or_create_schedule_csv(file_path)
    print("df=\n", df.to_markdown())
    
    # 验证start_datetime格式
    try:
        start_datetime = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M')
    except ValueError:
        raise ValueError("start_datetime格式错误，应为 'YYYY-MM-DD HH:MM'")
    
    
    # 计算end_datetime（如果未提供）
    if end_datetime is None and duration is not None:
        try:
            duration = int(duration)
        except ValueError:
            raise ValueError("duration必须是一个整数")
        end_datetime = start_datetime + timedelta(minutes=duration)
    elif end_datetime is not None:
        try:
            end_datetime = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M')
            duration = int((end_datetime - start_datetime).total_seconds() / 60)
        except ValueError:
            raise ValueError("end_datetime格式错误，应为 'YYYY-MM-DD HH:MM'")
    else:
        raise ValueError("必须提供duration或end_datetime")
    
    # 提取date, year_month, weekday
    date = start_datetime.strftime('%Y-%m-%d')
    year_month = start_datetime.strftime('%Y-%m')
    weekday = start_datetime.strftime('%A')
    
    # 创建新的日程条目
    new_entry = {
        'user_id': user_id,
        'role_name': role_name,
        'date': date,
        'year_month': year_month,
        'weekday': weekday,
        'start_datetime': start_datetime.strftime('%Y-%m-%d %H:%M'),
        'end_datetime': end_datetime.strftime('%Y-%m-%d %H:%M'),
        'activity': activity,
        'duration': duration
    }
    print("new_entry=\n", new_entry)
    
    # 检查时间冲突
    conflict_condition = (
        (df['user_id'].str.contains(user_id)) & (
        (df['role_name'].str.contains(role_name)) &
        ((df['start_datetime'] <= start_datetime.strftime('%Y-%m-%d %H:%M')) & (df['end_datetime'] > start_datetime.strftime('%Y-%m-%d %H:%M'))) |
        ((df['start_datetime'] < end_datetime.strftime('%Y-%m-%d %H:%M')) & (df['end_datetime'] >= end_datetime.strftime('%Y-%m-%d %H:%M')))
        )
    )
    print("conflict_condition=\n", conflict_condition)

    
    if df[conflict_condition].empty:
        # 没有时间冲突，将新的日程条目添加到DataFrame
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)

        ##如果df为非空，则按role_name, start_datetime排序
        if not df.empty:
            df = df.sort_values(by=['user_id', 'role_name', 'start_datetime']).reset_index(drop=True)
        
        # 保存DataFrame到CSV文件
        df.to_csv(file_path, index=False)
        
        result = "按您的要求，已添加到日程表."
    
        return str({"success": True, "result": result})
    
    else:
        # 存在时间冲突，返回冲突的数据行计划内容，并提示用户时间冲突
        conflicting_entries = df[conflict_condition]
        return f"提示用户时间冲突，建议调整新计划时间或者调整以下已有计划时间:\n{conflicting_entries.to_markdown()}"


# 查询日程安排
@mcp.tool()
def query_schedule(user_id: str,
                   role_name: str=None,
                   date: str=None,
                   year_month: str=None,
                   weekday: str=None,
                   start_datetime: str=None,
                   end_datetime: str=None,
                   activity: str=None,
                   duration: int=None,
                   ):
    """查询日程安排, 输入参数包括用户ID、角色名字、日程日期、日程年月、日程星期几、日程开始时间、日程结束时间、活动描述、日程持续时间，提供其中若干个信息，必须提供至少一个，用于查询日程安排。

    Args:
        user_id: 用户指定的用户ID名称, 当没有明确指定时为'测试员', 不能为空且优先取用户提示的用户ID名称, 不可以包含以下列表中任一元素:['姐姐','长公主','哥哥','大王子','弟弟','小王子','妹妹','小公主','妈妈','爸爸','奶奶', '爷爷'], 默认为'测试员'.
        role_name: 一位角色或多位角色名字，如有必须从以下列表中选出最接近的元素:['姐姐','长公主','哥哥','大王子','弟弟','小王子','妹妹','小公主','妈妈','爸爸','奶奶', '爷爷'], 当用户输入多个角色时用+连接，如'姐姐+妈妈'表示姐姐和妈妈同时参加. 可选
        date: 日程日期，格式为 'YYYY-MM-DD'，可选
        year_month: 日程年月，格式为 'YYYY-MM'，可选
        weekday: 日程星期几，格式为'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'，可选
        start_datetime: 日程开始时间，格式为 'YYYY-MM-DD HH:MM'，可选
        end_datetime: 日程结束时间，格式为 'YYYY-MM-DD HH:MM'，可选
        activity: 日程活动简短描述, 如'舞蹈培训在索菲拉'，可选
        duration: 日程持续时间（分钟），可选
    """
    user_id = user_id.strip()
    
    if role_name is not None:
        # 输入参数预处理        
        role_name_raw = role_name
        role_name = ""
        if "+" in role_name_raw:
            role_name_list = role_name_raw.split("+")
            role_name_list = list(sorted(role_name_list))
            for rname in role_name_list:
                rname = role_name_preprocess(rname)
                if role_name != "":
                    role_name = role_name + "+" + rname
                else:
                    role_name = rname
        else:
            role_name = role_name_preprocess(role_name_raw)
    print("role_name=", role_name)

    # 读取CSV文件
    df = read_or_create_schedule_csv(file_path)


    ## 检查输入参数格式
    if role_name is not None:
        role_name = str(role_name)
    if date is not None:
        try:
            date = datetime.strptime(date, '%Y-%m-%d')
            date = datetime.strftime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("date格式错误，应为 'YYYY-MM-DD'")
    if year_month is not None:
        try:
            year_month = datetime.strptime(year_month, '%Y-%m')
            year_month = datetime.strftime(year_month, '%Y-%m')
        except ValueError:
            raise ValueError("year_month格式错误，应为 'YYYY-MM'")
    if weekday is not None:
        weekday = str(weekday)
    if start_datetime is not None:
        try:
            start_datetime = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M')
            start_datetime = datetime.strftime(start_datetime, '%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError("start_datetime格式错误，应为 'YYYY-MM-DD HH:MM'")
    if end_datetime is not None:
        try:
            end_datetime = datetime.strptime(end_datetime, '%Y-%m-%d %H:%M')
            end_datetime = datetime.strftime(end_datetime, '%Y-%m-%d %H:%M')
        except ValueError:
            raise ValueError("end_datetime格式错误，应为 'YYYY-MM-DD HH:MM'")
    if activity is not None:
        activity = str(activity)
    if duration is not None:
        try:
            duration = int(duration)
        except ValueError:
            raise ValueError("duration必须是一个整数")

    # 筛选条件
    conditions = []
    
    conditions.append(df['user_id'] == user_id)
    if role_name is not None:
        conditions.append(df['role_name'] == role_name)
    if date is not None:
        conditions.append(df['date'] == date)
    if year_month is not None:
        conditions.append(df['year_month'] == year_month)
    if weekday is not None:
        conditions.append(df['weekday'] == weekday)
    if start_datetime is not None:
        conditions.append(df['start_datetime'] == start_datetime)
    if end_datetime is not None:
        conditions.append(df['end_datetime'] == end_datetime)
    if activity is not None:
        conditions.append(df['activity'].str.contains(activity))
    if duration is not None:
        conditions.append(df['duration'] == duration)
    
    if conditions:
        combined_condition = conditions[0]
        for condition in conditions[1:]:
            combined_condition = combined_condition & condition
        df = df[combined_condition]

    ##如果df为非空，则按role_name, start_datetime排序
    if not df.empty:
        df = df.sort_values(by=['user_id', 'role_name', 'start_datetime']).reset_index(drop=True)
    
    result = f"按您的要求，已查询到日程如下:\n{df.to_markdown()}"
    
    return str({"success": True, "result": result})


# 更新日程安排
@mcp.tool()
def update_schedule(user_id: str,
                    role_name: str,
                    activity: str,
                    start_datetime_new: str,
                    end_datetime_new: str=None,
                    duration_new: int=None):
    """更新日程安排, 输入参数包括角色名字、活动描述、更新的日程开始时间、更新的日程结束时间、更新的日程持续时间，必须提供角色名字、活动描述、更新的日程开始时间, 其中更新的日程结束时间、更新的日程持续时间为可选输入，用于更新日程安排。

    Args:
        user_id: 用户指定的用户ID名称, 当没有明确指定时为'测试员', 不能为空且优先取用户提示的用户ID名称, 不可以包含以下列表中任一元素:['姐姐','长公主','哥哥','大王子','弟弟','小王子','妹妹','小公主','妈妈','爸爸','奶奶', '爷爷'], 默认为'测试员'.
        role_name: 一位角色或多位角色名字，必须从以下列表中选出最接近的元素:['姐姐','长公主','哥哥','大王子','弟弟','小王子','妹妹','小公主','妈妈','爸爸','奶奶', '爷爷'], 当用户输入多个角色时用+连接，如'姐姐+妈妈'表示姐姐和妈妈同时参加. 
        activity: 日程活动简短描述, 如'舞蹈培训'
        start_datetime_new: 更新的日程开始时间，格式为 'YYYY-MM-DD HH:MM'
        end_datetime_new: 更新的日程结束时间，格式为 'YYYY-MM-DD HH:MM'，可选
        duration_new: 更新的日程持续时间（分钟），可选
    """
    # 输入参数预处理
    user_id = user_id.strip()
    role_name_raw = role_name
    role_name = ""
    if "+" in role_name_raw:
        role_name_list = role_name_raw.split("+")
        role_name_list = list(sorted(role_name_list))
        for rname in role_name_list:
            rname = role_name_preprocess(rname)
            if role_name != "":
                role_name = role_name + "+" + rname
            else:
                role_name = rname
    else:
        role_name = role_name_preprocess(role_name_raw)
    
    # 读取CSV文件
    df = read_or_create_schedule_csv(file_path)
    
    # 验证start_datetime_new格式
    try:
        start_datetime_new = datetime.strptime(start_datetime_new, '%Y-%m-%d %H:%M')
    except ValueError:
        raise ValueError("start_datetime_new格式错误，应为 'YYYY-MM-DD HH:MM'")    
    
    # 构建匹配条件
    match_condition = (df['user_id'] == user_id) & (df['role_name'] == role_name) & (df['activity'].str.contains(activity, na=False))
    
    # 查找匹配的行
    matching_rows = df[match_condition]
    
    if matching_rows.empty:
        return "未找到匹配的日程条目"
    
    ## TODO: 基于matching_rows第一行信息，计算end_datetime_new
    ## 获取matching_rows第一行的start_datetime, end_datetime值并计算duration=end_datetime-start_datetime,转换duration单位为分钟
    if (end_datetime_new is None) and (duration_new is None):
        duration = (int(matching_rows.iloc[0]['end_datetime'].split()[1].split(':')[0]) - int(matching_rows.iloc[0]['start_datetime'].split()[1].split(':')[0])) * 60 + (int(matching_rows.iloc[0]['end_datetime'].split()[1].split(':')[1]) - int(matching_rows.iloc[0]['start_datetime'].split()[1].split(':')[1]))
        duration_new = int(duration)
        end_datetime_new = start_datetime_new + timedelta(minutes=duration)
        print("To be updated end_datetime_new= ", end_datetime_new)
    elif (end_datetime_new is not None) and (duration_new is None):
        try:
            end_datetime_new = datetime.strptime(end_datetime_new, '%Y-%m-%d %H:%M')
            duration_new = int((end_datetime_new - start_datetime_new).total_seconds() / 60)
        except ValueError:
            raise ValueError("end_datetime_new格式错误，应为 'YYYY-MM-DD HH:MM'")
    elif (end_datetime_new is None) and (duration_new is not None):
        try:
            duration_new = int(duration_new)
        except ValueError:
            raise ValueError("duration_new必须是一个整数")
        end_datetime_new = start_datetime_new + timedelta(minutes=duration_new)
        print("To be updated end_datetime_new= ", end_datetime_new)

    print(start_datetime_new, end_datetime_new, duration_new)
    # 提取date, year_month, weekday
    date = start_datetime_new.strftime('%Y-%m-%d')
    year_month = start_datetime_new.strftime('%Y-%m')
    weekday = start_datetime_new.strftime('%A')

    # 检查时间冲突
    df_temp = df[~match_condition]
    conflict_condition = (
        (df['user_id'].str.contains(user_id)) & (
        (df_temp['role_name'].str.contains(role_name)) &
        ((df_temp['start_datetime'] <= start_datetime_new.strftime('%Y-%m-%d %H:%M')) & (df_temp['end_datetime'] > start_datetime_new.strftime('%Y-%m-%d %H:%M'))) |
        ((df_temp['start_datetime'] < end_datetime_new.strftime('%Y-%m-%d %H:%M')) & (df_temp['end_datetime'] >= end_datetime_new.strftime('%Y-%m-%d %H:%M')))
        )
    )
    
    if df_temp[conflict_condition].empty:
        # 更新匹配行的start_datetime, date, year_month, weekday
        df.loc[match_condition, 'start_datetime'] = start_datetime_new.strftime('%Y-%m-%d %H:%M')
        df.loc[match_condition, 'end_datetime'] = end_datetime_new.strftime('%Y-%m-%d %H:%M')
        df.loc[match_condition, 'duration'] = duration_new
        df.loc[match_condition, 'date'] = date
        df.loc[match_condition, 'year_month'] = year_month
        df.loc[match_condition, 'weekday'] = weekday

        ##如果df为非空，则按role_name, start_datetime排序
        if not df.empty:
            df = df.sort_values(by=['user_id', 'role_name', 'start_datetime']).reset_index(drop=True)
        
        # 保存更新后的DataFrame到CSV文件
        df.to_csv(file_path, index=False)
        
        result = "按您的要求，已更新了日程表."
    
        return str({"success": True, "result": result})
    
    else:
        # 存在时间冲突，返回冲突的数据行计划内容，并提示用户时间冲突
        conflicting_entries = df_temp[conflict_condition]
        return f"时间冲突，建议调整新计划时间或者调整以下已有计划时间:\n{conflicting_entries.to_markdown()}"


# 删除日程安排
@mcp.tool()
def delete_schedule(user_id: str,
                    role_name: str=None,
                    activity: str=None,
                    specific_role_name: str=None):
    """删除日程安排，输入参数包括角色名字、活动描述、特别指定一位需删除的角色名字，提供其中若干个信息，必须提供至少一个，用于删除日程安排。

    Args:
        user_id: 用户指定的用户ID名称, 当没有明确指定时为'测试员', 不能为空且优先取用户提示的用户ID名称, 不可以包含以下列表中任一元素:['姐姐','长公主','哥哥','大王子','弟弟','小王子','妹妹','小公主','妈妈','爸爸','奶奶', '爷爷'], 默认为'测试员'.
        role_name: 一位角色或多位角色名字，如有必须从以下列表中选出最接近的元素:['姐姐','长公主','哥哥','大王子','弟弟','小王子','妹妹','小公主','妈妈','爸爸','奶奶', '爷爷'], 当用户输入多个角色时用+连接，如'姐姐+妈妈'表示姐姐和妈妈同时参加. 可选
        activity: 日程活动简短描述, 如'舞蹈培训在索菲拉'，可选
        specific_role_name: 特别指定一位需删除的角色名字，用于从日程表role_name字段的多位角色中删除这一位角色，可选
    """

    user_id = user_id.strip()

    if role_name is not None:
        # 输入参数预处理        
        role_name_raw = role_name
        role_name = ""
        if "+" in role_name_raw:
            role_name_list = role_name_raw.split("+")
            role_name_list = list(sorted(role_name_list))
            for rname in role_name_list:
                rname = role_name_preprocess(rname)
                if role_name != "":
                    role_name = role_name + "+" + rname
                else:
                    role_name = rname
        else:
            role_name = role_name_preprocess(role_name_raw)


    # 读取CSV文件
    df = read_or_create_schedule_csv(file_path)
    
    # 构建匹配条件
    match_condition = pd.Series([True] * len(df))

    match_condition &= df['user_id'] == user_id
    if role_name is not None:
        match_condition &= df['role_name'] == role_name
    if activity is not None:
        match_condition &= df['activity'].str.contains(activity, na=False)
    
    # 查找匹配的行
    matching_rows = df[match_condition]
    
    if matching_rows.empty:
        return "未找到匹配的日程条目"
    
    # 如果指定了specific_role_name，则更新role_name字段中包含specific_role_name的行
    if specific_role_name is not None:
        df.loc[match_condition, 'role_name'] = df.loc[match_condition, 'role_name'].str.replace(f'+{specific_role_name}', '', regex=False)
        df.loc[match_condition, 'role_name'] = df.loc[match_condition, 'role_name'].str.replace(f'{specific_role_name}+', '', regex=False)
    else:
        # 删除匹配的行
        df = df[~match_condition]
    
    ##如果df为非空，则按role_name, start_datetime排序
    if not df.empty:
        df = df.sort_values(by=['user_id', 'role_name', 'start_datetime']).reset_index(drop=True)
    
    # 保存更新后的DataFrame到CSV文件
    df.to_csv(file_path, index=False)

    result = "按您的要求，已从日程表中删除."
    
    return str({"success": True, "result": result})



def main() -> None:

    mcp.run(transport='stdio')
    print("Hello from schedule-mcp-server!")
