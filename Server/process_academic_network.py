# coding: utf-8
import sqlite3
from datetime import datetime
import json
import networkx as nx


# 以下创建一个数据库+四张表
# 创建作者表
def create_author_table():
    # # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/AcademicNetwork.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()

    # 写sql语言,执行,创建作者表格. 注意:表格的字段不能命名为index,命名为id就可以了.
    author_sql = '''create table author (    
               id             int,
               name           text,
               institution    text,
               num_papers     int,
               num_citation   int,
               H_index        int,
               P_index        real,
               UP_index       real,
               interests      text
            )'''
    cursor.execute(author_sql)
    print("author created successfully")
    cursor.close()

    db.close()  # 关闭数据库


# 创建论文表
def create_paper_table():
    # # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/AcademicNetwork.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()

    # 写sql语言,执行,创建作者表格. 注意:表格的字段不能命名为index,命名为id就可以了.
    author_sql = '''create table paper (    
                   id             int,
                   title          text,
                   authors        text,
                   institution    text,
                   year           text,
                   public_venue   text,
                   id_reference   text,
                   abstract       text              

                )'''
    cursor.execute(author_sql)
    print("author created successfully")
    cursor.close()
    db.close()  # 关闭数据库


# 创建合作作者表
def create_coauthor_table():
    # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/AcademicNetwork.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()

    # 写sql语言,执行,创建作者表格. 注意:表格的字段不能命名为index,命名为id就可以了.
    author_sql = '''create table coauthor (    
                   source         int,
                   target         int,
                   num_papers     int                            

                )'''
    cursor.execute(author_sql)
    print("author created successfully")
    cursor.close()
    db.close()  # 关闭数据库


# 创建作者-论文表
def create_author2paper_table():
    # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/AcademicNetwork.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()

    # 写sql语言,执行,创建作者表格. 注意:表格的字段不能命名为index,命名为id就可以了.
    author_sql = '''create table author2paper (    
                    id         int,
                    id_author  int,
                    id_paper   int,
                    position_author int                            

                )'''
    cursor.execute(author_sql)
    print("author created successfully")
    cursor.close()
    db.close()  # 关闭数据库


############################################################################


# 以下往数据库中各个表写对应的数据
def write_author_table():
    start_time = datetime.now()
    with open("DB/AMiner-Author.txt", "r") as f:
        lines = f.readlines()
        all_authors = []

        for i in range(1712433):  # 共有1712433个作者.
            obj = {}
            all_authors.append(obj)
        index_count = 0  # all_authors的索引
        for line in lines:
            line = line.strip()
            line = line.split()
            # print(line)
            if line.__len__() > 0:
                if line[0] == "#index":

                    valid_str = ''
                    for each_one in line[1:]:
                        valid_str += each_one + " "
                    valid_str = valid_str.strip()  # valid_str是有效的字符串
                    if valid_str == "":
                        valid_str = "NULL"
                    # print("valid_str")
                    # print(valid_str)
                    index_count = int(valid_str) - 1
                    # print(index_count)
                    all_authors[index_count]["id"] = valid_str
                else:
                    # print("index_count")
                    # print(index_count)
                    valid_str = ''
                    for each_one in line[1:]:
                        valid_str += each_one + " "
                    valid_str = valid_str.strip()  # valid_str是有效的字符串
                    if valid_str == "":
                        valid_str = "NULL"
                    # 以下对号入座,避免了多行的情况.
                    if line[0] == "#n":
                        all_authors[index_count]["name"] = valid_str
                    if line[0] == "#a":
                        all_authors[index_count]["institution"] = valid_str
                    if line[0] == "#pc":
                        all_authors[index_count]["num_papers"] = valid_str
                    if line[0] == "#cn":
                        all_authors[index_count]["num_citation"] = valid_str
                    if line[0] == "#hi":
                        all_authors[index_count]["H_index"] = valid_str
                    if line[0] == "#pi":
                        all_authors[index_count]["P_index"] = valid_str
                    if line[0] == "#upi":
                        all_authors[index_count]["UP_index"] = valid_str
                    if line[0] == "#t":
                        all_authors[index_count]["interests"] = valid_str

        # print(all_authors[:3])

        dbname = "DB/AcademicNetwork.db"
        db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

        print("Opened database successfully")

        # 创建数据库中的游标对象
        cursor = db.cursor()

        for row in all_authors:  # row是字典{}

            cursor.execute('''insert into author (id, name, institution, num_papers, num_citation, H_index, P_index, UP_index, interests)
                            VALUES (?,?,?,?,?,?,?,?,?)''',
                           (row["id"], row["name"], row["institution"], row["num_papers"], row["num_citation"],
                            row["H_index"], row["P_index"], row["UP_index"], row["interests"]))

        db.commit()  # 必须提交事务，否则无法写入表格
        db.close()

        end_time = datetime.now()
        time = (end_time - start_time).seconds
        print("用时:")
        print(time)


