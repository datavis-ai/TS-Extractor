<template>
　　<div id="overView-global-graph"> 
  　　<div id="overView-container">
        <!-- <div id="lasso-tool-box">
          <button id='lasso-tool-enable'>lasso</button>
          <button id='lasso-tool-cancel'>cancel</button>
          <button id='lasso-tool-lock'>lock</button>
        </div> -->
       <div id="graph-container"></div>
                  
    </div> 
    
  </div>　　 
</template>
<script>
   import $ from 'jquery'
   import axios from 'axios' // 用于AJAX请求 
   import {vueFlaskRouterConfig} from '../vueFlaskRouterConfig'
   import bus from '../eventbus.js' // 事件总线.  
　　 
   export default {
　　　　　　data(){
　　　　　　　　return {
        　　lasso: null, //套索对象.         
          sigmaObj: null, //sigma对象.
          graph: null,         
          previousSeletedNodes: [],
          currentSelectedNodes: [],
          nodeColor: "grey", //橙色.
          nodeSize: 1, //节点大小.
          edgeColor: "grey",
          changeNodeColor: true,
          changeEdgeColor: true,
          // 套索选中的节点列表.
          selectedNodesInLasso: [], //选中的节点. [{x:x, y:x, id:x}, ...]
          clickSubgraphFlag: true, // 点击subgraph标志位.
         
　　　　　　　　}
　　　　　　},
      props:[
        'globallayoutdata' //属性名称.
      ],
      watch:{

      },
　　　　　　methods:{
       setCanvasSize(selector, width, height){ // 设置画布的大小.
         
         $(selector).width(width); // 画布宽度设置
         $(selector).height(height); // 画布高度设置
       },
       deleteEventInDiv(){
        // $("#view-graph > *").remove();
       },
       deleteGraphInSvg(svgId){
         $("#" + svgId + " > *").remove(); // 清除svg中旧的内容,包括各种事件.
       },
       enableLasso(elId){ //使能套索.
          let this_ = this;
          $("#" + elId).click(function (){
            this_.lasso.activate();
            this_.sigmaObj.refresh({skipIndexation: true}); // {skipIndexation: true}
            console.log("click lasso");
          });
          
        },
        renderHalo(activeState) { // 被选中的节点,用光晕高亮.
          let this_ = this;
          this_.sigmaObj.renderers[0].halo({
            nodes: activeState.nodes()
          });
        }
　　　　　　},
      created(){
        let this_ = this;
      },
      mounted(){
        let this_ = this;
        let selector = "#graph-container";
        let width =  this_.$store.state.globalGraphView.width; //画布的宽度.
        let height = this_.$store.state.globalGraphView.height; // 画布的高度
        this_.setCanvasSize(selector, width, height);
        this_.deleteEventInDiv();        
        // $.getJSON("../../static/json/connected_max_subgraph_citation_network_visualization.json", function(data){
        this_.graph = this_.globallayoutdata;
        // console.log("globallayoutdata");
        // console.log(this_.graph);
        //修改节点的颜色.
        if(this_.changeNodeColor){
            this_.graph.nodes.forEach(function (item, index){
              item.color = this_.nodeColor;
              item.size = this_.nodeSize;
            });
        }
        if(this_.changeEdgeColor){
            this_.graph.edges.forEach(function (item, index){
              item.color = this_.edgeColor;
            });
        }

        sigma.renderers.def = sigma.renderers.canvas; //设置成canvas为默认.

        this_.sigmaObj = new sigma({
          graph: this_.graph,
          renderer: {
            container: document.getElementById('graph-container'),
            type: 'canvas' // webgl不支持套索.
          },
          settings: { // 更多设置在src/sigma.settings.js.
            enableEdgeHovering: false,
            enableHovering: false,
            drawLabels: false,
            singleHover:true,
            borderSize: 2, //2
            outerBorderSize: 3,//3
            defaultNodeBorderColor: '#fff',
            defaultNodeOuterBorderColor: 'rgb(236, 81, 72)',
            // doubleClickZoomingRatio: 0,
            // zoomingRatio: 0,

            // 光晕参数设置.
            nodeHaloColor: '#fff',//'rgba(236, 81, 72, 0.2)',
            nodeHaloSize: 0, //节点被选中后,光圈的大小.
            nodeHaloStroke: false,
            nodeHaloStrokeColor: '#000',
            nodeHaloStrokeWidth: 0.5,
            nodeHaloClustering: false,
            nodeHaloClusteringMaxRadius: 1000,
            edgeHaloColor: '#fff',
            edgeHaloSize: 10,
            drawHalo: true,

            minNodeSize: 1,
            maxNodeSize: 2,
            minEdgeSize: 0.5,
            maxEdgeSize: 0.5,
          }
        });       

          
        let activeState = sigma.plugins.activeState(this_.sigmaObj); // 激活sigma实例.
        let keyboard = sigma.plugins.keyboard(this_.sigmaObj, this_.sigmaObj.renderers[0]); //键盘实例.

        

        
        let select = sigma.plugins.select(this_.sigmaObj, activeState); //实例化选择插件.
        select.bindKeyboard(keyboard); //将选择绑定到键盘上.
        
        // 备注:注释掉之后不能拖拽节点.
        // let dragListener = sigma.plugins.dragNodes(this_.sigmaObj, this_.sigmaObj.renderers[0], activeState); //初始化拖拽插件.

       
        this_.lasso = new sigma.plugins.lasso(this_.sigmaObj, this_.sigmaObj.renderers[0], { //初始化所套插件. s.renderers[0] canvas实例.
          'strokeStyle': 'rgb(236, 81, 72)',
          'lineWidth': 2,
          'fillWhileDrawing': true,
          'fillStyle': 'rgba(236, 81, 72, 0.2)',
          'cursor': 'crosshair' //准十字线.
        });

        select.bindLasso(this_.lasso); //select插件绑定lasso功能.             

       
        

        this_.sigmaObj.renderers[0].bind('render', function(e) {
          this_.renderHalo(activeState); // 被选中的节点,用光环高亮.
        });
        
        keyboard.bind('32+83', function() { // 套索快捷键设置.
          if (this_.lasso.isActive) { //如果处于激活状态.
            this_.lasso.deactivate(); //则关闭.
          } 
          else { //否则,激活.
            this_.lasso.activate();
          }
        });

    
        this_.lasso.bind('selectedNodes', function (event) { //监听套索选中的节点.
          // console.log("selectedNodes");
          // console.log(event);
          let selectedNodes = event.data; //获得被选中的节点.
          this_.previousSeletedNodes = this_.currentSelectedNodes;
          this_.currentSelectedNodes = event;
          let idCurrentSelectedNodes = []; //id列表.
          for(let i=0; i<this_.currentSelectedNodes.data.length; i++){
             let obj = this_.currentSelectedNodes.data[i];
             idCurrentSelectedNodes.push(obj.id);
          }
          if(this_.previousSeletedNodes.data){ //非空则进入.

              this_.previousSeletedNodes.data.forEach(function(item, index){
                if(idCurrentSelectedNodes.indexOf(item.id) == -1){ //不在里面.
                  item.color = this_.nodeColor; //恢复颜色.
                  item.active = false; //没有光环.
                }

              });
              this_.sigmaObj.refresh({skipIndexation: true}); // {skipIndexation: true}

          }


          setTimeout(function() {
              // this_.lasso.deactivate(); //异步关闭套.         
              this_.sigmaObj.refresh({skipIndexation: true}); //被选中节点高亮. { skipIndexation: true }
          }, 0);
          // console.log("selectedNodes");
          // console.log(selectedNodes);
          this_.selectedNodesInLasso = selectedNodes; //

          // console.log("previousSeletedNodes");
          // console.log(previousSeletedNodes);

          // console.log("currentSelectedNodes");
          // console.log(currentSelectedNodes);
        });
        // });
        // this_.enableLasso("lasso"); //套索图标使能.
        $("#lasso-icon-box").unbind(); //先解绑#lasso-icon-box上的事件,保证只注册一个事件.
        $("#lasso-icon-box").click(function (e){ //使能套索.#lasso-icon-box元素在globalGraphView.vue中定义.           
            
            if(this_.clickSubgraphFlag){
              // console.log("sendSplitPanesFlag true");
              // bus.$emit("sendSplitPanesFlag", true); // 弹开窗口.
              // this_.deleteGraphInSvg(this_.$store.state.globalFilteredSubgraphView.svgId); //点击套索图标,删除svg中的图及其绑定的事件.
              this_.$store.state.globalFilteredSubgraphView.isOpenFilteredSubgraph = false; //点击禁止对子图进行焦点删除操作.
              this_.clickSubgraphFlag = false;
              // this_.selectedNodesInLasso = []; // 由于graph的套索选中区域不会在点击套索图标时候自动清除,所以不清除选中节点列表,保持列表和看到的现象一致.
              let cssLasso = {
                "background":"#409EFF",
                "color":"#fff"
              };
              $("#lasso-icon-box").css(cssLasso); //用黑圈圈起来.

              let cssSubGraph = {
                "background":"#ddd",
                "color":"#000"
              };
              $("#check-filter-subgraph").css(cssSubGraph); //用黑圈圈起来.

              this_.lasso.activate(); // 激活套索.
              this_.sigmaObj.refresh({skipIndexation: true}); // {skipIndexation: true}
              
            }

        });
        
        $("#check-filter-subgraph").unbind(); //先解绑#lasso-icon-box上的事件,保证只注册一个事件.
        $("#check-filter-subgraph").click(function (e){ // #check-filter-subgraph元素在globalGraphView.vue中定义.
            // bus.$emit("sendSplitPanesFlag", true); // 弹开窗口.
            if(this_.clickSubgraphFlag === false){ //如果不为真.
                this_.$store.state.globalFilteredSubgraphView.isOpenFilteredSubgraph = true; //点击打开子图.
                // bus.$emit("sendSplitPanesFlag", true); // 弹开窗口.
                this_.clickSubgraphFlag = true;

                 let cssLasso = {
                   "background":"#ddd",
                   "color":"#000"
                };
                $("#lasso-icon-box").css(cssLasso); //

                let cssSubGraph = {
                  "background":"#409EFF",
                  "color":"#fff"
                };
                $("#check-filter-subgraph").css(cssSubGraph); //

                this_.lasso.deactivate(); //关闭套索. 
                bus.$emit("sendSelectedNodesInLasso", this_.selectedNodesInLasso); // 发送选中的节点数据到globalFilteredSubgraphView.vue组件中.
               
                // todo:下面对过滤出来的子图进行可视化展示.
                // console.log("this_.selectedNodesInLasso");console.log(this_.selectedNodesInLasso);
            }
            
          });

      },
      destroyed(){
        
      }
　　　　　　
    }
</script>
<style>
    
  /*kbd {
    background-color: #e7e7e7;
    background-image: -webkit-linear-gradient(#fefefe, #e7e7e7);
    background-image: linear-gradient(#fefefe, #e7e7e7);
    background-repeat: repeat-x;
    display: inline-block;
    padding: 3px 5px;
    font: 11px Consolas, "Liberation Mono", Menlo, Courier, monospace;
    line-height: 10px;
    color: #000;
    border: 1px solid #cfcfcf;
    border-radius: 2px;
  }

  .key.arrow {
     font-size: 15px;
     font-weight: bold
  }*/

  /*.over-view-nav {
    position: absolute;
    bottom: 0;
    right: 0;
    line-height: 30px;
    border: 1px solid #ccc;
    padding: 10px 20px;
    background: white;
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 13px;
  }
  .left {
    display: inline-block;
    width: 100px
  }*/
  
  #graph-container{    
    position: relative; /*没有这个设置时,canvas不随滚轴滚动.*/
    /*width:200px;
    height:200px;*/
  }
  #overView-container{
    position: relative;
  }
  /*#lasso-tool-box{
   width:40px;
   height:40px;   
   top: 0;
   right: 0;
 }*/
  </style>