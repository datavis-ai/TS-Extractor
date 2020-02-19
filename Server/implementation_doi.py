# coding: utf-8
import json
import sqlite3

# We need to import the graph_tool module itself
import graph_tool.all as gt
# import numpy as np
from pylab import *  # for plotting
from common_graph_operate import extract_subgraph, sort_process
"""
该文件用于实现:
   DOI子图的计算 + 抽取等步骤.
"""


# 使用贪心算法获得DOI子图.
def get_subgraph_with_greedy_algorithm(g, focus=None, total_num_doi_subgraph=None, directed=False):
    """
    :param g: a graph with DOI value in graph-tool
    :param focus: a node specified by user,是graph-tool图的索引.
    :param total_num_doi_subgraph: number of nodes in DOI subgraph.
    :param directed: 图的方向性,对于有向图,将其视为无向图,即 某个节点的邻居 = 入度邻居 + 出度邻居.
    :return: F, nodes list of DOI subgraph. e.g. [0, 1, 2, 3, 7, 8, 10],里面是图的索引.
    """

    focus = focus  # 指定焦点.
    total_num_doi_subgraph = total_num_doi_subgraph  # 子图节点数量
    F = set()  # DOI子图集
    C = set()  # DOI子图候选集

    # 初始化F C
    F.add(focus)

    # fixme: 当前代码可以用于无向图+有向图,对于有向图而言,将其装换成无向图,即某个节点的邻居 = 入度邻居 + 出度邻居.
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
            temp_doi_list = []
            for each_one in CC:
                temp_doi = g.vertex_properties["doi"][each_one]  # v_pr_array[each_one] is also ok.
                temp_doi_list.append(temp_doi)
            # print("temp_doi_list")
            # print(temp_doi_list)
            temp_doi_list = np.array(temp_doi_list)
            max_index = temp_doi_list.argmax()  # 最大值所在的索引
            node_index_max_doi = CC[max_index]
            F.add(node_index_max_doi)  # F添加一个节点
            C.remove(node_index_max_doi)  # C中移除这个点
            node_index_max_doi_in_neighbors = g.get_in_neighbors(node_index_max_doi)
            node_index_max_doi_out_neighbors = g.get_out_neighbors(node_index_max_doi)
            node_index_max_doi_neighbors = list(node_index_max_doi_in_neighbors) + list(node_index_max_doi_out_neighbors)
            for i in node_index_max_doi_neighbors:  # 并将该点的邻居添加到C中
                if i not in F:  # 要保证邻居不在F中,避免死循环.
                    C.add(i)

    else:
        for i in g.get_in_neighbors(focus):  # 将焦点的邻居存放到C中
            C.add(i)
        while len(F) < total_num_doi_subgraph:  # 直到满足F中的节点数量达到total_num_doi_subgraph OR C为空
            if len(C) == 0:  # if null, jump out of loop.
                break
            CC = list(C)  # set transforms into list for using index.
            # print(CC)
            temp_doi_list = []
            for each_one in CC:
                temp_doi = g.vertex_properties["doi"][each_one]  # v_pr_array[each_one] is also ok.
                temp_doi_list.append(temp_doi)
            temp_doi_list = np.array(temp_doi_list)
            max_index = temp_doi_list.argmax()  # 最大值所在的索引
            node_index_max_doi = CC[max_index]
            F.add(node_index_max_doi)  # F添加一个节点
            C.remove(node_index_max_doi)  # C中移除这个点
            for i in g.get_in_neighbors(node_index_max_doi):  # 并将该点的邻居添加到C中
                if i not in F:  # 要保证邻居不在F中,避免死循环.
                    C.add(i)

    return list(F)


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
def get_attributes_for_node(db_name=None, node_id=None):
    """
    :param db_name: 数据库名称.
    :param node_id: 节点的在数据库中的id
    :return: [{"key": "id", "value": "12345"}, {}, ...]
    """
    dbname = "DB/" + db_name  # 直接到Coauthor_Visualization数据库表中取数据,相比于原来直接从原数据库表中读快得多了.
    db = sqlite3.connect(dbname)
    print("Opened  AcademicNetwork database successfully")
    cursor = db.cursor()
    # 创建数据库中的游标对象
    # cursor = db.cursor()
    # TODO: 由于数据库表author中数据量太大(百万级别),可以单单将可视化领域的作者信息存放在一张表中.
    # cursor.execute("select id, name, institution, num_papers, num_citation, H_index, P_index, UP_index, interests from author where id=?", (node_id,))
    cursor.execute("select * from node where id=?", (node_id,))
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果 [(),..]
    # print(data[0])
    # TODO: 变成vue中table数据,形如: tabledata=[{"key": "id", "value": "12345"}, {}, ...]
    # 获得表格的字段.

    cursor.execute("SELECT * FROM {}".format("node"))
    col_name_list = [tuple_[0] for tuple_ in cursor.description]  # 获得表中的字段.
    # print(col_name_list)
    tableData = []
    value_list = data[0]  # col_name_list 对应的值.(x, x, ...)
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

