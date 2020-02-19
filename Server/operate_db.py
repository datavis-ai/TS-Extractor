# coding: utf-8
import sqlite3
import numpy as np


# 获得指定数据库中表格的字段.
def get_db_table_fields(dbname="DB/Coauthor_Visualization.db", table_name="node"):

    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    cursor = db.cursor()
    # cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    # cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
    # tables = cursor.fetchall()  # Tables 为元组列表 [('author',), ('paper',), ('coauthor',), ('author2paper',)]
    # print("tables")  #[('author',), ('paper',), ('coauthor',), ('author2paper',)]
    # print(tables)  #[('author',), ('paper',), ('coauthor',), ('author2paper',)]
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()  # Tables 为元组列表 [('author',), ('paper',), ('coauthor',), ('author2paper',)]
    db_tables_list = []  # 对应数据库中,除了node + edge之外的表, e.g.[publictions]
    for i in tables:
        tb = i[1]
        if tb != "node" and tb != "edge":
           db_tables_list.append(tb)

    # table_name = tables[which_table][0]  # 获取第一个表名 author表.
    cursor.execute("SELECT * FROM {}".format(table_name))

    col_name_list = [tuple_[0] for tuple_ in cursor.description]  # 获得表中的字段.
    col_name_type_list = {}  # col_name_list中各元素对应的类型.
    counter = -1
    for each_field in col_name_list:
        counter += 1
        type_field = "select typeof(" + each_field + ") from node limit 0,1"  # limit 0,1 表示从第1条开始的一条记录.
        cursor.execute(type_field)
        data = cursor.fetchall()
        type_each_field = data[0][0]
        # print(type_each_field)
        col_name_type_list[col_name_list[counter]] = type_each_field
    db.close()
    """
    返回格式:
    col_name_list=['id', 'name', 'institution', 'num_papers', 'num_citation', 'H_index', 'P_index', 'UP_index', 'interests']
    col_name_type_list={'num_citation': 'integer', 'P_index': 'real', 'interests': 'text', 'num_papers': 'integer', 'UP_index': 'real', 'H_index': 'integer', 'name': 'text', 'id': 'integer', 'institution': 'text'}
    """
    return col_name_list, col_name_type_list, db_tables_list


# TODO:获得指定数据库的对应字段的值.目前需要定制,即不同数据库,情况是不一样的.
def get_db_field_values(dbname=None, field=None):
    """
    :param dbname:
    :param field:
    :return: sort_result: [{"value":XXX, "number":XXX}, ...], 如果是字符串类型,按照出现次数降序排列,数值类型,则按照大小降序排列.
    """
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    cursor = db.cursor()
    results = set()
    # if dbname == "DB/Coauthor_Visualization.db":
    sql = "select " + field + " from node"
    cursor.execute(sql)
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果
    for each_one in data:
        results.add(each_one[0])
    results = list(results)  # [XXX, XXX, ...,XXX]

    type_field = ""  # 用于记录字段的类型.

    # 针对含有多个值的,比如兴趣,机构,按照分号划分,统计相同的iterm的数量.
    set_iterms = set()  # iterm的集合
    list_iterms = list()  # 所有iterm的列表.
    """
    备注:数据库表中,处理数据缺失的情况如下.
        1. 如果是text类型,则填入NULL.
        2. 如果是int类型,则填入0.
        3. 如果是float类型,则填入0.0.
        数据库表常见的类型也就这几种: text, real, int.
            
    """
    for each_one in results:  # TODO: 明天:如果是number类型则按照其大小排列,字符串则是按照出现频次排序.

        if isinstance(each_one, str):  # 如果是字符串.
            type_field = "string"
            if each_one.lower() != "null":  # 排除掉"NULL"
                each_one = each_one.strip()
                each_one = each_one.split(";")
                for i in each_one:
                    i = i.lower()  # 转化成小写
                    list_iterms.append(i)
                    set_iterms.add(i)
        elif isinstance(each_one, float):  # 如果是小数,数据库中如果没有值,则置0.0,故没有"NULL".
            type_field = "float"
            set_iterms.add(each_one)

        elif isinstance(each_one, int):  # 如果是整数.数据库中如果没有值,则置0,故没有"NULL".
            type_field = "int"
            set_iterms.add(each_one)

        else:  # 如果是其他类型,比如bool型.
            type_field = "bool"
            set_iterms.add(each_one)

    sort_result = []  # 用于装排序好的结果.

    if type_field == "string":  # 如果是字符串类型.
        # 统计每个iterm的数量.
        each_iterm_list = []  # 存放iterm的列表 [XXX, XXX, ...]
        num_each_iterm_list = []  # 每个iterm的数量,与each_iterm_list一一对应. [11, 22, ...]

        for each_one in set_iterms:
            each_iterm_list.append(each_one)
            num_ = list_iterms.count(each_one)
            num_each_iterm_list.append(num_)

        sort_result = sort_for_results(each_iterm_list=each_iterm_list, num_each_iterm_list_=num_each_iterm_list)  # 获得排序好的字段对应的值.

    elif type_field == "int" or type_field == "float":
        temp_list = list(set_iterms)  # 列表化.
        sort_result = sort_for_int_float(int_or_float_list=temp_list)
    else:  # 可能是bool型,暂时没有遇到.
        for i in set_iterms:
            temp_obj = {"value": i}
            sort_result.append(temp_obj)

    return sort_result  # [{"value":XXX, "number":XXX}, ...]


