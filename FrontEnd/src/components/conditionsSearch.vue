<template>
	<div id="conditions-search-view">
	  <el-form :inline="true" ref="searchConditionForm" :model="conditionForm" class="multiple-conditions-form">
        <el-form-item v-loading="loadingFlag" label="">   <!--数据库node表字段框-->           
          <el-select class="select-field-input" v-model="selectionfield" filterable placeholder="Select field">
              <el-option
                  v-for="(item, index) in optionsfield"               
                  :key="item.value"
                  :label="item.label"
                  :value="item.value">
              </el-option>
          </el-select>
        </el-form-item>
        <el-form-item v-loading="loadingFlag" label="">  <!--关键词输入框-->          
          <el-autocomplete
            popper-class="my-autocomplete"
            v-model="keyWord"
            :fetch-suggestions="querySearchAsync"
            placeholder="input"
            @focus="getFocusInInput"
            @select="handleSelect"
          >
          <i class="el-icon-edit el-input__icon"
          slot="suffix">                       
          </i>
          <template slot-scope="{ item }">
            <div class="name">{{ item.value }}</div>              
          </template>
          </el-autocomplete>
        </el-form-item>
        <!-- <el-form-item>
         <img id="icon-add" width="15" height="15" @click="addLadder" src="../../static/img/icon-add.png">
        </el-form-item> -->
        <!--点击增加条件框-->
       <!-- <el-row style="margin-left:1px;margin-right:-5px;" :gutter="10" v-for="(formObj,formIndex) in conditionForm.formDataList" >         
          
          <el-form-item v-loading="loadingFlag" label=""> 
            <el-select class="select-field-input" v-model="formObj.selectionfield" filterable placeholder="Select field">
                <el-option
                    v-for="(item, index) in optionsfield"               
                    :key="item.value"
                    :label="item.label"
                    :value="item.value">
                </el-option>
            </el-select>
          </el-form-item>
          
          <el-form-item v-loading="loadingFlag" label=""> 
            <el-autocomplete              
              popper-class="my-autocomplete"
              v-model="formObj.keyWord"            
              :fetch-suggestions="querySearchAsyncMulCons"
              placeholder="input"
              @focus="getFocusInInputNew"
              @select="handleSelect"              
            >
            <i class="el-icon-edit el-input__icon"
            slot="suffix">                       
            </i>
            <template slot-scope="{ item }">
              <div class="name">{{ item.value }}</div>              
            </template>
            </el-autocomplete>
          </el-form-item>       
          
          <el-form-item>            
            <img id="icon-remove" width="15" height="15" @click="deleteLadder(formIndex)" src="../../static/img/icon-subtract.png"> 
          </el-form-item>
       </el-row> -->

       <el-form-item>
          <el-button size="small" type="primary" class="el-icon-search" @click="onSubmit"></el-button>
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
  	data() {
      return {
       
        selectionfield: '', // 基本的字段选择框.
        keyWord: "", // 基本的关键字输入框.
        
        conditionForm:{ //多条件表单数据.
          formDataList: [] //增加的条件. conditionForm.formDataList:[{selectionfield:"All", keyWord:""}, ...]
        },        
        optionsfield:[], // 存放选中的数据库的node表的所有字段.
        allFieldData: [], // 只对基本关键词输入框,选中字段对应的所有取值构成的列表,格式:[{value:x, number:x},...]
        allFieldDataEachCon:{}, //{filed1:[{value:x, number:x},...],...}        
        /*
          "name":[{value:"maoty", number:2},{value:"jingjing", number:3}],
          "interests":[{value:"graph drawing", number:2},{value:"information visualization", number:3}]
        */

        loadingDbFlag: false, // 加载数据库标志量.
        loadingFlag: false,  // 加载标志量. true:加载, false:加载完成.
        
        histClickFlag: [false], // 用于记录是否点击了历史图片.[true]表示点击了,写成数组是为了用指针.

        dbLoadedFlag:{}, // 数据库加载完毕标志位.只有数据库加载完毕,才能请求对应的DOI子图.
        currentSelectedFieldInMulCons: null, //当多条件查询时,用于保存当前选中的字段. 
      }
  	},
  	watch:{
  		'conditionForm.formDataList':{ //深度监听conditionForm.formDataList的实时变化.
          handler(curVal, oldVal){ //[{selectionfield:"All", keyWord:""}, ...]
            let this_ = this;
            this_.$store.state.conditionsSearch.formDataList = curVal; //[{selectionfield:"All", keyWord:""}, ...]
            let allFieldsSet = new Set(); //一个集合.            
            for(let i=0; i<curVal.length; i++){
              let obj = curVal[i];
              allFieldsSet.add(obj.selectionfield); //{xxx, xxx}
            }            
            let exitFieldsList = Object.keys(this_.allFieldDataEachCon);            
            if(allFieldsSet.size > 0){ //保证里面有元素.
              allFieldsSet.forEach(function (key, val){ // val:字段值.
                if(val != "All" && val != ""){
                  if(exitFieldsList.indexOf(val) == -1){ //对不在allFieldDataEachCon里面的字段,向后台请求其值.                    
                    let param = {"dbName": this_.$store.state.selection.selectiondb, "field": val}; 
                    axios.post(vueFlaskRouterConfig.infoSearchForDbFieldsValues, {
                      param: JSON.stringify(param)
                    })
                    .then((res) => {
                        let data = res.data; // 获得指定数据库表格中的字段.
                        this_.allFieldDataEachCon[val] = data; //向allFieldDataEachCon添加对象,e.g.{name:[{}, ...], }
                        // console.log("this_.allFieldDataEachCon");
                        // console.log(this_.allFieldDataEachCon);                                       
                    })
                    .catch((error) => {            
                      console.error(error);
                    });
                  }
                }

              });
            }
          },
          deep:true
      },

      selectionfield: function(curVal, oldVal){ // selectionfield数据更新才执行. 选完字段后,请求后台获得选中字段的值,以供后续按照字段查询.
        let this_ = this;
        this_.$store.state.selection.selectionfield = curVal; // 保存在store中,保证实时更新.       
        if(this_.$store.state.selection.selectiondb){ // 保证先选择了数据库.
          if(this_.selectionfield != "All" && this_.selectionfield != ""){ // 如果已经选中了,且非All.
            this_.allFieldData.splice(0, this_.allFieldData.length);  // 先将数组清空. 注意:这样不会更改地址.
            let param = {"dbName": this_.$store.state.selection.selectiondb, "field": this_.selectionfield}; 
            axios.post(vueFlaskRouterConfig.infoSearchForDbFieldsValues, {
              param: JSON.stringify(param)
            })
            .then((res) => {   
                // this_.loadingFlag = false; // 加载完成.          
                let data = res.data; // 获得指定数据库表格中的字段.
                console.log("selectionfield data");
                // this_.allFieldData.splice(0, this_.allFieldData.length);  // 先将数组清空. 注意:这样不会更改地址.  
                this_.allFieldData = data;
                // console.log(data);          
                                
            })
            .catch((error) => {            
              console.error(error);
            }); 
          }
          else{
            this_.allFieldData.splice(0, this_.allFieldData.length);  // 先将数组清空. 注意:这样不会更改地址. 
          }

        }
      },

      keyWord: function(curVal, oldVal){
      	let this_ = this;
        this_.$store.state.selection.keyword = curVal; // 保存在store中,保证实时更新.        
        if(curVal == ""){  // 如果输入框中为空,则表格隐藏.          
          let isvisible = true; // 表格数据是否可见.
          bus.$emit("tabelDataVisible", isvisible);  // 往resultsSearch.vue发送状态.
        }                     

      }
  	},
  	methods:{
	  deleteLadder(index){
	  	let this_ = this;
	    if(this_.conditionForm.formDataList.length>0){
	       this_.conditionForm.formDataList.splice(index,1); //[{}, {}, ...]	      
	    }
      },
      addLadder(){ //新增加条件.
      	let this_ = this;
        this_.conditionForm.formDataList.push({selectionfield:"All", keyWord:""}); //[{}, {}, ...]
        
      },
      onSubmit() { //点击"Search",用以上设置的条件到后台匹配.
        let this_ = this;
        // bus.$emit("maotingyuntest", true);
        // bus.$emit("sendSplitPanesFlag", true); // 弹开窗口.
        if(this_.$store.state.selection.selectiondb != "" && this_.selectionfield != "" && this_.keyWord != ""){ //所有框都非空.
            console.log("已经点击Search,向后台请求表格数据!");
            // 数据库 + 字段 + 关键词更新.
            let newstate = {
              selectiondb: this_.$store.state.selection.selectiondb,
              selectionfield: this_.selectionfield,
              keyword: this_.keyWord
            }; 
            this_.$store.dispatch('changeStateSelection', newstate); // 注意:this_.$store.dispatch('changeStateSelection', newstate)是用来保存:数据库名 + 字段名 + 关键词. 
            let conditionsObj = JSON.parse(JSON.stringify(this_.conditionForm)); //深度拷贝.
            let addConditions = conditionsObj.formDataList; //[{selectionfield:"All", keyWord:""}, ...]
            addConditions.push({selectionfield: this_.selectionfield, keyWord: this_.keyWord}); //将基本条件加上去.
            // let param = {"dbName": this_.$store.state.selection.selectiondb, "dbfield": this_.selectionfield, "dbfieldvalue": this_.keyWord}; //将条件发送到后台,请求匹配的节点数据.
            let param = {"dbName": this_.$store.state.selection.selectiondb, "conditions": addConditions}; //将条件发送到后台,请求匹配的节点数据.
            axios.post(vueFlaskRouterConfig.infoSearchForResultsSearch, {
              param: JSON.stringify(param)
            })
            .then((res) => {                   
                    // console.log("param..........."); console.log(param);                
                    let tabelData = res.data;  // 通过查询选中焦点,然后用焦点的id获得图数据.                
                    bus.$emit("sendResultsSearch", tabelData);  // 向resultsSearch.vue发送数据.
                              
              })
            .catch((error) => {            
              console.error(error);
            });
        } 

      },
      fuzzyQuery(list, keyWord) { // 模糊查询,从字符串中匹配出含有查询项的字符串.
        let lowerCasekeyWord = keyWord.toLowerCase(); // 先转换成小写.
        var reg =  new RegExp(lowerCasekeyWord);
        var arr = [];
        if(list){
            for (var i = 0; i < list.length; i++) {
              let newStr = list[i].value.toLowerCase(); // 先转换成小写.
              if (reg.test(newStr)) {
                arr.push(list[i]);
              }
            }
        }
        
        return arr;
      },      
      querySearchAsync(queryString, cb) {
        let this_ = this;
        // console.log("queryString");console.log(queryString);
        let allFieldData = this_.allFieldData;        
        let results = this_.fuzzyQuery(allFieldData, queryString); // queryString实时输入的字符串.
        // console.log("results");console.log(results);
        cb(results);         
      },
      querySearchAsyncMulCons(queryString, cb){ //增加条件时,关键词表与选中的字段一一对应,避免共用一个变量.
        let this_ = this;
        let curField = this_.currentSelectedFieldInMulCons;          
        let allFieldData = this_.allFieldDataEachCon[curField]; //获得字段对应的值列表.[{value:x, number:x}, ...]        
        let results = this_.fuzzyQuery(allFieldData, queryString); // queryString实时输入的字符串.        
        cb(results);
      },
      getFocusInInput(event){ //当鼠标点击input框,出现光标时触发.
        // let this_ = this;
        // console.log("event");
        // // console.log(event);
        // let fieldVal = event.path[5]["0"].value; //获得字段值.
        // console.log(event.path[5]["0"].value);
      },
      getFocusInInputNew(event){
        let this_ = this;        
        let fieldVal = event.path[5].childNodes[1].previousSibling.firstElementChild.children["0"].lastChild.children["0"].value; // todo:这么做是有风险的,一旦element-ui框架版本更换,或者多加一个div,可能就无法获得字段值了.
        this_.currentSelectedFieldInMulCons = fieldVal; //保存当前选中的字段.      
      },    
      handleSelect(item) {
        console.log(item);
      }
  	},
  	created(){
  	  let this_ = this;
  	  // bus.$on('sendNodeId', function(data){         
     //    this_.keyWord = String(data); // data 必须转换成String型,否则将出现跨域问题,将节点id值赋给this_.keyWord表单.           
     //  });
      bus.$on("restoreFieldKeyWord", function (flag){
         if(flag){
         // 	this_.selectionfield = "All"; 
	        // this_.keyWord = "";
         }
      });
      bus.$on("sendLoadingFlagForFeildKeyWord", function (flag){
      	this_.loadingFlag = flag; //是否开始/完成加载.
      });
      bus.$on("sendLoadedInitFieldKeyWord", function (fields){ //加载完数据库后,初始化基本字段+ 关键词框.
      	  
      	  this_.optionsfield.splice(0,this_.optionsfield.length);  // 先将数组清空. 注意:这样不会更改地址.
	      let allFields = {label:"All", value:"All"};
	      this_.optionsfield.push(allFields);
	      for(let i=0; i<fields.length; i++){
	        this_.optionsfield.push(fields[i]);
	      }                 
	      this_.selectionfield = "All"; // 默认选中all.
	      this_.allFieldData.splice(0, this_.allFieldData.length);  // 先将数组清空. 
	      this_.keyWord = "";
      });
  	},
  	mounted(){    
      let this_ = this;
      console.log("conditionsSearch.vue mounted");
    },    

    beforeDestroy(){      
      // bus.$off("sendNodeId");
      bus.$off("restoreFieldKeyWord");
      bus.$off("sendLoadingFlagForFeildKeyWord");
      bus.$off("sendLoadedInitFieldKeyWord"); //加载完数据库后,初始化基本字段+ 关键词框.     
    }
  }

</script>

<style>
.select-field-input .el-input {
  position: relative;
  font-size: 14px;
  display: inline-block;
  width: 150px;
}
#conditions-search-view .el-row{
  margin-left: 1px;margin-right: -5px;
}
#conditions-search-view .el-form-item {
    margin-bottom: 5px;
    margin-top: 2px;
}
#conditions-search-view .select-field-input .el-input {     
    width: 130px;
}
#conditions-search-view .el-button--primary {
    color: #111010;
    background-color: #f5f7fa;
    border-color: #eae9e9;
}
</style>
