# coding: utf-8
from pylab import *  # 时间.
# We need to import the graph_tool module itself
import graph_tool.all as gt
from implementation_doi import compute_API_doi, doi_diffusion
from operate_db import read_table_edge_from_db, read_table_edge_from_db_for_change_db
import networkx as nx
import json
import matplotlib
import sqlite3
import numpy as np
from datetime import datetime
import re
import matplotlib.pyplot as plt
# 用于字符串的模糊匹配
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import random

import copy
import heapq

def test_1():
    g = gt.Graph(directed=False)  # 无向.

    def test(g, directed=None, links_list=None):
        g.set_directed(is_directed=directed)  # 设置方向性.
        g.clear()
        g.reindex_edges()
        N = 4
        g.add_vertex(n=N)
        # links_list = [(0, 1), (0, 2), (1, 2), (0, 3)]
        g.add_edge_list(edge_list=links_list)  # 添加边.

    links_list = [(0, 1), (0, 2), (1, 2), (0, 3)]
    test(g=g, directed=False, links_list=links_list)
    for i in g.get_edges():
        print(i)

    print("\n")
    links_list = [(0, 1), (0, 2), (1, 2), (0, 3), (3, 4)]
    test(g=g, directed=False, links_list=links_list)
    for i in g.get_edges():
        print(i)


def test_2():
    G = nx.DiGraph()
    edge_list = [(1, 2), (3, 1), (4, 5), (5, 1)]
    G.add_edges_from(edge_list)
    for i in G.edges():
        print(i)
    """
    G=nx.Graph() 无向图
    """
    # r = nx.clustering(G)
    # print(r)
    nodes_list = list(G.nodes())
    print("nodes_list")
    print(nodes_list)
    # r = nodes_list.index(5)
    og_not_normalized = nx.to_numpy_matrix(G)
    print("og_not_normalized")
    print(og_not_normalized)


def test_3():
    # start_time = datetime.datetime.now()
    G = gt.Graph(directed=True)
    # # fixme: 全局变量定义.
    # edges_list_with_weight = []  # [(source_id, target_id, weight), ...]
    # nodes_id_list = []  # [id0, id1, ...]
    # nodes_name_list = []  # [id0_name, id1_name, ...]
    # dbname = "DB/Citation_Visualization.db"
    # links_list = read_table_edge_from_db_for_change_db(dbname=dbname, edges_list_with_weight=edges_list_with_weight,
    #                                                    nodes_id_list=nodes_id_list, nodes_name_list=nodes_name_list)
    # g.set_directed(is_directed=False)  # 设置方向性.
    # N = len(nodes_id_list)  # 节点数量
    # g.add_vertex(n=N)
    # g.add_edge_list(edge_list=links_list)  # 添加边.
    # print("图初始化完成")
    #
    # # fixme: 添加图的边权重属性.
    # weight = g.new_edge_property("double")  # {e1:xx, e2: xx, e3: xx, ...}
    # g_edges = g.get_edges()
    # for edge_with_index in g_edges:
    #     edge = edge_with_index[:2]  # [source, target]
    #     index_edge = edge_with_index[2]  # index of edge.
    #     weight[edge] = edges_list_with_weight[index_edge][2]  # 从edges_list_with_weight里面取得对应边的权重.
    # # todo: 这个是否必要?
    # g.edge_properties["weight"] = weight  # {"weight":{e1:xx, ...}}, 获得对应边的权重: r = g.edge_properties["weight"][edge]
    #
    # print("连通图的节点+边数量: ", N, len(links_list))
    # end_time = datetime.datetime.now()  # start_time = datetime.datetime.now() # time = (end_time - start_time).seconds
    # time = (end_time - start_time).seconds
    # print("用时: " + str(time) + "秒")

    edge_list = [(0, 1), (0, 2), (1, 2), (1, 3)]
    weight_edges = [0.2, 0.5, 0.7, 0.9]
    # edge_list = [("mao", "ting"), ("mao", "ting"), ("mao", "yun")]

    G.add_edge_list(edge_list)
    edge_weights = G.new_edge_property('double')
    count = -1
    for e in G.edges():
        count += 1
        edge_weights[e] = weight_edges[count]
    # N = 4
    # nodes_list = [i for i in range(N)]
    # print(nodes_list)
    # d = G.get_out_degrees(vs=nodes_list, eweight=edge_weights)
    # print(d)
    # pg = gt.pagerank(g=G, weight=edge_weights)
    # print(list(pg))
    a = G.edge_index((0, 1))
    print(a)
    # r = edge_weights[(0, 1)]
    #
    # print(r)

    # todo:待会测试时间,用edge_weights及用g.edge_properties["weight"]

    '''
    无向:
      [ 0.7  1.8  1.2  0.9]
      [0.16577559753760573, 0.3751374205688214, 0.2621534019296019, 0.19693357996397085]
    有向:
      [ 0.7  1.6  0.   0. ]
      [0.037500000000000006, 0.04660714285714287, 0.07759988839285716, 0.05978404017857144]
    
    '''
    # pos = gt.sfdp_layout(G)
    # gt.graph_draw(G, pos, vertex_text=G.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2, output_size=(400, 400), output=None)


# 抽取DOI子图
def extract_doi_subgraph(g, edges_list_g, subgraph_nodes_list=None):
    """
    :param g: falsk启动时创建的全局图. graph-tool undireced Graph instance.
    edges_list_g: edges_list_g=[(source, target, value), ...]
    :param subgraph_nodes_list: list of subgraph nods, e.g.[0, 1, 5, 7],里面是图的索引.
    :return: subgraph_edges_listge格式与edges_list_g一致, subgraph_edges_listge=[(source, target, value), ...]
    """
    vfilt = g.new_vertex_property('bool')  # create PropertyMap instance for extracting subgraph.
    for v in subgraph_nodes_list:
        vfilt[v] = True
    # TODO: 获得子图.注意: 使用GraphView(),这个实例与原始图g共享数据,所以GraphView()修改,e.g. 添加,移除会改变原始图的数据.
    sub = gt.GraphView(g, vfilt)
    subgraph_edges_list = []  # [(source, target, weight),...]
    for e in sub.get_edges():  # 注意:使用 sub.get_edges() 这种方式可以获得边的索引.
        edge_index_in_org_graph = e[2]  # 获得该边在原图中的索引
        edge = edges_list_g[edge_index_in_org_graph]
        subgraph_edges_list.append(edge)

    # subgraph_edges_list = [(g.vertex_index[e.source()], g.vertex_index[e.target()]) for e in sub.edges()]
    # print("subgraph_edges: ", subgraph_edges_list[0])

    # subg = gt.Graph()
    # N = len(subgraph_nodes_list)
    # subg.add_vertex(n=N)
    # print("original graph layout")
    # pos = gt.sfdp_layout(g)
    # gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
    #               output_size=(200, 200), output=None)
    """
    注意: 这样获得的子图布局出来,其索引就是原图中对应的索引,因为它们共享同一份数据.
    """
    # print("subgraph layout")
    # pos = gt.sfdp_layout(sub)
    # gt.graph_draw(sub, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
    #               output_size=(200, 200), output=None)
    return subgraph_edges_list


# 使用贪心算法获得DOI子图.
def get_subgraph_with_greedy_algorithm(g, focus=None, total_num_doi_subgraph=None, directed=False):
    """
    :param g: a graph with DOI value in graph-tool
    :param focus: a node specified by user,是graph-tool图的索引.
    :param total_num_doi_subgraph: number of nodes in DOI subgraph.
    :return: F, nodes list of DOI subgraph. e.g. [0, 1, 2, 3, 7, 8, 10],里面是图的索引.
    """
    # TODO: 当前代码用于无向图,以后扩展为有向图.
    focus = focus  # 指定焦点.
    total_num_doi_subgraph = total_num_doi_subgraph  # 子图节点数量
    F = set()  # DOI子图集
    C = set()  # DOI子图候选集

    # 初始化F C
    F.add(focus)
    # print(len(F))
    # print(g.get_in_neighbors(focus))
    if directed:
        in_neighbors_list = g.get_in_neighbors(focus)
        out_neighbors_list = g.get_out_neighbors(focus)
        neighbors_list = list(in_neighbors_list) + list(out_neighbors_list)
        for i in neighbors_list:  # 将焦点的邻居存放到C中
            C.add(i)

        while len(F) < total_num_doi_subgraph:  # 直到满足F中的节点数量达到total_num_doi_subgraph OR C为空
            if len(C) == 0:  # if null, jump out of loop.
                break
            CC = list(C)  # set transforms into list for using index.
            # print(CC)
            temp_doi_list = []
            for each_one in CC:
                temp_doi = g.vertex_properties["doi"][each_one]  # v_pr_array[each_one] is also ok.
                # print("doi: ", temp_doi)
                temp_doi_list.append(temp_doi)
            temp_doi_list = np.array(temp_doi_list)
            max_index = temp_doi_list.argmax()  # 最大值所在的索引
            node_index_max_doi = CC[max_index]
            # print("node_index_max_doi: ", node_index_max_doi)
            F.add(node_index_max_doi)  # F添加一个节点
            # print("len(F)", len(F))
            # print(F)
            C.remove(node_index_max_doi)  # C中移除这个点
            node_index_max_doi_in_neighbors = g.get_in_neighbors(node_index_max_doi)
            node_index_max_doi_out_neighbors = g.get_out_neighbors(node_index_max_doi)
            node_index_max_doi_neighbors = list(node_index_max_doi_in_neighbors) + list(node_index_max_doi_out_neighbors)
            for i in node_index_max_doi_neighbors:  # 并将该点的邻居添加到C中
                if i not in F:  # 要保证邻居不在F中,避免死循环.
                    # print("neighbor: ", i)
                    C.add(i)

    else:
        for i in g.get_in_neighbors(focus):  # 将焦点的邻居存放到C中
            C.add(i)
        # v_pr_array = np.array(v_doi_list)
        while len(F) < total_num_doi_subgraph:  # 直到满足F中的节点数量达到total_num_doi_subgraph OR C为空
            if len(C) == 0:  # if null, jump out of loop.
                break
            CC = list(C)  # set transforms into list for using index.
            # print(CC)
            temp_doi_list = []
            for each_one in CC:
                temp_doi = g.vertex_properties["doi"][each_one]  # v_pr_array[each_one] is also ok.
                # print("doi: ", temp_doi)
                temp_doi_list.append(temp_doi)
            temp_doi_list = np.array(temp_doi_list)
            max_index = temp_doi_list.argmax()  # 最大值所在的索引
            node_index_max_doi = CC[max_index]
            # print("node_index_max_doi: ", node_index_max_doi)
            F.add(node_index_max_doi)  # F添加一个节点
            # print("len(F)", len(F))
            # print(F)
            C.remove(node_index_max_doi)  # C中移除这个点
            for i in g.get_in_neighbors(node_index_max_doi):  # 并将该点的邻居添加到C中
                if i not in F:  # 要保证邻居不在F中,避免死循环.
                    # print("neighbor: ", i)
                    C.add(i)

    return list(F)


# 测试贪心算法,用于DOI子图的获取.
def test_get_subgraph_with_greedy_algorithm(diffusion_factor, directed):
    """
        第一步: 创建图,准备图数据.
    """

    g = gt.Graph(directed=directed)
    N = 11  # 节点数量
    g.add_vertex(n=N)
    data_type = "fake"
    edges_list = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 7), (0, 8), (7, 8), (7, 9), (7, 10), (4, 5), (5, 6), (1, 2), (1, 4)]
    g.add_edge_list(edge_list=edges_list)
    r = gt.pagerank(g)
    print(r)
    v_doi_list = []
    for i in r:
        # print(i)
        v_doi_list.append(i)
    print(v_doi_list)

    v_prop_DOI = g.new_vertex_property("double")  # 给节点添加 doi 属性
    for v in g.vertices():
        v_prop_DOI[v] = v_doi_list[int(v)]
    g.vertex_properties["doi"] = v_prop_DOI  # 将pr值作为每个节点的pagerank属性值, 映射: v-->{"doi": 0.04633}
    # for i in g.vertex_properties["doi"]:
    #     print(i)
    fake_value = [0.5, 0.3, 0.4, 0.5, 0.1, 0.9, 0.8, 0.2, 0.22, 0.15, 0.17]
    if data_type == "fake":

        counter = -1
        for i in fake_value:
            counter = counter + 1
            g.vertex_properties["doi"][counter] = i  # 这种写法,必须在g.vertex_properties["doi"] = v_prop_DOI之后.
    # print("g.vertex_properties[doi][counter]")
    # t = g.vertex_properties["doi"][0]
    # print(t)
    # g.vertex_properties["doi"][0] = 100
    # t = g.vertex_properties["doi"][0]
    # print(t)
    edges_list = [(0, 1, 3), (0, 2, 5), (0, 3, 7), (0, 4, 5), (0, 7, 8), (0, 8, 5), (7, 8, 8), (7, 9, 3), (7, 10, 2), (4, 5, 7), (5, 6, 8), (1, 2, 9),
                  (1, 4, 7)]  # 在原来的边上增加了权重.
    orig_graph = {"nodes": [], "links": []}
    nodes = set()
    for edge in edges_list:
        source = edge[0]
        target = edge[1]
        weight = edge[2]
        temp_edge = {"source": str(source), "target": str(target), "value": str(weight)}
        orig_graph["links"].append(temp_edge)
        nodes.add(source)
        nodes.add(target)
    for node in nodes:
        temp_node = {"id": str(node), "name": str(node), "value": g.vertex_properties["doi"][node]}
        orig_graph["nodes"].append(temp_node)

    doi_diffusion(g=g, diffusion_factor=diffusion_factor, is_Edge_Attri=False, directed=directed)

    difussion_graph = {"nodes": [], "links": []}
    nodes = set()
    for edge in edges_list:
        source = edge[0]
        target = edge[1]
        weight = edge[2]
        temp_edge = {"source": str(source), "target": str(target), "value": str(weight)}
        difussion_graph["links"].append(temp_edge)
        nodes.add(source)
        nodes.add(target)
    for node in nodes:
        temp_node = {"id": str(node), "name": str(node), "value": g.vertex_properties["doi"][node]}
        difussion_graph["nodes"].append(temp_node)
    # [0, 1, 2, 3, 7, 8, 10]
    """
        第二步: 使用贪心算法,抽取DOI子图节点.
    """
    focus = 0
    total_num_doi_subgraph = 7
    F = get_subgraph_with_greedy_algorithm(g=g, focus=focus, total_num_doi_subgraph=total_num_doi_subgraph, directed=directed)
    print("F")
    print(F)
    # pos = gt.sfdp_layout(g)
    # gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2, output_size=(200, 200), output="jingjing.pdf")
    """
        第三步: 抽取DOI子图.
    """
    # TODO: 下一步抽取DOI子图
    subgraph_edges_list = extract_doi_subgraph(g, edges_list_g=edges_list, subgraph_nodes_list=F)
    print("subgraph_edges_list")
    print(subgraph_edges_list)
    doi_graph = {"nodes": [], "links": []}
    nodes = set()
    for edge in subgraph_edges_list:
        source = edge[0]
        target = edge[1]
        weight = edge[2]
        temp_edge = {"source": str(source), "target": str(target), "value": str(weight)}
        doi_graph["links"].append(temp_edge)
        nodes.add(source)
        nodes.add(target)
    for node in nodes:
        temp_node = {"id": str(node), "name": str(node), "value": g.vertex_properties["doi"][node]}
        doi_graph["nodes"].append(temp_node)
    return orig_graph, difussion_graph, doi_graph