# 将论文信息写入表中
def write_paper_table():
    start_time = datetime.now()
    with open("DB/AMiner-Paper.txt", "r") as f:
        lines = f.readlines()
        all_authors = []

        for i in range(2092356):  # 共有2,092,356篇论文.
            obj = {
                "id": '',
                "title": '',
                "authors": '',
                "institution": '',
                "year": '',
                "public_venue": '',
                "id_reference": [],
                "abstract": ''
            }
            all_authors.append(obj)
        index_count = 0  # all_authors的索引
        for line in lines:
            line = line.strip()
            line = line.split()
            # print(line)
            if line.__len__() > 0:
                if line[0] == "#index":

                    valid_str = ''
                    for each_one in line[1:]:
                        valid_str += each_one + " "
                    valid_str = valid_str.strip()  # valid_str是有效的字符串
                    if valid_str == "":
                        valid_str = "NULL"
                    # print("valid_str")
                    # print(valid_str)
                    index_count = int(valid_str) - 1
                    # print(index_count)
                    all_authors[index_count]["id"] = valid_str
                else:
                    # print("index_count")
                    # print(index_count)
                    valid_str = ''
                    for each_one in line[1:]:
                        valid_str += each_one + " "
                    valid_str = valid_str.strip()  # valid_str是有效的字符串
                    if valid_str == "":
                        valid_str = "NULL"
                    # 以下对号入座,避免了多行的情况.
                    if line[0] == "#*":
                        all_authors[index_count]["title"] = valid_str
                    if line[0] == "#@":
                        all_authors[index_count]["authors"] = valid_str
                    if line[0] == "#o":
                        all_authors[index_count]["institution"] = valid_str
                    if line[0] == "#t":
                        all_authors[index_count]["year"] = valid_str
                    if line[0] == "#c":
                        all_authors[index_count]["public_venue"] = valid_str
                    if line[0] == "#%":
                        all_authors[index_count]["id_reference"].append(valid_str)
                    if line[0] == "#!":
                        all_authors[index_count]["abstract"] = valid_str
        # print(all_authors)

        dbname = "DB/AcademicNetwork.db"
        db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

        print("Opened database successfully")

        # 创建数据库中的游标对象
        cursor = db.cursor()
        # count = 0
        for row in all_authors:  # row是字典{}
            # count += 1
            # print(count)
            reference_str = ""
            if row["id_reference"].__len__() > 0:  # if not empty.

                for i in row["id_reference"]:
                    reference_str += i + ";"
                reference_str = reference_str.strip(";")

            cursor.execute('''insert into paper (id, title, authors, institution, year, public_venue, id_reference, abstract)
                                    VALUES (?,?,?,?,?,?,?,?)''',
                           (row["id"], row["title"], row["authors"], row["institution"], row["year"],
                            row["public_venue"], reference_str, row["abstract"]))

        db.commit()  # 必须提交事务，否则无法写入表格
        db.close()
        '''
                   id             int,
                   title          text,
                   authors        text,
                   institution    text,
                   year           text,
                   public_venue   text,
                   id_reference   text,
                   abstract       text
        '''
        end_time = datetime.now()
        time = (end_time - start_time).seconds
        print("用时:")
        print(time)


# 将共同合作作者写入
def write_coauthor_table():
    start_time = datetime.now()
    with open("DB/AMiner-Coauthor.txt", "r") as f:
        lines = f.readlines()
        edges = []
        for line in lines:
            line = line.strip()
            line = line.split("#")
            line = line[1]
            line = line.strip()
            line = line.split()
            # print(line)
            edges.append(line)
        # print(edges)

        dbname = "DB/AcademicNetwork.db"
        db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

        print("Opened database successfully")

        # 创建数据库中的游标对象
        cursor = db.cursor()
        for row in edges:  # row是字典[]

            cursor.execute('''insert into coauthor (source, target, num_papers)
                              VALUES (?,?,?)''',
                           (row[0], row[1], row[2]))

        db.commit()  # 必须提交事务，否则无法写入表格
        db.close()
        '''
                   source         int,
                   target         int,
                   num_papers     int 
        '''
        end_time = datetime.now()
        time = (end_time - start_time).seconds
        print("用时:")
        print(time)


# 将作者-论文写入author2paper表
def write_author2paper_table():
    start_time = datetime.now()
    with open("DB/AMiner-Author2Paper.txt", "r") as f:
        lines = f.readlines()
        edges = []
        for line in lines:
            line = line.strip()
            line = line.split()
            edges.append(line)
        # print(edges)
        dbname = "AcademicNetwork.db"
        db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

        print("Opened database successfully")

        # 创建数据库中的游标对象
        cursor = db.cursor()
        for row in edges:  # row是字典[]

            cursor.execute('''insert into author2paper (id, id_author, id_paper, position_author)
                              VALUES (?,?,?,?)''',
                           (row[0], row[1], row[2], row[3]))

        db.commit()  # 必须提交事务，否则无法写入表格
        db.close()
        '''
                    id         int,
                    id_author  int,
                    id_paper   int,
                    position_author int
        '''
        end_time = datetime.now()
        time = (end_time - start_time).seconds
        print("用时:")
        print(time)


#########################################################################################


# 下面抽取可视化领域的学术网络.
def extract_papers_visualization():
    dbname = "DB/AcademicNetwork.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()
    venue = "%computer graphics forum%"
    """
    备注:
    1. SQlite3 的like子句使用, 百分号(%)代表零个,一个或多个数字或字符.下划线(_)代表一个单一的数字或字符.这些符号可以被组合使用.
    2. e.g. %information visualization% 将获得 Proceedings of the 1998 workshop on New paradigms in information visualization and manipulation
    3. 查询字符不区分大小写.
    """
    cursor.execute("select title, year, public_venue from paper where public_venue like ?", (venue,))
    """
                   id             int,
                   title          text,
                   authors        text,
                   institution    text,
                   year           text,
                   public_venue   text,
                   id_reference   text,
                   abstract       text 
    """
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果
    print("论文数量:")
    print(len(data))

    for paper in data[:10]:
        print(paper)

    db.close()  # 关闭数据库

    """
    可视化领域的期刊会议:
    1. TVCG: IEEE Transactions on Visualization and Computer Graphics
    2. IEEE Vis:In Proceedings of the IEEE Conference on Visualization
       inforvis: In IEEE Symposium on Information Visualization/IEEE Information Visualization
       scivis:
       VAST: IEEE Conference on Visual Analytics Science and Technology
    3. Pacificvis:
       IEEE Pacific Visualization Symposium
    4. EuroVis:
       Eurographics Conference on Visualization
    5. computer graphics forum
    6. Journal of Visualization
    7. IEEE Computer Graphics and Applications
    8. Information Visualization

    """


