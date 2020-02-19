<template>   
    <div id="main-view-for-graph">           
      <div class="svg-loading-box" v-loading="mainViewLoadingFlag">
        <div class="svg-container">
          <svg id="mainsvg" pointer-events="all" :width="width_" :height="height_"></svg>           
        </div>
      </div>                  
       <div id="historyGallery" :width="width_">            
         <div id="histwidget" style="text-align:right">                
           <el-form :inline="true" class="demo-form-inline" label-width="50px" size="mini">
              <el-row>
                <div class="histNav">                  
                  <div class="hist-nav-icon">                         
                    <el-popover
                      width="200"
                      v-model="visible2"                         
                      >
                      <p>Will you delete all histories?</p>
                      <div style="text-align: right; margin: 0">
                        <el-button size="mini" type="text" @click="visible2 = false">No</el-button>
                        <el-button type="primary" size="mini" @click="delAllHist">Yes</el-button>
                      </div>                 
                      
                      <div slot="reference" id="allhistdel">                             
                        <img src="../../static/img/icons-delete.png" width="20" height="20">
                      </div>
                    </el-popover>
                  </div>
                  <div class="hist-nav-icon hist-nav-text">
                    <div>Total: {{totalhist}}</div>
                  </div>                       
                </div>           
              </el-row>
         </el-form>                
         </div>
         <ul id="list"></ul>
       </div>
       <div class="histInfoContent"></div>  <!--悬浮历史图片,弹出的信息框--> 
       <div class="legend-info"></div>           
       <div id="nodeinfo">
         <nodeinfo :targetoffset="seemoretargetoffset" :targetselector="seemoretargetselector"></nodeinfo>  <!--这是组件-->           
       </div>
      <div id="doi-layout-setting">
        <diolayoutsetting></diolayoutsetting>
      </div>
      <div id="nodes-attris-exploration">
          <div id="match-node-con-box">
            <div class="match-box-div" id="attr-nodes-selected" v-if="dynamicAttriExplorList.length">
               <div class="attr-explor-title matched-panel-text">
                 <span v-if="dynamicAttriExplorList.length > 1">Selected Nodes</span>
                 <span v-if="dynamicAttriExplorList.length == 1">Selected Node</span>
               </div>
               <div id="seleced-nodes-list">
                 <el-tag
                  v-for="(tag,index) in dynamicAttriExplorList"
                  :key="tag.id"
                  class="tag-attri-node-box"        
                  closable
                  :disable-transitions="false"
                  @close="handleClose(tag)">
                    <span :id="index" class="tag-attri-node" v-if="tag.tag.length > 60">{{tag.tag.slice(0,20)+"..."}}</span>
                    <span :id="index" class="tag-attri-node" v-else>{{tag.tag}}</span>          
                 </el-tag>
               </div>              
            </div>
            
            <div class="match-box-div" id="attrs-selected-list" v-if="Object.keys(dynamicConditionExploreObj).length > 0">
               <div class="attr-explor-title matched-panel-text">
                 <span>Matching Conditions</span><span>  (The number of matching nodes:{{matchedNodesNum}})</span>
               </div> 
               <div calss="condition-div-list">                 
                 <div class="attri-conditions-box" :id="'macth-panel-condition-' + key" v-for="(key,index_) in dynamicAttriExplorNodeIdList">
                   <el-tag
                    v-for="(tag,index) in dynamicConditionExploreObj[key]"
                    :key="tag.attrValue"
                    class="tag-attri-conditions-box"
                    :id="tag.elementId + '-condition'"      
                    closable                    
                    :disable-transitions="false"
                    @close="handleCloseForConditionExploreObj(tag,key)">                    
                         <span v-if='nodeAttrType[tag.curNodeArr] == "text"' :id="index" class="tag-attri-node">{{tag.attrValue}}</span> 
                         <span v-else-if='parseFloat(tag.attrValue) > 0' :id="index" class="tag-attri-node">>={{tag.attrValue}}</span>
                         <span v-else-if='parseFloat(tag.attrValue) == 0' :id="index" class="tag-attri-node">>{{tag.attrValue}}</span>          
                  </el-tag>
                 </div>
               </div>
            </div>

          </div>
          <div id="attr-nodes-selected-table">
            <el-table
            :data="nodeAttriTableData"
            border
            empty-text="null"
            style="width: 100%"
            :max-height="tableheight"
            :cell-class-name="cell"> 
            <el-table-column
            fixed                 
            prop= "nodename"
            label= "#name"
            width="100"
            show-overflow-tooltip
            >              
            </el-table-column>       
            <el-table-column
            v-for="(item,index_) in nodeAttriTableheader"        
            :prop= "item.prop"
            :label= "item.label"
            width="120"
            show-overflow-tooltip
            >
          </el-table-column> 
          </el-table>
        </div>              
      </div>
      <div class="detail-info-box-mouse-over"></div>  <!--悬浮节点信息框中的cell,弹出的信息框,操作在nodeInfoView.vue中-->
      
      <div id="interest-attributes-mainview">
        <focusattributesselection :callback="callbackForInterestAttributes"></focusattributesselection>
      </div>
      <div id="history-quick-access-icon">
         <div class="img-icon-box" id="hist-icon"><!--历史走廊图标-->          
            <img class="img-icon" id="hist-img" width="20" height="20" src="../../static/img/icons-hist.png">  
         </div>
      </div>
      <div id="legend-quick-access-icon">
         <div class="img-icon-box" id="legend-icon"><!--图例图标-->          
            <img class="img-icon" id="legend-img" width="25" height="25" src="../../static/img/legend.svg">  
         </div>
      </div>

      <div id="edgeinfo-see-more-in-mianview">      
     </div> <!--节点信息,查看更多-->
     <div id="legend-box">
         <div id="node-color-legend">
             <span class="legend-title">Node Colors:</span>
             <div id="node-color-legend-svg">
                <svg id="legend-svg" width="250px" :height="legendSvgHeightCtrl">
                  <g transform="translate(10,10)">
                    <circle r="8" :fill="nodeColorSet.basenode"/>                      
                    <text x="10" y="3">nodes</text>
                  </g>               
                  <g transform="translate(10,28)">
                    <circle r="8" :fill="nodeColorSet.focusnodes"/>                      
                    <text v-if="focusNodeNumber < 2"  x="10" y="3">focus node</text>
                    <text v-if="focusNodeNumber > 1" x="10" y="3">focus nodes</text>
                  </g>
                  <g v-if="rightClickExplandNodes.length > 0" transform="translate(10,46)">
                    <circle r="8" :fill="nodeColorSet.explandnode"/>                      
                    <text x="10" y="3">the expanded node</text>
                  </g>
                  <g v-if="rightClickExplandNodes.length > 0" transform="translate(10,64)">
                    <circle r="8" :fill="nodeColorSet.explandNeighbors"/>                      
                    <text x="10" y="3">newly added neighbors</text>
                  </g>
                </svg>
             </div>
             
         </div>
         <div id="highlight-color-legend" v-if="conditionLegendList.length > 0">
           <span class="legend-title">Highlighting Nodes:</span>
           <div id="highlight-color-legend-svg">
             <svg id="highlight-legend-svg" width="250px" :height="legendHighlightingSvgHeightCtrl">
                 <g v-for="(item,index) in conditionLegendList" v-if="item.text !=' | 0'" :transform="'translate(10,' + (10 + index*18).toString() + ')'">
                    <circle r="8" :fill="item.color"/>
                    <circle r="6" fill="white"/>
                    <text class="legend-text" x="10" y="3">{{item.text}}</text>
                 </g>
             </svg>
           </div>
         </div>
         
     </div>
    </div>
</template>

