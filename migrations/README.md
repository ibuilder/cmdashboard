# This file contains documentation for database migrations. 
# It provides an overview of how to manage and apply migrations in the project. 

## Migrations Overview

This directory contains the migration scripts for the construction project dashboard application. Migrations are essential for managing changes to the database schema over time.

### Getting Started with Migrations

1. **Install Dependencies**: Ensure you have the necessary dependencies installed. You can do this by running:
   ```
   pip install -r requirements.txt
   ```

2. **Creating a Migration**: To create a new migration after making changes to the models, run:
   ```
   flask db migrate -m "Description of changes"
   ```

3. **Applying Migrations**: To apply the migrations to the database, use:
   ```
   flask db upgrade
   ```

4. **Downgrading Migrations**: If you need to revert to a previous migration, you can downgrade using:
   ```
   flask db downgrade
   ```

### Best Practices

- Always review the generated migration scripts before applying them to ensure they accurately reflect the intended changes.
- Keep your migrations organized and descriptive to make it easier to track changes over time.
- Regularly back up your database, especially before applying new migrations.

### Additional Resources

For more detailed information on managing migrations, refer to the [Flask-Migrate documentation](https://flask-migrate.readthedocs.io/en/latest/).