############################以下处理论文引用网络###################################


# 创建citation表
def create_citation_v10_table():
    # # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/Citation.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()
    # 备注: 为了方便后续处理没有数据的情况,所有的字段类型都是text,尤其是n_citation.
    # 写sql语言,执行,创建作者表格. 注意:表格的字段不能命名为references,命名为reference就可以了.
    citation_sql = '''create table citation (    
                   id             text,
                   title          text,
                   authors        text,              
                   public_venue   text,
                   year           text,
                   n_citation     text,
                   reference      text,
                   abstract       text
                )'''
    cursor.execute(citation_sql)
    print("citation created successfully")
    cursor.close()
    db.close()  # 关闭数据库


# 将数据写入数据库表
def write_citation_v10_table():
    dbname = "DB/Citation.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()
    start_time = datetime.now()
    for num in range(4):
        print("正在处理:")
        print("dblp-ref-" + str(num) + ".json")
        with open("dblp_citation_v10/dblp-ref-" + str(num) + ".json", encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                # print(type(line))
                obj = json.loads(line)
                # 如果没有abstract,则添加一个空的.
                if "abstract" not in obj.keys():
                    abstract = "NULL"
                else:
                    abstract = obj["abstract"]

                if "venue" not in obj.keys():
                    venue = "NULL"
                else:
                    venue = obj["venue"]

                if "title" not in obj.keys():
                    title = "NULL"
                else:
                    title = obj["title"]

                if "year" not in obj.keys():
                    year = "NULL"
                else:
                    year = obj["year"]

                if "n_citation" not in obj.keys():
                    n_citation = "NULL"
                else:
                    n_citation = obj["n_citation"]

                if "authors" not in obj.keys():
                    authors = "NULL"
                else:
                    authors = ''
                    for i in obj["authors"]:
                        authors += i + ";"
                    authors = authors.strip(";")

                if "references" not in obj.keys():
                    references = "NULL"
                else:
                    references = ''
                    for i in obj["references"]:
                        references += i + ";"
                    references = references.strip(";")

                cursor.execute('''insert into citation (id, title, authors,public_venue,year,n_citation,reference,abstract)
                                              VALUES (?,?,?,?,?,?,?,?)''',
                               (obj["id"], title, authors, venue, year, n_citation, references, abstract))
            """
                       id             text,
                       title          text,
                       authors        text,              
                       public_venue   text,
                       year           text,
                       n_citation     text,
                       reference      text,
                       abstract       text
            """
            db.commit()  # 必须提交事务，否则无法写入表格
    db.close()
    end_time = datetime.now()
    time = (end_time - start_time).seconds
    print("用时:")
    print(time)


# **************************************************************************************************************
# 以下创建可视化领域的引用网络:节点=论文, 边: source, target.
# ****************************************************************************************************************


# 创建可视化领域的表,存放可视化领域的论文信息.
def create_visualization_citation_table():
    # # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/Citation_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()
    # 备注: 为了方便后续处理没有数据的情况,所有的字段类型都是text,尤其是n_citation.
    # 写sql语言,执行,创建作者表格. 注意:表格的字段不能命名为references,命名为reference就可以了.
    citation_sql = '''create table papers (    
                   id             text,
                   title          text,
                   authors        text,              
                   public_venue   text,
                   year           text,
                   n_citation     text,
                   reference      text,
                   abstract       text
                )'''
    cursor.execute(citation_sql)
    print("citation created successfully")
    cursor.close()
    db.close()  # 关闭数据库


#  查询引用表格,抽取出某几个领域的论文.
def query_citation_v10_table():
    dbname = "DB/Citation.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()
    # venue_str1 = "%Pacific%visualization%"
    # venue_str2 = "%visualization%Pacific%"
    publication_venue = [
        "IEEE Transactions on Visualization and Computer Graphics",
        "computer graphics forum",
        "Journal of Visualization",
        "Information Visualization",
        "Journal of Graph Algorithms and Applications",
        "Graph Drawing",
        "Journal of Visual Languages and Computing",
        "IEEE Computer Graphics and Applications"
    ]

    visualization_papers = []  # 用于存放可视化领域的论文.
    visualization_papers_set = set()  # 去掉重复的论文.
    num_counter = 0
    for each_venue in publication_venue:
        venue = each_venue
        """
        备注:
        1. SQlite3 的like子句使用, 百分号(%)代表零个,一个或多个数字或字符.下划线(_)代表一个单一的数字或字符.这些符号可以被组合使用.
        2. e.g. %information visualization% 将获得 Proceedings of the 1998 workshop on New paradigms in information visualization and manipulation
        3. 查询字符不区分大小写.
        """
        # cursor.execute("select public_venue from citation where public_venue like ?", (venue,))
        cursor.execute(
            "select id, title, authors, public_venue, year, n_citation, reference, abstract from citation where public_venue like ?",
            (venue,))

        """            id             text,
                       title          text,
                       authors        text,              
                       public_venue   text,
                       year           text,
                       n_citation     text,
                       reference      text,
                       abstract       text
        """
        data = cursor.fetchall()  # 使用这种方式取出所有查询结果
        print(venue + "的论文数量:")
        temp_num = len(data)
        num_counter += temp_num
        print(temp_num)

        for each_one in data:  # each_one是元组而非列表.
            visualization_papers.append(each_one)
            visualization_papers_set.add(each_one)

    print("论文总数:")
    print(len(visualization_papers))
    print(num_counter)
    print("去重之后论文数量:")
    print(len(visualization_papers_set))
    db.close()  # 关闭数据库
    return visualization_papers_set  # [[], [],...[]]


"""
可视化领域的期刊会议:
期刊:
  1. TVCG: IEEE Transactions on Visualization and Computer Graphics 2668
  2. computer graphics forum 3016
  3. %Journal of Visualization% 1045, 这包含了:Journal of Visualization and Computer Animation等这样的期刊.
  4. Information Visualization(IV)683
  5. Journal of Graph Algorithms and Applications(GA&A)
  6. IEEE Computer Graphics and Applications(CG&A)
会议:
  1. IEEE Pacific Visualization Symposium (PacificVis) 
  2. IEEE Symposium on Information Visualization (InfoVis)(since 2006)
  3. International Conference on Information Visualisation(IV)
  4. Joint Eurographics–IEEE VGTC Symposium on Visualization (EuroVis) [1999–2004: VisSym; since 2008 a special
    issue of Computer Graphics Forum]
  5. Symposium on Graph Drawing(GD), 使用Graph Drawing才能搜索到.
  6. IEEE Symposium on Information Visualization(infovis)
能搜出结果的期刊和会议:
  1. TVCG: IEEE Transactions on Visualization and Computer Graphics  2668
  2. computer graphics forum  3016
  3. %Journal of Visualization%  1045, 这包含了:Journal of Visualization and Computer Animation等这样的期刊.
     其中,Journal of Visualization 有812
  4. Information Visualization  683
  5. Journal of Graph Algorithms and Applications(GA&A)  305
  6. Graph Drawing  909
  7. Journal of Visual Languages and Computing  661
  8. IEEE Computer Graphics and Applications(CG&A)  2268
接下来做去重处理.
------------------------------------------------------------------------------------------
顶级会议:
    1. IEEE Vis:In Proceedings of the IEEE Conference on Visualization
       inforvis: In IEEE Symposium on Information Visualization/IEEE Information Visualization
       scivis:
       VAST: IEEE Conference on Visual Analytics Science and Technology
    2. Pacificvis:
       IEEE Pacific Visualization Symposium
    3. EuroVis:
       Eurographics Conference on Visualization  
------------------------------------------------------------------------------------------
"""


# 将抽取出来的可视化论文信息写入citation_visualization数据库表中.
def write_citation_visualization_table():
    visualization_papers_set = query_citation_v10_table()  # 先获得可视化领域的论文,无重复的.
    # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/Citation_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()
    # 去掉重复的论文.
    for each_paper in visualization_papers_set:  # 一共10574条数据.
        cursor.execute('''insert into papers (id, title, authors,public_venue,year,n_citation,reference,abstract)
                                                      VALUES (?,?,?,?,?,?,?,?)''',
                       (each_paper[0], each_paper[1], each_paper[2], each_paper[3], each_paper[4], each_paper[5],
                        each_paper[6], each_paper[7]))
    db.commit()  # 必须提交事务，否则无法写入表格
    db.close()


# 前面从DBPL数据中抽取出可视化领域的论文信息,然后存入Citation_Visualization数据库中的citation表, 现在处理参考文献, 创建可视化领域的引用网络.
def create_citation_network_visualization_domain():
    dbname = "DB/Citation_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()
    # 去掉重复的论文.
    cursor.execute("select id, title, authors, public_venue, year, n_citation, reference, abstract from papers")
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果
    all_id_papars = []
    all_title_papers = []
    id_vs_references = []

    citation_network_edges_visualization_with_title = []  # 最后的自引网络的边集合,名字为title
    citation_network_edges_visualization_with_id = []  # 最后的自引网络的边集合,名字为id
    # citation_network_nodes_visualization = []
    for each_paper in data:
        all_id_papars.append(each_paper[0])  # 将id存放在all_id_papars,用于后面参考文献的筛选,因为要过滤出可视化领域的参考文献,生成一个自引网络.
        all_title_papers.append(each_paper[1])  # title
        temp_obj = {}
        temp_obj["source"] = each_paper[0]  # id
        temp_obj["target"] = each_paper[6]  # reference
        id_vs_references.append(temp_obj)  # [{}, {},...{}]
    for each_obj in id_vs_references:
        ref = each_obj["target"]
        paper_id = each_obj["source"]
        if ref != "" and ref != "NULL":  # 排除 空字符+NULL
            ref = ref.strip()
            ref = ref.split(";")  # 划分
            for each_ref in ref:  # 遍历每个参考文献
                # TODO:如果参考文献属于可视化领域,则建立边,否则丢弃,现在只建立自引网络
                if each_ref in all_id_papars:
                    edge_obj_id = {}
                    edge_obj = {}

                    edge_obj_id["source"] = paper_id
                    edge_obj_id["target"] = each_ref
                    citation_network_edges_visualization_with_id.append(edge_obj_id)

                    # source 标题
                    source_index = all_id_papars.index(paper_id)
                    source_title = all_title_papers[source_index]
                    # target 标题
                    target_index = all_id_papars.index(each_ref)
                    target_title = all_title_papers[target_index]
                    edge_obj["source"] = source_title
                    edge_obj["target"] = target_title
                    citation_network_edges_visualization_with_title.append(
                        edge_obj)  # [{"source": title1, "target": title2}, ...]
    # TODO: 现在先创建一个可以用echarts可视化的网络格式. 现在, {"source": id1, "target": id2}/{"source": title1, "target": title2}
    """
    备注: 1. eacharts可以适配的格式: {
        "nodes":[{"id": title1, "name": title1}, ...]
        "links":[{"source": title1, "target": title2}, ...]}
    """
    # 构造节点对象
    citation_network_nodes_visualization_with_title = []
    citation_network_nodes_visualization_with_id = []
    temp_index = -1  # 索引
    for each_id in all_id_papars:
        temp_index += 1
        node_obj_title = {}  # 标题作为name + id
        title_name = all_title_papers[temp_index]
        node_obj_title["id"] = title_name
        node_obj_title["name"] = title_name
        citation_network_nodes_visualization_with_title.append(node_obj_title)

        node_obj_id = {}  # id作为name + id
        node_obj_id["id"] = each_id
        node_obj_id["name"] = each_id
        citation_network_nodes_visualization_with_id.append(node_obj_id)

    # 构造网络.
    citation_network_with_nodes_edges_title = {"nodes": citation_network_nodes_visualization_with_title,
                                               "links": citation_network_edges_visualization_with_title}
    citation_network_with_nodes_edges_id = {"nodes": citation_network_nodes_visualization_with_id,
                                            "links": citation_network_edges_visualization_with_id}
    db.close()
    return citation_network_with_nodes_edges_id, citation_network_with_nodes_edges_title


# 创建可视化领域网络表,存放可视化领域的论文信息.
def create_visualization_citation_network_table():
    # # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/Citation_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()
    # 备注: 为了方便后续处理没有数据的情况,所有的字段类型都是text,尤其是n_citation.
    # 写sql语言,执行,创建作者表格. 注意:表格的字段不能命名为references,命名为reference就可以了.
    citation_sql = '''create table citation_edges (    
                   source          text,
                   target          text                    
                )'''
    cursor.execute(citation_sql)
    print("citation created successfully")
    cursor.close()
    db.close()  # 关闭数据库


# 将网络的边写入数据库中.
def write_visualization_citation_network_table():
    # # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/Citation_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()
    graph_id, graph_title = create_citation_network_visualization_domain()
    edges_id = graph_id["links"]
    for each_edge in edges_id:
        source = each_edge["source"]
        target = each_edge["target"]
        cursor.execute('''insert into citation_edges (source, target)
                             VALUES (?,?)''', (source, target))
    db.commit()  # 必须提交事务，否则无法写入表格
    db.close()


# TODO: 创建一个数据库,用于存放可视化领域的作者合作网络数据.
def create_coauthor_table_for_visualization():
    # # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/Coauthor_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()

    # 写sql语言,执行,创建作者表格. 注意:表格的字段不能命名为index,命名为id就可以了.
    author_sql = '''create table author (    
                   id             int,
                   name           text,
                   institution    text,
                   num_papers     int,
                   num_citation   int,
                   H_index        int,
                   P_index        real,
                   UP_index       real,
                   interests      text
                )'''
    cursor.execute(author_sql)
    print("author created successfully")
    cursor.close()

    db.close()  # 关闭数据库


# 先匹配,然后往里面写数据.
def write_coauthor_table_for_visualization():
    start_time = datetime.now()
    f = open("static/data/connected_max_subgraph_visualization_coauthor_edges.txt")  # 可视化领域的作者合作网络.
    # start_time = datetime.datetime.now()
    lines = f.readlines()
    f.close()
    # edges_list_with_weight = []
    nodes_set = set()
    for line in lines:
        line = line.strip()
        line = line.split("|")
        # edges_list_with_weight.append(line[:3])  # 带权重. edges_list_with_weight=[(source, target, value, source_name, target_name), ...]
        nodes_set.add(line[0])  # source
        nodes_set.add(line[1])  # target

    all_authors = []
    # 先从原数据库中匹配出可视化领域的作者.
    dbname = "DB/AcademicNetwork.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()
    for each_id in nodes_set:
        cursor.execute("select id,name,institution,num_papers,num_citation,H_index,P_index,UP_index,interests from author where id=?", (each_id, ))
        """
           id             int,
           name           text,
           institution    text,
           num_papers     int,
           num_citation   int,
           H_index        int,
           P_index        real,
           UP_index       real,
           interests      text
        """
        data = cursor.fetchall()  # 使用这种方式取出所有查询结果
        # print("data")
        # print(data)
        all_authors.append(data[0])
    db.close()

    dbname = "DB/Coauthor_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("................writing Coauthor_Visualization.db................")

    # 创建数据库中的游标对象
    cursor = db.cursor()

    for row in all_authors:  # row是字典{}
        cursor.execute('''insert into author (id, name, institution, num_papers, num_citation, H_index, P_index, UP_index, interests)
                            VALUES (?,?,?,?,?,?,?,?,?)''', (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8]))

    db.commit()  # 必须提交事务，否则无法写入表格
    db.close()

    end_time = datetime.now()
    time = (end_time - start_time).seconds
    print("用时:")
    print(time)


