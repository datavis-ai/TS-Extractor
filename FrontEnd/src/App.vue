<template>
  <div id="app">   
   <!-- App.vue作为页面入口文件 -->
   <div id="system-interface-box">
   <el-row :gutter="1">
      
      <el-row :gutter="1">
       <el-col :span="24">
         <div class="top-info-box">
           <div class="navbar-header-div">
             <a id="system-name">SA-Extractor</a>
           </div>
           <div class="navbar-header-div" id="load-database">
             <loaddb></loaddb>
           </div>
           <div class="navbar-header-div" id="right-side-div">
             <!-- <a class="place-right-side" id="about-us">About Us</a> -->
             <a class="place-right-side" id="help">Help</a>
           </div>
         </div>               
       </el-col>
      </el-row>

      <el-row :gutter="1">
         
          <splitpanes watch-slots @resized="listenResized('resized', $event)" class="default-theme"> <!-- watch-slots 使用resize组件-->
           
            <!--左侧栏,可以resize-->
            <div :splitpanes-size="leftBoxSplitSize" class="left-info-box"> <!--splitpanes-default:默认百分比, 现在都改成splitpanes-size-->
             
              <!-- <globalgraphview></globalgraphview> -->
              <!-- <rankingList></rankingList> -->
              <focusselection></focusselection>
              <!-- <conditionssearch></conditionssearch> -->
              <focussetview></focussetview>              
              <settings></settings>
             
            </div>
          
          
          
            <!--中间栏,可以resize-->
            <div :splitpanes-size="middleBoxSplitSize" class="middle-info-box">
              <splitpanes horizontal> 
                <!-- <div id="global-filtered-graph-box">
                  <globalfilteredsubgraphview></globalfilteredsubgraphview>
                </div> -->
                <div id="search-result-graph-box">               
                  <resultvisview></resultvisview>
                </div>                       
              </splitpanes>
            </div>            
            
            <!--右侧栏,DOI主视图,可以resize-->
            <div :splitpanes-size="rightBoxSplitSize" class="right-info-box">
              <div id="main-view-nav">
                <mainviewnav></mainviewnav>
              </div>           
              <div id="main-view">               
                 <mainview :width_="width" :height_="height"></mainview>
                 <!-- <overviewglobalgraph></overviewglobalgraph>  -->               
              </div>
            </div>           
                  
          </splitpanes>
          <!-- <div> -->
             <!-- <overviewglobalgraph></overviewglobalgraph> -->
             <!-- <overviewglobalheatmap></overviewglobalheatmap>              -->
          <!-- </div> -->
          <!-- <div>
            <publication></publication>
          </div> -->
      </el-row>
     
   </el-row>
   </div>  
  </div>
</template>

