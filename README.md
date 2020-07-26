# Imago - An MSG Image Server

Imago is the webserver that I use to power [the TEK Net CDN](https://i.jacktek.net). The server was designed to allow ShareX users to easily and securely upload their screenshots to a fast, well-designed and efficient server.

**If you need support or wish to report a bug, please join my Discord server: https://discord.gg/uFgNnWx**

## Features

Here's what you can expect from Imago once you install it on your machine and get it running:
- simple setup and installation
- well-designed dashboard
- plenty of configuration options
- efficient file upload and storage
- url shortening
- admin options for user and upload control
- secure token authorization
- configurable file compression options (with admin bypass options)
- markdown rendering

## Installation

Let's just cut to the chase, you want to know how to install this bad boy, don't you? Well then head over to the [tutorial page](https://docs.jacktek.net/imago) for a detailed setup walkthrough!

## Compression

This server has a set of configurable image compression options. At the moment, it uses Python's image manipulation package (PIL), limiting it strictly to image files only. 

### The compress option

Setting the 'compress' option to `yes` means that PIL will attempt to lower the file size without damaging the quality too much.

### The quality option

You can change the resolution of an image by changing the quality option. A lower number means a lower quality and smaller file size, a higher number means higher quality and file size. The number can only be as high as 100 because it's a percentage, therefore a number higher than 100 may cause stretching and distortion.

### Admin bypass

Administrators can be allowed to bypass compression with a number of options. You can allow them to bypass this by setting the can_bypass option to `yes`. If this is done, you can also choose whether or not admins need to pass a specific header in their request to bypass compression. If compression is not bypassed for admins by default then they need to pass a header - set in the config file - with any True content (something other than an empty string).

## Example ShareX Configuration

At first, configuring ShareX may not seem like a simple task. So here's an example for you:

### Image or file uploads

Field | Value
----- | -----
Destination type | Image uploader; File uploader; Text uploader
URL | https://example.com/api/upload
Method | POST
Body | Form data (multipart/form-data)
File form name | `upload`
Headers (key: value) | Authorization: your api token

### URL shortening

Field | Value
----- | -----
Destination type | URL shortener
URL | https://example.com/api/shorten
Method | POST
Body | JSON (application/json)
Body content | {"url": "$input$"}
Headers (key: value) | Authorization: your api token