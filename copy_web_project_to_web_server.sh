#!/bin/bash

# Директории источника 
SOURCE_DIR_v1="/root/docker_dev/ods_v3"
SOURCE_DIR_v3="/root/docker_dev/ods_v3"
# Директории назначения
# Обязательно должна быть создана директория на Apache HTTP Server, в которую копируем web-проект 
DEST_DIR_v1="/var/www/html/ODS/"
DEST_DIR_v3="/var/www/html/ODS_v3/"

cp -r "$SOURCE_DIR_v1/Data_store/" $DEST_DIR_v1
cp -r "$SOURCE_DIR_v1/image/" $DEST_DIR_v1
cp -r "$SOURCE_DIR_v1/index.htm" $DEST_DIR_v1
cp -r "$SOURCE_DIR_v1/style.css" $DEST_DIR_v1

cp -r "$SOURCE_DIR_v3/Data_store/" $DEST_DIR_v3
cp -r "$SOURCE_DIR_v3/image/" $DEST_DIR_v3
cp -r "$SOURCE_DIR_v3/index.htm" $DEST_DIR_v3
cp -r "$SOURCE_DIR_v3/style.css" $DEST_DIR_v3