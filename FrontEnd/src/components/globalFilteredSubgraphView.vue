<template>
  <div id=filtered-subgraph-view>  
     <div id="filtered-subgraph-box">
        <div id="filtered-subgraph-nav-box">
          <div class="filtered-subgraph-item filtered-subgraph-name">
            <span>Region of Interest</span>
          </div>

          <div class="filtered-subgraph-item filtered-subgraph-info graph-info-display"><!--节点及边的数量-->
            <span>(Nodes:{{subGraphNumNodes}}</span>
            <span>Edges:{{subGraphNumEdges}})</span>
          </div>
          <!-- <span>Subgraph From Graph Overview</span> -->
          <div class="filtered-subgraph-item filtered-subgraph-nav-icon">
            <div class="img-icon-box" id="filtered-subgraph-layout-setting"><!--节点布局设置-->
              <img class="img-icon" id="filtered-subgraph-nav-icons-setting" width="20" height="20" src="../../static/img/icons-setting-blue.png">
            </div>
            <div class="img-icon-box" id="export-roi-view-icon"><!--导出SVG为PNG-->
              <img class="img-icon" id="export-roi-view-svg-img" width="20" height="20" src="../../static/img/export-svg.png">         
            </div>
          </div>
        </div>            
        <svg :id="filteredSubgraphSvg"></svg>
    </div>

    <div id="filtered-subgraph-layout-control">
       <layoutsettingcomponent :bus-event-name="busEventName"></layoutsettingcomponent>
    </div>
    <div id="filtered-subgraph-node-info">
      <nodeinfocomponent :isopenchecknodedetailflag="isopenchecknodedetailflag" :sendnodeinfobusevent="sendNodeInfoBusEvent" :nodeinfobox="nodeInfoBox" :sendsvgidtocomp="filteredSubgraphSvg" :targetselector="seemoretargetselector" :targetoffset="seemoretargetoffset"></nodeinfocomponent>
    </div>
    <div id="interest-attributes">
      <focusattributesselection :callback="callbackForInterestAttributes"></focusattributesselection>
    </div>

  </div>
</template>