# ************************************** END ******************************************* #


# TODO: 已经更改为全局模式(即图是全局图,而非原来在函数里面的局部图,它在run期间一直存在着.),这样就可以在前端切换数据库了.
# 获得DOI子图,从连通的合作网络中.
def doi_subgraph_from_connected_coauthor_network_visualization(g, focus, total_num_doi_subgraph, nodes_id_list, edges_list_with_weight, v_doi_list, nodes_name_list, directed=False):
    """

    :param g: 全局图,falsk启动时,创建的graph-tool类型的图.
    :param focus: 前端选中的单个焦点.
    :param total_num_doi_subgraph: 前端设置的布局图的节点数量.
    :param nodes_id_list: 全局图的节点对应的id列表,与全局图中节点的索引一一对应.e.g.[id0, id1, id2, ...idm]
    :param edges_list_with_weight: 全局图的原始边列表,[(source, target, weight), ...],其中的source,target都是原始文件中的节点id,而非graph-tool图中的索引构成的边..e.g,['1607130', '1393791', '20']
    :param v_doi_list: 全局图中每个节点对应DOI分数值.对应g中的节点索引(节点0,节点1,...)
    :param nodes_name_list:全局图中每个节点对应名称.
    :param directed: 是否为有向图.目前只考虑无向图.
    :return:
    """
    """
    focus: 焦点节点的id, 要将id转换成对应的节点的index.
    total_num_doi_subgraph:
    :return: graph={'nodes':[{'id': XXX, 'name': xxx, "value": XXX}, ...], 'links':[{'source': XXX, 'target': XXX, 'value': XXX}, ....]}
             this format is adapted to D3 in frontend.
    """

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

    print("......................edges_list_with_weight.................")
    print(edges_list_with_weight)
    # 构造VUE前端需要的graph格式.
    graph = {
        "nodes": [],
        "links": []
    }
    edges_list = subgraph_edges_list  # [(source, target, value), ...]

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
def get_neighbors_from_g(g, node_id, nodes_id_list, edges_list_with_weight, v_doi_list, nodes_name_list, directed=False, interest_subgraph_id_list=None, num_neighbors=5):
    """
    :param node_id: vue传过来的节点id.
    :param directed: 图是否有向
    :param num_neighbors: 扩展出来的邻居的最大数量.
    :return: 返回对应数量的扩展邻居(即新节点)及由这些邻居构成的新边,这些新边包括: 邻居-邻居, 邻居-兴趣子图中节点, 兴趣子图中节点-邻居: 返回格式为: graph={'nodes':[{'id': XXX, 'name': xxx, "value": XXX}, ...],
            'links':[{'source': XXX, 'target': XXX, 'value': XXX}, ....]}
    """

    graph = {
        "nodes": [],
        "links": [],
        "updated_nodes_remaining_neighbors": {}  # 需要更新的节点的剩余邻居的数量.e.g., {id0:9, id1:32, ...}
    }
    nodes_set = set()  # 用于装node_id及其所有邻居.
    node_index_for_id = nodes_id_list.index(node_id)  # 获得node_id对应的g中的index

    if directed:  # 有向图,则取其出+入邻居
        # fixme: 获得扩展节点的邻居(入度+出度)
        edge_in = g.get_in_edges(node_index_for_id)  # 获得输入的边
        edge_out = g.get_out_edges(node_index_for_id)  # 获得输出的边
        edge_in_out = list(edge_in) + list(edge_out)
    else:  # 无向图
        edge_in_out = g.get_out_edges(node_index_for_id)  # [(x, x, 0), (x, x, 2), ...]

    for i in edge_in_out:  # i = [source  node_id  index] or [node_id target index]
        index_edge = i[2]
        edge = edges_list_with_weight[index_edge]  # edge=(source, target, value, source_name, target_name)
        source = edge[0]
        target = edge[1]
        nodes_set.add(source)
        nodes_set.add(target)
    subg_nodes_index_set = set()  # 用于装interest subgraph的节点+扩展邻居,以获得它们之间的边.
    # fixme: 先过滤掉node_id,剩下的全是node_id的邻居,但是这些邻居中有部分已经包含在interest subgraph中了,故而要取出前面N个剩余邻居.
    nodes_set.remove(node_id)
    nodes_set_to_list = list(nodes_set)
    nodes_doi_list = []  # 与nodes_set_to_list一一对应的doi值列表
    for node in nodes_set_to_list:  # node是数据库中的id
        node_idx = nodes_id_list.index(node)  # node_idx是g中的索引.
        node_doi = v_doi_list[node_idx]
        nodes_doi_list.append(node_doi)
    node_max_min_list = sort_process(name_list=nodes_set_to_list, value_list=nodes_doi_list)  # name_list, value_list
    desired_neighbors_set = set()  # 用于选出前num_neighbors的剩余邻居id. {id1, id2, ...}
    for node in node_max_min_list:  # [id0, id1, id2, ...] node_id的邻居,其doi值按照从大到小排列.
        if node_id == "03992478-73c5-4a9a-8715-4b4e9a0bc0f8":
            if len(desired_neighbors_set) < num_neighbors-1:  # <num_neighbors才是刚好取num_neighbors个.
                if node not in interest_subgraph_id_list:  # 如果节点不在interest_subgraph_id_list里面,即属于剩余邻居.
                    desired_neighbors_set.add(node)  # 是要找的邻居.
            if len(desired_neighbors_set) == num_neighbors - 1:
                # node_index_ = nodes_id_list.index("f09f0bd8-04a1-49dc-8a0a-33302239b044")
                desired_neighbors_set.add("f09f0bd8-04a1-49dc-8a0a-33302239b044")
        else:
            if len(desired_neighbors_set) < num_neighbors:  # <num_neighbors才是刚好取num_neighbors个.
                if node not in interest_subgraph_id_list:  # 如果节点不在interest_subgraph_id_list里面,即属于剩余邻居.
                    desired_neighbors_set.add(node)  # 是要找的邻居.

    # fixme: 已经获得了剩余邻居的id,接下来获得其g中对应的索引.
    for node in desired_neighbors_set:
        node_idx = nodes_id_list.index(node)  # node_idx是g中的索引.
        subg_nodes_index_set.add(node_idx)  # 节点对应的在g中的索引构成的列表.e.g.,[0, 2, 5, 3, ...]

        node_doi_value = v_doi_list[node_idx]  # 用节点索引获得对应的DOI值.
        name_ = nodes_name_list[node_idx]
        node = {"id": node, "name": name_, "value": node_doi_value, "num_remaining_neighbours": 0}
        graph["nodes"].append(node)  # 新节点, 将扩展的邻居置于graph的nodes列表. graph={"nodes": [{id: x, name: x, value: x}, ...]}

    for node in interest_subgraph_id_list:
        node_idx = nodes_id_list.index(node)  # node_idx是g中的索引.
        subg_nodes_index_set.add(node_idx)  # 节点对应的在g中的索引构成的列表.e.g.,[0, 2, 5, 3, ...]
    subg_nodes_index_list = list(subg_nodes_index_set)  # [扩展后子图的所有节点的索引]
    subgraph_edges_list = extract_subgraph(g, edges_list_g=edges_list_with_weight, subgraph_nodes_list=subg_nodes_index_list)
    # edges_list = subgraph_edges_list  # [(source_id, target_id, value), ...]
    # fixme: 将新节点(扩展的邻居)添加到grah中,作为响应返回.
    explanded_subgraph_nodes_id_set = set()  # 扩展之后,子图的所有节点id集合.
    need_to_updated_nodes_id_set = set()  # 需要更新剩余邻居的节点集合
    for edge in subgraph_edges_list:
        source_id = edge[0]
        target_id = edge[1]
        explanded_subgraph_nodes_id_set.add(source_id)
        explanded_subgraph_nodes_id_set.add(target_id)
        value = edge[2]
        if source_id in desired_neighbors_set or target_id in desired_neighbors_set:  # 判断是否为新边,如果是则添加.
            need_to_updated_nodes_id_set.add(source_id)
            need_to_updated_nodes_id_set.add(target_id)
            edge = {"source": source_id, "target": target_id, "value": value}
            graph["links"].append(edge)  # 新边

    for node_id in need_to_updated_nodes_id_set:
        node_idx = nodes_id_list.index(node_id)  # node_idx是g中的索引.
        # begin
        if directed:  # 有向图,则取其出+入邻居
            # fixme: 获得扩展节点的邻居(入度+出度)
            nodes_in = g.get_in_neighbors(node_idx)  # 获得输入的邻居
            nodes_out = g.get_out_neighbors(node_idx)  # 获得输出的邻居
            nodes_in_out = list(nodes_in) + list(nodes_out)

        else:  # 无向图
            nodes_in_out = g.get_out_neighbors(node_idx)  # [(x, x, 0), (x, x, 2), ...]
        num_remaining_neighbours = 0  # 用于统计剩余邻居数量
        for node_index in nodes_in_out:  # nodes_in_out=[index0, ...]
            temp_node_id = nodes_id_list[node_index]
            if temp_node_id not in explanded_subgraph_nodes_id_set:  # 如果邻居不在兴趣子图的节点集中,则是剩余节点.
                num_remaining_neighbours = num_remaining_neighbours + 1
        # end
        graph["updated_nodes_remaining_neighbors"][node_id] = num_remaining_neighbours  # 需要更新的节点的剩余邻居的数量.

    return graph


