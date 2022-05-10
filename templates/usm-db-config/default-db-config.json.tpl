{
    "UserManagement": {
      "dbConfig": {
            "HOST": "${DB_HOST}",
            "USER": "root",
            "PASSWORD": "${DB_ROOT_PASSWORD}",
            "DB": "${DB_NAME}",
            "dialect": "mysql",
            "pool": {
              "max": 5,
              "min": 0,
              "acquire": 30000,
              "idle": 10000
            }
      }
  }
  }