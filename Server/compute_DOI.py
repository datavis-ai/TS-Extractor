# coding: utf-8
import json
# import networkx as nx
# import graph_tool as gt
from pylab import *  # for plotting
import numpy as np
# We need to import the graph_tool module itself
# from graph_tool.all import *
import graph_tool.all as gt
import scipy.stats
import networkx as nx
import sqlite3


def test():
    g = gt.Graph(directed=False)
    N = 5  # 节点数量
    g.add_vertex(n=N)

    edges_list = [(0, 2), (1, 3), (3, 4)]
    g.add_edge_list(edge_list=edges_list)
    print(g.get_vertices())
    # pos_g = gt.sfdp_layout(g)
    # gt.graph_draw(g, pos_g, vertex_text=g.vertex_index, output=None)

    largest_comp = gt.GraphView(g, vfilt=gt.label_largest_component(g, directed=False))
    for i in largest_comp.get_edges():
        print(i)
    # sub_g = gt.Graph(largest_comp, directed=False, prune=True)
    # pos_g = gt.sfdp_layout(sub_g)
    # gt.graph_draw(sub_g, pos_g, vertex_text=sub_g.vertex_index, output=None)

# KL散度 + JS散度计算实例
def KL_JS_test():
    p = np.asarray([0.65, 0.25, 0.07, 0.03])
    q = np.array([0.6, 0.25, 0.1, 0.05])

    M = (p + q) / 2
    print(M)

    # 方法一：根据公式求解
    js1 = 0.5 * np.sum(p * np.log(p / M)) + 0.5 * np.sum(q * np.log(q / M))
    print(js1)

    # 方法二：调用scipy包求解
    js2 = 0.5 * scipy.stats.entropy(p, M) + 0.5 * scipy.stats.entropy(q, M)
    print(js2)


def test_networkx():
    # g = nx.Graph()
    # edges = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 7), (0, 8), (7, 8), (7, 9), (7, 10), (4, 5), (5, 6), (1, 2), (1, 4)]
    # g.add_edges_from(edges)
    # nodes = [0, 1, 2, 3, 4, 5, 6]
    # subg = g.subgraph(nodes=nodes)
    # print(list(subg.edges))
    # import networkx as nx
    g = nx.Graph()
    edges = [(0, 1), (2, 0), (1, 2), (4, 3)]
    g.add_edges_from(edges)

    # num = nx.number_connected_components(g)
    # print(num)

    # c = nx.connected_components(g)
    """
    这样可以获得图的子图的边
    """
    c = nx.connected_component_subgraphs(g, copy=True)
    for i in list(c):
        print(list(i.edges))


    # C = nx.connected_component_subgraphs(g)
    # print(list(C))
    # for i in list(C):
    #     pos = nx.spring_layout(i)
    #     nx.draw_networkx(i, pos=pos, node_size=4, with_labels=True)
    #     plt.show()