# 为int+float进行降序排列.
def sort_for_int_float(int_or_float_list=None):
    results = []
    temp = np.array(int_or_float_list)
    # print(temp)
    for i in range(len(int_or_float_list)):
        index_max = temp.argmax()
        value_max = int_or_float_list[index_max]
        obj_max = {"value": str(value_max)}  # str(value_max)
        results.append(obj_max)
        temp[index_max] = -1

    return results


# 按照字符串出现次数进行排序.
def sort_for_results(each_iterm_list, num_each_iterm_list_):
    sort_iterm_list = []  # 最后获得一个对象列表,越靠前的对象其出现次数越多.这个可以写在论文里面.
    num_each_iterm_list = np.array(num_each_iterm_list_)
    for each_one in range(len(num_each_iterm_list)):
        index_max = num_each_iterm_list.argmax()
        # TODO: 原来是num_each_iterm_list[index_max]造成jsonify(data)无法将对象转换成字符串.
        value_max = num_each_iterm_list_[index_max]
        iterm_max = each_iterm_list[index_max]

        temp_obj = {"value": iterm_max, "number": value_max}
        sort_iterm_list.append(temp_obj)
        """
        注意:不能清成0,应该清成-1.否则对于[11, 2, 0, 0, 0, 0]出现结果中有多项一样的情况.比如:        
            输入:
                ["A", "b", "c"]
                [22, 0, 0]
            输出:
                [{'number': 10, 'value': 'A'}, {'number': 10, 'value': 'A'}, {'number': 10, 'value': 'A'}]
        """
        num_each_iterm_list[index_max] = -1

    # print(sort_iterm_list)
    return sort_iterm_list


