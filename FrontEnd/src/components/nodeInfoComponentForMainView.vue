<template>
  <div id="nodeinfobox">
    <div id="node-info-box">
      <el-table
      :data="tableData"
      
      :height="height"
      :row-class-name="tableRowClassName"
      :cell-class-name="tableCellClassName"
      empty-text="null"    
      style="width: 100%"
      @cell-mouse-enter="handleMouseEnter"
      @cell-mouse-leave="handleMouseLeave"
      @row-click="getRowDetail"
      ><!---->
      <el-table-column
        prop="key"       
        label="key"        
        :width="widthKey"
        show-overflow-tooltip 
      >
      </el-table-column>
      <el-table-column
        prop="value"      
        label="value" 

        :width="widthValue"      
        filter-placement>
      </el-table-column>
      </el-table>
    </div>
     
     <div class="nodeinfo-see-more-in-mianview">      
     </div> <!--节点信息,查看更多-->
  </div>
</template>

<script>
  import {vueFlaskRouterConfig} from '../vueFlaskRouterConfig'
  import bus from '../eventbus.js' // 事件总线.
  import $ from 'jquery'
  import axios from 'axios' // 用于AJAX请求  
  import {jBox} from "../../static/js/jBox.js"  
  import "../../static/js/jquery.contextMenu.js"
  import "../../static/js/jquery.ui.position.js"

  export default {
    data() {
      return {
        tableData: null,
        widthKey: 0,
        widthValue:150,
        height:180,

        xOffset: 0,  // 悬浮历史图片弹出的信息框的位置.
        yOffset: 40, 

        unitWidth: 10, // 用于自适应字段长度.表示1个字符对应15px.

        overFlowLen: 18, // 表格单元格中字符串的溢出长度,目前是18,如果宽度被调整,则需要对应地调整.
        // tableRowClassName:"maotingyun"
        // tablesDbList:["node", "edge", "publications", "interests"],
        // curClickField:"publictions",
        ableClickClassName: "clickSeeMore", // 可以点击的行的类名称.
        // jboxTitle: "See More Of Node",
        nodeIdName:{}, // {id:x, name:x}用于保存点击的节点信息.
        flagOfTableDataChange: false, // 表格数据发生变化标志位.

        seeMoreKeyValObj: {}, // 用于保存可以点击查看See More的字段的值, e.g. {publications:"123;345;223"}
        
        seeMoreJbox:null, // 查看更多弹窗实例.
      }
    },
    props:[
     "targetoffset",
     "targetselector"
     
    ],
    created(){
      console.log("nodeInfo.vue created");
      let this_ = this;
      bus.$on("sendClearAttriExplorState", function(state){
        if(state){
          if(this_.tableData){
            this_.tableData = null;
            this_.seeMoreJbox.close();
          }
          
        }
      });     
    },
    watch:{
      tableData: function(curVal, oldVal){
        let this_ = this;
        this_.flagOfTableDataChange = true;
      }
    },
    methods:{
      insertSeeMore(){ // 插入See More提示.
        let this_ = this;
        let keyList = Object.keys(this_.seeMoreKeyValObj); // [x, x, ...]
        // console.log("this_.seeMoreKeyValObj");console.log(this_.seeMoreKeyValObj);
        for(let i=0; i<keyList.length; i++){
          let className = keyList[i]; // 字段名,也是calss name.
          let html = "<p class='cell-see-more'>See More...</p>";
          $("#nodeinfobox #node-info-box ." + className + " .value .cell").html(html); //用nodeinfobox来限定在哪里插入 see more.
        }        
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
      initSeeMore(){
        let coll = $(".nodeinfo-see-more-in-mianview .collapsible");    
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
      tableCellClassName({row, column, rowIndex, columnIndex}){
        
        return column.label;
      },
      tableRowClassName({row, rowIndex}){
        let this_ = this;
        // console.log("tableRowClassName");
        let fieldName = row.key;
        let className  = this_.ableClickClassName + " " + fieldName; // 如果在里头则可以点击查看更多.
        if(this_.$store.state.infoSearchView.dbtables.indexOf(fieldName) != -1){ // 如果在里面.
           return className;
        }
        else{
          return fieldName;
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
      highLightAttriVal(origString, matchedPhrase){ // 用origString的每个词去匹配matchedPhrase.             
              const origStringList = origString.split(/,|，|&|\s+/);
              let newKeyWords = "";
              for(let i=0; i<origStringList.length; i++){
                if(origStringList[i] != ""){
                   newKeyWords += origStringList[i] + " "
                }
              }
              let keywordString = newKeyWords.trim();

              const keywords = keywordString.split(/\s/); // 以空格分隔.

              // equivalent to: /(cake|pie|cookies)/g
              const pattern = new RegExp(`(${keywords.join('|')})`, 'g');
              const result = matchedPhrase.replace(pattern, match => `<span class="highlight">${match}</span>`);
              return result;
      },
      highlightMatchedText(innerHTML, text) { // 高亮匹配的文本.                         
        let index = innerHTML.indexOf(text);
        let isDisplayFlag = $(".el-tooltip__popper").attr("aria-hidden");
        // console.log("isDisplayFlag");console.log(isDisplayFlag);
        if (index >= 0) {
           innerHTML = innerHTML.substring(0,index) + "<span class='highlight'>" + innerHTML.substring(index,index+text.length) + "</span>" + innerHTML.substring(index + text.length);
           $(".el-tooltip__popper").html(innerHTML);
        }
      },
      handleMouseEnter(row, column, cell, e){
        let this_ = this;
        let text = "of";
        let innerHTML = row.value;
        let field = row.key; // 键
        // console.log("row");console.log(row);  
        // console.log("column");console.log(column.label);
        // console.log("cell");console.log(cell);
        // console.log("event");console.log(e);
         
        let isValue = column.label;        
        // attrValue:"XXX, VVV, Nnnn", // text类型的属性值
        // curNodeId:"13424", // 当前节点的id
        // curNodeArr:field // 所属的属性(字段)
        let lenInnerHTML = innerHTML.length; // 字符串长度.
        let dynamicConditionExploreKeyList = Object.keys(this_.$store.state.mainViewGraph.dynamicConditionExploreObj); // dynamicConditionExploreKeyList=[id0, id1, id2]
        if(dynamicConditionExploreKeyList.length == 0){ // 如果为空.说明还没有开始属性探索.
            if(isValue == "value" && lenInnerHTML > this_.overFlowLen){ // lenInnerHTML > 18说明内容溢出.
                let mousePos = this_.mousePosition(e);
                let  xOffset = this_.xOffset;
                let  yOffset = this_.yOffset;
                $(".detail-info-box-mouse-over").css("display","block").css("position","absolute")
                .css("top",(mousePos.y - yOffset) + "px")
                .css("left",(mousePos.x + xOffset) + "px");
                if(this_.$store.state.infoSearchView.dbtables.indexOf(field) != -1){ // 在里面
                   let newHtml = "<p>%s</p>";
                   let newInnerHTML = this_.sprintf(newHtml, "Click to see more!");
                   $(".detail-info-box-mouse-over").html(newInnerHTML);
                }
                else{ // 不在里面.
                   $(".detail-info-box-mouse-over").html(innerHTML);
                }
                
            }
            if(isValue == "value" && this_.$store.state.infoSearchView.dbtables.indexOf(field) != -1 && lenInnerHTML <=this_.overFlowLen){ // 在里面
                  let mousePos = this_.mousePosition(e);
                  let  xOffset = this_.xOffset;
                  let  yOffset = this_.yOffset;
                  $(".detail-info-box-mouse-over").css("display","block").css("position","absolute")
                    .css("top",(mousePos.y - yOffset) + "px")
                    .css("left",(mousePos.x + xOffset) + "px");
                  let newHtml = "<p>%s</p>";
                  let newInnerHTML = this_.sprintf(newHtml, "Click to see more!");
                  $(".detail-info-box-mouse-over").html(newInnerHTML);
            }             
        }
        else{ // 开始属性探索了.
          let strsObj = {}; // {field:x, ...},这个是条件值对应的field-value对.
          
          let fieldsListSet =  new Set();
          dynamicConditionExploreKeyList.forEach(function(item, index){ // key
             let conditionsList = this_.$store.state.mainViewGraph.dynamicConditionExploreObj[item]; // conditionsList==[{}, {}, ...]
             for(let i=0; i<conditionsList.length; i++){
                let tempObj = conditionsList[i]; // {}
                let key = tempObj.curNodeArr; // 字段.
                let val = tempObj.attrValue; // 字符串.
                if(strsObj[key]){
                  strsObj[key] = strsObj[key] + " " + val;
                  // console.log("val");console.log(val);
                }else{
                  strsObj[key] = val;
                }
                
                fieldsListSet.add(key);
             }
             
          });
          // console.log("strsObj");console.log(strsObj);
          let fieldsList = Array.from(fieldsListSet); // 集合转化成列表.
          if(isValue == "value" && lenInnerHTML > this_.overFlowLen){ // 只有是"value"时,有悬浮框.                 
              
              let mousePos = this_.mousePosition(e);
              let  xOffset = this_.xOffset;
              let  yOffset = this_.yOffset;
              $(".detail-info-box-mouse-over").css("display","block").css("position","absolute")
              .css("top",(mousePos.y - yOffset) + "px")
              .css("left",(mousePos.x + xOffset) + "px");
              let resultHtml = ""; //匹配后的条件.
              if(fieldsList.indexOf(field) != -1){ // 属于条件对应的属性.
                let origString = strsObj[field]; // origString是条件 field是鼠标悬浮处对应的字段.              
                resultHtml = this_.highLightAttriVal(origString, innerHTML); // 被高亮的text.
              }
              else{
                resultHtml = innerHTML; //其他字段的溢出值也显示.
              }

              if(this_.$store.state.infoSearchView.dbtables.indexOf(field) != -1){ // 在里面
                   let newHtml = "<p>%s</p>";
                   let newInnerHTML = this_.sprintf(newHtml, "Click to see more!") + resultHtml;
                   $(".detail-info-box-mouse-over").html(newInnerHTML);
              }
              else{ // 不在里面.
                 $(".detail-info-box-mouse-over").html(resultHtml);
              }
          }
          
          if(isValue == "value" && fieldsList.indexOf(field) == -1 && this_.$store.state.infoSearchView.dbtables.indexOf(field) != -1){ // 在里面
             let mousePos = this_.mousePosition(e);
             let  xOffset = this_.xOffset;
             let  yOffset = this_.yOffset;
             $(".detail-info-box-mouse-over").css("display","block").css("position","absolute")
                .css("top",(mousePos.y - yOffset) + "px")
                .css("left",(mousePos.x + xOffset) + "px");
             let newHtml = "<p>%s</p>";
             let newInnerHTML = this_.sprintf(newHtml, "Click to see more!");
             $(".detail-info-box-mouse-over").html(newInnerHTML);
          }
        }
        
        
        // this_.highlightMatchedText(innerHTML, text);
      },
      handleMouseLeave(row, column, cell, e){
        let this_ = this;
        let isValue = column.label;
        if(isValue == "value"){
          $(".detail-info-box-mouse-over").css("display","none"); // class=detail-info-box-mouse-over的div在mainView.vue中.这样做会加强组件间的耦合性.
        }
      },
      getRowDetail(row, event, column){       
        let this_ = this;
        let key = row.key;
        let value = null;
        if(this_.$store.state.infoSearchView.dbtables.indexOf(key) != -1){ // 在里面.
           value = this_.seeMoreKeyValObj[key];
        }
        else{
           value = row.value;
        }  
        let keysType = this_.$store.state.fields.fieldsType; // 所有字段及其类型.{字段:类型,...}
        // if(keysType[key] == "text" && this_.$store.state.infoSearchView.dbtables.indexOf(key) == -1) {     
        // // if(key == 'id'){
        //   bus.$emit('sendNodeId', value); //sendNodeId事件,在infoSearch.vue中监听.
        // }    
        
        if(this_.$store.state.infoSearchView.dbtables.indexOf(key) != -1){ // 在里面,这样保证字段有对应的数据库表.
          // todo:处理分号,向后台请求数据.          
          let dbName = this_.$store.state.selection.selectiondb; // 数据库的名称.
          let tableName = key;
          let param = { "dbName": dbName, // DB name
                        "value": value, // value="id1;id2;id3;id4"
                        "tableName": tableName}; // tableName="publications",刚好是字段的名称.
          
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
                let allHtml = this_.sprintf(tempHtml, this_.nodeIdName.name, String(totalNum));     
                for(let i=0; i<orderId.length; i++){
                  let id = orderId[i];
                  let obj = data[id];
                  let title = obj.title;
                  let authors = obj.authors;
                  let public_venue = obj.public_venue;
                  let year = obj.year;
                  let abstract = obj.abstract;
                  let html = '<div class="each-one"><h5 class="content">%s. %s</h5><p class="content"><em id="author">%s</em></p><p class="content"><strong id="venue">%s(%s)</strong></p><span class="collapsible"><img src="data:image/gif;base64,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"><span class="collapsible-icon-name">Abstract</span></span><div class="collapsible-content"><div class="abstract"><div class="abstract-content">%s</div></div></div></div>';
                  let newHtml = this_.sprintf(html, String(i+1), title, authors, public_venue, year, abstract);
                  allHtml += newHtml;
                }
                $(".nodeinfo-see-more-in-mianview").html(allHtml); // 这个操作不会进入updated里面.插入直接渲染,因此在下面可以调用initSeeMore函数来注册事件.
                this_.initSeeMore();
              }           
              
          })
          .catch((error) => {            
            console.error(error);
          });
          
          
        }
        
        
      },
      getMaxOfArray(numArray) {
        return Math.max.apply(null, numArray);
      },
    },
    mounted(){       
      let this_ = this; // VueComponent
      console.log("nodeInfo.vue mounted");
      bus.$on('sendNodeInfo', function (data) {  // 注意:bus.$on()只是放在mounted(){}中,而且其回调函数只有用箭头函数时,才能更新数据,如果是function(){}则不能更新数据.            
            // 对于function(){}来说,里面的this是bus. 而对()=>{}来说,this是vuecomponent.             
            this_.tableData = data;
            let fieldList = [];
            let nodeIdName = {}; // {id:x, name:x}, 用于后面See More.
            let seeMoreKeyValObj = {}; // e.g. {publications:"123;345;223"}
            for(let i=0; i<data.length; i++){
              let obj = data[i]; // {"key": "id", "value": "12345"}
              let key = obj.key; // 取出字段.
              fieldList.push(key.length);

              if(key == "name"){
                 nodeIdName.name = obj.value;
              }
              if(key == "id"){
                nodeIdName.id = obj.value;
              }

              if(this_.$store.state.infoSearchView.dbtables.indexOf(key) != -1){ // 在里面.
                seeMoreKeyValObj[key] = obj.value; // {publications:"123;345;223"}
              }
            }
            // console.log("seeMoreKeyValObj");console.log(seeMoreKeyValObj);
            let maxLenField = this_.getMaxOfArray(fieldList); // 字段的最大长度.
            this_.widthKey = maxLenField * this_.unitWidth;
            this_.nodeIdName = nodeIdName;
            this_.seeMoreKeyValObj = seeMoreKeyValObj;

        }        
      );      

    },
    updated(){
      console.log("nodeInfoView updated");
      let this_ = this;      
      if(this_.tableData.length > 0 && this_.flagOfTableDataChange){
          this_.flagOfTableDataChange = false;
          this_.insertSeeMore(); // 当更新完后,在可以点击查看更多的cell里面插入"See More..."提示.        
          this_.seeMoreJbox = new jBox('Modal', {
                  // id: "jBoxSeeMoreOfNodeId", // todo: 添加唯一的id就会出现问题.
                  addClass: "jBoxSeeMoreOfNode",  // 添加类型,这个功能很棒啊!
                  attach: "#nodeinfobox ." + this_.ableClickClassName, //指定在#nodeinfobox中,避免冲突.
                  width: 400,              // Maximal width 
                  maxHeight: 800,              
                  title: "Publications",
                  overlay: false,
                  zIndex: 1005, // fixme:注意多个jbox实例之间zIndex的值决定与最后一个实例.
                  createOnInit: true,
                  content: $(".nodeinfo-see-more-in-mianview"),  //.nodeinfo-see-more-in-mianview唯一.
                  draggable: true,
                  repositionOnOpen: false, //false
                  repositionOnContent: true,
                  // pointer: true,
                  // target: $(this_.targetselector), //$("#main-view-layout-setting") $(this_.targetselector), //targetselector targetoffset
                  // offset: this_.targetoffset, // {x: -186, y: 80} this_.targetoffset,//{x: 95, y: 145},
                  position:this_.$store.state.jboxPositionSet.topRightSide,
                  // 以下是弹窗事件,这些功能真的非常优秀!
                  onOpen: function(){ 
                     // this_.seeMoreJbox.position({
                     //    target: $(this_.targetselector) //$('.mian-view-item-info')
                             
                     // });                    
                     let css = {
                            "stroke-dasharray":0,
                            "stroke": "#fff",
                            "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
                      };
                      $("#mainsvg .nodecircle").css(css); // 先擦干净

                      // 如果已经开始属性探索,则高亮匹配上的节点.
                      // let attributesExplorNodeHighlight = this_.$store.state.mainViewGraph.attributesExplorNodeHighlight;
                      // if(attributesExplorNodeHighlight.length > 0){ 
                      //      attributesExplorNodeHighlight.forEach(function(item, index){
                                  
                      //        let css = {
                      //           "stroke-dasharray":0,
                      //           "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.clickMatchNodeAttri,
                      //           "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                      //         };
                      //         $("#mainsvg #" + item).css(css); // 点击节点,用黑色圆圈圈起来.
                      //     });
                      // }

                      // 用黑圈圈定对应的节点.
                      let cssNode = {
                          "stroke-dasharray":0,
                          "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.clickCheckNodeInfo,
                          "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                      };
                      let nodeId = this_.$store.state.mainViewGraph.clickNode2GetId;
                      $("#mainsvg #" + nodeId).css(cssNode); // 对应节点,用黑圈圈起来.
                  },
                  onCloseComplete: function(){ // todo: 发生一个很诡异的现象: 会执行多次onCloseComplete.明明see more框还开着确说已经关闭了,最后在mainView中使用jquery的css方法查看diaplay == block 或none来判断是否关闭.
                    
                     // this_.$store.state.nodeInfoView.isOpenSeeMoreFlag = false; // 已经关闭.
                     if(this_.$store.state.mainViewGraph.isOpenCheckNodeDetailFlag){ // 节点细节信息框还开着.                         
                         let css = {
                            "stroke-dasharray":0,
                            "stroke": "#fff",
                            "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
                          };
                          $("#mainsvg .nodecircle").css(css); // 先擦干净

                          // 如果已经开始属性探索,则高亮匹配上的节点.
                          // let attributesExplorNodeHighlight = this_.$store.state.mainViewGraph.attributesExplorNodeHighlight;
                          // if(attributesExplorNodeHighlight.length > 0){ 
                          //      attributesExplorNodeHighlight.forEach(function(item, index){
                                      
                          //            let css = {
                          //               "stroke-dasharray":0,
                          //               "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.clickMatchNodeAttri,
                          //               "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                          //             };
                          //             $("#mainsvg #" + item).css(css); // 点击节点,用黑色圆圈圈起来.
                          //     });
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
                     else{ // 节点细节信息框关闭了.
                        let css = {
                          "stroke-dasharray":0,
                          "stroke": "#fff",
                          "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidthNull
                        };
                        $("#mainsvg .nodecircle").css(css); // 先擦干净.

                        // 如果已经开始属性探索,则高亮匹配上的节点.
                        // let attributesExplorNodeHighlight = this_.$store.state.mainViewGraph.attributesExplorNodeHighlight;
                        // if(attributesExplorNodeHighlight.length > 0){ 
                        //      attributesExplorNodeHighlight.forEach(function(item, index){
                                    
                        //        let css = {
                        //           "stroke-dasharray":0,
                        //           "stroke": this_.$store.state.mainViewGraph.highlightColorSheet.clickMatchNodeAttri,
                        //           "stroke-width": this_.$store.state.mainViewGraph.highlightColorSheet.strokeWidth
                        //         };
                        //         $("#mainsvg #" + item).css(css); // 点击节点,用黑色圆圈圈起来.
                        //     });
                        // }
                     }
                  }
          });
          if($(".jBoxSeeMoreOfNode").length > 1){ // 这样可以避免出现多个id=jBoxSeeMoreOfNodeId的div.
            $(".jBoxSeeMoreOfNode").first().remove(); // .first()
          }   
                
      }      
      
    },
    beforeDestroy () {
       bus.$off('sendNodeInfo');  // 由于bus.on()不会自己注销,需要bus.$off()来注销,这样可以解决多次触发的问题.
       bus.$off("sendClearAttriExplorState");
    },
  }
</script>

<style>
    /*@import "../../static/css/jBox.css";
    @import "../../static/css/jquery.contextMenu.css";*/
  .highlight {
    background-color: yellow;
  }  
  .cell-see-more{
    color:#069;
  }
  #nodeinfobox .el-table .cell, #nodeinfobox .el-table th div{
    padding-right: 10px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .nodeinfo-see-more-in-mianview {
    display: none;
    max-height: 800px; 
    max-width: 700px;
    padding:2px 2px 2px 4px;
    overflow: scroll;
  }
  
/* 以下是论文的样式 */
.nodeinfo-see-more-in-mianview .abstract {
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
.nodeinfo-see-more-in-mianview .author-number{
  margin:2px 0px 8px 0px;
  border-style: solid;
  border-color:#E0E0E0;
  border-top-width: 0px;
  border-right-width: 0px;
  border-bottom-width: 1px;
  border-left-width: 0px;
}
.nodeinfo-see-more-in-mianview .author-number span{
  width:100%;
  border-spacing: 2px 2px;
  font: normal normal normal normal 14px;
  
}
.nodeinfo-see-more-in-mianview #author{
    color: #069;
    border-spacing: 2px 2px;
    font: italic normal 300 normal 12px / 20px Lato, sans-serif;
}
.nodeinfo-see-more-in-mianview #venue{
    border-spacing: 2px 2px;
    font: normal normal normal normal 12px / 20px Lato, sans-serif;
}
.nodeinfo-see-more-in-mianview h5{
   color: #069;
}
.nodeinfo-see-more-in-mianview .content{
  width: 489px;
  margin: 1px 1px 1px 1px;

}
#info-paper-box{
  max-height: 700px;
  max-width: 500px;
  overflow: scroll;
}

.nodeinfo-see-more-in-mianview .collapsible {
  color: #444;
  cursor: pointer;
  border: none;
  text-align: left;
  outline: none;
  font-size: 15px;
}

.nodeinfo-see-more-in-mianview .active .collapsible-icon-name, .nodeinfo-see-more-in-mianview .collapsible .collapsible-icon-name:hover {
  background-color: #069;
}


.nodeinfo-see-more-in-mianview .collapsible-content {
  display: none;
  overflow: hidden;
  background-color: #f1f1f1;
}
.nodeinfo-see-more-in-mianview .each-one{
 border-style: solid;
 border-color:#E0E0E0;
 border-top-width: 0px;
 border-right-width: 0px;
 border-bottom-width: 1px;
 border-left-width: 0px;
}
.cell-see-more {
   -webkit-margin-before: 0em;
    -webkit-margin-after: 0em;
    -webkit-margin-start: 0px;
    -webkit-margin-end: 0px;
}
#node-info-box thead th{
  padding: 0px 0px 0px 0px;
}
#node-info-box .el-table__body .el-table__row{
  font-size: 13px;
  font-weight: 500;
}
</style>