<script>
  // import * as d3 from 'd3'
  import * as d3 from '../../static/js/d3.v4.min.js'
  // import {d3Fisheye} from '../../static/js/fisheye.js'
  import $ from 'jquery'
  import axios from 'axios' // 用于AJAX请求
  // import qs from 'qs' 
  import {vueFlaskRouterConfig} from '../vueFlaskRouterConfig'
  import bus from '../eventbus.js' // 事件总线.
  import "../../static/js/d3-selection-multi.js"  // 从外部的static的js文件夹下导入第三方库.
  // import "../../static/js/jquery.min.js"
  import {jBox} from "../../static/js/jBox.js"
  import nodeinfo from '@/components/nodeInfoComponentForMainView'
  import "../../static/js/jquery.contextMenu.js"
  import "../../static/js/jquery.ui.position.js"  
  import diolayoutsetting from '@/components/layoutSettingsView'
  import focusattributesselection from "@/components/focusAttributesSelection"
  import fuzzball from "fuzzball"

  import {saveAs} from "../../static/js/FileSaver.min.js" // FileSaver.min.js canvas-toBlob.js
  import "../../static/js/canvas-toBlob.js"
  // import { Loading } from 'element-ui'

  export default{
        name: "mainview",
        data(){

          return {  
              linkedByIndex: {}, // 用于鼠标悬浮事件
              simulation: null, // D3 force的力学模型.                     
              graph: null, // DOI子图.
              explandGraph: null, // 扩展节点+邻居构成的子图.
              focus: null, // 焦点节点id.
              isDirected: false, // 控制图的方向性.
              explandNodeNum: 0, // 扩展节点的最大数量.
              rightClickExplandNodes: [], // fixme: 用于存放被扩展的节点, [id0, id1, ...]
              historyNum: 40, // 保留最近的historyNum个操作.
              radius: 10,
              usesearchFlag: false, // 是否使用搜索框获得graph数据.
              // doubleClickFlag: false, // DOI初始布局过程中不允许双击扩展操作.
              rightClickExplandFlag: false,  // 右键扩展标志位.
              originGraph: null, // 原始graph.
              // originFocus: null, // 原始focus.
              localStore: [], // 全局变量,用于本页面存储.以前使用cookie,但是cookie有大小为4K的限制,以后可以考虑使用indexeddb.
              storageMode:"webDB", // 探索历史存储模式."webDB": 使用indexedDB,大小50MB-125MB之间,使用localforage js API,后端驱动器可以设置为:indexedDB,webSQL,localStorage. localStorage(5MB)
              histImgWidth: "150", // 用于设置探索历史的图像大小.
              histImgHeight: "150",
              totalhist: 0, // 探索历史中图片的总数量.
              visible2: false,
              limitBox: false, // 是否限制D3布局图的大小.
              
              layoutSettings:{
                edgeMode: "line", // 边模式:curve-曲线, line-直线.
                linkLength: 80, // 边的长度. layoutSettings.linkLength
                chargeStrength: -200, // 力导引力度大小.
              },          

              xOffset: -100,  // 悬浮历史图片弹出的信息框的位置.
              yOffset: 380, //350

              clickHistImag: false, // 点击历史图片.
              
              multiple: null,

              nodeColorSet:{basenode:"#FF8700", focusnodes:"#1890ff", explandnode:"#109618", explandNeighbors: "#9966FF", remainingNighborsNum: "white"},  // 节点配色. 前端节点配色: (蓝, #1890ff) (#109618 绿) (#FF8700 橙)
              isClickNodeAtrrExplor: false, // 是否点击节点属性探索图标.

              nodesAttrObj: null, // {id:{field1:[x, x, x, ...], field2:[x, x, x, ...]}, ...}
              
              clickNodeFlag: null, // 点击节点,获得节点的id.             
              doiNodeAttr: null, // DOI图考虑的节点属性,[x, x, ...]              
              nodeAttriTableheader: null,
              nodeNameList: [], //["Mao", "Chen", "cher"], nodeNameList nodeIdList
              nodeIdList:[], // 选中节点,用于属性探索.
              nodeAttriTableData: [], // 用来装节点的属性值.
              tableheight: "200", // 属性探索弹出框中表格的高度.
              attriExplorCellWidth: "500", // 属性探索信息框中表格的单元格的最大宽度设置.
              dynamicAttriExplorList:[],  // 属性探索框中的候选节点列表, [{id:x, tag:x}, ...]
              dynamicConditionExploreList:[], // 属性值构成的条件列表: [{attrValue:"xxx",curNodeId:"13424",curNodeArr:field}, ...]
              dynamicConditionExploreObj:{}, // 一个条件对象:{id0:[], id1:[], ....},与dynamicAttriExplorList一一对应.
              nodeVsColorObj: {}, // 一个对象.与dynamicConditionExploreObj一一对应,用于将颜色与节点对应起来. dynamicConditionExploreObj nodeVsColorObj matchedNodesObj
              matchedNodesObj:{}, // 用于装匹配的节点.
              dynamicAttriExplorNodeIdList: [], // 动态添加节点的id列表.
              conditionLegendList: [], // [{color:x, text:x}, ...]
              isAdjustLayoutSettings: false, // 用于判断是否调节了布局参数.               
              matchedNodesList:[], // 用于装匹配节点.              
              matchedNodesNum: "", //"10 9 8"

              jBoxInstance:{
                hisJbox:null, // 历史走廊弹出窗.
                attriExplorJbox:null, // 属性探索弹出窗.
                nodeDetailJbox:null, // 节点的细节弹窗.
                edgeDetailJbox:null, // 边细节弹出窗.
                doiLayoutSetJbox:null, //DOI图布局参数设置.
                interestAttributes: null, // 焦点的兴趣属性. jBoxInstance.interestAttributes
                legendJbox:null, // 图例. jBoxInstance.legendJbox
              }, // jBox实例.
             
              seemoretargetselector: '#main-view-layout-setting', //seemore弹出框的弹出位置. // $('.mian-view-item-info'), {x: 95, y: 145}
              seemoretargetoffset: {x: -186, y: 80}, //seemore弹出框的位置.
              rightClickNodeGetId: "", // 被右键点击"Add it to the focus set"的节点的id.
              // isdispalymoreThan: false, // 用于判断是否显示大于或等于号.
              nodeAttrType: null, // 节点属性类型对象.{field1:x, field2:x, ...}
              // explandNewEdgeList: [], // 扩展的新边列表 [{source:x, target:x, value:x}, ...]
              explandNewNodeList: [], // 扩展的新节点id列表 [id0, id1, ...]
              explandNewEdgeColor: "#9966FF", // 扩展新边的颜色. 与explandNeighbors同色.
              commonEdgeColor: "grey", // 普通边的颜色．

              mainViewLoadingFlag: false, // svg加载标志位, false: 不加载, true: 加载.
              isExplandNodeForHist: false, // 是否扩展节点,用于判断是否保存当前数据.
              svgForExport: null, // 保存主视图中的svg,用于导出PNG.
              nodeLabelTextMaxLen: 38, // 节点标签的最长字符串限制.
              neighborR: 100, // 被扩展出来的邻居距离被扩展节点的距离,即邻居的布局半径.
              degreeDeviate: 8, //扩展出来的节点的最大邻居偏离X轴正方向的角度.
              // highLightColorList:["#FC03FC", "#33FFCC", "#CCFF00", "#33FF00", "#F06292", "#FF99FF"], // 用于匹配高亮. #F08080
              highLightColorList:["#33FFCC", "#FF3333", "#00FF00", "#8B2323", "#F06292", "#FF99FF"], // 用于匹配高亮. ["#33FFCC", "#FF3333", "#CCFF00", "#996633", "#F06292", "#FF99FF"]
              clickedEdgeIdList: [], // 注意:里面只装一个边的id.
              // d3EventTransform: {}, // 用于保存transform属性值.{x:0, y:0, k:0} 用于记录画布的位置和缩放比例.
              isExpandOnGraph: false, // 是否清除控制面板中的内容.
              nodeGroupForHighlightedMatchingNode: null, // 用于属性值匹配.
              avgRadius: null, // 节点半径的平均值.
              legendSvgHeightCtrl: "36px", // 用于控制svg的高度.
              legendHighlightingSvgHeightCtrl: '0px',
              focusNodeNumber: 0, // 焦点节点的数量

          }
        },
        computed:{          
          // legendSvgWidth: {
          //   get (){
          //       console.log("computed initial out");
          //       if(this.rightClickExplandNodes.length > 0){   
          //         return 250;
          //       }
          //       else{
          //         console.log("computed initial in");
          //         return 250;
          //       } 
          //   }
              
          // },          
          // legendSvgHeight: {
          //   get (){
          //     if(this.rightClickExplandNodes.length > 0){
          //        return 32;
          //     }
          //     else{
          //        return 74;
          //     }
          //   }
            
          // }          
        },
        components:{
          nodeinfo, // 注册组件.
          diolayoutsetting,
          focusattributesselection
        },
        props:{  // 注册SVG的width+height,以便父组件传参数给这个组件.
          width_: {
            type: Number,
            default: 500,
          },
          height_: {
            type: Number,
            default: 500,
          },
        },
        created(){ // 此时已经完成以下配置:
          // 数据观测(data observer)，属性和方法的运算， watch/event 事件回调.所以此出放置bus.$on是可以的,因为watch/event的回调已经完成.所以mounted(){}中的数据可以被及时地监听到.
          console.log("mainview.vue created");
          let this_ = this;
          // this_.nodeAttriTableheader = this_.$store.getters.getAttriSelection;
          bus.$on('explandNodeNum', function (data){
             this_.explandNodeNum = data;             
          }); 
          
          let indexedDB = window.indexedDB || window.webkitIndexedDB || window.mozIndexedDB || window.msIndexedDB;

          if(indexedDB){
              //alert("支持");
              this_.storageMode == "webDB"; // 支持indexedDB,则使用浏览器自带的indexedDB.
          }
          else {
              this_.storageMode == "noWEBDB"; // 不支持indexedDB,则使用全局变量模式.
          }

          if(this_.storageMode == "webDB"){ // 使用webdb,如果程序崩溃则所有历史数据不会丢失.           
            
          }
          else{ // 使用全局变量模式,如果程序崩溃则所有历史数据丢失.
            //this_.localStore = [];
            this_.localStore.splice(0, this_.localStore.length);  // 使用splice不会更改地址.
          }

          bus.$on("sendLayoutSettings", function (dataSetting){
           /*
              chargeStrength: -100, //力导引力大小设置.
              linkLength: 50, // 力导引边长度设置.
              edgeMode: true, // 边的模式: line OR curve, true: line , false: curve.
           */
          this_.isAdjustLayoutSettings = true; // 表明调整了布局参数.
          let data = dataSetting;            
          if(this_.focus){
              if(this_.focus.length > 0){               
                 let useSearchFlag = false; // 决定是否布局稳定后保存到历史中.
                 if(data.edgeMode)
                    this_.layoutSettings.edgeMode = "line";
                 else
                    this_.layoutSettings.edgeMode = "curve";
                 this_.layoutSettings.chargeStrength = data.chargeStrength;
                 this_.layoutSettings.linkLength = data.linkLength; 
                 // console.log("setting this_.originGraph");console.log(this_.originGraph);
                 // for(let i=0; i<this_.originGraph.nodes.length; i++){                   
                 // }
                 this_.originGraph.nodes.forEach(function(item, index){
                  if(item.hasOwnProperty("fx") && item.hasOwnProperty("fy")){
                     item.fx = null;
                     item.fy = null;
                  }
                 });
                 if(this_.$store.state.mainViewGraph.isExplandNodeFlag){ // 如果为true,则说明在当前SVG中扩展节点.
                    bus.$emit("sendGraphData", [this_.originGraph, this_.focus, useSearchFlag, this_.$store.state.mainViewGraph.graphDirection, this_.explandNewNodeList]);
                 }
                 else{ // false, 则说明已经获得了一个新的布局
                    let tempExplandNewNodeList = [];
                    bus.$emit("sendGraphData", [this_.originGraph, this_.focus, useSearchFlag, this_.$store.state.mainViewGraph.graphDirection, tempExplandNewNodeList]);
                 }
                 
              }
            }          

          });
          bus.$on("sendClearAttriExplorState", function(state){
            if(state){
              if(this_.originGraph){
                this_.clearDynamicAttriExplorList();
                this_.clearDynamicConditionExploreList();
                this_.nodeIdList = [];
                this_.nodeNameList = [];
                this_.nodeAttriTableData = []; 
                this_.originGraph = null;             
                // this_.jBoxInstance.hisJbox.close();
                this_.jBoxInstance.attriExplorJbox.close();             
                this_.jBoxInstance.attriExplorJbox.disable(); // 失能,直到布局结束才打开.
                this_.jBoxInstance.nodeDetailJbox.close();
                this_.isExpandOnGraph = false; // 失能,这样在布局后,matching  panel 参数清空.
              }
              
            }                       
          });
          
         bus.$on("sendMainViewLoadingFlag", function (data){
            if(data){
               this_.mainViewLoadingFlag = true; // 开始加载.
               console.log("this_.mainViewLoadingFlag in event");
               console.log(this_.mainViewLoadingFlag);
            }
         });
         bus.$on("sendClearExplandNewNodeListFlag", function (data){
            if(data){
               this_.explandNewNodeList = []; // 清空列表,避免被保存.
            }
         });
         bus.$on("sendHighLightedRing", function (data){
             this_.matchingPanelRestoreNodesHightLight();
         });
         bus.$on("sendClearNodeHighLighting", function (data){ // 切换数据库.
           if(data){
              this_.conditionLegendList.splice(0, this_.conditionLegendList.length); // 清除节点高亮.
              this_.rightClickExplandNodes.splice(0,this_.rightClickExplandNodes.length); // 清空扩展节点对应数组.
              this_.legendSvgHeightCtrl='36px';              
              $("#jBoxLegend").css("display","none"); // 关闭legend弹窗.
           }
         });
         bus.$on("sendFocusNodeNumber", function (data){
            this_.focusNodeNumber = data;
         });
         bus.$on("sendFixNodesCtrolFlag", function (data){
            if(data){ // 拖拉拽一个节点时,其他节点不动.           
                
                this_.graph.nodes.forEach(function (item, index){ // {id:x, name:x, x:x, y:x}
                   item.fx = item.x;
                   item.fy = item.y;
                });
            }
            else{ // 拖拉拽一个节点时,其他节点跟着动.
              // console.log("sendFixNodesCtrolFlag false");
              this_.graph.nodes.forEach(function (item, index){ // {id:x, name:x, x:x, y:x}
                   item.fx = null;
                   item.fy = null;
              });
            }
            
         });                     
                        
        },         
        updated(){
          console.log("mainView updated");
          let this_ = this;
          // this_.highlightMatchedText();
          // this_.MouseOverHighLightEventForAttrExplor(); 
          if(this_.nodeIdList.length > 0){ // 说明已经选中节点,用于属性探索.
            this_.createTagsInCell(); // 待表格更新后,插入数据.
            this_.createConditionExploration();            
            this_.MouseOverHighLightEventForAttrExplor();
            // this_.mouseOverTagCellAttriExplor(); // 鼠标悬浮属性值,探索条件中对应的标签也高亮.
            // this_.hightLightClickAttriVal();
            this_.hightLightClickAttriValMultiple();
            this_.mouseOverTagConditionVal();
            // console.log("mainView updated nodeIdList");
            this_.colorDivBorder();
            this_.tooltipMouseOverLegend(); // 悬浮图例子,显示文本.
          }       
        },        
        methods: {
          
          nodeHighlightedWithHalo(node, matchingNodeList, ringStroke){
              d3.selectAll(".arc-g").remove(); // 先擦除先前的高亮
              var tau = 2 * Math.PI; // http://tauday.com/tau-manifesto
              var arc = null;
              // var ringStroke = ringStroke; // the size of a ring
              let offset; // 偏离节点半径
              if(this.$store.state.mainViewGraph.isDirected){ // 有向.
                 offset = 6; // 偏离节点半径设置大些,避免挡住箭头.
              }
              else{
                 offset = 2; // 偏离节点半径
              }
              for(var i=0; i<matchingNodeList.length; i++){
                  var tempObj = matchingNodeList[i]; // {id:x, data:[{value:1, color:x}]}
                  var id = tempObj.id;
                  var data = tempObj.data;
                  let g = node.filter((d) => {
                    // console.log("radius jingjing d");console.log(d);
                    if(d.id == id){
                      arc = d3.arc()
                        .innerRadius(d.r + offset)
                        .outerRadius(d.r + offset + ringStroke)
                        .endAngle(tau);
                    }                    
                    return d.id == id;

                  })
                  .append("g").attr("class", "arc-g");

                  var pie = d3.pie()
                    .sort(null)
                    .value(function(d) {
                      return d.value;
                    });
                  g.selectAll(".arc")
                    .data(pie(data))
                    .enter()
                    .append("path")
                    .attr("class", "arc")
                    .style("fill", function(d) {
                      return d.data.color;
                    })
                    .attr("d", arc);
              }

          },
          getMatchingData(finalMatchNodes, highLightColorList){
             var finalMatchNodesKeysList = Object.keys(finalMatchNodes);
             var allMatchingNodeSet = new Set();
             for(var i=0; i<finalMatchNodesKeysList.length; i++){
                var key = finalMatchNodesKeysList[i];
                var tempList = finalMatchNodes[key];
                tempList.forEach(function(d){
                  allMatchingNodeSet.add(d);
                });

             }
             var allMatchingNodeList = Array.from(allMatchingNodeSet);             
             var intersectionForMatchingNodesList = allMatchingNodeList;
             var matchingNodeList = [];
             for(var i=0; i<intersectionForMatchingNodesList.length; i++){
                var nodeId = intersectionForMatchingNodesList[i];
                var tempData = [];
                finalMatchNodesKeysList.forEach(function (item, index){
                  var selectedNodeId = item;
                  var selectedNodeVsMatchingNodeList = finalMatchNodes[selectedNodeId];
                  if(selectedNodeVsMatchingNodeList.indexOf(nodeId) != -1){ // 在里面.
                     tempData.push({value:1, color: highLightColorList[selectedNodeId]});
                  }

                });
                matchingNodeList.push({id: nodeId, data: tempData});
             }          
             return matchingNodeList;
          },
          adjustEdgesOpaticy(){
            // let this_ = this;
            // this.$store.state.mainViewGraph.edgeOpacity
            // let css = {
            //   "font-size": this_.$store.state.mainViewGraph.fontSize.toString() + "px",
            //   "font-weight": this_.$store.state.mainViewGraph.fontWeight.toString()        
            // };
          },
          adjustFontSizeInSvg(){
            let this_ = this;
            let css = {
              "font-size": this_.$store.state.mainViewGraph.fontSize.toString() + "px",
              "font-weight": this_.$store.state.mainViewGraph.fontWeight.toString()        
            };        
            $("#mainsvg .nodes text").css(css); // 改变字体.
          },
          tooltipMouseOverLegend(){
            let this_ = this;
            $(".legend-text").unbind();
            $(".legend-text").mouseover(function(e){                
                 console.log("legend-text e");  console.log(e);
                 let elementText = e.toElement.innerHTML; // 元素的文本.
                 //获取鼠标位置函数
                let mousePos = this_.mousePosition(e);
                let  xOffset = 0;
                let  yOffset = 48;
                $(".legend-info").css("display","block").css("position","absolute")
                .css("top",(mousePos.y - yOffset) + "px")
                .css("left",(mousePos.x + xOffset) + "px");
                let stringHtml="<span>%s</sapn>";                                              
                let html = this_.sprintf(stringHtml, elementText);
                $(".legend-info").append(html);
                console.log("mousePos e");  console.log(mousePos);
                 console.log("html e");  console.log(html);

             });
            $(".legend-text").mouseout(function(){
                $(".legend-info").empty();
                $(".legend-info").css("display","none");                
            });
          },
          matchingPanelRestoreNodesHightLight(){
            let this_ = this;
            let keysList = this_.dynamicAttriExplorNodeIdList; // 这样保证有序.
            if(keysList.length > 0){ // 说明开始属性探索.
                // 一旦添加或删除条件,则实时地刷新整个图,然后高亮匹配的节点.
                this_.clearHighLight(); // 清除高亮. dynamicConditionExploreObj
                // let keysList = Object.keys(curVal); // [id0, id1, id2, ...]                
                for(let i=0; i<keysList.length; i++){             
                   let conditionsList = this_.dynamicConditionExploreObj[keysList[i]]; // [{id:x, tag:x}, ...]
                   let finalMatchNodes = this_.matchNodesforConditions(conditionsList); // 依据条件匹配满足条件的节点.             
                   this_.matchedNodesObj[keysList[i]] = finalMatchNodes; // {id0:[], id1:[], ...}
                   this_.nodeVsColorObj[keysList[i]] = this_.highLightColorList[i]; // 颜色映射: {id0: color0, id1: color1, id2: color2, ...}
                   // this_.highLightNodesOnMatchedNodesMultiple(finalMatchNodes, this_.highLightColorList[i]); // 高亮匹配节点.
                   let matchingNodeList = this_.getMatchingData(this_.matchedNodesObj, this_.nodeVsColorObj);            
                   this_.nodeHighlightedWithHalo(this_.nodeGroupForHighlightedMatchingNode, matchingNodeList, this_.$store.state.mainViewGraph.strokeWidth); 
                }
                this_.$store.state.mainViewGraph.dynamicConditionExploreObj = this_.dynamicConditionExploreObj; // {id0:[x, x], id1:[x,x], id2:[x,x,x]}
            }
            
          },
          indexOfMax(arr) {
              if (arr.length === 0) {
                  return -1;
              }

              var max = arr[0];
              var maxIndex = 0;

              for (var i = 1; i < arr.length; i++) {
                  if (arr[i] > max) {
                      maxIndex = i;
                      max = arr[i];
                  }
              }

              return maxIndex;
          },
          orderForArray(yearArr, idArr){
             let orderIdArr = [];
             let orderYear = [];

             let newYearArr = yearArr.slice();

             for(let i=0; i<newYearArr.length; i++){
                let maxIndex = this.indexOfMax(newYearArr);
                let maxVal = newYearArr[maxIndex];
                newYearArr[maxIndex] = 0;

                orderYear.push(maxVal);
                orderIdArr.push(idArr[maxIndex]);
             }
             return {orderIdArr: orderIdArr, orderYear: orderYear};
          },
          initAbstract(){
            let coll = $("#edgeinfo-see-more-in-mianview .collapsible");    
            for(let i=0; i<coll.length; i++){
              coll[i].addEventListener("click", function() {
                this.classList.toggle("active");
                let content = this.nextElementSibling;
                if (content.style.display === "block") {
                  content.style.display = "none";
                } else {
                  content.style.display = "block";
                }
              });
            }
          },
           colorDivBorder(){
             let this_ = this;
             // console.log("this_.nodeVsColorObj");console.log(this_.nodeVsColorObj);
             let keysList = Object.keys(this_.nodeVsColorObj); // [id0, id1, ...]
             for(let i=0; i<keysList.length; i++){
               let key = keysList[i];
               let css = {
                    "border-color": this_.nodeVsColorObj[key]
               };
              $("#" + "macth-panel-condition-" + key).css(css); // 点击节点,用黑色圆圈圈起来. 
             }
             
           },
           initClickExportSvgToPng(width, height){
              let this_ = this;
              $("#export-main-view-svg-img").click(function(e){
                var svgString = this_.getSVGString(this_.svgForExport.node());
                this_.svgString2Image(svgString, 2*width, 2*height, 'png', function(dataBlob, filesize){
                  saveAs(dataBlob, 'mainView.png'); // FileSaver.js function
                }); // passes Blob and filesize String to the callback                
              });
              
           },
           svgString2Image(svgString, width, height, format, callback) {
            var format = format ? format : 'png';

            var imgsrc = 'data:image/svg+xml;base64,'+ btoa(unescape(encodeURIComponent(svgString))); // Convert SVG string to data URL

            var canvas = document.createElement("canvas");
            var context = canvas.getContext("2d");

            canvas.width = width;
            canvas.height = height;

            var image = new Image();
            image.onload = function() {
              context.clearRect ( 0, 0, width, height );
              context.drawImage(image, 0, 0, width, height);

              canvas.toBlob( function(blob) {
                var filesize = Math.round( blob.length/1024 ) + ' KB';
                if ( callback ) callback( blob, filesize );
              });

              
            };

            image.src = imgsrc;
           },
           getSVGString(svgNode) {
              svgNode.setAttribute('xlink', 'http://www.w3.org/1999/xlink');
              var cssStyleText = getCSSStyles(svgNode);
              appendCSS(cssStyleText, svgNode);

              var serializer = new XMLSerializer();
              var svgString = serializer.serializeToString(svgNode);
              svgString = svgString.replace(/(\w+)?:?xlink=/g, 'xmlns:xlink='); // Fix root xlink without namespace
              svgString = svgString.replace(/NS\d+:href/g, 'xlink:href'); // Safari NS namespace fix

              return svgString;

              function getCSSStyles(parentElement) {
                var selectorTextArr = [];

                // Add Parent element Id and Classes to the list
                selectorTextArr.push( '#'+parentElement.id );
                for (var c = 0; c < parentElement.classList.length; c++)
                    if ( !contains('.'+parentElement.classList[c], selectorTextArr) )
                      selectorTextArr.push( '.'+parentElement.classList[c] );

                // Add Children element Ids and Classes to the list
                var nodes = parentElement.getElementsByTagName("*");
                for (var i = 0; i < nodes.length; i++) {
                  var id = nodes[i].id;
                  if ( !contains('#'+id, selectorTextArr) )
                    selectorTextArr.push( '#'+id );

                  var classes = nodes[i].classList;
                  for (var c = 0; c < classes.length; c++)
                    if ( !contains('.'+classes[c], selectorTextArr) )
                      selectorTextArr.push( '.'+classes[c] );
                }

                // Extract CSS Rules
                var extractedCSSText = "";
                for (var i = 0; i < document.styleSheets.length; i++) {
                  var s = document.styleSheets[i];

                  try {
                      if(!s.cssRules) continue;
                  } catch( e ) {
                        if(e.name !== 'SecurityError') throw e; // for Firefox
                        continue;
                      }

                  var cssRules = s.cssRules;
                  for (var r = 0; r < cssRules.length; r++) {
                    if ( contains( cssRules[r].selectorText, selectorTextArr ) )
                      extractedCSSText += cssRules[r].cssText;
                  }
                }


                return extractedCSSText;

                function contains(str,arr) {
                  return arr.indexOf( str ) === -1 ? false : true;
                }

              }

              function appendCSS(cssText, element) {
                var styleElement = document.createElement("style");
                styleElement.setAttribute("type","text/css");
                styleElement.innerHTML = cssText;
                var refNode = element.hasChildNodes() ? element.children[0] : null;
                element.insertBefore( styleElement, refNode );
              }
           },
           getNowFormatDate(){ // 获得系统的当前时间,用于记录历史探索信息.
                var date = new Date();
                var strMonth = date.getMonth() + 1;
                var strDate = date.getDate();
                var strHour = date.getHours();
                var strMin = date.getMinutes();
                var strSec = date.getSeconds();
                if (strMonth >= 1 && strMonth <= 9) {
                    strMonth = "0" + strMonth;
                }
                if (strDate >= 0 && strDate <= 9) {
                    strDate = "0" + strDate;
                }
                if (strHour >= 0 && strHour <= 9) {
                    strHour = "0" + strHour;
                }
                if (strMin >= 0 && strMin <= 9) {
                    strMin = "0" + strMin;
                }
                if (strSec >= 0 && strSec <= 9) {
                    strSec = "0" + strSec;
                }
                var currentdate = date.getFullYear() + '-'
                        + strMonth + '-'
                        + strDate + ' '
                        + strHour + ':'
                        + strMin + ':'
                        + strSec;
                return currentdate; // 返回一个字符串,用于保存到历史中.
          },          
          callbackForInterestAttributes(){
             let this_ = this;
             let node_id = this_.rightClickNodeGetId;
             let css = {
                    "stroke-dasharray":0,
                    "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.rightClickAsFocus,
                    "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
              };
              $("#mainsvg #" + node_id).css(css); // 点击节点,用颜色圆圈圈起来.                           
              
              let dbName = this_.$store.state.selection.selectiondb; // 取出节点对应的数据库名称
              // let param = {"nodeId": node_id, "dbName": dbName}; // 传递参数.                 
              let path = vueFlaskRouterConfig.mainViewNodeInfo + dbName + "/" + node_id; // 路径
              // console.log("path");console.log(path);
              axios.get(path) // todo:向python后台发送GET请求,这里不能使用post,原因未知.
                  .then((res) => { 
                    let tabledata = res.data;  // {id, name, institution, num_papers, num_citation, H_index, P_index, UP_index, interests}
                    // console.log("tabledata");console.log(tabledata);

                    let dbname = this_.$store.state.selection.selectiondb; // 数据库名称.
                    // let field =  this_.$store.state.selection.selectionfield; // 数据库表字段.
                    // let keyword = this_.$store.state.selection.keyword; // 数据库表字段对应的关键字.
                    let focusObj = {"id": node_id,  // id作为唯一标识,
                                    // "tag": tag, // tag作为节点的标签.
                                    "dbname":dbname,
                                    "field":"NULL", // 写成NULL没有影响.
                                    "keyword": "NULL", // 这么写没有影响.
                                    "attriselect": this_.$store.state.focusAttributesSelection.checkedFocusAttri
                                    };
                    let row = {}; // {field1: value, ...}
                    for(let i=0; i<tabledata.length; i++){
                      let tempObj = tabledata[i]; // 临时对象.{key:x, value:x}
                      if (tempObj.key == "name") {
                        focusObj.tag = tempObj.value;
                      }
                      row[tempObj.key] = tempObj.value;
                    }
                    // console.log("row");console.log(row);

                    let attributesValue = {};
                    let keysRow = Object.keys(row); // 获得键列表. [field1, ...]         
                    let keysType = this_.$store.state.fields.fieldsType; // 字段类型.{字段:类型,...}                                   
                    for(let i=0; i<keysRow.length; i++){
                       let key_ = keysRow[i]; // 键
                       let type_ = keysType[key_]; // 类型
                       let computedAttri = this_.$store.state.focusAttributesSelection.checkedFocusAttri;
                       if(computedAttri.indexOf(key_) != -1){ // 属于被考虑的属性.
                         attributesValue[key_] = row[key_];
                       }           
                        
                    }

                    focusObj.attributesValue = attributesValue; // 添加属性及其值.
                    // console.log("focusObj");console.log(focusObj);
                    //bus.$emit("sendSelectedFocus", focusObj);
                    bus.$emit("sendSlectedNode", focusObj); //该事件能避免重复添加.
                    this_.jBoxInstance.interestAttributes.close();

              })
              .catch((error) => {           
                console.error(error);
              });
          },
          isDisplayLabelNodes(){
            let this_ = this;
            let labelFlag = this_.$store.state.layoutSettingsView.labelDisplay; //用样式控制是否显示标签.          
            if(labelFlag){ // true
              $("#main-view-for-graph .svg-container .nodes text").css("display", "block");
            }
            else{ // false
               $("#main-view-for-graph .svg-container .nodes text").css("display", "none");
            }
          },
          initDeleteMainViewSvg(){ //删除主视图中的图.
            $("#delete-main-view-svg-img").click(function(e){
                $("svg#mainsvg > *").remove(); // 清除svg中旧的内容.
                let doiGraphInfo = {};               
                doiGraphInfo.numnodes = 0;
                doiGraphInfo.numedges = 0;
                doiGraphInfo.directed = false;
                bus.$emit("sendDoiGraphInfo", doiGraphInfo);
            });
          },
          toolipIconHist(){ //历史走廊上方导航栏,图标提示.
            $('.histNav .hist-nav-icon #allhistdel img').jBox('Mouse', { // jBox在本文件中并没有引入,但是也能用(在mainView.vue中引入了).
              theme: 'TooltipDark',
              content: 'Delete all histories',
              zIndex:1005, //可以这样修改z-index
              position: {
                x: 'left',
                y: 'bottom'
              },
            });
          },                       
          css(a) { // 获得一个指定元素的所有css样式.
              var sheets = document.styleSheets, o = {};
              for (var i in sheets) {
                  var rules = sheets[i].rules || sheets[i].cssRules;
                  for (var r in rules) {
                      if (a.is(rules[r].selectorText)) {
                          o = $.extend(o, this.css2json(rules[r].style), this.css2json(a.attr('style')));
                      }
                  }
              }
              return o;
          },

          css2json(css) {
            var s = {};
            if (!css) return s;
            if (css instanceof CSSStyleDeclaration) {
                for (var i in css) {
                    if ((css[i]).toLowerCase) {
                        s[(css[i]).toLowerCase()] = (css[css[i]]);
                    }
                }
            } else if (typeof css == "string") {
                css = css.split("; ");
                for (var i in css) {
                    var l = css[i].split(": ");
                    s[l[0].toLowerCase()] = (l[1]);
                }
            }
            return s;
          },
        
          hightLightClickAttriValMultiple(){ // 高亮在表格中选中的属性值标签.
              let this_ = this; 
              console.log("hightLightClickAttriValMultiple");             
              let keysList = Object.keys(this_.dynamicConditionExploreObj); // [x, xx, xxx]
              for(let i=0; i<keysList.length; i++){
                 let key = keysList[i];
                 let condList = this_.dynamicConditionExploreObj[key]; // [{}, ...]
                 condList.forEach(function(item, index){
                   let elId = item.elementId; // item={} "1234_institutions_9"
                   let nodeId = elId.split("_")[0];
                   let highlightedColor = this_.nodeVsColorObj[nodeId];
                   let css = {
                        "border-width":"2px",
                        "border-color": highlightedColor, // 这样颜色与框框保持一致.
                        "cursor":"pointer"
                      };
                   $("#" + elId).css(css); // 高亮表格中选中的标签
                });
              }
          },
          mouseOverTagConditionVal(){ // 鼠标悬浮属性值构成的条件,以标签形式呈现,对应的标签高亮显示.
            let this_ = this;
            if(this_.nodeAttriTableData.length > 0){
                let elementId = "";
                let origStyle = "";
                $(".tag-attri-conditions-box").mouseover(function(e){                
                    elementId = e.currentTarget.id; // span的id.
                    origStyle = this_.css($("#" + elementId));
                    let css = {
                            "border-width":"1px",
                            "border-color":"#33FFCC",
                            "cursor":"pointer"                                              
                          };
                    $("#" + elementId).css(css); // 点击节点,用黑色圆圈圈起来.
                });
                $(".tag-attri-conditions-box").mouseout(function(){
                    // let css = {
                    //          "border":"1px solid rgb(51, 255, 204)"                    
                    //       };
                    $("#" + elementId).css(origStyle); // 点击节点,用黑色圆圈圈起来.
                });
            }          
            
          },
          mouseOverTagCellAttriExplor(){ // 鼠标悬浮表格中的属性值标签.
            let this_ = this;
            // $(".el-tag-node-attri").unbind();  // 注意:首先对元素中原来绑定的事件进行解绑,这样就避免了信息重复输出.
            if(this_.nodeAttriTableData.length > 0){
              let elementId = "";
              let origStyle = "";
              let conditionOrigStyle = "";
              $(".attri-node-tag").mouseover(function(e){
                  elementId = e.target.parentElement.id;                   
                  // origStyle = this_.css($("#" + elementId));                   
                  // console.log("origStyle");console.log(e);
                  // let css = {
                  //         "border-width":"1px",
                  //         "border-color":"#33FFCC",
                  //         "cursor":"pointer"                        
                  //       };
                  // $("#" + elementId).css(css); // 点击节点,用黑色圆圈圈起来.

                  this_.dynamicConditionExploreList.forEach(function(item, index){ // 检查条件中哪个标签被高亮.
                     let elId = item.elementId; // item={} 
                     if(elId == elementId){
                      conditionOrigStyle = this_.css($("#" + elId + "-condition"));
                        let css = {
                            "border-width":"2px",
                            "border-color":"#33FFCC",
                            // "cursor":"pointer"
                          };
                       $("#" + elId + "-condition").css(css); // 点击节点,用黑色圆圈圈起来.
                     }
                  });                  

                  // console.log("parentId mouseover");console.log(parentId);
              });
              $(".attri-node-tag").mouseout(function(){
                  // let css = {
                  //         "border-width":"0px",
                  //         "border-color":"#409EFF",
                  //         // "cursor":"pointer"
                  //       };
                  // $(".el-tag-node-attri").css(origStyle); // 点击节点,用黑色圆圈圈起来.
                  
                  
                  // $("#" + elementId).css(origStyle); // 点击节点,用黑色圆圈圈起来.
                  this_.dynamicConditionExploreList.forEach(function(item, index){
                     let elId = item.elementId; // 
                     if(elId == elementId){
                        // let css = {
                        //     "border-width":"1px",
                        //     "border-color":"#33FFCC",
                        //     // "cursor":"pointer"
                        //   };
                       $("#" + elId + "-condition").css(conditionOrigStyle); // 点击节点,用黑色圆圈圈起来.
                     }
                  });
                    
              });
            }            
           
          },
          matchNodesforConditions(dynamicConditionExploreList){
              // todo:在主视图中,依据属性值构成的条件,动态实时匹配满足条件的节点.             
             let this_ = this;         
             let matchNodesSetList = [];
                
             for(let i=0; i<dynamicConditionExploreList.length; i++){ // [{}, ...], {}:一个条件
                let obj = dynamicConditionExploreList[i]; // 
                /*
                 obj={attrValue:"maotingyun, jjj", // text类型的属性值
                   curNodeId:"13424", // 当前节点的id
                   curNodeArr:field // 所属的属性(字段)
                 }
                */
                let attrValue = obj.attrValue; // 条件,比如:"Data Visualization"
                let curNodeId = obj.curNodeId;
                let curNodeArr = obj.curNodeArr; // 条件对应的节点属性: interests
                 
                this_.nodeAttrType = this_.$store.state.fields.fieldsType; // 这个不能删掉,否则会出错.
                // console.log("this_.$store.state.fields.fieldsType;");console.log(this_.$store.state.fields.fieldsType);  // integer:整型, text:字符串, real:浮点型
                // 以下,以 "dynamic graph visualization" 作为匹配条件为例子.
                if(this_.$store.state.fields.fieldsType[curNodeArr] == "text"){ // 如果是"text"类型则单词级匹配.
                    // this_.isdispalymoreThan = false; // 显示>=.
                    let lowerCasekeyWord = attrValue.toLowerCase(); // 先转换成小写."dynamic graph visualization"
                    let lowerCasekeyWordList = Array.from(new Set(lowerCasekeyWord.split(/,|，|&|\s+/))); // ["dynamic", "graph", "visualziation"]
                    let counterLowerCasekeyWord = 0; // fixme:条件中,有效单词的个数,"dynamic graph visualization"有效词个数是3.
                    let newLowerCasekeyWordList = []; // 非空,非停用词. ["dynamic", "graph", "visualziation"]
                    for(let ii=0; ii<lowerCasekeyWordList.length; ii++){
                      if(lowerCasekeyWordList[ii] != "" && this_.$store.state.mainViewGraph.stopWords.indexOf(lowerCasekeyWordList[ii]) == -1){
                         counterLowerCasekeyWord++; // 加1.
                         newLowerCasekeyWordList.push(lowerCasekeyWordList[ii]); // newLowerCasekeyWordList=[a,b,c,n]
                      }
                    }           
                    // fixme:现在counterLowerCasekeyWord=3, newLowerCasekeyWordList=["dynamic", "graph", "visualziation"]
                    // 兴趣子图视图中的所有节点.
                    let allNodesKeysList = Object.keys(this_.nodesAttrObj); // nodesAttrObj={id:{name:[x], field1:[x,...], field2:[x,...]},...}
                    let matchNodesSet = new Set(); // 属性值匹配上的节点集. 每个条件匹配的节点集.
                    matchNodesSet.add(curNodeId);
                    // 在线遍历图中每个节点.           
                    for(let i=0; i<allNodesKeysList.length; i++){ // allNodesKeysList=[id1, id2, ...] 兴趣子图视图中的所有节点的id列表
                      let nodeId = allNodesKeysList[i]; // 主视图中图的节点id.
                      if(curNodeId != nodeId){ // 避免重复匹配选中的节点.
                          let nodeObj = this_.nodesAttrObj[nodeId]; // 节点id对应的属性对象:{name:[x], field1:[x,...], field2:[x,...]}
                          let attrValList = nodeObj[curNodeArr]; // 对象中指定属性对应的值构成的数组: attrValList=[x, x, ...]
                          // console.log(" nodeId");console.log(nodeId);
                          // console.log(" attrValList");console.log(attrValList);
                          for (let j = 0; j < attrValList.length; j++) { // attrValList=[x, x, ...],例如:["graph visualization", "data visualization", "visual analytics", "data mining"]                           
                            if(attrValList[j] != ""){ // Start
                                let newStr = attrValList[j].toLowerCase(); // 指定的属性的某个取值: "graph visualization"
                                let newStrList = Array.from(new Set(newStr.split(/,|，|&|\s+/))); // 将每个单词分开: ["graph", "visualization"]
                                let newnewStrList = []; // 非空,非停用词.
                                let counterNewStrList = 0;
                                for(let jj=0; jj<newStrList.length; jj++){
                                  if(newStrList[jj] != "" && this_.$store.state.mainViewGraph.stopWords.indexOf(newStrList[jj]) == -1){
                                     counterNewStrList++; // 加1.
                                     newnewStrList.push(newStrList[jj]); // newnewStrList=[ab, cc, fg]
                                  }
                                }
                                // fixme: 现在counterNewStrList=2, newnewStrList=["graph", "visualization"]
                                let commonWordSet = new Set(); // 相同(相似)的单词的集合.
                                
                                for(let eachOne=0; eachOne<newLowerCasekeyWordList.length; eachOne++){ // 条件: ["dynamic", "graph", "visualziation"]
                                   // let reg =  new RegExp(newLowerCasekeyWordList[eachOne]); // // 用模糊匹配来确定是否为相似的词,若是则算作公共的单词.
                                   for(let each=0; each<newnewStrList.length; each++){  // 被匹配节点的一个对应的属性值: ["graph", "visualization"]                            
                                          // if (reg.test(newnewStrList[each]))
                                          // if (newnewStrList[each] == newLowerCasekeyWordList[eachOne]) // 原来的模糊匹配改成完全匹配.
                                          if(fuzzball.token_set_ratio(newnewStrList[each], newLowerCasekeyWordList[eachOne]) > 80) // 将原来的完全匹配改成模糊匹配,避免layouts与layout这样的情况. 比如,"graph"与"data"进行匹配.
                                          { 
                                             commonWordSet.add(newLowerCasekeyWordList[eachOne]); // 匹配比率>80%就算匹配上,将单词放入集合commonWordSet
                                             break; // 单词匹配上则跳出大循环,去判断下一个单词.
                                          }
                                      }                  
                                }
                                // 现在,匹配集合 commonWordSet={"graph", "visualziation"}
                                /*上面的两层循环嵌套实现:
                                    newLowerCasekeyWordList=["University", "California", "Davis"] 有效词有3个单词.
                                    newnewStrList=["Department", "Computer", "University", "California", "Davis", "Shields", "one", "Avenue", "CA"] 有效词有9个单词.                        
                                    commonWordSet=["University", "California", "Davis"] 匹配上3个单词.
                                    commonWordSet满足什么条件时,newLowerCasekeyWordList 与 newnewStrList表达的含义相同,下面就是判断两者是否相似的条件.
                                 */
                                 
                                /*********** 上下兼容版本: {visualization<--匹配-->graph visualization}*************/                                
                                console.log("this_.$store.state.attrNode.fullCompatibilityAtrr");
                                console.log(this_.$store.state.attrNode.fullCompatibilityAtrr);
                                console.log("curNodeArr");console.log(curNodeArr);
                                if(this_.$store.state.attrNode.fullCompatibilityAtrr.indexOf(curNodeArr) != -1){ // 当前属性属于上下兼容的属性. 
                                    console.log("up-down comp");
                                    let matchSize = commonWordSet.size; // 匹配上的词的数量=2                    
                                    let diff = counterLowerCasekeyWord - counterNewStrList; // 输入的匹配条件:"dynamic graph visualziation"有效词数量 - 被匹配节点的一个属性值的有效词数量 = 3 - 2 = 1
                                    let whichOne = 0; //取两者中较小者.                    
                                    if(diff > 0){ // 条件单词数多余被匹配的属性值单词数. 即:
                                      whichOne = counterNewStrList;                                  
                                    }
                                    else{
                                      whichOne = counterLowerCasekeyWord;
                                    }
                                    
                                    let threshold = 0;
                                    if(whichOne > 2){ // 不小于3个单词的时候,大于较小者的一半算是匹配上了.
                                      threshold = whichOne/2.0; // 加一个偏置,这样能够对于 "keywords" 这种属性(一般只有3个左右的有效字符)实现向下兼容.
                                    }
                                    else{ // 不大于2个,则需要完全匹配.
                                      threshold = whichOne;
                                    }
                                    if(matchSize >= threshold){ //如果匹配上的词的数量不小于最小的字符串的一半,则可以认为两个字符串描述的是一个实体.
                                      matchNodesSet.add(nodeId);
                                      break; // 已经确定当前节点是匹配节点,跳出大循环,判断下一个节点.
                                    }
                                }                                

                                /*********** 上下兼容版本 END *************/

                                /**************** 向下兼容版本 ***********/
                                /*
                                   fixme: 改成向下兼容,即: "visualization" --匹配--> "graph visualization" --匹配-->"dynamic graph visualization", 但是, "dynamic graph visualization" --不匹配--> "graph visualization" --不匹配-->"visualization"
                                */

                                else{
                                    console.log("down comp");
                                    let matchSize = commonWordSet.size; // 匹配上的词的数量=2
                                    let whichOne = 0;
                                    whichOne = counterLowerCasekeyWord; // 以匹配条件有效单词数量作为基准.
                                    let threshold = 0;
                                    if(whichOne > 2){ // 不小于3个单词的时候,大于较小者的一半算是匹配上了.
                                      threshold = whichOne/2.0 + 1; // 加一个偏置,这样能够对于 "keywords" 这种属性(一般只有3个左右的有效字符)实现向下兼容.
                                    }
                                    else{ // 不大于2个,则需要完全匹配.
                                      threshold = whichOne;
                                    }
                                    if(matchSize >= threshold){ //如果匹配上的词的数量不小于最小的字符串的一半,则可以认为两个字符串描述的是一个实体.
                                      matchNodesSet.add(nodeId);
                                      break; // 已经确定当前节点是匹配节点,跳出大循环,判断下一个节点.
                                    }
                                }                        
                                
                                
                                /**************** 向下兼容版本 END ***********/
                                
                            } // END
                                               
                          }
                      }              
                    }
                    
                    let matchNodesList = Array.from(matchNodesSet);
                    matchNodesSetList.push(matchNodesList); // [[id1, id2, ...], ...]
                } // end if "text"
                
                else{ // 如果是"integer" or "real"
                    // this_.isdispalymoreThan = true; // 显示>=.
                    let allNodesKeysList = Object.keys(this_.nodesAttrObj); // nodesAttrObj={id:{name:[x], field1:[x,...], field2:[x,...]},...}
                    let matchNodesSet = new Set(); // 属性值匹配上的节点集. 每个条件匹配的节点集.
                    matchNodesSet.add(curNodeId);
                    for(let i=0; i<allNodesKeysList.length; i++){ // allNodesKeysList=[id1, id2, ...] 兴趣子图视图中的所有节点的id列表
                      let nodeId = allNodesKeysList[i]; // 主视图中图的节点id.
                      if(curNodeId != nodeId){ // 避免重复匹配选中的节点.
                         let nodeObj = this_.nodesAttrObj[nodeId]; // {name:[], id:[], n_citation:[], year:[], ...}
                         let attrValNode = parseFloat(nodeObj[curNodeArr][0]); // 每个节点的对应属性的值.
                         let attrValCond = parseFloat(attrValue); // 条件中对应的数值. 都转换成float便于比较.
                         // console.log("attrValCond gggggg"); console.log(attrValCond);
                         if(attrValCond > 0){ //如果>0, 则取 >=
                           
                           if(attrValNode >= attrValCond){ // todo:简单取>=条件值,则匹配上.
                              matchNodesSet.add(nodeId);
                           }
                         }
                         else{ // =0,则取 >
                           if(attrValNode > attrValCond){ // todo:简单取>=条件值,则匹配上.
                              matchNodesSet.add(nodeId);
                           }
                          
                         }
                         // for (let j = 0; j < attrValList.length; j++){
                            
                         // }
                      }
                      
                    }

                    let matchNodesList = Array.from(matchNodesSet);
                    matchNodesSetList.push(matchNodesList); // [[id1, id2, ...], ...]
                }
                     
             
              }
             
              let finalMatchNodes = this_.intersection(matchNodesSetList); // matchNodesSetList=[[],[], ...],取得多个数组的交集,[x,x,...]
              
              return finalMatchNodes;

          },
          highLightNodesOnMatchedNodes(finalMatchNodes, color){
              let this_ = this;
              let css_ = { "stroke-dasharray":0,
                          "stroke": "#fff",
                          "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
              };
              $("#mainsvg .nodecircle").css(css_);  // fixme: 先擦干净,然后再高亮点击节点.
              
              // this_.$store.state.mainViewGraph.attributesExplorNodeHighlight = finalMatchNodes; // 联合条件,最后匹配的节点列表.
              this_.matchedNodesList = finalMatchNodes;
              finalMatchNodes.forEach(function (val, index){ // val=nodeId.                   
                    let css = {
                        "stroke-dasharray":0,
                        "stroke": color, //this_.$store.state.mainViewGraph.highlightColorSheet.clickMatchNodeAttri,
                        "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                    };
                    $("#mainsvg #" + val).css(css); // 点击节点,用黑色圆圈圈起来. 
              });
          },
          clearHighLight(){ // 清除高亮操作.
            let this_ = this;
              let css_ = { "stroke-dasharray":0,
                          "stroke": "#fff",
                          "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
              };
              $("#mainsvg .nodecircle").css(css_);  // fixme: 先擦干净,然后再高亮点击节点.
          },
          highLightNodesOnMatchedNodesMultiple(finalMatchNodes, color){
              let this_ = this;              
              this_.matchedNodesList = finalMatchNodes;
              finalMatchNodes.forEach(function (val, index){ // val=nodeId.                   
                    let css = {
                        "stroke-dasharray":0,
                        "stroke": color, //this_.$store.state.mainViewGraph.highlightColorSheet.clickMatchNodeAttri,
                        "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                    };
                    $("#mainsvg #" + val).css(css); // 点击节点,用黑色圆圈圈起来. 
              });
          },
          intersection() { // 多个数组取交集.
              let result = [];
              let lists;

              if(arguments.length === 1) {
                lists = arguments[0];
              } else {
                lists = arguments;
              }

              for(let i = 0; i < lists.length; i++) {
                let currentList = lists[i];
                for(let y = 0; y < currentList.length; y++) {
                  let currentValue = currentList[y];
                  if(result.indexOf(currentValue) === -1) {
                    let existsInAll = true;
                    for(let x = 0; x < lists.length; x++) {
                      if(lists[x].indexOf(currentValue) === -1) {
                        existsInAll = false;
                        break;
                      }
                    }
                    if(existsInAll) {
                      result.push(currentValue);
                    }
                  }
                }
              }
              return result;
          },
          createConditionExploration(){ // 点击表格中的属性值标签,创建属性值构成的条件用于匹配主视图中满足这个条件的节点,并高亮显示.
            let this_ = this;
            if(this_.nodeAttriTableData.length > 0){
              // console.log("this_.nodeAttriTableData cher cher");
              // console.log(this_.nodeAttriTableData);
              $(".el-tag-node-attri").click(function(e){                           
                let elementId = e.currentTarget.id; // span的id.                
                let attrValue = e.currentTarget.innerText; // 标签上的字符串. "AbBb Cbn,"                       
                
                let curNodeId = e.currentTarget.offsetParent.classList[2]; // 被选中节点的id.
                let curNodeArr = e.currentTarget.offsetParent.classList[3]; // 被选中节点的字段(属性).
                // console.log("el-tag-node-attri elementId");console.log(elementId);
                // console.log("el-tag-node-attri curNodeId");console.log(curNodeId);
                // console.log("el-tag-node-attri curNodeArr");console.log(curNodeArr);
                let isexistence = false; // 是否存在. 确保不重复添加.
               
                for(let i=0; i<this_.dynamicConditionExploreObj[curNodeId].length; i++){
                   if(this_.dynamicConditionExploreObj[curNodeId][i].elementId == elementId){
                      isexistence = true; // 如果true,则存在.
                      break;
                   }
                }
                if(isexistence === false){ // 如果不一样,则添加到数组中.
                  let objDynamicConditionExploreList = {};
                  objDynamicConditionExploreList.elementId = elementId;
                  objDynamicConditionExploreList.attrValue = attrValue;
                  objDynamicConditionExploreList.curNodeId = curNodeId;
                  objDynamicConditionExploreList.curNodeArr = curNodeArr;
                  // this_.dynamicConditionExploreList.push(objDynamicConditionExploreList); // 添加到数组中.
                  this_.dynamicConditionExploreObj[curNodeId].push(objDynamicConditionExploreList); // 将条件存放到对应的位置.
                                      
                }
                
              });
            }             
            
          },
          MouseOverHighLightEventForAttrExplor(){ // 鼠标悬浮选中作为属性探索的节点,主视图中对应的节点高亮显示.
             let this_ = this;
             $(".tag-attri-node-box").unbind();  // 注意:首先对元素中原来绑定的事件进行解绑,这样就避免了信息重复输出.
             $(".tag-attri-node-box").mouseover(function(e){
               let index = parseInt(e.currentTarget.firstChild.id); // 转化成int型.
               let nodeId = this_.dynamicAttriExplorList[index].id; // {id:x, tag:x}
              
               // let attributesExplorNodeHighlight = this_.$store.state.mainViewGraph.attributesExplorNodeHighlight;
               // let nodeIdList = Object.keys(attributesExplorNodeHighlight);
               // if(nodeIdList.length > 0){ // 如果已经开始属性探索.
               //     nodeIdList.forEach(function(item, index){
               //       let hightedNodesList = attributesExplorNodeHighlight[item]; // [id0, id1, ...]
               //       let hightedColor = this_.nodeVsColorObj[item];
               //       for(let ii=0; ii<hightedNodesList.length; ii++){
                        
               //          let css = {
               //          "stroke-dasharray":0,
               //          "stroke": hightedColor,
               //          "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
               //        };
               //        $("#mainsvg #" + hightedNodesList[ii]).css(css); // 节点用对应的颜色高亮.
               //       }
                     
               //    });
               //  }
                let css = {
                    "stroke-dasharray":0,
                    "stroke": "black", // #1890ff
                    "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                };
                $("#mainsvg #" + nodeId).css(css); // 点击节点,用黑色圆圈圈起来.
               
               });
             
             $(".tag-attri-node-box").mouseout(function(){
                  let css_ = {
                          "stroke-dasharray":0,
                          "stroke": "#fff",
                          "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
                  };
                  $("#mainsvg .nodecircle").css(css_);  // fixme: 先擦干净,然后再高亮点击节点.
                  // let attributesExplorNodeHighlight = this_.$store.state.mainViewGraph.attributesExplorNodeHighlight;
                  // let nodeIdList = Object.keys(attributesExplorNodeHighlight);
                 //  if(nodeIdList.length > 0){ // 如果已经开始属性探索.
                 //     nodeIdList.forEach(function(item, index){
                 //       let hightedNodesList = attributesExplorNodeHighlight[item]; // [id0, id1, ...]
                 //       let hightedColor = this_.nodeVsColorObj[item];
                 //       for(let ii=0; ii<hightedNodesList.length; ii++){
                          
                 //          let css = {
                 //          "stroke-dasharray":0,
                 //          "stroke": hightedColor,
                 //          "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                 //        };
                 //        $("#mainsvg #" + hightedNodesList[ii]).css(css); // 节点用对应的颜色高亮.
                 //       }
                       
                 //    });
                 // }
             });
          },
          nodeHighLightRestore(){
              let this_ = this;
              let attributesExplorNodeHighlight = this_.$store.state.mainViewGraph.attributesExplorNodeHighlight;
              let nodeIdList = Object.keys(attributesExplorNodeHighlight);
              if(this_.isAdjustLayoutSettings){                  
                  this_.isAdjustLayoutSettings = false;//关闭.
                  if(nodeIdList.length > 0){ // 如果已经开始属性探索.
                      // console.log("cccccccccccccccjjjjjjjjjjjjjjjjjjj");
                      let css = {
                          "stroke-dasharray":0,
                          "stroke": "#fff",
                          "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
                      };
                      $("#mainsvg .nodecircle").css(css); // 先擦干净.
                      // nodeIdList.forEach(function(item, index){
                      //      let hightedNodesList = attributesExplorNodeHighlight[item]; // [id0, id1, ...]
                      //      let hightedColor = this_.nodeVsColorObj[item];
                      //      for(let ii=0; ii<hightedNodesList.length; ii++){                          
                      //         let css = {
                      //         "stroke-dasharray":0,
                      //         "stroke": hightedColor,
                      //         "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                      //       };
                      //       $("#mainsvg #" + hightedNodesList[ii]).css(css); // 节点用对应的颜色高亮.
                      //      }
                           
                      // });
                      let isSeeMoreBoxOpen = $(".jBoxSeeMoreOfNode").css("display");
                      if(isSeeMoreBoxOpen == "block"){ // 没有关闭
                          // 用黑圈圈定对应的节点.
                          let cssNode = {
                              "stroke-dasharray":0,
                              "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.clickCheckNodeInfo,
                              "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                          };
                          let nodeId = this_.$store.state.mainViewGraph.clickNode2GetId;
                          $("#mainsvg #" + nodeId).css(cssNode); // 对应节点,用黑圈圈起来.
                      }
                      
                }                
              }                           
          },
          sendGraphNodeData(){ // 向后端发送节点数据,请求节点对应属性值.
             let this_ = this;
             let data = this_.originGraph.nodes;
              // 获得计算DOI时用到的属性.
             let keysType = this_.$store.state.fields.fieldsType; // 所有字段及其类型.{字段:类型,...}
             let discardfield = this_.$store.state.attrNode.discardfield; // [x, x, ...], 这是不用考虑的字段.
             let keysRow = Object.keys(keysType); // 获得键列表. [field1, ...] 
             let doiNodeAttr = []; // 计算DOI时,用到的节点属性.
             for(let i=0; i<keysRow.length; i++){
                let key_ = keysRow[i]; 
                // if(keysType[key_] == "text"){
                if(keysType[key_]){                                    
                    if(discardfield.indexOf(key_) == -1)  // key_不在里面.
                    { // TODO: 不取name + id,因为id + name一般只有一个,除非有重名的. && key_ != "authors"
                      doiNodeAttr.push(key_); // 注意:NULL的处理.                 
                    }
                }
             }
             this_.doiNodeAttr = doiNodeAttr;
             let dbName = this_.$store.state.selection.selectiondb; // 数据库的名称.
             let param = {"dbName": dbName, // DB name
                          "graphNodeData": data, // data=[{}, {}, ...]
                          "doiNodeAttr": doiNodeAttr}; // doiNodeAttr=[x, x, x, ...]
             
              axios.post(vueFlaskRouterConfig.mainViewGraphNodesAtrri, {
                param: JSON.stringify(param)
              })
              .then((res) => {                   
                      console.log("后台已经响应graph节点数据!");
                      let data = res.data;  // 通过查询选中焦点,然后用焦点的id获得图数据.
                      // todo: DOI图中所有节点属性数据保存.
                      this_.nodesAttrObj = data; // {id:{field1:[x, x, x, ...], field2:[x, x, x, ...]}, ...} 
                      // console.log("maotingyun this_.nodesAttrObj"); 
                      // console.log(data);      
                      // console.log("this_.nodesAttrObj");console.log(data);
                      this_.matchingPanelRestoreNodesHightLight(); // 开始放在外面,由于响应晚于匹配函数的执行,所以不能匹配,现在等待节点数据返回才执行便能正确匹配上扩展出来的节点.
                })
              .catch((error) => {            
                console.error(error);
              });
          },
          clearDynamicAttriExplorList(){
            this.dynamicAttriExplorList.splice(0, this.dynamicAttriExplorList.length);
            this.dynamicAttriExplorNodeIdList = [];
            
            for(let key in this.dynamicConditionExploreObj){ // 清除对象.
              delete this.dynamicConditionExploreObj[key];
            }

            for(let key in this.nodeVsColorObj){
              delete this.nodeVsColorObj[key];
            }

            for(let key in this.matchedNodesObj){
              delete this.matchedNodesObj[key];
            }
            
          },
          clearDynamicConditionExploreList(){
            this.dynamicConditionExploreList.splice(0, this.dynamicConditionExploreList.length);
          },
          handleClose(tag) {
            let this_ = this;
            // 删除数组中指定的元素.
            this_.dynamicAttriExplorList.splice(this_.dynamicAttriExplorList.indexOf(tag), 1); // array.splice(index,howmany,item1,.....,itemX),splice() 方法用于插入、删除或替换数组的元素。
            
          },
          handleCloseForConditionExplore(tag){
            // 删除数组中指定的元素.
            let this_ = this;
            this_.dynamicConditionExploreList.splice(this_.dynamicConditionExploreList.indexOf(tag), 1);
          },
          handleCloseForConditionExploreObj(tag,key){
            // 删除数组中指定的元素.
            let this_ = this;
            this_.dynamicConditionExploreObj[key].splice(this_.dynamicConditionExploreObj[key].indexOf(tag), 1);
          },
          getAllAttriSelection(){ // 获得属性探索信息框中的表头.
              // let nodeAttriTableheader = [{prop:"nodename", label:"","width":"120"}];
              let nodeAttriTableheader = [];
              let allFocusAttriIterms = this.$store.state.focusAttributesSelection.allFocusAttriIterms; // [x, x, ...]
              for(let i=0; i<allFocusAttriIterms.length; i++){
                let attriObj = {};             
                attriObj.prop = allFocusAttriIterms[i];
                attriObj.label = allFocusAttriIterms[i];
                attriObj["max-width"] = this.attriExplorCellWidth;
                nodeAttriTableheader.push(attriObj);            

              }
              this.nodeAttriTableheader = nodeAttriTableheader;
              // console.log("nodeAttriTableheader jjjjjjjjjjjjjj");console.log(nodeAttriTableheader);
          },
          getAttriSelectionTable(dynamicAttriExplorList, nodeAttriTableData){ //获得属性探索信息框中的表数据.
              let this_ = this;
              this_.nodeNameList = [];
              this_.nodeIdList = [];
              for(let i=0; i<dynamicAttriExplorList.length; i++){
                  let tagObjTemp = dynamicAttriExplorList[i];
                  this_.nodeIdList.push(tagObjTemp.id);
                  this_.nodeNameList.push(tagObjTemp.tag);
              }
              let nodeList = this_.nodeNameList; // ["xxxx", "xxxxx", ...]
              nodeAttriTableData.splice(0,nodeAttriTableData.length); // 清空.
              for(let i=0; i<nodeList.length; i++){
                let tmpObj = {};
                tmpObj.nodename = nodeList[i];
                nodeAttriTableData.push(tmpObj);
                // console.log("nodeAttriTableData jjjjjjjj");
                // console.log(nodeAttriTableData);
             }            
          },          
          resetLayoutSettings(){ // 恢复默认值.             
            // bus.$emit("sendHistLayoutSettings", true);
          },
          doiGraphInfo(data){
            let doiGraphInfo = {};
            let graph = data.graph;
            let directed = data.directed;
            doiGraphInfo.numnodes = graph.nodes.length;
            doiGraphInfo.numedges = graph.links.length;
            doiGraphInfo.directed = directed;
            bus.$emit("sendDoiGraphInfo", doiGraphInfo);  
          },
          sprintf(){  // 用于字符串格式输出.
              var args = arguments,
              string = args[0],
              i = 1;
              return string.replace(/%((%)|s|d)/g, function (m) {
                  // m is the matched format, e.g. %s, %d
                  var val = null;
                  if (m[2]) {
                      val = m[2];
                  } else {
                      val = args[i];
                      // A switch statement so that the formatter can be extended. Default is %s
                      switch (m) {
                          case '%d':
                              val = parseFloat(val);
                              if (isNaN(val)) {
                                  val = 0;
                              }
                              break;
                      }
                      i++;
                  }
                  return val;
              });
          },
          calculateX(tx, ty, sx, sy, radius){
              if(tx == sx) return tx;                 //if the target x == source x, no need to change the target x.
              var xLength = Math.abs(tx - sx);    //calculate the difference of x
              var yLength = Math.abs(ty - sy);    //calculate the difference of y
              //calculate the ratio using the trigonometric function
              var ratio = radius / Math.sqrt(xLength * xLength + yLength * yLength);
              if(tx > sx)  return tx - xLength * ratio;    //if target x > source x return target x - radius
              if(tx < sx) return  tx + xLength * ratio;    //if target x < source x return target x + radius
          },
          calculateY(tx, ty, sx, sy, radius){
              if(ty == sy) return ty;                 //if the target y == source y, no need to change the target y.
              var xLength = Math.abs(tx - sx);    //calculate the difference of x
              var yLength = Math.abs(ty - sy);    //calculate the difference of y
              //calculate the ratio using the trigonometric function
              var ratio = radius / Math.sqrt(xLength * xLength + yLength * yLength);
              if(ty > sy) return ty - yLength * ratio;   //if target y > source y return target x - radius
              if(ty < sy) return ty + yLength * ratio;   //if target y > source y return target x - radius
          },          
          delAllHist(){
            let this_ = this;
            this_.visible2 = false; // 这样才能点击No/Yes后删除弹出框.
            if(this_.storageMode == "webDB"){
                d3.selectAll("#historyGallery #list > *").remove(); // 删除所有图片.
                this_.$keysInStorage().then(function(allKeys) { // 删除所有数据.
                    for(let i=0; i<allKeys.length; i++){
                      this_.$removeItem(allKeys[i]).then(function(){ 
                        // console.log("already removed allKeys[i]");                     
                    });
                    }
                });
                this_.totalhist = $("#list li").length; // 获得图片的数量.
                // this_.usesearchFlag = true; // 使能,这样就可以保存当前布局图.
            }
            else{
              d3.selectAll("#historyGallery #list > *").remove(); // 删除所有图片.
              //this_.localStore = [];
              this_.localStore.splice(0,this_.localStore.length);
              this_.totalhist = $("#list li").length; // 获得图片的数量.
              // this_.usesearchFlag = true; // 使能,这样就可以保存当前布局图.
            }
            
          },
          mousePosition(ev){ 
                ev = ev || window.event; 
                if(ev.pageX || ev.pageY){ 
                    return {x:ev.pageX, y:ev.pageY}; 
                } 
                return { 
                    x:ev.clientX + document.body.scrollLeft - document.body.clientLeft, 
                    y:ev.clientY + document.body.scrollTop - document.body.clientTop 
                }; 
            },
          findkeysfromlocalStore(array){
                let temparray = [];
                for(let i=0;i<array.length;i++){
                  let key = array[i].name;
                  temparray.push(key);
                }
                return temparray;
          },
          findvaluefromlocalStore(name,array){               
                for(let i=0;i<array.length;i++){
                  if(array[i].name == name){
                     return array[i].value;
                  }
                  else{
                    continue;
                  }
                  
                }
                return null;                
          },
          findIndexOfGreatest(array) {
                let greatest;
                let indexOfGreatest;
                for (let i = 0; i < array.length; i++) {
                  if (!greatest || array[i] > greatest) {
                    greatest = array[i];
                    indexOfGreatest = i;
                  }
                }
                return indexOfGreatest; 
          },
          findIndexOfTopN(array, topN){
                let indexOfArr = [];
                if(array.length <= topN){
                   for(let i=0;i<array.length;i++){
                      indexOfArr.push(i);
                   }

                }
                else{
                  for(let i=0; i<topN; i++){
                    let idx = this.findIndexOfGreatest(array);
                    indexOfArr.push(idx)
                    array[idx]=-1; // 应该清成-1,而非0.
                }
                }    
                         
                return indexOfArr;
          },
          isConnected(a, b, isDirected, isConsiderDirecter) {  // isConsiderDirecter是否考虑方向性
            if(isConsiderDirecter){
                if(isDirected) // 只显示有方向性的节点
                {
                   return this.linkedByIndex[a.index + "," + b.index]|| a.index == b.index;  
                }
                else // 显示无方向性的节点
                {
                   return this.linkedByIndex[a.index + "," + b.index] || this.linkedByIndex[b.index + "," + a.index] || a.index == b.index; 
                }
            }
            else{
              return this.linkedByIndex[a.index + "," + b.index] || this.linkedByIndex[b.index + "," + a.index] || a.index == b.index; 
            }
                
                
          },
          fade(node, link, opacity, isDirected=true, svg=null, marker=null, explandNewNodeList=null, isConsiderDirecter, state) {
              let this_ = this;
              return function(d) {  // d 鼠标悬浮处的节点对象, o 所有节点对象.
                //console.log("d....");console.log(d);
                  node.style("stroke-opacity", function(o) { // 节点高亮.
                      // console.log("stroke-opacity this");console.log();
                      let isCon = this_.isConnected(d, o, isDirected, isConsiderDirecter);
                      // let thisOpacity = isCon ? 1 : opacity;  //opacity越小越透明, d + o如果有连接关系
                      // this.setAttribute('fill-opacity', thisOpacity);
                      let thisOpacity = null;
                      if(state == "mouseover"){
                        thisOpacity = isCon ? 1 : 0.1;
                        this.setAttribute('fill-opacity', thisOpacity); // 邻居不透明,其余节点透明.
                      }
                      else{
                        thisOpacity = isCon ? 1 : 1;
                        this.setAttribute('fill-opacity', thisOpacity); // 邻居不透明,其余节点透明.
                      }

                      // 显示标签.
                      if(this_.$store.state.layoutSettingsView.labelDisplay){ // 显示标签.
                        $("#mainsvg .nodes text").css("display", "block"); // 全部显示.
                      }
                      else{ // 不显示标签.
                        if(isCon){ // 连接点显示标签.
                          // console.log("stroke-opacity this");console.log(this.children().last());
                          if(state == "mouseover"){ // mouse离开.
                            $(this).children().last().css("display", "block");
                          }
                          else{
                            $(this).children().last().css("display", "none");
                          }
                          
                        }
                        else{ // 其他点不显示.
                          $(this).children().last().css("display", "none");
                        }

                      }
                      return thisOpacity;
                  });

                  link.style("stroke-opacity", function(o) { // 边高亮. o 所有边{source:{}, target:{}}
                    // if(isConsiderDirecter){
                    //   if(isDirected)  // 只显示有方向性的边
                    //     return o.source === d ? 1 : opacity;
                    //   else  // 显示无方向性的边.
                    //     return o.source === d || o.target === d ? 1 : opacity;
                    // }
                    // else{
                    //   return o.source === d || o.target === d ? 1 : opacity;
                    // }
                    if(isConsiderDirecter){
                        if(isDirected)  // 只显示有方向性的边
                        {
                          if(state === "mouseover"){
                             return o.source === d ? 1 : opacity; // 出度边不透明显示.
                          }
                          if(state === "mouseout"){
                            return o.source === d ? opacity : opacity; // 出度边不透明显示.
                          }                  
                        }
                        else  // 显示无方向性的边.
                        {
                          if(state === "mouseover"){
                             return o.source === d || o.target === d ? 1 : opacity; // 邻居边不透明显示.
                          }
                          if(state === "mouseout"){
                             return o.source === d || o.target === d ? opacity : opacity; // 邻居边不透明显示.
                          }
                        }
                    }
                    else{
                          if(state === "mouseover"){
                             return o.source === d || o.target === d ? 1 : opacity; // 邻居边不透明显示.
                          }
                          if(state === "mouseout"){
                             return o.source === d || o.target === d ? opacity : opacity; // 邻居边不透明显示.
                          }
                    }
                    
                  });
                  if(isDirected){
                    link.each(function(o) { // 每一条边.
                        let source = o.source;
                        let target = o.target;
                        // 之前认为source target是id,其实它们是节点对象{id:x, x:x, y:y, ...}
                        // console.log("source_target");console.log(source);
                        if(explandNewNodeList.indexOf(source.id) != -1 || explandNewNodeList.indexOf(target.id) != -1){ //新边
                          　d3.select(this).attr("marker-end", function (){
                            // console.log("jingjign new edge");
                            return state === "mouseout" || o.source === d || o.target === d ? marker(this_.explandNewEdgeColor) : opacity;
                          });
                        }
                        else{ // 旧边
                            // console.log("jingjign old edge");
                          　d3.select(this).attr("marker-end", function (){
                            return state === "mouseout" || o.source === d || o.target === d ? marker(this_.commonEdgeColor) : opacity;
                          });
                        }
                    });
                    // link.attr('marker-end', o => (opacity === 1 || o.source === d  ? 'url(#resolved)' : opacity)); // 原来的代码, opacity === 1, 保证鼠标移开后,能正常恢复箭头.如果没有这一项则箭头消失.
                    // link.attr('marker-end', o => {// opacity == 1, 表示鼠标离开．
                    // 　　　　let source = o.source;
                    //     let target = o.target;
                    //     if(this_.explandNewNodeList.indexOf(source) != -1 || this_.explandNewNodeList.indexOf(target) != -1){ // 这条边属于新边．
                         
                    //          return opacity === 1 || o.source === d  ? marker(this_.explandNewEdgeColor) : opacity;
                          
                    //     }
                    //     else{　// 不是新边．
                         
                    //          return opacity === 1 || o.source === d  ? marker(this_.explandNewEdgeColor) : opacity;
                    //     }                 　

                    // }); // opacity === 1, 保证鼠标移开后,能正常恢复箭头.如果没有这一项则箭头消失.
                 
                 }                     
                  
              };
          },
          // fixme: 扩展成多个焦点.
          mainviewD3Layout(graph, focus, isDirected, layoutSettings, explandNewNodeList){ // isDirected是否为有向图.
                      let this_ = this;                        
                      $("svg#mainsvg > *").remove(); // 清除svg中旧的内容.                                        
                      
                      // 画布设置
                      let svg = d3.select("svg#mainsvg"),
                          width = svg.attr("width"),
                          height = svg.attr("height");
                      
                      // fixme: 如果是有向图,则绘制箭头. 
                      if(isDirected){ // 如果是有向图. 
                      }  
                      // 边的不透明度              
                      let opacityMouseover = 0.1; // 鼠标悬浮时隐身部分边+节点的不透明度
                      let currentOpacity = this_.$store.state.mainViewGraph.edgeOpacity; // 当前整个图的边的不透明度

                      function marker(color) {
                            
                            if(color.indexOf("#") != -1){ // color里面有#，即十六进制, e.g., "#fff"
                                 svg.append("svg:marker")
                                    .attr("id", color.replace("#", "")) // color的取值只能是十六进制的.
                                    .attr("viewBox", "0 -5 10 10")
                                    .attr("refX", 10)
                                    .attr("refY", 0)                                     
                                    .attr("markerWidth", 5)
                                    .attr("markerHeight", 5)
                                    .attr("orient", "auto")
                                    .attr("markerUnits", "userSpaceOnUse")
                                    .append("svg:path")
                                    .attr("d", "M0,-5L10,0L0,5")
                                    .attr("opacity", 0.6)
                                    .style("fill", color);

                                 return "url(" + color + ")";
                            }
                            else{ // color里面没有#，即字符串，e.g., "blue"
                                  svg.append("svg:marker")
                                    .attr("id", color) // color的取值只能是十六进制的.
                                    .attr("viewBox", "0 -5 10 10")
                                    .attr("refX", 10)
                                    .attr("refY", 0)
                                    .attr("markerWidth", 5)
                                    .attr("markerHeight", 5)
                                    .attr("orient", "auto")
                                    .attr("markerUnits", "userSpaceOnUse")
                                    .append("svg:path")
                                    .attr("d", "M0,-5L10,0L0,5")
                                    .attr("opacity", 0.6)
                                    .style("fill", color);

                                 return "url(#" + color + ")";
                            }
                            
                      }
                      // 颜色配置
                      let color = d3.scaleOrdinal(d3.schemeCategory20);
                       
                      // 力导引参数配置.
                      let forceLink = d3.forceLink().id(function (d) {
                                            return d.id;
                                        })
                                        .distance(function (d) {
                                            // let numNodes=this_.graph.nodes.length; // 节点数量
                                            // if numNodes % 100
                                            return layoutSettings.linkLength;
                                        });
                                        // .strength(0.1);                       
                                        
                      this_.simulation = d3.forceSimulation()
                          // .force("link", d3.forceLink().id(function(d) { return d.id; }))
                          .force("link", forceLink)
                          .force("charge", d3.forceManyBody().strength(layoutSettings.chargeStrength))  // +表示吸引力, -表示排斥力, 当边的长度变大时,应当增大排斥力, -150
                          //  .force("charge", d3.forceManyBody().strength(function (d, i) {
                          //     var a = i == 0 ? -2000 : -1000;
                          //     return a;
                          // }).distanceMin(5).distanceMax(10))
                          .force("center", d3.forceCenter(width / 2, height / 2));
                        
                        // TODO: 开始将axios.get()放在这里,造成无法布局的问题.
                        this_.graph = graph;
                        this_.focus = focus;  // this_.focus
                        
                        console.log("开始图布局"); 
                        // console.log(this_.graph);  // 当nodes数量>90时候无法布局,找原因. 
                          
                        let g = svg.append("g")
                                   .attr("class", "everything")
                                   .attr("transform", function (){
                                      if(Object.keys(this_.$store.state.mainViewGraph.d3EventTransform).length > 0){ // 已经被缩放了.
                                          let k = this_.$store.state.mainViewGraph.d3EventTransform.k;
                                          let x = this_.$store.state.mainViewGraph.d3EventTransform.x;
                                          let y = this_.$store.state.mainViewGraph.d3EventTransform.y;
                                          let transformVal = "translate(" + x.toString() + "," + y.toString() + ") " + "scale(" + k.toString() + ")";
                                          return transformVal;
                                      }
                                      else{
                                        return "";
                                      }
                                   });               
                        
                        let link=null;
                        if(isDirected){ //如果有向. 
                          if(layoutSettings.edgeMode == "curve"){ // 曲边
                              // 创建边
                              link = g.append("g")
                                      .attr("class", "links")         
                                      // .selectAll("line")
                                      .selectAll("path")
                                      .data(this_.graph.links)
                                      // .enter().append("line")
                                      .enter().append("path")
                                      // .attr('marker-end','url(#resolved)');
                                      // .attr('marker-end','url(#blue)');
                                      // .attr("class", "interest-subgraph-link")
                                      .each(function(d) {
                                        let source = d.source;
                                        let target = d.target;
                                        if(explandNewNodeList.indexOf(source) != -1 || explandNewNodeList.indexOf(target) != -1){
                                          　d3.select(this).attr("marker-end", marker(this_.explandNewEdgeColor));
                                        }
                                        else{
                                          　d3.select(this).attr("marker-end", marker(this_.commonEdgeColor));
                                        }
                                      });
                                      
                              link.style('fill', 'none')
                                  .attr("class", "source-link-target") // 原来是attr,现改成style
                                  .attr("id", function(d){
                                         let source = d.source;
                                         let target = d.target;
                                         return "link-" + source + "-" + target;
                                      }) 
                                  .style("stroke", function(d) { // d={source:x, target:x, value:x} 原来是attr,现改成style
                                        
                                         let source = d.source;
                                         let target = d.target;
                                         // console.log("target");console.log(target);
                                         // console.log("this_.explandNewNodeList");console.log(this_.explandNewNodeList);
                                         if(explandNewNodeList.indexOf(source) != -1 || explandNewNodeList.indexOf(target) != -1){ // 判断是否属于新边,如果是新边,则换颜色.
                                           // console.log("jingjing");
                                           return this_.explandNewEdgeColor;

                                         }
                                         else{
                                           return this_.commonEdgeColor;
                                         }                                        
                                     
                                       }
                                  ) // 边的颜色
                                  .style('stroke-opacity', currentOpacity)
                                  .style("stroke-width", function(d) { return Math.sqrt(d.value); }); // 边的粗细
                          }
                          
                          if(layoutSettings.edgeMode == "line"){ //直边
                              // 创建边
                              link = g.append("g")
                                      .attr("class", "links")         
                                      .selectAll("line")                                      
                                      .data(this_.graph.links)
                                      .enter().append("line")                                      
                                      // .attr('marker-end','url(#resolved)')                                       
                                      .each(function(d) { // 为每一条边的箭头自定义颜色.
                                        let source = d.source;
                                        let target = d.target;
                                        
                                        if(explandNewNodeList.indexOf(source) != -1 || explandNewNodeList.indexOf(target) != -1){
                                          　d3.select(this).attr("marker-end", marker(this_.explandNewEdgeColor));
                                        }
                                        else{
                                          　d3.select(this).attr("marker-end", marker(this_.commonEdgeColor));
                                        }
                                        
                                      })
                                      .attr("class", "source-link-target") // 原来是attr,现改成style
                                      .attr("id", function(d){
                                         let source = d.source;
                                         let target = d.target;
                                         return "link-" + source + "-" + target;
                                      }) 
                                      .style("stroke", function(d) { // d={source:x, target:x, value:x} 原来是attr,现改成style
                                        
                                         let source = d.source;
                                         let target = d.target;
                                         // console.log("target");console.log(target);
                                         // console.log("this_.explandNewNodeList");console.log(this_.explandNewNodeList);
                                         if(explandNewNodeList.indexOf(source) != -1 || explandNewNodeList.indexOf(target) != -1){ // 判断是否属于新边,如果是新边,则换颜色.
                                           // console.log("jingjing");
                                           return this_.explandNewEdgeColor;

                                         }
                                         else{
                                           return this_.commonEdgeColor;
                                         }                                        
                                     
                                       }
                                      ) // 边的颜色
                                      .style('stroke-opacity', currentOpacity)
                                      .style("stroke-width", function(d) { return Math.sqrt(d.value); }); // 原来是attr,现改成style
                               
                          }
                          
                        }
                        else{ // 无向图

                          if(layoutSettings.edgeMode == "curve"){ // 曲线模式
                             link = g.append("g")
                                      .attr("class", "links")    
                                      .selectAll("path")
                                      .data(this_.graph.links)                                      
                                      .enter().append("path");          
                                       
                             link.style('fill', 'none')
                                 .attr("class", "source-link-target") // 原来是attr,现改成style
                                 .attr("id", function(d){
                                         let source = d.source;
                                         let target = d.target;
                                         return "link-" + source + "-" + target;
                                      }) 
                                 .style("stroke", function(d) { // d={source:x, target:x, value:x} 原来是attr,现改成style
                                        
                                         let source = d.source;
                                         let target = d.target;
                                         // console.log("target");console.log(target);
                                         // console.log("this_.explandNewNodeList");console.log(this_.explandNewNodeList);
                                         if(explandNewNodeList.indexOf(source) != -1 || explandNewNodeList.indexOf(target) != -1){ // 判断是否属于新边,如果是新边,则换颜色.
                                           // console.log("jingjing");
                                           return this_.explandNewEdgeColor;

                                         }
                                         else{
                                           return this_.commonEdgeColor;
                                         }                                        
                                     
                                       }
                                ) // 边的颜色
                                .style('stroke-opacity', currentOpacity)
                                .style("stroke-width", function(d) { return Math.sqrt(d.value); });

                          }
                          if(layoutSettings.edgeMode == "line"){ // 直线模式
                             link = g.append("g")
                                    .attr("class", "links")         
                                      .selectAll("line")                                      
                                      .data(this_.graph.links)
                                      .enter().append("line") 
                                      .attr("class", "source-link-target")                                    
                                      .attr("id", function(d){
                                         let source = d.source;
                                         let target = d.target;
                                         return "link-" + source + "-" + target;
                                      }) // 原来是attr,现改成style "source-link-target"
                                      .style("stroke", function(d) { // d={source:x, target:x, value:x} 原来是attr,现改成style
                                        
                                         let source = d.source;
                                         let target = d.target;
                                         // console.log("target");console.log(target);
                                         // console.log("this_.explandNewNodeList");console.log(this_.explandNewNodeList);
                                         if(explandNewNodeList.indexOf(source) != -1 || explandNewNodeList.indexOf(target) != -1){ // 判断是否属于新边,如果是新边,则换颜色.
                                           // console.log("jingjing");
                                           return this_.explandNewEdgeColor;

                                         }
                                         else{
                                           return this_.commonEdgeColor;
                                         }                                        
                                     
                                        }
                                      ) // 边的颜色
                                      .style('stroke-opacity', currentOpacity)
                                      .style("stroke-width", function(d) { return Math.sqrt(d.value); }); // // 原来是attr,现改成style

                          }
                          
                        }
                        
                        // for(let i=0; i<this_.graph.nodes.length; i++){
                        //    let nodeObj = this_.graph.nodes[i];
                        //    let nodeRadius = nodeObj.r;
                        // }
                        let nodeRadiusList = [];
                        let nodeRemainingNeighborList = [];
                        this_.graph.nodes.forEach(function(item, index){
                            nodeRadiusList.push(item.r);
                            nodeRemainingNeighborList.push(item.num_remaining_neighbours);                            
                        });
                        // 找出最小的节点半径.
                        // console.log("nodeRadiusList");console.log(nodeRadiusList);
                        let nodeMinRadius = Math.min.apply(null, nodeRadiusList); // 节点半径的最小值.
                        let nodeMaxReaminingNeighbor = Math.max.apply(null, nodeRemainingNeighborList); // 剩余邻居的最大值.
                        // 创建节点
                        let node = g.append("g")
                                      .attr("class", "nodes")  // .attr("class", "nodes")
                                      .selectAll("g")
                                      .data(this_.graph.nodes)
                                      .enter().append("g")
                                      .attr("class", "node_g"); // 用<g>管理每个节点
                        
                        this_.nodeGroupForHighlightedMatchingNode = node;
                        // 节点形状
                        let circles = node.append("circle")
                                          .attr("class", "nodecircle")
                                          .attr("id", function(d){
                                               return d.id;  // 以节点id作为circle标签的id.
                                          })
                                          .attr("r", function(d){ // 节点半径
                                              return d.r;                            
                                            
                                          })
                                          .attr("stroke-width", 0)
                                          .attr("fill", function(d) { 
                                                //if(d.id == this_.focus){ // 焦点
                                                if(this_.focus.indexOf(d.id) != -1){ // 属于焦点.
                                                  
                                                  return this_.nodeColorSet.focusnodes;
                                                }
                                                
                                                if(this_.rightClickExplandNodes.length > 0){ // 被扩展点 非空.

                                                   for(let i=0; i<this_.rightClickExplandNodes.length; i++){
                                                      if(d.id == this_.rightClickExplandNodes[i]){
                                                         return this_.nodeColorSet.explandnode;
                                                      }
                                                      else{
                                                         continue;
                                                      }
                                                   }
                                                }
                                                // 属于当前被扩展出来的邻居节点,则填充某种颜色.
                                                if(explandNewNodeList.indexOf(d.id) != -1){ // 当前被扩展出来的邻居.
                                                  return this_.nodeColorSet.explandNeighbors;
                                                }
                                                return this_.nodeColorSet.basenode;
                                             })
                                          .call(d3.drag()
                                              .on("start", function (d) {
                                                      if (!d3.event.active) this_.simulation.alphaTarget(0.3).restart(); // this_.simulation.stop();
                                                      d.fx = d.x;
                                                      d.fy = d.y;
                                                })
                                              .on("drag", function (d) {
                                                      d.fx = d3.event.x;
                                                      d.fy = d3.event.y;
                                                  })
                                              .on("end", function (d) {
                                                    if (!d3.event.active) this_.simulation.alphaTarget(0);
                                                    // d.fx = null;
                                                    // d.fy = null;
                                                    if(this_.$store.state.layoutSettingsView.fixedNode){ // 如果参数设置fixed: true,可以拖拽固定.
                                                      d.fx = d3.event.x;
                                                      d.fy = d3.event.y;
                                                    }
                                                    else{ // 否则,拖拽不固定.
                                                      // d.fx = null;
                                                      // d.fy = null;
                                                      d.fx = d3.event.x;
                                                      d.fy = d3.event.y;
                                                    }
                                          }));
                        let remainingNeighborsCodedColor = node.append("circle")
                                          .attr("class", "nodecircle-neighbors")                                          
                                          .attr("r", function(d){ // 节点半径
                                              // nodeMinRadius
                                              if(nodeMaxReaminingNeighbor > 1){
                                                 let baseSize = (nodeMinRadius - 2) / nodeMaxReaminingNeighbor;
                                                 return baseSize * d.num_remaining_neighbours; // todo: 找出最小半径的节点. 
                                              }
                                              else{
                                                 //let baseSize = (nodeMinRadius - 2) / nodeMaxReaminingNeighbor;
                                                 return nodeMinRadius * 0.1 * d.num_remaining_neighbours; // todo: 找出最小半径的节点.
                                              }
                                                                         
                                            
                                          })
                                          .attr("stroke-width", 0)
                                          .attr("fill", function(d) { 
                                                return this_.nodeColorSet.remainingNighborsNum;                                               
                                          })
                                          .call(d3.drag() // 不加d3.drag(),则拖动节点会拖动整个图.
                                              .on("start", function (d) {
                                                      if (!d3.event.active) this_.simulation.alphaTarget(0.3).restart();
                                                      d.fx = d.x;
                                                      d.fy = d.y;
                                                })
                                              .on("drag", function (d) {
                                                      d.fx = d3.event.x;
                                                      d.fy = d3.event.y;
                                                  })
                                              .on("end", function (d) {
                                                    if (!d3.event.active) this_.simulation.alphaTarget(0);
                                                    // d.fx = null;
                                                    // d.fy = null;
                                                    if(this_.$store.state.layoutSettingsView.fixedNode){ // 如果参数设置fixed: true,可以拖拽固定.
                                                      d.fx = d3.event.x;
                                                      d.fy = d3.event.y;
                                                    }
                                                    else{ // 否则,拖拽不固定.
                                                      // d.fx = null;
                                                      // d.fy = null;
                                                      d.fx = d3.event.x;
                                                      d.fy = d3.event.y;
                                                    }
                                                }));

                        // 节点标题
                        let　nodeTitle = node.append("title") // 将标题放在标签的前面,这样在this_fade()函数中的标签不显示情况下的代码就不用改.
      　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　　.text(function(d) { 
                                                // return "Number of remaining neighbors:" + d.num_remaining_neighbours + "(" + d.fx + "," + d.fy + ")"; 
                                                return "The number of remaining neighbors:" + d.num_remaining_neighbours;
                                           });　// 显示节点剩余邻居的数量.
                        // 节点标签
                        let lables = node.append("text")  // 显示节点的标签.
                                        .text(function(d) {
                                            if(d.name.length > this_.nodeLabelTextMaxLen){
                                              return d.name.slice(0,this_.nodeLabelTextMaxLen) + "...";
                                            }
                                            else{
                                              return d.name;
                                            }
                                            
                                        })                          
                                        // .attr('x', 10)
                                        .attr('x', function(d){
                                          if(isDirected){ // 有向
                                            return d.r + 6 + this_.$store.state.mainViewGraph.strokeWidth;
                                          }
                                          else{ // 无向
                                            return d.r + 2 + this_.$store.state.mainViewGraph.strokeWidth;
                                          }
                                          
                                        })
                                        .attr('y', 3);
                        this_.adjustFontSizeInSvg(); // 使svg中的字体大小与调整后的保持一致.
                        
                        // TODO: 添加事件.
                        circles.on("click", function(event){ // 节点点击事件.
                            // 添加交互内容
                            let node_id = event.id;
                            this_.clickNodeFlag = node_id; // 将节点id保存到变量中. 
                            let css_ = {
                                "stroke-dasharray":0,
                                "stroke": "#fff",
                                "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
                            };
                            $("#mainsvg .nodecircle").css(css_);  // fixme: 先擦干净,然后再高亮点击节点.
                            // let attributesExplorNodeHighlight = this_.$store.state.mainViewGraph.attributesExplorNodeHighlight;
                            // if(attributesExplorNodeHighlight.length > 0){ // 如果已经开始属性探索.
                            //    attributesExplorNodeHighlight.forEach(function(item, index){
                                      
                            //          let css = {
                            //             "stroke-dasharray":0,
                            //             "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.clickMatchNodeAttri,
                            //             "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                            //           };
                            //           $("#mainsvg #" + item).css(css); // 点击节点,用黑色圆圈圈起来.
                            //   });
                            // }
                            // let attributesExplorNodeHighlight = this_.$store.state.mainViewGraph.attributesExplorNodeHighlight;
                            // let nodeIdList = Object.keys(attributesExplorNodeHighlight);
                            // if(nodeIdList.length > 0){ // 如果已经开始属性探索.
                            //    nodeIdList.forEach(function(item, index){
                            //      let hightedNodesList = attributesExplorNodeHighlight[item]; // [id0, id1, ...]
                            //      let hightedColor = this_.nodeVsColorObj[item];
                            //      for(let ii=0; ii<hightedNodesList.length; ii++){
                                    
                            //         let css = {
                            //         "stroke-dasharray":0,
                            //         "stroke": hightedColor,
                            //         "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                            //         };
                            //         $("#mainsvg #" + hightedNodesList[ii]).css(css); // 节点用对应的颜色高亮.
                            //      }
                                 
                            //   });
                            // }
                            let css = {
                                "stroke-dasharray":0,
                                "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.clickCheckNodeInfo,
                                "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                            };
                            $("#mainsvg #" + node_id).css(css); // 点击节点,用黑色圆圈圈起来.                          
                            let dbName = this_.$store.state.selection.selectiondb; // 取出节点对应的数据库名称
                            // let param = {"nodeId": node_id, "dbName": dbName}; // 传递参数.                 
                            let path = vueFlaskRouterConfig.mainViewNodeInfo + dbName + "/" + node_id; // 路径
                            axios.get(path) // todo:向python后台发送GET请求,这里不能使用post,原因未知.
                                .then((res) => { 
                                  let tabledata = res.data;  // {id, name, institution, num_papers, num_citation, H_index, P_index, UP_index, interests}
                                  
                              bus.$emit("sendNodeInfo", tabledata);
                            })
                            .catch((error) => {            
                              console.error(error);
                            });                         

                        })
                        
                        //原来是circles,只凸显节点,标签正常显示,改成node后,节点及其标签一起凸显.                        
                        .on("mouseover", this_.fade(node, link, opacityMouseover, isDirected, svg, marker, explandNewNodeList, false, "mouseover")).on("mouseout", this_.fade(node, link, currentOpacity, isDirected, svg, marker, explandNewNodeList, false, "mouseout"));
                         
 
                        link.on("click", function(event){
                            // 添加交互内容                       
                            let weightValue = event.value; // 权重值
                            let source = event.source.id; // source id
                            let target = event.target.id; // target id
                            console.log("click link");console.log(event);
                            let linkId = "link-" + source + "-" + target;
                            if(this_.clickedEdgeIdList.length > 0){
                               let edgeId = this_.clickedEdgeIdList[0];
                               this_.clickedEdgeIdList.pop();
                               let css = {                                
                                "stroke": this_.commonEdgeColor                          
                               };
                               $("#mainsvg #" + edgeId).css(css); // 点击节点,用黑色圆圈圈起来.  clickedEdgeIdList 
                               this_.clickedEdgeIdList.push(linkId);
                            }
                            else{
                                this_.clickedEdgeIdList.push(linkId);
                              // // 高亮边,灰色变成其他颜色.
                              //   let css = {                                
                              //       "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.highLinkColor                               
                              //   };
                              //   $("#mainsvg #" + linkId).css(css); // 点击节点,用黑色圆圈圈起来. 
                            }
                            
                            let css = {                                
                                "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.highLinkColor                               
                            };
                            $("#mainsvg #" + linkId).css(css); // 点击节点,用黑色圆圈圈起来. 
                            
                            let dbName = this_.$store.state.selection.selectiondb;
                            let path = vueFlaskRouterConfig.mainViewEdgeDetails + "/" + dbName + "/" + source + "/" + target + "/" + weightValue; // 取出节点对应的数据库名称; // 路径
                            axios.get(path) // 向python后台发送GET请求
                                .then((res) => { 
                                    // let resultData = res.data; // 
                                    // console.log("resultData");console.log(resultData);
                                    let data = res.data;  // 通过查询选中焦点,然后用焦点的id获得图数据.
                                    if(dbName == "co-authorship.db" || dbName == "Coauthor_Visualization.db"){ // todo: publications的定制显示,对于其他的数据则需要另外编写代码来定制显示.这块不太好扩展.
                                      
                                      let allIdsList = Object.keys(data); // [id1, id2, ...], {id:{}, ...}
                                      
                                      let yearList = []; // [2016, 2018, ...] 转化成int类型.
                                      for(let i=0; i<allIdsList.length; i++){
                                        let id = allIdsList[i];
                                        let eachObj = data[id];
                                        yearList.push(parseInt(eachObj.year));
                                      }                
                                      let orderObj = this_.orderForArray(yearList, allIdsList); // {orderIdArr: orderIdArr, orderYear: orderYear}              
                                      let orderId = orderObj.orderIdArr;                
                                      let totalNum = allIdsList.length; // 总的数量.
                                      let tempHtml = "<div class='author-number'><span>Co-authors: %s</span><span>&nbsp&nbsp&nbsp&nbsp&nbsp&nbspnumber: %s</span></div>"; 
                                      let allHtml = this_.sprintf(tempHtml, event.source.name + " & " + event.target.name, String(totalNum));     
                                      for(let i=0; i<orderId.length; i++){
                                        let id = orderId[i];
                                        let obj = data[id];
                                        let title = obj.title;
                                        let authors = obj.authors;
                                        let public_venue = obj.public_venue;
                                        let year = obj.year;
                                        let abstract = obj.abstract;
                                        let html = '<div class="each-one"><h5 class="content">%s. %s</h5><p class="content"><em id="author">%s</em></p><p class="content"><strong id="venue">%s(%s)</strong></p><span class="collapsible"><img src="data:image/gif;base64,R0lGODlhHQAQAOZxAP////98A6urq/Pz89ra2t7e3uDg4NfX18TExPDw8LCwsO3t7f7+/u7u7tbW1uLi4uPj49zc3NTU1MjIyPj4+K+vr5mZmd/f37Gxsevr65iYmN3d3a2trff390tLS3V1ddPT07Kysunq6dvb2+zs7OHh4by8vfHx8aqqqkxMTMnJyc/Pz1ZWVr+/v6+vrZSUlE9PT+Tk5Pv7++bn5o+Pj5OTktnZ2Zubm83Nze/v70lJSUpKSoeIh+De3ebl5JCQj5KSkefo5+Tk47S0tIWFhcrKyuPk44qKire3t6SjooSEhH19ferq6paWlvr6+jExMZKSkqysrOXl5Do6OoCAgGtra6moppOUk7i4uOrr6tHR0cPDw56dnYeHh+Xl5aCgoI2NjImJiefn59/g3/n5+cLDwtna2dbU1L/Av0hISPLy8t3e3evs66SkpLu7u7a2tvf39v///wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAACH/C1hNUCBEYXRhWE1QPD94cGFja2V0IGJlZ2luPSLvu78iIGlkPSJXNU0wTXBDZWhpSHpyZVN6TlRjemtjOWQiPz4gPHg6eG1wbWV0YSB4bWxuczp4PSJhZG9iZTpuczptZXRhLyIgeDp4bXB0az0iQWRvYmUgWE1QIENvcmUgNS4wLWMwNjEgNjQuMTQwOTQ5LCAyMDEwLzEyLzA3LTEwOjU3OjAxICAgICAgICAiPiA8cmRmOlJERiB4bWxuczpyZGY9Imh0dHA6Ly93d3cudzMub3JnLzE5OTkvMDIvMjItcmRmLXN5bnRheC1ucyMiPiA8cmRmOkRlc2NyaXB0aW9uIHJkZjphYm91dD0iIiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RSZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtbG5zOnhtcD0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wLyIgeG1wTU06RG9jdW1lbnRJRD0ieG1wLmRpZDpDRjAzMTUwMzA1OTIxMUUxQkQ2NUREQzk1M0YyNzcxNCIgeG1wTU06SW5zdGFuY2VJRD0ieG1wLmlpZDpDRjAzMTUwMjA1OTIxMUUxQkQ2NUREQzk1M0YyNzcxNCIgeG1wOkNyZWF0b3JUb29sPSJBZG9iZSBQaG90b3Nob3AgQ1M1LjEgV2luZG93cyI+IDx4bXBNTTpEZXJpdmVkRnJvbSBzdFJlZjppbnN0YW5jZUlEPSJ4bXAuZGlkOkZENkY5OEU1NjkwNUUxMTFBMDRERjdGQUMyQkVCRkIwIiBzdFJlZjpkb2N1bWVudElEPSJ4bXAuZGlkOkZENkY5OEU1NjkwNUUxMTFBMDRERjdGQUMyQkVCRkIwIi8+IDwvcmRmOkRlc2NyaXB0aW9uPiA8L3JkZjpSREY+IDwveDp4bXBtZXRhPiA8P3hwYWNrZXQgZW5kPSJyIj8+Af/+/fz7+vn49/b19PPy8fDv7u3s6+rp6Ofm5eTj4uHg397d3Nva2djX1tXU09LR0M/OzczLysnIx8bFxMPCwcC/vr28u7q5uLe2tbSzsrGwr66trKuqqainpqWko6KhoJ+enZybmpmYl5aVlJOSkZCPjo2Mi4qJiIeGhYSDgoGAf359fHt6eXh3dnV0c3JxcG9ubWxramloZ2ZlZGNiYWBfXl1cW1pZWFdWVVRTUlFQT05NTEtKSUhHRkVEQ0JBQD8+PTw7Ojk4NzY1NDMyMTAvLi0sKyopKCcmJSQjIiEgHx4dHBsaGRgXFhUUExIREA8ODQwLCgkIBwYFBAMCAQAAIfkEAQAAcQAsAAAAAB0AEAAAB/+AcXFCLjVdNS4+gouMjY4MUj8mAwADJkBICJqbCDKOjT1gIAAMJAwAIFQQC6ytLRmfi1ZDAAAxUzG1CkW1vQBqGLGCRyMAHB8eHxwAK1++tSchjAGNRBcALywwLC8AEhYAFOIUMhnBiwHUi0kttRtPG7VYb04D9gNk5tPpi2dhEAA64OgAQIySAgMaKGwwwIuCffziwOFCQ8IpBg6WpNBgL4HHBBAeokunLlqZKxZS3uABw0OTBiSYZBGxRqQgkosSKGAzRgUaFQZE3PCQBkqQGUZmmLEZJ6KgBBUMGHgA4YGBEg80pNBBY8MFAxIqTGsE1UCBs2hLGNCwo8oKq2E1hcXJgSKCgwN48Tqw4aDNFrw2tKCQ22HChAgEEismMKIAYgIR3EyQK2gCBwGYM2vGHOUC5UAAOw=="><span class="collapsible-icon-name">Abstract</span></span><div class="collapsible-content"><div class="abstract"><div class="abstract-content">%s</div></div></div></div>';
                                        let newHtml = this_.sprintf(html, String(i+1), title, authors, public_venue, year, abstract);
                                        allHtml += newHtml;
                                      }
                                      $("#edgeinfo-see-more-in-mianview").html(allHtml); // 这个操作不会进入updated里面.插入直接渲染,因此在下面可以调用initSeeMore函数来注册事件.
                                      this_.initAbstract();
                                    }
                                  
                                })
                                .catch((error) => {            
                                  console.error(error);
                                });
                        });

                        // 开始布局 节点+边
                        this_.simulation
                            .nodes(this_.graph.nodes)
                            .on("tick", function() { // tick是一个监听事件, 只要拖动节点就会触发该事件,更新节点+边的坐标
                                // console.log("this_.graph = graph");console.log(this_.graph);                           
                                  if(layoutSettings.edgeMode == "curve"){
                                    link.attr("d", function(d) {                                       
                                       
                                      let sourceX = d.source.x;
                                      let sourceY = d.source.y;
                                      let targetX = d.target.x;
                                      let targetY = d.target.y;

                                      let theta = Math.atan((targetX - sourceX) / (targetY - sourceY));
                                      let phi = Math.atan((targetY - sourceY) / (targetX - sourceX));

                                      let sinTheta = d.source.r * Math.sin(theta);
                                      let cosTheta = d.source.r * Math.cos(theta);
                                      let sinPhi = d.target.r * Math.sin(phi);
                                      let cosPhi = d.target.r * Math.cos(phi);

                                      // Set the position of the link's end point at the source node
                                      // such that it is on the edge closest to the target node
                                      if (d.target.y > d.source.y) {
                                          // sourceX = sourceX + sinTheta;
                                          // sourceY = sourceY + cosTheta;
                                          sourceX = sourceX;
                                          sourceY = sourceY;
                                      }
                                      else {
                                          // sourceX = sourceX - sinTheta;
                                          // sourceY = sourceY - cosTheta;
                                          sourceX = sourceX;
                                          sourceY = sourceY;
                                      }

                                      // Set the position of the link's end point at the target node
                                      // such that it is on the edge closest to the source node
                                      if (d.source.x > d.target.x) {
                                          targetX = targetX + cosPhi;
                                          targetY = targetY + sinPhi;    
                                      }
                                      else {
                                          targetX = targetX - cosPhi;
                                          targetY = targetY - sinPhi;   
                                      }

                                      // Draw an arc between the two calculated points
                                      let dx = targetX - sourceX,
                                          dy = targetY - sourceY,
                                          dr = Math.sqrt(dx * dx + dy * dy);
                                      return "M" + sourceX + "," + sourceY + "A" + dr + "," + dr + " 0 0,1 " + targetX + "," + targetY;
                                    });
                                  }
                                  if(layoutSettings.edgeMode == "line"){                                     

                                      link
                                      .attr("x1", function (d) { return d.source.x; })
                                      .attr("y1", function (d) { return d.source.y; })
                                      .attr("x2", function (d) {
                                          return this_.calculateX(d.target.x, d.target.y, d.source.x, d.source.y, d.target.r);
                                      })
                                      .attr("y2", function (d) {
                                          return this_.calculateY(d.target.x, d.target.y, d.source.x, d.source.y, d.target.r);
                                      });
                                  }                         
                                  

                                  if(this_.limitBox){  // 将D3布局图限制在一个盒子里面.
                                    node
                                      .attr("transform", function(d) {
                                        d.x = Math.max(this_.radius, Math.min(width - this_.radius, d.x));
                                        d.y = Math.max(this_.radius, Math.min(height - this_.radius, d.y));
                                        return "translate(" + d.x + "," + d.y + ")";
                                      });
                                  }
                                  else{  // D3布局图不受限制.
                                    node
                                    .attr("transform", function(d) {
                                        // d.fx = d.x;
                                        // d.fy = d.y;
                                        return "translate(" + d.x + "," + d.y + ")";
                                    });
                                    // node
                                    // .attr("transform", function(d) {
                                    //     return "translate(" + d.fx + "," + d.fy + ")";
                                    // });                                     
                                  }
                                  
                        })                      
                        .on('end', function(){

                            this_.jBoxInstance.attriExplorJbox.enable(); // 可以点击属性探索弹窗.
                            this_.jBoxInstance.doiLayoutSetJbox.enable(); // 可以点击布局设置弹窗.
                            this_.rightClickExplandFlag = true; // 打开右键点击扩展操作.
                            // 布局完成后,执行里面的内容.                       
                            // 保存数据到cookie里面.
                            if(this_.usesearchFlag || this_.isExplandNodeForHist){ // 只有在Focus Set中点击Extract获得的图,才能保存在历史走廊中.
                              
                              /////////////////////////////////////////// 开始历史保存 ////////////////////////////////////////////////////////////////
                              let historyNum = this_.historyNum; // 保留的最大历史数量.
                              console.log(".........end layout................");
                              let curTime = new Date(); // 当前时间,构成历史记录的id部分.             
                              let cookieKey = "cookies" + curTime.getTime();  
                              let html = d3.select("#mainsvg")
                                          .attr("version", 1.1)
                                          .attr("xmlns", "http://www.w3.org/2000/svg")
                                          .node().parentNode.innerHTML;
                              //抓取SVG中的图片作为历史走廊的Thumbnail(缩略图).                        
                              let imgsrc = 'data:image/svg+xml;base64,'+ window.btoa(unescape(encodeURIComponent(html))); //string先转为utf-8,然后转换成base-64编码的AscII
                              // TODO: 要将所有参数(以后会有很多的参数),输入数据都存放到对象里,然后保存到indexedDB中.
                             // 
                              let originFocus = JSON.parse(JSON.stringify(this_.focus));// 子图对应的焦点集,[id0, id1, ...]                               
                              // todo: 现在需要保存兴趣子图的节点.
                              
                              let idNameObj = this_.$store.state.focusSetView.idNameObj; // 保存{id: name, ...}以便悬浮图片显示历史信息.                               
                              let settings = this_.$store.state.widgetView;  // 保存settings面板的参数.
                              let dbName = this_.$store.state.selection.selectiondb;
                              let setInterests = this_.$store.state.focusSetView.setInterests; 
                              let originGraph = this_.originGraph;// 图片对应的图数据.{nodes:[], links:[]}
                              let doiGraphInfo = {};
                              doiGraphInfo.numnodes = originGraph.nodes.length; // 节点数量
                              doiGraphInfo.numedges = originGraph.links.length; // 图的边数量
                              doiGraphInfo.directed = isDirected; // 图的方向性
                              let interestSubgraphNodeList = []; // 兴趣子图节点列表.
                              // 获得当前兴趣子图的所有节点:子图格式:{nodes:[{id:x, name:x}, ...], links:[{source:x, targett:x, value:x}, ...]}
                              for(let i=0; i<originGraph.nodes.length; i++){
                                let obj = originGraph.nodes[i]; // 节点对象.
                                interestSubgraphNodeList.push(obj.id); // id唯一的兴趣子图节点id列表, [id0, id1, ...]
                              }                              
                              // console.log("interestSubgraphNodeList");console.log(interestSubgraphNodeList);
                              let currentTime = this_.getNowFormatDate(); // 获得系统当前时间,用于记录历史时间.
                              let objCookie = {"originFocus": originFocus, "imgSrc": imgsrc, "settings":settings, "directed": isDirected, "dbName": dbName, "idNameObj":idNameObj, "setInterests":setInterests, "doiGraphInfo": doiGraphInfo, "currentTime": currentTime, "interestSubgraphNodeList": interestSubgraphNodeList, "explandNewNodeList": this_.explandNewNodeList, "explandedNodesList": this_.rightClickExplandNodes}; // "originGraph": originGraph, 一定要将数据存放到对象中,否则无法写入cookie.                              
                              
                              let objhis = {"name":cookieKey,"value":objCookie}; // 用全局变量实现.
                              this_.localStore.push(objhis);   // fixme: 保存数据到indexedDB.
                              ////////////////////////////////////////////////// 结束历史保存 /////////////////////////////////////////////////////////
                              
                              if(this_.storageMode == "webDB"){ // 历史保留的第一种模式: 使用IndexedDB浏览器自带的WEB数据库.
                                  this_.$setItem(cookieKey, objCookie, function() { // 由于localForage是异步的,所以要在其异步回调函数里面读取所有键的列表.
                                                                    
                                  this_.$keysInStorage().then(function(allKeys) {
                                    // TODO: 保证图片与cookies一一对应.
                                        
                                        if(allKeys.length > historyNum){ // 如果超出了最大历史记录数量,则将最早的历史记录删除.
                                          
                                          d3.selectAll("#historyGallery #list > " + "#" + allKeys[0]).remove(); // 同时删除前面的图片.
                                          
                                          this_.$removeItem(allKeys[0]).then(function(){ 
                                                console.log("already removed allkeys[0]");                        
                                            });
                                          }
                                        
                                        d3.select("#historyGallery #list").append("li") // 在历史走廊中创建一个li,用于显示当前保存的图片
                                          .attr("id", cookieKey)
                                          .attr("class", "histimgli")
                                          .append("img")
                                          .attr("width", this_.histImgWidth)  
                                          .attr("height", this_.histImgHeight)
                                          .attr("class", "histimg")
                                          .attr("src", imgsrc);
                                        this_.totalhist = $("#list li").length;
                                        $("#"+cookieKey).click(function(e){ // 给新添加的这张图片注册点击事件.
                                           console.log("now click history gallery");
                                           // this_.explandNewNodeList = []; // 先清空扩展节点列表.
                                           this_.initDeleteMainViewSvg(); //点击事件,删除主视图.             
                                           let cookieName = e.currentTarget.id; // 获得当前图片对应的cookie名字.
                                           this_.$getItem(cookieName).then(function(data){ // 点击缩略图恢复数据,并将数据送到后台用于计算图的DOI值.
                                                // let origGraph = data.originGraph;
                                                let origfocus = data.originFocus; // 一旦点击就获取缩略图对应的数据:焦点, 布局参数等数据.
                                                let settings = data.settings;
                                                // 清空双击节点扩展历史.
                                                this_.rightClickExplandNodes.splice(0,this_.rightClickExplandNodes.length);

                                                let dbName = data.dbName;                                  
                                                let setInterests = data.setInterests;  // 保存到store.js中.
                                                let scaleOfSingleFocus = data.settings.scaleOfSingleFocus;
                                                let diffFactor = data.settings.diffFactor;
                                                let UI_factor = data.settings.UIFactor;
                                                let API_factor = data.settings.APIFactor;
                                                let isEdgeAttri = data.settings.isEdgeAttri;
                                                let probRestart = data.settings.probRestart;
                                                let weightAttrNode = data.settings.weightAttrNode;
                                                let interestSubgraphNodeList = data.interestSubgraphNodeList; // 兴趣子图的节点列表.[id0, id1, ...]
                                                let tempExplandNewNodeList = []; // 恢复扩展节点列表.
                                                if(data.explandNewNodeList.length > 0 && data.explandedNodesList.length > 0){
                                                  tempExplandNewNodeList = data.explandNewNodeList; // 恢复扩展节点列表.
                                                }
                                                
                                                let explandedNodesList = data.explandedNodesList; // 恢复被扩展节点列表, [id0, id1, ...]
                                                this_.$store.state.focusSetView.setInterests = data.setInterests;  // 保存到store.js中. 
                                                this_.$store.state.focusSetView.idNameObj = data.idNameObj;  // 保存到store.js中.

                                                if(explandedNodesList){
                                                  for(let i=0; i<explandedNodesList.length; i++){
                                                   this_.rightClickExplandNodes.push(explandedNodesList[i]);
                                                  }
                                                }
                                                

                                                let param = {"setInterests": setInterests, 
                                                             "scaleOfSingleFocus": scaleOfSingleFocus,
                                                             "diffFactor": diffFactor,
                                                             "UI_factor": UI_factor,
                                                             "API_factor": API_factor,
                                                             "isEdgeAttri": isEdgeAttri,
                                                             "probRestart": probRestart,
                                                             "weightAttrNode": weightAttrNode,
                                                             "isClickHist": true, // 点击历史恢复数据
                                                             "interestSubgraphNodeList": interestSubgraphNodeList
                                                             }; // 焦点传递的是[{},...]
                                                console.log("new hist image was stored and now click one");
                                                bus.$emit("sendMainViewLoadingFlag", true); // 发送加载信号. 
                                                axios.post(vueFlaskRouterConfig.mainViewGraph, { // 将数据发送到后台.
                                                  param: JSON.stringify(param)
                                                })
                                                .then((res) => { 
                                                      
                                                        // TODO: 以下是原来发送焦点+节点数量,获得DOI子图数据的代码,以后还要用的.
                                                        console.log("后台已经响应graph数据!");
                                                        console.log("restore graph from history gallery");
                                                        let data = res.data;  // 通过查询选中焦点,然后用焦点的id获得图数据.
                                                        // TODO: 现在是单焦点,以后扩展成多个焦点,改成数组即可.
                                                        // TODO: 用于判断是否使用的是搜索框,如果是的话,在mainview.vue就需要清除双击历史,因为使用搜索框搜索,表示要重新选择焦点进行探索,一切历史都要清除,当然以后扩展到利用探索历史,可以不清除.
                                                        let graph = data.graph; 
                                                        let directed = data.directed;
                                                        let useSearchFlag = false; // 如果为true,则保存布局图,否则不保存.
                                                        // TODO: 现在只用第一个节点作为焦点来做实验.
                                                        // this_.layoutSettings = layoutSettings;
                                                        // let tempExplandNewNodeList = [];
                                                        this_.$store.state.mainViewGraph.isExplandNodeFlag = false; // 先失能该标志量,避免恢复布局后使用旧的扩展列表,出现新边的颜色.
                                                        bus.$emit("sendGraphData", [graph, origfocus, useSearchFlag, directed, tempExplandNewNodeList]); // 在mainView.vue中监听, 定义一个事件sendGraphData,用于分发graph+focus,注意:graph+focu得同时传过去,如果分开传会出现问题. 
                                                        this_.doiGraphInfo(data); // 发送DOI子图信息.
                                                  })
                                                  .catch((error) => {            
                                                    console.error(error);
                                                  });
                                            // let directed = this_.$store.state.mainViewGraph.graphDirection;
                                            // bus.$emit("sendGraphData", [origGraph, origfocus, false, directed]); // 发送图相关的数据,恢复图片对应的布局以及参数.
                                                 bus.$emit("Settings", settings); // 发送保存的settings数据到Settings控制面板. let settings = data.settings;
                                                 bus.$emit("sendDynamicTagsFocus", setInterests.setNodes);
                                                 // bus.$emit("sendHistLayoutSettings", layoutSettings);                                                
                                                 this_.resetLayoutSettings();
                                                 bus.$emit("tabelDataVisible", false);
                                                 this_.$store.state.selection.selectiondb = dbName;                            
                                                 bus.$emit("sendDbName", dbName);
                                                 this_.$store.state.selection.selectionfield = "All"; // 恢复默认
                                                 this_.$store.state.selection.keyword = ''; // 恢复默认

                                            });
                                          
                                                 
                                        });
                                        //hover某处, 显示悬浮框.
                                        $("#"+cookieKey).mouseover(function(e){
                                            let num = $(this).index()+1;   // 当前点击的li元素在一组li中的实际顺序                                
                                            let totalNum = $("#list li").length; // 获得图片的数量.
                                            this_.totalhist = num + "/" + totalNum;
                                            let cookieName = e.currentTarget.id; // 获得图片对应的cookie名字.
                                            //获取鼠标位置函数
                                            let mousePos = this_.mousePosition(e);
                                            let  xOffset = this_.xOffset;
                                            let  yOffset = this_.yOffset;
                                            $(".histInfoContent").css("display","block").css("position","absolute")
                                            .css("top",(mousePos.y - yOffset) + "px")
                                            .css("left",(mousePos.x + xOffset) + "px");
                                            // TODO: 以后添加更加具体的信息.
                                            this_.$getItem(cookieName).then(function(data){
                                            // let origGraph = data.originGraph; 
                                                                                       
                                            let idNameObj = data.idNameObj; 
                                            let settings = data.settings;
                                            let nameHtml = "";
                                            let keyList = Object.keys(idNameObj);
                                            let keySize = keyList.length;
                                            let counter = 0;
                                            for(let key in idNameObj){
                                               counter++;
                                               if(counter < keySize)
                                                  nameHtml += idNameObj[key] + "; ";
                                               else
                                                  nameHtml += idNameObj[key];
                                            }

                                            let doiGraphInfo = data.doiGraphInfo;
                                            let currentTime = data.currentTime;                                           
                                            let stringHtml="<div class='here-hist-info-box'><span>|V|=%s</span>&nbsp&nbsp<span>|E|=%s</span>&nbsp&nbsp<span>%s</span><h4>The Focus Set(%s)</h4><p>%s</p><h4>Settings</h4><p>ctrl_size_subgraph: %s<br>top_n_remaining_neighbors: %s<br>diffusion factor: %s<br>is_interest_edge: %s<br>Weight_UI: %s<br>Weight_API: %s<br>restart_prob: %s<br>weight_matching_edges: %s</p></div>";                                              
                                            let html = this_.sprintf(stringHtml, doiGraphInfo.numnodes,doiGraphInfo.numedges, currentTime, keySize, nameHtml, settings.scaleOfSingleFocus, settings.explandneighbors, settings.diffFactor, settings.isEdgeAttri, settings.UIFactor,settings.APIFactor, settings.probRestart, settings.weightAttrNode);
                                            $(".histInfoContent").append(html);
                                           
                                            });
                                            
                                                
                                         });
                                         //鼠标离开,隐藏悬浮框.
                                         $("#"+cookieKey).mouseout(function(){
                                             $(".histInfoContent").empty();
                                             $(".histInfoContent").css("display","none");
                                             this_.totalhist = $("#list li").length;
                                         });

                                        this_.usesearchFlag = false; // 失能,只有点击Search才使能.
                                        this_.isExplandNodeForHist = false; // 失能,只有再次扩展节点才使能.

                                      });
                                      
                                  }); 
                              }
                              else{// 历史保留的第二种模式: 使用全局变量模式,关闭浏览器历史即删除.
                                                                                            
                                  if(this_.localStore.length > historyNum){
                                     //let listkeys = this_.findkeysfromlocalStore(this_.localStore);
                                     d3.selectAll("#historyGallery #list > " + "#" + this_.localStore[0].name).remove(); // 同时删除前面的图片.
                                     this_.localStore.splice(0,1);//删除index=0的元素.
                                  }
                                  // let listkeys = this_.findkeysfromlocalStore(this_.localStore);
                                  // console.log("listkeys");console.log(listkeys);                            
                                   
                                  // TODO: 保证图片与cookies一一对应.
                                  d3.select("#historyGallery #list").append("li")
                                    .attr("id", cookieKey)
                                    .attr("class", "histimgli")
                                    .append("img")
                                    .attr("width", this_.histImgWidth)  
                                    .attr("height", this_.histImgHeight)
                                    .attr("class", "histimg")
                                    .attr("src", imgsrc);
                                  this_.totalhist = $("#list li").length;
                                  // let data = this_.findvaluefromlocalStore(cookieName,this_.localStore); // 现在使用全局变量.

                                  //    let origGraph = data.originGraph;
                                  //    let origfocus = data.originFocus;
                                  //添加图片点击事件. 
                                  $("#"+cookieKey).click(function(e){
                                    // this_.explandNewNodeList = []; // 先清空扩展节点列表.
                                    this_.initDeleteMainViewSvg(); //点击事件,删除主视图.                               
                                    let cookieName = e.currentTarget.id; // 获得图片对应的cookie名字.                                      
                                    let data = this_.findvaluefromlocalStore(cookieName,this_.localStore); // 现在使用全局变量.
                                    
                                    let settings = data.settings;
                                    // let origGraph = data.originGraph;
                                    let origfocus = data.originFocus;                                     
                                    this_.rightClickExplandNodes.splice(0,this_.rightClickExplandNodes.length);                                     
                                    // let directed = data.directed;
                                    let dbName = data.dbName;
                                    let setInterests = data.setInterests;  // 保存到store.js中.
                                    let scaleOfSingleFocus = data.settings.scaleOfSingleFocus;
                                    let diffFactor = data.settings.diffFactor;
                                    let UI_factor = data.settings.UIFactor;
                                    let API_factor = data.settings.APIFactor;
                                    let isEdgeAttri = data.settings.isEdgeAttri;
                                    let probRestart = data.settings.probRestart;
                                    let weightAttrNode = data.settings.weightAttrNode;
                                    let interestSubgraphNodeList = data.interestSubgraphNodeList; // 获得系统当前时间.                                    
                                    let tempExplandNewNodeList = []; // 恢复扩展节点列表.
                                    if(data.explandNewNodeList.length > 0 && data.explandedNodesList.length > 0){
                                      tempExplandNewNodeList = data.explandNewNodeList; // 恢复扩展节点列表.
                                    }

                                    let explandedNodesList = data.explandedNodesList; // 恢复被扩展节点列表, [id0, id1, ...]
                                    this_.$store.state.focusSetView.setInterests = data.setInterests;  // 保存到store.js中. 
                                    this_.$store.state.focusSetView.idNameObj = data.idNameObj;  // 保存到store.js中.

                                    if(explandedNodesList){
                                      for(let i=0; i<explandedNodesList.length; i++){
                                       this_.rightClickExplandNodes.push(explandedNodesList[i]);
                                      }
                                    }                                               
                                    
                                    let param = {"setInterests": setInterests, 
                                                 "scaleOfSingleFocus": scaleOfSingleFocus,
                                                 "diffFactor": diffFactor,
                                                 "UI_factor": UI_factor,
                                                 "API_factor": API_factor,
                                                 "isEdgeAttri": isEdgeAttri,
                                                 "probRestart": probRestart,
                                                 "weightAttrNode": weightAttrNode,
                                                 "isClickHist": true, // 点击历史恢复数据
                                                 "interestSubgraphNodeList": interestSubgraphNodeList
                                                 }; // 焦点传递的是[{},...]
                                    //let param = {"dbName": this_.selectiondb, "dbfield": this_.selectionfield, "dbfieldvalue": this_.nodeinfo}; //将条件发送到后台,请求匹配的节点数据.
                                    // let layoutSettings = data.layoutSettings;
                                    bus.$emit("sendMainViewLoadingFlag", true); // 发送加载信号. 
                                    axios.post(vueFlaskRouterConfig.mainViewGraph, { // 将数据发送到后台.
                                      param: JSON.stringify(param)
                                    })
                                    .then((res) => { 
                                          
                                            // TODO: 以下是原来发送焦点+节点数量,获得DOI子图数据的代码,以后还要用的.
                                            console.log("后台已经响应graph数据!");
                                            let data = res.data;  // 通过查询选中焦点,然后用焦点的id获得图数据.
                                            // TODO: 现在是单焦点,以后扩展成多个焦点,改成数组即可.
                                            // TODO: 用于判断是否使用的是搜索框,如果是的话,在mainview.vue就需要清除双击历史,因为使用搜索框搜索,表示要重新选择焦点进行探索,一切历史都要清除,当然以后扩展到利用探索历史,可以不清除.
                                            let graph = data.graph; 
                                            let directed = data.directed;
                                            let useSearchFlag = false; // 如果为true,则保存布局图,否则不保存.
                                            // TODO: 现在只用第一个节点作为焦点来做实验.
                                            // this_.layoutSettings = layoutSettings;
                                            // let tempExplandNewNodeList = [];
                                            this_.$store.state.mainViewGraph.isExplandNodeFlag = false; // 先失能该标志量,避免恢复布局后使用旧的扩展列表,出现新边的颜色.
                                            bus.$emit("sendGraphData", [graph, origfocus, useSearchFlag, directed, tempExplandNewNodeList]); // 在mainView.vue中监听, 定义一个事件sendGraphData,用于分发graph+focus,注意:graph+focu得同时传过去,如果分开传会出现问题. 
                                            this_.doiGraphInfo(data); 
                                      })
                                      .catch((error) => {            
                                        console.error(error);
                                      });
                                      bus.$emit("Settings", settings); // 发送保存的settings数据到Settings控制面板. let settings = data.settings;
                                      // bus.$emit("sendHistLayoutSettings", layoutSettings);
                                      this_.resetLayoutSettings();
                                      bus.$emit("sendDynamicTagsFocus", setInterests.setNodes);
                                      bus.$emit("tabelDataVisible", false);
                                      this_.$store.state.selection.selectiondb = dbName;                            
                                      bus.$emit("sendDbName", dbName);
                                      this_.$store.state.selection.selectionfield = "All"; // 恢复默认
                                      this_.$store.state.selection.keyword = ''; // 恢复默认

                                      
                                   });
                                   //hover某处显示悬浮框
                                   $("#"+cookieKey).mouseover(function(e){
                                      let num = $(this).index()+1;// 当前点击的li元素在一组li中的实际顺序                                
                                      let totalNum = $("#list li").length; // 获得图片的数量.
                                      this_.totalhist = num + "/" + totalNum;
                                      let cookieName = e.currentTarget.id; // 获得图片对应的cookie名字.
                                      //获取鼠标位置函数
                                      let mousePos = this_.mousePosition(e);
                                      let  xOffset = this_.xOffset;
                                      let  yOffset = this_.yOffset;
                                      $(".histInfoContent").css("display","block").css("position","absolute")
                                      .css("top",(mousePos.y - yOffset) + "px")
                                      .css("left",(mousePos.x + xOffset) + "px");
                                      // TODO: 以后添加更加具体的信息.
                                      let data = this_.findvaluefromlocalStore(cookieName,this_.localStore); // 现在使用全局变量.
                                                                                   
                                      let idNameObj = data.idNameObj; 
                                      let settings = data.settings;
                                      let nameHtml = "";
                                      let keyList = Object.keys(idNameObj);
                                      let keySize = keyList.length;
                                      let counter = 0;
                                      for(let key in idNameObj){
                                         counter++;
                                         if(counter < keySize)
                                            nameHtml += idNameObj[key] + "; ";
                                         else
                                            nameHtml += idNameObj[key];
                                      }
                                      
                                      let doiGraphInfo = data.doiGraphInfo;
                                      let currentTime = data.currentTime;                                           
                                      // let stringHtml="<div class='here-hist-info-box'><span>|V|=%s</span>&nbsp&nbsp<span>|E|=%s</span>&nbsp&nbsp<span>%s</span><h4>The Focus Set(%s)</h4><p>%s</p><h4>Settings</h4><p>Scale Of Single Focus: %s<br>Number Of Explanded Nodes: %s<br>Diffusion Factor: %s<br>Attribution_Edge_Diffusion: %s<br>UI_Factor: %s<br>API_Factor: %s<br>prob_restart: %s<br>weight_attr_node: %s</p></div>";      
                                      let stringHtml="<div class='here-hist-info-box'><span>|V|=%s</span>&nbsp&nbsp<span>|E|=%s</span>&nbsp&nbsp<span>%s</span><h4>The Focus Set(%s)</h4><p>%s</p><h4>Settings</h4><p>ctrl_size_subgraph: %s<br>top_n_remaining_neighbors: %s<br>diffusion factor: %s<br>is_interest_edge: %s<br>Weight_UI: %s<br>Weight_API: %s<br>restart_prob: %s<br>weight_matching_edges: %s</p></div>";                                     
                                      let html = this_.sprintf(stringHtml, doiGraphInfo.numnodes,doiGraphInfo.numedges, currentTime, keySize, nameHtml, settings.scaleOfSingleFocus, settings.explandneighbors, settings.diffFactor, settings.isEdgeAttri, settings.UIFactor,settings.APIFactor, settings.probRestart, settings.weightAttrNode);
                                      $(".histInfoContent").append(html);
                                          
                                   });
                                   //鼠标离开隐藏悬浮框
                                   $("#"+cookieKey).mouseout(function(){
                                       $(".histInfoContent").empty();
                                       $(".histInfoContent").css("display","none");
                                       this_.totalhist = $("#list li").length; // 获得图片的数量.
                                   });
                                   this_.usesearchFlag = false; // 失能.
                              }
                            
                            }
                            
                            //var img = '<img src="'+imgsrc+'"/>'; // 注意:使用v-bind指令,可以将标签的属性与变量绑定在一起,从而实现动态控制属性的值.
                            // let imgUrl = "/static/img/mty.png";
                            // var img = '<img src="'+imgUrl+'"/>';
                            //d3.select("#svgdataurl_").html(img);
                            
                        });

                        this_.simulation.force("link")
                            .links(this_.graph.links); 
                        //add zoom capabilities 
                      let zoomHandler = d3.zoom()
                                          .on("zoom", function (){                                   
                                            g.attr("transform", d3.event.transform);
                                            this_.$store.state.mainViewGraph.d3EventTransform = d3.event.transform; // 保存d3.event.transform值.
                                            // console.log("this_.d3EventTransform"); console.log(this_.d3EventTransform);                               
                                        });                                                     

                      zoomHandler(svg); // 可以缩放.                       
                      svg.on("dblclick.zoom", null); // fixme:失能双击放大. 
                      // svg.on("wheel.zoom", null) .on("mousewheel.zoom", null) .on("mousemove.zoom", null) .on("DOMMouseScroll.zoom", null);
                      this_.svgForExport = svg; //将svg保存起来,用于导出主要视图的SVG为PNG.

          },
          getGraphNodeSize(graph, baseSize){  // 用于决定节点大小的倍数.
              let this_ = this;
              let nodes = graph.nodes; // [[{'id': '260137', 'name': 'Thomas Ertl', 'value': 0.003416367015654839},...]
              // let nodes = [{'value': 0.003416367015654839}, {'value': 0.103416367015654839}]
              let tempList = [];
              let multiple = 0;
              nodes.forEach(function(i){            
                tempList.push(i.value);
              });
               
              // let maxValue = Math.max.apply(null,tempList);
              let minValue = Math.min.apply(null,tempList);
              // console.log("maxValue");console.log(maxValue);
              console.log("minValue");console.log(minValue);
              if(minValue < 0.0000001){
                multiple = baseSize / 0.000001;
              }
              else{
                multiple = baseSize / minValue;
              }              
              console.log("multiple");console.log(multiple);
              let avgRadiusSizeList = []; // 用于计算平均半径大小
              // 添加节点的半径.
              nodes.forEach(function(i){  // i={id:x, name:x, value:x}           
                if(i.value < 0.0000001){
                  i.r = Math.log(baseSize) / Math.log(2) + 5;
                }
                else{
                  i.r = Math.log(multiple*i.value) / Math.log(2) + 5;
                } 
                avgRadiusSizeList.push(i.r); // [9.8, 9.9, 3.0, ...]                             
              });
              let sum = avgRadiusSizeList.reduce((previous, current) => current += previous);
              this_.avgRadius = Math.round(sum / avgRadiusSizeList.length);
              bus.$emit("sendAvgRadiusFlag", this_.avgRadius); // 算得平均值
              // return multiple
          },
          cell({row, column, rowIndex, columnIndex}) { // 给表格的单元格打class,用于后期的动态插入.
              // console.log("cell({row, column, rowIndex, columnIndex})");console.log(row);
              // console.log(rowIndex);
              //this.nodeNameList与this.nodeIdList一一对应.
              let cellId = "";
              if(column.label == ""){
                 // cellId = row.nodename;
                 cellId = this.nodeIdList[rowIndex];
              }
              else{
                 cellId = this.nodeIdList[rowIndex] + "_" + column.label + " " + this.nodeIdList[rowIndex] + " " + column.label; // id_field.          
              }
              
              return cellId;  // 赋予单元格class.
          },
          fuzzyQuery(list, keyWord, matchList) { // 模糊查询,从字符串中匹配出含有查询项的字符串.
              let lowerCasekeyWord = keyWord.toLowerCase();
              var reg =  new RegExp(lowerCasekeyWord);
              var arr = [];
              for (var i = 0; i < list.length; i++) {
                let newStr = list[i].toLowerCase();
                if (reg.test(newStr)) {
                  // arr.push(list[i]);
                  matchList
                }
              }
              return arr;
          },
          // createClickTagEvent(){
          //   let this_ = this;
          //   $(".el-tag-node-attri").click(function(e){
          //     // console.log("click event");console.log(e);              
          //     let attrValue = e.currentTarget.innerText; // 标签上的字符串. "AbBb Cbn,"
          //     let lowerCasekeyWord = attrValue.toLowerCase(); // 先转换成小写."aabb cbn,"
          //     let lowerCasekeyWordList = Array.from(new Set(lowerCasekeyWord.split(/,|，|&|\s+/))); // [a,b,c,n, ""]
          //     let counterLowerCasekeyWord = 0; // 属性值中有效词,即非空,非停用词的个数.
          //     let newLowerCasekeyWordList = []; // 非空,非停用词.
          //     for(let ii=0; ii<lowerCasekeyWordList.length; ii++){
          //       if(lowerCasekeyWordList[ii] != "" && this_.$store.state.mainViewGraph.stopWords.indexOf(lowerCasekeyWordList[ii]) == -1){
          //          counterLowerCasekeyWord++; // 加1.
          //          newLowerCasekeyWordList.push(lowerCasekeyWordList[ii]); // newLowerCasekeyWordList=[a,b,c,n]
          //       }
          //     }
          //     // console.log("newLowerCasekeyWordList");console.log(newLowerCasekeyWordList);
          //     let className = e.currentTarget.offsetParent.classList[1]; // "1234_institution"
          //     let strArr = className.split("_"); // e.g.["1234", "institution"]
          //     let curNodeId = strArr[0]; // 被选中节点的id.
          //     let curNodeArr = strArr[1]; // 被选中节点的字段(属性).             
               
          //     let allNodesKeysList = Object.keys(this_.nodesAttrObj); // nodesAttrObj={id:{name:[x], field1:[x,...], field2:[x,...]},...}
          //     let matchNodesSet = new Set(); // 属性值匹配上的节点集.
          //     matchNodesSet.add(curNodeId);
          //     // let counterMatchWords = 0; // 匹配词的数量.             
          //     for(let i=0; i<allNodesKeysList.length; i++){ // allNodesKeysList=[id1, id2, ...]
          //       let nodeId = allNodesKeysList[i]; // 主视图中图的节点id.
          //       if(curNodeId != nodeId){ // 避免重复匹配选中的节点.
          //           let nodeObj = this_.nodesAttrObj[nodeId]; // 节点id对应的属性对象:{name:[x], field1:[x,...], field2:[x,...]}
          //           let attrValList = nodeObj[curNodeArr]; // 对象中指定属性对应的值构成的数组:attrValList=[x, x, ...]
          //           for (let j = 0; j < attrValList.length; j++) { // attrValList=[x, x, ...]
          //             let newStr = attrValList[j].toLowerCase(); // 指定的属性的某个取值: "ab, cc fg"                
          //             let newStrList = Array.from(new Set(newStr.split(/,|，|&|\s+/))); // [ab, cc, fg, ""]
          //             let newnewStrList = []; // 非空,非停用词.
          //             let counterNewStrList = 0;
          //             for(let jj=0; jj<newStrList.length; jj++){
          //               if(newStrList[jj] != "" && this_.$store.state.mainViewGraph.stopWords.indexOf(newStrList[jj]) == -1){
          //                  counterNewStrList++; // 加1.
          //                  newnewStrList.push(newStrList[jj]); // newnewStrList=[ab, cc, fg]
          //               }
          //             }
          //             // console.log("newnewStrList");console.log(newnewStrList);
          //             let commonWordSet = new Set(); // 相同(相似)的单词的集合.
                      
          //             for(let eachOne=0; eachOne<newLowerCasekeyWordList.length; eachOne++){
          //                // let reg =  new RegExp(newLowerCasekeyWordList[eachOne]); // // 用模糊匹配来确定是否为相似的词,若是则算作公共的单词.
          //                for(let each=0; each<newnewStrList.length; each++){                              
          //                       // if (reg.test(newnewStrList[each]))
          //                       if (newnewStrList[each] == newLowerCasekeyWordList[eachOne]) // 原来的模糊匹配改成完全匹配.
          //                       { 
          //                          commonWordSet.add(newLowerCasekeyWordList[eachOne]);
          //                          break; // 单词匹配上则跳出大循环,去判断下一个单词.
          //                       }
          //                   }                  
          //             }
          //             /*上面的两层循环嵌套实现:
          //                 newLowerCasekeyWordList=["University", "California", "Davis"] 3个单词.
          //                 newnewStrList=["Department", "Computer", "University", "California", "Davis", "Shields", "one", "Avenue", "CA"] 9个单词.                        
          //                 commonWordSet=["University", "California", "Davis"] 3个单词.
          //                 commonWordSet满足什么条件时,newLowerCasekeyWordList 与 newnewStrList表达的含义相同,下面就是判断两者是否相似的条件.
          //              */
          //             // console.log("commonWordSet");console.log(Array.from(commonWordSet));
          //             // this_.attributesExplorNodeHighlight = Array.from(commonWordSet); // 里面的元素是唯一的.
          //             let matchSize = commonWordSet.size; // 有效词中,公共词的个数.
          //             let whichOne = 0; //取两者中较小者.                    
          //             // let diff = counterLowerCasekeyWord - counterNewStrList;                                        
          //             // if(diff > 0){
          //             //   whichOne = counterNewStrList;
          //             // }
          //             // else{
          //             //   whichOne = counterLowerCasekeyWord;
          //             // }
          //             whichOne = counterLowerCasekeyWord; // 以标签上的属性值的有效词的个数为基准.
          //             let threshold = 0;
          //             if(whichOne > 2){ // 不小于3个单词的时候,大于较小者的一半算是匹配上了.
          //               threshold = whichOne/2.0 + 1;
          //             }
          //             else{ // 不大于2个有效词,则需要完全匹配.
          //               threshold = whichOne;
          //             }
          //             if(matchSize >= threshold){ //如果匹配上的词的数量不小于最小的字符串的一半,则可以认为两个字符串描述的是一个实体.
          //               matchNodesSet.add(nodeId);
          //               break; // 已经确定当前节点是匹配节点,跳出大循环,判断下一个节点.
          //             }                  
          //           }
          //       }              
          //     }
          //     // console.log("matchNodesSet");console.log(matchNodesSet);
          //     // todo: 高亮属性值相同的节点.
          //     let css_ = { "stroke-dasharray":0,
          //                 "stroke": "#fff",
          //                 "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
          //               };
          //     $("#mainsvg .nodecircle").css(css_);  // fixme: 先擦干净,然后再高亮点击节点.
          //     let matchNodesList = Array.from(matchNodesSet);
          //     // this_.attributesExplorNodeHighlight = matchNodesList;
          //     // this_.$store.state.mainViewGraph.attributesExplorNodeHighlight = matchNodesList;
          //     matchNodesSet.forEach(function (val, key){ // val=nodeId.                   
          //       let css = {
          //           "stroke-dasharray":0,
          //           "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.clickMatchNodeAttri,
          //           "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
          //       };
          //       $("#mainsvg #" + val).css(css); // 点击节点,用黑色圆圈圈起来. 
          //     });

          //   });         
          // },
          createTagsInCell(){ // 获得表格数据并且更新后,在单元格中动态插入对应的属性值,以标签形式呈现.
            let nodeIdList = this.nodeIdList;        
            for(let i=0; i < nodeIdList.length; i++){ // 开始的时候写成了nodeIdList.length;出现了一系列的bug.
               let tempId = nodeIdList[i];           
               let tempObj = this.nodesAttrObj[tempId]; // nodesAttrObj = {name:[x], field1:[x], field2:[x], ...}.                       
               let keyList = Object.keys(tempObj); // [x, x, ...]
               for(let j=0; j<keyList.length; j++){
                let key_ = keyList[j];
                 if(key_ != "name"){
                   let elementClass = tempId + "_" + key_;
                   let tempArr = tempObj[key_]; // [x, x, x, ...]
                   let allAttriNodeTag = "";
                   for(let eachVal=0; eachVal<tempArr.length; eachVal++){
                      let tagHtml = '<span id="%s" class="el-tag-node-attri"><span class="attri-node-tag">%s</span></span>'; // 表格单元格中的属性值(标签形式)
                      let value_ = tempArr[eachVal];
                      let tagId_ = tempId + "_" + key_ + "_" + eachVal; // 将标签的id设置成"nodeId_" + key + 序号的形式.
                      let htmlTemp = this.sprintf(tagHtml, tagId_, value_);
                      allAttriNodeTag += htmlTemp;
                   }
                   $("." + elementClass).html(allAttriNodeTag);
                 }             
               }
            }        
            
          }        
          
    },   
    mounted() {      
         let this_ = this;                   
         console.log("mainview.vue mounted");
         this_.tooltipMouseOverLegend();
         if(this_.storageMode == "webDB"){ // 打开页面时加载历史信息: 只有webDB模式才有保留的历史数据.
            this_.$keysInStorage().then(function(allKeys) { // 从IndexedDB中,恢复保存的历史数据,历史走廊中显示历史图片的缩略图.                 
                
                for(let i=0; i<allKeys.length; i++){
                   this_.$getItem(allKeys[i]).then(function(data){
                        // let origGraph = data.originGraph;
                        let origfocus = data.originFocus;
                        let imgSrc = data.imgSrc;
                        let settings = data.settings;
                        let directedG = data.directed;
                        let dbName = data.dbName;                                                                     
                        let idNameObj = data.idNameObj; 
                        
                        let nameHtml = "";
                        let keyList = Object.keys(idNameObj);
                        let keySize = keyList.length;
                        let counter = 0;
                        for(let key in idNameObj){
                           counter++;
                           if(counter < keySize)
                              nameHtml += idNameObj[key] + "; ";
                           else
                              nameHtml += idNameObj[key];
                        }

                        d3.select("#historyGallery #list").append("li")
                          .attr("id", allKeys[i])
                          .attr("class", "histimgli")
                          .append("img")
                          .attr("width", this_.histImgWidth)  
                          .attr("height", this_.histImgHeight)
                          .attr("class", "histimg")
                          .attr("src", imgSrc);
                        this_.totalhist = $("#list li").length; // 获得图片的数量.
                        
                        $("#"+allKeys[i]).click(function(e){ // 给每一张图片绑定一个点击事件.
                          // this_.explandNewNodeList = []; // 先清空扩展节点列表.
                          this_.initDeleteMainViewSvg(); //点击事件,删除主视图.
                          this_.clickHistImag = true;// 已经点击历史图片.
                          this_.$store.state.mainViewGraph.d3EventTransform = {};                                                              
                          let cookieName = e.currentTarget.id; // 获得图片对应的cookie名字.
                          if(cookieName == allKeys[i]){ // 保证每一张图片与存放在indexedDB中的数据一一对应.                            
                            this_.rightClickExplandNodes.splice(0,this_.rightClickExplandNodes.length);                     
                            
                            let setInterests = data.setInterests;  // 保存到store.js中.
                            let scaleOfSingleFocus = data.settings.scaleOfSingleFocus;
                            let diffFactor = data.settings.diffFactor;
                            let UI_factor = data.settings.UIFactor;
                            let API_factor = data.settings.APIFactor;
                            let isEdgeAttri = data.settings.isEdgeAttri;
                            let probRestart = data.settings.probRestart;
                            let weightAttrNode = data.settings.weightAttrNode;
                            let interestSubgraphNodeList = data.interestSubgraphNodeList;
                            let tempExplandNewNodeList = []; // 恢复扩展节点列表.
                            if(data.explandNewNodeList.length > 0 && data.explandedNodesList.length > 0){
                              tempExplandNewNodeList = data.explandNewNodeList; // 恢复扩展节点列表.
                            }

                            let explandedNodesList = data.explandedNodesList; // 恢复被扩展节点列表, [id0, id1, ...]
                            this_.$store.state.focusSetView.setInterests = data.setInterests;  // 保存到store.js中. 
                            this_.$store.state.focusSetView.idNameObj = data.idNameObj;  // 保存到store.js中.

                            if(explandedNodesList){
                              for(let i=0; i<explandedNodesList.length; i++){
                               this_.rightClickExplandNodes.push(explandedNodesList[i]);
                              }
                            }                                          

                            let param = {"setInterests": setInterests, 
                                         "scaleOfSingleFocus": scaleOfSingleFocus,
                                         "diffFactor": diffFactor,
                                         "UI_factor": UI_factor,
                                         "API_factor": API_factor,
                                         "isEdgeAttri": isEdgeAttri,
                                         "probRestart": probRestart,
                                         "weightAttrNode": weightAttrNode,
                                         "isClickHist": true, // 点击历史恢复数据
                                         "interestSubgraphNodeList": interestSubgraphNodeList
                                         };
                            let dbName = data.dbName;                                                                       
                            let dbLoadedFlag = this_.$store.state.infoSearchView.dbLoadedFlag[dbName.slice(0,-3)];                            
                            console.log("mounted selected database click hist image before loading");
                            if(dbLoadedFlag){ // 已经选中了某个数据库,那么点击历史图片,如果数据库不同就会切换数据库.
                                console.log("mounted mounted selected database click hist image loading");
                                bus.$emit("sendMainViewLoadingFlag", true); // 发送加载信号. 
                                axios.post(vueFlaskRouterConfig.mainViewGraph, { // 如果点击缩略图,则将恢复的数据发送给后台用于对应DOI图的计算.
                                  param: JSON.stringify(param)
                                })
                                .then((res) => { 
                                      
                                        // TODO: 以下是原来发送焦点+节点数量,获得DOI子图数据的代码,以后还要用的.
                                        console.log("后台已经响应graph数据!");
                                        let data = res.data;  // 通过查询选中焦点,然后用焦点的id获得图数据.
                                        // TODO: 现在是单焦点,以后扩展成多个焦点,改成数组即可.
                                        // TODO: 用于判断是否使用的是搜索框,如果是的话,在mainview.vue就需要清除双击历史,因为使用搜索框搜索,表示要重新选择焦点进行探索,一切历史都要清除,当然以后扩展到利用探索历史,可以不清除.
                                        let graph = data.graph; 
                                        let directed = data.directed;
                                        let useSearchFlag = false; // 如果为true,则保存布局图,否则不保存.
                                        // TODO: 现在只用第一个节点作为焦点来做实验.
                                        // this_.layoutSettings = layoutSettings;
                                        // let tempExplandNewNodeList = [];
                                        this_.$store.state.mainViewGraph.isExplandNodeFlag = false; // 先失能该标志量,避免恢复布局后使用旧的扩展列表,出现新边的颜色.
                                        bus.$emit("sendGraphData", [graph, origfocus, useSearchFlag, directed, tempExplandNewNodeList]); // 在mainView.vue中监听, 定义一个事件sendGraphData,用于分发graph+focus,注意:graph+focu得同时传过去,如果分开传会出现问题. 
                                        this_.doiGraphInfo(data);
                                  })
                                  .catch((error) => {            
                                    console.error(error);
                                  });
                            }
                            else{ // 数据库选项仍然为空,此时点击历史图片恢复数据.                             
                              bus.$on("dbLoadedState", function(data){ // 放在事件监听里面.
                                if(data){
                                    if(this_.clickHistImag){ // 判断是否点击过历史图片,否则不执行.加上这样的条件后就解决了切换数据库后自动恢复历史走廊中第一张图的bug.
                                        this_.clickHistImag = false;
                                        console.log("mounted database empty click hist image");
                                        bus.$emit("sendMainViewLoadingFlag", true); // 发送加载信号. 
                                        axios.post(vueFlaskRouterConfig.mainViewGraph, { // 如果点击缩略图,则将恢复的数据发送给后台用于对应DOI图的计算.
                                         param: JSON.stringify(param)
                                        })
                                        .then((res) => {
                                              
                                                // TODO: 以下是原来发送焦点+节点数量,获得DOI子图数据的代码,以后还要用的.
                                                console.log("后台已经响应graph数据!");
                                                let data = res.data;  // 通过查询选中焦点,然后用焦点的id获得图数据.
                                                // TODO: 现在是单焦点,以后扩展成多个焦点,改成数组即可.
                                                // TODO: 用于判断是否使用的是搜索框,如果是的话,在mainview.vue就需要清除双击历史,因为使用搜索框搜索,表示要重新选择焦点进行探索,一切历史都要清除,当然以后扩展到利用探索历史,可以不清除.
                                                let graph = data.graph; 
                                                let directed = data.directed;
                                                let useSearchFlag = false; // 如果为true,则保存布局图,否则不保存.
                                                // TODO: 现在只用第一个节点作为焦点来做实验.
                                                // this_.layoutSettings = layoutSettings;
                                                // let tempExplandNewNodeList = [];
                                                this_.$store.state.mainViewGraph.isExplandNodeFlag = false; // 先失能该标志量,避免恢复布局后使用旧的扩展列表,出现新边的颜色.
                                                bus.$emit("sendGraphData", [graph, origfocus, useSearchFlag, directed, tempExplandNewNodeList]); // 在mainView.vue中监听, 定义一个事件sendGraphData,用于分发graph+focus,注意:graph+focu得同时传过去,如果分开传会出现问题. 
                                                this_.doiGraphInfo(data);
                                        })
                                        .catch((error) => {            
                                          console.error(error);
                                        });
                                    }                                    
                                }
                                
                              });                                
                             
                            } 
                            bus.$emit("Settings", settings); // 发送保存的settings数据到Settings控制面板. let settings = data.settings;
                            bus.$emit("sendDynamicTagsFocus", setInterests.setNodes); 
                            // bus.$emit("sendHistLayoutSettings", layoutSettings);
                            this_.resetLayoutSettings();
                            bus.$emit("tabelDataVisible", false);
                            this_.$store.state.selection.selectiondb = dbName;                            
                            bus.$emit("sendDbName", dbName);
                            this_.$store.state.selection.selectionfield = "All"; // 恢复默认
                            this_.$store.state.selection.keyword = ''; // 恢复默认
                            this_.jBoxInstance.hisJbox.close(); // 点击一个历史子图,则关闭历史面板.
                          }                      
                         
                       });                         
                       
                        //hover某处显示悬浮框
                        $("#"+allKeys[i]).mouseover(function(e){
                            let num = $(this).index()+1;   // 当前点击的li元素在一组li中的实际顺序
                            //console.log("num");console.log(num);
                            let totalNum = $("#list li").length; // 获得图片的数量.
                            this_.totalhist = num + "/" + totalNum;         
                            //获取鼠标位置函数
                            let mousePos = this_.mousePosition(e);
                            let  xOffset = this_.xOffset;
                            let  yOffset = this_.yOffset;
                            $(".histInfoContent").css("display","block").css("position","absolute")
                            .css("top",(mousePos.y - yOffset) + "px")
                            .css("left",(mousePos.x + xOffset) + "px");
                            // TODO: 以后添加更加具体的信息.
                             
                            let doiGraphInfo = data.doiGraphInfo;
                            let currentTime = data.currentTime; // 获得历史时间.
                            // let edgeMode = data.layoutSettings.edgeMode;                                           
                           // let stringHtml="<span>|V|=%s</span>&nbsp&nbsp<span>|E|=%s</span><h4>Focus (%s)</h4><p>%s</p><h4>Settings</h4><p>Scale Of Single Focus: %s<br>Number Of Explanded Nodes: %s<br>Diffusion Factor: %s<br>Attribution_Edge_Diffusion: %s<br>UI_Factor: %s<br>API_Factor: %s<br>prob_restart: %s<br>weight_attr_node: %s</p>";    
                           // let stringHtml="<div class='here-hist-info-box'><span>|V|=%s</span>&nbsp&nbsp<span>|E|=%s</span>&nbsp&nbsp<span>%s</span><h4>The Focus Set(%s)</h4><p>%s</p><h4>Settings</h4><p>Scale Of Single Focus: %s<br>Number Of Explanded Nodes: %s<br>Diffusion Factor: %s<br>Attribution_Edge_Diffusion: %s<br>UI_Factor: %s<br>API_Factor: %s<br>prob_restart: %s<br>weight_attr_node: %s</p></div>"; 
                           let stringHtml="<div class='here-hist-info-box'><span>|V|=%s</span>&nbsp&nbsp<span>|E|=%s</span>&nbsp&nbsp<span>%s</span><h4>The Focus Set(%s)</h4><p>%s</p><h4>Settings</h4><p>ctrl_size_subgraph: %s<br>top_n_remaining_neighbors: %s<br>diffusion factor: %s<br>is_interest_edge: %s<br>Weight_UI: %s<br>Weight_API: %s<br>restart_prob: %s<br>weight_matching_edges: %s</p></div>";                                        
                           let html = this_.sprintf(stringHtml, doiGraphInfo.numnodes,doiGraphInfo.numedges, currentTime, keySize, nameHtml, settings.scaleOfSingleFocus, settings.explandneighbors, settings.diffFactor, settings.isEdgeAttri, settings.UIFactor,settings.APIFactor, settings.probRestart, settings.weightAttrNode);
                            $(".histInfoContent").append(html);
                      
                         });
                         //鼠标离开隐藏悬浮框
                         $("#"+allKeys[i]).mouseout(function(){
                             $(".histInfoContent").empty();
                             $(".histInfoContent").css("display","none");
                             this_.totalhist = $("#list li").length; // 获得图片的数量.
                         });


                   });
                }
           
           });
         }
         this_.toolipIconHist();          
         this_.jBoxInstance.hisJbox = new jBox('Modal', {
                  id: "jBoxHist",
                  addClass: "jBoxHistInfo",  // 添加类型,这个功能很棒啊!
                  attach: '#hist-icon',  // 这是历史走廊的图标.点击这个图标打开历史走廊弹窗.
                  width: 1310, // d3.select("svg#mainsvg").attr("width")
                  // height: 200,
                  adjustTracker:true,
                  title: 'History View',
                  overlay: false,
                  zIndex: 1005, // fixme:注意多个jBox实例之间zIndex的值决定与最后一个实例.
                  createOnInit: true,
                  content: $("#historyGallery"),  // jQuery('#jBox-content') 
                  draggable: true,
                  repositionOnOpen: false,
                  repositionOnContent: true,
                  // position: { // SVG的右上角,以后可以先计算出来再设计.
                  //   x: 622,  // number, 'left', 'right' or 'center'
                  //   y: 680  // number, 'top', 'right' or 'center'                    
                  // }
                  position:this_.$store.state.jboxPositionSet.bottom,
         }); 
         this_.jBoxInstance.legendJbox = new jBox('Modal', {
                  id: "jBoxLegend",
                  addClass: "jBoxLegendInfo",  // 添加类型,这个功能很棒啊!
                  attach: '#legend-icon',  // 这是历史走廊的图标.点击这个图标打开历史走廊弹窗.
                  maxWidth: 250,
                  // height: 200,
                  maxHeight: 450,
                  adjustTracker:true,
                  title: 'Legend',
                  overlay: false,
                  zIndex: 1005, // fixme:注意多个jBox实例之间zIndex的值决定与最后一个实例.
                  createOnInit: true,
                  content: $("#legend-box"),  // jQuery('#jBox-content') 
                  draggable: true,
                  repositionOnOpen: false,
                  repositionOnContent: true,                  
                  position:this_.$store.state.jboxPositionSet.topRightSideForLegend
         });

         this_.jBoxInstance.attriExplorJbox = new jBox('Modal', {
                  id: "jBoxAttribute",
                  addClass: "jBoxAttributeInfo",  // 添加类型,这个功能很棒啊!
                  attach: '#icons-search-attri',  // 这是节点属性探索图标,定义在infoSearchView.vue文件中.
                  width: 400, // d3.select("svg#mainsvg").attr("width"),
                  // height: 200,
                  title: 'Matching Panel',
                  overlay: false,
                  zIndex: 1005, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
                  createOnInit: true,
                  content: $("#nodes-attris-exploration"),  // jQuery('#jBox-content') 
                  draggable: true,
                  repositionOnOpen: false,
                  repositionOnContent: true,
                  // position: { // SVG的右上角,以后可以先计算出来再设计.
                  //   x: 622,  // number, 'left', 'right' or 'center'
                  //   y: 680  // number, 'top', 'right' or 'center'                    
                  // },
                  position:this_.$store.state.jboxPositionSet.matchingPanel, // matchingPanel this_.$store.state.jboxPositionSet.bottom
                  // 以下是弹窗事件,这些功能真的非常优秀!
                  onOpen: function(){
                    this_.isClickNodeAtrrExplor = true; // 点击图标打开弹窗.
                    // alert(this_.isClickNodeAtrrExplor);
                  },
                  onCloseComplete: function(){
                     this_.isClickNodeAtrrExplor = false; // 关闭弹窗.
                     // alert(this_.isClickNodeAtrrExplor);
                  }
         });
         this_.jBoxInstance.attriExplorJbox.disable(); // 在主视图中没有DOI图时,禁止弹窗.
         this_.jBoxInstance.doiLayoutSetJbox = new jBox('Modal', { //主视图DOI图布局参数窗口.
                  id: "jBoxDoiLayoutSetting",
                  addClass: "jBoxDoiLayoutSettingInfo",  // 添加类型,这个功能很棒啊!
                  attach: '#main-view-layout-setting',  // 这是节点属性探索图标,定义在infoSearchView.vue文件中.
                  width: 280,              // Maximal width
                  height: 302,             // Maximal height 
                  title: 'Layout Setting',
                  // fixed:true,
                  overlay: false,
                  zIndex: 100, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
                  createOnInit: true,
                  content: $("#doi-layout-setting"),  // jQuery('#jBox-content') 
                  draggable: false,
                  repositionOnOpen: false,
                  repositionOnContent: true,
                  target: $('#main-view-layout-setting'),
                  offset: {x: -125, y: 180},             
                  // position:this_.$store.state.jboxPositionSet.doiLayoutSetting,
                  // 以下是弹窗事件,这些功能真的非常优秀!
                  onOpen: function(){                   
                  },
                  onCloseComplete: function(){                     
                  }
         });
         this_.jBoxInstance.doiLayoutSetJbox.disable(); //失能.
         bus.$on('sendGraphData', function (data) { //实时监听graph数据,分发一次就被马上监听到.
              // fixme:所有请求的图数据,包括扩展的图数据 + 历史保存的图数据,都需要进入这里实时的响应并执行.
              console.log("监听到graph数据!");
              this_.mainViewLoadingFlag = false; // 关闭加载.
              console.log("this_.mainViewLoadingFlag in sendGraphData");
               console.log(this_.mainViewLoadingFlag);
              // console.log("this_.explandNewNodeList"); console.log(this_.explandNewNodeList);
              let graph = data[0];  // 图数据              
              // 将图的方向保存到store.js中.
              let focus = data[1]; // 扩展成多焦点. 
              let useSearchFlag = data[2]; // 是否使用搜索框,确定是否要清除双击历史.
              this_.usesearchFlag = useSearchFlag; // 否使用搜索框,用于保留原始DOI,即非扩展部分.
              if(useSearchFlag){
                this_.rightClickExplandNodes.splice(0,this_.rightClickExplandNodes.length);
                 // this_.doubleClickFlag = false; // 这个语句的作用:在DOI初始布局过程中关闭双击展开操作,只有布局结束后才能进行节点扩展操作.
                 this_.rightClickExplandFlag = false;  // 这个语句的作用:在DOI初始布局过程中关闭双击展开操作,只有布局结束后才能进行节点扩展操作.
              } 
              this_.originGraph = JSON.parse(JSON.stringify(graph));// 及时保留更新的原图数据以及焦点数据,但是要注意原图是一个对象,而对象传递参数时是传递地址的,即引用,所以要深度拷贝保存.             
              // console.log("this_.originGraph");console.log(this_.originGraph);
              // 由于created(){}调用时已经完成了属性和方法的计算,所以在这里面可以调用方法和属性.
              this_.getGraphNodeSize(graph, 10);              
              let graphDirection = data[3]; // 图的方向性.
              this_.$store.state.mainViewGraph.graphDirection = graphDirection;
              let isDirected = graphDirection; // 是否有向. 
              this_.$store.state.mainViewGraph.isDirected  = isDirected; // 保留到全局变量中.
              if(!this_.isAdjustLayoutSettings){
                this_.$store.state.mainViewGraph.attributesExplorNodeHighlight = {};               
              }
              let explandNewNodeList = data[4]; // 获得扩展出来的节点列表.
              // console.log("explandNewNodeList data[4]"); console.log(explandNewNodeList);
              // todo: 添加于2019-4-7,可能会存在问题,以后再改动.
              if(explandNewNodeList.length > 0){
                // console.log("hahahaha");
                this_.$store.state.mainViewGraph.isExplandNodeFlag = true;
                // this_.explandNewNodeList.splice(0,this_.explandNewNodeList.length); // 清空之前的列表, [{'id': XXX, 'name': xxx, "value": XXX},...] 用于存放被扩展节点在DOI子图中没有出现过的邻居节点.
                this_.explandNewNodeList = []; // 改成直接赋予[]就好了,看来是地址的问题.
                for(let i=0; i<explandNewNodeList.length; i++){                    
                    this_.explandNewNodeList.push(explandNewNodeList[i]);
                }
              }
              // 获得图数据.
              this_.mainviewD3Layout(graph, focus, isDirected, this_.layoutSettings, explandNewNodeList); // d3布局.
              this_.isDisplayLabelNodes(); //是否显示标签.         
              this_.linkedByIndex = {};  // 先清空this_.linkedByIndex,避免影响下一次布局鼠标悬浮事件.         
              
              graph.links.forEach(function(d) { // 如果放在mainviewD3Layout里面则d.source.index没有定义,因为还没有布局好,只有布局好了之后才有d.source.index,所以放在布局后,获得linkedByIndex,这样在鼠标悬浮事件中就可以检测到了.          
                this_.linkedByIndex[d.source.index + "," + d.target.index] = 1; // {'1,2':1, '2,3':1}
                
              });              
              this_.sendGraphNodeData(); // 获得主视图中节点的选中属性的值.        
              if(!this_.isAdjustLayoutSettings){ // 保证在调整布局时,保存matching panel.               
                // 如果不是在线调节布局参数,则清空上一个图的属性探索匹配节点,及属性探索框中的内容.              
                if(!this_.isExpandOnGraph){
                  this_.clearDynamicAttriExplorList(); // 每次主视图刷新都清空属性探索弹出框的数据,然后进入updated()钩子函数.
                  this_.clearDynamicConditionExploreList();
                }
                
              }
              this_.nodeHighLightRestore(); // 之前不能保留高亮的原因是没有执行clearDynamicAttriExplorList函数就不会进入updated()钩子函数.
                      
                           
              this_.jBoxInstance.nodeDetailJbox = new jBox('Modal', {
                id: "jBoxNodeInfo",
                addClass: "jBoxCircleInfo",  // 添加类型,这个功能很棒啊!
                attach: '#mainsvg .nodecircle',
                width: 280,                
                title: 'Node Details',
                overlay: false,
                createOnInit: true,
                content: $("#nodeinfo"),  // jQuery('#jBox-content') 
                draggable: true,
                repositionOnOpen: false,
                repositionOnContent: true,
                target: $(".mian-view-item-name"), //$(".mian-view-item-name"), //$('.mian-view-item-info'), // $('.mian-view-item-info'), {x: 95, y: 145}
                offset: {x: 63, y: 135},
                //position:this_.$store.state.jboxPositionSet.topLeftSide,                   
                onOpen: function(){ // 每次点击节点查看细节的时候都会进入这个函数.
                  // this_.jBoxInstance.nodeDetailJbox.position({
                  //   target: $(".mian-view-item-name"), //$('.mian-view-item-info') //注意,这样保证:当 jBoxInstance.resultVis 移动后,重新打开layoutSetting,layoutSetting能够跟着jBoxInstance.resultVis走.           
                  // }); 
                  
                  let nodeId = this_.clickNodeFlag; // 获得被点击的节点的id.
                  this_.$store.state.mainViewGraph.clickNode2GetId = nodeId;
                  this_.$store.state.mainViewGraph.isOpenCheckNodeDetailFlag = true;

                },
                onCloseComplete: function(){
                    this_.jBoxInstance.nodeDetailJbox.position({
                      target: $(".mian-view-item-name"), //$('.mian-view-item-info') //注意,这样保证:当 jBoxInstance.resultVis 移动后,重新打开layoutSetting,layoutSetting能够跟着jBoxInstance.resultVis走.           
                    });
                    this_.$store.state.mainViewGraph.isOpenCheckNodeDetailFlag = false;
                    let isSeeMoreBoxOpen = $(".jBoxSeeMoreOfNode").css("display"); // block:open, none:close
                    // todo: 发生一个很诡异的现象: 明明see more框还开着确说已经关闭了,最后使用jquery的css方法查看diaplay == block 或none来判断是否关闭.
                    if(isSeeMoreBoxOpen == "block"){ // See More框打开着.
                        // console.log("main  See More框打开着.");
                        let css = {
                          "stroke-dasharray":0,
                          "stroke": "#fff",
                          "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
                        };
                        $("#mainsvg .nodecircle").css(css); // 先擦干净

                        
                       //  let attributesExplorNodeHighlight = this_.$store.state.mainViewGraph.attributesExplorNodeHighlight;
                       //  let nodeIdList = Object.keys(attributesExplorNodeHighlight);
                       //  if(nodeIdList.length > 0){ // 如果已经开始属性探索.
                       //     nodeIdList.forEach(function(item, index){
                       //       let hightedNodesList = attributesExplorNodeHighlight[item]; // [id0, id1, ...]
                       //       let hightedColor = this_.nodeVsColorObj[item];
                       //       for(let ii=0; ii<hightedNodesList.length; ii++){
                                
                       //          let css = {
                       //          "stroke-dasharray":0,
                       //          "stroke": hightedColor,
                       //          "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                       //        };
                       //        $("#mainsvg #" + hightedNodesList[ii]).css(css); // 节点用对应的颜色高亮.
                       //       }
                             
                       //    });
                       // }

                        // 用黑圈圈定对应的节点.
                        let cssNode = {
                            "stroke-dasharray":0,
                            "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.clickCheckNodeInfo,
                            "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                        };
                        let nodeId = this_.$store.state.mainViewGraph.clickNode2GetId;
                        $("#mainsvg #" + nodeId).css(cssNode); // 对应节点,用黑圈圈起来.
                    }
                    if(isSeeMoreBoxOpen == "none"){ // See More框关闭.
                      // console.log("main See More框关闭");
                      let css = {
                        "stroke-dasharray":0,
                        "stroke": "#fff",
                        "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
                      };
                      $("#mainsvg .nodecircle").css(css); // 先擦干净.

                      
                     //  let attributesExplorNodeHighlight = this_.$store.state.mainViewGraph.attributesExplorNodeHighlight;
                     //  let nodeIdList = Object.keys(attributesExplorNodeHighlight);
                     //  if(nodeIdList.length > 0){ // 如果已经开始属性探索.
                     //     nodeIdList.forEach(function(item, index){
                     //       let hightedNodesList = attributesExplorNodeHighlight[item]; // [id0, id1, ...]
                     //       let hightedColor = this_.nodeVsColorObj[item];
                     //       for(let ii=0; ii<hightedNodesList.length; ii++){
                              
                     //          let css = {
                     //          "stroke-dasharray":0,
                     //          "stroke": hightedColor,
                     //          "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                     //        };
                     //        $("#mainsvg #" + hightedNodesList[ii]).css(css); // 节点用对应的颜色高亮.
                     //       }
                           
                     //    });
                     // }

                    }
                }
              });

             if($(".jBoxCircleInfo").length > 1){  // 这样可以避免出现多个id=jBoxNodeInfo的div.
               $("#jBoxNodeInfo").remove();
             }

             this_.jBoxInstance.edgeDetailJbox = new jBox('Modal', {
                id: "jBoxEdgeInfo", // 弹出兴趣属性选择框.
                addClass: "jBoxLinksInfo",  // 添加类型,这个功能很棒啊!
                attach: '#mainsvg .source-link-target',
                width: 300,              // Maximal width
                maxHeight: 300,             // Maximal height 
                title: 'Co-authored publications',
                // fixed:true,
                overlay: false,
                fixed: false,
                adjustTracker: true,
                zIndex: 1005, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
                createOnInit: true,
                content: $("#edgeinfo-see-more-in-mianview"),  // jQuery('#jBox-content') 
                draggable: true,
                repositionOnOpen: false,
                repositionOnContent: true,
                // target: $('#mainsvg .source-link-target'),//$('#filtered-subgraph-nav-icons-setting'),
                // offset: {x: 30, y: 30}, // {x: -135, y: 155},
                // 以下是弹窗事件,这些功能真的非常优秀!
                onOpen: function(){                   
                    this_.jBoxInstance.edgeDetailJbox.position({
                       // target: $('#mainsvg .source-link-target')//$('#filtered-subgraph-nav-icons-setting') //注意,这样保证:当 jBoxInstance.resultVis 移动后,重新打开layoutSetting,layoutSetting能够跟着jBoxInstance.resultVis走.           
                    });
                },
                onCloseComplete: function(){                     
                  let css = {                                
                              "stroke": this_.commonEdgeColor // 灰色.                               
                            };
                  $("#mainsvg #" + this_.clickedEdgeIdList[0]).css(css); // 点击节点,用黑色圆圈圈起来.  clickedEdgeIdList
                  this_.clickedEdgeIdList.pop();
                }
            });
           if($(".jBoxLinksInfo").length > 1){  // 这样可以避免出现多个id=jBoxNodeInfo的div.
             $("#jBoxEdgeInfo").remove();
           }           
                                    
           }      
         );
         
         $.contextMenu({  // fixme: 主视图中,节点的右键点击.
          // fixme: contextMenu插件是一个事件类型的,也就是说,mounted阶段并没有'#nodeinfobox .cell'这个元素,需要点击节点后才能渲染出来,但是由于这是一个事件,则直接在mounted里面注册,一旦出现个这样的元素则会直接绑定到上面,这样就不用考虑放在updated钩子函数里面了.
                  selector: '#mainsvg .node_g',
                  className: "focusSelectionMenuMainView",
                  callback: function(key, options) { 
                      console.log("function(key, options)"); console.log(options);   
                      // let node_id = options.$trigger.context.id; // todo: 主要视图中节点的id.
                      let node_id = options.$trigger["0"].firstElementChild.id;
                      // console.log("typeof(node_id)");console.log(typeof(node_id)); // 
                      // console.log("options");console.log(options);
                      if(key == "add"){
                          // if(this_.doubleClickFlag){                                                 
                         if(this_.rightClickExplandFlag){ // 保证布局稳定后才可以扩展.
                            // let node_id = d.id; 
                            this_.rightClickExplandNodes.pop(); // 先把旧的节点弹出去,然后在存入新的节点.                           
                            this_.rightClickExplandNodes.push(node_id); // 存放被扩展的节点.
                            let dbName = this_.$store.state.selection.selectiondb; // 取出节点对应的数据库名称
                            this_.isExpandOnGraph = true;
                            // let path = vueFlaskRouterConfig.mainViewNodeExpland + dbName + "/" + node_id; // 带参数的URL.
                            // param: JSON.stringify(param)
                            // console.log("path");console.log(path); 
                            let expandNodeXYList = []; // [x, y]
                            let interestSubgraphId = []; // 用于装当前兴趣子图节点id的列表.
                            for(let i=0; i<this_.graph.nodes.length; i++){
                              let tempNode = this_.graph.nodes[i]; // {id:x, name:x, x:x, y:y, vx:x, vy: x}                              
                              let tempNodeId = tempNode.id; // 节点的id.
                              if(tempNodeId == node_id){ // 找到被扩展节点的坐标.
                                 if(tempNode.hasOwnProperty("fx") && tempNode.hasOwnProperty("fy")){
                                   expandNodeXYList.push({x: tempNode.fx, y: tempNode.fy});
                                 }
                                 else{
                                   expandNodeXYList.push({x: tempNode.x, y: tempNode.y});
                                 }
                              }
                              interestSubgraphId.push(tempNodeId); // [id1, id2, ...]
                            }
                            let param = {
                                dbName: dbName,
                                nodeId: node_id,
                                interestSubgraphId: interestSubgraphId, // 当前子图所有节点的id构成的列表.
                                numNeighbors: this_.$store.state.widgetView.explandneighbors // 需要扩展的邻居数量.
                            };
                            // axios.get(path) // 向python后台发送GET请求
                            axios.post(vueFlaskRouterConfig.mainViewNodeExpland, {
                              param: JSON.stringify(param)
                            })
                            .then((res) => {
                              // TODO: 暂停布局,这个操作非常重要,对于D3 force来说,tick事件是用来迭代布局的,同时它监听svg中的变化,只要有变化,比如拖动节点就会触发这个事件,迭代直至稳定.
                              this_.simulation.stop(); // 暂停force布局
                              //explandGraph={"nodes":[{'id':xxx, 'name':xxx, "value": XXX}], "links":[{'source':xxx, 'target':xxx, 'value': xxx}]}
                              // TODO: 注意: 现在的扩展并没有考虑方向.
                              this_.explandGraph = res.data;  // 由新节点+新边构成的数据,格式: graph={nodes:[{}, ...], links:[{}, ...]},其中新节点是扩展的邻居节点,新边包括3种:邻居-兴趣子图节点, 兴趣子图节点-邻居, 邻居-邻居.
                              // todo: 接下来要将新点添加到扩展前的子图节点集中,而新边则添加到子图的边集中.                              

                              let differentEdges = []; // 新边, [{'source':xxx, 'target':xxx, 'value': xxx},...] 用于存放被扩展节点在DOI子图中没有出现过的邻边.
                              // this_.explandNewEdgeList.splice(0,this_.explandNewEdgeList.length); // 清空之前的新边列表                             
                              let exp_links = this_.explandGraph.links; // 新边: [{source:xx, target:xx, value:xx}, ...]                              
                              for(let i=0; i<exp_links.length; i++){
                                  differentEdges.push(exp_links[i]); // [{}, ...]
                                  // this_.explandNewEdgeList.push(exp_links[i]);
                              }                              
                              
                              
                              let exp_nodes = this_.explandGraph.nodes; // 新节点, 即扩展出来的邻居. [{id:xx, name:xx, value:xx}, ...]
                              
                              let differentNodes = []; 
                              let differentNodesValueList = []; // 用于装differentNodes中对应项的值,用于后续的排序.
                              this_.explandNewNodeList.splice(0,this_.explandNewNodeList.length); // 清空之前的列表, [{'id': XXX, 'name': xxx, "value": XXX},...] 用于存放被扩展节点在DOI子图中没有出现过的邻居节点.
                              for(let i=0; i<exp_nodes.length; i++){
                                  differentNodes.push(exp_nodes[i]); // [{}, ...]
                                  differentNodesValueList.push(exp_nodes[i].value);
                                  this_.explandNewNodeList.push(exp_nodes[i].id);
                              }
                              
                              let newGraph = {}; // 扩展后的图,焦点还是原来的焦点.
                              newGraph.links = [];
                              newGraph.nodes = [];

                              let newNodesList = []; // 用于存放扩展的TOPN节点的id,已备用于后面边的筛选.
                              let fromMaxMinIndexList = this_.findIndexOfTopN(differentNodesValueList, differentNodesValueList.length);
                                                            
                              // newGraph的节点构造.
                              for(let i=0; i<differentNodes.length; i++){
                                  let newNodeObj = {}; //{'id':xxx, 'name':xxx, "value": XXX}
                                  let indexNode = fromMaxMinIndexList[i];
                                  let nodeObj = differentNodes[indexNode]; // 节点对象. {id:x, name:x, value:x}
                                  newNodesList.push(nodeObj.id);
                                  // 新的节点在被双击节点的周围,现在以被双击点的x,y,vx,vy作为其初始值,可以减少迭代,同时保持mental map.
                                  // newNodeObj.x = d.x;
                                  // newNodeObj.y = d.y;
                                  // newNodeObj.vx = d.vx;
                                  // newNodeObj.vy = d.vy;
                                  // 被扩展出来的5个邻居.
                                  // newNodeObj.x = 0;
                                  // newNodeObj.y = 0;
                                  // newNodeObj.vx = 0;
                                  // newNodeObj.vy = 0;
                                  let expandNodeX = expandNodeXYList[0].x;
                                  let expandNodeY = expandNodeXYList[0].y;
                                  let degreeCircleDivide = 2*Math.PI / this_.$store.state.widgetView.explandneighbors; // 一个圆被划分多少份,默认为5份.
                                  let x = expandNodeX + this_.neighborR*Math.cos(degreeCircleDivide * i - this_.degreeDeviate*Math.PI / 180);
                                  let y = expandNodeY - this_.neighborR*Math.sin(degreeCircleDivide * i - this_.degreeDeviate*Math.PI / 180);
                                  newNodeObj.fx = x;
                                  newNodeObj.fy = y;

                                  newNodeObj.id = nodeObj.id;
                                  newNodeObj.name = nodeObj.name;
                                  newNodeObj.value = nodeObj.value;
                                  newNodeObj.num_remaining_neighbours = nodeObj.num_remaining_neighbours; // 节点的剩余邻居数量.
                                  // newNodeObj.fixed = false; // 新节点重新布局节点位置. 但是D3 V4版本已经没有fixed属性了.应该使用fx+fy属性.
                                  newGraph.nodes.push(newNodeObj);
                              }
                              // console.log("this_.graph");console.log(this_.graph);
                              
                              for(let i=0; i<this_.graph.nodes.length; i++){ //新节点加入到graph的nodes中.
                                  let newNodeObj = {}; // {'id':xxx, 'name':xxx, "value": XXX}
                                  let nodeObj = this_.graph.nodes[i];
                                  // 接下来构造新的节点,保证没有x y vx vy这样的属性.
                                  // 尽量使旧节点保持原来的位置以保持mental map,而实验证明,由于扩展的节点是被双击点的邻居,与其余点没有边相连,所以力很弱,这样旧点的位置就改得不是很大.
                                  newNodeObj.fx = nodeObj.x;
                                  newNodeObj.fy = nodeObj.y;
                                  // newNodeObj.vx = nodeObj.vx;
                                  // newNodeObj.vy = nodeObj.vy;
                                  newNodeObj.vx = 0;
                                  newNodeObj.vy = 0;

                                  newNodeObj.id = nodeObj.id;
                                  newNodeObj.name = nodeObj.name;
                                  newNodeObj.value = nodeObj.value;
                                  newNodeObj.num_remaining_neighbours = nodeObj.num_remaining_neighbours; // 节点的剩余邻居数量.
                                  // newNodeObj.fixed = true; // 旧节点保持原来的节点位置.
                                  newGraph.nodes.push(newNodeObj);
                                  // newGraph.nodes.push(nodeObj);
                              }                              

                              // newGraph的边构造.
                              for(let i=0; i<differentEdges.length; i++){ // 新边添加到graph的links中.
                                //{'source':xxx, 'target':xxx, 'value': xxx}
                                  let newEdgeObj = {};
                                  let edgeObj = differentEdges[i]; // {source':xxx, 'target':xxx, 'value': xxx}

                                  newEdgeObj.source = edgeObj.source;
                                  newEdgeObj.target = edgeObj.target;
                                  newEdgeObj.value = edgeObj.value;
                                  newGraph.links.push(newEdgeObj);
                              }
                              for(let i=0; i<this_.graph.links.length; i++){ //新节点加入到graph的nodes中.
                                  let newEdgeObj = {};//source':xxx, 'target':xxx, 'value': xxx}
                                  let edgeObj = this_.graph.links[i]; //

                                  newEdgeObj.source = edgeObj.source.id;
                                  newEdgeObj.target = edgeObj.target.id;
                                  newEdgeObj.value = edgeObj.value;
                                  newGraph.links.push(newEdgeObj);
                              }                              

                              /*
                              let setFromNodes = new Set(); // {id0, id1, ...} 所有节点构成的集合
                              let setFromEdges = new Set(); // {id0, id1, ...} 所有source+target构成的集合
                              for(let i=0; i<newGraph.nodes.length;i++){
                                setFromNodes.add(newGraph.nodes[i].id);

                              }

                              for(let i=0; i<newGraph.links.length;i++){
                                setFromEdges.add(newGraph.links[i].source);
                                setFromEdges.add(newGraph.links[i].target);
                              }*/
                              // todo: 需要更新节点的剩余邻居.
                              let updaedNodesRemainingNeighbs = this_.explandGraph.updated_nodes_remaining_neighbors; // {id0: 9, id1:90, ...}, 需要更新的节点的剩余邻居数量,其他节点的剩余邻居数量不变.
                              let updaedNodesIdList = Object.keys(updaedNodesRemainingNeighbs); // [id0, id1, ...] 需要更新的节点id列表.
                              newGraph["nodes"].forEach(function(node){ // 使用forEach可以直接操纵地址,完成一次性更新.
                                  let nodeId = node.id; // id.
                                  if(updaedNodesIdList.indexOf(nodeId) != -1){ //属于需要更新的节点.
                                     node.num_remaining_neighbours = updaedNodesRemainingNeighbs[nodeId]; // 更新节点的剩余邻居.
                                  }
                              });
                              // console.log("newGraph hahahaha");console.log(newGraph);
                              let useSearchFlag = false;
                              this_.isExplandNodeForHist = true; // 用于判断是否点击节点,用于保存扩展后的布局.                          
                              let directed = this_.$store.state.mainViewGraph.graphDirection;
                              this_.$store.state.mainViewGraph.isExplandNodeFlag = true; //激活标志位,表示执行了点击扩展节点这个动作.
                              bus.$emit("sendGraphData", [newGraph, this_.focus, useSearchFlag, directed, this_.explandNewNodeList]); // 发送到D3 force入口进行布局.
                              // console.log("newGraph");console.log(newGraph);
                              // todo: 将图的信息发送到图信息面板显示.
                              let doiGraphInfo = {};                                   
                              doiGraphInfo.numnodes = newGraph.nodes.length;
                              doiGraphInfo.numedges = newGraph.links.length;                               
                              bus.$emit("sendDoiGraphInfo", doiGraphInfo); // 更新节点+边的数量信息.
                          })
                          .catch((error) => {
                            console.error(error);
                          });
                        }

                       }
                       if(key == "cut"){ // 节点被选中用于属性探索.
                          this_.jBoxInstance.attriExplorJbox.open();                       
                          let css = {
                              "stroke-dasharray":0,
                              "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.rightClickSelectAttriEplor, // #1890ff
                              "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                          };
                          $("#mainsvg #" + node_id).css(css); // 点击节点,用黑色圆圈圈起来. 
                          let nodeName = this_.nodesAttrObj[node_id].name[0];
                          let tagObj = {}; // 被选中的节点以标签的形式呈现.
                          tagObj.id = node_id; // id作为唯一标识,
                          tagObj.tag = nodeName; // tag作为节点的标签.
                          // this_.dynamicAttriExplorList.push(tagObj);
                          let id = tagObj.id; // id,用于唯一标识.
                          let isexistence = false; // 是否存在. 确保不重复添加.
                          for(let i=0; i<this_.dynamicAttriExplorList.length; i++){
                             if(this_.dynamicAttriExplorList[i].id == id){
                                isexistence = true; // 如果true,则存在.
                                break;
                             }
                          }
                          if(isexistence === false){ // 如果不一样,则添加到数组中. 
                            this_.dynamicAttriExplorList.push(tagObj); // 添加到数组中.                       
                          }
                       }

                        if(key == "copy"){  // 选为焦点,并添加到焦点集中.                            
                            this_.rightClickNodeGetId = node_id;
                            // let css = {
                            //     "stroke-dasharray":0,
                            //     "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.rightClickAsFocus,
                            //     "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                            // };
                            // $("#mainsvg #" + node_id).css(css); // 点击节点,用黑色圆圈圈起来.                           
                            
                            // let dbName = this_.$store.state.selection.selectiondb; // 取出节点对应的数据库名称
                            // // let param = {"nodeId": node_id, "dbName": dbName}; // 传递参数.                 
                            // let path = vueFlaskRouterConfig.mainViewNodeInfo + dbName + "/" + node_id; // 路径
                            // // console.log("path");console.log(path);
                            // axios.get(path) // todo:向python后台发送GET请求,这里不能使用post,原因未知.
                            //     .then((res) => { 
                            //       let tabledata = res.data;  // {id, name, institution, num_papers, num_citation, H_index, P_index, UP_index, interests}
                            //       // console.log("tabledata");console.log(tabledata);

                            //       let dbname = this_.$store.state.selection.selectiondb; // 数据库名称.
                            //       // let field =  this_.$store.state.selection.selectionfield; // 数据库表字段.
                            //       // let keyword = this_.$store.state.selection.keyword; // 数据库表字段对应的关键字.
                            //       let focusObj = {"id": node_id,  // id作为唯一标识,
                            //                       // "tag": tag, // tag作为节点的标签.
                            //                       "dbname":dbname,
                            //                       "field":"NULL", // 写成NULL没有影响.
                            //                       "keyword": "NULL", // 这么写没有影响.
                            //                       "attriselect": this_.$store.state.focusAttributesSelection.checkedFocusAttri
                            //                       };
                            //       let row = {}; // {field1: value, ...}
                            //       for(let i=0; i<tabledata.length; i++){
                            //         let tempObj = tabledata[i]; // 临时对象.{key:x, value:x}
                            //         if (tempObj.key == "name") {
                            //           focusObj.tag = tempObj.value;
                            //         }
                            //         row[tempObj.key] = tempObj.value;
                            //       }
                            //       // console.log("row");console.log(row);

                            //       let attributesValue = {};
                            //       let keysRow = Object.keys(row); // 获得键列表. [field1, ...]         
                            //       let keysType = this_.$store.state.fields.fieldsType; // 字段类型.{字段:类型,...}                                   
                            //       for(let i=0; i<keysRow.length; i++){
                            //          let key_ = keysRow[i]; // 键
                            //          let type_ = keysType[key_]; // 类型
                            //          let computedAttri = this_.$store.state.focusAttributesSelection.checkedFocusAttri;
                            //          if(computedAttri.indexOf(key_) != -1){ // 属于被考虑的属性.
                            //            attributesValue[key_] = row[key_];
                            //          }           
                                      
                            //       }

                            //       focusObj.attributesValue = attributesValue; // 添加属性及其值.
                            //       // console.log("focusObj");console.log(focusObj);
                            //       //bus.$emit("sendSelectedFocus", focusObj);
                            //       bus.$emit("sendSlectedNode", focusObj); //该事件能避免重复添加.

                            // })
                            // .catch((error) => {           
                            //   console.error(error);
                            // });                        
                        }
                  },
                  items: { // todo:以后修改图标.                       
                      "add": {name: "Expand it"},  // 节点扩展.  , icon: "add"                    
                      "copy": {name: "Add it to the focus set", className: "addToTheFocusSet"}, // 作为焦点. , icon: "copy" 
                      "cut": {name: "Add it to Matching Panel"}, // , icon: "cut"
                      "quit": {name: "Quit"}
                      /*
                      icon: function(){  // 退出.
                          return 'context-menu-icon context-menu-icon-quit';
                      }*/
                  },                   
          });

         $.contextMenu({  // fixme: 历史走廊中,右键点击历史图片.
          // fixme: contextMenu插件是一个事件类型的,也就是说,mounted阶段并没有'#nodeinfobox .cell'这个元素,需要点击节点后才能渲染出来,但是由于这是一个事件,则直接在mounted里面注册,一旦出现个这样的元素则会直接绑定到上面,这样就不用考虑放在updated钩子函数里面了.
            selector: '.histimgli',
            className: "histViewContextMenu",
            callback: function(key, options) {
               let imgId = options.$trigger.context.id;  // 保存的图片的键.
               if(key == "delete"){  // 如果点击的是"delete"选项.
                    if(this_.storageMode == "webDB"){
                      $("#" + imgId).remove(); // 删除选中图片.
                      this_.$removeItem(imgId).then(function(){ 
                          console.log("already removed imgId");                     
                      });
                      this_.totalhist = $("#list li").length; // 获得图片的数量.
                      // this_.usesearchFlag = true; // 使能,这样就可以保存当前布局图.
                  }
                  else{
                      $("#" + imgId).remove(); // 删除选中图片.                      
                      // this_.localStore.splice(0,this_.localStore.length);
                      this_.$removeItem(imgId).then(function(){ 
                              console.log("already removed imgId");                     
                      });
                      this_.totalhist = $("#list li").length; // 获得图片的数量.
                      // this_.usesearchFlag = true; // 使能,这样就可以保存当前布局图.
                  }
               }
               
            },
            items: {
                // "edit": {name: "Edit", icon: "edit"},
                // "cut": {name: "Cut", icon: "cut"},
                // "copy": {name: "Copy", icon: "copy"},
                
                "delete": {name: "Delete", icon: "delete"},
                // "sep1": "---------",
                "quit": {name: "Quit", icon: function(){
                    return 'context-menu-icon context-menu-icon-quit';
                }}
            },
            zIndex: 200
         });

        this_.jBoxInstance.interestAttributes = new jBox('Modal', {
          id: "jBoxInterestAttributesMainView", // 弹出兴趣属性选择框.
          addClass: "jBoxInterestAttributesMainViewClass",  // 添加类型,这个功能很棒啊!
          attach: '.focusSelectionMenuMainView .addToTheFocusSet',
          width: 300,              // Maximal width
          height: 150,             // Maximal height 
          title: 'Attributes of Interest',
          // fixed:true,
          overlay: false,
          fixed: false,
          adjustTracker: true,
          zIndex: 1005, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
          createOnInit: true,
          content: $("#interest-attributes-mainview"),  // jQuery('#jBox-content') 
          draggable: true,
          repositionOnOpen: false,
          repositionOnContent: true,
          target: $('.focusSelectionMenuMainView .addToTheFocusSet'),//$('#filtered-subgraph-nav-icons-setting'),
          offset: {x: -135, y: 100}, // {x: -135, y: 155},
          // 以下是弹窗事件,这些功能真的非常优秀!
          onOpen: function(){                   
              this_.jBoxInstance.interestAttributes.position({
                 target: $('.focusSelectionMenuMainView .addToTheFocusSet')//$('#filtered-subgraph-nav-icons-setting') //注意,这样保证:当 jBoxInstance.resultVis 移动后,重新打开layoutSetting,layoutSetting能够跟着jBoxInstance.resultVis走.           
              });
              bus.$emit("attributesOfInterestPanelUpdate", true); // 提醒 "兴趣属性选择" 面板更新勾选列表.
          },
          onCloseComplete: function(){                     
            
          }
        });

        this_.initDeleteMainViewSvg(); //点击事件,删除主视图.
        this_.initClickExportSvgToPng(this_.width_, this_.height_); // 导出SVG.
        
    },
    computed:{},    
    watch:{ // 侦听器       
      isClickNodeAtrrExplor: function(curVal, oldVal){
        if(curVal){  // 如果点开节点属性探索信息框.          
          this.getAllAttriSelection(); // 获得表头.               
        }
      },
      conditionLegendList: function(curVal, oldVal){
         // console.log("conditionLegendList curVal change");
         // console.log(curVal);
         // console.log("conditionLegendList oldVal change");
         // console.log(oldVal);  
         if(curVal.length > 0){
           this.jBoxInstance.legendJbox.open(); // 打开legend.     
         }     
             
         this.legendHighlightingSvgHeightCtrl=(18+(curVal.length-1)*18).toString() + 'px';
      },
      rightClickExplandNodes: function(curVal, oldVal){
        console.log("rightClickExplandNodes change");
        if(curVal.length >0){
          this.legendSvgHeightCtrl='72px';
        }
        else{
          this.legendSvgHeightCtrl='36px'; 
        }
      },
      dynamicAttriExplorList: function(curVal, oldVal){ // [{id:xx, label:xx},...]
        
        let this_ = this;       
        this.getAttriSelectionTable(curVal, this.nodeAttriTableData); // 获得表格数据.
        let css_ = {
                      "stroke-dasharray":0,
                      "stroke": "#fff",
                      "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
                    };
        $("#mainsvg .nodecircle").css(css_);  // fixme: 先擦干净,然后再高亮点击节点.
        let selectedNodeIdList = []; // 被选中节点的id列表.
        this_.dynamicAttriExplorNodeIdList = [];
        for(let i=0; i<curVal.length; i++){
            let nodeId = curVal[i].id; // 节点id.
            this_.dynamicAttriExplorNodeIdList.push(nodeId); // [id0, id1, ...]
            selectedNodeIdList.push(nodeId); // [id0, id1, ...]         
            let css = {
                "stroke-dasharray":0,
                "stroke": this.$store.state.mainViewGraph.highlightColorSheet.rightClickSelectAttriEplor, // #1890ff
                "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
            };
            $("#mainsvg #" + nodeId).css(css); // 点击节点,用黑色圆圈圈起来. 
            
            let keysList = Object.keys(this_.dynamicConditionExploreObj); // [key0, key1, ...]
            if(keysList.indexOf(nodeId) == -1){ // 说明不存在,则添加新的键值对.               
               this_.$set(this_.dynamicConditionExploreObj, nodeId, []); // 注意:只有使用this.$set() + this.$delete()响应式动态地添加/删除对象的属性才能被监听到.
               this_.$set(this_.nodeVsColorObj, nodeId, null); // 与dynamicConditionExploreObj一一对应.{id0:null, id1:null, ...}
               this_.$set(this_.matchedNodesObj, nodeId, []);
            }                      
        }
        if(curVal.length == 0){ // 已经清空了,则dynamicConditionExploreList也清空.
          this_.clearDynamicConditionExploreList(); // 清空.
        }
        let againKeysList = Object.keys(this_.dynamicConditionExploreObj);
        
        if(selectedNodeIdList.length != againKeysList.length){ // 则应该删除对应的部分.
           let shouldDelteElementsList = againKeysList.filter(function(v){ return selectedNodeIdList.indexOf(v) == -1 }); // 应该被删除的元素构成的列表.
           for(let i=0; i<shouldDelteElementsList.length; i++){
             let deleteId = shouldDelteElementsList[i];
             // delete this_.dynamicConditionExploreObj[deleteId]; // 删除对应的键值对.
             this_.$delete(this_.dynamicConditionExploreObj, deleteId); // {id0:[], id1: [], ...}
             this_.$delete(this_.nodeVsColorObj, deleteId); // {id0: color0, ...}
             this_.$delete(this_.matchedNodesObj, deleteId); // {id0:[], id1: [], ...}
           }
        }      
        // console.log("this_.dynamicConditionExploreObj");console.log(this_.dynamicConditionExploreObj);
        // console.log("this_.nodeVsColorObj");console.log(this_.nodeVsColorObj);

      },
      
      dynamicConditionExploreObj: {
        handler(curVal, oldVal){
          // 一旦添加或删除条件,则实时地刷新整个图,然后高亮匹配的节点.
          this.clearHighLight(); // 清除高亮. dynamicConditionExploreObj
          // let keysList = Object.keys(curVal); // [id0, id1, id2, ...]
          let keysList = this.dynamicAttriExplorNodeIdList; // 这样保证有序.
          this.conditionLegendList.splice(0, this.conditionLegendList.length);
          for(let i=0; i<keysList.length; i++){
             let tempObj = {};                          
             let conditionsList = curVal[keysList[i]]; // [{id:x, tag:x}, ...]
             let finalMatchNodes = this.matchNodesforConditions(conditionsList); // 依据条件匹配满足条件的节点.             
             this.matchedNodesObj[keysList[i]] = finalMatchNodes; // {id0:[], id1:[], ...}
             this.nodeVsColorObj[keysList[i]] = this.highLightColorList[i]; // 颜色映射: {id0: color0, id1: color1, id2: color2, ...}
             // this.highLightNodesOnMatchedNodesMultiple(finalMatchNodes, this.highLightColorList[i]); // 高亮匹配节点.
            
             let matchingNodeList = this.getMatchingData(this.matchedNodesObj, this.nodeVsColorObj);            
             this.nodeHighlightedWithHalo(this.nodeGroupForHighlightedMatchingNode, matchingNodeList, this.$store.state.mainViewGraph.strokeWidth);             

             let texString = "";
             let counter = 0;
             console.log("conditionsList");console.log(conditionsList);
             conditionsList.forEach(function (ii){
               counter++;
               if(counter < conditionsList.length){
                 texString += ii.attrValue + " & ";
               }
               else{
                 texString += ii.attrValue;
               }
               
             });
             tempObj.text = texString;
             tempObj.color = this.highLightColorList[i];
             this.conditionLegendList.push(tempObj);
          }
          this.$store.state.mainViewGraph.dynamicConditionExploreObj = curVal; // {id0:[x, x], id1:[x,x], id2:[x,x,x]}
          // this.conditionLegendList = [];
          
          // this.conditionLegendList.push();
        },
        deep: true
      },
      // matchedNodesNum
      matchedNodesObj: {
        handler(curVal, oldVal){
          // 一旦添加或删除条件,则实时地刷新整个图,然后高亮匹配的节点.
          // this.clearHighLight(); // 清除高亮.
          // let keysList = Object.keys(curVal); // [id0, id1, id2, ...]
          let keysList = this.dynamicAttriExplorNodeIdList; // [id0, id1, id2, ...], 确保与颜色框一一对应.
          let tempString = "";
          for(let i=0; i<keysList.length; i++){
             let conditionsList = curVal[keysList[i]]; // [{id:x, tag:x}, ...]
             tempString += conditionsList.length.toString() + "  ";
             this.conditionLegendList.forEach(function(jj, index){
                if(index == i){
                   // jj.numMatch = conditionsList.length.toString(); // 匹配数量.
                   if(jj.text.split("|").length > 1){ // 有匹配数量.
                     jj.text = jj.text.split(" | ")[0] + " | " + conditionsList.length.toString();
                   }
                   else{ // 没有匹配数量.
                     jj.text = jj.text + " | " + conditionsList.length.toString();
                   }
                   
                }                
             });
          }
          this.matchedNodesNum = tempString;
          this.$store.state.mainViewGraph.attributesExplorNodeHighlight = curVal;

        },
        deep: true
      }
      
    },
    
    beforeDestroy () {       
       bus.$off('sendGraphData');  // 由于bus.on()不会自己注销,需要bus.$off()来注销,这样可以解决多次触发的问题.
       bus.$off('explandNodeNum');       
       bus.$off("dbLoadedState");
       bus.$off("sendLayoutSettings");
       bus.$off("sendClearAttriExplorState");
       bus.$off("sendMainViewLoadingFlag");
       bus.$off("sendClearExplandNewNodeListFlag"); 
       bus.$off("sendHighLightedRing");
       bus.$off("sendClearNodeHighLighting");      
       bus.$off("sendFocusNodeNumber");
       bus.$off("sendFixNodesCtrolFlag");
    },
    destroyed(){
      console.log("destroyed");
    },

  }

</script>

<style>  
  
    @import "../../static/css/jBox.css";
    @import "../../static/css/jquery.contextMenu.css";
    
    #interest-attributes-mainview{
       display: none;
    }
    #nodeinfo {
       display: none;
    }
    #historyGallery{
      display: none;
    }
    #legend-box{
      display: none;
    }
    #nodes-attris-exploration{
      display: none;
    }
    #doi-layout-setting{
      display: none;
    }
    .histInfoContent{ 
      display:none; /*这样可以避免刚打开页面时出现一个信息框*/    
      max-width:300px;       
      border-radius:2px;
      padding:2px 5px 2px 5px;
      position:absolute;       
      font-size:5px;
      background-color:#fff;
     /* color: white;*/
      z-index: 1007;
      border-style: solid;
      border-color:#ddd;
      border-top-width: 1px;
      border-right-width: 1px;
      border-bottom-width: 1px;
      border-left-width: 1px;
    }
    .legend-info{
      display:none; /*这样可以避免刚打开页面时出现一个信息框*/    
      max-width:500px;       
      border-radius:2px;
      padding:2px 5px 2px 5px;
      position:absolute;       
      font-size:5px;
      background-color:#34495E;
      color: white;
      z-index: 1007;
      border-style: solid;
      border-color:#ddd;
      border-top-width: 1px;
      border-right-width: 1px;
      border-bottom-width: 1px;
      border-left-width: 1px;
    }
    .here-hist-info-box{
       
    }
     #list{ 
      display: flex; 
      -webkit-flex-flow:row nowrap; 
      flex-flow:row nowrap; 
      overflow-x: auto; 
      list-style: none;
     } 
      
     #historyGallery #list li {        
       margin: 0px 10px 0px 10px;/*上 右 下 左*/
     }
     #historyGallery #list li img{
       /*transition: all 0.2s;*/
        transform: scale(1);
        border-style:solid;
        border-color:#c5c5c5;

     }
     #historyGallery #list li:hover img {
          transition: all 0.2s;
          transform: scale(3);
          position: relative;/* absolute */
          /*left:100px;
          top:150px;*/ 
          background: #f8f8f8;
          border-style:solid;
          border-color:"blue";          
          z-index: 100; 
           
          }
     .controls {
            position: fixed;
            top: 16px;
            left: 16px;
            background: #f8f8f8;
            padding: 0.5rem;
            display: flex;
            flex-direction: column;
        }

      .svg-container {
          /*display: table;          
          border-style: solid;
          border-color:#E0E0E0;
          border-top-width: 2px;
          border-right-width: 2px;
          border-bottom-width: 2px;
          border-left-width: 2px;
          margin: 0px 0px 0px 0px;*/
      }

      .controls>*+* {
          margin-top: 1rem;
      }

      label {
          display: block;
      }

      .links line {
          stroke: #999;
          stroke-opacity: 0.6;
      }

      /*.nodes circle {
          stroke: #fff;
          stroke-width: 0px;          
      } */     

      /*定制表格tip的样式*/
       .el-tooltip__popper.is-dark {
          background: #ecf5ff;
          color: #3a8ee6;           
          max-width: 250px;
      }     
      #licensing {
        fill: grey;
      }
      #resolved {
        fill: grey;
      }
      #end-arrow {
        fill: #88A;
      }
      .context-menu-list{
        /*max-width: 10px;*/
      }
      /*.histNav .hist-nav-icon{              
        float:right;
        margin:0px 5px 0px 0px; 
      }*/
      #histwidget{          
         display:block;
         height:20px;
         margin:0px 0px 0px 0px;
      }
    
    .histNav .hist-nav-icon{
      vertical-align: middle; 
      display: table-cell;      
      float:right;
      margin:0px 0px 0px 10px; 
      text-align:center; 
      /* 垂直居中 */ 
      vertical-align:middle;
     
    }
    .histNav .hist-nav-icon img:hover{
      background-color:#E0E0E0;
    }
    #allhistdel{
      max-width:20px;
      text-align:right;
    }
    #histwidget .el-row{
      height:20px;
    }
    /*#attr-nodes-selected{
      height:100px;
      width:400px;
      border-style: solid;
      border-color:#ddd;
      border-top-width: 0px;
      border-right-width: 0px;
      border-bottom-width: 0px;
      border-left-width: 0px;
      margin: 4px 4px 4px 4px;
      border-top-left-radius:5px;
      border-top-right-radius:5px; 
      border-bottom-left-radius:5px;
      border-bottom-right-radius:5px;      
    }*/

    #attrs-selected-list{
      height:100px;
      width: 400px;
      border-style: solid;
      border-color:#ddd;
      border-top-width: 0px;
      border-right-width: 0px;
      border-bottom-width: 0px;
      border-left-width: 0px;
      margin: 4px 4px 4px 4px;
      border-top-left-radius:5px;
      border-top-right-radius:5px; 
      border-bottom-left-radius:5px;
      border-bottom-right-radius:5px;
      /*overflow: auto;
      white-space: nowrap;*/
    }
    .condition-div-list{
      height:80px;
      width: 400px;
      /*border-style: solid;
      border-color:#ddd;
      border-top-width: 0px;
      border-right-width: 0px;
      border-bottom-width: 0px;
      border-left-width: 0px;
      margin: 4px 4px 4px 4px;
      border-top-left-radius:5px;
      border-top-right-radius:5px; 
      border-bottom-left-radius:5px;
      border-bottom-right-radius:5px;*/
      overflow-x: auto;
      overflow-y: auto;
      white-space: nowrap;
    }
    #attr-nodes-selected .el-tag:hover{
      border-width:1px;
      border-color:#2894FF;
      cursor:pointer;
    }
   
    .el-tag-node-attri{
      display: inline-block;
      background-color: rgba(64,158,255,.1);
      padding: 0 10px;
      height: 32px;
      line-height: 30px;
      font-size: 12px;
      color: #409EFF;/*#409EFF;*/
      border-radius: 4px;
      -webkit-box-sizing: border-box;
      box-sizing: border-box;
      border: 1px solid rgba(64,158,255,.2);
      white-space: nowrap;
    }
    
   #jBoxAttribute .el-table td{
      padding: 12px 0;
      min-width: 0;
      -webkit-box-sizing: border-box;
      box-sizing: border-box;
      text-overflow: ellipsis;
      vertical-align: middle;
      position: relative;
      text-align: left;
      overflow: hidden;
   }
   .attri-conditions-box{
      /*padding: 4px 2px 4px 2px;*/
      height:80px;
      width: 100px;
      border-style: solid;
      /*border-color:#ddd;*/
      border-top-width: 2px;
      border-right-width: 2px;
      border-bottom-width: 2px;
      border-left-width: 2px;
      overflow-y: auto;
      overflow-x: auto;
      padding: 2px 0px 0px 2px;
      display: inline-block;
      margin: 0px 2px 0px 0px;
   } 
   
   /*#seleced-nodes-list{
      height:80px;
      width: 400px;
      padding:0px 0px 2px 0px;
      border-style: solid;
      border-color:#ddd;
      border-top-width: 1px;
      border-right-width: 1px;
      border-bottom-width: 1px;
      border-left-width: 1px;
      margin: 0px 0px 0px 0px;
      overflow-y: auto;
      overflow-x: auto;
      padding: 2px 0px 0px 2px;
   }*/
   .detail-info-box-mouse-over {
    display:none; /*这样可以避免刚打开页面时出现一个信息框*/    
    max-width:300px;      
    border-radius:2px;
    padding:2px 5px 2px 5px;
    position:absolute;       
    font-size:5px;
    background:#ecf5ff;
    color:#409EFF;
    z-index: 1007;
  }
