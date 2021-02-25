#!/usr/bin/env python

import sys

import subprocess
import glob
import shutil

import multiprocessing as mp
import itertools

from contextlib import contextmanager

import configobj
import argparse
import textwrap
import os
import csv

import netCDF4

import datetime as dt
import calendar
import numpy as np


'''
About the co2 data:

 - The "old" data are numbers that have been with dvmdostem for a long time and are
probably from here: https://www.esrl.noaa.gov/gmd/ccgg/trends/data.html

 - The RCP_85 ("new") data are from here: http://www.iiasa.ac.at/web-apps/tnt/RcpDb

There are some very small differences in the data around the early 2000s.

Use this to snippet to plot them next to eachother.
    import pandas as pd
    import matplotlib.pyplot as plt
    odf = pd.DataFrame(dict(data=OLD_CO2_DATA, year=OLD_CO2_YEARS))
    ndf = pd.DataFrame(dict(data=RCP_85_CO2_DATA, year=RCP_85_CO2_YEARS))
    a = ndf.merge(odf, how='outer', on='year')
    plt.plot(a.year, a.data_x)
    plt.plot(a.year, a.data_y)
    plt.show()
'''
OLD_CO2_DATA = [ 296.311, 296.661, 297.04, 297.441, 297.86, 298.29, 298.726, 299.163,
  299.595, 300.016, 300.421, 300.804, 301.162, 301.501, 301.829, 302.154, 
  302.48, 302.808, 303.142, 303.482, 303.833, 304.195, 304.573, 304.966, 
  305.378, 305.806, 306.247, 306.698, 307.154, 307.614, 308.074, 308.531, 
  308.979, 309.401, 309.781, 310.107, 310.369, 310.559, 310.667, 310.697, 
  310.664, 310.594, 310.51, 310.438, 310.401, 310.41, 310.475, 310.605, 
  310.807, 311.077, 311.41, 311.802, 312.245, 312.736, 313.27, 313.842, 
  314.448, 315.084, 315.665, 316.535, 317.195, 317.885, 318.495, 318.935, 
  319.58, 320.895, 321.56, 322.34, 323.7, 324.835, 325.555, 326.55, 
  328.455, 329.215, 330.165, 331.215, 332.79, 334.44, 335.78, 337.655, 
  338.925, 340.065, 341.79, 343.33, 344.67, 346.075, 347.845, 350.055, 
  351.52, 352.785, 354.21, 355.225, 356.055, 357.55, 359.62, 361.69, 
  363.76, 365.83, 367.9, 368, 370.1, 372.2, 373.6943, 375.3507, 377.0071, 
  378.6636, 380.5236, 382.3536, 384.1336, 389.90, 391.65, 393.85, 396.52,
  398.65, 400.83, 404.24, 406.55 ]
OLD_CO2_YEARS = [ 1901, 1902, 1903, 1904, 1905, 1906, 1907, 1908, 1909, 1910, 1911,
  1912, 1913, 1914, 1915, 1916, 1917, 1918, 1919, 1920, 1921, 1922, 1923, 
  1924, 1925, 1926, 1927, 1928, 1929, 1930, 1931, 1932, 1933, 1934, 1935, 
  1936, 1937, 1938, 1939, 1940, 1941, 1942, 1943, 1944, 1945, 1946, 1947, 
  1948, 1949, 1950, 1951, 1952, 1953, 1954, 1955, 1956, 1957, 1958, 1959, 
  1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970, 1971, 
  1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 
  1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 
  1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 
  2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017 ]
