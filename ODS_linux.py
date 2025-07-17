from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import codecs
import datetime as dt
import time
import os
import os.path
import shutil
import re
import pdf2image
from PIL import Image
import base64


# # FOR WINDOWS
# # Изменение рабочего каталога
# os.chdir(os.path.join(os.getcwd(), 'Скрипты СЦ ГВО\ODS'))
# FOR LINUX
# Изменение рабочего каталога
os.chdir(os.path.join(os.getcwd(), '/root/ods_v3_lxc/lxc_project'))

LINK_TO_SITE = 'http://email.volganet.ru/'
# LINK_TO_SITE = 'https://email.volganet.ru/?Skin=Samoware'
MAX_INBOX_PAGES = 3

PATH_DIR_REPORT = os.path.join(os.getcwd(), "Report")
# # FOR WINDOWS
# PATH_DIR_DOWNLOADS = os.path.join(f"c:\\Users\\{os.getlogin( )}\\Downloads")
# FOR LINUX
PATH_DIR_DOWNLOADS = os.getcwd()

PATH_DIR_DATA_STORE = os.path.join(os.getcwd(), "Data_store")
PATH_DIR_PDF = os.path.join(os.getcwd(), "Data_store", 'pdf')
PATH_DIR_ARCHIVE_PDF = os.path.join(os.getcwd(), "Data_store", 'archive_pdf')
PATH_DIR_TMP_SOURCE_IMAGES = os.path.join(PATH_DIR_DATA_STORE, "tmp_files", "source_images")
PATH_DIR_IMAGE_FROM_PDF = os.path.join(PATH_DIR_DATA_STORE, "image_from_pdf")
PATH_DIR_ARCHIVE_IMAGE_FROM_PDF = os.path.join(PATH_DIR_DATA_STORE, "archive_image_from_pdf")

GROUP_NAME_FORECAST_VO = 'Прогноз ЧС ВО'
GROUP_NAME_FORECAST_UFO = 'Прогноз ЧС по ЮФО'
GROUP_NAME_FORECAST_EVERY_WEEK = 'Прогноз ВО недельный'
GROUP_NAME_FORECAST_INFORMATION_REPORT = 'Информационное донесение'
GROUP_NAME_FORECAST_4MOD = '4МОД'
LIST_ALL_GROUP_NAME = [GROUP_NAME_FORECAST_VO, GROUP_NAME_FORECAST_UFO, GROUP_NAME_FORECAST_EVERY_WEEK, GROUP_NAME_FORECAST_INFORMATION_REPORT, GROUP_NAME_FORECAST_4MOD]

# Задать дату, звонки до данный даты, если имеются в списке найденных сообщений от ОДС, 
# будут исключены из процесса парсинга  
START_DAY_AND_TIME_PARSER = dt.datetime(2024, 1, 10, 0, 0)
IS_START_DAY_AND_TIME_PARSER_SET_AUTOMATIC = True

date_and_time_start_parser = dt.datetime.now().strftime('%d.%m.%Y %H-%M')
path_to_file_report = os.path.join(PATH_DIR_REPORT, f"Status parser {date_and_time_start_parser}.txt")

parser_report = f"Дата и время запуска парсера: {date_and_time_start_parser}\n"
parser_report_errors = '\nСтатус по ошибкам:'
parser_report_find_messages_all = '\nВсе найденные сообщения:\n'
parser_report_find_messages_ods_all = '\n\nВсе найденные сообщения от ОДС:\n'
parser_report_messages_ods_all_choices = '\n\nВсе сообщения от ОДС, которые выбраны исходя из наличия в хранилище данных:\n'
parser_report_added_files = '\nСтатус по добавлению скаченных файлов в проект:\n'
removed_file_from_storage = '\n\nУдалены неактуальные файлы из хранилища:'


def rename_download_files(download_files, messages_ods_time_on_mail):
    list_download_files_of_parser = list()
    
    for download_file in download_files:
        if ".pdf" in download_file.lower():
            if GROUP_NAME_FORECAST_4MOD.lower() in download_file.lower():
                download_file_rename = os.path.join(PATH_DIR_DOWNLOADS, GROUP_NAME_FORECAST_4MOD + " " + messages_ods_time_on_mail + ".pdf")
                os.rename(os.path.join(PATH_DIR_DOWNLOADS, download_file), download_file_rename)
            elif GROUP_NAME_FORECAST_VO.lower() in download_file.lower():
                download_file_rename = os.path.join(PATH_DIR_DOWNLOADS, GROUP_NAME_FORECAST_VO + " " + messages_ods_time_on_mail + ".pdf")
                os.rename(os.path.join(PATH_DIR_DOWNLOADS, download_file), download_file_rename)
            elif GROUP_NAME_FORECAST_UFO.lower() in download_file.lower():
                download_file_rename = os.path.join(PATH_DIR_DOWNLOADS, GROUP_NAME_FORECAST_UFO + " " + messages_ods_time_on_mail + ".pdf")
                os.rename(os.path.join(PATH_DIR_DOWNLOADS, download_file), download_file_rename)
            elif GROUP_NAME_FORECAST_EVERY_WEEK.lower() in download_file.lower():
                download_file_rename = os.path.join(PATH_DIR_DOWNLOADS, GROUP_NAME_FORECAST_EVERY_WEEK + " " + messages_ods_time_on_mail + ".pdf")
                os.rename(os.path.join(PATH_DIR_DOWNLOADS, download_file), download_file_rename)
            elif GROUP_NAME_FORECAST_INFORMATION_REPORT.lower() in download_file.lower():
                download_file_rename = os.path.join(PATH_DIR_DOWNLOADS, GROUP_NAME_FORECAST_INFORMATION_REPORT + " " + messages_ods_time_on_mail + ".pdf")
                os.rename(os.path.join(PATH_DIR_DOWNLOADS, download_file), download_file_rename)
            else:
                print(f"Deleted invalid file from {PATH_DIR_DOWNLOADS} -> {download_file}")
                os.remove(os.path.join(PATH_DIR_DOWNLOADS, download_file))
                continue

            list_download_files_of_parser.append(download_file_rename)
        else:
            # Удаление файлов, которые не соответствуют .pdf
            os.remove(os.path.join(PATH_DIR_DOWNLOADS, download_file))
        
    return list_download_files_of_parser


def find_last_file_of_group(group_name, path_dir):
    all_files_name = [filename for filename in os.listdir(path_dir) if group_name.lower() in filename.lower()]
    all_files_time = [dt.datetime.strptime(re.search(r"[0-3]*[0-9][.][0-1][0-9][.][1-2][0-9][0-9][0-9]\s[0-2][0-9][-][0-5][0-9]", filename).group(), '%d.%m.%Y %H-%M') for filename in os.listdir(path_dir) if group_name.lower() in filename.lower()]
    last_file_name = all_files_name[all_files_time.index(max(all_files_time))]
    last_file_time = max(all_files_time)
    
    return {'file_name': last_file_name, 'datetime': last_file_time}


def find_last_file_data_store(list_all_group_name, path_dir):
    all_files_name = list()
    all_files_time = list()
    
    for group_name in list_all_group_name:
        all_files_name.append(find_last_file_of_group(group_name=group_name, path_dir=path_dir).get('file_name', None))
        all_files_time.append(find_last_file_of_group(group_name=group_name, path_dir=path_dir).get('datetime', None))
    
    last_file_name = all_files_name[all_files_time.index(max(all_files_time))]
    last_file_time = max(all_files_time)
    return {'file_name': last_file_name, 'datetime': last_file_time}


def check_is_downloaded_files(time_start_download):
    waiting_time = 11
    
    time.sleep(1.5)
    download_files_list_after_click = [[filename, os.stat(os.path.join(PATH_DIR_DOWNLOADS, filename)).st_mtime] for filename in os.listdir(PATH_DIR_DOWNLOADS)] 
    download_files_new = [file[0] for file in download_files_list_after_click if file[1] >= time_start_download]
    
    for second in range(waiting_time):
        if any([True for file in download_files_new if os.path.isfile(os.path.join(PATH_DIR_DOWNLOADS, file)) and ('Не\xa0подтверждено' in file or '.crdownload' in file)]):
            time.sleep(2)
        else:
            time.sleep(5)
            break
        
        assert  second != waiting_time - 1 , f"Не удалось загрузить фалы в течении {waiting_time} сек."


