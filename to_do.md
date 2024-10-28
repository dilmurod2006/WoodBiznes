<!-- Project name is WoodBiznes -->
# Bu loyihada yog'ochlar nazorati yani yog'och qabul qilindi yoki yog'och yuborildi.
# Ishchilar nazorati yani bugun qaysi ishchi qancha ishlagani haqida datalarni databasega saqlab boradi
# Ishchilarni oylik maoshini 1oylik hisobot qilib  excel shaklida adminga beradi.
# Omborda qancha yuk bor, qancha yuk keldi, qancha yuk jo'natildi, qancha yuk qayta ishlandi hammasi nazorat qib boradi bot orqali


# TelegramBot start function
       - **Cheack user is admin**
       - **Show main menu**
# Main Menu Buttons and functions
       - ** переход **
       - ** остаток **
       - ** рабочие 👥 **
       - ** расход **
       - ** другие функции **




# переход function
    input data:
        1. 
        """
        #WorkerName
        

        Толщина*Ширина*Длина or Толщина*Ширина*Длина*Кол-во
        Толщина*Ширина*Длина or Толщина*Ширина*Длина*Кол-во
        Толщина*Ширина*Длина or Толщина*Ширина*Длина*Кол-во
        Толщина*Ширина*Длина or Толщина*Ширина*Длина*Кол-во
        Толщина*Ширина*Длина or Толщина*Ширина*Длина*Кол-во
        Толщина*Ширина*Длина or Толщина*Ширина*Длина*Кол-во
        Толщина*Ширина*Длина or Толщина*Ширина*Длина*Кол-во
        Толщина*Ширина*Длина or Толщина*Ширина*Длина*Кол-во
        ....


        #description

        bu ishchi bugun shuncha yog'oh kesdi

        """
    
#TestWorker


0034*0098*005*1000
0034*0098*005*100
0034*0098*005*10
0034*0098*005*1
0034*0098*005*0.1
0034*0098*005*0.01
0034*0098*005*0.001
0034*0098*005*0.0001
0034*0098*005*0.00001
0034*0098*005*0.000001


#description


salom bu ishchi bugun shuncha yog'oh kesdi

# остаток function
    get excel reports wood in stock function
    range date input function
          - first input: start date
          - second input: end date
    


# рабочие 👥 function
    get excel reports work volume on date range function
    only for evry month


# расход function




# BotFather add setcommands 
    - transition -  Ежедневно переход
    - remainder - O остаток
    - consumption - O расход
    - other_function - Другие функции
    - start - главное меню 🏘

# SetCommands:> transition
    if add_daily_work True:
        --> add daily work
            <!-- first method only for one worker -->
            first method:
                input data:
                    WorkerFullName
                    VolumeWood:>Float
                        --> thickness*Width*Length*Quantity

                        OR

                        --> thickness*Width*Length

                    Description
            <!-- second method for many workers -->
            second method:
                input data:
                    WorkerFullName1
                    VolumeWood:>Float
                        --> thickness*Width*Length*Quantity

                        OR

                        --> thickness*Width*Length

                    Description

                    WorkerFullName2
                    VolumeWood:>Float
                        --> thickness*Width*Length*Quantity

                        OR

                        --> thickness*Width*Length

                    Description

                    WorkerFullName3
                    VolumeWood:>Float
                        --> thickness*Width*Length*Quantity

                        OR

                        --> thickness*Width*Length
                        
                    Description

                    another WorkerFullName...

# SetCommands:> remainder
    if display_wood True:
        --> display wood

# SetCommands:> consumption
    if display_wood True:
        --> display wood

# SetCommands:> other_function
    pass

    else:
        if add_wood True:
            --> add wood
# SetCommands:> other_function command
    --> add admin
    --> add worker
    --> add daily work
    --> display wood
    --> exit