# fixme: 创建可视化领域的作者合作网络,存放边.
def create_table_coauthor_network_for_visualization():
    # # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/Coauthor_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()

    # 写sql语言,执行,创建作者表格. 注意:表格的字段不能命名为index,命名为id就可以了.
    author_sql = '''create table coauthor_network (    
                   source         text,
                   target         text,
                   weight         int,
                   source_name    text,
                   target_name    text                    
                )'''
    cursor.execute(author_sql)
    print("author created successfully")
    cursor.close()

    db.close()  # 关闭数据库


# 将共同作者合作网络写入Coauthor_Visualization.db数据库的coauthor_network表中.
def write_table_coauthor_network_for_visualization():
    f = open("static/data/connected_max_subgraph_visualization_coauthor_edges.txt")  # 可视化领域的作者合作网络.
    lines = f.readlines()
    f.close()
    edges_list = []
    for line in lines:
        line = line.strip()
        line = line.split("|")  # [x, x, x, x, x]
        edges_list.append(line)  # fixme: 带权重. edges_list_with_weight=[(source, target, value, source_name, target_name), ...]

    dbname = "DB/Coauthor_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("................writing Coauthor_Visualization.db................")
    # 创建数据库中的游标对象
    cursor = db.cursor()

    for each_one in edges_list:  # [source, target, weight, source_name, target_name]
        cursor.execute('''insert into coauthor_network (source, target, weight, source_name, target_name)  VALUES (?,?,?,?,?)''',
                       (each_one[0], each_one[1], each_one[2], each_one[3], each_one[4]))
    db.commit()  # 必须提交事务，否则无法写入表格
    db.close()


