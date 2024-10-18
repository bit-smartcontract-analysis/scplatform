# ，Apifox 和 JMeter 性能测试用例构造指南

首先使用 apifox 构造请求接口，并自测：

![image-20241018152445402](./assets/image-20241018152445402.png)

创建自动化测试：

![image-20241018152533559](./assets/image-20241018152533559.png)

添加步骤从接口导入，增加自动同步

![image-20241018153046440](./assets/image-20241018153046440.png)

![image-20241018153113693](./assets/image-20241018153113693.png)

运行测试自测保证请求正确：

![image-20241018153724001](./assets/image-20241018153724001.png)

导出 jmeter 格式，prod 环境

![image-20241018155427948](./assets/image-20241018155427948.png)

放到项目的 test 目录 的  jmeter 目录

![image-20241018155521927](./assets/image-20241018155521927.png)

开启 jmeter 

![image-20241018155620791](./assets/image-20241018155620791.png)

file open 打开 jmx 文件

![image-20241018155722956](./assets/image-20241018155722956.png)

delete 这个 parameter

![image-20241018155807116](./assets/image-20241018155807116.png)

![image-20241018155828570](./assets/image-20241018155828570.png)

点击 add 按照这个表单填写，注意

*  file 不要绝对路径， 只需要文件和 jmx 一个目录即可，
* browser 不要点无效
* 注意 parameter name 有的业务是 file 有的 是 files， 要和业务接口保持一致

![image-20241018155854928](./assets/image-20241018155854928.png)

![image-20241018160127124](./assets/image-20241018160127124.png)

ctrl+s 保存，并点击绿色播放按钮自测

![image-20241018160415052](./assets/image-20241018160415052.png)

查看结果树，测试通过

![image-20241018160916551](./assets/image-20241018160916551.png)