# Inventory API

## If you encounter permission issues...
  1. Delete "Migrations" folder and "inventory.db". 
  2. Recreate inventory.db, via sqlite3
  3. Run the following commands again:
  
    flask db init
    flask db migrate
    flask db upgrade