# todo: 为了验证扩展性,先处理几个数据.
def create_table_citation_from_visualization():
    dbname = "DB/Citation_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()

    # 写sql语言,执行,创建作者表格. 注意:表格的字段不能命名为index,命名为id就可以了.
    author_sql = '''create table edge_mty (    
                       source         text,
                       target         text,
                       weight         int,
                       source_name    text,
                       target_name    text                    
                    )'''
    cursor.execute(author_sql)
    print("author created successfully")
    cursor.close()

    db.close()  # 关闭数据库


def write_table_citation_from_visualization():
    f = open("static/data/connected_max_subgraph_citation_network_visualization.json.txt")  # 可视化领域的作者合作网络.
    lines = f.readlines()
    f.close()
    dbname = "DB/Citation_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("Opened database successfully")
    # 创建数据库中的游标对象
    cursor = db.cursor()
    cursor.execute("select id, name from node")
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果
    id_list = []
    name_list = []
    for i in data:
        # print(i)
        id_ = i[0]
        name = i[1]
        id_list.append(id_)
        name_list.append(name)
    # print(id_list)
    # print(name_list)
    edges_list = []
    for line in lines:
        line = line.strip()
        line = line.split()
        # print(line)
        source = line[0]
        target = line[1]
        index_source = id_list.index(source)
        index_target = id_list.index(target)
        source_name = name_list[index_source]
        target_name = name_list[index_target]
        edges_list.append((source, target, 1, source_name, target_name))
    print(edges_list)
    for each_one in edges_list:  # [source, target, weight, source_name, target_name]
        cursor.execute('''insert into edge_mty (source, target, weight, source_name, target_name)  VALUES (?,?,?,?,?)''',
                       (each_one[0], each_one[1], each_one[2], each_one[3], each_one[4]))
    db.commit()  # 必须提交事务，否则无法写入表格
    db.close()


