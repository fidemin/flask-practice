from src.main import create_app

if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        from src.main.operators.fileserver import UploadCSVFromTableOperator

        upload_csv = UploadCSVFromTableOperator(table_name="very_large_table")
        upload_csv.execute()