def transport_downloaded_files_local_storage(list_download_files):
    parser_report_added_files_list = list()
    # Список всех файлов:
    list_all_data_store_files = [filename for filename in os.listdir(PATH_DIR_PDF)]
    
    # Проверка принадлежности загруженных файлов необходимым группам
    # list_download_files = [file_name for file_name in list_download_files if GROUP_NAME_FORECAST_VO in file_name or GROUP_NAME_FORECAST_UFO in file_name or GROUP_NAME_FORECAST_EVERY_WEEK  in  file_name or GROUP_NAME_FORECAST_INFORMATION_REPORT in file_name or GROUP_NAME_FORECAST_4MOD in file_name]

    for ful_path_download_file in list_download_files:
        ful_path_data_store_file =  os.path.join(PATH_DIR_PDF, os.path.basename(ful_path_download_file))
       
        if os.path.basename(ful_path_download_file).lower() not in (" ").join(list_all_data_store_files).lower() and ".pdf" in os.path.basename(ful_path_download_file).lower() and "~" not in os.path.basename(ful_path_download_file).lower():
            shutil.copyfile(ful_path_download_file, ful_path_data_store_file)
            
            os.remove(ful_path_download_file)
            print(f"File: {ful_path_download_file} added to {PATH_DIR_PDF}")
            parser_report_added_files_list.append(f"File: {ful_path_download_file} added to {PATH_DIR_PDF}")  
        else:
            os.remove(ful_path_download_file)
            print(f"File: {ful_path_download_file} don't add to {PATH_DIR_PDF}")
            parser_report_added_files_list.append(f"File: {ful_path_download_file} don't add to {PATH_DIR_PDF}")  

    # Подготовка отчета по статусу добавления файлов в хранилище проекта
    parser_report_added_files_str = "\n".join([str(i + 1) + " " + parser_report_added_files_list[i] for i in range(len(parser_report_added_files_list))])
    add_info_in_report_parser(path_to_file_report=path_to_file_report, mode_open_file='a', 
                              text_for_add=(parser_report_added_files + parser_report_added_files_str))     


def pdf_to_jpg(path_file_pdf, poppler_path="C:\\poppler-24.02.0\\Library\\bin", is_linux=False):
    # В аргументе poppler_path указываем место, где находится папка bin исходных файлов Poppler
    try:
        if is_linux:
            images_from_pdf = pdf2image.convert_from_path(path_file_pdf)
        else:
            images_from_pdf = pdf2image.convert_from_path(path_file_pdf, poppler_path=poppler_path)
    except Exception as e:
        exception_user_text = f"""\nФайл поврежден: {path_file_pdf}
        Файл поврежден: {path_file_pdf}
        Описание ошибки: {e}
        Данный файл был удален из директории: .\Data_store"""
        os.remove(path_file_pdf)
        print(exception_user_text)
        
        parser_report_errors_loc = parser_report_errors + "\n2. Ошибка при поиске и конвертации pdf файлов в png" + exception_user_text
        add_info_in_report_parser(path_to_file_report=path_to_file_report, mode_open_file='a', 
                              text_for_add=parser_report_errors_loc)
        return False
    else:
        for i in range(len(images_from_pdf)):
            images_from_pdf[i].save(os.path.join(PATH_DIR_TMP_SOURCE_IMAGES, f"image{i}.jpg"), 'JPEG') 
        return True
        
        
def create_result_image(name_file_png):
    images_from_dir_tmp = sorted([file for file in os.listdir(PATH_DIR_TMP_SOURCE_IMAGES) if '~' not in file and '.gitkeep' not in file])
    
    with  Image.open(os.path.join(PATH_DIR_TMP_SOURCE_IMAGES, images_from_dir_tmp[0])) as _img:
        result_image_width = _img.size[0]
        result_image_height = _img.size[1]
    
    result_image = Image.new('RGB', (result_image_width, result_image_height * len(images_from_dir_tmp) + 45 * (len(images_from_dir_tmp) - 1)))
    hight_count = 0

    for i in range(len(images_from_dir_tmp)):
        with Image.open(os.path.join(PATH_DIR_TMP_SOURCE_IMAGES, images_from_dir_tmp[i])) as image_opened:
            result_image.paste(image_opened, (0, hight_count))
            hight_count +=  result_image_height
            result_image.paste(Image.new('RGB', (0, 45), '#FFFFFF'), (0, hight_count))
            hight_count += 45   
            
    result_image = result_image.reduce(2)
    result_image.save(os.path.join(PATH_DIR_IMAGE_FROM_PDF, f"{name_file_png}.png"))
    
    for file in images_from_dir_tmp:
        os.remove(os.path.join(PATH_DIR_TMP_SOURCE_IMAGES, file))


def convert_image_to_base64(image_path):
    with open(image_path, 'rb') as img:
        return base64.b64encode(img.read()).decode('utf-8')        


# TODO: deprecate. Файлы с 29.05.2024 больше не добавляются в архив, а удаляются
def data_store_files_send_to_archive(source_dir_path, insert_dir_path, file_group, file_group_max_date, number_files_store_days=5):

    list_files_data_store = os.listdir(source_dir_path)
    list_files_and_dates = [[file, dt.datetime.strptime(re.search(r"[0-3]*[0-9][.][0-1][0-9][.][1-2][0-9][0-9][0-9]\s[0-2][0-9][-][0-5][0-9]", file).group(), '%d.%m.%Y %H-%M')] for file in list_files_data_store if file_group in file]
    file_group_min = dt.datetime.combine((file_group_max_date - dt.timedelta(days=number_files_store_days)).date(), dt.time(0, 0))

    list_files_insert_to_archive = [file[0] for file in list_files_and_dates if file[1] < file_group_min]

    for file in list_files_insert_to_archive:
        file_current_path = os.path.join(source_dir_path, file)
        file_insert_path = os.path.join(insert_dir_path, file)
        
        shutil.copyfile(file_current_path, file_insert_path)
        os.remove(file_current_path)
        print(f"File {file_current_path} added to {file_insert_path}")

        
def clear_data_store_files(source_dir_path, file_group, file_group_max_date, number_files_store_days=5):

    list_files_data_store = os.listdir(source_dir_path)
    list_files_and_dates = [[file, dt.datetime.strptime(re.search(r"[0-3]*[0-9][.][0-1][0-9][.][1-2][0-9][0-9][0-9]\s[0-2][0-9][-][0-5][0-9]", file).group(), '%d.%m.%Y %H-%M')] for file in list_files_data_store if file_group in file]
    file_group_min = dt.datetime.combine((file_group_max_date - dt.timedelta(days=number_files_store_days)).date(), dt.time(0, 0))

    list_files_for_remove = [file[0] for file in list_files_and_dates if file[1] < file_group_min]

    for file in list_files_for_remove:
        file_current_path = os.path.join(source_dir_path, file)
        
        os.remove(file_current_path)
        massage_user = f"\nFile {file_current_path} removed from data_store"
        add_info_in_report_parser(path_to_file_report=path_to_file_report, mode_open_file='a', 
                              text_for_add=massage_user)
        print(massage_user)    


def add_info_in_report_parser(path_to_file_report, mode_open_file, text_for_add):
    """mode_open_file:
    1) 'r' (чтение) - открывает файл только для чтения. Это значение по умолчанию. 
2) 'w' (запись) - открывает файл только для записи. Если файл не существует, он будет создан. Если файл существует, его содержимое будет удалено. 
3) 'x' (создание) - открывает файл только для записи. Если файл уже существует, возникнет ошибка. 
4) 'a' (добавление) - открывает файл для добавления данных в конец файла. Если файл не существует, он будет создан. 
5) 'b' (бинарный) - открывает файл в бинарном режиме. Используется для работы с бинарными данными, такими как изображения или аудио. 
6) '+' (чтение и запись) - открывает файл для чтения и записи. 
Режимы могут быть объединены, например 'rb' для чтения бинарного файла или 'w+' для чтения и записи."""
    
    with open(path_to_file_report, mode_open_file) as f:
        f.write(text_for_add)


def record_current_list_files_from_storage(text_header, path_dir):
    list_files = os.listdir(path_dir)
    list_files_for_report = text_header + "\n".join([str(i + 1) + " " + list_files[i]  for i in range(len(list_files))]) + "\n"
    
    add_info_in_report_parser(path_to_file_report=path_to_file_report, mode_open_file='a', 
                              text_for_add=list_files_for_report) 


