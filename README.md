# Work in Progress!
# SyPy
The aim of this library is to have the possibility to query Salesforce data from the comfy command line.
Its written in python. Get over it.


# Requirements
- python 3.10 or greater
- Connected App


# Why is there code? Just give me the .exe
Disclaimer! 
> Because username and password authentification is not cool these days, you will need to set up a **Connected App** in Salesforce. You can read up [here](https://developer.salesforce.com/docs/atlas.en-us.chatterapi.meta/chatterapi/quickstart.htm)

To install all needed libraries run:
```console
pip install -r requirements.txt
```

If you are a *superior* Linux user it is probably something like
```console
pip3 install -r requirements.txt
```

Create a .env file. You will need following entries there
```console
CLIENT_KEY=client_id from Connected App
CLIENT_SECRET=client_secret from Connected App
SF_INSTANCE=Instancename, e.g. sypy for Production, sypy--dev for Sandbox under sypy
DEBUG=If you dont want to have nice debug messages, you can remove this entry. Otherwise set it to anything you like. If you set it to False, you still will get debug messages because *'False'* == *True* :')
```

To run it
```console
python sfconnection.py
```

Again, if you are a *superior* Linux user it is probably something like
```conole
python3 sfconnection.py
```
# Description
Right now it does not really do anything. If you want to change the query, you have to change the code. Scary I know.
