# coding: utf-8

import re
import sqlite3
from datetime import datetime

from fuzzywuzzy import fuzz

from implementation_doi import extract_doi_subgraph, doi_diffusion, \
    get_subgraph_with_greedy_algorithm, \
    get_best_short_path_between_focus
# from py_files import graph_init as graph_doi
from walker import Walker

"""
备注: 对于networkx而言,如果在添加边的时候,如果边相同,即使权重不一样,最终添加的边都是一条.
具体地:
边列表:[(1, 2, 3), (1, 3, 1), (1, 3, 11)]
最后图中的边:(1, 2) (1, 3).
所以下面,不用单行边相同的情况,在添加边的时候会先自动处理成集合,然后再添加边的.
"""


# fixme: 使用停用词+单词匹配模式,构建新图,完成RWR计算.
def reconstruction_graph_with_attr_node(edges_list_with_weight=None, dbname=None, which_table="node", field_attri_values=None, seed_list=None, restart_prob=0.7, attri2node_weight=1, focus_id_list=None, directed=False, max_weight=None, stopWords=None, node_attributes_type_box=None, top_n_value=3, full_compatibility_attr_list=None):
    """
    :param edges_list_with_weight: 图的边,带权重.为了加快速度,将图数据保存在本地.[(source, target, weight), ...]
    :param dbname:存放图节点属性数据库名称.
    :param which_table: 指明数据库中的哪一张表.
    :param field:属性名字,即表格的字段,是一个列表. field=["interests", "institutes"]
    :param field_attri_values:字段(即焦点的兴趣属性)及其对应的值(属性值节点),是一个字典. e.g., {field1:[value1, value2, ...], field2:[value1, value2, ...]},比如作者合作网络里:{"institutions":[x, x, ...], "interests":[x, x, ...]}
    :param max_weight: edges_list_with_weight中的最大的权重值,用于后面的max-normalization. max_weight = [x], 这样做是为了使用地址.
    :param stopWords:停用词表.
    :param top_n_value: 如果一个属性的值有很多则只考虑其前n个.默认是3个
    :return:
      nodes_max_min_only_id: 随机游走获得的概率值从高到低的节点列表.
      probs_max_min_only_id:随机游走获得的从高到低的概率值列表,与nodes_max_min_only_id一一对应.是DOI的UI值.
    """
    neighbors_attr_val_matched_nodes_obj = {}  # 一个对象: {"匹配节点":{"属性值1", "属性值2"}, ...}
    # fixme: 构建通用+自定义停用词表.
    arrCommonStopWords = stopWords["commonStopWords"]  # 通用停用词.
    obj = stopWords["customStopWords"]  # 自定义停用词,是一个对象{dbname:[], ...}
    cur_db_name = dbname.split("/")[-1]  # 数据库名称.
    # 以下做容错处理.
    objKeysList = list(obj.keys())  # 已经自定义的数据库名称,格式:["db1", "db2", "db3"]
    if cur_db_name in objKeysList:  # 在里面,则有arrCustomStopWords.
        arrCustomStopWords = obj[cur_db_name]  # 获得当前数据库对应的自定义停用词.
        stopWords_list = arrCommonStopWords + arrCustomStopWords  # 通用 + 自定义 停用词表.
    else:  # 不在里面.则无arrCustomStopWords.
        stopWords_list = arrCommonStopWords

    fields = list(field_attri_values.keys())  # ["institutions", "interests", "H_index"]
    if attri2node_weight > 0.000000001 and len(fields) > 0:  # fixme: 如果前端weight_attr_node!=0 + 选中了属性,则正常执行.
        db = sqlite3.connect(dbname)
        print("Opened database successfully")
        attribute_to_node_list = []  # e.g. [(attribute, node, weight), ...] 这是"属性值-节点"的边列表.
        # attri_vs_nodes_list = []  # 所有属性值匹配上的全局图的节点构成的列表. e.g. [id1, id2, ...,idm] 表示属性值对应的全局图中节点的id.
        # 创建数据库中的游标对象
        cursor = db.cursor()
        # fields = list(field_attri_values.keys())  # ["institutions", "interests"]

        # fixme: 首先获得数据库中中所有的数据,格式:(id, institutions, interests)
        field_string = "id"
        for each_one in fields:  # FIXME: fields=["institutions", "interests"]
            field_string += "," + each_one  # e.g., id,institutions,interests,H_index
        sql_ = "select " + field_string + " from " + which_table
        cursor.execute(sql_)  # condition: 主要针对文本类型的属性值.
        node_id_fields_list = cursor.fetchall()  # fixme:整个数据库中的查询出来的每个节点的指定属性值: [("1234","UCAS","DM"), ("3456","JLU","ML"), ...]
        # fixme: 所以,node_id_fields_list中每个元组, 如("1234","UCAS","DM")是与fields是对应的.
        start_time_match = datetime.now()
        for each_field in fields:  # 兴趣属性. fields=["institutions", "interests", "H_index"]
            attri_values = field_attri_values[each_field]  # 兴趣属性值,可能有多个. 取出字典里面字段对应的值列表.
            for query_item in attri_values:  # [:top_n_value] 如果有多个兴趣属性值, 那么只取前3个. 例如:attri_values=["data visualization", "graph drawing"] or [12, 12.9]
                # todo: 直接使用属性值去精确匹配数据库中节点对应的属性,例如:%data visualization% 能够匹配上 graph data visualization.
                # todo: 但是,对于一个机构来说,可能有多种表达,此时,直接使用焦点的属性值就会错失很多节点.可以使用单词级的匹配.
                """
                匹配效果实例:
                query_item="Scientific Computing and Imaging Institute, Salt Lake City, UT, USA"
                如果用数据库like语句,则匹配上2个点: '89460', '142205'
                而用单词级匹配,则:
                '1148839', '847909', '828865', '831241', '391906', '89460', '107906', '365551', '982970', '642593', '142205'
                """
                # fixme: 目前考虑两种类型: string类型 + number类型(主要是int/float,在数据库中对应于integer/real)
                if type(query_item) == type("str"):  # fixme:如果查询项是字符串类型.
                    # 遍历匹配网络中的所有节点,找出query_item的匹配节点.
                    matched_node_list = get_matched_node(query_item=query_item,
                                                         node_id_fields_list=node_id_fields_list,
                                                         fields=fields,
                                                         each_field=each_field,
                                                         stopWords=stopWords_list,
                                                         neighbors_attr_val_matched_nodes_obj=neighbors_attr_val_matched_nodes_obj,
                                                         full_compatibility_attr_list=full_compatibility_attr_list
                                                         )

                else:  # fixme:不是字符串而是"int", "float"
                    matched_node_list = get_matched_node_for_number(query_item=query_item,
                                                                    node_id_fields_list=node_id_fields_list,
                                                                    fields=fields,
                                                                    each_field=each_field,
                                                                    neighbors_attr_val_matched_nodes_obj=neighbors_attr_val_matched_nodes_obj
                                                                    )

                for each_one in matched_node_list:  # [id1, id2, ...]
                    source = query_item  # 属性值. string类型 or int类型 or float类型
                    target = each_one  # id
                    target = str(target)  # fixme: 转化成字符串类型,以前是int类型,那么会不会因此出错了呢?先验证.会影响,所以接下来要保证所有的id都是string类型.
                    temp_edge = (source, target, attri2node_weight)  # fixme:前端将attri2node_weight设置为(0, 1)间的值.
                    attribute_to_node_list.append(temp_edge)
                    # attri_vs_nodes_list.append(target)

        db.close()
        end_time_match = datetime.now()
        time = (end_time_match - start_time_match).seconds
        print("Time Consumption of the matching nodes:", str(time))
        # todo: 现在用max-normalization(即各权重除以最大值以消除量纲,以反映权重的全局重要性),对全局图的权重进行归一化处理.
        edges_list_with_weight_norm = []

        for each_edge in edges_list_with_weight:
            source = each_edge[0]
            target = each_edge[1]
            edge_weight = each_edge[2]
            max_norm_weight = edge_weight / max_weight[0]  # (0, 1]之间的小数.
            edges_list_with_weight_norm.append((source, target, max_norm_weight))
        # fixme:新图 = 权重归一化的全局图 + 属性值-匹配节点构成的属性图, 有一个问题需要考虑: 对于非权重图而言,所有的边的权重值=1,此时无需处理.
        new_graph_attri_node = edges_list_with_weight_norm + attribute_to_node_list  # 构成一个新的图: 原来节点构成的边+新增的属性节点到原节点的边.

        # fixme:以焦点 + 属性值构成的列表,作为RWR的种子,计算出"新图"中每个节点的分数值.
        """
        备注: 1. new_graph_attri_node=[("123", "334", 1), (4, "567", 0.5), (4.08, "567", 0.5), ("data visualization", "234", 1), ... ]
             2. 由于使用的是networkx,而networkx在创建图的时候,边(u,v,w), u,v可以是任何类型的(4, "567", 0.5) or (4.08, "567", 0.5)都是可以与其他类型共存的.
        """
        print(".......computing RWR......")
        start_time = datetime.now()
        wk = Walker(edge_list=new_graph_attri_node, directed=directed)  # todo: 将有向图视为无向图处理.
        nodes_max_min, probs_max_min = wk.run_exp(source=seed_list, restart_prob=restart_prob)  # fixme: 以"焦点+属性值+关键词"为RWR的起始节点.
        ############ 包含属性节点的节点列表以及对应的概率值列表 ############
        # print("用于UI计算框架:")
        # print("nodes_max_min")
        # print(nodes_max_min)
        # print("probs_max_min")
        # print(probs_max_min)
        ########################
        end_time = datetime.now()
        time = (end_time - start_time).seconds
        print("Time Consumption of the computing RWR:", str(time))
        # 排除掉属性节点,只保留原图节点.
        attri_value_list = []  # TODO: 内容包括: 属性值 + 关键词. 用于接下来从计算结果中剔除属性值节点,只保留全局图节点.
        for each_one in seed_list:  # ["123", "AAA", "bbb", "145", 123, 8] 注意: 既有text型也有int/float
            if each_one not in focus_id_list:  # ["123", "145"]
                attri_value_list.append(each_one)  # ["AAA", "bbb", 123, 8], 注意: 即使含有123,它是int型,与"123"是不一样的

        nodes_max_min_only_id = []  # 剔除属性节点后概率值降序排列的节点列表.
        probs_max_min_only_id = []  # 剔除属性节点后概率值降序排列列表.即全局图中节点的UI值.

        # fixme: 下一步要使用 neighbors_attr_val_matched_nodes_obj 来进行属性值/关键词节点的概率值的扩散,用于抓取相关节点.
        for each_key in neighbors_attr_val_matched_nodes_obj.keys():
            temp_list = []
            key_index = nodes_max_min.index(each_key)
            key_prob = probs_max_min[key_index]
            temp_list.append(key_prob)
            key_value_set = neighbors_attr_val_matched_nodes_obj[each_key]  # set()
            for each_one in key_value_set:
                key_index_ = nodes_max_min.index(each_one)
                key_prob = probs_max_min[key_index_]
                temp_list.append(key_prob)
            max_val = max(temp_list)
            # update the corresponding value, i.e., diffuse the probs of atrribute value node to their neighbors.
            probs_max_min[key_index] = max_val

        # fixme:现在的probs_max_min是属性值节点的概率值扩散到匹配匹配节点,匹配节点更新后的值=max(匹配节点自身值,扩散过来的属性节点1的概率值,...,扩散过来的属性节点m的概率值).
        """
        例如, 图:[ (0, 1, 1), (0, 2, 1), (0, 3, 1), (3, 4, 1),
                  ("Vis", 2, 1), ("Vis", 3, 1), ("ML", 2, 1), ("ML", 4, 1)]
             以[0, "Vis", "ML"]为starting nodes,即, "Vis", "ML"为焦点的属性值节点. 运行PPR获得以下结果.        
        nodes_max_min = [0, 'Vis', 'ML', 2, 3, 4, 1]
        probs_max_min = [0.20576030746959784, 0.17215277191689077, 0.17184700245421164, 0.16841055969571259, 0.14081529037491164, 0.09300337555761463, 0.04801069253106056]
        neighbors_attr_val_matched_nodes_obj = {2: ["ML", "Vis"], 3: ["Vis"], 4: ["ML"]},则
        节点2的更新值=max(节点2的值, "ML"节点的值, "Vis"节点的值)=max(0.16841055969571259, 0.17215277191689077, 0.17184700245421164)=0.17215277191689077
        节点3的更新值=max(节点3的值, "Vis"节点的值)
        节点4的更新值=max(节点4的值, "ML"节点的值)
        所以, 更新后的probs_max_min:
        probs_max_min = [0.20576030746959784, 0.17215277191689077, 0.17184700245421164, 0.17215277191689077, 0.17215277191689077, 0.17184700245421164, 0.04801069253106056]
    
        """
        # print("test hahahaha nodes_max_min, probs_max_min")
        # print(nodes_max_min, probs_max_min)
        index_each_one = -1  # 做索引.
        for each_one in nodes_max_min:
            index_each_one += 1
            if each_one not in attri_value_list:  # fixme:说明是全局图中的节点
                nodes_max_min_only_id.append(str(each_one))  # each_one int类型.
                temp_prob = probs_max_min[index_each_one]
                probs_max_min_only_id.append(temp_prob)

        return nodes_max_min_only_id, probs_max_min_only_id

    else:
        # todo: 如果前端weight_attr_node=0, 则不会构建属性值-节点,而是直接:先对全局图进行权重归一化,然后以焦点为种子列表,输入RWR获得全局图节点分数.
        edges_list_with_weight_norm = []
        for each_edge in edges_list_with_weight:
            source = each_edge[0]
            target = each_edge[1]
            edge_weight = each_edge[2]
            max_norm_weight = edge_weight / max_weight[0]  # (0, 1)之间的小数.
            edges_list_with_weight_norm.append((source, target, max_norm_weight))
        print(".......computing RWR......")
        start_time = datetime.now()
        wk = Walker(edge_list=edges_list_with_weight_norm, directed=directed)
        nodes_max_min, probs_max_min = wk.run_exp(source=focus_id_list, restart_prob=restart_prob)  # source, restart_prob, og_prob, node_list = None
        end_time = datetime.now()
        time = (end_time - start_time).seconds
        print("Time Consumption of the computing RWR:", str(time))
        ########################
        # print("用于UI计算框架:")
        # print("nodes_max_min")
        # print(nodes_max_min)
        # print("probs_max_min")
        # print(probs_max_min)
        ########################
        return nodes_max_min, probs_max_min