# Создание скриншота сайта
# browser.get_screenshot_as_file('screenshot3.png')

# 1.	Парсинг файлов с почты 
try:
    options = webdriver.ChromeOptions()
    # options.add_argument("--start-maximized")
    
    # FOR LINUX
    # Работа c Chromedriver в режиме headless (консольный режим)
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    
    # Добавляем игнорирование ошибок сертификатов
    options.add_argument('--ignore-certificate-errors')
    
    browser = webdriver.Chrome(options)
    
    # !!!Важно: при изменении разрешения экрана, меняется атрибуты тегов (классы, …), бывает и так!
    # Селекторы элементов находились при разрешении: 1920х1080
    browser.set_window_size(1920, 1080)
    
    browser.implicitly_wait(15)
    browser.get(LINK_TO_SITE)
    
    # Создание скриншота браузера
    # browser.save_screenshot("screenshot.png")
    
    # 1. Авторизация на почте  
    # Select the Login box
    Login_box = browser.find_element(By.NAME, 'username')
    # Send Login box information
    Login_box.send_keys('d_korostelev')
    # Find password box
    password_box = browser.find_element(By.NAME, 'Password')
    # Send password box information
    password_box.send_keys('Ln##9uFTLn##9uFT')
    
    # Find login button and Click 
    login_button =  WebDriverWait(browser, 10).until(EC.element_to_be_clickable((By.NAME, 'login')))
    login_button.click()
    
    # 2. Получение необходимых списков сообщений   
    # Кнопка «Входящие», чтобы перейти в общий  список писем 
    inbox_button = browser.find_element(By.CSS_SELECTOR, "li.samoware-folder.samoware-folder_type_inbox.samoware-folder_nested_0.samoware-folder_mode_active.samoware-folder_mode_more:nth-child(2) > span.samoware-folder__link > span.samoware-folder__wrapper.ng-binding")
    inbox_button.click()
    
    find_messages_all_total_pages = list()
    find_messages_all_text_total_pages = list()
    find_messages_ods_text_all_total_pages = list()
    find_messages_ods_text_total_pages = list()
    
    find_messages_all_one_page = list()
    find_messages_all_text_one_pag = list()
    find_messages_ods_text_all_one_pag = list()
    find_messages_ods_text_one_pag = list()
    
    list_download_files_of_parser = list()
    
    for _ in range(MAX_INBOX_PAGES - 1):
        find_messages_all_one_page = browser.find_elements(By.CSS_SELECTOR, "div.samoware-mail-list.samoware-scroll.samoware-mail-list-with-page-controls > div.samoware-mail-list__item.ng-scope")
        find_messages_all_total_pages.extend(find_messages_all_one_page)
        find_messages_all_text_one_pag = [i.text for i in find_messages_all_one_page]
        find_messages_all_text_total_pages.extend(find_messages_all_text_one_pag)
        find_messages_ods_text_all_one_page = [item.text for item in find_messages_all_one_page if "ОДС Главного управления МЧС России по Волгоградской области"in item.text]
        find_messages_ods_text_all_total_pages.extend(find_messages_ods_text_all_one_page)
        
        # 3. Поиск и фильтрация сообщений, которые от ОДС Главного управления МЧС России по Волгоградской области
        if IS_START_DAY_AND_TIME_PARSER_SET_AUTOMATIC:
            # Фалы с почты будут парситься с крайней даты на которую есть данные в PATH_DIR_DATA_STORE. Время берется с 00:00.
            find_messages_ods_one_page = [item for item in find_messages_all_one_page if "ОДС Главного управления МЧС России по Волгоградской области"in item.text 
                                and dt.datetime.strptime(re.search(r"[0-3]*[0-9][./][0-1][0-9][./][0-9][0-9]\s[0-2][0-9][-:][0-5][0-9]", item.text).group(), '%d/%m/%y %H:%M') 
                                >= dt.datetime.combine(find_last_file_data_store(list_all_group_name=LIST_ALL_GROUP_NAME, path_dir=PATH_DIR_PDF).get('datetime', None).date(),dt.time(0, 0))]
        else:
            # Фалы с почты будут парситься с даты и времени, которая указана в  START_DAY_AND_TIME_PARSER
            find_messages_ods_one_page = [item for item in find_messages_all_one_page if "ОДС Главного управления МЧС России по Волгоградской области"in item.text 
                                and dt.datetime.strptime(re.search(r"[0-3]*[0-9][./][0-1][0-9][./][[0-9][0-9]\s[0-2][0-9][-:][0-5][0-9]", item.text).group(), '%d/%m/%y %H:%M')  >= START_DAY_AND_TIME_PARSER]

        find_messages_ods_text_one_pag = [item.text for item in find_messages_ods_one_page]
        find_messages_ods_text_total_pages.extend(find_messages_ods_text_one_pag)
        
        iframe = browser.find_element(By.CSS_SELECTOR, 'iframe.js-mail-content') 
        
        for i in range(len(find_messages_ods_one_page)):
            # Получение даты и времени из текста сообщения на почте
            text_masseg = find_messages_ods_text_one_pag[i]
            find_messages_ods_time_on_mail = re.search(r"[0-3]*[0-9][-/][0-1][0-9][-/][0-9][0-9]\s[0-2][0-9]:[0-5][0-9]", text_masseg).group()
            find_messages_ods_time_on_mail = find_messages_ods_time_on_mail.replace('/', '.').replace(':', '-')
            find_messages_ods_time_on_mail = re.sub(r'^[0-9][.]', '0' + find_messages_ods_time_on_mail[find_messages_ods_time_on_mail.find('.') - 1 : find_messages_ods_time_on_mail.find('.')] + '.', find_messages_ods_time_on_mail) if re.search(r'[0-9].', find_messages_ods_time_on_mail) is not None else find_messages_ods_time_on_mail
            find_messages_ods_time_on_mail = dt.datetime.strptime(re.search(r"[0-3]*[0-9][.][0-1][0-9][.][0-9][0-9]\s[0-2][0-9][-][0-5][0-9]", find_messages_ods_time_on_mail).group(), '%d.%m.%y %H-%M').strftime('%d.%m.%Y %H-%M')
            
            # Перейти в список сообщений
            # browser.find_element(By.XPATH, "//*[@id=\"samoware-mail\"]/div[1]/div[5]/ul/li[2]/span/span[1]").click() 
            # # Есть ли смысл, когда браузер открыт на есть экран
            # inbox_button.click()
            
            #  Выбрать сообщение от ОДС
            find_messages_ods_one_page[i].click()
            browser.switch_to.frame(iframe)

            time_start_download = time.time()
       
            # Каждый файл из вложения сообщения скачивается отдельно
            files_find_messages = browser.find_elements(By.XPATH, '//div[@class="samoware-mail__attach"]/div[@class="samoware-mail-message__attach__item"]//div[@title="Скачать"]/div[@class="samoware-general_svg-container-20 samoware-general_svg-icons-holder"]/*[@class="samoware-general_svg-container-no-scale"]')
            for i in range(len(files_find_messages)):
                element = files_find_messages[i]
                actions = ActionChains(browser)
                actions.move_to_element(element).click(element).perform()
            
            
            check_is_downloaded_files(time_start_download=time_start_download)
            # TODO: deprecated ???
            # time.sleep(14)
            time_final_download = time.time()
            browser.switch_to.default_content()
            
            all_download_files = [[filename, os.stat(os.path.join(PATH_DIR_DOWNLOADS, filename)).st_mtime] for filename in os.listdir(PATH_DIR_DOWNLOADS)]        
            download_files = [file[0] for file in all_download_files if file[1] >= time_start_download and  file[1] <= time_final_download]
            
            list_download_files_of_parser.extend(rename_download_files(download_files=download_files, messages_ods_time_on_mail=find_messages_ods_time_on_mail))
        
        # Проверка на необходимость поиска файлов от ОДС на новой странице 
        if len(find_messages_ods_text_all_one_page) == len(find_messages_ods_one_page):
            # Переход на новую страницу
            # Поиск кнопки перехода на следующую страницу во входящих
            inbox_page = browser.find_element(By.XPATH, '//div[@class="samoware-mail-list__page-actions-container"]/div[@class="samoware-mail-list__page-actions ng-isolate-scope"]/div[@title="Вперед" and @class="samoware-content__action-l samoware-action samoware-action_type_next"]/div/*[@class="samoware-general_svg-container samoware-general_svg-icons-holder samoware-general_svg-icons-holder-use"]')
            # Переход на следующую страницу во входящих
            inbox_page.click()
            time.sleep(2)
        else:
            break
