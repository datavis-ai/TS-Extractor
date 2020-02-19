<template>
   <div id="resultssearch">
   <!-- <el-collapse v-model="searchResult" @change="handleChange"> -->
      <!-- <el-collapse-item title="Text Search Results" name="Text Search Results"> -->
          <div id="nav-table-results-search-box">
            <div class="nav-table-results-search">
              <div class="nav-table-results-search-div" id="search-table-num-records">
                
                <div v-if="totalTable < 2 && tablevisible">Search result:{{totalTable}} row</div>
                <div v-if="totalTable >= 2 && tablevisible">Search results:{{totalTable}} rows</div>
                
              </div>
              <div class="nav-table-results-search-div" id="subgraph-ul-li">      
                <div v-show="totalTable > 0" id="result-vis-box">          
                 
                  <div id="result-vis-icon-div">                  
                  <img id="result-vis-icon" width="17" height="17" src="../../static/img/subgraph.png">
                  </div>
                </div>
              </div>
            </div>
          </div>
         
          <div v-if="tablevisible" id="search-result-table">
            <el-table            
            :data="tableData.slice((currentPage-1)*pageSize,currentPage*pageSize)"
            border
            ref="resultTable"
            highlight-current-row
            :row-class-name="tableRowClassNameResult"
            :cell-class-name="tableCellClassNameResult"
            empty-text="null"   
            v-if="tablevisible"
            style="width: 100%"    
            :max-height="tableheight"
            @row-click="getRowDetail"
            @cell-mouse-enter="handleMouseOver"
            @cell-mouse-leave="handleMouseLeave"
            @sort-change="handleSortChange"
            @cell-click="cellClickEvent">
              <!-- <el-table-column
                type="index"
                
                width="50" >   
              </el-table-column>  -->      
              <el-table-column
                v-for="item in tableheader"        
                :prop= "item.prop"
                v-if="item.prop!='id'" 
                :label= "item.label"
                :width="item.width"
                :sortable="item.label=='name'?false:true"                      
                show-overflow-tooltip
                >
               <!-- sortable -->
              </el-table-column>      
            </el-table>
            <div v-if="totalTable > 0" id="table-page-box">
              <el-pagination                
                @current-change="handleCurrentChange"
                :current-page="currentPage"                              
                :page-size="pageSize"
                layout="prev, pager, next, jumper"                
                :total="totalTable">
              </el-pagination>
            </div>
          </div>
          
      <!-- </el-collapse-item> -->
    <!-- </el-collapse> -->
    <div class="result-table-see-more"></div> <!--节点信息,查看更多-->     
    <div id="interest-attributes-search-result">
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
  import layoutsettingcomponent from '@/components/layoutSettingComponent'
  import focusattributesselection from "@/components/focusAttributesSelection"
  
  export default {
    data() {
      return {
        // isShowIndex: false,
        tableheight: "250", // 表格高度
        tablevisible: false, //控制是否显示.
        tableheader: [], // 表头
        tableData: [], // 表格数据[{field1:x, field2:x, ...},], e.g.[{id:x, name:x, ...}, ...]

        totalTable: null, // 表格数据量.
        jBoxInstance:{          
          layoutSetting: null, //布局设置.
          seeMoreJbox: null, //see more box.
          interestAttributes: null, // 焦点的兴趣属性. jBoxInstance.interestAttributes
        },
        
        jboxWidth: 800,
        jboxHeight: 800,
        
        svgWidth: 800,
        svgHeight: 700,

        // 以下属性与表格一一对应,表格清零,则其亦然.       
        
        tableRowClickNodeList: [], //表格行点击则装入数组中.[idx]
        selectedRowList:[], //选中的行被放入此中,是tableRowClickNodeList中id对应的行数据,用于高亮显示.
        
        tableRowClickTempNodeList: [], //在高亮行点击seemore时,临时存放tableRowClickNodeList中的id,[idx]
        selectedTempRowList:[], //在高亮行点击seemore时,临时存放selectedRowList中的row,[row]
        isClickSeeMore: false, //是否点击了see more.
        isClickSeeMoreOut: false, // 点击非see more的单元格.
        
        isHighLightCurrentRow: false, //是否高亮当前行.        
        
        ableClickClassName:"clickSeeMore",

        seeMoreObjList: {}, //{110:{publications:xxx}},用于后面的点击查看更多操作.
        seeMoreFieldList: null, //{"publication",...}

        busEventName: "sendLayoutSetOut", //子组件传入参数,发送出来的事件名称.

        currentPage: 1, //表格当前页面.
        pageSize: 0, //一页的数量. 在created()中初始化.        
        clickResultVis: false, // 点击result vis标志位.
        rightClickNodeGetId: "", // 被右键点击"Add it to the focus set"的节点的id.

      }
    },
    components:{
      layoutsettingcomponent,
      focusattributesselection
    },
    created(){
      console.log("resultsSearch created");
      let this_ = this;
      this_.$store.state.resultsSearchView.tableRowClickNodeList = this_.tableRowClickNodeList; //指针赋予.
      this_.busEventName = this_.$store.state.resultsSearchView.busEventName; //初始化变量.
      this_.pageSize = this_.$store.state.resultsSearchView.pageSize; //初始化变量.      
      bus.$on("focusSetClear", function(data){ //切换数据库.
        let labelsClear = data; // 数据库变化标志量.
        if(labelsClear){                  
          // this_.tableheader.splice(0, this_.tableheader.length); // 表格数据清空.
          // this_.tableData.splice(0, this_.tableData.length); // 表格数据清空.
          this_.tableheader = [];
          this_.tableData = [];
          this_.tablevisible = false; // 表格不可见.
          this_.totalTable = 0;          
        }
      });
      bus.$on("tabelDataVisible", function(data){ //data==false.
        // this_.tableheader.splice(0, this_.tableheader.length); // 表格数据清空.
        // this_.tableData.splice(0, this_.tableData.length); // 表格数据清空.
        if(data){ // 当data为true时,删除搜索结果表格.
          this_.tableheader = [];
          this_.tableData = [];
          this_.tablevisible = false; // 表格消失.
          this_.totalTable = 0; 
        }
             
      });
      bus.$on("sendResultsSearch", function(data){ //获得表格数据的源头.
         this_.getDefaultData(); //初始化.         
         this_.$store.state.resultsSearchView.focusStateList = []; //清空.
         this_.$store.state.resultsSearchView.resultVisGraph = null; //获得表格数据,清空前面的数据.
         this_.tablevisible = true; // 渲染表格.
         this_.tableheader = data.tableheader; // 表头
         this_.tableData = data.tabledata; //表数据
         // console.log("resultsSearch mounted this_.tableData");
         // console.log("this_.tableData jingjing");console.log(this_.tableData);
         this_.totalTable = this_.tableData.length; // 总的表格数据量.
         
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
         // console.log("this_.seeMoreObjList");
         // console.log(this_.seeMoreObjList);
         // console.log(this_.seeMoreFieldList);
      });
      bus.$on("sendLocalTablePosInClickEvent", function (data){
        let nodeId = data[0];
        let index = data[1];
        this_.localTablePosInClickEvent(nodeId, index);
      });

      bus.$on("sendCurrentPage", function (data){
         this_.currentPage = data; // 跳转到当前页码,并定位.
      });
      bus.$on("sendDeleteSearchTableFlag", function(data){
         if(data){
            // this_.tablevisible = false; // 表格不可见.
            // this_.tableData = [];
            this_.clickResultVis = false; // 第一次点击打开,再次关闭.
            bus.$emit("sendClickResultVis", this_.clickResultVis);
            bus.$emit("sendSplitPanesFlag", "close");
         }
      });

    },
    computed:{
       searchResult:{ // activeNames是v-model绑定的双向变量,则变量需要有getter + setter,这样才能既读又写.
          // getter
          get: function(){
            if(this.totalTable > 0){ // 
                let temp = [];
                temp.push("Text Search Results");
                return temp;
            }
            else{
              let temp = [];
              return temp;
            }           
         },
         // setter
         set: function(){ // get: 
          
         }
       }
    },
    watch:{ //监听.
      tableData: function(curVal, oldVal){
        let this_ = this;
        this_.$store.state.resultsSearchView.tableData = this_.tableData; //不能放在created()中,一旦tableData被赋值,则改变地址,造成未知后果,所以需要实时赋予.
        if(curVal.length > 0){
         
        }
        else{ //表格为空.
          this_.clickResultVis = false; // 需要重新点击.         
          bus.$emit("sendClickResultVis", this_.clickResultVis);          
          if(this_.jBoxInstance.seeMoreJbox != null){            
           this_.jBoxInstance.seeMoreJbox.close(); //关闭,seemore
          }
          
          this_.$store.state.resultsSearchView.resultVisGraph = null; //清空.
        }
      },
      currentPage: function(curVal, oldVal){
        // this.$store.state.resultsSearchView.currentPage = curVal;
      },
    },
    methods:{
      // iconTooltip(){ // 鼠标悬浮图标,提示功能
      //   $('#result-vis-icon-div').jBox('Mouse', { // jBox在本文件中并没有引入,但是也能用(在mainView.vue中引入了).
      //         theme: 'TooltipDark',
      //         content: 'Search Result Subgraph',
      //         position: {
      //           x: 'left',
      //           y: 'bottom'
      //        }
      //    });
      // },
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
          bus.$emit('sendSlectedNode', focusObj); //sendSlectedNode事件,在focusSetView.vue中监听.
          $("#search-result-table ." + nodeId + " td:first-child").css("background-color", this_.$store.state.resultsSearchView.focusColor); //选中该点作为焦点后,高亮.
          if(this_.$store.state.resultsSearchView.isOpenResultVis){ //如果打开了result vis 弹窗.
            $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css("fill", this_.$store.state.resultsSearchView.focusColor); //删除焦点后,取消高亮,恢复.
          }
          this_.$store.state.resultsSearchView.focusStateList.push(nodeId); //将该点的id记录在案.
          this_.jBoxInstance.interestAttributes.close();
      },
      clickResultVisInit(){
        let this_ = this;
        $("#nav-table-results-search-box #result-vis-icon-div").click(function (e){          
          if(this_.tableData.length > 0){ // 表格非空才有效.            
            this_.clickResultVis = !this_.clickResultVis; // 第一次点击打开,再次关闭.
            bus.$emit("sendClickResultVis", this_.clickResultVis);            
            if(this_.clickResultVis){ // 点击打开
              bus.$emit("sendSplitPanesFlag", "open"); // 弹开窗口.
            }
            else{
              bus.$emit("sendSplitPanesFlag", "close"); // 弹开窗口.
            }
          }           
        });
      },
      seeCurrentPage(nodeId){ //寻找nodeId所在页面.
        let this_ = this;
        let index = null; //nodeId所在的索引.
        let tableLength = this_.tableData.length;
        for(let i=0; i<tableLength; i++){
          let row = this_.tableData[i];
          if(nodeId == row.id){ //找到匹配的id.
             index = i;
             break;
          }
        }
        let currentPage = 0;
        let calculate = index/this_.pageSize;
        currentPage = parseInt(calculate) + 1; //由索引计算出当前所在页.
        return currentPage;
      },     
      handleCurrentChange(currentPage) { //改变当前页数.
        let this_ = this;
        this_.currentPage = currentPage;
      },     
      getDefaultData(){
        let this_ = this;
        this_.tableRowClickNodeList.splice(0, this_.tableRowClickNodeList.length); //表格行点击则装入数组中.[idx]
        this_.selectedRowList = []; //选中的行被放入此中,是tableRowClickNodeList中id对应的行数据,用于高亮显示.            
        this_.tableRowClickTempNodeList = []; //在高亮行点击seemore时,临时存放tableRowClickNodeList中的id,[idx]
        this_.selectedTempRowList = []; //在高亮行点击seemore时,临时存放selectedRowList中的row,[row]
        this_.$store.state.resultsSearchView.tableRowSortList = []; //表格中行的排序列表(当点击排序后,此列表更新,保持与表格排序后的顺序相同)
        // this_.seeMoreObjList: {}, //{110:{publications:xxx}},用于后面的点击查看更多操作.           
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
      insertSeeMore(){ // 插入See More提示.
        let this_ = this;        
        let keyList = Array.from(this_.seeMoreFieldList); //集合转化成数组.        
        for(let i=0; i<keyList.length; i++){
          let className = keyList[i]; // 字段名,也是calss name.
          let html = "<p class='cell-see-more'>See More...</p>";
          $("#search-result-table ." + className + " .cell").html(html);
        }        
      },
      localCurrentRow(row, i) {
        this.$refs.resultTable.setCurrentRow(row); //todo: 使用表格的方法setCurrentRow,使用方法:在表格el-table中写上ref="resultTable",这样就可以用this.$refs.resultTable.setCurrentRow了.
        const targetTop = this.$refs.resultTable.$el.querySelectorAll('.el-table__body tr')[i - 1].getBoundingClientRect().top;
        const containerTop = this.$refs.resultTable.$el.querySelector('.el-table__body').getBoundingClientRect().top;
        const scrollParent = this.$refs.resultTable.$el.querySelector('.el-table__body-wrapper');
        scrollParent.scrollTop = targetTop - containerTop;
        // this.isHighLightCurrentRow = true;
      },
      hightLightCurRow(row, selected){
        if(selected){ //高亮.
          this.$refs.resultTable.setCurrentRow(row);
        }
        else{ //不高亮.
          this.$refs.resultTable.setCurrentRow();
        }
        //this.$refs.resultTable.toggleRowSelection(row, selected);
      },     
      tableCellClassNameResult({row, column, rowIndex, columnIndex}){ //表格单元class命名.
        let this_ = this;        
        let fieldName = column.label; //字段名称.
        let className  = this_.ableClickClassName + " " + fieldName; // 如果在里头则可以点击查看更多.
        if(this_.$store.state.infoSearchView.dbtables.indexOf(fieldName) != -1){ // 如果在里面.
           return className;
        }
        else{
          return fieldName;
        }
      },
      tableRowClassNameResult({row, rowIndex}){ //实验证明,只要鼠标悬浮/点击就会执行这个函数,与右键插件的绑定无关,应该与绑定了表格本身只带事件有关系.
        let this_ = this;
        let rowClass = row.id; //节点id.
        $("#search-result-table .el-table__row" + " td:first-child").css("background-color", ""); //先擦干净. 原来:#fff
        for(let i=0; i<this_.$store.state.resultsSearchView.focusStateList.length; i++){ //重新定位高亮.
          let nodeId = this_.$store.state.resultsSearchView.focusStateList[i]; //焦点节点.          
          $("#search-result-table ." + nodeId + " td:first-child").css("background-color", this_.$store.state.resultsSearchView.focusColor); //选中该点作为焦点后,高亮.                                        
        }
        return rowClass;        
      },      
      localTablePosInClickEvent(nodeId, index){
          let this_ = this;
          let row = null;
          for(let i=0; i < this_.tableData.length; i++){
             let id = this_.tableData[i].id;
             if(id == nodeId){
                row = this_.tableData[i];
                break;
             }
          }

          /*********************** 以下实现 result vis 布局图中点击节点,节点用黑圈高亮,左侧表格高亮并置顶(如果能)********************************/
          if(this_.tableRowClickNodeList.length > 0){
            if(this_.tableRowClickNodeList.indexOf(nodeId) != -1){ //在里面,说明已经点击过,去掉高亮并删掉id.
              this_.tableRowClickNodeList.splice(this_.tableRowClickNodeList.indexOf(nodeId), 1); //删除nodeId.
              this_.selectedRowList.splice(this_.selectedRowList.indexOf(row), 1); //row是对象,可以这样找其索引吗?是可以的,因为不是地址比较,而是对象的值比较.
              let css = {
                "stroke-dasharray":0,
                "stroke": "#fff",
                "stroke-width": 0
              };
              $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css(css); //清除.
              // this_.isHighLightCurrentRow = false; //表格高亮去掉.
              this_.hightLightCurRow(row, false); //表格失去高亮.
              this_.jBoxInstance.seeMoreJbox.close(); //关闭,seemore
            }
            else{ //不在里面,说明没有点击过,则往里面加id,并高亮.
              let css_ = {
                "stroke-dasharray":0,
                "stroke": "#fff",
                "stroke-width": 0
              };
              $("#" + this_.$store.state.resultsSearchView.svgId + " ." + this_.tableRowClickNodeList[0]).css(css_); //清除之前的高亮.
              // this_.isHighLightCurrentRow = false; //表格高亮去掉.
              this_.hightLightCurRow(this_.selectedRowList[0], false);
              this_.tableRowClickNodeList.splice(0, 1); //删除原来的nodeId,保证里面只有一个值,这样就只能单选了,将此句注释掉,则可多选.
              this_.selectedRowList.splice(0, 1);
              this_.tableRowClickNodeList.push(nodeId);
              this_.selectedRowList.push(row);
              let css = {
               "stroke-dasharray":0,
               "stroke": "black",
               "stroke-width": 3
              };
              $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css(css); //用黑圈圈起来.
               // this_.isHighLightCurrentRow = true; //表格高亮.
               this_.hightLightCurRow(row, true); //表格高亮.
               this_.localCurrentRow(row, index); //定位表格.
            }
          }
          else{ //空的,没有点击过,则直接加入id,并高亮.
             this_.tableRowClickNodeList.push(nodeId);
             this_.selectedRowList.push(row);
             let css = {
               "stroke-dasharray":0,
               "stroke": "black",
               "stroke-width": 3
              };
              $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css(css); //用黑圈圈起来.
               // this_.isHighLightCurrentRow = true; //表格高亮.
               this_.hightLightCurRow(row, true); //表格高亮.
               this_.localCurrentRow(row, index); //定位表格.
          }
           /*********************** 以上实现 result vis 布局图中点击节点,节点用黑圈高亮,左侧表格高亮并置顶(如果能)********************************/
      },            
      handleChange(val){
        console.log(val);
      },
      initIconMouseEvent(){ //鼠标悬浮提示信息.
         $('#result-vis-icon').jBox('Mouse', { // jBox在本文件中并没有引入,但是也能用(在mainView.vue中引入了).
          theme: 'TooltipDark',
          content: 'Search Result Subgraph', //'Click to check visualization of result'
         });
      },
      getRowDetail(row, event, column){ // row={"id": xx, ...},注意:同时注册表格的单元格+行点击事件,先执行单元个点击事件.
          let this_ = this;
          let nodeId = row.id; // 节点id. string类型.
         
          /******* 以下实现 result vis 布局图中点击节点,节点用黑圈高亮,左侧表格高亮并置顶(如果能)*********/
          console.log("row click event");
          if(this_.tableRowClickNodeList.length > 0){
            if(this_.tableRowClickNodeList.indexOf(nodeId) != -1){ //在里面,说明已经点击过,去掉高亮并删掉id.
              this_.tableRowClickNodeList.splice(this_.tableRowClickNodeList.indexOf(nodeId), 1); //删除nodeId.
              this_.selectedRowList.splice(this_.selectedRowList.indexOf(row), 1); //row是对象,可以这样找其索引吗?是可以的,因为不是地址比较,而是对象的值比较.
              let css = {
                "stroke-dasharray":0,
                "stroke": "#fff",
                "stroke-width": 0
              };
              $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css(css); //清除.
              // this_.isHighLightCurrentRow = false; //表格高亮去掉.
              this_.hightLightCurRow(row, false); //表格不高亮.             
            }
            else{ //不在里面,说明没有点击过,则往里面加id,并高亮.
              let css_ = {
                "stroke-dasharray":0,
                "stroke": "#fff",
                "stroke-width": 0
              };
              $("#" + this_.$store.state.resultsSearchView.svgId + " ." + this_.tableRowClickNodeList[0]).css(css_); //清除之前的高亮.
              // this_.isHighLightCurrentRow = false; //表格高亮去掉.
              this_.hightLightCurRow(this_.selectedRowList[0], false);
              this_.tableRowClickNodeList.splice(0, 1); //删除原来的nodeId,保证里面只有一个值,这样就只能单选了,将此句注释掉,则可多选.
              this_.selectedRowList.splice(0, 1);
              this_.tableRowClickNodeList.push(nodeId);
              this_.selectedRowList.push(row);
              let css = {
               "stroke-dasharray":0,
               "stroke": "black",
               "stroke-width": 3
              };
              $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css(css); //用黑圈圈起来.
               // this_.isHighLightCurrentRow = true; //表格高亮.
               this_.hightLightCurRow(row, true); //表格高亮.
               // this_.localCurrentRow(row, index); //定位表格.
            }
          }
          else{ //空的,没有点击过,则直接加入id,并高亮.
             this_.tableRowClickNodeList.push(nodeId);
             this_.selectedRowList.push(row);
             let css = {
               "stroke-dasharray":0,
               "stroke": "black",
               "stroke-width": 3
              };
              $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css(css); //用黑圈圈起来.
               // this_.isHighLightCurrentRow = true; //表格高亮.
               this_.hightLightCurRow(row, true); //表格高亮.
               // this_.localCurrentRow(row, index); //定位表格.
          }
          if(this_.isClickSeeMore){ //点击了see more,则恢复,并保持高亮.
            this_.isClickSeeMore = false;
            this_.tableRowClickNodeList.push(this_.tableRowClickTempNodeList[0]);
            // this_.tableRowClickTempNodeList.push(id); //保持只有一个id.
            this_.selectedRowList.push(this_.selectedTempRowList[0]); //将当前row数据存入里面.
            this_.hightLightCurRow(this_.selectedTempRowList[0], true); //表格高亮.
            let css = {
               "stroke-dasharray":0,
               "stroke": "black",
               "stroke-width": 3
            };
            $("#" + this_.$store.state.resultsSearchView.svgId + " ." + this_.tableRowClickTempNodeList[0]).css(css); //用黑圈圈起来.
          }
          
          else{
                       
          }
         /******* 以上实现 result vis 布局图中点击节点,节点用黑圈高亮,左侧表格高亮并置顶(如果能)**************/
      },
      handleMouseOver(row, column, cell, event){ //鼠标悬浮某一行. 如果是焦点所在行,则高亮焦点标签.        
        let this_ = this;
        let nodeId = row.id; // 节点id. string类型.
        $("#focusesbox ." + nodeId).css("border", "1px solid #2894FF"); //如果是焦点,则高亮焦点标签.
        let css = {
          "stroke-dasharray":0,
          "stroke": "black",
          "stroke-width": 3
        };
        $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css(css); //用黑圈圈起来.
      },
      handleMouseLeave(row, column, cell, event){ //鼠标离开某一行. 如果是焦点所在行,则恢复焦点标签.
        let this_ = this;
        let nodeId = row.id; // 节点id. string类型.
        $("#focusesbox ." + nodeId).css("border", "1px solid rgba(64,158,255,.2)"); //如果是焦点,则恢复焦点标签样式.
        let css = {
              "stroke-dasharray":0,
              "stroke": "#fff",
              "stroke-width": 0
        };
       $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css(css); //用黑圈圈起来.
       for(let i=0; i<this_.tableRowClickNodeList.length; i++){ //点击选中的节点高亮.
           let id = this_.tableRowClickNodeList[i];
           let css = {
             "stroke-dasharray":0,
             "stroke": "black",
             "stroke-width": 3
            };
            $("#" + this_.$store.state.resultsSearchView.svgId + " ." + id).css(css); //用黑圈圈起来.
       }
      },
      handleSortChange({ column, prop, order }){
        let this_ = this;
        // console.log("maotingyunlvscj column");console.log(column);
        $("#search-result-table .el-table__row" + " td:first-child").css("background-color", ""); //先擦干净.
        for(let i=0; i<this_.$store.state.resultsSearchView.focusStateList.length; i++){ //重新定位高亮.
          let nodeId = this_.$store.state.resultsSearchView.focusStateList[i]; //焦点节点.
          $("#search-result-table ." + nodeId + " td:first-child").css("background-color", this_.$store.state.resultsSearchView.focusColor); //选中该点作为焦点后,高亮.                                        
        }
      },
      cellClickEvent(row, column, cell, event){ //注意:同时注册表格的单元格+行点击事件,先执行单元个点击事件.
        let this_ = this;
        let key = column.label; //publications.
        if(this_.$store.state.infoSearchView.dbtables.indexOf(key) != -1){ //在里面.只有点击"see more..."才会进入执行.
          this_.isClickSeeMoreOut = true;
          let nodeId = '';
          let letterCalssList = ["context-menu-active", "current-row", "el-table__row"];//字母组成的类名,只要表格不改动.这个列表就不改动.                
          event.target.offsetParent.parentElement.classList.forEach(function(item, index){
            if(letterCalssList.indexOf(item) == -1){ //不在里面.
               nodeId = item;
            }
          });
          if(this_.tableRowClickTempNodeList.length > 0){
            this_.tableRowClickTempNodeList.pop(); //弹出.
            this_.selectedTempRowList.pop();
          }
          if(this_.tableRowClickNodeList.length > 0){ //行已经被高亮
            let id = this_.tableRowClickNodeList[0]; //只有一个.
            if(nodeId == id){ //被高亮的是当前行.
              this_.isClickSeeMore = true; //点击了 see more
              this_.tableRowClickTempNodeList.push(id); //保持只有一个id.
              this_.selectedTempRowList.push(this_.selectedRowList[0]); //将当前row数据存入里面.
            }
          }
          
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
                $(".result-table-see-more").html(allHtml); // 这个操作不会进入updated里面.插入直接渲染,因此在下面可以调用initSeeMore函数来注册事件.
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
      }
    },    
    mounted(){
        console.log("resultsSearch mounted");
        let this_ = this;            
        this_.clickResultVisInit(); // 在注册点击事件.  
        $.contextMenu({  // fixme:右键表格中的某行,选为焦点.
            selector: '#search-result-table .el-table__row',
            className: "focusSelectionMenuSearch", // 添加自定义类名称.  
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
                    // let row = null; // 节点的信息,对应表格中的一行.
                    // for(let i=0; i<this_.tableData.length; i++){ // 从表格数据中选出被点击节点对应的记录.
                    //    let obj = this_.tableData[i];
                    //    if(obj.id == nodeId){ // 如果id相同,则找到了.
                    //      row = obj;
                    //      break; // 直接跳出大循环,避免继续找下去.注意,一定可以找到,除非出错了.
                    //    }
                    // }
                    // // console.log("ccccccccccjjjjjjjjjjjjj row");console.log(row);
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
                    //                 }; 
                    
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
                    // if(this_.$store.state.resultsSearchView.isOpenResultVis){ //如果打开了result vis 弹窗.
                    //   $("#" + this_.$store.state.resultsSearchView.svgId + " ." + nodeId).css("fill", this_.$store.state.resultsSearchView.focusColor); //删除焦点后,取消高亮,恢复.
                    // }
                    // this_.$store.state.resultsSearchView.focusStateList.push(nodeId); //将该点的id记录在案. 
                   
                  }
                 if(key == "cut"){ // 取消该点作为焦点.
                    // console.log("cut nodeId");console.log(nodeId);                    
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
            id: "jBoxInterestAttributesSearch", // 弹出兴趣属性选择框.
            addClass: "jBoxInterestAttributesSearchClass",  // 添加类型,这个功能很棒啊!
            attach: '.focusSelectionMenuSearch .addToTheFocusSet',
            width: 300,              // Maximal width
            height: 150,             // Maximal height 
            title: 'Attributes of Interest',
            // fixed:true,
            overlay: false,
            fixed: false,
            adjustTracker: true,
            zIndex: 1005, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
            createOnInit: true,
            content: $("#interest-attributes-search-result"),  // jQuery('#jBox-content') 
            draggable: true,
            repositionOnOpen: false,
            repositionOnContent: true,
            target: $('.focusSelectionMenuSearch .addToTheFocusSet'),//$('#filtered-subgraph-nav-icons-setting'),
            offset: {x: -135, y: 100}, // {x: -135, y: 155},
            // 以下是弹窗事件,这些功能真的非常优秀!
            onOpen: function(){                   
                this_.jBoxInstance.interestAttributes.position({
                   target: $('.focusSelectionMenuSearch .addToTheFocusSet')//$('#filtered-subgraph-nav-icons-setting') //注意,这样保证:当 jBoxInstance.resultVis 移动后,重新打开layoutSetting,layoutSetting能够跟着jBoxInstance.resultVis走.           
                });
                bus.$emit("attributesOfInterestPanelUpdate", true); // 提醒 "兴趣属性选择" 面板更新勾选列表.
            },
            onCloseComplete: function(){                     
              
            }
        }); 
        
    },
    updated(){
      console.log("resultsSearchView updated");
      let this_ = this;
      if(this_.totalTable > 0){
         // this_.iconTooltip(); // 鼠标tooltip
         this_.initIconMouseEvent(); //鼠标悬浮提示信息.
         // this_.clickResultVisInit(); // 在updated中注册点击事件.
         this_.insertSeeMore(); // 当更新完后,在可以点击查看更多的cell里面插入"See More..."提示.
         this_.jBoxInstance.seeMoreJbox = new jBox('Modal', {
                  //todo: 添加唯一的id就会出现问题.
                  addClass: "jBoxSeeMoreOfNodeResult",  // 添加类型,这个功能很棒啊!
                  attach: "#resultssearch ." + this_.ableClickClassName, //指定在#resultssearch内部,避免冲突.
                  width: 400,              // Maximal width 
                  maxHeight: 800,              
                  title: "Publications",
                  overlay: false,
                  zIndex: 1005, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
                  createOnInit: true,
                  content: $(".result-table-see-more"),  //唯一,避免冲突.
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
         if($(".jBoxSeeMoreOfNodeResult").length > 1){ // 这样可以避免出现多个
            $(".jBoxSeeMoreOfNodeResult").first().remove(); // .first()
         }  
         
      }
      if(this_.$store.state.resultsSearchView.refreshTablePageFlagForClickNode){ //信息不在当前页,刷新后进入执行定位操作.
          this_.$store.state.resultsSearchView.refreshTablePageFlagForClickNode = false; //保证执行一次.
          let nodeId = this_.$store.state.resultsSearchView.clickNodeId; //节点id.
          
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
          // console.log("this_.$store.state.resultsSearchView.tableRowSortList");
          // console.log(this_.$store.state.resultsSearchView.tableRowSortList);
          let index = -1;
          if(this_.$store.state.resultsSearchView.tableRowSortList.indexOf(nodeId) != -1){ //在里面,在当前页面.
             index = this_.$store.state.resultsSearchView.tableRowSortList.indexOf(nodeId) + 1;
             this_.localTablePosInClickEvent(nodeId, index);
          }
      }      
    },
    beforeDestroy(){
       let this_ = this;
       bus.$off('sendResultsSearch'); // 注销事件.
       bus.$off("tabelDataVisible"); 
       bus.$off("focusSetClear");       
       bus.$off("sendLocalTablePosInClickEvent");
       bus.$off("sendCurrentPage");
       bus.$off("sendDeleteSearchTableFlag");
    }
  }
</script>
<style>

.nav-table-results-search .nav-table-results-search-div{
  list-style:none;        
  float:left;
  margin:0px 2px 0px 4px; 
  /*display:inline-block;*/
  vertical-align:middle;
}
.nav-table-results-search{
  padding:0px 0px 0px 0px;
  margin: 1px 0px 0px 0px; /*避免ul内部的div偏离*/  
}
.result-table-see-more{
  display: none;
  max-height: 800px; 
  max-width: 700px;
  padding:2px 2px 2px 4px;
  overflow: scroll;
}
#result-vis-icon{
   color: "black";
}
#interest-attributes-search-result{
  display: none;
}

/* 以下是论文的样式 */
.result-table-see-more .abstract {
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
.result-table-see-more .author-number{
  margin:2px 0px 8px 0px;
  border-style: solid;
  border-color:#E0E0E0;
  border-top-width: 0px;
  border-right-width: 0px;
  border-bottom-width: 1px;
  border-left-width: 0px;
  font-size: 12px;
}
.result-table-see-more .author-number span{
  width:100%;
  border-spacing: 2px 2px;
  font: normal normal normal normal 12px;
  font-weight: 600;  
}
.result-table-see-more #author{
    color: #069;
    border-spacing: 2px 2px;
    font: italic normal 300 normal 12px / 20px Lato, sans-serif;
}
.result-table-see-more #venue{
    border-spacing: 2px 2px;
    font: normal normal normal normal 12px / 20px Lato, sans-serif;
}
.result-table-see-more h5{
   color: #069;
}
.result-table-see-more .content{
  width: 489px;
  margin: 1px 1px 1px 1px;

}
#info-paper-box{
  max-height: 700px;
  max-width: 500px;
  overflow: scroll;
}

