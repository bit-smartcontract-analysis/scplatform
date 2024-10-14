# zlbbs-cms

## Project setup
```
yarn install
```

### Compiles and hot-reloads for development
```
yarn serve or npm run serve
```

### Compiles and minifies for production
```
yarn build  or  npm run build
```

### Lints and fixes files
```
yarn lint
```

### Customize configuration
See [Configuration Reference](https://cli.vuejs.org/config/).

## 与Flask集成
https://cli.vuejs.org/zh/config/

生成flask使用文件
npm run build -- --mode development

# Troubleshooting

## 外部用户访问 mysql

容器登录

mysql -u root -p

例如 
```
CREATE USER root@100.64.0.7 IDENTIFIED BY '000000'
CREATE USER root@100.64.0.28 IDENTIFIED BY '000000'
```
