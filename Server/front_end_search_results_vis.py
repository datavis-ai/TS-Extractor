# coding: utf-8

import graph_tool.all as gt
from common_graph_operate import extract_subgraph

"""
备注: 用于前端搜索结果的图可视化.
"""


# fixme: 获得前端发送过来的id列表中每个id对应的图节点索引.
def get_subgraph_nodes_index_from_id(subg_id_list=None, nodes_id_list=None, nodes_name_list=None):
    """
    :param subg_id_list: 前端发送过来的id列表. [idx, idx, ....]
    :param nodes_id_list: 其索引与全局图g中节点的索引一一对应. [id0, id1, ...]
    :param nodes_name_list: 与nodes_id_list一一对应的名称.
    :return: subg_nodes_index_list 里面的索引与subg_id_list中的id一一对应, [node_index, node_index, ...] 获得id列表对应的图节点索引,用于后续的子图抽取.
    """
    subg_nodes_index_list = []
    subg_nodes_name_list = []
    for each_id in subg_id_list:  # each_id是str类型的,因为数据库中就是text类型.
        node_index = nodes_id_list.index(each_id)
        subg_nodes_index_list.append(node_index)
        name = nodes_name_list[node_index]
        subg_nodes_name_list.append(name)
    return subg_nodes_index_list, subg_nodes_name_list


def get_sub_graph(g, subg_id_list=None, nodes_id_list=None, nodes_name_list=None, edges_list_with_weight=None, v_API_doi_list=None):
    """
    :param g: graph-tool 全局图.
    :param subg_id_list: 前端发送来的子图列表.
    :param nodes_id_list: 全局图id列表,其索引与全局图g中的节点索引一一对应.
    :param nodes_name_list: 全局图节点名字列表,其索引与全局图g中的节点索引一一对应.
    :param edges_list_with_weight: 全局图的边,其索引与全局图中的边的索引一一对应.
    :param v_API_doi_list: API DOI,全局图g节点的先验DOI值.
    :return: graph,用于前端显示的格式.
    """
    subg_nodes_index_list, subg_nodes_name_list = get_subgraph_nodes_index_from_id(subg_id_list=subg_id_list,
                                                                                   nodes_id_list=nodes_id_list,
                                                                                   nodes_name_list=nodes_name_list)

    subgraph_edges_list = extract_subgraph(g, edges_list_g=edges_list_with_weight, subgraph_nodes_list=subg_nodes_index_list)
    edges_list = subgraph_edges_list  # [(source, target, value), ...]
    nodes_set = set()
    # 构造VUE前端需要的graph格式.
    graph = {
        "nodes": [],
        "links": []
    }
    for edge in edges_list:
        source = edge[0]
        target = edge[1]
        value = edge[2]
        edge = {"source": source, "target": target, "value": value}
        graph["links"].append(edge)
        nodes_set.add(source)
        nodes_set.add(target)
    # if len(nodes_set) == len(subg_id_list):
    """
    备注: 有的节点是孤立节点,并没有边,所以 len(nodes_set) <= len(subg_id_list)
    """
    index_counter = -1
    for node in subg_id_list:  # node是数据库中的id
        index_counter += 1
        name_ = subg_nodes_name_list[index_counter]
        node_idx = subg_nodes_index_list[index_counter]
        node_api_doi_value = v_API_doi_list[node_idx]  # fixme: 节点的value是先验DOI值.
        node = {"id": node, "name": name_, "value": node_api_doi_value}
        graph["nodes"].append(node)
    return graph


if __name__ == "__main__":
    a = [14, 29, 30, 44, 55]
    print(a.index(29))

