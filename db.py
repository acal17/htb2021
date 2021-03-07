import MySQLdb

class DatabaseInterface():

  def __init__(self, connection_data, database_name, primary_asset_ticker):
    host, port, user, password = connection_data
    self.database_name = database_name
    self.primary_asset_ticker = primary_asset_ticker

    conn = MySQLdb.connect(host=host, port=port, user=user, passwd=password, autocommit=True)
    self.cursor = conn.cursor()

    if self.database_exists():
      self.drop_database()
    
    self.create_database()
    self.insert_default_values()

  def database_exists(self):
    self.cursor.execute(f"SHOW DATABASES LIKE '{self.database_name}';")
    database_exists = self.cursor.fetchone() is not None
    return database_exists

  def drop_database(self):
    self.cursor.execute(f"DROP DATABASE {self.database_name};")

  def create_database(self):
    self.cursor.execute(f"CREATE DATABASE {self.database_name};")
    self.cursor.execute(f"USE {self.database_name};")

    self.cursor.execute("""CREATE TABLE AssetClass (
      id   INT         NOT NULL AUTO_INCREMENT,
      name VARCHAR(32) NOT NULL UNIQUE,
      PRIMARY KEY (id)
    );""")
    self.cursor.execute("""CREATE TABLE Asset (
      id     INT         NOT NULL AUTO_INCREMENT,
      ticker VARCHAR(8)  NOT NULL UNIQUE,
      name   VARCHAR(32) NOT NULL,
      classId  INT       NOT NULL,
      PRIMARY KEY (id),
      CONSTRAINT FK_AssetClass FOREIGN KEY (classId) REFERENCES AssetClass(id)
    );""")
    self.cursor.execute("""CREATE TABLE User (
      id   INT         NOT NULL AUTO_INCREMENT,
      name VARCHAR(32) NOT NULL,
      PRIMARY KEY (id)
    );""")
    self.cursor.execute("""CREATE TABLE UserAsset (
      userId   INT    NOT NULL,
      assetId  INT    NOT NULL,
      quantity DOUBLE NOT NULL,
      PRIMARY KEY (userId, assetId),
      CONSTRAINT FK_UserAsset_User  FOREIGN KEY (userId) REFERENCES User(id),
      CONSTRAINT FK_UserAsset_Asset FOREIGN KEY (assetId) REFERENCES Asset(id)
    );""")
    self.cursor.execute("""CREATE TABLE Badge (
      id          INT          NOT NULL AUTO_INCREMENT,
      name        VARCHAR(32)  NOT NULL,
      description VARCHAR(256) NOT NULL,
      imageUrl    VARCHAR(256) NOT NULL,
      PRIMARY KEY (id)
    );""")
    self.cursor.execute("""CREATE TABLE UserBadge (
      userId       INT    NOT NULL,
      badgeId      INT    NOT NULL,
      TIMESTAMP    DOUBLE NOT NULL,
      PRIMARY KEY (userId, badgeId),
      CONSTRAINT FK_UserBadge_User  FOREIGN KEY (userId) REFERENCES User(id),
      CONSTRAINT FK_UserBadge_Badge FOREIGN KEY (badgeId) REFERENCES Badge(id)
    );""")

  def insert_default_values(self):
    self.cursor.execute("INSERT INTO AssetClass(name) VALUES ('Fiat');")
    self.cursor.execute("INSERT INTO AssetClass(name) VALUES ('Stock');")
    
    self.cursor.execute("INSERT INTO Asset(ticker, name, classId) VALUES ('GBP', 'Pound Sterling', 1);")
    self.cursor.execute("INSERT INTO Asset(ticker, name, classId) VALUES ('CMP', 'CompCorp', 2);")
    self.cursor.execute("INSERT INTO Asset(ticker, name, classId) VALUES ('BTM', 'BefortManufacturing', 2);")
    self.cursor.execute("INSERT INTO Asset(ticker, name, classId) VALUES ('LSC', 'LazySolutionCompany', 2);")

  ###########

  def get_user_id(self, name):
    self.cursor.execute(f"SELECT id FROM User WHERE name = '{name}';")
    response = self.cursor.fetchone()
    if response is None:
      raise RuntimeError("User does not exist.")
    id = response[0]
    return id

  def get_asset_id(self, ticker):
    self.cursor.execute(f"SELECT id FROM Asset WHERE ticker = '{ticker}';")
    response = self.cursor.fetchone()
    if response is None:
      raise RuntimeError("Asset does not exist.")
    id = response[0]
    return id

  def create_user(self, name):
    self.cursor.execute(f"INSERT INTO User(name) VALUES ('{name}');")
    id = self.get_user_id(name)
    self.set_user_asset(name, self.primary_asset_ticker, 1000.0)

  def user_exists(self, name):
    self.cursor.execute(f"SELECT * FROM User WHERE name = '{name}';")
    user_exists = self.cursor.fetchone() is not None
    return user_exists

  def reset_user(self, name):
    if not self.user_exists(name):
      raise RuntimeError("User does not exist.")
    user_id = self.get_user_id(name)
    self.cursor.execute(f"DELETE FROM UserAsset WHERE userId = {user_id};")

  def user_asset_exists(self, name, ticker):
    user_id = self.get_user_id(name)
    asset_id = self.get_asset_id(ticker)
    self.cursor.execute(f"SELECT * FROM UserAsset WHERE userId = {user_id} AND assetId = {asset_id};")
    row_exists = self.cursor.fetchone() is not None
    return row_exists

  def create_user_asset(self, name, ticker):
    user_id = self.get_user_id(name)
    asset_id = self.get_asset_id(ticker)
    self.cursor.execute(f"INSERT INTO UserAsset(userId, assetId, quantity) VALUES ({user_id}, {asset_id}, 0.0);")

  def get_user_asset(self, name, ticker):
    if not self.user_asset_exists(name, ticker):
      self.create_user_asset(name, ticker)
    user_id = self.get_user_id(name)
    asset_id = self.get_asset_id(ticker)
    self.cursor.execute(f"SELECT quantity FROM UserAsset WHERE userId = {user_id} AND assetId = {asset_id};")
    quantity = self.cursor.fetchone()[0]
    return quantity
    
  def set_user_asset(self, name, ticker, quantity):
    if not self.user_asset_exists(name, ticker):
      self.create_user_asset(name, ticker)
    user_id = self.get_user_id(name)
    asset_id = self.get_asset_id(ticker)
    self.cursor.execute(f"UPDATE UserAsset SET quantity = {quantity} WHERE userId = {user_id} AND assetId = {asset_id};")

  def alter_user_asset(self, name, ticker, quantity):
    if not self.user_asset_exists(name, ticker):
      self.create_user_asset(name, ticker)
    previous = self.get_user_asset(name, ticker)
    new = previous + quantity
    if new < 0:
      raise RuntimeError("Alteration would cause user to have negative assets.")
    else:
      self.set_user_asset(name, ticker, new)

  def buy_asset(self, name, ticker, quantity, price):
    if quantity < 0 or price < 0:
      raise RuntimeError("Invalid parameters supplied.")
    self.alter_user_asset(name, self.primary_asset_ticker, -1 * (quantity * price))
    self.alter_user_asset(name, ticker, quantity)

  def sell_asset(self, name, ticker, quantity, price):
    if quantity < 0 or price < 0:
      raise RuntimeError("Invalid parameters supplied.")
    self.alter_user_asset(name, ticker, -1 * quantity)
    self.alter_user_asset(name, self.primary_asset_ticker, quantity * price)
    
  def get_portfolio(self, name):
    if not self.user_exists(name):
      raise RuntimeError("User does not exist.")
    id = self.get_user_id(name)
    self.cursor.execute(f"SELECT asset.ticker, userasset.quantity FROM userasset INNER JOIN asset ON asset.id = userasset.assetId WHERE userasset.userId = {id} AND userasset.quantity != 0.0;")
    rows = self.cursor.fetchall()
    return ", ".join(list(map(lambda x :str(x), rows)))