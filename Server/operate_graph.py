# coding: utf-8
from pylab import *  # 时间.
# We need to import the graph_tool module itself
import graph_tool.all as gt
import json
import sqlite3
from datetime import datetime
import os
import copy
import heapq
from operate_db import get_db_table_fields


# fixme:后台使用sfdp_layout算法获得全局图.
def get_global_graph_using_sfdp_layout(dbname, directed=None, which_table="edge", json_file_path="json/graph"):
    """
    :param dbname: 数据库路径.
    :param which_table: edge表.
    :param json_file_path: 生成json文件的存放路径.
    :return: 一个json文件
    """
    start_time = datetime.now()
    orig_name = dbname
    file_name = dbname.strip().split("/")[-1].split(".")[0]  # 文件名称. e.g. Citation_Visualization
    print(file_name)
    save_json_file_path = json_file_path + "/" + file_name + ".json"  # json/graph/Citation_Visualization.json

    # todo:如果不存在则创建.
    is_exist_file = os.path.exists(save_json_file_path)
    print(is_exist_file)
    if is_exist_file:  # 如果存在
        print("Global graph file already existed in " + json_file_path)
        return
    else:  # 不存在则创建
        print("creating Global graph file")
        db = sqlite3.connect(orig_name)  # 打开数据库
        print("open database successfully")
        cursor = db.cursor()
        sql = "select source, target from " + which_table
        cursor.execute(sql)
        lines = cursor.fetchall()  # [(source, target), ...]
        # print(lines[:10])
        graph = {
            "nodes": [],
            "edges": []
        }
        node_set = set()
        edge_list = []
        for line in lines:  # line=(source, target)
            source = line[0]
            target = line[1]
            node_set.add(source)
            node_set.add(target)
            edge_list.append((source, target))
        node_list = list(node_set)
        edge_list_with_index = []
        edge_obj_list = []
        counter = -1
        for edge in edge_list:
            counter = counter + 1
            source = edge[0]
            target = edge[1]
            temp = {}
            temp["id"] = "e" + str(counter)
            temp["source"] = source
            temp["target"] = target
            temp["size"] = 1
            temp["color"] = '#ccc'
            source_index = node_list.index(source)
            target_index = node_list.index(target)
            edge_list_with_index.append((source_index, target_index))
            edge_obj_list.append(temp)
        graph["edges"] = edge_obj_list

        G = gt.Graph(directed=directed)  # 创建图实例.
        N = len(node_list)
        G.add_vertex(n=N)  # 节点数量.
        G.add_edge_list(edge_list_with_index)  # 添加边.

        pos = gt.sfdp_layout(G)  # 使用胡一凡的sfdp_layout算法,获得节点的坐标.
        # gt.graph_draw(G, pos, vertex_text=G.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
        #               output_size=(800, 800), output=None)
        node_obj_list = []
        counter = -1
        for each_pos in pos:
            counter = counter + 1
            # print(each_pos)
            temp = {}
            temp["id"] = node_list[counter]
            temp["label"] = 'Node ' + str(counter)
            temp["x"] = each_pos[0]
            temp["y"] = each_pos[1]
            temp["size"] = 1
            temp["color"] = 'grey'
            node_obj_list.append(temp)
        graph["nodes"] = node_obj_list

        f_json = open(save_json_file_path, "w")
        json.dump(graph, f_json)  # 将数据写入json文件中.
        print("json file already saved in" + json_file_path)
        end_time = datetime.now()
        time = (end_time - start_time).seconds
        print("用时: " + str(time) + "秒")
        return graph


# fixme: 获得图的全局信息.
def get_global_graph_info(g):
    """
    :param g: graph-tool graph
    :return: global_graph_info
    """
    num_nodes = len(list(g.vertices()))
    num_edges = len(list(g.edges()))
    directed = g.is_directed()
    global_graph_info = {}
    global_graph_info["numnodes"] = num_nodes
    global_graph_info["numedges"] = num_edges
    global_graph_info["directed"] = directed

    return global_graph_info


# fixme: 找出列表num_list中前topk个值的索引
def getListMaxNumIndex(num_list, topk):
    """
    :param num_list: [x, xx ,xxx, ...]
    :param topk: m
    :return: [0, 6, 4, 7, ...], 前topk个值对应的索引列表,无重复.
    """
    num_dict = {}
    for i in range(len(num_list)):
        num_dict[i] = num_list[i]
    res_list = sorted(num_dict.items(), key=lambda e: e[1])
    max_num_index = [one[0] for one in res_list[::-1][:topk]]
    return max_num_index