# 根据条件检索数据库,获得匹配的数据.
def match_db_condition(dbName=None, which_table=None, conditions=None, table_width="120"):
    """
    :param dbName:数据库名称.
    :param which_table: 数据库间中的哪一张表.
    :param conditions:数据库表字段. [{selectionfield:"All", keyWord:""}, ...]
    :param table_width:前端表格宽度.
    :return: 返回匹配上的数据记录(节点,即作者).
    """
    # todo:不适用于这种情况:selectionfield:"xxx", keyWord:"xxx;xxx",即keyWord含有多个值并且用分号分隔的情况.
    # todo:以后可以扩展成属性探索中节点匹配的方式来匹配结果.
    # fields_list, fields_type_list = get_db_table_fields(dbname=dbname, table_name="node")
    db = sqlite3.connect(dbName)
    cursor = db.cursor()
    table_name = which_table  # 获取表名: node表.

    tableheader = []  # [{}, {}, ...]
    tabledata = []  # [{}, {}, ...]

    all_set = set()
    col_name_list, fields_type_list, _ = get_db_table_fields(dbname=dbName, table_name=table_name)

    condition_len = len(conditions)  # 条件的数量.
    if condition_len == 1:  # fixme:单条件查询时,分为两种情况:field='All' + field='xxx'
        con_obj = conditions[0]  # e.g.{selectionfield:"All", keyWord:""}
        dbfield = con_obj["selectionfield"]
        dbfieldvalue = con_obj["keyWord"]

        if dbfield == "All":  # fixme: 如果关键字是All,则只考虑查询text类型的字段.

            for each_one in col_name_list:

                if fields_type_list[each_one] == "text":  # 如果字段是text类型.则查询一波.
                    sql = "select * from " + which_table + " where " + each_one + " like ?"  # 模糊查询.
                    # print(sql)
                    value_condition = "%" + dbfieldvalue + "%"
                    # print(value_condition)
                    cursor.execute(sql, (value_condition,))
                    data = cursor.fetchall()  # 使用这种方式取出所有查询结果 data=[(xx, xx, ...,xx),...]
                    # print("lvchenjing")
                    # print(data)
                    for i in data:
                        all_set.add(i)
            for each_one in col_name_list:  # ['id', 'name', 'institution', 'num_papers', 'num_citation', 'H_index', 'P_index', 'UP_index', 'interests']
                temp_obj = {}
                temp_obj["prop"] = each_one
                temp_obj["label"] = each_one
                temp_obj["width"] = table_width  # 可以根据字符的数量确定宽度.
                tableheader.append(temp_obj)
            # all_list = list(all_set)
            for each_one in all_set:  # data=[(xx, xx, ...,xx),...]
                temp_obj = {}
                for i in range(len(each_one)):  # each_one=(xx, xx, ...,xx)
                    key_obj = col_name_list[i]
                    value = each_one[i]
                    temp_obj[key_obj] = value
                tabledata.append(temp_obj)

        else:

            # col_name_list中的字段与下面的数据是一一对应的.
            sql = "select * from " + which_table + " where " + dbfield + " like ?"  # 模糊查询.
            value_condition = "%" + dbfieldvalue + "%"

            cursor.execute(sql, (value_condition,))
            data = cursor.fetchall()  # 使用这种方式取出所有查询结果
            """
            表头:
               e.g.
               [{prop:"date",
                  label:"日期",
                  width:"120"        
                }]
            表格数据:
                [{},{},...{}]
            """
            # 构建表格数据: 表头+表格记录.

            for each_one in col_name_list:  # ['id', 'name', 'institution', 'num_papers', 'num_citation', 'H_index', 'P_index', 'UP_index', 'interests']
                temp_obj = {}
                temp_obj["prop"] = each_one
                temp_obj["label"] = each_one
                temp_obj["width"] = table_width  # 可以根据字符的数量确定宽度.
                tableheader.append(temp_obj)

            for each_one in data:  # data=[(xx, xx, ...,xx),...]
                temp_obj = {}
                for i in range(len(each_one)):  # each_one=(xx, xx, ...,xx)
                    key_obj = col_name_list[i]
                    value = each_one[i]
                    temp_obj[key_obj] = value
                tabledata.append(temp_obj)

    if condition_len > 1:  # fixme:多条件查询时,分为两种情况: 含有field='All' + 不含field='All'
        conditions_field_is_all = []  # 条件中的字段是all, [{selectionfield:"All", keyWord:"xxx"},...]
        conditions_field_is_not_all = []  # 条件中字段不是all. [{selectionfield:"name", keyWord:"xxx"},...]
        for each_obj in conditions:  # [{}, {}, {}]
            selectionfield = each_obj["selectionfield"]
            if selectionfield != "":  # 非空.
                if selectionfield == "All":
                    conditions_field_is_all.append(each_obj)
                else:
                    conditions_field_is_not_all.append(each_obj)
        field_is_all_num = len(conditions_field_is_all)  # 字段="All"的数量.
        # 分为两种情况来处理:有all和无all.
        if field_is_all_num == 0:  # 无all, 则构成 and sql语句查询结果.
            cons_sql = ''
            select_sql = "select * from " + which_table + " where "
            conditions_num = len(conditions)
            counter = 0
            cons_val = []
            for each_obj in conditions:
                counter = counter + 1
                field = each_obj["selectionfield"]
                keyWord = each_obj["keyWord"]
                each_val_sql = "%" + keyWord + "%"
                cons_val.append(each_val_sql)
                if counter < conditions_num:
                    cons_sql = cons_sql + field + " like " + "?" + " and "
                else:
                    cons_sql = cons_sql + field + " like " + "?"

            sql = select_sql + cons_sql
            cons_val = tuple(cons_val)
            # print(sql)
            # print(cons_val)
            cursor.execute(sql, cons_val)
            data = cursor.fetchall()  # 使用这种方式取出所有查询结果
            """
            表头:
               e.g.
               [{prop:"date",
                  label:"日期",
                  width:"120"        
                }]
            表格数据:
                [{},{},...{}]
            """
            # 构建表格数据: 表头+表格记录.
            for each_one in col_name_list:  # ['id', 'name', 'institution', 'num_papers', 'num_citation', 'H_index', 'P_index', 'UP_index', 'interests']
                temp_obj = {}
                temp_obj["prop"] = each_one
                temp_obj["label"] = each_one
                temp_obj["width"] = table_width  # 可以根据字符的数量确定宽度.
                tableheader.append(temp_obj)

            for each_one in data:  # data=[(xx, xx, ...,xx),...]
                temp_obj = {}
                for i in range(len(each_one)):  # each_one=(xx, xx, ...,xx)
                    key_obj = col_name_list[i]
                    value = each_one[i]
                    temp_obj[key_obj] = value
                tabledata.append(temp_obj)

        else:  # fixme:有all,则取并集. 分为两种情况: 全是All, 部分All.
            is_not_all_num = len(conditions_field_is_not_all)
            if is_not_all_num > 0:  # fixme: 部分All.
                # fixme: 先对非All部分,用and查询出结果,然后用All部分查询出其结果,最后取交集.

                # fixme: 用and查询出非All部分的结果.
                cons_sql = ''
                select_sql = "select * from " + which_table + " where "
                conditions_num = len(conditions_field_is_not_all)
                counter = 0
                cons_val = []
                for each_obj in conditions_field_is_not_all:
                    counter = counter + 1
                    field = each_obj["selectionfield"]
                    keyWord = each_obj["keyWord"]
                    each_val_sql = "%" + keyWord + "%"
                    cons_val.append(each_val_sql)
                    if counter < conditions_num:
                        cons_sql = cons_sql + field + " like " + "?" + " and "
                    else:
                        cons_sql = cons_sql + field + " like " + "?"

                sql = select_sql + cons_sql
                cons_val = tuple(cons_val)
                cursor.execute(sql, cons_val)
                is_not_all_data = cursor.fetchall()  # 使用这种方式取出所有查询结果,is_not_all_data=[{}, {}, ...]

                # fixme: 查询出All部分的结果.
                part_all_data_list = []  # [set(), ...]
                for each_keyword_obj in conditions_field_is_all:  # [{selectionfield:"All", keyWord:""}, ...]
                    each_keyword = each_keyword_obj["keyWord"]  # 每一个关键词.
                    temp_set = set()
                    for each_one in col_name_list:  # ["id", "name", ...]
                        if fields_type_list[each_one] == "text":  # 如果字段是text类型.则查询一波.
                            sql = "select * from " + which_table + " where " + each_one + " like ?"  # 模糊查询.
                            value_condition = "%" + each_keyword + "%"
                            cursor.execute(sql, (value_condition,))
                            data = cursor.fetchall()  # 使用这种方式取出所有查询结果 data=[(xx, xx, ...,xx),...]
                            # part_all_data_list.append(data)
                            for i in data:
                                temp_set.add(i)
                    part_all_data_list.append(temp_set)
                new_temp_set = set(is_not_all_data)
                part_all_data_list.append(new_temp_set)
                data = set.intersection(*part_all_data_list)  # [(xx, xx, ...,xx), ...]

                # 构建表格数据: 表头+表格记录.
                for each_one in col_name_list:  # ['id', 'name', 'institution', 'num_papers', 'num_citation', 'H_index', 'P_index', 'UP_index', 'interests']
                    temp_obj = {}
                    temp_obj["prop"] = each_one
                    temp_obj["label"] = each_one
                    temp_obj["width"] = table_width  # 可以根据字符的数量确定宽度.
                    tableheader.append(temp_obj)

                for each_one in data:  # data=[(xx, xx, ...,xx),...]
                    temp_obj = {}
                    for i in range(len(each_one)):  # each_one=(xx, xx, ...,xx)
                        key_obj = col_name_list[i]
                        value = each_one[i]
                        temp_obj[key_obj] = value
                    tabledata.append(temp_obj)

            else:  # fixme: 全部是All.
                part_all_data_list = []  # [set(), ...]
                for each_keyword_obj in conditions_field_is_all:  # [{selectionfield:"All", keyWord:""}, ...]
                    each_keyword = each_keyword_obj["keyWord"]  # 每一个关键词.
                    temp_set = set()
                    for each_one in col_name_list:  # ["id", "name", ...]
                        if fields_type_list[each_one] == "text":  # 如果字段是text类型.则查询一波.
                            sql = "select * from " + which_table + " where " + each_one + " like ?"  # 模糊查询.
                            value_condition = "%" + each_keyword + "%"
                            cursor.execute(sql, (value_condition,))
                            data = cursor.fetchall()  # 使用这种方式取出所有查询结果 data=[(xx, xx, ...,xx),...]
                            # part_all_data_list.append(data)
                            for i in data:
                                temp_set.add(i)
                    part_all_data_list.append(temp_set)

                data = set.intersection(*part_all_data_list)  # [(xx, xx, ...,xx), ...]
                # 构建表格数据: 表头+表格记录.
                for each_one in col_name_list:  # ['id', 'name', 'institution', 'num_papers', 'num_citation', 'H_index', 'P_index', 'UP_index', 'interests']
                    temp_obj = {}
                    temp_obj["prop"] = each_one
                    temp_obj["label"] = each_one
                    temp_obj["width"] = table_width  # 可以根据字符的数量确定宽度.
                    tableheader.append(temp_obj)

                for each_one in data:  # data=[(xx, xx, ...,xx),...]
                    temp_obj = {}
                    for i in range(len(each_one)):  # each_one=(xx, xx, ...,xx)
                        key_obj = col_name_list[i]
                        value = each_one[i]
                        temp_obj[key_obj] = value
                    tabledata.append(temp_obj)

    return tableheader, tabledata


