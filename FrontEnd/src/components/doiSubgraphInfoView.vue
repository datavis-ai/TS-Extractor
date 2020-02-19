<template>
	<div id="global-network-info-view">
    <div v-if="lenDoiGraphInfo.length > 0" class="doi-graph-info">
      <span>DOI subgraph</span>
      <div id="doi-box">
      	<p>	          		
      		|V|: {{doiGraphInfo.numnodes}}&nbsp&nbsp 
      		|E|: {{doiGraphInfo.numedges}}&nbsp&nbsp	          		 
      	</p>
      </div>         
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
       
        doiGraphInfo:{}, // DOI子图信息.        
      }
    },
    computed:{
       
       lenDoiGraphInfo: function(){
         return Object.keys(this.doiGraphInfo);
       },
    },
    methods: {     
       
    },
    created(){      
      let this_ = this;
      bus.$on("sendDoiGraphInfo", function(data){
        this_.doiGraphInfo = data;        
      });
    },
    mounted(){
    	let this_ = this;          
     
    },   
    
    beforeDestroy(){  
        
       bus.$off("sendDoiGraphInfo"); // 接收DOI graph 数据.      
    },
    watch:{ // 侦听器,用于侦听data里面定义的变量,只要变化就执行对应的动作.
    	 
    }

  }
</script>
<style>
.global-graph-info{
   border-style: solid;
   border-color:#E0E0E0;
   border-top-width: 1px;
   border-right-width: 0px;
   border-bottom-width: 0px;
   border-left-width: 0px;
}
.doi-graph-info{
   border-style: solid;
   border-color:#E0E0E0;
   border-top-width: 1px;
   border-right-width: 0px;
   border-bottom-width: 0px;
   border-left-width: 0px;
}   
</style>