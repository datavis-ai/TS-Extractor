<template> 
  <div id="foucus-set">
    <el-collapse v-model="activeNames">
      <el-collapse-item title="Focus Set" name="Focus Set"> 
          <!-- <span class="focus-num-span" v-if="numTag == 1"><strong>{{numTag}} Focus</strong></span>
          <span class="focus-num-span" v-if="numTag > 1"><strong>{{numTag}} Focuses</strong></span> -->
          <!-- <span class="focus-num-span" v-if="numTag == 1">{{numTag}} Focus</span>
          <span class="focus-num-span" v-if="numTag > 1">{{numTag}} Focuses</span> -->
          <div v-if="numTag > 0" id="focusesbox">    
            <el-tag
            v-for="(tag,index) in dynamicTagsFocus"
            :key="tag.id"
            :class= "tag.id"       
            closable
            :disable-transitions="false"
            @close="handleClose(tag)">
                <span :id="index" class="tag-focus" v-if="tag.tag.length > 30">{{tag.tag.slice(0,31)+"..."}}</span>
                <span :id="index" class="tag-focus" v-else>{{tag.tag}}</span>         
            </el-tag>
          </div>
          <div id="doibuttonbox" v-if="dynamicTagsFocus.length > 0">
            <el-button size="small" type="primary" @click="getSubgraph">Start</el-button>
          </div>
          <div class="tagInfoContent"></div>  <!--悬浮标签,弹出的信息框--> 
      </el-collapse-item>
    </el-collapse> 
   
  </div>
</template>