def get_subgraph_with_greedy_algorithm(g, focus=None, total_num_doi_subgraph=None):
    """

    :param G: a graph with DOI value in graph-tool
    :param focus: a node specified by user.
    :param total_num_doi_subgraph: number of nodes in DOI subgraph.
    :return: F, nodes list of DOI subgraph. e.g. [0, 1, 2, 3, 7, 8, 10]
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


# 抽取DOI子图
def extract_doi_subgraph(g, edges_list_g, subgraph_nodes_list=None):
    """
    :param g: graph-tool undireced Graph instance.
    edges_list_g: edges_list_g=[(source, target, value, source_name, target_name), ...]
    :param subgraph_nodes_list: list of subgraph nods, e.g.[0, 1, 5, 7].
    :return: subgraph_edges_listge格式与edges_list_g一致, subgraph_edges_listge=[(source, target, value, source_name, target_name), ...]
    """
    vfilt = g.new_vertex_property('bool')  # create PropertyMap instance for extracting subgraph.
    for v in subgraph_nodes_list:
        vfilt[v] = True
    # TODO: 获得子图.注意: 使用GraphView(),这个实例与原始图g共享数据,所以GraphView()修改,e.g. 添加,移除会改变原始图的数据.
    sub = gt.GraphView(g, vfilt)
    # for e in sub.edges():
    #     print("e")
    #     print(e)
    subgraph_edges_list = []
    for e in sub.get_edges():  # 注意:使用 sub.get_edges() 这种方式可以获得边的索引.
        # print("eeee")
        # print(e)
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


# 测试贪心算法,用于DOI子图的获取.
def test_get_subgraph_with_greedy_algorithm():
    """
        第一步: 创建图,准备图数据.
    """
    g = gt.Graph(directed=False)
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

    if data_type == "fake":
        fake_value = [0.5, 0.3, 0.4, 0.5, 0.1, 0.9, 0.8, 0.2, 0.22, 0.15, 0.17]
        counter = -1
        for i in fake_value:
            counter = counter + 1
            g.vertex_properties["doi"][counter] = i  # 这种写法,必须在g.vertex_properties["doi"] = v_prop_DOI之后.

    """
        第二步: 使用贪心算法,抽取DOI子图节点.
    """
    focus = 0
    total_num_doi_subgraph = 7
    F = get_subgraph_with_greedy_algorithm(g=g, focus=focus, total_num_doi_subgraph=total_num_doi_subgraph)
    print("F")
    print(F)
    # pos = gt.sfdp_layout(g)
    # gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2, output_size=(200, 200), output=None)
    """
        第三步: 抽取DOI子图.
    """
    # TODO: 下一步抽取DOI子图
    extract_doi_subgraph(g, edges_list_g=edges_list, subgraph_nodes_list=F)


def test_layout_citation_visualization():
    json_name = "static/json/citation_network_visualization.json"
    with open(json_name, "r") as f:
        citation_network_id = json.load(f)  # json文件使用json.load()变成一个对象.
        links = citation_network_id["links"]  # [{"source": , "target": }, ...]
        nodes = citation_network_id["nodes"]  # [{"id": , "name": }, ...]
        nodes_id_list = []
        edges_list = []
        for obj in nodes:
            nodes_id_list.append(obj["id"])

        for obj in links:
            source = obj["source"]
            target = obj["target"]
            source_id = nodes_id_list.index(source)
            target_id = nodes_id_list.index(target)
            edges_list.append((source_id, target_id))


        # 使用graph-tool构造一个图
        g = gt.Graph(directed=True)
        N = len(nodes_id_list)  # 节点数量
        g.add_vertex(n=N)
        g.add_edge_list(edge_list=edges_list)  # 添加边.

        tmp_node_list = []
        for i in range(N):
            tmp_node_list.append(i)
        r = g.get_in_degrees(tmp_node_list)
        # r = np.array(r)
        r = sorted(r, reverse=True)
        counter = 0
        for i in r:
            counter = counter + 1
            if i == 0:
                break
        print(counter)  # r[6901]
        print("没有参考可视化领域的论文数量", N - 6900)  # 1544
        pos = gt.sfdp_layout(g)  #
        gt.graph_draw(g, pos, vertex_text="0", vertex_font_size=18, vertex_size=10, edge_pen_width=1.2, output_size=(1000, 1000), output="citation.pdf")


# 从非连接图中抽取出连接图
def test_graph_tool_for_disconnected_graph():

    # Load a disconnected graph
    g = gt.collection.data["netscience"]

    # Extract the largest component
    largest_comp = gt.GraphView(g, vfilt=gt.label_largest_component(g))
    gt.graph_draw(g, output="largest.pdf")
    # Draw the largest component
    gt.graph_draw(largest_comp, output="largest_comp.pdf")


# ****************************************  从非连接图中, 抽取最大连接子图 **************************************************

# ************************************ 可视化领域的论文引用网络 *********************************************
# 查询Citation_Visualization.db中的paper表,获得对应节点的属性值.
def get_attributes_from_Citation_Visualization_for_paper(node_id=None):
    # *************************** 获得对应节点的属性值 **************************** #
    dbname = "DB/Citation_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("Opened database successfully")
    # 创建数据库中的游标对象
    cursor = db.cursor()
    cursor.execute("select id, title, authors, public_venue, year, n_citation, reference, abstract from citation_nodes where id=?", (node_id,))
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果 [(),..]
    print(data[0])

# 从可视化领域的引用网络中抽取最大的连通网络.
def extract_max_connected_component_from_citation_visualization():
    json_name = "static/json/citation_network_visualization.json"
    with open(json_name, "r") as f:
        citation_network_id = json.load(f)  # json文件使用json.load()变成一个对象.
        links = citation_network_id["links"]  # [{"source": , "target": }, ...]
        # nodes = citation_network_id["nodes"]  # [{"id": , "name": }, ...]
        nodes_id_set = set()
        edges_list = []
        for obj in links:
            source = obj["source"]
            target = obj["target"]
            nodes_id_set.add(source)
            nodes_id_set.add(target)
        # TODO: nodes_id_list,格式如[node_id1, ...], 图中节点的索引就是这个列表的索引,所以可以根据这个列表,获得对应的节点在数据库表中的id,从而获得该节点的属性信息.
        nodes_id_list = list(nodes_id_set)

        # get_attributes_from_Citation_Visualization_for_paper(node_id=nodes_id_list[0])
        edges_list_without_weight = []
        for obj in links:
            source = obj["source"]
            target = obj["target"]
            edges_list_without_weight.append((source, target))  # [(), (), ...]
            source_id = nodes_id_list.index(source)
            target_id = nodes_id_list.index(target)
            edges_list.append((source_id, target_id))
        # 注意: edges_list_without_weight 与 edges_list一一对应.
        # 使用graph-tool构造一个图
        g = gt.Graph(directed=True)
        N = len(nodes_id_list)  # 节点数量
        g.add_vertex(n=N)
        g.add_edge_list(edge_list=edges_list)  # 添加边.

        print("原图的节点和边数量: ", N, len(edges_list))
        """
        # 抽取里面的最大网络.
        """
        pos_g = gt.sfdp_layout(g)
        gt.graph_draw(g, pos_g, output="static/graph_drawing/mty_jj_citation_visualization.pdf")

        # TODO: 注意: gt.label_largest_component中directed=True时,不能提取出最大的连接子图.
        largest_comp = gt.GraphView(g, vfilt=gt.label_largest_component(g, directed=False))
        max_subgraph_edges = largest_comp.get_edges()  # # 获得最大子图的边的索引.
        f_subg = open("connected_max_subgraph_citation_network_visualization.json.txt", "w")
        for i in max_subgraph_edges:
            temp_edge_index = i[2]  # 边的索引
            temp_edge = edges_list_without_weight[temp_edge_index]
            # max_subgraph_edges_id_list.append(temp_edge)
            f_subg.write(temp_edge[0] + " " + temp_edge[1] + "\n")
        f_subg.close()
        # max_connected_component_edges = list(largest_comp.edges())  # 31544条边
        # max_connected_component_nodes = list(largest_comp.vertices())  # 8094个节点
        # print("max_connected_component_edges: ", len(max_connected_component_edges))
        # print("max_connected_component_nodes: ", len(max_connected_component_nodes))
        # pos_largest_comp = gt.sfdp_layout(largest_comp)
        # gt.graph_draw(largest_comp, pos_largest_comp, output="static/graph_drawing/mty_jj_largest_comp_citation_visualization.pdf")


# ************************************ 可视化领域的作者合作网络 **************************************************#


# 从数据库AcademicNetwork.db中查找node_id对应的作者属性值.
def get_attributes_from_AcademicNetwork_for_author(node_id=None):
    """
    :param node_id: 节点的在数据库中的id
    :return: [{"key": "id", "value": "12345"}, {}, ...]
    """
    dbname = "DB/AcademicNetwork.db"
    db = sqlite3.connect(dbname)
    print("Opened database successfully")
    # 创建数据库中的游标对象
    cursor = db.cursor()
    # TODO: 由于数据库表author中数据量太大(百万级别),可以单单将可视化领域的作者信息存放在一张表中.
    cursor.execute("select id, name, institution, num_papers, num_citation, H_index, P_index, UP_index, interests from author where id=?",(node_id,))
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果 [(),..]
    # print(data[0])
    # TODO: 变成vue中table数据,形如: tabledata=[{"key": "id", "value": "12345"}, {}, ...]
    # 获得表格的字段.
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()  # Tables 为元组列表 [('author',), ('paper',), ('coauthor',), ('author2paper',)]
    # print(tables)  #[('author',), ('paper',), ('coauthor',), ('author2paper',)]

    table_name = tables[0][0]  # 获取第一个表名 author表.

    cursor.execute("SELECT * FROM {}".format(table_name))
    col_name_list = [tuple_[0] for tuple_ in cursor.description]  # 获得表中的字段.
    print(col_name_list)
    tableData = []
    value_list = data[0]  # col_name_list 对应的值.
    # print(value_list)
    for i in range(len(col_name_list)):
        temp = {}
        temp["key"] = col_name_list[i]
        temp["value"] = value_list[i]
        tableData.append(temp)

    return tableData


# 根据作者Id 获得作者的名字,用于在D3上显示.
def get_author_name_for_node(node_id=None):
    """
        :param node_id: 节点的在数据库中的id
        :return: [{"key": "id", "value": "12345"}, {}, ...]
    """
    dbname = "DB/AcademicNetwork.db"
    db = sqlite3.connect(dbname)
    print("Opened database successfully")
    # 创建数据库中的游标对象
    cursor = db.cursor()
    # TODO: 由于数据库表author中数据量太大(百万级别),可以单单将可视化领域的作者信息存放在一张表中.
    cursor.execute("select name from author where id=?", (node_id,))

    data = cursor.fetchall()  # 使用这种方式取出所有查询结果 [(),..]
    author_name = data[0][0]  # 获得作者的名字
    # print(author_name)
    return author_name


# 由于visualization_coauthor_edges构成的网络是不连通的,所以需要抽取里面的最大连通子图,以备后续研究.
def extract_max_connected_component_from_coauthor_visualization():
    """
    # 对于graph-tool而言, 只需要有边就可以构造出一个图来了,
    # e.g. e=[(), (), ...],从中提取节点个数,构造节点的索引,最后就可以构造出一个图了.

    """

    with open("static/data/visualization_coauthor_edges.txt", "r") as f:
        start_time = datetime.datetime.now()
        lines = f.readlines()
        print(len(lines))
        # edges_list_without_weight = []
        edges_list_with_weight = []
        nodes_set = set()
        for line in lines:
            line = line.strip()
            line = line.split()
            # print(line)
            # edges_list_without_weight.append((line[0], line[1]))  # 不带权重
            edges_list_with_weight.append(line)  # 带权重.
            nodes_set.add(line[0])
            nodes_set.add(line[1])
        # TODO: # [node_id1, ...] 图中节点的索引就是这个列表的索引,所以可以根据这个列表,获得对应的节点在数据库表中的id,从而获得该节点的属性信息.
        nodes_id_list = list(nodes_set)
        # get_attributes_from_AcademicNetwork_for_author(nodes_id_list[0])

        links_list = []
        for edge in edges_list_with_weight:
            source = edge[0]
            target = edge[1]
            source_index = nodes_id_list.index(source)
            target_index = nodes_id_list.index(target)
            links_list.append((source_index, target_index))
        # 注意: edges_list_with_weight 与 links_list 是一一对应的.
        g = gt.Graph(directed=False)
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
        largest_comp = gt.GraphView(g, vfilt=gt.label_largest_component(g, directed=False))
        # max_connected_component_edges = list(largest_comp.edges())  # 7268 条边
        # max_connected_component_nodes = list(largest_comp.vertices())  # 2762 个节点
        #
        # print("max_connected_component_edges: ", max_connected_component_edges)
        # print("max_connected_component_nodes: ", max_connected_component_nodes)
        max_subgraph_edges_id_list = []
        # max_subgraph_nodes = largest_comp.get_vertices()  # 获得最大子图的节点的索引.
        max_subgraph_edges = largest_comp.get_edges()  # # 获得最大子图的边的索引.
        f_subg = open("connected_max_subgraph_visualization_coauthor_edges.txt", "w")
        for i in max_subgraph_edges:
            temp_edge_index = i[2]  # 边的索引
            temp_edge = edges_list_with_weight[temp_edge_index]
            # max_subgraph_edges_id_list.append(temp_edge)
            source_name = get_author_name_for_node(node_id=temp_edge[0])
            target_name = get_author_name_for_node(node_id=temp_edge[1])
            f_subg.write(temp_edge[0] + "|" + temp_edge[1] + "|" + temp_edge[2] + "|" + source_name + "|" + target_name + "\n")
        f_subg.close()
        # print("max_connected_component_edges: ", len(max_connected_component_edges))
        # print("max_connected_component_nodes: ", len(max_connected_component_nodes))
        # pos_largest_comp = gt.sfdp_layout(largest_comp)
        # gt.graph_draw(largest_comp, pos_largest_comp, output="static/graph_drawing/mty_largest_comp_coauthor_visualization.pdf")

        end_time = datetime.datetime.now()
        time = (end_time - start_time).seconds
        print("用时:")
        print(time)


# 对连通的可视化领域的作者合作网络进行操作.
def operate_connected_coauthor_network_visualization():
    # 先对其进行布局展示.
    f = open("static/data/connected_max_subgraph_visualization_coauthor_edges.txt")
    start_time = datetime.datetime.now()
    lines = f.readlines()
    print(len(lines))
    edges_list_with_weight = []
    nodes_set = set()
    for line in lines:
        line = line.strip()
        line = line.split()
        edges_list_with_weight.append(line)  # 带权重.
        nodes_set.add(line[0])
        nodes_set.add(line[1])
    # TODO: # [node_id1, ...] 图中节点的索引就是这个列表的索引,所以可以根据这个列表,获得对应的节点在数据库表中的id,从而获得该节点的属性信息.
    nodes_id_list = list(nodes_set)

    # get_attributes_from_AcademicNetwork_for_author(nodes_id_list[0])

    links_list = []
    for edge in edges_list_with_weight:
        source = edge[0]
        target = edge[1]
        source_index = nodes_id_list.index(source)
        target_index = nodes_id_list.index(target)
        links_list.append((source_index, target_index))
    # 注意: edges_list_with_weight 与 links_list 是一一对应的.
    g = gt.Graph(directed=False)
    N = len(nodes_set)  # 节点数量
    g.add_vertex(n=N)
    g.add_edge_list(edge_list=links_list)  # 添加边.
    print("节点, 边数量: ", N, len(links_list))
    print("graph drawing.......")
    pos = gt.sfdp_layout(g)
    end_time = datetime.datetime.now()
    time = (end_time - start_time).seconds
    print("用时:")
    print(time)
    # gt.graph_draw(g, pos, vertex_text="0", vertex_font_size=8, vertex_size=10, edge_pen_width=1.2, output_size=(1000, 1000), output=None)
    gt.graph_draw(g, pos, output_size=(1000, 1000), output=None)

# ************************************** END ******************************************* #


# 获得DOI子图,从连通的合作网络中.
def doi_subgraph_from_connected_coauthor_network_visualization(focus, total_num_doi_subgraph, directed=False):
    """
    focus: 焦点节点的id, 要将id转换成对应的节点的index.
    total_num_doi_subgraph:
    :return: graph={'nodes':[{'id': XXX, 'name': xxx, "value": XXX}, ...], 'links':[{'source': XXX, 'target': XXX, 'value': XXX}, ....]}
             this format is adapted to D3 in frontend.
    """
    """
        第一步: 构造一个图,计算doi值,并作为节点属性.
    """
    f = open("static/data/connected_max_subgraph_visualization_coauthor_edges.txt")  # 可视化领域的作者合作网络.
    start_time = datetime.datetime.now()
    lines = f.readlines()
    # print(len(lines))
    edges_list_with_weight = []
    nodes_set = set()
    for line in lines:
        line = line.strip()
        line = line.split("|")
        edges_list_with_weight.append(line)  # 带权重. edges_list_with_weight=[(source, target, value, source_name, target_name), ...]
        nodes_set.add((line[0], line[3]))  # (source, name)
        nodes_set.add((line[1], line[4]))  # (source, name)
    # TODO: nodes_id_list=[node_id1, ...] 图g中节点的索引就是这个列表的索引,所以可以根据这个列表,获得对应的节点在数据库表中的id,从而获得该节点的属性信息.它里面的顺序不影响后面边的构造,因为节点与构造的边是对应的.
    nodes_id_list = []
    nodes_name_list = []
    for each_iterm in nodes_set:
        node = each_iterm[0]
        name = each_iterm[1]
        nodes_id_list.append(node)
        nodes_name_list.append(name)
    # nodes_id_list 与 nodes_name_list 一一对应.
    # nodes_id_list = list(nodes_set)  # [id1, id2, ...]
    # get_attributes_from_AcademicNetwork_for_author(nodes_id_list[0])
    links_list = []

    for edge in edges_list_with_weight:
        source = edge[0]
        target = edge[1]
        source_index = nodes_id_list.index(source)
        target_index = nodes_id_list.index(target)
        links_list.append((source_index, target_index))
    # 注意: edges_list_with_weight 与 links_list 是一一对应的, 而edges_list_with_weight与文件行对应.
    g = gt.Graph(directed=directed)
    N = len(nodes_set)  # 节点数量
    g.add_vertex(n=N)
    g.add_edge_list(edge_list=links_list)  # 添加边.
    print("连通图的节点, 边数量: ", N, len(links_list))

    # TODO: 计算节点最后的DOI值,现在使用pg值作为DOI值,以后用自己的算法来替代gt.pagerank(g).
    DOI_list = gt.pagerank(g)  # 计算pagerank值作为DOI值,用于实验. DOI_list=(xxx, xxx, ....) 对应g图中的节点索引(节点0,节点1,...)
    v_doi_list = []  # 存放节点的DOI值,(x, x, ......) 其索引对应图g中的节点索引.
    for i in DOI_list:
        # print("v_doi_list")
        # print(i)
        v_doi_list.append(i)
    # print(v_doi_list)
    v_prop_DOI = g.new_vertex_property("double")  # 给节点添加pagerank属性
    # print("g.vertices()")
    # print(g.vertices())
    for v in g.vertices():  # g.vertices()里面的节点按照索引排列,即(0, 1, 2, ....N)
        # print("int(v)")
        # print(int(v))
        v_prop_DOI[v] = v_doi_list[int(v)]  # int(v)表示节点的索引, v_doi_list是索引对应的pg值,现在作为DOI值.
    g.vertex_properties["doi"] = v_prop_DOI  # 将pr值作为每个节点的pagerank属性值, 映射: v-->{"pagerank": 0.04633}

    """
       第二步: 使用贪心算法,抽取DOI子图节点.
    """
    focus_index = nodes_id_list.index(focus)  # 根据节点的id获得其在图中对应的索引

    # total_num_doi_subgraph = total_num_doi_subgraph
    F = get_subgraph_with_greedy_algorithm(g=g, focus=focus_index, total_num_doi_subgraph=total_num_doi_subgraph)
    # print("DOI子图节点列表:")
    # pos = gt.sfdp_layout(g)
    # gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2, output_size=(200, 200), output=None)
    """
       第三步: 抽取DOI子图.
    """
    # TODO: 下一步抽取DOI子图
    subgraph_edges_list = extract_doi_subgraph(g, edges_list_g=edges_list_with_weight, subgraph_nodes_list=F)

    print("edges_list_with_weight + subgraph_edges_list", edges_list_with_weight[0], subgraph_edges_list[0])

    # 由于边是由于index构成的,(index, index),一旦跳出函数就无法确定其对应节点在数据库中的id,所以,应该将这种边转换成(id, id)
    # subgraph_edges_list_with_id = []
    # for each_edge in subgraph_edges_list:
    #     source_id = nodes_id_list[each_edge[0]]
    #     target_id = nodes_id_list[each_edge[1]]
    #     subgraph_edges_list_with_id.append((source_id, target_id))

    # print("subgraph_edges_list")
    # print(subgraph_edges_list)
    # print("len(subgraph_edges_list)")
    # print(len(subgraph_edges_list))

    end_time = datetime.datetime.now()
    time = (end_time - start_time).seconds
    print("用时:")
    print(time)

    # 构造VUE前端需要的graph格式.
    graph = {
        "nodes": [],
        "links": []
    }
    edges_list = subgraph_edges_list  # [(source, target, value, source_name, target_name), ...]

    nodes_set = set()
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
        node_doi_value = v_doi_list[node_idx]  # 用节点索引获得对应的DOI值.
        name_ = nodes_name_list[node_idx]
        # name_ = get_author_name_for_node(node_id=node)
        node = {"id": node, "name": name_, "value": node_doi_value}
        graph["nodes"].append(node)

    return graph


# 从作者合作图中获得id对应的节点的所有邻居.
def get_neighbors_from_connected_coauthor_network_visualization(node_id, directed=False):
    """
    :param node_id: vue传过来的节点id.
    :param directed: 图是否有向
    :param num_neighbors: 取的邻居的最大数量.
    :return: 一个以node_id为中心及其邻居组成的图 graph={'nodes':[{'id': XXX, 'name': xxx, "value": XXX}, ...],
            'links':[{'source': XXX, 'target': XXX, 'value': XXX}, ....]}
    """
    f = open("static/data/connected_max_subgraph_visualization_coauthor_edges.txt")  # 可视化领域的作者合作网络.
    start_time = datetime.datetime.now()
    lines = f.readlines()
    # print(len(lines))
    edges_list_with_weight = []
    nodes_set = set()
    for line in lines:
        line = line.strip()
        line = line.split("|")
        edges_list_with_weight.append(line)  # 带权重. edges_list_with_weight=[(source, target, value, source_name, target_name), ...]
        nodes_set.add((line[0], line[3]))  # (source, name)
        nodes_set.add((line[1], line[4]))  # (source, name)
    # TODO: nodes_id_list=[node_id1, ...] 图g中节点的索引就是这个列表的索引,所以可以根据这个列表,获得对应的节点在数据库表中的id,从而获得该节点的属性信息.它里面的顺序不影响后面边的构造,因为节点与构造的边是对应的.
    # edges_list_with_weight=[(source, target, value, source_name, target_name), ...]
    # nodes_id_list 与 nodes_name_list 一一对应.
    nodes_id_list = []
    nodes_name_list = []
    for each_iterm in nodes_set:
        node = each_iterm[0]
        name = each_iterm[1]
        nodes_id_list.append(node)
        nodes_name_list.append(name)

    # 注意: edges_list_with_weight 与 links_list 是一一对应的, 而edges_list_with_weight与文件行对应.
    links_list = []

    for edge in edges_list_with_weight:
        source = edge[0]
        target = edge[1]
        source_index = nodes_id_list.index(source)
        target_index = nodes_id_list.index(target)
        links_list.append((source_index, target_index))

    g = gt.Graph(directed=directed)
    N = len(nodes_set)  # 节点数量
    g.add_vertex(n=N)
    g.add_edge_list(edge_list=links_list)  # 添加边.
    # TODO: 添加图的边权重属性.
    test = False
    if test:
        e_prop = g.new_edge_property("double")  # {e1:xx, e2: xx, e3: xx, ...}
        for edge_with_index in g.get_edges():
            edge = edge_with_index[:2]  # [source, target]
            index_edge = edge_with_index[2]  # index of edge.
            e_prop[edge] = edges_list_with_weight[index_edge][2]  # 从edges_list_with_weight里面取得对应边的权重.
        g.edge_properties["weight"] = e_prop  # {"weight":{e1:xx, ...}}
        # r = g.edge_properties["weight"][edge]  # 以这种方式获得对应边的权重.

    print("连通图的节点, 边数量: ", N, len(links_list))

    # TODO: 计算节点最后的DOI值,现在使用pg值作为DOI值,以后用自己的算法来替代gt.pagerank(g).
    DOI_list = gt.pagerank(g)  # 计算pagerank值作为DOI值,用于实验. DOI_list=(xxx, xxx, ....) 对应g图中的节点索引(节点0,节点1,...)
    # TODO: 增加DOI值扩散处理.

    v_doi_list = []  # 存放节点的DOI值,(x, x, ......) 其索引对应图g中的节点索引.
    for i in DOI_list:
        # print("v_doi_list")
        # print(i)
        v_doi_list.append(i)
    # print(v_doi_list)
    v_prop_DOI = g.new_vertex_property("double")  # 给节点添加pagerank属性 specify type of value in dict: {node_index: doube, ...}

    for v in g.vertices():  # g.vertices()里面的节点按照索引排列,即(0, 1, 2, ....N)
        v_prop_DOI[v] = v_doi_list[int(v)]  # 赋值 int(v)表示节点的索引, v_doi_list是索引对应的pg值,现在作为DOI值.
    g.vertex_properties["doi"] = v_prop_DOI  # {"doi": {node1_index: xxx, node2_index: xxx, node3_index: xxx, ...}}, 将pr值作为每个节点的doi属性值,

    graph = {
        "nodes": [],
        "links": []
    }
    nodes_set = set()
    node_index_for_id = nodes_id_list.index(node_id)  # 获得node_id对应的g中的index
    print("DOI node_id", node_id)
    print("DOI node_index_for_id", node_index_for_id)
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
        print("有向", edge_in, edge_out)
    else:  # 无向
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
    end_time = datetime.datetime.now()
    time = (end_time - start_time).seconds
    print("用时:")
    print(time)
    num_nb = g.get_out_neighbors(node_index_for_id)
    print(len(num_nb))
    print(num_nb)
    return graph


# 测试最短路径
def test_shortest_path():
    directed = False
    g = gt.Graph(directed=directed)
    N = 11  # 节点数量
    g.add_vertex(n=N)
    edges_list = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 7), (0, 8), (7, 8), (7, 9), (7, 10), (4, 5), (5, 6), (1, 2),
                  (1, 4), (8, 10), (0, 9), (9, 10)]
    g.add_edge_list(edge_list=edges_list)
    source = 0
    target = 10
    for path in gt.all_shortest_paths(g, source=g.vertex(source), target=g.vertex(target)):
        print(path)
    vlist, elist = gt.shortest_path(g, source=g.vertex(source), target=g.vertex(target))
    print([str(v) for v in vlist])
    print([str(e) for e in elist])

    # TODO: 对于无向图而言,使用get_out_edges才能获得指定点对应的边.

    # v_prop_DOI = g.new_vertex_property("double")  # 给节点添加pagerank属性
    #
    # for v in g.vertices():  # g.vertices()里面的节点按照索引排列,即(0, 1, 2, ....N)
    #     v_prop_DOI[v] = v_doi_list[int(v)]  # int(v)表示节点的索引, v_doi_list是索引对应的pg值,现在作为DOI值.
    # g.vertex_properties["doi"] = v_prop_DOI  # 将pr值作为每个节点的doi属性值, 映射: v-->{"doi": 0.04633}
    '''    
    if directed:  # 有向
        pass
    else:  # 无向.
        r = g.get_out_edges(v=4)
        e_prop = g.new_edge_property("string")  # {e1:xx, e2: xx, e3: xx, ...}
        for i in g.edges():
            e_prop[i] = str(i)
        g.edge_properties["weight"] = e_prop  # {"weight":{e1:xx, ...}}

        print(g.edge_properties["weight"][(10, 9)])
    '''
    # r = g.get_edges()
    # for edge in r:
    #     print(edge)
    # print(r)
    r = g.edge(s=4, t=0)

    print(r.edge_index)

    pos = gt.sfdp_layout(g)
    gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
                  output_size=(800, 800), output=None)


if __name__ == "__main__":

    # graph = doi_subgraph_from_connected_coauthor_network_visualization(focus="1416227", total_num_doi_subgraph=10)
    # print(graph)

    # directed = False
    # g = gt.Graph(directed=directed)
    # N = 11  # 节点数量
    # g.add_vertex(n=N)
    # edges_list = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 7), (0, 8), (7, 8), (7, 9), (7, 10), (4, 5), (5, 6), (1, 2),
    #               (1, 4), (8, 10), (0, 9), (9, 10)]
    # g.add_edge_list(edge_list=edges_list)

    # e_list = []
    # if directed:
    #     e_in = g.get_in_edges(7)
    #     e_out = g.get_out_edges(7)
    #     print("有向", e_in, e_out)
    # else:
    #     e_out = g.get_out_edges(7)
    #     print("无向", e_out)
    # a = g.get_out_neighbors(7)
    # b = g.get_in_neighbors(7)
    # print(r)

    # (source, target, value, source_name, target_name)
    # a = ("123", "456", 90, "mty", "jj")
    # print(a[:3])
    # a = [(1, 2), (3, 4)]
    # b = [(12, 22), (32, 42)]
    # c = a + b
    # print(c)
    # 647629
    # g = get_neighbors_from_connected_coauthor_network_visualization(node_id="522311", directed=False)

    # source = 0
    # target = 10
    # for path in gt.all_shortest_paths(g, source=g.vertex(source), target=g.vertex(target)):
    #     print(path)
    # vlist, elist = gt.shortest_path(g, source=g.vertex(source), target=g.vertex(target))
    # print([str(v) for v in vlist])
    # print([str(e) for e in elist])
    #
    # pos = gt.sfdp_layout(g)
    # gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
    #               output_size=(800, 800), output=None)
    # test_shortest_path()
    r = get_attributes_from_AcademicNetwork_for_author(node_id="244574")
    print(r)



















