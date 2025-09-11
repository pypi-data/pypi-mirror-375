from itgeeker.geekermaster_parse import parse_company_name, parse_school_name, parse_gender_name


ban_company_list = ['上海奇客罗方智能科技有限公司', '奇客罗方智能科技']
print(parse_company_name('来自 上海奇客罗方智能科技有限公司 的计技术奇客', ban_company_list))


from itgeeker import geekermaster_parse
ban_company_list = ['奇客罗方智能科技']
print(geekermaster_parse.parse_company_name('来自 上海奇客罗方智能科技有限公司 的计技术奇客', ban_company_list))


# code to test parse_school_name
print(parse_school_name('上海交通大学'))

print('\n' + '/*--*/' * 18)
# code to test parse_gender_name
print(parse_gender_name(' 男 '))
print(parse_gender_name(' 男生'))
