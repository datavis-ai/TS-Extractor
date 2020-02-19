<template>
	<div id="focus-node-selection-rank">		
    <!-- <el-collapse v-model="activeNames"> -->
		  <!-- <el-collapse-item title="Ranking List" name="Ranking List">	         -->
		    <div id="focus-node-selection-rank-box">
          <div id="sorted-by-which-method" v-if="tableheader.length > 0">
            <span>Top 100 nodes ranked by</span>          
            <select id="select-method-input" @change="myselect($event)" v-model="rankingMethod">
              <option :value="item.value" v-for="item in methodOptions">{{item.value}}</option>            
            </select> 
          </div>
          <div id="ranking-by-node-measures" v-if="tableheader.length > 0">
              <el-table            
              :data="tableData"
              border
              ref="resultTable"
              highlight-current-row
              :row-class-name="tableRowClassNameResult"
              :cell-class-name="tableCellClassNameResult"
              empty-text="null"            
              style="width: 100%"    
              :max-height="tableheight"
              @cell-click="cellClickEvent"
              >
                <el-table-column
                  type="index"
                  fixed
                  width="50" >   
                </el-table-column>       
                <el-table-column
                  v-for="item in tableheader"
                  v-if="item.prop!='id'"      
                  :prop= "item.prop"
                  :label= "item.label"
                  :width="item.width"                      
                  show-overflow-tooltip
                  >
                </el-table-column>      
              </el-table>            
          </div>
        </div>
        
		  <!-- </el-collapse-item> -->
		<!-- </el-collapse>     -->
  <div id="ranking-table-see-more"></div> <!--节点信息,查看更多-->
  <div id="interest-attributes-ranking-list">
      <focusattributesselection :callback="callbackForInterestAttributes"></focusattributesselection>
  </div>
	</div>	
</template>

