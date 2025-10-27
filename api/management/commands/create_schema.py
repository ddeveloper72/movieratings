"""
Custom Django management command to create schema in Azure SQL Database
for MovieRater API in a shared database environment.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.conf import settings
import environ

# Initialize environment
env = environ.Env()

class Command(BaseCommand):
    help = 'Creates the MovieRater API schema in Azure SQL Database for multi-tenant setup'

    def add_arguments(self, parser):
        parser.add_argument(
            '--schema-name',
            default=env('AZURE_SQL_SCHEMA', default='movie_rater_api'),
            help='Name of the schema to create (default: movie_rater_api)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print the SQL commands without executing them'
        )

    def handle(self, *args, **options):
        schema_name = options['schema_name']
        dry_run = options['dry_run']
        
        # SQL commands as separate statements
        check_schema_sql = f"SELECT COUNT(*) FROM sys.schemas WHERE name = '{schema_name}'"
        create_schema_sql = f"CREATE SCHEMA [{schema_name}]"
        grant_permissions_sql = f"GRANT CREATE TABLE, ALTER, SELECT, INSERT, UPDATE, DELETE ON SCHEMA::[{schema_name}] TO [{env('AZURE_SQL_USER', default='developer')}]"
        
        if dry_run:
            self.stdout.write(
                self.style.WARNING('DRY RUN MODE - SQL commands that would be executed:')
            )
            self.stdout.write(f"CHECK: {check_schema_sql}")
            self.stdout.write(f"CREATE: {create_schema_sql}")
            self.stdout.write(f"GRANT: {grant_permissions_sql}")
            return
        
        try:
            with connection.cursor() as cursor:
                # Check if schema exists
                cursor.execute(check_schema_sql)
                schema_exists = cursor.fetchone()[0] > 0
                
                if not schema_exists:
                    self.stdout.write(f'Creating schema: {schema_name}')
                    cursor.execute(create_schema_sql)
                else:
                    self.stdout.write(f'Schema {schema_name} already exists')
                
                # Grant permissions (always run this in case permissions are missing)
                self.stdout.write(f'Granting permissions on schema: {schema_name}')
                cursor.execute(grant_permissions_sql)
                
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully set up schema "{schema_name}" for MovieRater API'
                )
            )
            
            self.stdout.write(
                self.style.WARNING(
                    'Next steps:\n'
                    '1. Update your Heroku config: heroku config:set AZURE_SQL_SCHEMA=movie_rater_api\n'
                    '2. Run migrations: python manage.py migrate\n'
                    '3. Test the application'
                )
            )
            
        except Exception as e:
            raise CommandError(f'Error creating schema: {str(e)}')