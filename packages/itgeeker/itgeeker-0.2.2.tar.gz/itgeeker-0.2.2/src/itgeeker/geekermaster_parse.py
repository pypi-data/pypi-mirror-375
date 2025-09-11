# -*- coding: utf-8 -*-
import re

####################### cv parse #######################
# extract company pattern_none_greedy
def filter_co_name(co_name, ban_company_list):
    if ban_company_list:
        if co_name not in ban_company_list:
            if co_name.endswith('集团'):
                if 3 < len(co_name) < 10:
                    return co_name
            elif 5 < len(co_name) < 18:
                return co_name
            else:
                return False
    else:
        if co_name.endswith('集团'):
            if 3 < len(co_name) < 10:
                return co_name
        elif 5 < len(co_name) < 18:
            return co_name
        else:
            return False

def parse_company_name(text_str, ban_company_list):
    pattern_none_greedy = re.compile(r'(\w+?)(公司|集团)(\s)')
    if text_str:
        if isinstance(text_str, bytes):
            text_str = text_str.decode('utf-8')
            print('convert bytes text_str to string @geekermaster_api_parse')
        extract_res_list = re.findall(pattern_none_greedy, text_str)
        print('extract_res_list: %s' % extract_res_list)
        if extract_res_list:
            found_company_list = []
            for erl in extract_res_list:
                found_company_list.append("".join(erl))
            print('found_company_list: %s' % found_company_list)
            if found_company_list:
                final_list = []
                # ban_company_list = generate_ban_company_list()
                for fcl in found_company_list:
                    fcl = fcl.strip()
                    filtered_name = filter_co_name(fcl, ban_company_list)
                    if filtered_name:
                        final_list.append(filtered_name)
                    # if fcl.endswith('集团'):
                    #     if 3 < len(fcl) < 10:
                    #         final_list.append(fcl)
                    # elif 5 < len(fcl) < 18:
                    #     if ban_company_list:
                    #         if fcl not in ban_company_list:
                    #             final_list.append(fcl)
                    #     else:
                    #         final_list.append(fcl)
                print("will return final_list: %s", final_list)
                if final_list:
                    return final_list[0]
    return False

def parse_school_name(text_str):
    pattern_none_greedy = re.compile(r'(\w+?)(大学)')
    if text_str:
        if isinstance(text_str, bytes):
            text_str = text_str.decode('utf-8')
            print('convert text_str to string @geekermaster_api_parse')
        extract_res_list = re.findall(pattern_none_greedy, text_str)
        print('extract_res_list: %s' % extract_res_list)
        if extract_res_list:
            found_school_list = []
            for erl in extract_res_list:
                found_school_list.append("".join(erl))
            print('found_school_list: %s' % found_school_list)
            if found_school_list:
                final_list = []
                # ban_school_list = generate_ban_school_list()
                for fcl in found_school_list:
                    # if fcl.strip() not in ['有限公司', '目前公司', '所在公司', '给贵公司']:
                    if 3 < len(fcl.strip()) < 12:
                        # if ban_school_list:
                        #     if fcl.strip() not in ban_school_list:
                        #         final_list.append(fcl)
                        # else:
                        final_list.append(fcl)
                print("will return final_list: %s", final_list)
                if final_list:
                    return final_list[0]
    return False

def parse_gender_name(text_str):
    pattern_none_greedy = re.compile(r'(\s)(男|女|male|female)(\s)', re.I)
    if text_str:
        if isinstance(text_str, bytes):
            text_str = text_str.decode('utf-8')
            print('parse text_str for gender')
        extract_res_list = re.findall(pattern_none_greedy, text_str.lower())
        print('extract_res_list: %s' % extract_res_list)
        if extract_res_list:
            found_gender_list = []
            for erl in extract_res_list:
                found_gender_list.append("".join(erl))
            print('found_gender_list: %s' % found_gender_list)
            if found_gender_list:
                final_list = []
                # ban_gender_list = generate_ban_gender_list()
                for fcl in found_gender_list:
                    final_list.append(fcl.strip())
                print("will return final_list: %s", final_list)
                if final_list[0] in ['男', 'Male', 'male']:
                    return '男'
                elif final_list[0] in ['女', 'Female', 'female']:
                    return '女'
    return False