# fixme:从指定数据库中读取"edge"表.
def read_table_edge_from_db(dbname):
    dbname = dbname
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    print("Opened database successfully")
    cursor.execute("select source, target, weight, source_name, target_name from edge")  # 从edge表中读取边.
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果

    edges_list_with_weight = []  # 带权重的边.[(source, target, weight), ...]
    nodes_set = set()
    nodes_id_list = []  # 图中节点id的列表.
    nodes_name_list = []  # 图中节点id对应的名字(label).
    links_list = []  # 用于添加到全局图中.
    # test_id = set()

    for each_edge in data:
        # print(each_edge)
        edges_list_with_weight.append(each_edge[:3])  # [(source, target, weight), ...]
        source = each_edge[0]
        target = each_edge[1]
        # weight = each_edge[2]
        source_name = each_edge[3]
        target_name = each_edge[4]
        nodes_set.add((source, source_name))
        nodes_set.add((target, target_name))
        # test_id.add(source)
        # test_id.add(target)
    for each_iterm in nodes_set:
        node = each_iterm[0]
        name = each_iterm[1]
        nodes_id_list.append(node)
        nodes_name_list.append(name)

    for edge in edges_list_with_weight:
        source = edge[0]
        target = edge[1]
        source_index = nodes_id_list.index(source)
        target_index = nodes_id_list.index(target)
        links_list.append((source_index, target_index))  # todo: 这里用的是非权重图,接下来要验证权重图.
    return edges_list_with_weight, nodes_id_list, nodes_name_list, links_list


