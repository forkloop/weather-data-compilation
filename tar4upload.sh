#! /bin/bash
# -*- coding: utf-8 -*-


# tar...
cd $HOME
YESTERDAY=`date +"%Y-%m-%d" -d "yesterday"`
DIR="weather-data-$YESTERDAY"
mkdir $DIR
cp bin/*$YESTERDAY*.dat $DIR
TAR_FILE="$DIR.tar.gz"
tar -czf $TAR_FILE $DIR

# uploading...
BUCKET="weather-data-compilation"
ruby upload_file.rb $BUCKET $TAR_FILE