except Exception as e:
    parser_report_errors += f'\n1. Парсинг файлов с сайта: возникла ошибка\n{e}\n'
    print(parser_report_errors)
    parser_report += parser_report_errors
    
    add_info_in_report_parser(path_to_file_report=path_to_file_report, mode_open_file='w', text_for_add=parser_report)
else: 
    parser_report_errors += '\n1. Парсинг файлов с сайта: ошибки не выявлено'
    
    parser_report_find_messages_all += '\n'.join([str(i + 1) + " " + find_messages_all_text_total_pages[i].replace("\n", "\\n") for i in range(len(find_messages_all_text_total_pages))]) 
    parser_report_find_messages_ods_all += '\n'.join([str(i + 1) + " " + find_messages_ods_text_all_total_pages[i].replace("\n", "\\n") for i in range(len(find_messages_ods_text_all_total_pages))])
    parser_report_messages_ods_all_choices += '\n'.join([str(i + 1) + " " + find_messages_ods_text_total_pages[i].replace("\n", "\\n") for i in range(len(find_messages_ods_text_total_pages))])
    parser_report = parser_report + parser_report_find_messages_all + parser_report_find_messages_ods_all + parser_report_messages_ods_all_choices
    
    add_info_in_report_parser(path_to_file_report=path_to_file_report, mode_open_file='w', text_for_add=parser_report)     
finally:
    time.sleep(2)
    browser.quit()
    
print(find_messages_all_text_total_pages)
print(find_messages_ods_text_all_total_pages)
print(find_messages_ods_text_total_pages)

#2. Проверка файлов и добавление
# Запись стояния файлов в хранилище до манипуляций 
record_current_list_files_from_storage(text_header="\n\nИсходное стояние директории с хранимыми PDF-файлами:\n", path_dir=PATH_DIR_PDF)
record_current_list_files_from_storage(text_header="\n\nИсходное стояние директории с хранимыми PNG-файлами (конвертированные PDF):\n", path_dir=PATH_DIR_IMAGE_FROM_PDF)

# Транспортировка скаченных файлов в проект
transport_downloaded_files_local_storage(list_download_files=list_download_files_of_parser)

# Поиск и конвертация pdf файлов в png
data_store_files_of_groups = [file for file in os.listdir(PATH_DIR_PDF) if GROUP_NAME_FORECAST_VO in file or GROUP_NAME_FORECAST_UFO in file or GROUP_NAME_FORECAST_EVERY_WEEK in file or GROUP_NAME_FORECAST_INFORMATION_REPORT in file or GROUP_NAME_FORECAST_4MOD in file]
result_image_files_of_groups = [file for file in os.listdir(PATH_DIR_IMAGE_FROM_PDF) ]
list_files_pdf_to_convert = [file for file in data_store_files_of_groups if file.replace(".pdf", "").replace("PDF", "") not in (" ").join(result_image_files_of_groups)] 

for file in list_files_pdf_to_convert:
    is_completed = pdf_to_jpg(os.path.join(PATH_DIR_PDF, file), is_linux=True)
    
    if not is_completed:
        continue
    
    create_result_image(name_file_png=file.replace(".pdf", ""))
    
#3. Добавление файлов в архив c 29.05.2024 не производиться. Данные файлы удаляются
#PDF
last_file_name_and_datetime_UFO_pdf = find_last_file_of_group(group_name=GROUP_NAME_FORECAST_UFO, path_dir=PATH_DIR_PDF)
last_file_name_UFO_pdf = last_file_name_and_datetime_UFO_pdf.get('file_name', None)

last_file_name_and_datetime_CHS_VO_pdf = find_last_file_of_group(group_name=GROUP_NAME_FORECAST_VO, path_dir=PATH_DIR_PDF)
last_file_name_CHS_VO_pdf = last_file_name_and_datetime_CHS_VO_pdf.get('file_name', None)

last_file_name_and_datetime_KNP_VO_pdf = find_last_file_of_group(group_name=GROUP_NAME_FORECAST_EVERY_WEEK, path_dir=PATH_DIR_PDF)
last_file_name_KNP_VO_pdf = last_file_name_and_datetime_KNP_VO_pdf.get('file_name', None)

last_file_name_and_datetime_4MOD_pdf = find_last_file_of_group(group_name=GROUP_NAME_FORECAST_4MOD, path_dir=PATH_DIR_PDF)
last_file_name_4MOD_pdf = last_file_name_and_datetime_4MOD_pdf.get('file_name', None)

last_file_name_and_datetime_IDIV_pdf = find_last_file_of_group(group_name=GROUP_NAME_FORECAST_INFORMATION_REPORT, path_dir=PATH_DIR_PDF)
last_file_name_IDIV_pdf = last_file_name_and_datetime_IDIV_pdf.get('file_name', None)

#Image
last_file_name_and_datetime_UFO_image = find_last_file_of_group(group_name=GROUP_NAME_FORECAST_UFO, path_dir=PATH_DIR_IMAGE_FROM_PDF)
last_file_name_UFO_image = last_file_name_and_datetime_UFO_image.get('file_name', None)

last_file_name_and_datetime_CHS_VO_image = find_last_file_of_group(group_name=GROUP_NAME_FORECAST_VO, path_dir=PATH_DIR_IMAGE_FROM_PDF)
last_file_name_CHS_VO_image = last_file_name_and_datetime_CHS_VO_image.get('file_name', None)

last_file_name_and_datetime_KNP_VO_image = find_last_file_of_group(group_name=GROUP_NAME_FORECAST_EVERY_WEEK, path_dir=PATH_DIR_IMAGE_FROM_PDF)
last_file_name_KNP_VO_image = last_file_name_and_datetime_KNP_VO_image.get('file_name', None)

last_file_name_and_datetime_4MOD_image = find_last_file_of_group(group_name=GROUP_NAME_FORECAST_4MOD, path_dir=PATH_DIR_IMAGE_FROM_PDF)
last_file_name_4MOD_image = last_file_name_and_datetime_4MOD_image.get('file_name', None)

last_file_name_and_datetime_IDIV_image = find_last_file_of_group(group_name=GROUP_NAME_FORECAST_INFORMATION_REPORT, path_dir=PATH_DIR_IMAGE_FROM_PDF)
last_file_name_IDIV_image = last_file_name_and_datetime_IDIV_image.get('file_name', None)   

# Добавление в отчет по парсингу строчки: Удалены неактуальные файлы из хранилища:
add_info_in_report_parser(path_to_file_report=path_to_file_report, mode_open_file='a', 
                              text_for_add=removed_file_from_storage)

# 1.
clear_data_store_files(source_dir_path=PATH_DIR_PDF, file_group=GROUP_NAME_FORECAST_UFO, 
                                 file_group_max_date=last_file_name_and_datetime_UFO_pdf.get('datetime'), number_files_store_days=3)
clear_data_store_files(source_dir_path=PATH_DIR_PDF, file_group=GROUP_NAME_FORECAST_VO, 
                                 file_group_max_date=last_file_name_and_datetime_CHS_VO_pdf.get('datetime'), number_files_store_days=3)
clear_data_store_files(source_dir_path=PATH_DIR_PDF, file_group=GROUP_NAME_FORECAST_EVERY_WEEK, 
                                 file_group_max_date=last_file_name_and_datetime_KNP_VO_pdf.get('datetime'), number_files_store_days=3)
clear_data_store_files(source_dir_path=PATH_DIR_PDF, file_group=GROUP_NAME_FORECAST_4MOD, 
                                 file_group_max_date=last_file_name_and_datetime_4MOD_pdf.get('datetime'), number_files_store_days=3)

clear_data_store_files(source_dir_path=PATH_DIR_PDF, file_group=GROUP_NAME_FORECAST_INFORMATION_REPORT, 
                                 file_group_max_date=last_file_name_and_datetime_IDIV_pdf.get('datetime'), number_files_store_days=3)
# 2. 
clear_data_store_files(source_dir_path=PATH_DIR_IMAGE_FROM_PDF, file_group=GROUP_NAME_FORECAST_UFO, 
                                 file_group_max_date=last_file_name_and_datetime_UFO_image.get('datetime'), number_files_store_days=3)
