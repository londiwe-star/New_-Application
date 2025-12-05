"""
Management command to check database connection and health.

This command verifies database connectivity and provides
diagnostic information for troubleshooting.
"""

from django.core.management.base import BaseCommand
from django.db import connection
from django.conf import settings
import sys


class Command(BaseCommand):
    """
    Management command to check database health.
    
    Tests database connection and provides diagnostic information.
    """
    
    help = 'Check database connection and health'

    def handle(self, *args, **options):
        """Execute the command to check database."""
        
        self.stdout.write(self.style.SUCCESS('\n=== Database Health Check ===\n'))
        
        # Display database configuration
        db_config = settings.DATABASES['default']
        self.stdout.write(f"Database Engine: {db_config['ENGINE']}")
        self.stdout.write(f"Database Name: {db_config['NAME']}")
        self.stdout.write(f"Host: {db_config.get('HOST', 'default')}")
        self.stdout.write(f"Port: {db_config.get('PORT', 'default')}")
        self.stdout.write(f"User: {db_config.get('USER', 'default')}")
        
        # Test connection
        self.stdout.write('\n--- Testing Connection ---')
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                if result:
                    self.stdout.write(self.style.SUCCESS('✓ Database connection successful!'))
                else:
                    self.stdout.write(self.style.ERROR('✗ Database connection failed!'))
                    sys.exit(1)
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Database connection error: {str(e)}'))
            self.stdout.write('\nTroubleshooting tips:')
            self.stdout.write('1. Verify database server is running')
            self.stdout.write('2. Check database credentials in .env file')
            self.stdout.write('3. Ensure database exists')
            self.stdout.write('4. Check firewall/network settings')
            sys.exit(1)
        
        # Check tables
        self.stdout.write('\n--- Checking Tables ---')
        try:
            with connection.cursor() as cursor:
                if 'sqlite' in db_config['ENGINE']:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                else:
                    cursor.execute("SHOW TABLES")
                tables = cursor.fetchall()
                table_count = len(tables)
                self.stdout.write(self.style.SUCCESS(f'✓ Found {table_count} tables'))
                
                if table_count == 0:
                    self.stdout.write(self.style.WARNING('⚠ No tables found. Run migrations: python manage.py migrate'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Error checking tables: {str(e)}'))
        
        # Database-specific checks
        if 'mysql' in db_config['ENGINE'] or 'mariadb' in db_config['ENGINE']:
            self.stdout.write('\n--- MariaDB/MySQL Specific Checks ---')
            try:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT VERSION()")
                    version = cursor.fetchone()
                    self.stdout.write(f'Database Version: {version[0]}')
                    
                    cursor.execute("SHOW VARIABLES LIKE 'character_set%'")
                    charset_vars = cursor.fetchall()
                    self.stdout.write('\nCharacter Set Configuration:')
                    for var in charset_vars:
                        self.stdout.write(f'  {var[0]}: {var[1]}')
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'✗ Error: {str(e)}'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Database check complete ===\n'))