def read_table_edge_from_db_for_change_db(dbname, edges_list_with_weight, nodes_id_list, nodes_name_list):
    """

    :param dbname: 数据库名称.
    :param edges_list_with_weight: 格式:[(source_id, target_id, weight), ...]
    :param nodes_id_list: [node_id0, ...]
    :param nodes_name_list: [node_name0, ...]
    :return: links_list: [(node_index0, node_index1), ...], max_weight:最大权重值.
        links_list中的边与edges_list_with_weight中的一一对应,比如:links_list=[(0, 1), (1, 2)]
        edges_list_with_weight=[("1234", "4532", 9), ("4532", "6543", 1)],其中("1234", "4532", 9)与(0, 1)对应,
        0, 1对应的id分别是"1234", "4532".
    """
    dbname = dbname
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    print("Opened database successfully")
    cursor.execute("select source, target, weight, source_name, target_name from edge")  # 从edge表中读取边.
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果
    print("fetched data from database")
    nodes_set = set()
    links_list = []  # 用于添加到全局图中.
    # test_id = set()
    weight_set = set()  # 用来装权重集.以便之后找出最大权重值.
    # fixme: nodes_id_list + nodes_name_list都是来源于edge表. 所以必须按照已经定义好的格式来存放边的信息.
    for each_edge in data:
        # print(each_edge)
        edges_list_with_weight.append(each_edge[:3])  # [(source_id, target_id, weight), ...]
        source = each_edge[0]
        target = each_edge[1]
        weight = each_edge[2]  # weight int类型.
        weight_set.add(weight)
        source_name = each_edge[3]
        target_name = each_edge[4]
        nodes_set.add((source, source_name))  # 这样可以避免重名,因为:(123, mao) (223, mao) 是不相同的两个
        nodes_set.add((target, target_name))

        # test_id.add(source)
        # test_id.add(target)

    for each_iterm in nodes_set:  # nodes_set = [(123, mao), (223, mao), ...] 来源于edge表.
        node = each_iterm[0]
        name = each_iterm[1]
        nodes_id_list.append(node)
        nodes_name_list.append(name)

    for edge in edges_list_with_weight:  # [(source_id, target_id, weight), ...]
        source = edge[0]
        target = edge[1]
        source_index = nodes_id_list.index(source)
        target_index = nodes_id_list.index(target)
        links_list.append((source_index, target_index))  # todo: 这里用的是非权重图,接下来要验证权重图.
    max_weight = max(weight_set)
    print("max_weight return links_list, max_weight")
    # 如果max_weight==1,则对应的图为非权重图.
    return links_list, max_weight


