import netrc
import base64
import json
import logging
import os
import posixpath
import shutil
import urllib
from http.cookiejar import CookieJar
from os import makedirs
from os.path import abspath, expanduser
from os.path import dirname
from os.path import exists
from os.path import join
from time import perf_counter
import logging

import colored_logging as cl

logger = logging.getLogger(__name__)

import rasters as rt
from rasters import RasterGeometry, Raster

DEFAULT_URL = "https://daac.ornl.gov/daacdata/global_vegetation/Global_Clumping_Index/data/global_clumping_index.tif"
DEFAULT_DIRECTORY = join("~", "data", "MODISCI")

__author__ = "Gregory Halverson"


class MODISCI:
    logger = logging.getLogger(__name__)
    DEFAULT_CHUNK_SIZE = 2 ** 20

    def __init__(
            self,
            username: str = None,
            password: str = None,
            URL: str = None,
            directory: str = None,
            chunk_size: int = DEFAULT_CHUNK_SIZE):
        if URL is None:
            URL = DEFAULT_URL

        if directory is None:
            directory = DEFAULT_DIRECTORY

        if username is None or password is None:
            try:
                netrc_file = netrc.netrc()
                username, _, password = netrc_file.authenticators("daac.ornl.gov")
            except Exception as e:
                logger.warning("netrc credentials not found for daac.ornl.gov")

        if username is None or password is None:
            try:
                netrc_file = netrc.netrc()
                username, _, password = netrc_file.authenticators("urs.earthdata.nasa.gov")
            except Exception as e:
                logger.warning("netrc credentials not found for urs.earthdata.nasa.gov")

        self.URL = URL
        self.directory = directory
        self.chunk_size = chunk_size
        self._username = username
        self._password = password
        self._authenticate()

    def __repr__(self) -> str:
        return f'MODISCI(URL="{self.URL}", directory="{self.directory}")'

    def _authenticate(self):
        # https://wiki.earthdata.nasa.gov/display/EL/How+To+Access+Data+With+Python

        password_manager = urllib.request.HTTPPasswordMgrWithDefaultRealm()

        password_manager.add_password(
            realm=None,
            uri="https://urs.earthdata.nasa.gov",
            user=self._username,
            passwd=self._password
        )

        cookie_jar = CookieJar()

        # Install all the handlers.

        opener = urllib.request.build_opener(
            urllib.request.HTTPBasicAuthHandler(password_manager),
            # urllib2.HTTPHandler(debuglevel=1),    # Uncomment these two lines to see
            # urllib2.HTTPSHandler(debuglevel=1),   # details of the requests/responses
            urllib.request.HTTPCookieProcessor(cookie_jar)
        )

        urllib.request.install_opener(opener)

    @property
    def filename(self) -> str:
        return join(self.directory, posixpath.basename(self.URL))

    @property
    def filename_absolute(self) -> str:
        return abspath(expanduser(self.filename))

    def download(self) -> str:
        if exists(self.filename_absolute):
            self.logger.info("file already downloaded: " + cl.file(self.filename))
            return self.filename

        self.logger.info(f"downloading: {self.URL} -> {self.filename}")
        directory = dirname(self.filename_absolute)
        makedirs(directory, exist_ok=True)
        partial_filename = f"{self.filename_absolute}.download"
        command = f'wget -c --user {self._username} --password {self._password} -O "{partial_filename}" "{self.URL}"'
        download_start = perf_counter()
        os.system(command)
        download_end = perf_counter()
        download_duration = download_end - download_start
        self.logger.info(f"completed download in {download_duration:0.2f} seconds: {self.filename}")

        if not exists(partial_filename):
            raise IOError(f"unable to download URL: {self.URL}")

        shutil.move(partial_filename, self.filename_absolute)

        return self.filename

    def CI(self, geometry: RasterGeometry, resampling=None) -> Raster:
        self.download()
        CI = rt.Raster.open(self.filename_absolute, geometry=geometry, resampling=resampling, fill=20) / 255

        return CI