clear_data_store_files(source_dir_path=PATH_DIR_IMAGE_FROM_PDF, file_group=GROUP_NAME_FORECAST_VO, 
                                 file_group_max_date=last_file_name_and_datetime_CHS_VO_image.get('datetime'), number_files_store_days=3)
clear_data_store_files(source_dir_path=PATH_DIR_IMAGE_FROM_PDF, file_group=GROUP_NAME_FORECAST_EVERY_WEEK, 
                                 file_group_max_date=last_file_name_and_datetime_KNP_VO_image.get('datetime'), number_files_store_days=3)
clear_data_store_files(source_dir_path=PATH_DIR_IMAGE_FROM_PDF, file_group=GROUP_NAME_FORECAST_4MOD, 
                                 file_group_max_date=last_file_name_and_datetime_4MOD_image.get('datetime'), number_files_store_days=3)
clear_data_store_files(source_dir_path=PATH_DIR_IMAGE_FROM_PDF, file_group=GROUP_NAME_FORECAST_INFORMATION_REPORT, 
                                 file_group_max_date=last_file_name_and_datetime_IDIV_image.get('datetime'), number_files_store_days=3)

# Запись стояния файлов в хранилище после манипуляций 
record_current_list_files_from_storage(text_header="\n\nФинальное стояние директории с хранимыми PDF-файлами:\n", path_dir=PATH_DIR_PDF)
record_current_list_files_from_storage(text_header="\n\nФинальное стояние директории с хранимыми PNG-файлами (конвертированные PDF):\n", path_dir=PATH_DIR_IMAGE_FROM_PDF)       

#4. Создание html страницы
## Вариант 1. Изображения на странице берутся из директорий проекта
site_page_str_v1 = f"""<!DOCTYPE html>
<html>

<head>
    <meta charset="utf-8">
    <title></title>
    <link rel="stylesheet" href="style.css">
</head>

<body>
    <div class="dashboard">
        <h1> ОДС Главного управления МЧС России по Волгоградской области</h1>
        <div class="container">
            <div class="block_nav_pdf">
                <div>
                    <h1>Мониторинг пожароопасной ситуации</h1>
                    <p>{last_file_name_4MOD_pdf}</p>
                    <div class="block_button_and_info">
                        <input id="color-input1" type="button" value="Показать" onmousedown="viewDiv1()">
                        <div class="info">
                            <img src="image/inf_icon.png" alt="inf_icon">
                            <div class="tooltip-text">
                                <p><b>Дата и время в названии файлов:</b><br>дата и время, когда был получен файл от ОДС
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
                <div>
                    <h1>Оперативный ежедневный сводный прогноз ЮФО</h1>
                    <p>{last_file_name_UFO_pdf}</p>
                    <input id="color-input2" type="button" value="Показать" onmousedown="viewDiv2()">
                </div>
                <div>
                    <h1>Оперативный ежедневный сводный прогноз ВО</h1>
                    <p>{last_file_name_CHS_VO_pdf}</p>
                    <input id="color-input3" type="button" value="Показать" onmousedown="viewDiv3()">
                </div>
                <div>
                    <h1>Краткосрочный недельный прогноз ВО</h1>
                    <p>{last_file_name_KNP_VO_pdf}</p>
                    <input id="color-input4" type="button" value="Показать" onmousedown="viewDiv4()">
                </div>
                <div>
                    <h1>Информационное донесение</h1>
                    <p>{last_file_name_IDIV_pdf}</p>
                    <input id="color-input5" type="button" value="Показать" onmousedown="viewDiv5()">
                </div>
            </div>

            <div class="block_view_pdf">      
                <div class="head_view_pdf">
                    <input id="image_minus" type="button" value="-" onmousedown="ImageMinus()">
                    <input id="image_plus" type="button" value="+" onmousedown="ImagePlus()">
                    <a id="download_pdf_a" href="Data_store/pdf/{last_file_name_4MOD_pdf}" download><input id="download_pdf"
                            type="button" value="Скачать файл"></a>
                </div>
                <div class="body_view_pdf">
                    <img id="imageid" src="Data_store/image_from_pdf/{last_file_name_4MOD_image}" alt="">
                </div>
            </div>
        </div>

    </div>
    <script>
         function ImageMinus() {{
            var img = document.getElementById('imageid'), style = getComputedStyle(img, null),
                w = style.width, h = style.height, maxh = style.maxHeight, maxw = style.maxWidth;

            w = parseInt(w) * .9; // or whatever your modifier is 
            h = parseInt(h) * .9; // parseInt removes the traling "px" so
            img.style.width = w + "px"; // we need to append the "px" 
            img.style.height = h + "px";
        }};
        function ImagePlus() {{
            var img = document.getElementById('imageid'), style = getComputedStyle(img, null),
                w = style.width, h = style.height, maxh = style.maxHeight, maxw = style.maxHeight;
            w = parseInt(w) * 1.1; // or whatever your modifier is 
            h = parseInt(h) * 1.1; // parseInt removes the traling "px" so
            img.style.width = w + "px"; // we need to append the "px" 
            img.style.height = h + "px";
        }};

        function viewDiv1() {{
            document.getElementById("imageid").src = "Data_store/image_from_pdf/{last_file_name_4MOD_image}";
            document.getElementById("download_pdf_a").href = "Data_store/pdf/{last_file_name_4MOD_pdf}";
            document.getElementById("imageid").style.width = "100%";
            document.getElementById("imageid").style.height = "auto";

            document.getElementById("color-input1").style.color = "#ffffff";
            document.getElementById("color-input2").style.color = "#000";
            document.getElementById("color-input3").style.color = "#000";
            document.getElementById("color-input4").style.color = "#000";
            document.getElementById("color-input5").style.color = "#000";
            document.getElementById("color-input1").style.background = "rgb(49, 70, 139)";
            document.getElementById("color-input2").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input3").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input4").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input5").style.background = "hsl(225, 19%, 92%)";
        }};
        function viewDiv2() {{
            document.getElementById("imageid").src = "Data_store/image_from_pdf/{last_file_name_UFO_image}";
            document.getElementById("download_pdf_a").href = "Data_store/pdf/{last_file_name_UFO_pdf}";
            document.getElementById("imageid").style.width = "80%";
            document.getElementById("imageid").style.height = "auto";

            document.getElementById("color-input1").style.color = "#000";
            document.getElementById("color-input2").style.color = "#ffffff";
            document.getElementById("color-input3").style.color = "#000";
            document.getElementById("color-input4").style.color = "#000";
            document.getElementById("color-input5").style.color = "#000";
            document.getElementById("color-input1").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input2").style.background = "rgb(49, 70, 139)";
            document.getElementById("color-input3").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input4").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input5").style.background = "hsl(225, 19%, 92%)";
        }};
        function viewDiv3() {{
            document.getElementById("imageid").src = "Data_store/image_from_pdf/{last_file_name_CHS_VO_image}";
            document.getElementById("download_pdf_a").href = "Data_store/pdf/{last_file_name_CHS_VO_pdf}";
            document.getElementById("imageid").style.width = "80%";
            document.getElementById("imageid").style.height = "auto";

            document.getElementById("color-input1").style.color = "#000";
            document.getElementById("color-input2").style.color = "#000";
            document.getElementById("color-input3").style.color = "#ffffff";
            document.getElementById("color-input4").style.color = "#000";
            document.getElementById("color-input5").style.color = "#000";
            document.getElementById("color-input1").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input2").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input3").style.background = "rgb(49, 70, 139)";
            document.getElementById("color-input4").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input5").style.background = "hsl(225, 19%, 92%)";
        }};

        function viewDiv4() {{
            document.getElementById("imageid").src = "Data_store/image_from_pdf/{last_file_name_KNP_VO_image}";
            document.getElementById("download_pdf_a").href = "Data_store/pdf/{last_file_name_KNP_VO_pdf}";
            document.getElementById("imageid").style.width = "80%";
            document.getElementById("imageid").style.height = "auto";

            document.getElementById("color-input1").style.color = "#000";
            document.getElementById("color-input2").style.color = "#000";
            document.getElementById("color-input3").style.color = "#000";
            document.getElementById("color-input4").style.color = "#ffffff";
            document.getElementById("color-input5").style.color = "#000";
            document.getElementById("color-input1").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input2").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input3").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input4").style.background = "rgb(49, 70, 139)";
            document.getElementById("color-input5").style.background = "hsl(225, 19%, 92%)";
        }};

        function viewDiv5() {{
            document.getElementById("imageid").src = "Data_store/image_from_pdf/{last_file_name_IDIV_image}";
            document.getElementById("download_pdf_a").href = "Data_store/pdf/{last_file_name_IDIV_pdf}";
            document.getElementById("imageid").style.width = "80%";
            document.getElementById("imageid").style.height = "auto";

            document.getElementById("color-input1").style.color = "#000";
            document.getElementById("color-input2").style.color = "#000";
            document.getElementById("color-input3").style.color = "#000";
            document.getElementById("color-input4").style.color = "#000";
            document.getElementById("color-input5").style.color = "#ffffff";
            document.getElementById("color-input1").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input2").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input3").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input4").style.background = "hsl(225, 19%, 92%)";
            document.getElementById("color-input5").style.background = "rgb(49, 70, 139)";
        }};

        function myFunctionSearch() {{
            var input = document.getElementById("Search");
            var filter = input.value.toLowerCase();
            var nodes = document.getElementsByClassName('camera_block');

            for (i = 0; i < nodes.length; i++) {{
                if (nodes[i].innerText.toLowerCase().includes(filter)) {{
                    nodes[i].style.display = "block";
                }} else {{
                    nodes[i].style.display = "none";
                }}
            }}
        }}
    </script>
</body>

</html>"""