# 创建可视化领域的表,存放可视化领域的论文信息.
def create_table_citation_from_visualizaton():
    # # 如果没有数据库,则创建数据库,否则连接数据库
    dbname = "DB/Citation_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")

    # 创建数据库中的游标对象
    cursor = db.cursor()
    # 备注: 为了方便后续处理没有数据的情况,所有的字段类型都是text,尤其是n_citation.
    # 写sql语言,执行,创建作者表格. 注意:表格的字段不能命名为references,命名为reference就可以了.
    citation_sql = '''create table node_mty (    
                   id             text,
                   title          text,
                   authors        text,              
                   public_venue   text,
                   year           text,
                   n_citation     int,
                   reference      text,
                   abstract       text
                )'''
    cursor.execute(citation_sql)
    print("citation created successfully")
    cursor.close()
    db.close()  # 关闭数据库


def write_table_citation_from_visualizaton():
    f = open("static/data/connected_max_subgraph_citation_network_visualization.json.txt")  # 可视化领域的作者合作网络.
    lines = f.readlines()
    f.close()
    dbname = "DB/Citation_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("Opened database successfully")
    # 创建数据库中的游标对象
    cursor = db.cursor()
    cursor.execute("select * from node")
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果
    id_list = []
    row_list = []
    for i in data:
        id_ = i[0]
        id_list.append(id_)
        row_list.append(i)

    print("id_list")
    print(len(id_list))

    max_connected_id_list = set()
    for line in lines:
        line = line.strip()
        line = line.split()
        # print(line)
        source = line[0]
        target = line[1]
        max_connected_id_list.add(source)
        max_connected_id_list.add(target)
    print("max_connected_id_list")
    print(len(max_connected_id_list))

    for each_one in max_connected_id_list:
        index_id = id_list.index(each_one)
        each_paper = row_list[index_id]
        cursor.execute('''insert into node_mty (id, title, authors,public_venue,year,n_citation,reference,abstract)
                                                              VALUES (?,?,?,?,?,?,?,?)''',
                       (each_paper[0], each_paper[1], each_paper[2], each_paper[3], each_paper[4], each_paper[5],
                        each_paper[6], each_paper[7]))

    db.commit()  # 必须提交事务,否则无法写入表格.
    db.close()


def references_id_to_title():
    dbname = "DB_backup/Citation_Visualization.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("Opened database successfully")
    # 创建数据库中的游标对象
    cursor = db.cursor()
    cursor.execute("select id, reference from node")
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果
    # print(data)
    # id_list = []
    # reference = []
    for each_one in data:
        id_node = each_one[0]
        id_node = id_node.strip()
        # id_list.append(id_node)
        references = each_one[1]
        references = references.strip()
        references = references.split(";")
        references_text = ""
        for each_reference in references:
            # print(each_reference)
            if each_reference != "NULL":
                cursor.execute("select name from node where id=?", (each_reference,))
                data = cursor.fetchall()  # 使用这种方式取出所有查询结果[(x,)]

                for i in data:
                    name = i[0]
                    if name != "":
                        references_text += name + ";"

        references_text = references_text.strip(";")
        if references_text == "":
            references_text = "NULL"

        # print(id_node)
        # print(references_text)

        sql = "update node set ref=? where id=?"
        cursor.execute(sql, (references_text, id_node))
    db.commit()  # 必须提交事务,否则无法写入表格.
    db.close()


