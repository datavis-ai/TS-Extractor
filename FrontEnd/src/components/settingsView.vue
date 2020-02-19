<template>
  <div id="node_num_widget">
    <el-collapse v-model="activeNames" @change="handleChange">
       
      <el-collapse-item title="Control Panel" name="Control Panel">        
        <div id="settings-first-box">
          <div class="block-nodes-control settings-block">
            <span>ctrl_size_subgraph:</span>
            <el-slider v-model="scaleOfSingleFocus">    
            </el-slider>
            <!-- <span>max_num_neighbors</span>
            <el-slider v-model="explandneighbors">    
            </el-slider>  -->          
          </div>           
          <div class="block-doi settings-block">            
            <!-- <span>weight_API</span>
            <el-slider v-model="APIFactor" :max=1 :step=0.01>    
            </el-slider> -->
            <span>weight_R:</span>
            <el-slider v-model="UIFactor" :max=1 :step=0.01>    
            </el-slider>
          </div>
          <!--暂时放在这里-->
          <div class="block-diffusion settings-block">
              <span>diffusion factor:</span>
              <el-slider v-model="diffFactor" :max=1 :step=0.01>    
              </el-slider>            
          </div>
        </div>
        <!-- <div id="settings-second-box">
          <div class="block-random-walk settings-block">
              <span>restart_prob</span>
              <el-slider v-model="probRestart" :max=1 :step=0.01>    
              </el-slider>
              <span>weight_attr_node</span>
              <el-slider v-model="weightAttrNode" :max=1 :step=0.01>    
              </el-slider>
          </div>
          <div class="block-diffusion settings-block">
              <span>diffusion factor</span>
              <el-slider v-model="diffFactor" :max=1 :step=0.01>    
              </el-slider>
            <span>Attribution_Edge_Diffusion</span>
            <el-switch
              v-model="isEdgeAttri"
              active-color="#5DADE2"
              inactive-color="#EAECEE">
            </el-switch>
          </div>         
        </div> -->
        
        
        <div class="reset-fault-settings">
          <el-button size="mini" type="primary" @click="onReset">Reset</el-button>
        </div>
        
      </el-collapse-item>
      <!-- <el-collapse-item title="Controls" name="Controls">
      </el-collapse-item> -->
    </el-collapse>

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
        activeNames: [], // 用于折叠项,里面用于保存激活的折叠项的name.
        scaleOfSingleFocus:0, // DOI子图的节点数量.
        explandneighbors: 0, // 点击边缘节点时,扩展的邻居数量.
        diffFactor: 0, // FIXME: 用于DOI值的扩散.过程: 先对每个节点计算DOI=API_factor*API + UI_factor*UI, 得到每个节点的DOI值.最后使用扩散函数进行扩散,便于后期的贪心抽取.
        UIFactor: 0,  // UI_Factor, 用户兴趣因子.
        APIFactor: 0, // 注意: UIUIFactor + APIFactor = 1.
        isEdgeAttri: true, // 是否考虑边的属性.如果考虑则节点邻居DOI*对应的边权重.

        probRestart: 0,  // RWR重启概率.
        weightAttrNode: 0, // 属性节点-节点的权重.
      }
    },
    methods: {
       onReset(){          
          this.scaleOfSingleFocus = 30;  // scale Of Single Focus,用于单个焦点的抽取规模.  
          this.explandneighbors = 5; // 扩展节点的数量.  
          this.diffFactor = 0.85;  // 用于扩散函数的扩散程度控制.  
          this.UIFactor = 0.9;  // UI_Factor,用户兴趣度因子,API_factor = 1 - UI_factor.
          this.APIFactor = 0.1;  // API_Factor
          this.isEdgeAttri = true; // 在DOI扩散函数中是否考虑边的属性
          this.probRestart = 0.7;  // RWR重启概率.  
          this.weightAttrNode = 1; // 属性节点-节点的权重. 

          // scaleOfSingleFocus: 20,  // scale Of Single Focus,用于单个焦点的抽取规模. this.$store.state.widgetView.scaleOfSingleFocus
          // explandneighbors: 10, // 扩展节点的数量. this.$store.state.widgetView.explandneighbors
          // diffFactor: 1,  // 用于扩散函数的扩散程度控制. this.$store.state.widgetView.diffFactor
          // UIFactor: 0.9,  // UI_Factor,用户兴趣度因子,API_factor = 1 - UI_factor.
          // APIFactor: 0.1,  // API_Factor
          // isEdgeAttri: false, // 在DOI扩散函数中是否考虑边的属性
          // probRestart: 0.3,  // RWR重启概率. this.$store.state.widgetView.probRestart
          // weightAttrNode: 1, // 属性节点-节点的权重. this.$store.state.widgetView.weightAttrNode         
       },     
       handleChange(val) {  // 输出已经点开的项的名字(name).
        console.log(val);  // 比如已经点开了折叠项1 + 折叠项2,那么点开折叠项3时,输出[折叠项1,折叠项2,折叠项3]
      },
    },
    mounted(){
    	let this_ = this; 
      console.log("scaleOfSingleFocusNodeNum.vue mounted");      
      bus.$emit("explandNodeNum", this_.explandneighbors);
      bus.$on("Settings", function(settings){ // 来自loadDb.vue, 用于切换数据库时,更新reset参数,避免上一个数据探索时参数调整的影响.
        this_.scaleOfSingleFocus = settings.scaleOfSingleFocus;
        this_.explandneighbors = settings.explandneighbors;
        this_.diffFactor = settings.diffFactor; // 扩散因子.
        this_.UIFactor = settings.UIFactor; // UI因子.
        this_.APIFactor = settings.APIFactor; // API因子.
        this_.isEdgeAttri = settings.isEdgeAttri; // DOI扩散时,是否考虑边的属性.
        this_.probRestart = settings.probRestart;  // RWR重启概率.
        this_.weightAttrNode = settings.weightAttrNode; // 属性节点-节点的权重.
        /*
        probRestart: 0.7,  // RWR重启概率. this.$store.state.widgetView.probRestart
      weightAttrNode: 1,*/
      });
    },
    created(){
       console.log("this.scaleOfSingleFocus created");
       let this_ = this;       
       bus.$emit("explandNodeNum", this_.explandneighbors);
       bus.$emit("nodeNum", this_.scaleOfSingleFocus);
      
      // fixme: 用store.js中的全局变量初始化组件data中的变量.
      this_.scaleOfSingleFocus = this_.$store.state.widgetView.scaleOfSingleFocus;
      this_.explandneighbors = this_.$store.state.widgetView.explandneighbors;
      this_.diffFactor = this_.$store.state.widgetView.diffFactor; // 扩散因子.
      this_.UIFactor = this_.$store.state.widgetView.UIFactor; // UI因子.
      this_.APIFactor = this_.$store.state.widgetView.APIFactor; // API因子.
      this_.isEdgeAttri = this_.$store.state.widgetView.isEdgeAttri; // DOI扩散时,是否考虑边的属性.
      this_.probRestart = this_.$store.state.widgetView.probRestart;  // RWR重启概率.
      this_.weightAttrNode = this_.$store.state.widgetView.weightAttrNode; // 属性节点-节点的权重.
      bus.$on("dbLoadedState", function(data){
         // todo: 数据库装载成功后,直接获取全局图的各种统计信息.

      });
    },
    computed:{
      // test(){
      //   alert("this.explandneighbors");
      //   alert(this.explandneighbors);
      // }
    },
    beforeDestroy(){       
       bus.$off('Settings');  // 由于bus.on()不会自己注销,需要bus.$off()来注销,这样可以解决多次触发的问题. 
       bus.$off("dbLoadedState");  // 数据库装载成功.       
    },
    watch:{ // 侦听器,用于侦听data里面定义的变量,只要变化就执行对应的动作.
    	scaleOfSingleFocus: function(curVal, oldVal){
         //console.log(this.scaleOfSingleFocus);
         bus.$emit("nodeNum", curVal); // 注册自定义事件nodeNum,用于控制主视图中节点的数量. 
         this.$store.state.widgetView.scaleOfSingleFocus = curVal;
    	},
      explandneighbors: function(curVal, oldVal){
         bus.$emit("explandNodeNum", curVal); // 注册自定义事件explandNodeNum,用于控制主视图中扩展边缘节点的邻居数量.
         this.$store.state.widgetView.explandneighbors = curVal;
      },
      diffFactor: function(curVal, oldVal){
        this.$store.state.widgetView.diffFactor = curVal; // 将新的扩散因子值存入store中.
      },
      UIFactor: function(curVal, oldVal){
        this.$store.state.widgetView.UIFactor = curVal; // 将UI因子存入.
        this.$store.state.widgetView.APIFactor = 1.0 - curVal; // 将UI因子存入.
        this.APIFactor = 1.0 - curVal; 
      },
      APIFactor: function(curVal, oldVal){
        this.$store.state.widgetView.APIFactor = curVal; // 将API因子存入.
        this.$store.state.widgetView.UIFactor = 1.0 - curVal; // 将API因子存入.
        this.UIFactor = 1.0 - curVal; 
      },
      isEdgeAttri: function(curVal, oldVal){
         this.$store.state.widgetView.isEdgeAttri = curVal; // 将isEdgeAttri因子存入.
      },
      probRestart: function(curVal, oldVal){
         this.$store.state.widgetView.probRestart = curVal;  // RWR重启概率.      
      },
      weightAttrNode: function(curVal, oldVal){
         this.$store.state.widgetView.weightAttrNode = curVal; // 属性节点-节点的权重.
      },
    }

  }