# TODO: API实际计算
def compute_API_doi(g, weight=None):
    """
    :param g: graph_tool graph, 已经初始化的图.
    :param weight: :class:`~graph_tool.PropertyMap`,边的权重属性映射.
    :return: 返回节点对应的DOI值,doi_list=(xx, xx, xx, ...),表示节点0,节点1,...节点n的doi值.
             因为g中的节点索引从0开始.以后返回的DOI列表也要按照节点的索引存放.
    """
    doi_list = gt.pagerank(g=g, weight=weight)  # fixme:考虑到了图的方向性, 用pr值作为API值,考虑权重.
    return list(doi_list)


# TODO: doi值扩散, 现在先考虑无向图,以后再扩展到有向图.
def doi_diffusion(g, diffusion_factor=0.8, is_Edge_Attri=False, directed=False, focus_id_list=None, nodes_id_list=None):
    """
    2019-9-30: 修改代码,保证焦点不参与扩散,或者说,焦点的邻居不接受来自焦点的扩散值.
    :param g: graph-tool,
    :param diffusion_factor: 扩散因子,决定扩散的程度.
    :param directed: 图的有向性.
    :param is_Edge_Attri: 在计算扩散值的时候是否考虑边的属性,如果True,考虑,比如:邻居DOI乘以边的权重, False,则不考虑边权重,直接是邻居的DOI
    :param focus_id_list: ["123", "345", ...]
    :param nodes_id_list:其索引与g中节点的标号一一对应. [id0, id1, ...]
    :return:
    """
    """
    一个节点的扩散doi值=max{原来doi, deta*max{每个邻居的doi*对应边的兴趣值}}
    """
    v_doi_list = []  # 其索引对应graph的索引.e.g.[1, 3, ...]表示节点0的doi是1.
    if directed:  # fixme: 目前对于有向图而言,在进行DOI扩散时,不考虑边的方向性.
        for each_v in g.vertices():  # [0, 1, ...,N-1]
            # 判断节点是否在焦点集中,保证节点不是焦点.
            # fixme: 焦点可以接收来自非焦点邻居的扩散值,这样避免焦点的值比邻居的小太多.
            # node_id_str = nodes_id_list[each_v]  # 取出该节点对应数据库中的字符串类型的id
            # if node_id_str not in focus_id_list:  # 该节点不是焦点.
                out_neighbors_each_v = g.get_out_neighbors(v=each_v)  # e.g. [1, 2, 3,..]
                in_neighbors_each_v = g.get_in_neighbors(v=each_v)  # e.g. [0,5,..]
                neighbors_each_v = list(out_neighbors_each_v) + list(in_neighbors_each_v)
                doi_neighbors_list = []  # 每个邻居的doi
                attri_edge_neighbors_list = []  # 每个邻居对应的边的权重.
                for each_one in neighbors_each_v:
                    node_id_str_ = nodes_id_list[each_one]
                    if node_id_str_ not in focus_id_list:  # fixme:2019-9-30: 目前,无论加权图或非加权图焦点的邻居都不接收来自焦点的扩散.
                        temp_doi = g.vertex_properties["doi"][each_one]  # 获得邻居顶点对应的doi值.
                        doi_neighbors_list.append(temp_doi)
                        if is_Edge_Attri:
                            if each_one in out_neighbors_each_v:  # 说明each_one是出度邻居.
                                attri_edge = g.edge_properties["weight"][(each_v, each_one)]
                                attri_edge_neighbors_list.append(attri_edge)
                            else:  #
                                attri_edge = g.edge_properties["weight"][(each_one, each_v)]  # 找出这条边(each_one, each_v)的权重,用于后面的计算.
                                attri_edge_neighbors_list.append(attri_edge)
                # TODO:  现在直接乘以权重,权重越大,说明连接越紧密,但是乘以权重之后会扩大.
                if is_Edge_Attri:
                    diffusion_result_list = np.multiply(doi_neighbors_list, attri_edge_neighbors_list)  # 邻居DOI * 边的权重,

                else:
                    diffusion_result_list = doi_neighbors_list
                # print("diffusion_result_list")
                # print(diffusion_result_list)
                if len(diffusion_result_list) > 0:  # 如果邻居数量(排除焦点邻居后)>0
                    max_doi_neighbors = np.max(diffusion_result_list)  # 取出里面最大的.
                    max_doi_neighbors = diffusion_factor * max_doi_neighbors  # 乘以扩散因子.
                    v_doi = g.vertex_properties["doi"][each_v]  # 节点each_v的DOI
                    v_diffusion_doi = np.maximum(v_doi, max_doi_neighbors)
                    v_doi_list.append(v_diffusion_doi)
                else:  # 当前节点只有焦点一个邻居,由于不接收来自焦点的扩散,所以保持原来的值.
                    v_doi = g.vertex_properties["doi"][each_v]  # 节点each_v的DOI
                    v_diffusion_doi = v_doi
                    v_doi_list.append(v_diffusion_doi)

    else:  # 无向图.
        for each_v in g.vertices():  # [0, 1, ...,N-1]
            # fixme: 焦点可以接收来自非焦点邻居的扩散值,这样避免焦点的值比邻居的小太多.
            # node_id_str = nodes_id_list[each_v]  # 取出该节点对应数据库中的字符串类型的id
            # if node_id_str not in focus_id_list:  # 该节点不是焦点.
                neighbors_each_v = g.get_out_neighbors(v=each_v)  # e.g. [1, 2, 3,..]
                doi_neighbors_list = []  # 每个邻居的doi
                attri_edge_neighbors_list = []  # fixme:每个邻居对应的边的权重.
                for each_one in neighbors_each_v:
                    node_id_str_ = nodes_id_list[each_one]  # 取出该节点对应数据库中的字符串类型的id
                    if node_id_str_ not in focus_id_list:  # fixme: 2019-9-30: 目前,无论加权图或非加权图焦点的邻居都不接收来自焦点的扩散.
                        temp_doi = g.vertex_properties["doi"][each_one]  # 获得邻居顶点对应的doi值.
                        doi_neighbors_list.append(temp_doi)
                        if is_Edge_Attri:
                            attri_edge = g.edge_properties["weight"][(each_one, each_v)]  # fixme: 找出这条边(each_one, each_v)的权重,用于后面的计算.注意:对于无向图来说,(each_one, each_v)==(each_v, each_one)
                            attri_edge_neighbors_list.append(attri_edge)
                # TODO:  现在直接乘以权重,权重越大,说明连接越紧密,但是乘以权重之后会扩大.
                if is_Edge_Attri:
                    diffusion_result_list = np.multiply(doi_neighbors_list, attri_edge_neighbors_list)  # fixme:邻居DOI * 边的权重,

                else:
                    diffusion_result_list = doi_neighbors_list
                # print("diffusion_result_list")
                # print(diffusion_result_list)
                if len(diffusion_result_list) > 0:
                    max_doi_neighbors = np.max(diffusion_result_list)  # 取出里面最大的.
                    max_doi_neighbors = diffusion_factor * max_doi_neighbors  # 乘以扩散因子.
                    v_doi = g.vertex_properties["doi"][each_v]  # 节点each_v的DOI
                    v_diffusion_doi = np.maximum(v_doi, max_doi_neighbors)
                    v_doi_list.append(v_diffusion_doi)
                else:  # 当前节点只有焦点一个邻居,由于不接收来自焦点的扩散,所以保持原来的值.
                    v_doi = g.vertex_properties["doi"][each_v]  # 节点each_v的DOI
                    v_diffusion_doi = v_doi
                    v_doi_list.append(v_diffusion_doi)

    # TODO: 对于每个顶点,将扩散后的DOI覆盖原来的DOI.
    for each_v in g.vertices():
        g.vertex_properties["doi"][each_v] = v_doi_list[int(each_v)]


