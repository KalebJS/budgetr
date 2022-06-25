# Budgetr

A new way to budget

# Setup

To set up your instance of budgetr in production, you simply need to clone this repo into whatever service that you are using. I, for example, use PythonAnywhere to host my instance of this application. 

After cloning, open a command line interface (CLI) and create a virtual environment for your application to use. 

```bash
$ virtualenv budgetr
```

And then enter virtual environment by navigating to the directory where you cloned the repo and running the following command:

```bash
$ source budgetr/bin/activate
```

You will know you've entered the virtual environment when you see this before your command:

```bash
(budgetr) $
```

Go back to the cloned directory containing the `budgetr` code. Before attempting to run the application, you need to install the dependencies.

```bash
$ pip install -r requirements.txt
```

and you will need to initialize the database.

```bash
$ flask init-db
```

Next steps depend on what service you are using to host your application. In my case 