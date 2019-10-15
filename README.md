# Inventory API

## Local Installation

  0. Create a project directory, cd into it, and clone this project
  
    $ mkdir inventory_api
    $ cd inventory_api
    $ git clone <link-to-git-repository>
    $ cd inventory_api

  1. Create a virtual environment for Python3 

    $ virtualenv --python python3 venv
    
  2. Activate virtual environment
  
    $ source venv/bin/activate
    
  3. Install dependencies
  
    $ pip install -r requirements.txt
    
## Building and running API via Docker

  1. Build the image
  
    $ sudo docker build . -t flask_image
    
  2. Run API in Docker container
  
    $ sudo docker run --name inventory_container -p 5000:5000 flask_image

## If you encounter permission issues...
  1. Delete "Migrations" folder and "inventory.db". 
  2. Recreate inventory.db, via sqlite3
  3. Run the following commands again:
  
    $ flask db init
    $ flask db migrate
    $ flask db upgrade
    
    

