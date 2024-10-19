#!/bin/bash

cd /tmp/
sudo apt-get install zsh -y
wget https://gitee.com/mirrors/oh-my-zsh/raw/master/tools/install.sh 
chmod +x install.sh
sudo sed -i 's/REPO=${REPO:-ohmyzsh\/ohmyzsh}/REPO=${REPO:-mirrors\/oh-my-zsh}/' install.sh
sudo sed -i 's/REMOTE=${REMOTE:-https:\/\/github.com\/${REPO}.git}/REMOTE=${REMOTE:-https:\/\/gitee.com\/${REPO}.git}/' install.sh
./install.sh
cd ~/.oh-my-zsh
git remote set-url origin https://gitee.com/mirrors/oh-my-zsh.git
git pull
sudo chsh -s $(which zsh)

# passwd root
