IF DB_ID('trips') IS NULL CREATE DATABASE trips;
GO
IF DB_ID('packs') IS NULL CREATE DATABASE packs;
GO

IF SUSER_ID('trips_user') IS NULL
    CREATE LOGIN trips_user WITH PASSWORD = '$(TRIPS_PWD)';
GO
IF SUSER_ID('packs_user') IS NULL
    CREATE LOGIN packs_user WITH PASSWORD = '$(PACKS_PWD)';
GO

USE trips;
IF USER_ID('trips_user') IS NULL
    CREATE USER trips_user FOR LOGIN trips_user;
ALTER ROLE db_owner ADD MEMBER trips_user;
GO

USE packs;
IF USER_ID('packs_user') IS NULL
    CREATE USER packs_user FOR LOGIN packs_user;
ALTER ROLE db_owner ADD MEMBER packs_user;
GO