<template>
<div id="main-view-nav-box-div">
  <div class="mian-view-item mian-view-item-name">
    <span>Subgraph of Interest</span>
  </div>
  <div class="mian-view-item mian-view-item-info graph-info-display"><!--节点及边的数量-->
    <span>Nodes:{{doiGraphInfo.numnodes}}</span>
    <span>| Edges:{{doiGraphInfo.numedges}}</span>
  </div>
  <div class="mian-view-item" id="main-view-nav-box">
    <div class="img-icon-box" id="main-view-layout-setting"><!--节点布局设置-->
      <img class="img-icon" id="main-view-nav-icons-setting" width="20" height="20" src="../../static/img/icons-setting-blue.png">
    </div>
    <div class="img-icon-box" id="icons-search-attri"> <!--节点属性探索图标-->         
      <img class="img-icon" id="img-search-attri" width="20" height="20" src="../../static/img/icons-search-attri.png">
    </div>
    <!--历史走廊图标-->
    <!-- <div class="img-icon-box" id="hist-icon"> 
      <img class="img-icon" id="hist-img" width="20" height="20" src="../../static/img/icons-hist.png">         
    </div> -->
    <div class="img-icon-box" id="export-main-view-icon"><!--导出SVG为PNG-->
      <img class="img-icon" id="export-main-view-svg-img" width="20" height="20" src="../../static/img/export-svg.png">         
    </div>

    <div class="img-icon-box" id="delete-main-view-icon"><!--删除主要视图布局图图标-->
      <img class="img-icon" id="delete-main-view-svg-img" width="20" height="20" src="../../static/img/icons-delete.png">         
    </div>
  </div>
</div>
</template>

<script>
  import $ from 'jquery'
  import bus from '../eventbus.js' // 事件总线.
  export default {    
    data: function(){
      return {
         doiGraphInfo: {numnodes:0, numedges:0}, //DOI子图的信息.
      }
    },
    methods:{
      highLightIcon(){
        $(".img-icon-box").mouseover(function(e){
          // console.log("this");console.log(this);
          // console.log("this e");console.log();
          let id = e.currentTarget.childNodes["0"].id; //节点id.         
          $("#" + id).css("background-color", "#E0E0E0"); //如果是焦点,则高亮焦点标签.
        });
        $(".img-icon-box").mouseout(function(e){
          // console.log("this e");console.log(e.currentTarget.childNodes["0"].id);
          let id = e.currentTarget.childNodes["0"].id; //节点id.
          $("#" + id).css("background-color", "#fff"); //如果是焦点,则高亮焦点标签.
        });
      },
      createMouseOverEvents(){
          $('#img-search-attri').jBox('Mouse', { // jBox在本文件中并没有引入,但是也能用(在mainView.vue中引入了).
              theme: 'TooltipDark',
              content: 'Matching Panel',
              position: {
                x: 'left',
                y: 'bottom'
             }
          });
          $('#hist-img').jBox('Mouse', { // jBox在本文件中并没有引入,但是也能用(在mainView.vue中引入了).
            theme: 'TooltipDark',
            content: 'History View',
            position: {
              x: 'left',
              y: 'bottom'
            }
          });
          $('#legend-img').jBox('Mouse', { // jBox在本文件中并没有引入,但是也能用(在mainView.vue中引入了).
            theme: 'TooltipDark',
            content: 'Legend',
            position: {
             x: 'left',
              y: 'bottom'
            },
            offset: -5
          });
          $("#main-view-nav-icons-setting").jBox("Mouse", {
              theme: 'TooltipDark',
              content: 'Layout Setting',
              position: {
                x: 'left',
                y: 'bottom'
             }
          });
           $("#export-main-view-svg-img").jBox("Mouse", { ///
              theme: 'TooltipDark',
              content: 'Export svg to png',
              position: {
                x: 'left',
                y: 'bottom'
             }
          });
          $("#delete-main-view-svg-img").jBox("Mouse", {
              theme: 'TooltipDark',
              content: 'Delete graph',
              position: {
                x: 'left',
                y: 'bottom'
             }
          });

      },
    },
    created(){
       let this_ = this;
       bus.$on("sendDoiGraphInfo", function(data){
        this_.doiGraphInfo = data;        
      });
    },
    mounted(){
      let this_ = this;
      this_.highLightIcon();
      this_.createMouseOverEvents();
    },
    beforeDestroy(){
       bus.$off("sendDoiGraphInfo"); // 接收DOI graph 数据.      
    }    
  }
</script>

<style>
 .img-icon-box{
   float:right; /*由于是靠右对齐,所以按照从右边到左的顺序排放*/   
   width: 20px;
   height:20px;
   display: table-cell; /*table-cell*/ 
   /* 水平居中 */
   text-align:center; 
   /* 垂直居中 */ 
   vertical-align:middle;
   /*border: 1px solid #E0E0E0;*/
   margin:2px 4px 0px 4px;   
   
   /*border-style: solid;
   border-color:#E0E0E0;
   border-top-width: 0px;
   border-right-width: 1px;
   border-bottom-width: 1px;
   border-left-width: 1px;*/
 }
 #main-view-nav-box-div .mian-view-item{
  display:inline-block;
 }
 #main-view-nav-box-div #main-view-nav-box{
  float: right;
 }

 #main-view-nav-box-div{
   height:24px;
   vertical-align:middle; /* 垂直居中 */
   background-color: #f5f5f5; /*#f5f5f5*/
   margin: 0px 0px 0px 0px;
}

</style>
