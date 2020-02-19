# coding: utf-8
import json
import graph_tool.all as gt

# fixme: 全局图.用于后面的各种图操作.
g = gt.Graph(directed=False)
# fixme: 全局变量定义.
edges_list_with_weight = []  # [(source_id, target_id, weight), ...]
nodes_id_list = []  # fixme: 其索引与全局图g中节点的索引一一对应. e.g.[id0, id1, id2, ...idm],其中idm表示,该列表中索引m对应的节点id.
nodes_name_list = []  # [id0_name, id1_name, ...] 索引与节点索引一一对应.
v_doi_list = []  # 存储全局图的每个顶点扩散后的DOI值,用于扩展焦点.索引与节点索引一一对应.
v_API_doi_list = []  # 存储全局图顶点的API值列表. 索引与节点索引一一对应.
max_weight = []  # 存放最大权重值. 只有一个值.
node_attributes_type_box = []  # 节点属性类型盒,用于装节点的属性的类型对象, e.g. [{'num_citation': 'integer', 'P_index': 'real', 'interests': 'text'}]

# fixme: 读取已存在的数据库名称
db_name_list = []  # 存放数据库名称
db_name_directed_list = []  # 存放数据库中网络的方向性.
discard_fields_set = set()
full_compatibility_attr_set = set()
# fixme: 读取已存在的数据库名称(存放在数据库配置文件里)
with open("DB/database_config.json", 'r') as load_f:
    load_dict = json.load(load_f)
database_network = load_dict["database_network"]
for each_obj in database_network:
    name = each_obj["name"]
    directed = each_obj["directed"]
    db_name_list.append(name)
    db_name_directed_list.append(directed)
    discard_fields = each_obj["discard_fields"]  # [x, x, ...],在动态属性图构建时不考虑的字段.
    full_compatibility_attr = each_obj["full_compatibility_attr"]  # [xx, xx, ...], 全兼容,即可向上或向下兼容的属性.
    for i in discard_fields:
        discard_fields_set.add(i)
    for i in full_compatibility_attr:
        full_compatibility_attr_set.add(i)
# print(discard_fields_set)
discard_fields_list = list(discard_fields_set)  # fixme: 所有数据库不被考虑的字段的集合.
full_compatibility_attr_list = list(full_compatibility_attr_set)  # fixme: 所有数据库被指定可以上下兼容的属性集合.
# print("full_compatibility_attr_list")
# print(full_compatibility_attr_list)
with open("json/stopword/stopWords.json", 'r') as load_f:  # fixme: 获得停用词json文件.
    stopWords = json.load(load_f)  # stopWords是全局变量,在flask中调用方式:graph_doi.stopWords
print("已有数据库:")
print(db_name_list)
print(db_name_directed_list)
