# coding: utf-8
from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
from datetime import datetime
'''
# 通过import graph_init as graph_doi的方式进行图的初始化.
  注意: 对于graph-tool graph, 如果函数中的形参是graph,那么此时不是值传递,而是指针传递.也就是说,在函数里面对图进行更改
就是对原图进行更改.这点好理解,因为graph是一个对象,对象一般都是指针传递的.如果不想因为执行函数而更改原图,可以使用graph的拷贝:graph.copy(),作为形式参数的赋值.
# 目前只考虑无向图.
# 所有能用一个变量控制的给拎出来,然后用一个变量来控制.
# 可以使用graph_tool.stats对图进行统计.
'''
import global_graph_init as graph_doi
from implementation_doi import get_attributes_for_node, \
                               get_neighbors_from_g


from operate_db import get_db_table_fields, \
                       get_db_field_values, \
                       match_db_condition, \
                       get_graph_nodes_atrr_info, \
                       get_data_from_db_table_id, \
                       get_data_from_node_table

from dynamic_construct_attribute_graph import get_subgraph_using_RWR
from global_graph_change import change_db
from operate_graph import get_global_graph_info, \
                          get_global_graph_using_sfdp_layout, \
                          computing_measures_according_to_method
from front_end_search_results_vis import get_sub_graph

# configuration
DEBUG = True

# TODO: 规则:写函数尽量写得扩展性要好,以便于以后适应其他领域的数据.

