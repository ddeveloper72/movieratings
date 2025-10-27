# Database router for schema management in shared Azure SQL Database

import environ

# Initialize environment
env = environ.Env()

class MovieRaterSchemaRouter:
    """
    A router to control database operations for MovieRater API models
    Ensures all MovieRater tables are created in the designated schema
    """
    
    def __init__(self):
        self.schema_name = env('AZURE_SQL_SCHEMA', default='movie_rater_api')
        self.movie_rater_apps = {'api', 'home'}  # Your Django apps
    
    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        if model._meta.app_label in self.movie_rater_apps:
            return 'default'
        return None
    
    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""
        if model._meta.app_label in self.movie_rater_apps:
            return 'default'
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the movie_rater apps."""
        db_set = {'default'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain apps' models get created on the right database."""
        if app_label in self.movie_rater_apps:
            return db == 'default'
        elif db == 'default':
            # Don't migrate non-MovieRater apps to our database
            return app_label in self.movie_rater_apps
        return None
    
    def get_schema_name(self):
        """Get the schema name for MovieRater tables."""
        return self.schema_name