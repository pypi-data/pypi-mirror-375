import requests
import pandas as pd
import geopandas as gpd


class Sections:
    URL = "https://virbatim.ew.r.appspot.com/geojson/sections.geojson"

    @staticmethod
    def download() -> pd.DataFrame:
        """
        Downloads sections.geojson from a google bucket.

        Returns:
        --------
        sections_gdf : gpd.GeoDataFrame
            GeoDataFrame of the railway section
        """
        response = requests.get(Sections.URL)
        data = response.json()

        return gpd.GeoDataFrame.from_features(data["features"])
