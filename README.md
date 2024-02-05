# задание - время на сайте
После клика на рекламу пользователи **переходят на сайт рекламодателя (одну или несколько страниц)**. метрика, которую необходимо учитывать, - это время на сайте, (время, которое пользователь провел на сайте, проверяя информацию и перемещаясь между страницами.)

- Пользователь открывает страницу А и через 15 секунд переходит на другой сайт.
Время на сайте: 15 секунд.
- Пользователь открывает страницу A, через 30 секунд переходит на страницу B и закрывает вкладку еще через 30 секунд.
Время на сайте: 60 секунд.
- Пользователь открывает страницу A в качестве фоновой вкладки, через 30 минут возвращается на эту вкладку и закрывает ее через 30 секунд.
Время на сайте: 30 секунд.
- Пользователь открывает страницу A как фоновую вкладку, через 20 минут пользователь возвращается на эту вкладку и переходит на страницу B, закрывая ее через 60 секунд.
Время на сайте: 60 секунд.
Среднее значение для всех примеров - 41,25 секунды (менее минуты).

Наиболее популярное аналитическое решение Google Analytics использует следующий подход: Время на сайте равно времени между первым и последним событиями просмотра страницы в пределах 30-минутного окна. Это означает, что Google Analytics будет измерять следующее время для приведенных выше примеров:
0 секунд
30 секунд
0 секунд
1200 секунд
Среднее значение составит 307,5 секунд (более 6 минут).

## задача 
Разработайте решение для правильного измерения и создания отчетов по метрике "Время на сайте" для каждого пользователя:
Средняя ошибка измерения не превышает 10 %.
Решение рассчитано на линейное масштабирование

К рассмотрению принимаются как прототип, так и детальная концепция.

## концепт
Так как пользователь переходит на сайт рекламодателя, предлогаю следующее:

1. Скрипт который встраивается на сайт рекламодателя. Он сможет отслеживать действия пользователя и отправлять данные на сервер аналитики
2. Aсинхронное api, которое сохранияет записи в clickhouse 
3. Бэк на Django с воркерам, который просыпается каждые 5 минут, идет в clickhouse, забирает логи в окне (от -3:00:00 до -2:55:00) групирует их по сессиям и записывает сумарное время на сайте, в случае если host добавлен и активен.

## детали 
### скрипт
Я взял готовую библиотеку https://github.com/saleemkce/timeonsite, так как она может автоматически считать время только у активных вкладок.
Немного модифецировал ее. Теперь она может считать количество активных вкладок, и отправлять данные только с последней закрытой вкладки.

```js
const URL = "http://localhost:8000/tos/"
const LIB = '//cdn.jsdelivr.net/gh/saleemkce/timeonsite@1.2.1/timeonsitetracker.min.js'
var Tos;
var Tab
(()=> {
    let js, fjs = document.getElementsByTagName('script')[0];
    if (document.getElementById('TimeOnSiteTracker')) return;
    js = document.createElement('script');
    js.id = 'TimeOnSiteTracker';
    js.onload = function() {
        console.log('script loaded')
        let tab = {
            count: () => {
                let tabs = localStorage.getItem('tab_open');
                return (tabs) ? Number.parseInt(tabs) : 0
            },
            open: () => {
                let tabs = localStorage.getItem('tab_open');
                if(tab.count() >= 0){
                    localStorage.setItem('tab_open', tab.count() + 1)
                }
                if (tabs === null){
                    localStorage.setItem('tab_open', 0)
                }
            },
            close: () => {
                if(tab.count() > 0){
                    localStorage.setItem('tab_open', tab.count() - 1)
                }
            },
            clear: () => {
                localStorage.setItem('tab_open', 0)
                localStorage.setItem('seconds', 0)
            },
            timeTab : () => {
                    return Number.parseInt(Tos.getTimeOnPage().timeOnPage)
                },
            timeSite: () => {
                    let seconds = localStorage.getItem('seconds')
                    return (seconds) ? Number.parseInt(seconds) : 0
            },
            isNotChrome: () => navigator.appVersion.match('Chrome') === null,
            send: () => {
                fetch(URL, {
                    method: "POST",
                    mode: "no-cors",
                    keepalive: true,
                    headers: {

                        "Content-Type": "application/json",
                    },
                    body: JSON.stringify({
                        host: window.location.host, 
                        session: Tos.getTimeOnPage().TOSSessionKey, 
                        time: tab.timeTab()
                    })}
            )},
            sendBeacon: () => {
                const blob = new Blob([JSON.stringify({ 
                        host: window.location.host, 
                        session: Tos.getTimeOnPage().TOSSessionKey, 
                        time: tab.timeTab()
                    })], { type: 'application/json; charset=UTF-8' });

                navigator.sendBeacon(URL, blob) 
            },
            sendIfLast: () => {
                localStorage.setItem('seconds', tab.timeSite() + tab.timeTab())
                if(tab.count() === 1){

                    console.log('last tab')
                    if (navigator && typeof navigator.sendBeacon === 'function' && tab.isNotChrome()) { 
                        tab.sendBeacon() 
                    } else { 
                        tab.send()}
                    tab.clear()
                } else {
                    tab.close()
                }
            },
        }

        let config = {
            trackBy: 'seconds',
            trackHistoryChange: true, 
            callback: function(data) {
                if (data && data.trackingType) {
                    if (data.trackingType == 'tos') {
                        if (Tos.verifyData(data) != 'valid') {
                            console.log('Data abolished!');
                            return; 
                        }
                    }
                    tab.sendIfLast()
                }
            }
        };
        if(TimeOnSiteTracker) {
            Tos = new TimeOnSiteTracker(config);
            console.log('tos initialized')
            tab.open()
            console.log(tab.count())
            Tab = tab
        }
    };
    js.src = LIB;
    fjs.parentNode.insertBefore(js, fjs);
})();

```

- достаточно простая и компактная чтобы ее переписать, и модифицировать ее под свои нужды.
- она может быть легко встроена на любой сайт
- из минусов - библиотека платная и есть глобальные проблемы с отработкой скриптов в разных средах. (наличие расширений браузеуров, залоченые event и т.д).

### api
Я выбрал связку - простое api - которое пишет данные в clickhouse
- api легко масштабируется под нагрузкой

### back
На бэке мы имеем связку celery + celery_beat
- подход тоже может быть легко масштабирован
- но нужно будет подбирать время окна, если воркеров понадобиться больше
- 3 часа - это максимальная величина существования сессии (подбирал произвольно)
- окно (от -3:00 до 2:55) варьируется от количества воркеров и продолжительности сессии
- для демонстрации установил значения (от -0:05 до 0:00), при таком окне clickhouse не успевает удалить записи, поэтому сессии просто складываются. Если передвинуть окно в конец, то расчет сессий будет корректен
- 5 минут - время перезапуска воркера зависит от окна 

## запуск
```shell
docker compose up --build

```
По адресу http://localhost:1337/ будет находиться страница со встроенным скриптом. Если ее перезагрузить, или перейти с нее на нее же (enter), будут отправленны данные на api.
Чтобы это увидеть нужно перейти на http://localhost:1337/admin/tracker/trackedhost/ (admin:admin), и спустя 3 часа (5 мин для текущего примера) данные отобразятся сводные данные по каждому хосту.

Сервер хранит совсем немного данных по каждому пользователю (поэтому сейчас стоит sqlite3), но может быть легко модифицировано под тз.