RCP_85_CO2_YEARS = [
  1765,1766,1767,1768,1769,1770,1771,1772,1773,1774,1775,1776,1777,1778,1779,
  1780,1781,1782,1783,1784,1785,1786,1787,1788,1789,1790,1791,1792,1793,1794,
  1795,1796,1797,1798,1799,1800,1801,1802,1803,1804,1805,1806,1807,1808,1809,
  1810,1811,1812,1813,1814,1815,1816,1817,1818,1819,1820,1821,1822,1823,1824,
  1825,1826,1827,1828,1829,1830,1831,1832,1833,1834,1835,1836,1837,1838,1839,
  1840,1841,1842,1843,1844,1845,1846,1847,1848,1849,1850,1851,1852,1853,1854,
  1855,1856,1857,1858,1859,1860,1861,1862,1863,1864,1865,1866,1867,1868,1869,
  1870,1871,1872,1873,1874,1875,1876,1877,1878,1879,1880,1881,1882,1883,1884,
  1885,1886,1887,1888,1889,1890,1891,1892,1893,1894,1895,1896,1897,1898,1899,
  1900,1901,1902,1903,1904,1905,1906,1907,1908,1909,1910,1911,1912,1913,1914,
  1915,1916,1917,1918,1919,1920,1921,1922,1923,1924,1925,1926,1927,1928,1929,
  1930,1931,1932,1933,1934,1935,1936,1937,1938,1939,1940,1941,1942,1943,1944,
  1945,1946,1947,1948,1949,1950,1951,1952,1953,1954,1955,1956,1957,1958,1959,
  1960,1961,1962,1963,1964,1965,1966,1967,1968,1969,1970,1971,1972,1973,1974,
  1975,1976,1977,1978,1979,1980,1981,1982,1983,1984,1985,1986,1987,1988,1989,
  1990,1991,1992,1993,1994,1995,1996,1997,1998,1999,2000,2001,2002,2003,2004,
  2005,2006,2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017,2018,2019,
  2020,2021,2022,2023,2024,2025,2026,2027,2028,2029,2030,2031,2032,2033,2034,
  2035,2036,2037,2038,2039,2040,2041,2042,2043,2044,2045,2046,2047,2048,2049,
  2050,2051,2052,2053,2054,2055,2056,2057,2058,2059,2060,2061,2062,2063,2064,
  2065,2066,2067,2068,2069,2070,2071,2072,2073,2074,2075,2076,2077,2078,2079,
  2080,2081,2082,2083,2084,2085,2086,2087,2088,2089,2090,2091,2092,2093,2094,
  2095,2096,2097,2098,2099,2100,2101,2102,2103,2104,2105,2106,2107,2108,2109,
  2110,2111,2112,2113,2114,2115,2116,2117,2118,2119,2120,2121,2122,2123,2124,
  2125,2126,2127,2128,2129,2130,2131,2132,2133,2134,2135,2136,2137,2138,2139,
  2140,2141,2142,2143,2144,2145,2146,2147,2148,2149,2150,2151,2152,2153,2154,
  2155,2156,2157,2158,2159,2160,2161,2162,2163,2164,2165,2166,2167,2168,2169,
  2170,2171,2172,2173,2174,2175,2176,2177,2178,2179,2180,2181,2182,2183,2184,
  2185,2186,2187,2188,2189,2190,2191,2192,2193,2194,2195,2196,2197,2198,2199,
  2200,2201,2202,2203,2204,2205,2206,2207,2208,2209,2210,2211,2212,2213,2214,
  2215,2216,2217,2218,2219,2220,2221,2222,2223,2224,2225,2226,2227,2228,2229,
  2230,2231,2232,2233,2234,2235,2236,2237,2238,2239,2240,2241,2242,2243,2244,
  2245,2246,2247,2248,2249,2250,2251,2252,2253,2254,2255,2256,2257,2258,2259,
  2260,2261,2262,2263,2264,2265,2266,2267,2268,2269,2270,2271,2272,2273,2274,
  2275,2276,2277,2278,2279,2280,2281,2282,2283,2284,2285,2286,2287,2288,2289,
  2290,2291,2292,2293,2294,2295,2296,2297,2298,2299,2300,2301,2302,2303,2304,
  2305,2306,2307,2308,2309,2310,2311,2312,2313,2314,2315,2316,2317,2318,2319,
  2320,2321,2322,2323,2324,2325,2326,2327,2328,2329,2330,2331,2332,2333,2334,
  2335,2336,2337,2338,2339,2340,2341,2342,2343,2344,2345,2346,2347,2348,2349,
  2350,2351,2352,2353,2354,2355,2356,2357,2358,2359,2360,2361,2362,2363,2364,
  2365,2366,2367,2368,2369,2370,2371,2372,2373,2374,2375,2376,2377,2378,2379,
  2380,2381,2382,2383,2384,2385,2386,2387,2388,2389,2390,2391,2392,2393,2394,
  2395,2396,2397,2398,2399,2400,2401,2402,2403,2404,2405,2406,2407,2408,2409,
  2410,2411,2412,2413,2414,2415,2416,2417,2418,2419,2420,2421,2422,2423,2424,
  2425,2426,2427,2428,2429,2430,2431,2432,2433,2434,2435,2436,2437,2438,2439,
  2440,2441,2442,2443,2444,2445,2446,2447,2448,2449,2450,2451,2452,2453,2454,
  2455,2456,2457,2458,2459,2460,2461,2462,2463,2464,2465,2466,2467,2468,2469,
  2470,2471,2472,2473,2474,2475,2476,2477,2478,2479,2480,2481,2482,2483,2484,
  2485,2486,2487,2488,2489,2490,2491,2492,2493,2494,2495,2496,2497,2498,2499,
  2500 ]