<script>
  import Vue from 'vue'
  import fullscreen from 'vue-fullscreen'  
  import $ from 'jquery'
  import bus from './eventbus.js' // 事件总线.
  import mainview from '@/components/mainView'  
  import settings from '@/components/settingsView'
  
  import focussetview from '@/components/focusSetView'
  // import networkinformation from '@/components/networkInformationView'  
  // import focusattributesselection from '@/components/focusAttributesSelection'
  import mainviewnav from '@/components/mainViewNav'  
  import loaddb from '@/components/loadDb'
  import conditionssearch from '@/components/searchConditionView'  
  import globalgraphview from '@/components/globalGraphView'

  // import resultssearch from '@/components/resultsSearchView'
  import resultvisview from '@/components/resultVisView'
  
  import overviewglobalgraph from '@/components/overViewGlobalGraph'
  import globalfilteredsubgraphview from '@/components/globalFilteredSubgraphView'
  import splitpanes from 'splitpanes' // splitter/resizer
  import 'splitpanes/dist/splitpanes.css'
  // import publication from '@/page/publication'
  import rankingList from "@/components/displayTopnNodeView"
  import focusselection from "@/components/focusSelectionView"
  
  import axios from 'axios'
  import qs from 'qs'
  axios.interceptors.request.use(function (config) { // 只在App.vue中设置axios.interceptors.request.use就可以了,这样可避免跨域问题.切记:在flask中要用methods=["POST", "GET"],否则会出错的.
    if (config.method == 'post') {
      config.data = qs.stringify(config.data)
    }
    return config;
  }, function (error) {
    return Promise.reject(error);
  });
  
  Vue.use(fullscreen);

  export default {
    name: 'App',
    data(){
      return {
        width: 1816,  // 主视图的大小  
        height: 890,        
        fullscreen: false,  // 用于全屏扩展.

        //分栏大小初始化配置.
        leftBoxSplitSize: 28, // 左边
        middleBoxSplitSize: 0, // 中间
        rightBoxSplitSize: 72, // 右边

      }
    },
    created(){ 
      let this_ = this;     
      console.log("App.vue created");
      
      bus.$on("sendSplitPanesFlag", function (data){ // 依据条件更改窗口大小.
        if(data == "open"){
          if(this_.leftBoxSplitSize < 3.5 || this_.middleBoxSplitSize < 3.5 || this_.rightBoxSplitSize < 3.5){
            this_.leftBoxSplitSize = 28; // 左边
            this_.middleBoxSplitSize = 72; // 中间
            this_.rightBoxSplitSize = 0; // 右边
          }
          
        }
        if(data == "close"){ // 恢复初始状态.
            this_.leftBoxSplitSize = 28; // 左边
            this_.middleBoxSplitSize = 0; // 中间
            this_.rightBoxSplitSize = 72; // 右边
        }
      });      
    },
    methods: {
      listenResized(eventName, realTimeParamList){
        let this_ = this;
        this_.leftBoxSplitSize = realTimeParamList[0].width; // 左边
        this_.middleBoxSplitSize = realTimeParamList[1].width; // 中间
        this_.rightBoxSplitSize = realTimeParamList[2].width; // 右边    
         
      }
    },

    components:{  // TODO: 注册组件后,就可以在template中像普通HTML元素一样使用,如<mainview></mainview>
      // 注意:注册名为helloWorld的驼峰式命名, 那么在template中的引用可以是:<hello-world>,这是将大写变成小写,而且用"-"分开.
      // 也可以直接:<helloWorld>,这样就没有半点疑惑了,以后采用这种方式,容易识别.      
      mainview, // 图布局          
      settings, // 节点数量控件.
      // resultssearch, // 搜索结果信息表.
      focussetview, // 焦点集视图,用于显示选中的焦点.
      // networkinformation, // 图信息视图.      
      // focusattributesselection,
      splitpanes,
      mainviewnav,      
      loaddb,
      conditionssearch,
      globalgraphview,
      // overviewglobalheatmap,
      overviewglobalgraph,
      resultvisview,
      globalfilteredsubgraphview,
      // publication
      rankingList,
      focusselection
      
    },
    watch:{
      rightBoxSplitSize:function(curVal, oldVal){
        if(curVal > 72 && curVal < 100){ // 右边视图扩大
           this.leftBoxSplitSize = 28;
           this.middleBoxSplitSize = 0; // 中间
           this.rightBoxSplitSize = 72; // 右边
        }
      }
    },
    mounted(){
      let this_ = this;
      console.log("App.vue mounted");    
      // this_.resizeAble();  
    },
    beforeDestroy(){      
      bus.$off("sendSplitPanesFlag");
      // bus.$off("maotingyuntest");
    }

  }
