from flask import Flask, send_file, after_this_request
from database import dbapi
import pandas as pd
import os
import tempfile

app = Flask(__name__)
db = dbapi.DatabaseConnector()
session = db.session


@app.route('/download/<book_id>')
def download(book_id):
    borrow = session.query(dbapi.Borrow).filter_by(book_id=book_id)
    pd.read_sql(borrow.statement, session.bind).to_excel(f"../user_downloads/book_{book_id}_info.xlsx")
    @after_this_request
    def remove_file(response):
        try:
            os.remove(f"../user_downloads/book_{book_id}_info.xlsx")
        except Exception as e:
            app.logger.e("Error removing or closing file handle", e)
        return response
    return send_file(f"../user_downloads/book_{book_id}_info.xlsx")
