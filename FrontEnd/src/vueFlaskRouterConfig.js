// 将vue-->flask的请求路径放在vueFlaskRouterConfig中,方便以后的管理,后台的端口号:5050.
const vueFlaskRouterConfig = { 
	mainViewGraph: 'http://127.0.0.1:5050/mainview/graph', //主视图请求DOI子图数据.
	mainViewNodeInfo: 'http://127.0.0.1:5050/mainview/nodeinfo/', //主视图中点击节点,请求该节点的详细信息.
	mainViewNodeExpland: 'http://127.0.0.1:5050/mainview/nodeexpland', // 主视图中点击边缘节点,请求其扩展的邻居节点.
	infoSearchForDbSelection: "http://127.0.0.1:5050/infosearch/selectdb", // 选择数据库.
	infoSearchForDbFields: "http://127.0.0.1:5050/infosearch/getdbfields", // 向后台请求指定数据库中表格的字段.
	infoSearchForDbFieldsValues: "http://127.0.0.1:5050/infosearch/getdbfieldsvalues", // 向后台请求所有字段对应的数据.
	infoSearchForResultsSearch:"http://127.0.0.1:5050/infosearch/resultssearch", // 点击"Search"请求条件匹配数据.
	infoSearchForChangeDb: "http://127.0.0.1:5050/infosearch/changedb", // 前端更换数据库,后台加载对应的全局图.
	networkInformation: "http://127.0.0.1:5050/networkInformationView/getglobalinfo",
	mainViewGraphNodesAtrri: "http://127.0.0.1:5050/mainview/graphnodesattri", // 获得主视图中节点的属性信息.
	mainViewNodeDetailsSeeMore: "http://127.0.0.1:5050/mainview/nodedetails/seemore",
	mainViewEdgeDetails: "http://127.0.0.1:5050/mainview/edgedetails", // 点击边获得边的信息.
	getSearchResultGraph:"http://127.0.0.1:5050/resultsSearchView/getSearchResultGraph",
	globalGraphLayout: "http://127.0.0.1:5050/globalGraphView/globalGraphLayout", // 请求布局好的全局图json数据.
	getFilteredSubGraph:"http://127.0.0.1:5050/globalFilteredSubgraphView/getFilteredSubGraph",
	selctionFocusNodesByNodeMeasures:"http://127.0.0.1:5050/focusNodesSelection/structureFuture", //焦点通过节点度量来选择提供一个焦点选择的入口.

};
let searchFlag=false; // 搜索点击标志位.
export {	
	vueFlaskRouterConfig,
	searchFlag,
}; 
// export default{
// 	vueFlaskRouterConfig: vueFlaskRouterConfig,
// 	test:test,
// 	hell: hell(),

// };