</script>
<style>
  body {
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
  }
  #system-interface-box{
    margin-top: -8px;
    margin-bottom: 0px;
    margin-left: -5px;
    margin-right: -5px;
  }
  #main-view-nav{
    width:100%;
    max-height:20px;
  }
  #system-interface-box{
    /*width:1798px;*/
  }
  .top-info-box{
    height:34px;   
    margin: 0px -2px 1px -2px;
    padding:5px 0px 0px 5px;
    border-style: solid;
    border-color:#080808;
    border-top-width: 2px;
    border-right-width: 2px;
    border-bottom-width: 2px;
    border-left-width: 2px;
    /*background:#595959;*/
    color: #ffffff;
    /*以下是顶部框的圆角设置*/
    border-top-left-radius:0px;
    border-top-right-radius:0px;
    font-size: 19px; 
    background-image: linear-gradient(to bottom, #3c3c3c 0%, #222 100%);  

  }
  .left-info-box{  
    /*height: 895px;*/
    height: 902px;
    /*width:20px;*/
    overflow-y: auto;
    overflow-x: hidden;
    margin: 0px 0px 0px 0px;
    padding:0px 0px 0px 4px;
    border-style: solid;
    border-color:#ddd;
    border-top-width: 2px;
    border-right-width: 2px;
    border-bottom-width: 2px;
    border-left-width: 2px;

    background: #f5f5f5; /*原来:#f5f5f5 候选:#f3f3f3; background-color*/
    
  }
  .right-info-box{ /*右侧与左侧保持同高.*/
    height: 902px;
    /*display: table;*/
    /*border: 1px solid #f8f8f8;*/
    /*box-shadow: 0px 0px 4px rgba(0, 0, 0, .5);*/
    border-style: solid;
    border-color:#ddd;
    border-top-width: 2px;
    border-right-width: 2px;
    border-bottom-width: 2px;
    border-left-width: 2px;
    margin: 0px 0px 0px 0px;
  }
  .middle-info-box{
    height: 902px;
    /*display: table;*/
    /*border: 1px solid #f8f8f8;*/
    /*box-shadow: 0px 0px 4px rgba(0, 0, 0, .5);*/
    border-style: solid;
    border-color:#ddd;
    border-top-width: 2px;
    border-right-width: 2px;
    border-bottom-width: 2px;
    border-left-width: 2px;
    margin: 0px 0px 0px 0px;
  }
  #main-view-nav{
    height: 20px;
  }
  .splitpanes.default-theme .splitpanes__pane {
    background-color: #ffffff;
  }
  .navbar-header-div{
    display: inline-block;
  }
  #right-side-div{
    float:right;
  }
  .place-right-side{
    padding:0px 5px 0px 10px;
  }

  .splitpanes.default-theme .splitpanes__splitter{   

    background-color: #f5f5f5; /*原来:#f5f5f5, 候选:#f3f3f3*/
  }
  .context-menu-list{
     min-width: 100px;
     max-width: 350px;
  }
  
  .jBox-Modal.jBox-closeButton-title .jBox-title {
    padding-right: 55px;
    padding-left: 2px;
    padding-top: 10px;
    padding-bottom: 10px;
  }
  
  .jBox-title{
    font-size: large;
    font-weight: 600;
  }
  #load-database{
    margin:0px 0px 0px 30px;
    height:35px;
  }

  .graph-info-display{
    font-size: 14px;
    font-weight: 200;
  }
  #search-condition-view-box .el-input__inner, #load-db-view .el-input__inner{
     border-radius: 0px;
  }
  .el-button--mini, .el-button--small {
    height: 29px;
    font-size: 12px;
    border-radius: 0px;
  }  

  .left-info-box .el-collapse-item__header{
      padding-left: 5px;
      font-weight: 600;
      height: 30px;
      line-height: 30px;      
  }
   .left-info-box .el-collapse-item__arrow {
        
    float: left;
    line-height: 30px; 
    
  }   
   
   #focus-node-selection-rank  .el-collapse-item__header {
      padding-left: 5px;
      font-size:14px;
      font-weight: 500;
      height: 30px;
      line-height: 30px;
   }
   #focus-node-selection-rank .el-collapse-item__arrow {
    float: right;
    line-height: 30px; 
   }

   #search-condition-view-box .el-collapse-item__header {
      padding-left: 5px;
      font-size:14px;
      font-weight: 500;
      height: 30px;
      line-height: 30px;
   }
   #search-condition-view-box .el-collapse-item__arrow {
    float: right;
    line-height: 30px;
   }

  .el-table {
    /*font-size: 13px;*/
    font-weight: 400;
  }
  .el-table thead {
    color: #212020;
    font-weight: 500;
  }
  .el-collapse-item__content >div {
    margin: 0px;
    /* border: 0; */
    padding: 0;
  }
  .el-collapse-item__content {
    padding-bottom: 25px;
    font-size: 13px;
    color: #303133;
    line-height: 1.1;
  }
  #select-method-input{
    border-color: rgb(255, 255, 255);
    background-color: white;
  }
  #search-result-table .el-table .caret-wrapper {
    display: -webkit-inline-box;
    display: -ms-inline-flexbox;
    display: inline-flex;
    -webkit-box-orient: vertical;
    -webkit-box-direction: normal;
    -ms-flex-direction: column;
    flex-direction: column;
    -webkit-box-align: center;
    -ms-flex-align: center;
    align-items: center;
    height: 34px;
    width: 0px;
    vertical-align: middle;
    cursor: pointer;
    overflow: initial;
    position: relative;
}
#node_num_widget .el-button--primary, #foucus-set .el-button--primary{
    color: #303133;
    background-color: #eae9e9;
    border-color: #c1c1c1;
}
.reset-fault-layout-settings .el-button--primary{
    color: #303133;
    background-color: #eae9e9;
    border-color: #c1c1c1;
}
.el-button--primary span{
   font-weight: 600;
}
.block-layout-control{
  font-size:13px;
}