#history-quick-access-icon{
    width: 20px;
    height: 20px;
    /*background: blue;*/
    position: absolute;
    right: 0px;
    bottom: 0px;
    z-index: 1005;
    margin: 0px 10px 20px 0px;
}
#legend-quick-access-icon{
    width: 20px;
    height: 20px;
    /*background: blue;*/
    position: absolute;
    right: 0px;
    bottom: 0px;
    z-index: 1005;
    margin: 0px 13px 60px 0px;
}
#match-node-con-box{

}
/*{
  display: inline-block;
} */ 
.match-box-div{
  display: inline-block;
}

/*#attrs-selected-list*/
#edgeinfo-see-more-in-mianview {
    display: none;
    max-height: 300px; 
    max-width: 500px;
    padding:2px 2px 2px 4px;
    overflow: scroll;
  }
  
/* 以下是论文的样式 */
#edgeinfo-see-more-in-mianview .abstract {
  max-height: 217px;
  max-width: 489px;
  overflow: scroll;
  padding: 0px 0px 0px 5px;
  font: normal normal normal normal 12px / 20px Lato, sans-serif;
  /*border-style: solid;
  border-color:#E0E0E0;
  border-top-width: 1px;
  border-right-width: 1px;
  border-bottom-width: 1px;
  border-left-width: 1px;*/
  margin: 5px 1px 5px 1px;
}
#edgeinfo-see-more-in-mianview .author-number{
  margin:2px 0px 8px 0px;
  border-style: solid;
  border-color:#E0E0E0;
  border-top-width: 0px;
  border-right-width: 0px;
  border-bottom-width: 1px;
  border-left-width: 0px;
  font-size: 12px;
}
#edgeinfo-see-more-in-mianview .author-number span{
  width:100%;
  border-spacing: 2px 2px;
  font: normal normal normal normal 12px;
  font-weight: 600;
  
}
#edgeinfo-see-more-in-mianview #author{
    color: #069;
    border-spacing: 2px 2px;
    font: italic normal 300 normal 12px / 20px Lato, sans-serif;
}
#edgeinfo-see-more-in-mianview #venue{
    border-spacing: 2px 2px;
    font: normal normal normal normal 12px / 20px Lato, sans-serif;
}
#edgeinfo-see-more-in-mianview h5{
   color: #069;
}
#edgeinfo-see-more-in-mianview .content{
  width: 489px;
  margin: 1px 1px 1px 1px;

}
#info-paper-box{
  max-height: 700px;
  max-width: 500px;
  overflow: scroll;
}

