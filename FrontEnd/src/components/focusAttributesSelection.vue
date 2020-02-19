<template>
	<div id="focus-attributes-selection-view">
	    <!-- <el-collapse v-model="activeNames" @change="handleChange">
	      <el-collapse-item title="Interest Attribute" name="Focus Attribute Selection">
	        	        
	      </el-collapse-item>
	    </el-collapse> -->
      <div v-if="allAttriIterms.length > 0" class="attributes-selection-info">           
        <el-checkbox :indeterminate="isIndeterminate" v-model="checkAll" @change="handleCheckAllChange">select all</el-checkbox>
        <div style="margin: 5px 0;"></div>
        <el-checkbox-group v-model="checkedIterms" @change="handleCheckedItermChange">
          <el-checkbox v-for="iterm in allAttriIterms" :label="iterm" :key="iterm">{{iterm}}</el-checkbox>
        </el-checkbox-group>       
      </div>
      <div id="finished-interest-attributes">
        <el-button size="small" type="primary" @click="addNode2FocusSet">OK</el-button>
      </div>
      
	</div>	
</template>
<script>
  import axios from 'axios' // 用于AJAX请求
  import * as d3 from 'd3'
  import {vueFlaskRouterConfig} from '../vueFlaskRouterConfig'
  import bus from '../eventbus.js' // 事件总线.
  
  export default {
    data() {
      return {
        // activeNames: [], // 用于折叠项,里面用于保存激活的折叠项的name.
        checkAll: false, // 默认全都不选以增加用户与系统的交互.
        checkedIterms: [], // 存放被选中的属性
        allAttriIterms: [], // 所有候选的属性名称
        isIndeterminate: false,
        whichComponentRightClick: "", //用于判断哪个组件中右键点击"Add it to the focus set".             
      }
    },
    props:[
     "callback" // 回调函数.
    ],
    computed:{
       activeNames:{ // activeNames是v-model绑定的双向变量,则变量需要有getter + setter,这样才能既读又写.
          // getter
          get: function(){
            if(this.$store.state.focusSetView.dynamicTagsFocus.length > 0){ // 
                let temp = [];
                temp.push("Focus Attribute Selection");
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
    methods: {
      addNode2FocusSet(){        
        let this_ = this;
        this_.callback();                  
      },    
      handleChange(val) { // 输出已经点开的项的名字(name).
        console.log(val);  // 比如已经点开了折叠项1 + 折叠项2,那么点开折叠项3时,输出[折叠项1,折叠项2,折叠项3]
      },
      handleCheckAllChange(val) {
        this.checkedIterms = val ? this.allAttriIterms : [];
        this.isIndeterminate = false;
      },
      handleCheckedItermChange(value) {
        let checkedCount = value.length;
        // if(checkedCount === this.allAttriIterms.length){
        //   this.checkAll = true;
        // }
        // if(checkedCount == 0){
        //   this.checkAll = false;
        // } 
        this.checkAll = checkedCount === this.allAttriIterms.length;        
        this.isIndeterminate = checkedCount > 0 && checkedCount < this.allAttriIterms.length;
      },
      getFocusComputedAttri(){
         let this_ = this;
         let discardfield = this_.$store.state.attrNode.discardfield; // [x, x, ...], 这是不用考虑的字段.
         let keysType = this_.$store.state.fields.fieldsType; // 所有字段及其类型.{字段:类型,...}
         let doiNodeAttr = []; // 计算DOI时,用到的节点属性.
         if(discardfield != null && keysType != null){
             let keysRow = Object.keys(keysType); // 获得键列表. [field1, ...] 
             // console.log("all maotingyun keysRow discardfield keysType");console.log(keysRow);console.log(discardfield);console.log(keysType);
             for(let i=0; i<keysRow.length; i++){
                let key_ = keysRow[i]; 
                // if(keysType[key_] == "text"){ // 原来过滤出text类型.
                if(keysType[key_] == "text" || keysType[key_] == "integer" || keysType[key_] == "real"){                                    
                    if(discardfield.indexOf(key_) == -1)  // key_不在里面.
                    { // TODO: 不取name + id,因为id + name一般只有一个,除非有重名的. && key_ != "authors"
                      doiNodeAttr.push(key_); // 注意:NULL的处理.                 
                    }
                }
             }
         }        
         
         // this_.doiNodeAttr = doiNodeAttr;
          // console.log("all maotingyun doiNodeAttr");console.log(doiNodeAttr);
         return doiNodeAttr; // doiNodeAttr=[x, x, x, ...]
      }
    },
    mounted(){
    	let this_ = this;          
     
    },
    created(){
      console.log("this.scaleOfSingleFocus created");
      let this_ = this;
      bus.$on("sendFocusAttriType", function(data){ //说明已经获得数据库的字段类型.
        if(data){
          let doiNodeAttr = this_.getFocusComputedAttri(); // [x, x, x, ...]
          // this_.checkedIterms = doiNodeAttr;
          // this_.allAttriIterms = doiNodeAttr;
          // this_.checkAll = true;

          // this_.checkedIterms = doiNodeAttr;
          this_.allAttriIterms = doiNodeAttr;
          this_.checkAll = false;
        }
      }); // fieldsType 
      
      bus.$on("attributesOfInterestPanelUpdate", function(data){
        if(data){
          this_.checkedIterms = this_.$store.state.focusAttributesSelection.checkedFocusAttri;
        }
      });     
    },

    beforeDestroy(){        
      bus.$off("sendFocusAttriType");
      bus.$off("attributesOfInterestPanelUpdate");   
    },
    watch:{ // 侦听器,用于侦听data里面定义的变量,只要变化就执行对应的动作.
    	checkedIterms: function(culVal, oldVal){
         // console.log(" checkedIterms jingjing culVal");
         // console.log(culVal);
         this.$store.state.focusAttributesSelection.checkedFocusAttri = culVal; // 将选中的属性存放到store.js中.
      },
      allAttriIterms: function(culVal, oldVal){                      
         this.$store.state.focusAttributesSelection.allFocusAttriIterms = culVal; // 将所有将要考虑的属性存放到store.js中.
      }

    }

  }
</script>
<style>
#focus-attributes-selection-view .el-collapse-item__header{
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
  margin:0px 0px 2px 0px;
}

#focus-attributes-selection-view .el-collapse-item__wrap{

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
  /*margin:0px 0px 2px 0px;*/
}
#focus-attributes-selection-view .el-collapse-item__content{
  padding-bottom: 1px;
}
#finished-interest-attributes{
  float:right;
  margin:2px 4px 2px 0px;
  padding:4px 0px 4px 0px;
  border-style: solid;
  border-color:#E0E0E0;
  border-top-width: 0px;
  border-right-width: 0px;
  border-bottom-width: 0px;
  border-left-width: 0px;
  position: absolute;
  right: 0px;
  bottom: 0px;
}
</style>