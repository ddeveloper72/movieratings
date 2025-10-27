# Azure SQL Schema Management for MovieRater API

## Overview

This MovieRater API is configured to work in a **multi-tenant Azure SQL Database** environment, where multiple applications share the same database instance but use separate schemas for logical isolation.

## Current Setup

### Database Architecture
- **Database**: `myFreeDB` on `myfreesqldbserver72.database.windows.net`
- **MovieRater Schema**: `movie_rater_api` 
- **Drone App Schema**: `drone_app_v2`
- **System Schemas**: Various `db_*` schemas for SQL Server system roles

### Schema Benefits
✅ **Cost Optimization**: Multiple apps share one Azure SQL Database  
✅ **Logical Separation**: Each app has its own schema namespace  
✅ **Security Isolation**: Schema-level permissions  
✅ **Easy Maintenance**: Clear organization and deployment boundaries  
✅ **Scalability**: Easy to add new applications  

## Configuration

### Environment Variables
```bash
# Local Development (.env file)
AZURE_SQL_SCHEMA=movie_rater_api

# Heroku Production
heroku config:set AZURE_SQL_SCHEMA=movie_rater_api --app ddeveloper72-movie-rater-api
```

### Database Settings
- Database router: `movierater.database_router.MovieRaterSchemaRouter`
- Models explicitly specify schema in `db_table` Meta options
- Automatic schema isolation for all MovieRater tables

## Setup Instructions

### 1. Create Schema (One-time setup)
```bash
# Enable Azure SQL in .env (uncomment AZURE_SQL_* variables)
# Then run:
python manage.py create_schema --schema-name movie_rater_api

# For dry-run (see SQL without executing):
python manage.py create_schema --dry-run
```

### 2. Deploy to Heroku
```bash
# Set schema environment variable
heroku config:set AZURE_SQL_SCHEMA=movie_rater_api --app ddeveloper72-movie-rater-api

# Deploy code changes
git add . && git commit -m "Add schema management for multi-tenant Azure SQL"
git push heroku main

# Run migrations on Heroku
heroku run python manage.py migrate --app ddeveloper72-movie-rater-api
```

### 3. Verify Setup
```bash
# Check tables were created in correct schema
heroku run python manage.py dbshell --app ddeveloper72-movie-rater-api

# In SQL prompt:
SELECT TABLE_SCHEMA, TABLE_NAME 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_SCHEMA = 'movie_rater_api';
```

## Table Structure

### MovieRater Tables (in `movie_rater_api` schema)
- `movie_rater_api.movie` - Movie information
- `movie_rater_api.rating` - User ratings for movies  
- `movie_rater_api.auth_user` - Django user authentication (if using Azure SQL)
- `movie_rater_api.django_*` - Django framework tables

### Other Applications
- `drone_app_v2.*` - Your drone application tables
- `dbo.*` - Default schema (avoid using for new apps)

## Best Practices

### Adding New Applications
1. Create dedicated schema: `new_app_schema`
2. Set `AZURE_SQL_SCHEMA=new_app_schema` in app config
3. Use explicit `db_table` in model Meta classes
4. Configure database router for schema isolation

### Database Migrations
```bash
# Always run migrations with schema context
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

### Monitoring
- Monitor schema usage in Azure Portal
- Use Azure SQL Analytics for performance monitoring
- Set up alerts for DTU/CPU usage across all applications

## Troubleshooting

### Common Issues
1. **Tables created in wrong schema**: Check `AZURE_SQL_SCHEMA` environment variable
2. **Permission errors**: Ensure user has schema permissions  
3. **Migration conflicts**: Each app should manage its own schema

### Useful SQL Queries
```sql
-- List all schemas
SELECT name FROM sys.schemas WHERE principal_id = 1;

-- List tables by schema  
SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE
FROM INFORMATION_SCHEMA.TABLES 
ORDER BY TABLE_SCHEMA, TABLE_NAME;

-- Check current schema permissions
SELECT p.permission_name, p.state_desc, pr.name as principal_name, s.name as schema_name
FROM sys.database_permissions p
JOIN sys.schemas s ON p.major_id = s.schema_id  
JOIN sys.database_principals pr ON p.grantee_principal_id = pr.principal_id
WHERE s.name = 'movie_rater_api';
```

## Migration from Default Schema

If you have existing tables in `dbo` schema that need to be moved:

```sql
-- Example: Move existing table to new schema
ALTER SCHEMA movie_rater_api TRANSFER dbo.api_movie;
ALTER SCHEMA movie_rater_api TRANSFER dbo.api_rating;
```

**⚠️ Important**: Test schema migration thoroughly in development before applying to production!