#edgeinfo-see-more-in-mianview .collapsible {
  color: #444;
  cursor: pointer;
  border: none;
  text-align: left;
  outline: none;
  font-size: 15px;
}

#edgeinfo-see-more-in-mianview .active .collapsible-icon-name, #edgeinfo-see-more-in-mianview .collapsible .collapsible-icon-name:hover {
  background-color: #069;
}


#edgeinfo-see-more-in-mianview .collapsible-content {
  display: none;
  overflow: hidden;
  background-color: #f1f1f1;
}
#edgeinfo-see-more-in-mianview .each-one{
 border-style: solid;
 border-color:#E0E0E0;
 border-top-width: 0px;
 border-right-width: 0px;
 border-bottom-width: 1px;
 border-left-width: 0px;
}
/*.matched-panel-text{
  font-size:12px;
  font-weight: 200;
}*/
#main-view-for-graph #mainsvg{
  /*font-size:12px;*/
  font-weight:500;
}


#legend-box #legend-svg{
  /*max-width: 250px;*/
  /*max-height:36px;*/
}
#legend-box #highlight-legend-svg{
  max-width: 250px;
  max-height:170px;
}

.legend-title{
  font-size: 13px;
  font-weight: 600;
  margin:0px 0px 0px 2px;
}
#highlight-color-legend{
  border-style: solid;
  border-color:#E0E0E0;
  border-top-width: 1px;
  border-right-width: 0px;
  border-bottom-width: 0px;
  border-left-width: 0px;
}
#attr-nodes-selected-table{
  overflow-y: auto;
  overflow-x: auto;
}
#seleced-nodes-list {
    max-height: 80px;
    width: 390px;
    padding: 0px 0px 2px 0px;
    border-style: solid;
    border-color: #ddd;
    border-top-width: 1px;
    border-right-width: 1px;
    border-bottom-width: 1px;
    border-left-width: 1px;
    margin: 0px 0px 0px 0px;
    overflow-y: auto;
    overflow-x: auto;
    padding: 0px 0px 1px 1px;
}
#attr-nodes-selected {
    max-height: 100px;
    width: 390px;
    border-style: solid;
    border-color: #ddd;
    border-top-width: 0px;
    border-right-width: 0px;
    border-bottom-width: 0px;
    border-left-width: 0px;
    margin: 4px 4px 4px 4px;
    border-top-left-radius: 5px;
    border-top-right-radius: 5px;
    border-bottom-left-radius: 5px;
    border-bottom-right-radius: 5px;
}
#jBoxAttribute thead th{
  padding: 0px 0px 0px 0px;
}
#jBoxAttribute .el-tag + .el-tag {
    margin-left: 1px;
}
</style>