def get_graph_nodes_atrr_info(dbname, which_table=None, doi_node_attr=None, graph_nodes=None):
    """
    :param dbname: 数据库名称.
    :param which_table: 数据库间中的哪一张表.
    :param doi_node_attr: [field1, field2, ...]
    :param graph_nodes: [{id:x, name:x, value:x}, ...]
    :return:{id:{field1:[x, x, x, ...], field2:[x, x, x, ...]}, ...}
    """
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    print("Opened database successfully")
    select_fields = ""
    doi_node_attr = ["name"] + doi_node_attr
    for each_one in doi_node_attr:
        select_fields += each_one + ","
    select_fields = select_fields.strip(",")
    sql = "select " + select_fields + " from " + which_table + " where id=?"
    node_attr_obj = {}  # {id:{field1:[x, x, ...], filed2:[x, x, ...]}, ...}
    # print("graph_nodes")
    # print(graph_nodes)
    for each_node in graph_nodes:  # {id:x, name:x, value:x}
        node_id = each_node["id"]
        cursor.execute(sql, (node_id,))
        data = cursor.fetchall()  # [()]
        # print("data")
        # print(data)
        data = data[0]  # (x, x, ...)
        node_attr_obj_id_value = {}
        for each_one in range(len(data)):
            key_ = doi_node_attr[each_one]
            value_ = data[each_one]  # todo: 里面有分号,需要分号处理.
            if type(value_) == type("str"):
                value_ = value_.strip()
                value_ = value_.split(";")  # [xx, xx, ...]
            else:
                if type(value_) == type(1) or type(value_) == type(1.0):
                    value_ = [value_]  # [12] or [12.09]
            node_attr_obj_id_value[key_] = value_
        node_attr_obj[node_id] = node_attr_obj_id_value
    # print("node_attr_obj")
    # print(node_attr_obj)
    return node_attr_obj


