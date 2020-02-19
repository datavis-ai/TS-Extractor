import Vue from 'vue'
import Vuex from 'vuex'
Vue.use(Vuex);

const store = new Vuex.Store({  // 用const意味着地址不变,而对象的键值对是可以更改的.
  state: {  
    // 在组件中可以直接进行读写.
    selection:{ //选择框+输入框的状态.
      dboptions: [], // [{value:x, label:x, directed:x}, ...] this.$store.state.selection.dboptions
      selectiondb: '', // 选中的数据库名称. this.$store.state.selection.selectiondb
      selectionfield: '', // 选中的字段名称. this.$store.state.selection.selectionfield
      keyword: "", // 输入的关键字,用于匹配数据库.  this.$store.state.selection.keyword
    },
    
    fields:{
      fieldsType: null, // selectionfield中字段的类型.this.$store.state.fields.fieldsType
    },
    conditionsSearch:{
      formDataList:[] //增加的条件项,[{selectionfield:"All", keyWord:""}, ...], this.$store.state.conditionsSearch.formDataList
    },

    widgetView:{ // Settings面板参数默认值设置.
      scaleOfSingleFocus: 30,  // scale Of Single Focus,用于单个焦点的抽取规模. this.$store.state.widgetView.scaleOfSingleFocus
      explandneighbors: 5, // 扩展节点的数量. this.$store.state.widgetView.explandneighbors
      diffFactor: 0.85,  // 用于扩散函数的扩散程度控制. this.$store.state.widgetView.diffFactor
      UIFactor: 0.9,  // UI_Factor,用户兴趣度因子,API_factor = 1 - UI_factor.
      APIFactor: 0.1,  // API_Factor
      isEdgeAttri: true, // 在DOI扩散函数中是否考虑边的属性
      probRestart: 0.7,  // RWR重启概率. this.$store.state.widgetView.probRestart
      weightAttrNode: 1, // 属性节点-节点的权重. this.$store.state.widgetView.weightAttrNode
    },

    attrNode:{
      discardfield: null, // 属性图动态构建时,不需要考虑的字段,注意:这个是所有数据不需要考虑的字段的集合,而非选中数据库的非考量字段. this_.$store.state.attrNode.discardfield
      fullCompatibilityAtrr: null // 上下兼容属性,适用于属性值字符串比较长的属性,比如合作网络中的作者的隶属机构 this_.$store.state.attrNode.fullCompatibilityAtrr
    },

    mainViewGraph:{
      graphDirection: false,  //主视图中的DOI图的方向性. this.$store.state.mainViewGraph.graphDirection
      histClickFlag:null, // 用于记录是否点击了历史图片.[true]表示点击了,写成数组是为了用指针. this.$store.state.mainViewGraph.histClickFlag
      attributesExplorNodeHighlight: {}, // 用于保存布局图的节点属性探索匹配节点.this.$store.state.mainViewGraph.attributesExplorNodeHighlight
      highlightColorSheet:{ //主视图中各种节点高亮配色以及圈stroke大小设置.
        clickCheckNodeInfo: "#000000", // 点击节点查看细节信息时高亮的颜色. highlightColorSheet.clickCheckNodeInfo
        clickMatchNodeAttri: "#33FFCC", // 点击属性值匹配上的节点高亮的颜色.highlightColorSheet.clickMatchNodeAttri
        rightClickSelectAttriEplor: "#239B56", // 右键选中节点作为属性探索候选节点时高亮的颜色.highlightColorSheet.rightClickSelectAttriEplor
        rightClickAsFocus: "#1890ff", // 右键点击作为焦点时的高亮颜色.highlightColorSheet.rightClickAsFocus
        strokeWidth:3, // stroke-width的大小.
        strokeWidthNull:0, // 恢复时的stroke-width的大小.
        highLinkColor: "#FF8700", // 点击边高亮的颜色.
      },
      dynamicAttriExplorList:[], // this.$store.state.mainViewGraph.dynamicAttriExplorList
      dynamicConditionExploreObj:{}, // this.$store.state.mainViewGraph.dynamicConditionExploreList
      stopWords:[], // this.$store.state.mainViewGraph.stopWords
      clickNode2GetId: null, // 点击主视图中节点打开细节框的同时,获得节点的id. this.$store.state.mainViewGraph.clickNode2GetId
      isOpenCheckNodeDetailFlag: false, // 是否点击节点,打开节点细节信息框. this.$store.state.mainViewGraph.isOpenCheckNodeDetailFlag
      // nodeColorSet:{basenode:"#FF8700", focusnodes:"#1890ff", explandnode:"#109618"},  // 节点配色. this.$store.state.mainViewGraph.nodeColorSet
      isExplandNodeFlag: false, // 是否扩展节点标志位,用于控制扩展出来的新节点和新边的颜色显示. this_.$store.state.mainViewGraph.isExplandNodeFlag
      d3EventTransform:{}, // this_.$store.state.mainViewGraph.d3EventTransform 用于保存transform属性值.{x:0, y:0, k:0} 用于记录画布的位置和缩放比例.
      fontSize: 14, // interest subgraph的text的字体大小: this_.$store.state.mainViewGraph.fontSize
      fontWeight: 600, //interest subgraph的text的字体粗细: this_.$store.state.mainViewGraph.fontWeight
      edgeOpacity: 0.3, // 边的透明度
      strokeWidth: 4, // 高亮Ring的宽度. this_.$store.state.mainViewGraph.strokeWidth
      isDirected: null, // 网络是否有向: false/true,  this_.$store.state.mainViewGraph.isDirected  
    },

    focusSetView:{
      idNameObj: null, // {id: name, ...} 用于mainView组件中将数据保存到indexedDB中. this.$store.state.focusSetView.idNameObj
      setInterests: null,  // this.$store.state.focusSetView.setInterests
      dynamicTagsFocus: [], // this.$store.state.focusSetView.dynamicTagsFocus
    },
    infoSearchView:{
      dbLoadedFlag: null, // 数据库加载完毕标志位.只有数据库加载完毕,才能请求对应的DOI子图.this.$store.state.infoSearchView.dbLoadedFlag
      dbtables: [], // 选定数据库中,除了node + edge外的其他表格,e.g. ["publictions"] this.$store.state.infoSearchView.dbtables
      numNodes: 0, // 全局图的节点数量
    },
    networkInformationView:{  
        globalGraphInfo: {}, // 全局图信息. this.$store.state.networkInformationView.globalGraphInfo
        doiGraphInfo:null, // DOI子图信息. this.$store.state.networkInformationView.doiGraphInfo
    },
    focusAttributesSelection:{
      checkedFocusAttri: [], // this.$store.state.focusAttributesSelection.checkedFocusAttri
      allFocusAttriIterms:null // this.$store.state.focusAttributesSelection.allFocusAttriIterms
    },
    nodeInfoView:{
      // isOpenSeeMoreFlag: false, // 是否打开See More信息框. this.$store.state.nodeInfoView.isOpenSeeMoreFlag
    },
    layoutSettingsView:{
      labelDisplay: true, // 是否显示标签. this.$store.state.layoutSettingsView.labelDisplay
      fixedNode: false, // 是否可以固定节点.
    },
    resultsSearchView:{
      layoutSettings:{ //this.$store.state.resultsSearchView.layoutSettings
          linkLength: 80, // 边的长度.
          chargeStrength: -200, // 力导引力度大小.
          edgeMode: "line", // 边模式:curve-曲线 false, line-直线 true.
          labelDisplay: true, // 是否显示标签.
          limitBox: false, // 是否将布局结果限制在一个盒子里面.
          nodeColor:"#FF8700", // 节点的填充颜色.
          baseSize: 10, // 布局图中节点的基本大小.
          nodeLabelTextMaxLen: 38 // 节点标签操作过这个值,则用省略号表示.
      },
      svgId:"searchResultVisSvg", // resultsSearchView.vue中svg的id. this.$store.state.resultsSearchView.svgId
      focusStateList: [], //用于记录在表格中选中作为焦点的id. this.$store.state.resultsSearchView.focusStateList
      resultVisGraph:null, //表格对应的图,这样不用每次点开都向后台请求. this.$store.state.resultsSearchView.resultVisGraph
      tableRowSortList:[], //表格中行的排序列表(当点击排序后,此列表更新,保持与表格排序后的顺序相同) this.$store.state.resultsSearchView.tableRowSortList
      // currentPage: 1, //表格当前页面. this.$store.state.resultsSearchView.currentPage
      refreshTablePageFlagForClickNode: false, //result vis中,点击节点,如果没有当前页没有该节点的信息,则使能该标志位.this.$store.state.resultsSearchView.refreshTablePageFlagForClickNode
      clickNodeId: null, //在result vis中点击节点的id. this.$store.state.resultsSearchView.clickNodeId
      pageSize: 100, //一页的数量. this.$store.state.resultsSearchView.pageSize
      tableData: null, //表格数据,使用指针指向组件中的tableData. this.$store.state.resultsSearchView.tableData
      focusColor:"#409EFF", //焦点颜色. this.$store.state.resultsSearchView.focusColor
      isOpenResultVis: false, //是否打开搜索结果可视化弹窗. this.$store.state.resultsSearchView.isOpenResultVis
      busEventName: "sendLayoutSetOut", //子组件传入参数,发送出来的事件名称. this.$store.state.resultsSearchView.busEventName
      tableRowClickNodeList: null, //表格行点击则装入数组中.[idx] this.$store.state.resultsSearchView.tableRowClickNodeList
      svgWidth: 1816, // result vis中svg的大小设置.
      svgHeight: 890,
    },
    jboxPositionSet:{ //this.$store.state.jboxPositionSet
      topRightSide:{ //右上角.
        x: 1445,  // number, 'left', 'right' or 'center'
        y: 80  // number, 'top', 'right' or 'center' 
      },
      topRightSideForLegend:{
        x: 1598,  // number, 'left', 'right' or 'center'
        y: 80 
      },
      topLeftSide:{ //左上角.
        x: 622,  // number, 'left', 'right' or 'center'
        y: 80  // number, 'top', 'bottom' or 'center'
      },
      bottom:{ //底部.
        x: 535,  // number, 'left', 'right' or 'center'
        y: 707  // number, 'top', 'right' or 'center'
      },
      leftCenter:{ //左中.
        x: 622,  // number, 'left', 'right' or 'center'
        y: 340  // number, 'top', 'right' or 'center'
      },
      doiLayoutSetting:{
        x: 1540,  // number, 'left', 'right' or 'center'
        y: 110 
      },
      matchingPanel:{
        x: 535,  // number, 'left', 'right' or 'center'
        y: 540  // number, 'top', 'right' or 'center'
      }
    },
    globalGraphView:{
      globalGraphLayoutData: null, // 布局好的全局图数据.this.$store.state.globalGraphView.globalGraphLayoutData
      isLoadGlobalLayoutData:[], //用来表示已经请求到的全局图数据.[a.db], 表示a.db的全局图数据已经请求到了.
      width: 200, //全局图的画布大小. this.$store.state.globalGraphView.width
      height: 200, // this.$store.state.globalGraphView.height
      //globalGraphInfo: null, // 全局图的节点数量. this_.$store.state.globalGraphView.globalGraphInfo
    },
    globalFilteredSubgraphView:{
      layoutSettings:{ //this.$store.state.globalFilteredSubgraphView.layoutSettings
          linkLength: 80, // 边的长度.
          chargeStrength: -200, // 力导引力度大小.
          edgeMode: "line", // 边模式:curve-曲线 false, line-直线 true.
          labelDisplay: true, // 是否显示标签.
          limitBox: false, // 是否将布局结果限制在一个盒子里面.
          nodeColor:"#FF8700", // 节点的填充颜色.
          baseSize: 10 // 布局图中节点的基本大小.
      },
      svgId:"filteredSubgraphSvg", //this.$store.state.globalFilteredSubgraphView.svgId
      isOpenFilteredSubgraph: false, // 是否打开了过滤子图. this.$store.state.globalFilteredSubgraphView.isOpenFilteredSubgraph
      svgWidth: 890, // global filtered subgraph中svg的大小设置.
      svgHeight: 890,
      focusColor:"#409EFF", //焦点的颜色. this.$store.state.globalFilteredSubgraphView.focusColor
      globalFilteredGraph: null, //用于保存选中的全局过滤子图. this.$store.state.globalFilteredSubgraphView.globalFilteredGraph
      focusStateList: [], //用于存放焦点. this.$store.state.globalFilteredSubgraphView.focusStateList
      clickNode2GetId: null, // this_.$store.state.globalFilteredSubgraphView.clickNode2GetId

    },    
    isShowGlobalGraphFlag: false, // 控制是否请求布局好的全局图数据 this_.$store.state.isShowGlobalGraphFlag
    isUsingRankMeasures: true, // 是否使用排序度量来提供焦点选择 this_.$store.state.isUsingRankMeasures
    nodeRankTable:{ // this_.$store.state.nodeRankTable.topN
     topN: 100, // 默认取前100个.
     focusStateList: [], //用于记录ranking List中被选为焦点的id. this_.$store.state.nodeRankTable.focusStateList
    }
     
  },
  getters:{  // 读取state的值,简化组件中读取state的代码.类似于computed属性,调用的时不用加(),e.g. state.xxx, 而非state.xxx()
    getSelectiondb(state){  // 在组件中的调用方式:this.$store.getters.getSelectiondb.
      return state.selection.selectiondb;
    },
    getSelectionfield(state){
      return state.selection.selectionfield;
    },
    getKeyword(state){
      return state.selection.keyword;
    },
    getAttriSelection(state){ // this.$store.getters.getAttriSelection
      return state.focusAttributesSelection.allFocusAttriIterms;
    }
  },
  mutations:{  // 对state中的状态进行修改.简化组件中对state的修改.
    changeSelection(state, newstate){
       state.selection.selectiondb = newstate.selectiondb;
       state.selection.selectionfield = newstate.selectionfield;
       state.selection.keyword = newstate.keyword;
    }
  },
  actions:{ // 对state进行异步修改,mutations的升级,用于异步,提高效率.
    changeStateSelection(context, newstate){  // this.$store.dispatch('changeStateSelection', newstate)
      context.commit("changeSelection", newstate);
    }
  }
});

// 外部接口,外部使用时,格式如:import {xx, xx} from "xxx"
export {
    store // 在main.js中引用.
 }

/* 例子:

const store = new Vuex.Store({
  state: {
    totalPrice: 0
  },
  getters: {  // 使用方法: this.$store.getters.getTotal
    getTotal (state) {
      return state.totalPrice*2
    }
  },
  mutations: { // 使用方法: this.$store.commit('decrement', this.price)
    increment (state, price) {
      state.totalPrice += price
    },
    decrement (state, price) {
      state.totalPrice -= price
    }
  },
  actions: { // 使用方法: this.$store.dispatch('increase', this.price)
    increase (context, price) {
      context.commit('increment', price)
    }
  }
})
*/