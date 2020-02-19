<template>
	<div id="network-info-view">
	    <!-- <el-collapse v-model="activeNames" @change="handleChange">
	      <el-collapse-item title="Layout Settings" name="Layout Settings">	          
	      </el-collapse-item>
	    </el-collapse> -->
      <div class="block-layout-control">
          <div id="force-layout-parameter-setting">
            <div class="control-layout">
              <div>Charge: </div>
              <el-slider v-model="chargeStrength" :min=-400 :max=400 :step=10></el-slider>
            </div>

            <div class="control-layout"> 
            <div>Link Length: </div>
            <el-slider v-model="linkLength" :max=400 :step=5></el-slider>    
            </div>

            <div class="control-layout">
            <div>Edge Mode:</div>               
            <el-switch
              style="display: block"
              v-model="edgeMode"               
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

            <div class="control-layout">
            <div>Fix_Nodes:</div>             
            <el-switch
              style="display: block"
              v-model="fixNodesCtrol"               
              active-text="true"
              inactive-text="false">
            </el-switch>
            </div>

          </div>

          <!-- <div class="control-layout">
          <div>Fix Nodes:</div>             
          <el-switch
            style="display: block"
            v-model="fixedNode"               
            active-text="true"
            inactive-text="false">
          </el-switch>
          </div> -->
          <div id="css-style-setting">
            <div class="control-layout">
              <div>Font Size: </div>
              <el-slider v-model="fontSize" :min=0 :max=60 :step=1></el-slider>            
            </div>
            <div class="control-layout">
              <div>Font Weight: </div>
              <el-slider v-model="fontWeight" :min=100 :max=1000 :step=10></el-slider>
            </div>
            <div class="control-layout">
              <div>Edge Opacity: </div>
              <el-slider v-model="edgeOpacity" :min=0.2 :max=1 :step=0.1></el-slider>
            </div>
            <div class="control-layout">
              <div>Ring Width: </div>
              <el-slider v-model="strokeWidthRing" :min=2 :max=10 :step=1></el-slider>
            </div>
          </div>

      </div>
      <div class="reset-fault-layout-settings">
        <el-button size="mini" type="primary" @click="onReset">Reset</el-button>
      </div>
	</div>	