<script>
  import axios from 'axios' // 用于AJAX请求
  import * as d3 from '../../static/js/d3.v4.min.js'
  import {d3GraphLayout} from "../../static/js/d3ForceGraph.js"
  import {jBox} from "../../static/js/jBox.js" 
  import $ from 'jquery'
  import {vueFlaskRouterConfig} from '../vueFlaskRouterConfig'
  import bus from '../eventbus.js' // 事件总线.
  import "../../static/js/jquery.contextMenu.js"
  import "../../static/js/jquery.ui.position.js"
  import layoutsettingcomponent from '@/components/layoutSettingComponent'
  import nodeinfocomponent from '@/components/nodeInfoComponent'
  import focusattributesselection from "@/components/focusAttributesSelection"

  import {saveAs} from "../../static/js/FileSaver.min.js" // FileSaver.min.js canvas-toBlob.js
  import "../../static/js/canvas-toBlob.js"

  export default {    
    data: function(){
      return {
         subGraphNumNodes: 0, // 子图节点数量.
         subGraphNumEdges: 0, // 子图边的数量.
         busEventName:"sendFilteredSubgraph", // 用于数据传输的中央事件名称.
         filteredSubgraphSvg: null, // 该组件中svg的id.
         jBoxInstance:{
            layoutSetting: null, // 布局参数弹出窗口.
            nodeDetailJbox: null, // 节点信息窗口.
            interestAttributes: null // 焦点的兴趣属性. jBoxInstance.interestAttributes
         },

         clickedNodeId:'', //之前被点击的节点.
         sendNodeInfoBusEvent: "sendNodeInfoInFilteredSug", // 发送数据给nodeInfoFilteredSubgraph组件的事件名称.
         nodeInfoBox: "filteredsubgraphnodeinfo", // nodeInfoComponent子组件的div的id.
         isopenchecknodedetailflag: [false], //[true] OR [false]

         seemoretargetselector: '#filtered-subgraph-layout-setting', //seemore弹出框弹出的所在位置.
         seemoretargetoffset: {x: -186, y: 80}, //seemore弹出框的位置.
         callbacktointerestattributes: null, // 传递给focusattributesselection的回调函数.
         rightClickNodeGetId: "", // 被右键点击"Add it to the focus set"的节点的id.
         svgForExport: null, // SVG TO PNG
      }
    },
    components: {
      layoutsettingcomponent, //注册组件为元素.
      nodeinfocomponent, //节点信息组件,用于显示节点的信息.
      focusattributesselection // 焦点的属性选择.(选择兴趣属性)
    },
    methods:{
      svgForExportCallback(svg){ // 使用回调函数来获得SVG
        let this_ = this;
        this_.svgForExport = svg;
        // console.log("jingjing svgForExport");
        // console.log(this_.svgForExport);
        // console.log("jingjing svg");
        // console.log(svg);
      },
      initClickExportSvgToPng(width, height){
        let this_ = this;
        $("#export-roi-view-svg-img").click(function(e){
          var svgString = this_.getSVGString(this_.svgForExport.node());
          // var svgString = this_.getSVGString(globalSvg.node());
          this_.svgString2Image(svgString, 2*width, 2*height, 'png', function(dataBlob, filesize){
            saveAs(dataBlob, 'mainView.png' ); // FileSaver.js function
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
      callbackForInterestAttributes(){
        let this_ = this;
        console.log("first click ok");
        let dbName = this_.$store.state.selection.selectiondb; // 取出节点对应的数据库名称   
        let nodeId = this_.rightClickNodeGetId;                        
        let path = vueFlaskRouterConfig.mainViewNodeInfo + dbName + "/" + nodeId; // 复用mainView组件中的右键选为焦点.              
        axios.get(path) // todo:向python后台发送GET请求,这里不能使用post,原因未知.
            .then((res) => { 
              let tabledata = res.data;  // 一个对象: {id:x, name:x, institution, num_papers, num_citation, H_index, P_index, UP_index, interests}
              // console.log("tabledata");console.log(tabledata);
              let dbname = this_.$store.state.selection.selectiondb; // 数据库名称.                      
              let focusObj = {"id": nodeId,  // id作为唯一标识,                                     
                              "dbname":dbname,
                              "field":"NULL", // 非关键词查询,写成NULL没有影响.
                              "keyword": "NULL", // 非关键词查询,这么写没有影响.
                              "attriselect": this_.$store.state.focusAttributesSelection.checkedFocusAttri
                              };
              let row = {}; // {field1: value, ...}
              for(let i=0; i<tabledata.length; i++){
                let tempObj = tabledata[i]; // 临时对象.{key:x, value:x}
                if (tempObj.key == "name" || tempObj.key == "title") {
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
                 // console.log("computedAttri ........");console.log(computedAttri);
                 if(computedAttri.indexOf(key_) != -1){ // 属于被考虑的属性.
                   attributesValue[key_] = row[key_];
                 }           
                  
              }

              focusObj.attributesValue = attributesValue; // 添加属性及其值. 这个是兴趣属性对应的对象,如果兴趣属性是[A, B], attributesValue={A: value, B: value}
              // console.log("focusObj");console.log(focusObj);
              bus.$emit("sendSlectedNode", focusObj); //该事件能避免重复添加.
              $("#" + this_.$store.state.globalFilteredSubgraphView.svgId + " ." + nodeId).css("fill", this_.$store.state.globalFilteredSubgraphView.focusColor); //选为焦点后高亮.

              this_.jBoxInstance.interestAttributes.close(); // 关闭弹窗.

        })
        .catch((error) => {           
          console.error(error);
        });
      },
      toolLipForIcon(){ //鼠标悬浮提示图标对应的功能.
        $('#filtered-subgraph-nav-icons-setting').jBox('Mouse', { // jBox在本文件中并没有引入,但是也能用(在mainView.vue中引入了).
              theme: 'TooltipDark',
              content: 'Layout Settings',
              position: {
                x: 'left',
                y: 'bottom'
             }
        });
        //export-roi-view-svg-img
        $('#export-roi-view-svg-img').jBox('Mouse', { // jBox在本文件中并没有引入,但是也能用(在mainView.vue中引入了).
              theme: 'TooltipDark',
              content: 'Export svg to png',
              position: {
                x: 'left',
                y: 'bottom'
             }
        });
      },
      callbackMouseOver(node, mouseState){ //鼠标悬浮时的回调函数. node:鼠标悬浮时的节点对象.node={id:x,name:x,value:x}.
        let nodeId = node.id;        
        if(mouseState == "mouseover"){ //鼠标悬浮.
          $("#focusesbox ." + nodeId).css("border", "1px solid #2894FF"); //如果是焦点,则高亮焦点标签.
        }
        if(mouseState == "mouseout"){ //鼠标离开.
          $("#focusesbox ." + nodeId).css("border", "1px solid rgba(64,158,255,.2)"); //如果是焦点,则恢复焦点标签样式.
        }
      },
      circleClickEvent(event){ // D3节点点击事件的回调函数,作为参数传到 d3GraphLayout 函数中.这样就能自定义节点点击行为了,便于以后在其他组件中调用d3GraphLayout.
          
        let this_ = this;
        let nodeId = event.id; //节点id.
        console.log("filtered subgraph nodeId");
        console.log(nodeId);
        this_.clickedNodeId = nodeId; //保存节点ID
        // todo:点击查看节点的信息.        
        let css_ = {
            "stroke-dasharray":0,
            "stroke": "#fff",
            "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
        };
        $("#" + this_.$store.state.globalFilteredSubgraphView.svgId + " .nodecircle").css(css_);  // fixme: 所有节点先恢复,然后再高亮点击节点.        
        
        let css = {
            "stroke-dasharray":0,
            "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.clickCheckNodeInfo,
            "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
        };
        $("#" + this_.$store.state.globalFilteredSubgraphView.svgId + " ." + nodeId).css(css); // 点击节点,用黑色圆圈圈起来.

        let dbName = this_.$store.state.selection.selectiondb; // 取出节点对应的数据库名称
        
        // 获取方式与mainView.vue相同.             
        let path = vueFlaskRouterConfig.mainViewNodeInfo + dbName + "/" + nodeId; // 路径
        axios.get(path) // todo:向python后台发送GET请求,这里不能使用post,原因未知.
             .then((res) => { 
              let tabledata = res.data;  // {id, name, institution, num_papers, num_citation, H_index, P_index, UP_index, interests}              
              bus.$emit(this_.sendNodeInfoBusEvent, tabledata); //将请求到的表格数据发送给nodeInfoView.vue组件.
        })
        .catch((error) => {            
          console.error(error);
        });
        
      },

    },
    created(){
      let this_ = this;
      this_.filteredSubgraphSvg = this_.$store.state.globalFilteredSubgraphView.svgId; //svg画布的id初始化.
      bus.$on("sendSelectedNodesInLasso", function (data){
         let selectedNodesList = data; // [{x:x, y:y, id:x}, ...]
         let dbName = this_.$store.state.selection.selectiondb; //数据库名称.
         if(selectedNodesList.length > 0){
            let param = {               
               "selectedNodesList": selectedNodesList, // 选中的节点列表.
               "dbName": dbName
            };            
            axios.post(vueFlaskRouterConfig.getFilteredSubGraph, {
                param: JSON.stringify(param)
            })
            .then((res) => {
               let filteredSubGraph = res.data; // 得到过滤出来的子图.
               this_.$store.state.globalFilteredSubgraphView.globalFilteredGraph = filteredSubGraph; // 保存到store的全局变量中.
               console.log("filteredSubGraph");console.log(filteredSubGraph);
               bus.$emit("recieveFilteredSubgraphData", filteredSubGraph); // 在总接收口接受数据,并进行布局.

            })
            .catch((error) => {            
              console.error(error);
            });
         }                 
      });

      bus.$on(this_.busEventName, function(data){ // 布局参数更新,重新布局.
          let isReLayout = data[0]; //是否重新布局.
          let setting = data[1]; // 参数.
          if(isReLayout){ //true: 重新布局.
            if(this_.$store.state.globalFilteredSubgraphView.globalFilteredGraph != null){
              this_.$store.state.globalFilteredSubgraphView.layoutSettings = setting;           
              
              let data = this_.$store.state.globalFilteredSubgraphView.globalFilteredGraph;
              bus.$emit("recieveFilteredSubgraphData", data); // 在总接收口接受数据,并进行布局.
              
              for(let i=0; i<this_.$store.state.globalFilteredSubgraphView.focusStateList.length; i++){
                let nodeId = this_.$store.state.globalFilteredSubgraphView.focusStateList[i]; //焦点节点.
                $("#" + svgId + " ." + nodeId).css("fill", this_.$store.state.globalFilteredSubgraphView.focusColor); //高亮                       
              }              
            }
          }
          else{ //false: 不需要重新布局, 通过样式来控制标签的显示.
            if(setting){ //true.
              $("#global-filtered-graph-box #filtered-subgraph-view .nodes text").css("display", "block");
              this_.$store.state.globalFilteredSubgraphView.layoutSettings.labelDisplay = true; //由于d3GraphLayout中布局参数是通过地址传入的,所以改变this_.$store.state.resultsSearchView.layoutSettings中labelDisplay的值就能直接改变函数中的参数,而不需要再次执行d3GraphLayout函数.
            }
            else{ //false.
              $("#global-filtered-graph-box #filtered-subgraph-view .nodes text").css("display", "none");
              this_.$store.state.globalFilteredSubgraphView.layoutSettings.labelDisplay = false;
            }            
          }
      });

      bus.$on("recieveFilteredSubgraphData", function (data){ //作为过滤子图数据接收的总入口,对选中的子图进行布局. data={graph:{nodes:[], links:[]}, directed:x}
        
        let graph = data.graph;
        let directed = data.directed;
        this_.subGraphNumNodes = graph.nodes.length;
        this_.subGraphNumEdges = graph.links.length;
        let layoutSettings = this_.$store.state.globalFilteredSubgraphView.layoutSettings;
        let svgId = this_.$store.state.globalFilteredSubgraphView.svgId;
        let svgWidth = this_.$store.state.globalFilteredSubgraphView.svgWidth;
        let svgHeight = this_.$store.state.globalFilteredSubgraphView.svgHeight;                   
        d3GraphLayout(graph, directed, layoutSettings, svgId, svgWidth, svgHeight,this_.circleClickEvent, null, this_.callbackMouseOver, null, this_.svgForExportCallback);
        console.log("this_.svgForExport");console.log(this_.svgForExport);
        // 新建节点信息弹窗.
        this_.jBoxInstance.nodeDetailJbox = new jBox('Modal', {
            id: "jBoxNodeInfoInFilteredSubgraph",
            addClass: "jBoxCircleInfoInFilteredSubgraph",  // 添加类型,这个功能很棒啊!
            attach: "#" + this_.$store.state.globalFilteredSubgraphView.svgId + " .nodecircle",
            width: 280,                
            title: 'Node Details',
            overlay: false,
            createOnInit: true,
            content: $("#filtered-subgraph-node-info"),  // 节点信息框.
            draggable: true,
            repositionOnOpen: false,
            repositionOnContent: true,
            target: $(".filtered-subgraph-name"),//$('.filtered-subgraph-info'),
            offset: {x: 34, y: 145},      
            // position:this_.$store.state.jboxPositionSet.topLeftSide,                   
            onOpen: function(){ // 每次点击节点查看细节的时候都会进入这个函数. 
              this_.jBoxInstance.nodeDetailJbox.position({
                target: $(".filtered-subgraph-name"),//$('.filtered-subgraph-info')           
              });    
              
              this_.$store.state.globalFilteredSubgraphView.clickNode2GetId = this_.clickedNodeId; // 获得被点击的节点的id.
              this_.isopenchecknodedetailflag.pop(); //将旧的值弹出.
              this_.isopenchecknodedetailflag.push(true); //压入新值,这样保证只有一个值.

            },
            onCloseComplete: function(){
                this_.isopenchecknodedetailflag.pop(); //将旧的值弹出.
                this_.isopenchecknodedetailflag.push(false); //压入新值,这样保证只有一个值.

                let isSeeMoreBoxOpen = $("." + this_.sendNodeInfoBusEvent + "jBoxSeeMoreOfNode").css("display"); // 判断子组件中seemore框是否关闭.block:open, none:close
               
                // todo: 发生一个很诡异的现象: 明明see more框还开着确说已经关闭了,最后使用jquery的css方法查看diaplay == block 或none来判断是否关闭.
                if(isSeeMoreBoxOpen == "block"){ // See More框打开着.
                    // console.log("main  See More框打开着.
                    let css = {
                      "stroke-dasharray":0,
                      "stroke": "#fff",
                      "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
                    };
                    $("#" + this_.$store.state.globalFilteredSubgraphView.svgId + " .nodecircle").css(css); // 所有节点恢复原样式.

                    // 用黑圈圈定对应的节点.
                    let cssNode = {
                        "stroke-dasharray":0,
                        "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.clickCheckNodeInfo,
                        "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                    };
                    let nodeId = this_.$store.state.globalFilteredSubgraphView.clickNode2GetId;//使用clickNode2GetId的目的;如果seemore弹窗没有关闭,则节点仍然高亮,用于指示seemore框.
                    $("#" + this_.$store.state.globalFilteredSubgraphView.svgId + " ." + nodeId).css(cssNode); // 点击节点,用黑色圆圈圈起来.
                }
                if(isSeeMoreBoxOpen == "none"){ // See More框关闭.
                  // console.log("main See More框关闭");
                  let css = {
                    "stroke-dasharray":0,
                    "stroke": "#fff",
                    "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
                  };
                  $("#" + this_.$store.state.globalFilteredSubgraphView.svgId + " .nodecircle").css(css); // 所有节点恢复原样式.

                }
            }
        });

        if($(".jBoxCircleInfoInFilteredSubgraph").length > 1){  // 这样可以避免出现多个id=jBoxNodeInfo的div.
           $("#jBoxNodeInfoInFilteredSubgraph").remove(); //删除第一个,保证只出现当前jbox.
        }
        
      });

      bus.$on("clearGraphEVFlag", function(flag){
         if(flag){
           this_.subGraphNumNodes = 0; // 子图节点数量.
           this_.subGraphNumEdges = 0; // 子图边的数量.
         }
      });
    },
    mounted(){
      let this_ = this;
      $.contextMenu({  // fixme: 在结果过滤子图的布局图中右键节点,选为焦点+删除焦点.
        selector: '#' + this_.filteredSubgraphSvg + ' .nodecircle', //绑定到当前svg节点上.
        className: "focusSelectionMenu", // 添加自定义类名称.        
        callback: function(key, options) {     
             let nodeId = options.$trigger.context.classList[1]; // todo: 在搜索结果可视化布局中选中某个节点作为焦点.
             
             // console.log("filteredSubgraphSvg nodeId");console.log(nodeId);
             if(key == "copy"){  // 选为焦点,并添加到焦点集中.
                this_.rightClickNodeGetId = nodeId; //更新节点Id.
             }
             if (key == "cut"){ //取消焦点,并在焦点集中删除对应的焦点.
               
               let param = {
                 svgId: this_.$store.state.globalFilteredSubgraphView.svgId,
                 nodeColor: this_.$store.state.globalFilteredSubgraphView.layoutSettings.nodeColor
               }
               bus.$emit("sendDeleteFocusInFilteredSubgraph", [nodeId, param, this_.$store.state.globalFilteredSubgraphView.isOpenFilteredSubgraph]); //发送删除焦点的信号.               
             }
        },
        items: { // todo:以后修改图标.                      
                             
            "copy": {name: "Add it to the focus set", className: "addToTheFocusSet"}, // 作为焦点. , icon: "copy" 
            "cut": {name: "Delete it from the focus set"},              
            "quit": {name: "Quit"}                
        }                   
      });

      this_.jBoxInstance.layoutSetting = new jBox('Modal', {
        id: "jBoxFilteredSubgraphLayoutSetting",
        addClass: "jBoxFilteredSubgraphLayoutSettingInfo",  // 添加类型,这个功能很棒啊!
        attach: '#filtered-subgraph-nav-icons-setting',
        width: 300,              // Maximal width
        height: 230,             // Maximal height 
        title: 'Layout Setting',
        // fixed:true,
        overlay: false,
        fixed: false,
        adjustTracker: true,
        zIndex: 1005, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
        createOnInit: true,
        content: $('#filtered-subgraph-layout-control'),  // jQuery('#jBox-content') 
        draggable: false,
        repositionOnOpen: false,
        repositionOnContent: true,
        target: $('#filtered-subgraph-nav-icons-setting'),//$('#filtered-subgraph-nav-icons-setting'),
        offset: {x: -135, y: 155}, // {x: -135, y: 155},
        // 以下是弹窗事件,这些功能真的非常优秀!
        onOpen: function(){                   
          this_.jBoxInstance.layoutSetting.position({
            target: $('#filtered-subgraph-nav-icons-setting'),//$('#filtered-subgraph-nav-icons-setting') //注意,这样保证:当 jBoxInstance.resultVis 移动后,重新打开layoutSetting,layoutSetting能够跟着jBoxInstance.resultVis走.           
          });
        },
        onCloseComplete: function(){                     
        }
      });
      this_.jBoxInstance.interestAttributes = new jBox('Modal', {
        id: "jBoxInterestAttributes", // 弹出兴趣属性选择框.
        addClass: "jBoxInterestAttributesClass",  // 添加类型,这个功能很棒啊!
        attach: '.focusSelectionMenu .addToTheFocusSet',
        width: 300,              // Maximal width
        height: 150,             // Maximal height 
        title: 'Attributes of Interest',
        // fixed:true,
        overlay: false,
        fixed: false,
        adjustTracker: true,
        zIndex: 1005, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
        createOnInit: true,
        content: $("#interest-attributes"),  // jQuery('#jBox-content') 
        draggable: true,
        repositionOnOpen: false,
        repositionOnContent: true,
        target: $('.focusSelectionMenu .addToTheFocusSet'),//$('#filtered-subgraph-nav-icons-setting'),
        offset: {x: -135, y: 100}, // {x: -135, y: 155},
        // 以下是弹窗事件,这些功能真的非常优秀!
        onOpen: function(){                   
            this_.jBoxInstance.interestAttributes.position({
               target: $('.focusSelectionMenu .addToTheFocusSet')//$('#filtered-subgraph-nav-icons-setting') //注意,这样保证:当 jBoxInstance.resultVis 移动后,重新打开layoutSetting,layoutSetting能够跟着jBoxInstance.resultVis走.           
            });
            bus.$emit("attributesOfInterestPanelUpdate", true); // 提醒 "兴趣属性选择" 面板更新勾选列表.
        },
        onCloseComplete: function(){                     
        }
      });
      this_.toolLipForIcon();
      this_.initClickExportSvgToPng(this_.$store.state.globalFilteredSubgraphView.svgWidth, this_.$store.state.globalFilteredSubgraphView.svgHeight);
      

    },
    updated(){
        let this_ = this;
        console.log("filtered subgraph");
        
        
    },
    beforeDestroy(){      
      let this_ = this;
      bus.$off("sendSelectedNodesInLasso");   
      bus.$off(this_.busEventName);
      bus.$off("recieveFilteredSubgraphData");
      bus.$off("clearGraphEVFlag");
    }    
  }
</script>

<style>
#filtered-subgraph-node-info{
  display: none;
}
#interest-attributes{
  display: none;
}
#filtered-subgraph-layout-control{
  display: none;
}

#filtered-subgraph-nav-box{
   height:24px;
   vertical-align:middle; /* 垂直居中 */
   background-color: #f5f5f5; /*#f5f5f5*/
}

#filtered-subgraph-nav-box .filtered-subgraph-item{
  display:inline-block;
}
#filtered-subgraph-nav-box .filtered-subgraph-nav-icon{
  float: right;
   
}

#filtered-subgraph-layout-setting{
   /* 水平居中 */
   text-align:center; 
   /* 垂直居中 */ 
   vertical-align:middle;
}
.context-menu-list{
     min-width: 100px;
     max-width: 350px;
}
.filtered-subgraph-name{
  font-weight: 500;
}
.jBox-Modal .jBox-title {
    border-radius: 4px 4px 0 0;
    padding: 15px 20px;
    background: #080808;
    border-bottom: 1px solid #eee;  
  }
</style>