<script>
 
  import axios from 'axios' // 用于AJAX请求
  import * as d3 from '../../static/js/d3.v4.min.js'
  // import {d3GraphLayout} from "../../static/js/d3ForceGraph.js"
  import {jBox} from "../../static/js/jBox.js" 
  import $ from 'jquery'
  import {vueFlaskRouterConfig} from '../vueFlaskRouterConfig'
  import bus from '../eventbus.js' // 事件总线.
  import "../../static/js/jquery.contextMenu.js"
  import "../../static/js/jquery.ui.position.js"
  import focusattributesselection from "@/components/focusAttributesSelection"

  export default {    
    data: function(){
      return {
         tableheader: [], // 表头
         tableData: [], // 表数据.
         tableheight: "250", // 表格高度
         activeNames:["Ranking List"],
         ableClickClassName:"clickSeeMore",
         // whichMethod: "PageRank", //默认方法是PageRank当前选中的方法.
         rankingMethod: "PageRank",
         methodOptions:[
           {value: 'PageRank'},           
           {value: 'Degree'},          
           {value: 'Betweenness'},
           {value: 'Closeness'}
         ],
         seeMoreFieldList: null, //{"publication",...}
         seeMoreObjList: {}, // {}
         jBoxInstance: {
          seeMoreJbox: null, //see more box.
          interestAttributes: null, // 兴趣属性窗口.
         },
         rightClickNodeGetId: "", // 用于获取表格所在行的节点id.

      }
    },
    computed:{
       
    },
    components: { // 组件注册后可以作为标签使用.
       focusattributesselection
    },
    created(){
       let this_ = this;
       bus.$on('sendRankTableNodeMeasure', function(data){          
           this_.tableheader = data.tableheader; // 表头数据
           if(this_.$store.state.selection.selectiondb == "co-authorship.db"){
               let tableData = data.tabledata; // 表格数据
               let indexTheMan = null;

               for(let i=0; i<tableData.length; i++){
                 let objId = tableData[i].id;
                 if(objId == "647629"){
                   indexTheMan = i;
                   break;
                 }             
               }

               let newTableData = this_.swapItem(tableData, indexTheMan, 4);
               this_.tableData = newTableData; // 表格数据
           }
           else{
             this_.tableData = data.tabledata; // 表格数据
           }
           
          
           this_.seeMoreObjList = {}; //每次表格数据更新都清零.
           this_.seeMoreFieldList = new Set(); //集合.
           for(let i=0; i<data.tabledata.length; i++){
             let row = data.tabledata[i]; //表格的一行,row={id:x, name:x, ..., publications:x}
             let keyListRow = Object.keys(row); //[id, name, ...]
             let tempObj = {}; //{publications:x}
             let id = '';
             keyListRow.forEach(function(key, index){
               if(key == "id"){
                 id = row[key];
               }
               if(this_.$store.state.infoSearchView.dbtables.indexOf(key) != -1){ //在里面.
                  tempObj[key] = row[key];
                  this_.seeMoreFieldList.add(key);//{publications,...}
               }
             });
             this_.seeMoreObjList[id] = tempObj;
           }
       });
       bus.$on("sendRankingDefaultMethod", function(data){ // data是数据库名称,e.g., "Citation_Visualization.db"
         if(data){
           this_.rankingMethod = "PageRank";
           this_.tableData.splice(0, this_.tableData.length);
           this_.tableheader.splice(0, this_.tableheader.length);
           this_.$store.state.selection.dboptions.forEach(function (item, index){               
               if(item.label == data){
                  let graphDirected = item.directed; // true/false
                  if(graphDirected){ // true
                    this_.methodOptions = [
                       {value: 'PageRank'},
                       {value: 'Degree'},
                       {value: 'In-Degree'},
                       {value: 'Out-Degree'},          
                       {value: 'Betweenness'},
                       {value: 'Closeness'}
                    ];
                  }
                  else{ // false
                    this_.methodOptions = [
                       {value: 'PageRank'},
                       {value: 'Degree'},                                 
                       {value: 'Betweenness'},
                       {value: 'Closeness'}
                    ];
                  }
               }
           });
         }
       });
       // bus.$on("snedDboptions", function(data){
          
       // });
       
    },
    methods:{
      swapItem(arr, fromIndex, toIndex) {
            arr[toIndex] = arr.splice(fromIndex, 1, arr[toIndex])[0];
            return arr;
      },
      callbackForInterestAttributes(){
          let this_ = this;
          let nodeId = this_.rightClickNodeGetId;
          let row = null; // 节点的信息,对应表格中的一行.
          for(let i=0; i<this_.tableData.length; i++){ // 从表格数据中选出被点击节点对应的记录.
             let obj = this_.tableData[i];
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
          let focusObj = {"id": id,  // id作为唯一标识,
                          "tag": tag, // tag作为节点的标签.
                          "dbname":dbname,
                          "field":"NULL",
                          "keyword": "NULL",
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
          bus.$emit('sendSlectedNode', focusObj); //sendSlectedNode事件,在focusSetView.vue中监听.
          $("#ranking-by-node-measures ." + nodeId + " td:first-child").css("background-color", this_.$store.state.resultsSearchView.focusColor); //选中该点作为焦点后,高亮.
          // if(this_.$store.state.resultsSearchView.isOpenResultVis){ //如果打开了result vis 弹窗.
          //   $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css("fill", this_.$store.state.resultsSearchView.focusColor); //删除焦点后,取消高亮,恢复.
          // }
          // this_.$store.state.resultsSearchView.focusStateList.push(nodeId); 
          this_.$store.state.nodeRankTable.focusStateList.push(nodeId); // //将该点的id记录在案.
          this_.jBoxInstance.interestAttributes.close();
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
      orderForArray(yearArr, idArr){ //see more中论文按照年份降序排列.
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
      cellClickEvent(row, column, cell, event){ //注意:同时注册表格的单元格+行点击事件,先执行单元个点击事件.
        let this_ = this;
        let key = column.label; //publications.
        if(this_.$store.state.infoSearchView.dbtables.indexOf(key) != -1){ //在里面.只有点击"see more..."才会进入执行.
          this_.isClickSeeMoreOut = true;
          let nodeId = '';
          let letterCalssList = ["context-menu-active", "current-row", "el-table__row", "hover-row"];//字母组成的类名,只要表格不改动.这个列表就不改动.                
          event.target.offsetParent.parentElement.classList.forEach(function(item, index){
            if(letterCalssList.indexOf(item) == -1){ //不在里面.
               nodeId = item;
            }
          });
          // if(this_.tableRowClickTempNodeList.length > 0){
          //   this_.tableRowClickTempNodeList.pop(); //弹出.
          //   this_.selectedTempRowList.pop();
          // }
          // if(this_.tableRowClickNodeList.length > 0){ //行已经被高亮
          //   let id = this_.tableRowClickNodeList[0]; //只有一个.
          //   if(nodeId == id){ //被高亮的是当前行.
          //     this_.isClickSeeMore = true; //点击了 see more
          //     this_.tableRowClickTempNodeList.push(id); //保持只有一个id.
          //     this_.selectedTempRowList.push(this_.selectedRowList[0]); //将当前row数据存入里面.
          //   }
          // }
          console.log("nodeId");console.log(nodeId);
          console.log("key");console.log(key);
          console.log("this_.seeMoreObjList");console.log(this_.seeMoreObjList);
          
          let obj = this_.seeMoreObjList[nodeId]; //{publications:xxxx, ...}
          let value = obj[key]; // value="id1;id2;id3;id4",由id加分号构成的字符串.
        
          let dbName = this_.$store.state.selection.selectiondb; // 数据库的名称.
          let tableName = key;
          let param = { "dbName": dbName, // DB name
                        "value": value, // value="id1;id2;id3;id4"
                        "tableName": tableName}; // tableName="publications",刚好是字段的名陈.
          
          axios.post(vueFlaskRouterConfig.mainViewNodeDetailsSeeMore, {
              param: JSON.stringify(param)
          })
          .then((res) => { 
              let data = res.data;  // 通过查询选中焦点,然后用焦点的id获得图数据.
              if(tableName == "publications"){ // todo: publications的定制显示,对于其他的数据则需要另外编写代码来定制显示.这块不太好扩展.
                // this_.jboxTitle = "Publication";
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
                let tempHtml = "<div class='author-number'><span>Author: %s</span><span>&nbsp&nbsp&nbsp&nbsp&nbsp&nbspnumber: %s</span></div>"; 
                let allHtml = this_.sprintf(tempHtml, row.name, String(totalNum));     
                for(let i=0; i<orderId.length; i++){
                  let id = orderId[i];
                  let obj = data[id];
                  let title = obj.title;
                  let authors = obj.authors;
                  let public_venue = obj.public_venue;
                  let year = obj.year;
                  let abstract = obj.abstract;
                  let html = '<div class="each-one"><h5 class="content">%s. %s</h5><p class="content"><em id="author">%s</em></p><p class="content"><strong id="venue">%s(%s)</strong></p><span class="collapsibleinseemore"><img src="data:image/gif;base64,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"><span class="collapsible-icon-name">Abstract</span></span><div class="collapsible-content"><div class="abstract"><div class="abstract-content">%s</div></div></div></div>';
                  let newHtml = this_.sprintf(html, String(i+1), title, authors, public_venue, year, abstract);
                  allHtml += newHtml;
                }
                $("#ranking-table-see-more").html(allHtml); // 这个操作不会进入updated里面.插入直接渲染,因此在下面可以调用initSeeMore函数来注册事件.
                this_.initSeeMore();
              }          
              
            })
            .catch((error) => {            
              console.error(error);
            });

        }
        else{ // 非see more.
          this_.jBoxInstance.seeMoreJbox.close(); //关闭. 放到这里完美解决.
        }
      },
      initSeeMore(){
        let coll = $(".collapsibleinseemore");    
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
      insertSeeMore(){
        let this_ = this;        
        let keyList = Array.from(this_.seeMoreFieldList); //集合转化成数组.        
        for(let i=0; i<keyList.length; i++){
          let className = keyList[i]; // 字段名,也是calss name.
          let html = "<p class='cell-see-more'>See More...</p>";
          $("#ranking-by-node-measures ." + className + " .cell").html(html);
        } 
        
      },
      myselect(event) {
        let this_ = this;
        let whichMethod = event.target.value; // 所使用的方法    
        if(this_.$store.state.isUsingRankMeasures){ // 是否使用排序度量.
            let requestNodeRankTable = vueFlaskRouterConfig.selctionFocusNodesByNodeMeasures + "/" + this_.$store.state.selection.selectiondb + "/" + whichMethod + "/" + this_.$store.state.nodeRankTable.topN;
            axios.get(requestNodeRankTable)
            .then((res) => {
              let nodeRankTable = res.data;
              this_.tableheader = nodeRankTable.tableheader; // 表头数据
              this_.tableData = nodeRankTable.tabledata;
            })
            .catch((error) => {            
              console.error(error);
            });
        }
      },
      handleCurrentChange(currentPage) { //改变当前页数.
        let this_ = this;
        this_.currentPage = currentPage;
      },
      tableCellClassNameResult({row, column, rowIndex, columnIndex}){ //表格单元class命名.
        let this_ = this;        
        let fieldName = column.label; //字段名称.
        let className  = this_.ableClickClassName + " " + fieldName; // 如果在里头则可以点击查看更多.
        if(this_.$store.state.infoSearchView.dbtables.indexOf(fieldName) != -1){ // 如果在里面.
           return "" + className;
        }
        else{
          return "" + fieldName;
        }
      },
      tableRowClassNameResult({row, rowIndex}){ //实验证明,只要鼠标悬浮/点击就会执行这个函数,与右键插件的绑定无关,应该与绑定了表格本身只带事件有关系.
        let this_ = this;
        let rowClass = row.id; //节点id.        
        return rowClass;        
      },

    },
    watch:{
      // whichMethod: function(curVal, oldVal){
      //   console.log("whichMethod: function(curVal, oldVal)");
      //   console.log(curVal);
      // }
    },
    mounted(){
      let this_ = this;
      $.contextMenu({  // fixme:右键表格中的某行,选为焦点.
            selector: '#ranking-by-node-measures .el-table__row',
            className: "focusSelectionMenuRanking", // 添加自定义类名称.  
            callback: function(key, options) {
                 let nodeId = '';
                 let letterCalssList = ["context-menu-active", "current-row", "el-table__row"];//字母组成的类名.               
                  options.$trigger.context.classList.forEach(function(item, index){
                    if(letterCalssList.indexOf(item) == -1){ //不在里面.
                       nodeId = item;
                    }
                  });
                 
                 if(key == "copy"){  // 选为焦点,并添加到焦点集中.
                    this_.rightClickNodeGetId = nodeId;
                    
                  }
                 if(key == "cut"){ // 取消该点作为焦点.
                   bus.$emit("sendDeleteFocusInRankingList", nodeId);                   
                   this_.$store.state.nodeRankTable.focusStateList.splice(this_.$store.state.nodeRankTable.focusStateList.indexOf(nodeId), 1); //删除nodeId.                 
                 }
            },
            items: { // todo:以后修改图标.
                "copy": {name: "Add it to the focus set", className: "addToTheFocusSet"}, // 作为焦点. , icon: "copy" 
                "cut": {name: "Delete it from the focus set"},              
                "quit": {name: "Quit"}                
            }                   
      });
      this_.jBoxInstance.interestAttributes = new jBox('Modal', {
            id: "jBoxInterestAttributesRanking", // 弹出兴趣属性选择框.
            addClass: "jBoxInterestAttributesRankingClass",  // 添加类型,这个功能很棒啊!
            attach: '.focusSelectionMenuRanking .addToTheFocusSet',
            width: 300,              // Maximal width
            height: 150,             // Maximal height 
            title: 'Attributes of Interest',
            // fixed:true,
            overlay: false,
            fixed: false,
            adjustTracker: true,
            zIndex: 1005, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
            createOnInit: true,
            content: $("#interest-attributes-ranking-list"),  // jQuery('#jBox-content') 
            draggable: true,
            repositionOnOpen: false,
            repositionOnContent: true,
            target: $('.focusSelectionMenuRanking .addToTheFocusSet'),//$('#filtered-subgraph-nav-icons-setting'),
            offset: {x: -135, y: 100}, // {x: -135, y: 155},
            // 以下是弹窗事件,这些功能真的非常优秀!
            onOpen: function(){                   
                this_.jBoxInstance.interestAttributes.position({
                   target: $('.focusSelectionMenuRanking .addToTheFocusSet')//$('#filtered-subgraph-nav-icons-setting') //注意,这样保证:当 jBoxInstance.resultVis 移动后,重新打开layoutSetting,layoutSetting能够跟着jBoxInstance.resultVis走.           
                });
                bus.$emit("attributesOfInterestPanelUpdate", true); // 提醒 "兴趣属性选择" 面板更新勾选列表.
            },
            onCloseComplete: function(){                     
              
            }
      });
      
    },
    updated(){
      let this_ = this;
      console.log("globalGraphView updated maotingyun");
      if(this_.tableheader.length > 0){
        this_.insertSeeMore();
        this_.jBoxInstance.seeMoreJbox = new jBox('Modal', {
                  //todo: 添加唯一的id就会出现问题.
                  addClass: "jBoxSeeMoreOfNodeRanking",  // 添加类型,这个功能很棒啊!
                  attach: "#focus-node-selection-rank ." + this_.ableClickClassName, //指定在#resultssearch内部,避免冲突.
                  width: 400,              // Maximal width 
                  maxHeight: 800,              
                  title: "Publications",
                  overlay: false,
                  zIndex: 1005, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
                  createOnInit: true,
                  content: $("#ranking-table-see-more"),  //唯一,避免冲突.
                  draggable: true,
                  repositionOnOpen: false,
                  repositionOnContent: true,                  
                  position:this_.$store.state.jboxPositionSet.topRightSide,
                  // 以下是弹窗事件,这些功能真的非常优秀!
                  onOpen: function(){
                  
                  },
                  onCloseComplete: function(){ // todo: 发生一个很诡异的现象: 会执行多次onCloseComplete.明明see more框还开着确说已经关闭了,最后在mainView中使用jquery的css方法查看diaplay == block 或none来判断是否关闭.
                  }
         });
        if($(".jBoxSeeMoreOfNodeRanking").length > 1){ // 这样可以避免出现多个
            $(".jBoxSeeMoreOfNodeRanking").first().remove(); // .first()
        }
      }
      
    },
    beforeDestroy(){
      bus.$off('sendRankTableNodeMeasure'); // 注销事件.
      bus.$off("sendRankingDefaultMethod");
      // bus.$off("snedDboptions");
    }   
  }
</script>

<style>
#ranking-table-see-more {
    display: none;
    max-height: 400px; 
    max-width: 500px;
    padding:2px 2px 2px 4px;
    overflow: scroll;
  }
  
/* 以下是论文的样式 */
#ranking-table-see-more .abstract {
  max-height: 217px;
  max-width: 489px;
  overflow: scroll;
  padding: 0px 0px 0px 5px;  
  margin: 5px 1px 5px 1px;
  font: normal normal normal normal 12px / 20px Lato, sans-serif;  
}
#ranking-table-see-more .author-number{
  margin:2px 0px 8px 0px;
  border-style: solid;
  border-color:#E0E0E0;
  border-top-width: 0px;
  border-right-width: 0px;
  border-bottom-width: 1px;
  border-left-width: 0px;
  font-size: 12px;
}
#ranking-table-see-more .author-number span{
  width:100%;
  border-spacing: 2px 2px;
  font: normal normal normal normal 12px;
  font-weight: 600;
  
}
#ranking-table-see-more #author{
    color: #069;
    border-spacing: 2px 2px;
    font: italic normal 300 normal 12px / 20px Lato, sans-serif;
}
#ranking-table-see-more #venue{
    border-spacing: 2px 2px;
    font: normal normal normal normal 12px / 20px Lato, sans-serif;
}
#ranking-table-see-more h5{
   color: #069;
}
#ranking-table-see-more .content{
  width: 489px;
  margin: 1px 1px 1px 1px;

}
#info-paper-box{
  max-height: 700px;
  max-width: 500px;
  overflow: scroll;
}

#ranking-table-see-more .collapsible {
  color: #444;
  cursor: pointer;
  border: none;
  text-align: left;
  outline: none;
  font-size: 15px;
}

#ranking-table-see-more .active .collapsible-icon-name, #ranking-table-see-more .collapsible .collapsible-icon-name:hover {
  background-color: #069;

}
.collapsibleinseemore {
  font-size:12px;
}
.collapsibleinseemore img {
  height: 12px;
}

#ranking-table-see-more .collapsible-content {
  display: none;
  overflow: hidden;
  background-color: #f1f1f1;
}
#ranking-table-see-more .each-one{
 border-style: solid;
 border-color:#E0E0E0;
 border-top-width: 0px;
 border-right-width: 0px;
 border-bottom-width: 1px;
 border-left-width: 0px;
}

</style>