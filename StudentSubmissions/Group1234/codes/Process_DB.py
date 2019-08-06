#Compute which bus stops are in a D-metre ball around DA centroids
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
import numpy as np
from scipy.spatial import cKDTree  
import zipfile

DF = pd.read_csv("/home/csis/codes/GTFS/GTFS_Sources_temp.csv", encoding='iso-8859-1')

DF=DF.loc[(DF.Open=='Open') & (DF.Complete=='Yes')]
Prov=DF.Province
City=DF["City or Region"]

combine=zip(City,Prov)
#radius
D=1000.

#city='Montreal'


#read shapefile with geopandas into geodataframe
#sc1=gpd.read_file('/home/csis/codes/StatCanBounds/lda_000b16a_e/lda_000b16a_e.shp')
sc1=pd.read_csv('DB_Centroids.csv')
sc1['geometry']=sc1.apply(lambda z: Point(z.longitude,z.latitude),axis=1)
sc1=gpd.GeoDataFrame(sc1)
db_lon=list(sc1.longitude)
db_lat=list(sc1.latitude)
sc1.crs={'init': 'epsg:4326'}
sc1=sc1.to_crs({'init': 'epsg:3347'})
Centroids = np.array(list(zip(sc1.geometry.x, sc1.geometry.y)) )

#stop locations are in csv, read as pd dataframe

for city, prov in combine:
	print(city, prov)
	zf = zipfile.ZipFile('/home/csis/codes/GTFS/'+prov+'/'+city+'/GTFS.zip')
	transit=pd.read_csv(zf.open('stops.txt'))
	transit=transit[['stop_id','stop_lat','stop_lon']]
	#convert to GeoDataFrame
	transit['geometry']=transit.apply(lambda z: Point(z.stop_lon,z.stop_lat),axis=1)
	transit=gpd.GeoDataFrame(transit)
	stop_lon=list(transit.stop_lon)
	stop_lat=list(transit.stop_lat)

	#assume lon/lats are standard wgs84
	transit.crs={'init': 'epsg:4326'}

	#convert to statcan projection
	transit=transit.to_crs({'init': 'epsg:3347'})

	#projections are now the same, so we can compute a distance matrix

	#for efficiency, construc k-dim trees using scipy

	Stops = np.array(list(zip(transit.geometry.x, transit.geometry.y)) )

	C_tree=cKDTree(Centroids)
	S_tree=cKDTree(Stops)
	#find all stops in radius D of every centroid

	points=C_tree.query_ball_tree(S_tree,r=D)


	#points is a list of lists, where each list i contains indices of stops within range for centroid i.
	N=len(points)
	DB=[]
	stop=[]
	stop_x=[]
	stop_y=[]
	DB_x=[]
	DB_y=[]
	distance=[]
	print(transit.head())
	DBlist=list(sc1.DBUID)
	stoplist=list(transit.stop_id)
	for i in range(N):
	    l=points[i]


	    if l==[]:
	#        DA.append(DAlist[i])
	#        stop.append('')
	#        distance.append('')
    		continue
	    else:
		    for j in l:
                
		        DB.append(DBlist[i])
		        DB_x.append(db_lon[i])
		        DB_y.append(db_lat[i])
		        stop.append(stoplist[j])
		        stop_x.append(stop_lon[j])
		        stop_y.append(stop_lat[j])
		        distance.append(np.linalg.norm(Centroids[i]-Stops[j]))
	#output distances
	dictionary={'DBUID':DB,'DB_x':DB_x,'DB_y':DB_y, 'stop_id':stop,'stop_lon':stop_x, 'stop_lat':stop_y,'distance':distance}            
	df=pd.DataFrame(dictionary)
	df=df.dropna()
	df.to_csv('DB_Stop_1km_'+prov+'_'+city+'.csv',index=False)