# Html_file = codecs.open("index — копия.html","w", "utf-8")
Html_file = codecs.open("index.htm", "w", "utf-8")
Html_file.write(site_page_str_v1)
Html_file.close()

# Вариант 2. Изображения хранятся в формате base64 прям в html файле
# site_page_str_v2 = f"""<!DOCTYPE html>
# <html>

# <head>
#     <meta charset="utf-8">
#     <title></title>
#     <link rel="stylesheet" href="style.css">
# </head>

# <body>
#     <div class="dashboard">
#         <h1> ОДС Главного управления МЧС России по Волгоградской области</h1>
#         <div class="container">
#             <div class="block_nav_pdf">
#                 <div>
#                     <h1>Мониторинг пожароопасной ситуации</h1>
#                     <p>{last_file_name_4MOD_pdf}</p>
#                     <div class="block_button_and_info">
#                         <input id="color-input1" type="button" value="Показать" onmousedown="viewDiv1()">
#                         <div class="info">
#                             <img src="data:image/png;base64, {convert_image_to_base64('image/inf_icon.png')}" alt="inf_icon">
#                             <div class="tooltip-text">
#                                 <p><b>Дата и время в названии файлов:</b><br>дата и время, когда был получен файл от ОДС
#                                 </p>
#                             </div>
#                         </div>
#                     </div>
#                 </div>
#                 <div>
#                     <h1>Оперативный ежедневный сводный прогноз ЮФО</h1>
#                     <p>{last_file_name_UFO_pdf}</p>
#                     <input id="color-input2" type="button" value="Показать" onmousedown="viewDiv2()">
#                 </div>
#                 <div>
#                     <h1>Оперативный ежедневный сводный прогноз ВО</h1>
#                     <p>{last_file_name_CHS_VO_pdf}</p>
#                     <input id="color-input3" type="button" value="Показать" onmousedown="viewDiv3()">
#                 </div>
#                 <div>
#                     <h1>Краткосрочный недельный прогноз ВО</h1>
#                     <p>{last_file_name_KNP_VO_pdf}</p>
#                     <input id="color-input4" type="button" value="Показать" onmousedown="viewDiv4()">
#                 </div>
#                 <div>
#                     <h1>Информационное донесение</h1>
#                     <p>{last_file_name_IDIV_pdf}</p>
#                     <input id="color-input5" type="button" value="Показать" onmousedown="viewDiv5()">
#                 </div>
#             </div>

#             <div class="block_view_pdf">      
#                 <div class="head_view_pdf">
#                     <input id="image_minus" type="button" value="-" onmousedown="ImageMinus()">
#                     <input id="image_plus" type="button" value="+" onmousedown="ImagePlus()">
#                     <a id="download_pdf_a" href="Data_store/pdf/{last_file_name_4MOD_pdf}" download><input id="download_pdf"
#                             type="button" value="Скачать файл"></a>
#                 </div>
#                 <div class="body_view_pdf">
#                     <img id="imageid" src="data:image/png;base64, {convert_image_to_base64(os.path.join('Data_store/image_from_pdf/', last_file_name_4MOD_image))}" alt="">
#                 </div>
#             </div>
#         </div>

#     </div>
#     <script>
#          function ImageMinus() {{
#             var img = document.getElementById('imageid'), style = getComputedStyle(img, null),
#                 w = style.width, h = style.height, maxh = style.maxHeight, maxw = style.maxWidth;

#             w = parseInt(w) * .9; // or whatever your modifier is 
#             h = parseInt(h) * .9; // parseInt removes the traling "px" so
#             img.style.width = w + "px"; // we need to append the "px" 
#             img.style.height = h + "px";
#         }};
#         function ImagePlus() {{
#             var img = document.getElementById('imageid'), style = getComputedStyle(img, null),
#                 w = style.width, h = style.height, maxh = style.maxHeight, maxw = style.maxHeight;
#             w = parseInt(w) * 1.1; // or whatever your modifier is 
#             h = parseInt(h) * 1.1; // parseInt removes the traling "px" so
#             img.style.width = w + "px"; // we need to append the "px" 
#             img.style.height = h + "px";
#         }};

#         function viewDiv1() {{
#             document.getElementById("imageid").src = "data:image/png;base64, {convert_image_to_base64(os.path.join('Data_store/image_from_pdf/', last_file_name_4MOD_image))}";
#             document.getElementById("download_pdf_a").href = "Data_store/pdf/{last_file_name_4MOD_pdf}";
#             document.getElementById("imageid").style.width = "100%";
#             document.getElementById("imageid").style.height = "auto";

#             document.getElementById("color-input1").style.color = "#ffffff";
#             document.getElementById("color-input2").style.color = "#000";
#             document.getElementById("color-input3").style.color = "#000";
#             document.getElementById("color-input4").style.color = "#000";
#             document.getElementById("color-input5").style.color = "#000";
#             document.getElementById("color-input1").style.background = "rgb(49, 70, 139)";
#             document.getElementById("color-input2").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input3").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input4").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input5").style.background = "hsl(225, 19%, 92%)";
#         }};
#         function viewDiv2() {{
#             document.getElementById("imageid").src = "data:image/png;base64, {convert_image_to_base64(os.path.join('Data_store/image_from_pdf/', last_file_name_UFO_image))}";
#             document.getElementById("download_pdf_a").href = "Data_store/pdf/{last_file_name_UFO_pdf}";
#             document.getElementById("imageid").style.width = "80%";
#             document.getElementById("imageid").style.height = "auto";

#             document.getElementById("color-input1").style.color = "#000";
#             document.getElementById("color-input2").style.color = "#ffffff";
#             document.getElementById("color-input3").style.color = "#000";
#             document.getElementById("color-input4").style.color = "#000";
#             document.getElementById("color-input5").style.color = "#000";
#             document.getElementById("color-input1").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input2").style.background = "rgb(49, 70, 139)";
#             document.getElementById("color-input3").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input4").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input5").style.background = "hsl(225, 19%, 92%)";
#         }};
#         function viewDiv3() {{
#             document.getElementById("imageid").src = "data:image/png;base64, {convert_image_to_base64(os.path.join('Data_store/image_from_pdf/', last_file_name_CHS_VO_image))}";
#             document.getElementById("download_pdf_a").href = "Data_store/pdf/{last_file_name_CHS_VO_pdf}";
#             document.getElementById("imageid").style.width = "80%";
#             document.getElementById("imageid").style.height = "auto";

#             document.getElementById("color-input1").style.color = "#000";
#             document.getElementById("color-input2").style.color = "#000";
#             document.getElementById("color-input3").style.color = "#ffffff";
#             document.getElementById("color-input4").style.color = "#000";
#             document.getElementById("color-input5").style.color = "#000";
#             document.getElementById("color-input1").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input2").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input3").style.background = "rgb(49, 70, 139)";
#             document.getElementById("color-input4").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input5").style.background = "hsl(225, 19%, 92%)";
#         }};

#         function viewDiv4() {{
#             document.getElementById("imageid").src = "data:image/png;base64, {convert_image_to_base64(os.path.join('Data_store/image_from_pdf/', last_file_name_KNP_VO_image))}";
#             document.getElementById("download_pdf_a").href = "Data_store/pdf/{last_file_name_KNP_VO_pdf}";
#             document.getElementById("imageid").style.width = "80%";
#             document.getElementById("imageid").style.height = "auto";

