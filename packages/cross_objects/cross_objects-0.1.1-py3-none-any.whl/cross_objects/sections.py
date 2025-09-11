import requests
import pandas as pd
import geopandas as gpd


class Sections:
    URL = "https://virbatim.ew.r.appspot.com/geojson/sections.geojson"

    @staticmethod
    def download() -> gpd.GeoDataFrame:
        """
        Downloads sections.geojson from a google bucket.

        Returns:
        --------
        sections_gdf : gpd.GeoDataFrame
            GeoDataFrame of the railway section
        """
        response = requests.get(Sections.URL)
        data = response.json()
        gdf = gpd.GeoDataFrame.from_features(data["features"])
        gdf.crs = 4326  # It is not saved with CRS for some reason...

        return gdf
