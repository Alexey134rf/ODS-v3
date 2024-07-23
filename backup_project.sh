#!/bin/bash

# Директории источника 
SOURCE_DIR="/root/docker_dev/ods_v3"
# Директории назначения
DEST_DIR="/var/Backups/ods_v3/"

# Формат даты
DATE=$(date +"%d-%m-%Y %H-%M")

# Имя файла резервной копии
BACKUP_FILE="$DEST_DIR/backup-$DATE.tar.gz"  

# Создание резервной копии
tar -czf "$BACKUP_FILE" /root/docker_dev/ods_v3  # Укажите путь к данным, которые нужно сохранить

# Удаление резервных копий старше 7 дней
find "$DEST_DIR" -type f -name "*.tar.gz" -mtime +7 -exec rm {} \;