# fixme: 根据输入的数值,找出符合条件的节点
def get_matched_node_for_number(query_item, node_id_fields_list, fields, each_field, neighbors_attr_val_matched_nodes_obj):
    """
    :param query_item: 一个数值. sqlite中的integer/real类型对应python中的int/float.
    :param node_id_fields_list: 查询出的结果,e.g.,[(id, field1_value, field2_value), ...]
    :param fields: 如,["institutions", "interests", "H_index"],是Sqlite中对应表行除了id外按照从左到右顺序排列的字段.
    :param each_field: 如"institutions".
    :return: 值>/>=输入值的节点构成的列表, [id1, id2, ...]
    """
    if type(query_item) == type(1) or type(query_item) == type(1.0):  # 保证是int or float.
        matchNodesSet = set()  # 属性值匹配上的节点集.["1223", "4567", "6678"]
        field_index = fields.index(each_field) + 1
        for each_one in node_id_fields_list:  # [(id, field1_value, field2_value), ...]
            node_id = each_one[0]
            node_value = each_one[field_index]  # 该节点对应属性的值.
            # todo: 目前的条件很简单,没有为特定的数据属性(比如H_index)做定制(为了系统的泛化),如果实验效果不好可以使用属性定制.
            if query_item != 0:  # 不为0
                if node_value >= query_item:  # 大于或等于匹配上.
                    matchNodesSet.add(node_id)
                    if node_id in neighbors_attr_val_matched_nodes_obj.keys():
                        neighbors_attr_val_matched_nodes_obj[node_id].add(query_item)
                    else:
                        neighbors_attr_val_matched_nodes_obj[node_id] = set()
                        neighbors_attr_val_matched_nodes_obj[node_id].add(query_item)

            else:  # 等于0
                if node_value > query_item:  # 大于或等于匹配上.
                    matchNodesSet.add(node_id)
                    if node_id in neighbors_attr_val_matched_nodes_obj.keys():
                        neighbors_attr_val_matched_nodes_obj[node_id].add(query_item)
                    else:
                        neighbors_attr_val_matched_nodes_obj[node_id] = set()
                        neighbors_attr_val_matched_nodes_obj[node_id].add(query_item)

        return list(matchNodesSet)  # [id1, id2, ...]


