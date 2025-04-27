# schema_dump.py
from app import create_app, db
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    inspector = inspect(db.engine)
    
    # Get all table names
    tables = inspector.get_table_names()
    
    with open('schema.txt', 'w') as f:
        for table in tables:
            f.write(f"Table: {table}\n")
            f.write("-" * 50 + "\n")
            
            # Get columns
            columns = inspector.get_columns(table)
            f.write("Columns:\n")
            for column in columns:
                f.write(f"  - {column['name']} ({column['type']})")
                if column.get('nullable') is False:
                    f.write(" NOT NULL")
                if column.get('default') is not None:
                    f.write(f" DEFAULT {column['default']}")
                f.write("\n")
            
            # Get primary keys
            pks = inspector.get_pk_constraint(table)
            if pks.get('constrained_columns'):
                f.write("\nPrimary Key:\n")
                f.write(f"  - {', '.join(pks['constrained_columns'])}\n")
            
            # Get foreign keys
            fks = inspector.get_foreign_keys(table)
            if fks:
                f.write("\nForeign Keys:\n")
                for fk in fks:
                    f.write(f"  - {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}\n")
            
            # Get indexes
            indexes = inspector.get_indexes(table)
            if indexes:
                f.write("\nIndexes:\n")
                for index in indexes:
                    f.write(f"  - {index['name']} on ({', '.join(index['column_names'])})")
                    if index.get('unique'):
                        f.write(" UNIQUE")
                    f.write("\n")
            
            f.write("\n\n")

    print(f"Schema dumped to schema.txt")