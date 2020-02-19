<template>
	<div id="global-graph-view-box">
		<el-collapse v-model="activeNames">
		  <el-collapse-item title="Heatmap View" name="Global Graph">	        
		    <div id="global-graph-view-nav">
          <div class='global-graph-view-div' id="switch-tab-box">
            <ul class="global-graph-view-tab">
              <!-- <li>
                <div class="heatmap-a" @click='clickHeatMap'>HeatMap</div>        
              </li> -->
              <!-- <li>               
                <div class="global-graph-a" @click='clickGraph'>Node-Link</div>       
              </li> -->
            </ul>
          </div>

          <div class='global-graph-view-div' id="lasso-tool-nav">
            <ul calss="global-graph-view-tool-tab">
              <!-- <li>
                <div id="graph-info-icon-box">
                  <img id="graph-info-icon" width="20" height="20" src="../../static/img/icons-graph-info.png">                 
                </div>
              </li> -->
              <li>
                <div id="lasso-icon-box">
                  <img id="lasso-icon" width="20" height="20" src="../../static/img/icons-lasso.png">                  
                </div>
              </li>
              <li>
                <div id='check-filter-subgraph'>
                  <img id="subgraph-icon" width="20" height="20" src="../../static/img/subgraph.png"> 
                </div>
              </li>
            </ul>
          </div>          

        </div>
        <div id="global-switch-view">
          <div class="globalgraph-div" id="view-graph">
            <!-- <router-view></router-view> -->
            <div v-if="clickSwitchFlag === true">
               <overviewglobalheatmap :globallayoutdata="globalGraphLayoutData"></overviewglobalheatmap>
            </div>
            <div v-if="clickSwitchFlag === false">
              <overviewglobalgraph :globallayoutdata="globalGraphLayoutData"></overviewglobalgraph>
            </div>           

          </div>
         
         <!--对于全局图的信息,可以通过点击图标弹出弹窗进行查看,因为我们系统的重点不是全局图-->
          <!-- <div class="globalgraph-div" id="view-graph-info">
            <globalgraphinfoview></globalgraphinfoview>
          </div> -->
         
        </div>
		  </el-collapse-item>
		</el-collapse>

    <!--对于全局图的信息,可以通过点击图标弹出弹窗进行查看,因为我们系统的重点不是全局图-->
    <div id="view-graph-info-box">
      <div id="view-graph-info">
         <!-- <globalgraphinfoview></globalgraphinfoview> -->
      </div>
    </div>

	</div>	
</template>