# fixme:获得数据库中匹配的节点
# v3.0版本的节点匹配函数,主要将完全匹配改成了模糊匹配(利用fuzzywuzzy).
def get_matched_node(query_item, node_id_fields_list, fields, each_field, stopWords, neighbors_attr_val_matched_nodes_obj,full_compatibility_attr_list):
    """
    :param query_item: 一个text类型的属性值,e.g. "data visualization"
    :param node_id_fields_list: [(id, field1_val, field2_val), ...],即对应sqlite中的字段.
    :param fields: 焦点的兴趣属性列表:["institutions", "interests"],也就是兴趣属性.
    :param each_field: 当前字段,如"institutions"
    :param stopWords: 通用+自定义的停用词列表,[xx, xx, ..., xx]
    :return: query_item在数据库中匹配上的节点的列表.如,[id1, id2, ...]
    """
    lowerCasekeyWord = query_item.lower()  # 输入词,先转换成小写
    result_list = re.split("，|,|&|\t|\s+", lowerCasekeyWord)  # 利用分隔符,转化成列表, result_list = ["data", "visualization"]
    word_set = set([x for x in result_list if x])  # 去掉空字符,取集合
    lowerCasekeyWordList = list(word_set)  # 输入词,["volume", "data", "visualization", "in"]

    # counterLowerCasekeyWord = 0  # 属性值中有效词,即非空,非停用词的个数.
    newLowerCasekeyWordList = []  # 输入属性值的有效词(非空,非停用词)构成的列表.
    # 去掉停用词.
    for each_one in lowerCasekeyWordList:  # ["volume", "data", "visualization", "in"]
        if each_one != "":
            if each_one not in stopWords:  # 不在停用词表.
                # counterLowerCasekeyWord = counterLowerCasekeyWord + 1  # 统计匹配非停用词的数量.
                newLowerCasekeyWordList.append(each_one)  # FIXME: 有效词列表:["volume", "data", "visualization"],去掉停用词"in".

    allNodesKeysList = node_id_fields_list  # fixme: 整个网络中各个节点id+兴趣属性值. [("123", "某某机构1"), ("3456", "某某机构2"), ("567", "某某机构3"), ("891", "某某机构4")]  # 整个图的节点id列表. nodesAttrObj={id:{name:[x], field1:[x,...], field2:[x,...]},...}
    matchNodesSet = set()  # 属性值匹配上的节点集.["1223", "4567", "6678"]

    # fixme:遍历全局图中的每个节点,找出匹配节点.
    for each_one in allNodesKeysList:  # allNodesKeysList=[("123", "某某机构1"), ...]
        nodeId = each_one[0]  # 节点id.
        field_index = fields.index(each_field) + 1
        attr_val_string = each_one[field_index]  # 兴趣属性对应的值, 形如"aaa;bbb;ccc"
        attr_val_string = attr_val_string.strip()
        attrValList = attr_val_string.split(";")  # 对象中指定属性对应的值构成的数组: e.g, attrValList=["large graph visualization", "science visualization", "graph drawing", "data visualization"]

        for each_word in attrValList:  # each_word="large graph visualization"
            newStr = each_word.lower()  # "large graph visualization"

            result_list = re.split("，|,|&|\t|\s+", newStr)  # 利用分隔符,转化成列表.
            word_set = set([x for x in result_list if x])  # 去掉空字符,取集合
            newStrList = list(word_set)  # ["large", "graph", "visualization"]
            newnewStrList = []  # 非空,非停用词.
            counterNewStrList = 0

            # 去停用词.
            for each_string in newStrList:  # ["science", "visualization", "the"]
                if each_string != "" and each_string not in stopWords:
                    counterNewStrList = counterNewStrList + 1  # 加1.
                    newnewStrList.append(each_string)
            # 此时, newnewStrList = ["large", "graph", "visualization"]
            commonWordSet = set()  # 相同(相似)的单词的集合.

            '''
            假设: query_item=="graph visualization" 被匹配节点的一个属性值(如果有多个属性值的话)为"large graph visualization",
            newLowerCasekeyWordList==["graph", "visualization"]
            newnewStrList==["large", "graph", "visualization"]
            commonWordSet==["graph", "visualization"]
            但是直接使用"if each_valid_word_in_db == each_valid_word_in_attri_val"这样的条件会出现这样的问题:
            algorithm与algorithms不相等,为了避免这样的情况使用模糊比较.
            '''
            for each_valid_word_in_attri_val in newLowerCasekeyWordList:  # 输入的属性值的有效词列表: ["volume", "data", "visualization"]
                for each_valid_word_in_db in newnewStrList:  # 被匹配节点的有效属性值列表: ["science", "visualization"]

                    if fuzz.token_set_ratio(each_valid_word_in_db, each_valid_word_in_attri_val) > 80:  # 模糊匹配
                    # if each_valid_word_in_db == each_valid_word_in_attri_val:  # 原来的模糊匹配改成完全匹配.
                        commonWordSet.add(each_valid_word_in_attri_val)
                        break  # 单词匹配上则跳出大循环,去判断下一个单词.

            # 上下兼容版本 #
            if each_field in full_compatibility_attr_list:  # 如果当前字段属于指定的上下兼容属性,例如:institution
                matchSize = len(commonWordSet)  # 匹配词的个数.
                # whichOne = len(newLowerCasekeyWordList)  # 以语义节点的有效词数量为基准,实现向下兼容.
                diff = len(newLowerCasekeyWordList) - len(newnewStrList)
                if diff > 0:
                    whichOne = len(newnewStrList)
                else:
                    whichOne = len(newLowerCasekeyWordList)
                if whichOne > 2:  # 不小于3个单词的时候,大于较小者的一半算是匹配上了.
                    threshold = whichOne / 2.0  # 加一个偏置1,使得<=3的字符串完全匹配.

                else:  # 不大于2个有效词,则需要完全匹配.
                    threshold = whichOne  # 2或1

                if matchSize >= threshold:  # 如果匹配上的词的数量不小于最小的字符串的一半,则可以认为两个字符串描述的是一个实体.
                    matchNodesSet.add(nodeId)  # nodeId: 全局图中与属性值query_item节点匹配的节点.
                    # FIXME:用于语义节点扩散,neighbors_attr_val_matched_nodes_obj: {"123":{"data mining", "information visualization"}}
                    if nodeId in neighbors_attr_val_matched_nodes_obj.keys():
                        neighbors_attr_val_matched_nodes_obj[nodeId].add(query_item)
                    else:
                        neighbors_attr_val_matched_nodes_obj[nodeId] = set()
                        neighbors_attr_val_matched_nodes_obj[nodeId].add(query_item)
                    break  # 已经确定当前节点是匹配节点,跳出当前大循环,判断下一个节点.
            # 向下兼容版本 #
            else:
                matchSize = len(commonWordSet)  # 匹配词的个数.
                whichOne = len(newLowerCasekeyWordList)  # 以语义节点的有效词数量为基准,实现向下兼容.

                if whichOne > 2:  # 不小于3个单词的时候,大于较小者的一半算是匹配上了.
                    threshold = whichOne / 2.0 + 1  # 加一个偏置1,使得<=3的字符串完全匹配.

                else:  # 不大于2个有效词,则需要完全匹配.
                    threshold = whichOne  # 2或1

                if matchSize >= threshold:  # 如果匹配上的词的数量不小于最小的字符串的一半,则可以认为两个字符串描述的是一个实体.
                    matchNodesSet.add(nodeId)  # nodeId: 全局图中与属性值query_item节点匹配的节点.
                    # FIXME:用于语义节点扩散,neighbors_attr_val_matched_nodes_obj: {"123":{"data mining", "information visualization"}}
                    if nodeId in neighbors_attr_val_matched_nodes_obj.keys():
                        neighbors_attr_val_matched_nodes_obj[nodeId].add(query_item)
                    else:
                        neighbors_attr_val_matched_nodes_obj[nodeId] = set()
                        neighbors_attr_val_matched_nodes_obj[nodeId].add(query_item)
                    break  # 已经确定当前节点是匹配节点,跳出当前大循环,判断下一个节点.

    return list(matchNodesSet)  # [id1, id2, ...]

