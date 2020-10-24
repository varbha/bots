#!/bin/bash

cd /usr/src/app

mkdir clone_url_repo

cd clone_url_repo

echo  https://$GITUSER:$GITPASS@gitlab.com/xfes/projects/20200817/a20-xfes-0002/xfes.git/

git clone https://$GITUSER:$GITPASS@gitlab.com/xfes/projects/20200817/a20-xfes-0002/xfes.git/

cd $2

git diff --name-status origin/$4 origin/$3 > /usr/src/app/markdown-linux.txt

cd /usr/src/app 

rm -r clone_url_repo