<script>
  import overviewglobalheatmap from '@/components/overViewGlobalHeatMap'
  import overviewglobalgraph from '@/components/overViewGlobalGraph'
  import bus from '../eventbus.js' // 事件总线.
  // import globalgraphinfoview from "@/components/globalGraphInfoView.vue"
  import {jBox} from "../../static/js/jBox.js" 

  export default {    
    data: function(){
      return {
         activeNames:["Global Graph"],
         showWho: true, //默认显示热力图.
         clickSwitchFlag: null, //点击切换按钮.
         globalGraphLayoutData: null, // 用于指向布局好的全局图数据.
         jBoxInstance:{
           globalGraphInfo: null, // 用于展示全局图的信息的弹窗. this_.jBoxInstance.globalGraphInfo
         }
      }
    },
    computed:{
       // clickSwitchFlag:{
       //  // getter
       //    get: function(){
       //      if(this.globalGraphLayoutData){ //每次更换数据库globalGraphLayoutData就发生变化.
       //         return true;
       //     }
       //     else{
       //       return null;
       //     }          
       //   },
       //   // setter
       //   set: function(data){
       //      return data;
       //   }       
         
       // }
    },
    components: { // 组件注册后可以作为标签使用.
       overviewglobalheatmap,
       overviewglobalgraph,
       // globalgraphinfoview
    },
    created(){
       let this_ = this;
       bus.$on("sendGlobalGraphLayoutDataFlag", function (data){ //这么做是为了clickSwitchFlag现有个过渡状态,然后再渲染出对应的heatmap.
           if(data){
             this_.clickSwitchFlag = null;
           }
       });
       bus.$on("sendGlobalGraphLayoutData", function (data){ //更换数据库时实时响应.
          if(data){
             
             console.log("get sendGlobalGraphLayoutData");                       
             this_.globalGraphLayoutData = this_.$store.state.globalGraphView.globalGraphLayoutData; //将数据赋给子组件.
             this_.clickSwitchFlag = true; //渲染heatmap.
             let cssHeatMap = {
              "background":"#409EFF",
              "color":"#fff"
             };
             $(".heatmap-a").css(cssHeatMap); //用黑圈圈起来.
             let cssGraph = {
                "background":"#ddd",
                "color":"#000"
             };
             $(".global-graph-a").css(cssGraph);

          }
       });
    },
    methods:{
      iconClickEvent(){ // 图标点击事件.
        $("#subgraph-icon").click(function(e){
           bus.$emit("sendSplitPanesFlag", "open"); // 弹开窗口.
        });
      },
      iconTooltip(){ // 图标提示
        // $('#graph-info-icon-box').jBox('Mouse', { // jBox在本文件中并没有引入,但是也能用(在mainView.vue中引入了).
        //   theme: 'TooltipDark',
        //   content: 'Graph Informations', //'Click to check visualization of result'
        //  });
        $('#subgraph-icon').jBox('Mouse', { // jBox在本文件中并没有引入,但是也能用(在mainView.vue中引入了).
          theme: 'TooltipDark',
          content: 'Region of Interest', //'Click to check visualization of result'
         });
      },
      setCanvasSize(selector, width, height){ // 设置画布的大小.         
         $(selector).width(width); // 画布宽度设置
         $(selector).height(height); // 画布高度设置
      },
      deleteGraphInSvg(svgId){
         $("#" + svgId + " > *").remove(); // 清除svg中旧的内容,包括各种事件.
      },   
      clickHeatMap(e){ //点击heatmap
        let this_ = this;
        this_.deleteGraphInSvg(this_.$store.state.globalFilteredSubgraphView.svgId);
        this_.clickSwitchFlag = true;
        // console.log("clickHeatMap");
        // console.log(e);        
        let cssHeatMap = {
          "background":"#409EFF",
          "color":"#fff"
        };
        $(".heatmap-a").css(cssHeatMap); //用黑圈圈起来.
        
        let cssGraph = {
          "background":"#ddd",
          "color":"#000"
        };
        $(".global-graph-a").css(cssGraph); //用黑圈圈起来.

        let cssLasso = {
            "background":"#ddd",
             "color":"#000"
            };
        $("#lasso-icon-box").css(cssLasso); //用黑圈圈起来.
        
        let cssSubGraph = {
          "background":"#ddd",
          "color":"#000"
        };
        $("#check-filter-subgraph").css(cssSubGraph); //用黑圈圈起来.
        
        bus.$emit("clearGraphEVFlag", true); //发送清除|V| + |E|信号
      },
      clickGraph(e){ // 点击graph
        let this_ = this;
        this_.deleteGraphInSvg(this_.$store.state.globalFilteredSubgraphView.svgId);
        this_.clickSwitchFlag = false;
        // console.log("clickGraph");
        // console.log(e);
        
        let cssHeatMap = {
          "background":"#ddd",
          "color":"#000"
        };
        $(".heatmap-a").css(cssHeatMap); //用黑圈圈起来.
        
        let cssGraph = {
          "background":"#409EFF",
          "color":"#fff"
        };
        $(".global-graph-a").css(cssGraph); //用黑圈圈起来.

        let cssLasso = {
            "background":"#ddd",
             "color":"#000"
            };
        $("#lasso-icon-box").css(cssLasso); //用黑圈圈起来.

        let cssSubGraph = {
          "background":"#ddd",
          "color":"#000"
        };
        $("#check-filter-subgraph").css(cssSubGraph); //用黑圈圈起来.

        bus.$emit("clearGraphEVFlag", true); //发送清除|V| + |E|信号         
      },

    },
    watch:{
      showWho: function(curVal, oldVal){
        console.log("curVal");
        console.log(curVal);
      }
    },
    mounted(){
      let this_ = this;
      this_.iconTooltip(); // 图标提示
      this_.iconClickEvent(); // 图标点击事件.
      let selector = "#view-graph";
      let width = this_.$store.state.globalGraphView.width;
      let height = this_.$store.state.globalGraphView.height;
      // this_.setCanvasSize(selector, width, height);      
      this_.jBoxInstance.globalGraphInfo = new jBox('Modal', {
            id: "jBoxGlobalGraphInfo", // 弹出兴趣属性选择框.
            addClass: "jBoxGlobalGraphInfoClass",  // 添加类型,这个功能很棒啊!
            attach: '#graph-info-icon',
            width: 300,              // Maximal width
            height: 250,             // Maximal height 
            title: 'Graph Informations',
            // fixed:true,
            overlay: false,
            fixed: false,
            adjustTracker: true,
            zIndex: 1005, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
            createOnInit: true,
            content: $("#view-graph-info-box"),  // jQuery('#jBox-content') 
            draggable: true,
            repositionOnOpen: false,
            repositionOnContent: true,
            target: $('#graph-info-icon'),//$('#filtered-subgraph-nav-icons-setting'),
            offset: {x: -135, y: 155}, // {x: -135, y: 155},
            // 以下是弹窗事件,这些功能真的非常优秀!
            onOpen: function(){                   
              this_.jBoxInstance.globalGraphInfo.position({
                target: $('#graph-info-icon'),//$('#filtered-subgraph-nav-icons-setting') //注意,这样保证:当 jBoxInstance.resultVis 移动后,重新打开layoutSetting,layoutSetting能够跟着jBoxInstance.resultVis走.           
              });
            },
            onCloseComplete: function(){                     
            }
        });
      
    },
    updated(){
      console.log("globalGraphView updated maotingyun")
    },
    beforeDestroy(){
      bus.$off("sendGlobalGraphLayoutData");
      bus.$off("sendGlobalGraphLayoutDataFlag");      
    }   
  }
