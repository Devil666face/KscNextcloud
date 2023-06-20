[![pipeline status](https://git.dev.ap17.mil.ru/3-otdel/KscNextcloud/badges/main/pipeline.svg)](https://git.dev.ap17.mil.ru/3-otdel/KscNextcloud/-/commits/main)
[![Latest Release](https://git.dev.ap17.mil.ru/3-otdel/KscNextcloud/-/badges/release.svg)](https://git.dev.ap17.mil.ru/3-otdel/KscNextcloud/-/releases)

### Nextcloud deploy

Для развертывания Nexctloud используйте готовый и сконфигурированный [qcow2](https://git.dev.ap17.mil.ru/3-otdel/KscNextcloud/-/package_files/2/download) файл на базе ALSE 1.7.3uu2

### Install

```bash
cd /opt
sudo wget https://git.dev.ap17.mil.ru/av.kalinkin/KscNextcloud/uploads/18ce463dcc4a1ab7c2f62d2e4477c099/KscNextcloud.tgz
sudo tar -xf KscNextcloud.tgz && sudo rm KscNextcloud.tgz
chmod +x KscNextcloud/main.bin
cp KscNextcloud/kscnextcloud.service /etc/systemd/system/
systemctl enable kscnextcloud --now
```
### Usage

- Use `./main.bin -h` for get help message
```bash
usage: main.bin [-h] [-r] [-d] [-w] [-i]

options:
  -h, --help       show this help message and exit
  -r, --remove     remove all records from database.db
  -d, --daemon     exec in daemon mode
  -w, --write      save results in dump.csv
  -i, --iteration  make one iteration for make users from KSC
```
---

### Добавление общей share папки в nextcloud
1. Создаем общую группу, которую будем использовать для всех пользователей с шарой -> MSIO
2. Создаем папку -> "Общее сетевое хранилище"
3. Добавляем в права папки группу MSIO на только чтение
4. Копируем ссылку на доступ к папке
```php
vim /var/www/nextcloud/core/template/login.php

<?php /** @var \OCP\IL10N $l */ ?>
<?php
script('core', 'dist/login');
?>
<a class="button login primary" href="http://data.msio.local/index.php/s/share" >
        <p>Общее сетевое хранилище</p>
</a>

<div id="login"></div>

<?php if (!empty($_['alt_login'])) { ?>
    <div id="alternative-logins" class="alternative-logins">
        <?php foreach ($_['alt_login'] as $login): ?>
            <a class="button <?php p($login['style'] ?? ''); ?>" href="<?php print_unescaped($login['href']); ?>" >
                <?php p($login['name']); ?>
            </a>
        <?php endforeach; ?>
    </div>
<?php } ?>
```
5. В теге href ставим ссылку на шару