def test_4(directed=True):
    G = gt.Graph(directed=directed)
    edge_list = [(0, 1), (0, 2), (1, 2), (3, 0)]
    N = 4
    G.add_vertex(n=N)
    G.add_edge_list(edge_list)
    out_neighbors_list = G.get_out_neighbors(v=0)
    print(out_neighbors_list)
    in_neighbors_list = G.get_in_neighbors(v=0)
    print(in_neighbors_list)
    neighbors_list = list(out_neighbors_list) + list(in_neighbors_list)
    print(neighbors_list)

    pos = gt.sfdp_layout(G)
    gt.graph_draw(G, pos, vertex_text=G.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2, output_size=(400, 400), output=None)


def test_centrality():
    directed = False
    g = gt.Graph(directed=directed)
    N = 11  # 节点数量
    g.add_vertex(n=N)

    edges_list = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 7), (0, 8), (7, 8), (7, 9), (7, 10), (4, 5), (5, 6), (1, 2),
                  (1, 4)]
    g.add_edge_list(edge_list=edges_list)
    # pos = gt.sfdp_layout(g)
    # gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
    #               output_size=(400, 400), output=None)
    # g = gt.collection.data["polblogs"]
    # g = gt.GraphView(g, vfilt=gt.label_largest_component(g))
    vp, ep = gt.betweenness(g)
    # print("vp")
    # print(vp)
    # for i in vp:
    #     print(i)
    # print("ep")
    # print(ep)
    pos = gt.sfdp_layout(g)
    for i in pos:
        print(i)
    gt.graph_draw(g,
                 pos=pos,
                 vertex_fill_color=vp,
                 vertex_text=g.vertex_index,
                 vertex_size=gt.prop_to_size(vp, mi=5, ma=15),
                 # edge_pen_width=gt.prop_to_size(ep, mi=0.5, ma=5),
                 # vcmap=matplotlib.cm.gist_heat,
                 vorder=vp,
                 output=None)

    # gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
    #               output_size=(400, 400), output=None)


def get_author_id_list(dbname):

    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    print("Opened database successfully")
    sql = "select id from node"
    cursor.execute(sql)
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果
    id_authors_list = []  # 作者id列表.
    for each_one in data:
        # print(each_one)
        id_authors_list.append(each_one[0])
    print(len(id_authors_list))
    print(id_authors_list)
    return id_authors_list


def get_papers_for_each_author(dbname, author_list):
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    print("Opened database successfully")
    papers_list_for_all_authors = {}  # {id:[x, x, x,], id:[x, x, x,], ...}
    papers_set_for_all_authors = set()  # 用于后面抽取出所有可视化领域的论文.
    for each_author in author_list:  # todo: gai
        sql = "select id_paper from author2paper where id_author=?"
        cursor.execute(sql, (each_author,))
        data = cursor.fetchall()  # 使用这种方式取出所有查询结果
        papers_each_author_list = []  # 每个作者对应的论文id列表.

        for each_p in data:  # each_p=(x,), data=[(), (), (), ...()]
            paper_id = each_p[0]
            papers_set_for_all_authors.add(paper_id)
            papers_each_author_list.append(paper_id)
        papers_list_for_all_authors[each_author] = papers_each_author_list

    return papers_list_for_all_authors, papers_set_for_all_authors

# def insert_papers_into_node():
#
#         sql = "update node set ref=? where id=?"
#         cursor.execute(sql, (references_text, id_node))
#
#
#     db.commit()  # 必须提交事务,否则无法写入表格.
#     db.close()
"""
CREATE TABLE publications ( id int, title text, authors text, institution text, year text, public_venue text, id_reference text, abstract text )
"""


