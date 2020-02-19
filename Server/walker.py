# coding:utf-8
import sys
import numpy as np
import networkx as nx
from sklearn.preprocessing import normalize

# convergence criterion - when vector L1 norm drops below 10^(-6)
CONV_THRESHOLD = 0.000001  # 收敛阈值设置. 10-6
MAX_ITERATION = 50  # 最大迭代次数.


class Walker:
    """ Class for multi-graph walk to convergence, using matrix computation.

    PPR(Personalized PageRank) recursive formula: p_t = (1-r)*W*p_t + r*p_0

    Attributes:
    -----------
        og_matrix (np.array) : The column-normalized adjacency matrix
                               representing the original graph LCC, with no
                               nodes removed

        restart_prob (float) : The probability of restarting from the source
                               node for each step in run_path.
    """

    def __init__(self, edge_list, directed=False):  # remove_nodes=[]
        self._build_matrices(edge_list, directed)

    def run_exp(self, source, restart_prob):  # node_list=[]
        """ Run a multi-graph random walk experiment, and print results.

        Parameters:
        -----------
            source (list):  种子列表   The source node indices (i.e. a list of Entrez
                                  gene IDs)
            restart_prob (float): 跳转概率或重启概率.
        """

        self.restart_prob = restart_prob

        # set up the starting probability vector
        p_0 = self._set_up_p0(source)  # 如果两个种子节点,索引是0 1, 则[1/2, 1/2, 0, ..., 0],即索引0, 1 瓜分了概率,其余节点为0.
        # diff_norm = 1
        # this needs to be a deep copy, since we're reusing p_0 later
        p_t = np.copy(p_0)

        for iteration in range(MAX_ITERATION):
        # while (diff_norm > CONV_THRESHOLD):  # 迭代运行,直到获得小于阈值的结果.
            # first, calculate p^(t + 1) from p^(t)
            # fixme: 更新公式:p(t+1) = (1-r)*W*p(t) + r*p(0), 列标准化的邻接矩阵W,重启概率r.p(0)初始状态,例如(0, 1/2, 1/2, 0, ...,0) 其和为1,种子瓜分概率.
            p_t_1 = self._calculate_next_p(p_t, p_0)

            # calculate L1 norm of difference between p^(t + 1) and p^(t),
            # for checking the convergence condition
            diff_norm = np.linalg.norm(np.subtract(p_t_1, p_t), 1)  # fixme: 计算差值,用于判停.

            # then, set p^(t) = p^(t + 1), and loop again if necessary
            # no deep copy necessary here, we're just renaming p
            p_t = p_t_1  # fixme: 更新p(t)
            if diff_norm <= CONV_THRESHOLD:
                # print("diff_norm <= CONV_THRESHOLD")
                break

        # 上面通过迭代达到稳定状态,然后获得一个额稳定的概率.
        nodes_max_min = []
        probs_max_min = []
        # now, generate and print a rank list from the final prob vector

        for node, prob in self._generate_rank_list(p_t):
            nodes_max_min.append(node)
            probs_max_min.append(prob)

        return nodes_max_min, probs_max_min

    def _generate_prob_list(self, p_t, node_list):
        gene_probs = dict(zip(self.OG.nodes(), p_t.tolist()))
        for node in node_list:
            yield node, gene_probs[node]

    def _generate_rank_list(self, p_t):
        """ Return a rank list, generated from the final probability vector.

        Gene rank list is ordered from highest to lowest probability.
        """
        # gene_probs = zip(self.OG.nodes(), p_t.tolist())  # 原来的列表.
        gene_probs = zip(self.OG.nodes(), p_t)
        # sort by probability (from largest to smallest), and generate a
        # sorted list of Entrez IDs
        for s in sorted(gene_probs, key=lambda x: x[1], reverse=True):
            yield s[0], s[1]

    def _calculate_next_p(self, p_t, p_0):
        """ Calculate the next probability vector. """
        epsilon = np.squeeze(np.asarray(np.dot(self.og_matrix, p_t)))  # self.og_matrix: l1正则化后的邻接矩阵,也就是转移概率矩阵W.更新公式:p(t+1) = (1-r)*W*p(t) + r*p(0)
        no_restart = epsilon * (1 - self.restart_prob)
        restart = p_0 * self.restart_prob
        return np.add(no_restart, restart)

    def _set_up_p0(self, source):  # source种子列表.
        """ Set up and return the 0th probability vector. """
        p_0 = [0] * self.OG.number_of_nodes()  # p_0 = [0, 0, ..., 0]
        prob_value = 1 / float(len(source))
        for source_id in source:  # source: 种子列表, [x, x, ...]
            try:
                # matrix columns are in the same order as nodes in original nx
                # graph, so we can get the index of the source node from the OG
                source_index = list(self.OG.nodes()).index(source_id)  # 原来是这样的:source_index = self.OG.nodes().index(source_id)
                p_0[source_index] = prob_value  # 假设图一共有10个节点,种子有2个,索引是0 3,则得到的p0=[1/2, 0, 1/2, 0,...,0]
            except ValueError:
                sys.exit("Source node {} is not in original graph. Source: {}. Exiting.".format(source_id, source))

        return np.array(p_0)

    def _build_matrices(self, edge_list, directed):
        """ Build column-normalized adjacency matrix for each graph.

        NOTE: these are column-normalized adjacency matrices (not nx
              graphs), used to compute each p-vector
        edge_list: 带权重的边列表.
        """
        original_graph = self._build_og(edge_list, directed)  # original_graph, nx graph.

        self.OG = original_graph  # nx graph
        # print("获得图矩阵...")
        og_not_normalized = nx.to_numpy_matrix(original_graph)  # fixme: 邻接矩阵,矩阵中的元素是权重.因为建立的是一个权重图.
        self.og_matrix = self._normalize_cols(og_not_normalized)  # fixme: 建立的是一个无向的加权图,邻接矩阵A按列正则化,得到的矩阵的列被正则化,列所在元素的和是1.

        """
        例如,归一化后的图为:
            [[ 0.          1.          1.        ]
             [ 0.47368421  0.          0.        ]
             [ 0.52631579  0.          0.        ]]
        """

    def _build_og(self, edge_list, directed=False):  # edge_list=[(1, 2, 3), (), ...]
        """ Build the original graph, without any nodes removed. """
        # if directed:  # fixme:如果有向.
        #     G = nx.DiGraph()  # 无向图,有向图用DiGraph().
        #     G.add_weighted_edges_from(edge_list)  # edge_list=[(1, 2, 3), (), ...]
        # else:
        #     G = nx.Graph()  # 无向图,有向图用DiGraph().
        #     G.add_weighted_edges_from(edge_list)  # edge_list=[(1, 2, 3), (), ...]
        # fixme: 将有向图视为无向图处理.注意: 对于有向图来说,PPR递推公式中的W=邻接矩阵行归一化的转置.
        G = nx.Graph()  # 无向图,有向图用DiGraph().
        G.add_weighted_edges_from(edge_list)  # edge_list=[(1, 2, 3), (), ...]

        return G

    def _normalize_cols(self, matrix):
        """ Normalize the columns of the adjacency matrix """
        """
        p-norm: p正则化,即||x||p = (sum(|x|^p))^(1/p)
        对矩阵每一列做l1正则化,就是将一列中的每个元素除以这一列元素的绝对值之和.
        l2正则化是将一列的每个元素除以这一列每个元素的平方和的平方根.
        当matrix是Numpy矩阵时,copy置成False,避免内存溢出.
        """
        return normalize(matrix, norm='l1', copy=False, axis=0)  # TODO: 当copy=False时,可以运行,明天检查copy对结果的影响.实验结果:copy=Ture/False,不影响列标准化.


