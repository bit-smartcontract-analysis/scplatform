<template>
  <div class="container">
    <div class="split left">
      <h2 align="center">长安链·ChainMaker</h2>
      <br />
      <h1 align="center">数字信任经济的价值流动新引擎</h1>
    </div>
    <div class="box">
      <div class="logo">
        <img src="../assets/logo2.png" alt="" align="middle" />
      </div>
      <div class="context">
        <div class="text">我们提供一套面向长安链智能合约的漏洞检测系统</div>
        <br />

        <ul class="live">
          <li>智能合约</li>
          <li>漏洞检测工具</li>
          <li>智能合约检测</li>
          <li>合约检测成果</li>
        </ul>
        <br />
        <div class="box_a">
          <h4><a href="https://chainmaker.org.cn/home">长安链官网</a></h4>
          <em>|</em><span><a href="http://180.76.173.179/cms#/tool">合约检测</a></span>
        </div>
      </div>
    </div>
  </div>
</template>
<style scoped>
* {
  margin: 0;
  padding: 0;
}

a {
  text-decoration: none;
  color: black;
}

body {
  background-color: #f5f5f5;
}

.box {
  width: 280px;
  height: 360px;
  background-color: #fff;
  margin: 200px auto;
  border-radius: 14px;
}

.box img {
  width: 100%;
  border-radius: 14px 14px 0 0;
}

.box p {
  height: 100px;
  font-size: 14px;
  padding: 0 16px;
  margin-top: 20px;
}

.text {
  font-size: 14px;
  color: #cdcdcd;
  padding: 0 16px;
  margin-top: 10px;
}

.box_a {
  padding: 0 16px;
  margin-top: 20px;
}

.box_a h4 {
  display: inline-block;
  font-weight: 400;
  width: 130px;
  text-align: center;
}

.box_a h4 a:hover {
  color: #6594ff;
}

.box_a em {
  font-style: normal;
  margin: 0 16px 0 20px;
}

.box_a span {
  color: green;
}
.context {
  margin-top: -100px;
}

img {
  margin-top: -150px;
  object-fit: contain;
  text-align: center;
  margin-right: -70px;
}
.logo {
  height: 200px;
  width: 200px;
  text-align: center;
}
.selected {
  background-color: #cfd8dc !important;
  color: white;
}
.heroes {
  margin: 0 0 2em 0;
  list-style-type: none;
  padding: 0;
  width: 15em;
}
.heroes li {
  cursor: pointer;
  position: relative;
  left: 0;
  background-color: #eee;
  margin: 0.5em;
  padding: 0.3em 0;
  height: 1.6em;
  border-radius: 4px;
}
.heroes li.selected:hover {
  background-color: #bbd8dc !important;
  color: white;
}
.heroes li:hover {
  color: #607d8b;
  background-color: #ddd;
  left: 0.1em;
}
.heroes .text {
  position: relative;
  top: -3px;
}
.heroes .badge {
  display: inline-block;
  font-size: small;
  color: white;
  padding: 0.8em 0.7em 0 0.7em;
  background-color: #405061;
  line-height: 1em;
  position: relative;
  left: -1px;
  top: -4px;
  height: 1.8em;
  margin-right: 0.8em;
  border-radius: 4px 0 0 4px;
}
.live {
  overflow: hidden;
}
.live > li {
  list-style: none;
  position: relative;
  padding: 0 0 0 2em;
  margin: 0 0 0.5em 10px;
  -webkit-transition: 0.12s;
  transition: 0.12s;
}
.live > li::before {
  position: absolute;
  content: "\2022";
  font-family: Arial;
  color: black;
  top: 0;
  left: 0;
  text-align: center;
  font-size: 2em;
  opacity: 0.5;
  line-height: 0.75;
  -webkit-transition: 0.5s;
  transition: 0.5s;
}
.live > li:hover {
  color: green;
}
.live > li:hover::before {
  -webkit-transform: scale(2);
  -ms-transform: scale(2);
  transform: scale(2);
  opacity: 1;
  text-shadow: 0 0 4px;
  -webkit-transition: 0.1s;
  transition: 0.1s;
}

ol,
ul {
  width: 128%;
  display: inline-block;
  text-align: left;
  vertical-align: top;

  color: black;

  padding: 1.5em;
}
</style>
