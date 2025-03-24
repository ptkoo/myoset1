import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import glob
import os

# Find all .nc files in the 2024 folder
nc_files = glob.glob("2021/RDEFT4_*.nc")

for file_path in nc_files:
    # Load the netCDF file
    ds1 = xr.open_dataset(file_path)
    
    # Extract base filename for saving
    base_name = os.path.basename(file_path).replace(".nc", "")
    output_filename = f"2021/{base_name}.png"
    
    # Process data
    sea_ice = ds1["sea_ice_thickness"]
    sea_ice_valid = sea_ice.where(sea_ice != -9999).where(sea_ice != -999).where(sea_ice >= 0)
    
    # Assign coordinates
    sea_ice_valid = sea_ice_valid.rename(y="y", x="x").assign_coords(
        lat=(("y", "x"), ds1["lat"].values),
        lon=(("y", "x"), ds1["lon"].values)
    )

    # Create plot
    fig = plt.figure(figsize=(8, 8))
    ax = plt.subplot(
        1, 1, 1,
        projection=ccrs.Orthographic(central_longitude=0, central_latitude=90)
    )

    sea_ice_valid.plot(
        ax=ax,
        x="lon",
        y="lat",
        transform=ccrs.PlateCarree(),
        cmap="viridis",
        robust=True
    )

    ax.coastlines()
    ax.set_extent([-180, 180, 50, 90], crs=ccrs.PlateCarree())
    plt.title(f"Sea Ice Thickness ({base_name.split('_')[-1]})")
    
    # Save the plot
    plt.savefig(output_filename, bbox_inches='tight', dpi=300)
    plt.close()  # Important to free memory
    
    print(f"Saved: {output_filename}")

print("Processing complete!")