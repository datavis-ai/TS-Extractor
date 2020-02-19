"""
Main script for running tissue-specific graph walk experiments, to convergence.

"""
import sys

import graph_tool.all as gt

from walker import Walker


def generate_seed_list(seed_file):
    """ Read seed file into a list. """
    seed_list = []

    try:
        fp = open(seed_file, "r")
    except IOError:
        sys.exit("Error opening file {}".format(seed_file))

    for line in fp.readlines():
        info = line.rstrip().split()
        if len(info) > 1:
            seed_list.append(info[1])
        else:
            seed_list.append(info[0])

    fp.close()
    print("seed_list")
    print(seed_list)
    return seed_list


def get_node_list(node_file):
    node_list = []
    try:
        fp = open(node_file, 'r')
    except IOError:
        sys.exit('Could not open file: {}'.format(node_file))

    # read the first (i.e. largest) connected component
    cur_line = fp.readline()
    while cur_line and not cur_line.isspace():
        if cur_line:
            node_list.append(cur_line.rstrip())
        cur_line = fp.readline()

    fp.close()
    return node_list


def main():

    # run the experiments, and write a rank list to stdout
    edge_list = [("mao", "ting", 0.98), ("mao", "yun", 0.88), ("mao", "jj", 0.99), ("jj", "ting", 0.76)]
    wk = Walker(edge_list=edge_list)
    restart_prob = 0.7
    original_graph_prob = 0.3
    seed_list = ["yun"]  # 522311
    nodes_max_min, probs_max_min = wk.run_exp(seed_list, restart_prob)
    print(nodes_max_min)
    print(probs_max_min)


if __name__ == '__main__':
    # main()
    # 用于验证: 当使用属性节点化之后,能将远离焦点的节点赋予大的分数值.
    g = gt.Graph(directed=False)
    """
    1. 单个焦点 + 单个属性值: [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (4, 5, 1), (1, 6, 1), (7, 0, 1), (7, 5, 1), (7, 6, 1)]
    2. 两个焦点 + 两个属性值:[(0, 2, 1), (0, 4, 1), (0, 5, 1), (0, 6, 1), (0, 13, 1), (3, 2, 1), (13, 12, 1), (6, 7, 1),
     (1, 12, 1), (1, 7, 1), (1, 8, 1), (1, 9, 1), (1, 10, 1), (10, 11, 1),
     (14, 3, 1), (14, 0, 1), (15, 1, 1), (15, 11, 1)]             
    3. 单个焦点 + 多个属性值: [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (4, 5, 1), (1, 6, 1), (7, 0, 1), (7, 5, 1), (7, 6, 1)]
    """
    edges_list = [(0, 1, 1), (0, 2, 1), (1, 2, 1), (2, 3, 1), (1, 3, 1),  # 5
                  (4, 8, 1), (4, 11, 1), (8, 9, 1), (9, 11, 1), (9, 10, 1), (10, 11, 1),  # 6
                  (5, 6, 1), (5, 7, 1), (6, 7, 1),  # 3
                  (0, 5, 1), (4, 5, 1), (3, 4, 1),
                  (12, 8, 1), (12, 0, 1)]   # 3
    node_set = set()  # DOI子图候选集
    for each_one in edges_list:
        node_set.add(each_one[0])
        node_set.add(each_one[1])
    g.add_vertex(n=len(node_set))
    data_type = "fake"
    # edges_list = [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (0, 7, 1), (0, 8, 1), (7, 8, 1), (7, 9, 1), (7, 10, 1), (4, 5, 1), (5, 6, 1), (1, 2, 1),
    #               (1, 4, 1), (6, 0, 1)]  # , (11, 0, 1), (11, 6, 1)
    # edges_list = [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (4, 5, 1), (1, 6, 1), (7, 0, 1), (7, 5, 1), (7, 6, 1)]

    wk = Walker(edge_list=edges_list)
    restart_prob = 0.3
    original_graph_prob = 0.3
    seed_list = [0, 12]  # 522311  , 7, 11
    nodes_max_min, probs_max_min = wk.run_exp(seed_list, restart_prob)
    print(nodes_max_min)
    print(probs_max_min)

    total_sum = 0
    for each_one in probs_max_min:
        total_sum += each_one
    print("total_sum")
    print(total_sum)

    g.add_edge_list(edge_list=edges_list)
    r = gt.pagerank(g)

    # print(r)
    pagerank_list = []
    for ii in r:
        # print(ii)
        pagerank_list.append(ii)
    print("pagerank_list")
    print(pagerank_list)
    print("sum")
    print(sum(pagerank_list))
    pos = gt.sfdp_layout(g)  # 使用胡一凡的sfdp_layout算法,获得节点的坐标.
    gt.graph_draw(g, pos, vertex_text=g.vertex_index, vertex_font_size=18, vertex_size=10, edge_pen_width=1.2,
                  output_size=(800, 800), output=None)

    #[0, 7, 8, 9, 10, 1, 4, 2, 3, 5, 6]
    #[0, 7, 11, 6, 8, 9, 10, 1, 4, 2, 3, 5]
    """
    1. 以0为焦点. 6的值=0.0006622557130004887
    2. 以0为焦点. 添加边(11, 0, 1) + (11, 6, 1), 6的值=0.005519068720294709
    3. 以0 11 为焦点. 6的值=0.05817806202259499
    """
    """
    [0, 3, 4, 1, 2]
    [0.4683474824976549, 0.1681246774451286, 0.1681246774451286, 0.14474299976160407, 0.050660162850483526]
    
    
    """