# v2.0版本
# def get_matched_node(query_item, node_id_fields_list, fields, each_field, stopWords):
#       """
#       :param query_item: 一个text类型的属性值,e.g. "data visualization"
#       :param node_id_fields_list: [(id, field1_val, field2_val), ...],即对应sqlite中的字段.
#       :param fields: 焦点考虑的字段列表:["institutions", "interests"],也就是兴趣属性.
#       :param each_field: 当前字段,如"institutions"
#       :param stopWords: 通用+自定义的停用词列表,[xx, xx, ..., xx]
#       :return: query_item在数据库中匹配上的节点列表.如,[id1, id2, ...]
#       """
#       lowerCasekeyWord = query_item.lower()  # 先转换成小写
#       result_list = re.split("，|,|&|\t|\s+", lowerCasekeyWord)  # 利用分隔符,转化成列表.
#       word_set = set([x for x in result_list if x])  # 去掉空字符,取集合
#       lowerCasekeyWordList = list(word_set)  # ["volume", "data", "visualization", "in"]
#
#       counterLowerCasekeyWord = 0  # 属性值中有效词,即非空,非停用词的个数.
#       newLowerCasekeyWordList = []  # 非空,非停用词.
#
#       for each_one in lowerCasekeyWordList:
#         if each_one != "":
#           if each_one not in stopWords:  # 不在停用词表.
#             counterLowerCasekeyWord = counterLowerCasekeyWord + 1  # 统计匹配非停用词的数量.
#             newLowerCasekeyWordList.append(each_one)  # 有效词列表:["volume", "data", "visualization"],去掉停用词"in".
#
#       allNodesKeysList = node_id_fields_list  #[("123", "institutions"), ("3456", "institutions"), ("567", "institutions"), ("891", "institutions")]  # 整个图的节点id列表. nodesAttrObj={id:{name:[x], field1:[x,...], field2:[x,...]},...}
#       matchNodesSet = set()  # 属性值匹配上的节点集.["1223", "4567", "6678"]
#
#       for each_one in allNodesKeysList:  # allNodesKeysList=[("123", "institutions"), ("3456", "institutions")]
#         nodeId = each_one[0]  # 节点id.
#         field_index = fields.index(each_field) + 1
#         attr_val_string = each_one[field_index]  # "aaa;bbb;ccc"
#         attr_val_string = attr_val_string.strip()
#         attrValList = attr_val_string.split(";")  # 对象中指定属性对应的值构成的数组:attrValList=[x, x, ...]
#
#         for each_word in attrValList:
#           newStr = each_word.lower()  # 指定属性的某个取值: "ab, cc fg"
#
#           result_list = re.split("，|,|&|\t|\s+", newStr)  # 利用分隔符,转化成列表.
#           word_set = set([x for x in result_list if x])  # 去掉空字符,取集合
#           newStrList = list(word_set)  # [ab, cc, fg, ""]
#           newnewStrList = []  # 非空,非停用词.
#           counterNewStrList = 0
#
#           for each_string in newStrList:
#             if each_string != "" and each_string not in stopWords:
#                counterNewStrList = counterNewStrList + 1  # 加1.
#                newnewStrList.append(each_string)  # newnewStrList=[ab, cc, fg]
#
#           commonWordSet = set()  # 相同(相似)的单词的集合.
#
#           for each_valid_word_in_attri_val in newLowerCasekeyWordList:  # 有效词列表:["volume", "data", "visualization"]
#                 for each_valid_word_in_db in newnewStrList:
#                     if each_valid_word_in_db == each_valid_word_in_attri_val:  # 原来的模糊匹配改成完全匹配.
#                        commonWordSet.add(each_valid_word_in_attri_val)
#                        break  # 单词匹配上则跳出大循环,去判断下一个单词.
#
#           matchSize = len(commonWordSet)  # 有效词中,公共词的个数.
#           whichOne = counterLowerCasekeyWord  # 以标签上的属性值的有效词的个数为基准.
#
#           if whichOne > 2:  # 不小于3个单词的时候,大于较小者的一半算是匹配上了.
#             threshold = whichOne/2.0
#
#           else:  # 不大于2个有效词,则需要完全匹配.
#             threshold = whichOne
#
#           if matchSize >= threshold:  # 如果匹配上的词的数量不小于最小的字符串的一半,则可以认为两个字符串描述的是一个实体.
#             matchNodesSet.add(nodeId)
#             break  # 已经确定当前节点是匹配节点,跳出大循环,判断下一个节点.
#
#       return list(matchNodesSet)  # [id1, id2, ...]
'''
# fixme: 原来的代码:直接对属性值,使用数据库like语句模糊匹配,缺点:不适用于"同一个意思,描述不同"的情况.
# 建立动态的属性异质图. 属性异质图:将属性节点化的图.
def reconstruction_graph_with_attr_node(edges_list_with_weight=None, dbname=None, which_table="node", field_attri_values=None, seed_list=None, restart_prob=0.7, attri2node_weight=1, focus_id_list=None, directed=False, max_weight=None, stopWords=None):
    """
    :param edges_list_with_weight: 图的边,带权重.为了加快速度,将图数据保存在本地.[(source, target, weight), ...]
    :param dbname:存放图节点属性数据库名称.
    :param which_table: 指明数据库中的哪一张表.
    :param field:属性名字,即表格的字段,是一个列表. field=["interests", "institutes"]
    :param field_attri_values:字段(即焦点需要考虑的属性)及其对应的值(属性值节点),是一个字典. attri_values={field1:[value1, value2, ...], field1:[value1, value2, ...]},比如作者合作网络里:{"institutions":[x, x, ...], "interests":[x, x, ...]}
    :param max_weight: edges_list_with_weight中的最大的权重值,用于后面的max-normalization. max_weight = [x], 这样做是为了使用地址.
    :param stopWords: 停用词表.
    :return:
      nodes_max_min_only_id: 随机游走获得的概率值从高到低的节点列表.
      probs_max_min_only_id:随机游走获得的从高到低的概率值列表,与nodes_max_min_only_id一一对应.
    """
    if attri2node_weight > 0.000001:  # fixme: 如果前端weight_attr_node!=0,正常执行.
        db = sqlite3.connect(dbname)
        print("Opened database successfully")
        attribute_to_node_list = []  # e.g. [(attribute, node, weight), ...] 这是"属性值-节点"的边列表.
        attri_vs_nodes_list = []  # 所有属性值匹配上的全局图的节点构成的列表. e.g. [id1, id2, ...,idm] 表示属性值对应的全局图中节点的id.
        # 创建数据库中的游标对象
        cursor = db.cursor()
        fields = list(field_attri_values.keys())  # ["institutions", "interests"]

        for each_field in fields:  # field=[xx, xx, ...]
            attri_values = field_attri_values[each_field]  # 取出字典里面字段对应的值列表.
            for query_item in attri_values:  # 例如:attri_values=["data visualization", "graph drawing"]
                # todo: 直接使用属性值去精确匹配数据库中节点对应的属性,例如:%data visualization% 能够匹配上 graph data visualization.
                # todo: 但是,对于一个机构来说,可能有多种表达,此时,直接使用焦点的属性值就会错失很多节点.可以使用单词级的匹配.
                condition = "%" + query_item + "%"  # 备注:一定要使用%XXXX%的形式,否则返回空.
                sql_ = "select id from " + which_table + " where " + each_field + " like ?"
                cursor.execute(sql_, (condition,))  # condition: 主要针对文本类型的属性值.
                data = cursor.fetchall()

                for each_one in data:  # [(xx,), (xx,), ...]
                    source = query_item  # 属性值. string类型.
                    target = each_one[0]  # id
                    target = str(target)  # fixme: 转化成字符串类型,以前是int类型,那么会不会因此出错了呢?先验证.会影响,所以接下来要保证所有的id都是string类型.
                    temp_edge = (source, target, attri2node_weight)  # fixme:前端将attri2node_weight设置为(0, 1)间的值.
                    attribute_to_node_list.append(temp_edge)
                    attri_vs_nodes_list.append(target)

        db.close()
        # todo: 现在用max-normalization(即各权重除以最大值以消除量纲,以反映权重的全局重要性),对全局图的权重进行归一化处理.
        edges_list_with_weight_norm = []

        for each_edge in edges_list_with_weight:
            source = each_edge[0]
            target = each_edge[1]
            edge_weight = each_edge[2]
            max_norm_weight = edge_weight / max_weight[0]  # (0, 1)之间的小数.
            edges_list_with_weight_norm.append((source, target, max_norm_weight))
        # fixme:新图 = 权重归一化的全局图 + 属性值-匹配节点构成的属性图
        new_graph_attri_node = edges_list_with_weight_norm + attribute_to_node_list  # 构成一个新的图: 原来节点构成的边+新增的属性节点到原节点的边.

        # fixme:以焦点 + 属性值构成的列表,作为RWR的种子,计算出"新图"中每个节点的分数值.
        wk = Walker(edge_list=new_graph_attri_node, low_list=None, remove_nodes=None, directed=directed)
        nodes_max_min, probs_max_min = wk.run_exp(source=seed_list, restart_prob=restart_prob)  # source, restart_prob, og_prob, node_list = None

        # 排除掉属性节点,只保留原图节点.
        attri_value_list = []  # TODO: 内容包括: 属性值 + 关键词. 用于接下来从计算结果中剔除属性值节点,只保留全局图节点.
        for each_one in seed_list:  # ["123", "AAA", "bbb", "145"]
            if each_one not in focus_id_list:  # ["123", "145"]
                attri_value_list.append(each_one)  # ["AAA", "bbb"]

        nodes_max_min_only_id = []  # 剔除属性节点后概率值降序排列的节点列表.
        probs_max_min_only_id = []  # 剔除属性节点后概率值降序排列列表.即全局图中节点的UI值.

        index_each_one = -1  # 做索引.
        for each_one in nodes_max_min:
            index_each_one += 1
            if each_one not in attri_value_list:  # fixme:说明是全局图中的节点
                nodes_max_min_only_id.append(str(each_one))  # each_one int类型.
                temp_prob = probs_max_min[index_each_one]
                probs_max_min_only_id.append(temp_prob)

        return nodes_max_min_only_id, probs_max_min_only_id

    else:
        # todo: 如果前端weight_attr_node=0, 则不会构建属性值-节点,而是直接:先对全局图进行权重归一化,然后以焦点为种子列表,输入RWR获得全局图节点分数.
        edges_list_with_weight_norm = []
        for each_edge in edges_list_with_weight:
            source = each_edge[0]
            target = each_edge[1]
            edge_weight = each_edge[2]
            max_norm_weight = edge_weight / max_weight[0]  # (0, 1)之间的小数.
            edges_list_with_weight_norm.append((source, target, max_norm_weight))

        wk = Walker(edge_list=edges_list_with_weight_norm, low_list=None, remove_nodes=None, directed=directed)
        nodes_max_min, probs_max_min = wk.run_exp(source=focus_id_list, restart_prob=restart_prob)  # source, restart_prob, og_prob, node_list = None

        return nodes_max_min, probs_max_min
'''


