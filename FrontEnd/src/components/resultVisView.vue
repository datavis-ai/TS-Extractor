<template>
  <div id="resultssearchvis">
   
    <div id="searchResultVisSvg-box">
        <div id="result-vis-nav-box">
          <div class="result-vis-item result-vis-box-name">
            <span>Search Results</span>
          </div>
          <div class="result-vis-item result-vis-graph-info graph-info-display"><!--节点及边的数量-->
            <span>Nodes:{{resultNumNodes}}</span>
            <span>| Edges:{{resultNumEdge}}</span>
          </div>
          <!-- <div class="result-vis-item result-vis-box-name">
            <span>Subgraph From Search Results</span>
          </div> -->
          
          <div class="result-vis-item result-vis-nav-icon">
            <div class="img-icon-box" id="result-vis-layout-setting"><!--节点布局设置-->
              <img class="img-icon" id="result-vis-nav-icons-setting" width="20" height="20" src="../../static/img/icons-setting-blue.png">
            </div>
            <div class="img-icon-box" id="export-resultvis-view-icon"><!--导出SVG为PNG-->
              <img class="img-icon" id="export-resultvis-view-svg-img" width="20" height="20" src="../../static/img/export-svg.png">         
            </div>
          </div>
        </div>            
        <svg :id="searchResultVisSvg"></svg>
    </div>

    <div id="result-vis-layout-control">
       <layoutsettingcomponent :bus-event-name="busEventName"></layoutsettingcomponent>
    </div>

    <div id="interest-attributes-result-vis">
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
  import focusattributesselection from "@/components/focusAttributesSelection"

  import {saveAs} from "../../static/js/FileSaver.min.js" // FileSaver.min.js canvas-toBlob.js
  import "../../static/js/canvas-toBlob.js"

  export default {    
    data: function(){
      return {
         busEventName: "sendLayoutSetOut",
         jBoxInstance:{
           layoutSetting: null,
           interestAttributes: null, // 焦点的兴趣属性. jBoxInstance.interestAttributes
         },
         resultNumNodes: 0, //节点数量
         resultNumEdge: 0, //边数量.

         svgWidth: 1300,
         svgHeight: 890,
         searchResultVisSvg: null, // svg的id.
         rightClickNodeGetId: "", // 被右键点击"Add it to the focus set"的节点的id.
         svgForExport: null, // svg to png.
      }
    },
    components: {
      layoutsettingcomponent,
      focusattributesselection
    },
    methods:{
      svgForExportCallback(svg){ // 使用回调函数来获得SVG
        let this_ = this;
        this_.svgForExport = svg;
      },
      initClickExportSvgToPng(width, height){
        let this_ = this;
        $("#export-resultvis-view-svg-img").click(function(e){
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
        let nodeId = this_.rightClickNodeGetId;
        let row = null; // 节点的信息,对应表格中的一行.
        for(let i=0; i<this_.$store.state.resultsSearchView.tableData.length; i++){ // 从表格数据中选出被点击节点对应的记录.
           let obj = this_.$store.state.resultsSearchView.tableData[i];
           if(obj.id == nodeId){ // 如果id相同,则找到了.
             row = obj;
             break; // 直接跳出大循环,避免继续找下去.注意,一定可以找到,除非出错了.
           }
        }
        let id = row.id; // 节点id. string类型.
        let tag = row.name; // 名字作为节点标签. 
        let dbname = this_.$store.state.selection.selectiondb; // 数据库名称.
        
        let field =  this_.$store.state.selection.selectionfield; // 数据库表字段.
        let keyword = this_.$store.state.selection.keyword; // 数据库表字段对应的关键字.
        let fieldString = field;
        let keywordString = keyword;
        let consObjList = this_.$store.state.conditionsSearch.formDataList; //[{selectionfield:"All", keyWord:""}, ...]
        for(let i=0; i<consObjList.length; i++){
          let obj = consObjList[i];
          let field = obj.selectionfield;
          let keyWord = obj.keyWord;
          fieldString += ";" + field;
          keywordString += ";" + keyWord;
        } 
        
        let focusObj = {"id": id,  // id作为唯一标识,
                        "tag": tag, // tag作为节点的标签.
                        "dbname":dbname,
                        "field":fieldString,
                        "keyword": keywordString,
                        "attriselect": this_.$store.state.focusAttributesSelection.checkedFocusAttri
        };
        
        let attributesValue = {};
        let keysRow = Object.keys(row); // 获得键列表. [field1, ...]         
        let keysType = this_.$store.state.fields.fieldsType; // 字段类型.{字段:类型,...}
        // console.log("keysType");console.log(keysType);
        for(let i=0; i<keysRow.length; i++){
           let key_ = keysRow[i]; // 键
           let type_ = keysType[key_]; // 类型
           let computedAttri = this_.$store.state.focusAttributesSelection.checkedFocusAttri;
           if(computedAttri.indexOf(key_) != -1){ // 属于被考虑的属性.
             attributesValue[key_] = row[key_];
           }
        }        
        focusObj.attributesValue = attributesValue; // 添加属性及其值.
        // console.log("sendSlectedNode");console.log(focusObj);
        bus.$emit('sendSlectedNode', focusObj); //sendSlectedNode事件,在focusSetView.vue中监听.
        $("#search-result-table ." + nodeId + " td:first-child").css("background-color", this_.$store.state.resultsSearchView.focusColor); //选中该点作为焦点后,高亮.                  
        $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css("fill", this_.$store.state.resultsSearchView.focusColor); //选为焦点后高亮.
        this_.$store.state.resultsSearchView.focusStateList.push(nodeId); //将该点的id记录在案.
        this_.jBoxInstance.interestAttributes.close();

      },
      toolLipForIcon(){ //鼠标悬浮提示图标对应的功能.
        $('#result-vis-nav-icons-setting').jBox('Mouse', { // jBox在本文件中并没有引入,但是也能用(在mainView.vue中引入了).
              theme: 'TooltipDark',
              content: 'Layout Settings',
              position: {
                x: 'left',
                y: 'bottom'
             }
        });
        $('#export-resultvis-view-svg-img').jBox('Mouse', { // jBox在本文件中并没有引入,但是也能用(在mainView.vue中引入了).
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
          $("#focusesbox ." + nodeId).css("border", "1px solid rgba(64,158,255,.2)"); //如果是焦点,则恢复焦点标签样式. rgba(64,158,255,.2)
        }
      },
      seeCurrentPage(nodeId){ //寻找nodeId所在页面.
        let this_ = this;
        let index = null; //nodeId所在的索引.
        let tableLength = this_.$store.state.resultsSearchView.tableData.length;
        for(let i=0; i<tableLength; i++){
          let row = this_.$store.state.resultsSearchView.tableData[i];
          if(nodeId == row.id){ //找到匹配的id.
             index = i;
             break;
          }
        }
        let currentPage = 0;
        let calculate = index/this_.$store.state.resultsSearchView.pageSize;
        currentPage = parseInt(calculate) + 1; //由索引计算出当前所在页.
        return currentPage;
      },
      circleClickEvent(event){ // D3节点点击事件的回调函数,作为参数传到 d3GraphLayout 函数中.这样就能自定义节点点击行为了,便于以后在其他组件中调用d3GraphLayout.
          
        let this_ = this;
        let nodeId = event.id; //节点id.        
        this_.$store.state.resultsSearchView.tableRowSortList = []; //清零.
        $("#search-result-table .el-table__body tbody").find("tr").each(function(){
            let className = $(this).attr("class");
            let classNameList = className.split(" ");
            let letterCalssList = ["context-menu-active", "current-row", "el-table__row"];
            for(let i=0; i<classNameList.length; i++){
              if(letterCalssList.indexOf(classNameList[i]) == -1){ // 不在里面.则为id.
                this_.$store.state.resultsSearchView.tableRowSortList.push(classNameList[i]);
              }
            }

        });
        
        let index = -1;
        if(this_.$store.state.resultsSearchView.tableRowSortList.indexOf(nodeId) != -1){ //在里面,在当前页面.
           console.log("in current page");
           index = this_.$store.state.resultsSearchView.tableRowSortList.indexOf(nodeId) + 1;
           bus.$emit("sendLocalTablePosInClickEvent", [nodeId, index]);
        }
        else{ //不在里面.不在当前页面.
          console.log("not in current page");
          let currentPage = this_.seeCurrentPage(nodeId); //bus.$emit("sendSeeCurrentPage", nodeId);
          // this_.$store.state.resultsSearchView.currentPage = currentPage;
          bus.$emit("sendCurrentPage", currentPage); //将当前页发送给resultsSearchView.vue
          this_.$store.state.resultsSearchView.refreshTablePageFlagForClickNode = true; //表格刷新页面标志位.
          this_.$store.state.resultsSearchView.clickNodeId = nodeId; //保存节点id.
        }
      }

      
    },
    created(){
      let this_ = this;
      this_.svgWidth = this_.$store.state.resultsSearchView.svgWidth; //svg的宽度.
      this_.svgHeight = this_.$store.state.resultsSearchView.svgHeight; // svg的高度.
      this_.searchResultVisSvg = this_.$store.state.resultsSearchView.svgId; //初始化svg的id.
      this_.busEventName = this_.$store.state.resultsSearchView.busEventName;
      bus.$on(this_.busEventName, function(data){ // 布局参数更新,重新布局.
          let isReLayout = data[0]; //是否重新布局.
          let setting = data[1]; // 参数.
          if(isReLayout){ //true: 重新布局.
            if(this_.$store.state.resultsSearchView.resultVisGraph != null){
              this_.$store.state.resultsSearchView.layoutSettings = setting;           
              
              let data = this_.$store.state.resultsSearchView.resultVisGraph;              
              let graph = data.graph;
              let directed = data.directed;
              this_.resultNumNodes = graph.nodes.length;
              this_.resultNumEdge = graph.links.length;
              let layoutSettings = this_.$store.state.resultsSearchView.layoutSettings;
              let svgId = this_.$store.state.resultsSearchView.svgId;
              let svgWidth = this_.svgWidth;
              let svgHeight = this_.svgHeight;                   
              d3GraphLayout(graph, directed, layoutSettings, svgId, svgWidth, svgHeight,this_.circleClickEvent, null, this_.callbackMouseOver, null, this_.svgForExportCallback);
              for(let i=0; i<this_.$store.state.resultsSearchView.focusStateList.length; i++){
                let nodeId = this_.$store.state.resultsSearchView.focusStateList[i]; //焦点节点.
                 $("#" + svgId + " ." + nodeId).css("fill", this_.$store.state.resultsSearchView.focusColor); //高亮                       
              }
              if(this_.$store.state.resultsSearchView.tableRowClickNodeList.length > 0){ //非空.
                let css = {
                 "stroke-dasharray":0,
                 "stroke": "black",
                 "stroke-width": 3
                };
                $("#" + this_.$store.state.resultsSearchView.svgId + " ." + this_.$store.state.resultsSearchView.tableRowClickNodeList[0]).css(css); //用黑圈圈起来.
              }
            }
          }
          else{ //false: 不需要重新布局, 通过样式来控制标签的显示.
            if(setting){ //true.
              $("#resultssearchvis #searchResultVisSvg-box .nodes text").css("display", "block");
              this_.$store.state.resultsSearchView.layoutSettings.labelDisplay = true; //由于d3GraphLayout中布局参数是通过地址传入的,所以改变this_.$store.state.resultsSearchView.layoutSettings中labelDisplay的值就能直接改变函数中的参数,而不需要再次执行d3GraphLayout函数.
            }
            else{ //false.
              $("#resultssearchvis #searchResultVisSvg-box .nodes text").css("display", "none");
              this_.$store.state.resultsSearchView.layoutSettings.labelDisplay = false;
            }            
          }
      });
      bus.$on("sendClickResultVis", function (data){ //点击result vis 打开布局.
         if(data){ //如果为true.
            let css = {
              background:"#409EFF",
              color:"#fff"                       
            };         
            $("#result-vis-icon-div").css(css); //变蓝.            
            this_.$store.state.resultsSearchView.isOpenResultVis = true; //打开弹窗.
            if(this_.$store.state.resultsSearchView.resultVisGraph == null){
                let resultNodesList = [];
                for(let i=0; i < this_.$store.state.resultsSearchView.tableData.length; i++){
                  let obj = this_.$store.state.resultsSearchView.tableData[i];
                  resultNodesList.push(obj.id); // [id0, ...] id是string类型的.
                }
                let dbName = this_.$store.state.selection.selectiondb; // 数据库名称.
                let param = {"dbName": dbName, "resultNodesList": resultNodesList}; //将条件发送到后台,请求匹配的节点数据.                  
                axios.post(vueFlaskRouterConfig.getSearchResultGraph, {
                  param: JSON.stringify(param)
                })
                .then((res) => {                    
                  let data = res.data;
                  this_.$store.state.resultsSearchView.resultVisGraph = data; //JSON.parse(JSON.stringify(data)), 保存在this_.$store.state.resultsSearchView.resultVisGraph中.
                  // 及时保留更新的原图数据以及焦点数据,但是要注意原图是一个对象,而对象传递参数时是传递地址的,即引用,所以要深度拷贝保存.              
                  let graph = data.graph;
                  let directed = data.directed;
                  this_.resultNumNodes = graph.nodes.length;
                  this_.resultNumEdge = graph.links.length;
                  let layoutSettings = this_.$store.state.resultsSearchView.layoutSettings;
                  let svgId = this_.$store.state.resultsSearchView.svgId;
                  let svgWidth = this_.svgWidth;
                  let svgHeight = this_.svgHeight;                   
                  d3GraphLayout(graph, directed, layoutSettings, svgId, svgWidth, svgHeight,this_.circleClickEvent, null, this_.callbackMouseOver, null, this_.svgForExportCallback);
                  for(let i=0; i<this_.$store.state.resultsSearchView.focusStateList.length; i++){
                    let nodeId = this_.$store.state.resultsSearchView.focusStateList[i]; //焦点节点.
                     $("#" + svgId + " ." + nodeId).css("fill", this_.$store.state.resultsSearchView.focusColor); //高亮                       
                  }
                  if(this_.$store.state.resultsSearchView.tableRowClickNodeList.length > 0){ //非空.
                    let css = {
                     "stroke-dasharray":0,
                     "stroke": "black",
                     "stroke-width": 3
                    };
                    $("#" + this_.$store.state.resultsSearchView.svgId + " ." + this_.$store.state.resultsSearchView.tableRowClickNodeList[0]).css(css); //用黑圈圈起来.
                  }               
                  
                  })
                .catch((error) => {            
                  console.error(error);
                });
            }
            else{
                  let data = this_.$store.state.resultsSearchView.resultVisGraph;
                  let graph = data.graph;
                  let directed = data.directed;
                  this_.resultNumNodes = graph.nodes.length;
                  this_.resultNumEdge = graph.links.length;
                  let layoutSettings = this_.$store.state.resultsSearchView.layoutSettings;
                  let svgId = this_.$store.state.resultsSearchView.svgId;
                  let svgWidth = this_.svgWidth;
                  let svgHeight = this_.svgHeight;                   
                  d3GraphLayout(graph, directed, layoutSettings, svgId, svgWidth, svgHeight,this_.circleClickEvent, null, this_.callbackMouseOver, null, this_.svgForExportCallback);
                  for(let i=0; i<this_.$store.state.resultsSearchView.focusStateList.length; i++){
                    let nodeId = this_.$store.state.resultsSearchView.focusStateList[i]; //焦点节点.
                     $("#" + svgId + " ." + nodeId).css("fill", this_.$store.state.resultsSearchView.focusColor); //高亮                       
                  }
                  if(this_.$store.state.resultsSearchView.tableRowClickNodeList.length > 0){ //非空.
                    let css = {
                     "stroke-dasharray":0,
                     "stroke": "black",
                     "stroke-width": 3
                    };
                    $("#" + this_.$store.state.resultsSearchView.svgId + " ." + this_.$store.state.resultsSearchView.tableRowClickNodeList[0]).css(css); //用黑圈圈起来.
                  }
            }
         }
         else{ //关闭result vis.
            let css = {              
              "background":"#ddd",
              "color":"#000",          
            };         
            $("#result-vis-icon-div").css(css); //变灰.           
            this_.$store.state.resultsSearchView.isOpenResultVis = false;
            this_.jBoxInstance.layoutSetting.close(); //布局设置弹窗,随着result vis 关闭.
            $("#" + this_.$store.state.resultsSearchView.svgId + " > *").remove(); // 清除svg中的内容,以提高性能.
            this_.resultNumNodes = 0; //节点数量.
            this_.resultNumEdge = 0; //边的数量.
         }
      });
    },
    beforeDestroy(){
      let this_ = this;       
      bus.$off(this_.busEventName);
      bus.$off("sendClickResultVis");
    },
    mounted(){
      let this_ = this;
      $.contextMenu({  // fixme: 在结果可视化图中右键节点,选为焦点.
        selector: '#'+ this_.$store.state.resultsSearchView.svgId + ' .nodecircle',
        className: "focusSelectionMenuSearchVis",
        callback: function(key, options) {     
             let nodeId = options.$trigger.context.classList[1]; // todo: 在搜索结果可视化布局中选中某个节点作为焦点.             
             if(key == "copy"){ // 选为焦点,并添加到焦点集中.
                this_.rightClickNodeGetId = nodeId;
                // let row = null; // 节点的信息,对应表格中的一行.
                // for(let i=0; i<this_.$store.state.resultsSearchView.tableData.length; i++){ // 从表格数据中选出被点击节点对应的记录.
                //    let obj = this_.$store.state.resultsSearchView.tableData[i];
                //    if(obj.id == nodeId){ // 如果id相同,则找到了.
                //      row = obj;
                //      break; // 直接跳出大循环,避免继续找下去.注意,一定可以找到,除非出错了.
                //    }
                // }
                // let id = row.id; // 节点id. string类型.
                // let tag = row.name; // 名字作为节点标签. 
                // let dbname = this_.$store.state.selection.selectiondb; // 数据库名称.
                
                // let field =  this_.$store.state.selection.selectionfield; // 数据库表字段.
                // let keyword = this_.$store.state.selection.keyword; // 数据库表字段对应的关键字.
                // let fieldString = field;
                // let keywordString = keyword;
                // let consObjList = this_.$store.state.conditionsSearch.formDataList; //[{selectionfield:"All", keyWord:""}, ...]
                // for(let i=0; i<consObjList.length; i++){
                //   let obj = consObjList[i];
                //   let field = obj.selectionfield;
                //   let keyWord = obj.keyWord;
                //   fieldString += ";" + field;
                //   keywordString += ";" + keyWord;
                // } 
                
                // let focusObj = {"id": id,  // id作为唯一标识,
                //                 "tag": tag, // tag作为节点的标签.
                //                 "dbname":dbname,
                //                 "field":fieldString,
                //                 "keyword": keywordString,
                //                 "attriselect": this_.$store.state.focusAttributesSelection.checkedFocusAttri
                // };
                
                // let attributesValue = {};
                // let keysRow = Object.keys(row); // 获得键列表. [field1, ...]         
                // let keysType = this_.$store.state.fields.fieldsType; // 字段类型.{字段:类型,...}
                // // console.log("keysType");console.log(keysType);
                // for(let i=0; i<keysRow.length; i++){
                //    let key_ = keysRow[i]; // 键
                //    let type_ = keysType[key_]; // 类型
                //    let computedAttri = this_.$store.state.focusAttributesSelection.checkedFocusAttri;
                //    if(computedAttri.indexOf(key_) != -1){ // 属于被考虑的属性.
                //      attributesValue[key_] = row[key_];
                //    }
                // }        
                // focusObj.attributesValue = attributesValue; // 添加属性及其值.
                // // console.log("sendSlectedNode");console.log(focusObj);
                // bus.$emit('sendSlectedNode', focusObj); //sendSlectedNode事件,在focusSetView.vue中监听.
                // $("#search-result-table ." + nodeId + " td:first-child").css("background-color", this_.$store.state.resultsSearchView.focusColor); //选中该点作为焦点后,高亮.                  
                // $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css("fill", this_.$store.state.resultsSearchView.focusColor); //选为焦点后高亮.
                // this_.$store.state.resultsSearchView.focusStateList.push(nodeId); //将该点的id记录在案.                         
             
             }
             if (key == "cut"){
               this_.$store.state.resultsSearchView.focusStateList.splice(this_.$store.state.resultsSearchView.focusStateList.indexOf(nodeId), 1); //删除nodeId.
               let param = {
                 svgId: this_.$store.state.resultsSearchView.svgId,
                 nodeColor: this_.$store.state.resultsSearchView.layoutSettings.nodeColor
               }
               bus.$emit("sendDeleteFocusInResultVis", [nodeId, param, this_.$store.state.resultsSearchView.isOpenResultVis]);
             }
        },
        items: { // todo:以后修改图标.                       
                             
            "copy": {name: "Add it to the focus set", className: "addToTheFocusSet"}, // 作为焦点. , icon: "copy" 
            "cut": {name: "Delete it from the focus set"},              
            "quit": {name: "Quit"}            
        }                   
      });
      this_.jBoxInstance.interestAttributes = new jBox('Modal', {
          id: "jBoxInterestAttributesSearchVis", // 弹出兴趣属性选择框.
          addClass: "jBoxInterestAttributesSearchVisClass",  // 添加类型,这个功能很棒啊!
          attach: '.focusSelectionMenuSearchVis .addToTheFocusSet',
          width: 300,              // Maximal width
          height: 150,             // Maximal height 
          title: 'Attributes of Interest',
          // fixed:true,
          overlay: false,
          fixed: false,
          adjustTracker: true,
          zIndex: 1005, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
          createOnInit: true,
          content: $("#interest-attributes-result-vis"),  // jQuery('#jBox-content') 
          draggable: true,
          repositionOnOpen: false,
          repositionOnContent: true,
          target: $('.focusSelectionMenuSearchVis .addToTheFocusSet'),//$('#filtered-subgraph-nav-icons-setting'),
          offset: {x: -135, y: 100}, // {x: -135, y: 155},
          // 以下是弹窗事件,这些功能真的非常优秀!
          onOpen: function(){                   
              this_.jBoxInstance.interestAttributes.position({
                 target: $('.focusSelectionMenuSearchVis .addToTheFocusSet')//$('#filtered-subgraph-nav-icons-setting') //注意,这样保证:当 jBoxInstance.resultVis 移动后,重新打开layoutSetting,layoutSetting能够跟着jBoxInstance.resultVis走.           
              });
              bus.$emit("attributesOfInterestPanelUpdate", true); // 提醒 "兴趣属性选择" 面板更新勾选列表.
          },
          onCloseComplete: function(){                     
            
          }
      });

      this_.jBoxInstance.layoutSetting = new jBox('Modal', {
        id: "jBoxresultVisLayoutSetting",
        addClass: "jBoxresultVisLayoutSettingInfo",  // 添加类型,这个功能很棒啊!
        attach: '#result-vis-nav-icons-setting',  // 这是节点属性探索图标,定义在infoSearchView.vue文件中.
        width: 200,              // Maximal width
        height: 156,             // Maximal height 
        title: 'Layout Setting',
        // fixed:true,
        overlay: false,
        fixed: false,
        adjustTracker: true,
        zIndex: 1005, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
        createOnInit: true,
        content: $('#result-vis-layout-control'),  // jQuery('#jBox-content') 
        draggable: false,
        repositionOnOpen: false,
        repositionOnContent: true,
        target: $('#result-vis-nav-icons-setting'),
        offset: {x: -90, y: 110},
        // 以下是弹窗事件,这些功能真的非常优秀!
        onOpen: function(){                   
          this_.jBoxInstance.layoutSetting.position({
            target: $('#result-vis-nav-icons-setting') //注意,这样保证:当 jBoxInstance.resultVis 移动后,重新打开layoutSetting,layoutSetting能够跟着jBoxInstance.resultVis走.           
          });
        },
        onCloseComplete: function(){                     
        }
      });
      this_.toolLipForIcon(); // 图标功能提示.    
      this_.initClickExportSvgToPng(this_.$store.state.globalFilteredSubgraphView.svgWidth, this_.$store.state.globalFilteredSubgraphView.svgHeight);
    }    
  }
</script>

<style>
#result-vis-layout-control{
  display:none;
}
#result-vis-nav-box{
   height:24px;
   vertical-align:middle; /* 垂直居中 */
   background-color: #f5f5f5; /*#f5f5f5*/
   margin: 0px 0px 0px 0px;
}
#result-vis-nav-box .result-vis-item{
  display:inline-block;
  text-align: center;
}
#result-vis-nav-box .result-vis-nav-icon{
  float: right;
}
#result-vis-nav-box .result-vis-box-name{
  /*height:24px;
  width:200px;*/  
}
#interest-attributes-result-vis{
  display: none;
}

</style>