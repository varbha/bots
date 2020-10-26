#!/bin/bash

# Values for test
# repository=http://pcommgt01v/vendor/reds/mXPT/release/20210123/XFES.git
# workdir=/c/projects/gitbot/mrmaker
# markdownFile=$workdir/markdown-linux.txt
# releaseDate=20200901
# targetBranch=master
# sourceBranch=autotools
# baseTag=mockv1.0.0
# developer=Taeho
# engineerLeader=Takemura
# projectLeader=Varun

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
nameStatus_stv=$tmpdir/namestatus_stv
nameStatus_base=$tmpdir/namestatus_base
numStat_stv=$tmpdir/numstat_stv
numStat_base=$tmpdir/numstat_base
reportdir=/usr/src/app/$now
markdownFile=$reportdir/markdown-linux.txt
mvnRegex="\(pom.xml\|Maven\)"
opRegex="\(jboss\|OpenShift\|standalone\)"
stvTagRegex="_stv*"
masterTagRegex="master/[0-9][0-9][0-9][0-9][0-2][0-9][0-3][0-9]"
prefix=origin
developer=
engineerLeader=
projectLeader=

# Logic
[ ! -d $workdir ] && mkdir -p $workdir && cd $workdir
[ ! -d $destination ] && git clone -q $repository $destination
[ ! -d $reportdir ] && mkdir -p $reportdir
cd $destination
mkdir -p $tmpdir

baseTag=$(git tag -l $masterTagRegex | tail -1)
baseHash=$(git log $baseTag -1 --pretty=%H)
targetHash=$(git log $prefix/$targetBranch -1 --pretty=%H)
sourceHash=$(git log $prefix/$sourceBranch -1 --pretty=%H)
ancestor1=$(git merge-base $baseHash $targetHash)
ancestor2=$(git merge-base $baseHash $sourceHash)

# Check base
if [ "$baseHash" != "$ancestor1" -o "$baseHash" != "$ancestor2" -o "$ancestor1" != "$ancestor2" ]
then
    echo "[ERROR] Please check base tag of your branch again." > $markdownFile
    echo -e "Base tag: $baseTag  \nBase tag hash: $baseHash  \nAncestor base~target hash: $ancestor1  \nAncestor base~source hash: $ancestor2  \n" >> $markdownFile
fi

# Make diff table with previous _stv tag
diffHead="| No. | Status | File | Plus | Minus | Type |\n| --- | --- | --- | --- | --- | --- |\n"
previousStvTag=$(git tag -l $stvTagRegex | tail -1)
if [ ! -z "$previousStvTag" ]
then
    echo "前回移行申請したバージョン = $previousStvTag"
    git diff --name-status $previousStvTag $prefix/$sourceBranch > $nameStatus_stv
    git diff --numstat $previousStvTag $prefix/$sourceBranch > $numStat_stv

    diffBodyWithPreSt=$(awk 'FNR==NR {arr[FNR]="| "FNR" | "$1" | "$2" |"; next} {print arr[FNR], $1" | "$2" | App |"}' $nameStatus_stv $numStat_stv\
    | sed '/'"$opRegex"'/ s/ App |$/ Openshift |/'\
    | sed '/'"$mvnRegex"'/ s/ App |$/ Maven |/')

    diffTableWithPreSt=$diffHead$diffBodyWithPreSt
else
    echo "初回移行申請"
fi

# Make diff table with base tag
git diff --name-status $baseTag $prefix/$sourceBranch > $nameStatus_base
git diff --numstat $baseTag $prefix/$sourceBranch > $numStat_base

diffBodyWithBase=$(awk 'FNR==NR {arr[FNR]="| "FNR" | "$1" | "$2" |"; next} {print arr[FNR], $1" | "$2" | App |"}' $nameStatus_base $numStat_base\
| sed '/'"$opRegex"'/ s/ App |$/ Openshift |/'\
| sed '/'"$mvnRegex"'/ s/ App |$/ Maven |/')

diffTableWithBase=$diffHead$diffBodyWithBase

# Check artifact's changes
[[ $diffBodyWithBase =~ Openshift ]] && opChangeFlag=1
[[ $diffBodyWithBase =~ Maven ]] && mvnChangeFlag=1
configMapChangeFlag=0

# Make description file
echo -e "# MR [ $sourceBranch --> $targetBranch ]\n" >> $markdownFile
echo -e "## Basic Information\n" >> $markdownFile
echo -e "- 案件担当者: $developer" >> $markdownFile
echo -e "- EL: $engineerLeader" >> $markdownFile
echo -e "- PL: $projectLeader" >> $markdownFile
echo -e "- リリース日: $releaseDate" >> $markdownFile
echo -e "- 改修ベースタグ: $baseTag\n" >> $markdownFile
echo -e "## Additional Information\n" >> $markdownFile
[ "$opChangeFlag" == "1" ] && echo -e "1. [x] Openshift artifact変更有無" >> $markdownFile || echo -e "1. [ ] Openshift artifact変更有無" >> $markdownFile
[ "$mvnChangeFlag" == "1" ] && echo -e "2. [x] Maven artifact変更有無" >> $markdownFile || echo -e "2. [ ] Maven artifact変更有無" >> $markdownFile
[ "$configMapChangeFlag" == "1" ] \
    && echo -e "3. [x] Maven artifact変更有無" >> $markdownFile && echo -e "  - 置換条件一覧ファイル: [$configMapPath]($configMapPath)\n" >> $markdownFile \
    || echo -e "3. [ ] Maven artifact変更有無\n" >> $markdownFile
[ ! -z "$previousStvTag" ] && echo -e "## Diff [ $previousStvTag ~ $sourceBranch ]\n" >> $markdownFile && echo -e "$diffTableWithPreSt\n" >> $markdownFile
echo -e "## Diff [ $baseTag ~ $sourceBranch ]\n" >> $markdownFile
echo -e "$diffTableWithBase" >> $markdownFile


rm -r $workdir
