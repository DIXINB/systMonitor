## systMonitor 
### Назначение  
Мониторинг системных параметров: загрузок процессора и оперативной памяти, дискового пространства.  
Запись в базу данных нужных фрагментов, просмотр записанного фрагмента в статическом режиме, если  
это необходимо.  
### Состав и запуск  
Это приложение состоит из одного модуля и готово к работе. Версия Python 3.8.10, которая идет с 
Ubuntu 20.04,  
использована и в виртуальном окружении программы. Последовательность действий для  
запуска (под Linux) такова:  
  1) Создаем и активируем виртуальное окружение venv  
     $python3 -m venv venv  
     $source venv/bin/activate
  2) Устанавливаем зависимости, т.е. дополнительные  пакеты  
     (venv)$pip install -r requirements.txt
  3) После успешной установки запускаем приложение  
     (venv)$python3 e631_7_5.py
  4) Открываем окно браузера, введя адрес
     http://127.0.0.1:8050/
### Описание  
После запуска вы должны увидеть таблицу с одной строкой, в которой динамически отображаются  
значения (%) параметров. Ниже будет зелёная кнопка "START"  и две таблицы, ждущие приёма значений.  
При появлении "подозрительного" значения параметра вы жмёте зелёную кнопку и начинается заполнение  
второй таблицы параметрами со значениями текущего времени. Кнопка станет красной с надписью "STOP".  
Таблица представляет собой "временное окно", показывающее последние 16 значений. Одновременно  с этим  
в текущем каталоге будет создана SQLite база данных syst_data.db, в таблицы *current* и *syst_data*  
которой будут записываться параметры. Во вторую таблицу помимо времени будет записан номер фрагмента в  
колонку Frame.  
После нажатия на кнопку "STOP", рядом появится белая кнопка "Done" и окошко таймера. При нажатии на неё  
третья таблица будет заполнена значениями последнего сформированного фрагмента.

     
   