# 测试贪心算法,用于DOI子图的获取.
def test_get_subgraph_with_greedy_algorithm(diffusion_factor):
    """
        第一步: 创建图,准备图数据.
    """
    # print(diffusion_factor)
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

    doi_diffusion(g=g, diffusion_factor=diffusion_factor, is_Edge_Attri=False, directed=False)

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
    F = get_subgraph_with_greedy_algorithm(g=g, focus=focus, total_num_doi_subgraph=total_num_doi_subgraph)
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


# TODO: 对连通的可视化领域的作者合作网络进行随机游走实验
def test_RWR_connected_coauthor_network_visualization(seed_list):
    # 先对其进行布局展示.
    f = open("static/data/connected_max_subgraph_citation_network_visualization.json.txt")  # 可视化领域的作者合作网络.
    # start_time = datetime.datetime.now()
    lines = f.readlines()
    f.close()
    edges_list_with_weight = []
    nodes_set = set()
    for line in lines:
        line = line.strip()
        line = line.split()
        edges_list_with_weight.append((line[0], line[1], 1))  # 带权重. edges_list_with_weight=[(source, target, value, source_name, target_name), ...]
        nodes_set.add((line[0], line[0]))  # (source, name)
        nodes_set.add((line[1], line[1]))  # (target, name)

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
    # TODO: # [node_id1, ...] 图中节点的索引就是这个列表的索引,所以可以根据这个列表,获得对应的节点在数据库表中的id,从而获得该节点的属性信息.

    # wk = Walker(edge_list=edges_list_with_weight, low_list=None, remove_nodes=None)
    # restart_prob = 0.7
    # original_graph_prob = 0.3
    # seed_list = seed_list  # 710233:Kwan-Liu Ma, 1439729:Wei Chen
    # nodes_max_min, probs_max_min = wk.run_exp(seed_list, restart_prob, original_graph_prob)

    # 构造VUE前端需要的graph格式.
    graph = {
        "nodes": [],
        "links": []
    }
    edges_list = edges_list_with_weight  # [(source, target, value), ...]

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
        # prob_node_index = nodes_max_min.index(node)  # 用节点索引获得对应的DOI值.
        # prob_value = probs_max_min[prob_node_index]
        prob_value = 1
        name_ = nodes_name_list[node_idx]
        # name_ = get_author_name_for_node(node_id=node)
        node = {"id": node, "name": name_, "value": prob_value}
        graph["nodes"].append(node)

    return graph


