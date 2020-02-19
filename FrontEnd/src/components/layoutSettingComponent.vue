<template>
  <div id="layout-setting-component">
      <div class="block-layout-control">
          <div class="control-layout">
            <div>Charge: </div>
            <el-slider v-model="layoutParam.chargeStrength" :min=-500 :max=500 :step=10></el-slider>
          </div>

          <div class="control-layout"> 
          <div>Link Length: </div>
          <el-slider v-model="layoutParam.linkLength" :max=200 :step=5></el-slider>    
          </div>

          <div class="control-layout">
          <div>Edge Mode:</div>               
          <el-switch
            style="display: block"
            v-model="layoutParam.edgeMode"               
            active-text="line"
            inactive-text="curve">
          </el-switch>
          </div>
          
          <div class="control-layout">
          <div>Label:</div>               
          <el-switch
            style="display: block"
            v-model="labelDisplay"               
            active-text="true"
            inactive-text="false">
          </el-switch>
          </div>

      </div>
      <div class="reset-fault-layout-settings">
        <el-button size="mini" type="primary" @click="onReset">Reset</el-button>
      </div>
  </div>
</template>

<script>
  import $ from 'jquery'
  import bus from '../eventbus.js' // 事件总线.
  export default {    
    data: function(){
      return {
        layoutParam:{
          linkLength: 80, // 边的长度.
          chargeStrength: -200, // 力导引力度大小.
          edgeMode: true, // 边模式:curve-曲线 false, line-直线 true.          
          limitBox: false, // 是否将布局结果限制在一个盒子里面.
          nodeColor:"#FF8700", // 节点的填充颜色.
          baseSize: 10, // 布局图中节点的基本大小.
          labelDisplay: true //是否显示标签
        },
        labelDisplay: true, // 是否显示标签,用css控制是否显示而非重新布局.
        
      }
    },
    props:[
     'busEventName' //名称.
    ],
    watch:{
      layoutParam:{ //深度监听，可监听到对象、数组的变化
        handler(curVal, oldVal){
           
           let this_ = this;
           curVal.labelDisplay = this_.labelDisplay;
           let newObj = JSON.parse(JSON.stringify(curVal)); //深度拷贝.
           // 必须做以下转化处理,否则布局出来的图没有边.
           if(newObj.edgeMode == true){ // "line"
             newObj.edgeMode = "line"; //直线
           }
           else{ //"curve"
             newObj.edgeMode = "curve"; //曲线
           }
           bus.$emit(this_.busEventName, [true, newObj]); //true: 需要重新布局, 向外部实时发送数据,作为该子组件的输出,便于解耦.
           // bus.$emit(this_.busEventName, "curVal");
        },
        deep:true
      },
      labelDisplay: function (curVal, oldVal){
        let this_ = this;
        bus.$emit(this_.busEventName, [false, curVal]); //false:表示不需要重新布局.
      }
    },
    methods:{
      onReset(){ // 恢复默认值.         
        this.layoutParam.chargeStrength = -200;
        this.layoutParam.linkLength = 80;
        this.layoutParam.edgeMode = true;
        this.labelDisplay = true;
      },      
    },
    created(){
      let this_ = this;
    },
    mounted(){
      let this_ = this;
      
    }    
  }
</script>

<style>
 #layout-setting-component .block-layout-control{
     border-style: solid;
     border-color:#E0E0E0;
     border-top-width: 1px;
     border-right-width: 0px;
     border-bottom-width: 0px;
     border-left-width: 0px;
     margin: 0px 0px 2px 0px;
     padding: 0px 0px 0px 5px;
  }
  #layout-setting-component .reset-fault-layout-settings{     
     float: right;
     margin-right: 5px;
  }
  #layout-setting-component .control-layout{
    margin:0px 0px 0px 0px;
  }
  #layout-setting-component .control-layout div{
    display:inline-block;    
  }
  
  .reset-fault-layout-settings .el-button--mini{
    padding-top: 7px;
    padding-right: 4px;
    padding-bottom: 7px;
    padding-left: 4px;
    margin: 0px 2px 0px 0px;
  }
</style>
