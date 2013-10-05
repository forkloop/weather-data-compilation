weather-data-compilation
========================

install cron tasks
---

```shell
0 0,6,12,18 * * * . $HOME/.credentials; $HOME/weather-data-compilation/wunderground-data.py >> $HOME/logs/wunderground.log 2>&1
0 1,7,13,19 * * * . $HOME/.credentials; $HOME/weather-data-compilation/wwo-data.py >> $HOME/logs/wwo.log 2>&1
0 2,8,14,20 * * * . $HOME/.credentials; $HOME/weather-data-compilation/hamweather-data.py >> $HOME/logs/hamweather.log 2>&1
0 4 * * * . $HOME/.credentials; $HOME/weather-data-compilation/s3-upload.rb >> $HOME/logs/upload.log 2>&1
```
