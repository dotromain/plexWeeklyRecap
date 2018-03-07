# plexRecapWeekly

Track recently added movies in your Plex Media Server (PMS) and send a weekly newsletter to your users.

plexRecapWeekly connects to your Plex Media Server to grab all movies added in the last 7 days, generate an HTML template with jinja2, and send it to the recipients that you have configured in config.ini.

## Usage:

Rename config.ini.example => config.ini and fill it with your infos.
Launch it with .

```bash
python3 plexWeeklyRecap.py
```

![plexWeeklyRecap Screenshot](https://i.imgur.com/x0NN9fr.gif)

## ToDo:

So many things, but you know, it works... Which suits perfectly to my needs.

I'll try to update it as soon as I have - free or boring - time

## Built With

* [Configobj](https://github.com/esp8266/Arduino/tree/master/libraries/ESP8266WiFi) - Config file reader
* [Jinja2](http://pubsubclient.knolleary.net/) - Templating engine
* [Requests](https://github.com/wemos/WEMOS_SHT3x_Arduino_Library) - HTTP library
* [Cerberus](http://tedgoas.github.io/Cerberus/) - Patterns for HTML email

## Authors

* **Romain Boulanger** - [*dotromain.github.io*](https://dotromain.github.io)

## License

This project is licensed under GPLv3 License - see the [LICENSE.md](LICENSE.md) file for details
