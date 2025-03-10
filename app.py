from flask import Flask, request, jsonify
import xarray as xr
import pandas as pd
from scipy.stats import linregress
import glob
import re
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
# Helper function to extract date from filenames
def extract_date(filename):
    match = re.search(r"RDEFT4_(\d{8})", filename)
    return pd.to_datetime(match.group(1), format="%Y%m%d") if match else None

@app.route('/get_sea_ice_trend', methods=['GET'])
def get_sea_ice_trend():
    # Get the start and end dates from query parameters
    start_year = int(request.args.get('startYear'))
    start_month = int(request.args.get('startMonth'))
    start_day = int(request.args.get('startDay'))
    
    end_year = int(request.args.get('endYear'))
    end_month = int(request.args.get('endMonth'))
    end_day = int(request.args.get('endDay'))

    # Create datetime objects
    start_date = pd.to_datetime(f"{start_year}-{start_month:02d}-{start_day:02d}")
    end_date = pd.to_datetime(f"{end_year}-{end_month:02d}-{end_day:02d}")

    # Get all relevant NetCDF files based on the date range
    # Adjusting the file pattern to dynamically fetch files for the given year range
    nc_files = []
    for year in range(start_year, end_year + 1):
        # We need the files for each year in the '2024' directory
        files_for_year = glob.glob(f"2024/RDEFT4_{year}*.nc")  # Change from 2021 to 2024
        nc_files.extend(files_for_year)

    # Now filter the files by date range
    dates = []
    mean_thickness = []

    for file_path in sorted(nc_files):
        date = extract_date(file_path)
        if date and start_date <= date <= end_date:
            ds = xr.open_dataset(file_path)
            sea_ice = ds["sea_ice_thickness"]
            sea_ice_valid = sea_ice.where((sea_ice >= 0) & (sea_ice != -9999) & (sea_ice != -999))
            
            # Compute mean thickness
            mean_value = sea_ice_valid.mean().item()
            mean_thickness.append(mean_value)
            dates.append(date)

    # Perform linear regression
    df = pd.DataFrame({"Date": dates, "Mean_Thickness": mean_thickness}).sort_values("Date")
    df['Date_ordinal'] = df['Date'].apply(lambda x: x.toordinal())
    
    # Perform linear regression to find the trend line
    slope, intercept, r_value, p_value, std_err = linregress(df['Date_ordinal'], df['Mean_Thickness'])
    df['Trend_Line'] = slope * df['Date_ordinal'] + intercept
    
    # Prepare the data to send back
    response_data = {
        'dates': df['Date'].dt.strftime('%Y-%m-%d').tolist(),
        'mean_thickness': df['Mean_Thickness'].tolist(),
        'trend_line': df['Trend_Line'].tolist()
    }

    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)
