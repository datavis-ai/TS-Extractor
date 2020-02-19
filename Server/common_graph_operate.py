# coding: utf-8
import graph_tool.all as gt
import numpy as np
"""
备注: 这个文件用于写对图的基本操作函数.其他文件可以引用这个文件中的函数.
"""


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

    # # graph drawing
    # pos = gt.sfdp_layout(g)
    # gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
    #               output_size=(400, 400), output=None)
    # # graph drawing
    # pos = gt.sfdp_layout(sub)
    # gt.graph_draw(sub, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
    #               output_size=(400, 400), output=None)

    return subgraph_edges_list


# 排序处理函数
def sort_process(name_list, value_list):
    """
    :param name_list: e.g, ["a", "b", "c"]
    :param value_list:与name_list一一对应的值列表[1, 90, 11]
    :return: ["b", "c", "a"], 降序排列输出
    """
    value_array = np.array(value_list)
    result_name_max_min_list = []
    for i in range(len(value_array)):
        max_index = value_array.argmax()
        # print(max_index)
        result_name_max_min_list.append(name_list[max_index])
        value_array[max_index] = -1
    # print(result_name_max_min_list)
    return result_name_max_min_list

if __name__ == "__main__":

    ff = open("txt/jingjing.txt")
    line = ff.readline()
    while line:
        temp_line = line.strip()  # B000001F3P,B000001EEN
        # temp_line = temp_line.split(",")  # [source, target]
        # source = temp_line[0]
        # target = temp_line[1]
        print(temp_line)
        line = ff.readline()
    print("ok")