#!/bin/bash

# Variables
repository=$1
subsystemName=$2
targetBranch=$3
sourceBranch=$4
now=$5
releaseDate=$(echo $repository | awk -F/ '{print $(NF-1)}')
workdir=/usr/mr_maker_work/$releaseDate/$sourceBranch/$now
destination=$workdir/$subsystemName
tmpdir=$workdir/tmp
modifiedInstanceList=$tmpdir/modified_instance_list
releaseInstanceList=$tmpdir/release_instance_list
pomList=$tmpdir/pom_list
errorlog=$tmpdir/release_instance_finder_errorlog
reportdir=/usr/src/app/$now
releaseInstanceFile=$reportdir/release-instance-linux.txt
masterTagRegex="master/[0-9][0-9][0-9][0-9][0-2][0-9][0-3][0-9]"
prefix=origin
resultFlag=Successful

# Functions
pomVerCheck()
{
    result=$(awk -F '(<version>|</version>)' '/<artifactId>'"$1"'/,/<\/version>/ {print $2}' $2 | sed '/^$/d')

    [ "$result" != "" ] && echo $2 | awk -F/ '{print $3}' >> $releaseInstanceList &&
    for version in $result
    do
        [ $version != $artifactVersion ] \
            && echo "[ERROR]対象ファイル：$2::「$1」のバージョンが「$version」になっていて、想定バージョン「$artifactVersion」とは異なる。" >> $errorlog \
            && resultFlag=Failed
    done
}

# Logic
[ ! -d $workdir ] && mkdir -p $workdir && cd $workdir
[ ! -d $destination ] && git clone -q $repository $destination
[ ! -d $reportdir ] && mkdir -p $reportdir
cd $destination
mkdir -p $tmpdir

baseTag=$(git tag -l $masterTagRegex | tail -1)
artifactVersion=$releaseDate
git diff --name-status $baseTag $prefix/$sourceBranch | awk -F/ '/App/ && !/pom.xml/ {print $3}' | sort -u > $modifiedInstanceList
find App -name "pom.xml" > $pomList
[ -f $releaseInstanceList ] && rm $releaseInstanceList
[ -f $releaseInstanceFile ] && rm $releaseInstanceFile
[ -f $errorlog ] && rm $errorlog

while IFS= read -r instance
do
    while IFS= read -r pom
    do
        pomVerCheck $instance $pom
    done < $pomList
done < $modifiedInstanceList

sort -u $releaseInstanceList -o $releaseInstanceList

echo "# リリースインスタンス" >> $releaseInstanceFile
echo -e "\n## 基本情報" >> $releaseInstanceFile
echo -e "\n- ソースブランチ: $sourceBranch\n- 改修ベースタグ: $baseTag" >> $releaseInstanceFile
echo -e "\n## 改修サービス" >> $releaseInstanceFile
sed 's/^/- /g' $modifiedInstanceList >> $releaseInstanceFile
echo -e "\n## リリース対象インスタンス" >> $releaseInstanceFile
sed 's/^/- /g' $releaseInstanceList >> $releaseInstanceFile
echo -e "\n## Errorログ" >> $releaseInstanceFile
sed 's/$/\n/g' $errorlog >> $releaseInstanceFile
echo -e "\n## Pom artifact version更新検査結果" >> $releaseInstanceFile
echo -e "\n$resultFlag" >> $releaseInstanceFile

rm -rf $workdir