#             document.getElementById("color-input1").style.color = "#000";
#             document.getElementById("color-input2").style.color = "#000";
#             document.getElementById("color-input3").style.color = "#000";
#             document.getElementById("color-input4").style.color = "#ffffff";
#             document.getElementById("color-input5").style.color = "#000";
#             document.getElementById("color-input1").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input2").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input3").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input4").style.background = "rgb(49, 70, 139)";
#             document.getElementById("color-input5").style.background = "hsl(225, 19%, 92%)";
#         }};

#         function viewDiv5() {{
#             document.getElementById("imageid").src = "data:image/png;base64, {convert_image_to_base64(os.path.join('Data_store/image_from_pdf/', last_file_name_IDIV_image))}";
#             document.getElementById("download_pdf_a").href = "Data_store/pdf/{last_file_name_IDIV_pdf}";
#             document.getElementById("imageid").style.width = "80%";
#             document.getElementById("imageid").style.height = "auto";

#             document.getElementById("color-input1").style.color = "#000";
#             document.getElementById("color-input2").style.color = "#000";
#             document.getElementById("color-input3").style.color = "#000";
#             document.getElementById("color-input4").style.color = "#000";
#             document.getElementById("color-input5").style.color = "#ffffff";
#             document.getElementById("color-input1").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input2").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input3").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input4").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input5").style.background = "rgb(49, 70, 139)";
#         }};

#         function myFunctionSearch() {{
#             var input = document.getElementById("Search");
#             var filter = input.value.toLowerCase();
#             var nodes = document.getElementsByClassName('camera_block');

#             for (i = 0; i < nodes.length; i++) {{
#                 if (nodes[i].innerText.toLowerCase().includes(filter)) {{
#                     nodes[i].style.display = "block";
#                 }} else {{
#                     nodes[i].style.display = "none";
#                 }}
#             }}
#         }}
#     </script>
# </body>

# </html>"""

# # Html_file = codecs.open("index — копия.html","w", "utf-8")
# Html_file = codecs.open("index.htm", "w", "utf-8")
# Html_file.write(site_page_str_v2)
# Html_file.close()

# # Вариант 3. Изображения хранятся в формате base64 прям в html файле. Упрощено для непосредственного использования в ИАП
# site_page_str_v3 = f"""<!DOCTYPE html>
# <html>

# <head>
#     <meta charset="utf-8">
#     <title></title>
#     <style>
#         body {{
#     background-color: #ffffff;
#     margin: 0;
# }}

# #MOD {{
#     display: block;
# }}

# #CHS_UFO {{
#     display: none;
# }}

# #CHS_VO {{
#     display: none;
# }}

# #KNP_VO {{
#     display: none;
# }}

# #IDIV {{
#     display: none;
# }}

# #color-input1 {{
#     color: rgb(255, 255, 255);
#     font-family: roboto, sans-serif;
#     font-size: 16px;
#     Font-weight: bold;
#     background-color: rgb(49, 70, 139);
# }}

# #color-input2 {{
#     color: rgb(0, 0, 0);
#     font-family: roboto, sans-serif;
#     font-size: 16px;
#     Font-weight: bold;
#     background-color: hsl(225, 19%, 92%);
# }}

# #color-input3 {{
#     color: rgb(0, 0, 0);
#     font-family: roboto, sans-serif;
#     font-size: 16px;
#     Font-weight: bold;

#     background-color: hsl(225, 19%, 92%);
# }}

# #color-input4 {{
#     color: rgb(0, 0, 0);
#     font-family: roboto, sans-serif;
#     font-size: 16px;
#     Font-weight: bold;

#     background-color: hsl(225, 19%, 92%);
# }}

# #color-input5 {{
#     color: rgb(0, 0, 0);
#     font-family: roboto, sans-serif;
#     font-size: 16px;
#     Font-weight: bold;

#     background-color: hsl(225, 19%, 92%);
# }}

# .dashboard {{
#     background-color: rgb(255, 255, 255);
# }}

# .dashboard>h1 {{
#     text-align: center;
#     margin: 0 0 20 0;
#     padding: 15px 0px 15px;
#     color: rgb(253, 253, 253);
#     font-family: roboto, sans-serif;
#     font-size: calc(25px + 0.60vw);

#     Font-weight: middle;
#     background-color: rgb(48, 51, 61);
# }}

# .container {{
#     display: flex;
#     width: 100%;

# }}

# .block_nav_pdf {{
#     width: 28%;
#     height: 85vh;
#     overflow: auto;

# }}

# .block_button_and_info {{
#     display: flex;
#     justify-content: space-between;
# }}

# .block_nav_pdf h1 {{
#     margin: 0 0 0 0;
#     padding: 10px 10px 10px 10px;
#     min-height: 36px;

#     color: rgb(253, 253, 253);
#     font-family: roboto, sans-serif;
#     font-size: calc(14px + 0.35vw);
#     background-color: rgb(48, 51, 61);
#     border: solid 3px rgb(82, 83, 85);
# }}

# .block_nav_pdf p {{
#     margin: 0 0 0 0;
#     padding: 10px 10px 10px 10px;

#     color: rgb(0, 0, 0);
#     font-family: roboto, sans-serif;
#     font-size: calc(14px + 0.20vw);
#     Font-weight: middle;
# }}

# .block_nav_pdf input {{
#     display: inline-block;

#     width: calc(80px + 7vw);
#     height: 35px;
#     margin: 0 15px 15px 10px;

#     color: rgb(0, 0, 0);
#     font-family: roboto, sans-serif;
#     font-size: 16px;
#     Font-weight: middle;
# }}

# .block_nav_pdf input:hover {{
#     transition: 0.7s;
# }}

# .info {{
#     display: block;
#     padding-right: 5%;
#     padding-top: 5px;
#     /* height: 250px;
#     width: 250px; */
# }}

# .info img {{
#     width: 25px !important;
#     height: 25px !important;
# }}

# /* .info img[title]:hover:after {{
#     content: attr(title);
#     background-color: blue;
#     font-size: 20px;
# }} */

# .tooltip-text {{
#     display: none;
# }}

# .tooltip-text p {{
#     position: absolute;
#     font-family: "PT Sans", sans-serif;
#     background-color: #ccffcb;
#     color: #000000;
#     font-size: calc(14px + 0.20vw);
#     font-weight: 400;
#     text-transform: none;
#     padding: 20px 18px 18px 22px;
#     border-radius: 10px;
#     left: 17%;
#     z-index: 1;
#     transform: translateX(-450%);
#     transform: translateY(10%);
# }}

# .info img:hover+.tooltip-text {{
#     display: block;
# }}


# .block_view_pdf {{
#     width: 72%;

# }}

# .head_view_pdf {{

#     display: flex;
#     justify-content: right;
#     align-items: center;


#     height: 60px;
#     background-color: rgb(48, 51, 61);
#     font-family: roboto, sans-serif;
#     font-size: 16px;
#     Font-weight: middle;
#     border: solid 1px rgb(82, 83, 85);
# }}

# .body_view_pdf {{
#     height: 77vh;
#     margin: 0 0 0 0;
#     overflow: auto;
# }}

# .body_view_pdf img {{
#     width: 100%;
#     height: auto;
# }}

# .head_view_pdf input {{
#     display: inline-block;
#     color: rgb(255, 255, 255);
#     font-family: roboto, sans-serif;
#     Font-weight: bold;
#     background-color: rgb(88, 87, 87);
# }}

# .head_view_pdf #image_minus {{
#     width: calc(45px + 0.80vw);
#     height: calc(25px + 0.80vw);
#     font-size: calc(12px + 0.70vw);

# }}

# .head_view_pdf #image_plus {{
#     width: calc(45px + 0.80vw);
#     height: calc(25px + 0.80vw);
#     font-size: calc(12px + 0.70vw);

# }}

# .head_view_pdf #download_pdf {{
#     margin-right: 20px;
#     width: calc(135px + 0.80vw);
#     height: calc(25px + 0.80vw);
#     margin-left: 45px;
#     font-size: calc(10px + 0.45vw);
# }}

# .head_view_pdf input:hover {{
#     background-color: rgb(49, 70, 139);
# }}
#     </style>
# </head>

