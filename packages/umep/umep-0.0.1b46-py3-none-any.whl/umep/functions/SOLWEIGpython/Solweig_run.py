# This is the main function of the SOLWEIG model
# 2025-Mar-21
# Fredrik Lindberg, fredrikl@gvc.gu.se
# Goteborg Urban Climate Group
# Gothenburg University

# sommon imports
import json
import zipfile
from shutil import copyfile

import matplotlib.pylab as plt
import numpy as np
import pandas as pd

from ...functions import wallalgorithms as wa
from ...functions.SOLWEIGpython import PET_calculations as p
from ...functions.SOLWEIGpython import Solweig_2025a_calc_forprocessing as so
from ...functions.SOLWEIGpython import UTCI_calculations as utci
from ...functions.SOLWEIGpython.CirclePlotBar import PolarBarPlot
from ...functions.SOLWEIGpython.patch_characteristics import hemispheric_image
from ...functions.SOLWEIGpython.Tgmaps_v1 import Tgmaps_v1
from ...functions.SOLWEIGpython.wall_surface_temperature import load_walls
from ...functions.SOLWEIGpython.wallsAsNetCDF import walls_as_netcdf
from ...util.SEBESOLWEIGCommonFiles.clearnessindex_2013b import clearnessindex_2013b
from ...util.SEBESOLWEIGCommonFiles.Solweig_v2015_metdata_noload import Solweig_2015a_metdata_noload
from ...util.umep_solweig_export_component import read_solweig_config

# imports from osgeo/qgis dependency
try:
    from osgeo.gdalconst import *

    from ...functions.SOLWEIGpython.wallOfInterest import pointOfInterest
except:
    pass

# imports for standalone
try:
    import geopandas as gpd
    from rasterio.transform import Affine, rowcol
    from tqdm import tqdm

    from umep import common
except:
    pass


