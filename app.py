from flask import Flask, render_template, request, redirect, url_for, send_file, flash
import pandas as pd
import os
from io import BytesIO

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['SAMPLE_DATA_FOLDER'] = 'sample_data/'
app.config['PROCESSED_FOLDER'] = 'processed/'  # Temporary folder to store processed files\
app.secret_key = 'secret_key'
DEFAULT_CSV = os.path.join(app.config['SAMPLE_DATA_FOLDER'], 'trading_symbols_numeric_risk_ratings.csv')


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files.get('file', None)
        num_rows = request.form.get('num_rows', 5, type=int)


        if file and not file.filename.endswith('.csv'):
            flash('Only CSV uploads are allowed. Please upload a CSV file.')
            return redirect(request.url)

        if file and file.filename.endswith('.csv'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
        else:
            file_path = DEFAULT_CSV

        df = pd.read_csv(file_path)
        df.columns = df.columns.str.lower()

        if 'trading symbol' in df.columns: #handle regex

            risk_columns = df.select_dtypes(include=['int64', 'float64']).columns

            #calculations
            df['mean risk'] = df[risk_columns].mean(axis=1)
            max_rows = len(df)
            if num_rows > max_rows:
                flash(f"Requested {num_rows} rows exceeds the total available rows ({max_rows}). Showing all available rows.")
                num_rows = max_rows

            total_risks = df['trading symbol'].nunique()
            min_mean_risk = df['mean risk'].min()
            max_mean_risk = df['mean risk'].max()
            risk_range = (min_mean_risk, max_mean_risk)

            max_risk_symbols = df.nlargest(5, 'mean risk')['trading symbol'].tolist()
            min_risk_symbols = df.nsmallest(5, 'mean risk')['trading symbol'].tolist()
            std_dev_mean_risk = df['mean risk'].std()

            stats = {
                'Total Number of Risks': total_risks,
                'Range': f"({min_mean_risk}, {max_mean_risk})",
                'Max Risks (Top 5)': ', '.join(max_risk_symbols),
                'Min Risks (Top 5)': ', '.join(min_risk_symbols),
                'Standard Deviation of Mean Risk': std_dev_mean_risk
            }
            processed_file_path = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_table.csv')
            df.to_csv(processed_file_path, index=False)

            table_html = df.head(num_rows).to_html(classes='data', index=False).replace("\n", "")

            return render_template('index.html', tables=table_html,

                                   stats=stats, rows=num_rows, download_link=url_for('download_file'))
    return render_template('index.html')


@app.route('/download')
def download_file():
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], 'processed_table.csv')
    return send_file(file_path, as_attachment=True, download_name="processed_table.csv", mimetype='text/csv')


if __name__ == '__main__':
    os.makedirs(app.config['SAMPLE_DATA_FOLDER'], exist_ok=True)
    os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
    app.run(host="0.0.0.0", port=5000,debug=True)