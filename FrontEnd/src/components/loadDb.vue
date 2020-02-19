<template>
　　<div id="load-db-view"> 
  　　<el-form :inline="true" class="db-select-form">
          <el-form-item v-loading="loadingDbFlag" label="">  <!--选择数据库框-->          
            <el-select 
            v-model="selectiondb" 
            filterable
            @visible-change="dropDownBoxVisible" 
            placeholder="Select Dataset">
                <el-option
                    v-for="(item, index) in dboptions"
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                </el-option>
            </el-select>
          </el-form-item>
          
      </el-form>
  </div>　　 
</template>

<script>
  import axios from 'axios' // 用于AJAX请求
  import * as d3 from '../../static/js/d3.v4.min.js'
  import $ from 'jquery'
  import {vueFlaskRouterConfig, searchFlag} from '../vueFlaskRouterConfig'
  import bus from '../eventbus.js' // 事件总线.

  export default {
	data(){
	　　　return {
	    　loadingDbFlag: false, // 加载数据库标志量.
	     // loadingFlag: false, //基本字段 + 关键词框加载标志.
	     selectiondb: '', // 选择数据库v-model绑定属性.
	     dboptions:[], // 数据库名称存放.
	     dbLoadedFlag:{}, // 数据库加载完毕标志位.只有数据库加载完毕,才能请求对应的DOI子图.
	     histClickFlag: [false], // 用于记录是否点击了历史图片.[true]表示点击了,写成数组是为了用指针.
       stopwordsObj: null, //存放停用词的对象.
	　　 }
	},
	watch:{
	  selectiondb: function(curVal, oldVal){ // 选择数据库/切换数据库
        let this_ = this;
        this_.$store.state.selection.selectiondb = curVal; // 数据库名称更新.
        this_.$store.state.mainViewGraph.d3EventTransform = {};
        bus.$emit("sendClearNodeHighLighting", true); //渲染热力图.
        bus.$emit("sendRankingDefaultMethod", curVal); // 将ranking method 默认成API.
        if(this_.stopwordsObj){ // 非null
          let stopWords = this_.stopwordsObj; //停用词对象.
          let arrCommonStopWords = stopWords.commonStopWords; // 通用停用词.              
          let obj = stopWords.customStopWords; // 自定义停用词,是一个对象{dbname:[], ...}        
          let arrCustomStopWords = obj[curVal]; // 获得当前数据库对应的自定义停用词.         
          this_.$store.state.mainViewGraph.stopWords = arrCommonStopWords.concat(arrCustomStopWords)// 合并获得停用词集.         
        }
        else{ // null,则请求
          let path = vueFlaskRouterConfig.infoSearchForDbSelection;
          axios.get(path) // 用get的速度大于用post.
          .then((res) => {
              // this_.loadingDbFlag = false;                
              let data = res.data; // 获得指定数据库表格中的字段.            
              this_.dboptions = data.dbname; // [{}, ...] 
              // a.slice(0,-3) 
              for(let i=0; i<this_.dboptions.length; i++){
                 let dbName = this_.dboptions[i].label;
                 let key_ = dbName.slice(0,-3); // 这样做是为了去掉.db后缀,因为键不能带点.
                 this_.dbLoadedFlag[key_] = false;  // {dbname1: false, ...} 表示对应的数据库没有加载.
              } 
              
              this_.$store.state.attrNode.discardfield = data.discardfield; // 焦点选择时,应该丢弃的属性. [x, x, ...]
              this_.$store.state.attrNode.fullCompatibilityAtrr = data.fullCompatibilityAttr; // [x, x, ...] 用于mainView的匹配函数中,用于判断字段是否要上下兼容,适用于属性值比较长的属性,比如institution.
              // console.log("this_.$store.state.attrNode.discardfield");console.log(this_.$store.state.attrNode.discardfield);
              // console.log("this_.$store.state.attrNode.fullCompatibilityAtrr");console.log(this_.$store.state.attrNode.fullCompatibilityAtrr);
              this_.stopwordsObj = data.stopword; //存放停用词,停用词json文件在后台. 
              let stopWords = this_.stopwordsObj; //停用词对象.
              let arrCommonStopWords = stopWords.commonStopWords; // 通用停用词.              
              let obj = stopWords.customStopWords; // 自定义停用词,是一个对象{dbname:[], ...}        
              let arrCustomStopWords = obj[curVal]; // 获得当前数据库对应的自定义停用词.         
              this_.$store.state.mainViewGraph.stopWords = arrCommonStopWords.concat(arrCustomStopWords)// 合并获得停用词集.                     
                              
            })
          .catch((error) => {            
            console.error(error);
          });
        }             
        
        let histClickFlag = this_.histClickFlag[0]; // 是否点击了历史图片.
        
        if(!histClickFlag){ // 没有点击过历史图片, 直接切换数据库.
            if(curVal != "" && oldVal != ""){ // 不同数据库间的切换.              
              let labelsClear = true; // 标签清零
              bus.$emit("focusSetClear", labelsClear);  // 发送状态到focusSetView.vue,让标签清零.
              let settings = this_.onReset();  // 获得默认值.
              bus.$emit("Settings", settings); // 发送保存的settings数据到Settings控制面板.
            }
        }
        else{ // 点击了历史图片,自动切换数据库.
          this_.histClickFlag.pop();
          this_.histClickFlag.push(false);
          console.log("this_.histClickFlag.push(false)");          
        }
        $("svg#mainsvg > *").remove(); // 清除svg中旧的内容.注意,虽然本组件中没有svg,但是jquery会在整个页面中(vue是单页面的)寻找svg#mainsvg下的所有元素,并删除.      
        bus.$emit("sendClearAttriExplorState", true); // 更改数据库时,清除属性值匹配相关的数据.

        // this_.$store.state.selection.selectiondb = curVal; // 保存当前的数据库名称到store.js中.
        if(curVal != ""){ //数据库框不为空.
          // this_.loadingFlag = true; //加载状态.
          bus.$emit("sendLoadingFlagForFeildKeyWord", true); //基本字段 + 关键词框加载.         
          let path = vueFlaskRouterConfig.infoSearchForDbFields + "/" + curVal; // 带参数的URL.          
          axios.get(path)
          .then((res) => {
                  // fixme: 获得指定数据库中,node表的字段 + 字段类型 + 除了node和edge表之外的其他表.
                  // this_.loadingFlag = false; // 加载完成.
                  bus.$emit("sendLoadingFlagForFeildKeyWord", false); //基本字段 + 关键词框不在加载.
                  for(let key in this_.dbLoadedFlag){
                      let tempName = key + ".db"; //数据库名称.
                      if(tempName == curVal){ //是否相同.
                        this_.dbLoadedFlag[key] = true; //表示已经加载完毕.
                        // 只有数据加载完毕才能说明API已经计算好了,取得前N个节点.
                        if(this_.$store.state.isUsingRankMeasures){ // 是否使用排序度量.                          
                          let requestNodeRankTable = vueFlaskRouterConfig.selctionFocusNodesByNodeMeasures + "/" + this_.$store.state.selection.selectiondb + "/PageRank" + "/" + this_.$store.state.nodeRankTable.topN;
                          axios.get(requestNodeRankTable)
                          .then((res) => {
                            let nodeRankTable = res.data; //已经获得了布局好的全局图数据.
                            // this_.$store.state.globalGraphView.globalGraphLayoutData = globalGraphLayoutData; // 更新全局图布局数据.
                            bus.$emit("sendRankTableNodeMeasure", nodeRankTable); //渲染热力图.

                          })
                          .catch((error) => {            
                            console.error(error);
                          });
                        }
                      }
                      else{
                        this_.dbLoadedFlag[key] = false;
                      }
                  } 
                  // console.log("this_.dbLoadedFlag");console.log(this_.dbLoadedFlag);
                  
                  let data = res.data; 
                  // let dbtables = data.dbtables; // 获得该数据库中的所有表,用于后面的"see more"
                  this_.$store.state.infoSearchView.dbtables = data.dbtables; // 获得该数据库中的所有表,用于后面的"see more"
                  this_.$store.state.infoSearchView.numNodes = data.numNodes; // 全局图的节点数量
                   
                  let fields = data.fields; // 获得字段信息.[{label:字段, value:字段}, ...]
                  
                  bus.$emit("sendLoadedInitFieldKeyWord", fields); //加载完数据库后,初始化基本字段+ 关键词框.

                  // this_.optionsfield.splice(0,this_.optionsfield.length);  // 先将数组清空. 注意:这样不会更改地址.
                  // let allFields = {label:"All", value:"All"};
                  // this_.optionsfield.push(allFields);
                  // for(let i=0; i<fields.length; i++){
                  //   this_.optionsfield.push(fields[i]);
                  // }                 
                  // this_.selectionfield = "All"; // 默认选中all.
                  // this_.allFieldData.splice(0, this_.allFieldData.length);  // 先将数组清空. 
                  // this_.keyWord = "";
                  
                  let fieldsType = data.fieldstype; // 获得字段类型.{字段:类型,...}
                  this_.$store.state.fields.fieldsType = fieldsType; // 将字段类型存在store.js中.
                  // console.log("this_.$store.state.fields.fieldsType");console.log(fieldsType); 
                  bus.$emit("sendFocusAttriType", fieldsType); // 在focusAttributesSelection.vue文件中监听.                  
                  bus.$emit("dbLoadedState", true);
                 
          })
          .catch((error) => {            
            console.error(error);
          });
          // 请求布局好的全局图数据.
          if(this_.$store.state.isShowGlobalGraphFlag){
            let requestGlobalGraphPath = vueFlaskRouterConfig.globalGraphLayout + "/" + curVal;
            axios.get(requestGlobalGraphPath)
            .then((res) => {
              let globalGraphLayoutData = res.data; //已经获得了布局好的全局图数据.
              this_.$store.state.globalGraphView.globalGraphLayoutData = globalGraphLayoutData; // 更新全局图布局数据.
              bus.$emit("sendGlobalGraphLayoutData", true); //渲染热力图.

            })
            .catch((error) => {            
              console.error(error);
            });
          }
          // if(this_.$store.state.isUsingRankMeasures){ // 是否使用排序度量.
          //   let requestNodeRankTable = vueFlaskRouterConfig.selctionFocusNodesByNodeMeasures + "/" + this_.$store.state.selection.selectiondb + "/default" + "/" + this_.$store.state.nodeRankTable.topN;
          //   axios.get(requestNodeRankTable)
          //   .then((res) => {
          //     let nodeRankTable = res.data; //已经获得了布局好的全局图数据.
          //     // this_.$store.state.globalGraphView.globalGraphLayoutData = globalGraphLayoutData; // 更新全局图布局数据.
          //     bus.$emit("sendRankTableNodeMeasure", nodeRankTable); //渲染热力图.

          //   })
          //   .catch((error) => {            
          //     console.error(error);
          //   });
          // }          

        }       

        let nullObj = {numnodes:0, numedges:0};
        bus.$emit("sendDoiGraphInfo", nullObj);
      
    }
	},
	methods:{
		 onReset(){
          let settings = {  // Settings面板参数默认值设置.
            // scaleOfSingleFocus: 20,  // scale Of Single Focus,用于单个焦点的抽取规模.  
            // explandneighbors: 10, // 扩展节点的数量.  
            // diffFactor: 0.8,  // 用于扩散函数的扩散程度控制.  
            // UIFactor: 0.9,  // UI_Factor,用户兴趣度因子,API_factor = 1 - UI_factor.
            // APIFactor: 0.1,  // API_Factor
            // isEdgeAttri: true, // 在DOI扩散函数中是否考虑边的属性
            // probRestart: 0.3,  // RWR重启概率.  
            // weightAttrNode: 1, // 属性节点-节点的权重.  
            scaleOfSingleFocus: 30,  // scale Of Single Focus,用于单个焦点的抽取规模.  
            explandneighbors: 5, // 扩展节点的数量.  
            diffFactor: 0.85,  // 用于扩散函数的扩散程度控制.  
            UIFactor: 0.9,  // UI_Factor,用户兴趣度因子,API_factor = 1 - UI_factor.
            APIFactor:0.1,  // API_Factor
            isEdgeAttri: true, // 在DOI扩散函数中是否考虑边的属性
            probRestart: 0.7,  // RWR重启概率.  
            weightAttrNode: 1, // 属性节点-节点的权重. 
          };
          return settings;
     },
	   dropDownBoxVisible(flag){
	        let this_ = this;	        
	        if(flag && this_.dboptions.length == 0){ //点开下拉框时,且没有请求到数据,否则不执行.
	          this_.loadDbs();
	        }
     },
     loadDbs(){
	        let this_ = this;        
	        let path = vueFlaskRouterConfig.infoSearchForDbSelection;
	        axios.get(path) // 用get的速度大于用post.
	        .then((res) => {
	            // this_.loadingDbFlag = false;                
	            let data = res.data; // 获得指定数据库表格中的字段.            
	            this_.dboptions = data.dbname; // [{}, ...] 
	            // console.log("this_.dboptions");console.log(this_.dboptions);
              this_.$store.state.selection.dboptions = this_.dboptions; // [{value:x, label:x, directed:x}, ...]
              // bus.$emit("snedDboptions", this_.dboptions);
	            for(let i=0; i<this_.dboptions.length; i++){
	               let dbName = this_.dboptions[i].label;
	               let key_ = dbName.slice(0,-3); // 这样做是为了去掉.db后缀,因为键不能带点.
	               this_.dbLoadedFlag[key_] = false;  // {dbname1: false, ...} 表示对应的数据库没有加载.
	            } 
	            
	            this_.$store.state.attrNode.discardfield = data.discardfield; // 焦点选择时,应该丢弃的属性. [x, x, ...]
              this_.$store.state.attrNode.fullCompatibilityAtrr = data.fullCompatibilityAttr; // [x, x, ...] 用于mainView的匹配函数中,用于判断字段是否要上下兼容,适用于属性值比较长的属性,比如institution.
              // console.log("this_.$store.state.attrNode.discardfield");console.log(this_.$store.state.attrNode.discardfield);
              // console.log("this_.$store.state.attrNode.fullCompatibilityAtrr");console.log(this_.$store.state.attrNode.fullCompatibilityAtrr);
              this_.stopwordsObj = data.stopword; //存放停用词,停用词json文件在后台.           
	                            
	          })
	        .catch((error) => {            
	          console.error(error);
	        });
     },
	},
	created(){ //里面的内容主要针对数据库.
      let this_ = this;
      console.log("loadDb.vue created");
      this_.$store.state.mainViewGraph.histClickFlag = this_.histClickFlag; // 指针赋予.
      this_.$store.state.infoSearchView.dbLoadedFlag = this_.dbLoadedFlag; // 指针赋予,方便后面状态的实时改变.
      this_.loadDbs(); // 装载数据库名称,以供选择.
      
      bus.$on('sendDbName', function(data){
	      this_.$store.state.mainViewGraph.histClickFlag.splice(0, this_.$store.state.mainViewGraph.histClickFlag.length); // 先清零.
	      this_.$store.state.mainViewGraph.histClickFlag.push(true);  // 点击了历史图片.
	      if(this_.selectiondb == data){ //将历史图片对应的数据库名称填入框中.
	         
	         bus.$emit("restoreFieldKeyWord", true);
	      }
	      this_.selectiondb = data;
	  });
    },
    mounted(){
      let this_ = this;
	  console.log("loadDb.vue mounted");
    },
    beforeDestroy(){
      bus.$off("sendDbName");
    }	
}

</script>

<style>
#load-db-view{
  margin: 0px 0px 0px 0px;
  /*padding:0px 0px 0px 0px;
  border-style: solid;
  border-color:#E0E0E0;
  border-top-width: 2px;
  border-right-width: 2px;
  border-bottom-width: 2px;
  border-left-width: 2px;*/
}
#load-db-view .el-input{
  /*border-style: solid;
  border-color:#E0E0E0;
  border-top-width: 2px;
  border-right-width: 2px;
  border-bottom-width: 2px;
  border-left-width: 2px;*/
}
#load-db-view .el-form-item{
  margin-bottom:5px;
}
#load-db-view .el-input__inner{
   height: 30px;
}
#load-db-view .el-form-item__content{
   line-height: 30px;
}
#load-db-view .el-input__suffix{
   height: 113%;
}
</style>