RCP_85_CO2_DATA = [
  278.0516,  278.1062,  278.2204,  278.3431,  278.4706,  278.6005,  278.7328,  278.8688,
  279.0091,  279.1532,  279.3018,  279.4568,  279.6181,  279.7819,  279.9432,  280.0974,
  280.2428,  280.3817,  280.5183,  280.6572,  280.8026,  280.9568,  281.1181,  281.2819,
  281.4432,  281.5982,  281.7468,  281.8909,  282.0312,  282.1673,  282.2990,  282.4268,
  282.5509,  282.6712,  282.7873,  282.8990,  283.0068,  283.1109,  283.2113,  283.3074,
  283.3996,  283.4898,  283.5780,  283.6612,  283.7351,  283.7968,  283.8467,  283.8885,
  283.9261,  283.9627,  284.0011,  284.0427,  284.0861,  284.1285,  284.1667,  284.1982,
  284.2233,  284.2443,  284.2631,  284.2813,  284.3003,  284.3200,  284.3400,  284.3600,
  284.3800,  284.4000,  284.3850,  284.2800,  284.1250,  283.9750,  283.8250,  283.6750,
  283.5250,  283.4250,  283.4000,  283.4000,  283.4250,  283.5000,  283.6000,  283.7250,
  283.9000,  284.0750,  284.2250,  284.4000,  284.5750,  284.7250,  284.8750,  285.0000,
  285.1250,  285.2750,  285.4250,  285.5750,  285.7250,  285.9000,  286.0750,  286.2250,
  286.3750,  286.5000,  286.6250,  286.7750,  286.9000,  287.0000,  287.1000,  287.2250,
  287.3750,  287.5250,  287.7000,  287.9000,  288.1250,  288.4000,  288.7000,  289.0250,
  289.4000,  289.8000,  290.2250,  290.7000,  291.2000,  291.6750,  292.1250,  292.5750,
  292.9750,  293.3000,  293.5750,  293.8000,  294.0000,  294.1750,  294.3250,  294.4750,
  294.6000,  294.7000,  294.8000,  294.9000,  295.0250,  295.2250,  295.5000,  295.8000,
  296.1250,  296.4750,  296.8250,  297.2000,  297.6250,  298.0750,  298.5000,  298.9000,
  299.3000,  299.7000,  300.0750,  300.4250,  300.7750,  301.1000,  301.4000,  301.7250,
  302.0750,  302.4000,  302.7000,  303.0250,  303.4000,  303.7750,  304.1250,  304.5250,
  304.9750,  305.4000,  305.8250,  306.3000,  306.7750,  307.2250,  307.7000,  308.1750,
  308.6000,  309.0000,  309.4000,  309.7500,  310.0000,  310.1750,  310.3000,  310.3750,
  310.3750,  310.3000,  310.2000,  310.1250,  310.1000,  310.1250,  310.2000,  310.3250,
  310.5000,  310.7500,  311.1000,  311.5000,  311.9250,  312.4250,  313.0000,  313.6000,
  314.2250,  314.8475,  315.5000,  316.2725,  317.0750,  317.7950,  318.3975,  318.9250,
  319.6475,  320.6475,  321.6050,  322.6350,  323.9025,  324.9850,  325.8550,  327.1400,
  328.6775,  329.7425,  330.5850,  331.7475,  333.2725,  334.8475,  336.5250,  338.3600,
  339.7275,  340.7925,  342.1975,  343.7825,  345.2825,  346.7975,  348.6450,  350.7375,
  352.4875,  353.8550,  355.0175,  355.8850,  356.7775,  358.1275,  359.8375,  361.4625,
  363.1550,  365.3225,  367.3475,  368.8650,  370.4675,  372.5225,  374.7600,  376.8125,
  378.8125,  380.8275,  382.7775,  384.8000,  387.0123,  389.3242,  391.6380,  394.0087,
  396.4638,  399.0040,  401.6279,  404.3282,  407.0959,  409.9270,  412.8215,  415.7802,
  418.7963,  421.8644,  424.9947,  428.1973,  431.4747,  434.8262,  438.2446,  441.7208,
  445.2509,  448.8349,  452.4736,  456.1770,  459.9640,  463.8518,  467.8500,  471.9605,
  476.1824,  480.5080,  484.9272,  489.4355,  494.0324,  498.7297,  503.5296,  508.4327,
  513.4561,  518.6106,  523.9001,  529.3242,  534.8752,  540.5428,  546.3220,  552.2119,
  558.2122,  564.3131,  570.5167,  576.8434,  583.3047,  589.9054,  596.6466,  603.5205,
  610.5165,  617.6053,  624.7637,  631.9947,  639.2905,  646.6527,  654.0984,  661.6449,
  669.3047,  677.0776,  684.9543,  692.9020,  700.8942,  708.9316,  717.0155,  725.1360,
  733.3067,  741.5237,  749.8047,  758.1823,  766.6445,  775.1745,  783.7514,  792.3658,
  801.0188,  809.7146,  818.4221,  827.1572,  835.9559,  844.8047,  853.7254,  862.7260,
  871.7768,  880.8644,  889.9816,  899.1241,  908.2887,  917.4714,  926.6653,  935.8744,
  945.1321,  954.4662,  963.8391,  973.2408,  982.6804,  992.1429, 1001.6311, 1011.1191,
  1020.6085, 1030.1004, 1039.5892, 1049.1233, 1058.7002, 1068.3216, 1077.9995, 1087.6999,
  1097.4303, 1107.1765, 1116.9122, 1126.6592, 1136.4015, 1146.1344, 1155.9064, 1165.7401,
  1175.6176, 1185.5295, 1195.4833, 1205.4772, 1215.4661, 1225.4530, 1235.4493, 1245.4190,
  1255.3970, 1265.4211, 1275.4843, 1285.5943, 1295.7632, 1305.9625, 1316.1708, 1326.3936,
  1336.6283, 1346.8594, 1357.0727, 1367.2797, 1377.5097, 1387.7930, 1398.1376, 1408.5226,
  1418.9467, 1429.3969, 1439.8354, 1450.2111, 1460.4793, 1470.5915, 1480.5564, 1490.4552,
  1500.2994, 1510.0573, 1519.7332, 1529.3276, 1538.8274, 1548.2214, 1557.5025, 1566.6838,
  1575.7093, 1584.5792, 1593.3890, 1602.1444, 1610.8232, 1619.4189, 1627.9283, 1636.3423,
  1644.6544, 1652.8621, 1660.9472, 1668.8714, 1676.6491, 1684.3479, 1691.9855, 1699.5543,
  1707.0542, 1714.4671, 1721.7857, 1728.9986, 1736.0730, 1743.0204, 1749.8272, 1756.4845,
  1763.0469, 1769.5420, 1775.9720, 1782.3281, 1788.5985, 1794.7605, 1800.7999, 1806.7334,
  1812.5201, 1818.1423, 1823.6498, 1829.0556, 1834.3733, 1839.6122, 1844.7812, 1849.8682,
  1854.8490, 1859.7106, 1864.4469, 1869.0362, 1873.4672, 1877.7840, 1881.9947, 1886.1097,
  1890.1554, 1894.1313, 1898.0123, 1901.7766, 1905.4235, 1908.9603, 1912.3445, 1915.5465,
  1918.6217, 1921.6126, 1924.5227, 1927.3520, 1930.1000, 1932.7513, 1935.2926, 1937.7127,
  1940.0103, 1942.1583, 1944.1572, 1946.0278, 1947.7762, 1949.4392, 1951.0121, 1952.5138,
  1953.9433, 1955.2718, 1956.4604, 1957.4929, 1958.4280, 1959.1897, 1959.7707, 1960.2847,
  1960.7288, 1961.0674, 1961.3194, 1961.4957, 1961.5683, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774,
  1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774, 1961.5774 ]