</script>
<style>
 
  .el-collapse-item__header{
    font-size: 18px; /*1.25rem;*/
    /*font-weight: 600;
    padding-left: 15px;*/
  }
  .el-slider{
    width:50%;
  }
  .el-collapse-item__content >div{
    margin:1px;
    /*border:0;*/
    padding:0;
  }
  .block-nodes-control{
     border-style: solid;
     border-color:#ddd;
     border-top-width: 0px;
     border-right-width: 0px;
     border-bottom-width: 0px;
     border-left-width: 0px;
  }
  .block-diffusion{
     border-style: solid;
     border-color:#ddd;
     border-top-width: 0px;
     border-right-width: 0px;
     border-bottom-width: 0px;
     border-left-width: 0px;
  }
  .block-doi{
     border-style: solid;
     border-color:#ddd;
     border-top-width: 0px;
     border-right-width: 0px;
     border-bottom-width: 0px;
     border-left-width: 0px;
  }
  .block-random-walk{
     border-style: solid;
     border-color:#ddd;
     border-top-width: 0px;
     border-right-width: 0px;
     border-bottom-width: 0px;
     border-left-width: 0px;
     margin: 0px 0px 1px 0px; 
  }
  .reset-fault-settings{
    float: right;
    margin:0px 3px 2px 0px;
  }
  #node_num_widget .el-slider__runway {
    width: 100px;
    height: 6px;
    margin: 16px 0;
    background-color: #e4e7ed;
    border-radius: 3px;
    position: relative;
    cursor: pointer;
    vertical-align: middle;
  }

  #node_num_widget .el-collapse-item__header{
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

  #node_num_widget .el-collapse-item__wrap{
  
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
#node_num_widget .el-collapse-item__content{
  margin-left: 5px;
}
.settings-block{
  width: 120px;
  display: inline-block;
  margin: 0px 10px 0px 0px;
}
.el-slider__button {
    width: 10px;
    height: 10px;
    border: 2px solid #409EFF;
    background-color: #fff;
    border-radius: 50%;
    -webkit-transition: .2s;
    transition: .2s;
    -webkit-user-select: none;
    -moz-user-select: none;
    -ms-user-select: none;
    user-select: none;
}
#node_num_widget .el-button--mini{
    padding-top: 7px;
    padding-right: 4px;
    padding-bottom: 7px;
    padding-left: 4px;
}
#settings-first-box{
  padding: 2px 0px 0px 0px;
}
#node_num_widget .el-slider__bar {
    background-color: #91d5ff;
}
#node_num_widget .el-slider__button {    
    border: 2px solid #91d5ff;   
}
</style>