# TODO: 获取焦点间最佳最短路径.
def get_best_short_path_between_focus(g, directed=False, source=None, target=None):
    """
    :param g: graph-tool全局图(flask中初始化的图)
    :param direct: 图的方向性.
    :param source: 启始节点.
    :param target: 结束节点.
    :param directed: 图的方向性.
    :return: 最佳路径,一个列表,e.g. [2, 9, 0, 1],里面是全局图的索引.
    备注: 由于g的边权重体现为边的属性,所以最短路径还是看跳数,也就是说其邻接矩阵表示边的有无,而非权重大小(因为weights=None).
    """
    # all_paths = []  # e.g. [[1, 3, 0, 9], ...]
    # paths_sum_score = []  # 用于存放每条路径的总分.
    if directed:  # 有向图.
        # *********** source -----> source *************#
        """
        对于有向图的策略: 先转化成无向图,选出best_path, 尔后,恢复成有向图.
        """
        g.set_directed(is_directed=False)  # 转换成无向图.
        # all_paths = []  # e.g. [[1, 3, 0, 9], ...]
        # paths_sum_score = []  # 用于存放每条路径的总分.
        # for path in gt.all_shortest_paths(g=g, source=g.vertex(source), target=g.vertex(target), weights=None):
        #     path = list(path)
        #     all_paths.append(path)
        #     sum_doi = 0
        #     for each_v in path:  # TODO: 计算path的分数.
        #         temp_doi_v = g.vertex_properties["doi"][each_v]  # 取出DOI值.each_v是全局图的索引.
        #         sum_doi += temp_doi_v
        #     paths_sum_score.append(sum_doi)
        # if len(paths_sum_score) > 0:
        #     paths_sum_score = np.array(paths_sum_score)  # 转化成数组,便于从中取出最大值.
        #     max_index = paths_sum_score.argmax()  # 获得最大值所在的索引.
        #     best_path = all_paths[max_index]  # 取出最佳路径. [source, X, X, .., target]
        # else:
        #     best_path = []
        # best_path_source_target = best_path
        # *********** target -----> source *************#
        # all_paths = []  # e.g. [[1, 3, 0, 9], ...]
        # paths_sum_score = []  # 用于存放每条路径的总分.
        # for path in gt.all_shortest_paths(g=g, source=g.vertex(target), target=g.vertex(source), weights=None):
        #     path = list(path)
        #     # print("hahahhahaha path")
        #     # print(path)
        #     all_paths.append(path)
        #     sum_doi = 0
        #     for each_v in path:  # TODO: 计算path的分数.
        #         temp_doi_v = g.vertex_properties["doi"][each_v]  # 取出DOI值.each_v是全局图的索引.
        #         sum_doi += temp_doi_v
        #     paths_sum_score.append(sum_doi)
        # if len(paths_sum_score) > 0:
        #     paths_sum_score = np.array(paths_sum_score)  # 转化成数组,便于从中取出最大值.
        #     max_index = paths_sum_score.argmax()  # 获得最大值所在的索引.
        #     best_path = all_paths[max_index]  # 取出最佳路径. [source, X, X, .., target]
        # else:
        #     best_path = []
        # best_path_target_source = best_path
        # best_path = best_path_source_target + best_path_target_source
        all_paths = []  # e.g. [[1, 3, 0, 9], ...]
        paths_sum_score = []  # 用于存放每条路径的总分.
        for path in gt.all_shortest_paths(g=g, source=g.vertex(source), target=g.vertex(target), weights=None):
            path = list(path)
            all_paths.append(path)
            sum_doi = 0
            for each_v in path:  # TODO: 计算path的分数.
                temp_doi_v = g.vertex_properties["doi"][each_v]  # 取出DOI值.each_v是全局图的索引.
                sum_doi += temp_doi_v
            paths_sum_score.append(sum_doi)
        if len(paths_sum_score) > 0:
            paths_sum_score = np.array(paths_sum_score)  # 转化成数组,便于从中取出最大值.
            max_index = paths_sum_score.argmax()  # 获得最大值所在的索引.
            best_path = all_paths[max_index]  # 取出最佳路径. [source, X, X, .., target]
        else:
            best_path = []
        g.set_directed(is_directed=True)  # 恢复成有向图.
        return best_path
    else:  # 无向图
        all_paths = []  # e.g. [[1, 3, 0, 9], ...]
        paths_sum_score = []  # 用于存放每条路径的总分.
        for path in gt.all_shortest_paths(g=g, source=g.vertex(source), target=g.vertex(target), weights=None):
            path = list(path)
            all_paths.append(path)
            sum_doi = 0
            for each_v in path:  # TODO: 计算path的分数.
                temp_doi_v = g.vertex_properties["doi"][each_v]  # 取出DOI值.each_v是全局图的索引.
                sum_doi += temp_doi_v
            paths_sum_score.append(sum_doi)
        if len(paths_sum_score) > 0:
            paths_sum_score = np.array(paths_sum_score)  # 转化成数组,便于从中取出最大值.
            max_index = paths_sum_score.argmax()  # 获得最大值所在的索引.
            best_path = all_paths[max_index]  # 取出最佳路径. [source, X, X, .., target]
        else:
            best_path = []
        return best_path