# Paths to input files from
BASE_AR5_RCP85_CONFIG = textwrap.dedent('''\
  veg src = 'land_cover/v_0_4/iem_vegetation_model_input_v0_4.tif'

  drainage src = 'drainage/Lowland_1km.tif'

  soil clay src = 'BLISS_IEM/mu_claytotal_r_pct_0_25mineral_2_AK_CAN.img'
  soil sand src = 'BLISS_IEM/mu_sandtotal_r_pct_0_25mineral_2_AK_CAN.img'
  soil silt src = 'BLISS_IEM/mu_silttotal_r_pct_0_25mineral_2_AK_CAN.img'

  topo slope src = 'slope/iem_prism_slope_1km.tif'
  topo aspect src = 'aspect/iem_prism_aspect_1km.tif'
  topo elev src = 'elevation/iem_prism_dem_1km.tif'

  h clim first yr = 1901
  h clim last yr = 2015
  h clim orig inst = 'CRU'
  h clim ver = 'TS40'
  h clim tair src = 'tas_mean_C_iem_cru_TS40_1901_2015/tas/tas_mean_C_CRU_TS40_historical_'
  h clim prec src = 'pr_total_mm_iem_cru_TS40_1901_2015/pr_total_mm_CRU_TS40_historical_'
  h clim rsds src = 'rsds_mean_MJ-m2-d1_iem_CRU-TS40_historical_1901_2015_fix/rsds/rsds_mean_MJ-m2-d1_iem_CRU-TS40_historical_'
  h clim vapo src = 'vap_mean_hPa_iem_CRU-TS40_historical_1901_2015_fix/vap/vap_mean_hPa_iem_CRU-TS40_historical_'

  fire fri src = 'iem_ancillary_data/Fire/FRI.tif'
  ''')

MRI_CGCM3_AR5_RCP85_CONFIG = textwrap.dedent('''\
  p clim first yr = 2006
  p clim last yr = 2100
  p clim ver = 'rcp85'

  p clim orig inst = 'MRI-CGCM3'
  p clim tair src = 'tas_mean_C_ar5_MRI-CGCM3_rcp85_2006_2100/tas/tas_mean_C_iem_ar5_MRI-CGCM3_rcp85_'
  p clim prec src = 'pr_total_mm_ar5_MRI-CGCM3_rcp85_2006_2100/pr/pr_total_mm_iem_ar5_MRI-CGCM3_rcp85_'
  p clim rsds src = 'rsds_mean_MJ-m2-d1_ar5_MRI-CGCM3_rcp85_2006_2100_fix/rsds/rsds_mean_MJ-m2-d1_iem_ar5_MRI-CGCM3_rcp85_'
  p clim vapo src = 'vap_mean_hPa_ar5_MRI-CGCM3_rcp85_2006_2100_fix/vap/vap_mean_hPa_iem_ar5_MRI-CGCM3_rcp85_'
  ''')

NCAR_CCSM4_AR5_RCP85_CONFIG = textwrap.dedent('''\
  p clim first yr = 2006
  p clim last yr = 2100
  p clim ver = 'rcp85'

  p clim orig inst = 'NCAR-CCSM4'
  p clim tair src = 'tas_mean_C_ar5_NCAR-CCSM4_rcp85_2006_2100/tas/tas_mean_C_iem_ar5_NCAR-CCSM4_rcp85_'
  p clim prec src = 'pr_total_mm_ar5_NCAR-CCSM4_rcp85_2006_2100/pr/pr_total_mm_iem_ar5_NCAR-CCSM4_rcp85_'
  p clim rsds src = 'rsds_mean_MJ-m2-d1_ar5_NCAR-CCSM4_rcp85_2006_2100_fix/rsds/rsds_mean_MJ-m2-d1_iem_ar5_NCAR-CCSM4_rcp85_'
  p clim vapo src = 'vap_mean_hPa_ar5_NCAR-CCSM4_rcp85_2006_2100_fix/vap/vap_mean_hPa_iem_ar5_NCAR-CCSM4_rcp85_'
  ''')

# variable specification, units, datatype, etc
# more or less the same as defining with netcdf CDL I guess..?
VARSPEC = {
  'vegetation.nc': {
    'veg_class': {'dims':'Y,X', 'dtype': 'i4'}
  },
  'soil-texture.nc': {
    'pct_sand': {'dims':'Y,X', 'dtype': 'f4'},
    'pct_silt': {'dims':'Y,X', 'dtype': 'f4'},
    'pct_clay': {'dims':'Y,X', 'dtype': 'f4'},
  },
  'drainage.nc': {
    'drainage_class': {'dims':'Y,X', 'dtype': 'i4'},
  },
  # Note not really using the same pattern for co2
  # seems simplest to just treat it differently since the
  # format is so different from all the other files. So just
  # copied the creation and filling code from create_region_input.py
  'co2.nc': { 
    'year': {'dims': 'year', 'dtype':'i4'},
    'co2': {'dims': 'year', 'dtype':'f4'},
  },
  'topo.nc': {
    'slope': {'dims':'Y,X', 'dtype':'f4'},
    'aspect': {'dims':'Y,X', 'dtype':'f4'},
    'elevation': {'dims':'Y,X', 'dtype':'f4'}
  },
  'fri-fire.nc': {
    'fri': {'dims':'Y,X', 'dtype':'i4'},
    'fri_severity': {'dims':'Y,X', 'dtype':'i4'},
    'fri_jday_of_burn': {'dims':'Y,X', 'dtype':'i4'},
    'fri_area_of_burn': {'dims':'Y,X', 'dtype':'i4'}
  },
  'projected-explicit-fire.nc': {
    'time': {'dims':'time', 'dtype':'f4', 'units':'REPLACE ME', 'long_name':'time','calendar':'365_day'},
    'exp_burn_mask': {'dims':'time,Y,X', 'dtype':'i4'},
    'exp_area_of_burn': {'dims':'time,Y,X', 'dtype':'i4'},
    'exp_fire_severity': {'dims':'time,Y,X', 'dtype':'i4'},
    'exp_jday_of_burn': {'dims':'time,Y,X', 'dtype':'i4'},
  },       
  'historic-explicit-fire.nc': {
    'time': {'dims':'time','dtype':'f4', 'units':'REPLACE ME', 'long_name':'time','calendar':'365_day'},
    'exp_burn_mask': {'dims':'time,Y,X','dtype':'i4'},
    'exp_area_of_burn': {'dims':'time,Y,X','dtype':'i4'},
    'exp_fire_severity': {'dims':'time,Y,X','dtype':'i4'},
    'exp_jday_of_burn': {'dims':'time,Y,X','dtype':'i4'},
  },       
  'projected-climate.nc': {
    'time': {'dims':'time', 'dtype':'f4', 'units':'REPLACE ME', 'long_name':'time','calendar':'365_day'},
    'tair': {'dims':'time,Y,X', 'dtype':'f4', 'units':'celsius', 'standard_name':'air_temperature'},
    'nirr': {'dims':'time,Y,X', 'dtype':'f4', 'units':'W m-2', 'standard_name':'downwelling_shortwave_flux_in_air'},
    'precip': {'dims':'time,Y,X', 'dtype':'f4', 'units':'mm month-1', 'standard_name':'precipitation_amount'},
    'vapor_press': {'dims':'time,Y,X', 'dtype':'f4', 'units':'hPa', 'standard_name':'water_vapor_pressure'},
  },   
  'historic-climate.nc': {
    'time': {'dims':'time','dtype':'f4', 'units':'REPLACE ME', 'long_name':'time','calendar':'365_day'},
    'tair': {'dims':'time,Y,X','dtype':'f4', 'units':'celsius', 'standard_name':'air_temperature'},
    'nirr': {'dims':'time,Y,X','dtype':'f4', 'units':'W m-2', 'standard_name':'downwelling_shortwave_flux_in_air'},
    'precip': {'dims':'time,Y,X','dtype':'f4', 'units':'mm month-1', 'standard_name':'precipitation_amount'},
    'vapor_press': {'dims':'time,Y,X','dtype':'f4', 'units':'', 'standard_name':'water_vapor_pressure'},
  },
}

