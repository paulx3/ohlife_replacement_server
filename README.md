[![Build Status](https://travis-ci.org/paulx3/ohlife_relacement_server.svg?branch=master)](https://travis-ci.org/paulx3/ohlife_relacement_server)
[![Coverage Status](https://coveralls.io/repos/github/paulx3/ohlife_relacement_server/badge.svg)](https://coveralls.io/github/paulx3/ohlife_relacement_server)
# Ohlife Replacement Server
An replacement or alternative to Ohlife

------------
Overview
------------
After [Ohlife](http://ohlife.com/index.php) ,the Chinese alternative [juzishiguang](http://juzitime.com) also shutdown. 
After lots of searching, I found that those open source replacements are either limited in 
function or hard to deploy. So I came up with the idea using Flask to write an easy-to-deploy
Ohlife replacement.


------------
What is it?
------------
In a word, it's a email-based diary system.

The long version:

This program sends you an email everyday (or any time period you set) with greetings.
All you have to do is reply this email and the reply content will be saved on the server.
Pretty much the same as the original Ohlife.


------------
Quickstart
------------
**Warning:** The methods below can't be used right now.


Clone the repository and fill the config.cfg file according to comments and hit 
**deploy.sh** script.

Boom!


And enjoy using it.


------------
How to deploy
------------
Basically , you just need a Linux server with **Python3** installed. **Python2** is
not supported.

The author have provided one-click install [script](https://github.com/paulx3/res/raw/master/ohlife_replacement_deploy_script.sh) in the project.But
this script is not tested on many servers, if you want to deploy it manually or you 
encounter some wired problems. Please follow the steps below(The Steps are only tested on Ubuntu 14):


1. Install Postfix 
<br>Use `sudo apt-get install postfix` to install postfix as the local SMTP server. During installation,
you have to set your host name and server type. As for this project , you can choose 'Internet Server'.
However,if you have some kind of SMTP service like [SendGrid](https://sendgrid.com), you can pass this step.


2. Clone the project
<br>Use `git clone https://github.com/paulx3/ohlife_relacement_server.git` to clone the
repository to your local server.


3. Install Python 3 and its dependencies
<br>Install Python3 using `sudo apt-get install -y python3-pip`.
Enter the project folder `cd ohlife_relacement_server` and install all python dependencies `pip3 install -r requirements.txt`


4. Register Cloudmailin
<br>This project uses Cloudmailin or services alike to transform email into 
post request. So you should register one first. A much more detailed 
instructions will follow along in a couple of days.


5. Add Credential
<br>You need to add several credentials before you deploy the server:
* Cloudmailin address
* Default admin username and password
* (optional) Amazon S3 credential
<br><br>There is a template file called **config.cfg** in server folder.
The content is pretty much obvious. You can just fill in your config and credentials.



6. Set Cron Task
<br>You need set Cron task to run `ohlife.py` to send email to all the users.
------------
Localization
------------
This project has already provided two locale options. All you need to change is `locale:en-US` in `config.cfg` 
file. For example, if you want the Chinese version , you can change `locale:en-US` in `config.cfg`
to `locale:zh_Hans_CN`.

The project uses Python-Babel to achieve localization.The author
 tries to tag all the text using Babel `gettext()`
 
 
 
 I know the locale function for this app can be over-engineering. 
 
 So if you have a better option.
 You can open an issue or pull request.
 So if you are interested in localizing the project, please folow instruction below:
 1. Enter `locale` folder under `server` folder and copy the folder `en-US` and 
 give it a new name.
 2. Using tools like [Poedit](https://poedit.net/) to edit `ohlife.po` file and
 translate. The tool will automatically compile po file into mo binary file.
 3. Edit `locale` in `config.cfg` to the name of your new folder. For example, if 
 you add a new folder called `spanish`. Then you have to use `locale:spanish`.
 
 For detailed example of how to use Babel to do the localization , you can check [this](https://github.com/iver56/python-i18n-basics.git) repository.
 
------------
Current developing status
------------
* Add logging system ![progress](http://progressed.io/bar/0?title=ongoing)
* Supporting email with photo attachment ![progress](http://progressed.io/bar/0?title=halt)
* Third party SMTP service login support ![progress](http://progressed.io/bar/80?title=halt)
* At least 80% code coverage [![Coverage Status](https://coveralls.io/repos/github/paulx3/ohlife_relacement_server/badge.svg)](https://coveralls.io/github/paulx3/ohlife_relacement_server)
* Email sending function ![progress](http://progressed.io/bar/80?title=ongoing)
* Deploy instruction ![progress](http://progressed.io/bar/65?title=ongoing)
* Deploy script ![progress](http://progressed.io/bar/40?title=ongoing)
* Front and end support for mobile app ![progress](http://progressed.io/bar/60?title=ongoing)
* Mobile app ![progress](http://progressed.io/bar/40?title=ongoing)
* Chinese Readme ![progress](http://progressed.io/bar/0?title=halt)
* Localization ![progress](http://progressed.io/bar/100?title=done)
* Amazon S3 backup service ![progress](http://progressed.io/bar/90?title=halt)
* A timer for backup and email sending task ![progress](http://progressed.io/bar/20?title=halt)