# fixme:根据节点的id,获得其在全局图(flask启动时,创建的一个全局的graph-tool图)中对应的索引,以便于后面的子图抽取.
def get_index_org_graph(nodes_max_min_only_id=None, nodes_id_list=None):
    """
    :param nodes_max_min_only_id: 经过随机游走算法,获得的降序排列的节点id列表.
    :param nodes_id_list: 全局图(flask启动时,创建的一个全局的graph-tool图)的索引对应的节点id列表,即[id0, id1, ...idm]表示索引m的id
    :return:nodes_max_min_only_id中各个元素在全局图中的索引构成的列表,与nodes_max_min_only_id一一对应.
    """
    index_nodes_max_min_only_id = []
    for each_one in nodes_max_min_only_id:  # [X, X,...,X] each_one 已经转成str类型,原来是int类型的.
        each_one_index = nodes_id_list.index(each_one)
        index_nodes_max_min_only_id.append(each_one_index)
    return index_nodes_max_min_only_id


"""
# 根据前端返回的兴趣集,包括:节点集 + 关键词集, 用set_interests表示.
接下来需要做的: 根据节点集,取出所有节点的text型属性,构成"节点属性集",然后构造节点属性集 + 关键词集动态构造的新图,最后
以节点集 + 节点属性集合 + 关键词集 作为随机游走的种子,计算整个图中每个节点的分数.
备注: 
  节点属性集合的获取有两种方法:
   1. 前端获得节点id,后台访问数据库匹配.
   2. 前端已经获得了节点的完整信息,直接在前端和节点绑定在一起. 经过分析,选择这一种.
明天: 完成上述工作.
"""
"""
setNodes: [{ "id": "927218",  # id作为唯一标识,
             "tag": "Javier López", # tag作为节点的标签.
             "dbname":"Coauthor_Visualization.db", # 数据库名称.
             "field":"name;interests", # 数据库表字段. 如果是多条件查询,则每个属性之间用";"分开.
             "keyword": "wei chen;visualization technique", # 关键字. 如果是多条件查询,则每个属性值之间用";"分开.
             "attriselect": [x, x, ...], # 焦点要考虑的属性(在前端选择),attributesValue为其中属性-值对对象.
             "attributesValue": {"institution":"University of Joensuu", "interests":"current mode;data structure"}},...]; # attriselect中属性-值对.
"""


