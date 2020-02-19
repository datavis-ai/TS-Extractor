<template>
  <div id="over-view-global-heat-map">  
     <div id="heat-map-box">
       <canvas id="graph-heat-map"></canvas>
     </div>
     <!-- <div id="lasso-tool-box">
       <button id='lasso-tool-enable'>lasso</button>
       <button id='lasso-tool-cancel'>cancel</button>
       <button id='lasso-tool-lock'>lock</button>
     </div> -->
  </div>
</template>

<script>
  import $ from 'jquery'
  import * as d3 from '../../static/js/d3.v4.min.js'
  // import '../../static/js/lasso.dist.js'
  import axios from 'axios' // 用于AJAX请求 
  import {vueFlaskRouterConfig} from '../vueFlaskRouterConfig'
  import bus from '../eventbus.js' // 事件总线.

  export default {    
    data: function(){
      return {
        xyPoints: [], //保存布局好的节点.[{x:1123, y:456}, ...]
        kdeWidth: 200, //画布大小.
        kdeHeight: 200,

        // 两个参数: 格子大小,格子越小越平滑. h带宽过大过于平滑,太小只为一个点.
        gridSize: 2, //格子大小
        h: 4, //h=带宽
        qt: null,
        grid: null, //将 kdeWidth*kdeHeight 大小的画布划分成 gridSize*gridSize 的方格,grid=[{x:123, y:456}, ...],坐标是格子的中心.
        outerScale: null, // 一个指数函数.
        heatmapColor: null, //颜色映射函数.

        //套索样式设置.
        lassoAreaColor: "#33FFCC", //套索区域的颜色.
        lassoLineColor: "#33FFCC", //套索线的颜色.
        lassoStrokeDasharray: '3, 2', //套索线段长度 + 线段间距.
        fillOpacity: 0.2, //套索区域的透明度.
        strokeWidth: 2, // 套索虚线的粗细.

        // 套索选中的节点列表.
        selectedNodesInLasso: [], //选中的节点. [{x:x, y:x, id:x}, ...]
        clickSubgraphFlag: true, // 点击subgraph标志位.
      }
    },
    props:[
     'globallayoutdata' //属性名称.
    ],
    methods:{
      deleteEventInDiv(){
        // $("#view-graph > *").remove();
      },
      deleteGraphInSvg(svgId){
         $("#" + svgId + " > *").remove(); // 清除svg中旧的内容,包括各种事件.
       },
      polygonToPath(polygon) { //多边形.
        return ("M" + (polygon.map(function (d) { return d.join(','); }).join('L')));
      },
      lasooDistance(pt1, pt2) { //两个点之间的距离.
        return Math.sqrt(Math.pow( (pt2[0] - pt1[0]), 2 ) + Math.pow( (pt2[1] - pt1[1]), 2 ));
      },      
      lassoTool() { // 套索函数,此函数是闭包函数
        let this_ = this; // 全局上下文.
        let dispatch = d3.dispatch('start', 'end'); // 定义'start'+'end'两个自定义事件,自定义事件类似于click,dlclick元素自带事件.

        // distance last point has to be to first point before it auto closes when mouse is released
        let closeDistance = 75;
        let lockLasso = false; //用于锁住绘制好的套索,这样点击就不会删除.

        function lasso(root) { // root是d3的selection,即选中的元素,在该组件中是SVG.
          // append a <g> with a rect               
          let g = root.append('g').attr('class', 'lasso-group'); //创建一个g元素.
          let bbox = root.node().getBoundingClientRect(); // 获取SVG元素的位置和大小, 返回一个对象:{top:x,left:x,right:x,bottom:x,width:x, height:x}
          let area = g
            .append('rect')
            .attr('width', bbox.width)
            .attr('height', bbox.height)
            .attr('fill', 'tomato')
            .attr('opacity', 0); //在g元素中创建一个rect元素:矩形块元素,此元素的位置和大小与SVG一样,等于是将矩形框蒙在SVG上.

          let drag = d3 // 注册d3中鼠标拖拽时的三个事件:start,drag及end, 并将事件与回调函数绑定在一起.
            .drag()
            .on('start', handleDragStart)
            .on('drag', handleDrag)
            .on('end', handleDragEnd);
          
          // console.log("maomaomao area.call");
          area.call(drag); //将事件附在rect元素上. 这种调用drag函数对象的方式 等效于 drag(area).

          let lassoPolygon; //套索多边形
          let lassoPath; //套索路径:鼠标绘制过程的轨迹.
          let closePath; // 封闭套索路径: 当鼠标当前点与起始点的距离小于阈值时,自动将两点连接形成封闭套索区域的线段.

          function handleDragStart() { //拖拽开始.
            
            
            if(!lockLasso){
                // console.log("maomaomao handleDragStart");
                lassoPolygon = [d3.mouse(this)]; //套索的起始点坐标,即鼠标开始画套索的起点坐标.
                // console.log("lassoPolygon handleDragStart");console.log(lassoPolygon);
                if (lassoPath) { // 如果已经有了套索区域,则移除,保证只有当前绘制的套索区域.
                  lassoPath.remove(); // 这条语句保证重新绘制,或点击画布会删除之前的套索区域.
                }

                lassoPath = g // 在g内创建一个path元素.
                  .append('path')
                  .attr('fill', this_.lassoAreaColor) //套索区域的颜色. #0bb
                  .attr('fill-opacity', this_.fillOpacity) // this_.fillOpacity = 0.1
                  .attr('stroke', this_.lassoLineColor) //套索线的颜色.
                  .attr('stroke-width', this_.strokeWidth) //套索线的粗细
                  .attr('stroke-dasharray', this_.lassoStrokeDasharray); // 套索虚线. '3, 3':前者表示线段长, 后者表示线段间距.

                closePath = g
                  .append('line')
                  .attr('x2', lassoPolygon[0][0])  // 以套索的起始点作为封闭线段的终点. lassoPolygon=[[x, y], ...]
                  .attr('y2', lassoPolygon[0][1])
                  .attr('stroke', this_.lassoLineColor) // '#0bb'
                  .attr('stroke-width', this_.strokeWidth) //套索线的粗细
                  .attr('stroke-dasharray', this_.lassoStrokeDasharray)
                  .attr('opacity', 0); // opacity越小越透明.

                dispatch.call('start', lasso, lassoPolygon);

            }
            
          }

          function handleDrag() {
            if(!lockLasso){
                // console.log("maomaomao handleDrag");
                let point = d3.mouse(this);
                lassoPolygon.push(point); // 将鼠标经过的点存放到lassoPolygon中,lassoPolygon将点按照顺序连起来就是一个多边形.
                lassoPath.attr('d', this_.polygonToPath(lassoPolygon)); //将点数组传入,获得一个多边形路径,并在画布上画出来.

                // indicate if we are within closing distance
                if (
                  this_.lasooDistance(lassoPolygon[0], lassoPolygon[lassoPolygon.length - 1]) <
                  closeDistance
                ) { // 如果当前点与起始点的距离小于阈值,则绘制用于封闭的线段.
                  closePath
                    .attr('x1', point[0])
                    .attr('y1', point[1])
                    .attr('opacity', 1); //line不透明.
                } else {
                  closePath.attr('opacity', 0); //否则透明.
                }
            }
            
          }

          function handleDragEnd() {
            if(!lockLasso){
                // console.log("maomaomao handleDragEnd");
                // remove the close path
                closePath.remove(); // 删除line,避免重叠.
                closePath = null;

                // succesfully closed
                if (
                  this_.lasooDistance(lassoPolygon[0], lassoPolygon[lassoPolygon.length - 1]) <
                  closeDistance
                ) {
                  lassoPath.attr('d', this_.polygonToPath(lassoPolygon) + 'Z'); // SVG中path元素的d属性用于编码路径,举个例子:<path d="M120, 210L120, 110L110, 120Z"></path>表示以(120, 210)为起点,连接(120, 110),再连接(110, 120)最后形成闭环,连接到起点.
                  dispatch.call('end', lasso, lassoPolygon);

                  // otherwise cancel
                } else {
                  lassoPath.remove();
                  lassoPath = null;
                  lassoPolygon = null;
                }
            }
            
          }

          lasso.reset = function () {
            if (lassoPath) {
              lassoPath.remove();
              lassoPath = null;
            }

            lassoPolygon = null;
            if (closePath) {
              closePath.remove();
              closePath = null;
            }
          };
        }

        lasso.on = function (type, callback) {
          dispatch.on(type, callback);
          return lasso;
        };
        lasso.setLockLasso = function (flag){ // 用于设置lassoLock变量的方法,调用此方法用于锁定或解锁.
            lockLasso = flag;
        }
        // lasso.remove = function (){

        // }

        return lasso;
      },
      handleLassoEnd(lassoPolygon) { //选出套索中的节点集.
        let this_ = this;
        console.log("handleLassoEnd");
        let selectedPoints = this_.xyPoints.filter(function (d) { // 选定的点[{x:123, y:456}, ...]
             let x = d.x;
             let y = d.y;
             // lassoPolygon=[[x, y], [x, y], ...]
             return d3.polygonContains(lassoPolygon, [x, y]); //使用d3的polygonContains函数来判断[x, y]是否在指定的多边形内,如果在则将d返回存入selectedPoints数组中.
        });
        // console.log(selectedPoints);
        this_.selectedNodesInLasso = selectedPoints; //[{}, {}, {}, ...]

      },
      // reset selected points when starting a new polygon
      handleLassoStart(lassoPolygon) {
         console.log("start");
      },
      computeDensities (param) {
        /*
      　　param={
          　bandwidth: 4, //带宽大小,当bandwidthComputedMode=="common"有效.
          　densitiesComputedMode:"speedup", //密度估计计算模式,"speedup":利用barneshut树加速,"common":普通方式计算.
          　bandwidthComputedMode:"common" //带宽计算模式,"common":手动设置,bandwidth有效. "adaption":自适应,bandwidth失效.
      　　}
         核心部分:密度计算.
         参数：
         　hComputedMode:带宽计算模式."adaption":自适应, "common":一般模式.
        */
        let this_ = this;
        // Density at each (x,y) coordinate in the grid
        let densities = [];

        // Update bandwidth
        // Use same bandwidth for each dimension
        // 取出x坐标并按照大小排列,例如: xyPoints:[{x:1, y:2}, {x:44, y:6}, {x:7, y:9}] => xPoints:[1, 7, 44]
        let xPoints = this_.xyPoints.map(function(d) { return d.x }).sort(function(a,b) { return a - b });
        
        //自适应带宽估计,也可以自己自由设计.
        if(param.bandwidthComputedMode == "common"){ // 人为设置带宽．
          this_.h = param.bandwidth;
        }
        if(param.bandwidthComputedMode == "adaption"){ //自动估计带宽．
          let iqr = d3.quantile(xPoints, 0.75) - d3.quantile(xPoints, 0.25); //iqr = 第三个四分位数 - 第一个四分位数
          this_.h = 1.06 * Math.min(d3.deviation(xPoints), iqr / 1.34) * Math.pow(this_.xyPoints.length, -0.2); // d3.deviation:计算标准差.
        }
        if(param.densitiesComputedMode == "common"){ //一般模式.
            // Compute KDE for each (x,y) pair and update the color scale
            densities = this_.grid.map(function(point) { return this_.kdeBrute(point); }); //densities.length == grid.length
      //      outerScale.domain([0, d3.max(densities)]); //更改定义域为[0, d3.max(densities)]
      //      drawHeatmap(bruteContext, densities);
        }
        if(param.densitiesComputedMode == "speedup"){ //利用barneshut加速模式.
            let pointsList = []; //[[x, y], [x, y], ...]
            this_.xyPoints.forEach(function (p){
              let x = p.x;
              let y = p.y;
              pointsList.push([x, y]);
            });
            this_.qt = d3.quadtree(pointsList)
              .extent([[0, 0], [this_.kdeWidth, this_.kdeHeight]])
              .visitAfter(this_.accumulate);
            densities = this_.grid.map(function(point) { return this_.kdeBarneshut(point); });
      //      outerScale.domain([0, d3.max(densities)]); //更改定义域为[0, d3.max(densities)]
      //      drawHeatmap(barneshutContext, densities);
        }
        return densities;

      },
      renderHeatMap(densities, canvasContext){ //最后使用的API接口.
        /*
        densities: [x, x, ...]每个格子中心坐标的密度.
        canvasContext: 画布上下文.
        */
        let this_ = this;
        this_.outerScale.domain([0, d3.max(densities)]); //更改定义域为[0, d3.max(densities)]
        this_.drawHeatmap(canvasContext, densities);
      },
      drawHeatmap(context, densities) {
        let this_ = this;
        // Draw the grid
        //根据概率密度值,用颜色渲染格子
        this_.grid.forEach(function(point, idx) { //densities与grid一一对应.
          context.beginPath(); //启动路径绘制
          context.fillStyle = this_.heatmapColor(this_.outerScale(densities[idx])); //获得填充的颜色.
          // Subtract to get the corner of the grid cell
          context.rect(point.x - this_.gridSize/2, point.y - this_.gridSize/2, this_.gridSize, this_.gridSize);
          context.fill();
          context.closePath();
        });
      },
      accumulate(quad) {
        // Sum of x/y coordinates
        let sx = 0;
        let sy = 0;

        let count = 0, q;

        // This quadrant has children.
        if (quad.length) {
          let i = -1;
          let c;
          while (++i < 4) {
            c = quad[i];
            if (c == null) continue;
            count += c.count;
            sx += c.sx;
            sy += c.sy;
          }
        }

        // This is a leaf node.
        else {
          q = quad;
          do {
            count += 1;
            sx += q.data[0];
            sy += q.data[1];
          } while (q = q.next);
        }

        quad.sx = sx;
        quad.sy = sy;
        quad.count = count;
      },
      kdeBrute(gridPoint) { //gridPoint 一个坐标点, h带宽(核半径)
        // 节点实际位置xyPoints=[{x:1, y:2}, {x:3, y:4}, {x:5, y:6}]  格子中心位置gridPoint={x:4.5, y:6.5}  注意:由于使用的是标准核函数,故而除以带宽:distance(p, gridPoint) / h
        /*
          gridPoint是一个格子中心的坐标,xyPoints是布局好的节点的坐标,节点都是密度=1的点,现在要估计每个格子中心的密度值.估计方法:
          1. 先计算gridPoint与xyPoints中每个节点的距离,然后除以带宽h归一化,接着带入核函数中计算出gridPoint相对该节点的密度值,再求平均值,最后平局值/面积(h*h),得到gridPoint所在的单位面积密度值.
        */
        let this_ = this;
        return d3.mean(this_.xyPoints, function(p) { return this_.kernelFunction(this_.distance(p, gridPoint) / this_.h); });// / (h*h); //得到单位面积的密度大小.
      },

      kdeBarneshut(gridPoint) {
        let this_ = this;
        let estimate = 0;
        // let theta2 = 0.64; // 原来的值取0.64
        let theta2 = 0.64;      

        this_.qt.visit(function (quadNode, x1, y1, x2, y2) {
          
          // Average x/y coordinates in this quadrant.
          let xx = quadNode.sx/quadNode.count;
          let yy = quadNode.sy/quadNode.count;
          let p = {x: xx, y: yy}; //构建一个对象．
          let dx = p.x - gridPoint.x;
          let dy = p.y - gridPoint.y;
          let dw = x2 - x1;
          let dist = dx * dx + dy * dy;

          // Barnes-Hut: If the quadrant size is small relative to its
          // distance from the grid point, then aggregate the points in
          // that quadrant and treat them as a single large point (or many
          // individual points all in the same location).
          if (dw * dw / theta2 < dist && !(gridPoint.x >= x1 && gridPoint.x < x2 && gridPoint.y >= y1 && gridPoint.y < y2)) {
            estimate += quadNode.count * this_.kernelFunction(this_.distance(p, gridPoint) / this_.h);
            return true;
          }

          if (quadNode.point) {
            let distanceHere = Math.sqrt((quadNode.point[0] - gridPoint.x) * (quadNode.point[0] - gridPoint.x) + (quadNode.point[1] - gridPoint.y) * (quadNode.point[1] - gridPoint.y));
            estimate += this_.kernelFunction(distanceHere / this_.h);
          }

          // Stop recursing if there are no more nodes.
          return !quadNode.count;
        });

        return estimate / this_.xyPoints.length;
      },
      
      distance(v1, v2) { //v1与v2间的距离.
        return Math.sqrt((v1.x - v2.x) * (v1.x - v2.x) + (v1.y - v2.y) * (v1.y - v2.y));
      },

      kernelFunction(x) { //标准: 均值=0,方差=1
        // sqrt(2 * PI) is approximately 2.5066
        let mode = "Gaussian"; //核函数.

        if(mode == "Gaussian"){
          return Math.exp(-x * x / 2) / 2.5066;
        }

        if(mode == "Quartic"){
           return 0.9375*Math.pow((1 - x*x), 2);
        }

        if(mode == "Epanechnikov"){
          return 0.75*(1 - x*x);
        }

        if(mode == "Triweight"){
          return 1.09375*Math.pow((1 - x*x), 3);
        }

      }

    },
    created(){
      let this_ = this;
      this_.kdeWidth = this_.$store.state.globalGraphView.width; // 画布大小设置.
      this_.kdeHeight = this_.$store.state.globalGraphView.height;
      //完成一系列变量的初始化.
      this_.grid = d3.merge(d3.range(0, this_.kdeHeight/this_.gridSize).map(function(i) {
          return d3.range(0, this_.kdeWidth/this_.gridSize).map(function(j) { return {x: j*this_.gridSize + this_.gridSize/2, y: i*this_.gridSize + this_.gridSize/2} });
      }));
      this_.outerScale = d3.scalePow() //指数函数. y=f(x)
                         .exponent(0.4) //指数=0.4
                         .domain([0,1]) //定义域
                         .range([0,1]); //值域
      this_.heatmapColor = d3.scaleLinear() //颜色分段函数 y=f(x)
                        .clamp(true)
                        .domain([0, 0.1111111111111111, 0.2222222222222222, 0.3333333333333333, 0.4444444444444444, 0.5555555555555555, 0.6666666666666666, 0.7777777777777777, 0.8888888888888888, 1])
                        .range(['#ffffff','#fff7f3','#fde0dd','#fcc5c0','#fa9fb5',
                          '#f768a1','#dd3497','#ae017e','#7a0177','#49006a']);
    },
    mounted(){
      let this_ = this;
      this_.deleteEventInDiv(); //删除DIV内的事件等内容.
      let visRoot = d3.selectAll("#heat-map-box") // div:用于装 canvas + svg, canvas:画点, svg:套索.
                      .style('position', 'relative');

      let canvasContext = d3.selectAll("#graph-heat-map")
                            .attr("width", this_.kdeWidth)
                            .attr("height", this_.kdeHeight);
      let graphCanvasContext = canvasContext.node().getContext("2d"); //2D画布.

      // d3.json("../../static/json/connected_max_subgraph_citation_network_visualization.json", function(error, graph_) {
         let graph = JSON.parse(JSON.stringify(this_.globallayoutdata)); //深度
         let nodes = graph["nodes"]; //[{id:"1234", x:1.2, y:3.3}, ...]
         //这么用的前提是:nodes中的坐标都是非负数.
         let xMaxVal = -1;
         let xMinVal = 100000;
         let yMaxVal = -1;
         let yMinVal = 100000;

         nodes.forEach(function (node, idx){
            let x = node.x;
            let y = node.y;

            //找x最大值.
            if(x >= xMaxVal){
              xMaxVal = x;
            }

            //找x最小值
            if(x <= xMinVal){
              xMinVal = x;
            }

            //找y最大值
            if(y >= yMaxVal){
              yMaxVal = y;
            }

            //找y最小值
            if(y <= yMinVal){
              yMinVal = y;
            }
         });

         let fx = this_.kdeWidth / (xMaxVal - xMinVal); //x轴的变换因子.
         let fy = this_.kdeHeight / (yMaxVal - yMinVal); //y轴的变换因子.

         nodes.forEach(function (node, idx){
            let x = node.x * fx - fx*xMinVal;
            let y = node.y * fy - fy*yMinVal;
            let nodeId = node.id; //节点id.
            this_.xyPoints.push({x: x, y: y, id:nodeId}); //xyPoints里面装的是坐标变换之后的节点,{x:x, y:y, id:nodeId}
         });
        
         let param = {};
         if(this_.$store.state.infoSearchView.numNodes < 3000){ // 如果全局图的节点数量小于3000,则使用普通模式.
            param={
               bandwidth: 4, //带宽大小,当bandwidthComputedMode=="common"有效.
               densitiesComputedMode:"common", //密度估计计算模式,"speedup":利用barneshut树加速,"common":普通方式计算,在vue框架下,数据量过大,浏览器崩溃.
               bandwidthComputedMode:"common" //带宽计算模式,"common":手动设置,bandwidth有效. "adaption":自适应,bandwidth失效.
            };
         }
         else{
            param={
              bandwidth: 4, //带宽大小,当bandwidthComputedMode=="common"有效.
              densitiesComputedMode:"speedup", //密度估计计算模式,"speedup":利用barneshut树加速,"common":普通方式计算,在vue框架下,数据量过大,浏览器崩溃.
              bandwidthComputedMode:"common" //带宽计算模式,"common":手动设置,bandwidth有效. "adaption":自适应,bandwidth失效.
            };
         }
        
         //  let param={
         //    bandwidth: 4, //带宽大小,当bandwidthComputedMode=="common"有效.
         //    densitiesComputedMode:"common", //密度估计计算模式,"speedup":利用barneshut树加速,"common":普通方式计算,在vue框架下,数据量过大,浏览器崩溃.
         //    bandwidthComputedMode:"common" //带宽计算模式,"common":手动设置,bandwidth有效. "adaption":自适应,bandwidth失效.
         // };
         // TODO: 可以在这里加上一个节点阈值,一旦低于这个值使用普通渲染模式以获得平滑的热力图.
         let densities = this_.computeDensities(param);
         let canvasContext_ = graphCanvasContext;
         this_.renderHeatMap(densities, canvasContext_);
         
         // add in an interaction layer as an SVG
         let interactionSvg = visRoot // 定义一个SVG画布.
            .append('svg')
            .attr('width', this_.kdeWidth)
            .attr('height', this_.kdeHeight)
            .style('position', 'absolute') // 样式设置成这样保证SVG这套索图层完全蒙在canvas上.
            .style('top', 0)
            .style('left', 0);

          //attach lasso to interaction SVG
          // let lassoInstance = this_.lasso()
          //     .on('start', this_.handleLassoStart)
          //     .on('end', this_.handleLassoEnd);
          // interactionSvg.call(lassoInstance);
          
          // 定义套索实例.
          let lassoInstance = this_.lassoTool()
                .on('start', this_.handleLassoStart)
                .on('end', this_.handleLassoEnd); 
          
          $("#lasso-icon-box").unbind(); //先解绑#lasso-icon-box上的事件,保证只注册一个事件.
          $("#lasso-icon-box").click(function (e){ //使能套索.#lasso-icon-box元素在globalGraphView.vue中定义.
            if(this_.clickSubgraphFlag){
                // console.log("heatMap");
                this_.deleteGraphInSvg(this_.$store.state.globalFilteredSubgraphView.svgId); //点击套索图标,删除svg中的图及其绑定的事件.
                this_.clickSubgraphFlag = false;
                this_.$store.state.globalFilteredSubgraphView.isOpenFilteredSubgraph = false; //点击失能子图.
                this_.selectedNodesInLasso = []; // 清空选中列表.
                this_.$store.state.globalFilteredSubgraphView.globalFilteredGraph = null; //清空store.js中过滤子图.
                let cssLasso = {
                  "background":"#409EFF",
                  "color":"#fff"
                };
                $("#lasso-icon-box").css(cssLasso); //用黑圈圈起来.

                let cssSubGraph = {
                  "background":"#ddd",
                  "color":"#000"
                };
                $("#check-filter-subgraph").css(cssSubGraph); //用黑圈圈起来.

                lassoInstance.setLockLasso(false);
                // attach lasso to interaction SVG 
                interactionSvg.selectAll("g").remove(); // 删除svg里面的旧的g元素.                 
                interactionSvg.call(lassoInstance); //将套索附在SVG上.这种写法等价于lassoInstance(interactionSvg), 这种写法的好处是可以链式写法.
                bus.$emit("clearGraphEVFlag", true); //发送清除|V| + |E|信号
               
            }
            

          });
      
          $("#check-filter-subgraph").unbind(); //先解绑#lasso-icon-box上的事件,保证只注册一个事件.
          $("#check-filter-subgraph").click(function (e){ // #check-filter-subgraph元素在globalGraphView.vue中定义.
            if(this_.clickSubgraphFlag === false){
                this_.clickSubgraphFlag = true;
                this_.$store.state.globalFilteredSubgraphView.isOpenFilteredSubgraph = true; //点击打开子图.
                let cssLasso = {
                   "background":"#ddd",
                   "color":"#000"
                };
                $("#lasso-icon-box").css(cssLasso); //用黑圈圈起来.

                let cssSubGraph = {
                  "background":"#409EFF",
                  "color":"#fff"
                };
                $("#check-filter-subgraph").css(cssSubGraph); //用黑圈圈起来.

                lassoInstance.setLockLasso(true); //锁定套索.
                bus.$emit("sendSelectedNodesInLasso", this_.selectedNodesInLasso); // 发送选中的节点数据到globalFilteredSubgraphView.vue组件中.
                
                // todo:下面对过滤出来的子图进行可视化展示.
                console.log("this_.selectedNodesInLasso");console.log(this_.selectedNodesInLasso);
                // bus.$emit("sendViewResize", 30); // 测试resize控件.


            }
            
          });
    // });
    },
    beforeDestroy(){
      
    } 
  }
</script>

<style>
#over-view-global-heat-map{
  position: relative;
}
 /*#lasso-tool-box{
   width:40px;
   height:40px;
   position: absolute;
   top: 0;
   right: 0;
 }*/
 #lasso-tool{
   /*width:40px;
   height:40px;*/

 }
</style>