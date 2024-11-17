from src.main import create_app

if __name__ == '__main__':
    app = create_app()

    with app.app_context():
        from src.main.operators.fileserver import UploadCSVFromTableOperator

        upload_csv = UploadCSVFromTableOperator(table_name="very_large_table", chunk_size=20 * 1024 * 1024)
        upload_csv.execute_alt()