def get_seed_field_value_from_set_interests(set_interests=None, discard_fields_list=None):
    """
    :param set_interests:前端请求发送的参数set_interests={"setNodes": [{}, {},...], "setKeyword":{field1:xxx, ...}}
    如{'setNodes': [{'attriselect': ['interest'], 'dbname': 'attr_test.db', 'id': '0', 'keyword': 'BJ', 'attributesValue': {'interest': 'football'}, 'field': 'work_place', 'tag': '0'}, {'attriselect': ['work'], 'dbname': 'attr_test.db', 'id': '4', 'keyword': 'BJ', 'attributesValue': {'work': 'doctor'}, 'field': 'work_place', 'tag': '4'}], 'setKeyword': {}}
    备注: 我们考虑的节点属性是text类型的属性,它们的值接下来要被节点化,并与节点的id一起作为种子,用随机游走来计算整个图中的节点分数.
    我们暂时将这些属性称为"被节点化属性",其值称为"被节点化属性值".
    :return: focus_id_list, seed_list, field_attri_values,分别是焦点的id集, 新图的种子集, 字段及其值组成的集.
    focus_id_list里面存放焦点的id, seed_list里面的内容包括: 焦点id + 焦点的兴趣属性值(除去name等在数据库配置文件中指明的属性) + 关键词集中的关键词(目前没有用到) + 兴趣关键词(比如,field:institution, keyword:UCAS 中的UCAS),
    field_attri_values: 一个对象,e.g.{字段1: [所选焦点字段对应的值 + 属于该字段的关键词], 字段2: [], ...},如{'work_place': ['bj'], 'interest': ['football'], 'work': ['doctor']},interest是焦点0的兴趣属性,work是焦点4的兴趣属性,work_place是焦点的兴趣关键词对应的属性.
    field_attri_value会被用于匹配属性值节点.
    """
    nodes_set = set_interests["setNodes"]  # fixme:选中的节点集,即焦点集.
    keyword_set = set_interests["setKeyword"]  # fixme: 必须将keyword设置成这样的格式:keyword_set={field1:"AAA;bbb;ccc", ...},field1作为数据库表查询时的条件,这是以后的扩展,关键词集, 目前是空的.前端没有设置.

    # print("nodes_set是否有新添加的属性")
    # print(nodes_set[0]["attributesValue"])
    # *****************************************
    seed_set = set()  # fixme: 种子节点集. {"12345", "4325", "science visualization", "volume visualization", "machine learning"}
    nodes_id_set = set()  # fixme:焦点id集. {"12345", "4325"}
    field_attri_values = {}  # fixme: 属性值节点集. {interest: set("science visualization", "volume visualization", "machine learning")}
    # fixme: 以上三者的关系: seed_set = nodes_id_set + field_attri_values
    # *****************************************

    # fixme:属性值节点化需要考虑的text型属性(字段,在前端选择),e.g.['institutions', 'interests', ...] 如果为空,即[].
    node_fields_list = set()
    for each_focus in nodes_set:  # nodes_set=[{id:x,tag:x,...}, ...]
        key_list = each_focus["attributesValue"].keys()  # fixme:每个焦点对应的兴趣属性:["institutions", "interests"],是在前端选中的属性(每个焦点需要考虑的属性可以不相同).
        for each_key in key_list:  # 每一个兴趣属性.
            node_fields_list.add(each_key)  # {'institutions', 'interests'}

        ############### 修改的 ###########
        field_val_list_string = each_focus["field"]
        field_val_list_string = field_val_list_string.strip()
        field_val_list = field_val_list_string.split(";")

        keyword_val_list_string = each_focus["keyword"]
        keyword_val_list_string = keyword_val_list_string.strip()
        keyword_val_list = keyword_val_list_string.split(";")
        # todo: 需要考虑:焦点不考虑任何属性,而关键词属于text类型字段的值.
        if len(field_val_list) == len(keyword_val_list):  # 字段数量 == 关键词数量.得保证个数相同.
            counter = -1
            for each_field in field_val_list:  # [x, x]
                counter = counter + 1
                if each_field not in discard_fields_list:  # fixme:如果field不在被丢弃的字段列表中.
                    if each_field.lower() != "null" and each_field.lower() != "all":  # fixme: 同时不是NULL + All
                        node_fields_list.add(each_field)  # todo: 保存each_field.
        ##########################

    node_fields_list = list(node_fields_list)  # fixme: e.g.['institutions', 'interests'],所有焦点在前端选择的属性的集合(有的选择interests, 有的没有选择属性,有的选择了"institutions"+"interests",将这些做成一个集合["institutions","interests"])
    # text_search_field_set = set()  # 前端搜索视图关键词对应字段的集合.
    # 初始化field_attri_values.
    # if len(node_fields_list) > 0:  # fixme: 如果焦点考虑了兴趣属性.
    for each_one in node_fields_list:  # [field1, field2, ...]
        field_attri_values[each_one] = set()  # 初始化成字段-字段值集合对:{institutions: set(), interests: set(), ...}

    # ********** 保证焦点不考虑任何属性时,而关键词对应的字段属于被考虑范围 ****************#

    # else:  # fixme: 如果焦点没有考虑任何属性.
    #     for each_node in nodes_set:
    #         # 现在满足多条件搜索.
    #         field_val_list_string = each_node["field"]
    #         field_val_list_string = field_val_list_string.strip()
    #         field_val_list = field_val_list_string.split(";")
    #
    #         keyword_val_list_string = each_node["keyword"]
    #         keyword_val_list_string = keyword_val_list_string.strip()
    #         keyword_val_list = keyword_val_list_string.split(";")
    #         # todo: 需要考虑:焦点不考虑任何属性,而关键词属于text类型字段的值.
    #         if len(field_val_list) == len(keyword_val_list):  # 字段数量 == 关键词数量.得保证个数相同.
    #             counter = -1
    #             for each_field in field_val_list:  # [x, x]
    #                 counter = counter + 1
    #                 if each_field not in discard_fields_list:  # fixme:如果field不在被丢弃的字段列表中.
    #                     if each_field.lower() != "null" and each_field.lower() != "all":  # fixme: 同时不是NULL + All
    #                         text_search_field_set.add(each_field)  # todo: 保存each_field.
    #
    # text_search_field_list = list(text_search_field_set)
    # print("text_search_field_list")
    # print(text_search_field_list)
    # if len(text_search_field_list) > 0:
    #     for each_one in text_search_field_list:  # [field1, field2, ...]
    #         field_attri_values[each_one] = set()  # 初始化成字段-字段值集合对:{field1: set(), field2: set(), ...}

    ###########################################################################
    for each_node in nodes_set:  # 遍历每个焦点.[{}, {}, ...,{}]
        node_id = each_node["id"]  # 获得节点的id,id是唯一标识.
        # node_id = str(node_id)  # FIXME: 必须将id转化成字符串类型.虽然数据库中的id是int型的,但是在写查询语言时不用考虑类型.查询时直接按照字符串查询.
        seed_set.add(node_id)
        nodes_id_set.add(node_id)  # [id1, id2, ...]

        # fixme:针对该焦点对应的搜索条件(单/多条件搜索)
        """
        # 原来的单个条件搜索.
        if each_node["field"] in node_fields_list:  # fixme:判断搜索条件中,选择的字段(属性)是否为在考虑的范围之内.
            node_keyword = each_node["keyword"]  # text类型.
            node_keyword = node_keyword.strip()  # 去掉前后的空格.
            seed_set.add(node_keyword)  # 丢到种子列表里面. 同时也要被放在节点化属性中.
            field_attri_values[each_node["field"]].add(node_keyword)  # fixme: 因为搜索的字段在考虑的字段内部,所以,需要将其值添加到属性节点集中.

        """
        # fixme: 先取兴趣关键词(如果存在的话)现在满足多条件搜索.
        field_val_list_string = each_node["field"]
        field_val_list_string = field_val_list_string.strip()
        field_val_list = field_val_list_string.split(";")

        keyword_val_list_string = each_node["keyword"]
        keyword_val_list_string = keyword_val_list_string.strip()
        keyword_val_list = keyword_val_list_string.split(";")
        # todo: 需要考虑:焦点不考虑任何属性,而关键词属于text类型字段的值.
        if len(field_val_list) == len(keyword_val_list):  # 字段数量 == 关键词数量.得保证个数相同.
            counter = -1
            for each_field in field_val_list:  # [x, x]
                counter = counter + 1
                # if len(node_fields_list) > 0:  # fixme:如果焦点考虑了属性
                if each_field in node_fields_list:  # fixme:判断搜索条件中,选择的字段(属性)是否为在考虑的范围之内.
                    node_keyword = keyword_val_list[counter]  # 取出对应的关键词,text类型.
                    node_keyword = node_keyword.strip()  # 去掉前后的空格.
                    node_keyword = node_keyword.lower()  # fixme: 字符串小写化,避免重复,如这种情况: "Graph Drawing","graph drawing"
                    if node_keyword != "null" and node_keyword != "":
                        seed_set.add(node_keyword)  # 丢到种子列表里面. 同时也要被放在节点化属性中.
                        field_attri_values[each_field].add(node_keyword)
                ##################
                # else:  # fixme:如果焦点没有考虑属性
                #     if each_field not in discard_fields_list:  # fixme:如果field不在被丢弃的字段列表中.
                #         if each_field.lower() != "null" and each_field.lower() != "all":  # fixme: 同时不是NULL + All
                #             node_keyword = keyword_val_list[counter]  # 取出对应的关键词,text类型.
                #             node_keyword = node_keyword.strip()  # 去掉前后的空格.
                #             node_keyword = node_keyword.lower()  # fixme: 字符串小写化
                #             if node_keyword != "null" and node_keyword != "":
                #                 seed_set.add(node_keyword)  # 丢到种子列表里面. 同时也要被放在节点化属性中.
                #                 field_attri_values[each_field].add(node_keyword)

                ##################

        else:
            print("Conditions do not meet the requirement")

        # fixme:针对焦点的兴趣属性,例如'institutions' + 'interests'
        attributesValue = each_node["attributesValue"]  # e.g. {institutions:XXX, interests:XXX}
        for each_key in node_fields_list:  # 每个需要考虑的属性. e.g.['institutions', 'interests']
            if each_key in attributesValue:
                obj_value = attributesValue[each_key]  # FIXME: 原来的text类型. 例如:"AAA;BBB;CCC"; 现在添加number类型(e.g., H_index, P_index, ...).
                if type(obj_value) == type("str"):  # todo: 如果类型是字符串.
                    obj_value = obj_value.strip()  # 去掉前后的空格.
                    obj_value = obj_value.split(";")  # 只有text类型的才有多个值,如, 按照";"划分. (AAA, BBB, CCC)
                    for iterm in obj_value:
                        iterm = iterm.strip()
                        iterm = iterm.lower()  # fixme: 小写化
                        if iterm != "null" and iterm != "":  # 处理掉"NULL" + ""
                            seed_set.add(iterm)
                            field_attri_values[each_key].add(iterm)
                else:  # fixme: 处理非字符类型的值.
                    seed_set.add(obj_value)  # 将值放入种子集中.
                    field_attri_values[each_key].add(obj_value)

    # fixme: keyword集扩展:
    key_keyword_list = list(keyword_set.keys())
    for each_key in key_keyword_list:
        if each_key in node_fields_list:  # 如果字段属于兴趣属性. e.g.['institutions', 'interests']
            iterm = keyword_set[each_key]  # keyword_set={field1:"AAA;bbb;ccc", ...}
            iterm = iterm.strip()
            iterm = iterm.split(";")  # [xxx, xxx, ...]
            for each_item in iterm:
                each_item = each_item.lower()
                if each_item != 'null' and each_item != '':
                    seed_set.add(each_item)
                    field_attri_values[each_key].add(each_item)

    # fixme: 将{field1: set(), ...}转化成{field1: list(), ...}
    for each_one in list(field_attri_values.keys()):  # e.g. ['institutions', 'interests']
        temp_list = list(field_attri_values[each_one])
        field_attri_values[each_one] = temp_list  # fixme: {field1:[x, x, x, ...], ...}

    seed_list = list(seed_set)  # fixme: 里面的id已经是字符串了. [x, x, ...]
    focus_id_list = list(nodes_id_set)  # fixme: 焦点集,里面是字符串的id. [x, x, ...]
    # print("ok")
    # FIXME: seed_list = focus_id_list + field_attri_values中属性值列表
    return focus_id_list, seed_list, field_attri_values


