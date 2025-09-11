import json
import pandas as pd
from tqdm import tqdm
import geopandas as gpd

from google.cloud import storage


class FullModel:
    @staticmethod
    def download() -> gpd.GeoDataFrame:
        """
        Downloads the Full Network Model from the Google Cloud Storage bucket.

        Source:
        - Google Cloud Storage Bucket: hubble-elr-geojsons
        - Blob: Data/2024-March/NetworkLinks.geojson

        Returns:
        --------
        elr_gdf : gpd.GeoDataFrame
            GeoDataFrame of the Full Network Model.

        Notes:
        ------
        See docs: https://docs.crosstech.co.uk/doc/network-model-kfGqIB0lxL
        """
        client = storage.Client()
        bucket = client.get_bucket("hubble-elr-geojsons")
        blob = bucket.blob("Data/2024-March/NetworkLinks.geojson")

        elr_string = json.loads(blob.download_as_string())
        elr_gdf = gpd.GeoDataFrame.from_features(elr_string["features"])
        elr_gdf.crs = "EPSG:27700"

        return elr_gdf


class SimplifiedModel:
    @staticmethod
    def download_full() -> gpd.GeoDataFrame:
        """
        Downloads the Simplified Network Model (CRS ESPG:4326) in full from the Google Cloud Storage bucket.

        Source:
        - Google Cloud Storage Bucket: hubble-elr-geojsons
        - Blob: Data/2024-March/NetworkLinks.geojson

        Returns:
        --------
        elr_gdf : gpd.GeoDataFrame
            GeoDataFrame of the Full Network Model.

        Notes:
        ------
        See docs: https://docs.crosstech.co.uk/doc/network-model-kfGqIB0lxL
        """
        client = storage.Client()
        bucket = client.get_bucket("hubble-elr-geojsons")
        blob = bucket.blob("Data/2024-March-Simplified/NetworkModel.geojson")

        elr_string = json.loads(blob.download_as_string())
        elr_gdf = gpd.GeoDataFrame.from_features(elr_string["features"])
        elr_gdf.crs = "EPSG:4326"

        return elr_gdf

    @staticmethod
    def download_ref_lines(**kwargs) -> gpd.GeoDataFrame:
        """
        Downloads the Simplified Network Model Reference Lines from the Google Cloud Storage bucket, ELR by ELR.
        You can specify the ELR or ELRs you want to download, optionally.

        Parameters:
        -----------
        elr : str (optional)
            The ELR you want to download.
        elrs : list[str] (optional)
            A list of ELRs you want to download

        Returns:
        --------
        merged_gdf : gpd.GeoDataFrame
            GeoDataFrame of the Reference Lines.

        Notes:
        ------
        See docs: https://docs.crosstech.co.uk/doc/network-model-kfGqIB0lxL
        """
        elr: str = kwargs.get("elr", None)
        elrs: list[str] = kwargs.get("elrs", None)

        client = storage.Client()
        bucket = client.get_bucket("hubble-elr-geojsons")
        blobs = list(bucket.list_blobs(prefix="reference_line_geojsons/"))

        if elr is not None:
            blobs = [blob for blob in blobs if elr in blob.name]
        if elrs is not None and len(elrs) != 0:
            blobs = [blob for blob in blobs if any(elr in blob.name for elr in elrs)]

        gdfs = []
        for blob in tqdm(blobs):
            if blob.name.endswith(".geojson"):
                elr_string = json.loads(blob.download_as_string())
                elr_gdf = gpd.GeoDataFrame.from_features(elr_string["features"])
                elr_gdf.crs = "EPSG:4326"
                gdfs.append(elr_gdf)

        if gdfs:
            merged_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
            return merged_gdf
        else:
            return gpd.GeoDataFrame()

    @staticmethod
    def download_chain_segments(**kwargs) -> gpd.GeoDataFrame:
        """
        Downloads the Simplified Network Model by chains from the Google Cloud Storage bucket, ELR by ELR.
        You can specify the ELR or ELRs you want to download, optionally. Each ELR file is separated by single chain segments.

        !DANGER!
        Don't use .explore() on the whole dataset, it will fry your RAM.

        Parameters:
        -----------
        elr : str (optional)
            The ELR you want to download.
        elrs : list[str] (optional)
            A list of ELRs you want to download

        Returns:
        --------
        merged_gdf : gpd.GeoDataFrame
            GeoDataFrame of the Reference Lines.

        Notes:
        ------
        See docs: https://docs.crosstech.co.uk/doc/network-model-kfGqIB0lxL
        """
        elr = kwargs.get("elr", None)
        elrs = kwargs.get("elrs", None)

        client = storage.Client()
        bucket = client.get_bucket("hubble-elr-geojsons")
        blobs = list(bucket.list_blobs(prefix="elr_by_chain_geojsons/"))

        if elr is not None:
            blobs = [blob for blob in blobs if elr in blob.name]
        if elrs is not None and len(elrs) != 0:
            blobs = [blob for blob in blobs if any(elr in blob.name for elr in elrs)]

        gdfs = []
        for blob in tqdm(blobs):
            if blob.name.endswith(".geojson"):
                elr_string = json.loads(blob.download_as_string())
                elr_gdf = gpd.GeoDataFrame.from_features(elr_string["features"])
                elr_gdf.crs = "EPSG:4326"
                gdfs.append(elr_gdf)

        if gdfs:
            merged_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True))
            return merged_gdf
        else:
            return gpd.GeoDataFrame()