.result-table-see-more .collapsible {
  color: #444;
  cursor: pointer;
  border: none;
  text-align: left;
  outline: none;
  font-size: 15px;
}

.result-table-see-more .active .collapsible-icon-name, .result-table-see-more .collapsible .collapsible-icon-name:hover {
  background-color: #069;
}


.result-table-see-more .collapsible-content {
  display: none;
  overflow: hidden;
  background-color: #f1f1f1;
}
.result-table-see-more .each-one{
 border-style: solid;
 border-color:#E0E0E0;
 border-top-width: 0px;
 border-right-width: 0px;
 border-bottom-width: 1px;
 border-left-width: 0px;
}


#result-vis-box #result-vis-icon-div {
    text-decoration: none;
    color: #000;
    background: #ddd;
    display: inline-block;
    width: 25px;
    height: 25px;
    text-align: center;
    line-height: 25px;

    border-top-left-radius:0px;
    border-top-right-radius:0px; 
    border-bottom-left-radius:0px;
    border-bottom-right-radius:0px;  
}
#result-vis-icon{
  vertical-align: middle;
}
.cell-see-more {
   -webkit-margin-before: 0em;
    -webkit-margin-after: 0em;
    -webkit-margin-start: 0px;
    -webkit-margin-end: 0px;
}
#resultssearch .el-collapse-item__header{
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
  margin:0px 0px 2px 0px;
}

#resultssearch .el-collapse-item__wrap{

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
  /*margin:0px 0px 2px 0px;*/
}
#resultssearch{
   /*border-color:#ddd;
  border-style: solid;
  border-top-width: 1px;
  border-right-width: 1px;
  border-bottom-width: 1px;
  border-left-width: 1px;*/
}
#search-result-table{
  border-color:#ddd;
  border-style: solid;
  border-top-width: 0px;
  border-right-width: 0px;
  border-bottom-width: 0px;
  border-left-width: 0px;
}
#subgraph-ul-li{
  float: right;
  margin:0px 5px 0px 0px;
}
#search-table-num-records{
    padding: 8px 0px 0px 0px;
}

</style>