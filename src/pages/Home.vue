<template>
  <div id="home">
    <h1>首页</h1>
  </div>
  <div class="sc-chart" id="board-post-count"></div>
  <div class="sc-chart" id="day7-post-count"></div>
</template>

<script>
import * as echarts from "echarts";
import { ElMessage } from 'element-plus';
export default {
  name: "AppHome",
  mounted() {
    this.loadBoardPostCountChat();
    this.load7DayPostCountChat();
  },
  methods: {
    loadBoardPostCountChat() {
      this.$http.getBoardPostCount().then((res) => {
        if(res['code' != 200]){
          ElMessage.error(res['message']);
          return;
        }
        var data = res['data'];
        var board_names = data['board_names'];
        var post_counts = data['post_counts'];
        var chartDom = document.getElementById("board-post-count");
        var myChart = echarts.init(chartDom);
        var option;

        option = {
          title: {
            text: '板块帖子数',
            x: "center",
            y: "bottom"
          },
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            type: "category",
            data:board_names,
          },
          yAxis: {
            type: "value",
          },
          series: [
            {
              data: post_counts,
              type: "bar",
              showBackground: true,
              backgroundStyle: {
                color: "rgba(180, 180, 180, 0.2)",
              },
            },
          ],
        };
        option && myChart.setOption(option);
      });
    },
    load7DayPostCountChat() {
      this.$http.getDay7PostCount().then(res =>{
        if(res['code'] !=200){
          ElMessage.error(res['message']);
          return;
        }
        var data = res['data']
        var dates = data['dates']
        var counts = data['counts']

        var chartDom = document.getElementById("day7-post-count");
        var myChart = echarts.init(chartDom);
        var option;

        option = {
          title: {
            text: '近7天帖子数量',
            x: "center",
            y: "bottom"
          },
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            type: "category",
            boundaryGap: false,
            data: dates,
          },
          yAxis: {
            type: "value",
          },
          series: [
            {
              data: counts,
              type: "line",
              areaStyle: {},
            },
          ],
        };

        option && myChart.setOption(option);
      })
   
    },
  },
};
</script>

<style scoped>
.sc-chart {
  height: 300px;
  width: 100%;
}
</style>