# 使用RWR获得子图.
def get_subgraph_using_RWR(
        g=None,
        directed=False,
        set_interests=None,
        restart_prob=0.7,
        attri2node_weight=1,
        max_weight=None,
        edges_list_with_weight=None,
        dbname=None,
        which_table="node",
        nodes_id_list=None,
        nodes_name_list=None,
        scale_extraction_for_single_focus=None,
        v_API_doi_list=None,
        API_factor=0.1,
        UI_factor=0.9,
        v_doi_list=None,
        is_Edge_Attri_diffusion=False,
        diffusion_factor=0.85,
        stopWords=None,
        discard_fields_list=None,
        full_compatibility_attr_list=None,
        node_attributes_type_box=None,
        is_click_hist=None,
        interest_subgraph_node_list=None
):
    # fixme:由兴趣集获得 焦点集+种子集+属性值节点集
    print(".....obtaining seeds list.....")
    focus_id_list, seed_list, field_attri_values = get_seed_field_value_from_set_interests(set_interests=set_interests, discard_fields_list=discard_fields_list)
    # fixme: 由焦点集+种子集+属性值节点集,获得按照分数值从大到小排序的id列表 + 与之对应的概率值(UI值)列表
    # print(".....computing seeds.....")
    ############# 用于显示种子节点 ###############
    print("focus_id_list")
    print(focus_id_list)
    print("seed_list")
    print(seed_list)
    print("field_attri_values")
    print(field_attri_values)
    ############################
    nodes_max_min_only_id, probs_max_min_only_id = reconstruction_graph_with_attr_node(edges_list_with_weight=edges_list_with_weight,
                                                                                       dbname=dbname,
                                                                                       which_table=which_table,
                                                                                       field_attri_values=field_attri_values,
                                                                                       seed_list=seed_list,
                                                                                       restart_prob=restart_prob,
                                                                                       attri2node_weight=attri2node_weight,
                                                                                       focus_id_list=focus_id_list,
                                                                                       directed=directed,
                                                                                       max_weight=max_weight,
                                                                                       stopWords=stopWords,
                                                                                       node_attributes_type_box=node_attributes_type_box,
                                                                                       top_n_value=3,
                                                                                       full_compatibility_attr_list=full_compatibility_attr_list
                                                                                      )
    # fixme: nodes_max_min_only_id中字符类型的id对应于index_nodes_max_min_only_id中全局图的索引.如["1234", "3452", "5624"] <-->[0, 2, 1]
    index_nodes_max_min_only_id = get_index_org_graph(nodes_max_min_only_id=nodes_max_min_only_id, nodes_id_list=nodes_id_list)

    ############## 用于显示全局图节点id列表以及id对应的节点索引 ##################

    print("UI值:全局图中节点列表")
    print(nodes_max_min_only_id)
    print("UI值列表")
    print(probs_max_min_only_id)
    print("节点对应的图索引")
    print(index_nodes_max_min_only_id)

    ################################

    # 构造VUE前端需要的graph格式.
    graph = {
        "nodes": [],
        "links": []
    }

    v_doi_list.clear()  # fixme: 现将其清零,注意不能使用v_doi_list=[],因为这样会直接更改地址.

    # fixme:DOI计算的核心部分, DOI = API_factor * API + UI_factor * UI
    for v in g.vertices():  # 按顺序,从索引0开始, [0, 1, 2, ...]
        index_v = int(v)  # 获得节点的索引.
        API_val = v_API_doi_list[index_v]  # fixme:获得v_API_doi_list中索引对应的API.
        i_id = index_nodes_max_min_only_id.index(index_v)  # nodes_max_min_only_id
        UI_val = probs_max_min_only_id[i_id]  # fixme:获得UI值
        DOI_val = API_factor * API_val + UI_factor * UI_val
        g.vertex_properties["doi"][v] = DOI_val  # fixme: 重写,更新DOI
    # fixme: 使用扩散函数做DOI值扩散处理(避免局部最优)
    doi_diffusion(g=g, diffusion_factor=diffusion_factor, is_Edge_Attri=is_Edge_Attri_diffusion, directed=directed, focus_id_list=focus_id_list, nodes_id_list=nodes_id_list) # diffusion_factor表示最大值邻居对节点的影响力,越大影响力越大.
    # fixme: 扩散之后,更新每个节点对应的DOI值.
    for each_v in g.vertices():  # 从0开始,所以v_doi_list的索引即为节点在全局图中的索引.
        temp_doi = g.vertex_properties["doi"][each_v]  # g.vertex_properties["doi"][each_v] 其中each_v可以是int型.
        v_doi_list.append(temp_doi)  # fixme: 扩散后的DOI值存放到v_doi_list中.


    ############# 扩散后面的DOI ################
    print("扩散后的DOI列表")
    print(v_doi_list)
    #############################
    # fixme: 接下来根据焦点集抽取子图. focus_id_list 焦点集列表.
    F_all = []  # 各焦点抽出的节点列表,里面是图的索引, 可能会有相同的,最后要做成集合.

    if is_click_hist:  # 根据 interest_subgraph_node_list 中的节点列表恢复子图.
        for node_id in interest_subgraph_node_list:  # [id0, id1, id2, ...]
            node_index_for_id = nodes_id_list.index(node_id)
            F_all.append(node_index_for_id)

    else:  # 如果是点击前端"Focus Set"中的"Start"获得的请求,则重新计算兴趣子图.
        hist_store = []
        for each_focus in focus_id_list:  # 注意:focus_id_list里面的元素是text型的.
            focus_index = nodes_id_list.index(each_focus)  # fixme: 根据节点的id列表,获得其在图中对应的索引
            total_num_doi_subgraph_each_focus = scale_extraction_for_single_focus  # TODO:每个焦点抽取的最大节点个数,暂时定成20个.
            F_temp = get_subgraph_with_greedy_algorithm(g=g, focus=focus_index, total_num_doi_subgraph=total_num_doi_subgraph_each_focus, directed=directed)
            F_all += F_temp  # 列表累积.

            # fixme: 下面获取焦点间最佳路径.注意:对于无向图来说,(a,b)==(b,a),对于有向图则不然.
            for target_focus in focus_id_list:
                if each_focus != target_focus:  # 如果两个点不相同,则考虑在内.
                    if directed:  # fixme:如果是有向图,则(a, b) != (b, a)
                        source = nodes_id_list.index(each_focus)  # fixme: 先将id转换成全局图对应的索引.
                        target = nodes_id_list.index(target_focus)
                        best_path = get_best_short_path_between_focus(g=g, directed=True, source=source, target=target)
                        print("best_path")
                        print(best_path)
                        F_all += best_path
                    else:  # fixme:如果是无向图,则(a, b) == (b, a)
                        temp_hist = (each_focus, target_focus)
                        if temp_hist not in hist_store:
                            source = nodes_id_list.index(each_focus)  # fixme: 先将id转换成全局图对应的索引.
                            target = nodes_id_list.index(target_focus)
                            best_path = get_best_short_path_between_focus(g=g, directed=False, source=source, target=target)
                            F_all += best_path
                            hist_store.append((target_focus, each_focus))  # fixme: 这样可以避免重复计算.

    # TODO: 已经获得了抽取出的节点集.
    F = set(F_all)  # fixme:变成集合. 最后的子图集.
    subgraph_edges_list = extract_doi_subgraph(g, edges_list_g=edges_list_with_weight, subgraph_nodes_list=F)
    edges_list = subgraph_edges_list  # [(source, target, value), ...]
    nodes_set = set()  # 兴趣子图所有节点集合.
    for edge in edges_list:
        source = edge[0]
        target = edge[1]
        value = edge[2]
        edge = {"source": source, "target": target, "value": value}
        graph["links"].append(edge)
        nodes_set.add(source)
        nodes_set.add(target)
    for node in nodes_set:  # node是数据库中的id
        node_idx = nodes_id_list.index(node)  # node_idx是g中的索引.
        name_ = nodes_name_list[node_idx]
        node_doi_value = v_doi_list[node_idx]  # fixme: 节点的value应该是扩散后的DOI值.

        if directed:  # 有向图,则取其出+入邻居
            # fixme: 获得扩展节点的邻居(入度+出度)
            nodes_in = g.get_in_neighbors(node_idx)  # 获得输入的邻居
            nodes_out = g.get_out_neighbors(node_idx)  # 获得输出的邻居
            nodes_in_out = list(nodes_in) + list(nodes_out)

        else:  # 无向图
            nodes_in_out = g.get_out_neighbors(node_idx)  # [(x, x, 0), (x, x, 2), ...]
        num_remaining_neighbours = 0  # 用于统计剩余邻居数量
        for node_index in nodes_in_out:  # nodes_in_out=[index0, ...]
            node_id = nodes_id_list[node_index]
            if node_id not in nodes_set:  # 如果邻居不在兴趣子图的节点集中,则是剩余节点.
                num_remaining_neighbours = num_remaining_neighbours + 1

        node = {"id": node, "name": name_, "value": node_doi_value, "num_remaining_neighbours": num_remaining_neighbours}  # todo: num_remaining_neighbours 表示剩余邻居的数量.
        graph["nodes"].append(node)

    return graph