# 如下实现跨域请求.
app = Flask(__name__)
app.config.from_object(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

"""
用于工程的初始化
"""
# TODO: 数据库名称列表.

# ************************** 正式的Project **************************

# fixme: 前端点击DOI发来请求,向主视图响应graph数据.
@app.route('/mainview/graph', methods=['GET', 'POST'])  # methods=['GET', 'POST'],默认为GET,要这么写才能使用POST.
def mainview():
    '''
    focus: 节点id.
    备注: 以后不管什么数据,都按照这个格式来即可:
         graph={"nodes":[{'id':数据库中的id, 'name':对应作者的名字,作为节点的显示标签, "value": 最后的DOI值}], "links":[{'source':作者的id, 'target':作者的id, 'value': 权重值}]}
         边是根据节点的id来识别并连接的.比如: 1234 5674 2
    '''
    param = json.loads(request.values.get('param'))
    """
    let setInterests = {"setNodes": [{},...], "setKeyword":[xxx, xxx,...]};
    其中,setNodes: [{"id": id,  # id作为唯一标识,
                        "tag": tag, # tag作为节点的标签.
                        "dbname":dbname, # 数据库名称.
                        "field":field, # 数据库表字段.
                        "keyword": keyword, # 关键字.
                        "attributesValue": {field1: xxx, field2: xxx, ...}}, 
                        ...]; 
    """
    set_interests = param["setInterests"]  # 一个兴趣集
    db_name = set_interests["setNodes"][0]["dbname"]
    index_db = graph_doi.db_name_list.index(db_name)
    dbname = "DB/" + db_name
    directed = graph_doi.db_name_directed_list[index_db]
    print("set_interests")
    print(set_interests)

    print("dbname")
    print(dbname)

    scale_extraction_for_single_focus = param["scaleOfSingleFocus"]  # 单焦点抽取时的最大节点数量(对于多个焦点,每个焦点单独用贪心算法抽取出数量不超过该变量的值).

    # todo: 为了便于后续实验, 以下要在前端设计控件控制.
    diffusion_factor = param["diffFactor"]

    UI_factor = param["UI_factor"]
    API_factor = param["API_factor"]  # TODO: 目前API_factor + UI_factor = 1, 是否考虑其和不为1的情况.
    isEdgeAttri = param["isEdgeAttri"]
    probRestart = param["probRestart"]
    weightAttrNode = param["weightAttrNode"]
    # FIXME:下面两个参数用于恢复历史轴廊中缩略图对应的兴趣子图.
    """
     is_click_hist==False, 则 interest_subgraph_node_list == []
     todo: 接下来,把判断false/true
    """
    is_click_hist = param["isClickHist"]  # true/false, 该请求是否由点击前端历史走廊中的缩略图而发送的.
    interest_subgraph_node_list = param["interestSubgraphNodeList"]  # [id0, id1, ...] 缩略图对应的兴趣子图中的所有节点,这样可以保证历史保存的数据与重新计算得到的是同一个子图,只是它们的DOI值有所差别而已.

    print("diffusion_factor")
    print(diffusion_factor)

    print("UI_factor")
    print(UI_factor)

    print("API_factor")
    print(API_factor)

    print("probRestart")
    print(probRestart)

    print("weightAttrNode")
    print(weightAttrNode)
    start_time = datetime.now()
    graph = get_subgraph_using_RWR(
        g=graph_doi.g,
        directed=directed,  # 建模成无向图.
        set_interests=set_interests,  # fixme:每个兴趣集(焦点集)对应一个graph_doi.v_doi_list列表,前端历史走廊中每一张历史图片都有自己的v_doi_list.
        restart_prob=probRestart,
        attri2node_weight=weightAttrNode,
        max_weight=graph_doi.max_weight,
        edges_list_with_weight=graph_doi.edges_list_with_weight,
        dbname=dbname,
        which_table="node",
        nodes_id_list=graph_doi.nodes_id_list,  # 节点索引对应的id.
        nodes_name_list=graph_doi.nodes_name_list,  # 节点索引对应的名称.
        scale_extraction_for_single_focus=scale_extraction_for_single_focus,  # 用于控制每个焦点用贪心算法抽取的最大数量.
        v_API_doi_list=graph_doi.v_API_doi_list,  # 每个节点的API值列表,节点从索引0开始.
        API_factor=API_factor,  # API 因子, 先验分数在总DOI中的比重.
        UI_factor=UI_factor,  # UI 因子,多焦点随机游走在总DOI中的比重.
        v_doi_list=graph_doi.v_doi_list,  # fixme:用于存放扩散后的DOI值.后面的节点扩展需要用到,但是目前只能:前端先点击DOI,计算获得图的DOI,然后依据DOI大小进行扩展.
        is_Edge_Attri_diffusion=isEdgeAttri,  # 扩散函数是否考虑边的属性(权重)
        diffusion_factor=diffusion_factor,  # 扩散函数的扩散因子. 先根据这个公式: DOI=API_factor*API + UI_factor*UI,获得每个点的DOI,然后按照扩散公式对DOI进行扩散.
        stopWords=graph_doi.stopWords,  # 停用词表.
        discard_fields_list=graph_doi.discard_fields_list,  # 不需要考虑的字段列表. 这个保证在焦点不考虑任何属性的情况下,符合要求的关键词作为节点.
        full_compatibility_attr_list=graph_doi.full_compatibility_attr_list,
        node_attributes_type_box=graph_doi.node_attributes_type_box,
        is_click_hist=is_click_hist,
        interest_subgraph_node_list=interest_subgraph_node_list
    )
    end_time = datetime.now()
    time = (end_time - start_time).seconds
    print("Total Time Consumption:", str(time))
    data = {
        "directed": directed,
        "graph": graph
    }
    # TODO: 焦点是id.
    return jsonify(data)


# 发送主视图中的节点的详细信息.
@app.route('/mainview/nodeinfo/<db_name>/<node_id>', methods=['GET', 'POST'])
def mainview_node_info(db_name, node_id):
    db_name = db_name
    node_id = node_id
    table_node_info = get_attributes_for_node(db_name=db_name, node_id=node_id)
    return jsonify(table_node_info)


#  响应主视图发来的扩展请求.
@app.route('/mainview/nodeexpland', methods=['GET', 'POST'])
def mainview_node_expland():  # db_name, node_id
    """
    expland_graph:graph={"nodes":[{'id':数据库中的id, 'name':对应作者的名字,作为节点的显示标签, "value": 最后的DOI值}], "links":[{'source':作者的id, 'target':作者的id, 'value': 权重值}]}
    其以node_id + 其邻居构成的子图. 边是根据节点的id来识别并连接的.比如: 1234 5674 2
    """
    param = json.loads(request.values.get('param'))
    db_name = param["dbName"]
    node_id = param["nodeId"]
    interest_subgraph_id_list = param["interestSubgraphId"]  # [id1, id2, ...]
    num_neighbors = param["numNeighbors"]  # 节点的数量.
    print("num_neighbors")
    print(num_neighbors)
    index_db = graph_doi.db_name_list.index(db_name)
    directed = graph_doi.db_name_directed_list[index_db]
    # fixme: 需要获得节点对应的数据库名称.
    expland_graph = get_neighbors_from_g(g=graph_doi.g,
                                         node_id=node_id,
                                         nodes_id_list=graph_doi.nodes_id_list,
                                         edges_list_with_weight=graph_doi.edges_list_with_weight,
                                         v_doi_list=graph_doi.v_doi_list,
                                         nodes_name_list=graph_doi.nodes_name_list,
                                         directed=directed,
                                         interest_subgraph_id_list=interest_subgraph_id_list,
                                         num_neighbors=num_neighbors
                                         )  # todo: 这里暂时写成False.
    print("expland_graph")
    print(expland_graph)
    return jsonify(expland_graph)


# fixme: 前端created钩子函数发来请求,响应已存在的数据库选项.
@app.route('/infosearch/selectdb', methods=['GET', 'POST'])
def select_db_for_search():
    data = {}
    db_data = []
    counter = -1
    for i in graph_doi.db_name_list:
        counter = counter + 1
        directed = graph_doi.db_name_directed_list[counter]
        temp_obj = {"label": i, "value": i, "directed": directed}
        db_data.append(temp_obj)
    """    
      [{   label:"mty",
         value:'mty'
      }],
      
    """
    print("将所有数据库名称传到前端")
    print(db_data)
    data["dbname"] = db_data
    data["discardfield"] = graph_doi.discard_fields_list
    data["fullCompatibilityAttr"] = graph_doi.full_compatibility_attr_list
    data["stopword"] = graph_doi.stopWords

    return jsonify(data)


# fixme: 前端选中一个数据库,响应该数据库对应的node表的所有字段.(目前本界面的第一个操作,如果不直接点击历史图片的话.)
@app.route('/infosearch/getdbfields/<db_name>', methods=['GET', 'POST'])
def db_fields_for_search(db_name):
    db_name = db_name
    index_db = graph_doi.db_name_list.index(db_name)
    dbname = "DB/" + db_name
    directed = graph_doi.db_name_directed_list[index_db]
    # fixme: 更换数据库,更新全局图.
    change_db(
        g=graph_doi.g,
        directed=directed,
        dbname=dbname,
        edges_list_with_weight=graph_doi.edges_list_with_weight,
        nodes_id_list=graph_doi.nodes_id_list,
        nodes_name_list=graph_doi.nodes_name_list,
        v_API_doi_list=graph_doi.v_API_doi_list,
        max_weight=graph_doi.max_weight
    )
    # todo:根据数据库表的不同,自己定义,以后扩展的话,可以在前端,或者后台的命令中指明数据库名称 + 存放节点属性的表格名称.
    fields_list, fields_type_list, db_tables_list = get_db_table_fields(dbname=dbname, table_name="node")  # ['id', 'name', 'institution', 'num_papers', 'num_citation', 'H_index', 'P_index', 'UP_index', 'interests']
    # data = [{"label": "all_fields", "value": "all_fields"}]
    # todo: 更新node_attributes_type_box.
    graph_doi.node_attributes_type_box.clear()  # 先清除旧的内容
    graph_doi.node_attributes_type_box.append(fields_type_list)  # [{name: "text", H_index: "integer"}]

    num_node = len(graph_doi.nodes_id_list)  # 节点数量.
    data = {"fields": [], "fieldstype": fields_type_list, "dbtables": db_tables_list, "numNodes": num_node}
    for i in fields_list:
        temp_obj = {"label": i, "value": i}
        data["fields"].append(temp_obj)
    """
     [{  label:"mty",
        value:'mty'
     }]
    """
    return jsonify(data)


# fixme: 前端选中一个字段,响应该该字段对应的所有取值的集合(按照一定的规则排列)
# todo:排列规则可以再考虑考虑.
@app.route('/infosearch/getdbfieldsvalues', methods=['GET', 'POST'])
def db_fields_values_for_search():
    param = json.loads(request.values.get('param'))
    db_name = param["dbName"]
    field = param["field"]
    dbname = "DB/" + db_name
    data = get_db_field_values(dbname=dbname, field=field)
    # TODO: 原来jsonify(data)无法将data转化成字符串格式,原因:data中每个对象的"number"键的值取之与数组,改成列表后就可以了.
    # [{"value": XXX, "number": XXX}, ...], 如果是字符串类型, 按照出现次数降序排列, 数值类型, 则按照大小降序排列.
    return jsonify(data)


# fixme:响应点击Search按钮,发送匹配的表格数据(匹配的节点).
@app.route('/infosearch/resultssearch', methods=['GET', 'POST'])
def resultssearch():
    '''
    请求发来查询条件,根据查询条件匹配数据库.将匹配的数据按照前端要求的格式响应给前端.
    '''
    param = json.loads(request.values.get('param'))
    """
    let param = {"dbName": this_.selectiondb, "dbfield": this_.selectionfield, "dbfieldvalue": this_.nodeinfo, "focus": this_.nodeinfo, "nodenum": this_.nodenum};
    dbName, dbfield, dbfieldvalue
    """
    dbName = "DB/" + param["dbName"]  # 数据库名称.
    conditions = param["conditions"]  # [{}, ...]
    # TODO: 可以统计字符数量,自适应地变更表格宽度.
    table_width = "125"  # 表格单元格宽度
    which_table = "node"
    tableheader, tabledata = match_db_condition(dbName=dbName, which_table=which_table, conditions=conditions, table_width=table_width)
    data = {"tableheader": tableheader, "tabledata": tabledata}
    return jsonify(data)


# fixme: 获得全局图的统计信息.用于前端显示.
@app.route('/networkInformationView/getglobalinfo', methods=['GET', 'POST'])
def get_global_info():
    global_graph_info = get_global_graph_info(graph_doi.g)
    return jsonify(global_graph_info)


# fixme: 获得前端主视图中节点的属性信息.
@app.route('/mainview/graphnodesattri', methods=['GET', 'POST'])
def graph_nodes_attri():
    param = json.loads(request.values.get('param'))
    graph_nodes = param["graphNodeData"]  # 格式:[{id:x, name:x, value:x}, ...]
    doi_node_attr = param["doiNodeAttr"]  # [xxx, xxx, ...]
    dbName = "DB/" + param["dbName"]  # 数据库名称.
    which_table = "node"  # 从node表格中获取数据.
    node_attr_obj = get_graph_nodes_atrr_info(dbname=dbName, which_table=which_table, graph_nodes=graph_nodes, doi_node_attr=doi_node_attr)
    return jsonify(node_attr_obj)


# fixme: 前端点击节点细节,点击提示的字段查看更多(see more, 实际上,字段的名称就是数据库表,这样才能方便扩展).
@app.route('/mainview/nodedetails/seemore', methods=['GET', 'POST'])
def node_details_see_more():

    param = json.loads(request.values.get('param'))
    dbName = "DB/" + param["dbName"]  # "xxx.db"
    tableName = param["tableName"]  # "publications"
    value = param["value"]  # "id1;id2;id3;id4" text
    value = value.strip()  # 去掉前后的空格或回车.
    value = value.split(";")  # [x, x, ...]
    idList = []
    for each_id in value:
        each_id = each_id.strip()
        idList.append(each_id)
    ids_records_obj = get_data_from_db_table_id(dbname=dbName, which_table=tableName, id_list=idList)
    return jsonify(ids_records_obj)


# fixme: 前端点击边,弹出边信息窗口,显示边的信息.
@app.route('/mainview/edgedetails/<db_name>/<source_id>/<target_id>/<weight>', methods=['GET', 'POST'])
def see_edge_details(db_name, source_id, target_id, weight):
    dbName = "DB/" +db_name  # "xxx.db"
    which_table = "node"
    co_publications_list = get_data_from_node_table(dbName, which_table, source_id, target_id)
    if len(co_publications_list) >= int(weight):
        print("The number of publications: " + str(len(co_publications_list)))
        ids_records_obj = get_data_from_db_table_id(dbname=dbName, which_table="publications", id_list=co_publications_list)
        return jsonify(ids_records_obj)
    else:
        print("No co-publication")
        return jsonify({})


# fixme: 前端点击查看搜索结果的可视化图.
@app.route('/resultsSearchView/getSearchResultGraph', methods=['GET', 'POST'])
def get_search_result_graph():
    param = json.loads(request.values.get('param'))
    subg_id_list = param["resultNodesList"]  # [id0, ...]
    db_name = param["dbName"]  # "xxx.db"
    index_db = graph_doi.db_name_list.index(db_name)
    directed = graph_doi.db_name_directed_list[index_db]  # 图数据的方向性.
    graph = get_sub_graph(g=graph_doi.g,
                          subg_id_list=subg_id_list,
                          nodes_id_list=graph_doi.nodes_id_list,
                          nodes_name_list=graph_doi.nodes_name_list,
                          edges_list_with_weight=graph_doi.edges_list_with_weight,
                          v_API_doi_list=graph_doi.v_API_doi_list)
    data = {"graph": graph, "directed": directed}
    return jsonify(data)


# fixme: 前端请求布局好的全局图数据.
@app.route('/globalGraphView/globalGraphLayout/<db_name>', methods=['GET', 'POST'])
def get_global_graph_layout(db_name):

    dbname = db_name  # "xxx.db"
    index_db = graph_doi.db_name_list.index(dbname)
    directed = graph_doi.db_name_directed_list[index_db]  # 图数据的方向性.
    # 先判断是否存在文件.
    file_name = "json/graph/" + dbname.strip().split(".")[0] + ".json"
    is_exist_file = os.path.exists(file_name)
    print(is_exist_file)

    if is_exist_file:  # 如果存在,则直接从路径中获取.
        with open(file_name, 'r') as load_f:
            graph = json.load(load_f)
            print("已经发送 graph json")
        return jsonify(graph)

    else:  # 如果不存在,则先布局.
        dbname = "DB/" + dbname  # 数据库间所在路径
        directed = directed  # 图的方向性.
        which_table = "edge"  # 从数据库中的edge表获得图数据.
        json_file_path = "json/graph"  # 布局好的布局数据存放的路径.
        graph = get_global_graph_using_sfdp_layout(dbname=dbname, directed=directed, which_table=which_table, json_file_path=json_file_path)
        return jsonify(graph)


# fixme: 根据前端用套索过滤出来的数据获得对应的子图.
@app.route("/globalFilteredSubgraphView/getFilteredSubGraph", methods=['GET', 'POST'])
def get_filtered_subgraph():
    param = json.loads(request.values.get('param'))
    selected_nodes_list = param["selectedNodesList"]  # [{x:xx, y:xx, id:xx}, ...]
    subg_id_list = []  # [id0, id1, ...]
    for each_node in selected_nodes_list:  # each_node = {x:xx, y:xx, id:xx}
        node_id = each_node["id"]
        subg_id_list.append(node_id)
    db_name = param["dbName"]  # [{x:x, y:x, id:x}, ...]
    index_db = graph_doi.db_name_list.index(db_name)
    directed = graph_doi.db_name_directed_list[index_db]  # 图数据的方向性.
    graph = get_sub_graph(g=graph_doi.g,
                          subg_id_list=subg_id_list,
                          nodes_id_list=graph_doi.nodes_id_list,
                          nodes_name_list=graph_doi.nodes_name_list,
                          edges_list_with_weight=graph_doi.edges_list_with_weight,
                          v_API_doi_list=graph_doi.v_API_doi_list)
    data = {"graph": graph, "directed": directed}
    return jsonify(data)


# fixme: 前端焦点选择面板,选择对应算法计算获得Topn节点.
@app.route("/focusNodesSelection/structureFuture/<db_name>/<method>/<top_n>", methods=['GET', 'POST'])
def get_top_n_nodes_according_to_measures(db_name, method, top_n):
    print("请求ranking list")
    which_method = method  # [{x:xx, y:xx, id:xx}, ...]
    print(which_method)
    top_n = top_n
    index_db = graph_doi.db_name_list.index(db_name)
    directed = graph_doi.db_name_directed_list[index_db]  # 图数据的方向性.
    db_name = "DB/" + db_name  # "xxx.db"
    tableheader, tabledata = computing_measures_according_to_method(db_name=db_name, g=graph_doi.g, directed=directed, v_API_doi_list=graph_doi.v_API_doi_list, nodes_id_list=graph_doi.nodes_id_list, which_method=which_method, top_n=top_n, table_width="120")
    data = {"tableheader": tableheader, "tabledata": tabledata}
    return jsonify(data)


if __name__ == "__main__":
    # 备注: python+flask 作为后台,vue作为前端的请求-响应通信测试, 2018-8-20
    app.run(port=5050, debug=True)  # debug模式,当你更改代码保存后会自动重新解释.可想而知,全局变量会重新初始化一次.

    """
    解决端口被占用:
    端口查询:netstat -anp|grep 5050
    端口关闭: kill -9 PID号
    """
    """
    前端节点配色: (蓝, #1890ff) (#109618 绿) (#FF8700 橙)
    context-menu-icon-copy
    """
    """
    当出现未发现scipy模块时的解决方案: sudo apt install --reinstall python*-decorator
    """