# 根据条件抽取作者
def extract_author_according_to_conditions(conditions=None):
    dbname = "DB/backup/AcademicNetwork.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")
    id_set = set()
    row_set = set()
    # 创建数据库中的游标对象
    cursor = db.cursor()
    for each_one in conditions:

        conditions_aql = "%" + each_one + "%"
        """
        备注:
        1. SQlite3 的like子句使用, 百分号(%)代表零个,一个或多个数字或字符.下划线(_)代表一个单一的数字或字符.这些符号可以被组合使用.
        2. e.g. %information visualization% 将获得 Proceedings of the 1998 workshop on New paradigms in information visualization and manipulation
        3. 查询字符不区分大小写.
        """
        cursor.execute("select id, name, institution, num_papers, num_citation, H_index, P_index, UP_index, interests from author where interests like ?", (conditions_aql,))
        """
          id, name, institution, num_papers, num_citation, H_index, P_index, UP_index, interests
        """
        data = cursor.fetchall()  # 使用这种方式取出所有查询结果
        # print("数量:")
        # print(len(data))

        for each_one in data:
            # print(each_one[0])
            node_id = each_one[0]
            id_set.add(node_id)
            row_set.add(each_one)

    print("节点数量:")
    print(len(row_set))
    f_nodes = open("nodes_corresponding_conditions.txt", "w")
    f_rows = open("rows_corresponding_conditions.txt", "w")
    for each_one in id_set:
        # each_one = each_one.strip()
        f_nodes.write(str(each_one) + "\n")

    for each_one in row_set:  # [(), ()]
        temp_str = ""
        for jj in each_one:
            jj = str(jj)
            temp_str += jj + "||"
        temp_str = temp_str.strip("||")
        # each_one = each_one.strip()
        f_rows.write(temp_str + "\n")
    db.close()  # 关闭数据库


def find_edges_corresponding_condition():
    dbname = "DB/backup/AcademicNetwork.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")
    cursor = db.cursor()
    cursor.execute("select source, target, num_papers from coauthor")
    data = cursor.fetchall()  # 使用这种方式取出所有查询结果

    ff = open("nodes_corresponding_conditions.txt")
    lines = ff.readlines()
    ff.close()
    nodes_list = []
    for each_one in lines:
        each_one = each_one.strip()
        nodes_list.append(each_one)
    fff = open("edges_corresponding_conditions.txt", "w")
    for each_one in data:  # [(source, target, num_papers), ...]
        source = str(each_one[0])
        target = str(each_one[1])
        num_papers = str(each_one[2])
        if source in nodes_list and target in nodes_list:
            fff.write(source + "," + target + "," + num_papers + "\n")
    fff.close()


# todo: 抽取出最大子图.
def get_max_connected_subgraph(f_name=None):
    start_time = datetime.now()
    f = open(f_name, "r")
    lines = f.readlines()
    f.close()
    print(len(lines))

    edges_list_with_weight = []
    # edges_weight_list = []
    for line in lines:
        line = line.strip()
        line = line.split(",")  # (source, target, weight)
        edges_list_with_weight.append(line)  # 带权重.
        # edges_weight_list.append(line[2])
    print("edges_list_with_weight[:10]")
    print(edges_list_with_weight[:10])
    G = nx.Graph()
    G.add_weighted_edges_from(edges_list_with_weight)
    largest_components = max(nx.connected_components(G), key=len)
    nx.connected_components(G)
    print("节点数量")
    print(len(largest_components))

    f_nodes = open("max_connected_subgraph_Academy_nodes.txt", "w")
    for each_node in largest_components:
        f_nodes.write(str(each_node) + "\n")
    f_nodes.close()

    max_subgraph = G.subgraph(largest_components)
    # print("Obtaining all edges of the max_connected_subgraph")
    max_subgraph_edge_list = list(max_subgraph.edges.data('weight', default=1))  # [(3, 4), (3, 5), (3, 6), (4, 5), (5, 6)]
    print("边数量")
    print(len(max_subgraph_edge_list))

    f_subg = open("max_connected_subgraph_Academy.txt", "w")
    # print("writing all edgrs to the file")
    print("max_subgraph_edge_list[:2]")
    print(max_subgraph_edge_list[:2])
    for each_edge in max_subgraph_edge_list:  # (source, target)
        # temp_tuple = (each_edge[0], each_edge[1])
        # edge_index = edges_list_with_weight.index(temp_tuple)
        # weight_edge = edges_weight_list[edge_index]
        source_node = each_edge[0]
        target_node = each_edge[1]
        weight_edge = each_edge[2]
        f_subg.write(str(source_node) + "," + str(target_node) + "," + weight_edge + "\n")
    f_subg.close()
    print("end writing")
    end_time = datetime.now()
    time = (end_time - start_time).seconds
    print("time:")
    print(time)


def find_nodes_info_for_max_connected_subgraph(all_nodes_info_file, max_connected_subg_nodes_file):
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
        node = line[0]
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


def edges_info(max_connected_subg_edges_file=None, max_connected_subg_nodes_file=None):
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
        weight = temp_edge[2]
        source_index = node_info_lines_id_list.index(source)
        target_index = node_info_lines_id_list.index(target)
        source_name = node_info_lines_name_list[source_index]
        target_name = node_info_lines_name_list[target_index]
        # print(source + ";" + target + ";" + "1" + ";" + source_name + ";" + target_name)
        fff.write(source + "||" + target + "||" + str(weight) + "||" + source_name + "||" + target_name + "\n")
    print("counter=")
    print(counter)
    fff.close()


###################################################################

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
                   id             text,
                   name           text,
                   institution    text,
                   num_papers     int,
                   num_citation   int,
                   H_index        int,
                   P_index        real,
                   UP_index       real,
                   interests      text
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

        new_line = line
        nodes_list.append(new_line)  # fixme: 带权重. edges_list_with_weight=[(source, target, value, source_name, target_name), ...]

    dbname = "DB/" + db_name
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("................writing................")
    # 创建数据库中的游标对象
    cursor = db.cursor()

    for each_one in nodes_list:  # (source, target, weight, source_name, target_name)
        cursor.execute('''insert into node (id, name, institution, num_papers, num_citation, H_index, P_index, UP_index, interests) VALUES (?,?,?,?,?,?,?,?,?)''', (each_one[0], each_one[1], each_one[2], each_one[3], each_one[4], each_one[5], each_one[6], each_one[7], each_one[8]))
    db.commit()  # 必须提交事务，否则无法写入表格
    db.close()