</template>
<script>
  import axios from 'axios' // 用于AJAX请求
  import * as d3 from 'd3'
  import $ from 'jquery'
  import {vueFlaskRouterConfig} from '../vueFlaskRouterConfig'
  import bus from '../eventbus.js' // 事件总线.
  
  export default {
    data() {
      return {
        // activeNames: [], // 用于折叠项,里面用于保存激活的折叠项的name.       
        
        chargeStrength: -200, //力导引力大小设置.
        linkLength: 100, // 力导引边长度设置.
        edgeMode: true, // 边的模式: line OR curve, true: line , false: curve.
        labelDisplay: true, // 是否显示标签. 
        fixedNode: false, // 是否可以固定节点  
        fontSize: 14, //默认字体大小.
        fontWeight: 500, // 默认字体粗细.
        edgeOpacity: 0.3, // 边的透明度
        strokeWidthRing: 4, // 环的大小
        fixNodesCtrol: false, // 是否启动实时布局. 表现:只要拖动节点就会布局.
        
      }
    },
    methods: {     
      handleChange(val) {  // 输出已经点开的项的名字(name).
         console.log(val);  // 比如已经点开了折叠项1 + 折叠项2,那么点开折叠项3时,输出[折叠项1,折叠项2,折叠项3]
      },
      onReset(){ // 恢复默认值.         
        this.chargeStrength = -200;
        this.linkLength = 100;
        this.edgeMode = true;
        this.labelDisplay = true;
        this.fixedNode = false;
        this.fontSize = 14;
        this.fontWeight = 500;
        this.edgeOpacity = 0.3;
        this.strokeWidthRing = 4;
        this.fixNodesCtrol=false;
      }
    },
    mounted(){
    	let this_ = this;
    },
    created(){       
      let this_ = this;             
      bus.$on("sendAvgRadiusFlag", function(data){ // 节点的平均半径,用于决定字体的大小.     
        if(data > 10){
           this_.fontSize = 10; // 如果半径过大,则设置成14px.
        }
        else{
          this_.fontSize = data; // 里面一定不能用this,一定要用this_,否则无法改变fontSize属性,即字体大小与节点的半径相同.
        }
      }); 

    },
    computed:{        
        
    },
    beforeDestroy(){              
       bus.$off("sendAvgRadiusFlag");  // 发送节点的平均半径.          
    },
    watch:{ // 侦听器,用于侦听data里面定义的变量,只要变化就执行对应的动作.  
      fixNodesCtrol: function(curVal, oldVal){
        bus.$emit("sendFixNodesCtrolFlag", curVal); // true / false.
      },    
      chargeStrength:function(curVal, oldVal){
        let tempObj = {};         
        tempObj.chargeStrength = curVal;
        tempObj.linkLength = this.linkLength;
        tempObj.edgeMode = this.edgeMode;

        bus.$emit("sendLayoutSettings", tempObj);
        // this.isClickHistImg = false;
      },
      linkLength: function(curVal, oldVal){
        let tempObj = {};         
        tempObj.chargeStrength = this.chargeStrength;
        tempObj.linkLength = curVal;
        tempObj.edgeMode = this.edgeMode;

        bus.$emit("sendLayoutSettings", tempObj);
        // this.isClickHistImg = false;

      },
      edgeMode: function(curVal, oldVal){
        let tempObj = {};         
        tempObj.chargeStrength = this.chargeStrength;
        tempObj.linkLength = this.linkLength;
        tempObj.edgeMode = curVal;

        bus.$emit("sendLayoutSettings", tempObj);
        // this.isClickHistImg = false;
      },
      labelDisplay: function(curVal, oldVal){
        this.$store.state.layoutSettingsView.labelDisplay = curVal; // 状态实时更新.
        if(curVal){ // true
          $("#main-view-for-graph .svg-container .nodes text").css("display", "block");
        }
        else{ // false
           $("#main-view-for-graph .svg-container .nodes text").css("display", "none");
        }
      },
      fixedNode: function(curVal, oldVal){
        this.$store.state.layoutSettingsView.fixedNode = curVal;
      },
      fontSize: function(curVal, oldVal){
        this.$store.state.mainViewGraph.fontSize = curVal;
        let css = {
          "font-size": this.fontSize.toString() + "px"
                   
        };        
        $("#mainsvg .nodes text").css(css); // 改变字体.
        // console.log("maoty loves cher");
      },
      fontWeight: function(curVal, oldVal){
        this.$store.state.mainViewGraph.fontWeight = curVal;
        let css = {
          "font-weight": this.fontWeight.toString()                  
        };        
        $("#mainsvg .nodes text").css(css); // 改变字体. 
      },
      edgeOpacity: function(curVal, oldVal){
         this.$store.state.mainViewGraph.edgeOpacity = curVal;
         let css = {
          "stroke-opacity": this.edgeOpacity.toString()                  
         };        
         $("#mainsvg .links .source-link-target").css(css); // 改变字体. 
      },
      strokeWidthRing: function(curVal, oldVal){
         this.$store.state.mainViewGraph.strokeWidth = curVal;         
         bus.$emit("sendHighLightedRing");
      }
    }

  }
</script>
<style>
  #network-info-view .block-layout-control{
     border-style: solid;
     border-color:#E0E0E0;
     border-top-width: 1px;
     border-right-width: 0px;
     border-bottom-width: 0px;
     border-left-width: 0px;
     margin: 0px 0px 2px 0px;
     padding: 0px 0px 0px 5px;
  }
  #network-info-view .reset-fault-layout-settings{     
     float: right;
  }
  #network-info-view .control-layout{
    margin:0px 0px 0px 0px;
  }
  #network-info-view .control-layout div{
    display:inline-block;    
  }
 .el-button--mini{
    padding-top: 7px;
    padding-right: 4px;
    padding-bottom: 7px;
    padding-left: 4px;
  }
 #force-layout-parameter-setting{
     border-style: solid;
     border-color:#E0E0E0;
     border-top-width: 1px;
     border-right-width: 1px;
     border-bottom-width: 1px;
     border-left-width: 1px;
     margin: 1px 1px 1px 0px;
     padding: 0px 0px 2px 4px;
 }
 #css-style-setting{
     border-style: solid;
     border-color:#E0E0E0;
     border-top-width: 1px;
     border-right-width: 1px;
     border-bottom-width: 1px;
     border-left-width: 1px;
     margin: 1px 1px 1px 0px;
     padding: 0px 0px 0px 4px;
 }
</style>