# coding:utf-8
import graph_tool.all as gt
from common_graph_operate import extract_subgraph
"""
该文件用于实现:
    用户先对图进行结构+属性的探索,对图有了一定的认识之后,用于确定感兴趣的点(焦点).
"""


# fixme: 获得指定节点的n-order邻居子图.
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


if __name__ == "__main__":
    pass