# fixme: 从指定的数据库 + 表中获得id对应的数据.
def get_data_from_db_table_id(dbname, which_table, id_list=None):
    """
    :param dbname: 数据库名称.
    :param which_table: 数据库中的哪一个表.
    :param id_list: id构成的列表,e.g. [id1, id2, ...],用于到数据库表中查询每个id对应的信息,然后在前端显示.
    :return:ids_records_obj 一个对象,{id1:{id:x, title:x, ...}, ...}
    """
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    print("Opened database successfully")
    # sql = "select source, target, weight, source_name, target_name from edge"
    # cursor.execute()  # 从edge表中读取边.
    # data = cursor.fetchall()  # 使用这种方式取出所有查询结果
    cursor.execute("SELECT * FROM {}".format(which_table))
    col_name_list = [tuple_[0] for tuple_ in cursor.description]  # 获得表中的字段.
    # print("col_name_list")
    # print(col_name_list)  # ['id', 'title', 'authors', 'institution', 'year', 'public_venue', 'id_reference', 'abstract']
    sql = "select * from " + which_table + " where id=?"  # select * from publications where id=?
    # print(sql)
    ids_records_obj = {}
    for each_one in id_list:  # fixme: 注意id是text类型的.
        recordObj = {}
        cursor.execute(sql, (each_one,))
        row = cursor.fetchall()  # [()]
        row = row[0]
        counter = -1
        for each_key in col_name_list:
            counter += 1
            recordObj[each_key] = row[counter]  # 构建一个字典.
        ids_records_obj[each_one] = recordObj

    return ids_records_obj


# fixme: 从node表中获得作者共同合作的论文的id.
def get_data_from_node_table(dbname, which_table, source_id, target_id):
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    print("Opened database successfully")
    sql = "select publications from " + which_table + " where id=?"  # select * from publications where id=?
    cursor.execute(sql, (source_id,))
    source_row = cursor.fetchall()  # [()]
    cursor.execute(sql, (target_id,))
    target_row = cursor.fetchall()  # [()]
    # 接下来取交集
    source_row = source_row[0][0].strip()
    source_row = source_row.split(";")
    target_row = target_row[0][0].strip()
    target_row = target_row.split(";")
    co_publication_list = list(set(source_row).intersection(set(target_row)))

    return co_publication_list

if __name__ == "__main__":
    # import json
    # sort_result = get_db_field_values(dbname="DB/Coauthor_Visualization.db", field="P_index")
    # print(sort_result)
    # col_name_list, type_each_field = get_db_table_fields(dbname="DB/Coauthor_Visualization.db", table_name="author")
    # print(col_name_list)
    # print(type_each_field)
    # edges_list_with_weight, nodes_id_list, nodes_name_list, links_list = read_table_edge_from_db(dbname="DB/Coauthor_Visualization.db")
    # doi_node_attr = ["a", "b", "c"]
    # select_fields = ""
    # for each_one in doi_node_attr:
    #     select_fields += each_one + ","
    # select_fields = select_fields.strip(",")
    # print(select_fields)
    # doi_node_attr = ["institution", "interests"]
    # graph_nodes = [{"id": "1229915", "name": "Pierre Dragicevic", "value": 0.132}, {"id": "275436", "name": "Georgios A. Pavlopoulos", "value": 0.897}]
    # dbName = "DB/" + "Coauthor_Visualization.db"
    # r = get_graph_nodes_atrr_info(dbname=dbName, which_table="node", doi_node_attr=doi_node_attr, graph_nodes=graph_nodes)
    # print(r)
    # string = "mao;ting;yun"
    # string.split(";")
    listA = [1, 2, 4, 4, 5, 9, 0]
    listB = [0, 9, 3, 5]
    retB = list(set(listB).intersection(set(listA)))
    print(retB)