def abstract_visualization_papers(papers_set_for_all_authors):
    dbname = "DB/backup/AcademicNetwork.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("Opened database successfully")
    # 创建数据库中的游标对象
    cursor = db.cursor()


    all_records = []
    papers_set_for_all_authors = list(papers_set_for_all_authors)
    sql = "select * from paper where id=?"
    for each_one in papers_set_for_all_authors:
        cursor.execute(sql, (each_one,))
        row = cursor.fetchall()  # [()]
        # print("row")
        # print(row)
        all_records.append(row[0])
    # print("all_records")
    # print(all_records)

    dbname = "DB/new_coauthor_db/Coauthor_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("Opened database successfully")
    # 创建数据库中的游标对象
    cursor = db.cursor()
    for row in all_records:  # [(), (), ...]
        cursor.execute('''insert into publications (id, title, authors, institution, year, public_venue, id_reference, abstract)
                                            VALUES (?,?,?,?,?,?,?,?)''',
                       (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
    db.commit()  # 必须提交事务，否则无法写入表格
    db.close()

def deal_data_for_db():
    start_time = datetime.datetime.now()
    # time = (end_time - start_time).seconds

    author_list = get_author_id_list(dbname="DB/Coauthor_Visualization.db")  # 获得作者id列表.
    papers_list_for_all_authors, papers_set_for_all_authors = get_papers_for_each_author(
        dbname="DB/backup/AcademicNetwork.db", author_list=author_list)  # 获得每个作者id对应的论文id.

    print("author_list的大小:")
    print(len(author_list))
    print("papers_list_for_all_authors的大小:")
    print(len(papers_list_for_all_authors))
    print("papers_set_for_all_authors的大小")
    print(len(papers_set_for_all_authors))
    # print(papers_list_for_all_authors)


    dbname = "DB/new_coauthor_db/Coauthor_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("Opened database successfully")
    # 创建数据库中的游标对象
    cursor = db.cursor()
    sql = "update node set publications=? where id=?"

    for author_id in papers_list_for_all_authors:
        publications = ""
        for i in papers_list_for_all_authors[author_id]:
            publications = publications + str(i) + ";"
        publications = publications.strip(";")
        cursor.execute(sql, (publications, author_id))
    db.commit()  # 必须提交事务,否则无法写入表格.
    db.close()

    abstract_visualization_papers(papers_set_for_all_authors)
    end_time = datetime.datetime.now()
    time = (end_time - start_time).seconds
    print("time")
    print(time)


def get_all_tables_from_db(dbname="DB/Coauthor_Visualization.db"):
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    cursor = db.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    cursor.execute("SELECT * FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()  # Tables 为元组列表 [('author',), ('paper',), ('coauthor',), ('author2paper',)]
    # print("tables")  #[('author',), ('paper',), ('coauthor',), ('author2paper',)]
    # print(tables)  #[('author',), ('paper',), ('coauthor',), ('author2paper',)]
    db_tables_list = []
    for i in tables:
        tb = i[1]
        db_tables_list.append(tb)
    print(db_tables_list)


# fixme: 从指定的数据库 + 表中获得id对应的数据.
def get_data_from_db_table_id(dbname, which_table, id_list=None):
    """
    :param dbname: 数据库名称.
    :param which_table: 数据库中的哪一个表.
    :param id_list: id构成的列表,e.g. [id1, id2, ...],用于到数据库表中查询每个id对应的信息,然后在前端显示.
    :return:
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
    # print(ids_records_obj)
    return ids_records_obj


# fixme: 获得指定节点的n-order子图.
def get_n_order_subgraph(g, directed, edges_list_g, which_node=None, order_neighbor=1):
    """
    :param g: graph-tool graph
    :param edges_list_g: g的边列表.
    :param which_node:指定节点
    :param order_neighbor: 获得指定节点的n-order子图.
    :return: subgraph_edges_list, n-order子图的边列表.
    """
    candidate_set = set()
    candidate_set.add(which_node)  # {0}
    subgraph_node_set = set()
    subgraph_node_set.add(which_node)  # {0}

    for counter in range(order_neighbor):  # 邻居的阶数控制.
        temp_set = set()
        for each_v in candidate_set:  # 候选节点集.0阶:[0], 1阶:[1, 2, 3], 2阶:[4, 6, 8]

            if directed:  # 有向
                out_neighbors = g.get_out_neighbors(each_v)
                in_neighbors = g.get_in_neighbors(each_v)
                all_neighbors = list(out_neighbors) + list(in_neighbors)

            else:  # 无向
                all_neighbors = g.get_out_neighbors(each_v)

            for i in all_neighbors:  # 1阶:[1, 2, 3] 2阶: 1:[0, 2, 8] 2:[0, 1, 3, 6] 3:[0, 2, 4, 8]
                if i not in subgraph_node_set:  # 0阶:[0], 1阶:[0, 1, 2, 3], 2阶:[0, 1, 2, 3, 4, 6, 8]
                    temp_set.add(i)
                subgraph_node_set.add(i)

        candidate_set.clear()  # 先清除.
        for i in temp_set:  # 再加入.
            candidate_set.add(i)

    subgraph_nodes_list = list(subgraph_node_set)
    subgraph_edges_list = extract_subgraph(g=g, edges_list_g=edges_list_g, subgraph_nodes_list=subgraph_nodes_list)
    return subgraph_edges_list


# fixme: 抽取子图
def extract_subgraph(g, edges_list_g, subgraph_nodes_list=None):
    """
    :param g: falsk启动时创建的全局图. graph-tool undireced Graph instance.
    edges_list_g: edges_list_g=[(source, target, value), ...]
    :param subgraph_nodes_list: list of subgraph nods, e.g.[0, 1, 5, 7],里面是图的索引.
    :return: subgraph_edges_listge格式与edges_list_g一致, subgraph_edges_listge=[(source, target, value), ...]
    """
    vfilt = g.new_vertex_property('bool')  # create PropertyMap instance for extracting subgraph.
    for v in subgraph_nodes_list:
        vfilt[v] = True
    # TODO: 获得子图.注意: 使用GraphView(),这个实例与原始图g共享数据,所以GraphView()修改,e.g. 添加,移除会改变原始图的数据.
    sub = gt.GraphView(g, vfilt)
    subgraph_edges_list = []  # [(source, target, weight),...]
    for e in sub.get_edges():  # 注意:使用 sub.get_edges() 这种方式可以获得边的索引.
        edge_index_in_org_graph = e[2]  # 获得该边在原图中的索引
        edge = edges_list_g[edge_index_in_org_graph]
        subgraph_edges_list.append(edge)

    # graph drawing
    pos = gt.sfdp_layout(g)
    gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
                  output_size=(400, 400), output=None)
    # graph drawing
    pos = gt.sfdp_layout(sub)
    gt.graph_draw(sub, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
                  output_size=(400, 400), output=None)

    return subgraph_edges_list


def test_get_n_order_subgraph():
    edge_list = [(1, 0), (2, 4), (2, 0), (0, 3), (1, 8), (2, 6), (4, 3), (4, 5), (6, 7), (8, 9), (2, 3), (1, 2), (4, 6),
                 (3, 8)]
    # edge_list = [(0, 1), (1, 2), (2, 3), (4, 0), (2, 4)]
    nodes_set = set()
    for edge in edge_list:
        nodes_set.add(edge[0])
        nodes_set.add(edge[1])
    N = len(nodes_set)  # 节点数量
    directed = True
    g = gt.Graph(directed=directed)
    g.add_vertex(n=N)
    g.add_edge_list(edge_list=edge_list)

    subgraph_edges_list = get_n_order_subgraph(g=g, directed=directed, edges_list_g=edge_list, which_node=0,
                                               order_neighbor=2)
    print("subgraph_edges_list")
    print(subgraph_edges_list)


def test_heatmap(directed=True, edge_list=None):
    G = gt.Graph(directed=directed)
    edge_list = edge_list  # [(0, 1), (0, 2), (1, 2), (3, 0)]
    N = set()
    for each_edge in edge_list:
        N.add(each_edge[0])
        N.add(each_edge[1])

    N = len(N)
    G.add_vertex(n=N)
    G.add_edge_list(edge_list)
    out_neighbors_list = G.get_out_neighbors(v=0)
    print(out_neighbors_list)
    in_neighbors_list = G.get_in_neighbors(v=0)
    print(in_neighbors_list)
    neighbors_list = list(out_neighbors_list) + list(in_neighbors_list)
    print(neighbors_list)

    pos = gt.sfdp_layout(G)
    for i in pos:
        print(i)
    gt.graph_draw(G, pos, vertex_text=G.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2, output_size=(400, 400), output=None)
    return pos
"""
for (i = 0; i < N; i++)
  g.nodes.push({
    id: 'n' + i,
    label: 'Node ' + i,
    x: Math.random(),
    y: Math.random(),
    size: Math.random(),
    color: '#666'
  });

for (i = 0; i < E; i++)
  g.edges.push({
    id: 'e' + i,
    source: 'n' + (Math.random() * N | 0),
    target: 'n' + (Math.random() * N | 0),
    size: Math.random(),
    color: '#ccc'
  });
"""


def generate_graph():
    with open("static/data/connected_max_subgraph_citation_network_visualization.json") as f:
        lines = f.readlines()
        graph = {
            "nodes": [],
            "edges": []
        }
        node_set = set()
        edge_list = []
        for line in lines:
            line = line.split()
            print(line)
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

        directed = True
        G = gt.Graph(directed=directed)
        N = len(node_list)
        G.add_vertex(n=N)
        G.add_edge_list(edge_list_with_index)

        pos = gt.sfdp_layout(G)
        gt.graph_draw(G, pos, vertex_text=G.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
                      output_size=(800, 800), output=None)
        node_obj_list = []
        counter = -1
        for each_pos in pos:
            counter = counter + 1
            print(each_pos)
            temp = {}
            temp["id"] = node_list[counter]
            temp["label"] = 'Node ' + str(counter)
            temp["x"] = each_pos[0]
            temp["y"] = each_pos[1]
            temp["size"] = 8
            temp["color"] = '#666'
            node_obj_list.append(temp)
        graph["nodes"] = node_obj_list

        f_json = open("connected_max_subgraph_citation_network_visualization.json", "w")
        json.dump(graph, f_json)

        # return graph

def reconstruction_graph_with_attr_node(edges_list_with_weight=None, dbname=None, which_table="node", field_attri_values=None, seed_list=None, restart_prob=0.7, attri2node_weight=1, focus_id_list=None, directed=False, max_weight=None, stopWords=None):
    """
    :param edges_list_with_weight: 图的边,带权重.为了加快速度,将图数据保存在本地.[(source, target, weight), ...]
    :param dbname:存放图节点属性数据库名称.
    :param which_table: 指明数据库中的哪一张表.
    :param field:属性名字,即表格的字段,是一个列表. field=["interests", "institutes"]
    :param field_attri_values:字段(即焦点需要考虑的属性)及其对应的值(属性值节点),是一个字典. attri_values={field1:[value1, value2, ...], field1:[value1, value2, ...]},比如作者合作网络里:{"institutions":[x, x, ...], "interests":[x, x, ...]}
    :param max_weight: edges_list_with_weight中的最大的权重值,用于后面的max-normalization. max_weight = [x], 这样做是为了使用地址.
    :param stopWords:停用词表.
    :return:
      nodes_max_min_only_id: 随机游走获得的概率值从高到低的节点列表.
      probs_max_min_only_id:随机游走获得的从高到低的概率值列表,与nodes_max_min_only_id一一对应.
    """
    arrCommonStopWords = stopWords["commonStopWords"]  # 通用停用词.
    obj = stopWords["customStopWords"]  # 自定义停用词,是一个对象{dbname:[], ...}
    cur_db_name = dbname.split("/")[-1]  # 数据库的名陈.
    arrCustomStopWords = obj[cur_db_name]  # 获得当前数据库对应的自定义停用词.
    stopWords_list = arrCommonStopWords + arrCustomStopWords  # 通用 + 自定义 停用词表.

    fields = list(field_attri_values.keys())  # ["institutions", "interests"]
    if attri2node_weight > 0.000000001 and len(fields) > 0:  # fixme: 如果前端weight_attr_node!=0 + 选中了属性,则正常执行.
        db = sqlite3.connect(dbname)
        print("Opened database successfully")
        attribute_to_node_list = []  # e.g. [(attribute, node, weight), ...] 这是"属性值-节点"的边列表.
        attri_vs_nodes_list = []  # 所有属性值匹配上的全局图的节点构成的列表. e.g. [id1, id2, ...,idm] 表示属性值对应的全局图中节点的id.
        # 创建数据库中的游标对象
        cursor = db.cursor()
        # fields = list(field_attri_values.keys())  # ["institutions", "interests"]

        # fixme: 首先获得数据库中中所有的数据,格式:(id, institutions, interests)
        field_string = "id"
        for each_one in fields:
            field_string += "," + each_one
        sql_ = "select " + field_string + " from " + which_table
        cursor.execute(sql_)  # condition: 主要针对文本类型的属性值.
        node_id_fields_list = cursor.fetchall()  # [(xx,xx,xx), (xx,xx,xx), ...]

        for each_field in fields:  # field=["institutions", "interests"]
            attri_values = field_attri_values[each_field]  # 取出字典里面字段对应的值列表.
            for query_item in attri_values:  # 例如:attri_values=["data visualization", "graph drawing"]
                # todo: 直接使用属性值去精确匹配数据库中节点对应的属性,例如:%data visualization% 能够匹配上 graph data visualization.
                # todo: 但是,对于一个机构来说,可能有多种表达,此时,直接使用焦点的属性值就会错失很多节点.可以使用单词级的匹配.

                # condition = "%" + query_item + "%"  # 备注:一定要使用%XXXX%的形式,否则返回空.
                # sql_ = "select id from " + which_table + " where " + each_field + " like ?"
                # cursor.execute(sql_, (condition,))  # condition: 主要针对文本类型的属性值.
                # data = cursor.fetchall()

                matched_node_list = get_matched_node(query_item=query_item,
                                          node_id_fields_list=node_id_fields_list,
                                          fields=fields,
                                          each_field=each_field,
                                          stopWords=stopWords_list)
                print("query_item")
                print(query_item)
                print("matched_node_list")
                print(matched_node_list)

                for each_one in matched_node_list:  # [id1, id2, ...]
                    source = query_item  # 属性值. string类型.
                    target = each_one  # id
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


# fixme:获得数据库中匹配的节点
def get_matched_node(query_item, node_id_fields_list, fields, each_field, stopWords):
      """
      :param query_item: 一个属性值,e.g. "data visualization"
      :param node_id_fields_list: [(id, field1_val, field2_val), ...]
      :param fields: 焦点考虑的字段列表:["institutions", "interests"]
      :param each_field: 当前字段,如"institutions"
      :param stopWords: 通用+自定义的停用词列表,[xx, xx, ..., xx]
      :return: query_item在数据库中匹配上的节点列表.如,[id1, id2, ...]
      """
      lowerCasekeyWord = query_item.lower()  # 先转换成小写
      result_list = re.split("，|,|&|\t|\s+", lowerCasekeyWord)  # 利用分隔符,转化成列表.
      word_set = set([x for x in result_list if x])  # 去掉空字符,取集合
      lowerCasekeyWordList = list(word_set)  # ["volume", "data", "visualization", "in"]

      counterLowerCasekeyWord = 0  # 属性值中有效词,即非空,非停用词的个数.
      newLowerCasekeyWordList = []  # 非空,非停用词.

      for each_one in lowerCasekeyWordList:
        if each_one != "":
          if each_one not in stopWords:  # 不在停用词表.
            counterLowerCasekeyWord = counterLowerCasekeyWord + 1  # 统计匹配非停用词的数量.
            newLowerCasekeyWordList.append(each_one)  # 有效词列表:["volume", "data", "visualization"],去掉停用词"in".

      allNodesKeysList = node_id_fields_list  #[("123", "institutions"), ("3456", "institutions"), ("567", "institutions"), ("891", "institutions")]  # 整个图的节点id列表. nodesAttrObj={id:{name:[x], field1:[x,...], field2:[x,...]},...}
      matchNodesSet = set()  # 属性值匹配上的节点集.["1223", "4567", "6678"]

      for each_one in allNodesKeysList:  # allNodesKeysList=[("123", "institutions"), ("3456", "institutions")]
        nodeId = each_one[0]  # 节点id.
        field_index = fields.index(each_field) + 1
        attr_val_string = each_one[field_index]  # "aaa;bbb;ccc"
        attr_val_string = attr_val_string.strip()
        attrValList = attr_val_string.split(";")  # 对象中指定属性对应的值构成的数组:attrValList=[x, x, ...]

        for each_word in attrValList:
          newStr = each_word.lower()  # 指定属性的某个取值: "ab, cc fg"

          result_list = re.split("，|,|&|\t|\s+", newStr)  # 利用分隔符,转化成列表.
          word_set = set([x for x in result_list if x])  # 去掉空字符,取集合
          newStrList = list(word_set)  # [ab, cc, fg, ""]
          newnewStrList = []  # 非空,非停用词.
          counterNewStrList = 0

          for each_string in newStrList:
            if each_string != "" and each_string not in stopWords:
               counterNewStrList = counterNewStrList + 1  # 加1.
               newnewStrList.append(each_string)  # newnewStrList=[ab, cc, fg]

          commonWordSet = set()  # 相同(相似)的单词的集合.

          for each_valid_word_in_attri_val in newLowerCasekeyWordList:  # 有效词列表:["volume", "data", "visualization"]
                for each_valid_word_in_db in newnewStrList:
                    if each_valid_word_in_db == each_valid_word_in_attri_val:  # 原来的模糊匹配改成完全匹配.
                       commonWordSet.add(each_valid_word_in_attri_val)
                       break  # 单词匹配上则跳出大循环,去判断下一个单词.

          matchSize = len(commonWordSet)  # 有效词中,公共词的个数.
          whichOne = counterLowerCasekeyWord  # 以标签上的属性值的有效词的个数为基准.

          if whichOne > 2:  # 不小于3个单词的时候,大于较小者的一半算是匹配上了.
            threshold = whichOne/2.0

          else:  # 不大于2个有效词,则需要完全匹配.
            threshold = whichOne

          if matchSize >= threshold:  # 如果匹配上的词的数量不小于最小的字符串的一半,则可以认为两个字符串描述的是一个实体.
            matchNodesSet.add(nodeId)
            break  # 已经确定当前节点是匹配节点,跳出大循环,判断下一个节点.

      return list(matchNodesSet)  # [id1, id2, ...]


# fixme:后台使用sfdp_layout算法获得全局图.
def get_global_graph_using_sfdp_layout(dbname, directed=None, which_table="edge", json_file_path="json/graph"):
    """
    :param dbname: 数据库路径.
    :param which_table: edge表.
    :param json_file_path: 生成json文件的存放路径.
    :return: 一个json文件
    """
    start_time = datetime.datetime.now()
    orig_name = dbname
    file_name = dbname.strip().split("/")[-1].split(".")[0]  # 文件名称. e.g. Citation_Visualization
    print(file_name)
    save_json_file_path = json_file_path + "/" + file_name + ".json"  # json/graph/Citation_Visualization.json

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
    # todo:如果不存在则创建.
    f_json = open(save_json_file_path, "w")
    json.dump(graph, f_json)  # 将数据写入json文件中.
    print("json file already saved in" + json_file_path)
    end_time = datetime.datetime.now()
    time = (end_time - start_time).seconds
    print("用时: " + str(time) + "秒")


def generate_citation_file():
    dbname = "DB/Citation_Visualization.db"
    db = sqlite3.connect(dbname)
    cursor = db.cursor()
    print("Opened database successfully")
    cursor.execute("select id, name from node")  # 从edge表中读取边.
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果
    citation_f = open("citation_id_name.txt", "a+")
    for each_one in data:
        print(each_one)
        id_citation = each_one[0].strip()
        name_citation = each_one[1].strip()
        citation_f.write(id_citation + ";" + name_citation + "\n")
    citation_f.close()
    print("finished citation_id_name.txt")
def mtylvjj():
    # extract_max_connected_component_from_patent_citation()
    # filter_patent_citation()
    """
    which_table = 'node'
    conditions = [{"selectionfield": "name", "keyWord": "chenjing"}]

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
    print(sql)
    print(cons_val)
    """
    #
    # dbname = "DB/Citation_Visualization.db"
    # directed = False
    # which_table = "edge"
    # json_file_path = "json/graph"
    #
    # get_global_graph_using_sfdp_layout(dbname=dbname, directed=directed, which_table=which_table, json_file_path=json_file_path)
    # import os
    # file_name = "json/graph/" + "Citation_Visualization" + ".json"
    # is_exist_file = os.path.exists(file_name)
    # print(is_exist_file)
    #
    # if is_exist_file:  # 如果存在,则直接从路径中获取.
    #     with open(file_name, 'r') as load_f:
    #         load_dict = json.load(load_f)
    #         print(load_dict)
    # g = gt.Graph(directed=False)
    # g.add_edge_list()
    # g = gt.Graph(directed=True)
    # N = 11  # 节点数量
    # g.add_vertex(n=N)
    #
    # edges_list = [(0, 1), (2, 0), (0, 3), (3, 4), (0, 7), (0, 8), (7, 8), (7, 9), (7, 10), (4, 5), (5, 6), (1, 2),
    #               (1, 4), (2, 4)]
    # g.add_edge_list(edge_list=edges_list)
    # pos = gt.sfdp_layout(g)  # 使用胡一凡的sfdp_layout算法,获得节点的坐标.
    #
    # path_all = gt.all_shortest_paths(g=g, source=g.vertex(4), target=g.vertex(0), weights=None)
    # print("有向图")
    # for each_path in path_all:
    #     print(each_path)
    # gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=4,
    #               output_size=(800, 800), output=None)
    #
    # g.set_directed(is_directed=False)  # 设置方向性.
    # path_all = gt.all_shortest_paths(g=g, source=g.vertex(4), target=g.vertex(0), weights=None)
    # print("无向")
    # for each_path in path_all:
    #     print(each_path)
    # gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=4,
    #               output_size=(800, 800), output=None)
    #
    # g.set_directed(is_directed=True)  # 设置方向性.
    # path_all = gt.all_shortest_paths(g=g, source=g.vertex(4), target=g.vertex(0), weights=None)
    # print("有向")
    # for each_path in path_all:
    #     print(each_path)
    # directed_g = g.is_directed()
    # print("directed_g 有向性")
    # print(directed_g)
    # gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=4,
    #               output_size=(800, 800), output=None)


def patent_citation():

    f = open("cite75_99.txt")
    lines = f.readlines()  # [(source, target), ...]
    # for each_one in lines[1:10]:
    #     each_one = each_one.strip()
    #     print(each_one)

    nodes_set = set()
    nodes_id_list = []
    links_list = []  # 里面的节点是nodes_id_list中对应节点的索引
    edges_list_with_weight = []

    for each_edge in lines[1:]:  # [(source, target), ...]
        # print(each_edge)
        edges_list_with_weight.append((each_edge[0], each_edge[1], 1))  # [(source_id, target_id, weight), ...]
        source = each_edge[0]
        target = each_edge[1]

        nodes_set.add(source)
        nodes_set.add(target)

    for each_item in nodes_set:  # nodes_set={id, ...}
        nodes_id_list.append(each_item)  # nodes_id_list=[id, ...]

    for edge in edges_list_with_weight:  # [(source_id, target_id, weight), ...]
        source = edge[0]
        target = edge[1]
        source_index = nodes_id_list.index(source)
        target_index = nodes_id_list.index(target)
        links_list.append((source_index, target_index))  # todo: 这里用的是非权重图,接下来要验证权重图.

    g = gt.Graph(directed=True)
    # g.set_directed(is_directed=directed)  # 设置方向性.
    N = len(nodes_id_list)  # 节点数量
    g.add_vertex(n=N)
    g.add_edge_list(edge_list=links_list)  # fixme:links_list是索引构成的边,格式:[(0, 2), ...],其中索引与nodes_id_list一一对应.
    # fixme: 全局图中节点的索引与nodes_id_list是一一对应的.


def extract_max_connected_component_from_patent_citation():
    """
    # 对于graph-tool而言, 只需要有边就可以构造出一个图来了,
    # e.g. e=[(), (), ...],从中提取节点个数,构造节点的索引,最后就可以构造出一个图了.

    """

    with open("cite75_99.txt", "r") as f:
        start_time = datetime.now()
        lines = f.readlines()
        print(len(lines))

        edges_list_with_weight = []
        nodes_set = set()
        for line in lines[1:]:
            line = line.strip()
            line = line.split(",")  # (source, target)
            # print(line)
            # edges_list_without_weight.append((line[0], line[1]))  # 不带权重
            edges_list_with_weight.append(line)  # 带权重.
            nodes_set.add(line[0])
            nodes_set.add(line[1])
        # TODO: # [node_id1, ...] 图中节点的索引就是这个列表的索引,所以可以根据这个列表,获得对应的节点在数据库表中的id,从而获得该节点的属性信息.
        nodes_id_list = list(nodes_set)

        links_list = []
        for edge in edges_list_with_weight:  # [(source, target), ...]
            source = edge[0]
            target = edge[1]
            source_index = nodes_id_list.index(source)
            target_index = nodes_id_list.index(target)
            links_list.append((source_index, target_index))
        # 注意: edges_list_with_weight 与 links_list 是一一对应的.
        g = gt.Graph(directed=True)
        N = len(nodes_set)  # 节点数量
        g.add_vertex(n=N)

        g.add_edge_list(edge_list=links_list)  # 添加边.

        print("原图的节点和边数量: ", N, len(links_list))

        # print("graph drawing.......")
        # pos = gt.sfdp_layout(g)
        # # gt.graph_draw(g, pos, vertex_text="0", vertex_font_size=8, vertex_size=10, edge_pen_width=1.2, output_size=(1000, 1000), output=None)
        # gt.graph_draw(g, pos, output="static/graph_drawing/mty_coauthor_visualization.pdf")

        # Draw the largest component
        # TODO: 注意: gt.label_largest_component中directed=True时,如果原图是有向的,directed=None,则会出错,写成directed=False就好了,不能提取出最大的连接子图.

        """
            # 注意:
            #  1. Graph: directed==Ture, 则gt.label_largest_component(g, directed=False)才能正确地抽取.
            #  2. Graph: directed==False, 则gt.label_largest_component(g, directed=False/None)都能正确地抽取.
        """
        print("extracting......")
        largest_comp = gt.GraphView(g, vfilt=gt.label_largest_component(g, directed=False))
        # max_connected_component_edges = list(largest_comp.edges())  # 7268 条边
        # max_connected_component_nodes = list(largest_comp.vertices())  # 2762 个节点
        #
        # print("max_connected_component_edges: ", max_connected_component_edges)
        # print("max_connected_component_nodes: ", max_connected_component_nodes)
        max_subgraph_edges_id_list = []
        # max_subgraph_nodes = largest_comp.get_vertices()  # 获得最大子图的节点的索引.
        max_subgraph_edges = largest_comp.get_edges()  # # 获得最大子图的边的索引.
        f_subg = open("max_connected_subgraph.txt", "w")
        for i in max_subgraph_edges:
            temp_edge_index = i[2]  # 边的索引
            temp_edge = edges_list_with_weight[temp_edge_index]
            # max_subgraph_edges_id_list.append(temp_edge)
            # source_name = get_author_name_for_node(node_id=temp_edge[0])
            # target_name = get_author_name_for_node(node_id=temp_edge[1])
            f_subg.write(temp_edge[0] + "," + temp_edge[1] + "\n")
        f_subg.close()
        # print("max_connected_component_edges: ", len(max_connected_component_edges))
        # print("max_connected_component_nodes: ", len(max_connected_component_nodes))
        # pos_largest_comp = gt.sfdp_layout(largest_comp)
        # gt.graph_draw(largest_comp, pos_largest_comp, output="static/graph_drawing/mty_largest_comp_coauthor_visualization.pdf")

        end_time = datetime.now()
        time = (end_time - start_time).seconds
        print("用时:")
        print(time)

# ************************************** END ******************************************* #


def filter_patent_citation():
    with open("apat63_99.txt", "r") as f:
        start_time = datetime.now()
        lines = f.readlines()
        print(len(lines))
        comp_and_communi_list = []
        ff = open("computers_communications.txt", "w")

        ff.write(lines[0].strip() + "\n")
        for line in lines[1:3]:
            line = line.strip()
            raw_line = line
            line = line.split(",")  #
            print(line)
            print(raw_line)
            if line[10] == "2":  # 过滤出Computers & Communications 类别: 2
                print(line)
                comp_and_communi_list.append(line)

            ff.write(raw_line + "\n")

        end_time = datetime.now()
        time = (end_time - start_time).seconds
        print("用时:")
        print(time)


def test_networkx():
    edge_list = [("123", "456", 1), (4, "123", 0.5), (4.08, "123", 0.5), ("data visualization", "456", 1)]
    G = nx.DiGraph()  # 无向图,有向图用DiGraph().
    G.add_weighted_edges_from(edge_list)  # edge_list=[(1, 2, 3), (), ...]
    nx.draw(G, pos=nx.random_layout(G), node_color='b', edge_color='r', with_labels=True, font_size=18, node_size=20)
    plt.show()


# 往Citation_Visualization.db数据node表中添加keywords字段及其值.
def matched_db_for_keywords(file_name):

    f = open(file_name)
    lines = f.readlines()
    f.close()

    dbname = "DB_backup/Citation_Visualization.db"
    db = sqlite3.connect(dbname)
    print("Opened database successfully")
    cursor = db.cursor()

    for line in lines:
        line = line.strip()
        line = line.split("||")
        node_id = line[0].strip()
        node_title = line[1].strip()
        node_keywords = line[2].strip()
        node_doi = line[3].strip()
        node_citation = line[4].strip()
        node_research_points = line[5].strip()
        # print("node_id")
        print(node_id)
        # print("node_research_points")
        # print(node_research_points)
        # 写入条件
        if node_research_points != "":
            keywords = node_research_points
        else:
            if node_keywords != "":
                keywords = node_keywords
            else:  # 没有研究热点+关键词,则用标题替代.
                keywords = node_title
        sql = "update node set keywords=? where id=?"
        cursor.execute(sql, (keywords, node_id))

    db.commit()  # 必须提交事务,否则无法写入表格.
    db.close()


# 找出没有关键词的数据
def find_invalid_data():
    f = open("citation_keywords.txt")
    lines = f.readlines()
    f.close()
    ff = open("no_keywords_citation_keywords.txt", "w")
    for line in lines:
        if "||||||||" in line:
            line = line.strip()
            ff.write(line + "\n")
    ff.close()

# 从作者合作图中获得id对应的节点的所有邻居.
def get_neighbors_from_g(g, node_id, nodes_id_list, edges_list_with_weight, v_doi_list, nodes_name_list, directed=False, interest_subgraph_id_list=None, num_neighbors=5):
    """
    :param node_id: vue传过来的节点id.
    :param directed: 图是否有向
    :param num_neighbors: 取的邻居的最大数量.
    :return: 一个以node_id为中心及其邻居组成的图 graph={'nodes':[{'id': XXX, 'name': xxx, "value": XXX}, ...],
            'links':[{'source': XXX, 'target': XXX, 'value': XXX}, ....]}
    """

    graph = {
        "nodes": [],
        "links": []
    }
    nodes_set = set()
    node_index_for_id = nodes_id_list.index(node_id)  # 获得node_id对应的g中的index
    # print("DOI node_id", node_id)
    # print("DOI node_index_for_id", node_index_for_id)
    if directed:  # 有向
        edge_in = g.get_in_edges(node_index_for_id)  # 获得输入的边
        edge_out = g.get_out_edges(node_index_for_id)  # 获得输出的边
        edge_in_out = list(edge_in) + list(edge_out)
        print(edge_in_out)  # [(), (), ...]
        for i in edge_in_out:  # i = [source  node_id  index]
            index_edge = i[2]
            edge = edges_list_with_weight[index_edge]  # edge=(source, target, value, source_name, target_name)
            # edges_list_for_node_id.append()
            source = edge[0]
            target = edge[1]
            value = edge[2]
            edge = {"source": source, "target": target, "value": value}
            graph["links"].append(edge)
            nodes_set.add(source)
            nodes_set.add(target)
        for node in nodes_set:  # node是数据库中的id
            node_idx = nodes_id_list.index(node)  # node_idx是g中的索引.
            node_doi_value = v_doi_list[node_idx]  # 用节点索引获得对应的DOI值.
            name_ = nodes_name_list[node_idx]
            # name_ = get_author_name_for_node(node_id=node)
            node = {"id": node, "name": name_, "value": node_doi_value}
            graph["nodes"].append(node)
        # print("有向", edge_in, edge_out)
    else:  # 无向图.
        edge_out = g.get_out_edges(node_index_for_id)
        for i in edge_out:  # i = [node_id  target  index]
            index_edge = i[2]
            edge = edges_list_with_weight[index_edge]  # edge=(source, target, value, source_name, target_name)
            # edges_list_for_node_id.append()
            source = edge[0]
            target = edge[1]
            value = edge[2]
            edge = {"source": source, "target": target, "value": value}
            graph["links"].append(edge)
            nodes_set.add(source)
            nodes_set.add(target)
        for node in nodes_set:  # node是数据库中的id
            node_idx = nodes_id_list.index(node)  # node_idx是g中的索引.
            node_doi_value = v_doi_list[node_idx]  # 用节点索引获得对应的DOI值.
            name_ = nodes_name_list[node_idx]
            # name_ = get_author_name_for_node(node_id=node)
            node = {"id": node, "name": name_, "value": node_doi_value}
            graph["nodes"].append(node)
    return graph


def sort_process(name_list, value_list):
    value_array = np.array(value_list)
    result_name_max_min_list = []
    for i in range(len(value_array)):
        max_index = value_array.argmax()
        print(max_index)
        result_name_max_min_list.append(name_list[max_index])
        value_array[max_index] = -1
    # print(result_name_max_min_list)
    return result_name_max_min_list

def get_matched_node_(query_item, node_id_fields_list, fields, each_field, stopWords):
    """
    :param query_item: 一个text类型的属性值,e.g. "data visualization"
    :param node_id_fields_list: [(id, field1_val, field2_val), ...],即对应sqlite中的字段.
    :param fields: 焦点考虑的字段列表:["institutions", "interests"],也就是兴趣属性.
    :param each_field: 当前字段,如"institutions"
    :param stopWords: 通用+自定义的停用词列表,[xx, xx, ..., xx]
    :return: query_item在数据库中匹配上的节点列表.如,[id1, id2, ...]
    """
    lowerCasekeyWord = query_item.lower()  # 输入词,先转换成小写
    result_list = re.split("，|,|&|\t|\s+", lowerCasekeyWord)  # 利用分隔符,转化成列表, result_list = ["data", "visualization"]
    word_set = set([x for x in result_list if x])  # 去掉空字符,取集合
    lowerCasekeyWordList = list(word_set)  # 输入词,["volume", "data", "visualization", "in"]

    # counterLowerCasekeyWord = 0  # 属性值中有效词,即非空,非停用词的个数.
    newLowerCasekeyWordList = []  # 输入属性值的有效词(非空,非停用词)构成的列表.

    for each_one in lowerCasekeyWordList:  # ["volume", "data", "visualization", "in"]
        if each_one != "":
            if each_one not in stopWords:  # 不在停用词表.
                # counterLowerCasekeyWord = counterLowerCasekeyWord + 1  # 统计匹配非停用词的数量.
                newLowerCasekeyWordList.append(each_one)  # 有效词列表:["volume", "data", "visualization"],去掉停用词"in".

    allNodesKeysList = node_id_fields_list  # [("123", "某某机构1"), ("3456", "某某机构2"), ("567", "某某机构3"), ("891", "某某机构4")]  # 整个图的节点id列表. nodesAttrObj={id:{name:[x], field1:[x,...], field2:[x,...]},...}
    matchNodesSet = set()  # 属性值匹配上的节点集.["1223", "4567", "6678"]

    for each_one in allNodesKeysList:  # allNodesKeysList=[("123", "institutions"), ("3456", "institutions")]
        nodeId = each_one[0]  # 节点id.
        field_index = fields.index(each_field) + 1
        attr_val_string = each_one[field_index]  # "aaa;bbb;ccc"
        attr_val_string = attr_val_string.strip()
        attrValList = attr_val_string.split(";")  # 对象中指定属性对应的值构成的数组:attrValList=[x, x, ...]

        for each_word in attrValList:  # attrValList: 被匹配节点对应的属性值列表, e.g., ["science visualization", "graph drawing", "data visualization"]
            newStr = each_word.lower()  # 指定属性的某个取值: "ab, cc fg"

            result_list = re.split("，|,|&|\t|\s+", newStr)  # 利用分隔符,转化成列表.
            word_set = set([x for x in result_list if x])  # 去掉空字符,取集合
            newStrList = list(word_set)  # ["science", "visualization"]
            newnewStrList = []  # 非空,非停用词.
            counterNewStrList = 0

            for each_string in newStrList:  # ["science", "visualization", "the"]
                if each_string != "" and each_string not in stopWords:
                    counterNewStrList = counterNewStrList + 1  # 加1.
                    newnewStrList.append(each_string)  # newnewStrList=["science", "visualization"]

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

                    if fuzz.token_set_ratio(each_valid_word_in_db, each_valid_word_in_attri_val) > 90:  # 模糊匹配
                    # if each_valid_word_in_db == each_valid_word_in_attri_val:  # 原来的模糊匹配改成完全匹配.
                        commonWordSet.add(each_valid_word_in_attri_val)
                        break  # 单词匹配上则跳出大循环,去判断下一个单词.

            matchSize = len(commonWordSet)  # 有效词中,公共词的个数.
            whichOne = len(newLowerCasekeyWordList)  # 以标签上的属性值的有效词的个数为基准.

            if whichOne > 2:  # 不小于3个单词的时候,大于较小者的一半算是匹配上了.
                threshold = whichOne / 2.0  # 需要大于一半.

            else:  # 不大于2个有效词,则需要完全匹配.
                threshold = whichOne  # 2或1

            if matchSize >= threshold:  # 如果匹配上的词的数量不小于最小的字符串的一半,则可以认为两个字符串描述的是一个实体.
                matchNodesSet.add(nodeId)
                break  # 已经确定当前节点是匹配节点,跳出大循环,判断下一个节点.

    return list(matchNodesSet)  # [id1, id2, ...]


def test_fuzzywuzzy():
    # result = fuzz.ratio("data visualization", "data visualizations")
    # print(result)

    string1 = "ffff"
    string2 = "jjjjjing"
    result = fuzz.token_set_ratio(string1, string2)  # 忽略单词的顺序以及重复的单词.
    print(result)

    # query_item = "State Key Lab of CAD&CG, Zhejiang University, Zhejiang, China"
    # lowerCasekeyWord = query_item.lower()  # 先转换成小写
    # result_list = re.split("，|,|&|\t|\s+", lowerCasekeyWord)  # 利用分隔符,转化成列表.
    # print(result_list)


def updated_db():
    db_name = "Citation_Visualization.db"
    dbname = "DB_backup/" + db_name
    db = sqlite3.connect(dbname)
    print("Opened database successfully")
    cursor = db.cursor()
    sql = "select id, keywords from node where keywords like ?"

    condition = "%graph visualization%"
    insert_word = "network visualization"

    cursor.execute(sql, (condition, ))
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果

    need_to_update_id_list = []  # [{"123": "maotingyun;kakakka;ddddd"}, {}, ...]
    for line in data:  # [(id, keywords), ...] 每一个节点
        node_id = line[0]
        node_keywords = line[1]
        keyword_str = line[1]
        # print(line)
        node_keywords = node_keywords.strip()
        node_keywords = node_keywords.split(";")  # ["graph drawing", "graph layout", "graph visualization"]

        num_counter = 0
        for each_word in node_keywords:
            each_word = each_word.strip()
            if each_word.lower() == insert_word:
                num_counter = num_counter + 1
        if num_counter == 0:  # 说明没有指定的词.
            temp_obj = {}
            temp_obj[node_id] = keyword_str
            need_to_update_id_list.append(temp_obj)
    print(need_to_update_id_list)
    for each_obj in need_to_update_id_list:  # [{}, ...]
        node_id = list(each_obj.keys())[0]
        value = each_obj[node_id]
        new_value = value + ";" + insert_word
        # print(new_value)

        sql = "update node set keywords=? where id=?"
        cursor.execute(sql, (new_value, node_id))

    db.commit()  # 必须提交事务,否则无法写入表格.
    db.close()


def extract_max_connected_component_from_Amazon():
    """
    # 对于graph-tool而言, 只需要有边就可以构造出一个图来了,
    # e.g. e=[(), (), ...],从中提取节点个数,构造节点的索引,最后就可以构造出一个图了.

    """

    with open("txt/Amazon0302.txt", "r") as f:
        start_time = datetime.now()
        lines = f.readlines()
        print(len(lines))

        edges_list_with_weight = []
        nodes_set = set()
        for line in lines:
            line = line.strip()
            line = line.split()  # (source, target)
            # print(line)
            # edges_list_without_weight.append((line[0], line[1]))  # 不带权重
            edges_list_with_weight.append(line)  # 带权重.
            nodes_set.add(line[0])
            nodes_set.add(line[1])
        # TODO: # [node_id1, ...] 图中节点的索引就是这个列表的索引,所以可以根据这个列表,获得对应的节点在数据库表中的id,从而获得该节点的属性信息.
        nodes_id_list = list(nodes_set)

        links_list = []
        for edge in edges_list_with_weight:  # [(source, target), ...]
            source = edge[0]
            target = edge[1]
            source_index = nodes_id_list.index(source)
            target_index = nodes_id_list.index(target)
            links_list.append((source_index, target_index))
        # 注意: edges_list_with_weight 与 links_list 是一一对应的.
        g = gt.Graph(directed=True)
        N = len(nodes_set)  # 节点数量
        g.add_vertex(n=N)

        g.add_edge_list(edge_list=links_list)  # 添加边.

        print("原图的节点和边数量: ", N, len(links_list))

        # Draw the largest component
        # TODO: 注意: gt.label_largest_component中directed=True时,如果原图是有向的,directed=None,则会出错,写成directed=False就好了,不能提取出最大的连接子图.

        """
            # 注意:
            #  1. Graph: directed==Ture, 则gt.label_largest_component(g, directed=False)才能正确地抽取.
            #  2. Graph: directed==False, 则gt.label_largest_component(g, directed=False/None)都能正确地抽取.
        """
        print("extracting......")
        largest_comp = gt.GraphView(g, vfilt=gt.label_largest_component(g, directed=False))
        max_subgraph_edges = largest_comp.get_edges()  # # 获得最大子图的边的索引.
        f_subg = open("max_connected_subgraph_Amazon.txt", "w")
        for i in max_subgraph_edges:
            temp_edge_index = i[2]  # 边的索引
            temp_edge = edges_list_with_weight[temp_edge_index]
            f_subg.write(temp_edge[0] + "," + temp_edge[1] + "\n")
        f_subg.close()
        end_time = datetime.now()  # start_time = datetime.now() time = (end_time - start_time).seconds
        time = (end_time - start_time).seconds
        print("用时:")
        print(time)

# ************************************** END ******************************************* #

def using_networkx_extract_max_connected_graph():

    with open("txt/Amazon0302.txt", "r") as f:
        start_time = datetime.now()
        lines = f.readlines()
        print(len(lines))

        edges_list_with_weight = []
        nodes_set = set()
        for line in lines[:20]:
            line = line.strip()
            line = line.split()  # (source, target)
            # print(line)
            # edges_list_without_weight.append((line[0], line[1]))  # 不带权重
            edges_list_with_weight.append(line)  # 带权重.
            nodes_set.add(line[0])
            nodes_set.add(line[1])
        # TODO: # [node_id1, ...] 图中节点的索引就是这个列表的索引,所以可以根据这个列表,获得对应的节点在数据库表中的id,从而获得该节点的属性信息.
        nodes_id_list = list(nodes_set)

        links_list = []
        for edge in edges_list_with_weight:  # [(source, target), ...]
            source = edge[0]
            target = edge[1]
            source_index = nodes_id_list.index(source)
            target_index = nodes_id_list.index(target)
            links_list.append((source_index, target_index))
        # 注意: edges_list_with_weight 与 links_list 是一一对应的.
        g = gt.Graph(directed=True)
        N = len(nodes_set)  # 节点数量
        g.add_vertex(n=N)

        g.add_edge_list(edge_list=links_list)  # 添加边.

        print("原图的节点和边数量: ", N, len(links_list))

        # Draw the largest component
        # TODO: 注意: gt.label_largest_component中directed=True时,如果原图是有向的,directed=None,则会出错,写成directed=False就好了,不能提取出最大的连接子图.

        """
            # 注意:
            #  1. Graph: directed==Ture, 则gt.label_largest_component(g, directed=False)才能正确地抽取.
            #  2. Graph: directed==False, 则gt.label_largest_component(g, directed=False/None)都能正确地抽取.
        """
        print("extracting......")
        largest_comp = gt.GraphView(g, vfilt=gt.label_largest_component(g, directed=False))
        max_subgraph_edges = largest_comp.get_edges()  # # 获得最大子图的边的索引.
        f_subg = open("max_connected_subgraph_Amazon.txt", "w")
        for i in max_subgraph_edges:
            temp_edge_index = i[2]  # 边的索引
            temp_edge = edges_list_with_weight[temp_edge_index]
            f_subg.write(temp_edge[0] + "," + temp_edge[1] + "\n")
        f_subg.close()
        end_time = datetime.now()
        time = (end_time - start_time).seconds
        print("用时:")
        print(time)


# # todo:处理亚马逊元数据.
def processing_amazon_meta_data():
    start_time = datetime.now()
    products_list = []  # [[x, xx, xxx], ...]
    each_product = []
    f_name = "txt/amazon-meta.txt"  # "txt/amaon_cut_test.txt"
    f = open(f_name)
    line = f.readline()
    while line:
        if line == "\n":
            products_list.append(each_product)
            each_product = []
        else:
            each_product.append(line)

        line = f.readline()
    products_list.append(each_product)
    f.close()
    # create node file and edge file
    f_node = open("amazon_co-purchasing_products.txt", "w")
    # f_edge = open("amazon_co-purchasing_connections.txt", "w")
    print("len products_list")
    print(len(products_list))
    for each_one in products_list:  # products_list=[[x, xx, xxx], ...] each_one=[x, xx , xxx]
        if len(each_one) > 3:  # 避免不再生产的产品.
            counter_index = -1
            ASIN = []
            group = []
            node_info = ""
            edge_info = ""
            reviews_n_lines = []  # reviews的索引是reviews_n_lines
            for line in each_one:  # each_one=[x, xx ,xxx]  line="xxx"
                counter_index += 1
                line = line.strip()  # "Id:   2"

                if counter_index == 0:  # Id:
                    temp = line.split(":")  # ["Id", "   2"]
                    num = temp[1].strip()
                    node_info += num + "||"  # "Id;"
                    # print("id")
                    # print(num)

                if counter_index == 1:  # ASIN:
                    temp = line.split(":")  # ["ASIN", "   0738700797"]
                    num = temp[1].strip()
                    ASIN.append(num)
                    # print("ASIN.append(num)")
                    # print(ASIN)
                    node_info += num + "||"  # "Id;ASIN;"

                if counter_index == 2:  # title:
                    temp = line.split("title:")   # ['', ' Candlemas: Feast of Flames']
                    product_title = temp[1].strip()
                    node_info += product_title + "||"  # "Id;ASIN;title;"

                if counter_index == 3:  # group:
                    temp = line.split("group:")  # ['', 'book']
                    product_group = temp[1].strip()
                    group.append(product_group)
                    node_info += product_group + "||"  # "Id;ASIN;title;group;"
                    # print("product_group")
                    # print(group)

                if counter_index == 4:  # salesrank:
                    temp = line.split("salesrank:")  # ['', '9999']
                    product_salesrank = temp[1].strip()
                    node_info += product_salesrank + "||"  # "Id;ASIN;title;group;salesrank;"

                if counter_index == 5:  # similar:
                    temp = line.split("similar:")  # ['', ' 5  0738700827  1567184960  1567182836  0738700525  0738700940']
                    product_similar = temp[1].strip()
                    connected_node_list = product_similar.split()  # ["5", "999", "87", ..., "56"]
                    temp_str = ""
                    if int(connected_node_list[0]) > 0:  # 如果有连接节点.
                        for each_i in connected_node_list[1:]:  # "999"
                            # print("ASIN")
                            # print(ASIN)
                            temp_edge = ASIN[0] + "," + each_i
                            # f_edge.write(temp_edge + "\n")
                            temp_str += each_i + ";"  # 999,87,...,56
                            # ASIN.clear()  # 清空 []
                        ASIN.clear()  # 清空 []
                    else:
                        temp_str += "NULL"
                    temp_str = temp_str.strip(";")
                    node_info += temp_str + "||"

                if counter_index == 6:  # categories:
                    # categories: 1
                    temp = line.split("categories:")  #
                    product_categories = temp[1].strip()  # categories: 1
                    if int(product_categories) > 0:
                        reviews_n_lines.append(6 + int(product_categories) + 1)  # reviews的索引是reviews_n_lines
                    else:  # <=0
                        reviews_n_lines.append(7)  # 否则在下一行.

                    # node_info += product_salesrank + ";"
                if counter_index == 7:
                    if len(reviews_n_lines) > 0:  # 说明已经处理了"categories"
                        if reviews_n_lines[0] == 7:  # 说明没有categories=0
                            reviews_index = reviews_n_lines[0]
                            reviews_line = each_one[reviews_index]
                            temp = reviews_line.split("avg rating:")
                            avg_rating = temp[1].strip()
                            node_info += "NULL" + "||"  # 没有categories,则写入NULL.
                            node_info += avg_rating + "||"

                        else:  # 说明categories > 0
                            reviews_index = reviews_n_lines[0]
                            categories_list = each_one[7:reviews_index]  # [xxx, xxx]
                            categories_set = set()
                            for each_jj in categories_list:
                                if len(group) > 0:
                                    product_g = group[0]
                                    # print("product_g")
                                    # print(product_g)
                                    if product_g.lower() == "book":  # 如果是book.
                                        each_categorie = each_jj
                                        each_categorie_list = each_categorie.split("|")
                                        if len(each_categorie_list) > 2:
                                            if each_categorie_list[2].strip() == 'Subjects[1000]':
                                                temp_list_3 = each_categorie_list[3].split("[")
                                                temp_list_4 = each_categorie_list[4].split("[")

                                                final_str = temp_list_3[0] + ":" + temp_list_4[0]
                                                # print(final_str)
                                                categories_set.add(final_str)

                                    if product_g.lower() == "music":  # 如果是book.
                                        each_categorie = each_jj
                                        each_categorie = each_categorie.strip()
                                        each_categorie_list = each_categorie.split("|")
                                        # print("each_categorie_list")
                                        # print(each_categorie_list)
                                        if each_categorie_list[2].strip() == 'Styles[301668]':
                                            # print("each_categorie_list")
                                            # print(each_categorie_list)
                                            if len(each_categorie_list) > 3:
                                                temp_list_3 = each_categorie_list[3].split("[")
                                                final_str = temp_list_3[0]
                                                categories_set.add(final_str)

                                    if product_g.lower() == "video":  # 如果是book.
                                        each_categorie = each_jj
                                        each_categorie = each_categorie.strip()
                                        each_categorie_list = each_categorie.split("|")
                                        # print("each_categorie_list")
                                        # print(each_categorie_list)
                                        if len(each_categorie_list) > 3:
                                            if each_categorie_list[3].strip() == "Genres[404274]":
                                                temp_list_4 = each_categorie_list[4].split("[")
                                                final_str = temp_list_4[0]
                                                categories_set.add(final_str)

                                    if product_g.lower() == "dvd":  # 如果是book.
                                        each_categorie = each_jj
                                        each_categorie = each_categorie.strip()
                                        each_categorie_list = each_categorie.split("|")
                                        # print("each_categorie_list")
                                        # print(each_categorie_list)
                                        if len(each_categorie_list) > 4:
                                            if each_categorie_list[3].strip() == 'Genres[404276]':
                                                temp_list_4 = each_categorie_list[4].split("[")
                                                final_str = temp_list_4[0]
                                                categories_set.add(final_str)

                            # 提取平均分数.
                            temp_string = ''
                            for i in categories_set:
                                temp_string += i + ";"
                            temp_string = temp_string.strip(";")
                            node_info += temp_string + "||"
                            reviews_index = reviews_n_lines[0]
                            reviews_line = each_one[reviews_index]
                            temp = reviews_line.split("avg rating:")
                            # print("temp")
                            # print(temp)
                            avg_rating = temp[1].strip()
                            node_info += avg_rating + "||"

                if counter_index == 8:
                    break

            node_info = node_info.strip("||")
            f_node.write(node_info + "\n")

    f_node.close()
    # f_edge.close()
    end_time = datetime.now()
    time = (end_time - start_time).seconds
    print("time:")
    print(time)


# TODO: 第一步: 从amazon_co-purchasing_connections_new.txt中提取最大连通子图.
def get_max_connected_subgraph(f_name="amazon_co-purchasing_connections_new.txt"):
    start_time = datetime.now()
    f = open(f_name, "r")
    lines = f.readlines()
    f.close()
    print(len(lines))

    edges_list_with_weight = []
    for line in lines:
        line = line.strip()
        line = line.split(",")  # (source, target)
        edges_list_with_weight.append(line)  # 带权重.
    print("edges_list_with_weight[:10]")
    print(edges_list_with_weight[:10])
    G = nx.Graph()
    # G.add_edges_from([(1, 0), (0, 1), (1, 2), (2, 0), (3, 4), (3, 5), (3, 6), (5, 4), (5, 6)])
    G.add_edges_from(edges_list_with_weight)
    # nx.draw(G,
    #         with_labels=True,  # 这个选项让节点有名称
    #         edge_color='b',  # b stands for blue!
    #         pos=nx.circular_layout(G),  # 这个是选项选择点的排列方式，具体可以用 help(nx.drawing.layout) 查看
    #         # 主要有spring_layout  (default), random_layout, circle_layout, shell_layout
    #         # 这里是环形排布，还有随机排列等其他方式
    #         node_color='r',  # r = red
    #         node_size=1000,  # 节点大小
    #         width=3,  # 边的宽度
    #         )
    # plt.show()
    largest_components = max(nx.connected_components(G), key=len)
    nx.connected_components(G)
    print("节点数量")
    print(len(largest_components))

    f_nodes = open("max_connected_subgraph_Amazon_nodes.txt", "w")
    for each_node in largest_components:
        f_nodes.write(str(each_node) + "\n")
    f_nodes.close()

    max_subgraph = G.subgraph(largest_components)
    print("Obtaining all edges of the max_connected_subgraph")
    max_subgraph_edge_list = list(max_subgraph.edges)  # [(3, 4), (3, 5), (3, 6), (4, 5), (5, 6)]
    print("边数量")
    print(len(max_subgraph_edge_list))

    f_subg = open("max_connected_subgraph_Amazon.txt", "w")
    print("writing all edgrs to the file")
    for each_edge in max_subgraph_edge_list:  # (source, target)
        source_node = each_edge[0]
        target_node = each_edge[1]
        f_subg.write(str(source_node) + "," + str(target_node) + "\n")
    f_subg.close()
    print("end writing")
    end_time = datetime.now()
    time = (end_time - start_time).seconds
    print("time:")
    print(time)


def fiter_amazon_dataset(f_name, max_lines):
    start_time = datetime.now()
    f = open(f_name, "r")
    lines = f.readlines()
    f.close()
    print(len(lines))

    edges_list_with_weight = []
    # print("lines")
    # print(lines[:10])
    sample_lines = random.sample(lines, max_lines)  # 从list中随机获取5个元素,作为一个片断返回
    for line in sample_lines:
        line = line.strip()
        line = line.split(",")  # (source, target)
        edges_list_with_weight.append(line)  # 带权重.
    print("edges_list_with_weight[:10]")
    print(edges_list_with_weight[:10])
    G = nx.Graph()
    G.add_edges_from(edges_list_with_weight)
    largest_components = max(nx.connected_components(G), key=len)
    nx.connected_components(G)
    print("节点数量:")
    print(len(largest_components))

    f_nodes = open("max_connected_subgraph_Amazon_filter_nodes.txt", "w")
    for each_node in largest_components:
        f_nodes.write(str(each_node) + "\n")
    f_nodes.close()

    max_subgraph = G.subgraph(largest_components)
    print("Obtaining all edges of the max_connected_subgraph")
    max_subgraph_edge_list = list(max_subgraph.edges)  # [(3, 4), (3, 5), (3, 6), (4, 5), (5, 6)]
    print("边数量")
    print(len(max_subgraph_edge_list))

    f_subg = open("max_connected_subgraph_Amazon_filter.txt", "w")
    print("writing all edgrs to the file")
    for each_edge in max_subgraph_edge_list:  # (source, target)
        source_node = each_edge[0]
        target_node = each_edge[1]
        f_subg.write(str(source_node) + "," + str(target_node) + "\n")
    f_subg.close()
    print("end writing")
    end_time = datetime.now()
    time = (end_time - start_time).seconds
    print("time:")
    print(time)


# TODO: 过滤掉没有信息的节点构成的边.
def filter_edges_without_info(all_nodes_info_file, all_edges_file):
    f = open(all_nodes_info_file)  # 可视化领域的作者合作网络.
    all_nodes_info_lines = f.readlines()  # all_nodes_info_lines=["line0\n", "line1\n",...]
    f.close()

    ff = open(all_edges_file)  # 可视化领域的作者合作网络.
    # max_connected_subg_nodes_info_lines = ff.readlines()  # ["B0001FVDWS\n", ...]
    # ff.close()

    fff = open(all_edges_file.split(".")[0] + "_new.txt", "w")

    all_nodes_list = []
    for line in all_nodes_info_lines:
        line = line.strip()
        line = line.split(";")
        node = line[1]
        all_nodes_list.append(node)

    line = ff.readline()
    while line:
        temp_line = line.strip()  # B000001F3P,B000001EEN
        temp_line = temp_line.split(",")  # [source, target]
        source = temp_line[0]
        target = temp_line[1]
        if source in all_nodes_list and target in all_nodes_list:
            fff.write(line)
        line = ff.readline()

    ff.close()
    fff.close()


# TODO: 第二步: 从amazon共同购买网络中采样子图.如果想要合适规模的网络数据,则使用该网路进行采样.
def sample_co_purchasing_network(num_sample_edges):
    f_name = "max_connected_subgraph_Amazon.txt"  # 从最大子图中进行采样.
    max_lines = num_sample_edges
    fiter_amazon_dataset(f_name, max_lines)


# TODO: 第三步: 获得采样子图后,找出其节点对应的信息,便于后续存放数据库.
def find_nodes_info_from_max_connected_subgraph(all_nodes_info_file, max_connected_subg_nodes_file):
    f = open(all_nodes_info_file)  # 可视化领域的作者合作网络.
    all_nodes_info_lines = f.readlines()  # all_nodes_info_lines=["line0\n", "line1\n",...]
    f.close()

    ff = open(max_connected_subg_nodes_file)  # 可视化领域的作者合作网络.
    max_connected_subg_nodes_info_lines = ff.readlines()  # ["B0001FVDWS\n", ...]
    ff.close()

    fff = open(max_connected_subg_nodes_file.split(".")[0] + "_info.txt", "w")
    """
    1;0827229534;Patterns of Preaching: A Sermon Sampler;Book;396585;0804215715,156101074X,0687023955,0687074231,082721619X;Religion & Spirituality:Christianity;5

    """
    all_nodes_list = []
    for line in all_nodes_info_lines:
        line = line.strip()
        line = line.split("||")
        node = line[1]
        all_nodes_list.append(node)
    # print(all_nodes_list)
    print("开始匹配节点数据")
    for line in max_connected_subg_nodes_info_lines:
        node = line.strip()
        # print(node)
        node_index = all_nodes_list.index(node)
        node_line = all_nodes_info_lines[node_index]
        fff.write(node_line)

    fff.close()
    print("匹配结束")
    # print(all_nodes_list)


# TODO: 第四步: 完善边的信息. source target weight source_name target_name
def edges_info(max_connected_subg_edges_file=None, max_connected_subg_nodes_file="max_connected_subgraph_Amazon_filter_nodes_23650.txt"):
    f = open(max_connected_subg_nodes_file.split(".")[0] + "_info.txt")
    node_info_lines = f.readlines()
    f.close()
    ff = open(max_connected_subg_edges_file)
    edge_lines = ff.readlines()
    ff.close()

    fff = open(max_connected_subg_edges_file.split(".")[0] + "_info.txt", "w")
    node_info_lines_id_list = []
    node_info_lines_name_list = []

    for each_one in node_info_lines:
        temp_node = each_one.strip()
        temp_node = temp_node.split("||")
        node_id = temp_node[0]
        node_name = temp_node[1]
        node_info_lines_id_list.append(node_id)  # [id0, id1, id2, ...]
        node_info_lines_name_list.append(node_name)  # [name0, name1, name2, ...]
    counter = 0
    for each_edge in edge_lines:
        counter += 1
        temp_edge = each_edge.strip()
        temp_edge = temp_edge.split(",")
        source = temp_edge[0]
        target = temp_edge[1]
        source_index = node_info_lines_id_list.index(source)
        target_index = node_info_lines_id_list.index(target)
        source_name = node_info_lines_name_list[source_index]
        target_name = node_info_lines_name_list[target_index]
        # print(source + ";" + target + ";" + "1" + ";" + source_name + ";" + target_name)
        fff.write(source + "||" + target + "||" + "1" + "||" + source_name + "||" + target_name + "\n")
    print("counter=")
    print(counter)
    fff.close()

############################################################################################


def create_table_edge(db_name):
    # # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/" + db_name
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()

    # 写sql语言,执行,创建作者表格. 注意:表格的字段不能命名为index,命名为id就可以了.
    edge = '''create table edge (    
                   source         text,
                   target         text,
                   weight         int,
                   source_name    text,
                   target_name    text                    
                )'''
    cursor.execute(edge)
    print("edge created successfully")
    cursor.close()

    db.close()  # 关闭数据库


def write_table_edge(db_name, file_name):
    f = open(file_name)  # 可视化领域的作者合作网络.
    lines = f.readlines()
    f.close()
    edges_list = []
    for line in lines:
        line = line.strip()
        line = line.split("||")  # (source, target)
        edges_list.append(line)  # fixme: 带权重. edges_list_with_weight=[(source, target, value, source_name, target_name), ...]

    dbname = "DB/" + db_name
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("................writing................")
    # 创建数据库中的游标对象
    cursor = db.cursor()

    for each_one in edges_list:  # (source, target, weight, source_name, target_name)
        cursor.execute('''insert into edge (source, target, weight, source_name, target_name) VALUES (?,?,?,?,?)''', (each_one[0], each_one[1], int(each_one[2]), each_one[3], each_one[4]))
    db.commit()  # 必须提交事务，否则无法写入表格
    db.close()


def create_table_node(db_name):
    # # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/" + db_name
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()

    # 写sql语言,执行,创建作者表格. 注意:表格的字段不能命名为index,命名为id就可以了.
    node = '''create table node (    
                   id                   text,
                   name                 text,
                   group_product        text,
                   categories_product   text,
                   avg_rating           real
                )'''
    cursor.execute(node)
    print("node created successfully")
    cursor.close()

    db.close()  # 关闭数据库


def write_table_node(db_name, file_name):
    f = open(file_name)  # 可视化领域的作者合作网络.
    lines = f.readlines()
    f.close()
    nodes_list = []
    for line in lines:
        line = line.strip()
        line = line.split("||")  # (source, target)
        caltegory = line[6]  # x,x,xx"
        caltegory_list = caltegory.split(";")
        temp_str = ""
        # if len(caltegory_list) > 0:
        for each_one in caltegory_list:
            each_one = each_one.strip()
            # if each_one != "A-Z":
            temp_str += each_one + ";"
        temp_str = temp_str.strip(";")
        if temp_str == "NULL" or temp_str == "":
            temp_str = "null"
        new_line = (line[1], line[2], line[3], temp_str, line[7])
        nodes_list.append(new_line)  # fixme: 带权重. edges_list_with_weight=[(source, target, value, source_name, target_name), ...]

    dbname = "DB/" + db_name
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("................writing................")
    # 创建数据库中的游标对象
    cursor = db.cursor()

    for each_one in nodes_list:  # (source, target, weight, source_name, target_name)
        cursor.execute('''insert into node (id, name, group_product, categories_product, avg_rating) VALUES (?,?,?,?,?)''', (each_one[0], each_one[1], each_one[2], each_one[3], each_one[4]))
    db.commit()  # 必须提交事务，否则无法写入表格
    db.close()

# TODO:创建数据库.
def add_node_edge_table():
    # #todo: 创建edge表,写入数据.
    db_name = "Co-purchasing_Network.db"
    create_table_edge(db_name)  # 先创建edge表
    file_name = "max_connected_subgraph_Amazon_filter_25105_info.txt"
    write_table_edge(db_name, file_name)  # 将数据写入edge表

    # #todo: 创建node表,写入数据.
    db_name = "Co-purchasing_Network.db"
    file_name = "max_connected_subgraph_Amazon_filter_nodes_25105_info.txt"
    create_table_node(db_name)
    write_table_node(db_name, file_name)


def processing_amazon_data_steps():
    edge_num = 48908
    node_num = 45176
    # # todo:第三步: 匹配节点对应的信息,便于后续存放数据库.(如果要添加数据规模,直接从这一步开始.)
    all_nodes_info_file = "amazon_co-purchasing_products.txt"
    max_connected_subg_nodes_file = "max_connected_subgraph_Amazon_filter_nodes_" + str(node_num) + ".txt"
    find_nodes_info_from_max_connected_subgraph(all_nodes_info_file, max_connected_subg_nodes_file)

    # # todo: 第四步:完善边的信息. source target weight source_name target_name
    max_connected_subg_edges_file = "max_connected_subgraph_Amazon_filter_" + str(edge_num) + ".txt"
    max_connected_subg_nodes_file = "max_connected_subgraph_Amazon_filter_nodes_" + str(node_num) + ".txt"
    edges_info(max_connected_subg_edges_file=max_connected_subg_edges_file,
               max_connected_subg_nodes_file=max_connected_subg_nodes_file)

    # # todo: 第五步: 将数据写入数据库
    # add_node_edge_table()
    # #todo: 创建edge表,写入数据.
    db_name = "Co-purchasing_Network.db"
    create_table_edge(db_name)  # 先创建edge表
    file_name = "max_connected_subgraph_Amazon_filter_" + str(edge_num) + "_info.txt"
    write_table_edge(db_name, file_name)  # 将数据写入edge表

    # #todo: 创建node表,写入数据.
    db_name = "Co-purchasing_Network.db"
    file_name = "max_connected_subgraph_Amazon_filter_nodes_" + str(node_num) + "_info.txt"
    create_table_node(db_name)
    write_table_node(db_name, file_name)


# todo:更新co-author数据库
def insert_publications():
    start_time = datetime.now()
    ff = open("txt/jingjing.txt")
    lines = ff.readlines()
    ff.close()
    node_list = []
    publications_list = []
    papers_set = set()
    for each_one in lines:
        each_one = each_one.strip()
        each_one = each_one.split("||")
        node_id = each_one[0]
        papers = each_one[1]
        node_list.append(node_id)
        publications_list.append(papers)
        for ii in papers.split(";"):
            ii = ii.strip()
            papers_set.add(ii)

    jj_f = open("max_connected_subgraph_Academy_publications.txt", "w")
    for jj in papers_set:
        jj_f.write(jj + "\n")

    dbname = "DB/new_coauthor_db/co-authorship.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("Opened database successfully")
    # 创建数据库中的游标对象
    cursor = db.cursor()
    sql = "update node set publications=? where id=?"

    counter = -1
    for author_id in node_list:
        counter += 1
        publications = publications_list[counter]
        cursor.execute(sql, (publications, author_id))

    db.commit()  # 必须提交事务,否则无法写入表格.
    db.close()

    # abstract_visualization_papers(papers_set_for_all_authors)
    end_time = datetime.now()
    time = (end_time - start_time).seconds
    print("time")
    print(time)


def updated_table(old_db_name, new_db_name):
    dbname = old_db_name
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("Opened database successfully")
    # 创建数据库中的游标对象
    cursor = db.cursor()

    # sql = "update node set publications=? where id=?"
    sql = "select * from node"
    cursor.execute(sql)
    data = cursor.fetchall()

    for each_one in data:  # [(id, name, ...), ...]
        print(each_one)
        node_id = each_one[0]  # [(id, name, ...), ...]


def test_maotingyun():
    g = gt.Graph(directed=False)  # 无向.

    def test(g, directed=None, links_list=None):
        g.set_directed(is_directed=directed)  # 设置方向性.
        g.clear()
        g.reindex_edges()
        N = 4
        g.add_vertex(n=N)
        # links_list = [(0, 1), (0, 2), (1, 2), (0, 3)]
        g.add_edge_list(edge_list=links_list)  # 添加边.

    links_list = [(0, 1), (0, 3), (0, 4), (2, 3), (2, 1), (2, 4), (0, 5), (0, 6), (6, 7), (0, 8)]
    test(g=g, directed=False, links_list=links_list)
    node_index_list = range(4)
    r_out = g.get_out_degrees(node_index_list)
    r_in = g.get_in_degrees(node_index_list)
    print("r_out")
    print(r_out)
    print("r_in")
    print(r_in)
    cc = gt.closeness(g=g)
    print(cc)
    for ii in cc:
        print(ii)


def get_layout_graph(file_name=None):  # txt/soc-Epinions1.txt
    with open(file_name, "r") as ff:
        lines = ff.readlines()
        print(len(lines))

        edges_list_with_weight = []
        nodes_set = set()
        for line in lines:
            line = line.strip()
            line = line.split()  # (source, target)
            # print(line)
            # edges_list_without_weight.append((line[0], line[1]))  # 不带权重
            edges_list_with_weight.append(line)  # 带权重.
            nodes_set.add(line[0])
            nodes_set.add(line[1])
        nodes_id_list = list(nodes_set)
        # print("edges_list_with_weight")
        # print(edges_list_with_weight)
        # print("nodes_id_list")
        # print(nodes_id_list)

        links_list = []
        for edge in edges_list_with_weight:  # [(source, target), ...]
            source = edge[0]
            target = edge[1]
            source_index = nodes_id_list.index(source)
            target_index = nodes_id_list.index(target)
            links_list.append((source_index, target_index))

        g = gt.Graph(directed=False)
        N = len(nodes_set)  # 节点数量
        g.add_vertex(n=N)

        g.add_edge_list(edge_list=links_list)  # 添加边.

        print("原图的节点和边数量: ", N, len(links_list))
        pos = gt.sfdp_layout(g)  # 使用胡一凡的sfdp_layout算法,获得节点的坐标.
        gt.graph_draw(g, pos, vertex_text=None, vertex_font_size=18, vertex_size=8, edge_pen_width=1.2,
                      output_size=(1000, 1000), output="static/graph_drawing/jingjing_test_graph1.pdf")




    # directed = False
    # G = gt.Graph(directed=directed)  # 创建图实例.
    # node_list = []
    # N = len(node_list)
    # G.add_vertex(n=N)  # 节点数量.
    # G.add_edge_list(edge_list_with_index)  # 添加边.
    #
    # pos = gt.sfdp_layout(G)  # 使用胡一凡的sfdp_layout算法,获得节点的坐标.
    # # gt.graph_draw(G, pos, vertex_text=G.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
    # #               output_size=(800, 800), output=None)


def get_db_table_fields(dbname="DB/Co-purchasing_Network.db", table_name="node"):

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

# todo: 原来的获取种子等的函数,如果出错则拷贝此函数替代修改过的.
def get_seed_field_value_from_set_interests(set_interests=None, discard_fields_list=None):
    """
    :param set_interests:前端请求发送的参数set_interests={"setNodes": [{}, {},...], "setKeyword":{field1:xxx, ...}}
    备注: 我们考虑的节点属性是text类型的属性,它们的值接下来要被节点化,并与节点的id一起作为种子,用随机游走来计算整个图中的节点分数.
    我们暂时将这些属性称为"被节点化属性",其值称为"被节点化属性值".
    :return: focus_id_list, seed_list, field_attri_values,分别是焦点的id集, 新图的种子集, 字段及其值组成的集.
    focus_id_list里面存放焦点的id, seed_list里面的内容包括: 节点id + 节点的text属性值(除去name等在数据库配置文件中指明的属性) + 关键词集中的关键词 + field属于被考虑字段对应的值(比如,field: institution,keyword:xxx的值xxx将被节点化,同时作为种子.),
    field_attri_values: 一个对象,e.g.{字段1: [所选焦点字段对应的值 + 属于该字段的关键词], 字段2: [], ...}
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
            node_fields_list.add(each_key)
    node_fields_list = list(node_fields_list)  # fixme: e.g.['institutions', 'interests'],所有焦点在前端选择的属性的集合(有的选择interests, 有的没有选择属性,有的选择了"institutions"+"interests",将这些做成一个集合["institutions","interests"])
    text_search_field_set = set()  # 前端搜索视图关键词对应字段的集合.
    # 初始化field_attri_values.
    if len(node_fields_list) > 0:  # fixme: 如果焦点考虑了兴趣属性.
        for each_one in node_fields_list:  # [field1, field2, ...]
            field_attri_values[each_one] = set()  # 初始化成字段-字段值集合对:{institutions: set(), interests: set(), ...}

    # ********** 保证焦点不考虑任何属性时,而关键词对应的字段属于被考虑范围 ****************#
    else:  # fixme: 如果焦点没有考虑任何属性.
        for each_node in nodes_set:
            # 现在满足多条件搜索.
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
                    if each_field not in discard_fields_list:  # fixme:如果field不在被丢弃的字段列表中.
                        if each_field.lower() != "null" and each_field.lower() != "all":  # fixme: 同时不是NULL + All
                            text_search_field_set.add(each_field)  # todo: 保存each_field.

    text_search_field_list = list(text_search_field_set)
    print("text_search_field_list")
    print(text_search_field_list)
    if len(text_search_field_list) > 0:
        for each_one in text_search_field_list:  # [field1, field2, ...]
            field_attri_values[each_one] = set()  # 初始化成字段-字段值集合对:{field1: set(), field2: set(), ...}
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
        # 现在满足多条件搜索.
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
                if len(node_fields_list) > 0:  # fixme:如果焦点考虑了属性
                    if each_field in node_fields_list:  # fixme:判断搜索条件中,选择的字段(属性)是否为在考虑的范围之内.
                        node_keyword = keyword_val_list[counter]  # 取出对应的关键词,text类型.
                        node_keyword = node_keyword.strip()  # 去掉前后的空格.
                        node_keyword = node_keyword.lower()  # fixme: 字符串小写化,避免重复,如这种情况: "Graph Drawing","graph drawing"
                        if node_keyword != "null" and node_keyword != "":
                            seed_set.add(node_keyword)  # 丢到种子列表里面. 同时也要被放在节点化属性中.
                            field_attri_values[each_field].add(node_keyword)
                else:  # fixme:如果焦点没有考虑属性
                    if each_field not in discard_fields_list:  # fixme:如果field不在被丢弃的字段列表中.
                        if each_field.lower() != "null" and each_field.lower() != "all":  # fixme: 同时不是NULL + All
                            node_keyword = keyword_val_list[counter]  # 取出对应的关键词,text类型.
                            node_keyword = node_keyword.strip()  # 去掉前后的空格.
                            node_keyword = node_keyword.lower()  # fixme: 字符串小写化
                            if node_keyword != "null" and node_keyword != "":
                                seed_set.add(node_keyword)  # 丢到种子列表里面. 同时也要被放在节点化属性中.
                                field_attri_values[each_field].add(node_keyword)


        else:
            print("Conditions do not meet the requirement")

        # fixme:针对焦点需要考虑的属性,例如'institutions' + 'interests'
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
    # print("focus_id_list")
    # print(focus_id_list)
    # print("seed_list")
    # print(seed_list)
    # print("field_attri_values")
    # print(field_attri_values)
    # FIXME: seed_list = focus_id_list + field_attri_values中属性值列表
    return focus_id_list, seed_list, field_attri_values



if __name__ == "__main__":
    """
    amazon_co-purchasing_connections.txt: 1788725条边(百万)
    amazon_co-purchasing_products.txt: (十万)
    
    max_connected_subgraph_Amazon_nodes.txt 节点: 524366个(十万)
    max_connected_subgraph_Amazon.txt 边数量: 1491774 (百万)
    
    """
    """
        amazon_co-purchasing_connections_new.txt: 1231400条边(百万)
        amazon_co-purchasing_products.txt: (十万)

        max_connected_subgraph_Amazon_nodes.txt 节点: 334852 个(十万)
        max_connected_subgraph_Amazon.txt 边数量: 925823 (百万)

        """
    # all_nodes_info_file = "amazon_co-purchasing_products.txt"
    # max_connected_subg_nodes_file = "max_connected_subgraph_Amazon_filter_nodes_17651.txt"
    # find_nodes_info_from_max_connected_subgraph(all_nodes_info_file, max_connected_subg_nodes_file)

    # all_nodes_info_file = "amazon_co-purchasing_products.txt"
    # all_edges_file = "amazon_co-purchasing_connections.txt"
    # filter_edges_without_info(all_nodes_info_file, all_edges_file)

    # # todo: 第二步: 从amazon共同购买网络中采样子图.如果想要合适规模的网络数据,则使用该网路进行采样.
    # get_max_connected_subgraph(f_name="amazon_co-purchasing_connections_new.txt")
    # num_sample_edges = 184852
    # sample_co_purchasing_network(num_sample_edges)
    ##################################################################################

    # # # todo:第三步: 匹配节点对应的信息,便于后续存放数据库.(如果要添加数据规模,直接从这一步开始.)
    # all_nodes_info_file = "amazon_co-purchasing_products.txt"
    # max_connected_subg_nodes_file = "max_connected_subgraph_Amazon_filter_nodes_31271.txt"
    # find_nodes_info_from_max_connected_subgraph(all_nodes_info_file, max_connected_subg_nodes_file)
    #
    # # # todo: 第四步:完善边的信息. source target weight source_name target_name
    # max_connected_subg_edges_file = "max_connected_subgraph_Amazon_filter_33435.txt"
    # max_connected_subg_nodes_file = "max_connected_subgraph_Amazon_filter_nodes_31271.txt"
    # edges_info(max_connected_subg_edges_file=max_connected_subg_edges_file,
    #            max_connected_subg_nodes_file=max_connected_subg_nodes_file)
    #
    # # # todo: 第五步: 将数据写入数据库
    # # add_node_edge_table()
    # # #todo: 创建edge表,写入数据.
    # db_name = "Co-purchasing_Network.db"
    # create_table_edge(db_name)  # 先创建edge表
    # file_name = "max_connected_subgraph_Amazon_filter_33435_info.txt"
    # write_table_edge(db_name, file_name)  # 将数据写入edge表
    #
    # # #todo: 创建node表,写入数据.
    # db_name = "Co-purchasing_Network.db"
    # file_name = "max_connected_subgraph_Amazon_filter_nodes_31271_info.txt"
    # create_table_node(db_name)
    # write_table_node(db_name, file_name)
    # processing_amazon_data_steps()

    # insert_publications()
    # 338595 | | Measuring
    # lift
    # quality in database
    # marketing | | Gregory
    # Piatetsky - Shapiro;
    # Sam
    # Steingold | | Xchange
    # Inc., One
    # Lincoln
    # Plaza, 89
    # South
    # Street, Boston, MA;
    # Xchange
    # Inc., One
    # Lincoln
    # Plaza, 89
    # South
    # Street, Boston, MA | | 2000 | | ACM
    # SIGKDD
    # Explorations
    # Newsletter - Special
    # issue
    # on “Scalable
    # data
    # mining
    # algorithms” | | 280442
    # test_maotingyun()
    # get_layout_graph(file_name="txt/soc-Epinions1.txt")  # txt/soc-Epinions1.txt
    # from scipy._lib.decorator import decorator
    # print("maotingyunlvjingjing")

    # col_name_list, col_name_type_list, db_tables_list = get_db_table_fields(dbname="DB/Co-purchasing_Network.db", table_name="node")
    # print(col_name_list)
    # print(col_name_type_list)
    # print(db_tables_list)

    # g = gt.Graph(directed=False)
    # N = 11  # 节点数量
    # g.add_vertex(n=N)
    # data_type = "fake"
    # edges_list = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 7), (0, 8), (7, 8), (7, 9), (7, 10), (4, 5), (5, 6), (1, 2),
    #               (1, 4)]
    # g.add_edge_list(edge_list=edges_list)
    # r = gt.pagerank(g)
    # pos = gt.sfdp_layout(g)  # 使用胡一凡的sfdp_layout算法,获得节点的坐标.
    # gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
    #               output_size=(800, 800), output=None)

    # def test_get_subgraph_with_greedy_algorithm():
    #     """
    #         第一步: 创建图,准备图数据.
    #     """
    #     g = gt.Graph(directed=False)
    #     N = 11  # 节点数量
    #     g.add_vertex(n=N)
    #     data_type = "fake"
    #     edges_list = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 7), (0, 8), (7, 8), (7, 9), (7, 10), (4, 5), (5, 6), (1, 2),
    #                   (1, 4)]
    #     g.add_edge_list(edge_list=edges_list)
    #     r = gt.pagerank(g)
    #     print(r)
    #     v_doi_list = []
    #     for i in r:
    #         # print(i)
    #         v_doi_list.append(i)
    #     print(v_doi_list)
    #
    #     v_prop_DOI = g.new_vertex_property("double")  # 给节点添加 doi 属性
    #     for v in g.vertices():
    #         v_prop_DOI[v] = v_doi_list[int(v)]
    #     g.vertex_properties["doi"] = v_prop_DOI  # 将pr值作为每个节点的pagerank属性值, 映射: v-->{"doi": 0.04633}
    #     # for i in g.vertex_properties["doi"]:
    #     #     print(i)
    #
    #     if data_type == "fake":
    #         fake_value = [0.5, 0.3, 0.4, 0.5, 0.1, 0.9, 0.8, 0.2, 0.22, 0.15, 0.17]
    #         counter = -1
    #         for i in fake_value:
    #             counter = counter + 1
    #             g.vertex_properties["doi"][counter] = i  # 这种写法,必须在g.vertex_properties["doi"] = v_prop_DOI之后.
    #
    #     """
    #         第二步: 使用贪心算法,抽取DOI子图节点.
    #     """
    #     focus = 0
    #     total_num_doi_subgraph = 7
    #     F = get_subgraph_with_greedy_algorithm(g=g, focus=focus, total_num_doi_subgraph=total_num_doi_subgraph)
    #     print("F")
    #     print(F)
    #     # pos = gt.sfdp_layout(g)
    #     # gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2, output_size=(200, 200), output=None)
    #     """
    #         第三步: 抽取DOI子图.
    #     """
    #     # TODO: 下一步抽取DOI子图
    #     extract_doi_subgraph(g, edges_list_g=edges_list, subgraph_nodes_list=F)
    #
    #
    # test_get_subgraph_with_greedy_algorithm()

    # neighbors_attr_val_matched_nodes_obj = {}
    # def test_just(neighbors_attr_val_matched_nodes_obj):
    #     query_item = ["A", "B", "C"]
    #     node_id = ["100", "101", "102", "102", "103", "104", "105"]
    #     for each_node in node_id:
    #         if each_node in neighbors_attr_val_matched_nodes_obj.keys():
    #             neighbors_attr_val_matched_nodes_obj[each_node].add("f")
    #         else:
    #             neighbors_attr_val_matched_nodes_obj[each_node] = set()
    #             neighbors_attr_val_matched_nodes_obj[each_node].add("A")
    #
    #
    # test_just(neighbors_attr_val_matched_nodes_obj)
    # print("matched_node_interest_attr_values_obj")
    # print(neighbors_attr_val_matched_nodes_obj)
    # G = nx.DiGraph()  # 无向图,有向图用DiGraph().
    # edge_list = [("A", "B", 5), ("A", "C", 1)]
    # G.add_weighted_edges_from(edge_list)
    # R = nx.to_numpy_matrix(G)
    # print(R)

    # l = [0.009, 0.9, 0.7, 0.05]
    # print(l)
    # print(max(l))
    # obj = {"mao": 90, "jingjing": 100}
    # print(obj.keys())
    # for each_key in obj.keys():
    #     print(each_key)
    #
    # nodes_max_min = [0, 3, "ML", 1, "Vis"]
    # probs_max_min = [0.8, 0.6, 0.4, 0.33, 0.2]
    # neighbors_attr_val_matched_nodes_obj = {0: set()}

    """
    nodes_max_min = [0, 'Vis', 'ML', 2, 3, 4, 1]
    probs_max_min = [0.20576030746959784, 0.17215277191689077, 0.17184700245421164, 0.16841055969571259, 0.14081529037491164, 0.09300337555761463, 0.04801069253106056]
    # [0.20576030746959784, 0.17215277191689077, 0.17184700245421164, 0.17215277191689077, 0.17215277191689077, 0.17184700245421164, 0.04801069253106056]
    print("probs_max_min1")
    print(probs_max_min)
    neighbors_attr_val_matched_nodes_obj = {2: ["ML", "Vis"], 3: ["Vis"], 4: ["ML"]}

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
        # update the corresponding value, i.e., diffuse the probs.
        probs_max_min[key_index] = max_val

    print("probs_max_min")
    print(probs_max_min)
    """
    # [0.20576030746959784, 0.17215277191689077, 0.17184700245421164, 0.17215277191689077, 0.17215277191689077, 0.17184700245421164, 0.04801069253106056]
    # a = zip(np.array([1, 2, 3, 4]), np.array([4, 5, 6, 8]))
    # print(a)
    # for i in a:
    #     print(i)
    # diffusion_result_list = []
    # a = max(diffusion_result_list)
    # print(a)
    # print(len(diffusion_result_list))

    # edge_list = [("ML", "Vis", 1), ("ml", "vis", 1), ("ML", "vis", 1)]
    # G = nx.Graph()  # 无向图,有向图用DiGraph().
    # # idx = list(G.nodes()).index("ml")
    # G.add_weighted_edges_from(edge_list)  # edge_list=[(1, 2, 3), (), ...]
    # G_node_list = list(G.nodes())
    # idx = G_node_list.index("ml")
    # print("G_node_list")
    # print(G_node_list)
    # print("idx")
    # print(idx)
    #
    # pos = nx.spring_layout(G)
    # nx.draw(G, pos, with_labels=True, font_weight='bold')
    # plt.show()
    # a = {'setNodes': [{'attributesValue': {'interests': 'Info map;visualizing information flow;Eigenfactor project;Eigenfactor score;scientific citation network;Moritz Stefaner;different aspect;hierarchical clustering;individual journal;interactive visualization'}, 'attriselect': ['interests'], 'keyword': 'University of Washington', 'id': '946942', 'tag': 'Martin Rosvall', 'dbname': 'co-authorship.db', 'field': 'institution'}], 'setKeyword': {}}
    # nodes_max_min = ["123", "889"]
    # probs_max_min = [1.32, 9.654]
    # print(nodes_max_min, probs_max_min)
    # a = ['4', '0', 'football', 'doctor', '8', '5', '12', '1', '2', '3', '7', '11', '9', '6', '10']
    # b = ['4', '0', 'bj', '11', '5', '1', '2', '3', '8', '9', '10', '7', '6', '12']
    # edges_list = [(0, 1, 1), (0, 2, 1), (1, 2, 1)]
    # g = gt.Graph(directed=False)
    # node_set = set()
    # for each_one in edges_list:
    #     node_set.add(each_one[0])
    #     node_set.add(each_one[1])
    # g.add_vertex(n=len(node_set))
    #
    # g.add_edge_list(edge_list=edges_list)
    #
    # for v in g.vertices():
    #     print(v)
    nodes_max_min = ['10', '1', '6', '4', '2', '3', '11', '14', '13', '8', '7', '9', '12', '5']
    probs_max_min = [0.365, 0.362, 0.0654, 0.045, 0.043, 0.035, 0.0286, 0.0281, 0.0076, 0.0053, 0.0044, 0.0044, 0.0036, 0.0034]
    UI_obj = {}
    counter = -1
    for each_one in nodes_max_min:
        counter += 1
        UI_obj[each_one] = probs_max_min[counter]
    print("UI_obj")
    print(UI_obj)

    node_list = ['10', '1', '6', '4', '2', '3', '11', '14', '13', '8', '7', '9', '12', '5']
    node_index = [7, 2, 0, 3, 4, 10, 13, 5, 8, 6, 1, 11, 9, 12]
    final_DOI = [0.0705, 0.0599, 0.333, 0.0504, 0.046, 0.0306, 0.0599, 0.338, 0.0284, 0.0284, 0.0429, 0.0599, 0.0429, 0.0334]
    id_DOI = {}
    counter = -1
    for each_node in node_list:
        counter += 1
        corr_DOI_index = node_index[counter]
        id_DOI[each_node] = final_DOI[corr_DOI_index]  # {"10": 0.177, "1":0.1722}
    print("id_DOI")
    print(id_DOI)














