if __name__ == "__main__":
    r = fuzz.token_set_ratio("MAO", "mao")
    print(r)
    """
    # 随机游走参数设置
    seed_list = ["interactive exploration", "710233"]  # 710233:Kwan-Liu Ma, 1439729:Wei Chen
    restart_prob = 0
    attri2node_weight = 1
    # 查询值设置
    field_attri_values = {"interests": ["interactive exploration", "volume rendering", "information visualization"]}

    nodes_max_min_only_id, probs_max_min_only_id = reconstruction_graph_with_attr_node(edges_list_with_weight=graph_doi.edges_list_with_weight,
                                        dbname="DB/Coauthor_Visualization.db",
                                        which_table="author",
                                        field_attri_values=field_attri_values,
                                        seed_list=seed_list,
                                        restart_prob=restart_prob,
                                        attri2node_weight=attri2node_weight,
                                        focus_id_list=["710233"]
                                       )
    print(nodes_max_min_only_id[:20])
    print(probs_max_min_only_id[:20])
    """

    """
    w = 1
    ['710233', '144816', '260137', '797749', '290018', '794512', '563525', '768914', '1196408', '967663', '765407', '883946', '763689', '789886', '1451388', '1622761', '568669', '345787', '920433', '1214207']
[0.3680677127071181, 0.012146945726970256, 0.010212425933771637, 0.009363074812256319, 0.00904006762265856, 0.007546704165412771, 0.007504775461097333, 0.007504775461097333, 0.007317101663285468, 0.0071823186493124155, 0.00704133980211418, 0.007009109415848199, 0.007009109415848199, 0.006702011481685325, 0.006483126869940719, 0.006406346707204513, 0.006383473588343803, 0.006377722376878811, 0.006360834755108386, 0.006355630710570911]
    w = 10
    ['710233', '144816', '797749', '290018', '260137', '563525', '768914', '1196408', '794512', '967663', '765407', '789886', '763689', '883946', '1451388', '568669', '1214207', '113198', '1622761', '920433']
[0.36632071756497997, 0.011302166922433821, 0.009316678577119033, 0.008940633044337279, 0.008254559604254643, 0.0073601661729273725, 0.0073601661729273725, 0.00722041040261605, 0.00717486993925903, 0.006878909157272458, 0.006849871431995993, 0.006818067517041492, 0.0067249849546889146, 0.0067249849546889146, 0.006612626137465726, 0.006603579647120547, 0.006590163362067841, 0.006587281436968899, 0.0065821904382753265, 0.006575019334610879]
   w = 100
    ['710233', '144816', '797749', '290018', '768914', '563525', '1196408', '260137', '794512', '789886', '967663', '765407', '883946', '763689', '113198', '345787', '1214207', '568669', '1451388', '920433']
[0.36551953744596233, 0.010978774343883, 0.009290348404747717, 0.008904020259137285, 0.007354057538819896, 0.007354057538819896, 0.007158572539909351, 0.007075057601612086, 0.0068254516376616324, 0.006763103919663154, 0.006754326979401027, 0.00674884819794999, 0.0067202811161451255, 0.0067202811161451255, 0.006715607535202876, 0.006712313388745525, 0.006709597117770477, 0.0067088770100314265, 0.006707551494437893, 0.006704380477872021]
    """

    # set_interests = {
    #     "setNodes": [
    #                    {
    #                       "id": "123",  # id作为唯一标识,
    #                       "tag": "Javier López",  # tag作为节点的标签.
    #                       "dbname": "Coauthor_Visualization.db",  # 数据库名称.
    #                       "field": "name",  # 数据库表字段.
    #                       "keyword": "visualization technique",  # 关键字. algorithms concretization;traditional algorithm visualization technique;hands-on robotics;real physical world;real world;software visualization;basic idea;computer screen;current mode;data structure
    #                       "attributesValue": {"institution": "University of aaa", "interests": "AAA;BBB;CCC;DDD"}
    #                     },
    #                     {
    #                         "id": "456",  # id作为唯一标识,
    #                         "tag": "jingjing",  # tag作为节点的标签.
    #                         "dbname": "Coauthor_Visualization.db",  # 数据库名称.
    #                         "field": "name",  # 数据库表字段.
    #                         "keyword": "visualization tool",  # 关键字.
    #                         "attributesValue": {"institution": "University of bbb",
    #                                             "interests": "NULL;222;333"}
    #                     },
    #
    #     ],
    #     "setKeyword": []
    #
    # }

    # set_interests = {'setNodes': [{'attributesValue': {
    #     'institution': 'ESATSCD, Katholieke Universiteit Leuven, Leuven, Belgium,IBBTK.U.Leuven Future Health Department, Katholieke Universiteit Leuven, Leuven, Belgium',
    #     'interests': 'supplementary data;Bioinformatics online;ligand pair;visualization tool;genetic algorithm;ChIP-chip experiment data;available data set;data analysis;data miner;high dimensional data'},
    #     'tag': 'Georgios A. Pavlopoulos', 'field': 'interests', 'dbname': 'Coauthor_Visualization.db',
    #     'keyword': 'visualization tool', 'id': 275436}, {'attributesValue': {
    #     'institution': 'Simon Fraser University Burnaby, BC V5A 1S6, Canada;Department of Computer Science, University of British Columbia, 2366 Main Mall, Vancouver BC, V6T 1Z4 Canada.;University of Victoria, Victoria, BC;University of Victoria',
    #     'interests': 'orientation icon;visualization tool;information visualization novice;scientific visualization;visualization specification;collaborative visual data analysis;data analysis;data model;non-spatial data;spatial data'},
    #     'tag': 'Melanie Tory', 'field': 'interests',
    #     'dbname': 'Coauthor_Visualization.db',
    #     'keyword': 'visualization tool', 'id': 1224391}, {
    #     'attributesValue': {
    #         'institution': 'Universidade Federal do Pará, Brasil;Centro de Universitário do Pará (CESUPA), BelémPABrasil;Centro Universitário do Pará Brasil',
    #         'interests': 'data dynamic filter;desktop information visualization tool;information visualization;Augmented Reality environment;software tool;AR environment;real environment;attribute selection;common task;customized version'},
    #     'tag': 'Aruanda Simoes Goncalves', 'field': 'interests', 'dbname': 'Coauthor_Visualization.db',
    #     'keyword': 'visualization tool', 'id': 634439}, {
    #     'attributesValue': {'institution': 'IBM T.J. Watson Research Center',
    #                         'interests': 'information visualization technique;three-dimensional visualization;visualization module;options data;patient record data;complex interaction;custom 3-D visualization;information visualization presentation;information visualization toolkit;interactive information visualization environment'},
    #     'tag': 'D. L. Gresh', 'field': 'interests', 'dbname': 'Coauthor_Visualization.db',
    #     'keyword': 'visualization tool', 'id': 650856}, {'attributesValue': {'institution': 'NULL',
    #                                                                          'interests': 'Illustrative Visualization;GPU-based interactive visualization;egocentric visualization;visualization method;visualization strategy;visualization tool;general relativistic ray;image-based special relativistic rendering;relativistic scenario;special relativistic'},
    #                                                      'tag': 'C. Zahn', 'field': 'interests',
    #                                                      'dbname': 'Coauthor_Visualization.db',
    #                                                      'keyword': 'visualization tool', 'id': 591262}],
    #     'setKeyword': []}
    #
    # graph = get_subgraph_using_RWR(
    #         g=graph_doi.g,
    #         set_interests=set_interests,
    #         restart_prob=0.7,
    #         attri2node_weight=1,
    #         edges_list_with_weight=graph_doi.edges_list_with_weight,
    #         dbname="DB/Coauthor_Visualization.db",
    #         which_table="author",
    #         nodes_id_list=graph_doi.nodes_id_list,
    #         nodes_name_list=graph_doi.nodes_name_list,
    #         num_subgraph_nodes=20
    #     )
    #
    # print(graph)







    """
    实验结果:
    一. 同类型属性节点-作者节点的权重都一样
    1. 3个属性节点: "interactive exploration", "volume rendering", " information visualization"
       种子节点:["interactive exploration"]
    attri2node_weight = 1:
    ['interactive exploration', 345787, 260137, 920433, 1622761, 1451388, 1214207, 763689, 87893, 967663]
    [0.7625808460601079, 0.013471017869481676, 0.013471017869481676, 0.013459075643406171, 0.013457310685651092, 0.013457310685651092, 0.013457310685651092, 0.013457310685651092, 0.013457310685651092, 0.013457310685651092]
    
    attri2node_weight = 10
    ['interactive exploration', 345787, 260137, 920433, 1622761, 967663, 1451388, 1214207, 763689, 568669]
    [0.7625808460601079, 0.013471017869481676, 0.013471017869481676, 0.013459075643406171, 0.013457310685651092, 0.013457310685651092, 0.013457310685651092, 0.013457310685651092, 0.013457310685651092, 0.013457310685651092]
    
    attri2node_weight = 100
    ['interactive exploration', 345787, 260137, 920433, 789886, 967663, 1214207, 568669, 765407, 883946]
    [0.7625808460601079, 0.013471017869481676, 0.013471017869481676, 0.013459075643406171, 0.013457310685651092, 0.013457310685651092, 0.013457310685651092, 0.013457310685651092, 0.013457310685651092, 0.013457310685651092]
   结论: 权重对这种情况几乎没有影响.
    
    2. 3个属性节点: "interactive exploration", "volume rendering", " information visualization"
       种子节点:["interactive exploration", "710233"]


['interactive exploration', '710233', '144816', '797749', '290018', '1196408', 345787, 260137, 920433, 1622761]
[0.3812904694267809, 0.367217687053883, 0.011129163819320538, 0.009341946472128337, 0.009055673499445813, 0.007317103484816166, 0.006735505978424308, 0.006735505978424308, 0.0067295350625342885, 0.006728652613606312]

['interactive exploration', '710233', '144816', '797749', '290018', '1196408', 345787, 260137, 920433, 1451388]
[0.3812904694267809, 0.367217687053883, 0.011129163819320536, 0.009341946472128337, 0.009055673         499445813, 0.007317103484816166, 0.006735505978424308, 0.006735505978424308, 0.0067295350625342885, 0.006728652613606312]

['710233', '144816', '797749', '290018', '1196408', '336471', '981099', '905222', '1641204', '769398']
[0.7344354138257488, 0.02225832992636813, 0.018683893377326073, 0.018111348053102244, 0.014634207761749974, 0.012271914423735559, 0.008710412680227198, 0.008328169472518096, 0.006390936123134625, 0.00577784694152525]


['710233', '144816', '797749', '290018', '1196408', '336471', '981099', '905222', '1641204', '769398']
[0.7344354138257488, 0.022258329926368132, 0.018683893377326073, 0.018111348053102244, 0.014634207761749974, 0.012271914423735559, 0.008710412680227198, 0.008328169472518096, 0.006390936123134625, 0.00577784694152525]



结论: 权重对这种情况几乎没有影响.
        初步证明:
      不同属性值之间是独立的,还需要进一步的验证.
      不同属性之间是否独立要看接下来的实验验证.
      明天: 字段改成列表:多个字段,不同字段,对应不同的属性值,这个怎么对应,明天要搞清楚.
    """