# TODO:创建数据库.
def add_node_edge_table():
    # #todo: 创建edge表,写入数据.
    db_name = "co-authorship.db"
    create_table_edge(db_name)  # 先创建edge表
    file_name = "max_connected_subgraph_Academy_info.txt"
    write_table_edge(db_name, file_name)  # 将数据写入edge表

    # #todo: 创建node表,写入数据.
    db_name = "co-authorship.db"
    file_name = "max_connected_subgraph_Academy_nodes_info.txt"
    create_table_node(db_name)
    write_table_node(db_name, file_name)


# todo: 找出节点对应的publications
def get_author_punlications():
    dbname = "DB/backup/AcademicNetwork.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表

    print("Opened database successfully")
    cursor = db.cursor()

    ff = open("max_connected_subgraph_Academy_nodes.txt")
    lines = ff.readlines()
    ff.close()
    fff = open("max_connected_subgraph_Academy_nodes_publications.txt", "w")
    for each_one in lines:
        each_one = each_one.strip()
        id_author = each_one
        cursor.execute("select id_paper from author2paper where id_author=?", (id_author, ))
        data = cursor.fetchall()  # 使用这种方式取出所有查询结果
        temp_paper_str = ""
        papers_set = set()
        for each_paper in data:  # [(), (), ...]
            each_paper = each_paper[0].strip()
            papers_set.add(each_paper)
        for ii in papers_set:
            temp_paper_str += ii + ";"
        temp_paper_str = temp_paper_str.strip(";")
        fff.write(id_author + "||" + temp_paper_str + "\n")

    db.close()
    fff.close()


# 更新节点的publications字段.
def insert_publications():
    start_time = datetime.now()
    ff = open("max_connected_subgraph_Academy_nodes_publications.txt")
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


def extrct_papers():
    start_time = datetime.now()
    dbname = "DB/backup/AcademicNetwork.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("Opened database successfully")
    # 创建数据库中的游标对象
    cursor = db.cursor()

    # all_records = []
    ff = open("max_connected_subgraph_Academy_publications.txt")
    lines = ff.readlines()
    ff.close()
    papers_set_for_all_authors = []
    for ii in lines:
        ii = ii.strip()
        papers_set_for_all_authors.append(ii)
    print("papers_set_for_all_authors[:10]")
    print(papers_set_for_all_authors[:10])

    cursor.execute("select * from paper")
    row = cursor.fetchall()  # [(), (), ....]
    paper_id = []
    for jj in row:
        paper_id.append(str(jj[0]))

    counter = 0
    f_save = open("co-author_academy_publications__info.txt", "w")
    for each_one in papers_set_for_all_authors:  # [12, 99, ...]
        node_index = paper_id.index(each_one)
        paper_info = row[node_index]  # paper_info = (id, title, ...)
        counter += 1
        if counter % 100 == 0:
            print(paper_info)
        temp_string = ""
        for i in paper_info:
            i = str(i).strip()
            if i == "":
                temp_string += "NULL" + "||"
            else:
                temp_string += i + "||"
        temp_string = temp_string.strip("||")
        f_save.write(temp_string + "\n")

    f_save.close()
    print("f_save ok")

    # start_time = datetime.now()
    dbname = "DB/co-authorship.db"
    db = sqlite3.connect(dbname)  # 将要在PacificVIS.db数据库中创建PAPER表格，数据库中已经有Colection表
    print("Opened database successfully")
    # 创建数据库中的游标对象
    cursor = db.cursor()

    f_mao = open("co-author_academy_publications__info.txt")
    lines = f_mao.readlines()
    f_mao.close()
    all_records = []
    for jj in lines:
        jj = jj.strip()
        jj = jj.split("||")
        # print(jj)
        all_records.append(jj)  # [(), ...]

    for row in all_records:  # [(), (), ...]
        print("len(row)")
        print(len(row))
        print(row)
        cursor.execute('''insert into publications (id, title, authors, institution, year, public_venue, id_reference, abstract)
                                            VALUES (?,?,?,?,?,?,?,?)''', (row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
    db.commit()  # 必须提交事务，否则无法写入表格
    db.close()

    end_time = datetime.now()
    time = (end_time - start_time).seconds
    print("time")
    print(time)


if __name__ == "__main__":

    # conditions = ["visual",  # 可视化
    #               "human-computer interaction", "human computer interaction", "human-machine interaction", "man-machine interaction",
    #               "data mining", "data-mining",
    #               "machine learning", "machine-learning"
    #               ]
    # extract_author_according_to_conditions(conditions=conditions)
    # find_edges_corresponding_condition()



    # f_name = "edges_corresponding_conditions.txt"
    # get_max_connected_subgraph(f_name=f_name)
    # all_nodes_info_file = "rows_corresponding_conditions.txt"
    # max_connected_subg_nodes_file = "max_connected_subgraph_Academy_nodes.txt"
    # find_nodes_info_for_max_connected_subgraph(all_nodes_info_file, max_connected_subg_nodes_file)
    # max_connected_subg_edges_file = "max_connected_subgraph_Academy.txt"
    # max_connected_subg_nodes_file = "max_connected_subgraph_Academy_nodes.txt"
    # edges_info(max_connected_subg_edges_file=max_connected_subg_edges_file, max_connected_subg_nodes_file=max_connected_subg_nodes_file)
    # add_node_edge_table()

    # get_author_punlications()
    # insert_publications()
    extrct_papers()















