# Imago - An MSG Image Server

Imago is the webserver that the MSG Staff use to serve content at https://cdn.mila-software.group. The server was designed to allow ShareX users to easily and securely upload their screenshots to a fast, well-designed and efficient server.

## Features

Here's what you can expect from Imago once you install it on your machine and get it running:
- simple setup and installation
- well-designed dashboard
- plenty of configuration options
- efficient file upload and storage
- admin options for user and upload control
- secure token authorization
- optional Discord webhook logging
- WIP localization files for different languages
- configurable file compression options (with admin bypass options)

## Compression

This server has a set of configurable image compression options. At the moment, it uses Python's image manipulation package (PIL), limiting it strictly to image files only. 

### The compress option

Setting the 'compress' option to `yes` means that PIL will attempt to lower the file size without damaging the quality too much.

### The quality option

You can change the resolution of an image by changing the quality option. A lower number means a lower quality and smaller file size, a higher number means higher quality and file size. The number can only be as high as 100 because it's a percentage, therefore a number higher than 100 may cause stretching and distortion.

### Admin bypass

Administrators can be allowed to bypass compression with a number of options. You can allow them to bypass this by setting the can_bypass option to `yes`. If this is done, you can also choose whether or not admins need to pass a specific header in their request to bypass compression. If compression is not bypassed for admins by default then they need to pass a `Compression-Bypass` header with any True content (something other than an empty string).

## Example ShareX Configuration

At first, configuring ShareX may not seem like a simple task. So here's an example for you:

Field | Value
----- | -----
URL | https://example.com/api/upload
Method | POST
Body | Form data (multipart/form-data)
File form name | `upload`
Headers (key: value) | Authorization: your api token

## Installation

At first glance, there doesn't appear to be any obvious way to setup this server. So here's a guide on how to do it yourself!

0. There are several necessities that you will need to install before you attempt to install this server, they are as follows:
    - [Python 3.6](https://www.python.org/downloads/release/python-3610/) or later
    - [GIT](https://git-scm.com/downloads)
    - A [PostgreSQL](https://postgresql.org) server
    - A web server or reverse proxy such as [Nginx](https://nginx.com)
    - Something like [screen](https://gnu.org/software/screen/) or [Docker](https://docker.com) to keep your application running the background
    - A [CloudFlare](https://cloudflare.com) account
    - An externally accessible host machine, preferably with [Ubuntu](https://ubuntu.com) as the OS

1. Firstly, you should clone this repo to your host machine via this console command:
    
    ```
    git clone https://github.com/milasoftwaregroup/imago
    ```

2. Now that you have the server scripts on your machine, make sure that you're in the repo's directory and run the following command:
    ```
    pip install -r requirements.txt
    ```

3. It's configuring time! To start off, rename `config.example.yml` to `config.yml` and begin editing it. You are able to configure whatever values to whatever you wish.

4. Great! You're getting there, but there's one more thing you need to do before you can start the server. If you ran the start script at this point, the server would terminate as soon as you closed the terminal. To prevent this, you can use screen, Docker or anything similar to keep your application running in the background. We recommend you use screen as it's much simpler than Docker and does the job well. To enter a screen session, run:
    ```
    screen -S <some_name>
    ```

5. To start the server, you need to [cd](https://www.google.co.uk/url?sa=t&rct=j&q=&esrc=s&source=web&cd=11&cad=rja&uact=8&ved=2ahUKEwiN0pGc_LroAhUYkHIEHTTiC1wQFjAKegQIBxAB&url=https%3A%2F%2Fen.wikipedia.org%2Fwiki%2FCd_(command)&usg=AOvVaw3bknciTsDVK0HpAMlObHtH) into the `imagoweb` folder and run the imago.py file. This is commonly done by running:
    ```
    python imago.py
    ```

6. You should now be able to find the server at the configured port of your IP address. However, if you own a domain name, you may want to serve Imago at that domain. For this, we can use Nginx with a configuration that looks something like this:
    ```
    server {
        listen 80;
        server_name your.domain.name;

        location / {
            proxy_pass         http://127.0.0.1:<your configured port>;

            proxy_set_header   Host                 $host;
            proxy_set_header   X-Real-IP            $remote_addr;
            proxy_set_header   X-Forwarded-For      $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto    $scheme;
        }
    }
    ```

7. Once you're done configuring Nginx, head over to [CloudFlare](https://cloudflare.com) and setup your domain name there (if you haven't already). Once that's done, go into the DNS section of your domain and add a A record where the name is `@` and the IPv4 address is the address of your host machine. 

## Notice of Copyright

This repository includes 2 files located in [/imagoweb/static/assets](https://github.com/milasoftwaregroup/imago/tree/master/imagoweb/static/assets) that do not belong to [Mila Software Group™](https://mila-software.group). Said files are:
- [login_background.jpg](https://github.com/milasoftwaregroup/imago/tree/master/imagoweb/static/assets/login_background.jpg)
- [error_background.png](https://github.com/milasoftwaregroup/imago/tree/master/imagoweb/static/assets/error_background.png)
These files are property of [DiscordApp](https://discordapp.com) and all rights are reserved to them for these files.
