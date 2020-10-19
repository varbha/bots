#!/bin/sh

cd /usr/src/app

mkdir clone_url_repo

cd clone_url_repo

git clone $1

cd $2

git diff --name-status origin/$4 origin/$3 > /usr/src/app/markdown-linux.txt

cd /usr/src/app 

rm -r clone_url_repo