def make_co2_file(fpath, fname, start_idx, end_idx):
  '''Generates a co2 file for dvmdostem from the RCP C02 data...'''

  print("Creating a co2 file...")
  new_ncfile = netCDF4.Dataset(os.path.join(fpath, fname), mode='w', format='NETCDF4')

  # Dimensions
  yearD = new_ncfile.createDimension('year', None) # append along time axis
    
  # Coordinate Variable
  yearV = new_ncfile.createVariable('year', np.int, ('year',))
    
  # Data Variables
  co2V = new_ncfile.createVariable('co2', np.float32, ('year',))

  co2V[:] = RCP_85_CO2_DATA[start_idx:end_idx]
  yearV[:] = RCP_85_CO2_YEARS[start_idx:end_idx]

  #new_ncfile.source = source_attr_string()
  new_ncfile.close()

def gli_wrapper(srcfile, lon, lat, dtype=None):
  '''gdallocationinfo wrapper'''
  s = "gdallocationinfo -wgs84 -valonly {} {} {}".format(srcfile, lon, lat)
  result = subprocess.run(s.split(' '), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
  # Should handle errors here....not sure what to do with them yet...
  data = result.stdout.decode('utf-8').strip()
  return data

def create_empty_file(fpath, fname):

  ncfile = netCDF4.Dataset(os.path.join(fpath,fname), mode='w', format='NETCDF4')

  Y = ncfile.createDimension('Y', 1)
  X = ncfile.createDimension('X', 1)
  
  if 'time' in VARSPEC[fname]:
    ncfile.createDimension('time', None) # append along time axis

  lat = ncfile.createVariable('lat', np.float32, ('Y', 'X',))
  lon = ncfile.createVariable('lon', np.float32, ('Y', 'X',))
  print(fname)
  print(VARSPEC[fname])
  for varname, spec in VARSPEC[fname].items():
    v = ncfile.createVariable(varname, spec['dtype'], spec['dims'].split(','))
    for attribute, attribute_value in spec.items():
      if attribute == 'dtype' or attribute == 'dims':
        pass
      else:
        v.setncattr(attribute, attribute_value)

  ncfile.close()

def fill_file_A(fpath, fname, var=None, data=None, startpt=None):
  '''Assumes that data passed in is the correct shape. No precautions taken here.'''
  if var not in VARSPEC[fname]:
    raise RuntimeError("Can't find var: {} in VARSPEC!".format(var))
  ncfile = netCDF4.Dataset(os.path.join(fpath, fname), mode='a')
  ncfile.variables[var][:] = data

  if var == 'time' and 'units' in ncfile.variables[var].ncattrs():
    ncfile.variables[var].units = startpt.strftime('days since %Y-%m-%d %H:%M:%S')

  ncfile.close()

def fill_file_B(fpath, fname, var=None, data=None, start=None, end=None):
  '''Not tested, don't think this is the way to go...prefer A'''
  if var not in VARSPEC[fname]:
    raise RuntimeError("Can't find var: {} in VARSPEC!".format(var))
  if start is None and end is None:
    print("Start and end are both None, assume this file does not have a time axis to worry about.")
    # Assumptions: 
    #  - file has dims Y,X each size 1
    #  - file has dims lat,lon each in terms of (Y,X)
    #  - file has one or more data variables, each in terms of (Y,X)
    ncfile = netCDF4.Dataset(os.path.join(fpath, fname), mode='a')
    ncfile.variables[var][:] = data
    ncfile.close()
  else: 
    print("Start or end is set, so we have to assume file has time axis.")
    # Assumptions: 
    #  - file has dims time,Y,X; time dimension is unlimited, Y and X are both size=1
    #  - file has coordinate variable named time, interms of (time)
    #  - file has variables lat,lon each in terms of (Y,X)
    #  - file has one of more variables in terms of (time,Y,X)
    #  - file 
    print("STUB - not doing anything yet...")

# Function used for building out the time coordinate variable info...
def time_offset(dt_obj, start_point):
  '''Takes a datetime object and a starting point (also datetime object)
  and returns the netcdf time offset, i.e. "days since YYYY-MM-DD".
  '''
  dt_obj = dt.datetime(dt_obj.year, dt_obj.month, dt_obj.day)
  tm_offset = netCDF4.date2num(
      dt_obj, 
      units="days since {}".format(start_point), 
      calendar='365_day'
  )
  return tm_offset

# Make some infor for the time coordinate. Minimal error checking...
# Time coordinate variable is a list of "offsets" from 
# the starting point. This code here sort of assumes monthly
# data, no time info. NetCDF/CF standards allow for much more
# detail, but we are ignoring for now...
# Get a time coordinate array
def basic_timecoord(start, end):
  time_coord_data = []
  for y in range(start.year, end.year+1):
    for m in range(start.month, end.month+1):
      d = fromisoformat('{}-{}-01'.format(y, m))
      time_coord_data.append(time_offset(d, start))
      #print(d, time_offset(d, start))
  return time_coord_data


def get_SNAP_climate_data(var, lon, lat, which=None, config=None, start=None, end='all'):
  '''Extract climate data from SNAP source files.
  This function is specific to the SNAP tif files so don't try to 
  generalize it.
  
  The timecoord is filled out by looking at the first source file, 
  finding the date, and then using netCDF4.date2num to get offset value
  in "days since..." resolution for each subsequent file (date parsed
  from file name)

  Returns
  -------
  data: list or numpy.array
    the data array for the point, read from source 
    files using gdallocationinfo
  timecoord: list or numpy.array
    the offsets from the starting point - from 
    starting point - for each of the src files 
  starting_point: datetime.date object
    the  for the first file in the source files
  '''
  if start is None:
    raise RuntimeError("Must set start date: 'YYYY-MM-DD'")

  # Map here from SNAP variable names (as in config dict) to 
  # our desired names (as expressed in VARSPEC)

  if which == 'historic':
    src_path = os.path.join(args.src_climate, config['h clim {} src'.format(var)])
  elif which == 'projected':
    src_path = os.path.join(args.src_climate, config['p clim {} src'.format(var)])
  else:
    src_path = '' # probably gonna crash later

  src_files = glob.glob(src_path + "*.tif")
  
  def date_key(x):
    '''Function that helps sort files by date. 
    Takes something like: 
        /some/long/path/mean_C_CRU_TS40_historical_11_1902.tif
    and returns a datetime object created from end of the file name.
    '''
    fdate = dt.date(
      year=int(os.path.splitext(os.path.basename(x))[0].split('_')[-1]), 
      month=int(os.path.splitext(os.path.basename(x))[0].split('_')[-2]),
      day=1)
    return fdate

  src_files = sorted(src_files, key=date_key)

  if start < date_key(src_files[0]) or end > date_key(src_files[-1]):
    raise RuntimeError("Date range exceeds available source files!!")

  # filter src_files here based on start and end...
  src_files = list(filter(lambda x: date_key(x) >= start and date_key(x) <= end, src_files))

  # basic, non-parallel approach:
  #data = [gli_wrapper(i, lon, lat) for i in src_files]

  # Or parallel approach
  # make the args (list of tuples) that get passed to gli_wrapper
  arg_list = zip(src_files, itertools.repeat(lon), itertools.repeat(lat))
  with mp.Pool(processes=6) as pool:
    data = pool.starmap(gli_wrapper, arg_list)

  #from IPython import embed; embed()
  # Handle issues for each variable...
  if var == 'rsds':
    # Coerce data into expected type. Note variable names are different - 
    # in the SNAP files (config dict) it is rsds, in our files (VARSPEC) it is nirr
    data = np.array(data, dtype=VARSPEC['{}-climate.nc'.format(which)]['nirr']['dtype'])
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    print("%% NOTE! Converting rsds (nirr) from MJ/m^2/day to W/m^2!")
    print("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%")
    data[:] = (1000000 / (60*60*24)) * data[:]

  assert len(data) == len(src_files), "data array does not match number of source files!"

  start_point = date_key(src_files[0]).strftime('%Y-%m-%d')
  timecoord = [time_offset(date_key(i), start_point) for i in src_files]

  return data, timecoord, dt.datetime.fromordinal(date_key(src_files[0]).toordinal())

def make_climate(lon, lat, which=None, config=None, start=None, end=None):
  if which == 'historic':
    create_empty_file(base_outdir, 'historic-climate.nc')
    tair_data, _, _ = get_SNAP_climate_data('tair', lon, lat, which='historic', config=config, start=start, end=end)
    nirr_data, _, _ = get_SNAP_climate_data('rsds', lon, lat, which='historic', config=config, start=start, end=end)
    vapo_data, _, _ = get_SNAP_climate_data('vapo', lon, lat, which='historic',config=config, start=start, end=end)
    precip_data, time_coord, startpt = get_SNAP_climate_data('prec', lon, lat, which='historic', config=config, start=start, end=end)
    fill_file_A(base_outdir, 'historic-climate.nc', var='tair', data=tair_data)
    fill_file_A(base_outdir, 'historic-climate.nc', var='nirr', data=nirr_data)
    fill_file_A(base_outdir, 'historic-climate.nc', var='vapor_press', data=vapo_data)
    fill_file_A(base_outdir, 'historic-climate.nc', var='precip', data=precip_data)
    fill_file_A(base_outdir, 'historic-climate.nc', var='time', data=time_coord, startpt=startpt)

  elif which == 'projected':
    create_empty_file(base_outdir, 'projected-climate.nc')
    tair_data, _, _ = get_SNAP_climate_data('tair', lon, lat, which='projected', config=config, start=start, end=end)
    nirr_data, _, _ = get_SNAP_climate_data('rsds', lon, lat, which='projected', config=config, start=start, end=end)
    vapo_data, _, _ = get_SNAP_climate_data('vapo', lon, lat, which='projected',config=config, start=start, end=end)
    precip_data, time_coord, startpt = get_SNAP_climate_data('prec', lon, lat, which='projected', config=config, start=start, end=end)
    fill_file_A(base_outdir, 'projected-climate.nc', var='tair', data=tair_data)
    fill_file_A(base_outdir, 'projected-climate.nc', var='nirr', data=nirr_data)
    fill_file_A(base_outdir, 'projected-climate.nc', var='vapor_press', data=vapo_data)
    fill_file_A(base_outdir, 'projected-climate.nc', var='precip', data=precip_data)
    fill_file_A(base_outdir, 'projected-climate.nc', var='time', data=time_coord, startpt=startpt)


def fromisoformat(isostring):
  '''
  Work around since python 3.6 does not have dt.date.fromisoformat().
  Parameters:
    `isostring` is expected to be YYYY-MM-DD formatted.
  Returns:
    A date object (no time)
  '''
  d = dt.datetime.strptime(isostring, "%Y-%m-%d")
  return dt.date(d.year, d.month, d.day)


def lat_validator(lat):
  if lat < 0 or lat > 90:
    raise argparse.ArgumentTypeError("Invalid latitude")
  return lat

def lon_validator(lon):
  if lon < -359 or lon > 360:
    raise argparse.ArgumentTypeError("Invalid longitude")

def src_climate_validator(arg_src_climate):
  '''Make sure that the directory exists and has files...'''
  try:
    files = os.listdir(arg_src_climate)
  except OSError as e:
    msg = "Invalid folder for source climate data! {}".format(e)
    raise argparse.ArgumentTypeError(msg)
  return arg_src_climate

if __name__ == '__main__':

  parser = argparse.ArgumentParser(
 
      description=textwrap.dedent('''help'''),
      epilog=textwrap.dedent('''epilog'''),
  )
  parser.add_argument('--src-climate', type=src_climate_validator,  help='path to source climate files')
  parser.add_argument('--src-ancillary', help='path to source ancillary files')
  parser.add_argument('--src-config', default='mri-cgcm3', choices=['mri-cgcm3','ncar-ccsm4'],
    help='choose config that maps how the source input files should be laid out (directories, file names, etc)')

  parser.add_argument('--date-range', type=fromisoformat, nargs=2,
    help='start and end dates for the generated files. must be w/in 1901-2100')

  parser.add_argument('--lat', default=65.161991, type=lat_validator, help="Latitude of point")
  parser.add_argument('--lon', default=-164.823923, type=lon_validator, help="Longitude of point")

  parser.add_argument('--outdir', default='input-staging-area', 
    help='path to directory where new folder of files should be written')
  
  parser.add_argument('--tag', default='cru-ts40_ar5_rcp85_')

  args = parser.parse_args()
  print("Command line args: {}".format(args))

  # More validation....
  if args.date_range[0] < fromisoformat('1901-01-01'):
    raise argparse.ArgumentTypeError("Start date too early")
  if args.date_range[1] > fromisoformat('2100-12-31'):
    raise argparse.ArgumentTypeError("End date too late")

  print("Reading config file...")
  config = configobj.ConfigObj(BASE_AR5_RCP85_CONFIG.split("\n"))

  # Pick up the user's config option for which projected climate to use 
  # overwrite the section in the config object.
  cmdline_config = configobj.ConfigObj()
  if 'ncar-ccsm4' in args.src_config:
    cmdline_config = configobj.ConfigObj(NCAR_CCSM4_AR5_RCP85_CONFIG.split("\n"))
  elif 'mri-cgcm3' in args.src_config:
    cmdline_config = configobj.ConfigObj(MRI_CGCM3_AR5_RCP85_CONFIG.split("\n"))
  config.merge(cmdline_config)
  #print("\n".join(config.write()))

  # Location as requested from command line
  lon = args.lon
  lat = args.lat

  # Dates as requested from command line
  start, end = args.date_range

  # Setup name of files
  base_outdir = os.path.join( args.outdir, 'SITE_{}_{}'.format(args.tag, config['p clim orig inst']) )
  print("Will be (over)writing files to:    ", base_outdir)
  if not os.path.exists(base_outdir):
    os.makedirs(base_outdir)

  with netCDF4.Dataset(os.path.join(base_outdir, 'run-mask.nc'), 'w', format='NETCDF4') as ds:
  
    ds.createDimension('Y', 1)
    ds.createDimension('X', 1)
    ds.createVariable('run', np.int, ('Y', 'X',))
    ds.variables['run'][:] = 1
    print(ds)

  # Start making and filling files
  create_empty_file(base_outdir, 'drainage.nc')
  drainage_class = gli_wrapper(os.path.join(args.src_ancillary, config['drainage src']), lon, lat)
  # NOTE!: Need to threshold drainage data before writing...
  fill_file_A(base_outdir, 'drainage.nc', var='drainage_class', data=drainage_class)

  create_empty_file(base_outdir, 'topo.nc')
  slope = gli_wrapper(os.path.join(args.src_ancillary, config['topo slope src']), lon, lat)
  aspect = gli_wrapper(os.path.join(args.src_ancillary, config['topo aspect src']), lon, lat)
  elevation = gli_wrapper(os.path.join(args.src_ancillary, config['topo elev src']), lon, lat)
  fill_file_A(base_outdir, 'topo.nc', var="slope", data=slope)
  fill_file_A(base_outdir, 'topo.nc', var="aspect", data=aspect)
  fill_file_A(base_outdir, 'topo.nc', var="elevation", data=elevation)

  create_empty_file(base_outdir, 'vegetation.nc')
  veg_class = gli_wrapper(os.path.join(args.src_ancillary, config['veg src']), lon, lat)
  fill_file_A(base_outdir, 'vegetation.nc', var='veg_class', data=veg_class)

  create_empty_file(base_outdir, 'soil-texture.nc')
  pct_sand = gli_wrapper(os.path.join(args.src_ancillary, config['soil sand src']), lon, lat)
  pct_silt = gli_wrapper(os.path.join(args.src_ancillary, config['soil silt src']), lon, lat)
  pct_clay = gli_wrapper(os.path.join(args.src_ancillary, config['soil clay src']), lon, lat)
  fill_file_A(base_outdir, 'soil-texture.nc', var='pct_sand', data=pct_sand)
  fill_file_A(base_outdir, 'soil-texture.nc', var='pct_silt', data=pct_silt)
  fill_file_A(base_outdir, 'soil-texture.nc', var='pct_clay', data=pct_clay)

  # Fire - stubbed out for now w/ hard coded values as we don't have a source dataset setup yet...
  create_empty_file(base_outdir, 'fri-fire.nc')
  vnames = ['fri', 'fri_severity', 'fri_jday_of_burn', 'fri_area_of_burn']
  for v in vnames:
    fill_file_A(base_outdir, 'fri-fire.nc', var=v, data=0)


  # TIME dependant files: climate, fire, CO2

  # Climate and fire inputs share assumptions about time axis:
  # both are monthly resolution, while CO2 is yearly.
  # For now it is assumed that the fire files time axis matches 
  # exactly the climate files time axis. The climate files time 
  # axis is set based on the values in the config objects and the
  # availability of the files. If we setup fire inputs in the future
  # we could add entries to the config object. For now we will set
  # the fire time axes based on the climate files.

  # range of dates available in input climate files (as set in config)
  hrange = (fromisoformat('{}-01-01'.format(config['h clim first yr'])), fromisoformat('{}-12-01'.format(config['h clim last yr'])))
  prange = (fromisoformat('{}-01-01'.format(config['p clim first yr'])), fromisoformat('{}-12-01'.format(config['p clim last yr'])))

  # Basic check - user dates within range of historic and projected
  if not (start >= hrange[0] and end <= prange[1]):
    raise RuntimeError("Invalid date range!")

  if start <= hrange[1]:
    if end <= hrange[1]: # historic: start => end
      # CLIMATE
      make_climate(lon, lat, which='historic', config=config, start=start, end=end)

      # FIRE
      create_empty_file(base_outdir, 'historic-explicit-fire.nc')
      tc_data = basic_timecoord(start, end)
      fill_file_A(base_outdir, 'historic-explicit-fire.nc', var='time', data=tc_data, startpt=start)
      vnames = 'exp_burn_mask,exp_area_of_burn,exp_fire_severity,exp_jday_of_burn'.split(',')
      for v in vnames:
        fill_file_A(base_outdir, 'historic-explicit-fire.nc', var=v, data=np.zeros(len(tc_data)))

      # CO2
      sidx = RCP_85_CO2_YEARS.index(start.year)
      eidx = RCP_85_CO2_YEARS.index(end.year) + 1
      make_co2_file(base_outdir, 'co2.nc', sidx, eidx)
    elif end > hrange[1]: # historic: start => hrange[1], projected: hrange[1]+1 => end
      # CLIMATE - historic
      make_climate(lon, lat, which='historic', config=config, start=start, end=hrange[1])

      # FIRE - historic
      create_empty_file(base_outdir, 'historic-explicit-fire.nc')
      tc_data = basic_timecoord(start, hrange[1])
      fill_file_A(base_outdir, 'historic-explicit-fire.nc', var='time', data=tc_data, startpt=start)
      vnames = 'exp_burn_mask,exp_area_of_burn,exp_fire_severity,exp_jday_of_burn'.split(',')
      for v in vnames:
        fill_file_A(base_outdir, 'historic-explicit-fire.nc', var=v, data=np.zeros(len(tc_data)))

      # CO2 - historic
      sidx = RCP_85_CO2_YEARS.index(start.year)
      eidx = RCP_85_CO2_YEARS.index(hrange[1].year) + 1
      make_co2_file(base_outdir, 'co2.nc', sidx, eidx)

      # make projected files from hrange[1] + 1 month to end
      begin_proj = hrange[1] + dt.timedelta(days=calendar.monthrange(hrange[1].year, hrange[1].month)[1])

      # CLIMATE - projected 
      make_climate(lon, lat, which='projected', config=config, start=begin_proj, end=end)

      # FIRE - projected
      create_empty_file(base_outdir, 'projected-explicit-fire.nc')
      vnames = 'exp_burn_mask,exp_area_of_burn,exp_fire_severity,exp_jday_of_burn'.split(',')
      tc_data = basic_timecoord(begin_proj, end)
      fill_file_A(base_outdir, 'projected-explicit-fire.nc', var='time', data=tc_data, startpt=begin_proj)
      for v in vnames:
        fill_file_A(base_outdir, 'projected-explicit-fire.nc', var=v, data=np.zeros(len(tc_data)))

      # C02 - projected
      sidx = RCP_85_CO2_YEARS.index(begin_proj.year)
      eidx = RCP_85_CO2_YEARS.index(end.year) + 1
      make_co2_file(base_outdir, 'projected-co2.nc', sidx, eidx)
    else:
      print("How did I get here???")
  elif start > hrange[1]: # make projected: start => end
    # CLIMATE
    make_climate(lon, lat, which='projected', config=config, start=start, end=end)

    # FIRE
    create_empty_file(base_outdir, 'projected-explicit-fire.nc')
    vnames = 'exp_burn_mask,exp_area_of_burn,exp_fire_severity,exp_jday_of_burn'.split(',')
    tc_data = basic_timecoord(start, end)
    fill_file_A(base_outdir, 'projected-explicit-fire.nc', var='time', data=tc_data, startpt=start)
    for v in vnames:
      fill_file_A(base_outdir, 'projected-explicit-fire.nc', var=v, data=np.zeros(len(tc_data)))

    # CO2
    sidx = RCP_85_CO2_YEARS.index(start.year)
    eidx = RCP_85_CO2_YEARS.index(end.year) + 1 
    make_co2_file(base_outdir, 'projected-co2.nc', sidx, eidx)
  else:
    print("How did I get here???")






# ./scripts/create_site_input.py \
# --src-climate ../snap-data-2019 \
# --src-ancillary ../snap-data-2019/ancillary \
# --date-range 2016-01-01 2017-12-01