</script>

<style>
#switch-tab-box ul { /*.global-graph-view-tab*/
    margin: 0;
    padding: 0;
    overflow: hidden;
    list-style-type: none;
}
#switch-tab-box ul li {
    float: left;
}
#switch-tab-box ul li div {
    text-decoration: none;
    color: #000;
    background: #ddd;
    display: inline-block;
    width: 60px;
    height: 25px;
    text-align: center;
    line-height: 25px;
    cursor: pointer; /*鼠标移到元素上面时变成小手,不可选中字体进行赋值操作*/
    margin: 1px 5px 0px 0px;

    border-top-left-radius:2px;
    border-top-right-radius:2px; 
    border-bottom-left-radius:2px;
    border-bottom-right-radius:2px;
}
#global-graph-view-nav{ /*导航栏样式*/
    
    margin: 2px 0px 4px 0px;
    padding:0px 0px 0px 0px;
    border-style: solid;
    border-color:#ddd;
    border-top-width: 0px;
    border-right-width: 0px;
    border-bottom-width: 0px;
    border-left-width: 0px;
}

/* 以下是套索部分 */

#global-graph-view-nav .global-graph-view-div{ /*切换菜单 + 套索部分*/
  display:inline-grid; /*保证横排*/
}
#lasso-tool-nav{
  margin:0px 0px 0px 20px; /*切换菜单与套索工具间的间距*/
}
#lasso-tool-nav ul{
    margin: 0;
    padding: 0;
    overflow: hidden;
    list-style-type: none;
}
#lasso-tool-nav ul li{
  float:left;
  list-style:none;  
}