# fixme:根据前端选择的methods,计算出对应的measure.
def computing_measures_according_to_method(db_name, g, directed, v_API_doi_list, nodes_id_list, which_method, top_n, table_width="120"):
    """
    :param which_method: 哪一种方法,支持pagerank, degree, clossness, betweeness
    :param top_n: 排名前多少个节点.
    :return: 数量为top_n的节点列表.
    """
    tableheader = []  # tableheader, tabledata
    tabledata = []
    max_num_index_list = []
    db = sqlite3.connect(db_name)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    cursor = db.cursor()
    sql = "select * from node where id=?"
    # ['id', 'name', 'institution', 'num_papers', 'num_citation', 'H_index', 'P_index', 'UP_index', 'interests']
    col_name_list, _, _ = get_db_table_fields(dbname=db_name, table_name="node")

    for each_one in col_name_list:  # [id, name, institution, ...]
        # if each_one != "publications":
        temp_obj = {}
        temp_obj["prop"] = each_one
        temp_obj["label"] = each_one
        temp_obj["width"] = table_width  # 可以根据字符的数量确定宽度.
        tableheader.append(temp_obj)


    if which_method == "PageRank":
        print("using PageRank")
        max_num_index = getListMaxNumIndex(num_list=v_API_doi_list, topk=int(top_n))

    if which_method == "Degree":
        print("using Degree")
        if directed:  # 有向
            node_index_list = range(len(nodes_id_list))
            r_out = g.get_out_degrees(node_index_list)
            r_in = g.get_in_degrees(node_index_list)
            r_total = np.add(r_out, r_in)  # [x, x, xx, ...]
            r_total = list(r_total)
            max_num_index = getListMaxNumIndex(num_list=r_total, topk=int(top_n))

        else:  # 无向
            node_index_list = range(len(nodes_id_list))
            r_out = g.get_out_degrees(node_index_list)  # [100, 89, 700, ...]
            r_out = list(r_out)
            max_num_index = getListMaxNumIndex(num_list=r_out, topk=int(top_n))
    if which_method == "In-Degree":
        if directed:  # 有向
            node_index_list = range(len(nodes_id_list))
            # r_out = g.get_out_degrees(node_index_list)
            r_in = g.get_in_degrees(node_index_list)
            r_total = r_in  # np.add(r_out, r_in)  # [x, x, xx, ...]
            r_total = list(r_total)
            max_num_index = getListMaxNumIndex(num_list=r_total, topk=int(top_n))

    if which_method == "Out-Degree":
        if directed:  # 有向
            node_index_list = range(len(nodes_id_list))
            r_out = g.get_out_degrees(node_index_list)
            # r_in = g.get_in_degrees(node_index_list)
            r_total = r_out  # np.add(r_out, r_in)  # [x, x, xx, ...]
            r_total = list(r_total)
            max_num_index = getListMaxNumIndex(num_list=r_total, topk=int(top_n))

    if which_method == "Betweenness":
        print("using Betweenness")
        vprop, _ = gt.betweenness(g=g)
        betweenness_list = []
        for each_one in vprop:
            betweenness_list.append(each_one)
        max_num_index = getListMaxNumIndex(num_list=betweenness_list, topk=int(top_n))

    if which_method == "Closeness":
        print("using Closeness")
        cc = gt.closeness(g=g)
        cc_list = []
        for each_one in cc:
            cc_list.append(each_one)
        max_num_index = getListMaxNumIndex(num_list=cc_list, topk=int(top_n))

    ############################################################
    for each_index in max_num_index:  # [x, x, ...]
        node_id = nodes_id_list[each_index]  # 节点的id,字符串.
        cursor.execute(sql, (node_id,))
        data = cursor.fetchall()  # 使用这种方式取出所有查询结果 [()]
        for each_one in data:  # data=[(xx, xx, ...,xx)] each_one=(xx, xx, ...,xx)
            temp_obj = {}
            for i in range(len(each_one)):  # each_one=(xx, xx, ...,xx)
                key_obj = col_name_list[i]
                value = each_one[i]
                temp_obj[key_obj] = value
            tabledata.append(temp_obj)

    db.close()
    return tableheader, tabledata


if __name__ == "__main__":
    # dbname = "DB/Citation_Visualization.db"
    # directed = False
    # which_table = "edge"
    # json_file_path = "json/graph"
    #
    # get_global_graph_using_sfdp_layout(dbname=dbname, directed=directed, which_table=which_table, json_file_path=json_file_path)
    #
    #
    # file_name = "json/graph/" + "Citation_Visualization" + ".json"
    # is_exist_file = os.path.exists(file_name)
    # print(is_exist_file)
    #
    # if is_exist_file:  # 如果存在,则直接从路径中获取.
    #     with open(file_name, 'r') as load_f:
    #         load_dict = json.load(load_f)
    #         print(load_dict)
    # v_API_doi_list = [0.00019308920973551215, 6.038407395130295e-05, 2.4164974586679724e-05, 9.756243420515969e-05, 0.00012391620701380658, 2.4065426856424408e-05, 8.961205980344451e-05, 9.00277536368592e-05, 6.378844815105128e-05, 4.2393475923353446e-05]  # 0 2 1
    # topk = 3
    # max_num_index = map(v_API_doi_list.index, heapq.nlargest(topk, v_API_doi_list))
    # print(list(max_num_index))
    # max_num_index_list = []
    # for each_one in max_num_index:
    #     max_num_index_list.append(each_one)
    # print("max_num_index_list")
    # print(max_num_index_list)
    # a = [1, 8, 0]
    # b = [12, 18, 10]
    # c = np.add(a, b)
    # print(c)
    # node_index_list = range(3)
    # print(node_index_list)
    r_out = [90, 90, 90, 80, 79, 88, 55, 55, 55]
    # r = map(r_out.index, heapq.nlargest(int(6), r_out))
    # r = list(r)
    # print(r)
    nlargest_list = heapq.nlargest(int(5), r_out)
    # print(nlargest_list)
    # top_n_node_index_list = []
    # print("r_out.index")
    # print(r_out.index)



    max_num_index = getListMaxNumIndex(r_out, 5)
    print("max_num_index")
    print(max_num_index)