# <body>
#     <div class="dashboard">
#         <h1> ОДС Главного управления МЧС России по Волгоградской области</h1>
#         <div class="container">
#             <div class="block_nav_pdf">
#                 <div>
#                     <h1>Мониторинг пожароопасной ситуации</h1>
#                     <p>{last_file_name_4MOD_pdf}</p>
#                     <div class="block_button_and_info">
#                         <input id="color-input1" type="button" value="Показать" onmousedown="viewDiv1()">
#                         <div class="info">
#                             <img src="data:image/png;base64, {convert_image_to_base64('image/inf_icon.png')}" alt="inf_icon">
#                             <div class="tooltip-text">
#                                 <p><b>Дата и время в названии файлов:</b><br>дата и время, когда был получен файл от ОДС
#                                 </p>
#                             </div>
#                         </div>
#                     </div>
#                 </div>
#                 <div>
#                     <h1>Оперативный ежедневный сводный прогноз ЮФО</h1>
#                     <p>{last_file_name_UFO_pdf}</p>
#                     <input id="color-input2" type="button" value="Показать" onmousedown="viewDiv2()">
#                 </div>
#                 <div>
#                     <h1>Оперативный ежедневный сводный прогноз ВО</h1>
#                     <p>{last_file_name_CHS_VO_pdf}</p>
#                     <input id="color-input3" type="button" value="Показать" onmousedown="viewDiv3()">
#                 </div>
#                 <div>
#                     <h1>Краткосрочный недельный прогноз ВО</h1>
#                     <p>{last_file_name_KNP_VO_pdf}</p>
#                     <input id="color-input4" type="button" value="Показать" onmousedown="viewDiv4()">
#                 </div>
#                 <div>
#                     <h1>Информационное донесение</h1>
#                     <p>{last_file_name_IDIV_pdf}</p>
#                     <input id="color-input5" type="button" value="Показать" onmousedown="viewDiv5()">
#                 </div>
#             </div>

#             <div class="block_view_pdf">      
#                 <div class="head_view_pdf">
#                     <input id="image_minus" type="button" value="-" onmousedown="ImageMinus()">
#                     <input id="image_plus" type="button" value="+" onmousedown="ImagePlus()">
#                 </div>
#                 <div class="body_view_pdf">
#                     <img id="imageid" src="data:image/png;base64, {convert_image_to_base64(os.path.join('Data_store/image_from_pdf/', last_file_name_4MOD_image))}" alt="">
#                 </div>
#             </div>
#         </div>

#     </div>
#     <script>
#          function ImageMinus() {{
#             var img = document.getElementById('imageid'), style = getComputedStyle(img, null),
#                 w = style.width, h = style.height, maxh = style.maxHeight, maxw = style.maxWidth;

#             w = parseInt(w) * .9; // or whatever your modifier is 
#             h = parseInt(h) * .9; // parseInt removes the traling "px" so
#             img.style.width = w + "px"; // we need to append the "px" 
#             img.style.height = h + "px";
#         }};
#         function ImagePlus() {{
#             var img = document.getElementById('imageid'), style = getComputedStyle(img, null),
#                 w = style.width, h = style.height, maxh = style.maxHeight, maxw = style.maxHeight;
#             w = parseInt(w) * 1.1; // or whatever your modifier is 
#             h = parseInt(h) * 1.1; // parseInt removes the traling "px" so
#             img.style.width = w + "px"; // we need to append the "px" 
#             img.style.height = h + "px";
#         }};

#         function viewDiv1() {{
#             document.getElementById("imageid").src = "data:image/png;base64, {convert_image_to_base64(os.path.join('Data_store/image_from_pdf/', last_file_name_4MOD_image))}";
#             document.getElementById("imageid").style.width = "100%";
#             document.getElementById("imageid").style.height = "auto";

#             document.getElementById("color-input1").style.color = "#ffffff";
#             document.getElementById("color-input2").style.color = "#000";
#             document.getElementById("color-input3").style.color = "#000";
#             document.getElementById("color-input4").style.color = "#000";
#             document.getElementById("color-input5").style.color = "#000";
#             document.getElementById("color-input1").style.background = "rgb(49, 70, 139)";
#             document.getElementById("color-input2").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input3").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input4").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input5").style.background = "hsl(225, 19%, 92%)";
#         }};
#         function viewDiv2() {{
#             document.getElementById("imageid").src = "data:image/png;base64, {convert_image_to_base64(os.path.join('Data_store/image_from_pdf/', last_file_name_UFO_image))}";
#             document.getElementById("imageid").style.width = "80%";
#             document.getElementById("imageid").style.height = "auto";

#             document.getElementById("color-input1").style.color = "#000";
#             document.getElementById("color-input2").style.color = "#ffffff";
#             document.getElementById("color-input3").style.color = "#000";
#             document.getElementById("color-input4").style.color = "#000";
#             document.getElementById("color-input5").style.color = "#000";
#             document.getElementById("color-input1").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input2").style.background = "rgb(49, 70, 139)";
#             document.getElementById("color-input3").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input4").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input5").style.background = "hsl(225, 19%, 92%)";
#         }};
#         function viewDiv3() {{
#             document.getElementById("imageid").src = "data:image/png;base64, {convert_image_to_base64(os.path.join('Data_store/image_from_pdf/', last_file_name_CHS_VO_image))}";
#             document.getElementById("download_pdf_a").href = "Data_store/pdf/{last_file_name_CHS_VO_pdf}";
#             document.getElementById("imageid").style.width = "80%";
#             document.getElementById("imageid").style.height = "auto";

#             document.getElementById("color-input1").style.color = "#000";
#             document.getElementById("color-input2").style.color = "#000";
#             document.getElementById("color-input3").style.color = "#ffffff";
#             document.getElementById("color-input4").style.color = "#000";
#             document.getElementById("color-input5").style.color = "#000";
#             document.getElementById("color-input1").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input2").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input3").style.background = "rgb(49, 70, 139)";
#             document.getElementById("color-input4").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input5").style.background = "hsl(225, 19%, 92%)";
#         }};

#         function viewDiv4() {{
#             document.getElementById("imageid").src = "data:image/png;base64, {convert_image_to_base64(os.path.join('Data_store/image_from_pdf/', last_file_name_KNP_VO_image))}";
#             document.getElementById("imageid").style.width = "80%";
#             document.getElementById("imageid").style.height = "auto";

#             document.getElementById("color-input1").style.color = "#000";
#             document.getElementById("color-input2").style.color = "#000";
#             document.getElementById("color-input3").style.color = "#000";
#             document.getElementById("color-input4").style.color = "#ffffff";
#             document.getElementById("color-input5").style.color = "#000";
#             document.getElementById("color-input1").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input2").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input3").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input4").style.background = "rgb(49, 70, 139)";
#             document.getElementById("color-input5").style.background = "hsl(225, 19%, 92%)";
#         }};

#         function viewDiv5() {{
#             document.getElementById("imageid").src = "data:image/png;base64, {convert_image_to_base64(os.path.join('Data_store/image_from_pdf/', last_file_name_IDIV_image))}";
#             document.getElementById("imageid").style.width = "80%";
#             document.getElementById("imageid").style.height = "auto";

#             document.getElementById("color-input1").style.color = "#000";
#             document.getElementById("color-input2").style.color = "#000";
#             document.getElementById("color-input3").style.color = "#000";
#             document.getElementById("color-input4").style.color = "#000";
#             document.getElementById("color-input5").style.color = "#ffffff";
#             document.getElementById("color-input1").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input2").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input3").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input4").style.background = "hsl(225, 19%, 92%)";
#             document.getElementById("color-input5").style.background = "rgb(49, 70, 139)";
#         }};

#         function myFunctionSearch() {{
#             var input = document.getElementById("Search");
#             var filter = input.value.toLowerCase();
#             var nodes = document.getElementsByClassName('camera_block');

#             for (i = 0; i < nodes.length; i++) {{
#                 if (nodes[i].innerText.toLowerCase().includes(filter)) {{
#                     nodes[i].style.display = "block";
#                 }} else {{
#                     nodes[i].style.display = "none";
#                 }}
#             }}
#         }}
#     </script>
# </body>

# </html>"""

# Html_file = codecs.open("index — копия.html","w", "utf-8")
# Html_file = codecs.open("index_ODS_FOR_IAP.htm", "w", "utf-8")
# Html_file.write(site_page_str_v3)
# Html_file.close()