#lasso-tool-nav ul li #lasso-icon-box{
    text-decoration: none;
    color: #000;
    background: #ddd;
    display: inline-block;
    width: 25px;
    height: 25px;   
    line-height: 25px;
    cursor: pointer; /*鼠标移到元素上面时变成小手,不可选中字体进行赋值操作*/
    margin: 1px 5px 0px 0px;

     /* 水平居中 */
     text-align:center; 
     /* 垂直居中 */ 
     vertical-align:middle;

     border-top-left-radius:2px;
     border-top-right-radius:2px; 
     border-bottom-left-radius:2px;
     border-bottom-right-radius:2px;

    /*border-style: solid;
    border-color:#ddd;
    border-top-width: 1px;
    border-right-width: 1px;
    border-bottom-width: 1px;
    border-left-width: 1px; */
}
#lasso-icon{
  vertical-align: middle;
}

#lasso-tool-nav ul li #graph-info-icon-box{
    text-decoration: none;
    color: #000;
    background: #ddd;
    display: inline-block;
    width: 25px;
    height: 25px;   
    line-height: 25px;
    cursor: pointer; /*鼠标移到元素上面时变成小手,不可选中字体进行赋值操作*/
    margin: 1px 5px 0px 0px;

    /* 水平居中 */
   text-align:center; 
   /* 垂直居中 */ 
   vertical-align:middle;

   border-top-left-radius:2px;
   border-top-right-radius:2px; 
   border-bottom-left-radius:2px;
   border-bottom-right-radius:2px; 
}
#graph-info-icon{
  vertical-align: middle;
}

#lasso-tool-nav ul li #check-filter-subgraph{
    text-decoration: none;
    color: #000;
    background: #ddd;
    display: inline-block;
    width: 25px;
    height: 25px;   
    line-height: 25px;
    cursor: pointer; /*鼠标移到元素上面时变成小手,不可选中字体进行赋值操作*/
    margin: 1px 5px 0px 0px;
    /* 水平居中 */
   text-align:center; 
   /* 垂直居中 */ 
   vertical-align:middle;

   border-top-left-radius:2px;
   border-top-right-radius:2px; 
   border-bottom-left-radius:2px;
   border-bottom-right-radius:2px;  
}

#subgraph-icon{
  vertical-align: middle;
}

/* 全局图 + 热力图 + 图信息部分 */
#global-switch-view{
  /*width:600px;*/
}


#view-graph{
    /*margin: 2px 0px 2px 0px;*/
    /*padding:0px 0px 0px 0px;*/
    /*width:200px;
    height:200px;*/
    border-style: solid;
    border-color:#ddd;
    border-top-width: 0px;
    border-right-width: 0px;
    border-bottom-width: 0px;
    border-left-width: 0px;
}
#view-graph-info{
  max-width:300px;
  height:250px;
  margin:0px 0px 0px 0px;
  border-style: solid;
  border-color:#ddd;
  border-top-width: 0px;
  border-right-width: 0px;
  border-bottom-width: 0px;
  border-left-width: 0px;
  overflow-y: auto;
  overflow-x: auto;
}
#global-switch-view .globalgraph-div{
  /*width:600px;*/
  /*display: inline;*/
  float:left;
}

#global-graph-view-box .el-collapse-item__header{
  /*background-color: #f5f5f5;*/
  color: #333;  
  border-color:#ddd;
  border-style: solid;
  border-top-width: 1px;
  border-right-width: 1px;
  border-bottom-width: 1px;
  border-left-width: 1px;
  border-top-left-radius:5px;
  border-top-right-radius:5px; 
  border-bottom-left-radius:5px;
  border-bottom-right-radius:5px;
  margin:0px 0px 0px 0px;
  /*height:40px;*/
}

#global-graph-view-box .el-collapse-item__wrap{

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
  border-bottom-left-radius:5px;
  border-bottom-right-radius:5px;
  /*margin:0px 0px 2px 0px;*/
}
#global-graph-view-box #global-graph-view-nav{
  margin-left: 5px;
}
#global-switch-view{
  display: -webkit-flex;
  display: flex;
  -webkit-align-items: center;
  align-items: center;
  -webkit-justify-content: center;
  justify-content: center;
}
#lasso-tool-nav{
  float: right;
}
#global-graph-view-box .el-collapse-item__content {
  padding-bottom: 1px;    
}
#view-graph-info-box{
   display: none;
}
</style>