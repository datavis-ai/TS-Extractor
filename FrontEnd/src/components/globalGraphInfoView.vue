<template>
	<div id="global-network-info-view">      
      <div v-if="lenGlobalGraphInfo.length > 0" class="global-graph-info">
        <!-- <span>global graph</span> -->
        <div id="global-box">
        	<p>	          		
        		|V|: {{globalGraphInfo.numnodes}}&nbsp&nbsp 
        		|E|: {{globalGraphInfo.numedges}}&nbsp&nbsp
        		directed: {{globalGraphInfo.directed}}
        	</p>
          <p>               
            |V|: {{globalGraphInfo.numnodes}}&nbsp&nbsp 
            |E|: {{globalGraphInfo.numedges}}&nbsp&nbsp
            directed: {{globalGraphInfo.directed}}
          </p>
          <p>               
            |V|: {{globalGraphInfo.numnodes}}&nbsp&nbsp 
            |E|: {{globalGraphInfo.numedges}}&nbsp&nbsp
            directed: {{globalGraphInfo.directed}}
          </p>
          <p>               
            |V|: {{globalGraphInfo.numnodes}}&nbsp&nbsp 
            |E|: {{globalGraphInfo.numedges}}&nbsp&nbsp
            directed: {{globalGraphInfo.directed}}
          </p>
          <p>               
            |V|: {{globalGraphInfo.numnodes}}&nbsp&nbsp 
            |E|: {{globalGraphInfo.numedges}}&nbsp&nbsp
            directed: {{globalGraphInfo.directed}}
          </p>
          <p>               
            |V|: {{globalGraphInfo.numnodes}}&nbsp&nbsp 
            |E|: {{globalGraphInfo.numedges}}&nbsp&nbsp
            directed: {{globalGraphInfo.directed}}
          </p>
          <p>               
            |V|: {{globalGraphInfo.numnodes}}&nbsp&nbsp 
            |E|: {{globalGraphInfo.numedges}}&nbsp&nbsp
            directed: {{globalGraphInfo.directed}}
          </p>
          <p>               
            |V|: {{globalGraphInfo.numnodes}}&nbsp&nbsp 
            |E|: {{globalGraphInfo.numedges}}&nbsp&nbsp
            directed: {{globalGraphInfo.directed}}
          </p>
          <p>               
            |V|: {{globalGraphInfo.numnodes}}&nbsp&nbsp 
            |E|: {{globalGraphInfo.numedges}}&nbsp&nbsp
            directed: {{globalGraphInfo.directed}}
          </p>
          <p>               
            |V|: {{globalGraphInfo.numnodes}}&nbsp&nbsp 
            |E|: {{globalGraphInfo.numedges}}&nbsp&nbsp
            directed: {{globalGraphInfo.directed}}
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
       
        globalGraphInfo: {}, // 全局图信息.
               
      }
    },
    computed:{
       lenGlobalGraphInfo: function(){
         return Object.keys(this.globalGraphInfo);
       },
       
    },
    methods: {     
       
    },
    created(){
      console.log("this.scaleOfSingleFocus created");
      let this_ = this;
      
      bus.$on("dbLoadedState", function(data){ // todo: 数据库装载成功后,直接获取全局图的各种统计信息.         
         if(data){
         
            let path = vueFlaskRouterConfig.networkInformation;
            axios.get(path)
            .then((res) => {
              
                // TODO: 以下是原来发送焦点+节点数量,获得DOI子图数据的代码,以后还要用的.
                console.log("后台已经响应graph information数据!");
                let data = res.data;  // 通过查询选中焦点,然后用焦点的id获得图数据.  
                this_.globalGraphInfo = data;
                // console.log(data);  
                //this_.$store.state.globalGraphView.globalGraphInfo = data; // 更新节点数量信息.  this_.$store.state.globalGraphView.globalGraphInfo.numnodes     
            })
            .catch((error) => {            
              console.error(error);
            });
         }         
      });      
    },
    mounted(){
    	let this_ = this;          
     
    },   
    
    beforeDestroy(){        
       bus.$off("dbLoadedState");  // 数据库装载成功.            
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