if __name__ == "__main__":
    # directed = False
    # seed_list = ["1639", "9846", "10261"]
    # restart_prob = 0.3
    #
    # f = open("max_connected_subgraph_Amazon.txt", "r")
    # lines = f.readlines()
    # f.close()
    # print(len(lines))
    #
    # edges_list_with_weight = []
    # for line in lines:
    #     line = line.strip()
    #     line = line.split(",")  # (source, target)
    #     edges_list_with_weight.append((line[0], line[1], 1))  # 带权重.
    # print("edges_list_with_weight[:10]")
    # print(edges_list_with_weight[:10])
    # '''
    # 1.计算RWR时候4G内存耗尽,应该想办法解决这一块的问题,才能解决大图问题.
    # 2. 图矩阵l1归一化的时候发生了内存耗尽,如果加内存条也不能解决问题,那么就是代码优化的问题了.(2019-5-17)
    #
    #
    # '''
    # wk = Walker(edge_list=edges_list_with_weight, low_list=None, remove_nodes=None, directed=directed)  # todo: 将有向图视为无向图处理.
    # nodes_max_min, probs_max_min = wk.run_exp(source=seed_list, restart_prob=restart_prob)  # fixme: 以"焦点+属性值+关键词"为RWR的起始节点.
    # print("nodes_max_min[:10]")
    # print(nodes_max_min[:10])
    # print(probs_max_min[:10])

    # edge_list = [("A", "B", 6), ("A", "C", 8), ("B", "C", 2)]
    # G = nx.Graph()  # 无向图,有向图用DiGraph().
    # G.add_weighted_edges_from(edge_list)  # edge_list=[(1, 2, 3), (), ...]
    # matrix = nx.to_numpy_matrix(G)  # 这个产生的邻接矩阵的位置一直在变.
    # print("matrix")
    # print(matrix)
    # r = normalize(matrix, norm='l1', copy=False, axis=0)  # 'l1', 'l2', or 'max'
    # print("normalize r")
    # print(r)

    # p_t = [0.5, 0, 0.5]
    # p_t = np.array(p_t)
    # print("p_t")
    # print(p_t)
    # r = np.dot(matrix, p_t)
    # print("r")
    # print(r)
    # epsilon = np.squeeze(np.asarray(np.dot(matrix, p_t)))
    # print("epsilon")
    # print(epsilon)
    # aa = np.array([1, 2, 3])
    # bb = np.array([11, 32, 73])
    # rr = np.add(aa, bb)
    # print(rr)


    # edge_list = [("A", "B", 6), ("A", "C", 8), ("B", "C", 2)]
    # wk = Walker(edge_list=edge_list, low_list=None, remove_nodes=None, directed=False)  # todo: 将有向图视为无向图处理.
    # nodes_max_min, probs_max_min = wk.run_exp(source=["A"], restart_prob=0.3)  # fixme: 以"焦点+属性值+关键词"为RWR的起始节点.
    # print("nodes_max_min")
    # print(nodes_max_min)
    #
    # print("probs_max_min")
    # print(probs_max_min)
    # main()
    import graph_tool.all as gt
    # 用于验证: 当使用属性节点化之后,能将远离焦点的节点赋予大的分数值.
    g = gt.Graph(directed=False)
    """
    1. 单个焦点 + 单个属性值: [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (4, 5, 1), (1, 6, 1), (7, 0, 1), (7, 5, 1), (7, 6, 1)]
    2. 两个焦点 + 两个属性值:[(0, 2, 1), (0, 4, 1), (0, 5, 1), (0, 6, 1), (0, 13, 1), (3, 2, 1), (13, 12, 1), (6, 7, 1),
     (1, 12, 1), (1, 7, 1), (1, 8, 1), (1, 9, 1), (1, 10, 1), (10, 11, 1),
     (14, 3, 1), (14, 0, 1), (15, 1, 1), (15, 11, 1)]             
    3. 单个焦点 + 多个属性值: [(0, 1, 1), (0, 2, 1), (0, 3, 1), (0, 4, 1), (4, 5, 1), (1, 6, 1), (7, 0, 1), (7, 5, 1), (7, 6, 1)]
    """
    edges_list = [(0, 1, 1), (0, 2, 1), (0, 3, 1), (3, 4, 1),
                  ("Vis", 2, 1), ("Vis", 3, 1), ("ML", 2, 1), ("ML", 4, 1)]

    wk = Walker(edge_list=edges_list)
    restart_prob = 0.3
    seed_list = [0, "Vis", "ML"]  # 522311  , 7, 11
    nodes_max_min, probs_max_min = wk.run_exp(seed_list, restart_prob)
    print(nodes_max_min)
    print(probs_max_min)

    total_sum = 0
    for each_one in probs_max_min:
        total_sum += each_one
    print("total_sum")
    print(total_sum)

    """
    原来的:[0.20576030746959784, 0.17215277191689077, 0.17184700245421164, 0.16841055969571259, 0.14081529037491164, 0.093003375557614634, 0.048010692531060557]
    扩散的:[0.20576030746959784, 0.17215277191689077, 0.17184700245421164, 0.17215277191689077, 0.17215277191689077, 0.17184700245421164, 0.04801069253106056]
    """