# 测试最短路径
def test_shortest_path():
    directed = True
    g = gt.Graph(directed=directed)
    N = 11  # 节点数量
    g.add_vertex(n=N)
    edges_list = [(0, 1), (0, 2), (0, 3), (0, 4), (0, 7), (0, 8), (7, 8), (7, 9), (7, 10), (4, 5), (5, 6), (1, 2),
                  (1, 4), (8, 10), (0, 9), (9, 10)]
    g.add_edge_list(edge_list=edges_list)
    source = 0
    target = 6
    all_paths = []
    for path in gt.all_shortest_paths(g, source=g.vertex(source), target=g.vertex(target)):
        all_paths.append(list(path))
    print(all_paths)

    # vlist, elist = gt.shortest_path(g, source=g.vertex(source), target=g.vertex(target))
    #
    # print([str(v) for v in vlist])
    # print([str(e) for e in elist])

    # if directed:  # 有向
    #     pass
    # else:  # 无向.
    #     r = g.get_out_edges(v=4)
    #     e_prop = g.new_edge_property("string")  # {e1:xx, e2: xx, e3: xx, ...}
    #     for i in g.edges():
    #         e_prop[i] = str(i)
    #     g.edge_properties["weight"] = e_prop  # {"weight":{e1:xx, ...}}
    #
    #     print(g.edge_properties["weight"][(10, 9)])
    #
    # n_nb = g.get_out_neighbors(v=5)
    # print("n_nb", n_nb)
    #
    # for each_v in g.vertices():
    #     print(int(each_v))

    pos = gt.sfdp_layout(g)
    gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
                  output_size=(800, 800), output=None)


if __name__ == "__main__":
    def mty(name):
        if name == "jingjing":
            a = "yes"
        else:
            a = "no"
        return a
    r = mty(name="jdingjing")
    print(r)