def solweig_run(configPath, feedback):
    """
    Input:
    configPath : config file including geodata paths and settings.
    feedback : To communicate with qgis gui. Set to None if standalone
    """

    # Load config file
    configDict = read_solweig_config(configPath)

    # Load parameters settings for SOLWEIG
    with open(configDict["para_json_path"]) as jsn:
        param = json.load(jsn)

    standAlone = int(configDict["standalone"])

    # Load DSM
    dsm_arr, dsm_trf_arr, dsm_crs_wkt, dsm_nd_val = common.load_raster(configDict["filepath_dsm"], bbox=None)
    # trf is a list: [top left x, w-e pixel size, rotation, top left y, rotation, n-s pixel size]
    scale = 1 / dsm_trf_arr[1]  # pixel resolution in metres
    left_x = dsm_trf_arr[0]
    top_y = dsm_trf_arr[3]
    lng, lat = common.xy_to_lnglat(dsm_crs_wkt, left_x, top_y)
    rows = dsm_arr.shape[0]
    cols = dsm_arr.shape[1]

    # response to issue #85
    dsm_arr[dsm_arr == dsm_nd_val] = 0.0
    if dsm_arr.min() < 0:
        dsmraise = np.abs(dsm_arr.min())
        dsm_arr = dsm_arr + dsmraise
    else:
        dsmraise = 0

    alt = np.median(dsm_arr)
    if alt < 0:
        alt = 3

    # Vegetation
    transVeg = param["Tree_settings"]["Value"]["Transmissivity"]
    trunkratio = param["Tree_settings"]["Value"]["Trunk_ratio"]
    usevegdem = int(configDict["usevegdem"])
    if usevegdem == 1:
        vegdsm, _, _, _ = common.load_raster(configDict["filepath_cdsm"], bbox=None)
        if configDict["filepath_tdsm"] != "":
            vegdsm2, _, _, _ = common.load_raster(configDict["filepath_tdsm"], bbox=None)
        else:
            vegdsm2 = vegdsm * trunkratio
    else:
        vegdsm = 0
        vegdsm2 = 0

    # Land cover
    landcover = int(configDict["landcover"])
    if landcover == 1:
        lcgrid, _, _, _ = common.load_raster(configDict["filepath_lc"], bbox=None)
    else:
        lcgrid = 0

    # DEM for buildings #TODO: fix nodata in standalone
    demforbuild = int(configDict["demforbuild"])
    if demforbuild == 1:
        dem, _, _, dem_nd_val = common.load_raster(configDict["filepath_dem"], bbox=None)
        # response to issue and #230
        dem[dem == dem_nd_val] = 0.0
        if dem.min() < 0:
            demraise = np.abs(dem.min())
            dem = dem + demraise
        else:
            demraise = 0

    # SVF
    zip = zipfile.ZipFile(configDict["input_svf"], "r")
    zip.extractall(configDict["working_dir"])
    zip.close()

    svf, _, _, _ = common.load_raster(configDict["working_dir"] + "/svf.tif", bbox=None)
    svfN, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfN.tif", bbox=None)
    svfS, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfS.tif", bbox=None)
    svfE, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfE.tif", bbox=None)
    svfW, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfW.tif", bbox=None)

    if usevegdem == 1:
        svfveg, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfveg.tif", bbox=None)
        svfNveg, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfNveg.tif", bbox=None)
        svfSveg, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfSveg.tif", bbox=None)
        svfEveg, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfEveg.tif", bbox=None)
        svfWveg, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfWveg.tif", bbox=None)

        svfaveg, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfaveg.tif", bbox=None)
        svfNaveg, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfNaveg.tif", bbox=None)
        svfSaveg, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfSaveg.tif", bbox=None)
        svfEaveg, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfEaveg.tif", bbox=None)
        svfWaveg, _, _, _ = common.load_raster(configDict["working_dir"] + "/svfWaveg.tif", bbox=None)
    else:
        svfveg = np.ones((rows, cols))
        svfNveg = np.ones((rows, cols))
        svfSveg = np.ones((rows, cols))
        svfEveg = np.ones((rows, cols))
        svfWveg = np.ones((rows, cols))
        svfaveg = np.ones((rows, cols))
        svfNaveg = np.ones((rows, cols))
        svfSaveg = np.ones((rows, cols))
        svfEaveg = np.ones((rows, cols))
        svfWaveg = np.ones((rows, cols))

    tmp = svf + svfveg - 1.0
    tmp[tmp < 0.0] = 0.0
    # %matlab crazyness around 0
    svfalfa = np.arcsin(np.exp(np.log(1.0 - tmp) / 2.0))

    wallheight, _, _, _ = common.load_raster(configDict["filepath_wh"], bbox=None)
    wallaspect, _, _, _ = common.load_raster(configDict["filepath_wa"], bbox=None)

    # Metdata
    headernum = 1
    delim = " "
    Twater = []

    metdata = np.loadtxt(configDict["input_met"], skiprows=headernum, delimiter=delim)

    location = {"longitude": lng, "latitude": lat, "altitude": alt}
    YYYY, altitude, azimuth, zen, jday, leafon, dectime, altmax = Solweig_2015a_metdata_noload(
        metdata, location, int(configDict["utc"])
    )

    DOY = metdata[:, 1]
    hours = metdata[:, 2]
    minu = metdata[:, 3]
    Ta = metdata[:, 11]
    RH = metdata[:, 10]
    radG = metdata[:, 14]
    radD = metdata[:, 21]
    radI = metdata[:, 22]
    P = metdata[:, 12]
    Ws = metdata[:, 9]

    # POIs check
    if configDict["poi_file"] != "":  # usePOI:
        header = (
            "yyyy id   it imin dectime altitude azimuth kdir kdiff kglobal kdown   kup    keast ksouth "
            "kwest knorth ldown   lup    least lsouth lwest  lnorth   Ta      Tg     RH    Esky   Tmrt    "
            "I0     CI   Shadow  SVF_b  SVF_bv KsideI PET UTCI  CI_Tg   CI_TgG  KsideD  Lside   diffDown    Kside"
        )
        poi_field = configDict["poi_field"]
        if standAlone == 0:
            poi_field = configDict["poi_field"]
            poisxy, poiname = pointOfInterest(configDict["poi_file"], poi_field, scale, gdal_dsm)
        else:
            pois_gdf = gpd.read_file(configDict["poi_file"])
            numfeat = pois_gdf.shape[0]
            poisxy = np.zeros((numfeat, 3)) - 999
            poiname = []
            for idx, row in pois_gdf.iterrows():
                y, x = rowcol(
                    Affine.from_gdal(*dsm_trf_arr), row["geometry"].centroid.x, row["geometry"].centroid.y
                )  # TODO: This produce different result since no standalone round coordinates
                if configDict["poi_field"]:
                    poiname.append(row[configDict["poi_field"]])
                else:
                    poiname.append(str(idx))
                poisxy[idx, 0] = idx
                poisxy[idx, 1] = x
                poisxy[idx, 2] = y

        for k in range(0, poisxy.shape[0]):
            poi_save = []
            data_out = configDict["output_dir"] + "POI_" + str(poiname[k]) + ".txt"
            np.savetxt(data_out, poi_save, delimiter=" ", header=header, comments="")
        print(poisxy)
        # Num format for POI output
        numformat = "%d %d %d %d %.5f " + "%.2f " * 36

        # Other PET variables
        sensorheight = param["Wind_Height"]["Value"]["magl"]
        age = param["PET_settings"]["Value"]["Age"]
        mbody = param["PET_settings"]["Value"]["Weight"]
        ht = param["PET_settings"]["Value"]["Height"]
        clo = param["PET_settings"]["Value"]["clo"]
        activity = param["PET_settings"]["Value"]["Activity"]
        sex = param["PET_settings"]["Value"]["Sex"]
    else:
        poisxy = None

    # Posture settings
    if param["Tmrt_params"]["Value"]["posture"] == "Standing":
        Fside = param["Posture"]["Standing"]["Value"]["Fside"]
        Fup = param["Posture"]["Standing"]["Value"]["Fup"]
        height = param["Posture"]["Standing"]["Value"]["height"]
        Fcyl = param["Posture"]["Standing"]["Value"]["Fcyl"]
        pos = 1
    else:
        Fside = param["Posture"]["Sitting"]["Value"]["Fside"]
        Fup = param["Posture"]["Sitting"]["Value"]["Fup"]
        height = param["Posture"]["Sitting"]["Value"]["height"]
        Fcyl = param["Posture"]["Sitting"]["Value"]["Fcyl"]
        pos = 0

    # Radiative surface influence, Rule of thumb by Schmid et al. (1990).
    first = np.round(height)
    if first == 0.0:
        first = 1.0
    second = np.round(height * 20.0)

    if usevegdem == 1:
        # Conifer or deciduous
        if configDict["conifer_bool"]:
            leafon = np.ones((1, DOY.shape[0]))
        else:
            leafon = np.zeros((1, DOY.shape[0]))
            if param["Tree_settings"]["Value"]["First_day_leaf"] > param["Tree_settings"]["Value"]["Last_day_leaf"]:
                leaf_bool = (param["Tree_settings"]["Value"]["First_day_leaf"] < DOY) | (
                    param["Tree_settings"]["Value"]["Last_day_leaf"] > DOY
                )
            else:
                leaf_bool = (param["Tree_settings"]["Value"]["First_day_leaf"] < DOY) & (
                    param["Tree_settings"]["Value"]["Last_day_leaf"] > DOY
                )
            leafon[0, leaf_bool] = 1

        # % Vegetation transmittivity of shortwave radiation
        psi = leafon * transVeg
        psi[leafon == 0] = 0.5
        # amaxvalue
        vegmax = vegdsm.max()
        amaxvalue = dsm_arr.max() - dsm_arr.min()
        amaxvalue = np.maximum(amaxvalue, vegmax)

        # Elevation vegdsms if buildingDEM includes ground heights
        vegdsm = vegdsm + dsm_arr
        vegdsm[vegdsm == dsm_arr] = 0
        vegdsm2 = vegdsm2 + dsm_arr
        vegdsm2[vegdsm2 == dsm_arr] = 0

        # % Bush separation
        bush = np.logical_not(vegdsm2 * vegdsm) * vegdsm

        svfbuveg = svf - (1.0 - svfveg) * (1.0 - transVeg)  # % major bug fixed 20141203
    else:
        psi = leafon * 0.0 + 1.0
        svfbuveg = svf
        bush = np.zeros([rows, cols])
        amaxvalue = 0

    # Initialization of maps
    Knight = np.zeros((rows, cols))
    Tgmap1 = np.zeros((rows, cols))
    Tgmap1E = np.zeros((rows, cols))
    Tgmap1S = np.zeros((rows, cols))
    Tgmap1W = np.zeros((rows, cols))
    Tgmap1N = np.zeros((rows, cols))

    # Create building boolean raster from either land cover or height rasters
    if demforbuild == 0:
        buildings = np.copy(lcgrid)
        buildings[buildings == 7] = 1
        buildings[buildings == 6] = 1
        buildings[buildings == 5] = 1
        buildings[buildings == 4] = 1
        buildings[buildings == 3] = 1
        buildings[buildings == 2] = 0
    else:
        buildings = dsm_arr - dem
        buildings[buildings < 2.0] = 1.0
        buildings[buildings >= 2.0] = 0.0

    if int(configDict["savebuild"]) == 1:
        common.save_raster(
            configDict["output_dir"] + "/buildings.tif",
            buildings,
            dsm_trf_arr,
            dsm_crs_wkt,
            dsm_nd_val,
        )

    # Import shadow matrices (Anisotropic sky)
    anisotropic_sky = int(configDict["aniso"])
    if anisotropic_sky == 1:  # UseAniso
        data = np.load(configDict["input_aniso"])
        shmat = data["shadowmat"]
        vegshmat = data["vegshadowmat"]
        vbshvegshmat = data["vbshmat"]
        if usevegdem == 1:
            diffsh = np.zeros((rows, cols, shmat.shape[2]))
            for i in range(0, shmat.shape[2]):
                diffsh[:, :, i] = shmat[:, :, i] - (1 - vegshmat[:, :, i]) * (
                    1 - transVeg
                )  # changes in psi not implemented yet
        else:
            diffsh = shmat

        # Estimate number of patches based on shadow matrices
        if shmat.shape[2] == 145:
            patch_option = 1  # patch_option = 1 # 145 patches
        elif shmat.shape[2] == 153:
            patch_option = 2  # patch_option = 2 # 153 patches
        elif shmat.shape[2] == 306:
            patch_option = 3  # patch_option = 3 # 306 patches
        elif shmat.shape[2] == 612:
            patch_option = 4  # patch_option = 4 # 612 patches

        # asvf to calculate sunlit and shaded patches
        asvf = np.arccos(np.sqrt(svf))

        # Empty array for steradians
        steradians = np.zeros(shmat.shape[2])
    else:
        # anisotropic_sky = 0
        diffsh = None
        shmat = None
        vegshmat = None
        vbshvegshmat = None
        asvf = None
        patch_option = 0
        steradians = 0

    # % Ts parameterisation maps
    if landcover == 1.0:
        # Get land cover properties for Tg wave (land cover scheme based on Bogren et al. 2000, explained in Lindberg et al., 2008 and Lindberg, Onomura & Grimmond, 2016)
        [TgK, Tstart, alb_grid, emis_grid, TgK_wall, Tstart_wall, TmaxLST, TmaxLST_wall] = Tgmaps_v1(
            lcgrid.copy(), param
        )
    else:
        TgK = Knight + param["Ts_deg"]["Value"]["Cobble_stone_2014a"]
        Tstart = Knight - param["Tstart"]["Value"]["Cobble_stone_2014a"]
        TmaxLST = param["TmaxLST"]["Value"]["Cobble_stone_2014a"]
        alb_grid = Knight + param["Albedo"]["Effective"]["Value"]["Cobble_stone_2014a"]
        emis_grid = Knight + param["Emissivity"]["Value"]["Cobble_stone_2014a"]
        TgK_wall = param["Ts_deg"]["Value"]["Walls"]
        Tstart_wall = param["Tstart"]["Value"]["Walls"]
        TmaxLST_wall = param["TmaxLST"]["Value"]["Walls"]

    # Import data for wall temperature parameterization TODO: fix for standalone
    wallScheme = int(configDict["wallscheme"])
    if wallScheme == 1:
        wallData = np.load(configDict["input_wall"])
        voxelMaps = wallData["voxelId"]
        voxelTable = wallData["voxelTable"]
        # Get wall type from standalone
        if standAlone == 1:
            wall_type_standalone = {"Brick_wall": "100", "Concrete_wall": "101", "Wood_wall": "102"}
            wall_type = wall_type_standalone[configDict["walltype"]]
        else:
            # Get wall type set in GUI
            wall_type = configDict[
                "walltype"
            ]  # str(100 + int(self.parameterAsString(parameters, self.WALL_TYPE, context))) #TODO

        # Get heights of walls including corners
        walls_scheme = wa.findwalls_sp(dsm_arr, 2, np.array([[1, 1, 1], [1, 0, 1], [1, 1, 1]]))
        # Get aspects of walls including corners
        dirwalls_scheme = wa.filter1Goodwin_as_aspect_v3(walls_scheme.copy(), scale, dsm_arr, None, 100.0 / 180.0)

        # Used in wall temperature parameterization scheme
        first_timestep = (
            pd.to_datetime(YYYY[0][0], format="%Y")
            + pd.to_timedelta(DOY[0] - 1, unit="d")
            + pd.to_timedelta(hours[0], unit="h")
            + pd.to_timedelta(minu[0], unit="m")
        )
        second_timestep = (
            pd.to_datetime(YYYY[0][1], format="%Y")
            + pd.to_timedelta(DOY[1] - 1, unit="d")
            + pd.to_timedelta(hours[1], unit="h")
            + pd.to_timedelta(minu[1], unit="m")
        )

        timeStep = (second_timestep - first_timestep).seconds

        # Load voxelTable as Pandas DataFrame
        voxelTable, dirwalls_scheme = load_walls(
            voxelTable, param, wall_type, dirwalls_scheme, Ta[0], timeStep, alb_grid, landcover, lcgrid, dsm_arr
        )

        # Use wall of interest
        woi_file = configDict["woi_file"]
        if woi_file:
            # (dsm_minx, dsm_x_size, dsm_x_rotation, dsm_miny, dsm_y_rotation, dsm_y_size) = gdal_dsm.GetGeoTransform() #TODO: fix for standalone
            if standAlone == 0:
                woi_field = configDict["woi_field"]  # self.parameterAsStrings(parameters, self.WOI_FIELD, context)
                woisxy, woiname = pointOfInterest(configDict["woi_file"], woi_field, scale, gdal_dsm)
            else:
                pois_gdf = gpd.read_file(configDict["poi_file"])
                numfeat = pois_gdf.shape[0]
                poisxy = np.zeros((numfeat, 3)) - 999
                for idx, row in pois_gdf.iterrows():
                    y, x = rowcol(
                        dsm_trf_arr, row["geometry"].centroid.x, row["geometry"].centroid.y
                    )  # TODO: This produce different result since no standalone round coordinates
                    poiname.append(row[configDict["poi_field"]])
                    poisxy[idx, 0] = idx
                    poisxy[idx, 1] = x
                    poisxy[idx, 2] = y

        # Create pandas datetime object to be used when createing an xarray DataSet where wall temperatures/radiation is stored and eventually saved as a NetCDf
        if configDict["wallnetcdf"] == 1:
            met_for_xarray = (
                pd.to_datetime(YYYY[0][:], format="%Y")
                + pd.to_timedelta(DOY - 1, unit="d")
                + pd.to_timedelta(hours, unit="h")
                + pd.to_timedelta(minu, unit="m")
            )
    else:
        wallScheme = 0
        voxelMaps = 0
        voxelTable = 0
        timeStep = 0
        # thermal_effusivity = 0
        walls_scheme = np.ones((rows, cols)) * 10.0
        dirwalls_scheme = np.ones((rows, cols)) * 10.0

    # Initialisation of time related variables
    if Ta.__len__() == 1:
        timestepdec = 0
    else:
        timestepdec = dectime[1] - dectime[0]
    timeadd = 0.0
    firstdaytime = 1.0

    # Save hemispheric image
    if anisotropic_sky == 1:
        if poisxy is not None:
            patch_characteristics = hemispheric_image(poisxy, shmat, vegshmat, vbshvegshmat, voxelMaps, wallScheme)

    # If metfile starts at night
    CI = 1.0

    # reading variables from config and parameters that is not yet presented
    cyl = int(configDict["cyl"])
    albedo_b = param["Albedo"]["Effective"]["Value"]["Walls"]
    ewall = param["Emissivity"]["Value"]["Walls"]
    onlyglobal = int(configDict["onlyglobal"])
    elvis = 0.0
    absK = param["Tmrt_params"]["Value"]["absK"]
    absL = param["Tmrt_params"]["Value"]["absL"]

    # Main loop
    tmrtplot = np.zeros((rows, cols))
    TgOut1 = np.zeros((rows, cols))

    # Initiate array for I0 values
    if np.unique(DOY).shape[0] > 1:
        unique_days = np.unique(DOY)
        first_unique_day = DOY[unique_days[0] == DOY]
        I0_array = np.zeros(first_unique_day.shape[0])
    else:
        first_unique_day = DOY.copy()
        I0_array = np.zeros(DOY.shape[0])

    if standAlone == 1:
        progress = tqdm(total=Ta.__len__())

    for i in np.arange(0, Ta.__len__()):
        if feedback is not None:
            feedback.setProgress(int(i * (100.0 / Ta.__len__())))  # move progressbar forward
            if feedback.isCanceled():
                feedback.setProgressText("Calculation cancelled")
                break
        else:
            progress.update(1)

        # Daily water body temperature
        if landcover == 1:
            if (dectime[i] - np.floor(dectime[i])) == 0 or (i == 0):
                Twater = np.mean(Ta[jday[0] == np.floor(dectime[i])])
        # Nocturnal cloudfraction from Offerle et al. 2003
        if (dectime[i] - np.floor(dectime[i])) == 0:
            daylines = np.where(np.floor(dectime) == dectime[i])
            if daylines.__len__() > 1:
                alt = altitude[0][daylines]
                alt2 = np.where(alt > 1)
                rise = alt2[0][0]
                [_, CI, _, _, _] = clearnessindex_2013b(
                    zen[0, i + rise + 1],
                    jday[0, i + rise + 1],
                    Ta[i + rise + 1],
                    RH[i + rise + 1] / 100.0,
                    radG[i + rise + 1],
                    location,
                    P[i + rise + 1],
                )
                if (CI > 1.0) or (np.inf == CI):
                    CI = 1.0
            else:
                CI = 1.0

        (
            Tmrt,
            Kdown,
            Kup,
            Ldown,
            Lup,
            Tg,
            ea,
            esky,
            I0,
            CI,
            shadow,
            firstdaytime,
            timestepdec,
            timeadd,
            Tgmap1,
            Tgmap1E,
            Tgmap1S,
            Tgmap1W,
            Tgmap1N,
            Keast,
            Ksouth,
            Kwest,
            Knorth,
            Least,
            Lsouth,
            Lwest,
            Lnorth,
            KsideI,
            TgOut1,
            TgOut,
            radIout,
            radDout,
            Lside,
            Lsky_patch_characteristics,
            CI_Tg,
            CI_TgG,
            KsideD,
            dRad,
            Kside,
            steradians,
            voxelTable,
        ) = so.Solweig_2025a_calc(
            i,
            dsm_arr,
            scale,
            rows,
            cols,
            svf,
            svfN,
            svfW,
            svfE,
            svfS,
            svfveg,
            svfNveg,
            svfEveg,
            svfSveg,
            svfWveg,
            svfaveg,
            svfEaveg,
            svfSaveg,
            svfWaveg,
            svfNaveg,
            vegdsm,
            vegdsm2,
            albedo_b,
            absK,
            absL,
            ewall,
            Fside,
            Fup,
            Fcyl,
            altitude[0][i],
            azimuth[0][i],
            zen[0][i],
            jday[0][i],
            usevegdem,
            onlyglobal,
            buildings,
            location,
            psi[0][i],
            landcover,
            lcgrid,
            dectime[i],
            altmax[0][i],
            wallaspect,
            wallheight,
            cyl,
            elvis,
            Ta[i],
            RH[i],
            radG[i],
            radD[i],
            radI[i],
            P[i],
            amaxvalue,
            bush,
            Twater,
            TgK,
            Tstart,
            alb_grid,
            emis_grid,
            TgK_wall,
            Tstart_wall,
            TmaxLST,
            TmaxLST_wall,
            first,
            second,
            svfalfa,
            svfbuveg,
            firstdaytime,
            timeadd,
            timestepdec,
            Tgmap1,
            Tgmap1E,
            Tgmap1S,
            Tgmap1W,
            Tgmap1N,
            CI,
            TgOut1,
            diffsh,
            shmat,
            vegshmat,
            vbshvegshmat,
            anisotropic_sky,
            asvf,
            patch_option,
            voxelMaps,
            voxelTable,
            Ws[i],
            wallScheme,
            timeStep,
            steradians,
            walls_scheme,
            dirwalls_scheme,
        )

        # Save I0 for I0 vs. Kdown output plot to check if UTC is off
        if i < first_unique_day.shape[0]:
            I0_array[i] = I0
        elif i == first_unique_day.shape[0]:
            # Output I0 vs. Kglobal plot
            radG_for_plot = radG[first_unique_day[0] == DOY]
            dectime_for_plot = dectime[first_unique_day[0] == DOY]
            fig, ax = plt.subplots()
            ax.plot(dectime_for_plot, I0_array, label="I0")
            ax.plot(dectime_for_plot, radG_for_plot, label="Kglobal")
            ax.set_ylabel("Shortwave radiation [$Wm^{-2}$]")
            ax.set_xlabel("Decimal time")
            ax.set_title("UTC" + str(configDict["utc"]))
            ax.legend()
            fig.savefig(configDict["output_dir"] + "/metCheck.png", dpi=150)

        tmrtplot = tmrtplot + Tmrt

        if altitude[0][i] > 0:
            w = "D"
        else:
            w = "N"

        # Write to POIs
        if poisxy is not None:
            for k in range(0, poisxy.shape[0]):
                poi_save = np.zeros((1, 41))
                poi_save[0, 0] = YYYY[0][i]
                poi_save[0, 1] = jday[0][i]
                poi_save[0, 2] = hours[i]
                poi_save[0, 3] = minu[i]
                poi_save[0, 4] = dectime[i]
                poi_save[0, 5] = altitude[0][i]
                poi_save[0, 6] = azimuth[0][i]
                poi_save[0, 7] = radIout
                poi_save[0, 8] = radDout
                poi_save[0, 9] = radG[i]
                poi_save[0, 10] = Kdown[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 11] = Kup[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 12] = Keast[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 13] = Ksouth[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 14] = Kwest[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 15] = Knorth[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 16] = Ldown[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 17] = Lup[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 18] = Least[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 19] = Lsouth[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 20] = Lwest[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 21] = Lnorth[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 22] = Ta[i]
                poi_save[0, 23] = TgOut[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 24] = RH[i]
                poi_save[0, 25] = esky
                poi_save[0, 26] = Tmrt[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 27] = I0
                poi_save[0, 28] = CI
                poi_save[0, 29] = shadow[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 30] = svf[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 31] = svfbuveg[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 32] = KsideI[int(poisxy[k, 2]), int(poisxy[k, 1])]
                # Recalculating wind speed based on powerlaw
                WsPET = (1.1 / sensorheight) ** 0.2 * Ws[i]
                WsUTCI = (10.0 / sensorheight) ** 0.2 * Ws[i]
                resultPET = p._PET(
                    Ta[i], RH[i], Tmrt[int(poisxy[k, 2]), int(poisxy[k, 1])], WsPET, mbody, age, ht, activity, clo, sex
                )
                poi_save[0, 33] = resultPET
                resultUTCI = utci.utci_calculator(Ta[i], RH[i], Tmrt[int(poisxy[k, 2]), int(poisxy[k, 1])], WsUTCI)
                poi_save[0, 34] = resultUTCI
                poi_save[0, 35] = CI_Tg
                poi_save[0, 36] = CI_TgG
                poi_save[0, 37] = KsideD[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 38] = Lside[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 39] = dRad[int(poisxy[k, 2]), int(poisxy[k, 1])]
                poi_save[0, 40] = Kside[int(poisxy[k, 2]), int(poisxy[k, 1])]
                data_out = configDict["output_dir"] + "/POI_" + str(poiname[k]) + ".txt"
                # f_handle = file(data_out, 'a')
                f_handle = open(data_out, "ab")
                np.savetxt(f_handle, poi_save, fmt=numformat)
                f_handle.close()

        # If wall temperature parameterization scheme is in use
        if configDict["wallscheme"] == 1:  # folderWallScheme: TODO: Fix for standalone
            # Store wall data for output
            if woisxy is not None:
                for k in range(0, woisxy.shape[0]):
                    temp_wall = voxelTable.loc[
                        ((voxelTable["ypos"] == woisxy[k, 2]) & (voxelTable["xpos"] == woisxy[k, 1])), "wallTemperature"
                    ].to_numpy()
                    K_in = voxelTable.loc[
                        ((voxelTable["ypos"] == woisxy[k, 2]) & (voxelTable["xpos"] == woisxy[k, 1])), "K_in"
                    ].to_numpy()
                    L_in = voxelTable.loc[
                        ((voxelTable["ypos"] == woisxy[k, 2]) & (voxelTable["xpos"] == woisxy[k, 1])), "L_in"
                    ].to_numpy()
                    wallShade = voxelTable.loc[
                        ((voxelTable["ypos"] == woisxy[k, 2]) & (voxelTable["xpos"] == woisxy[k, 1])), "wallShade"
                    ].to_numpy()
                    temp_all = np.concatenate([temp_wall, K_in, L_in, wallShade])
                    wall_data = np.zeros((1, 7 + temp_all.shape[0]))
                    # Part of file name (wallid), i.e. WOI_wallid.txt
                    data_out = configDict["output_dir"] + "/WOI_" + str(woiname[k]) + ".txt"
                    if i == 0:
                        # Output file header
                        header = (
                            "yyyy id   it imin dectime Ta  SVF"
                            + " Ts" * temp_wall.shape[0]
                            + " Kin" * K_in.shape[0]
                            + " Lin" * L_in.shape[0]
                            + " shade" * wallShade.shape[0]
                        )
                        woi_save = []  #
                        np.savetxt(data_out, woi_save, delimiter=" ", header=header, comments="")
                    # Fill wall_data with variables
                    wall_data[0, 0] = YYYY[0][i]
                    wall_data[0, 1] = jday[0][i]
                    wall_data[0, 2] = hours[i]
                    wall_data[0, 3] = minu[i]
                    wall_data[0, 4] = dectime[i]
                    wall_data[0, 5] = Ta[i]
                    wall_data[0, 6] = svf[int(woisxy[k, 2]), int(woisxy[k, 1])]
                    wall_data[0, 7:] = temp_all

                    # Num format for output file data
                    woi_numformat = "%d %d %d %d %.5f %.2f %.2f" + " %.2f" * temp_all.shape[0]
                    # Open file, add data, save
                    f_handle = open(data_out, "ab")
                    np.savetxt(f_handle, wall_data, fmt=woi_numformat)
                    f_handle.close()

            # Save wall temperature/radiation as NetCDF TODO: fix for standAlone?
            if configDict["wallnetcdf"] == "1":  # wallNetCDF:
                netcdf_output = configDict["outputDir"] + "/walls.nc"
                walls_as_netcdf(
                    voxelTable, rows, cols, met_for_xarray, i, dsm_arr, configDict["filepath_dsm"], netcdf_output
                )

        if hours[i] < 10:
            XH = "0"
        else:
            XH = ""
        if minu[i] < 10:
            XM = "0"
        else:
            XM = ""

        time_code = (
            str(int(YYYY[0, i])) + "_" + str(int(DOY[i])) + "_" + XH + str(int(hours[i])) + XM + str(int(minu[i])) + w
        )

        if configDict["outputtmrt"] == "1":
            common.save_raster(
                configDict["output_dir"] + "/Tmrt_" + time_code + ".tif",
                Tmrt,
                dsm_trf_arr,
                dsm_crs_wkt,
                dsm_nd_val,
            )
        if configDict["outputkup"] == "1":
            common.save_raster(
                configDict["output_dir"] + "/Kup_" + time_code + ".tif",
                Kup,
                dsm_trf_arr,
                dsm_crs_wkt,
                dsm_nd_val,
            )
        if configDict["outputkdown"] == "1":
            common.save_raster(
                configDict["output_dir"] + "/Kdown_" + time_code + ".tif",
                Kdown,
                dsm_trf_arr,
                dsm_crs_wkt,
                dsm_nd_val,
            )
        if configDict["outputlup"] == "1":
            common.save_raster(
                configDict["output_dir"] + "/Lup_" + time_code + ".tif",
                Lup,
                dsm_trf_arr,
                dsm_crs_wkt,
                dsm_nd_val,
            )
        if configDict["outputldown"] == "1":
            common.save_raster(
                configDict["output_dir"] + "/Ldown_" + time_code + ".tif",
                Ldown,
                dsm_trf_arr,
                dsm_crs_wkt,
                dsm_nd_val,
            )
        if configDict["outputsh"] == "1":
            common.save_raster(
                configDict["output_dir"] + "/Shadow_" + time_code + ".tif",
                shadow,
                dsm_trf_arr,
                dsm_crs_wkt,
                dsm_nd_val,
            )
        if configDict["outputkdiff"] == "1":
            common.save_raster(
                configDict["output_dir"] + "/Kdiff_" + time_code + ".tif",
                dRad,
                dsm_trf_arr,
                dsm_crs_wkt,
                dsm_nd_val,
            )

        # Sky view image of patches
        if (anisotropic_sky == 1) & (i == 0) & (poisxy is not None):
            for k in range(poisxy.shape[0]):
                Lsky_patch_characteristics[:, 2] = patch_characteristics[:, k]
                skyviewimage_out = configDict["output_dir"] + "/POI_" + str(poiname[k]) + ".png"
                PolarBarPlot(
                    Lsky_patch_characteristics,
                    altitude[0][i],
                    azimuth[0][i],
                    "Hemisphere partitioning",
                    skyviewimage_out,
                    0,
                    5,
                    0,
                )

    # Save files for Tree Planter
    if configDict["outputtreeplanter"] == "1":  # outputTreeplanter:
        if feedback is not None:
            feedback.setProgressText("Saving files for Tree Planter tool")
        # Save DSM
        copyfile(configDict["filepath_dsm"], configDict["output_dir"] + "/DSM.tif")

        # Save CDSM
        if usevegdem == 1:
            copyfile(configDict["filepath_cdsm"], configDict["output_dir"] + "/CDSM.tif")

        albedo_g = param["Albedo"]["Effective"]["Value"]["Cobble_stone_2014a"]
        eground = param["Emissivity"]["Value"]["Cobble_stone_2014a"]

        # Saving settings from SOLWEIG for SOLWEIG1D in TreePlanter
        settingsHeader = "UTC, posture, onlyglobal, landcover, anisotropic, cylinder, albedo_walls, albedo_ground, emissivity_walls, emissivity_ground, absK, absL, elevation, patch_option"
        settingsFmt = (
            "%i",
            "%i",
            "%i",
            "%i",
            "%i",
            "%i",
            "%1.2f",
            "%1.2f",
            "%1.2f",
            "%1.2f",
            "%1.2f",
            "%1.2f",
            "%1.2f",
            "%i",
        )
        settingsData = np.array(
            [
                [
                    int(configDict["utc"]),
                    pos,
                    onlyglobal,
                    landcover,
                    anisotropic_sky,
                    cyl,
                    albedo_b,
                    albedo_g,
                    ewall,
                    eground,
                    absK,
                    absL,
                    alt,
                    patch_option,
                ]
            ]
        )
        np.savetxt(
            configDict["output_dir"] + "/treeplantersettings.txt",
            settingsData,
            fmt=settingsFmt,
            header=settingsHeader,
            delimiter=" ",
        )

    # Copying met file for SpatialTC
    copyfile(configDict["input_met"], configDict["output_dir"] + "/metforcing.txt")

    tmrtplot = tmrtplot / Ta.__len__()  # fix average Tmrt instead of sum, 20191022
    common.save_raster(
        configDict["output_dir"] + "/Tmrt_average.tif",
        tmrtplot,
        dsm_trf_arr,
        dsm_crs_wkt,
        dsm_nd_val,
    )