#jBoxHist .jBox-title{  
  font-weight: 600;
}
#conditions-search-view .el-form--inline .el-form-item{
    margin-right: 0px; 
}
#jBoxAttribute .el-tag {
    background-color: rgba(64,158,255,.1);
    padding: 0 10px;
    height: auto;
    line-height: 6px;
    font-size: 6px;
    color: #409EFF;
    border-radius: 4px;
    -webkit-box-sizing: border-box;
    box-sizing: border-box;
    border: 1px solid rgba(64,158,255,.2);
    white-space: nowrap;
}
#jBoxAttribute .el-tag-node-attri{
  background-color: rgba(64,158,255,.1);
    padding: 0 10px;
    height: auto;
    line-height: 14px;
    font-size: 6px;
    color: #409EFF;
    border-radius: 4px;
    -webkit-box-sizing: border-box;
    box-sizing: border-box;
    border: 1px solid rgba(64,158,255,.2);
    white-space: nowrap;
}
#ranking-by-node-measures thead th{
  padding: 0px 0px 0px 0px;
}
#search-result-table thead th{
  padding: 0px 0px 0px 0px;
}
/*#ranking-by-node-measures .el-table__body-wrapper tbody tr{
  padding: 0px 0px 0px 0px;
}*/
.jBoxSeeMoreOfNodeRanking .jBox-title{
  font-size:15px;
}
.jBoxSeeMoreOfNode .jBox-title{
  font-size:15px;
}
.nodeinfo-see-more-in-mianview .author-number{
  font-size:12px;
  font-weight:600;
}
.jBoxSeeMoreOfNodeResult .jBox-title{
  font-size:15px;
}
.hist-nav-text{  
  font-size: 15px;
}
.el-slider__bar{
  background-color: #91d5ff;
}
#jBoxDoiLayoutSetting .el-slider__button{
  border: 2px solid #91d5ff;
}
#jBoxresultVisLayoutSetting .el-slider__button{
  border: 2px solid #91d5ff;
}
.el-switch.is-checked .el-switch__core {
    border-color: #91d5ff;
    background-color: #91d5ff;
}
.el-switch__label.is-active{
  color: #6cb2de;
}
#doi-layout-setting .el-slider__runway{
  margin: 10px 0px 10px 0px;
}
#result-vis-layout-control .el-slider__runway{
  margin: 10px 0px 10px 0px;
}
.el-table{
  font-size: 14px;
  font-weight: 500;
}
.el-autocomplete-suggestion li{
  font-size: 13px;
  font-weight: 500;
}
.el-input__inner{
  font-size: 14px;
  font-weight: 500;
}
.el-select-dropdown__item{
  font-size: 14px;
  font-weight: 500;
}
/*以下控制各个视图标题大小*/
.el-collapse-item__header{
  /*左侧标题字体大小*/
  font-size: 17px;
}
.mian-view-item-name{
  font-weight: 600;
  font-size:17px;
}
.result-vis-box-name{
  font-size:17px;
  font-weight: 600;
}
#jBoxHist .jBox-title{
  font-size:17px;
}
#force-layout-parameter-setting{
  font-size: 13px;
  font-weight: 500;
}
#css-style-setting{
  font-size: 13px;
  font-weight: 500;
}
#focus-selection-view-box .el-button--mini, .el-button--small{
 font-size: 13px;
}
#conditions-search-view button{
      height: 30px;
      margin: 0px 0px 0px 0px;
}
#jBoxInterestAttributesRanking .jBox-title{
    font-size: 15px;
    font-weight: 600;
}
.context-menu-list{
  width:230px;  
}
.context-menu-list li{
  font-size: 14px;
}
.focusSelectionMenuMainView{
  width:208px;
}
.histViewContextMenu{
  width:50px;
}
#jBoxInterestAttributesMainView .jBox-title{
    font-size: 15px;
    font-weight: 600;
}
#jBoxInterestAttributesSearchVis .jBox-title{
    font-size: 15px;
    font-weight: 600;
}
#jBoxInterestAttributesSearch .jBox-title{
    font-size: 15px;
    font-weight: 600;
}
#jBoxAttribute .jBox-title{
  font-size: 15px;
  font-weight: 600;
}
/*.condition-div-list{
    width:400px;
    overflow-x: auto;
    overflow-y: auto;
}
.attri-conditions-box{
  
}*/
#sorted-by-which-method{
  font-weight: 500;
}
#search-table-num-records{
  font-weight: 500;
}
#settings-first-box{
  font-weight: 500;
}
/*.matched-panel-text{
  font-size: 13px;
  font-weight: 500;
}*/
#node-info-box td{
  font-size:14px;
  font-weight: 500;
}
#jBoxLegend text{
  font-size: 14px;
  font-weight: 500;
}
.attr-explor-title{
  padding:0px 2px 2px 2px;
  border-style: solid;
  border-color:#ddd;
  border-top-width: 0px;
  border-right-width: 0px;
  border-bottom-width: 0px;
  border-left-width: 0px;
  margin: 0px 0px 0px 0px;
  width:400px;
  font-size: 14px;
  font-weight:500;
}
#settings-first-box{
  font-size: 14px;
  font-weight:500;
}
#sorted-by-which-method{
  font-size: 14px;
  font-weight:400;
}
#search-table-num-records{
  font-size: 14px;
  font-weight:400;
}
/*各弹出窗口标题的字体大小*/
#jBoxLegend .jBox-title {
  font-size: 15px;
  font-weight: 600;
}
#jBoxNodeInfo .jBox-title{
  font-size: 15px;
  font-weight: 600;
}
#jBoxresultVisLayoutSetting .jBox-title, #jBoxDoiLayoutSetting .jBox-title, #jBoxEdgeInfo .jBox-title{
  font-size: 15px;
  font-weight: 500;
}
#focus-attributes-selection-view{
  padding: 0px 0px 0px 2px;
}
body {
    font-family: Yantramanav,Helvetica Neue,Helvetica,sans-serif;
    color: #333;
}
.el-table{
  color: #333;
}
.el-input__inner{
  color: #333;
}
.el-collapse-item__header{
  background-color: #eae9e9;
}
#jBoxHist #list{
  margin: 5px 0px 0px 0px;
  padding: 0px 0px 0px 0px;
}
/*浏览器样式设计*/
/*定义滚动区域的样式，设置高度无意义*/
/* 设置滚动条的样式 */
/*::-webkit-scrollbar {
    width: 10px;
}*/
/* 滚动槽 */
/*::-webkit-scrollbar-track {
    -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.3);
    border-radius: 10px;
}*/
/* 滚动条滑块 */
/*::-webkit-scrollbar-thumb {
    border-radius: 10px;
    background: #bbb;
    -webkit-box-shadow: inset 0 0 6px rgba(0,0,0,0.5);
}
::-webkit-scrollbar-thumb:window-inactive {
    background: rgba(255,0,0,0.4);
}
*/


</style>