<script>
import $ from 'jquery'
import axios from 'axios' // 用于AJAX请求
// import qs from 'qs' 
import {vueFlaskRouterConfig} from '../vueFlaskRouterConfig'
import bus from '../eventbus.js' // 事件总线.
  export default {
    data() {
      return {
        /*         
        dynamicTagsFocus=[{
          attributesValue:{institution: "xxx", interests: "xxx"},
          attriselect:["institution", "interests"],
          dbname: "Coauthor_Visualization.db",
          field: "institution",
          id: "1620830",
          keyword: "University of Utah",
          tag: "Fangxiang Jiao"
        }, ...]
        在bus.$on('sendSlectedNode')中添加标签.
        注意:dynamicTagsFocus在created()中,将dynamicTagsFocus的指针赋予了this_.$store.state.focusSetView.dynamicTagsFocus,所以this_.$store.state.focusSetView.dynamicTagsFocus改变,则改组件中的dynamicTagsFocus也会发生改变.但是这样使用具有风险,一旦什么时候不小心错误赋值则无法使用了.
        */
        dynamicTagsFocus: [], // [{}, ...]用于保存选中的焦点集,注意在本组件中其指针没有发生改变,所以let mao=dynamicTagsFocus,mao是其引用.js中的对象和数组的赋值都是引用.
        nodenum: null, // 保存节点数量.
        focusSet:[], // 焦点的id集合,用于装id,注意id是String类型的,例如[xxx, xxx, ...]
        tagName: "",
        xOffset: 10,  // 悬浮历史图片弹出的信息框的位置.
        yOffset: 45       
        
      };
    },
    computed:{
      numTag: function(){ // 标签数量.
         let num = this.dynamicTagsFocus.length; // 标签数量.
         return num;
      },
      activeNames:{ // activeNames是v-model绑定的双向变量,则变量需要有getter + setter,这样才能既读又写.
          // getter
          get: function(){
            if(this.dynamicTagsFocus.length > 0){ // 
                let temp = [];
                temp.push("Focus Set");
                return temp;
            }
            else{
              let temp = [];
              return temp;
            }           
         },
         // setter
         set: function(){
          
         }
       }
    },
    watch:{  // 侦听data里面属性,跟v-model绑定没有关系,只要是data里面属性就可以了.
      dynamicTagsFocus: function(curVal, oldVal){                
         console.log("curVal");
         console.log(curVal);
         bus.$emit("sendFocusNodeNumber", curVal.length); // 将节点的数量发送到mainView.vue中.
      }
    },
    updated(){ // 利用了updated()钩子函数.
      let this_ = this; 
      if(this_.dynamicTagsFocus.length > 0){
        $(".tag-focus").unbind();  // 注意:首先对元素中原来绑定的事件进行解绑,这样就避免了信息重复输出.
        $(".tag-focus").mouseover(function(e){ // 焦点标签鼠标悬浮事件.
              // console.log("tag-focus e");console.log(e);
              let tagId = parseInt(e.currentTarget.id); // 标签的id转化成int型就是索引.              
              let nodeId = e.currentTarget.parentElement.classList[1]; //获得焦点的id.
              $("#focusesbox ." + nodeId).css("border", "1px solid #2894FF"); //标签本身高亮.             
              
              let attributesExplorNodeHighlight = this_.$store.state.mainViewGraph.attributesExplorNodeHighlight;
              if(attributesExplorNodeHighlight.length > 0){ // 如果已经开始属性探索.
                 attributesExplorNodeHighlight.forEach(function(item, index){
                        
                   let css = {
                      "stroke-dasharray":0,
                      "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.clickMatchNodeAttri,
                      "stroke-width": 3
                    };
                    $("#mainsvg #" + item).css(css); // 点击节点,用黑色圆圈圈起来.
                });
              }
              let css = {
                  "stroke-dasharray":0,
                  "stroke": "black", // #1890ff
                  "stroke-width": 3
              };
              $("#mainsvg #" + this_.dynamicTagsFocus[tagId].id).css(css); //mainView视图中节点黑圈高亮.              
              $("#" + this_.$store.state.resultsSearchView.svgId + " ." + this_.dynamicTagsFocus[tagId].id).css(css); //results vis中节点用黑圈高亮.
              $("#" + this_.$store.state.globalFilteredSubgraphView.svgId + " ." + this_.dynamicTagsFocus[tagId].id).css(css); //filtered subgraph View中节点高亮.             

               //获取鼠标位置函数
              let mousePos = this_.mousePosition(e);
              let  xOffset = this_.xOffset;
              let  yOffset = this_.yOffset;
              $(".tagInfoContent").css("display","block").css("position","absolute")
              .css("top",(mousePos.y - yOffset) + "px")
              .css("left",(mousePos.x + xOffset) + "px");

              // TODO: 以后添加更加具体的信息.
              let stringHtml="<div class='here-focus-info-box'><p><strong>id</strong>: %s<br><strong>name</strong>: %s<br><strong>graph data</strong>: %s<br><strong>selected atrribute</strong>: %s<br><strong>keywords</strong>: %s<br><strong>attributes of interest</strong>: %s</p></div>";
              let attriselect = null;  
              if(this_.dynamicTagsFocus[tagId].attriselect.length > 0){
                 attriselect = this_.dynamicTagsFocus[tagId].attriselect;
              }
              else{
                attriselect = "NULL";
              }
                                             
              let html = this_.sprintf(stringHtml, this_.dynamicTagsFocus[tagId].id, this_.dynamicTagsFocus[tagId].tag, this_.dynamicTagsFocus[tagId].dbname, this_.dynamicTagsFocus[tagId].field,  this_.dynamicTagsFocus[tagId].keyword, attriselect);
              $(".tagInfoContent").append(html);
              
                  
           });
         //鼠标离开,隐藏悬浮框.
         $(".tag-focus").mouseout(function(e){
             // console.log("tag-focus e mouseout");console.log(e);
             let nodeId = e.currentTarget.parentElement.classList[1]; //获得焦点的id.
             //取消result vis节点高亮
             let restoreCss = {
                "stroke-dasharray":0,
                "stroke": "#fff",
                "stroke-width": 0
              };
             $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css(restoreCss); //清除之前的高亮.
             $("#" + this_.$store.state.globalFilteredSubgraphView.svgId + " ." + nodeId).css(restoreCss); //filtered subgraph View中节点高亮.

             $("#focusesbox ." + nodeId).css("border", "1px solid rgba(64,158,255,.2)"); //恢复原貌.
             $(".tagInfoContent").empty();
             $(".tagInfoContent").css("display","none");
             let css_ = {
                          "stroke-dasharray":0,
                          "stroke": "#fff",
                          "stroke-width": 0
             };
            $("#mainsvg .nodecircle").css(css_);  // fixme: 先恢复原来的样式,然后再高亮点击节点.
            let attributesExplorNodeHighlight = this_.$store.state.mainViewGraph.attributesExplorNodeHighlight;
              if(attributesExplorNodeHighlight.length > 0){ // 如果已经开始属性探索.
                 attributesExplorNodeHighlight.forEach(function(item, index){
                        
                   let css = {
                      "stroke-dasharray":0,
                      "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.clickMatchNodeAttri,
                      "stroke-width": 3
                    };
                    $("#mainsvg #" + item).css(css);
                });
              }            
         });
      }            
         
    },
    created(){
      let this_ = this;       
      this_.$store.state.focusSetView.dynamicTagsFocus = this_.dynamicTagsFocus;  // 先将dynamicTagsFocus的地址保存在store.js中. 注意:以后别再用指针了很难维护.
      bus.$on('sendSlectedNode', function(data){ //用于监听新添加的焦点,要避免焦点重复添加.        
          let id = data.id; // id,用于唯一标识.
          let isexistence = false; // 是否存在. 确保不重复添加.
          for(let i=0; i<this_.dynamicTagsFocus.length; i++){
             if(this_.dynamicTagsFocus[i].id == id){
                isexistence = true; // 如果true,则存在.
                break;
             }
          }
          if(isexistence === false){ // 如果不一样,则添加到数组中. 
            this_.dynamicTagsFocus.push(data); // 添加标签. 添加到数组中.                    
          }
          /*
            data={
              id: "1620830", // 焦点的id.
              tag: "Fangxiang Jiao" // 标签的名字.
              attriselect:["institution", "interests"], //焦点需要考虑的属性(可选择)
              attributesValue:{institution: "xxx", interests: "xxx"}, //焦点需要考虑的属性的值.               
              dbname: "Coauthor_Visualization.db",
              field: "institution", // 条件查询对应的字段.                
              keyword: "University of Utah", // 条件查询对应的字段的值.                
            }
          */
          
      });
      bus.$on("nodeNum", function(data){ // 实时监听,实时更新nodenum
          this_.nodenum = data; // data int型 更新节点数量.
          //console.log("this_.nodenumjinjing");console.log(data);

      });
      bus.$on("focusSetClear", function(data){
        let labelsClear = data; // 数据库变化标志量.
        if(labelsClear){
          this_.dynamicTagsFocus.splice(0, this_.dynamicTagsFocus.length); // 标签(焦点集合清零)清空.
        }
      });
      bus.$on("sendDynamicTagsFocus", function(data){
        
        this_.dynamicTagsFocus.splice(0,this_.dynamicTagsFocus.length);  // 先清除里面的数据. 
        for(let i=0; i<data.length; i++){
            this_.dynamicTagsFocus.push(data[i]);           
        }       
        
      });

      // bus.$on("sendSelectedFocus", function(data){
      //     this_.dynamicTagsFocus.push(data);  // 添加到当前焦点集中.          
      // });

      bus.$on("sendDeleteFocusInResultVis", function(data){
          //data = [nodeId, param, this_.isOpenResultVis]
         let nodeId = data[0];
         let param = data[1]; //哪一个, result_table / result_vis
         let isOpenResultVis = data[2]; //是否打开了result vis.
         for(let i=0; i<this_.dynamicTagsFocus.length; i++){
           let tag = this_.dynamicTagsFocus[i]; //{id:x, tag:x, ...}
           if(tag.id == nodeId){ //找到该焦点并删除.
             this_.dynamicTagsFocus.splice(i, 1);
             break; //跳出大循环,避免继续循环.
           }
         }
         if(isOpenResultVis){ //点开了result vis弹窗.
           $("#" + param.svgId + " ." + nodeId).css("fill", param.nodeColor); //删除焦点后,取消布局图被选节点的高亮,恢复.
         }         
         $("#search-result-table ." + nodeId + " td:first-child").css("background-color", ""); //删除焦点后,取消表格高亮.恢复.  #fff 
         // $("#search-result-table ." + nodeId + " td:first-child").css("background-color", "auto"); //删除焦点后,取消表格高亮.恢复.       
        
      });
      bus.$on("sendDeleteFocusInRankingList", function(data){
        //data = [nodeId, param, this_.isOpenResultVis]
         let nodeId = data;
         // let param = data[1]; //哪一个, result_table / result_vis
         // let isOpenResultVis = data[2]; //是否打开了result vis.
         for(let i=0; i<this_.dynamicTagsFocus.length; i++){
           let tag = this_.dynamicTagsFocus[i]; //{id:x, tag:x, ...}
           if(tag.id == nodeId){ //找到该焦点并删除.
             this_.dynamicTagsFocus.splice(i, 1);
             break; //跳出大循环,避免继续循环.
           }
         }                  
         $("#ranking-by-node-measures ." + nodeId + " td:first-child").css("background-color", ""); //删除焦点后,取消表格高亮.恢复. 
          
      });
      bus.$on("sendDeleteFocusInFilteredSubgraph", function (data){
         // data = [nodeId, param, this_.isOpenFilteredSubgraph]
         let nodeId = data[0];
         let param = data[1]; //哪一个, result_table / result_vis
         let isOpenFilteredSubgraph = data[2]; //是否打开了result vis.
         for(let i=0; i<this_.dynamicTagsFocus.length; i++){
           let tag = this_.dynamicTagsFocus[i]; //{id:x, tag:x, ...}
           if(tag.id == nodeId){ //找到该焦点并删除.
             this_.dynamicTagsFocus.splice(i, 1);
             break; //跳出大循环,避免继续循环.
           }
         }
         
         if(isOpenFilteredSubgraph){ //点开了filtered graph按钮,对过滤子图进行布局.
           console.log("cancel highlight");
           $("#" + param.svgId + " ." + nodeId).css("fill", param.nodeColor); //删除焦点后,取消高亮,恢复.
           console.log(param.svgId);
           console.log(param.nodeColor);
           
         }

      });  
    },
    methods:{
      highLightNodeInSvg(svgId){ //高亮指定SVG中的对应节点.
        
      },
      restoreNodeStyleInSvg(svgId){ //取消SVG中的对应节点的高亮.与highLightNodeInSvg配套使用.

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
      sprintf(){  // 用于字符串格式输出.
        let args = arguments,
        string = args[0],
        i = 1;
        return string.replace(/%((%)|s|d)/g, function (m) {
            // m is the matched format, e.g. %s, %d
            let val = null;
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
      getSubgraph(){
        let this_ = this;          
        console.log("向后台请求graph数据!"); 

        // TODO:焦点集,用于扩展多焦点. e.g. [1234, 4532, 5556]
        //this_.focusSet = []; // 清空,保证和dynamicTagsFocus是同步的,内容一样. 在 bus.$emit("sendGraphData")中用到.最后是在d3的布局中用颜色高亮焦点.
        this_.focusSet.splice(0,this_.focusSet.length); // 清空,保证和dynamicTagsFocus是同步的,内容一样. 在 bus.$emit("sendGraphData")中用到.最后是在d3的布局中用颜色高亮焦点.
        let idNameObj = {}; // 焦点对象, {焦点1的id: 焦点1的名称, 焦点2的id: 焦点2的名称}
        for(let i=0; i<this_.dynamicTagsFocus.length; i++){
          let id = this_.dynamicTagsFocus[i].id;
          // console.log("typeof(id)");console.log(typeof(id)); // string
          idNameObj[id] = this_.dynamicTagsFocus[i].tag;  // {id: tag, ...}
          this_.focusSet.push(String(id)); // 装入焦点集中.要考虑id的类型. 必须转换成String型,否则将出现跨域问题.
         }
        this_.$store.state.focusSetView.idNameObj = idNameObj;  // 保存到store.js中.
        // 判断是否删除搜索结果
        if(this_.dynamicTagsFocus.length > 0){ // 如果有多个焦点,则在点击Extract时,删除搜索出来的表格.
          bus.$emit("sendDeleteSearchTableFlag", true);
        }
        let setInterests = {"setNodes": this_.dynamicTagsFocus, "setKeyword":{}}; // TODO: 一个兴趣集,里面包含 节点集 + 关键词集,关键词集是以后的扩展. 注意:"setKeyword"应该是这种格式{field1:[],...},作为以后的扩展.
        this_.$store.state.focusSetView.setInterests = setInterests;  // 保存到store.js中. this_.$store.state.focusSetView.idNameObj = idNameObj;  // 保存到store.js中.
         
        let diffFactor = this_.$store.state.widgetView.diffFactor;
        let UI_factor = this_.$store.state.widgetView.UIFactor;
        let API_factor = this_.$store.state.widgetView.APIFactor;
        let isEdgeAttri = this_.$store.state.widgetView.isEdgeAttri;
        let probRestart = this_.$store.state.widgetView.probRestart;
        let weightAttrNode = this_.$store.state.widgetView.weightAttrNode;
        let param = {"setInterests": setInterests, 
                     "scaleOfSingleFocus": this_.nodenum,
                     "diffFactor": diffFactor,
                     "UI_factor": UI_factor,
                     "API_factor": API_factor,
                     "isEdgeAttri": isEdgeAttri,
                     "probRestart": probRestart,
                     "weightAttrNode": weightAttrNode,
                     "isClickHist": false,
                     "interestSubgraphNodeList": []}; // 添加"isClickHist",用于让后台判断该请求是否是由点击历史缩略图而发送的.
        
        bus.$emit("sendMainViewLoadingFlag", true); // 发送加载信号.    
        
        axios.post(vueFlaskRouterConfig.mainViewGraph, { // 将焦点集发送到后台,计算DOI图.
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
                let useSearchFlag = true; 
                // TODO: 现在只用第一个节点作为焦点来做实验.
                let tempExplandNewNodeList = [];
                this_.$store.state.mainViewGraph.isExplandNodeFlag = false; // 先失能该标志量,避免恢复布局后使用旧的扩展列表,出现新边的颜色.
                bus.$emit("sendGraphData", [graph, this_.focusSet, useSearchFlag, directed, tempExplandNewNodeList]); // 在mainView.vue中监听, 定义一个事件sendGraphData,用于分发graph+focus,注意:graph+focu得同时传过去,如果分开传会出现问题. 
                bus.$emit("sendClearExplandNewNodeListFlag", true); // 在mianView.vue中接收,用于清除
                this_.doiGraphInfo(data); // 发送DOI子图信息.      


          })
          .catch((error) => {            
            console.error(error);
          });

      },
      handleClose(tag) { //fixme:点击删除焦点.
        let this_ = this;
        let nodeId = tag.id;
        // 删除数组中指定的元素.
        this_.dynamicTagsFocus.splice(this_.dynamicTagsFocus.indexOf(tag), 1); // array.splice(index,howmany,item1,.....,itemX),splice() 方法用于插入,删除或替换数组的元素.
        this_.$store.state.resultsSearchView.focusStateList.splice(this_.$store.state.resultsSearchView.focusStateList.indexOf(nodeId), 1); //删除nodeId.
        
        // 删除焦点,results vis + 搜索结果列表中对应的节点和列表的高亮被取消,恢复原状.
        $("#search-result-table ." + nodeId + " td:first-child").css("background-color", "");
        // $("#search-result-table ." + nodeId + " td:first-child").css("background-color", "auto"); //删除焦点后,取消表格高亮.恢复.  #fff  
        $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css("fill", this_.$store.state.resultsSearchView.layoutSettings.nodeColor); //删除焦点后,取消高亮,恢复.   

        // 删除焦点,filtered subgraph子图布局图中高亮的节点恢复原状.
        $("#" + this_.$store.state.globalFilteredSubgraphView.svgId + " ." + nodeId).css("fill", this_.$store.state.globalFilteredSubgraphView.layoutSettings.nodeColor);
        
        this_.$store.state.nodeRankTable.focusStateList.splice(this_.$store.state.nodeRankTable.focusStateList.indexOf(nodeId), 1); //删除nodeId.
        $("#ranking-by-node-measures ." + nodeId + " td:first-child").css("background-color", "");

      },     
    },
    mounted(){
      let this_ = this;
      
    },    
    beforeDestroy () {
       bus.$off("nodeNum"); // DOI子图节点数量控制.
       bus.$off('sendSlectedNode');  // 由于bus.on()不会自己注销,需要bus.$off()来注销,这样可以解决多次触发的问题.    
       bus.$off("focusSetClear");   // 焦点集清空.    
       bus.$off("sendDynamicTagsFocus");
       // bus.$off("sendSelectedFocus");
       bus.$off("sendDeleteFocusInResultVis"); //在results vis中删除焦点.
       bus.$off("sendDeleteFocusInFilteredSubgraph"); //在filtered subgraph中删除焦点.
       bus.$off("sendDeleteFocusInRankingList"); // 删除Ranking List中的焦点.
    },       
  }
</script>
<style>
  .tagInfoContent{
      display:none; /*这样可以避免刚打开页面时出现一个信息框*/    
      max-width:300px;
      /*max-height:100px;*/
      border-radius:2px;
      padding:2px 5px 2px 5px;
      position:absolute;
      /*top:15px;*/
      /*bottom:300px;
      left:80px;*/
      font-size:5px;
      background-color:#fff;
      z-index: 100;
      border-style: solid;
      border-color:#ddd;
      border-top-width: 1px;
      border-right-width: 1px;
      border-bottom-width: 1px;
      border-left-width: 1px;
  }
  .here-focus-info-box{
    padding: 0px 0px 0px 5px;
  }
  .el-tag + .el-tag {
    margin-left: 10px;
  }
  .button-new-tag {
    margin-left: 10px;
    height: 32px;
    line-height: 30px;
    padding-top: 0;
    padding-bottom: 0;
  }
  .input-new-tag {
    width: 90px;
    margin-left: 10px;
    vertical-align: bottom;
  }
  /*.el-tag{
    max-width:300px;
  }
  .el-tag span{
        overflow: hidden; 
        text-overflow: ellipsis; 
        -o-text-overflow: ellipsis;
        white-space:nowrap;
        max-width:240px;
         
        display:inline;
  }*/
  /*#focusesbox .el-tag:hover{   
    border-width:1px;
    border-color:#2894FF;
    cursor:pointer;
  }*/
  #focusesbox{
      margin:2px 4px 0px 4px;
      padding:4px 4px 4px 4px;
      max-height:100px;
      border-style: solid;
      border-color:#ddd;
      border-top-width: 1px;
      border-right-width: 1px;
      border-bottom-width: 1px;
      border-left-width: 1px;
      border-top-left-radius:2px;
      border-top-right-radius:2px; 
      border-bottom-left-radius:2px;
      border-bottom-right-radius:2px;
      overflow-y: auto;
      overflow-x: auto;
  }
  #doibuttonbox{
      float:right;
      margin:0px 4px 0px 0px;
      padding:2px 0px 2px 0px;
      border-style: solid;
      border-color:#E0E0E0;
      border-top-width: 0px;
      border-right-width: 0px;
      border-bottom-width: 0px;
      border-left-width: 0px;
  }
#foucus-set .el-collapse-item__header{
  /*background-color: #f5f5f5;*/
  color: #333;  
  border-color:#ddd;
  border-style: solid;
  border-top-width: 1px;
  border-right-width: 1px;
  border-bottom-width: 1px;
  border-left-width: 1px;
  border-top-left-radius:0px;
  border-top-right-radius:0px; 
  border-bottom-left-radius:0px;
  border-bottom-right-radius:0px;
  margin:0px 0px 0px 0px;
}

#foucus-set .el-collapse-item__wrap{

  /*background-color: #f5f5f5;*/
  color: #333;  
  border-color:#ddd;
  border-style: solid;
  border-top-width: 0px;
  border-right-width: 1px;
  border-bottom-width: 1px;
  border-left-width: 1px;
  border-top-left-radius:0px;
  border-top-right-radius:0px; 
  border-bottom-left-radius:0px;
  border-bottom-right-radius:0px;
  /*margin:0px 0px 2px 0px;*/
}
.focus-num-span{
  margin:0px 0px 0px 4px;
}
#doibuttonbox .el-button--small{
    padding-top: 7px;
    padding-right: 4px;
    padding-bottom: 7px;
    padding-left: 4px;
}
#doibuttonbox button:hover{   
    border-width:1px;
    border-color:#91d5ff;
    cursor:pointer;
}
</style>