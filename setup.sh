curl -L -o pygplates.zip http://downloads.sourceforge.net/project/gplates/pygplates/beta-revision-12/pygplates_rev12_python27_MacOS64.zip?r=&ts=1467312228&use_mirror=tenet
unzip -a pygplates.zip
rm pygplates.zip

curl -L -O ftp://earthbyte.org/earthbyte/GPlates/SampleData_GPlates1.5/Individual/FeatureCollections/Rotations.zip
unzip -a Rotations.zip
rm Rotations.zip

curl -L -O ftp://earthbyte.org/earthbyte/GPlates/SampleData_GPlates1.5/Individual/FeatureCollections/ContinentalPolygons.zip
unzip -a ContinentalPolygons.zip
rm ContinentalPolygons.zip

curl -L -O ftp://ftp.earthbyte.org/papers/Wright_etal_Paleobiogeography/1_Phanerozoic_Plate_Motions_GPlates.zip
unzip -a 1_Phanerozoic_Plate_Motions_GPlates.zip
rm 1_Phanerozoic_Plate_Motions_GPlates.zip

curl -L -O ftp://earthbyte.org/earthbyte/GPlates/SampleData_GPlates1.5/Individual/FeatureCollections/StaticPolygons.zip
unzip -a StaticPolygons.zip
rm StaticPolygons.zip

curl -L -O http://download.osgeo.org/libspatialindex/spatialindex-src-1.8.5.tar.gz
tar -zxvf spatialindex-src-1.8.5.tar.gz
rm spatialindex-src-1.8.5.tar.gz
cd spatialindex-src-1.8.5
make
make install
cd ..

echo "Done downloading pygplates and associated data"
