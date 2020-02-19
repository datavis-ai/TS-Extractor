# coding: utf-8
from pylab import *  # 时间.
from implementation_doi import compute_API_doi
from operate_db import read_table_edge_from_db_for_change_db


# fixme: 用户数据库切换后,对应的全局图的加载和各种全局变量的初始化.
def change_db(g, directed=False, dbname=None, edges_list_with_weight=None, nodes_id_list=None, nodes_name_list=None, v_API_doi_list=None, max_weight=None):

    start_time = datetime.datetime.now()
    # print("必须先对原来的图以及各种相关的全局列表清零,否则会追加.")
    # fixme: 关键的步骤,必须先对原来的图以及各种相关的全局列表清零,否则会追加.
    g.clear()
    g.reindex_edges()  # fixme: 以前出错是因为索引随着清除次数增加,现在使用reindex_edges()方法可以重新将索引恢复成从0开始.
    edges_list_with_weight.clear()
    nodes_id_list.clear()
    nodes_name_list.clear()
    v_API_doi_list.clear()
    max_weight.clear()

    dbname = dbname
    links_list, max_weight_value = read_table_edge_from_db_for_change_db(dbname=dbname, edges_list_with_weight=edges_list_with_weight, nodes_id_list=nodes_id_list, nodes_name_list=nodes_name_list)
    print("最大权重值")
    print(max_weight_value)
    max_weight.append(max_weight_value)  # 存放最大权重值. max_weight是int类型的.
    g.set_directed(is_directed=directed)  # 设置方向性.
    N = len(nodes_id_list)  # 节点数量
    g.add_vertex(n=N)
    g.add_edge_list(edge_list=links_list)  # fixme:links_list是索引构成的边,格式:[(0, 2), ...],其中索引与nodes_id_list一一对应.
    # fixme: 全局图中节点的索引与nodes_id_list是一一对应的.
    print("图初始化完成")
    end_time = datetime.datetime.now()
    time = (end_time - start_time).seconds
    print("用时: " + str(time) + "秒")
    # fixme: 添加图的边权重属性.
    weight = g.new_edge_property("double")  # {e1:xx, e2: xx, e3: xx, ...}
    g_edges = g.get_edges()
    for edge_with_index in g_edges:  # [source, target, index]
        edge = edge_with_index[:2]  # [source, target]
        index_edge = edge_with_index[2]  # index of edge.
        weight[edge] = edges_list_with_weight[index_edge][2]  # 从edges_list_with_weight里面取得对应边的权重.
    # todo: 边的权重作为边的属性.其用于API的计算 + DOI扩散(可选).
    g.edge_properties["weight"] = weight  # {"weight":{e1:xx, ...}}, 获得对应边的权重: r = g.edge_properties["weight"][edge]

    print("连通图的节点+边数量: ", N, len(links_list))

    # TODO: 先计算节点的API值,现在使用pg值作为API值.
    API_DOI_list = compute_API_doi(g=g, weight=weight)  # 计算pagerank值作为DOI值, API_DOI_list=(xxx, xxx, ....) 对应g图中的节点索引(节点0,节点1,...)
    for each_one in API_DOI_list:  # (x, x, x, ...)
        v_API_doi_list.append(each_one)  # 因为v_API_doi_list是全局变量,所以要使用append().
    # fixme: 添加图的顶点属性.
    v_prop_DOI = g.new_vertex_property("double")  # 给节点添加pagerank属性 specify type of value in dict: {node_index: doube, ...}
    for v in g.vertices():  # g.vertices()里面的节点按照索引排列,即(0, 1, 2, ....N)
        v_prop_DOI[v] = v_API_doi_list[int(v)]  # 赋值 int(v)表示节点的索引, v_doi_list是索引对应的pg值,现在作为DOI值.
    g.vertex_properties["doi"] = v_prop_DOI  # fixme: 先占一个坑,以后就可以直接写或读"doi"的值了,其映射相当于: {"doi": {node1_index: xxx, node2_index: xxx...}}, 将pr值作为每个节点的先验doi属性值,


if __name__ == "__main__":
    a = []

    def test(a):
        for i in [9, 0, 7, 88]:
            a.append(i)

    test(a)
    print(a)














